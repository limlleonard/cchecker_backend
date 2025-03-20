from django.urls import path
from .consumers import Game1

websocket_urlpatterns = [
    path("ws/game1/", Game1.as_asgi()),
]
