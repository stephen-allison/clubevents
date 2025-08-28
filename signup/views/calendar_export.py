from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import pytz

from ..models import Signup
from ..models.user import UserProfile


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