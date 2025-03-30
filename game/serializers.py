from rest_framework import serializers
from .models import GameState3


class SerializerGameState(serializers.ModelSerializer):
    class Meta:
        model = GameState3
        fields = "__all__"
