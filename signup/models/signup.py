from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from signup.models import Event


class Signup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    signup_name = models.CharField(max_length=512)
    signup_email = models.EmailField()
    signup_date = models.DateField()

    def __str__(self):
        return f'{self.signup_name} ({self.signup_email}) signed up for {self.event.name} on {self.event.date}'
