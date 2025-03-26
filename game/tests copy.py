from django.test import TestCase
from .models import GameState


class Test1(TestCase):
    def test1(self):
        self.assertIs(False, False)


class GameStateTestCase(TestCase):
    def setUp(self):
        """Set up initial test data before each test runs."""
        self.game_state1 = GameState.objects.create(
            order=1,
            roomnr=100,
            state_players={"player1": "active", "player2": "waiting"},
        )

    def test_game_state_creation(self):
        """Test if a Game_state instance is created correctly."""
        game_state = GameState.objects.get(roomnr=100)
        self.assertEqual(game_state.order, 1)
        self.assertEqual(
            game_state.state_players, {"player1": "active", "player2": "waiting"}
        )

    def test_roomnr_uniqueness(self):
        """Ensure that roomnr must be unique."""
        with self.assertRaises(
            Exception
        ):  # IntegrityError may occur, but Django wraps it differently
            GameState.objects.create(order=2, roomnr=100, state_players={})

    def test_json_field_storage(self):
        """Ensure JSONField correctly stores and retrieves data."""
        self.game_state1.state_players = {"player1": "inactive", "player3": "joined"}
        self.game_state1.save()

        updated_game_state = GameState.objects.get(roomnr=100)
        self.assertEqual(
            updated_game_state.state_players,
            {"player1": "inactive", "player3": "joined"},
        )

    def test_default_empty_json(self):
        """Ensure state_players can handle empty JSON input."""
        game_state2 = GameState.objects.create(order=2, roomnr=101, state_players={})
        self.assertEqual(game_state2.state_players, {})

    def test_string_representation(self):
        """Check if the string representation is correct."""
        self.assertEqual(str(self.game_state1), f"Game_state {self.game_state1.roomnr}")
