import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { questions, ukrainianQuestions, questionPool, poolCoverage, categories } from "../src/questions.js";
import { validateEligibility } from "../src/eligibility.js";
import { selectQuestions } from "../src/game.js";

const read = (path) => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));
const reviews = read("../data/editorial/eu-ua/review-decisions.json").decisions;
const flags = new Set(read("../data/editorial/eu-ua/quality-flags.json").flags
  .filter((f) => f.blocking && f.status === "pending").map((f) => f.id));
const english = new Set(questionPool("en", "Europe").map((q) => q.id));
const ukrainian = new Set(questionPool("uk", "Europe").map((q) => q.id));

test("Europe applies every human decision while separating Ukrainian repair flags", () => {
  for (const r of reviews) {
    if (r.decision === "Keep") {
      assert(english.has(r.id), r.id);
      assert.equal(ukrainian.has(r.id), !flags.has(r.id), r.id);
    } else {
      assert(!ukrainian.has(r.id), r.id);
      if (r.decision === "Exclude" && r.reason !== "Translation / language")
        assert(!english.has(r.id), r.id);
      if (r.decision === "Unreviewed") assert(!english.has(r.id), r.id);
    }
  }
  const parseltongue = "otqa:1aed00510a4ddd49b75390eb";
  assert(english.has(parseltongue));
  assert(!ukrainian.has(parseltongue));
  const circus = "otqa:53d90d0aed07653ee690559b";
  assert(english.has(circus));
  assert(!ukrainian.has(circus));
});

test("unassessed EU records stay out, US retains its existing audience pool", () => {
  const document = read("../data/editorial/eu-eligibility.json");
  const pending = document.records.find((r) => r.en.rules.includes("UNASSESSED"));
  assert(pending);
  assert(!english.has(pending.id));
  const washington = "otqa:0c9d703a1b1eaa02c553e332";
  assert(!english.has(washington));
  assert(questionPool("en", "US").some((q) => q.id === washington));
  for (const language of ["en", "uk"])
    assert.deepEqual(questionPool(language, "US").map((q) => q.id),
      (language === "uk" ? [...ukrainianQuestions.values()] : questions)
        .filter((q) => ["US", "Unclassified", "Global"].includes(q.region)).map((q) => q.id));
});

test("both game modes enforce EU eligibility and keep canonical correct-choice alignment", () => {
  const originals = new Map(questions.map((q) => [q.id, q]));
  for (const language of ["en", "uk"])
    for (const mode of ["trivia", "millionaire"])
      for (const category of categories) {
        const pool = questionPool(language, "Europe").filter((q) => q.category === category);
        if (!pool.length) {
          assert.throws(() => selectQuestions({ language, mode, region: "Europe", categories: [category] }), /No questions match/);
          continue;
        }
        const selected = selectQuestions({ language, mode, region: "Europe", categories: [category] });
        assert.equal(selected.length, Math.min(pool.length, mode === "trivia" ? 10 : 15));
        for (const q of selected) {
          assert((language === "uk" ? ukrainian : english).has(q.id));
          const source = language === "uk" ? ukrainianQuestions.get(q.id) : originals.get(q.id);
          assert.equal(q.choices[q.correct], source.choices[source.correct]);
        }
        assert.equal(poolCoverage[language].Europe.categories[category], pool.length);
      }
});

test("eligibility validation rejects missing records, stale fingerprints and nonexistent translations", () => {
  const source = [{ id: "sample", text: "Question?", choices: ["A", "B", "C", "D"] }];
  const hash = (text, choices) => createHash("sha256").update(JSON.stringify([text, choices])).digest("hex");
  const translated = { ...source[0], text: "Запитання?" };
  const translations = new Map([["sample", translated]]);
  const decision = { outcome: "candidate", rules: [], evidence: "fixture", origin: "fixture" };
  const document = { schemaVersion: 1, audience: "Europe", records: [{ id: "sample",
    sourceHash: hash(source[0].text, source[0].choices), en: decision,
    uk: { ...decision, translationHash: hash(translated.text, translated.choices) } }] };
  assert(validateEligibility(document, source, translations).uk.has("sample"));
  for (const mutate of [
    (d) => d.records.pop(),
    (d) => { d.records[0].sourceHash = "stale"; },
    (d) => { d.records[0].uk.translationHash = "stale"; },
    (d) => { d.records[0].en.outcome = "unknown"; },
  ]) {
    const copy = structuredClone(document); mutate(copy);
    assert.throws(() => validateEligibility(copy, source, translations));
  }
  assert.throws(() => validateEligibility(document, source, new Map()), /no Ukrainian translation/);
});
