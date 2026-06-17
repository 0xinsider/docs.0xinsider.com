#!/usr/bin/env node
// Validates the Node webhook-verification snippet in guides/webhooks.mdx against
// a signature produced by the documented scheme:
//   v1=hex(HMAC_SHA256(secret, `${timestamp}.${rawBody}`))
// Asserts a valid signature verifies and a tampered body is rejected. Exits
// non-zero on any failure so CI catches a drifted snippet (#4972).
import crypto from "node:crypto";

const SECRET = "whsec_test_secret_value";
const TOLERANCE_SECONDS = 300;

// --- The verify function from guides/webhooks.mdx (keep in sync) ---
function verify(rawBody, signatureHeader, timestampHeader) {
  const ts = Number(timestampHeader);
  if (!Number.isFinite(ts)) return false;
  if (Math.abs(Date.now() / 1000 - ts) > TOLERANCE_SECONDS) return false;

  const expected =
    "v1=" +
    crypto
      .createHmac("sha256", SECRET)
      .update(`${timestampHeader}.${rawBody}`)
      .digest("hex");

  return signatureHeader
    .split(",")
    .map((s) => s.trim())
    .some((candidate) => {
      const a = Buffer.from(candidate);
      const b = Buffer.from(expected);
      return a.length === b.length && crypto.timingSafeEqual(a, b);
    });
}

// --- Reproduce the server signing scheme to produce a real signature ---
function sign(secret, timestamp, rawBody) {
  return (
    "v1=" +
    crypto.createHmac("sha256", secret).update(`${timestamp}.${rawBody}`).digest("hex")
  );
}

const ts = String(Math.floor(Date.now() / 1000));
const body = JSON.stringify({
  id: "evt_whale_trades_inserted_1718634500123_7",
  type: "whale_trades_inserted",
  created_at: "2026-06-17T14:28:20Z",
  data: { count: 7 },
});
const sig = sign(SECRET, ts, body);

let failed = 0;
function check(name, cond) {
  if (cond) {
    console.log(`ok   - ${name}`);
  } else {
    console.error(`FAIL - ${name}`);
    failed += 1;
  }
}

check("valid signature verifies", verify(body, sig, ts) === true);
check("tampered body is rejected", verify(body + " ", sig, ts) === false);
check("wrong secret is rejected", verify(body, sign("whsec_other", ts, body), ts) === false);
check("stale timestamp is rejected", verify(body, sign(SECRET, "1000000000", body), "1000000000") === false);
check(
  "comma-joined header still matches",
  verify(body, `v0=deadbeef, ${sig}`, ts) === true
);

if (failed > 0) {
  console.error(`\n${failed} webhook snippet check(s) failed`);
  process.exit(1);
}
console.log("\nall webhook snippet checks passed (Node)");
