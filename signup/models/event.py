from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=512)
    date = models.DateField()
    signup_cutoff = models.DateTimeField(null=True, blank=True, help_text="Deadline for signups")
    description = models.TextField(blank=True, help_text="Event description")
    website = models.URLField(blank=True, help_text="Event website")
    location = models.CharField(max_length=512, blank=True, help_text="Event location")
    geo = models.CharField(max_length=100, blank=True, help_text="Coordinates (lat,lng) for mapping")
    organiser_email = models.EmailField(blank=True, help_text="Organiser email")
    reminder_email_sent = models.BooleanField(default=False)
    participants_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.date.isoformat()})'
