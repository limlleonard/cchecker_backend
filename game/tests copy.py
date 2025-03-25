from django.test import TestCase
import unittest
from math import isclose
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from .game import Board, Game
from .models import Game_state
from .views import starten


class Test1(TestCase):
    def test1(self):
        self.assertIs(False, False)


class TestBoard(unittest.TestCase):
    def setUp(self):
        """Initialize Board before each test"""
        self.board = Board()

    def test_board_initialization(self):
        """Test that Board initializes correctly"""
        self.assertIsInstance(self.board.dct_board, dict)
        self.assertGreater(len(self.board.dct_board), 0)  # Ensure board is not empty

    def test_board_coordinates_structure(self):
        """Test if board dictionary contains valid (x, y) coordinates"""
        for key, value in self.board.dct_board.items():
            self.assertIsInstance(key, tuple)
            self.assertEqual(len(key), 3)  # Ensure key has (nr_layer, nr_beam, nr_side)
            self.assertIsInstance(value, tuple)
            self.assertEqual(len(value), 2)  # Ensure value has (x, y) coordinates

    def test_lst_board_generation(self):
        """Ensure lst_board contains correct coordinates from dct_board"""
        expected_list = list(self.board.dct_board.values())
        self.assertEqual(self.board.lst_board, expected_list)

    def test_lst_board_int_rounding(self):
        """Ensure lst_board_int contains rounded coordinates"""
        for original, rounded in zip(self.board.lst_board, self.board.lst_board_int):
            self.assertTrue(isclose(round(original[0]), rounded[0], abs_tol=1e-5))
            self.assertTrue(isclose(round(original[1]), rounded[1], abs_tol=1e-5))


class GameStateTestCase(TestCase):
    def setUp(self):
        """Set up initial test data before each test runs."""
        self.game_state1 = Game_state.objects.create(
            order=1,
            roomnr=100,
            state_players={"player1": "active", "player2": "waiting"},
        )

    def test_game_state_creation(self):
        """Test if a Game_state instance is created correctly."""
        game_state = Game_state.objects.get(roomnr=100)
        self.assertEqual(game_state.order, 1)
        self.assertEqual(
            game_state.state_players, {"player1": "active", "player2": "waiting"}
        )

    def test_roomnr_uniqueness(self):
        """Ensure that roomnr must be unique."""
        with self.assertRaises(
            Exception
        ):  # IntegrityError may occur, but Django wraps it differently
            Game_state.objects.create(order=2, roomnr=100, state_players={})

    def test_json_field_storage(self):
        """Ensure JSONField correctly stores and retrieves data."""
        self.game_state1.state_players = {"player1": "inactive", "player3": "joined"}
        self.game_state1.save()

        updated_game_state = Game_state.objects.get(roomnr=100)
        self.assertEqual(
            updated_game_state.state_players,
            {"player1": "inactive", "player3": "joined"},
        )

    def test_default_empty_json(self):
        """Ensure state_players can handle empty JSON input."""
        game_state2 = Game_state.objects.create(order=2, roomnr=101, state_players={})
        self.assertEqual(game_state2.state_players, {})

    def test_string_representation(self):
        """Check if the string representation is correct."""
        self.assertEqual(str(self.game_state1), f"Game_state {self.game_state1.roomnr}")


class StartenApiTestCase(APITestCase):
    def setUp(self):
        """Set up initial data for testing."""
        self.valid_data = {
            "nrPlayer": 2,
            "roomnr": 101,
        }
        self.invalid_data = {
            "nrPlayer": "invalid",  # Invalid data type
            "roomnr": 101,
        }
        self.roomnr_existing = 102
        self.roomnr_non_existing = 103
        # Setting up the game in dct_game to simulate an existing game
        dct_game = {}
        dct_game[self.roomnr_existing] = Game(nr_player=3, roomnr=self.roomnr_existing)

    def test_start_new_game(self):
        """Test if a new game is started and returned correctly."""
        response = self.client.post("/starten/", self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exist"], False)
        self.assertIn("ll_piece", response.data)  # Ensure ll_piece is returned

    def test_start_existing_game(self):
        """Test if an existing game responds correctly."""
        response = self.client.post(
            "/api/starten/",
            {
                "nrPlayer": 4,
                "roomnr": self.roomnr_existing,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exist"], True)
        self.assertIn("ll_piece", response.data)  # Ensure ll_piece is returned

    def test_invalid_input(self):
        """Test if invalid input returns a 400 error."""
        response = self.client.post("/api/starten/", self.invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid input")

    def test_missing_data(self):
        """Test if missing data returns a 400 error."""
        invalid_data = {
            "nrPlayer": 2,
            # roomnr is missing
        }
        response = self.client.post("/api/starten/", invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid input")
