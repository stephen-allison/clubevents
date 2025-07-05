from django.shortcuts import render
from django.http import HttpResponse
from .models import Event
# Create your views here.

def index(request):
    events = Event.objects.all()
    context = {'events': events}
    return render(request, 'signup/index.html', context)

def event(request, event_id):
    event = Event.objects.get(id=event_id)
    return HttpResponse(f'Event {event.name} with id {event_id} is {event}.')

def all_events(request):
    events = Event.objects.all()
    response = [str(e) for e in events]
    return HttpResponse('<br/>'.join(response))

