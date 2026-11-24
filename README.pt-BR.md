🌐 [English](README.md) | **Português (BR)**

# devops-automation-pipeline

Pipeline completo de automação DevOps com scripts em Python, containerização com Docker, orquestração com Kubernetes, CI/CD com GitHub Actions e infraestrutura como código.

## O que tem aqui

| Área | Local | Descrição |
|------|-------|-----------|
| CLI de automação | `automation/` | Comandos `health`, `backup` e `deploy` |
| Configuração | `config/services.yaml` | Serviços a monitorar, origens de backup e configurações de deploy |
| Contêineres | `Dockerfile`, `docker-compose.yml` | Imagem sem root e uma stack de demonstração local |
| Kubernetes | `k8s/` | Deployment (rolling update, probes, limites), Service e HPA |
| CI/CD | `.github/workflows/` | Testes + build da imagem + validação do Terraform; workflow de deploy manual |
| IaC | `terraform/` | Repositório ECR e bucket S3 versionado para backups, com regra de ciclo de vida |
| Testes | `tests/` | Suíte pytest (health checks, backups, renderização de manifestos) |

## Início rápido

```bash
pip install -r requirements.txt
python -m pytest -q

python -m automation health                  # código de saída 1 se algum serviço estiver indisponível
python -m automation backup                  # tar.gz + rotação (mantém os N mais recentes)
python -m automation deploy --tag v1.0.0     # dry-run: imprime os manifestos renderizados
python -m automation deploy --tag v1.0.0 --apply   # kubectl apply + rollout status
```

Stack de demonstração local: `docker compose up --build` sobe um alvo nginx e roda o health check contra ele.

## Pipeline

1. **CI** (`ci.yml`): roda o pytest, faz o build da imagem Docker (enviada ao GHCR a partir da `main`) e valida o Terraform.
2. **Deploy** (`deploy.yml`): disparado manualmente com uma tag de imagem; renderiza os manifestos, aplica com `kubectl` e depois roda o health check.

Os templates de manifesto em `k8s/` usam os placeholders `__IMAGE__`, `__NAMESPACE__`, `__REPLICAS__` e `__PORT__`, preenchidos a partir de `config/services.yaml`.

## Infraestrutura

```bash
cd terraform
terraform init
terraform plan
```

Cria um repositório ECR com tags imutáveis e scan no push, e um bucket S3 versionado que expira os backups após `backup_retention_days`.

## Histórico de desenvolvimento

Este projeto foi desenvolvido localmente entre 26/11/2025 e 06/12/2025. O histórico de commits foi criado depois, e as datas dos commits foram ajustadas para corresponder ao período em que o trabalho foi realmente feito.
