"""DeepRead Demo Web App — Upload a document, get structured data back."""

import os
import time

import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("DEEPREAD_API_KEY")
BASE = "https://api.deepread.tech"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/extract", methods=["POST"])
def extract():
    if not API_KEY:
        return jsonify({"error": "DEEPREAD_API_KEY not set"}), 500

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    mode = request.form.get("mode", "ocr")
    headers = {"X-API-Key": API_KEY}

    if mode == "structured":
        schema = request.form.get("schema", '{"type":"object","properties":{"vendor":{"type":"string","description":"Company name"},"total":{"type":"number","description":"Total amount"},"date":{"type":"string","description":"Document date"}}}')
        resp = requests.post(
            f"{BASE}/v1/process",
            headers=headers,
            files={"file": (file.filename, file.read(), file.content_type)},
            data={"schema": schema},
        )
    elif mode == "pii":
        resp = requests.post(
            f"{BASE}/v1/pii/redact",
            headers=headers,
            files={"file": (file.filename, file.read(), file.content_type)},
        )
    else:
        resp = requests.post(
            f"{BASE}/v1/process",
            headers=headers,
            files={"file": (file.filename, file.read(), file.content_type)},
        )

    if resp.status_code != 200:
        return jsonify({"error": f"API error: {resp.status_code}", "detail": resp.text}), resp.status_code

    job = resp.json()
    job_id = job["id"]

    # Determine poll endpoint
    if mode == "pii":
        poll_url = f"{BASE}/v1/pii/{job_id}"
    else:
        poll_url = f"{BASE}/v1/jobs/{job_id}"

    # Poll with backoff (max 5 min)
    delay = 5
    start = time.time()
    while time.time() - start < 300:
        time.sleep(delay)
        result = requests.get(poll_url, headers=headers).json()

        if result["status"] == "completed":
            return jsonify(result)
        elif result["status"] == "failed":
            return jsonify(result), 500

        delay = min(delay * 1.5, 15)

    return jsonify({"error": "Processing timed out after 5 minutes"}), 504


@app.route("/health")
def health():
    return jsonify({"status": "ok", "api_key_set": bool(API_KEY)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
