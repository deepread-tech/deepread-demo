#!/bin/bash
# Fill a PDF form with AI vision
FILE=${1:?"Usage: ./03_form_fill.sh <blank_form.pdf>"}

JOB_ID=$(curl -s -X POST https://api.deepread.tech/v1/form-fill \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@$FILE" \
  -F 'form_fields={"full_name":"Jane Smith","date_of_birth":"1990-03-15","address":"123 Main St, San Francisco, CA 94102"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

echo "Submitted: $JOB_ID"

while true; do
  sleep 5
  RESULT=$(curl -s "https://api.deepread.tech/v1/form-fill/$JOB_ID" -H "X-API-Key: $DEEPREAD_API_KEY")
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  echo "  Status: $STATUS"
  [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ] && break
done

echo "$RESULT" | python3 -c "
import sys,json
r = json.load(sys.stdin)
if r['status'] == 'completed':
    print(f'Fields detected: {r.get(\"fields_detected\")}')
    print(f'Fields filled: {r.get(\"fields_filled\")}')
    print(f'Filled form: {r.get(\"filled_form_url\", \"N/A\")}')
else:
    print(f'Failed: {r.get(\"error_message\", \"Unknown\")}')"
