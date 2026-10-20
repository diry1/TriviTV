import test from "node:test";
import assert from "node:assert/strict";
import { setTimeout as delay } from "node:timers/promises";
import { createAppServer } from "../src/server.js";
const settings = {
  mode: "trivia",
  region: "Europe",
  categories: ["Geography", "Entertainment"],
};
async function fixture(t, partyDemo = false, options = {}) {
  const server = createAppServer({ partyDemo, ...options });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  t.after(
    () =>
      new Promise((r) => {
        server.closeAllConnections();
        server.close(r);
      }),
  );
  const base = `http://127.0.0.1:${server.address().port}`;
  return async (path, data, token) => {
    const res = await fetch(base + path, {
      method: data ? "POST" : "GET",
      headers: {
        ...(data ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      ...(data ? { body: JSON.stringify(data) } : {}),
    });
    return {
      status: res.status,
      data: res.headers.get("content-type")?.includes("application/json")
        ? await res.json()
        : await res.text(),
    };
  };
}
test("HTTP flow has separate pick/correct/review stages and supports Trivia pause and rejects stale answers", async (t) => {
  let clock = 1000;
  const api = await fixture(t, false, { now: () => clock });
  const host = (await api("/api/rooms", settings)).data;
  const { code, token } = host;
  const phone = (await api("/api/join", { code, name: "Phone" })).data;
  const action = (data, key = token) =>
    api(`/api/rooms/${code}/action`, data, key);
  const read = async () =>
    (await api(`/api/rooms/${code}`, undefined, token)).data;
  assert.equal((await api(`/api/rooms/${code}`)).status, 403);
  assert.equal((await action({ type: "start" }, phone.token)).status, 403);
  const started = (await action({ type: "start" })).data;
  const questionId = started.question.id;
  assert.equal(started.questionEndsAt, 61000);
  assert(!("correct" in started.question));
  assert.equal(
    (await action({ type: "answer", choice: 0, questionId }, phone.token)).data
      .phase,
    "question",
  );
  assert.equal((await action({ type: "reveal" })).status, 400);
  assert.equal(
    (
      await action({
        type: "answer",
        choice: 0,
        questionId,
        playerId: phone.playerId,
      })
    ).status,
    403,
  );
  let state = (
    await action({
      type: "answer",
      choice: 0,
      questionId,
      playerId: host.state.players[0].id,
    })
  ).data;
  assert.equal(state.phase, "answers");
  assert(!("correct" in state.question));
  assert(state.players.every((p) => p.score === 0));
  assert.equal(state.review, null);
  clock = state.stageEndsAt;
  state = await read();
  assert.equal(state.phase, "correct");
  assert(Number.isInteger(state.question.correct));
  assert.equal(state.review, null);
  clock = state.stageEndsAt;
  state = await read();
  assert.equal(state.phase, "reveal");
  assert.equal(state.review.endsAt, clock + 4000);
  assert.equal((await action({ type: "pause", questionId })).status, 200);
  assert.equal((await action({ type: "resume", questionId })).status, 200);
  assert.equal(
    (await action({ type: "pause", questionId }, phone.token)).status,
    403,
  );
  clock = state.review.endsAt;
  state = await read();
  assert.equal(state.index, 1);
  assert.equal(state.phase, "question");
  assert.equal(state.questionEndsAt, clock + 60000);
  assert.equal(
    (
      await action({
        type: "answer",
        choice: 0,
        playerId: host.state.players[0].id,
        questionId,
      })
    ).status,
    409,
  );
  assert.equal(
    (await action({ type: "next", questionId: state.question.id })).status,
    400,
  );
});
test("late HTTP answers cannot replace a timeout random pick", async (t) => {
  let clock = 1000;
  const api = await fixture(t, false, { now: () => clock });
  const host = (await api("/api/rooms", settings)).data;
  const phone = (await api("/api/join", { code: host.code, name: "Phone" }))
    .data;
  const path = `/api/rooms/${host.code}`;
  const action = (data, token = host.token) =>
    api(path + "/action", data, token);
  const playing = (await action({ type: "start" })).data;
  const questionId = playing.question.id;
  await action({
    type: "answer",
    choice: 2,
    questionId,
    playerId: playing.players[0].id,
  });
  clock = playing.questionEndsAt;
  assert.equal(
    (await action({ type: "answer", choice: 1, questionId }, phone.token))
      .status,
    409,
  );
  const state = (await api(path, undefined, host.token)).data;
  assert.equal(state.phase, "answers");
  assert.equal(state.players[0].answer, 2);
  assert.equal(state.players[0].autoPicked, false);
  assert.equal(state.players[1].autoPicked, true);
  assert([0, 1, 2, 3].includes(state.players[1].answer));
  assert(!("correct" in state.question));
});
test("Party cannot be unlocked by a client flag; free cap includes the host", async (t) => {
  const api = await fixture(t);
  assert.equal(
    (await api("/api/rooms", { ...settings, party: true })).status,
    403,
  );
  const host = (await api("/api/rooms", settings)).data;
  for (const name of ["Two", "Three"])
    assert.equal(
      (await api("/api/join", { code: host.code, name })).status,
      201,
    );
  assert.equal(
    (await api("/api/join", { code: host.code, name: "Four" })).status,
    409,
  );
});
test("demo permits larger groups; Millionaire phone handoff stays solo without pause", async (t) => {
  let clock = 1000;
  const api = await fixture(t, true, { now: () => clock });
  const host = (await api("/api/rooms", { ...settings, party: true })).data;
  for (let i = 0; i < 5; i++)
    assert.equal(
      (await api("/api/join", { code: host.code, name: `P${i}` })).status,
      201,
    );
  const solo = (
    await api("/api/rooms", { ...settings, mode: "millionaire", party: true })
  ).data;
  assert.equal(
    (await api("/api/join", { code: solo.code, name: "" })).status,
    400,
  );
  assert.equal(
    (await api(`/api/rooms/${solo.code}`, undefined, solo.token)).data.players
      .length,
    1,
  );
  const phone = (
    await api("/api/join", { code: solo.code, name: "Solo phone" })
  ).data;
  assert.equal(phone.state.players.length, 1);
  assert.equal(
    (await api("/api/join", { code: solo.code, name: "Second phone" })).status,
    409,
  );
  const action = (data, token) =>
    api(`/api/rooms/${solo.code}/action`, data, token);
  const playing = (await action({ type: "start" }, solo.token)).data;
  const questionId = playing.question.id;
  let state = (
    await action({ type: "answer", choice: 0, questionId }, phone.token)
  ).data;
  assert.equal(state.phase, "answers");
  clock = state.stageEndsAt;
  state = (await api(`/api/rooms/${solo.code}`, undefined, phone.token)).data;
  assert.equal(state.phase, "correct");
  clock = state.stageEndsAt;
  state = (await api(`/api/rooms/${solo.code}`, undefined, phone.token)).data;
  assert.equal(state.phase, "reveal");
  assert.equal(
    (await action({ type: "pause", questionId }, solo.token)).status,
    403,
  );
  assert.equal(
    (await action({ type: "pause", questionId }, phone.token)).status,
    409,
  );
  assert.equal(state.review, null);
  clock += 60000;
  state = (await api(`/api/rooms/${solo.code}`, undefined, solo.token)).data;
  assert.equal(state.phase, "reveal");
  assert.equal(
    (await action({ type: "next", questionId }, phone.token)).status,
    403,
  );
  assert.equal(
    (await action({ type: "next", questionId: "stale" }, solo.token)).status,
    409,
  );
  const continued = await action({ type: "next", questionId }, solo.token);
  assert.equal(continued.status, 200);
  assert.notEqual(continued.data.phase, "reveal");
});
test("server timers fill timed-out Trivia answers without polling", async (t) => {
  let reads = 0;
  const api = await fixture(t, false, {
    answerDurationMs: 30,
    answersRevealMs: 20,
    correctRevealMs: 20,
    reviewDurationMs: 20000,
    now: () => {
      reads++;
      return Date.now();
    },
  });
  const host = (await api("/api/rooms", settings)).data;
  const path = `/api/rooms/${host.code}`;
  await api(path + "/action", { type: "start" }, host.token);
  const before = reads;
  await delay(200);
  assert(reads > before);
  const state = (await api(path, undefined, host.token)).data;
  assert.equal(state.phase, "reveal");
  assert(
    state.players.every((p) => p.autoPicked && [0, 1, 2, 3].includes(p.answer)),
  );
});
test("Trivia timers advance independently and freeze during pause", async (t) => {
  const { questions } = await import("../src/questions.js");
  let reads = 0;
  const api = await fixture(t, false, {
    answersRevealMs: 20,
    correctRevealMs: 20,
    reviewDurationMs: 500,
    now: () => {
      reads++;
      return Date.now();
    },
  });
  const host = (await api("/api/rooms", settings)).data;
  const path = `/api/rooms/${host.code}`;
  const action = (data) => api(path + "/action", data, host.token);
  let playing = (await action({ type: "start" })).data;
  const pick = (state) => ({
    type: "answer",
    questionId: state.question.id,
    playerId: state.players[0].id,
    choice: state.question.choices.indexOf(
      questions.find((q) => q.id === state.question.id).choices[0],
    ),
  });
  await action(pick(playing));
  await delay(800);
  playing = (await api(path, undefined, host.token)).data;
  assert.equal(playing.index, 1);
  let state = (await action(pick(playing))).data;
  for (let i = 0; i < 50 && state.phase !== "reveal"; i++) {
    await delay(5);
    state = (await api(path, undefined, host.token)).data;
  }
  assert.equal(state.phase, "reveal");
  await action({ type: "pause", questionId: playing.question.id });
  const pausedReads = reads;
  await delay(600);
  assert.equal(reads, pausedReads);
  assert((await api(path, undefined, host.token)).data.review.paused);
  await action({ type: "resume", questionId: playing.question.id });
  await delay(650);
  assert.equal((await api(path, undefined, host.token)).data.index, 2);
});
test("malformed input and invalid authentication return controlled errors", async (t) => {
  const api = await fixture(t);
  assert.equal(
    (await api("/api/rooms", { ...settings, categories: [] })).status,
    400,
  );
  assert.equal(
    (await api("/api/join", { code: "ABCDEF", name: "No room" })).status,
    404,
  );
  const host = (await api("/api/rooms", settings)).data;
  assert.equal(
    (await api(`/api/rooms/${host.code}`, undefined, "é".repeat(48))).status,
    403,
  );
  assert.equal(
    (
      await api(
        `/api/rooms/${host.code}/action`,
        { type: "unknown" },
        host.token,
      )
    ).status,
    400,
  );
});

test("only Player 1 can pause timed Trivia questions, and answers are blocked until resumed", async (t) => {
  let clock = 1000;
  const api = await fixture(t, false, { now: () => clock });
  const host = (await api("/api/rooms", settings)).data;
  const phone = (await api("/api/join", { code: host.code, name: "Phone" }))
    .data;
  const path = `/api/rooms/${host.code}`;
  const action = (body, token = host.token) =>
    api(path + "/action", body, token);
  const state = (await action({ type: "start" })).data;
  const questionId = state.question.id;
  clock = 11000;
  assert.equal(
    (await action({ type: "pause", questionId }, phone.token)).status,
    403,
  );
  const paused = (await action({ type: "pause", questionId })).data;
  assert(paused.questionPaused);
  assert.equal(paused.questionRemainingMs, 50000);
  clock = 100000;
  assert.equal(
    (await action({ type: "answer", choice: 0, questionId }, phone.token))
      .status,
    409,
  );
  assert.equal(
    (await action({ type: "resume", questionId }, phone.token)).status,
    403,
  );
  const resumed = (await action({ type: "resume", questionId })).data;
  assert.equal(resumed.questionEndsAt, 150000);
  assert.equal(
    (await action({ type: "answer", choice: 0, questionId }, phone.token))
      .status,
    200,
  );
});

test("source-based categories and attribution are available without exposing answers", async (t) => {
  const api = await fixture(t);
  const config = (await api("/api/config")).data;
  assert.equal(config.categories.length, 20);
  assert(config.categories.includes("Movies"));
  assert(config.categories.includes("Science & Technology"));
  assert.equal(config.bank.name, "OpenTriviaQA");
  assert(config.bank.count > 10000);
  assert.equal(config.bank.license, "CC-BY-SA-4.0");
  assert(!("questions" in config));
  const credits = await api("/credits");
  assert.equal(credits.status, 200);
  assert.match(credits.data, /Attribution–ShareAlike/);
  assert.match(credits.data, /Changes made/);
  const license = await api("/licenses/opentriviaqa.txt");
  assert.equal(license.status, 200);
  assert.match(license.data, /Attribution-ShareAlike 4.0/);
  assert.equal((await api("/data/opentriviaqa/questions.json")).status, 404);
});

test("Ukrainian room language is shared with phones and hidden answer keys remain hidden", async (t) => {
  const api = await fixture(t);
  const config = (await api("/api/config")).data;
  assert.equal(config.languages.en.count, 38926);
  assert(config.languages.uk.count > 0);
  assert.equal(config.languages.uk.status, "preview");
  assert(config.pools.uk.Europe.count < config.languages.uk.count);
  assert(config.pools.en.Europe.count < config.languages.en.count);
  assert.equal(Object.values(config.pools.uk.Europe.categories).reduce((a, b) => a + b, 0), config.pools.uk.Europe.count);
  const host = (await api("/api/rooms", { ...settings, language: "uk" })).data;
  assert.equal(host.state.settings.language, "uk");
  assert.equal(host.state.players[0].name, "ТВ-гравець");
  const phone = (await api("/api/join", { code: host.code, name: "Ready" }))
    .data;
  assert.equal(phone.state.settings.language, "uk");
  const state = (
    await api(`/api/rooms/${host.code}/action`, { type: "start" }, host.token)
  ).data;
  assert.match(state.question.text, /[А-Яа-яІіЇїЄєҐґ]/u);
  assert.equal(state.question.correct, undefined);
  assert.equal(
    (await api(`/api/rooms/${host.code}`, undefined, phone.token)).data.question
      .text,
    state.question.text,
  );
  assert.equal(
    (await api("/api/rooms", { ...settings, language: "invalid" })).status,
    400,
  );
  assert.match((await api("/i18n.js")).data, /export function translate/);
});
