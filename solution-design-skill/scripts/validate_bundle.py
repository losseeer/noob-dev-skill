#!/usr/bin/env python3
"""Validate schemas, cross-artifact references, and bundled examples.

Run from inside scripts/ (it imports validate_artifact), or via absolute path.

    python validate_bundle.py            # validate schemas + rules + examples
    python validate_bundle.py --selftest # validate this checker itself
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Callable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from validate_artifact import load_yaml, SCHEMA_FILES


SCHEMA_FILES_PER_ARTIFACT = {
    "current.yaml": "current",
    "tech/stack.yaml": "stack",
    "tech/data-model.yaml": "data_model",
    "tech/interfaces.yaml": "interfaces",
}


# --------------------------------------------------------------------------
# cross-artifact checks (shared by real validation and by --selftest)
# --------------------------------------------------------------------------


def check_decision_refs(docs: dict) -> list[str]:
    current = docs.get("current") or {}
    have = docs.get("decision_files") or set()
    failures: list[str] = []

    missing = sorted(set(current.get("decisions") or []) - have)
    if missing:
        failures.append(
            "current.yaml: decisions reference nonexistent ADR files: "
            + ", ".join(missing)
        )

    for selection in (docs.get("stack") or {}).get("selections") or []:
        ref = selection.get("decision_ref")
        if ref and ref not in have:
            failures.append(
                f"stack/{selection.get('id')}: decision_ref {ref} has no file "
                "under decisions/"
            )
    return failures


def check_acceptance_coverage(docs: dict) -> list[str]:
    current = docs.get("current") or {}
    interfaces = docs.get("interfaces") or {}
    failures: list[str] = []

    registered = {
        item.get("acceptance_ref")
        for item in current.get("coverage") or []
        if item.get("acceptance_ref")
    }
    for iface in interfaces.get("interfaces") or []:
        for ref in iface.get("acceptance_refs") or []:
            if ref not in registered:
                failures.append(
                    f"interfaces/{iface.get('id')}: {ref} is claimed by an interface "
                    "but not registered in current.yaml coverage"
                )

    claimed: set[str] = set()
    for iface in interfaces.get("interfaces") or []:
        claimed.update(iface.get("acceptance_refs") or [])
    for entity in (docs.get("data_model") or {}).get("entities") or []:
        claimed.update(entity.get("source_refs") or [])

    for item in current.get("coverage") or []:
        if item.get("status") not in ("covered", "partial"):
            continue
        covered_by = item.get("covered_by") or {}
        substance = any(
            covered_by.get(key) for key in ("interfaces", "entities", "pages")
        )
        ref = item.get("acceptance_ref")
        if not substance and ref not in claimed:
            failures.append(
                f"current.yaml: {ref} is marked {item.get('status')} but no "
                "interface, entity, or page claims it"
            )
    return failures


def check_stack_selections(docs: dict) -> list[str]:
    failures: list[str] = []
    for selection in (docs.get("stack") or {}).get("selections") or []:
        if selection.get("basis") == "assumption" and not selection.get(
            "why_assumed"
        ):
            failures.append(
                f"stack/{selection.get('id')}: assumption without why_assumed"
            )
        if selection.get("confidence") == "low" and not selection.get("revisit_when"):
            failures.append(
                f"stack/{selection.get('id')}: low confidence without revisit_when"
            )
    return failures


def check_prototype_files(docs: dict) -> list[str]:
    current = docs.get("current") or {}
    proto = current.get("prototype") or {}
    if not proto.get("needed"):
        return []
    failures: list[str] = []
    pages = proto.get("pages") or []
    if not pages:
        failures.append(
            "current.yaml: prototype.needed is true but no pages are listed"
        )
    files = docs.get("prototype_files") or set()
    for page in pages:
        if page.get("file") not in files:
            failures.append(f"prototype: missing file {page.get('file')}")
    return failures


def check_assumption_followthrough(docs: dict) -> list[str]:
    current = docs.get("current") or {}
    failures: list[str] = []
    known = {item.get("id") for item in current.get("assumptions") or []}
    review = docs.get("review") or {}
    unknown = sorted(set(review.get("unresolved_assumptions") or []) - known)
    if unknown:
        failures.append(
            "review: unresolved_assumptions reference unknown IDs: "
            + ", ".join(unknown)
        )
    for item in current.get("assumptions") or []:
        if not item.get("mitigation"):
            failures.append(
                f"current.yaml: {item.get('id')} has impact_if_wrong but no mitigation"
            )
    return failures


ALL_CHECKS: list[Callable[[dict], list[str]]] = [
    check_decision_refs,
    check_acceptance_coverage,
    check_stack_selections,
    check_prototype_files,
    check_assumption_followthrough,
]


def run_checks(docs: dict) -> list[str]:
    failures: list[str] = []
    for check in ALL_CHECKS:
        failures.extend(check(docs))
    return failures


# --------------------------------------------------------------------------
# real validation
# --------------------------------------------------------------------------


def load_case(case_dir: Path) -> tuple[dict, list[str]]:
    failures: list[str] = []
    schemas_root = Path(__file__).resolve().parents[1] / "schemas"

    docs: dict = {}
    for rel, kind in SCHEMA_FILES_PER_ARTIFACT.items():
        path = case_dir / rel
        if not path.exists():
            failures.append(f"{path}: missing required example artifact")
            continue
        artifact = load_yaml(path)
        schema = load_yaml(schemas_root / SCHEMA_FILES[kind])
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for error in validator.iter_errors(artifact):
            pointer = "/".join(str(part) for part in error.path) or "$"
            failures.append(f"{rel}:{pointer}: {error.message}")
        docs["current" if rel == "current.yaml" else kind] = artifact

    for review_path in sorted((case_dir / "reviews").glob("*.yaml")):
        schema = load_yaml(schemas_root / SCHEMA_FILES["review"])
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        artifact = load_yaml(review_path)
        for error in validator.iter_errors(artifact):
            pointer = "/".join(str(part) for part in error.path) or "$"
            failures.append(f"reviews/{review_path.name}:{pointer}: {error.message}")
        docs.setdefault("review", artifact)

    docs["decision_files"] = {
        path.name.split("-")[0] + "-" + path.name.split("-")[1]
        for path in (case_dir / "decisions").glob("ADR-*.md")
    }
    proto_dir = case_dir / "prototype"
    docs["prototype_files"] = {
        path.name for path in proto_dir.glob("**/*") if path.is_file()
    }

    failures.extend(run_checks(docs))
    return docs, failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    schema_dir = root / "schemas"
    rules_dir = root / "rules"
    example_dir = root / "examples"

    failures: list[str] = []
    schemas = {
        path.name: load_yaml(path) for path in sorted(schema_dir.glob("*.yaml"))
    }
    for name, schema in schemas.items():
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            failures.append(f"schemas/{name}: invalid JSON Schema: {exc.message}")

    if not list(schema_dir.glob("*.yaml")):
        failures.append("schemas: no schema files found")
    if not list(rules_dir.glob("*.yaml")):
        failures.append("rules: no rule files found")

    for case_dir in sorted(path for path in example_dir.iterdir() if path.is_dir()):
        docs, case_failures = load_case(case_dir)
        failures.extend(case_failures)

    if failures:
        print("Bundle validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        "Bundle validation passed: schemas, cross-artifact references, "
        "and examples are consistent."
    )
    return 0


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------


BASE_CURRENT = {
    "version": 1,
    "as_of": "2026-10-16",
    "project": "demo",
    "upstream": {
        "positioning": {"status": "found", "ref": ".project/positioning/current.yaml"},
        "requirements": {"status": "found", "ref": ".project/requirements/"},
    },
    "summary": "demo design",
    "coverage": [
        {
            "acceptance_ref": "AC-001",
            "requirement_ref": "REQ-001",
            "status": "covered",
            "covered_by": {"interfaces": ["IF-001"]},
        }
    ],
    "decisions": ["ADR-001"],
    "prototype": {
        "needed": True,
        "stack": "html",
        "pages": [
            {
                "name": "home",
                "file": "index.html",
                "covers": ["REQ-001"],
                "review_status": "pending",
            }
        ],
    },
    "assumptions": [
        {
            "id": "ASM-001",
            "statement": "traffic stays under one instance",
            "impact_if_wrong": "latency alarms at 10x",
            "mitigation": "add autoscaling trigger before launch",
        }
    ],
    "status": "draft",
}

BASE_STACK = {
    "version": 1,
    "as_of": "2026-10-16",
    "selections": [
        {
            "id": "SEL-001",
            "area": "storage",
            "choice": "SQLite",
            "basis": "constraint",
            "source_ref": "constraints.local_only",
            "confidence": "high",
            "decision_ref": "ADR-001",
        }
    ],
}

BASE_INTERFACES = {
    "version": 1,
    "interfaces": [
        {
            "id": "IF-001",
            "name": "create link",
            "kind": "http",
            "method": "POST",
            "path": "/api/links",
            "acceptance_refs": ["AC-001"],
        }
    ],
}

BASE_DOCS = {
    "current": BASE_CURRENT,
    "stack": BASE_STACK,
    "interfaces": BASE_INTERFACES,
    "decision_files": {"ADR-001"},
    "prototype_files": {"index.html"},
}


def _mutate(**changes: object) -> dict:
    docs = copy.deepcopy(BASE_DOCS)
    for key, value in changes.items():
        docs[key] = copy.deepcopy(value)
    return docs


def _all_selftest_cases() -> list[tuple[str, dict, list[str]]]:
    cases: list[tuple[str, dict, list[str]]] = [
        ("benign design should pass", BASE_DOCS, []),
    ]

    no_adr = copy.deepcopy(BASE_CURRENT)
    no_adr["decisions"] = ["ADR-002"]
    cases.append(
        (
            "decision without ADR file should fail",
            _mutate(current=no_adr, decision_files={"ADR-001"}),
            ["decisions"],
        )
    )

    unregistered = copy.deepcopy(BASE_INTERFACES)
    unregistered["interfaces"][0]["acceptance_refs"] = ["AC-099"]
    cases.append(
        (
            "interface claiming unregistered AC should fail",
            _mutate(interfaces=unregistered),
            ["AC-099"],
        )
    )

    hollow = copy.deepcopy(BASE_CURRENT)
    hollow["coverage"][0]["covered_by"] = {}
    cases.append(
        (
            "covered AC with nothing claiming it should fail",
            _mutate(
                current=hollow,
                interfaces={"version": 1, "interfaces": []},
                data_model=None,
            ),
            ["AC-001"],
        )
    )

    brittle = copy.deepcopy(BASE_STACK)
    brittle["selections"][0]["basis"] = "assumption"
    brittle["selections"][0].pop("source_ref", None)
    cases.append(
        (
            "assumption without why_assumed should fail",
            _mutate(stack=brittle),
            ["why_assumed"],
        )
    )

    missing_proto = copy.deepcopy(BASE_CURRENT)
    missing_proto["prototype"]["pages"] = [
        {"name": "home", "file": "gone.html", "review_status": "pending"}
    ]
    cases.append(
        (
            "prototype page without file should fail",
            _mutate(current=missing_proto, prototype_files={"index.html"}),
            ["gone.html"],
        )
    )

    unmitigated = copy.deepcopy(BASE_CURRENT)
    unmitigated["assumptions"][0].pop("mitigation")
    cases.append(
        (
            "assumption without mitigation should fail",
            _mutate(current=unmitigated),
            ["ASM-001"],
        )
    )

    return cases


def selftest() -> int:
    passed = 0
    failed = 0
    for name, docs, expected_markers in _all_selftest_cases():
        failures = run_checks(docs)
        missing = [
            marker
            for marker in expected_markers
            if not any(marker in failure for failure in failures)
        ]
        if expected_markers and not failures:
            print(f"  [FAIL] {name}: expected failures, got none")
            failed += 1
        elif not expected_markers and failures:
            print(f"  [FAIL] {name}: unexpected failures: {failures}")
            failed += 1
        elif missing:
            print(f"  [FAIL] {name}: did not detect {', '.join(missing)}")
            failed += 1
        else:
            print(f"  [ok  ] {name}")
            passed += 1

    print(f"selftest: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    raise SystemExit(main())
