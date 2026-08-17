# Web Engineering Lab: Notes App (Client-Server Demo)

This lab demonstrates the fundamentals of **client-server web architecture**
using a small "Notes" application:

- A **backend** REST API written in Python with Flask (`backend/app.py`)
- A **frontend** static web page that talks to the backend using the Fetch
  API (`frontend/index.html`, `frontend/style.css`, `frontend/app.js`)

It is intentionally small and dependency-light so the concepts are easy to
follow: an in-memory data store instead of a database, and a simplified
token-based authentication scheme instead of a full identity system.

---

## 1. Client-server architecture

In this model, two separate programs communicate over HTTP:

```
 ┌────────────────────┐        HTTP requests (fetch)        ┌──────────────────────┐
 │      CLIENT         │ ───────────────────────────────────▶ │       SERVER          │
 │  (frontend/*.html,  │                                      │  (backend/app.py,     │
 │   *.css, *.js —     │ ◀─────────────────────────────────── │   Flask REST API)     │
 │   runs in browser)  │        JSON responses                │  in-memory data store │
 └────────────────────┘                                      └──────────────────────┘
```

- The **client** (browser) owns the *presentation* layer: it renders HTML,
  handles user interaction, and never touches the data store directly. It
  only knows how to make HTTP requests and render whatever JSON comes back.
- The **server** owns the *data and business logic*: it stores notes,
  validates input, enforces authentication/authorization rules, and exposes
  that functionality only through a well-defined HTTP API.
- The two communicate exclusively through HTTP requests/responses carrying
  **JSON** payloads. This separation means the frontend could be swapped
  for a mobile app, and the backend could be swapped for a different
  language, without the other side needing to change — as long as the API
  contract (the endpoints below) stays the same.
- The browser's `fetch()` function is what makes this demo a *client-server*
  demo rather than a single monolithic page: every button click in
  `app.js` results in an outgoing HTTP request to the Flask server, and the
  DOM is updated only after a response comes back.

---

## 2. REST API design

All endpoints are served by `backend/app.py` under the `/api` prefix and
exchange JSON. The API follows REST conventions: resources are nouns
(`/notes`), and the HTTP verb expresses the action.

| Method | Endpoint             | Auth required? | Description                                   | Success | Error codes        |
|--------|-----------------------|-----------------|------------------------------------------------|---------|---------------------|
| POST   | `/api/login`          | No              | Exchange username/password for a bearer token   | 200     | 400, 401            |
| POST   | `/api/logout`         | Yes             | Invalidate the current bearer token             | 200     | 401                 |
| GET    | `/api/notes`          | No              | List all notes                                  | 200     | —                   |
| GET    | `/api/notes/<id>`     | No              | Get a single note by id                         | 200     | 404                 |
| POST   | `/api/notes`          | Yes             | Create a new note                               | 201     | 400, 401            |
| PUT    | `/api/notes/<id>`     | Yes             | Update an existing note (partial update allowed)| 200     | 400, 401, 404       |
| DELETE | `/api/notes/<id>`     | Yes             | Delete a note                                   | 200     | 401, 404            |

### Request/response examples

**Login**

```
POST /api/login
Content-Type: application/json

{ "username": "demo", "password": "password123" }
```

```
200 OK
{ "token": "8f1c...", "token_type": "Bearer", "username": "demo" }
```

**Create a note**

```
POST /api/notes
Authorization: Bearer 8f1c...
Content-Type: application/json

{ "title": "Groceries", "content": "Milk, eggs, bread" }
```

```
201 Created
{ "id": 3, "title": "Groceries", "content": "Milk, eggs, bread" }
```

### Status codes used, and why

- **200 OK** — a read/update/delete/login succeeded.
- **201 Created** — a new note resource was created (POST `/api/notes`).
- **400 Bad Request** — the request body is missing, malformed, or fails
  validation (e.g. `title` missing, `title` is empty, wrong JSON shape).
- **401 Unauthorized** — the request is missing a valid `Authorization:
  Bearer <token>` header on a protected endpoint, or login credentials
  were wrong.
- **404 Not Found** — the requested note id does not exist.
- **405 Method Not Allowed** — a request used a verb the endpoint doesn't
  support (handled by a generic Flask error handler).

Read endpoints (`GET /api/notes`, `GET /api/notes/<id>`) are left public in
this demo so the frontend can display notes before anyone logs in — this
mirrors many real apps where reading is public but writing requires an
account. Every endpoint that mutates data (create, update, delete, logout)
is protected by the `@require_auth` decorator.

---

## 3. Authentication & authorization approach

This lab uses a deliberately simplified **token-based authentication**
scheme so the mechanics are easy to see end-to-end:

1. **Login (`POST /api/login`)** — the client sends a username and
   password as JSON. The server checks them against a single hard-coded
   demo account (`demo` / `password123`). If they match, the server
   generates a random token (`secrets.token_hex(16)`) and stores it in an
   in-memory `active_tokens` dictionary, mapping token → username. The
   token is returned to the client in the JSON response.

2. **Using the token** — the client stores the token in memory (in
   `app.js`, in the `authToken` variable) and attaches it to every
   subsequent write request as an HTTP header:

   ```
   Authorization: Bearer <token>
   ```

   This is the standard **Bearer token** scheme used by most real-world
   REST APIs (OAuth2, JWT-based APIs, etc.), just without the
   cryptographic signing a production system would add.

3. **Authorization (`@require_auth` decorator)** — on the server, the
   `@require_auth` decorator wraps every protected view function
   (`create_note`, `update_note`, `delete_note`, `logout`). It:
   - Reads the `Authorization` header from the incoming request.
   - Rejects the request with **401** if the header is missing, doesn't
     start with `"Bearer "`, or the token isn't present in
     `active_tokens`.
   - Otherwise lets the request proceed to the actual endpoint logic.

   This cleanly separates the **cross-cutting concern of authentication**
   from each endpoint's own **business logic** (validation, CRUD), which is
   a common real-world pattern (middleware/decorators/guards).

4. **Logout (`POST /api/logout`)** — removes the token from
   `active_tokens`, immediately invalidating it for future requests.

### What is intentionally simplified (and why)

This is a **teaching demo**, not production-ready authentication. To keep
the focus on the client-server/REST concepts, the following shortcuts were
made deliberately:

- A single hard-coded username/password instead of a user database.
- Passwords compared in plain text instead of hashed (a real system must
  use a strong password hash, e.g. bcrypt/argon2, and never store or
  compare raw passwords).
- Tokens never expire and are stored in a plain in-memory dictionary
  (a real system would use signed/expiring tokens such as JWTs, or a
  server-side session store backed by a database/cache).
- No HTTPS enforcement (in production, bearer tokens must only ever be
  sent over HTTPS, since anyone on the network could otherwise read them).

Despite the simplifications, the *shape* of the solution — exchange
credentials for a token, attach the token to subsequent requests, verify
the token server-side before allowing an action — mirrors how real
token-based auth (including JWT and OAuth2 bearer flows) works.

---

## 4. Running the project

### 4.1 Backend (Flask API)

**Requirements:** Python 3 and Flask.

```bash
pip install flask
```

From the `backend/` directory, start the server with either:

```bash
python app.py
```

or:

```bash
flask --app app run
```

By default the server runs at `http://127.0.0.1:5000`. You should see log
output confirming the development server has started. The API comes
pre-seeded with two example notes so `GET /api/notes` returns data
immediately.

You can test the API directly with `curl`, for example:

```bash
curl http://127.0.0.1:5000/api/notes

curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"demo\", \"password\": \"password123\"}"
```

### 4.2 Frontend (static site)

The frontend is plain HTML/CSS/JS and needs no build step or server of its
own — but it does need the backend running first, since every action in
the page calls the Flask API over HTTP.

1. Make sure the backend is running (see 4.1).
2. Open `frontend/index.html` directly in a web browser (double-click it,
   or use "Open File" from the browser's File menu).
3. In the page, confirm the **Backend URL** field matches where Flask is
   running (default: `http://127.0.0.1:5000`).
4. Use the **Login** form with the demo credentials shown on the page
   (`demo` / `password123`) to obtain a token.
5. Add notes with the **New note** form, and delete notes with the
   **Delete** button next to each note. The **Refresh** button re-fetches
   the list from the server.

> Note: Because the frontend is opened as a local `file://` page while the
> backend runs on `http://127.0.0.1:5000`, this is a **cross-origin**
> request from the browser's point of view. Flask's development server
> allows this in practice for a local demo; a production deployment would
> need to explicitly configure CORS (e.g. with `flask-cors`) or serve the
> frontend from the same origin as the API.

---

## 5. Key concepts recap

- **Client-server separation**: the browser (client) and Flask app
  (server) are independent programs that only communicate over HTTP/JSON.
- **REST API design**: resources (`/api/notes`) manipulated via HTTP verbs
  (GET/POST/PUT/DELETE), with meaningful status codes for success and
  failure.
- **Statelessness**: each HTTP request from the client carries everything
  the server needs to authorize it (the bearer token in the header) — the
  server does not rely on a stateful browser session/cookie.
- **DOM manipulation**: `app.js` builds and updates the notes list purely
  through JavaScript DOM APIs (`createElement`, `appendChild`, `textContent`)
  in response to data returned from the server.
- **Input validation**: the backend rejects malformed requests (missing
  fields, empty titles, wrong types) with `400 Bad Request` before ever
  touching the data store.
