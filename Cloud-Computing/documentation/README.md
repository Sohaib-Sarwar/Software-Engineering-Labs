# Cloud Computing Lab: Packaging, Deploying, and Scaling a Service

This lab folder walks through a single, tiny Flask "hello service" as it
moves through the standard cloud-computing deployment stack: a container
image, a local multi-container composition, and a Kubernetes-style
deployment manifest. Each artifact is real, runnable code -- not a
diagram -- so you can build it, run it, and inspect it directly.

```
Cloud-Computing/
├── deployments/
│   ├── app.py                 # the Flask service itself
│   ├── requirements.txt       # its one dependency (Flask)
│   ├── Dockerfile             # packages app.py into a container image
│   └── docker-compose.yml     # runs the app + a Redis service together
├── configurations/
│   └── cloud-deployment-manifest.yaml   # Kubernetes Deployment + Service
└── documentation/
    └── README.md              # this file
```

---

## 1. IaaS vs PaaS vs SaaS

Cloud computing is usually described as a spectrum of "how much of the
stack does the provider manage for you." Using concrete, well-known
products as reference points:

| Layer | What the provider manages | What you still manage | Concrete examples |
|---|---|---|---|
| **IaaS** (Infrastructure as a Service) | Physical servers, networking, virtualization, storage hardware | OS, runtime, middleware, your app, patching, scaling logic | AWS EC2, Google Compute Engine, Azure Virtual Machines, DigitalOcean Droplets |
| **PaaS** (Platform as a Service) | Everything IaaS manages, plus the OS, runtime, and often scaling/load-balancing | Your application code and its configuration | Google App Engine, Heroku, AWS Elastic Beanstalk, Azure App Service, a managed Kubernetes control plane such as GKE/EKS/AKS |
| **SaaS** (Software as a Service) | The entire application, including the code itself | Just your data and account configuration | Gmail, Salesforce, Slack, Dropbox, Microsoft 365 |

A useful mental model: as you move from IaaS toward SaaS, you trade
**control** for **convenience**. IaaS gives you a blank virtual machine and
maximum flexibility; SaaS gives you a finished product and zero
infrastructure to think about. PaaS sits in between: you still write and
own your application code, but the provider handles the servers, OS
patching, and often the autoscaling underneath it.

### Where this lab's artifacts sit on that spectrum

- **`deployments/Dockerfile`** packages the application together with its
  runtime (Python + Flask) into a single portable image. This is exactly
  the unit of work an **IaaS** virtual machine *or* a **PaaS** container
  platform (Cloud Run, Elastic Beanstalk, App Service) expects you to hand
  it -- the same image can run unmodified on either.
- **`deployments/docker-compose.yml`** simulates running that container
  alongside a second managed-style service (Redis) the way you might on a
  single IaaS VM during development, or the way a PaaS's "add-on"
  marketplace (e.g. Heroku Redis, a managed Cloud SQL instance) attaches a
  data service to your app without you provisioning the server yourself.
- **`configurations/cloud-deployment-manifest.yaml`** is written for
  Kubernetes, which is itself commonly consumed as a **PaaS**: a managed
  Kubernetes service (GKE/EKS/AKS) runs and patches the control plane for
  you, and you simply describe *what* you want running (this manifest)
  rather than *how* to provision the machines underneath it.
- None of the files here are SaaS -- SaaS is the finished product a cloud
  vendor sells you (e.g. Gmail), not something you build and deploy
  yourself. It's included in the table only for contrast.

---

## 2. Running the lab

### 2.1 Run the Flask app directly (no containers)

```bash
cd deployments
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000/`, `http://localhost:5000/healthz`, and
`http://localhost:5000/env-demo`.

### 2.2 Build and run the container image (`Dockerfile`)

```bash
cd deployments
docker build -t hello-service:latest .
docker run --rm -p 5000:5000 -e GREETING="Hi there" hello-service:latest
```

This demonstrates **application packaging**: the image bundles the Python
interpreter, Flask, and `app.py` together so it behaves identically no
matter which machine or cloud provider runs it.

### 2.3 Run the multi-container composition (`docker-compose.yml`)

```bash
cd deployments
docker compose up --build
```

This starts two independently-scalable services -- `hello-service` (the
app tier) and `cache` (a Redis data tier) -- on a shared private network,
each with its own healthcheck, demonstrating a multi-container,
cloud-style deployment topology. Stop it with `docker compose down`.

### 2.4 Apply the Kubernetes-style manifest

Against any Kubernetes cluster (a managed cloud cluster, or a local one
such as `minikube` or `kind`):

```bash
cd configurations
kubectl apply -f cloud-deployment-manifest.yaml
kubectl get deployments,pods,svc -l app=hello-service
kubectl delete -f cloud-deployment-manifest.yaml
```

---

## 3. Scalability strategies demonstrated here

**Horizontal scaling (scale out), not just vertical scaling (scale up).**
`app.py` is deliberately stateless -- it keeps no data in memory or on
local disk between requests -- so it can be scaled out to any number of
identical copies without them conflicting or needing to share local state.
That is what makes the following possible:

- **`replicas: 3`** in `cloud-deployment-manifest.yaml` runs three
  identical pods of the same image from the start.
- The **`Service`** object load-balances traffic across however many pod
  replicas currently exist, under one stable internal DNS name
  (`hello-service`), so callers never need to know how many replicas exist
  or which one answered.
- The commented **`HorizontalPodAutoscaler`** example shows how a cloud
  platform can adjust `replicas` automatically based on observed CPU load
  (e.g. between 3 and 10 pods, targeting 70% average CPU utilization) --
  scaling out under load and back in to save cost when idle.
- **`resources.requests` / `resources.limits`** on the container bound how
  much CPU/memory each replica may consume, so the cluster's scheduler can
  safely pack many replicas (from this service and others) onto shared
  nodes without one pod starving its neighbors.

---

## 4. Availability strategies demonstrated here

- **Health endpoints**: `app.py` exposes `GET /healthz`, a cheap,
  dependency-free endpoint that only reports "is this process able to
  respond at all" -- deliberately kept simple so probes can call it
  frequently without adding meaningful load.
- **Liveness probes** (`livenessProbe` in the manifest, `HEALTHCHECK` in
  the Dockerfile, `healthcheck` in docker-compose): if the process hangs
  or deadlocks, the platform detects the failed check and restarts the
  container automatically, recovering without human intervention.
- **Readiness probes** (`readinessProbe` in the manifest): distinguish
  "alive" from "ready to receive traffic." A pod that fails its readiness
  check is pulled out of the Service's load-balancing pool (but not
  killed) until it passes again -- this is what prevents traffic from
  being routed to a pod that is still starting up.
- **Rolling updates** (`strategy.rollingUpdate` in the manifest, with
  `maxSurge: 1` / `maxUnavailable: 1`): deployments replace pods
  gradually, always keeping most replicas serving traffic, so a new
  version can be rolled out with zero downtime.
- **Multiple replicas across a Service** mean the failure of any single
  pod (crash, node failure, in-progress restart) does not take the whole
  service down -- the remaining healthy replicas keep serving.
- **`depends_on: condition: service_healthy`** in `docker-compose.yml`
  ensures the app container only starts once its Redis dependency reports
  healthy, avoiding a class of "started too early" failures.

---

## 5. Basic cloud security notes

- **Never hardcode secrets in code, images, or manifests.** Every
  credential-shaped value in this lab (`DB_PASSWORD`) is a placeholder
  string such as `YOUR_DB_PASSWORD` -- never a real password, key, or
  token. Real secrets belong in a secrets manager (AWS Secrets Manager,
  Google Secret Manager, Azure Key Vault, HashiCorp Vault) or a
  platform-native secret store (a Kubernetes `Secret` object, referenced
  via `secretKeyRef` as shown -- commented out -- in
  `cloud-deployment-manifest.yaml`), then injected into the running
  process as an environment variable at deploy time. The application code
  (`app.py`) only ever reads `os.environ.get(...)`; it never contains a
  literal secret.
- **Configuration via environment variables, not source code** (the
  "config" factor of a 12-factor app). This is what lets the exact same
  container image be promoted from dev -> staging -> production, and
  reused across cloud providers, by changing only its environment, not
  its code.
- **Least privilege at the container/pod level**:
  - The `Dockerfile` creates and switches to a non-root `appuser` (`USER
    appuser`) so the process inside the container cannot act as root even
    if it is compromised.
  - The Kubernetes manifest's `securityContext` goes further:
    `runAsNonRoot: true`, `allowPrivilegeEscalation: false`,
    `readOnlyRootFilesystem: true`, and `capabilities: drop: ["ALL"]` --
    each one removes a privilege the app doesn't need, shrinking what an
    attacker could do if the container were ever compromised.
- **Least privilege at the access-control level** (not shown in code
  here, since it is cluster/account configuration rather than application
  config, but worth knowing): grant a deployment pipeline or service
  account only the specific permissions it needs (e.g. "deploy to this
  one namespace") rather than broad admin access, following the same
  principle as the container-level settings above.
- **Resource limits double as a security control**, not just a
  performance one: capping CPU/memory (`resources.limits` in the
  manifest) limits the blast radius of a runaway or compromised process,
  preventing it from starving every other workload on a shared node.
- **Small, version-pinned base images** (`python:3.12-slim` in the
  Dockerfile, `flask==3.0.3` in `requirements.txt`) reduce the attack
  surface compared to a full OS image and keep builds reproducible.

---

## 6. Quick concept-to-file map

| Concept | Where it appears |
|---|---|
| Application packaging | `deployments/Dockerfile`, `deployments/app.py` |
| Multi-container / multi-tier deployment | `deployments/docker-compose.yml` |
| Scalability (horizontal scaling, replicas, autoscaling) | `configurations/cloud-deployment-manifest.yaml` (`replicas`, `HorizontalPodAutoscaler`) |
| Availability (probes, rolling updates, load balancing) | `configurations/cloud-deployment-manifest.yaml` (`livenessProbe`, `readinessProbe`, `strategy`, `Service`); `Dockerfile`/`docker-compose.yml` (`HEALTHCHECK`) |
| Resource governance | `configurations/cloud-deployment-manifest.yaml` (`resources.requests`/`resources.limits`) |
| Externalized configuration | `deployments/app.py` (`os.environ.get`), all three deployment files (`environment:` / `env:`) |
| Secrets management (placeholders only) | `deployments/docker-compose.yml`, `configurations/cloud-deployment-manifest.yaml` (`DB_PASSWORD` / `secretKeyRef`, all placeholder values) |
| Least privilege | `deployments/Dockerfile` (`USER appuser`), `configurations/cloud-deployment-manifest.yaml` (`securityContext`) |
