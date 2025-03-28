from rest_framework.test import APITestCase
from rest_framework import status
from .game import Game
from .views import dct_game


class StartenApiTestCase(APITestCase):
    """
    save a game, start a game
    """

    def setUp(self):
        """Set up initial data for testing."""
        self.game_valid = {"nrPlayer": 1, "roomnr": 104}
        self.game_invalid = {"nrPlayer": 2, "roomnr": "invalid roomnr"}
        self.game_setup = {"nrPlayer": 2, "roomnr": 103}
        self.click1 = {
            "roomnr": self.game_setup["roomnr"],
            "xr": 420,
            "yr": 533,
        }
        self.click2 = {
            "roomnr": self.game_setup["roomnr"],
            "xr": 400,
            "yr": 499,
        }
        dct_game[self.game_setup["roomnr"]] = Game(
            nr_player=self.game_setup["nrPlayer"], roomnr=self.game_setup["roomnr"]
        )

    def test_start_new_game(self):
        """Test if a new game is started and returned correctly."""
        response = self.client.post("/starten/", self.game_valid, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exist"], False)
        self.assertIn("ll_piece", response.data)
        # print(response.data["ll_piece"])
        # Initial positions of players
        # [(420, 533), (380, 533), (340, 533), (300, 533), (400, 568), (360, 568), (320, 568), (380, 602), (340, 602), (360, 637)]

    def test_start_old_game(self):
        """Test if an old game is started and returned correctly."""
        response = self.client.post("/starten/", self.game_valid, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["exist"], True)
        self.assertIn("ll_piece", response.data)

    # def test_invalid_input(self):
    #     """Test if invalid input returns a 400 error."""
    #     response = self.client.post("/starten/", self.game_invalid, format="json")
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("error", response.data)

    def test_get_info(self):
        response = self.client.get("/room_info/", format="json")
        print(response.data)
        self.assertIsNotNone(response.data)
        # self.assertIn("lst_roomnr_taken", response.data)
        # self.assertIn(self.game_setup["roomnr"], response.data["lst_roomnr_taken"])

    def test_start_game_make_move_save(self):
        response_start1 = self.client.post("/starten/", self.game_setup, format="json")
        self.assertEqual(response_start1.status_code, status.HTTP_200_OK)

        response_click1 = self.client.post("/klicken/", self.click1, format="json")
        self.assertEqual(response_click1.status_code, status.HTTP_200_OK)
        for key in ["selected", "validPos", "neueFiguren", "order", "gewonnen"]:
            self.assertIn(key, response_click1.data)

        response_click2 = self.client.post("/klicken/", self.click2, format="json")
        self.assertEqual(response_click2.status_code, status.HTTP_200_OK)
        for key in ["selected", "validPos", "neueFiguren", "order", "gewonnen"]:
            self.assertIn(key, response_click2.data)

        response_save1 = self.client.post(
            "/save_state/", {"roomnr": self.game_setup["roomnr"]}, format="json"
        )
        self.assertEqual(response_save1.status_code, status.HTTP_201_CREATED)

        response_reload1 = self.client.get(
            "/reload_state/", {"roomnr": self.game_setup["roomnr"]}
        )
        # print(response_reload1.data)


# class BackendInfoTestCase(APITestCase):
#     def setUp(self):
#         self.test1 = None

#     def test_get_info(self):
#         response = self.client.get("/backend_info/", format="json")
#         self.assertIsNotNone(response)
#         # print(response.data)


# class KlickenTestCase(APITestCase):
#     def setUp(self):
#         self.roomnr1 = 101
#         dct_game[self.roomnr1] = Game(nr_player=1, roomnr=self.roomnr1)
#         self.click1 = {
#             "roomnr": self.roomnr1,
#             "xr": 420,
#             "yr": 533,
#         }
#         self.click2 = {
#             "roomnr": self.roomnr1,
#             "xr": 400,
#             "yr": 499,
#         }

#     def test_click_on_piece(self):
#         """Click on a piece"""
#         response1 = self.client.post("/klicken/", self.click1, format="json")
#         self.assertEqual(response1.status_code, status.HTTP_200_OK)
#         for key in ["selected", "validPos", "neueFiguren", "order", "gewonnen"]:
#             self.assertIn(key, response1.data)
#         # print(response1.data)

#         response2 = self.client.post("/klicken/", self.click2, format="json")
#         self.assertEqual(response2.status_code, status.HTTP_200_OK)
#         for key in ["selected", "validPos", "neueFiguren", "order", "gewonnen"]:
#             self.assertIn(key, response2.data)
#         # print(response2.data)
