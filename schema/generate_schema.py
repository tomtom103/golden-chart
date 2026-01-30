#!/usr/bin/env python3
"""
Generate JSON Schema from Pydantic models for values.yaml validation
This schema can be used by YAML LSP servers for autocomplete and validation
"""

import json
import sys
from pathlib import Path

try:
    from models import HelmValues
except ImportError:
    print(
        "Error: Could not import models. Make sure you're running from the schema directory or it's in PYTHONPATH"
    )
    sys.exit(1)


def generate_schema():
    """Generate JSON schema from Pydantic model"""
    schema = HelmValues.model_json_schema()

    # Add schema metadata
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"
    schema["title"] = "Golden Helm Chart Values"
    schema["description"] = "Schema for golden-chart Helm values.yaml"

    return schema


def main():
    # Generate schema
    schema = generate_schema()

    # Write to values.schema.json in chart root
    schema_path = Path(__file__).parent.parent / "values.schema.json"

    with open(schema_path, "w") as f:
        json.dump(schema, f, indent=2)

    print(f"✓ Generated JSON schema: {schema_path}")
    print(f"✓ Schema contains {len(schema.get('properties', {}))} top-level properties")


if __name__ == "__main__":
    main()
