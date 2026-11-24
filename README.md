🌐 **English** | [Português (BR)](README.pt-BR.md)

# devops-automation-pipeline

Complete DevOps automation pipeline with Python scripts, Docker containerization, Kubernetes orchestration, CI/CD with GitHub Actions, and infrastructure as code.

## What's inside

| Area | Location | Description |
|------|----------|-------------|
| Automation CLI | `automation/` | `health`, `backup` and `deploy` commands |
| Config | `config/services.yaml` | Services to monitor, backup sources, deploy settings |
| Containers | `Dockerfile`, `docker-compose.yml` | Non-root image and a local demo stack |
| Kubernetes | `k8s/` | Deployment (rolling update, probes, limits), Service, HPA |
| CI/CD | `.github/workflows/` | Tests + image build + Terraform validate; manual deploy workflow |
| IaC | `terraform/` | ECR repository and versioned S3 backup bucket with lifecycle rule |
| Tests | `tests/` | pytest suite (health checks, backups, manifest rendering) |

## Quick start

```bash
pip install -r requirements.txt
python -m pytest -q

python -m automation health                  # exit code 1 if any service is unhealthy
python -m automation backup                  # tar.gz + rotation (keeps the newest N)
python -m automation deploy --tag v1.0.0     # dry-run: prints the rendered manifests
python -m automation deploy --tag v1.0.0 --apply   # kubectl apply + rollout status
```

Local demo stack: `docker compose up --build` starts an nginx target and runs the health check against it.

## Pipeline

1. **CI** (`ci.yml`): run pytest, build the Docker image (pushed to GHCR from `main`), validate Terraform.
2. **Deploy** (`deploy.yml`): manually dispatched with an image tag; renders manifests, applies them with `kubectl`, then runs the health check.

Manifest templates in `k8s/` use `__IMAGE__`, `__NAMESPACE__`, `__REPLICAS__` and `__PORT__` placeholders filled from `config/services.yaml`.

## Infrastructure

```bash
cd terraform
terraform init
terraform plan
```

Creates an immutable-tag ECR repository with scan-on-push and a versioned S3 bucket that expires backups after `backup_retention_days`.

## Development history

This project was developed locally between 2025-11-26 and 2025-12-06. The commit history was created afterwards, and the commit dates were adjusted to match the period in which the work was actually done.
