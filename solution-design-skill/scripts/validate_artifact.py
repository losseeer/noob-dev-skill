#!/usr/bin/env python3
"""Validate a solution-design YAML artifact against its schema."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
    from jsonschema.exceptions import SchemaError
except ImportError as exc:
    print(
        "Missing dependency. Install scripts/requirements.txt in an isolated environment.",
        file=sys.stderr,
    )
    print(f"Import error: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc


SCHEMA_FILES = {
    "current": "current.schema.yaml",
    "stack": "stack.schema.yaml",
    "data_model": "data-model.schema.yaml",
    "interfaces": "interfaces.schema.yaml",
    "review": "review.schema.yaml",
}


class ArtifactLoader(yaml.SafeLoader):
    """Keep dates as strings so `YYYY-MM-DD` can be written unquoted in YAML."""


ArtifactLoader.yaml_implicit_resolvers = {
    tag: [rule for rule in rules if rule[0] != "tag:yaml.org,2002:timestamp"]
    for tag, rules in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a solution-design YAML artifact."
    )
    parser.add_argument(
        "kind",
        choices=sorted(SCHEMA_FILES),
        help="Artifact kind and schema to use.",
    )
    parser.add_argument("artifact", type=Path, help="YAML artifact path.")
    return parser.parse_args()


def load_yaml(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.load(handle, Loader=ArtifactLoader)
    except FileNotFoundError as exc:
        print(f"File not found: {path}", file=sys.stderr)
        raise SystemExit(2) from exc
    except yaml.YAMLError as exc:
        print(f"Invalid YAML in {path}: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def format_path(parts: object) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def error_sort_key(error: object) -> tuple[int, str]:
    path = getattr(error, "path", ())
    return len(path), "/".join(str(part) for part in path)


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    schema_path = skill_root / "schemas" / SCHEMA_FILES[args.kind]

    schema = load_yaml(schema_path)
    artifact = load_yaml(args.artifact.resolve())

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        print(f"Schema is invalid: {schema_path}", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 2

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(artifact), key=error_sort_key)
    if errors:
        print(f"Validation failed: {args.artifact}", file=sys.stderr)
        for error in errors:
            print(f"- {format_path(error.path)}: {error.message}", file=sys.stderr)
        return 1

    print(f"Validation passed: {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
