from django.shortcuts import render
import uuid
from django.conf import settings
from django.shortcuts import redirect


def hh_login(request):
    print(request)
    state = uuid.uuid4().hex
    request.session['oauth_state'] = state
    redirect_uri: str = 'https://work.dobrochan.ru' + '/callback'
    # https://api.hh.ru/openapi/redoc#section/Avtorizaciya
    auth_url: str = (
        f'https://hh.ru/oauth/authorize?response_type=code'
        f'&client_id={settings.HH_CLIENT_ID} '
        f'&state={state}'
        f'&redirect_uri={redirect_uri}'
    )
    return redirect(auth_url)


def hh_callback(request):
    print(request)


def index(request):
    return render(request, 'index.html')
# Create your views here.
