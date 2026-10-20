import { readFileSync } from "node:fs";
import { loadEligibility } from "./eligibility.js";

// OpenTriviaQA-only, pinned and adapted under CC BY-SA 4.0. See /credits.
// Facts are community-supplied, difficulty is unrated, and region cues are automatic.
const root = new URL("../data/opentriviaqa/", import.meta.url);
export const bank = JSON.parse(
  readFileSync(new URL("manifest.json", root), "utf8"),
);
export const questions = JSON.parse(
  readFileSync(new URL("questions.json", root), "utf8"),
);
export const categories = Object.keys(bank.categories);

// Keep translations separate: IDs, answer keys, source records and regional tags stay canonical.
import { createHash } from "node:crypto";
export function sourceHash(question) {
  return createHash("sha256")
    .update(JSON.stringify([question.text, question.choices]))
    .digest("hex");
}
export function validateTranslations(document, source = questions) {
  if (
    document.language !== "uk" ||
    document.license !== "CC-BY-SA-4.0" ||
    document.sourceRevision !== bank.source.revision ||
    !Array.isArray(document.questions)
  )
    throw new Error("Invalid Ukrainian translation metadata.");
  const originals = new Map(source.map((q) => [q.id, q]));
  const translated = new Map();
  for (const row of document.questions) {
    const original = originals.get(row.id);
    if (
      !original ||
      translated.has(row.id) ||
      row.sourceHash !== sourceHash(original) ||
      !["draft", "reviewed"].includes(row.status) ||
      typeof row.text !== "string" ||
      !row.text.trim() ||
      !Array.isArray(row.choices) ||
      row.choices.length !== 4 ||
      row.choices.some((c) => typeof c !== "string" || !c.trim()) ||
      new Set(
        row.choices.map((c) =>
          c.trim().normalize("NFKC").toLocaleLowerCase("uk"),
        ),
      ).size !== 4 ||
      !/[А-Яа-яІіЇїЄєҐґ]/u.test(row.text) ||
      "correct" in row ||
      !row.method
    )
      throw new Error(`Invalid or stale Ukrainian translation: ${row.id}`);
    translated.set(row.id, {
      ...original,
      text: row.text,
      choices: row.choices,
      language: "uk",
      translationStatus: row.status,
    });
  }
  return translated;
}
const ukrainianDocument = JSON.parse(
  readFileSync(new URL("../translations/uk.json", root), "utf8"),
);
export const ukrainianQuestions = validateTranslations(ukrainianDocument);
export const languageCoverage = {
  en: { count: questions.length, status: "source" },
  uk: {
    count: ukrainianQuestions.size,
    status: "preview",
    reviewed: ukrainianDocument.questions.filter((q) => q.status === "reviewed")
      .length,
  },
};

const eu = loadEligibility(questions, ukrainianQuestions);
export const euEligibleIds = eu.eligible;
export const euEligibilitySummary = eu.document.summary;
const languageSources = { en: questions, uk: [...ukrainianQuestions.values()] };
export function questionPool(language, region) {
  const source = languageSources[language];
  if (!source || !["Europe", "US"].includes(region)) return [];
  if (region === "Europe") return source.filter((q) => euEligibleIds[language].has(q.id));
  return source.filter((q) => ["Global", "Unclassified", "US"].includes(q.region));
}
export const poolCoverage = Object.fromEntries(["en", "uk"].map((language) => [language,
  Object.fromEntries(["Europe", "US"].map((region) => {
    const pool = questionPool(language, region);
    return [region, { count: pool.length, categories: Object.fromEntries(categories.map((c) =>
      [c, pool.filter((q) => q.category === c).length])) }];
  })),
]));
