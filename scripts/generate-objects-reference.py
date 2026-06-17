#!/usr/bin/env python3
"""Generate the Objects reference MDX from the OpenAPI component schemas.

The page at `api-reference/objects.mdx` is GENERATED from
`api-reference/openapi.json` (`components.schemas`) so it can never drift from
the spec. Do not hand-edit the output; edit this script or the spec and
re-run (#4972):

    python3 scripts/generate-objects-reference.py

The docs spec is itself a synced copy of the canonical app spec, enforced by
`check-spec-sync.py`. So this page tracks the live API contract end to end.
"""
import json
import os
import sys

SPEC = "api-reference/openapi.json"
OUT = "api-reference/objects.mdx"

HEADER = """---
title: "Objects"
description: "Every object the API returns, generated from the OpenAPI schema."
---

{/* GENERATED FILE -- do not edit by hand. Run scripts/generate-objects-reference.py. */}

These are the objects the API returns, generated directly from the OpenAPI
schema so they always match the live contract. Each table lists a field, its
type, whether it is always present, and what it means.

"""


def ref_name(ref):
    return ref.rsplit("/", 1)[-1]


def type_label(node):
    """Render a property's type as a short markdown string."""
    if node is None:
        return "any"
    if "$ref" in node:
        return f"`{ref_name(node['$ref'])}`"
    if "oneOf" in node:
        return " or ".join(type_label(n) for n in node["oneOf"])
    if "enum" in node:
        vals = " \\| ".join(f"`{v}`" for v in node["enum"])
        return vals
    t = node.get("type")
    if t == "array":
        return f"array of {type_label(node.get('items'))}"
    if t == "object":
        ap = node.get("additionalProperties")
        if isinstance(ap, dict):
            return f"map of {type_label(ap)}"
        return "object"
    if isinstance(t, list):
        return " \\| ".join(t)
    return t or "object"


def escape(text):
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def render_schema(name, schema):
    lines = [f"## {name}", ""]
    desc = schema.get("description")
    if desc:
        lines += [escape(desc), ""]

    if "oneOf" in schema:
        variants = ", ".join(f"`{ref_name(n['$ref'])}`" for n in schema["oneOf"] if "$ref" in n)
        disc = schema.get("discriminator", {}).get("propertyName")
        lines.append(f"One of: {variants}." + (f" Discriminated by `{disc}`." if disc else ""))
        lines.append("")
        return "\n".join(lines)

    if "enum" in schema and "properties" not in schema:
        vals = ", ".join(f"`{v}`" for v in schema["enum"])
        lines += [f"String enum: {vals}.", ""]
        return "\n".join(lines)

    props = schema.get("properties")
    if not props:
        lines += ["_No documented fields._", ""]
        return "\n".join(lines)

    required = set(schema.get("required", []))
    lines += ["| Field | Type | Required | Description |", "|---|---|---|---|"]
    for field, node in props.items():
        req = "Yes" if field in required else "No"
        lines.append(
            f"| `{field}` | {type_label(node)} | {req} | {escape(node.get('description'))} |"
        )
    lines.append("")
    return "\n".join(lines)


def main():
    if not os.path.exists(SPEC):
        print(f"spec not found: {SPEC}", file=sys.stderr)
        return 1
    with open(SPEC, encoding="utf-8") as handle:
        spec = json.load(handle)
    schemas = spec.get("components", {}).get("schemas", {})
    if not schemas:
        print("no component schemas found", file=sys.stderr)
        return 1

    body = [HEADER]
    for name in sorted(schemas):
        body.append(render_schema(name, schemas[name]))
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(body).rstrip() + "\n")
    print(f"wrote {OUT} ({len(schemas)} schemas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
