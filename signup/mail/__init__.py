from django.conf import settings
from django.core.mail import send_mail
from django_q import tasks


def send_basic(event_name, event_date, address):
    tasks.async_task('signup.mail._do_send_basic', event_name, event_date, address)

def _do_send_basic(event_name, event_date, address):
    content = f'You signed up for {event_name} at {event_date}'
    send_mail(
        'You registered for an event',
        content,
        settings.DEFAULT_FROM_EMAIL,
    ['steve.allison@clara.co.uk'], fail_silently=False)