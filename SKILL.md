---
name: lyric-film
description: Make a dense, multi-scene kinetic lyric video from a Suno song, with per-letter lyric fill synced to the vocal, including held notes. Use for "/lyric-film", "make a lyric video like the AGI/P(doom) one", or turning a Suno track + lyrics into a scene-per-line film.
---

# Lyric Film

Goal: every lyric line gets its own visual metaphor inside ONE locked art direction,
and the sung text fills letter-by-letter exactly as it is sung, slowing on held notes.

Project folder: `~/lyric-films/<slug>/` (any folder works; keep one per film).

## Music style (default — use for every film unless the user asks otherwise)
Matches the reference film (x.com/justalexoki/status/2103841051228418113: ~130 bpm,
E♭ major, heavy synth sub-bass, bright female lead, breakdown ~60% in).
Never pick a genre from the topic's mood — a sad/3am topic still gets this sound.

Suno "Style of Music":
```
upbeat electropop, 130 bpm, E-flat major, punchy four-on-the-floor drums, deep synth sub bass, bright arpeggiated synths, catchy confident female pop vocal, crisp clear enunciation, belted sustained notes on the chorus hooks, glossy modern production, anthemic instantly catchy chorus hook, chant-along post-chorus, stripped-back bridge breakdown into a huge final chorus
```
Suno "Exclude styles": `acoustic, folk, slow, lo-fi, ballad`

## Songwriting (user feedback from film 1 "N+1": visuals + sync were great, but the song had
## no part that hooked them to come back — the chorus must be the strongest thing in the film)

The hook (non-negotiable):
- ONE short, chantable hook phrase (2–5 words) that IS the title, e.g. "N plus one". It opens the
  chorus AND closes it, and repeats at least 2× per chorus. If you can't hum it after one read,
  rewrite it.
- Chorus lines: short (3–7 syllables), simple words, repetition over cleverness. Save the dense
  references for the verses; the chorus trades detail for singability.
- Give the hook a lift: a [Pre-Chorus] that builds tension (rising, shorter lines) so the chorus
  lands as a release. Add a [Post-Chorus] that chants the hook (or a wordless "oh-oh" on the
  hook melody) so the drop sections are hooky, not just instrumental.
- Reach the first chorus within ~35s. The chorus appears 3×; the last one is doubled/bigger.

Craft (user preference, stated after film 2 draft — applies to EVERY song):
- Lots of TIGHT rhyme. Every line pair rhymes at the end (AABB or ABAB, no orphan lines), and
  verses also carry internal and multisyllabic rhymes ("queue page / blue rage / two days").
  Prefer perfect or near-perfect rhymes over loose slant rhymes; read each couplet aloud.
- SHARP, SMART references. Every verse line should carry a specific, niche detail an insider of
  the subject would recognise (jargon, in-jokes, famous incidents, exact numbers/quotes, game
  mechanics used as metaphor). Generic lines ("I tried so hard") get rewritten.
- Wordplay that double-codes: a phrase that works literally AND as a subject reference
  (e.g. using a card-game mechanic or a classic game line to describe the real-life situation).
- Research pass for this (Phase 1, before writing): a subagent gathers 25+ niche references with
  sources — community lore and drama, slang, iconic quotes/mechanics, current events — ranked by
  "would an insider nod at this?". Write from that list; cite nothing you can't verify.
  (Reddit blocks fetches and the headless browser; use news/wikis/blogs, or ask the user to
  paste posts.)

Structure: [Intro] (hook teased) → [Verse] → [Pre-Chorus] → [Chorus] → [Post-Chorus] →
[Verse 2] → [Pre-Chorus] → [Chorus] → [Bridge] → [Final Chorus] (×2, key change or bigger) → [Outro].
Verse lines: punchy, ~8–12 syllables, every line drawable. Chorus line-ends on open vowels
for belted holds (the held-note visuals need them).
Write the full chorus text every time (no "(repeat)") — alignment needs the exact sung text.

Pronunciation (Suno sang "post ID" as the word "id", not "I-D"):
- Spell every acronym/initialism the way it must be sung, letters hyphenated: "I-D", "S-Q-L",
  "A-P-I", "C-P-U". Numbers and symbols as words: "P ninety-nine", "forty-seven percent".
  Only leave a term unspelled if it's said as a word (e.g. "Rubocop", "OOM" → write "O-O-M").
- The lyrics text in suno.md must equal what is sung (alignment depends on it); scenes may show
  the stylized form (ID, SQL, p99) in UI props, but the sung lyric line uses the sung spelling.
- Before handing lyrics over, scan every line for capitals, digits and symbols and fix them.

Only if the user gives a DIFFERENT reference: analyze its audio first (librosa tempo,
key via chroma vs. Krumhansl profiles, band energy, pyin vocal range above 140 Hz,
RMS per 10s for structure) and write a style that matches it.

## Phase 1 — Concept & lyrics (stop for approval)
- Topic must be dense with drawable references (artifacts, UI, diagrams, numbers, memes).
- Write lyrics where EVERY line names something drawable. Rewrite abstract lines.
  Put long open vowels on chorus line-ends so there are held notes to show off.
- Self-check before showing lyrics: (1) say the hook out loud — is it the title, ≤5 words,
  repeated ≥2× per chorus? (2) pronunciation scan: no bare acronyms/digits/symbols.
  (3) rhyme scan: mark each line's end-rhyme letter — no unrhymed lines; count internal rhymes
  per verse (aim 2+). (4) reference scan: every verse line has a niche, verifiable detail.
- `suno.md`: title, the default style + exclude styles above, exact lyrics with [Section] tags,
  download instructions. Also give the user these as copy/paste blocks in chat.
- `design.md`: bg, ONE accent color, display + mono + serif fonts, HUD grammar,
  lyric rendering rules, 3–4 recurring props used as callbacks.
- `scenes.md`: one row per line → visual, how text behaves with that visual.

## Phase 2 — Song (user does this in Suno)
- User generates and picks a take matching the lyrics; they drop the WAV in the project
  folder (Downloads is fine — copy it to `song.wav`). A vocal stem is nice but NOT required:
  separate it yourself (Demucs, below).

## Kit (start every film from these — `kit/` in this skill folder)
Working, battle-tested files from the first film (N+1). Copy into the project, then adapt:
- `align.py` — lyrics (from suno.md) → per-letter `chars.json` + `video/lyrics-data.js`.
- `plan.py` — scene list → beat-snapped `video/scenes.json` (+ BEATS/DOWNBEATS/SCENES globals).
  The SCENES table is per-film; the snapping logic is reusable.
- `assemble.py` — scenes.json → root `video/index.html` (audio, fonts, tokens, HUD, hosts).
  The HUD keyframes are per-film.
- `lyric-engine.js` — `LF.mount / onPath / animate / measure / withLayout`. Copy to `video/assets/`.
- `BUILD.md` — the scene-builder brief (rules + lyric rules + verify). Update paths/story.
- `example-scene.html` — a working scene to copy.

Environment: HyperFrames needs Node ≥ 22 (`export PATH=~/.nvm/versions/node/v22.*/bin:$PATH`).
Python: one venv in the project: `uv venv --python 3.11 .venv && uv pip install demucs stable-ts
librosa soundfile "torch<2.9" "torchaudio<2.9"`. Needs ~3 GB disk (torch + whisper medium.en).

## Phase 3 — Timing
0. Copy the kit, then per film: `sung.md` (optional, lyrics exactly as sung if the take deviates),
   `hits.json` (optional wordless-vocal windows), the SCENES table in plan.py, and the palette +
   HUD keyframes in assemble.py. Engine colors come from `--accent` / `--bone` CSS variables.
- Suno sings ANYTHING the user pastes. Films 2 AND 3 both ended with Suno singing the "how to pick a
  take" notes, even with the lyrics fenced — the user copies everything after the lyrics too.
  RULE: in the chat hand-off, the lyrics copy block is the LAST thing in the message. All notes
  (how to pick a take, where to save the WAV) go ABOVE it. Nothing follows the block.
  Always transcribe the ending; trim the audio (ffmpeg -t + afade) before any stray singing.
- Suno often repeats the hook more times than written (film 3: 3x instead of 2x in early choruses,
  4x in the last). Forced alignment then squeezes the next line into the extra hooks. Detect it:
  stable-ts `model.align(clip, variant_text)` for each candidate repetition count and compare mean
  word `probability` (highest wins; cross-check with the windowed transcript), then write the true
  lyrics to `sung.md` (align.py prefers it). Also trim `vocals.wav` at the song's real end before
  aligning, or the aligner drags the outro into any trailing junk.
- Suno doesn't always hit the requested BPM (asked 130, got 136): use the measured grid only.
- Once builders start, `cp video/scenes.json scenes.lock.json`: plan.py then keeps those cut times even if
  timing data is regenerated, and compresses any held word that would overrun its scene's cut.
- Hold detection (tested on film 2): extend word ends on loudness only. Looser rules (pitched OR quiet,
  or mixes) chain into backing vocals/reverb and make fills lag the lead. Long (≥0.7s) line-final words
  count as held even when the pitch moves (belts). Many chorus "gone"-type words are genuinely short with
  instrumental gaps after — scenes should animate those gaps rather than the data faking a hold.
- assemble.py refuses to build if a scene's #root id was renamed or an inner element reuses the scene id
  (builders did this 3x across two films).
1. `python -m demucs --two-stems=vocals -n htdemucs -o sep song.wav` → `vocals.wav`.
2. Run `align.py` (stable-ts `medium.en`, forced alignment of the KNOWN lyrics on vocals.wav).
3. ALWAYS also free-transcribe the vocals (in ~15s windows, `condition_on_previous_text=False`)
   and compare: Suno adds ad-libs / "oh oh" / vocal chops that aren't in the lyrics. Forced
   alignment will drag a word into them (symptom: a > 2s gap inside one line). `align.py`
   re-aligns such lines in a tight window. Wordless sections become interlude scenes synced
   to `VOCAL_HITS`.
4. Legato ad-libs ("ohhh-oh") have no onset; detect each new syllable as a pyin pitch change.
5. Held notes: pyin steady pitch ≥ 350ms. Silent final e (data-BASE, ma-CHINE, in-CLUDES):
   the hold goes to the previous vowel. Zero-length pickup words share time with the next word.
6. Cross-check: word starts vs. librosa onsets on vocals → median offset should be ~0ms.

## Phase 4 — Build (HyperFrames: load /hyperframes first)
- ~1 scene per lyric line + interludes; every scene its own visual technique (3D card fields,
  SVG draw-on line art, UI recreations, inverted paper scenes, data-viz, full-frame flashes).
- Parallelize: one builder subagent per 3–4 scenes sharing motifs, each given BUILD.md.
  Write the example scene yourself first and snapshot it to prove the engine.
- Hard-won gotchas (all handled in the kit, but keep them in BUILD.md):
  - Scenes build inside `document.fonts.ready` after the runtime set inactive slots to
    display:none → rects/offsets read 0. The engine wraps fonts.ready with `withLayout`.
    Prefer `LF.measure(el)` (canvas, honors text-transform) for text widths.
  - index.html must kick off `document.fonts.load(...)` for every face in <head>.
  - Never give an element the scene's own id (the host slot uses it).
  - Spaces between words must be spans (flex containers drop whitespace text nodes).
  - drop-shadow glow: alpha must follow `--g`, or the ghost text gets a ruby tint.
  - SVG draw-on: `pathLength="1000"`, not 1 (GSAP rounds dashoffset to whole px).
  - Text driven by `onUpdate` can be skipped on seek; use a setter proxy (see HUD).
  - Concurrent `hyperframes snapshot` runs on one project hang. Builders verify in a /tmp copy
    whose index.html loads only their scenes; the orchestrator snapshots the full project alone.

## Phase 5 — Verify
- Lint: 0 errors. Full-project snapshot (with `--timeout 15000`) at: start of each scene, middle of its longest held
  word, end of its line, and several vocal hits per interlude; review as contact sheets.
- Look specifically for: overlapping text, missing elements (zero-measure bugs), clipped words,
  ghost text legibility, fill state matching timing.
- Render: `npx hyperframes render . -o renders/<name>.mp4 --fps 60 -q looks`.
- After render: extract frames at the 5 longest held notes and confirm the fill progresses
  across the note frame by frame.
