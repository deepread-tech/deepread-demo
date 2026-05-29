# deepread-demo

Working examples for the [DeepRead](https://www.deepread.tech) document AI API — OCR extraction, structured data, form filling, and PII redaction.

## Quick Start

### 1. Get your API key (free, no credit card)

Sign up at [deepread.tech/dashboard](https://www.deepread.tech/dashboard)

### 2. Set up

```bash
git clone https://github.com/deepread-tech/deepread-demo.git
cd deepread-demo
cp .env.example .env
# paste your API key in .env
```

### 3. Run your first example

```bash
export DEEPREAD_API_KEY=sk_live_your_key_here

# Python
cd python && pip install -r requirements.txt
python 01_ocr_extract.py ../path/to/your/document.pdf

# Node.js
cd node
node 01_ocr_extract.mjs ../path/to/your/document.pdf

# cURL
cd curl && chmod +x *.sh
./01_ocr_extract.sh ../path/to/your/document.pdf
```

## Examples

| # | Example | What it does | Python | Node.js | cURL |
|---|---------|-------------|--------|---------|------|
| 01 | OCR Extract | Extract text from any PDF/image | [01_ocr_extract.py](python/01_ocr_extract.py) | [01_ocr_extract.mjs](node/01_ocr_extract.mjs) | [01_ocr_extract.sh](curl/01_ocr_extract.sh) |
| 02 | Structured Extraction | Extract fields as JSON with a schema | [02_structured_extraction.py](python/02_structured_extraction.py) | [02_structured_extraction.mjs](node/02_structured_extraction.mjs) | [02_structured_extraction.sh](curl/02_structured_extraction.sh) |
| 03 | Form Fill | Fill a blank PDF form with AI vision | [03_form_fill.py](python/03_form_fill.py) | [03_form_fill.mjs](node/03_form_fill.mjs) | [03_form_fill.sh](curl/03_form_fill.sh) |
| 04 | PII Redact | Redact names, SSNs, cards from documents | [04_pii_redact.py](python/04_pii_redact.py) | [04_pii_redact.mjs](node/04_pii_redact.mjs) | [04_pii_redact.sh](curl/04_pii_redact.sh) |
| 05 | Webhook Server | Receive results via webhook | [05_webhook_server.py](python/05_webhook_server.py) | — | — |

## Example Output

### Structured Extraction

```json
{
  "extraction": {
    "fields": [
      {"key": "vendor", "value": "Acme Corp", "needs_review": false, "location": {"page": 1}},
      {"key": "total", "value": 1250.00, "needs_review": false, "location": {"page": 1}},
      {"key": "invoice_number", "value": "INV-2026-0042", "needs_review": false, "location": {"page": 1}},
      {"key": "date", "value": "2026-03-15", "needs_review": true, "review_reason": "Multiple dates found", "location": {"page": 1}}
    ]
  }
}
```

Fields with `needs_review: true` need human review — DeepRead tells you exactly which fields to check.

### PII Redaction Report

```json
{
  "total_redactions": 6,
  "confidence_threshold_used": 0.85,
  "below_threshold_count": 0,
  "pii_detected": {
    "NAME": {"count": 3, "pages": [1, 2], "confidence_avg": 0.92, "confidence_min": 0.87},
    "SSN": {"count": 1, "pages": [1], "confidence_avg": 0.98, "confidence_min": 0.98},
    "PHONE": {"count": 2, "pages": [1], "confidence_avg": 0.89, "confidence_min": 0.85}
  }
}
```

Before: `Patient John Smith, SSN 456-78-9012`
After: `Patient ██████████, SSN ███████████`

## API Reference

- **Base URL**: `https://api.deepread.tech`
- **Auth**: `X-API-Key` header
- **Free tier**: 2,000 pages/month, no credit card
- **Docs**: [deepread.tech](https://www.deepread.tech)

## Web Demo App

For a deployable web UI (OCR, structured extraction, form fill, PII redaction), use the standalone **[deepread-webapp](https://github.com/deepread-tech/deepread-webapp)** repository — it's the official Railway template:

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template/deepread)

> *Note: this repo previously bundled a Flask web app in `webapp/`. It is superseded by the standalone `deepread-webapp` repo, which adds Form Fill and ships as the official Railway template.*

## n8n Integration

Use DeepRead in no-code workflows with our [n8n community node](https://www.npmjs.com/package/n8n-nodes-deepread). Install in n8n: Settings → Community Nodes → `n8n-nodes-deepread`. Supports OCR, structured extraction, form filling, and PII redaction — drag and drop into any workflow.

## AI Agent Skills

DeepRead works with Claude Code, Cursor, Codex, OpenCode, Cline, and 50+ other AI coding agents.

**Claude Code (official community marketplace):**
```bash
/plugin install deepread@claude-community
```

**Universal install (works with all agents via skills.sh):**
```bash
npx skills add deepread-tech/skills
```

**ClawHub (individual skills):**
```bash
clawhub install uday390/deepread-ocr          # OCR & structured extraction
clawhub install uday390/deepread-form-fill     # PDF form filling
clawhub install uday390/deepread-pii           # PII redaction
clawhub install uday390/deepread-byok          # Bring Your Own Key
clawhub install uday390/deepread-invoice       # Invoice processing
clawhub install uday390/deepread-medical       # Medical records
clawhub install uday390/deepread-legal         # Legal documents
clawhub install uday390/deepread-insurance     # Insurance claims
```

## BYOK — Bring Your Own Key

Connect your own OpenAI, Google, or OpenRouter API key via the [dashboard](https://www.deepread.tech/dashboard/byok). All processing routes through your account — zero DeepRead LLM costs, page quota skipped entirely.

## License

MIT
