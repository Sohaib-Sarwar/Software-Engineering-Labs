# Cloud Computing Lab — Packaging, Deploying, and Scaling a Service

Part of the **Software-Engineering-Labs** repository. This branch is scoped to a single subject — it contains only the `Cloud-Computing/` lab and this README; the `main` branch holds all subjects.

## What's here

A small Flask service packaged for cloud deployment: a Dockerfile, a multi-container `docker-compose.yml`, and a Kubernetes-style deployment manifest illustrating scalability (replicas) and availability (readiness/liveness probes, resource limits).

```
Cloud-Computing/
├── deployments/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── configurations/
│   └── cloud-deployment-manifest.yaml
└── documentation/
    └── README.md
```

## Full write-up

See [`Cloud-Computing/documentation/README.md`](Cloud-Computing/documentation/README.md) for IaaS/PaaS/SaaS notes, scalability & availability strategies, basic cloud security notes, and exact commands to run the app directly, in Docker, via compose, and against the deployment manifest.
