"""Extract structured JSON fields from a document using a schema."""

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
    print("Usage: python 02_structured_extraction.py <invoice.pdf>")
    sys.exit(1)

headers = {"X-API-Key": API_KEY}

# Define what fields to extract
schema = json.dumps({
    "type": "object",
    "properties": {
        "vendor": {"type": "string", "description": "Company or vendor name"},
        "invoice_number": {"type": "string", "description": "Invoice or receipt number"},
        "date": {"type": "string", "description": "Invoice date"},
        "total": {"type": "number", "description": "Total amount due"},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "amount": {"type": "number"}
                }
            },
            "description": "List of line items"
        }
    }
})

# Submit with schema
with open(file_path, "rb") as f:
    resp = requests.post(
        f"{BASE}/v1/process",
        headers=headers,
        files={"file": f},
        data={"schema": schema},
    )
    resp.raise_for_status()

job = resp.json()
job_id = job["id"]
print(f"Submitted: {job_id}")

# Poll with backoff
delay = 5
while True:
    time.sleep(delay)
    result = requests.get(f"{BASE}/v1/jobs/{job_id}", headers=headers).json()
    status = result["status"]
    print(f"  Status: {status}")

    if status == "completed":
        data = result["result"]["data"]
        print("\n--- Extracted Fields ---")
        print(json.dumps(data, indent=2))

        # Show human-in-the-loop flags
        for field, value in data.items():
            if isinstance(value, dict) and value.get("hil_flag"):
                print(f"\n  Warning: '{field}' flagged for review: {value.get('reason', 'low confidence')}")
        break
    elif status == "failed":
        print(f"Failed: {result.get('error', 'Unknown error')}")
        break

    delay = min(delay * 1.5, 15)
