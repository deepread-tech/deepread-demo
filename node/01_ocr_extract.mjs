// Extract text from a PDF or image using DeepRead OCR

import { readFileSync } from "fs";

const API_KEY = process.env.DEEPREAD_API_KEY;
const BASE = "https://api.deepread.tech";
const filePath = process.argv[2];

if (!API_KEY) { console.error("Set DEEPREAD_API_KEY"); process.exit(1); }
if (!filePath) { console.error("Usage: node 01_ocr_extract.mjs <file.pdf>"); process.exit(1); }

const form = new FormData();
form.append("file", new Blob([readFileSync(filePath)]), filePath.split("/").pop());

const { id: jobId } = await fetch(`${BASE}/v1/process`, {
  method: "POST",
  headers: { "X-API-Key": API_KEY },
  body: form,
}).then(r => r.json());

console.log(`Submitted: ${jobId}`);

let delay = 3000;
while (true) {
  await new Promise(r => setTimeout(r, delay));
  const result = await fetch(`${BASE}/v1/jobs/${jobId}`, {
    headers: { "X-API-Key": API_KEY },
  }).then(r => r.json());

  console.log(`  Status: ${result.status}`);

  if (result.status === "completed") {
    console.log("\n--- Extracted Text ---");
    console.log((result.text_preview || result.text || "").slice(0, 2000));
    if (result.preview_url) console.log(`\nFull preview: ${result.preview_url}`);
    break;
  } else if (result.status === "failed") {
    console.error(`Failed: ${result.error || "Unknown error"}`);
    break;
  }
  delay = Math.min(delay * 1.5, 15000);
}
