"""Redact PII from documents — names, SSNs, credit cards, and 11 other types."""

import os
import sys
import json
import time
import requests

API_KEY = os.environ.get("DEEPREAD_API_KEY")
BASE = "https://api.deepread.tech"

if not API_KEY:
    print("Set DEEPREAD_API_KEY in your environment or .env file")
    sys.exit(1)

file_path = sys.argv[1] if len(sys.argv) > 1 else None
if not file_path:
    print("Usage: python 04_pii_redact.py <document.pdf>")
    sys.exit(1)

headers = {"X-API-Key": API_KEY}

# Submit for PII redaction
with open(file_path, "rb") as f:
    resp = requests.post(
        f"{BASE}/v1/pii/redact",
        headers=headers,
        files={"file": f},
    )
    resp.raise_for_status()

job = resp.json()
job_id = job["id"]
print(f"Submitted: {job_id}")

# Poll with backoff
delay = 3
while True:
    time.sleep(delay)
    result = requests.get(f"{BASE}/v1/pii/{job_id}", headers=headers).json()
    status = result["status"]
    print(f"  Status: {status}")

    if status == "completed":
        report = result.get("report", {})
        print(f"\n--- PII Detection Report ---")
        print(f"Pages scanned: {report.get('page_count')}")
        print(f"Total redactions: {report.get('total_redactions')}")
        print(f"Confidence threshold: {report.get('confidence_threshold_used', 0.85)}")
        print(f"Below threshold: {report.get('below_threshold_count', 0)}")

        for pii_type, info in report.get("pii_detected", {}).items():
            print(f"  {pii_type}: {info['count']} found on pages {info['pages']} (avg: {info['confidence_avg']:.2f}, min: {info.get('confidence_min', 0):.2f})")

        # Download redacted file
        redacted_url = result.get("redacted_file_url")
        if redacted_url:
            pdf = requests.get(redacted_url).content
            out_path = file_path.rsplit(".", 1)[0] + "_redacted." + file_path.rsplit(".", 1)[1]
            with open(out_path, "wb") as f:
                f.write(pdf)
            print(f"\nRedacted file saved: {out_path}")
        break
    elif status == "failed":
        print(f"Failed: {result.get('error', 'Unknown error')}")
        break

    delay = min(delay * 1.5, 15)
