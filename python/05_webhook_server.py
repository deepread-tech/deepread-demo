"""Receive DeepRead results via webhook instead of polling."""

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/webhooks/deepread", methods=["POST"])
def handle_webhook():
    payload = request.json
    event = payload.get("event")
    job_id = payload.get("job_id")
    status = payload.get("status")

    print(f"\nWebhook received: {event}")
    print(f"  Job: {job_id}")
    print(f"  Status: {status}")

    if status == "completed":
        result = payload.get("result", {})
        preview = payload.get("preview_url")
        print(f"  Preview: {preview}")

        if result.get("data"):
            print(f"  Extracted data: {result['data']}")
        if result.get("text_preview"):
            print(f"  Text preview: {result['text_preview'][:200]}")

    return jsonify({"ok": True}), 200

if __name__ == "__main__":
    print("Webhook server running on http://localhost:5001/webhooks/deepread")
    print("Use this URL (or an ngrok tunnel) as webhook_url when submitting documents:")
    print('  -F "webhook_url=https://your-domain.com/webhooks/deepread"')
    app.run(port=5001)
