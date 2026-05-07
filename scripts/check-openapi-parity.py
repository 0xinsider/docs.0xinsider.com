#!/usr/bin/env python3
"""Verify Mintlify endpoint pages cover every local OpenAPI path."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = REPO_ROOT / "api-reference" / "openapi.json"
DOCS_JSON_PATH = REPO_ROOT / "docs.json"
ENDPOINT_DIR = REPO_ROOT / "api-reference" / "endpoint"


def load_openapi_endpoints() -> set[str]:
    spec = json.loads(OPENAPI_PATH.read_text())
    endpoints: set[str] = set()
    for path, operations in spec["paths"].items():
        for method in operations:
            endpoints.add(f"{method.upper()} {path}")
    return endpoints


def load_page_endpoints() -> dict[str, Path]:
    pages: dict[str, Path] = {}
    pattern = re.compile(r'^openapi:\s*"([^"]+)"\s*$', re.MULTILINE)
    for path in ENDPOINT_DIR.glob("*.mdx"):
        text = path.read_text()
        match = pattern.search(text)
        if match:
            pages[match.group(1)] = path.relative_to(REPO_ROOT)
    return pages


def load_navigation_pages() -> set[str]:
    docs_json = json.loads(DOCS_JSON_PATH.read_text())
    pages: set[str] = set()

    def visit(value: object) -> None:
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, str):
            pages.add(value)

    visit(docs_json.get("navigation", {}))
    return pages


def main() -> int:
    openapi = load_openapi_endpoints()
    page_endpoints = load_page_endpoints()
    nav_pages = load_navigation_pages()

    missing_pages = sorted(openapi - set(page_endpoints))
    stale_pages = sorted(set(page_endpoints) - openapi)
    missing_nav = sorted(
        str(path.with_suffix(""))
        for endpoint, path in page_endpoints.items()
        if endpoint in openapi and str(path.with_suffix("")) not in nav_pages
    )

    errors: list[str] = []
    if missing_pages:
        errors.append("Missing endpoint pages:\n" + "\n".join(f"- {p}" for p in missing_pages))
    if stale_pages:
        errors.append("Endpoint pages not present in OpenAPI:\n" + "\n".join(f"- {p}" for p in stale_pages))
    if missing_nav:
        errors.append("Endpoint pages missing from docs.json navigation:\n" + "\n".join(f"- {p}" for p in missing_nav))

    if errors:
        print("\n\n".join(errors), file=sys.stderr)
        return 1

    print(f"OpenAPI/docs parity OK: {len(openapi)} operations covered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
