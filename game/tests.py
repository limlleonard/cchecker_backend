from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .game import Game
from .views import dct_game


class StartenApiTestCase(APITestCase):
    def setUp(self):
        """Set up initial data for testing."""
        self.valid_data = {
            "nrPlayer": 1,
            "roomnr": 104,
        }
        self.invalid_data = {
            "nrPlayer": 2,
            "roomnr": "invalid roomnr",
        }
        self.roomnr_existing = 103
        self.nr_player_existing = 3
        dct_game[self.roomnr_existing] = Game(
            nr_player=self.nr_player_existing, roomnr=self.roomnr_existing
        )

    def test_start_new_game(self):
        """Test if a new game is started and returned correctly."""
        url = reverse("starten")
        response = self.client.post(url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exist"], False)
        self.assertIn("ll_piece", response.data)
        # print(response.data["ll_piece"])
        # Initial positions of players
        # [(420, 533), (380, 533), (340, 533), (300, 533), (400, 568), (360, 568), (320, 568), (380, 602), (340, 602), (360, 637)]

    def test_start_old_game(self):
        """Test if an old game is started and returned correctly."""
        response = self.client.post("/starten/", self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exist"], True)
        self.assertIn("ll_piece", response.data)

    def test_invalid_input(self):
        """Test if invalid input returns a 400 error."""
        response = self.client.post("/starten/", self.invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class KlickenTestCase(APITestCase):
    def setUp(self):
        self.roomnr1 = 101
        dct_game[self.roomnr1] = Game(nr_player=1, roomnr=self.roomnr1)
        self.click1 = {
            "roomnr": self.roomnr1,
            "xr": 420,
            "yr": 533,
        }
        self.click2 = {
            "roomnr": self.roomnr1,
            "xr": 400,
            "yr": 499,
        }

    def test_click_on_piece(self):
        """Click on a piece"""
        response1 = self.client.post("/klicken/", self.click1, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        for key in ["selected", "validPos", "neueFiguren", "order", "gewonnen"]:
            self.assertIn(key, response1.data)
        print(response1.data)

        response2 = self.client.post("/klicken/", self.click2, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        for key in ["selected", "validPos", "neueFiguren", "order", "gewonnen"]:
            self.assertIn(key, response2.data)
        print(response2.data)
