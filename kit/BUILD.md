# <TITLE> — scene builder brief

<!-- PER FILM: fill every <...> below, then hand this file to each scene builder. -->

You build HyperFrames scene sub-compositions for a <LENGTH>s, <BPM> bpm lyric video about <STORY: one or two
sentences>. Each scene should land its line's reference visually. Bar: the reference film (dense, inventive,
every line its own visual metaphor, ONE locked art direction, sung text filling letter-by-letter in sync).

Project: `<PROJECT_DIR>` (call it P). HyperFrames project: `P/video/`.

## Read first
- `P/design.md` — art direction (colors, fonts, HUD, motion). Obey it.
- `P/video/compositions/<REFERENCE_SCENE>.html` — the WORKING reference scene you wrote first. Copy its structure exactly.
- `P/scenes.md` — the per-line visual plan (plus any research notes on what each reference means).
- `P/video/assets/lyric-engine.js` — the lyric API (`LF.mount / LF.onPath / LF.animate / LF.beats / LF.hits`).
- `P/video/scenes.json` — every scene's id, song-time `start`, `duration`, lyric `lines`, concept.
- Word/letter timing: `python3 -c "import json;d=json.load(open('P/chars.json'));[print(w['w'],w['t0'],w['t1'],'HELD' if w['held'] else '') for w in d[N]['words']]"` (N = line index).
- Wordless vocal hit times for interlude scenes: `P/vocal_hits.json` = `window.VOCAL_HITS` (if the film has any).

## Globals available in every scene (loaded by index.html)
- `gsap`, `LF`, `window.LYRICS`, `window.BEATS`, `window.DOWNBEATS`, `window.SCENES[id]` (scene song-time start), `window.VOCAL_HITS`.
- CSS vars: `--bg <HEX>`, `--bone <HEX>`, `--bone-50`, `--bone-20`, `--ghost`, `--accent <HEX>` (the ONLY accent), `--accent-glow`.
  Never use another hue. For GSAP color tweens use the literal hex values.
- Font CLASSES (never write `font-family` yourself — lint needs @font-face, which lives in index.html):
  `.f-display`, `.f-bold`, `.f-mono`, `.f-serif` (faces chosen in design.md / assemble.py).
- A persistent HUD (<describe it>) is drawn ABOVE every scene by index.html. Keep key content out of the outer
  ~110px top/bottom bands.

## IP rule (when the topic involves someone else's brand)
Original stylized art ONLY: silhouettes, generic shapes, UI pastiche. No official artwork, logos, trademark
shapes or recognizable character designs. Brand and character names may appear as TEXT when they're in the lyrics.

## Hard rules (HyperFrames contract — breaking these breaks the render)
1. File shape = the reference scene: `<template>` containing `<style>`, `<div id="root" data-composition-id="<ID>" data-width="1920" data-height="1080">`, `<script>`. Everything inside `<template>`. Style the root as `#root`.
2. Prefix EVERY id and class you create with the scene prefix (e.g. `s07-`), except `#root`.
3. Exactly one `gsap.timeline({ paused: true })`, registered as `window.__timelines["<ID>"] = tl` AFTER the build finishes (inside `document.fonts.ready.then(...)` when you measure text, as the reference scene does).
4. Deterministic: no `Math.random` (use the seeded `rnd()` from the example scene), no Date, no network, no `repeat: -1` (finite repeats only), no CSS animations/transitions.
5. Use `tl.fromTo(...)` with explicit start values. A second tween on the same property of the same element needs `immediateRender: false`.
6. Never set a CSS `transform` on an element GSAP also moves — set the start state in `fromTo` (use `xPercent/yPercent` to center).
7. Timeline time is LOCAL to the scene (0 = scene start). Convert song time with `t - window.SCENES[ID]`. Scene length = its `duration` in scenes.json; nothing after that is visible.
8. No `<br>` in text. Images: inline SVG only (no external files). No `<video>`/`<audio>`.

## Lyric rules (the whole point)
- Every lyric line of your scene is rendered with `LF.mount` + `LF.animate` — never hand-type timings.
- The full line is visible as ghost text before it is sung (or flies/falls/draws in as ghost BEFORE its first letter's t0).
- Lyrics are big and readable: typically 84–150px `.f-display`; quieter lines may use `.f-serif` large. Wrap long lines with a width-limited container (`white-space: normal`), as the reference scene does.
- Make the text belong to the scene: ride a path (`LF.onPath`), sit inside a UI element, get engraved, freeze, sink, etc.
- Held notes (words with HELD) must FEEL held: the engine already slows the fill and swells letters; add a scene-specific
  response during the hold (drip, frost spreading, bar growing, ring expanding, letters spacing out...).
- Never move/scale a letter in a way that hides its fill while it is being sung.

## Music sync
- <BPM> bpm, <60/BPM> s/beat. Use `LF.beats(T, DUR)` / `LF.beats(T, DUR, window.DOWNBEATS)` to pulse, flash, cut, or step things on the beat.
- Interlude scenes (no lyrics) sync visual events to `LF.hits("<name>", T)`.
- Motion: snappy (power2/power3/expo eases, 0.15–0.5s), punch on downbeats. Bridge scenes (s21–s23) drift slowly and warmly.

## Variety (each scene owns a distinct technique — do not converge on "text over dark grid")
Mix: SVG line art drawn on with stroke-dashoffset · CSS 3D perspective (rotateX/rotateY, translateZ, preserve-3d) ·
full-bleed kinetic typography · UI recreations (terminal, editor, pager LCD, progress bar, dashboards) ·
data-viz (graphs, counters, trees) · INVERTED bone-paper scenes (bone bg, dark ink, accent-colored marks) where they fit ·
full-frame yellow flashes on big hits · particle-like grids of small elements (seeded).
Small mono HUD-style labels/annotations inside your scenes add density (like the reference): e.g. `queue position: —`, `qty 28`, `23.42 g`.

## Gotchas found in film 1 (each one broke a scene)
- The engine wraps `document.fonts.ready` so layout exists inside it — do ALL measuring there. For text
  widths prefer `LF.measure(el)` (canvas; honors text-transform). Never divide by a width that could be 0.
- Never give an element the same id as the scene (the host slot in index.html already uses it).
  Rename only inner elements — never change `#root`'s `data-composition-id`.
- Word spaces are `.lf-sp` spans; if you hide words, also remove/handle those spans.
- SVG draw-on: `pathLength="1000"` with dash values in thousands (not `pathLength="1"`).
- Text you redraw from code (counters, typed strings): use a setter proxy object tweened by GSAP
  (see the "But nothing happened." typer in s03), not `onUpdate`.
- `document.fonts.load(...)` is already kicked off in index.html; just use `document.fonts.ready`.
- (film 2) An element you later hide with `autoAlpha` needs an explicit visible start (`autoAlpha: 1` in the
  fromTo "from"), or it can blank for the whole scene. Things that must START hidden: hide them in CSS
  (`tl.set` at 0 does not render frame 0). Lint rejects tweening `letterSpacing` — spread letters with
  per-letter `x` instead.
- (film 2) Snapshots: always pass `--timeout 15000` (the 5s default fails silently: scenes render in their
  pre-script state). A snapshot within one frame of a scene's start can resolve to the previous scene.
- Read scene start from `window.SCENES[ID]`; the cut times are locked once building starts.
- (film 3) Never tween CSS `visibility` (it hid a whole sub-scene in render) — fade with opacity only.
  Never target `#root` from a scene script (every scene's root is #root; it hits ALL scenes) —
  assemble.py now refuses both #root-in-script and inner ids equal to the scene id.
- (film 3) The FIRST tween that hides an element with autoAlpha must use the default immediateRender
  (later tweens on the same property use immediateRender:false). Hit effects whose "from" state is
  visible (rings, shockwaves, speed lines) need immediateRender:false or they show from frame 0.
- (film 3) svgOrigin/transformOrigin on SVG <g> can land far off-centre. To scale/rotate an SVG
  group, put that SVG in its own absolutely-positioned HTML div and animate the div instead.

## Verify in an ISOLATED copy (full-project snapshots hang when several builders run at once)
```bash
export PATH=$(ls -d ~/.nvm/versions/node/v22*/bin | tail -1):$PATH
W=/tmp/ag-<yourname>; rm -rf $W; mkdir -p $W
cd P/video && for f in *; do ln -s "$PWD/$f" $W/$f; done; rm $W/index.html $W/compositions
# (film 4) copy compositions/ for real: the bundler treats symlinked scene files as "empty" and skips them
cp -R compositions $W/compositions   # re-copy your scene after each edit
# write $W/index.html = P/video/index.html with every scene host REMOVED except yours (keep HUD + audio)
cd $W && npx hyperframes@latest snapshot . --at <song-times> --no-end -o P/video/snapshots/<ID> --describe false --timeout 15000
```

## Verify (required before you finish)
```bash
export PATH=$(ls -d ~/.nvm/versions/node/v22*/bin | tail -1):$PATH; cd P/video
npx hyperframes@latest snapshot . --at <song-times> --no-end -o snapshots/<ID> --describe false
```
Snapshot each scene at: just after its start, mid-line, and 2–3 points through each HELD word, then LOOK at the PNGs
(Read tool). Check: lyric legible, fill state matches the timing, nothing clipped/overlapping the HUD, scene looks
finished and inventive. Fix and re-snapshot until it is great. Also run
`npx hyperframes@latest lint . 2>&1 | grep -A3 "<your ids>"` and fix every error/warning in YOUR files.
Only edit your own `compositions/<ID>.html` files. Do not edit index.html, the engine, or other scenes.

## Report back
Per scene: one line on the concept as built, which song times you snapshotted, and anything you could not get right.
