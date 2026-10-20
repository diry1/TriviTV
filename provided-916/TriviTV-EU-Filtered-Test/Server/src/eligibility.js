import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

const fingerprint = (text, choices) =>
  createHash("sha256").update(JSON.stringify([text, choices])).digest("hex");

export function validateEligibility(document, source, translations) {
  if (document.schemaVersion !== 1 || document.audience !== "Europe" ||
      !Array.isArray(document.records) || document.records.length !== source.length)
    throw new Error("Invalid EU eligibility metadata or incomplete coverage.");
  const originals = new Map(source.map((q) => [q.id, q]));
  const seen = new Set();
  const eligible = { en: new Set(), uk: new Set() };
  for (const row of document.records) {
    const original = originals.get(row.id);
    if (!original || seen.has(row.id) || row.sourceHash !== fingerprint(original.text, original.choices))
      throw new Error(`Invalid or stale EU eligibility: ${row.id}`);
    seen.add(row.id);
    for (const language of ["en", "uk"]) {
      const decision = row[language];
      if (!decision || !["candidate", "exclude", "hold"].includes(decision.outcome) ||
          !Array.isArray(decision.rules) || !decision.evidence || !decision.origin)
        throw new Error(`Invalid EU decision: ${row.id}/${language}`);
      if (language === "uk") {
        const translated = translations.get(row.id);
        if (translated && decision.translationHash !== fingerprint(translated.text, translated.choices))
          throw new Error(`Stale Ukrainian EU eligibility: ${row.id}`);
        if (!translated && decision.outcome === "candidate")
          throw new Error(`EU eligibility has no Ukrainian translation: ${row.id}`);
      }
      if (decision.outcome === "candidate") eligible[language].add(row.id);
    }
  }
  return eligible;
}

export function loadEligibility(source, translations) {
  const root = new URL("../", import.meta.url);
  const document = JSON.parse(readFileSync(new URL("data/editorial/eu-eligibility.json", root), "utf8"));
  // A policy, review, source or translation change must regenerate eligibility.
  // Never silently revert to the old permissive region filter.
  if (!document.inputHashes || !Object.keys(document.inputHashes).length)
    throw new Error("Missing EU eligibility input fingerprints.");
  for (const [path, expected] of Object.entries(document.inputHashes)) {
    if (!/^(data|docs)\/[a-zA-Z0-9_./-]+$/.test(path) || path.split("/").includes(".."))
      throw new Error("Invalid EU eligibility input path.");
    const actual = createHash("sha256").update(readFileSync(new URL(path, root))).digest("hex");
    if (actual !== expected) throw new Error(`EU eligibility needs rebuilding: ${path}`);
  }
  return { eligible: validateEligibility(document, source, translations), document };
}
