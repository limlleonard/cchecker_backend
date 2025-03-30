import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs


class Game1(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope["query_string"].decode())
        self.roomnr = query_params.get("roomnr", [None])[0]
        print(f"connect, {self.roomnr}")
        await self.channel_layer.group_add(self.roomnr, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f"disconnect, {self.roomnr}")
        # if int(self.roomnr) in dct_game:
        #     del dct_game[int(self.roomnr)]
        await self.channel_layer.group_discard(self.roomnr, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # print("received", data)
        await self.channel_layer.group_send(
            self.roomnr, {"type": "piece_update", "data": data}
        )

    async def piece_update(self, event):
        # print("sent: ", event["data"])
        await self.send(text_data=json.dumps(event["data"]))
