from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .repositories import ReservationsRepo

# Create your views here.
def get_with_previous(request):
    return JsonResponse(ReservationsRepo().get_with_previous(), safe = False)

def get_with_previous_sql(request):
    return JsonResponse(ReservationsRepo().get_with_previous_sql(), safe = False)