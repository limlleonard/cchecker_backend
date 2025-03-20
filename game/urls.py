from django.urls import path  # , include

# from rest_framework import routers # Class viewers
from . import views

# router = routers.DefaultRouter()
# router.register(r'score', views.ViewsetScore)

urlpatterns = [
    # path("", views.home, name="home"),
    path("return_board/", views.return_board, name="return_board"),
    path("starten/", views.starten, name="starten"),
    path("reset/", views.reset, name="reset"),
    path("klicken/", views.klicken, name="klicken"),
    # path("return_score/", views.return_score, name="return_score"),
    # path('api/', include(router.urls)),
    # path('api/add_score/', views.ViewsetScore.as_view({'post': 'add_score'})),
    path("get_score/", views.get_score, name="get_score"),
    path("add_score/", views.add_score, name="add_score"),
    path("save_state/", views.save_state, name="save_state"),
    path("reload_state/", views.reload_state, name="reload_state"),
    path("backend_info/", views.backend_info, name="backend_info"),
]
