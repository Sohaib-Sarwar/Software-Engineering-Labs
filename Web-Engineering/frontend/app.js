/*
 * Notes App - frontend logic (Web Engineering lab demo)
 *
 * Demonstrates:
 *   - Client-server communication using the Fetch API
 *   - Sending/receiving JSON
 *   - Token-based authentication from the client side (storing and
 *     attaching a Bearer token to protected requests)
 *   - DOM manipulation (rendering a list of notes, showing status
 *     messages, clearing forms, etc.)
 *
 * This file talks to the Flask backend in ../backend/app.py.
 * See documentation/README.md for how to start the backend server.
 */

(() => {
  "use strict";

  // ---------------------------------------------------------------------
  // Element references
  // ---------------------------------------------------------------------
  const apiBaseInput = document.getElementById("api-base");
  const loginForm = document.getElementById("login-form");
  const usernameInput = document.getElementById("username");
  const passwordInput = document.getElementById("password");
  const authStatusEl = document.getElementById("auth-status");

  const noteForm = document.getElementById("note-form");
  const noteTitleInput = document.getElementById("note-title");
  const noteContentInput = document.getElementById("note-content");

  const notesListEl = document.getElementById("notes-list");
  const refreshBtn = document.getElementById("refresh-btn");

  const messageEl = document.getElementById("message");

  // ---------------------------------------------------------------------
  // Client-side state
  // ---------------------------------------------------------------------
  let authToken = null; // Bearer token received from POST /api/login

  function apiBase() {
    // Trim trailing slash so we can safely do `${base}/api/...`
    return apiBaseInput.value.trim().replace(/\/+$/, "");
  }

  // ---------------------------------------------------------------------
  // Small UI helpers
  // ---------------------------------------------------------------------
  function showMessage(text, kind) {
    messageEl.textContent = text;
    messageEl.className = "message" + (kind ? " " + kind : "");
  }

  function setAuthStatus() {
    if (authToken) {
      authStatusEl.textContent = "Logged in as \"" + usernameInput.value + "\".";
      authStatusEl.className = "status logged-in";
    } else {
      authStatusEl.textContent = "Not logged in. Log in to add or delete notes.";
      authStatusEl.className = "status logged-out";
    }
  }

  function clearNotesList() {
    while (notesListEl.firstChild) {
      notesListEl.removeChild(notesListEl.firstChild);
    }
  }

  function renderNotes(notes) {
    clearNotesList();

    if (!Array.isArray(notes) || notes.length === 0) {
      const empty = document.createElement("li");
      empty.className = "empty-state";
      empty.textContent = "No notes yet. Add one above!";
      notesListEl.appendChild(empty);
      return;
    }

    for (const note of notes) {
      const item = document.createElement("li");
      item.className = "note-item";

      const textWrap = document.createElement("div");

      const heading = document.createElement("h3");
      heading.textContent = note.title;
      textWrap.appendChild(heading);

      const body = document.createElement("p");
      body.textContent = note.content;
      textWrap.appendChild(body);

      const meta = document.createElement("div");
      meta.className = "note-meta";
      meta.textContent = "id: " + note.id;
      textWrap.appendChild(meta);

      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "danger";
      deleteBtn.textContent = "Delete";
      deleteBtn.addEventListener("click", () => deleteNote(note.id));

      item.appendChild(textWrap);
      item.appendChild(deleteBtn);
      notesListEl.appendChild(item);
    }
  }

  // ---------------------------------------------------------------------
  // API calls
  // ---------------------------------------------------------------------

  /** Build the headers for an authenticated (write) request. */
  function authHeaders() {
    const headers = { "Content-Type": "application/json" };
    if (authToken) {
      headers["Authorization"] = "Bearer " + authToken;
    }
    return headers;
  }

  async function login(username, password) {
    const response = await fetch(apiBase() + "/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "Login failed (HTTP " + response.status + ").");
    }

    return data.token;
  }

  async function fetchNotes() {
    const response = await fetch(apiBase() + "/api/notes", { method: "GET" });
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "Failed to load notes (HTTP " + response.status + ").");
    }

    return data;
  }

  async function createNote(title, content) {
    const response = await fetch(apiBase() + "/api/notes", {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ title, content }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "Failed to create note (HTTP " + response.status + ").");
    }

    return data;
  }

  async function deleteNoteRequest(id) {
    const response = await fetch(apiBase() + "/api/notes/" + encodeURIComponent(id), {
      method: "DELETE",
      headers: authHeaders(),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "Failed to delete note (HTTP " + response.status + ").");
    }

    return data;
  }

  // ---------------------------------------------------------------------
  // High-level actions (wire API calls to UI state/DOM updates)
  // ---------------------------------------------------------------------

  async function loadNotes() {
    try {
      showMessage("Loading notes...", "");
      const notes = await fetchNotes();
      renderNotes(notes);
      showMessage("Notes loaded.", "success");
    } catch (err) {
      showMessage(err.message, "error");
      renderNotes([]);
    }
  }

  async function handleLogin(event) {
    event.preventDefault();
    try {
      const username = usernameInput.value.trim();
      const password = passwordInput.value;
      authToken = await login(username, password);
      setAuthStatus();
      showMessage("Logged in successfully.", "success");
    } catch (err) {
      authToken = null;
      setAuthStatus();
      showMessage(err.message, "error");
    }
  }

  async function handleCreateNote(event) {
    event.preventDefault();

    if (!authToken) {
      showMessage("You must log in before adding a note.", "error");
      return;
    }

    const title = noteTitleInput.value.trim();
    const content = noteContentInput.value;

    try {
      await createNote(title, content);
      noteForm.reset();
      showMessage("Note added.", "success");
      await loadNotes();
    } catch (err) {
      showMessage(err.message, "error");
    }
  }

  async function deleteNote(id) {
    if (!authToken) {
      showMessage("You must log in before deleting a note.", "error");
      return;
    }

    try {
      await deleteNoteRequest(id);
      showMessage("Note deleted.", "success");
      await loadNotes();
    } catch (err) {
      showMessage(err.message, "error");
    }
  }

  // ---------------------------------------------------------------------
  // Event wiring
  // ---------------------------------------------------------------------
  loginForm.addEventListener("submit", handleLogin);
  noteForm.addEventListener("submit", handleCreateNote);
  refreshBtn.addEventListener("click", loadNotes);

  // Initial state on page load.
  setAuthStatus();
  loadNotes();
})();
