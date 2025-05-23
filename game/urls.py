from django.urls import path  # , include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("return_board/", views.return_board, name="return_board"),
    path("starten/", views.starten, name="starten"),
    path("reset/", views.reset, name="reset"),
    path("klicken/", views.klicken, name="klicken"),
    path("reload_state/", views.reload_state, name="reload_state"),
    path("room_info/", views.room_info, name="room_info"),
    path("ward/", views.ward, name="ward"),
]
