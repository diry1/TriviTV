import test from "node:test";
import assert from "node:assert/strict";
import { questions, categories } from "../src/questions.js";
import {
  createGame,
  addPlayer,
  start,
  answer,
  reveal,
  next,
  fifty,
  walk,
  view,
  selectQuestions,
  ladder,
  advance,
  pauseReview,
  resumeReview,
  REVIEW_DURATION_MS,
  ANSWER_DURATION_MS,
  ANSWERS_REVEAL_MS,
  CORRECT_REVEAL_MS,
  nextDeadline,
} from "../src/game.js";
const settings = (mode = "trivia", region = "Europe", cats = categories) => ({
  mode,
  region,
  categories: cats,
});

test("question bank has four unique choices, valid regions, balanced difficulties, and unique IDs", () => {
  assert.equal(new Set(questions.map((q) => q.id)).size, questions.length);
  for (const q of questions) {
    assert.equal(q.choices.length, 4);
    assert.equal(new Set(q.choices).size, 4);
    assert(["Europe", "US", "Global"].includes(q.region));
    assert(categories.includes(q.category));
    assert([1, 2, 3].includes(q.difficulty));
  }
  for (const region of ["Europe", "US"])
    assert(selectQuestions(settings("millionaire", region)).length === 15);
});
test("regions change the audience references and exclusions apply to both modes", () => {
  for (const mode of ["millionaire", "trivia"])
    for (const region of ["Europe", "US"])
      for (const category of categories) {
        const selected = selectQuestions(settings(mode, region, [category]));
        assert(selected.length > 0);
        assert(selected.every((q) => q.category === category));
        assert(
          selected.every((q) => q.region === region || q.region === "Global"),
        );
      }
  assert.throws(() => createGame(settings("trivia", "Europe", [])), /category/);
  assert.throws(() => createGame(settings("trivia", "Asia")), /Europe or US/);
  assert(
    questions.some((q) => q.text.includes("Vienna") && q.region === "Europe"),
  );
  assert(
    questions.some((q) => q.text.includes("Washington") && q.region === "US"),
  );
});
test("free capacity is three; Party supports more; Millionaire always stays solo", () => {
  for (const party of [false, true]) {
    const game = createGame(settings(), { party });
    for (let i = 0; i < 3; i++) addPlayer(game, `P${i}`);
    if (party) {
      for (let i = 3; i < 100; i++) addPlayer(game, `P${i}`);
      assert.equal(game.players.length, 100);
    } else assert.throws(() => addPlayer(game, "P4"), /3 players/);
    const solo = createGame(settings("millionaire"), { party });
    addPlayer(solo, "One");
    assert.throws(() => addPlayer(solo, "Two"), /one player/);
  }
});

function toReview(game) {
  assert.equal(game.phase, "answers");
  advance(game, game.stageEndsAt);
  assert.equal(game.phase, "correct");
  advance(game, game.stageEndsAt);
  assert.equal(game.phase, "reveal");
  return game.review.endsAt;
}
function finishRound(game) {
  next(game, toReview(game));
}
test("player picks appear first, then correct answer and scores, then a full three-second review", () => {
  const game = createGame(settings());
  const a = addPlayer(game, "A"),
    b = addPlayer(game, "B");
  start(game, 1000);
  assert.equal(game.questionEndsAt, 61000);
  assert(!("correct" in view(game).question));
  answer(game, a.id, game.questions[0].correct, 1001);
  assert.throws(() => answer(game, a.id, 0, 1002), /already locked/);
  assert(!("answer" in view(game, b.id).players[0]));
  assert.equal(view(game, b.id).myAnswer, null);
  answer(game, b.id, (game.questions[0].correct + 1) % 4, 1003);
  assert.equal(game.phase, "answers");
  assert.equal(game.stageEndsAt, 1003 + ANSWERS_REVEAL_MS);
  assert.equal(view(game).players[0].answer, game.questions[0].correct);
  assert(!("correct" in view(game).question));
  assert.equal(game.scores[a.id], 0);
  assert.equal(game.review, null);
  assert.equal(advance(game, game.stageEndsAt - 1), false);
  advance(game, game.stageEndsAt);
  assert.equal(game.phase, "correct");
  assert.equal(game.scores[a.id], 100);
  assert.equal(game.scores[b.id], 0);
  assert(Number.isInteger(view(game).question.correct));
  assert.equal(game.review, null);
  const reviewStart = game.stageEndsAt;
  advance(game, reviewStart);
  assert.equal(game.phase, "reveal");
  assert.equal(REVIEW_DURATION_MS, 3000);
  assert.equal(game.review.endsAt, reviewStart + 3000);
  assert.equal(advance(game, game.review.endsAt - 1), false);
  advance(game, game.review.endsAt);
  assert.equal(game.index, 1);
  assert.deepEqual(game.answers, {});
  assert.equal(game.autoPicked.length, 0);
  assert.equal(game.questionEndsAt, reviewStart + 3000 + ANSWER_DURATION_MS);
  assert.equal(game.scores[a.id], 100);
});
test("Trivia timeout randomly fills only missing players, labels picks, and rejects late answers", () => {
  const game = createGame(settings());
  const a = addPlayer(game, "A"),
    b = addPlayer(game, "B"),
    c = addPlayer(game, "C");
  start(game, 1000);
  answer(game, a.id, 2, 60000);
  assert.equal(advance(game, 60999), false);
  assert.throws(() => answer(game, b.id, 1, 61000), /Time is up/);
  advance(game, 61000);
  assert.equal(game.phase, "answers");
  assert.equal(game.answers[a.id], 2);
  assert.deepEqual(game.autoPicked, [b.id, c.id]);
  for (const id of [b.id, c.id])
    assert(
      Number.isInteger(game.answers[id]) &&
        game.answers[id] >= 0 &&
        game.answers[id] < 4,
    );
  assert(view(game).players.filter((p) => p.autoPicked).length === 2);
  assert(!("correct" in view(game).question));
  assert.equal(game.questionEndsAt, null);
  assert.throws(() => answer(game, b.id, 1, 61001), /closed/);
  const snapshot = { ...game.answers };
  advance(game, game.stageEndsAt);
  assert.deepEqual(game.answers, snapshot);
});
test("everyone answering early skips the minute; Millionaire has no question deadline", () => {
  const trivia = createGame(settings());
  const p = addPlayer(trivia, "One");
  start(trivia, 1000);
  answer(trivia, p.id, 0, 1001);
  assert.equal(trivia.phase, "answers");
  assert.deepEqual(trivia.autoPicked, []);
  const solo = createGame(settings("millionaire"));
  addPlayer(solo, "Solo");
  start(solo, 1000);
  assert.equal(solo.questionEndsAt, null);
  assert.equal(nextDeadline(solo), null);
  assert.equal(advance(solo, 1e12), false);
  assert.equal(solo.phase, "question");
});
test("Millionaire lifeline never removes correct answer; checkpoints, loss and completion work through staged reveals", () => {
  const game = createGame(settings("millionaire"));
  const p = addPlayer(game, "Solo");
  start(game, 0);
  fifty(game);
  assert.equal(game.eliminated.length, 2);
  assert(!game.eliminated.includes(game.questions[0].correct));
  assert.throws(() => answer(game, p.id, game.eliminated[0], 1), /available/);
  assert.throws(() => fifty(game), /unavailable/);
  for (let i = 0; i < 5; i++) {
    answer(game, p.id, game.questions[game.index].correct, 1000 + i * 10000);
    finishRound(game);
  }
  assert.equal(game.secured, 1000);
  answer(game, p.id, (game.questions[game.index].correct + 1) % 4, 100000);
  finishRound(game);
  assert.equal(game.phase, "finished");
  assert.equal(game.won, 1000);
  assert.equal(game.finishReason, "wrong");
  const full = createGame(settings("millionaire"));
  const p2 = addPlayer(full, "Solo");
  start(full, 0);
  for (let i = 0; i < 15; i++) {
    answer(full, p2.id, full.questions[full.index].correct, i * 10000);
    toReview(full);
    if (i === 9) assert.equal(full.secured, 32000);
    next(full, full.review.endsAt);
  }
  assert.equal(full.won, 1000000);
  assert.equal(full.phase, "finished");
});
test("only Millionaire supports pausing; exact remaining time survives multiple pause/resume cycles", () => {
  const game = createGame(settings("millionaire"));
  const p = addPlayer(game, "One");
  start(game, 0);
  answer(game, p.id, game.questions[0].correct, 1000);
  assert.throws(() => pauseReview(game, 1001), /no running review/);
  toReview(game);
  const end = game.review.endsAt;
  pauseReview(game, end - 2250);
  assert.equal(game.review.remainingMs, 2250);
  assert.equal(game.review.endsAt, null);
  assert.equal(advance(game, 100000), false);
  assert.throws(() => next(game, 100000), /still running/);
  resumeReview(game, 200000);
  assert.equal(game.review.endsAt, 202250);
  pauseReview(game, 202000);
  assert.equal(game.review.remainingMs, 250);
  resumeReview(game, 300000);
  assert.equal(advance(game, 300249), false);
  assert.equal(advance(game, 300250), true);
  assert.equal(game.index, 1);
  assert.equal(game.review, null);
  assert.equal(game.scores[p.id], 100);
  const trivia = createGame(settings());
  const p2 = addPlayer(trivia, "One");
  start(trivia, 0);
  answer(trivia, p2.id, 0, 1);
  toReview(trivia);
  assert.throws(() => pauseReview(trivia, 2), /Millionaire only/);
  assert.throws(() => resumeReview(trivia, 2), /Millionaire only/);
});
test("last and losing answers finish only after both animations and the three-second review", () => {
  for (const mode of ["trivia", "millionaire"]) {
    const game = createGame(settings(mode));
    const p = addPlayer(game, "One");
    start(game, 0);
    game.index = game.questions.length - 1;
    answer(
      game,
      p.id,
      mode === "millionaire"
        ? (game.questions[game.index].correct + 1) % 4
        : game.questions[game.index].correct,
      1000,
    );
    const end = toReview(game);
    assert.equal(advance(game, end - 1), false);
    advance(game, end);
    assert.equal(game.phase, "finished");
    assert.equal(game.review, null);
  }
});
test("invalid transitions stay rejected and walk-away preserves prior winnings", () => {
  const game = createGame(settings("millionaire"));
  assert.throws(() => start(game, 0), /player/);
  const p = addPlayer(game, "One");
  assert.throws(() => addPlayer(game, "One"), /one player/);
  start(game, 0);
  assert.throws(() => next(game, 0), /Reveal/);
  assert.throws(() => answer(game, "stranger", 0, 1), /Unknown/);
  assert.throws(() => answer(game, p.id, -1, 1), /available/);
  answer(game, p.id, game.questions[0].correct, 1);
  assert.throws(() => walk(game), /before answering/);
  finishRound(game);
  walk(game);
  assert.equal(game.won, ladder[0]);
  assert.equal(game.finishReason, "walked");
});
