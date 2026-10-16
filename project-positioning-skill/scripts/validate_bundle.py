#!/usr/bin/env python3
"""Validate schemas, rule field references, and bundled examples."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from validate_artifact import load_yaml


ARTIFACTS = {
    "coverage.yaml": "coverage.schema.yaml",
    "current.yaml": "positioning.schema.yaml",
}


def iter_rule_fields(node: object) -> Iterator[str]:
    if isinstance(node, dict):
        field = node.get("field")
        if isinstance(field, str):
            yield field
        for value in node.values():
            yield from iter_rule_fields(value)
    elif isinstance(node, list):
        for value in node:
            yield from iter_rule_fields(value)


def validate_document(
    document: object, schema: object, label: str
) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    messages: list[str] = []
    for error in validator.iter_errors(document):
        path = "/".join(str(part) for part in error.path) or "$"
        messages.append(f"{label}:{path}: {error.message}")
    return messages


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    schema_dir = root / "schemas"
    rule_dir = root / "rules"
    example_dir = root / "examples"

    schemas = {
        path.name: load_yaml(path)
        for path in sorted(schema_dir.glob("*.yaml"))
    }
    failures: list[str] = []

    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            failures.append(f"schemas/{name}: invalid JSON Schema: {exc.message}")

    coverage_schema = schemas["coverage.schema.yaml"]
    gate_schema = schemas["requirement_gate.schema.yaml"]
    coverage_dimensions = set(
        coverage_schema["$defs"]["coverage_item"]["properties"]["dimension"]["enum"]
    )
    gate_fields = set(gate_schema["properties"])

    for rule_name in ("level_rules.yaml", "conflict_rules.yaml"):
        rules = load_yaml(rule_dir / rule_name)
        unknown = sorted(set(iter_rule_fields(rules)) - coverage_dimensions)
        if unknown:
            failures.append(
                f"rules/{rule_name}: unknown coverage fields: {', '.join(unknown)}"
            )

    gate_rules = load_yaml(rule_dir / "gate_rules.yaml")
    unknown_gate_fields = sorted(set(iter_rule_fields(gate_rules)) - gate_fields)
    if unknown_gate_fields:
        failures.append(
            "rules/gate_rules.yaml: unknown gate fields: "
            + ", ".join(unknown_gate_fields)
        )

    load_yaml(rule_dir / "default_rules.yaml")

    positioning_schema = schemas["positioning.schema.yaml"]
    if "glossary" in positioning_schema.get("required", []):
        failures.append(
            "schemas/positioning.schema.yaml: glossary must stay optional so the skill "
            "works without requirement-analysis-skill"
        )

    positioning_without_glossary: list[str] = []

    for case_dir in sorted(path for path in example_dir.iterdir() if path.is_dir()):
        for file_name, schema_name in ARTIFACTS.items():
            artifact_path = case_dir / file_name
            if not artifact_path.exists():
                failures.append(f"{artifact_path}: missing required example artifact")
                continue
            artifact = load_yaml(artifact_path)
            failures.extend(
                validate_document(
                    artifact, schemas[schema_name], str(artifact_path)
                )
            )
            if file_name == "current.yaml" and isinstance(artifact, dict):
                if "glossary" not in artifact:
                    positioning_without_glossary.append(str(artifact_path))
            if file_name == "coverage.yaml" and isinstance(artifact, dict):
                covered = {
                    item.get("dimension")
                    for item in artifact.get("coverage", [])
                    if isinstance(item, dict)
                }
                skipped = {
                    item.get("dimension")
                    for item in artifact.get("skipped", [])
                    if isinstance(item, dict)
                }
                defaulted = {
                    item.get("dimension")
                    for item in artifact.get("defaults_applied", [])
                    if isinstance(item, dict)
                }
                missing_dimensions = sorted(
                    coverage_dimensions - covered - skipped - defaulted
                )
                if missing_dimensions:
                    failures.append(
                        f"{artifact_path}: unchecked dimensions: "
                        + ", ".join(missing_dimensions)
                    )
                overlap = sorted(skipped & defaulted)
                if overlap:
                    failures.append(
                        f"{artifact_path}: dimensions cannot be both skipped and defaulted: "
                        + ", ".join(overlap)
                    )
        for gate_path in sorted(case_dir.glob("*.yaml")):
            if gate_path.name in ARTIFACTS:
                continue
            failures.extend(
                validate_document(
                    load_yaml(gate_path),
                    schemas["requirement_gate.schema.yaml"],
                    str(gate_path),
                )
            )

    if not positioning_without_glossary:
        failures.append(
            "examples: at least one positioning card must omit glossary to prove the "
            "skill works standalone"
        )

    if failures:
        print("Bundle validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("Bundle validation passed: schemas, rules, and examples are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
