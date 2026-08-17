# syntax=docker/dockerfile:1
#
# Dockerfile for the tiny Flask "hello service" (app.py in this same
# folder). This demonstrates the core cloud-computing idea of "application
# packaging": bundling code + runtime + dependencies into one immutable,
# portable artifact (an image) that runs identically on a laptop, a CI
# runner, or any cloud provider's container platform (e.g. AWS ECS/Fargate,
# Google Cloud Run, Azure Container Apps, or a Kubernetes cluster -- see
# ../configurations/cloud-deployment-manifest.yaml for the Kubernetes side
# of this same app).
#
# Build:
#   docker build -t hello-service:latest .
# Run:
#   docker run --rm -p 5000:5000 -e GREETING="Hi there" hello-service:latest
# Then visit http://localhost:5000/

# ---- Base image -----------------------------------------------------------
# Small, official, version-pinned base image keeps the attack surface and
# image size down -- both are cloud cost and security best practices.
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffering stdout/stderr, which
# keeps container logs flowing immediately to whatever log aggregator the
# cloud platform is using.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ---- Dependencies -----------------------------------------------------------
# Copy only the requirements file first so Docker can cache this layer and
# skip re-installing dependencies when only application code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Application code -------------------------------------------------------
COPY app.py .

# ---- Security: run as a non-root user --------------------------------------
# Least-privilege principle applied at the container level: the process
# inside the container should not run as root.
RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

# ---- Runtime configuration ---------------------------------------------------
# Defaults; override at `docker run -e` / docker-compose / Kubernetes env
# time. Nothing sensitive is hardcoded here -- see README for secrets
# management notes.
ENV SERVICE_NAME=hello-service \
    GREETING="Hello from the cloud!" \
    PORT=5000

EXPOSE 5000

# Container-level healthcheck, mirrored by the readiness/liveness probes in
# the Kubernetes manifest and the healthcheck in docker-compose.yml.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/healthz', timeout=2).status == 200 else 1)"

CMD ["python", "app.py"]
