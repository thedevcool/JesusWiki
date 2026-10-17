// Validates every entry in /entries and builds the static site into /dist.
import { readdirSync, readFileSync, writeFileSync, mkdirSync, copyFileSync } from "node:fs";
import { join } from "node:path";

const STRENGTHS = ["strong", "probable", "debated", "weak"];
const isStr = (v) => typeof v === "string" && v.trim().length > 0;
const isUrl = (v) => /^https?:\/\/\S+$/i.test(v);
const errors = [];
const entries = [];

const files = readdirSync("entries").filter((f) => f.endsWith(".json")).sort();
for (const f of files) {
  const id = f.replace(/\.json$/, "");
  const err = (m) => errors.push(`entries/${f}: ${m}`);
  let e;
  try { e = JSON.parse(readFileSync(join("entries", f), "utf8")); }
  catch (x) { err("not valid JSON (" + x.message + ")"); continue; }

  if (!isStr(e.claim)) err("claim is required");
  if (!STRENGTHS.includes(e.strength)) err("strength must be one of " + STRENGTHS.join(", "));
  if (!Array.isArray(e.bible) || !e.bible.length) err("bible needs at least one passage");
  else e.bible.forEach((b, i) => { if (!isStr(b.ref) || !isStr(b.note)) err(`bible[${i}] needs ref and note`); });
  if (!Array.isArray(e.outside) || !e.outside.length) err("outside needs at least one source");
  else e.outside.forEach((o, i) => {
    if (!isStr(o.source) || !isStr(o.date) || !isStr(o.note)) err(`outside[${i}] needs source, date and note`);
    if (o.link && !isUrl(o.link)) err(`outside[${i}].link must start with http:// or https://`);
    if ((o.note || "").length > 700) err(`outside[${i}].note is over 700 characters; summarize instead of quoting at length`);
  });
  if (!isStr(e.counter)) err("counter (the strongest objection) is required");
  entries.push({ id, ...e });
}

if (errors.length) {
  console.error("Validation failed:\n" + errors.map((m) => " - " + m).join("\n"));
  process.exit(1);
}

mkdirSync("dist", { recursive: true });
writeFileSync("dist/entries.json", JSON.stringify(entries));
copyFileSync("site/index.html", "dist/index.html");
console.log(`OK: ${entries.length} entries built into dist/`);
