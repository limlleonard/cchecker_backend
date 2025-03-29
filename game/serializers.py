from rest_framework import serializers
from .models import Score, GameState3


class SerializerScore(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = "__all__"


class SerializerGameState(serializers.ModelSerializer):
    extra_var = serializers.SerializerMethodField()  # Custom field

    class Meta:
        model = GameState3
        fields = [
            "roomnr",
            "playernr",
            "turnwise",
            "movenr",
            "selected",
            "valid_pos",
            "extra_var",
        ]

    def get_extra_var(self, obj):
        # Define the extra variable logic here
        return "This is an extra value"  # Example static value
