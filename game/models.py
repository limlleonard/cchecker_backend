from django.db import models


class Score(models.Model):
    score = models.IntegerField()
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name}: {self.score}"


class Board(models.Model):
    int1 = models.IntegerField()
    float1 = models.FloatField()


class GameState(models.Model):
    order = models.IntegerField()
    roomnr = models.IntegerField(unique=True)
    state_players = models.JSONField()

    def __str__(self):
        return f"GameState {self.roomnr}"


class GameStateTemp(models.Model):
    selected = models.JSONField(null=True, blank=True)
    valid_pos = models.JSONField(null=True, blank=True)
    order = models.IntegerField()
    roomnr = models.IntegerField(unique=True)
    state_players = models.JSONField()

    def __str__(self):
        return f"GameStateTemp {self.roomnr}"
