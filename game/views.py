import json

# import pickle
# import base64
from django.shortcuts import render

# from rest_framework import viewsets, status # class view
# from rest_framework.renderers import JSONRenderer  # class view
from rest_framework.response import Response  # update database
from rest_framework.decorators import (
    api_view,
    renderer_classes,
)  # action, update database
from django.http import JsonResponse, HttpResponse

# from django.views.decorators.csrf import csrf_exempt
from .game import Game, Board
from .models import Score, Game_state
from .serializers import SerializerScore

board1 = Board()  # to initialize board when the game is loaded for the first time
dct_game = {}
roomnr = 0


def index(request):
    return HttpResponse("Homepage")


def return_board(request):
    return JsonResponse(board1.lst_board_int, safe=False)


@api_view(["POST"])
def starten(request):
    """this should start game. Front should send nr_player here and reset game"""
    try:
        nr_player = int(request.data.get("nrPlayer", 0))
        roomnr = int(request.data.get("roomnr", 0))
        if roomnr not in dct_game:
            dct_game[roomnr] = Game(nr_player=nr_player, roomnr=roomnr)
            return Response(
                {"exist": False, "ll_piece": dct_game[roomnr].get_ll_piece()}
            )
        else:
            return Response(
                {"exist": True, "ll_piece": dct_game[roomnr].get_ll_piece()}
            )
    except Exception as e:
        print(e)
        return Response({"error": "Invalid input"}, status=400)


@api_view(["POST"])
def reset(request):
    """Remove the instance from dct_game and the saved game in db"""
    try:
        roomnr = int(request.data.get("roomnr", 0))
        del dct_game[int(roomnr)]
        # game_state = Game_state.objects.get(roomnr=roomnr)
        # game_state.delete()
        return Response({"ok": True})
    except Exception as e:
        print(e)
        return Response({"ok": False}, status=400)


# @csrf_exempt  # This disables 'Cross-site request forgery' for this view
@api_view(["POST"])  # DRF handles JSON & CSRF protection
def klicken(request):
    try:
        coord_round = (int(request.data.get("xr", 0)), int(request.data.get("yr", 0)))
        roomnr = int(request.data.get("roomnr", 0))
        # game1 = pickle.loads(
        #     base64.b64decode(request.session.get("game").encode("utf-8"))
        # )
        selected, valid_pos, neue_figuren, order, gewonnen = dct_game[roomnr].klicken(
            coord_round
        )
        # request.session["game"] = base64.b64encode(pickle.dumps(game1)).decode("utf-8")
        return Response(
            {
                "selected": selected,
                "validPos": valid_pos,
                "neueFiguren": neue_figuren,
                "order": order,
                "gewonnen": gewonnen,
            }
        )
    except (TypeError, ValueError):
        return Response({"error": "Invalid JSON data"}, status=400)


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


@api_view(["POST"])
def save_state(request):
    roomnr = int(request.data.get("roomnr", 0))
    if roomnr in dct_game:
        dct_game[roomnr].save_state()
        return Response({"message": "game saved"}, status=201)
    else:
        return Response({"message": "game not saved"}, status=201)


@api_view(["GET"])
def reload_state(request):
    """Search in DB, if exist return"""
    # roomnr = int(request.data.get("roomnr", 0))
    roomnr = int(request.GET.get("roomnr"))
    raw_states = Game_state.objects.filter(roomnr=roomnr)
    lst_state = list(raw_states.values("order", "roomnr", "state_players"))
    if not raw_states.exists():
        return Response({"exist": False})
    if roomnr in dct_game:
        return Response({"exist": True, "taken": True})
    dct_game[roomnr] = Game(
        roomnr=roomnr,
        state_players=lst_state[0]["state_players"],
        order=lst_state[0]["order"],
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
def backend_info(request):
    """Return backend information"""
    lst_roomnr_db = Game_state.objects.values_list("roomnr", flat=True).distinct()
    return Response({"lst_roomnr": dct_game.keys(), "lst_roomnr_db": lst_roomnr_db})


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
