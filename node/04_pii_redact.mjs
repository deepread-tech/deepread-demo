// Redact PII from documents — 14 types detected with context-aware AI

import { readFileSync, writeFileSync } from "fs";

const API_KEY = process.env.DEEPREAD_API_KEY;
const BASE = "https://api.deepread.tech";
const filePath = process.argv[2];

if (!API_KEY) { console.error("Set DEEPREAD_API_KEY"); process.exit(1); }
if (!filePath) { console.error("Usage: node 04_pii_redact.mjs <document.pdf>"); process.exit(1); }

const form = new FormData();
form.append("file", new Blob([readFileSync(filePath)]), filePath.split("/").pop());

const { id: jobId } = await fetch(`${BASE}/v1/pii/redact`, {
  method: "POST",
  headers: { "X-API-Key": API_KEY },
  body: form,
}).then(r => r.json());

console.log(`Submitted: ${jobId}`);

let delay = 3000;
while (true) {
  await new Promise(r => setTimeout(r, delay));
  const result = await fetch(`${BASE}/v1/pii/${jobId}`, {
    headers: { "X-API-Key": API_KEY },
  }).then(r => r.json());

  console.log(`  Status: ${result.status}`);

  if (result.status === "completed") {
    const report = result.report || {};
    console.log("\n--- PII Detection Report ---");
    console.log(`Pages scanned: ${report.page_count}`);
    console.log(`Total redactions: ${report.total_redactions}`);
    for (const [type, info] of Object.entries(report.pii_detected || {})) {
      console.log(`  ${type}: ${info.count} found on pages ${info.pages} (avg: ${info.confidence_avg.toFixed(2)})`);
    }
    if (result.redacted_file_url) {
      const pdf = await fetch(result.redacted_file_url).then(r => r.arrayBuffer());
      const outPath = filePath.replace(/\.(\w+)$/, "_redacted.$1");
      writeFileSync(outPath, Buffer.from(pdf));
      console.log(`\nRedacted file saved: ${outPath}`);
    }
    break;
  } else if (result.status === "failed") {
    console.error(`Failed: ${result.error}`);
    break;
  }
  delay = Math.min(delay * 1.5, 15000);
}
