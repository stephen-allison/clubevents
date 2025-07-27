from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=512)
    date = models.DateField()
    signup_cutoff = models.DateTimeField(null=True, blank=True, help_text="Deadline for signups")
    description = models.TextField(blank=True, help_text="Event description")
    website = models.URLField(blank=True, help_text="Event website")
    location = models.CharField(max_length=512, blank=True, help_text="Event location")
    geo = models.CharField(max_length=100, blank=True, help_text="Coordinates (lat,lng) for mapping")

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

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calendar_uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
    else:
        UserProfile.objects.create(user=instance)
