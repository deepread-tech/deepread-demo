#!/bin/bash
# Extract structured JSON fields from a document
FILE=${1:?"Usage: ./02_structured_extraction.sh <invoice.pdf>"}

JOB_ID=$(curl -s -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@$FILE" \
  -F 'schema={"type":"object","properties":{"vendor":{"type":"string"},"total":{"type":"number"},"date":{"type":"string"},"invoice_number":{"type":"string"}}}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Submitted: $JOB_ID"

while true; do
  sleep 5
  RESULT=$(curl -s "https://api.deepread.tech/v1/jobs/$JOB_ID" -H "X-API-Key: $DEEPREAD_API_KEY")
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  echo "  Status: $STATUS"
  [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ] && break
done

echo "$RESULT" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin).get('structured_data',{}), indent=2))"
