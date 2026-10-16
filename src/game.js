import { randomInt, randomUUID } from "node:crypto";
import { categories, questions } from "./questions.js";
export { categories };
export const REVIEW_DURATION_MS = 3000;
export const ANSWER_DURATION_MS = 60000;
export const ANSWERS_REVEAL_MS = 800;
export const CORRECT_REVEAL_MS = 600;
export const ladder = [
  100, 200, 300, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 125000,
  250000, 500000, 1000000,
];
export class GameError extends Error {
  constructor(message, status = 400) {
    super(message);
    this.status = status;
  }
}
const requireThat = (ok, message, status) => {
  if (!ok) throw new GameError(message, status);
};
function shuffle(items) {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = randomInt(i + 1);
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
export function selectQuestions(settings) {
  requireThat(
    ["millionaire", "trivia"].includes(settings.mode),
    "Choose a game mode.",
  );
  requireThat(
    ["Europe", "US"].includes(settings.region),
    "Choose Europe or US.",
  );
  requireThat(
    Array.isArray(settings.categories) &&
      settings.categories.length > 0 &&
      settings.categories.every((c) => categories.includes(c)),
    "Include at least one valid category.",
  );
  const pool = questions.filter(
    (q) =>
      settings.categories.includes(q.category) &&
      (q.region === "Global" || q.region === settings.region),
  );
  const count = Math.min(
    settings.mode === "millionaire" ? 15 : 10,
    pool.length,
  );
  requireThat(count > 0, "No questions match these settings.");
  // Spread Millionaire questions across available difficulties, then increase difficulty.
  let chosen;
  if (settings.mode === "millionaire") {
    const groups = [1, 2, 3].map((d) =>
      shuffle(pool.filter((q) => q.difficulty === d)),
    );
    chosen = [];
    while (chosen.length < count && groups.some((g) => g.length))
      for (const group of groups)
        if (group.length && chosen.length < count) chosen.push(group.pop());
    chosen.sort((a, b) => a.difficulty - b.difficulty);
  } else chosen = shuffle(pool).slice(0, count);
  return chosen.map((q) => {
    const order = shuffle([0, 1, 2, 3]);
    return {
      ...q,
      choices: order.map((i) => q.choices[i]),
      correct: order.indexOf(q.correct),
    };
  });
}
export function createGame(
  settings,
  {
    party = false,
    reviewDurationMs = REVIEW_DURATION_MS,
    answerDurationMs = ANSWER_DURATION_MS,
    answersRevealMs = ANSWERS_REVEAL_MS,
    correctRevealMs = CORRECT_REVEAL_MS,
  } = {},
) {
  const selected = selectQuestions(settings);
  return {
    settings: {
      mode: settings.mode,
      region: settings.region,
      categories: [...new Set(settings.categories)],
    },
    party: !!party,
    phase: "lobby",
    players: [],
    questions: selected,
    index: 0,
    answers: {},
    scores: {},
    eliminated: [],
    usedFifty: false,
    won: 0,
    secured: 0,
    finishReason: null,
    reviewDurationMs,
    answerDurationMs,
    answersRevealMs,
    correctRevealMs,
    review: null,
    questionEndsAt: null,
    stageEndsAt: null,
    autoPicked: [],
  };
}
export function addPlayer(game, name, local = false) {
  requireThat(game.phase === "lobby", "This game has already started.", 409);
  requireThat(
    typeof name === "string" &&
      name.trim().length > 0 &&
      name.trim().length <= 24,
    "Use a name from 1 to 24 characters.",
  );
  const max =
    game.settings.mode === "millionaire" ? 1 : game.party ? Infinity : 3;
  requireThat(
    game.players.length < max,
    game.settings.mode === "millionaire"
      ? "Millionaire is for one player."
      : "Free Trivia supports 3 players. Party Mode unlocks larger groups.",
    409,
  );
  requireThat(
    !game.players.some(
      (p) => p.name.toLowerCase() === name.trim().toLowerCase(),
    ),
    "That name is already in use.",
    409,
  );
  const player = { id: randomUUID(), name: name.trim(), local };
  game.players.push(player);
  game.scores[player.id] = 0;
  return player;
}
export function start(game, now = Date.now()) {
  requireThat(game.phase === "lobby", "Game already started.", 409);
  requireThat(game.players.length > 0, "Add at least one player.");
  beginQuestion(game, now);
}
function beginQuestion(game, now) {
  game.phase = "question";
  game.questionEndsAt =
    game.settings.mode === "trivia" ? now + game.answerDurationMs : null;
  game.stageEndsAt = null;
}
export function answer(game, playerId, choice, now = Date.now()) {
  requireThat(game.phase === "question", "Answers are closed.", 409);
  requireThat(
    game.questionEndsAt === null || now < game.questionEndsAt,
    "Time is up. Unanswered picks are assigned randomly.",
    409,
  );
  requireThat(
    game.players.some((p) => p.id === playerId),
    "Unknown player.",
    403,
  );
  requireThat(
    Number.isInteger(choice) &&
      choice >= 0 &&
      choice < 4 &&
      !game.eliminated.includes(choice),
    "Choose an available answer.",
  );
  requireThat(
    !(playerId in game.answers),
    "Your answer is already locked.",
    409,
  );
  game.answers[playerId] = choice;
  if (game.players.every((p) => p.id in game.answers)) reveal(game, now);
}
export function reveal(game, now = Date.now()) {
  requireThat(game.phase === "question", "No question to reveal.", 409);
  requireThat(
    game.players.every((p) => p.id in game.answers),
    "Wait for every player to answer.",
    409,
  );
  game.phase = "answers";
  game.questionEndsAt = null;
  game.stageEndsAt = now + game.answersRevealMs;
}
function revealCorrect(game, now) {
  const correct = game.questions[game.index].correct;
  for (const p of game.players)
    if (game.answers[p.id] === correct) game.scores[p.id] += 100;
  if (game.settings.mode === "millionaire") {
    const right = game.answers[game.players[0].id] === correct;
    if (right) {
      game.won = ladder[game.index];
      if ([4, 9].includes(game.index)) game.secured = game.won;
    } else {
      game.won = game.secured;
      game.finishReason = "wrong";
    }
  }
  game.phase = "correct";
  game.stageEndsAt = now + game.correctRevealMs;
}
function beginReview(game, now) {
  game.phase = "reveal";
  game.stageEndsAt = null;
  game.review = {
    paused: false,
    remainingMs: game.reviewDurationMs,
    endsAt: now + game.reviewDurationMs,
  };
}
export function next(game, now = Date.now()) {
  requireThat(game.phase === "reveal", "Reveal the answer first.", 409);
  requireThat(
    !game.review.paused && now >= game.review.endsAt,
    "The answer review is still running.",
    409,
  );
  game.review = null;
  if (
    game.finishReason === "wrong" ||
    game.index === game.questions.length - 1
  ) {
    game.phase = "finished";
    game.finishReason ??= "completed";
    return;
  }
  game.index++;
  game.answers = {};
  game.eliminated = [];
  game.autoPicked = [];
  beginQuestion(game, now);
}
// Every phase has a server-owned deadline. Reveals never leak the answer through scores.
export function nextDeadline(game) {
  if (game.phase === "question") return game.questionEndsAt;
  if (["answers", "correct"].includes(game.phase)) return game.stageEndsAt;
  if (game.phase === "reveal" && !game.review.paused) return game.review.endsAt;
  return null;
}
export function advance(game, now = Date.now()) {
  const deadline = nextDeadline(game);
  if (deadline === null || now < deadline) return false;
  if (game.phase === "question") {
    for (const player of game.players)
      if (!(player.id in game.answers)) {
        game.answers[player.id] = randomInt(4);
        game.autoPicked.push(player.id);
      }
    reveal(game, now);
  } else if (game.phase === "answers") revealCorrect(game, now);
  else if (game.phase === "correct") beginReview(game, now);
  else next(game, now);
  return true;
}
export function pauseReview(game, now = Date.now()) {
  requireThat(
    game.settings.mode === "millionaire",
    "Pause is available in Millionaire only.",
    409,
  );
  requireThat(
    game.phase === "reveal" && !game.review.paused && now < game.review.endsAt,
    "There is no running review to pause.",
    409,
  );
  game.review.remainingMs = game.review.endsAt - now;
  game.review.endsAt = null;
  game.review.paused = true;
}
export function resumeReview(game, now = Date.now()) {
  requireThat(
    game.settings.mode === "millionaire",
    "Pause is available in Millionaire only.",
    409,
  );
  requireThat(
    game.phase === "reveal" && game.review.paused,
    "The review is not paused.",
    409,
  );
  game.review.endsAt = now + game.review.remainingMs;
  game.review.paused = false;
}
export function fifty(game) {
  requireThat(
    game.settings.mode === "millionaire" &&
      game.phase === "question" &&
      !game.usedFifty,
    "50:50 is unavailable.",
    409,
  );
  requireThat(
    Object.keys(game.answers).length === 0,
    "Use 50:50 before locking an answer.",
    409,
  );
  game.eliminated = shuffle(
    [0, 1, 2, 3].filter((i) => i !== game.questions[game.index].correct),
  ).slice(0, 2);
  game.usedFifty = true;
}
export function walk(game) {
  requireThat(
    game.settings.mode === "millionaire" && game.phase === "question",
    "You can walk away before answering.",
    409,
  );
  requireThat(
    Object.keys(game.answers).length === 0,
    "Your answer is already locked.",
    409,
  );
  game.phase = "finished";
  game.finishReason = "walked";
}
export function view(game, viewerId = null, now = Date.now()) {
  const q = game.questions[game.index];
  const show = ["correct", "reveal", "finished"].includes(game.phase);
  const showPicks = show || game.phase === "answers";
  return {
    settings: game.settings,
    party: game.party,
    phase: game.phase,
    serverNow: now,
    questionEndsAt: game.questionEndsAt,
    answerDurationMs: game.answerDurationMs,
    stageEndsAt: game.stageEndsAt,
    review: game.review
      ? { ...game.review, durationMs: game.reviewDurationMs }
      : null,
    index: game.index,
    total: game.questions.length,
    players: game.players.map((p) => ({
      ...p,
      score: game.scores[p.id],
      answered: p.id in game.answers,
      ...(showPicks
        ? {
            answer: game.answers[p.id] ?? null,
            autoPicked: game.autoPicked.includes(p.id),
          }
        : {}),
    })),
    question:
      game.phase === "lobby"
        ? null
        : {
            id: q.id,
            text: q.text,
            category: q.category,
            choices: q.choices,
            eliminated: game.eliminated,
            ...(show ? { correct: q.correct } : {}),
          },
    myAnswer: game.answers[viewerId] ?? null,
    usedFifty: game.usedFifty,
    won: game.won,
    secured: game.secured,
    finishReason: game.finishReason,
    ladder: ladder.slice(0, game.questions.length),
  };
}
