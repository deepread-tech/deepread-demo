#!/bin/bash
# Redact PII from a document
FILE=${1:?"Usage: ./04_pii_redact.sh <document.pdf>"}

JOB_ID=$(curl -s -X POST https://api.deepread.tech/v1/pii/redact \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@$FILE" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Submitted: $JOB_ID"

while true; do
  sleep 5
  RESULT=$(curl -s "https://api.deepread.tech/v1/pii/$JOB_ID" -H "X-API-Key: $DEEPREAD_API_KEY")
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  echo "  Status: $STATUS"
  [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ] && break
done

echo "$RESULT" | python3 -c "
import sys,json
r = json.load(sys.stdin)
if r['status'] == 'completed':
    rpt = r.get('report', {})
    print(f'Total redactions: {rpt.get(\"total_redactions\")}')
    for t, info in rpt.get('pii_detected', {}).items():
        print(f'  {t}: {info[\"count\"]} found')
    print(f'Redacted file: {r.get(\"redacted_file_url\", \"N/A\")}')
else:
    print(f'Failed: {r.get(\"error\", \"Unknown\")}')"
