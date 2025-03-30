from django.db import models


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
    selected = models.JSONField(default=list)
    valid_pos = models.JSONField(default=list)
    win = models.IntegerField(default=0)

    def __str__(self):
        return f"GameStateTemp {self.roomnr}"


class Moves1(models.Model):
    roomnr = models.IntegerField()
    movenr = models.IntegerField(default=0)
    coord_from = models.JSONField()
    coord_to = models.JSONField()

    def __str__(self):
        return f"Move - {self.roomnr} - {self.movenr}"
