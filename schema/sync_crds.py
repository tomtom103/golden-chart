#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0", "typer>=0.15"]
# ///
"""
Sync Istio CRD JSON schemas for kubeconform validation.

Downloads Istio CRDs for the version declared in supported-k8s-versions.json
and converts the embedded OpenAPI v3 validation schemas to standalone JSON schema
files compatible with kubeconform.

Output structure:
  schemas/
    networking.istio.io/
      gateway_v1beta1.json
      virtualservice_v1beta1.json
      destinationrule_v1beta1.json
      ...
"""

import json
import sys
import urllib.request
from pathlib import Path
from typing import Annotated, Optional

import typer
import yaml

REPO_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
VERSIONS_FILE = REPO_ROOT / "supported-k8s-versions.json"

# Istio CRD bundle URL pattern (per release branch)
ISTIO_CRD_URL = (
    "https://raw.githubusercontent.com/istio/istio/"
    "{branch}/manifests/charts/base/files/crd-all.gen.yaml"
)

app = typer.Typer(help="Sync Istio CRD JSON schemas for kubeconform.")


def get_istio_version() -> str:
    """Read Istio version from supported-k8s-versions.json."""
    data = json.loads(VERSIONS_FILE.read_text())
    return data["istio"]["version"]


def download_crds(version: str) -> str:
    """Download the Istio CRD bundle for a given version."""
    parts = version.split(".")
    branch = f"release-{parts[0]}.{parts[1]}"
    url = ISTIO_CRD_URL.format(branch=branch)

    typer.echo(f"Downloading Istio CRDs from {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "golden-chart/1.0"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def openapi_to_jsonschema(openapi_schema: dict) -> dict:
    """
    Convert an OpenAPI v3 validation schema (from a CRD) to a JSON Schema
    compatible with kubeconform.
    """
    if not isinstance(openapi_schema, dict):
        return openapi_schema

    result = {}
    for key, value in openapi_schema.items():
        if key == "x-kubernetes-preserve-unknown-fields":
            result["x-kubernetes-preserve-unknown-fields"] = value
            continue
        if key.startswith("x-"):
            continue
        if key in ("properties", "additionalProperties") and isinstance(value, dict):
            if key == "properties":
                result[key] = {
                    k: openapi_to_jsonschema(v) for k, v in value.items()
                }
            else:
                result[key] = openapi_to_jsonschema(value)
        elif key == "items" and isinstance(value, dict):
            result["items"] = openapi_to_jsonschema(value)
        elif key in ("oneOf", "anyOf", "allOf") and isinstance(value, list):
            result[key] = [openapi_to_jsonschema(v) for v in value]
        else:
            result[key] = value

    return result


def extract_schemas(crd_yaml: str) -> list[dict]:
    """Extract JSON schemas from CRD definitions."""
    schemas = []
    for doc in yaml.safe_load_all(crd_yaml):
        if not doc or doc.get("kind") != "CustomResourceDefinition":
            continue

        spec = doc.get("spec", {})
        group = spec.get("group", "")
        kind = spec.get("names", {}).get("kind", "")

        if not group or not kind:
            continue

        for ver_entry in spec.get("versions", []):
            version = ver_entry.get("name", "")
            openapi_schema = (
                ver_entry.get("schema", {}).get("openAPIV3Schema", {})
            )

            if not version or not openapi_schema:
                continue

            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "description": f"{kind} ({group}/{version})",
                "type": "object",
                "x-kubernetes-group-version-kind": [
                    {
                        "group": group,
                        "kind": kind,
                        "version": version,
                    }
                ],
            }

            converted = openapi_to_jsonschema(openapi_schema)
            if "properties" in converted:
                json_schema["properties"] = converted["properties"]
            if "required" in converted:
                json_schema["required"] = converted["required"]
            if "type" in converted:
                json_schema["type"] = converted["type"]

            schemas.append(
                {
                    "group": group,
                    "kind": kind.lower(),
                    "version": version,
                    "schema": json_schema,
                }
            )

    return schemas


def write_schemas(schemas: list[dict], output_dir: Path) -> None:
    """Write schemas to disk in kubeconform-compatible layout."""
    for entry in schemas:
        group_dir = output_dir / entry["group"]
        group_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{entry['kind']}_{entry['version']}.json"
        filepath = group_dir / filename
        filepath.write_text(json.dumps(entry["schema"], indent=2) + "\n")


@app.command()
def sync(
    version: Annotated[
        Optional[str],
        typer.Argument(help="Istio version to sync (e.g. 1.24.0). Reads from supported-k8s-versions.json if omitted."),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", "-o", help="Output directory for schemas."),
    ] = SCHEMAS_DIR,
) -> None:
    """Download Istio CRDs and convert to kubeconform-compatible JSON schemas."""
    resolved_version = version or get_istio_version()
    typer.echo(f"Syncing Istio CRD schemas for version {resolved_version}")

    crd_yaml = download_crds(resolved_version)
    schemas = extract_schemas(crd_yaml)

    if not schemas:
        typer.echo("Error: No schemas extracted from CRDs", err=True)
        raise typer.Exit(code=1)

    write_schemas(schemas, output_dir)

    groups: dict[str, list[str]] = {}
    for s in schemas:
        groups.setdefault(s["group"], []).append(f"{s['kind']}_{s['version']}")

    typer.echo(f"\nWrote {len(schemas)} schemas to {output_dir}/")
    for group, kinds in sorted(groups.items()):
        typer.echo(f"  {group}/: {', '.join(sorted(kinds))}")


if __name__ == "__main__":
    app()
