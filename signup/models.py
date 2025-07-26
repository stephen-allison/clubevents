from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=512)
    date = models.DateField()

    def __str__(self):
        return f'{self.name} ({self.date.isoformat()})'

class Signup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    signup_name = models.CharField(max_length=512)
    signup_email = models.EmailField()
    signup_date = models.DateField()

    def __str__(self):
        return f'{self.signup_name} ({self.signup_email}) signed up for {self.event.name} on {self.event.date}'
