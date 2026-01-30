#!/usr/bin/env python3
"""
Validation script for Helm values files using Pydantic models.

Usage:
    python schema/validate.py values.yaml
    python schema/validate.py examples/values-dev.yaml
    python schema/validate.py examples/values-production.yaml
"""

import sys
import yaml
from pathlib import Path
from typing import Any
from pydantic import ValidationError

# Add schema directory to path
schema_dir = Path(__file__).parent
sys.path.insert(0, str(schema_dir))

from models import HelmValues


def load_yaml_file(file_path: str) -> dict[str, Any]:
    """Load YAML file and return as dictionary."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f) or {}


def validate_values(values_dict: dict[str, Any], file_path: str) -> bool:
    """
    Validate values dictionary against Pydantic model.

    Returns:
        True if validation succeeds, False otherwise.
    """
    try:
        # Validate the values
        helm_values = HelmValues(**values_dict)

        print(f"✅ Validation successful for {file_path}")
        print(f"\nSummary:")

        # Print resource counts
        if helm_values.deployments:
            print(f"  - Deployments: {len(helm_values.deployments)}")
        if helm_values.services:
            print(f"  - Services: {len(helm_values.services)}")
        if helm_values.configMaps:
            print(f"  - ConfigMaps: {len(helm_values.configMaps)}")
        if helm_values.secrets:
            print(f"  - Secrets: {len(helm_values.secrets)}")
        if helm_values.cronjobs:
            print(f"  - CronJobs: {len(helm_values.cronjobs)}")
        if helm_values.horizontalPodAutoscalers:
            print(f"  - HPAs: {len(helm_values.horizontalPodAutoscalers)}")

        if helm_values.istio and helm_values.istio.enabled:
            print(f"  - Istio enabled: Yes")
            if helm_values.istio.gateways:
                print(f"    - Gateways: {len(helm_values.istio.gateways)}")
            if helm_values.istio.virtualServices:
                print(
                    f"    - VirtualServices: {len(helm_values.istio.virtualServices)}"
                )
            if helm_values.istio.destinationRules:
                print(
                    f"    - DestinationRules: {len(helm_values.istio.destinationRules)}"
                )

        return True

    except ValidationError as e:
        print(f"❌ Validation failed for {file_path}\n")
        print("Errors:")
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            print(f"  - {location}: {error['msg']}")
            if "input" in error:
                print(f"    Input value: {error['input']}")

        return False
    except Exception as e:
        print(f"❌ Unexpected error validating {file_path}: {e}")
        return False


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python schema/validate.py <values-file.yaml>")
        print("\nExamples:")
        print("  python schema/validate.py values.yaml")
        print("  python schema/validate.py examples/values-dev.yaml")
        print("  python schema/validate.py examples/values-production.yaml")
        sys.exit(1)

    file_path = sys.argv[1]

    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    print(f"Validating {file_path}...\n")

    # Load YAML file
    try:
        values_dict = load_yaml_file(file_path)
    except yaml.YAMLError as e:
        print(f"❌ Failed to parse YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to load file: {e}")
        sys.exit(1)

    # Validate values
    success = validate_values(values_dict, file_path)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
