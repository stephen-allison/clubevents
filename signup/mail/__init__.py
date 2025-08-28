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
    [address], fail_silently=False)


def send_email_verification(to_address, link):
    content = f'Click the following link to verify your email: {link}'
    tasks.async_task('signup.mail._do_send_email_verification', to_address, content)

def _do_send_email_verification(to_address, content):
    print(settings.DEFAULT_FROM_EMAIL)
    send_mail(
        'Verify your email',
        content,
        settings.DEFAULT_FROM_EMAIL,
        [to_address])

