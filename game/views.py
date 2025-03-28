import json
from rest_framework.response import Response  # update database
from rest_framework.decorators import (
    api_view,
    renderer_classes,
)  # action, update database
from django.http import JsonResponse, HttpResponse

from .game import Game, Board, GameStateless
from .models import *
from .serializers import SerializerScore

board1 = Board()  # to initialize board when the game is loaded for the first time
dct_game = {}
game1 = GameStateless()
roomnr = 0


def index(request):
    return HttpResponse("Homepage. Please play the game from the frontend")


def return_board(request):
    return JsonResponse(board1.lst_board_int, safe=False)


@api_view(["POST"])
def starten(request):
    """this should start game. Front should send nr_player here and reset game"""
    try:
        playernr = int(request.data.get("nrPlayer", 0))
        roomnr = int(request.data.get("roomnr", 0))
        if roomnr not in dct_game:
            dct_game[roomnr] = Game(nr_player=playernr, roomnr=roomnr)
            GameState3.objects.filter(roomnr=roomnr).delete()
            GameState3.objects.create(
                roomnr=roomnr,
                playernr=playernr,
            )
            return Response(
                {"exist": False, "ll_piece": dct_game[roomnr].get_ll_piece()}
            )
        else:
            return Response(
                {"exist": True, "ll_piece": dct_game[roomnr].get_ll_piece()}
            )
    except Exception as e:
        print("Error by starting the game: ", e)
        return Response({"error": "Invalid input"}, status=400)


@api_view(["POST"])
def reset(request):
    """Remove the instance from dct_game and the saved game in db"""
    try:
        roomnr = int(request.data.get("roomnr", 0))
        if int(roomnr) in dct_game:
            del dct_game[int(roomnr)]
        game_state = GameState.objects.filter(roomnr=roomnr)
        if game_state.exists():
            game_state.delete()
        game_state1 = GameState1.objects.filter(roomnr=roomnr)
        if game_state1.exists():
            game_state1.delete()
        return Response({"ok": True})
    except Exception as e:
        print("Error by reseting the game: ", e)
        return Response({"ok": False}, status=400)


# @csrf_exempt  # This disables 'Cross-site request forgery' for this view
@api_view(["POST"])  # DRF handles JSON & CSRF protection
def klicken(request):
    try:
        coord_int = (int(request.data.get("xr", 0)), int(request.data.get("yr", 0)))
        roomnr = int(request.data.get("roomnr", 0))
        movenr = int(request.data.get("movenr", 0))
        # selected is None means it is waiting for clicking on a piece
        try:
            state = GameState3.objects.get(roomnr=roomnr)
        except GameState3.DoesNotExist:
            print("Game should have been created but not exist")
        if state.selected is None:
            # selected and valid_pos must be none or not none at the same time
            # print(get_ll_pieces(roomnr, movenr, game1))
            valid_pos1 = game1.click_piece(
                coord_int, state.turnwise, get_ll_pieces(roomnr, movenr, game1)
            )
            if valid_pos1:
                selected1 = coord_int
                GameState3.objects.update_or_create(
                    roomnr=roomnr,
                    defaults={
                        "selected": selected1,
                        "valid_pos": valid_pos1,
                    },
                )
        else:
            # a piece is alread selected, now make the move
            if list(coord_int) in state.valid_pos:
                GameState3.objects.update_or_create(
                    roomnr=roomnr,
                    defaults={
                        "selected": None,
                        "valid_pos": None,
                        "turnwise": state.turnwise + 1 % state.playernr,
                        "movenr": state.movenr + 1,
                    },
                )
                Moves1.objects.update_or_create(
                    roomnr=roomnr,
                    movenr=movenr,
                    defaults={
                        "coord_from": state.selected,
                        "coord_to": coord_int,
                    },
                )
            else:
                print("invalid move")

        selected, valid_pos, neue_figuren, order, gewonnen = dct_game[roomnr].klicken(
            coord_int
        )
        return Response(
            {
                "selected": selected,
                "validPos": valid_pos,
                "neueFiguren": neue_figuren,
                "order": order,
                "gewonnen": gewonnen,
            }
        )
    except Exception as e:
        print("Error by click: ", e)
        return Response({"error": "Invalid JSON data"}, status=400)


@api_view(["POST"])
def save_state(request):
    roomnr = int(request.data.get("roomnr", 0))
    if roomnr in dct_game:
        dct_game[roomnr].save_state()
        return Response({"message": "game saved"}, status=201)
    else:
        return Response({"message": "game not saved"}, status=200)


@api_view(["GET"])
def reload_state(request):
    """Search in DB, if exist return"""
    # roomnr = int(request.data.get("roomnr", 0))
    roomnr = int(request.GET.get("roomnr"))
    raw_states = GameState.objects.filter(roomnr=roomnr)
    lst_state = list(raw_states.values("order", "roomnr", "state_players"))
    if not raw_states.exists():
        return Response({"exist": False})
    if roomnr in dct_game:
        return Response({"exist": True, "taken": True})
    dct_game[roomnr] = Game(
        roomnr=roomnr,
        state_players=lst_state[0]["state_players"],
        turnwise=lst_state[0]["order"],
    )
    return Response(
        {
            "exist": True,
            "taken": False,
            "ll_piece": dct_game[roomnr].get_ll_piece(),
            "order": lst_state[0]["order"],
        }
    )
    # except Game_state.DoesNotExist:
    #     return Response({})


@api_view(["GET"])
def room_info(request):
    """Return backend information"""
    lst_roomnr_saved = list(
        GameState.objects.values_list("roomnr", flat=True)
    )  # .distinct()
    lst_roomnr_saved.sort()
    lst_roomnr_taken = list(dct_game.keys())
    lst_roomnr_taken.sort()
    lst_roomnr_temp = list(GameState1.objects.values_list("roomnr", flat=True))
    lst_roomnr_temp.sort()
    return Response(
        {
            "lst_roomnr_taken": lst_roomnr_taken,
            "lst_roomnr_saved": lst_roomnr_saved,
            "lst_roomnr_temp": lst_roomnr_temp,
        }
    )


@api_view(["GET"])
# @renderer_classes([JSONRenderer])  # Ensure response is JSON
def get_score(request):
    scores = Score.objects.all().order_by("score")[:5]
    serializer = SerializerScore(scores, many=True)  # serializing multiple object
    return Response(serializer.data)


@api_view(["POST"])
# @renderer_classes([JSONRenderer])
def add_score(request):
    score = request.data.get("score")
    name = request.data.get("name")

    if not score or not name or len(name) > 20:
        return Response({"error": "Invalid input"}, status=400)
    Score.objects.create(score=score, name=name)
    scores = Score.objects.all().order_by("score")
    if scores.count() > 5:
        scores.last().delete()

    return Response({"success": "Score added"}, status=201)


# import pickle
# import base64
# from django.shortcuts import render
# from rest_framework import viewsets, status # class view
# from rest_framework.renderers import JSONRenderer  # class view
# from django.views.decorators.csrf import csrf_exempt
# class ViewsetScore(viewsets.ModelViewSet):
#     queryset = Score.objects.all().order_by('score')[:5]
#     serializer_class = SerializerScore
#     renderer_classes = [JSONRenderer] # otherwise it will search for html template, which doesn't exist

#     @action(detail=False, methods=['post'])
#     def add_score(self, request):
#         score = request.data.get('score')
#         name = request.data.get('name')

#         if not score or not name or len(name) > 20:
#             return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)

#         # Add the new score to the database
#         Score.objects.create(score=score, name=name)

#         # Maintain a maximum of 5 rows in the database, remove the highest score if needed
#         scores = Score.objects.all().order_by('score')
#         if scores.count() > 5:
#             scores.last().delete()

#         return Response({'success': 'Score added'}, status=status.HTTP_201_CREATED)

# pickle example
# request.session["test_home"] = "test_home"
# if "game" in request.session.keys():
#     game1 = pickle.loads(
#         base64.b64decode(request.session.get("game").encode("utf-8"))
#     )
# else:
#     game1 = Game()
#     request.session["game"] = base64.b64encode(pickle.dumps(game1)).decode("utf-8")
