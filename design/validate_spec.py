"""Local structural checks for the OpenAPI document."""

from __future__ import annotations

from pathlib import Path

import yaml


def walk(value, refs: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "$ref" and isinstance(item, str) and item.startswith("#/components/"):
                refs.add(item)
            walk(item, refs)
    elif isinstance(value, list):
        for item in value:
            walk(item, refs)


def resolve(doc: dict, pointer: str):
    current = doc
    for part in pointer[2:].split("/"):
        current = current[part]
    return current


def main() -> None:
    path = Path("docs/openapi.yaml")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    refs: set[str] = set()
    walk(doc, refs)
    missing = []
    for ref in sorted(refs):
        try:
            resolve(doc, ref)
        except (KeyError, TypeError):
            missing.append(ref)
    operations = 0
    for route in doc["paths"].values():
        operations += sum(
            1 for method in route if method in {"get", "post", "put", "patch", "delete", "head", "options"}
        )
    print(f"paths={len(doc['paths'])} operations={operations} schemas={len(doc['components']['schemas'])} refs={len(refs)}")
    print("missing refs:", missing or "none")
    assert not missing


if __name__ == "__main__":
    main()
