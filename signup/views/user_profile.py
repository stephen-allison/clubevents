from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.utils import timezone
import pytz

from ..models import Signup


@login_required
def my_details(request):
    """Show user's profile details"""
    context = {
        'user': request.user
    }
    return render(request, 'signup/my_details.html', context)


@login_required
@never_cache
def my_events(request):
    # Get today's date in London timezone
    london_tz = pytz.timezone('Europe/London')
    today = timezone.now().astimezone(london_tz).date()
    
    # Get user's signups for current and future events
    user_signups = Signup.objects.filter(
        user=request.user,
        event__date__gte=today
    ).select_related('event').order_by('event__date')
    
    # Detect webcal support based on user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    supports_webcal = (
        'iphone' in user_agent or 
        'ipad' in user_agent or 
        'macintosh' in user_agent or
        'mac os x' in user_agent
    )
    
    context = {
        'signups': user_signups,
        'supports_webcal': supports_webcal,
        'user_agent': user_agent
    }
    return render(request, 'signup/my_events.html', context)