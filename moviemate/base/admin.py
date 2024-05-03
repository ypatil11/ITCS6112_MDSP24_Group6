from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(MovieGoer)
admin.site.register(MoviePreferences)
admin.site.register(SeatPreferences)