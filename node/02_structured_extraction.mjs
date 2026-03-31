// Extract structured JSON fields from a document using a schema

import { readFileSync } from "fs";

const API_KEY = process.env.DEEPREAD_API_KEY;
const BASE = "https://api.deepread.tech";
const filePath = process.argv[2];

if (!API_KEY) { console.error("Set DEEPREAD_API_KEY"); process.exit(1); }
if (!filePath) { console.error("Usage: node 02_structured_extraction.mjs <invoice.pdf>"); process.exit(1); }

const schema = JSON.stringify({
  type: "object",
  properties: {
    vendor: { type: "string", description: "Company or vendor name" },
    invoice_number: { type: "string", description: "Invoice or receipt number" },
    date: { type: "string", description: "Invoice date" },
    total: { type: "number", description: "Total amount due" },
    line_items: {
      type: "array",
      items: { type: "object", properties: { description: { type: "string" }, amount: { type: "number" } } },
      description: "List of line items",
    },
  },
});

const form = new FormData();
form.append("file", new Blob([readFileSync(filePath)]), filePath.split("/").pop());
form.append("schema", schema);

const { id: jobId } = await fetch(`${BASE}/v1/process`, {
  method: "POST",
  headers: { "X-API-Key": API_KEY },
  body: form,
}).then(r => r.json());

console.log(`Submitted: ${jobId}`);

let delay = 5000;
while (true) {
  await new Promise(r => setTimeout(r, delay));
  const result = await fetch(`${BASE}/v1/jobs/${jobId}`, {
    headers: { "X-API-Key": API_KEY },
  }).then(r => r.json());

  console.log(`  Status: ${result.status}`);

  if (result.status === "completed") {
    console.log("\n--- Extracted Fields ---");
    console.log(JSON.stringify(result.result.data, null, 2));
    break;
  } else if (result.status === "failed") {
    console.error(`Failed: ${result.error}`);
    break;
  }
  delay = Math.min(delay * 1.5, 15000);
}
