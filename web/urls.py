from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.index, name="index"),
    path('oauth/login', views.hh_login, name='hh_login'),
    path("oauth/callback", views.hh_callback),
]