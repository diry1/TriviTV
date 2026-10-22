# TriviTV arcade asset pack v1

Original project assets based on the user's screenshot and the first playful Canva direction. These are reusable assets and a visual sample, not a live-game update.

## Included

- Four text-free mode illustrations: Trivia question/answer tiles, Millionaire prize steps/trophy, Imposter secret cards, Turf War 5×5 grid/flag. Animals are never mode symbols.
- Eight original whole-animal drawings: lion, bat, turtle, fox, owl, whale, rabbit and deer. Each has a navy monochrome version and a colored badge. No faces, eyes, mouths or expressions.
- Sixteen control symbols; seven button states; question panel, tile and cooldown tile.
- Five 1920×1080 backgrounds; two wordmark color variants, app mark and decorative shapes.
- One original transparent party-arena illustration in PNG and optimized WebP.
- Every SVG also exported as PNG. Tokens, CSS and an interactive HTML gallery included.

## Palette

Cream `#F6E7C8`, navy `#1B233F`, teal `#16A6A4`, coral `#F06D5F`, mango `#F5B940`, lavender `#A88BEB`.

These are the reference direction's labeled colors. SVG/CSS values are exact. The generated arena uses shaded variants and is not restricted to a six-color indexed palette. Cream is intentional on selected surfaces; there is no global sepia filter.

Player colors are independent: blue `#6599D1`, orange `#D99B63`, green `#79AE84`, purple `#A18BC5`, rose `#CD87AA`, yellow `#C5B56C`, cyan `#70B8BF`, gray `#C6C8CE`. Always show animal and player number alongside color. Do not rely on hue alone, especially for color-vision differences.

## Use

Open `index.html` directly to browse offline, or serve this folder with any static server. Select a mode and Play to inspect a visual sample. This does not create rooms or change scores. The sample question is illustrative and does not modify the production bank.

Use `modes/*.svg` at 96–256 CSS pixels; `avatars/*-badge.svg` at 32–64px and monochrome animals at 24–48px. Keep player numbers as real UI text. SVGs have explicit viewBoxes and transparent surroundings; use `object-fit:contain` and preserve aspect ratio. Use localised real text alongside illustrations.

`theme.css` is opt-in under `.arcade`; no production stylesheet was modified. It supplies responsive native button states and reduced-motion support. Use SVG panels as references or scale them with preserved aspect ratio. For variable-length answer labels, prefer the CSS button over stretching a raster panel.

Control SVGs are navy for light surfaces. On dark surfaces, use the same SVG as a CSS mask with a cream background color. Keep focus, correct/incorrect checks and cooldown hatching alongside colors. Do not recolor game correctness states to match player colors.

The SVG wordmarks use Arial Bold with a sans-serif fallback. The PNG exports freeze their appearance and need no font. Segoe UI/Arial are system font references only; no font files are distributed.

Keep the detailed arena art on a title/lobby or loading screen; use the calmer backgrounds behind questions. Backgrounds fill 16:9; use cover for other ratios. Leave all controls within the game's existing TV safe margins.

## Provenance and regeneration

The vector artwork and CSS were authored for TriviTV in code. Animal geometry derives from the original drawings made in this project, not a downloaded icon library. The arena was generated with the built-in image generation tool using the supplied screenshot solely as a style/palette reference. No third-party game characters, logos, fonts or sample libraries were included. See `PROMPT.md` for the generation brief.

Rebuild source vectors with `../build-asset-pack.py`; preview with `../build-asset-gallery.py`; raster exports with `../render-asset-pack.cjs` (requires sharp; adjust its local runtime path as needed). The generated arena master is preserved separately and is not overwritten by these scripts. `manifest.json` lists files, dimensions and hashes.

The earlier Canva draft remains separate and uncommitted pending its own preview approval. This pack does not depend on that transaction.
