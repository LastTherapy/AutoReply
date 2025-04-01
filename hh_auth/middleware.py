from .views import get_current_hh_user


class HHUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.hh_user = get_current_hh_user(request)
        response = self.get_response(request)
        return response
