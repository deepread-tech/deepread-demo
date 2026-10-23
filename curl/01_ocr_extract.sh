#!/bin/bash
# Extract text from a PDF or image
FILE=${1:?"Usage: ./01_ocr_extract.sh <file.pdf>"}

# Submit
JOB_ID=$(curl -s -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@$FILE" \
  -F "preview=true" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Submitted: $JOB_ID"

# Poll
HEADERS=$(mktemp)
while true; do
  sleep "${WAIT:-5}"; WAIT=5
  RESULT=$(curl -s -D "$HEADERS" "https://api.deepread.tech/v1/jobs/$JOB_ID" -H "X-API-Key: $DEEPREAD_API_KEY")
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null)
  if [ -z "$STATUS" ]; then  # 429 or 503: no status, wait Retry-After and retry
    WAIT=$(grep -i '^retry-after:' "$HEADERS" | tr -dc '0-9'); WAIT=${WAIT:-5}; continue
  fi
  echo "  Status: $STATUS"
  [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ] && break
done

echo "$RESULT" | python3 -c "
import sys,json
r = json.load(sys.stdin)
if r['status'] == 'completed':
    content = r['document']['content']
    print('\n--- Extracted Text ---')
    print(content.get('text_preview', content.get('text', ''))[:2000])
    if r.get('artifacts', {}).get('preview_url'):
        print(f'\nShareable preview: {r[\"artifacts\"][\"preview_url\"]}')
else:
    print(f'Failed: {r.get(\"error\", \"Unknown\")}')"
