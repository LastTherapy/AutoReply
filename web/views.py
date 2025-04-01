from django.shortcuts import render, redirect
import uuid
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
import requests


def hh_login(request):
    print(request)
    state = uuid.uuid4().hex
    request.session['oauth_state'] = state
    redirect_uri: str = f'{settings.HOST}/oauth/callback'
    # https://api.hh.ru/openapi/redoc#section/Avtorizaciya
    auth_url: str = (
        f'https://hh.ru/oauth/authorize?response_type=code'
        f'&client_id={settings.HH_CLIENT_ID} '
        f'&state={state}'
        f'&redirect_uri={redirect_uri}'
    )
    return redirect(auth_url)


def hh_callback(request):
    code = request.GET.get('code')
    returned_state = request.GET.get('state')
    session_state = request.session.get('oauth_state')

    if returned_state != session_state:
        return HttpResponseBadRequest("Invalid state")

    # Обмениваем code на access_token
    response = requests.post('https://hh.ru/oauth/token', data={
        'grant_type': 'authorization_code',
        'client_id': 'ВАШ_CLIENT_ID',
        'client_secret': 'ВАШ_CLIENT_SECRET',
        'code': code,
        'redirect_uri': f'{settings.HOST}/oauth/callback'
    })

    if response.status_code != 200:
        return HttpResponseBadRequest("Failed to get access token")

    token_data = response.json()
    access_token = token_data.get('access_token')
    print("Access token: ", access_token)
    # Здесь можно сохранить access_token в БД или сессию
    return JsonResponse(token_data)


def index(request):
    return render(request, 'index.html')
# Create your views here.
