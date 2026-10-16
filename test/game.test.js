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
test("answer locking, hidden answers, reveal scoring and advancement", () => {
  const game = createGame(settings());
  const a = addPlayer(game, "A"),
    b = addPlayer(game, "B");
  start(game);
  assert(!("correct" in view(game).question));
  assert(!("questions" in view(game)));
  answer(game, a.id, game.questions[0].correct);
  assert.throws(() => answer(game, a.id, 0), /already locked/);
  assert(!("answer" in view(game, b.id).players[0]));
  assert.equal(view(game, b.id).myAnswer, null);
  assert.equal(view(game).players[0].score, 0);
  answer(game, b.id, (game.questions[0].correct + 1) % 4);
  assert.equal(game.phase, "reveal");
  assert.equal(game.scores[a.id], 100);
  assert.equal(game.scores[b.id], 0);
  assert.throws(() => reveal(game), /No question/);
  assert.throws(() => answer(game, b.id, 0), /closed/);
  next(game, game.review.endsAt);
  assert.equal(game.index, 1);
  assert.deepEqual(game.answers, {});
});
test("Millionaire lifeline never removes correct answer, cannot be reused, and safety floor applies", () => {
  const game = createGame(settings("millionaire"));
  const p = addPlayer(game, "Solo");
  start(game);
  fifty(game);
  assert.equal(game.eliminated.length, 2);
  assert(!game.eliminated.includes(game.questions[0].correct));
  assert.throws(() => answer(game, p.id, game.eliminated[0]), /available/);
  assert.throws(() => fifty(game), /unavailable/);
  for (let i = 0; i < 5; i++) {
    answer(game, p.id, game.questions[game.index].correct);
    next(game, game.review.endsAt);
  }
  assert.equal(game.secured, 1000);
  answer(game, p.id, (game.questions[game.index].correct + 1) % 4);
  next(game, game.review.endsAt);
  assert.equal(game.phase, "finished");
  assert.equal(game.won, 1000);
  assert.equal(game.finishReason, "wrong");
});
test("Millionaire second checkpoint, full completion and walking away", () => {
  const game = createGame(settings("millionaire"));
  const p = addPlayer(game, "Solo");
  start(game);
  for (let i = 0; i < 15; i++) {
    answer(game, p.id, game.questions[game.index].correct);
    if (i === 9) assert.equal(game.secured, 32000);
    next(game, game.review.endsAt);
  }
  assert.equal(game.won, 1000000);
  assert.equal(game.phase, "finished");
  const short = createGame(settings("millionaire", "Europe", ["Science"]));
  const p2 = addPlayer(short, "Solo");
  start(short);
  answer(short, p2.id, short.questions[0].correct);
  next(short, short.review.endsAt);
  walk(short);
  assert.equal(short.won, ladder[0]);
  assert.equal(short.finishReason, "walked");
  assert.throws(() => start(short), /already/);
});
test("state transitions reject invalid play and completed Trivia stays finished", () => {
  const game = createGame(settings());
  assert.throws(() => start(game), /player/);
  const p = addPlayer(game, "Player");
  assert.throws(() => addPlayer(game, "player"), /already/);
  start(game);
  assert.throws(() => addPlayer(game, "late"), /started/);
  assert.throws(() => answer(game, p.id, -1), /available/);
  assert.throws(() => answer(game, "stranger", 0), /Unknown/);
  assert.throws(() => next(game), /Reveal/);
  for (let i = 0; i < game.questions.length; i++) {
    answer(game, p.id, game.questions[game.index].correct);
    next(game, game.review.endsAt);
  }
  assert.equal(game.phase, "finished");
  assert.equal(game.scores[p.id], game.questions.length * 100);
});

test("five-second review auto-advances once; pause preserves exact remaining time", () => {
  const game = createGame(settings());
  const p = addPlayer(game, "One");
  start(game);
  answer(game, p.id, game.questions[0].correct, 1000);
  assert.equal(game.phase, "reveal");
  assert.equal(REVIEW_DURATION_MS, 5000);
  assert.equal(game.review.endsAt, 6000);
  assert.equal(advance(game, 5999), false);
  pauseReview(game, 2750);
  assert.equal(game.review.remainingMs, 3250);
  assert.equal(game.review.endsAt, null);
  assert.equal(advance(game, 100000), false);
  assert.throws(() => next(game, 100000), /still running/);
  assert.throws(() => pauseReview(game, 3000), /no running review/);
  resumeReview(game, 200000);
  assert.equal(game.review.endsAt, 203250);
  assert.equal(advance(game, 203249), false);
  assert.equal(advance(game, 203250), true);
  assert.equal(game.index, 1);
  assert.equal(game.review, null);
  assert.equal(advance(game, 300000), false);
  assert.equal(game.scores[p.id], 100);
  assert.throws(() => resumeReview(game), /not paused/);
});
test("last and losing answers keep their review window before automatic final results", () => {
  for (const mode of ["trivia", "millionaire"]) {
    const game = createGame(settings(mode));
    const p = addPlayer(game, "One");
    start(game);
    game.index = game.questions.length - 1;
    answer(
      game,
      p.id,
      mode === "millionaire"
        ? (game.questions[game.index].correct + 1) % 4
        : game.questions[game.index].correct,
      1000,
    );
    assert.equal(game.phase, "reveal");
    assert.equal(advance(game, 5999), false);
    assert.equal(advance(game, 6000), true);
    assert.equal(game.phase, "finished");
    assert.equal(game.review, null);
  }
});
