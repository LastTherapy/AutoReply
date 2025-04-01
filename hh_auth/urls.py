from django.urls import path
from hh_auth.views import hh_login, hh_callback

app_name = "hh_auth"

urlpatterns = [
    path('login/', hh_login, name='hh_login'),
    path('callback/', hh_callback, name='hh_callback'),
]
