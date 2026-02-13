# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Golden Chart is a production-ready Helm chart for Kubernetes deployments. It supports multiple deployments, services, CronJobs, Helm hooks, HPAs, Istio service mesh (Gateway, VirtualService, DestinationRule), and arbitrary extra resources from a single chart.

## Commands

```bash
make setup              # Install helm-unittest plugin and kubeconform
make lint               # Lint chart with helm lint
make test               # Run unit tests (helm-unittest)
make template           # Render templates with default values
make schema             # Generate values.schema.json from Pydantic models
make validate           # Validate example values against Pydantic schema
make validate-k8s       # Validate rendered templates against supported K8s versions
make template-dev       # Render templates with dev values
make template-staging   # Render templates with staging values
make template-production # Render templates with production values
make deploy-dev         # Deploy to current cluster with dev values
make deploy-staging     # Deploy to current cluster with staging values
make deploy-production  # Deploy to current cluster with production values
make clean              # Remove generated files
```

Run a single test file: `helm unittest tests/deployment_test.yaml .`

Python scripts use `uv run` with inline script dependencies (PEP 723).

## Architecture

### Map-based resource configuration

All major resources (deployments, services, configmaps, secrets, cronjobs, hooks, HPAs) are defined as maps in `values.yaml` where the key becomes part of the resource name:

```yaml
deployments:
  data-api: { image: { repository: data-platform/api, tag: v2.1.0 } }
  celery-worker: { image: { repository: data-platform/api, tag: v2.1.0 } }
```

### Top-level values structure

- `nameOverride`, `fullnameOverride`, `namespaceOverride` — at top level (NOT under `global`)
- `imagePullSecrets` — at top level
- `global` — only contains `labels` and `annotations`
- `defaults` — inherited by deployments (via `merge`/`deepCopy`) and by hooks/cronjobs (via `| default`)
- `cronjobs` — lowercase (not `cronJobs`)

### Defaults inheritance

- **Deployments**: `merge (deepCopy $deployment) (deepCopy $.Values.defaults)` — full deep merge
- **Hooks/CronJobs**: individual fields fall back via `$hook.field | default $.Values.defaults.field` for `resources`, `nodeSelector`, `tolerations`, `affinity`, and image

### Template helpers (`templates/_helpers.tpl`)

- `golden-chart.fullname` — release-prefixed name
- `golden-chart.labels` — common labels applied to all resources
- `golden-chart.resourceName` — generates `fullname-component` for component-specific names
- `golden-chart.serviceSelectorLabels` — service-to-deployment selectors
- `golden-chart.namespace` — respects `namespaceOverride`
- `golden-chart.imagePullSecrets` — renders imagePullSecrets block
- `golden-chart.resolveGateway` — resolves Istio gateway references

### Key directories

- `templates/` — Helm templates; `templates/istio/` for Istio resources
- `schema/` — Pydantic v2 models (`models.py`), `generate_schema.py`, `validate.py`, `read_versions.py`
- `examples/` — Data platform values files (dev, staging, production)
- `tests/` — helm-unittest test files

### Schema workflow

Edit `schema/models.py` (Pydantic v2) → run `make schema` → `values.schema.json` is regenerated. The schema provides IDE autocompletion for `values.yaml`.

### Kubernetes version validation

- `supported-k8s-versions.json` — declares supported K8s versions (programmatically updatable)
- `Chart.yaml` `kubeVersion` — Helm-level version constraint
- `make validate-k8s` — uses kubeconform to validate rendered templates against each supported K8s version's upstream JSON schemas (from yannh/kubernetes-json-schema)

## Conventions

- All resources check `{{- if ne ($resource.enabled | toString) "false" }}` — enabled by default unless explicitly disabled
- Templates iterate maps with `{{- range $key, $value := .Values.<resource> }}`
- Security defaults: non-root, read-only root filesystem, dropped capabilities
- Hook/cronjob image construction is inlined (not via helper) matching deployment.yaml pattern
- YAML uses 2-space indentation
- Python scripts use PEP 723 inline metadata for `uv run` compatibility
- Python code uses Pydantic v2, snake_case variables, PascalCase classes
