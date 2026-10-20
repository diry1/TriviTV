import http from "node:http";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { resolve, extname } from "node:path";
import { randomBytes, timingSafeEqual } from "node:crypto";
import * as rules from "./game.js";
import { bank, languageCoverage, poolCoverage } from "./questions.js";
const webRoot = fileURLToPath(new URL("../web/", import.meta.url));
const token = () => randomBytes(24).toString("hex");
const same = (a, b) =>
  typeof a === "string" &&
  /^[a-f0-9]{48}$/.test(a) &&
  a.length === b.length &&
  timingSafeEqual(Buffer.from(a), Buffer.from(b));
async function body(req) {
  let data = "";
  for await (const part of req) {
    data += part;
    if (Buffer.byteLength(data) > 8192)
      throw new rules.GameError("Request too large.", 413);
  }
  try {
    const value = JSON.parse(data || "{}");
    if (!value || typeof value !== "object" || Array.isArray(value))
      throw new Error();
    return value;
  } catch {
    throw new rules.GameError("Invalid JSON object.");
  }
}
export function createAppServer({
  partyDemo = false,
  reviewDurationMs = rules.REVIEW_DURATION_MS,
  answerDurationMs = rules.ANSWER_DURATION_MS,
  answersRevealMs = rules.ANSWERS_REVEAL_MS,
  correctRevealMs = rules.CORRECT_REVEAL_MS,
  now = Date.now,
} = {}) {
  const rooms = new Map();
  const attempts = new Map();
  function schedule(room) {
    clearTimeout(room.timer);
    room.timer = null;
    const deadline = rules.nextDeadline(room.game);
    if (deadline === null) return;
    room.timer = setTimeout(
      () => {
        room.timer = null;
        rules.advance(room.game, now());
        schedule(room);
      },
      Math.max(0, deadline - now()),
    );
    room.timer.unref();
  }
  const server = http.createServer(async (req, res) => {
    const json = (status, value) => {
      res.writeHead(status, {
        "Content-Type": "application/json",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      res.end(JSON.stringify(value));
    };
    try {
      const url = new URL(req.url, "http://localhost");
      if (
        req.method === "POST" &&
        req.headers.origin &&
        new URL(req.headers.origin).host !== req.headers.host
      )
        throw new rules.GameError(
          "Cross-origin requests are not allowed.",
          403,
        );
      if (url.pathname.startsWith("/api/")) {
        const timestamp = now();
        for (const [code, room] of rooms)
          if (timestamp - room.updated > 6 * 60 * 60 * 1000) {
            clearTimeout(room.timer);
            rooms.delete(code);
          }
        if (req.method === "POST") {
          const ip = req.socket.remoteAddress;
          const rate = attempts.get(ip) || { since: timestamp, count: 0 };
          if (timestamp - rate.since > 60000) {
            rate.since = timestamp;
            rate.count = 0;
          }
          rate.count++;
          attempts.set(ip, rate);
          if (rate.count > 180)
            throw new rules.GameError(
              "Too many requests. Try again shortly.",
              429,
            );
          for (const [key, value] of attempts)
            if (timestamp - value.since > 60000) attempts.delete(key);
        }
        if (req.method === "GET" && url.pathname === "/api/config")
          return json(200, {
            categories: rules.categories,
            partyDemo,
            freePlayers: 3,
            languages: languageCoverage,
            pools: poolCoverage,
            bank: {
              name: "OpenTriviaQA",
              count: bank.questionCount,
              revision: bank.source.revision,
              license: bank.source.license,
              categories: bank.categories,
              difficulty: "unrated",
              regions: "Europe: editorial eligibility; US: automatic-keywords",
            },
          });
        if (req.method === "GET" && url.pathname === "/api/health")
          return json(200, { status: "ok" });
        if (req.method === "POST" && url.pathname === "/api/rooms") {
          if (rooms.size >= 1000)
            throw new rules.GameError("Server is full. Try again later.", 503);
          const input = await body(req);
          if (input.party && !partyDemo)
            throw new rules.GameError(
              "Party purchases are not available in this prototype.",
              403,
            );
          const game = rules.createGame(input, {
            party: !!input.party && partyDemo,
            reviewDurationMs,
            answerDurationMs,
            answersRevealMs,
            correctRevealMs,
          });
          rules.addPlayer(
            game,
            input.name ||
              (input.language === "uk" ? "ТВ-гравець" : "TV player"),
            true,
          );
          let code;
          do {
            code = randomBytes(4).toString("hex").slice(0, 6).toUpperCase();
          } while (rooms.has(code));
          const host = token();
          const room = { game, host, members: new Map(), updated: timestamp };
          rooms.set(code, room);
          return json(201, {
            code,
            token: host,
            role: "host",
            state: rules.view(game, null, timestamp),
          });
        }
        if (req.method === "POST" && url.pathname === "/api/join") {
          const input = await body(req);
          const code = String(input.code || "").toUpperCase();
          const room = rooms.get(code);
          if (!room)
            throw new rules.GameError("Room not found. Check the code.", 404);
          let player;
          if (
            room.game.settings.mode === "millionaire" &&
            room.game.phase === "lobby" &&
            room.game.players.length === 1 &&
            room.game.players[0].local
          ) {
            const draft = { ...room.game, players: [], scores: {} };
            player = rules.addPlayer(draft, input.name);
            room.game.players = draft.players;
            room.game.scores = draft.scores;
          } else player = rules.addPlayer(room.game, input.name);
          const key = token();
          room.members.set(key, player.id);
          room.updated = timestamp;
          return json(201, {
            code,
            token: key,
            playerId: player.id,
            role: "player",
            state: rules.view(room.game, player.id, timestamp),
          });
        }
        const match = url.pathname.match(
          /^\/api\/rooms\/([A-F0-9]{6})(\/action)?$/,
        );
        if (!match) throw new rules.GameError("Not found.", 404);
        const room = rooms.get(match[1]);
        if (!room)
          throw new rules.GameError(
            "Room expired or server restarted. Create a new game.",
            404,
          );
        const key = req.headers.authorization?.replace(/^Bearer /, "");
        const host = same(key, room.host);
        const playerId = room.members.get(key);
        if (!host && !playerId)
          throw new rules.GameError("Rejoin this room to continue.", 403);
        room.updated = timestamp;
        if (rules.advance(room.game, timestamp)) schedule(room);
        if (req.method === "GET" && !match[2])
          return json(200, rules.view(room.game, playerId, timestamp));
        if (req.method !== "POST" || !match[2])
          throw new rules.GameError("Method not allowed.", 405);
        const input = await body(req);
        const actionTime = now();
        if (rules.advance(room.game, actionTime)) schedule(room);
        const game = room.game;
        if (
          ["answer", "pause", "resume", "fifty", "walk", "next"].includes(
            input.type,
          ) &&
          input.questionId !== game.questions[game.index].id
        ) {
          throw new rules.GameError(
            "That question has changed. Please try again.",
            409,
          );
        }
        if (input.type === "answer") {
          const id = host ? input.playerId : playerId;
          if (host && !game.players.some((p) => p.id === id && p.local))
            throw new rules.GameError(
              "Use that player’s phone to answer.",
              403,
            );
          rules.answer(game, id, input.choice, actionTime);
        } else if (["pause", "resume"].includes(input.type)) {
          const first = game.players[0];
          const playerOne =
            first && ((host && first.local) || playerId === first.id);
          if (!playerOne)
            throw new rules.GameError(
              "Only Player 1 can pause or resume the game.",
              403,
            );
          if (input.type === "pause") rules.pauseGame(game, actionTime);
          else rules.resumeGame(game, actionTime);
        } else {
          if (!host)
            throw new rules.GameError("Only the TV host can do that.", 403);
          switch (input.type) {
            case "start":
              rules.start(game, actionTime);
              break;
            case "next":
              if (game.settings.mode !== "millionaire")
                throw new rules.GameError("Trivia advances automatically.");
              rules.next(game, actionTime);
              break;
            case "fifty":
              rules.fifty(game);
              break;
            case "walk":
              rules.walk(game);
              break;
            case "add":
              rules.addPlayer(game, input.name, true);
              break;
            default:
              throw new rules.GameError("Unknown action.");
          }
        }
        schedule(room);
        return json(200, rules.view(game, playerId, actionTime));
      }
      if (req.method !== "GET" && req.method !== "HEAD")
        throw new rules.GameError("Method not allowed.", 405);
      const files = {
        "/": "index.html",
        "/app.js": "app.js",
        "/i18n.js": "i18n.js",
        "/styles.css": "styles.css",
        "/credits": "credits.html",
        "/licenses/opentriviaqa.txt": "../data/opentriviaqa/LICENSE.txt",
      };
      const filename = files[url.pathname];
      if (!filename) {
        res.writeHead(404);
        return res.end("Not found");
      }
      const content = await readFile(resolve(webRoot, filename));
      res.writeHead(200, {
        "Content-Type": {
          ".html": "text/html; charset=utf-8",
          ".js": "text/javascript; charset=utf-8",
          ".css": "text/css; charset=utf-8",
          ".txt": "text/plain; charset=utf-8",
        }[extname(filename)],
        "Cache-Control": "no-cache",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy":
          "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
      });
      res.end(req.method === "HEAD" ? undefined : content);
    } catch (error) {
      if (!res.headersSent)
        json(error.status || 500, {
          error: error.status ? error.message : "Unexpected server error.",
        });
      if (!error.status) console.error(error);
    }
  });
  server.on("close", () => {
    for (const room of rooms.values()) clearTimeout(room.timer);
  });
  return server;
}
if (
  process.argv[1] &&
  resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  const server = createAppServer({
    partyDemo: process.env.TRIVITV_DEMO_PARTY === "1",
  });
  server.listen(
    Number(process.env.PORT || 3000),
    process.env.HOST || "127.0.0.1",
    () =>
      console.log(
        `TriviTV listening on port ${server.address().port}. Party demo: ${process.env.TRIVITV_DEMO_PARTY === "1" ? "ON (not a purchase)" : "off"}`,
      ),
  );
}
