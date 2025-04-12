import json
from rest_framework.response import Response  # update database
from rest_framework.decorators import api_view  # action, update database
from django.http import JsonResponse, HttpResponse

from .game import Board, GameStateless
from .models import Moves, GameStateTemp
from .serializers import SerializerGameState

Board.setup_class()
game1 = GameStateless()


def index(request):
    return HttpResponse("Homepage. Please play the game from the frontend")


def return_board(request):
    return JsonResponse(Board.lst_board_int, safe=False)


@api_view(["POST"])
def starten(request):
    """Front should send nr_player here and reset game
    Args:
        request:
            - nrPlayer (int): The number of players.
            - roomnr (int): The room number.
    Returns:
        Response: ll_piece (list)
    """
    try:
        playernr = int(request.data.get("nrPlayer"))
        roomnr = int(request.data.get("roomnr"))
        GameStateTemp.objects.filter(roomnr=roomnr).delete()
        Moves.objects.filter(roomnr=roomnr).delete()
        GameStateTemp.objects.create(roomnr=roomnr, playernr=playernr)
        return Response({"ll_piece": GameStateless.dct_ll_piece_init[playernr].copy()})

    except Exception as e:
        print("Error by starten: ", e)
        return Response({"error": "Invalid input"}, status=400)


@api_view(["POST"])
def reset(request):
    """Remove the saved game in db
    Args:
        request: roomnr
    Returns:
        Response: ok
    """
    try:
        roomnr = int(request.data.get("roomnr"))
        game_state1 = GameStateTemp.objects.filter(roomnr=roomnr)
        if game_state1.exists():
            game_state1.delete()
        move1 = Moves.objects.filter(roomnr=roomnr)
        if move1.exists():
            move1.delete()
        return Response({"ok": True})
    except Exception as e:
        print("Error by reset: ", e)
        return Response({"ok": False}, status=400)


@api_view(["POST"])  # DRF handles JSON & CSRF protection
def klicken(request):
    """
    If the player backward to the middle of the game and then click, it should delete the record of previous play to avoid branch
    Args:
        request: roomnr, xr, yr
    Returns:
        Response: ll_piece, turnwise, movenr, selected, valid_pos, win
    """
    try:
        roomnr = int(request.data.get("roomnr"))
        coord_int = (int(request.data.get("xr")), int(request.data.get("yr")))
        GameStateless.click(roomnr, coord_int)

        state = GameStateTemp.objects.get(roomnr=roomnr)
        Moves.objects.filter(roomnr=roomnr, movenr__gt=state.movenr).delete()
        moves = Moves.objects.filter(roomnr=roomnr)

        serializer = SerializerGameState(state)
        dct_response = serializer.data
        dct_response["ll_piece"] = GameStateless.get_ll_piece(state, moves)
        return Response(dct_response)

    except Exception as e:
        print("Error by click: ", e)
        return Response({"error": "Invalid JSON data"}, status=400)


@api_view(["GET"])
def reload_state(request):
    """Search in DB, if exist return
    Args:
        request: roomnr
    Returns:
        Response: ll_piece, turnwise, movenr, selected, valid_pos
    """
    roomnr = int(request.GET.get("roomnr"))
    state = GameStateTemp.objects.filter(roomnr=roomnr).first()
    if not state:
        return Response({"exist": False})
    else:
        moves = Moves.objects.filter(roomnr=roomnr)
        serializer = SerializerGameState(state)
        dct_response = serializer.data
        dct_response["ll_piece"] = game1.get_ll_piece(state, moves)
        dct_response["exist"] = True
        return Response(dct_response)


@api_view(["GET"])
def room_info(request):
    """Return under which roomnr is moves saved
    Returns:
        Response: lst_roomnr"""
    lst_roomnr = list(
        GameStateTemp.objects.values_list("roomnr", flat=True)
    )  # plain list
    lst_roomnr.sort()
    return Response({"lst_roomnr": lst_roomnr})


@api_view(["POST"])
def ward(request):
    """Method for (one step) backward or forward
    Moves are saved in the DB as following: When the player makes the first move, the movenr is 0, so the first move is give a movenr 0. Therefore, if there is a match when Moves in DB is greater or equal to movenr from frontend, it can be forwarded, not only greater
    Args:
        request: roomnr, direction
    Returns:
        Response: moved, ll_piece, turnwise, movenr, selected, valid_pos
    """
    direction = request.data.get("direction")  # true for forward
    roomnr = int(request.data.get("roomnr"))
    try:
        state = GameStateTemp.objects.get(roomnr=roomnr)
    except GameStateTemp.DoesNotExist:
        Response({"moved": False})
    moves = Moves.objects.filter(roomnr=roomnr)
    if direction:
        moves_gt = moves.filter(movenr__gte=state.movenr)
        if moves_gt:
            GameStateTemp.objects.update_or_create(
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
            GameStateTemp.objects.update_or_create(
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
    state2 = GameStateTemp.objects.get(roomnr=roomnr)
    serializer = SerializerGameState(state2)
    dct_response = serializer.data
    dct_response["ll_piece"] = game1.get_ll_piece(state2, moves)
    dct_response["moved"] = True
    return Response(dct_response)
