"""Have a person review the extraction in DeepRead.

The reviewer is emailed a link, signs in with an emailed code, checks and
corrects the values, and completes the review. The corrected data then arrives
at your webhook_url as a review.completed event: the same body as
GET /v1/jobs/{id}, with review.changes[] listing every corrected value as
{key, previous_value, value, changed_at, changed_by, version}.
Run 05_webhook_server.py to receive it. Webhooks need the Standard plan or above.

Usage: python 06_human_review.py <invoice.pdf> <reviewer@example.com>
       (set WEBHOOK_URL to your public webhook address)
"""

import os
import sys
import json
import time
import requests

API_KEY = os.environ.get("DEEPREAD_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
BASE = "https://api.deepread.tech"

if not API_KEY:
    print("Set DEEPREAD_API_KEY in your environment or .env file")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: python 06_human_review.py <invoice.pdf> <reviewer@example.com>")
    sys.exit(1)
file_path, reviewer_email = sys.argv[1], sys.argv[2]

headers = {"X-API-Key": API_KEY}

schema = json.dumps({
    "type": "object",
    "properties": {
        "vendor": {"type": "string", "description": "Company or vendor name"},
        "invoice_number": {"type": "string", "description": "Invoice or receipt number"},
        "total": {"type": "number", "description": "Total amount due"},
    },
})

data = {
    "pipeline": "extract",
    "schema": schema,
    "reviewer_email": reviewer_email,  # one email, or several separated by commas
    "review_due_hours": "24",
}
if WEBHOOK_URL:
    data["webhook_url"] = WEBHOOK_URL

with open(file_path, "rb") as f:
    resp = requests.post(f"{BASE}/v1/process", headers=headers, files={"file": f}, data=data)
    resp.raise_for_status()

job_id = resp.json()["id"]
print(f"Submitted: {job_id}")

# Poll with backoff
delay = 5
while True:
    time.sleep(delay)
    resp = requests.get(f"{BASE}/v1/jobs/{job_id}", headers=headers)
    if resp.status_code in (429, 503):  # rate limited or busy: no status, wait and retry
        delay = float(resp.headers.get("Retry-After", 5))
        continue
    result = resp.json()
    status = result["status"]
    print(f"  Status: {status}")

    if status == "completed":
        review = result.get("review", {})
        print("\n--- Review ---")
        print(f"Status: {review.get('status')}")
        print(f"Reviewers: {review.get('reviewers')}")
        print(f"Review link: {review.get('url')}")
        print(f"Due: {review.get('due_at')}")
        print("\nThe corrected data arrives at your webhook as review.completed.")
        break
    elif status == "failed":
        print(f"Failed: {result.get('error', 'Unknown error')}")
        break

    delay = min(delay * 1.5, 15)
