"""Receive DeepRead results via webhook instead of polling."""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhooks/deepread", methods=["POST"])
def handle_webhook():
    payload = request.json
    # The webhook payload is identical to GET /v1/jobs/{id} (schema_version "dp02").
    job_id = payload.get("id")
    status = payload.get("status")

    print(f"\nWebhook received (schema: {payload.get('schema_version')})")
    print(f"  Job: {job_id}")
    print(f"  Status: {status}")

    if status == "completed":
        preview = payload.get("artifacts", {}).get("preview_url")
        print(f"  Preview: {preview}")

        fields = payload.get("extraction", {}).get("fields")
        if fields:
            print(f"  Extracted fields: {fields}")
        content = payload.get("document", {}).get("content", {})
        if content.get("text_preview"):
            print(f"  Text preview: {content['text_preview'][:200]}")

    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    print("Webhook server running on http://localhost:5001/webhooks/deepread")
    print("Use this URL (or an ngrok tunnel) as webhook_url when submitting documents:")
    print('  -F "webhook_url=https://your-domain.com/webhooks/deepread"')
    app.run(port=5001)
