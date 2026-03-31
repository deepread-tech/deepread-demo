"""Fill a PDF form with AI vision — works on scanned and non-editable PDFs."""

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
    print("Usage: python 03_form_fill.py <blank_form.pdf>")
    sys.exit(1)

headers = {"X-API-Key": API_KEY}

# Data to fill into the form
form_fields = json.dumps({
    "full_name": "Jane Smith",
    "date_of_birth": "1990-03-15",
    "address": "123 Main St, San Francisco, CA 94102",
    "phone": "(555) 867-5309",
    "email": "jane.smith@example.com",
    "ssn": "456-78-9012"
})

# Submit form + data
with open(file_path, "rb") as f:
    resp = requests.post(
        f"{BASE}/v1/form-fill",
        headers=headers,
        files={"file": f},
        data={"form_fields": form_fields},
    )
    resp.raise_for_status()

job = resp.json()
job_id = job["id"]
print(f"Submitted: {job_id}")

# Poll with backoff
delay = 3
while True:
    time.sleep(delay)
    result = requests.get(f"{BASE}/v1/form-fill/{job_id}", headers=headers).json()
    status = result["status"]
    print(f"  Status: {status}")

    if status == "completed":
        filled_url = result.get("filled_file_url")
        print(f"\nFilled form: {filled_url}")

        # Download the filled PDF
        if filled_url:
            pdf = requests.get(filled_url).content
            out_path = file_path.replace(".pdf", "_filled.pdf")
            with open(out_path, "wb") as f:
                f.write(pdf)
            print(f"Saved to: {out_path}")
        break
    elif status == "failed":
        print(f"Failed: {result.get('error', 'Unknown error')}")
        break

    delay = min(delay * 1.5, 15)
