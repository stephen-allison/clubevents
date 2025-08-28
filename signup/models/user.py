import hashlib
import datetime
import uuid
from datetime import timezone

from django.conf import settings
from django.contrib.auth.models import AbstractUser, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class ClubUser(AbstractUser):
    '''
    User details
    - ea_urn is the England Athletic code for the user
    - birth_date is needed by event organisers
    - user_uuid is used for user-specific links, e.g. calendars
    '''
    ea_urn = models.CharField(max_length=64, unique=True, editable=False)
    birth_date = models.DateField(null=True, blank=False)
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class PreRegistration(models.Model):
    '''
    Holds data to be bulk-uploaded from club records
    and will be used to pre-populate ClubUser fields when
    someone registers the first time

    ea_urn is England Athletics code
    activated will be set tyo True when someone uses this data to
        qctivate a 'full' account
    '''
    ea_urn = models.CharField(max_length=64, unique=True, editable=True, null=True)
    first_name = models.CharField(max_length=512)
    last_name = models.CharField(max_length=512)
    email = models.EmailField()
    birth_date = models.DateField(null=True, blank=False)
    activated = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name} EA:{self.ea_urn}'


class PendingVerification(models.Model):
    email = models.EmailField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    verified_time = models.DateTimeField(null=True, blank=True)

    @property
    def token(self):
        uuid_str = str(self.uuid)
        tok_str = uuid_str + self.email
        uuid_hash = hashlib.sha256(tok_str.encode('utf-8')).hexdigest()
        return uuid_hash

    def verify(self, candidate_token):
        age = datetime.datetime.now(datetime.timezone.utc) - self.created
        not_too_old = age.total_seconds() <= 4 * 60 * 60
        print(f'verifying token {candidate_token}')
        print(f'age {age}')
        print(f'not_too_old {not_too_old}')
        print(f'token to match {self.token}')
        return not_too_old and (candidate_token == self.token)

    def __str__(self):
        return f'{self.email} {self.created} {self.token}'

class UserProfile(models.Model):
    '''
    UserProfile holds supplementary user data
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
