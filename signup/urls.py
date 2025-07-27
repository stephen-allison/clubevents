from django.urls import path
from django.contrib.auth.views import LogoutView
from signup import views

app_name = 'signup'
urlpatterns = [
    path('', views.index, name='index'),
    path('event/<int:event_id>', views.event, name='event'),
    path('event/<int:event_id>/signup/', views.event_signup, name='event_signup'),
    path('signup/<int:signup_id>/withdraw/', views.withdraw_signup, name='withdraw_signup'),
    path('event-signups/', views.event_list_with_signups, name='event_list_signups'),
    path('my-events/', views.my_events, name='my_events'),
    path('my-events/calendar.ics', views.my_events_ics, name='my_events_ics'),
    path('calendar/<uuid:uid>.ics', views.calendar_feed, name='calendar_feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='signup:index'), name='logout'),
]
