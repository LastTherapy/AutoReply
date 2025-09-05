from django.shortcuts import render, redirect
import uuid
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
import requests
from hh_auth.decorators import hh_authenticated
from hh_auth.views import get_valid_access_token


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


@hh_authenticated
def api_resumes(request):
    user = request.hh_user
    token = get_valid_access_token(user)
    headers = {
        "Authorization": f"Bearer {token}",
        "HH-User-Agent": settings.HH_USER_AGENT,
    }

    resp = requests.get("https://api.hh.ru/resumes/mine", headers=headers, params={"per_page": 100})
    if resp.status_code != 200:
        return JsonResponse({"error": "failed_to_fetch_resumes"}, status=resp.status_code)

    data = resp.json()
    items = data.get("items", [])
    resumes = []
    for it in items:
        resumes.append({
            "id": it.get("id") or it.get("resume_id"),
            "title": it.get("title") or it.get("name") or "Без названия",
        })

    return JsonResponse({"resumes": resumes})


@hh_authenticated
def api_vacancies(request):
    resume_id = request.GET.get("resume_id")
    if not resume_id:
        return JsonResponse({"error": "resume_id_required"}, status=400)

    user = request.hh_user
    token = get_valid_access_token(user)
    headers = {
        "Authorization": f"Bearer {token}",
        "HH-User-Agent": settings.HH_USER_AGENT,
    }

    url = f"https://api.hh.ru/resumes/{resume_id}/suitable_vacancies"
    resp = requests.get(url, headers=headers, params={"per_page": 50})

    if resp.status_code != 200:
        # Fallback: generic vacancies feed if suitable_vacancies is unavailable
        resp2 = requests.get("https://api.hh.ru/vacancies", headers=headers, params={"per_page": 50})
        if resp2.status_code != 200:
            return JsonResponse({"error": "failed_to_fetch_vacancies"}, status=resp.status_code)
        data = resp2.json()
    else:
        data = resp.json()

    items = data.get("items", [])
    vacancies = []
    for v in items:
        employer = (v.get("employer") or {}).get("name")
        area = (v.get("area") or {}).get("name")
        snippet = (v.get("snippet") or {}).get("requirement") or (v.get("snippet") or {}).get("responsibility") or ""
        vacancies.append({
            "id": v.get("id"),
            "name": v.get("name"),
            "employer": employer,
            "area": area,
            "snippet": snippet,
            "url": v.get("alternate_url") or v.get("url"),
        })

    return JsonResponse({"vacancies": vacancies})


@hh_authenticated
def api_apply_all(request):
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)
    # Placeholder implementation; apply logic can be added later
    return JsonResponse({"status": "ok"})
