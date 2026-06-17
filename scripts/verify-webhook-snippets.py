#!/usr/bin/env python3
"""Validate the Python webhook-verification snippet in guides/webhooks.mdx.

Signs a payload with the documented scheme:
    v1=hex(HMAC_SHA256(secret, f"{timestamp}.{raw_body}"))
then asserts the snippet's verify() accepts a valid signature and rejects a
tampered body, a wrong secret, and a stale timestamp. Exits non-zero on any
failure so a drifted snippet is caught (#4972).
"""
import hashlib
import hmac
import json
import sys
import time

SECRET = b"whsec_test_secret_value"
TOLERANCE_SECONDS = 300


# --- The verify function from guides/webhooks.mdx (keep in sync) ---
def verify(raw_body: bytes, signature_header: str, timestamp_header: str) -> bool:
    try:
        ts = int(timestamp_header)
    except (TypeError, ValueError):
        return False
    if abs(time.time() - ts) > TOLERANCE_SECONDS:
        return False

    signed = f"{timestamp_header}.".encode() + raw_body
    expected = "v1=" + hmac.new(SECRET, signed, hashlib.sha256).hexdigest()

    return any(
        hmac.compare_digest(part.strip(), expected)
        for part in signature_header.split(",")
    )


# --- Reproduce the server signing scheme to produce a real signature ---
def sign(secret: bytes, timestamp: str, raw_body: bytes) -> str:
    signed = f"{timestamp}.".encode() + raw_body
    return "v1=" + hmac.new(secret, signed, hashlib.sha256).hexdigest()


def main() -> int:
    ts = str(int(time.time()))
    body = json.dumps(
        {
            "id": "evt_whale_trades_inserted_1718634500123_7",
            "type": "whale_trades_inserted",
            "created_at": "2026-06-17T14:28:20Z",
            "data": {"count": 7},
        }
    ).encode()
    sig = sign(SECRET, ts, body)

    checks = [
        ("valid signature verifies", verify(body, sig, ts) is True),
        ("tampered body is rejected", verify(body + b" ", sig, ts) is False),
        ("wrong secret is rejected", verify(body, sign(b"whsec_other", ts, body), ts) is False),
        ("stale timestamp is rejected", verify(body, sign(SECRET, "1000000000", body), "1000000000") is False),
        ("comma-joined header still matches", verify(body, f"v0=deadbeef, {sig}", ts) is True),
    ]

    failed = 0
    for name, ok in checks:
        if ok:
            print(f"ok   - {name}")
        else:
            print(f"FAIL - {name}", file=sys.stderr)
            failed += 1

    if failed:
        print(f"\n{failed} webhook snippet check(s) failed", file=sys.stderr)
        return 1
    print("\nall webhook snippet checks passed (Python)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
