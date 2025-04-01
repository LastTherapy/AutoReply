from django.shortcuts import render
import uuid
from datetime import timedelta
from django.shortcuts import redirect
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseBadRequest, HttpResponse
import requests
from .models import HHUser


# Create your views here.
def hh_login(request):
    if request.session.get('hh_user_id'):
        return redirect('web:profile')
    state = uuid.uuid4().hex
    request.session['oauth_state'] = state
    redirect_uri = f'https://{settings.HOST}/oauth/callback'

    auth_url = (
        f'https://hh.ru/oauth/authorize?response_type=code'
        f'&client_id={settings.HH_CLIENT_ID}'
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

    # Обмен code на токен
    token_resp = requests.post('https://hh.ru/oauth/token', data={
        'grant_type': 'authorization_code',
        'client_id': settings.HH_CLIENT_ID,
        'client_secret': settings.HH_CLIENT_SECRET,
        'code': code,
        'redirect_uri': f'https://{settings.HOST}/oauth/callback'
    })

    if token_resp.status_code != 200:
        return HttpResponseBadRequest("Failed to get access token")

    token_data = token_resp.json()
    access_token = token_data['access_token']
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data['expires_in']

    # Получаем info о пользователе
    headers = {
        "Authorization": f"Bearer {access_token}",
        "HH-User-Agent": settings.HH_USER_AGENT,
    }
    user_resp = requests.get("https://api.hh.ru/me", headers=headers)
    if user_resp.status_code != 200:
        return HttpResponse("Failed to get user info", status=401)

    user_info = user_resp.json()

    hh_user, _ = HHUser.objects.update_or_create(
        hh_id=user_info['id'],
        defaults={
            'first_name': user_info.get('first_name', ''),
            'last_name': user_info.get('last_name', ''),
            'email': user_info.get('email'),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': timezone.now() + timedelta(seconds=expires_in),
        }
    )

    request.session['hh_user_id'] = user_info['id']
    return redirect('web:profile')


def get_current_hh_user(request):
    hh_id = request.session.get('hh_user_id')
    if not hh_id:
        return None
    try:
        return HHUser.objects.get(hh_id=hh_id)
    except HHUser.DoesNotExist:
        return None


def get_valid_access_token(hh_user: HHUser):
    if hh_user.expires_at <= timezone.now():
        response = requests.post('https://hh.ru/oauth/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': hh_user.refresh_token,
            'client_id': settings.HH_CLIENT_ID,
            'client_secret': settings.HH_CLIENT_SECRET,
        })

        if response.status_code == 200:
            data = response.json()
            hh_user.access_token = data['access_token']
            hh_user.refresh_token = data.get('refresh_token', hh_user.refresh_token)
            hh_user.expires_at = timezone.now() + timedelta(seconds=data['expires_in'])
            hh_user.save()

    return hh_user.access_token