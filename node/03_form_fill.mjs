// Fill a PDF form with AI vision

import { readFileSync, writeFileSync } from "fs";

const API_KEY = process.env.DEEPREAD_API_KEY;
const BASE = "https://api.deepread.tech";
const filePath = process.argv[2];

if (!API_KEY) { console.error("Set DEEPREAD_API_KEY"); process.exit(1); }
if (!filePath) { console.error("Usage: node 03_form_fill.mjs <blank_form.pdf>"); process.exit(1); }

const formFields = JSON.stringify({
  full_name: "Jane Smith",
  date_of_birth: "1990-03-15",
  address: "123 Main St, San Francisco, CA 94102",
  phone: "(555) 867-5309",
  email: "jane.smith@example.com",
});

const form = new FormData();
form.append("file", new Blob([readFileSync(filePath)]), filePath.split("/").pop());
form.append("form_fields", formFields);

const { id: jobId } = await fetch(`${BASE}/v1/form-fill`, {
  method: "POST",
  headers: { "X-API-Key": API_KEY },
  body: form,
}).then(r => r.json());

console.log(`Submitted: ${jobId}`);

let delay = 3000;
while (true) {
  await new Promise(r => setTimeout(r, delay));
  const result = await fetch(`${BASE}/v1/form-fill/${jobId}`, {
    headers: { "X-API-Key": API_KEY },
  }).then(r => r.json());

  console.log(`  Status: ${result.status}`);

  if (result.status === "completed") {
    const filledUrl = result.filled_file_url;
    console.log(`\nFilled form: ${filledUrl}`);
    if (filledUrl) {
      const pdf = await fetch(filledUrl).then(r => r.arrayBuffer());
      const outPath = filePath.replace(".pdf", "_filled.pdf");
      writeFileSync(outPath, Buffer.from(pdf));
      console.log(`Saved to: ${outPath}`);
    }
    break;
  } else if (result.status === "failed") {
    console.error(`Failed: ${result.error}`);
    break;
  }
  delay = Math.min(delay * 1.5, 15000);
}
