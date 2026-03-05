import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.urls import reverse

from user import views


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def make_request(method="GET", post_data=None, session_data=None):
    """
    Crea un oggetto request con sessione simulata.
    """
    factory = RequestFactory()

    if method == "POST":
        request = factory.post("/user/dashboard/", data=post_data or {})
    else:
        request = factory.get("/user/dashboard/")

    session = {}
    if session_data:
        session.update(session_data)
    request.session = session

    return request


# ──────────────────────────────────────────────
# TEST: get_user
# ──────────────────────────────────────────────

class TestGetUser:
    def test_get_user_no_session(self):
        request = make_request(session_data={})
        result = views.get_user(request)
        assert result is None

    @patch("user.views.MyUser.objects")
    def test_get_user_found(self, mock_objects):
        fake_user = MagicMock()
        fake_user.id = 42
        mock_objects.filter.return_value.first.return_value = fake_user
        request = make_request(session_data={"id_user": 42})
        result = views.get_user(request)
        assert result == fake_user
        mock_objects.filter.assert_called_once_with(id=42)

    @patch("user.views.MyUser.objects")
    def test_get_user_not_found(self, mock_objects):
        mock_objects.filter.return_value.first.return_value = None
        request = make_request(session_data={"id_user": 99})
        result = views.get_user(request)
        assert result is None


# ──────────────────────────────────────────────
# TEST: logout
# ──────────────────────────────────────────────

class TestLogout:
    def test_logout_flushes_session_and_redirects(self):
        request = make_request(session_data={"id_user": 1})
        mock_session = MagicMock()
        request.session = mock_session
        response = views.logout(request)
        mock_session.flush.assert_called_once()
        assert response.status_code == 302
        assert response["Location"] == reverse("index")


# ──────────────────────────────────────────────
# TEST: update_user
# ──────────────────────────────────────────────

class TestUpdateUser:
    def test_update_user_no_session(self):
        request = make_request(method="POST", session_data={})
        result = views.update_user(request)
        assert "error" in result

    @patch("user.views.get_object_or_404")
    def test_update_user_all_fields(self, mock_get_obj):
        fake_user = MagicMock()
        mock_get_obj.return_value = fake_user
        request = make_request(
            method="POST",
            post_data={"name": "Mario", "surname": "Rossi", "email": "m@r.it"},
            session_data={"id_user": 1}
        )
        result = views.update_user(request)
        assert result["success"] == "User updated correctly."
        assert fake_user.name == "Mario"
        assert fake_user.surname == "Rossi"
        assert fake_user.email == "m@r.it"
        fake_user.save.assert_called_once()


# ──────────────────────────────────────────────
# TEST: View redirection (Auth)
# ──────────────────────────────────────────────

class TestAuthRedirection:
    """Verifica che le view reindirizzino se l'utente non è loggato."""
    
    @pytest.mark.parametrize("view_func", [
        views.dashboard_view,
        views.file_manager_view,
        views.upload_center_view,
        views.semantic_search_view,
        views.notifications_view
    ])
    def test_views_redirect_unauthenticated(self, view_func):
        request = make_request(session_data={}) # Nessun id_user
        response = view_func(request)
        assert response.status_code == 302
        assert response["Location"] == reverse("index")


# ──────────────────────────────────────────────
# TEST: dashboard_view
# ──────────────────────────────────────────────

class TestDashboardView:
    @patch("user.views.get_documents_by_user")
    @patch("user.views.get_user")
    def test_dashboard_renders(self, mock_get_user, mock_get_docs):
        mock_get_user.return_value = MagicMock(id=1, name="Mario")
        mock_get_docs.return_value = MagicMock()
        
        request = make_request(session_data={"id_user": 1})
        response = views.dashboard_view(request)
        
        assert response.status_code == 200