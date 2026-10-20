import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  questions,
  categories,
  bank,
  ukrainianQuestions,
  validateTranslations,
  languageCoverage,
} from "../src/questions.js";
import {
  selectQuestions,
  createGame,
  addPlayer,
  start,
  answer,
  advance,
  view,
} from "../src/game.js";
import { translate, categoryLabels } from "../web/i18n.js";
const document = JSON.parse(
  readFileSync(new URL("../data/translations/uk.json", import.meta.url)),
);
const settings = {
  mode: "trivia",
  region: "Europe",
  categories,
  language: "uk",
};

test("Ukrainian translations cover all categories, inherit source keys and expose review status", () => {
  assert.equal(languageCoverage.en.count, bank.questionCount);
  assert.equal(languageCoverage.uk.count, ukrainianQuestions.size);
  assert.deepEqual(
    new Set([...ukrainianQuestions.values()].map((q) => q.category)),
    new Set(categories),
  );
  for (const [id, q] of ukrainianQuestions) {
    const source = questions.find((q) => q.id === id);
    assert.equal(q.correct, source.correct);
    assert.equal(q.region, source.region);
    assert.equal(q.difficulty, source.difficulty);
    assert.deepEqual(q.source, source.source);
    assert(["draft", "reviewed"].includes(q.translationStatus));
    assert.equal(categoryLabels[q.category] !== undefined, true);
  }
});
test("language selection filters translated pool before shuffle and preserves scoring for both regions and modes", () => {
  for (const region of ["Europe", "US"])
    for (const mode of ["trivia", "millionaire"]) {
      const game = createGame({ ...settings, region, mode });
      const player = addPlayer(game, "Ready");
      start(game, 1000);
      assert.equal(game.settings.language, "uk");
      assert.equal(game.questions.length, mode === "trivia" ? 10 : 15);
      for (const q of game.questions) {
        const translation = ukrainianQuestions.get(q.id);
        assert(translation);
        assert.equal(q.text, translation.text);
        assert.equal(
          q.choices[q.correct],
          translation.choices[translation.correct],
        );
        assert.notEqual(q.region, region === "Europe" ? "US" : "Europe");
      }
      let v = view(game, player.id, 1000);
      assert.equal(v.question.correct, undefined);
      answer(game, player.id, game.questions[0].correct, 1100);
      advance(game, game.stageEndsAt);
      v = view(game, player.id, 2000);
      assert.equal(v.players[0].score, 100);
      assert.equal(
        v.question.choices[v.question.correct],
        ukrainianQuestions.get(v.question.id).choices[
          questions.find((q) => q.id === v.question.id).correct
        ],
      );
    }
  assert.throws(
    () => selectQuestions({ ...settings, language: "ru" }),
    /English or Ukrainian/,
  );
  const english = createGame({ ...settings, language: undefined });
  assert.equal(english.settings.language, "en");
  assert.equal(
    english.questions[0].text,
    questions.find((q) => q.id === english.questions[0].id).text,
  );
});
test("translation loading rejects stale sources, duplicates, malformed choices and imported answer keys", () => {
  for (const mutate of [
    (d) => (d.questions[0].sourceHash = "stale"),
    (d) => d.questions.push(d.questions[0]),
    (d) => d.questions[0].choices.pop(),
    (d) => (d.questions[0].choices[1] = d.questions[0].choices[0]),
    (d) => (d.questions[0].choices[0] = ""),
    (d) => (d.questions[0].correct = 3),
    (d) => (d.questions[0].text = "Untranslated English question"),
    (d) => (d.sourceRevision = "stale"),
  ]) {
    const copy = structuredClone(document);
    mutate(copy);
    assert.throws(() => validateTranslations(copy));
  }
});
test("UI localization keeps canonical labels and English text stable, and handles dynamic labels", () => {
  assert.equal(translate("Next question", "en"), "Next question");
  assert.equal(translate("Next question", "uk"), "Наступне запитання");
  assert.equal(translate("1 question available with these settings.", "uk"), "Доступно запитань із цими налаштуваннями: 1.");
  assert.equal(
    translate("Secured: 1,000 pts", "uk"),
    "Гарантовано: 1,000 балів",
  );
  assert.equal(translate("QUESTION 2 / 10", "uk"), "ЗАПИТАННЯ 2 / 10");
  assert.equal(translate("Animals · Music", "uk"), "Тварини · Музика");
  assert.equal(
    translate("Ready, what’s your answer?", "uk"),
    "Ready, яка ваша відповідь?",
  );
});
