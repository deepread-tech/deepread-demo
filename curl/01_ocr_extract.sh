#!/bin/bash
# Extract text from a PDF or image
FILE=${1:?"Usage: ./01_ocr_extract.sh <file.pdf>"}

# Submit
JOB_ID=$(curl -s -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@$FILE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Submitted: $JOB_ID"

# Poll
while true; do
  sleep 5
  RESULT=$(curl -s "https://api.deepread.tech/v1/jobs/$JOB_ID" -H "X-API-Key: $DEEPREAD_API_KEY")
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  echo "  Status: $STATUS"
  [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ] && break
done

echo "$RESULT" | python3 -c "
import sys,json
r = json.load(sys.stdin)
if r['status'] == 'completed':
    print('\n--- Extracted Text ---')
    print(r.get('text_preview', r.get('text', ''))[:2000])
else:
    print(f'Failed: {r.get(\"error\", \"Unknown\")}')"
