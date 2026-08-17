"""
Notes App - Flask REST API (lab/demo backend)

This is a small educational REST API for a "Notes" application. It
demonstrates:
    - REST-style CRUD endpoints (GET / POST / PUT / DELETE)
    - An in-memory data store (no database required)
    - A minimal token-based authentication demo (fake bearer tokens)
    - An @require_auth decorator that protects write endpoints
    - Basic input validation with proper HTTP status codes

REQUIREMENT: This file requires Flask. Install it first with:

    pip install flask

Run the server with either:

    python app.py
    (or) flask --app app run

The server listens on http://127.0.0.1:5000 by default.

NOTE ON SECURITY: The authentication here is intentionally simplified for
teaching purposes. Tokens are generated with `secrets.token_hex`, stored in
a plain in-memory dictionary, and never expire. There is a single demo user.
This is NOT production-ready auth (no password hashing, no HTTPS
enforcement, no token expiry, no persistent storage) - it exists purely to
demonstrate the *shape* of token-based auth in a REST API.
"""

from flask import Flask, jsonify, request
from functools import wraps
import secrets

app = Flask(__name__)

# ---------------------------------------------------------------------------
# "Database" - a simple in-memory data store.
# Restarting the server resets all data. Good enough for a teaching demo.
# ---------------------------------------------------------------------------

notes = {}
next_id = 1

# Demo user credentials (hard-coded for the sake of the demo only).
DEMO_USERNAME = "demo"
DEMO_PASSWORD = "password123"

# Maps active bearer tokens -> username. Populated by POST /api/login.
active_tokens = {}


def _seed_data():
    """Add a couple of example notes so GET /api/notes returns something
    useful the first time the server is started."""
    global next_id
    for title, content in (
        ("Welcome", "This is your first note. Try editing or deleting it!"),
        ("Shopping list", "Milk, eggs, bread, coffee"),
    ):
        notes[next_id] = {"id": next_id, "title": title, "content": content}
        next_id += 1


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def require_auth(view_func):
    """Decorator that protects an endpoint with simple bearer-token auth.

    Expects a header of the form:

        Authorization: Bearer <token>

    If the header is missing, malformed, or the token is unknown, the
    request is rejected with 401 Unauthorized before the wrapped view runs.
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return (
                jsonify(
                    {
                        "error": "Missing or malformed Authorization header. "
                        "Expected format: 'Bearer <token>'."
                    }
                ),
                401,
            )

        token = auth_header[len("Bearer "):].strip()

        if not token or token not in active_tokens:
            return jsonify({"error": "Invalid or expired token."}), 401

        # Authentication succeeded; continue to the actual view function.
        return view_func(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------------------
# Auth endpoints
# ---------------------------------------------------------------------------

@app.route("/api/login", methods=["POST"])
def login():
    """Exchange a username/password for a bearer token.

    Expects JSON body: {"username": "...", "password": "..."}
    Returns 200 with {"token": "..."} on success.
    Returns 400 if the body is missing/invalid.
    Returns 401 if the credentials are wrong.
    """
    data = request.get_json(silent=True)

    if not data or "username" not in data or "password" not in data:
        return (
            jsonify(
                {"error": "Request body must be JSON with 'username' and 'password'."}
            ),
            400,
        )

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "'username' and 'password' must be strings."}), 400

    if username != DEMO_USERNAME or password != DEMO_PASSWORD:
        return jsonify({"error": "Invalid username or password."}), 401

    # Generate a fake bearer token and remember it server-side.
    token = secrets.token_hex(16)
    active_tokens[token] = username

    return jsonify({"token": token, "token_type": "Bearer", "username": username}), 200


@app.route("/api/logout", methods=["POST"])
@require_auth
def logout():
    """Invalidate the bearer token used for this request."""
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[len("Bearer "):].strip()
    active_tokens.pop(token, None)
    return jsonify({"message": "Logged out."}), 200


# ---------------------------------------------------------------------------
# Notes CRUD endpoints
# ---------------------------------------------------------------------------

def _validate_note_payload(data, require_all_fields):
    """Validate a note payload from the request body.

    Returns (error_message, status_code) if invalid, otherwise (None, None).
    When require_all_fields is True, both 'title' and 'content' must be
    present (used for POST). When False, at least one of them must be
    present (used for PUT, allowing partial updates).
    """
    if data is None or not isinstance(data, dict):
        return "Request body must be a JSON object.", 400

    has_title = "title" in data
    has_content = "content" in data

    if require_all_fields and not (has_title and has_content):
        return "Both 'title' and 'content' are required.", 400

    if not require_all_fields and not (has_title or has_content):
        return "At least one of 'title' or 'content' must be provided.", 400

    if has_title:
        title = data["title"]
        if not isinstance(title, str) or not title.strip():
            return "'title' must be a non-empty string.", 400

    if has_content:
        content = data["content"]
        if not isinstance(content, str):
            return "'content' must be a string.", 400

    return None, None


@app.route("/api/notes", methods=["GET"])
def list_notes():
    """Return all notes, sorted by id. Read-only endpoint - no auth
    required, so the frontend can display notes without logging in."""
    result = [notes[note_id] for note_id in sorted(notes.keys())]
    return jsonify(result), 200


@app.route("/api/notes/<int:note_id>", methods=["GET"])
def get_note(note_id):
    """Return a single note by id."""
    note = notes.get(note_id)
    if note is None:
        return jsonify({"error": f"Note {note_id} not found."}), 404
    return jsonify(note), 200


@app.route("/api/notes", methods=["POST"])
@require_auth
def create_note():
    """Create a new note. Requires authentication.

    Expects JSON body: {"title": "...", "content": "..."}
    """
    global next_id

    data = request.get_json(silent=True)
    error, status = _validate_note_payload(data, require_all_fields=True)
    if error:
        return jsonify({"error": error}), status

    note = {
        "id": next_id,
        "title": data["title"].strip(),
        "content": data["content"],
    }
    notes[next_id] = note
    next_id += 1

    return jsonify(note), 201


@app.route("/api/notes/<int:note_id>", methods=["PUT"])
@require_auth
def update_note(note_id):
    """Update an existing note. Requires authentication.

    Expects a JSON body containing 'title' and/or 'content'. Fields that
    are omitted are left unchanged.
    """
    note = notes.get(note_id)
    if note is None:
        return jsonify({"error": f"Note {note_id} not found."}), 404

    data = request.get_json(silent=True)
    error, status = _validate_note_payload(data, require_all_fields=False)
    if error:
        return jsonify({"error": error}), status

    if "title" in data:
        note["title"] = data["title"].strip()
    if "content" in data:
        note["content"] = data["content"]

    return jsonify(note), 200


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
@require_auth
def delete_note(note_id):
    """Delete a note by id. Requires authentication."""
    if note_id not in notes:
        return jsonify({"error": f"Note {note_id} not found."}), 404

    del notes[note_id]
    return jsonify({"message": f"Note {note_id} deleted."}), 200


# ---------------------------------------------------------------------------
# Fallback error handlers so unexpected paths / methods return JSON, not
# Flask's default HTML error pages.
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"error": "Resource not found."}), 404


@app.errorhandler(405)
def handle_405(e):
    return jsonify({"error": "Method not allowed on this endpoint."}), 405


if __name__ == "__main__":
    _seed_data()
    app.run(debug=True)
else:
    # Also seed data when run via `flask run`, so the demo has content on
    # first load regardless of how the server was started.
    _seed_data()
