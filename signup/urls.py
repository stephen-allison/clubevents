from django.urls import path
from django.contrib.auth.views import LogoutView
from signup import views

app_name = 'signup'
urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='index'),
    path('signuphx/<int:event_id>/signup/', views.hx_event_signup, name='hx_event_signup'),
    path('signuphx/<int:signup_id>/withdraw/', views.hx_withdraw_signup, name='hx_withdraw_signup'),
    path('event-signups/', views.event_list_with_signups, name='event_list_signups'),
    path('my-details/', views.my_details, name='my_details'),
    path('my-events/', views.my_events, name='my_events'),
    path('my-events/calendar.ics', views.my_events_ics, name='my_events_ics'),
    path('calendar/<uuid:uid>.ics', views.calendar_feed, name='calendar_feed'),
    path('event/<int:event_id>/participants/', views.participants_for_event, name='participants_for_event'),
    path('activateemail/', views.ea_email_lookup_view, name='activate_email'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='signup:login'), name='logout'),
    path('register_with_email/<str:token>/<str:ea_email>/', views.register_with_preregistration_view_email, name='register_with_preregistration_email'),
    path('register_submit/', views.register_form_submit, name='register_form_submit'),
    path('email_verified/<str:token>/<str:ea_email>/', views.verify_email_finish, name='email_verified'),
    path('check_email_verification/<str:email>/', views.check_email_verification, name='check_email_verification')
]
