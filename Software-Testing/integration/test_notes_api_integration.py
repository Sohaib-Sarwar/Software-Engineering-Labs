"""
test_notes_api_integration.py - integration tests for the Notes REST API.

*** IMPORTANT: THE BACKEND SERVER MUST ALREADY BE RUNNING BEFORE YOU  ***
*** RUN THIS FILE. These are INTEGRATION tests, not unit tests: they  ***
*** send real HTTP requests over the network to a live server. They  ***
*** do NOT start the server themselves and will SKIP (not fail) if   ***
*** no server answers at the configured base URL.                    ***

The server under test is the Flask "Notes" API defined in:
    ../Web-Engineering/backend/app.py

Endpoints exercised here:
    POST   /api/login          - exchange demo credentials for a bearer token
    GET    /api/notes           - list all notes (no auth required)
    GET    /api/notes/<id>      - get a single note (no auth required)
    POST   /api/notes           - create a note (requires auth)
    PUT    /api/notes/<id>      - update a note (requires auth)
    DELETE /api/notes/<id>      - delete a note (requires auth)

How to run this test suite
---------------------------
1. Start the backend server first, in a separate terminal:

       cd Web-Engineering/backend
       pip install flask      (only needed the first time)
       python app.py

   The server listens on http://127.0.0.1:5000 by default and prints
   something like " * Running on http://127.0.0.1:5000".

2. With the server still running, execute these tests from the
   Software-Testing/ folder:

       python -m unittest integration.test_notes_api_integration -v

   or run the whole lab's test suite (unit + integration) with:

       python -m unittest discover

   If the server is not reachable, every test class below reports
   itself as SKIPPED with an explanatory message instead of failing,
   so "discover" still completes cleanly when the backend isn't up.

Implementation notes
---------------------
This file intentionally uses ONLY Python's standard library
(urllib.request / urllib.error / json) so that running the integration
suite never requires "pip install requests" or any other third-party
package. If you prefer the third-party `requests` library, the same
tests could be rewritten using `requests.post(...)` /
`requests.get(...)` etc.; it is not required here.

The demo login credentials used below ("demo" / "password123") are
NOT secrets - they are hard-coded, publicly documented demo
credentials defined directly in Web-Engineering/backend/app.py
(DEMO_USERNAME / DEMO_PASSWORD) purely so this teaching demo has
*something* to log in with. They grant no access to anything beyond
this local, in-memory practice server.
"""

import json
import os
import unittest
import urllib.error
import urllib.request

# Base URL of the running Flask server. Override with the
# NOTES_API_BASE_URL environment variable if the server is started on a
# different host/port.
BASE_URL = os.environ.get("NOTES_API_BASE_URL", "http://127.0.0.1:5000").rstrip("/")

# How long (in seconds) to wait for a single HTTP response before giving up.
REQUEST_TIMEOUT = 5

# Demo credentials matching DEMO_USERNAME / DEMO_PASSWORD in
# Web-Engineering/backend/app.py.
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "password123"

# An id that should never correspond to a real note, used to exercise the
# "not found" (404) paths without depending on exactly which ids happen to
# exist already (the server's notes store is in-memory and grows every
# time notes are created, including by previous test runs).
NONEXISTENT_NOTE_ID = 999_999_999


def _http_request(method, path, body=None, token=None):
    """Send a single HTTP request to the Notes API and return
    (status_code, parsed_json_body_or_None).

    Uses only the standard library (urllib). Raises
    urllib.error.URLError (or a subclass, such as
    ConnectionRefusedError wrapped as URLError, or socket.timeout) if
    the server cannot be reached at all - callers use that to detect
    "server is not running".
    """
    url = f"{BASE_URL}{path}"
    data = None
    headers = {"Accept": "application/json"}

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            status = response.getcode()
            raw = response.read()
    except urllib.error.HTTPError as exc:
        # Flask returns a JSON error body even for 4xx/5xx responses;
        # HTTPError behaves like a response object we can still read
        # from - use it as a context manager so the underlying socket
        # is closed properly instead of relying on the garbage collector.
        with exc:
            status = exc.code
            raw = exc.read()

    parsed = None
    if raw:
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            parsed = None

    return status, parsed


def _server_is_reachable():
    """Return True if the Notes API answers at BASE_URL, False if the
    connection itself fails (server not started)."""
    try:
        _http_request("GET", "/api/notes")
        return True
    except urllib.error.URLError:
        return False


class LiveNotesServerTestCase(unittest.TestCase):
    """Common base class for every test class in this file.

    setUpClass checks that the backend is reachable before any test in
    the subclass runs. If it isn't, every test in the subclass is
    reported as SKIPPED (not FAILED / ERROR) with a message that tells
    you exactly how to start the server.
    """

    @classmethod
    def setUpClass(cls):
        if not _server_is_reachable():
            raise unittest.SkipTest(
                "Notes API backend is not reachable at "
                f"{BASE_URL}. Start it first, then re-run this suite: "
                "cd Web-Engineering/backend && pip install flask && "
                "python app.py"
            )


class TestLoginEndpoint(LiveNotesServerTestCase):
    """Integration tests for POST /api/login."""

    def test_login_with_valid_credentials_returns_token(self):
        status, resp = _http_request(
            "POST",
            "/api/login",
            body={"username": DEMO_USERNAME, "password": DEMO_PASSWORD},
        )
        self.assertEqual(status, 200)
        self.assertIsInstance(resp, dict)
        self.assertIn("token", resp)
        self.assertIsInstance(resp["token"], str)
        self.assertTrue(len(resp["token"]) > 0)
        self.assertEqual(resp.get("username"), DEMO_USERNAME)

    def test_login_with_wrong_password_returns_401(self):
        status, resp = _http_request(
            "POST",
            "/api/login",
            body={"username": DEMO_USERNAME, "password": "not-the-password"},
        )
        self.assertEqual(status, 401)
        self.assertIn("error", resp)

    def test_login_with_unknown_username_returns_401(self):
        status, resp = _http_request(
            "POST",
            "/api/login",
            body={"username": "no-such-user", "password": DEMO_PASSWORD},
        )
        self.assertEqual(status, 401)
        self.assertIn("error", resp)

    def test_login_missing_password_field_returns_400(self):
        status, resp = _http_request(
            "POST", "/api/login", body={"username": DEMO_USERNAME}
        )
        self.assertEqual(status, 400)
        self.assertIn("error", resp)

    def test_login_with_non_string_fields_returns_400(self):
        status, resp = _http_request(
            "POST", "/api/login", body={"username": 12345, "password": DEMO_PASSWORD}
        )
        self.assertEqual(status, 400)
        self.assertIn("error", resp)

    def test_login_with_empty_body_returns_400(self):
        status, resp = _http_request("POST", "/api/login", body={})
        self.assertEqual(status, 400)
        self.assertIn("error", resp)


class TestNotesReadEndpoints(LiveNotesServerTestCase):
    """Integration tests for the read-only, unauthenticated endpoints:
    GET /api/notes and GET /api/notes/<id>."""

    def test_list_notes_returns_a_list_of_note_objects(self):
        status, resp = _http_request("GET", "/api/notes")
        self.assertEqual(status, 200)
        self.assertIsInstance(resp, list)
        # Every item, if any exist, must have the expected note shape.
        for note in resp:
            self.assertIn("id", note)
            self.assertIn("title", note)
            self.assertIn("content", note)

    def test_get_nonexistent_note_returns_404(self):
        status, resp = _http_request("GET", f"/api/notes/{NONEXISTENT_NOTE_ID}")
        self.assertEqual(status, 404)
        self.assertIn("error", resp)


class TestNotesWriteEndpoints(LiveNotesServerTestCase):
    """Integration tests for the authenticated write endpoints:
    POST /api/notes, PUT /api/notes/<id>, DELETE /api/notes/<id>.

    Test methods are numbered (test_01_, test_02_, ...) because they
    share state through class attributes and must run in a specific
    order to exercise a realistic create -> read -> update -> delete
    lifecycle against the same note. unittest's default loader sorts
    test names alphabetically, so zero-padded numeric prefixes give us
    a predictable execution order within this class.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # may raise SkipTest if the server is down
        status, resp = _http_request(
            "POST",
            "/api/login",
            body={"username": DEMO_USERNAME, "password": DEMO_PASSWORD},
        )
        if status != 200:
            raise unittest.SkipTest(
                "Could not log in to obtain a bearer token for the "
                "authenticated write tests; login endpoint returned "
                f"status {status}."
            )
        cls.token = resp["token"]
        cls.created_note_id = None

    def test_01_create_note_without_auth_returns_401(self):
        status, resp = _http_request(
            "POST", "/api/notes", body={"title": "No auth", "content": "should fail"}
        )
        self.assertEqual(status, 401)
        self.assertIn("error", resp)

    def test_02_create_note_with_missing_fields_returns_400(self):
        status, resp = _http_request(
            "POST", "/api/notes", body={"title": "Missing content"}, token=self.token
        )
        self.assertEqual(status, 400)
        self.assertIn("error", resp)

    def test_03_create_note_with_empty_title_returns_400(self):
        status, resp = _http_request(
            "POST",
            "/api/notes",
            body={"title": "   ", "content": "whitespace-only title"},
            token=self.token,
        )
        self.assertEqual(status, 400)
        self.assertIn("error", resp)

    def test_04_create_note_with_auth_returns_201_and_persists(self):
        status, resp = _http_request(
            "POST",
            "/api/notes",
            body={
                "title": "Integration test note",
                "content": "Created by test_notes_api_integration.py",
            },
            token=self.token,
        )
        self.assertEqual(status, 201)
        self.assertIsInstance(resp, dict)
        self.assertIn("id", resp)
        self.assertEqual(resp["title"], "Integration test note")
        self.assertEqual(resp["content"], "Created by test_notes_api_integration.py")

        # Remember the id so later tests in this class can operate on
        # the exact note that was just created.
        type(self).created_note_id = resp["id"]

    def test_05_get_created_note_matches_what_was_created(self):
        self.assertIsNotNone(
            self.created_note_id, "test_04 must run first and create a note"
        )
        status, resp = _http_request("GET", f"/api/notes/{self.created_note_id}")
        self.assertEqual(status, 200)
        self.assertEqual(resp["id"], self.created_note_id)
        self.assertEqual(resp["title"], "Integration test note")

    def test_06_update_note_without_auth_returns_401(self):
        status, resp = _http_request(
            "PUT",
            f"/api/notes/{self.created_note_id}",
            body={"title": "Should not apply"},
        )
        self.assertEqual(status, 401)
        self.assertIn("error", resp)

    def test_07_update_note_title_only_with_auth_returns_200(self):
        status, resp = _http_request(
            "PUT",
            f"/api/notes/{self.created_note_id}",
            body={"title": "Updated by integration test"},
            token=self.token,
        )
        self.assertEqual(status, 200)
        self.assertEqual(resp["title"], "Updated by integration test")
        # Content should be unchanged since it wasn't included in the
        # PUT body (partial update semantics).
        self.assertEqual(resp["content"], "Created by test_notes_api_integration.py")

    def test_08_update_nonexistent_note_returns_404(self):
        status, resp = _http_request(
            "PUT",
            f"/api/notes/{NONEXISTENT_NOTE_ID}",
            body={"title": "Does not matter"},
            token=self.token,
        )
        self.assertEqual(status, 404)
        self.assertIn("error", resp)

    def test_09_update_note_with_no_fields_returns_400(self):
        status, resp = _http_request(
            "PUT",
            f"/api/notes/{self.created_note_id}",
            body={},
            token=self.token,
        )
        self.assertEqual(status, 400)
        self.assertIn("error", resp)

    def test_10_delete_note_without_auth_returns_401(self):
        status, resp = _http_request(
            "DELETE", f"/api/notes/{self.created_note_id}"
        )
        self.assertEqual(status, 401)
        self.assertIn("error", resp)

    def test_11_delete_nonexistent_note_returns_404(self):
        status, resp = _http_request(
            "DELETE", f"/api/notes/{NONEXISTENT_NOTE_ID}", token=self.token
        )
        self.assertEqual(status, 404)
        self.assertIn("error", resp)

    def test_12_delete_note_with_auth_returns_200_and_removes_it(self):
        status, resp = _http_request(
            "DELETE", f"/api/notes/{self.created_note_id}", token=self.token
        )
        self.assertEqual(status, 200)
        self.assertIn("message", resp)

        # The note should now be gone.
        status, resp = _http_request("GET", f"/api/notes/{self.created_note_id}")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
