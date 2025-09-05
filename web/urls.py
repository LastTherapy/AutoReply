from django.urls import path
from .views import profile, index, api_resumes, api_vacancies, api_apply_all

app_name = "web"

urlpatterns = [
    path("", index, name="index"),
    path("profile/", profile, name="profile"),
    # API endpoints
    path("api/resumes/", api_resumes, name="api_resumes"),
    path("api/vacancies/", api_vacancies, name="api_vacancies"),
    path("api/apply-all/", api_apply_all, name="api_apply_all"),
]
