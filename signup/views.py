import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.db.models import Prefetch
from django.utils import timezone
import pytz

from .forms import MultiEventSignupForm, CustomUserCreationForm
from .models import Event, Signup, UserProfile

# Create your views here.

def index(request):
    events = Event.objects.all()
    context = {'events': events}
    return render(request, 'signup/index.html', context)


def event(request, event_id):
    event = Event.objects.get(id=event_id)
    return HttpResponse(f'Event {event.name} with id {event_id} is {event}.')



def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('signup:event_list_signups')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'signup/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('signup:event_list_signups')

@login_required
def event_signup(request, event_id):
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
    
    # Check where the request came from to determine redirect
    referer = request.META.get('HTTP_REFERER', '')
    if 'event-signups' in referer:
        return redirect('signup:event_list_signups')
    else:
        return redirect('signup:signups')


@login_required
def hx_event_signup(request, event_id):
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

    context = {'event': event}
    return render(request, 'signup/event_card.html', context)

@login_required
def withdraw_signup(request, signup_id):
    # Get the signup and ensure it belongs to the current user
    signup = Signup.objects.get(id=signup_id, user=request.user)
    signup.delete()
    
    # Check where the request came from to determine redirect
    referer = request.META.get('HTTP_REFERER', '')
    if 'event-signups' in referer:
        return redirect('signup:event_list_signups')
    else:
        return redirect('signup:signups')


@login_required
def hx_withdraw_signup(request, signup_id):
    # Get the signup and ensure it belongs to the current user
    signup = Signup.objects.get(id=signup_id, user=request.user)
    signup.delete()
    event = Event.objects.get(id=signup.event.id)
    context = {'event': event}
    return render(request, 'signup/event_card.html', context)

def event_list_with_signups(request):
    # Get today's date in London timezone
    london_tz = pytz.timezone('Europe/London')
    today = timezone.now().astimezone(london_tz).date()
    
    events = Event.objects.filter(date__gte=today).order_by('date').prefetch_related(
        Prefetch('signup_set', queryset=Signup.objects.order_by('-signup_date', '-id'))
    )
    
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

@login_required
def my_events(request):
    # Get today's date in London timezone
    london_tz = pytz.timezone('Europe/London')
    today = timezone.now().astimezone(london_tz).date()
    
    # Get user's signups for current and future events
    user_signups = Signup.objects.filter(
        user=request.user,
        event__date__gte=today
    ).select_related('event').order_by('event__date')
    
    context = {'signups': user_signups}
    return render(request, 'signup/my_events.html', context)

@login_required
def my_events_ics(request):
    # Get today's date in London timezone
    london_tz = pytz.timezone('Europe/London')
    today = timezone.now().astimezone(london_tz).date()
    
    # Get user's signups for current and future events
    user_signups = Signup.objects.filter(
        user=request.user,
        event__date__gte=today
    ).select_related('event').order_by('event__date')
    
    # Create ICS content
    ics_content = "BEGIN:VCALENDAR\r\n"
    ics_content += "VERSION:2.0\r\n"
    ics_content += "PRODID:-//SignupApp//My Events//EN\r\n"
    ics_content += "CALSCALE:GREGORIAN\r\n"
    
    for signup in user_signups:
        event = signup.event
        # Create a unique ID for each event
        uid = f"event-{event.id}-{request.user.id}@signupapp.local"
        
        ics_content += "BEGIN:VEVENT\r\n"
        ics_content += f"UID:{uid}\r\n"
        ics_content += f"DTSTART;VALUE=DATE:{event.date.strftime('%Y%m%d')}\r\n"
        ics_content += f"SUMMARY:{event.name}\r\n"
        
        # Build description with available information
        description_parts = [f"Signed up on {signup.signup_date}"]
        if event.description:
            description_parts.append(event.description)
        if event.website:
            description_parts.append(f"Website: {event.website}")
        ics_content += f"DESCRIPTION:{' | '.join(description_parts)}\r\n"
        
        # Add location if available
        if event.location:
            ics_content += f"LOCATION:{event.location}\r\n"
            
        # Add URL if available
        if event.website:
            ics_content += f"URL:{event.website}\r\n"
            
        ics_content += "END:VEVENT\r\n"
    
    ics_content += "END:VCALENDAR\r\n"
    
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename="my_events.ics"'
    return response

def calendar_feed(request, uid):
    """Public ICS feed accessible via unique UID"""
    try:
        user_profile = UserProfile.objects.get(calendar_uid=uid)
        user = user_profile.user
    except UserProfile.DoesNotExist:
        return HttpResponse("Invalid calendar link", status=404)
    
    # Get today's date in London timezone
    london_tz = pytz.timezone('Europe/London')
    today = timezone.now().astimezone(london_tz).date()
    
    # Get user's signups for current and future events
    user_signups = Signup.objects.filter(
        user=user,
        event__date__gte=today
    ).select_related('event').order_by('event__date')
    
    # Create ICS content
    ics_content = "BEGIN:VCALENDAR\r\n"
    ics_content += "VERSION:2.0\r\n"
    ics_content += "PRODID:-//SignupApp//My Events//EN\r\n"
    ics_content += "CALSCALE:GREGORIAN\r\n"
    ics_content += f"X-WR-CALNAME:{user.username}'s Events\r\n"
    ics_content += f"X-WR-CALDESC:Events signed up for by {user.username}\r\n"
    
    for signup in user_signups:
        event = signup.event
        # Create a unique ID for each event
        uid_str = f"event-{event.id}-{user.id}@signupapp.local"
        
        ics_content += "BEGIN:VEVENT\r\n"
        ics_content += f"UID:{uid_str}\r\n"
        ics_content += f"DTSTART;VALUE=DATE:{event.date.strftime('%Y%m%d')}\r\n"
        ics_content += f"SUMMARY:{event.name}\r\n"
        
        # Build description with available information
        description_parts = [f"Signed up on {signup.signup_date}"]
        if event.description:
            description_parts.append(event.description)
        if event.website:
            description_parts.append(f"Website: {event.website}")
        ics_content += f"DESCRIPTION:{' | '.join(description_parts)}\r\n"
        
        # Add location if available
        if event.location:
            ics_content += f"LOCATION:{event.location}\r\n"
            
        # Add URL if available
        if event.website:
            ics_content += f"URL:{event.website}\r\n"
            
        ics_content += "END:VEVENT\r\n"
    
    ics_content += "END:VCALENDAR\r\n"
    
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = 'inline; filename="calendar.ics"'
    return response
