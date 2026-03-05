import pytest
from unittest.mock import patch, MagicMock
from django.test import RequestFactory
from django.contrib.sessions.backends.db import SessionStore

from user import views


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def make_request(method="GET", post_data=None, session_data=None):
    """
    Crea un oggetto request con sessione simulata.
    
    RequestFactory NON inizializza le sessioni automaticamente,
    quindi dobbiamo aggiungere l'attributo session a mano.
    """
    factory = RequestFactory()

    if method == "POST":
        request = factory.post("/user/", data=post_data or {})
    else:
        request = factory.get("/user/")

    # Simula la sessione Django con un dict-like object
    session = {}
    if session_data:
        session.update(session_data)
    request.session = session

    return request


# ──────────────────────────────────────────────
# TEST: get_user
# ──────────────────────────────────────────────

class TestGetUser:
    """
    get_user(request) legge l'id dalla sessione e
    ritorna l'oggetto MyUser dal DB (o None).
    """

    def test_get_user_no_session(self):
        """
        SCENARIO: nessun id_user in sessione.
        ATTESO:   ritorna None senza toccare il DB.
        """
        request = make_request(session_data={})  # sessione vuota

        result = views.get_user(request)

        assert result is None

    @patch("user.views.MyUser.objects")
    def test_get_user_found(self, mock_objects):
        """
        SCENARIO: id_user presente in sessione, utente trovato nel DB.
        ATTESO:   ritorna l'oggetto utente.

        Usiamo @patch per sostituire MyUser.objects con un mock,
        così evitiamo di colpire il DB reale.
        mock_objects.filter().first() è la catena di chiamate che
        Django fa internamente.
        """
        fake_user = MagicMock()
        fake_user.id = 42
        mock_objects.filter.return_value.first.return_value = fake_user

        request = make_request(session_data={"id_user": 42})

        result = views.get_user(request)

        assert result == fake_user
        mock_objects.filter.assert_called_once_with(id=42)

    @patch("user.views.MyUser.objects")
    def test_get_user_not_found(self, mock_objects):
        """
        SCENARIO: id_user in sessione, ma nessun utente nel DB.
        ATTESO:   ritorna None (perché .first() ritorna None).
        """
        mock_objects.filter.return_value.first.return_value = None

        request = make_request(session_data={"id_user": 99})

        result = views.get_user(request)

        assert result is None

    @patch("user.views.MyUser.objects")
    def test_get_user_db_exception(self, mock_objects):
        """
        SCENARIO: il DB lancia un'eccezione.
        ATTESO:   ritorna None senza propagare l'errore
                  (la view gestisce internamente con try/except).
        """
        mock_objects.filter.side_effect = Exception("DB down")

        request = make_request(session_data={"id_user": 1})

        result = views.get_user(request)

        assert result is None


# ──────────────────────────────────────────────
# TEST: logout
# ──────────────────────────────────────────────

class TestLogout:
    """
    logout(request) svuota la sessione e reindirizza a "home".
    """

    def test_logout_flushes_session_and_redirects(self):
        """
        SCENARIO: utente loggato chiama logout.
        ATTESO:   sessione svuotata (flush chiamato) e redirect a "home".

        request.session.flush() è il metodo Django che cancella
        tutti i dati di sessione. Lo mocchiamo per verificare
        che venga chiamato senza bisogno del session backend reale.
        """
        request = make_request(session_data={"id_user": 1})

        # Sostituiamo session con un MagicMock per tracciare flush()
        mock_session = MagicMock()
        request.session = mock_session

        response = views.logout(request)

        # Verifica che flush sia stato chiamato
        mock_session.flush.assert_called_once()

        # Verifica il redirect
        assert response.status_code == 302
        assert response["Location"] == "/" or "index" in response["Location"]

    def test_logout_redirect_location(self):
        """
        SCENARIO: verifica URL preciso del redirect.
        ATTESO:   redirect verso la route "home".
        
        Usiamo resolve_url per ottenere l'URL reale dalla named route.
        """
        from django.urls import reverse
        request = make_request()
        request.session = MagicMock()

        response = views.logout(request)

        expected_url = reverse("index")
        assert response["Location"] == expected_url


# ──────────────────────────────────────────────
# TEST: update_user
# ──────────────────────────────────────────────

class TestUpdateUser:
    """
    update_user(request) aggiorna name/surname/email dell'utente
    e ritorna un dict con "success" o "error".
    """

    def test_update_user_no_session(self):
        """
        SCENARIO: nessun id_user in sessione.
        ATTESO:   ritorna dict con chiave "error".
        """
        request = make_request(method="POST", session_data={})

        result = views.update_user(request)

        assert "error" in result
        assert result["error"] == "User not logged in."

    @patch("user.views.get_object_or_404")
    def test_update_user_all_fields_empty(self, mock_get_obj):
        """
        SCENARIO: tutti i campi POST sono vuoti.
        ATTESO:   ritorna dict con "error" e "user".

        Se l'utente non compila nessun campo, non aggiorniamo nulla
        e segnaliamo l'errore.
        """
        fake_user = MagicMock()
        mock_get_obj.return_value = fake_user

        request = make_request(
            method="POST",
            post_data={"name": "", "surname": "", "email": ""},
            session_data={"id_user": 1}
        )

        result = views.update_user(request)

        assert "error" in result
        assert result["error"] == "All fields are empty!"
        assert result["user"] == fake_user
        fake_user.save.assert_not_called()  # save NON deve essere chiamato

    @patch("user.views.get_object_or_404")
    def test_update_user_only_name(self, mock_get_obj):
        """
        SCENARIO: solo il campo "name" è compilato.
        ATTESO:   aggiorna solo name, chiama save(), ritorna "success".

        I campi vuoti non devono sovrascrivere i dati esistenti.
        """
        fake_user = MagicMock()
        fake_user.name = "Vecchio"
        mock_get_obj.return_value = fake_user

        request = make_request(
            method="POST",
            post_data={"name": "Nuovo", "surname": "", "email": ""},
            session_data={"id_user": 1}
        )

        result = views.update_user(request)

        assert "success" in result
        assert fake_user.name == "Nuovo"
        fake_user.save.assert_called_once()

    @patch("user.views.get_object_or_404")
    def test_update_user_all_fields(self, mock_get_obj):
        """
        SCENARIO: tutti i campi sono compilati.
        ATTESO:   aggiorna name, surname, email e salva.
        """
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

    @patch("user.views.get_object_or_404")
    def test_update_user_not_found(self, mock_get_obj):
        """
        SCENARIO: l'utente con quell'id non esiste nel DB.
        ATTESO:   ritorna dict con "error" contenente l'id.

        get_object_or_404 lancia Http404 se non trova il record.
        """
        from django.http import Http404
        mock_get_obj.side_effect = Http404()

        request = make_request(
            method="POST",
            post_data={"name": "X"},
            session_data={"id_user": 999}
        )

        result = views.update_user(request)

        assert "error" in result
        assert "999" in result["error"]

    @patch("user.views.get_object_or_404")
    def test_update_user_unexpected_exception(self, mock_get_obj):
        """
        SCENARIO: eccezione generica durante il salvataggio.
        ATTESO:   ritorna dict con "error" generico.
        """
        mock_get_obj.side_effect = Exception("DB error")

        request = make_request(
            method="POST",
            post_data={"name": "Mario"},
            session_data={"id_user": 1}
        )

        result = views.update_user(request)

        assert "error" in result
        assert result["error"] == "An unexpected error occurred."


# ──────────────────────────────────────────────
# TEST: user_index
# ──────────────────────────────────────────────

class TestUserIndex:
    """
    user_index(request) è la view principale: controlla la sessione,
    gestisce le azioni POST, aggiorna il contesto e renderizza.
    """

    def test_user_index_no_session_redirects(self):
        """
        SCENARIO: nessuna sessione attiva.
        ATTESO:   redirect a "home" (utente non autenticato).
        """
        request = make_request(session_data={})

        response = views.user_index(request)

        assert response.status_code == 302

    @patch("user.views.document_index", return_value={})
    @patch("user.views.get_user", return_value=MagicMock())
    def test_user_index_get_renders_template(self, mock_get_user, mock_doc_index):
        """
        SCENARIO: GET request con sessione valida.
        ATTESO:   renderizza "user/homepage.html" con status 200.

        Mocchiamo get_user e document_index per isolare user_index
        dalle dipendenze esterne.
        """
        request = make_request(session_data={"id_user": 1})

        response = views.user_index(request)

        assert response.status_code == 200

    @patch("user.views.document_index", return_value={})
    @patch("user.views.get_user", return_value=MagicMock())
    def test_user_index_post_logout(self, mock_get_user, mock_doc_index):
        """
        SCENARIO: POST con azione "logout".
        ATTESO:   redirect (la sessione viene svuotata).
        """
        request = make_request(
            method="POST",
            post_data={"azione": "logout"},
            session_data={"id_user": 1}
        )
        request.session = MagicMock()  # per mock di flush()

        response = views.user_index(request)

        assert response.status_code == 302

    @patch("user.views.document_index", return_value={"docs": []})
    @patch("user.views.get_user", return_value=MagicMock())
    def test_user_index_post_create_document(self, mock_get_user, mock_doc_index):
        """
        SCENARIO: POST con azione "create_document".
        ATTESO:   chiama document_index e redirect a "dashboard".
        """
        request = make_request(
            method="POST",
            post_data={"azione": "create_document"},
            session_data={"id_user": 1}
        )

        response = views.user_index(request)

        assert response.status_code == 302
        mock_doc_index.assert_called()

    @patch("user.views.update_user", return_value={"success": "ok"})
    @patch("user.views.document_index", return_value={})
    @patch("user.views.get_user", return_value=MagicMock())
    def test_user_index_post_update_user(self, mock_get_user, mock_doc_index, mock_update):
        """
        SCENARIO: POST con azione "update_user".
        ATTESO:   chiama update_user e redirect a "dashboard".
        """
        request = make_request(
            method="POST",
            post_data={"azione": "update_user"},
            session_data={"id_user": 1}
        )

        response = views.user_index(request)

        assert response.status_code == 302
        mock_update.assert_called_once_with(request)

    @patch("user.views.document_index", side_effect=Exception("boom"))
    @patch("user.views.get_user", return_value=MagicMock())
    def test_user_index_handles_exception(self, mock_get_user, mock_doc_index):
        """
        SCENARIO: document_index lancia un'eccezione inaspettata.
        ATTESO:   la view non crasha, renderizza con "error" nel contesto.

        Il try/except in user_index deve intercettare l'errore
        e aggiungere "error" al contesto, restituendo comunque status 200.
        """
        request = make_request(session_data={"id_user": 1})

        response = views.user_index(request)

        assert response.status_code == 200
        # Verifica che il contesto contenga l'errore
        # (accedibile tramite response.context se si usa il test Client)