"""Extract text from a PDF or image using DeepRead OCR."""

import os
import sys
import time
import requests

API_KEY = os.environ.get("DEEPREAD_API_KEY")
BASE = "https://api.deepread.tech"

if not API_KEY:
    print("Set DEEPREAD_API_KEY in your environment or .env file")
    sys.exit(1)

file_path = sys.argv[1] if len(sys.argv) > 1 else None
if not file_path:
    print("Usage: python 01_ocr_extract.py <file.pdf>")
    sys.exit(1)

headers = {"X-API-Key": API_KEY}

# Submit document
with open(file_path, "rb") as f:
    resp = requests.post(f"{BASE}/v1/process", headers=headers, files={"file": f})
    resp.raise_for_status()

job = resp.json()
job_id = job["id"]
print(f"Submitted: {job_id} (status: {job['status']})")

# Poll with backoff
delay = 5
while True:
    time.sleep(delay)
    result = requests.get(f"{BASE}/v1/jobs/{job_id}", headers=headers).json()
    status = result["status"]
    print(f"  Status: {status}")

    if status == "completed":
        res = result["result"]
        print("\n--- Extracted Text ---")
        print(res.get("text_preview") or res.get("text", "")[:2000])
        if result.get("preview_url"):
            print(f"\nShareable preview: {result['preview_url']}")
        break
    elif status == "failed":
        print(f"Failed: {result.get('error', 'Unknown error')}")
        break

    delay = min(delay * 1.5, 15)
