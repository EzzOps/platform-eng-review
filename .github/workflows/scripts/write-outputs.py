#!/usr/bin/env python3
"""Read review JSON from env vars and write to files for aggregation."""
import os, json, sys

for key, dest in [
    ("SECURITY_RESULTS", "/tmp/security-review.json"),
    ("CNCF_RESULTS", "/tmp/cncf-review.json"),
    ("QUALITY_RESULTS", "/tmp/quality-review.json"),
]:
    raw = os.environ.get(key, "null")
    if raw and isinstance(raw, str) and raw.startswith('"') and raw.endswith('"'):
        raw = json.loads(raw)
    with open(dest, "w") as f:
        f.write(raw if isinstance(raw, str) else json.dumps(raw))
    print(f"Wrote {dest}", flush=True)
