from django.db import models


class Score(models.Model):
    score = models.IntegerField()
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}: {self.score}"


class GameState(models.Model):
    turnwise = models.IntegerField()
    roomnr = models.IntegerField(unique=True)
    state_players = models.JSONField()

    def __str__(self):
        return f"GameState {self.roomnr}"


class GameState3(models.Model):
    roomnr = models.IntegerField(unique=True)
    playernr = models.IntegerField(default=1)
    turnwise = models.IntegerField(default=0)
    movenr = models.IntegerField(default=0)
    selected = models.JSONField(null=True, blank=True, default=None)
    valid_pos = models.JSONField(null=True, blank=True, default=None)

    def __str__(self):
        return f"GameStateTemp {self.roomnr}"


class Moves1(models.Model):
    roomnr = models.IntegerField()
    movenr = models.IntegerField(default=0)
    coord_from = models.JSONField()
    coord_to = models.JSONField()

    def __str__(self):
        return f"Move - {self.roomnr} - {self.movenr}"


def get_ll_pieces(roomnr, movenr, game1):
    state = GameState3.objects.get(roomnr=roomnr)
    moves = Moves1.objects.filter(roomnr=roomnr)
    ll_pieces = game1.init_state(state.playernr)
    for movenr in range(state.movenr):
        move1 = moves.filter(movenr=movenr).first()
        for lst_pieces in ll_pieces:
            if tuple(move1.coord_from) in lst_pieces:
                index_from = lst_pieces.index(tuple(move1.coord_from))
                lst_pieces.pop(index_from)
                lst_pieces.append(tuple(move1.coord_to))
    return ll_pieces
