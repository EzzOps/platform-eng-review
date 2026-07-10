# Platform Engineering Multi-Agent PR Review

A **GitHub Actions-powered multi-agent PR review pipeline** that catches security issues, CNCF best practice violations, and code quality problems — all before a human reviewer looks at it.

## How It Works

On every PR, three review jobs run in **parallel**:

| Job | What it checks |
|-----|---------------|
| 🔒 **Security Review** | Dockerfile (root user, pinned images, secrets). K8s manifests (securityContext, capabilities). Terraform (backend, hardcoded secrets). CI/CD (injection vectors). |
| ✅ **CNCF Best Practices** | Resource limits, probes, graceful shutdown, pod disruption budgets, topology spread, labels, ConfigMaps. |
| 📋 **Code Quality** | Debug artifacts, TODO/FIXME markers, large files, error handling, hardcoded credentials, YAML indentation. |

Results are **aggregated** into a single PR comment with a verdict.

## Architecture

```
Pull Request opened
        │
        ▼
┌─────────────────────────────────────────────┐
│  pr-review.yaml (GitHub Actions Workflow)    │
│                                             │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Security  │  │  CNCF    │  │  Quality │ │
│  │  Review    │  │  Review  │  │  Review  │ │
│  └─────┬──────┘  └────┬─────┘  └────┬─────┘ │
│        │              │              │        │
│        └──────────────┴──────────────┘        │
│                        │                      │
│                   ┌────▼─────┐                │
│                   │ Aggregate│                │
│                   │ & Post   │                │
│                   └──────────┘                │
│                        │                      │
│                        ▼                      │
│              PR Comment with review           │
└──────────────────────────────────────────────┘
```

## Setup

1. Push this repo to GitHub (already done)
2. The workflow runs automatically on every PR
3. Review results are posted as PR comments

No API keys, no external services, no LLM costs — pure Python pattern matching.

## Local Testing

```bash
# Simulate a PR review locally
FILES=$(git diff --name-only main...HEAD | tr '\n' ' ')
python3 .github/workflows/scripts/security-review.py $FILES
python3 .github/workflows/scripts/cncf-review.py $FILES
python3 .github/workflows/scripts/quality-review.py $FILES
```

## Sample Files

The `infrastructure/` and `examples/` directories contain intentionally flawed code to validate the pipeline:

- `infrastructure/docker/Dockerfile` — insecure Dockerfile (root, secrets, unpinned)
- `infrastructure/kubernetes/insecure-deployment.yaml` — k8s without securityContext
- `infrastructure/kubernetes/secure-deployment.yaml` — k8s following all CNCF best practices
- `infrastructure/terraform/main.tf` — Terraform with no backend + hardcoded secrets
- `examples/test-script.py` — Python with debug artifacts + hardcoded token
- `.github/workflows/ci-injection-test.yaml` — CI/CD with injection vectors
