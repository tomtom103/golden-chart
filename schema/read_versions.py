#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["typer>=0.15"]
# ///
"""Read supported versions from supported-k8s-versions.json."""
import json
from pathlib import Path
from typing import Annotated

import typer

VERSIONS_FILE = Path(__file__).parent.parent / "supported-k8s-versions.json"

app = typer.Typer(help="Read supported versions from supported-k8s-versions.json.")


@app.command()
def read(
    component: Annotated[
        str,
        typer.Argument(help="Component to read versions for: 'kubernetes' or 'istio'."),
    ] = "kubernetes",
) -> None:
    """Print supported versions for the given component."""
    data = json.loads(VERSIONS_FILE.read_text())

    if component in ("istio", "kubernetes"):
        typer.echo(" ".join(data[component]["versions"]))
    else:
        typer.echo(f"Unknown component: {component}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
