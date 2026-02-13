#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic>=2.0", "pyyaml>=6.0", "typer>=0.15"]
# ///
"""Validate Helm values files against Pydantic models."""

import sys
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from pydantic import ValidationError

# Add schema directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models import HelmValues

app = typer.Typer(help="Validate Helm values files against the Pydantic schema.")


def load_yaml_file(file_path: Path) -> dict[str, Any]:
    """Load YAML file and return as dictionary."""
    with open(file_path, "r") as f:
        return yaml.safe_load(f) or {}


def validate_values(values_dict: dict[str, Any], file_path: str) -> bool:
    """Validate values dictionary against Pydantic model."""
    try:
        helm_values = HelmValues(**values_dict)

        typer.echo(f"✅ Validation successful for {file_path}")
        typer.echo(f"\nSummary:")

        if helm_values.deployments:
            typer.echo(f"  - Deployments: {len(helm_values.deployments)}")
        if helm_values.services:
            typer.echo(f"  - Services: {len(helm_values.services)}")
        if helm_values.configMaps:
            typer.echo(f"  - ConfigMaps: {len(helm_values.configMaps)}")
        if helm_values.secrets:
            typer.echo(f"  - Secrets: {len(helm_values.secrets)}")
        if helm_values.cronjobs:
            typer.echo(f"  - CronJobs: {len(helm_values.cronjobs)}")
        if helm_values.horizontalPodAutoscalers:
            typer.echo(f"  - HPAs: {len(helm_values.horizontalPodAutoscalers)}")

        if helm_values.istio and helm_values.istio.enabled:
            typer.echo(f"  - Istio enabled: Yes")
            if helm_values.istio.gateways:
                typer.echo(f"    - Gateways: {len(helm_values.istio.gateways)}")
            if helm_values.istio.virtualServices:
                typer.echo(
                    f"    - VirtualServices: {len(helm_values.istio.virtualServices)}"
                )
            if helm_values.istio.destinationRules:
                typer.echo(
                    f"    - DestinationRules: {len(helm_values.istio.destinationRules)}"
                )

        return True

    except ValidationError as e:
        typer.echo(f"❌ Validation failed for {file_path}\n", err=True)
        typer.echo("Errors:", err=True)
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            typer.echo(f"  - {location}: {error['msg']}", err=True)
            if "input" in error:
                typer.echo(f"    Input value: {error['input']}", err=True)

        return False
    except Exception as e:
        typer.echo(f"❌ Unexpected error validating {file_path}: {e}", err=True)
        return False


@app.command()
def validate(
    values_file: Annotated[
        Path,
        typer.Argument(help="Path to the values YAML file to validate."),
    ],
) -> None:
    """Validate a Helm values file against the Pydantic schema."""
    if not values_file.exists():
        typer.echo(f"❌ File not found: {values_file}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Validating {values_file}...\n")

    try:
        values_dict = load_yaml_file(values_file)
    except yaml.YAMLError as e:
        typer.echo(f"❌ Failed to parse YAML file: {e}", err=True)
        raise typer.Exit(code=1)

    success = validate_values(values_dict, str(values_file))
    if not success:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
