from rest_framework.test import APITestCase
from rest_framework import status
from .game import GameStateless


class StartenApiTestCase(APITestCase):
    """
    start game, move a few steps
    """

    def setUp(self):
        """Set up initial data for testing."""
        self.game1 = {"nrPlayer": 1, "roomnr": 104}
        self.game2 = {"nrPlayer": 2, "roomnr": 103}
        self.click1 = {"roomnr": self.game2["roomnr"], "xr": 420, "yr": 533}
        self.click2 = {"roomnr": self.game2["roomnr"], "xr": 400, "yr": 499}
        self.click3 = {"roomnr": self.game2["roomnr"], "xr": 320, "yr": 152}
        self.click4 = {"roomnr": self.game2["roomnr"], "xr": 360, "yr": 221}
        self.reload = {"roomnr": self.game2["roomnr"]}
        self.reset = {"roomnr": self.game2["roomnr"]}

    # Initial positions of players
    # [(420, 533), (380, 533), (340, 533), (300, 533), (400, 568), (360, 568), (320, 568), (380, 602), (340, 602), (360, 637)]
    # [(300, 187), (340, 187), (380, 187), (420, 187), (320, 152), (360, 152), (400, 152), (340, 118), (380, 118), (360, 83)]

    def test_start_game_make_move_save(self):
        response_start1 = self.client.post("/starten/", self.game2, format="json")
        self.assertEqual(response_start1.status_code, status.HTTP_200_OK)
        self.assertIn("ll_piece", response_start1.data)
        # print(response_start1.data["ll_piece"])

        response = self.client.get("/room_info/", format="json")
        self.assertIn(self.game2["roomnr"], response.data["lst_roomnr"])

        response_click1 = self.client.post("/klicken/", self.click1, format="json")
        self.assertEqual(response_click1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_click1.data["turnwise"], 0)
        self.assertEqual(response_click1.data["movenr"], 0)
        self.assertEqual(
            response_click1.data["selected"], [self.click1["xr"], self.click1["yr"]]
        )
        self.assertIn(
            [self.click1["xr"], self.click1["yr"]], response_click1.data["valid_pos"]
        )

        response_click2 = self.client.post("/klicken/", self.click2, format="json")
        self.assertEqual(response_click2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_click2.data["turnwise"], 1)
        self.assertEqual(response_click2.data["movenr"], 1)
        self.assertEqual(response_click2.data["selected"], [])
        self.assertEqual(response_click2.data["valid_pos"], [])

        response_click3 = self.client.post("/klicken/", self.click3, format="json")
        self.assertEqual(response_click3.status_code, status.HTTP_200_OK)
        self.assertEqual(response_click3.data["turnwise"], 1)
        self.assertEqual(response_click3.data["movenr"], 1)
        self.assertEqual(
            response_click3.data["selected"], [self.click3["xr"], self.click3["yr"]]
        )
        self.assertEqual(
            response_click3.data["valid_pos"], [[320, 152], [360, 221], [280, 221]]
        )

        response_click4 = self.client.post("/klicken/", self.click4, format="json")
        self.assertEqual(response_click3.status_code, status.HTTP_200_OK)
        for key in "ll_piece, turnwise, movenr, selected, valid_pos, win".split(", "):
            self.assertIn(key, response_click4.data)
        self.assertEqual(response_click4.data["turnwise"], 0)
        self.assertEqual(response_click4.data["movenr"], 2)
        self.assertEqual(response_click4.data["selected"], [])
        self.assertEqual(response_click4.data["valid_pos"], [])

        response_reload = self.client.get("/reload_state/", self.reload, format="json")
        self.assertEqual(response_reload.data["turnwise"], 0)
        self.assertEqual(response_reload.data["movenr"], 2)
        self.assertIn(
            (self.click2["xr"], self.click2["yr"]),
            response_reload.data["ll_piece"][0],
        )
        self.assertIn(
            (self.click4["xr"], self.click4["yr"]),
            response_reload.data["ll_piece"][1],
        )

        response_reset = self.client.post("/reset/", self.reload, format="json")
        self.assertEqual(response_reset.data["ok"], True)
