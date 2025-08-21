from django.urls import path
from django.contrib.auth.views import LogoutView
from signup import views

app_name = 'signup'
urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='index'),
    path('signuphx/<int:event_id>/signup/', views.hx_event_signup, name='hx_event_signup'),
    path('signuphx/<int:signup_id>/withdraw/', views.hx_withdraw_signup, name='hx_withdraw_signup'),
    path('event-signups/', views.event_list_with_signups, name='event_list_signups'),
    path('my-events/', views.my_events, name='my_events'),
    path('my-events/calendar.ics', views.my_events_ics, name='my_events_ics'),
    path('calendar/<uuid:uid>.ics', views.calendar_feed, name='calendar_feed'),
    path('activate/', views.ea_urn_lookup_view, name='activate'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='signup:login'), name='logout'),
    path('register/<str:ea_urn>/', views.register_with_preregistration_view, name='register_with_preregistration'),
]
