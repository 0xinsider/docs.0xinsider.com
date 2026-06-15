#!/usr/bin/env python3
"""Assert the docs OpenAPI spec is a structural copy of the app's canonical spec.

The app spec (`web/public/api/v1/openapi.json` in the 0xinsider repo) is the
single source of truth for the public V1 API. The docs spec
(`api-reference/openapi.json`) must be a synced copy of it -- never
hand-maintained, never a second source of truth (#4972).

Run this when re-syncing (point `--app-spec` at the 0xinsider checkout):

    python3 scripts/check-spec-sync.py \\
      --app-spec ../0xinsider/web/public/api/v1/openapi.json

Exits non-zero (with a path/schema drift report) when the two specs are not
structurally equal, so a re-sync is never silently half-done. Pair it with
`check-openapi-parity.py`, which checks that every spec operation has a docs page.
"""
import argparse
import json
import sys


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--app-spec",
        required=True,
        help="path to the canonical app openapi.json (0xinsider web/public/api/v1/openapi.json)",
    )
    parser.add_argument(
        "--docs-spec",
        default="api-reference/openapi.json",
        help="path to the docs openapi.json (default: api-reference/openapi.json)",
    )
    args = parser.parse_args()

    app = load(args.app_spec)
    docs = load(args.docs_spec)

    app_paths = set(app.get("paths", {}))
    docs_paths = set(docs.get("paths", {}))
    app_schemas = set(app.get("components", {}).get("schemas", {}))
    docs_schemas = set(docs.get("components", {}).get("schemas", {}))

    drift = []
    for label, in_app, in_docs in (
        ("path", app_paths, docs_paths),
        ("schema", app_schemas, docs_schemas),
    ):
        for name in sorted(in_app - in_docs):
            drift.append(f"  {label} in app spec, MISSING from docs spec: {name}")
        for name in sorted(in_docs - in_app):
            drift.append(f"  {label} in docs spec, NOT in app spec: {name}")

    structurally_equal = json.dumps(app, sort_keys=True) == json.dumps(
        docs, sort_keys=True
    )

    if drift or not structurally_equal:
        print("OpenAPI spec drift: the docs spec is not a structural copy of the app spec.")
        for line in drift:
            print(line)
        if not drift and not structurally_equal:
            print(
                "  (path/schema sets match but the specs differ structurally "
                "-- a field/param/example drifted; re-sync from the app spec)"
            )
        print(
            "Re-sync: cp <0xinsider>/web/public/api/v1/openapi.json api-reference/openapi.json"
        )
        sys.exit(1)

    print(
        f"OpenAPI spec sync OK: {len(docs_paths)} paths / {len(docs_schemas)} schemas "
        "match the app spec exactly."
    )


if __name__ == "__main__":
    main()
