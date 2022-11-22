from django.urls import path
from . import views

urlpatterns = [
    path('reservations_with_prev', views.get_with_previous, name='reservations_with_prev'),
    path('reservations_with_prev_sql', views.get_with_previous_sql, name='reservations_with_prev_sql'),
]
