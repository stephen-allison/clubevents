import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy

from ..models import Event, Signup
import signup.mail as mail


def hx_event_signup(request, event_id):
    if not request.user.is_authenticated:
        redirect_to = reverse_lazy('signup:login')
        print(f'not logged in , redirecting to {redirect_to}')
        response = HttpResponse('Unauthorized', status=401)
        response['HX-Redirect'] = redirect_to
        return response

    event = Event.objects.get(id=event_id)
    # Use get_or_create to prevent duplicates atomically
    signup, created = Signup.objects.get_or_create(
        user=request.user,
        event=event,
        defaults={
            'signup_name': request.user.get_full_name() or request.user.username,
            'signup_email': request.user.email,
            'signup_date': datetime.date.today()
        }
    )
    print(signup, created)
    event.user_signup = signup

    mail.send_basic(event.name, event.date, request.user.email)

    context = {'event': event}
    return render(request, 'signup/event_card2.html', context)


def hx_withdraw_signup(request, signup_id):
    if not request.user.is_authenticated:
        redirect_to = reverse_lazy('signup:login')
        print(f'not logged in , redirecting to {redirect_to}')
        response = HttpResponse('Unauthorized', status=401)
        response['HX-Redirect'] = redirect_to
        return response
    # Get the signup and ensure it belongs to the current user
    signup = Signup.objects.get(id=signup_id, user=request.user)
    signup.delete()
    event = Event.objects.get(id=signup.event.id)
    context = {'event': event}
    return render(request, 'signup/event_card2.html', context)