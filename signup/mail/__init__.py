from django.conf import settings
from django.core.mail import send_mail
from django_q import tasks


def send_basic(event_name, event_date, address):
    tasks.async_task('signup.mail._do_send_basic', event_name, event_date, address)

def _do_send_basic(event_name, event_date, address):
    content = f'''
    You've signed up for the following event:
    
    {event_name} taking place on {event_date}
    
    If you can't attend please use the 'withdraw' button on the web site.
    
    Thanks!
    
    The QPH team.
    '''
    send_mail(
        'You registered for an event',
        content,
        settings.DEFAULT_FROM_EMAIL,
    [address], fail_silently=False)


def send_email_verification(to_address, link):
    content = f'''
    Hi! You're registering with the QPH events website. 
    The next step is to verify your email by clicking the link below.  
    
    When you've done that return to the site to continue.
    
    {link}
    
    Thanks!
    
    The QPH team.
    '''

    tasks.async_task('signup.mail._do_send_email_verification', to_address, content)

def _do_send_email_verification(to_address, content):
    print(settings.DEFAULT_FROM_EMAIL)
    send_mail(
        'Verify your email',
        content,
        settings.DEFAULT_FROM_EMAIL,
        [to_address])

