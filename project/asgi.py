import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

# Load Django application first to initialize settings
django_asgi_app = get_asgi_application()


# Import routing inside a function to avoid premature access
def get_application():
    from game.routing import websocket_urlpatterns  # Lazy import

    return ProtocolTypeRouter(
        {
            "http": django_asgi_app,
            "websocket": URLRouter(websocket_urlpatterns),
        }
    )


application = get_application()

# from game.routing import websocket_urlpatterns
# application = ProtocolTypeRouter(
#     {
#         "http": get_asgi_application(),
#         "websocket": URLRouter(websocket_urlpatterns),
#     }
# )
# # application = get_asgi_application()
