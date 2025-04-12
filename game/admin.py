from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(GameStateEnd)
admin.site.register(GameStateTemp)
admin.site.register(Moves)
