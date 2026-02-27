#!/usr/bin/env python3
"""Open Contract Validator

Validates contract YAML files to ensure they meet the required schema.
"""

import sys
import os

REQUIRED_TOP_LEVEL_FIELDS = ["name", "version", "endpoints"]
REQUIRED_ENDPOINT_FIELDS = ["path", "method", "responses"]
VALID_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}


def load_yaml(filepath):
    """Load a YAML or JSON file."""
    if filepath.endswith(".json"):
        import json
        with open(filepath, "r") as f:
            return json.load(f)

    try:
        import yaml
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    except ImportError:
        raise RuntimeError(
            "PyYAML is not installed. Install it with: pip install pyyaml"
        )


def validate_contract(contract, filepath):
    """Validate a contract dictionary. Returns a list of error messages."""
    errors = []

    if not isinstance(contract, dict):
        errors.append(f"{filepath}: Contract must be a YAML mapping at the top level.")
        return errors

    # Check required top-level fields
    for field in REQUIRED_TOP_LEVEL_FIELDS:
        if field not in contract:
            errors.append(f"{filepath}: Missing required field '{field}'.")

    # Validate endpoints if present
    endpoints = contract.get("endpoints")
    if endpoints is not None:
        if not isinstance(endpoints, list):
            errors.append(f"{filepath}: 'endpoints' must be a list.")
        else:
            for i, endpoint in enumerate(endpoints):
                prefix = f"{filepath}: endpoint[{i}]"
                if not isinstance(endpoint, dict):
                    errors.append(f"{prefix}: Each endpoint must be a mapping.")
                    continue
                for field in REQUIRED_ENDPOINT_FIELDS:
                    if field not in endpoint:
                        errors.append(f"{prefix}: Missing required field '{field}'.")
                method = endpoint.get("method", "").upper()
                if method and method not in VALID_METHODS:
                    errors.append(
                        f"{prefix}: Invalid HTTP method '{method}'. "
                        f"Must be one of {sorted(VALID_METHODS)}."
                    )
                responses = endpoint.get("responses")
                if responses is not None and not isinstance(responses, list):
                    errors.append(f"{prefix}: 'responses' must be a list.")

    return errors


def validate_file(filepath):
    """Validate a single contract file. Returns True if valid, False otherwise."""
    if not os.path.isfile(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return False

    try:
        contract = load_yaml(filepath)
    except Exception as e:
        print(f"ERROR: Could not parse '{filepath}': {e}", file=sys.stderr)
        return False

    errors = validate_contract(contract, filepath)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return False

    print(f"OK: '{filepath}' is valid.")
    return True


def main():
    if len(sys.argv) < 2:
        # Default: validate all contracts in the contracts/ directory
        contracts_dir = os.path.join(os.path.dirname(__file__), "contracts")
        if not os.path.isdir(contracts_dir):
            print("No contract files specified and 'contracts/' directory not found.")
            sys.exit(1)
        files = [
            os.path.join(contracts_dir, f)
            for f in os.listdir(contracts_dir)
            if f.endswith(".yml") or f.endswith(".yaml") or f.endswith(".json")
        ]
        if not files:
            print("No contract files found in 'contracts/' directory.")
            sys.exit(1)
    else:
        files = sys.argv[1:]

    all_valid = all(validate_file(f) for f in files)
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
