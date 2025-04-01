from django.urls import path
from .views import profile, index

app_name = "web"

urlpatterns = [
    path("", index, name="index"),
    path("profile/", profile, name="profile"),
]