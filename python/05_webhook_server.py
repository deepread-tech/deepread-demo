"""Receive DeepRead results via webhook instead of polling.

Every delivery is signed: X-DeepRead-Signature: t=<unix>,v1=<hex>, where v1 is
HMAC-SHA256 over "<t>.<raw body>" keyed by your webhook secret. Read the secret
at GET /dashboard/v1/webhooks/secret and set it as DEEPREAD_WEBHOOK_SECRET.
"""

import hashlib
import hmac
import os
import time

from flask import Flask, request, jsonify

SECRET = os.environ.get("DEEPREAD_WEBHOOK_SECRET", "")
TOLERANCE_SECONDS = 300  # reject deliveries signed more than 5 minutes ago

app = Flask(__name__)


def verify(header: str, body: bytes) -> bool:
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    try:
        t = int(parts["t"])
    except (KeyError, ValueError):
        return False
    if abs(time.time() - t) > TOLERANCE_SECONDS:
        return False
    expected = hmac.new(SECRET.encode(), f"{t}.".encode() + body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))


@app.route("/webhooks/deepread", methods=["POST"])
def handle_webhook():
    body = request.get_data()  # the exact bytes that were signed
    if not verify(request.headers.get("X-DeepRead-Signature", ""), body):
        return jsonify({"error": "bad signature"}), 401

    payload = request.get_json()
    # The webhook payload is identical to GET /v1/jobs/{id} (schema_version "dp02").
    event = payload.get("event")
    print(f"\nWebhook received: {event} (schema: {payload.get('schema_version')})")
    print(f"  Job: {payload.get('id')}")

    if event == "job.completed":
        preview = payload.get("artifacts", {}).get("preview_url")
        if preview:
            print(f"  Preview: {preview}")
        fields = payload.get("extraction", {}).get("fields")
        if fields:
            print(f"  Extracted fields: {fields}")
        content = payload.get("document", {}).get("content", {})
        if content.get("text"):
            print(f"  Text: {content['text'][:200]}")
    elif event == "job.failed":
        print(f"  Failed: {payload.get('error')}")
    elif event in ("review.completed", "review.updated"):
        review = payload.get("review", {})
        print(f"  Reviewed by {review.get('completed_by')} (version {review.get('version')})")
        for change in review.get("changes") or []:
            print(f"  {change['key']}: {change['previous_value']!r} -> {change['value']!r}")
    else:  # review.overdue, review.cancelled, review.expired
        print(f"  Review status: {payload.get('review', {}).get('status')}")

    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    if not SECRET:
        print("Set DEEPREAD_WEBHOOK_SECRET (from GET /dashboard/v1/webhooks/secret)")
    print("Webhook server running on http://localhost:5001/webhooks/deepread")
    print("Use this URL (or an ngrok tunnel) as webhook_url when submitting documents:")
    print('  -F "webhook_url=https://your-domain.com/webhooks/deepread"')
    app.run(port=5001)
