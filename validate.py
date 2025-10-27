#!/usr/bin/env python3
import os
import sys
import json
import re

# We need a YAML loader. To avoid a dependency on app.py, we can include a simple one here.
# This loader should be robust enough for our known file structures.
def _yaml_load(text: str) -> dict:
    """
    A robust YAML loader that tries to use PyYAML if available,
    but falls back to a basic parser for our specific structure.
    """
    try:
        import yaml
        return yaml.safe_load(text) or {}
    except ImportError:
        # This fallback is intentionally simple and may not cover all YAML features.
        # It's designed for the key-value and list structures in our project.
        data: dict = {}
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line.strip() or line.strip().startswith('#'):
                i += 1
                continue

            match = re.match(r'^(\s*)(\S+):\s*(.*)', line)
            if not match:
                i += 1
                continue

            indent, key, value = match.groups()

            if value:
                data[key] = value.strip('\'"')
                i += 1
            else:
                # It's a block, could be a list or dict
                block_lines = []
                j = i + 1
                while j < len(lines) and (not lines[j].strip() or len(re.match(r'^(\s*)', lines[j]).group(1)) > len(indent)):
                    block_lines.append(lines[j])
                    j += 1

                # Check if it's a list
                if block_lines and block_lines[0].strip().startswith('-'):
                    data[key] = [item.strip()[2:] for item in block_lines]
                else: # Assume it's a dictionary
                    sub_yaml = "\n".join([l.strip() for l in block_lines])
                    data[key] = _yaml_load(sub_yaml)
                i = j
        return data


def load_yaml_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return _yaml_load(f.read())

def main():
    # This script must be run from the root of the repository.
    try:
        from jsonschema import validate, ValidationError
    except ImportError:
        print("Error: jsonschema is not installed. Please run 'pip install jsonschema'", file=sys.stderr)
        sys.exit(1)

    print("--- Running Configuration Validator ---")

    # Load schemas
    try:
        with open('schemas/role_schema.json', 'r') as f:
            role_schema = json.load(f)
        with open('schemas/tool_schema.json', 'r') as f:
            tool_schema = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: Could not load schema files. Make sure you are in the repo root.", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)

    error_count = 0

    # Validate roles
    print("\nValidating roles in /role/...")
    for root, _, files in os.walk('role'):
        for file in files:
            if file.endswith('.yaml'):
                path = os.path.join(root, file)
                try:
                    instance = load_yaml_file(path)
                    validate(instance=instance, schema=role_schema)
                    print(f"  ✅ {path}")
                except (ValidationError, Exception) as e:
                    print(f"  ❌ {path} - Validation Failed!")
                    print(f"     {e}")
                    error_count += 1

    # Validate tools
    print("\nValidating tools in /tool_definitions/...")
    for root, _, files in os.walk('tool_definitions'):
        for file in files:
            if file.endswith('.yaml'):
                path = os.path.join(root, file)
                try:
                    instance = load_yaml_file(path)
                    validate(instance=instance, schema=tool_schema)
                    print(f"  ✅ {path}")
                except (ValidationError, Exception) as e:
                    print(f"  ❌ {path} - Validation Failed!")
                    print(f"     {e}")
                    error_count += 1

    # Validate prompts
    print("\nValidating prompts in /prompt/...")
    for root, _, files in os.walk('prompt'):
        for file in files:
            if file.endswith('.yaml'):
                path = os.path.join(root, file)
                try:
                    instance = load_yaml_file(path)
                    # Basic validation for prompt structure
                    if 'name' not in instance:
                        raise ValidationError("Missing required field: name")
                    if 'persona' not in instance:
                        raise ValidationError("Missing required field: persona")
                    if 'prompt' not in instance:
                        raise ValidationError("Missing required field: prompt")
                    print(f"  ✅ {path}")
                except (ValidationError, Exception) as e:
                    print(f"  ❌ {path} - Validation Failed!")
                    print(f"     {e}")
                    error_count += 1

    # Validate rules
    print("\nValidating rules in /rule/...")
    for root, _, files in os.walk('rule'):
        for file in files:
            if file.endswith('.md'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Basic validation for rule structure
                    if not content.startswith('---'):
                        raise ValidationError("Rule file must start with frontmatter")
                    lines = content.split('\n')
                    if len(lines) < 3 or not lines[1].startswith('name:'):
                        raise ValidationError("Rule file must have name in frontmatter")
                    print(f"  ✅ {path}")
                except (ValidationError, Exception) as e:
                    print(f"  ❌ {path} - Validation Failed!")
                    print(f"     {e}")
                    error_count += 1

    # Validate config files
    print("\nValidating config files in /config/...")
    if os.path.exists('config'):
        for root, _, files in os.walk('config'):
            for file in files:
                if file.endswith('.yaml'):
                    path = os.path.join(root, file)
                    try:
                        instance = load_yaml_file(path)
                        # Basic validation for config structure
                        if not isinstance(instance, dict):
                            raise ValidationError("Config file must contain a dictionary")
                        print(f"  ✅ {path}")
                    except (ValidationError, Exception) as e:
                        print(f"  ❌ {path} - Validation Failed!")
                        print(f"     {e}")
                        error_count += 1
                elif file.endswith('.json'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            json.load(f)
                        print(f"  ✅ {path}")
                    except Exception as e:
                        print(f"  ❌ {path} - Validation Failed!")
                        print(f"     {e}")
                        error_count += 1

    if error_count > 0:
        print(f"\n--- Validation Complete: Found {error_count} errors. ---")
        sys.exit(1)
    else:
        print("\n--- Validation Complete: All configuration files are valid! ---")

if __name__ == "__main__":
    main()
