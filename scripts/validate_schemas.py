#!/usr/bin/env python3
"""
Schema validator for AI Agent Framework contracts.

Validates workflow.schema.yaml, memory.api.json, plugin.manifest.json against their
internal self-validation and cross-compatibility. Integrates with CI via exit codes.

Requires: pip install jsonschema pyyaml
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Dict, Any

try:
    from jsonschema import validate, Draft7Validator
    import yaml
except ImportError as e:
    print(f"Missing dependencies: {e}. Install with 'pip install jsonschema pyyaml'")
    sys.exit(1)

from core.shared_utils import load_yaml_file

BASE_PATH = Path(__file__).parent.parent
SCHEMAS_DIR = BASE_PATH / "schemas"

def load_json_schema(path: Path) -> Dict[str, Any]:
    """Load JSON schema file."""
    with path.open("r") as f:
        return json.load(f)

def validate_yaml_against_schema(yaml_path: Path, schema: Dict[str, Any]) -> bool:
    """Validate YAML file against JSON schema."""
    try:
        data = load_yaml_file(yaml_path)
        validate(instance=data, schema=schema)
        return True
    except Exception as e:
        print(f"Validation failed for {yaml_path}: {e}")
        return False

def validate_self_referential_schemas():
    """Validate each schema against JSON Schema Draft 7."""
    validator = Draft7Validator
    results = {}
    
    # workflow.schema.yaml (YAML, but treat as JSON-like)
    workflow_schema_path = SCHEMAS_DIR / "workflow.schema.yaml"
    workflow_data = load_yaml_file(workflow_schema_path)
    try:
        validate(instance=workflow_data, schema=validator.SCHEMA)
        results["workflow"] = True
    except Exception as e:
        print(f"Self-validation failed for workflow.schema.yaml: {e}")
        results["workflow"] = False
    
    # memory.api.json
    memory_schema_path = SCHEMAS_DIR / "memory.api.json"
    memory_schema = load_json_schema(memory_schema_path)
    try:
        validate(instance=memory_schema, schema=validator.SCHEMA)
        results["memory"] = True
    except Exception as e:
        print(f"Self-validation failed for memory.api.json: {e}")
        results["memory"] = False
    
    # plugin.manifest.json
    plugin_schema_path = SCHEMAS_DIR / "plugin.manifest.json"
    plugin_schema = load_json_schema(plugin_schema_path)
    try:
        validate(instance=plugin_schema, schema=validator.SCHEMA)
        results["plugin"] = True
    except Exception as e:
        print(f"Self-validation failed for plugin.manifest.json: {e}")
        results["plugin"] = False
    
    return all(results.values())

def validate_cross_compatibility():
    """Basic cross-validation (e.g., version constraints)."""
    # Load schemas
    memory_schema = load_json_schema(SCHEMAS_DIR / "memory.api.json")
    plugin_schema = load_json_schema(SCHEMAS_DIR / "plugin.manifest.json")
    workflow_data = load_yaml_file(SCHEMAS_DIR / "workflow.schema.yaml")
    
    # Check version consistency (all v1.0.0)
    versions = [
        workflow_data.get("version", "unknown"),
        memory_schema.get("version", "unknown"),
        plugin_schema.get("version", "unknown")
    ]
    if not all(v == "1.0.0" for v in versions if v != "unknown"):
        print("Version mismatch: All schemas must be v1.0.0")
        return False
    
    # Check compat_matrix presence
    if "compat_matrix" not in workflow_data:
        print("workflow.schema.yaml missing compat_matrix")
        return False
    if "compat_matrix" not in memory_schema:
        print("memory.api.json missing compat_matrix")
        return False
    if "compat_matrix" not in plugin_schema:
        print("plugin.manifest.json missing compat_matrix")
        return False
    
    print("Cross-compatibility checks passed")
    return True

def main():
    """Run all validations."""
    print("Validating AI Agent Framework schemas...")
    
    if not validate_self_referential_schemas():
        print("Self-referential validation failed")
        sys.exit(1)
    
    if not validate_cross_compatibility():
        print("Cross-compatibility validation failed")
        sys.exit(1)
    
    print("All schema validations passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()