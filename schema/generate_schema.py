#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pydantic>=2.0", "typer>=0.15"]
# ///
"""Generate JSON Schema from Pydantic models for values.yaml validation."""

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

# Ensure schema directory is importable
sys.path.insert(0, str(Path(__file__).parent))

from models import HelmValues

app = typer.Typer(help="Generate JSON schema from Pydantic models.")


@app.command()
def generate(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output path for the schema file."),
    ] = Path(__file__).parent.parent / "values.schema.json",
) -> None:
    """Generate values.schema.json from Pydantic models."""
    schema = HelmValues.model_json_schema()

    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["title"] = "Golden Helm Chart Values"
    schema["description"] = "Schema for golden-chart Helm values.yaml"

    with open(output, "w") as f:
        json.dump(schema, f, indent=2)

    typer.echo(f"✓ Generated JSON schema: {output}")


if __name__ == "__main__":
    app()
