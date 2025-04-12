from rest_framework import serializers
from .models import GameStateTemp


class SerializerGameState(serializers.ModelSerializer):
    class Meta:
        model = GameStateTemp
        fields = "__all__"
