from django.urls import path
from signup import views

app_name = 'signup'
urlpatterns = [
    path('', views.index, name='index'),
    path('event/<int:event_id>', views.event, name='event'),
    path('events', views.all_events, name='all_events'),
]