const app = document.querySelector("#app");
const esc = (v) =>
  String(v ?? "").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
let config,
  session,
  state,
  screen = "home",
  mode = "trivia",
  region = "Europe",
  selected = new Set(),
  party = false,
  localPlayer = null,
  busy = false,
  snapshot = "",
  connectionLost = false,
  pollEpoch = 0;
try {
  session = JSON.parse(sessionStorage.getItem("trivitv-session") || "null");
} catch {}
const params = new URLSearchParams(location.search);
const prefill = params.get("join");
function notify(message) {
  const n = document.querySelector("#notice");
  n.textContent = message;
  n.hidden = false;
  clearTimeout(notify.timer);
  notify.timer = setTimeout(() => (n.hidden = true), 6000);
}
async function api(path, body) {
  const res = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: {
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...(session ? { Authorization: `Bearer ${session.token}` } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  const data = await res.json();
  if (!res.ok) {
    const error = new Error(data.error);
    error.status = res.status;
    throw error;
  }
  return data;
}
function saveSession(value) {
  session = value;
  try {
    sessionStorage.setItem("trivitv-session", JSON.stringify(value));
  } catch {
    notify("Session storage is unavailable. Keep this tab open.");
  }
}
function setState(value) {
  state = value;
  const next = JSON.stringify(value);
  if (next !== snapshot) {
    snapshot = next;
    render();
  }
}
function status() {
  return `<div class="eyebrow">${state.settings.mode === "millionaire" ? "SOLO · MILLIONAIRE" : "MULTIPLAYER · TRIVIA"} <span class="dot">•</span> ${esc(state.settings.region)} <span class="dot">•</span> ${state.party ? "PARTY DEMO" : "FREE PLAY"}</div>`;
}
function home() {
  return `<section class="intro"><div class="eyebrow">THE SOFA IS YOUR GAME SHOW</div><h1>A little friendly<br><em>competition.</em></h1><p>One screen. Your favourite people. Something<br class="desktop"> everyone thinks they know the answer to.</p></section><div class="home-grid"><section class="setup"><div class="section-heading"><h2>Pick your game</h2><span>01 / THE FORMAT</span></div><div class="modes"><button class="mode ${mode === "trivia" ? "active" : ""}" data-mode="trivia"><span class="mode-icon">✳</span><span><strong>Trivia</strong><small>Four choices. Plenty of opinions.</small></span><span class="tag">1–3 FREE</span></button><button class="mode ${mode === "millionaire" ? "active" : ""}" data-mode="millionaire"><span class="mode-icon amber">◇</span><span><strong>Millionaire</strong><small>One player. One climb to the top.</small></span><span class="tag">SOLO</span></button></div><div class="section-heading"><h2>Make it your kind of quiz</h2><span>02 / THE MIX</span></div><div class="setting-row"><div><h3>Your region</h3><p>Familiar references, different perspectives.</p></div><div class="segmented" role="group" aria-label="Question region">${["Europe", "US"].map((r) => `<button data-region="${r}" class="${region === r ? "selected" : ""}" aria-pressed="${region === r}">${r === "Europe" ? "Europe" : "United States"}</button>`).join("")}</div></div><div class="category-head"><h3>Include categories</h3><button id="all-categories" class="text-button">${selected.size === config.categories.length ? "Clear all" : "Select all"}</button></div><div class="categories">${config.categories.map((c, i) => `<button class="chip ${selected.has(c) ? "selected" : ""}" data-category="${c}" aria-pressed="${selected.has(c)}"><span>${["◎", "♫", "⌛", "⚛", "⚑", "✎"][i]}</span>${c}<b>${selected.has(c) ? "✓" : "+"}</b></button>`).join("")}</div><p class="fine">Selected categories only. Regional questions are mixed with worldwide knowledge.</p><button class="primary start-button" id="create" ${selected.size ? "" : "disabled"}>Set up ${mode === "millionaire" ? "my climb" : "the game"} <span>→</span></button><p class="fine">${mode === "millionaire" ? "Up to 15 questions · 50:50 · Walk away · Fictional points" : "Up to 10 questions · No timers · Everyone gets a turn"}</p></section><aside><section class="party-card"><div class="eyebrow">A BIGGER NIGHT IN</div><div class="party-art">✦<span>✳</span>✧</div><h2>More friends.<br>More possibilities.</h2><p>The full game is free for up to three players. Party Passes will unlock bigger groups and extras like picture questions.</p><div class="passes"><div><strong>2 days</strong><small>For the weekend</small></div><div><strong>30 days</strong><small>Keep the party going</small></div></div><p class="fine">Planned one-time payments. Never auto-renew. Purchases and picture questions are not available yet.</p>${config.partyDemo ? `<label class="demo-toggle"><input id="party" type="checkbox" ${party ? "checked" : ""} ${mode === "millionaire" ? "disabled" : ""}> Enable development Party Mode</label><p class="fine">Testing only. No payment or paid access is granted.</p>` : ""}</section><section class="join-card"><span class="small-icon">↗</span><h3>Already have a room?</h3><p>Your phone is your controller.</p><button id="join-screen" class="secondary">Join a game <span>→</span></button></section></aside></div>`;
}
function joinForm() {
  return `<section class="join-page"><div class="eyebrow">PULL UP A SEAT</div><h1>You’re invited.</h1><p>Enter the code on the TV. No app download needed.</p><form id="join-form"><label>Room code<input name="code" id="code" maxlength="6" autocapitalize="characters" autocomplete="off" value="${esc(prefill || "")}" placeholder="A1B2C3" required pattern="[A-Fa-f0-9]{6}"></label><label>Your name<input name="name" maxlength="24" autocomplete="nickname" placeholder="What should we call you?" required></label><button class="primary">Join the room →</button></form><button id="back" class="text-button">← Back to game setup</button></section>`;
}
function people() {
  return `<div class="players">${state.players.map((p) => `<div class="player"><span class="avatar">${esc(p.name.slice(0, 1).toUpperCase())}</span><strong>${esc(p.name)}</strong><span class="muted">${p.local ? "TV remote" : "Phone"}</span><span class="player-score">${state.phase === "question" ? (p.answered ? "Locked ✓" : "Thinking…") : state.phase === "lobby" ? "Ready" : `${p.score} pts`}</span></div>`).join("")}</div>`;
}
function lobby() {
  const isHost = session.role === "host";
  const joinURL = `${location.origin}/?join=${session.code}`;
  return `<section class="room-page">${status()}<div class="room-top"><div><h1>${isHost ? "Good company?" : "You’re in."}<br><em>${isHost ? "Great. Let’s play." : "Make yourself comfortable."}</em></h1><p>${isHost ? "Add players, then start when everyone is ready." : "The TV host will start the game."}</p></div><div class="room-code"><small>ROOM CODE</small><strong>${session.code}</strong><span>${esc(location.host)} · Join a game</span></div></div><div class="lobby-grid"><section>${people()}${isHost && state.settings.mode === "trivia" ? `<form id="add-form" class="add-player"><label class="sr-only" for="local-name">Local player name</label><input id="local-name" name="name" maxlength="24" placeholder="Add a player using the TV remote" required><button class="secondary">Add player +</button></form>` : ""}${isHost ? `<button id="start" class="primary wide">Everyone’s here. Let’s play →</button>` : '<p class="waiting">Waiting for the host…</p>'}</section><aside class="room-info"><h3>Your question mix</h3><p>${esc(state.settings.categories.join(" · "))}</p><p>${state.total} questions · ${esc(state.settings.region)}</p>${state.total < 15 && state.settings.mode === "millionaire" ? '<p class="fine">This category mix has a shorter ladder. Include more categories for all 15 steps.</p>' : ""}<h3>Phones welcome</h3><p>On the same Wi-Fi, open this server’s network address on your phone and enter the room code.</p><button id="copy-link" class="secondary" data-link="${esc(joinURL)}">Copy joining link</button><p class="fine">A localhost address works only on this device. Use your computer’s LAN IP for other devices.</p>${state.party ? '<p class="demo-label">DEVELOPMENT PARTY MODE · NO PAYMENT</p>' : '<p class="fine">Free Trivia: up to 3 players. Millionaire: 1 player.</p>'}</aside></div></section>`;
}
function play() {
  const isHost = session.role === "host",
    q = state.question,
    revealed = state.phase === "reveal";
  const local = state.players.filter((p) => p.local);
  if (!local.some((p) => p.id === localPlayer))
    localPlayer = local.find((p) => !p.answered)?.id || local[0]?.id;
  const mine = isHost
    ? state.players.find((p) => p.id === localPlayer)
    : state.players.find((p) => p.id === session.playerId);
  const canAnswer = !revealed && mine && !mine.answered;
  const allAnswered = state.players.every((p) => p.answered);
  return `<section class="play-page">${status()}<div class="game-meta"><span>QUESTION ${state.index + 1} / ${state.total}</span><span class="tag">${esc(q.category)}</span>${state.settings.mode === "millionaire" ? `<span class="prize">FOR ${state.ladder[state.index].toLocaleString()} POINTS</span>` : `<span>${state.players.length} PLAYERS</span>`}</div><div class="play-grid"><section><h1 class="question">${esc(q.text)}</h1>${isHost && local.length > 1 && !revealed ? `<label class="local-picker">Answering with the remote<select id="local-player">${local.map((p) => `<option value="${p.id}" ${p.id === localPlayer ? "selected" : ""}>${esc(p.name)}${p.answered ? " · locked" : ""}</option>`).join("")}</select></label>` : ""}${mine && !revealed ? `<p class="answer-status">${mine.answered ? `${esc(mine.name)}, your answer is locked.` : `${esc(mine.name)}, what’s your answer?`}</p>` : ""}<div class="answers">${q.choices.map((choice, i) => `<button data-answer="${i}" class="answer ${revealed && i === q.correct ? "correct" : ""} ${revealed && mine?.answer === i && i !== q.correct ? "incorrect" : ""} ${!revealed && state.myAnswer === i ? "locked" : ""}" ${!canAnswer || q.eliminated.includes(i) ? "disabled" : ""}><span>${"ABCD"[i]}</span>${q.eliminated.includes(i) ? "—" : esc(choice)}${revealed && i === q.correct ? "<b>✓</b>" : ""}</button>`).join("")}</div>${revealed ? `<p class="result-note">${state.settings.mode === "millionaire" && state.finishReason === "wrong" ? `The climb ends here. You keep ${state.won.toLocaleString()} points.` : `Correct answer: ${esc(q.choices[q.correct])}`}</p>` : `<p class="fine">Answers lock immediately. ${state.players.filter((p) => p.answered).length} of ${state.players.length} locked.</p>`}${isHost ? `<div class="host-actions">${!revealed ? `<button id="reveal" class="primary" ${state.settings.mode === "millionaire" && !allAnswered ? "disabled" : ""}>${allAnswered ? "Reveal the answer" : "Reveal · unanswered players get 0"}</button>${state.settings.mode === "millionaire" ? `<button id="fifty" class="secondary" ${state.usedFifty || mine?.answered ? "disabled" : ""}>50:50 ${state.usedFifty ? "· used" : ""}</button><button id="walk" class="quiet" ${mine?.answered ? "disabled" : ""}>Walk away</button>` : ""}` : `<button id="next" class="primary">${state.index === state.total - 1 || state.finishReason === "wrong" ? "See results" : "Next question"} →</button>`}</div>` : `<p class="waiting">${revealed ? "Waiting for the next question…" : mine?.answered ? "Look at the TV for the reveal." : "Choose on your phone. The host controls the reveal."}</p>`}</section><aside>${
    state.settings.mode === "millionaire"
      ? `<div class="ladder"><h3>Your climb</h3><p class="fine">Fictional points. No cash prizes.</p>${[
          ...state.ladder,
        ]
          .reverse()
          .map((v, j) => {
            const i = state.ladder.length - j - 1;
            return `<div class="rung ${i === state.index ? "current" : ""} ${[4, 9].includes(i) ? "safe" : ""}"><span>${i + 1}</span><strong>${v.toLocaleString()}</strong></div>`;
          })
          .join(
            "",
          )}<p class="fine">Secured: ${state.secured.toLocaleString()} pts</p></div>`
      : people()
  }</aside></div></section>`;
}
function results() {
  const sorted = [...state.players].sort((a, b) => b.score - a.score);
  return `<section class="results-page">${status()}<div class="trophy">✦</div><h1>${state.settings.mode === "millionaire" ? (state.finishReason === "walked" ? "A smart exit." : "That’s your climb.") : "Good game.<br><em>Great company.</em>"}</h1>${state.settings.mode === "millionaire" ? `<div class="big-score">${state.won.toLocaleString()} <small>points</small></div><p>${state.finishReason === "completed" ? "You reached the top of this ladder." : state.finishReason === "walked" ? "You walked away with your winnings." : "Every question is a new chance to learn."}</p>` : `<div class="standings">${sorted.map((p, i) => `<div class="player"><span class="avatar">${sorted.findIndex((other) => other.score === p.score) + 1}</span><strong>${esc(p.name)}</strong><span class="player-score">${p.score} pts</span></div>`).join("")}</div>`}<button id="finish" class="primary">Back to game setup →</button><p class="fine">Scores are for fun. No money or real-world prizes.</p></section>`;
}
function render() {
  const focus = document.activeElement;
  const key = focus?.dataset.focus || focus?.id;
  app.innerHTML =
    session && state
      ? state.phase === "lobby"
        ? lobby()
        : state.phase === "finished"
          ? results()
          : play()
      : screen === "join"
        ? joinForm()
        : home();
  document.querySelector("#home").hidden = !session;
  document.querySelector("#home").textContent =
    session?.role === "host" ? "Leave room" : "Leave game";
  for (const button of app.querySelectorAll("button")) {
    button.dataset.focus =
      button.id ||
      button.dataset.category ||
      button.dataset.mode ||
      button.dataset.region ||
      (button.dataset.answer !== undefined
        ? "answer-" + button.dataset.answer
        : button.textContent.trim());
    if (button.dataset.mode)
      button.onclick = () => {
        mode = button.dataset.mode;
        render();
      };
    if (button.dataset.region)
      button.onclick = () => {
        region = button.dataset.region;
        render();
      };
    if (button.dataset.category)
      button.onclick = () => {
        const c = button.dataset.category;
        selected.has(c) ? selected.delete(c) : selected.add(c);
        render();
      };
    if (button.dataset.answer)
      button.onclick = () =>
        act("answer", {
          choice: Number(button.dataset.answer),
          playerId: localPlayer,
        });
  }
  const on = (id, handler) => {
    const el = document.getElementById(id);
    if (el) el.onclick = handler;
  };
  on("all-categories", () => {
    selected =
      selected.size === config.categories.length
        ? new Set()
        : new Set(config.categories);
    render();
  });
  on("join-screen", () => {
    screen = "join";
    render();
  });
  on("back", () => {
    screen = "home";
    render();
  });
  on("finish", leave);
  on("create", create);
  on("start", () => act("start"));
  on("reveal", () => act("reveal"));
  on("next", () => act("next"));
  on("fifty", () => act("fifty"));
  on("walk", () => {
    if (confirm("Walk away with your current points?")) act("walk");
  });
  const toggle = document.getElementById("party");
  if (toggle) toggle.onchange = () => (party = toggle.checked);
  const picker = document.getElementById("local-player");
  if (picker)
    picker.onchange = () => {
      localPlayer = picker.value;
      render();
    };
  const join = document.getElementById("join-form");
  if (join)
    join.onsubmit = async (e) => {
      e.preventDefault();
      await run(async () => {
        const value = await api(
          "/api/join",
          Object.fromEntries(new FormData(join)),
        );
        saveSession(value);
        setState(value.state);
      });
    };
  const add = document.getElementById("add-form");
  if (add)
    add.onsubmit = (e) => {
      e.preventDefault();
      act("add", { name: new FormData(add).get("name") });
    };
  on("copy-link", async () => {
    const link = document.getElementById("copy-link").dataset.link;
    try {
      await navigator.clipboard.writeText(link);
      notify("Joining link copied.");
    } catch {
      prompt("Copy this joining link:", link);
    }
  });
  if (key) {
    const target =
      document.getElementById(key) ||
      [...app.querySelectorAll("[data-focus]")].find(
        (el) => el.dataset.focus === key,
      );
    target?.focus();
  }
}
async function run(work) {
  if (busy) return;
  busy = true;
  pollEpoch++;
  try {
    await work();
  } catch (e) {
    notify(e.message);
  } finally {
    busy = false;
  }
}
async function create() {
  await run(async () => {
    const value = await api("/api/rooms", {
      mode,
      region,
      categories: [...selected],
      party: mode === "trivia" && party,
    });
    saveSession(value);
    setState(value.state);
  });
}
async function act(type, extra = {}) {
  await run(async () =>
    setState(
      await api(`/api/rooms/${session.code}/action`, { type, ...extra }),
    ),
  );
}
function leave() {
  pollEpoch++;
  saveSession(null);
  state = null;
  snapshot = "";
  screen = "home";
  history.replaceState(null, "", "/");
  render();
}
document.querySelector("#home").onclick = () => {
  if (
    confirm(
      "Leave this room? Other players can stay, but host controls remain in this tab only.",
    )
  )
    leave();
};
// Directional navigation also supports Android TV D-pad events in the WebView shell.
document.addEventListener("keydown", (e) => {
  if (
    !["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key) ||
    ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)
  )
    return;
  const elements = [
    ...document.querySelectorAll("button:not(:disabled),a,input,select"),
  ].filter((el) => el.getClientRects().length);
  const active = document.activeElement;
  if (!elements.includes(active)) {
    elements[0]?.focus();
    e.preventDefault();
    return;
  }
  const r = active.getBoundingClientRect(),
    cx = r.x + r.width / 2,
    cy = r.y + r.height / 2;
  const vertical = ["ArrowUp", "ArrowDown"].includes(e.key),
    sign = ["ArrowDown", "ArrowRight"].includes(e.key) ? 1 : -1;
  const ranked = elements
    .filter((el) => el !== active)
    .map((el) => {
      const b = el.getBoundingClientRect();
      const dx = b.x + b.width / 2 - cx,
        dy = b.y + b.height / 2 - cy;
      return {
        el,
        forward: (vertical ? dy : dx) * sign,
        side: Math.abs(vertical ? dx : dy),
      };
    })
    .filter((c) => c.forward > 2)
    .sort((a, b) => a.forward + a.side * 3 - (b.forward + b.side * 3));
  if (ranked[0]) {
    ranked[0].el.focus();
    ranked[0].el.scrollIntoView({ block: "nearest" });
  }
  e.preventDefault();
});
async function boot() {
  try {
    config = await api("/api/config");
    selected = new Set(config.categories);
    if (session) {
      try {
        state = await api(`/api/rooms/${session.code}`);
        snapshot = JSON.stringify(state);
      } catch (e) {
        if ([403, 404].includes(e.status)) saveSession(null);
        else throw e;
      }
    }
    if (prefill && !session) screen = "join";
    render();
    setInterval(async () => {
      if (!session || busy) return;
      const epoch = pollEpoch,
        code = session.code;
      try {
        const value = await api(`/api/rooms/${code}`);
        if (epoch !== pollEpoch || session?.code !== code) return;
        if (connectionLost) {
          connectionLost = false;
          notify("Connected again.");
        }
        setState(value);
      } catch (e) {
        if (epoch !== pollEpoch || session?.code !== code) return;
        if ([403, 404].includes(e.status)) {
          leave();
          notify(e.message);
        } else if (!connectionLost) {
          connectionLost = true;
          notify("Connection interrupted. Reconnecting…");
        }
      }
    }, 1200);
  } catch (e) {
    app.innerHTML =
      "<h1>Couldn’t reach the game.</h1><p>Check the server and reload this page.</p>";
    notify(e.message);
  }
}
boot();
