import json
from rest_framework.response import Response  # update database
from rest_framework.decorators import (
    api_view,
    renderer_classes,
)  # action, update database
from django.http import JsonResponse, HttpResponse

from .game import Game, Board, GameStateless
from .models import *
from .serializers import SerializerScore, SerializerGameState

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
        playernr = int(request.data.get("nrPlayer"))
        roomnr = int(request.data.get("roomnr"))
        GameState3.objects.filter(roomnr=roomnr).delete()
        Moves1.objects.filter(roomnr=roomnr).delete()
        GameState3.objects.create(roomnr=roomnr, playernr=playernr)
        return Response({"ll_piece": game1.init_ll_piece(playernr)})

    except Exception as e:
        print("Error by starten: ", e)
        return Response({"error": "Invalid input"}, status=400)


@api_view(["POST"])
def reset(request):
    """Remove the instance from dct_game and the saved game in db"""
    try:
        roomnr = int(request.data.get("roomnr"))
        game_state1 = GameState3.objects.filter(roomnr=roomnr)
        if game_state1.exists():
            game_state1.delete()
        move1 = Moves1.objects.filter(roomnr=roomnr)
        if move1.exists():
            move1.delete()
        return Response({"ok": True})
    except Exception as e:
        print("Error by reset: ", e)
        return Response({"ok": False}, status=400)


# @csrf_exempt  # This disables 'Cross-site request forgery' for this view
@api_view(["POST"])  # DRF handles JSON & CSRF protection
def klicken(request):
    # because of backward function, it should delete the moves, if it is forwarded to the middle and make a move
    try:
        roomnr = int(request.data.get("roomnr"))
        coord_int = (int(request.data.get("xr")), int(request.data.get("yr")))
        game1.click(roomnr, coord_int)

        state = GameState3.objects.get(roomnr=roomnr)
        Moves1.objects.filter(roomnr=roomnr, movenr__gt=state.movenr).delete()
        # once insert a move, the recorded moves should be deleted to avoid branch
        moves = Moves1.objects.filter(roomnr=roomnr)

        serializer = SerializerGameState(state)
        dct_response = serializer.data
        dct_response["ll_piece"] = game1.get_ll_piece(state, moves)
        dct_response["gewonnen"] = False
        return Response(dct_response)

    except Exception as e:
        print("Error by click: ", e)
        return Response({"error": "Invalid JSON data"}, status=400)


@api_view(["GET"])
def reload_state(request):
    """Search in DB, if exist return"""
    roomnr = int(request.GET.get("roomnr"))
    state = GameState3.objects.filter(roomnr=roomnr).first()
    if not state:
        return Response({"exist": False})
    else:
        moves = Moves1.objects.filter(roomnr=roomnr)
        serializer = SerializerGameState(state)
        dct_response = serializer.data
        dct_response["ll_piece"] = game1.get_ll_piece(state, moves)
        dct_response["exist"] = True
        return Response(dct_response)


@api_view(["GET"])
def room_info(request):
    """Return backend information"""
    lst_roomnr = list(GameState3.objects.values_list("roomnr", flat=True))
    lst_roomnr.sort()
    return Response({"lst_roomnr": lst_roomnr})


@api_view(["POST"])
def ward(request):
    """Method for backward or forward"""
    direction = request.data.get("direction")
    roomnr = int(request.data.get("roomnr"))
    try:
        state = GameState3.objects.get(roomnr=roomnr)
    except GameState3.DoesNotExist:
        Response({"moved": False})
    moves = Moves1.objects.filter(roomnr=roomnr)
    if direction:
        moves_gt = moves.filter(movenr__gt=state.movenr)
        print(moves_gt)
        if moves_gt:
            GameState3.objects.update_or_create(
                roomnr=roomnr,
                defaults={
                    "selected": [],
                    "valid_pos": [],
                    "turnwise": (state.turnwise + 1) % state.playernr,
                    "movenr": state.movenr + 1,
                },
            )
        else:
            Response({"moved": False})
    else:
        if state.movenr > 0:
            GameState3.objects.update_or_create(
                roomnr=roomnr,
                defaults={
                    "selected": [],
                    "valid_pos": [],
                    "turnwise": (state.turnwise - 1 + state.playernr) % state.playernr,
                    "movenr": state.movenr - 1,
                },
            )
        else:
            Response({"moved": False})
    state2 = GameState3.objects.get(roomnr=roomnr)
    # moves = Moves1.objects.filter(roomnr=roomnr)
    serializer = SerializerGameState(state2)
    dct_response = serializer.data
    dct_response["ll_piece"] = game1.get_ll_piece(state2, moves)
    dct_response["gewonnen"] = False
    dct_response["moved"] = True
    return Response(dct_response)
