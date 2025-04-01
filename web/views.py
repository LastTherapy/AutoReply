from django.shortcuts import render, redirect
import uuid
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
import requests


def index(request):
    return render(request, 'index.html')
# Create your views here.


def profile(request):
    user = request.hh_user
    if not user:
        return redirect('hh_auth:hh_login')

    return render(request, 'profile.html', {
        'user': user
    })

