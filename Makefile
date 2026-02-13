.PHONY: help lint test template schema validate validate-k8s sync-crds clean setup \
	template-dev template-staging template-production \
	deploy-dev deploy-staging deploy-production

.DEFAULT_GOAL := help

CHART_DIR := .
RELEASE_NAME := golden-chart

# kubeconform schema location for local Istio CRD schemas
CRD_SCHEMA_LOCATION := schemas/{{.Group}}/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-22s %s\n", $$1, $$2}'

setup: ## Install helm-unittest plugin and kubeconform
	@helm plugin list | grep -q unittest || helm plugin install --verify=false https://github.com/helm-unittest/helm-unittest.git
	@command -v kubeconform >/dev/null 2>&1 || { echo "Install kubeconform: https://github.com/yannh/kubeconform#installation"; exit 1; }

lint: ## Lint the Helm chart
	@helm lint .

test: ## Run unit tests
	@helm unittest .

template: ## Render templates with default values
	@helm template test-release .

schema: ## Generate values.schema.json from Pydantic model
	@uv run schema/generate_schema.py

validate: ## Validate example values files against Pydantic schema
	@echo "Validating example values files..."
	@uv run schema/validate.py examples/values-dev.yaml
	@echo ""
	@uv run schema/validate.py examples/values-staging.yaml
	@echo ""
	@uv run schema/validate.py examples/values-production.yaml

sync-crds: ## Download Istio CRD schemas for kubeconform validation
	@uv run schema/sync_crds.py

validate-k8s: ## Validate rendered templates against K8s + Istio schemas (all supported versions)
	@command -v kubeconform >/dev/null 2>&1 || { echo "Error: kubeconform not found. Run 'make setup' or install from https://github.com/yannh/kubeconform"; exit 1; }
	@test -d schemas/ || { echo "Error: schemas/ directory not found. Run 'make sync-crds' first."; exit 1; }
	@for version in $$(uv run schema/read_versions.py kubernetes); do \
		echo "=== Validating against Kubernetes $$version ==="; \
		for values_file in examples/values-dev.yaml examples/values-staging.yaml examples/values-production.yaml; do \
			echo "  $$values_file:"; \
			helm template test . -f $$values_file 2>/dev/null | \
				kubeconform -strict -kubernetes-version $$version \
				-schema-location default \
				-schema-location '$(CRD_SCHEMA_LOCATION)' \
				-summary 2>&1 | sed 's/^/    /'; \
		done; \
		echo ""; \
	done

template-dev: ## Render templates with dev values
	@helm template $(RELEASE_NAME) $(CHART_DIR) -f examples/values-dev.yaml

template-staging: ## Render templates with staging values
	@helm template $(RELEASE_NAME) $(CHART_DIR) -f examples/values-staging.yaml

template-production: ## Render templates with production values
	@helm template $(RELEASE_NAME) $(CHART_DIR) -f examples/values-production.yaml

deploy-dev: ## Deploy to current cluster with dev values
	@helm upgrade --install $(RELEASE_NAME) $(CHART_DIR) -f examples/values-dev.yaml

deploy-staging: ## Deploy to current cluster with staging values
	@helm upgrade --install $(RELEASE_NAME) $(CHART_DIR) -f examples/values-staging.yaml

deploy-production: ## Deploy to current cluster with production values
	@helm upgrade --install $(RELEASE_NAME) $(CHART_DIR) -f examples/values-production.yaml

clean: ## Remove generated files
	@rm -f *.tgz values.schema.json
