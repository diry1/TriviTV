import { readFileSync } from "node:fs";

// OpenTriviaQA-only, pinned and adapted under CC BY-SA 4.0. See /credits.
// Facts are community-supplied, difficulty is unrated, and region cues are automatic.
const root = new URL("../data/opentriviaqa/", import.meta.url);
export const bank = JSON.parse(
  readFileSync(new URL("manifest.json", root), "utf8"),
);
export const questions = JSON.parse(
  readFileSync(new URL("questions.json", root), "utf8"),
);
export const categories = Object.keys(bank.categories);
