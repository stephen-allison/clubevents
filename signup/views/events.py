from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.db.models import Prefetch
from django.utils import timezone
import pytz

from ..models import Event, Signup


def index(request):
    events = Event.objects.all()
    context = {'events': events}
    return render(request, 'signup/index.html', context)


def event(request, event_id):
    event = Event.objects.get(id=event_id)
    return HttpResponse(f'Event {event.name} with id {event_id} is {event}.')


@never_cache
def event_list_with_signups(request):
    # Get today's date in London timezone
    london_tz = pytz.timezone('Europe/London')
    today = timezone.now().astimezone(london_tz).date()
    
    events = Event.objects.filter(date__gte=today).order_by('date').prefetch_related(
        Prefetch('signup_set', queryset=Signup.objects.order_by('-signup_date', '-id'))
    )

    print(f'user is authenticated? {request.user.is_authenticated}')

    # Add user signup info and cutoff status to each event if authenticated
    if request.user.is_authenticated:
        user_signups = Signup.objects.filter(user=request.user).select_related('event')
        user_signup_map = {signup.event_id: signup for signup in user_signups}
        
        # Get current time in London timezone for cutoff comparison
        london_tz = pytz.timezone('Europe/London')
        now = timezone.now().astimezone(london_tz)
        
        for event in events:
            event.user_signup = user_signup_map.get(event.id)
            # Check if signup cutoff has passed
            if event.signup_cutoff:
                event.signup_closed = now > event.signup_cutoff.astimezone(london_tz)
            else:
                event.signup_closed = False
    
    context = {'events': events}
    return render(request, 'signup/event_list_signups.html', context)