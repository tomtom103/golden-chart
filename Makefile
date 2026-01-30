.PHONY: help lint test template schema validate clean

.DEFAULT_GOAL := help

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

setup: ## Install helm-unittest plugin and Python dependencies
	@helm plugin list | grep -q unittest || helm plugin install --verify=false https://github.com/helm-unittest/helm-unittest.git
	@pip3 install -q pydantic pyyaml

lint: ## Lint the Helm chart
	@helm lint .

test: ## Run unit tests
	@helm unittest .

template: ## Render templates with default values
	@helm template test-release .

schema: ## Generate values.schema.json from Pydantic model
	@python3 schema/generate_schema.py

validate: ## Validate example values files
	@echo "Validating example values files..."
	@python3 schema/validate.py examples/values-dev.yaml
	@echo ""
	@python3 schema/validate.py examples/values-staging.yaml
	@echo ""
	@python3 schema/validate.py examples/values-production.yaml
	@echo ""
	@python3 schema/validate.py examples/values-comprehensive.yaml

clean: ## Remove generated files
	@rm -f *.tgz values.schema.json
