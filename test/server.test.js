import test from "node:test";
import assert from "node:assert/strict";
import { createAppServer } from "../src/server.js";
const settings = {
  mode: "trivia",
  region: "Europe",
  categories: ["Geography", "Entertainment"],
};
async function fixture(t, partyDemo = false) {
  const s = createAppServer({ partyDemo });
  await new Promise((r) => s.listen(0, "127.0.0.1", r));
  t.after(
    () =>
      new Promise((r) => {
        s.closeAllConnections();
        s.close(r);
      }),
  );
  const base = `http://127.0.0.1:${s.address().port}`;
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
test("real HTTP multiplayer flow enforces roles, hides answers and scores a question", async (t) => {
  const api = await fixture(t);
  const host = await api("/api/rooms", settings);
  assert.equal(host.status, 201);
  const { code, token } = host.data;
  const player = await api("/api/join", { code, name: "Phone" });
  assert.equal(player.status, 201);
  assert.equal((await api(`/api/rooms/${code}`)).status, 403);
  assert.equal(
    (
      await api(
        `/api/rooms/${code}/action`,
        { type: "start" },
        player.data.token,
      )
    ).status,
    403,
  );
  const started = await api(
    `/api/rooms/${code}/action`,
    { type: "start" },
    token,
  );
  assert(!("correct" in started.data.question));
  assert.equal(
    (
      await api(
        `/api/rooms/${code}/action`,
        { type: "answer", choice: 0, playerId: host.data.state.players[0].id },
        player.data.token,
      )
    ).status,
    200,
  );
  const state = (await api(`/api/rooms/${code}`, undefined, token)).data;
  assert(state.players.find((p) => p.name === "Phone").answered);
  assert(!state.players.find((p) => p.local).answered);
  assert.equal(
    (
      await api(
        `/api/rooms/${code}/action`,
        { type: "answer", choice: 0, playerId: player.data.playerId },
        token,
      )
    ).status,
    403,
  );
  const revealed = await api(
    `/api/rooms/${code}/action`,
    { type: "reveal" },
    token,
  );
  assert(Number.isInteger(revealed.data.question.correct));
  assert.equal(
    (await api(`/api/rooms/${code}/action`, { type: "next" }, token)).data
      .index,
    1,
  );
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
test("explicit demo unlock permits a fourth player and Millionaire phone handoff stays solo", async (t) => {
  const api = await fixture(t, true);
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
  const phone = await api("/api/join", { code: solo.code, name: "Solo phone" });
  assert.equal(phone.status, 201);
  assert.equal(phone.data.state.players.length, 1);
  assert.equal(
    (await api("/api/join", { code: solo.code, name: "Second phone" })).status,
    409,
  );
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
