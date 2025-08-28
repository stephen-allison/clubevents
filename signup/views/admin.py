from django.http import HttpResponse
from django.shortcuts import render

from ..models import Event, Signup


def participants_for_event(request, event_id):
    """Get all users that have signups for a specific event"""
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return HttpResponse("Event not found", status=404)
    
    # Get all signups for this event with related user data
    signups = Signup.objects.filter(event=event).select_related('user').order_by('signup_date')
    
    # Get unique users (in case there are duplicate signups, though shouldn't happen)
    users = []
    seen_users = set()
    
    for signup in signups:
        if signup.user and signup.user.id not in seen_users:
            users.append(signup.user)
            seen_users.add(signup.user.id)
        elif not signup.user:  # Handle signups without user accounts (legacy data)
            # Create a pseudo-user object for display purposes
            class PseudoUser:
                def __init__(self, name, email):
                    self.full_name = name
                    self.email = email
                    self.username = email
                    self.id = None
            
            pseudo_user = PseudoUser(signup.signup_name, signup.signup_email)
            users.append(pseudo_user)
    
    context = {
        'event': event,
        'users': users,
        'participant_count': len(users)
    }
    return render(request, 'signup/participants_for_event.html', context)