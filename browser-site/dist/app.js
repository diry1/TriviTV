import { localApi, clearProgress } from './local-state.js';
import { translate, localize } from "/i18n.js";
let language = "uk";
try {
  language = "uk";
} catch {}
const requestedLanguage = new URLSearchParams(location.search).get("language");
language = "uk";
const t = (text) => translate(text, language);
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
  categoryPanelOpen = false,
  party = false,
  localPlayer = null,
  busy = false,
  snapshot = "",
  connectionLost = false,
  pollEpoch = 0,
  polling = false,
  clockOffset = 0,
  renderedPhase = null,
  renderedTurn = null,
  renderedPaused = false;
try {
  session = JSON.parse(localStorage.getItem("trivitv-browser-session") || "null");
} catch {}
const params = new URLSearchParams(location.search);
const prefill = params.get("join");
function notify(message) {
  const n = document.querySelector("#notice");
  n.textContent = t(message);
  n.hidden = false;
  clearTimeout(notify.timer);
  notify.timer = setTimeout(() => (n.hidden = true), 6000);
}
async function api(path,body){ return localApi(path,body); }
function saveSession(value) {
  session = value;
  try {
    localStorage.setItem("trivitv-browser-session", JSON.stringify(value));
  } catch {
    notify("Session storage is unavailable. Keep this tab open.");
  }
}
function setState(value) {
  state = value;
  language = state.settings.language ?? "en";
  const next = JSON.stringify(value);
  if (next !== snapshot) {
    snapshot = next;
    render();
  }
}
function status() {
  return `<div class="eyebrow">${state.settings.mode === "millionaire" ? "SOLO · MILLIONAIRE" : "ВІКТОРИНА · СОЛО"} <span class="dot">•</span> ${esc(state.settings.region)} <span class="dot">•</span> ${state.party ? "PARTY DEMO" : "ЛОКАЛЬНЕ ТЕСТУВАННЯ"}</div>`;
}
function home() {
  const coverage = config.pools[language][region];
  const available = [...selected].reduce((sum, category) => sum + (coverage.categories[category] || 0), 0);
  return `<section class="intro"><div class="eyebrow">THE SOFA IS YOUR GAME SHOW</div><h1>A little friendly<br><em>competition.</em></h1><p>One screen. Your favourite people. Something<br class="desktop"> everyone thinks they know the answer to.</p></section><div class="home-grid"><section class="setup"><div class="section-heading"><h2>Pick your game</h2><span>01 / THE FORMAT</span></div><div class="modes"><button class="mode ${mode === "trivia" ? "active" : ""}" data-mode="trivia"><span class="mode-icon">✳</span><span><strong>Trivia</strong><small>Four choices. Plenty of opinions.</small></span><span class="tag">SOLO</span></button><button class="mode ${mode === "millionaire" ? "active" : ""}" data-mode="millionaire"><span class="mode-icon amber">◇</span><span><strong>Millionaire</strong><small>One player. One climb to the top.</small></span><span class="tag">SOLO</span></button></div><div class="section-heading"><h2>Make it your kind of quiz</h2><span>02 / THE MIX</span></div><div class="setting-row"><div><h3>Your region</h3><p>Prefer familiar references.</p></div><div class="segmented" role="group" aria-label="Question region">${["Europe"].map((r) => `<button data-region="${r}" class="${region === r ? "selected" : ""}" aria-pressed="${region === r}">${r === "Europe" ? "Europe" : "United States"}</button>`).join("")}</div></div><details id="category-panel" class="category-panel" ${categoryPanelOpen ? "open" : ""}><summary id="category-toggle"><strong>Categories</strong><span>${selected.size === config.categories.length ? `All ${config.categories.length} included` : `${selected.size} included`}</span></summary><div class="category-head"><h3>Include categories (${config.categories.length})</h3><button id="all-categories" class="text-button">${selected.size === config.categories.length ? "Clear all" : "Select all"}</button></div><div class="categories">${config.categories.map((c, i) => `<button class="chip ${selected.has(c) ? "selected" : ""}" data-category="${c}" aria-pressed="${selected.has(c)}"><span>${["◎", "♫", "⌛", "⚛", "⚑", "✎"][i % 6]}</span>${c}<b>${selected.has(c) ? "✓" : "+"}</b></button>`).join("")}</div></details>${language === "uk" ? `<p class="fine translation-preview">Ukrainian preview: translated questions only. Draft translations need review.<br>916 запитань · Українська · Європа</p>` : ""}<p class="fine">${region === "Europe" ? "Questions filtered for a European audience; difficulty is unrated." : "Source categories only. Unclassified questions are shared across regions; difficulty is unrated."}</p><p id="pool-availability" class="fine">${available} ${available === 1 ? "question" : "questions"} available with these settings.</p><button class="primary start-button" id="create" ${selected.size && available ? "" : "disabled"}>Set up ${mode === "millionaire" ? "my climb" : "the game"} <span>→</span></button><p class="fine">${mode === "millionaire" ? "Up to 15 questions · 50:50 · Walk away · Fictional points" : "Up to 10 questions · 60 seconds · Automatic reveal"}</p></section></div>`;
}
function people() {
  return `<div class="players">${state.players.map((p) => `<div class="player"><span class="avatar" data-no-translate>${esc(p.name.slice(0, 1).toUpperCase())}</span><strong data-no-translate>${esc(p.name)}</strong><span class="muted">Локально</span><span class="player-score">${state.phase === "question" ? (p.answered ? "Locked ✓" : "Thinking…") : state.phase === "lobby" ? "Ready" : `${p.score} pts`}</span></div>`).join("")}</div>`;
}
function lobby() { return `<section class="room-page">${status()}<h1>Готові грати?</h1><p>${state.total} запитань · Українська · Європа</p><section class="room-info"><h3>Ваші категорії</h3><p>${state.settings.categories.map(c=>esc(t(c))).join(' · ')}</p></section><button id="start" class="primary wide">Почати гру →</button></section>`; }
function canControlPause() {
  const first = state?.players[0];
  return (
    state.settings.mode === "trivia" &&
    !!first &&
    ((session.role === "host" && first.local) || session.playerId === first.id)
  );
}
function pausedNow() {
  return state.phase === "question"
    ? state.questionPaused
    : state.review?.paused;
}
function pauseButton() {
  return canControlPause()
    ? `<button id="pause-review" class="pause-secondary"><svg class="pause-icon" viewBox="0 0 12 12" aria-hidden="true"><path d="${pausedNow() ? "M3 1L11 6L3 11Z" : "M2 1H5V11H2ZM7 1H10V11H7Z"}"/></svg> ${pausedNow() ? "Resume" : "Pause"}</button>`
    : "";
}
function reviewControls() {
  if (state.settings.mode === "millionaire") {
    const last =
      state.finishReason === "wrong" || state.index === state.total - 1;
    return session.role === "host"
      ? `<div class="review-timing"><button id="next" class="primary">${last ? "View results" : "Next question"}</button></div>`
      : `<p class="fine">Waiting for the TV host to continue.</p>`;
  }
  return `<section class="review-timing" aria-label="Answer review"><div class="review-heading">
    <strong id="review-countdown" role="status"></strong><div class="pause-countdown">
    <div class="countdown-ring" role="img" aria-label="Time remaining before the next round"><svg viewBox="0 0 48 48" aria-hidden="true"><circle class="ring-track" cx="24" cy="24" r="20"/><circle id="review-ring" class="ring-fill" cx="24" cy="24" r="20" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"/></svg></div>
    ${state.settings.mode === "trivia" ? pauseButton() : ""}</div></div>
    </section>`;
}
function updateCountdown() {
  if (state?.phase === "question" && state.settings.mode === "trivia") {
    const remaining = state.questionPaused
      ? state.questionRemainingMs
      : Math.max(0, state.questionEndsAt - (Date.now() + clockOffset));
    const seconds = Math.ceil(remaining / 1000);
    const clock = document.getElementById("answer-countdown");
    if (clock)
      clock.textContent = state.questionPaused
        ? t("Paused")
        : `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
    const progress = document.getElementById("answer-progress");
    if (progress) progress.value = remaining;
  }
  if (state?.phase !== "reveal" || !state.review) return;
  const remaining = state.review.paused
    ? state.review.remainingMs
    : Math.max(0, state.review.endsAt - (Date.now() + clockOffset));
  const last =
    state.finishReason === "wrong" || state.index === state.total - 1;
  const text = document.getElementById("review-countdown");
  const message = state.review.paused
    ? "Paused · answer stays on screen"
    : remaining > 0
      ? `${last ? "Results" : "Next question"}`
      : "Moving on…";
  if (text && text.textContent !== t(message)) text.textContent = t(message);
  document
    .getElementById("review-ring")
    ?.setAttribute(
      "stroke-dashoffset",
      String(100 * (1 - remaining / state.review.durationMs)),
    );
}
function play() {
  const isHost = session.role === "host",
    q = state.question,
    answering = state.phase === "question",
    revealed = ["correct", "reveal"].includes(state.phase),
    showPicks = ["answers", "correct", "reveal"].includes(state.phase);
  const local = state.players.filter((p) => p.local);
  const pending = local.find((p) => !p.answered);
  if (
    !local.some((p) => p.id === localPlayer) ||
    (answering && local.find((p) => p.id === localPlayer)?.answered && pending)
  )
    localPlayer = pending?.id || local[0]?.id;
  const mine = isHost
    ? state.players.find((p) => p.id === localPlayer)
    : state.players.find((p) => p.id === session.playerId);
  const canAnswer =
    answering && !state.questionPaused && mine && !mine.answered;
  return `<section class="play-page">${status()}
    <div class="game-meta"><span>QUESTION ${state.index + 1} / ${state.total}</span><span class="tag">${esc(q.category)}</span>${state.settings.mode === "millionaire" ? `<span class="prize">FOR ${state.ladder[state.index].toLocaleString()} POINTS</span>` : `<span>${state.players.length} PLAYERS</span>`}</div>
    <div class="play-grid"><section><h1 class="question" data-no-translate>${esc(q.text)}</h1>
    ${isHost && local.length > 1 && answering && pending ? `<p class="remote-turn">Remote turn: <strong data-no-translate>${esc(pending.name)}</strong><span>One press locks your answer and passes the remote.</span></p>` : ""}
    ${mine && answering ? `<p class="answer-status">${mine.answered ? `${esc(mine.name)}, your answer is locked. Waiting for the other players…` : `${esc(mine.name)}, what’s your answer?`}</p>` : ""}
    ${answering && state.settings.mode === "trivia" ? `<div class="answer-clock"><span>Time to answer</span><div class="answer-clock-controls">${pauseButton()}<strong id="answer-countdown" role="timer" aria-live="off">1:00</strong></div><progress id="answer-progress" max="${state.answerDurationMs}" value="${state.answerDurationMs}" aria-label="Answer time remaining"></progress><small id="pause-hint">${state.questionPaused ? "Player 1 paused the game. All answers are frozen until resumed." : "Any unanswered pick is chosen at random when time runs out."}</small></div>` : ""}
    <div class="answers ${state.phase === "answers" ? "revealing-picks" : state.phase === "correct" ? "revealing-correct" : ""}" data-stage="${state.phase}">${q.choices
      .map((choice, i) => {
        const voters = showPicks
          ? state.players.filter((p) => p.answer === i)
          : [];
        return `<button data-answer="${i}" class="answer ${voters.length ? "picked" : ""} ${revealed && i === q.correct ? "correct" : ""} ${revealed && mine?.answer === i && i !== q.correct ? "incorrect" : ""} ${answering && state.myAnswer === i ? "locked" : ""}" ${!canAnswer || q.eliminated.includes(i) ? "disabled" : ""}><span>${"ABCD"[i]}</span><div class="answer-content"><strong data-no-translate>${q.eliminated.includes(i) ? "—" : esc(choice)}</strong>${voters.length ? `<small class="answer-voters">${voters.map((p) => `<i><span data-no-translate>${esc(p.name)}</span>${p.autoPicked ? ` · ${t("random")}` : ""}</i>`).join("")}</small>` : ""}</div>${revealed && i === q.correct ? "<b>✓</b>" : ""}</button>`;
      })
      .join("")}</div>
    ${state.phase === "answers" ? '<p class="stage-message" role="status">Revealing everyone’s picks…</p>' : revealed ? `<p class="result-note" role="status">${state.settings.mode === "millionaire" && state.finishReason === "wrong" ? `The climb ends here. You keep ${state.won.toLocaleString()} points.` : `<span>${t("Correct answer:")}</span> <span data-no-translate>${esc(q.choices[q.correct])}</span>`}</p>${state.phase === "reveal" ? reviewControls() : '<p class="stage-message">Revealing the correct answer…</p>'}` : `<p class="fine">${state.players.filter((p) => p.answered).length} of ${state.players.length} answers locked. ${state.settings.mode === "trivia" ? "Reveals when everyone answers or the minute is up." : "Reveals automatically after your pick."}</p>`}
    ${isHost && answering && state.settings.mode === "millionaire" ? `<div class="host-actions"><button id="fifty" class="secondary" ${state.usedFifty || mine?.answered ? "disabled" : ""}>50:50 ${state.usedFifty ? "· used" : ""}</button><button id="walk" class="quiet" ${mine?.answered ? "disabled" : ""}>Walk away</button></div>` : ""}
    ${!isHost && answering ? `<p class="waiting">${mine?.answered ? "Look at the TV for the reveal." : "Choose on your phone. The answer reveals automatically."}</p>` : ""}</section>
    <aside>${
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
  return `<section class="results-page">${status()}<div class="trophy">✦</div><h1>${state.settings.mode === "millionaire" ? (state.finishReason === "walked" ? "A smart exit." : "That’s your climb.") : "Good game.<br><em>Great company.</em>"}</h1>${state.settings.mode === "millionaire" ? `<div class="big-score">${state.won.toLocaleString()} <small>points</small></div><p>${state.finishReason === "completed" ? "You reached the top of this ladder." : state.finishReason === "walked" ? "You walked away with your winnings." : "Every question is a new chance to learn."}</p>` : `<div class="standings">${sorted.map((p, i) => `<div class="player"><span class="avatar" data-no-translate>${sorted.findIndex((other) => other.score === p.score) + 1}</span><strong data-no-translate>${esc(p.name)}</strong><span class="player-score">${p.score} pts</span></div>`).join("")}</div>`}<button id="finish" class="primary">Back to game setup →</button><p class="fine">Scores are for fun. No money or real-world prizes.</p></section>`;
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
        ? home()
        : home();
  localize(app, language);
  try { localStorage.setItem("trivitv-browser-settings",JSON.stringify({mode,categories:[...selected]})); } catch {}
  document.documentElement.lang = language;
  document.title =
    language === "uk"
      ? "TriviTV · Дружнє суперництво"
      : "TriviTV · A little friendly competition";
  document.querySelector(".header-note").textContent = t(
    "GOOD COMPANY. GREAT QUESTIONS.",
  );
  document.querySelector("footer span").textContent = t(
    "MADE FOR YOUR NEXT NIGHT IN",
  );
  document.querySelector("footer a").textContent = t(
    "Questions: OpenTriviaQA · CC BY-SA 4.0",
  );
  document.querySelector(".logo").setAttribute("aria-label", t("TriviTV home"));
  document.querySelector("#language-label").textContent = t("Language");
  const languagePicker = document.querySelector("#language");
  languagePicker.value = language;
  languagePicker.disabled = !!session;
  languagePicker.setAttribute("aria-label", t("Language"));
  document.querySelector("#home").hidden = !session;
  document.querySelector("#home").textContent = t(
    "Завершити гру",
  );
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
  on("next", () => act("next"));
  on("pause-review", () => act(pausedNow() ? "resume" : "pause"));
  on("fifty", () => act("fifty"));
  on("walk", () => {
    if (confirm(t("Walk away with your current points?"))) act("walk");
  });
  const panel = document.getElementById("category-panel");
  if (panel)
    panel.ontoggle = () => {
      categoryPanelOpen = panel.open;
    };
  const toggle = document.getElementById("party");
  if (toggle) toggle.onchange = () => (party = toggle.checked);
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
      prompt(t("Copy this joining link:"), link);
    }
  });
  if (key) {
    const target =
      document.getElementById(key) ||
      [...app.querySelectorAll("[data-focus]")].find(
        (el) => el.dataset.focus === key,
      );
    if (target && !target.disabled) target.focus();
  }
  const turn =
    session && state ? `${session.code}:${state.index}:${localPlayer}` : null;
  if (
    state?.phase === "question" &&
    !state.questionPaused &&
    (renderedPhase !== "question" || turn !== renderedTurn || renderedPaused)
  ) {
    app.querySelector(".answer:not(:disabled)")?.focus();
  } else if (
    state?.phase === "reveal" &&
    renderedPhase !== "reveal" &&
    state.settings.mode === "millionaire"
  ) {
    document.getElementById("next")?.focus();
  } else if (state?.phase === "finished" && renderedPhase !== "finished") {
    document.getElementById("finish")?.focus();
  } else if (state?.phase === "lobby" && renderedPhase !== "lobby") {
    document.getElementById("start")?.focus();
  }
  renderedPaused = state?.questionPaused || false;
  renderedPhase = state?.phase || null;
  renderedTurn = turn;
  updateCountdown();
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
      language,
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
      await api(`/api/rooms/${session.code}/action`, {
        type,
        questionId: state.question?.id,
        ...extra,
      }),
    ),
  );
}
function leave() {
  pollEpoch++;
  saveSession(null);
  clearProgress();
  state = null;
  snapshot = "";
  screen = "home";
  history.replaceState(null, "", "/");
  render();
}
document.querySelector("#language").onchange = (event) => {
  if (session) return;
  language = event.target.value;
  if (language === "uk") region = "Europe";
  try {
    localStorage.setItem("trivitv-language", language);
  } catch {}
  render();
};
document.querySelector("#home").onclick = () => {
  if (
    confirm(
      t(
        "Завершити цю гру та повернутися до налаштувань?",
      ),
    )
  )
    leave();
};
// Ignore held buttons across transitions; a held OK must not answer for the next player.
document.addEventListener("keydown", (e) => {
  if (["Enter", " ", "MediaPlayPause"].includes(e.key) && e.repeat) {
    e.preventDefault();
    return;
  }
  if (
    e.key === "MediaPlayPause" &&
    ["question", "reveal"].includes(state?.phase) &&
    canControlPause()
  ) {
    e.preventDefault();
    act(pausedNow() ? "resume" : "pause");
  }
});
// Directional navigation also supports Android TV D-pad events in the WebView shell.
document.addEventListener("keydown", (e) => {
  if (
    !["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(e.key) ||
    ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)
  )
    return;
  const elements = [
    ...document.querySelectorAll(
      "button:not(:disabled),a,input,select,summary",
    ),
  ].filter((el) => el.getClientRects().length);
  const active = document.activeElement;
  if (!elements.includes(active)) {
    const target =
      state?.phase === "reveal"
        ? document.getElementById("pause-review") || elements[0]
        : elements[0];
    target?.focus();
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
    try { const saved=JSON.parse(localStorage.getItem('trivitv-browser-settings')); if(saved){mode=['trivia','millionaire'].includes(saved.mode)?saved.mode:'trivia'; selected=new Set(saved.categories.filter(c=>config.categories.includes(c)));} } catch {}
    if (session) {
      try {
        state = await api(`/api/rooms/${session.code}`);
        language = state.settings.language ?? "en";
        snapshot = JSON.stringify(state);
      } catch (e) {
        if ([403, 404].includes(e.status)) saveSession(null);
        else throw e;
      }
    }
    if (prefill && !session) screen = "join";
    render();
    setInterval(async () => {
      if (!session || busy || polling) return;
      polling = true;
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
      } finally {
        polling = false;
      }
    }, 250);
    setInterval(updateCountdown, 100);
  } catch (e) {
    app.innerHTML =
      "<h1>Couldn’t reach the game.</h1><p>Check the server and reload this page.</p>";
    localize(app, language);
    notify(e.message);
  }
}
boot();
