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
    return { status: res.status, data: await res.json() };
  };
}
test("HTTP flow automatically reveals only after everyone answers; only Player 1 pauses", async (t) => {
  let clock = 1000;
  const api = await fixture(t, false, { now: () => clock });
  const host = (await api("/api/rooms", settings)).data;
  const { code, token } = host;
  const phone = (await api("/api/join", { code, name: "Phone" })).data;
  const action = (data, key = token) =>
    api(`/api/rooms/${code}/action`, data, key);
  assert.equal((await api(`/api/rooms/${code}`)).status, 403);
  assert.equal((await action({ type: "start" }, phone.token)).status, 403);
  const started = (await action({ type: "start" })).data;
  const questionId = started.question.id;
  assert(!("correct" in started.question));
  const first = await action(
    {
      type: "answer",
      choice: 0,
      questionId,
      playerId: host.state.players[0].id,
    },
    phone.token,
  );
  assert.equal(first.status, 200);
  assert.equal(first.data.phase, "question");
  assert(!("correct" in first.data.question));
  assert.equal((await action({ type: "reveal" })).status, 400); // no manual bypass
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
  const revealed = (
    await action({
      type: "answer",
      choice: 0,
      questionId,
      playerId: host.state.players[0].id,
    })
  ).data;
  assert.equal(revealed.phase, "reveal");
  assert(Number.isInteger(revealed.question.correct));
  assert.equal(revealed.review.endsAt, 6000);
  assert.equal(
    (await action({ type: "pause", questionId }, phone.token)).status,
    403,
  );
  clock = 2500;
  const paused = (await action({ type: "pause", questionId })).data;
  assert.equal(paused.review.remainingMs, 3500);
  assert(paused.review.paused);
  clock = 100000;
  assert(
    (await api(`/api/rooms/${code}`, undefined, phone.token)).data.review
      .paused,
  );
  assert.equal(
    (await action({ type: "resume", questionId }, phone.token)).status,
    403,
  );
  const resumed = (await action({ type: "resume", questionId })).data;
  assert.equal(resumed.review.endsAt, 103500);
  clock = 103499;
  assert.equal(
    (await api(`/api/rooms/${code}`, undefined, token)).data.phase,
    "reveal",
  );
  clock = 103500;
  const advanced = (await api(`/api/rooms/${code}`, undefined, token)).data;
  assert.equal(advanced.index, 1);
  assert.equal(advanced.phase, "question");
  assert(!("correct" in advanced.question));
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
  assert.equal((await action({ type: "next" })).status, 400);
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
test("demo permits larger groups; solo phone Player 1 owns pause after handoff", async (t) => {
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
  assert.equal(
    (await action({ type: "answer", choice: 0, questionId }, phone.token)).data
      .phase,
    "reveal",
  );
  assert.equal(
    (await action({ type: "pause", questionId }, solo.token)).status,
    403,
  );
  assert.equal(
    (await action({ type: "pause", questionId }, phone.token)).status,
    200,
  );
  clock = 20000;
  assert(
    (await api(`/api/rooms/${solo.code}`, undefined, phone.token)).data.review
      .paused,
  );
  assert.equal(
    (await action({ type: "resume", questionId }, phone.token)).status,
    200,
  );
});
test("server timer advances without a polling client, and stops while paused", async (t) => {
  let clockReads = 0;
  const api = await fixture(t, false, {
    reviewDurationMs: 150,
    now: () => {
      clockReads++;
      return Date.now();
    },
  });
  const host = (await api("/api/rooms", settings)).data;
  const path = `/api/rooms/${host.code}`;
  const action = (data) => api(path + "/action", data, host.token);
  let playing = (await action({ type: "start" })).data;
  await action({
    type: "answer",
    choice: 0,
    questionId: playing.question.id,
    playerId: playing.players[0].id,
  });
  const reads = clockReads;
  await delay(300);
  assert(clockReads > reads, "the timer must run without HTTP polling");
  playing = (await api(path, undefined, host.token)).data;
  assert.equal(playing.index, 1);
  await action({
    type: "answer",
    choice: 0,
    questionId: playing.question.id,
    playerId: playing.players[0].id,
  });
  await action({ type: "pause", questionId: playing.question.id });
  const pausedReads = clockReads;
  await delay(300);
  assert.equal(clockReads, pausedReads);
  assert((await api(path, undefined, host.token)).data.review.paused);
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
