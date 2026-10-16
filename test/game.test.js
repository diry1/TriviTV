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
  reveal(game);
  assert.equal(game.scores[a.id], 100);
  assert.equal(game.scores[b.id], 0);
  assert.throws(() => reveal(game), /No question/);
  assert.throws(() => answer(game, b.id, 0), /closed/);
  next(game);
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
    reveal(game);
    next(game);
  }
  assert.equal(game.secured, 1000);
  answer(game, p.id, (game.questions[game.index].correct + 1) % 4);
  reveal(game);
  next(game);
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
    reveal(game);
    if (i === 9) assert.equal(game.secured, 32000);
    next(game);
  }
  assert.equal(game.won, 1000000);
  assert.equal(game.phase, "finished");
  const short = createGame(settings("millionaire", "Europe", ["Science"]));
  const p2 = addPlayer(short, "Solo");
  start(short);
  answer(short, p2.id, short.questions[0].correct);
  reveal(short);
  next(short);
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
    reveal(game);
    next(game);
  }
  assert.equal(game.phase, "finished");
  assert.equal(game.scores[p.id], game.questions.length * 100);
});
