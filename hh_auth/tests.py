from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from .models import HHUser
from .views import get_current_hh_user, get_valid_access_token
from .decorators import hh_authenticated
from .middleware import HHUserMiddleware


def add_session(request):
    """Attach a session to the request object."""
    middleware = SessionMiddleware(lambda r: HttpResponse())
    middleware.process_request(request)
    request.session.save()
    return request


class HHUserModelTests(TestCase):
    def test_is_token_expired_true(self):
        user = HHUser(
            hh_id="1",
            first_name="A",
            last_name="B",
            email="a@example.com",
            access_token="t",
            refresh_token="r",
            expires_at=timezone.now() - timedelta(minutes=5),
        )
        self.assertTrue(user.is_token_expired())

    def test_is_token_expired_false(self):
        user = HHUser(
            hh_id="2",
            first_name="A",
            last_name="B",
            email="a@example.com",
            access_token="t",
            refresh_token="r",
            expires_at=timezone.now() + timedelta(minutes=5),
        )
        self.assertFalse(user.is_token_expired())


class GetCurrentHHUserTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = HHUser.objects.create(
            hh_id="10",
            first_name="John",
            last_name="Doe",
            email="j@example.com",
            access_token="token",
            refresh_token="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def _get_request(self):
        req = self.factory.get("/")
        return add_session(req)

    def test_returns_none_without_user(self):
        request = self._get_request()
        self.assertIsNone(get_current_hh_user(request))

    def test_returns_none_for_invalid_id(self):
        request = self._get_request()
        request.session["hh_user_id"] = "missing"
        self.assertIsNone(get_current_hh_user(request))

    def test_returns_user_for_valid_session(self):
        request = self._get_request()
        request.session["hh_user_id"] = self.user.hh_id
        self.assertEqual(get_current_hh_user(request), self.user)


class GetValidAccessTokenTests(TestCase):
    def setUp(self):
        self.user = HHUser.objects.create(
            hh_id="20",
            first_name="John",
            last_name="Doe",
            email="j@example.com",
            access_token="old",
            refresh_token="refresh",
            expires_at=timezone.now() - timedelta(hours=1),
        )

    def test_no_refresh_when_token_valid(self):
        self.user.expires_at = timezone.now() + timedelta(hours=1)
        self.user.save()
        with patch("hh_auth.views.requests.post") as mocked:
            token = get_valid_access_token(self.user)
            self.assertEqual(token, "old")
            mocked.assert_not_called()

    def test_refresh_when_token_expired(self):
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            "access_token": "new",
            "refresh_token": "new_refresh",
            "expires_in": 3600,
        }
        with patch("hh_auth.views.requests.post", return_value=response_mock) as mocked:
            token = get_valid_access_token(self.user)
            mocked.assert_called_once()
        self.assertEqual(token, "new")
        self.user.refresh_from_db()
        self.assertEqual(self.user.access_token, "new")
        self.assertEqual(self.user.refresh_token, "new_refresh")
        self.assertGreater(self.user.expires_at, timezone.now())


class HHAuthenticatedDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = HHUser.objects.create(
            hh_id="30",
            first_name="John",
            last_name="Doe",
            email="j@example.com",
            access_token="token",
            refresh_token="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def _get_request(self):
        req = self.factory.get("/")
        return add_session(req)

    def test_redirects_when_no_user(self):
        request = self._get_request()
        with patch("hh_auth.decorators.redirect", return_value=HttpResponse(status=302)) as mock_redir:
            @hh_authenticated
            def view(req):
                return HttpResponse("ok")

            response = view(request)
            self.assertEqual(response.status_code, 302)
            mock_redir.assert_called_once_with("hh_login")

    def test_calls_view_when_user_exists(self):
        request = self._get_request()
        request.session["hh_user_id"] = self.user.hh_id

        @hh_authenticated
        def view(req):
            return HttpResponse("ok")

        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")


class HHUserMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = HHUser.objects.create(
            hh_id="40",
            first_name="John",
            last_name="Doe",
            email="j@example.com",
            access_token="token",
            refresh_token="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
        )

    def _get_request(self):
        req = self.factory.get("/")
        return add_session(req)

    def test_middleware_sets_user(self):
        request = self._get_request()
        request.session["hh_user_id"] = self.user.hh_id
        middleware = HHUserMiddleware(lambda r: HttpResponse())
        middleware(request)
        self.assertEqual(request.hh_user, self.user)
