"""
Tiny Flask "hello service" used to demonstrate application packaging for
cloud deployment (see ../documentation/README.md for the full write-up).

Endpoints:
  GET /            -> human-friendly greeting, echoes the pod/container
                       hostname so you can see load-balancing across
                       multiple replicas in action.
  GET /healthz     -> liveness/readiness probe target, returns 200 + JSON.
  GET /env-demo    -> shows how configuration is injected via environment
                       variables instead of being hardcoded (12-factor app
                       style config), which is how cloud platforms (and the
                       Kubernetes manifest / docker-compose file in this
                       folder) pass settings into a container.

Run locally (after `pip install flask`):
    python app.py
Then visit http://localhost:5000/

This file intentionally has zero external state (no database, no disk
writes) so it can be scaled horizontally to any number of replicas without
any of them stepping on each other -- a core idea behind cloud scalability.
"""

import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)

# Configuration read from the environment rather than hardcoded in source.
# This mirrors how the Dockerfile, docker-compose.yml, and the Kubernetes
# manifest in this lab all inject settings at deploy time.
SERVICE_NAME = os.environ.get("SERVICE_NAME", "hello-service")
GREETING = os.environ.get("GREETING", "Hello from the cloud!")
# NOTE: never hardcode real secrets here. In a real deployment this value
# would come from a secrets manager / Kubernetes Secret, injected as an
# environment variable at runtime. This lab only ever uses a placeholder.
DB_PASSWORD_PLACEHOLDER = os.environ.get("DB_PASSWORD", "YOUR_DB_PASSWORD")


@app.route("/")
def hello():
    return jsonify(
        {
            "message": GREETING,
            "service": SERVICE_NAME,
            "served_by_host": socket.gethostname(),
        }
    )


@app.route("/healthz")
def healthz():
    # Kept intentionally cheap and dependency-free so it is safe to call
    # frequently from a liveness/readiness probe without adding load.
    return jsonify({"status": "ok"}), 200


@app.route("/env-demo")
def env_demo():
    # Demonstrates that configuration/secrets are supplied externally
    # (env vars) rather than baked into the image or committed to source
    # control. DB_PASSWORD is never a real credential in this lab -- only
    # a placeholder string, and it is never printed in full below.
    has_custom_password = DB_PASSWORD_PLACEHOLDER != "YOUR_DB_PASSWORD"
    return jsonify(
        {
            "service_name": SERVICE_NAME,
            "greeting": GREETING,
            "db_password_configured": has_custom_password,
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
