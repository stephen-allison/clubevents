from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Event, Signup, PreRegistration

USER_MODEL = get_user_model()

# Register your models here.
admin.site.register(Event)
admin.site.register(Signup)
admin.site.register(PreRegistration)
admin.site.register(USER_MODEL, UserAdmin)