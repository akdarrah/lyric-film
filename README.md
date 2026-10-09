# lyric-film

A [Claude Code](https://claude.com/claude-code) skill that turns a topic into a dense, scene-per-line kinetic
lyric video: Claude writes the song with you, you generate it in [Suno](https://suno.com), and Claude aligns
every sung letter to the vocal and builds one animated scene per lyric line with
[HyperFrames](https://hyperframes.heygen.com). Lyrics fill letter by letter exactly as they're sung, slowing down
on held notes.

## Films made with it

- [N+1](https://youtu.be/G1s02Yy8j0o) — a 3 a.m. Rails N+1 query incident
- [Gotta Catch 'Em All Gone](https://youtu.be/7F-IUyoiHGU) — losing the Pokémon Center queue to bots and scalpers
- [Ten-Eight, Wichita](https://youtu.be/5iMaHzzBZ2k) — a rookie officer's first shift
- [Now We're Live](https://youtu.be/oadlWQrSfg0) — building the blog akdarrah.com

Read more: [akdarrah.com](https://akdarrah.com)

## How it works

1. **Concept and lyrics.** Claude researches insider references for your topic and writes a tightly rhymed,
   hook-first electropop song where every line is drawable. You approve the lyrics, a design spec and a
   per-line scene plan.
2. **Song.** You generate it in Suno with the style prompt from `suno.md` and save the WAV.
3. **Timing.** Demucs separates the vocal, stable-ts force-aligns the known lyrics, and `align.py` spreads each
   word's letters over time (held vowels stretched, ad-libs detected). `plan.py` snaps scene cuts to the beat.
4. **Build.** Claude writes one reference scene, then parallel subagents build the rest from `BUILD.md`, each
   checking their own snapshots. `assemble.py` writes the root composition with audio, fonts and a HUD.
5. **Verify and render.** Lint, full-project snapshots as contact sheets, frame checks on the longest held notes,
   then a 1080p60 MP4.

## Install

```sh
git clone https://github.com/akdarrah/lyric-film ~/.claude/skills/lyric-film
```

Then in Claude Code: `/lyric-film a song about <your topic>`.

## Requirements

- Claude Code, and a Suno account to generate the song.
- Node 22+ (for HyperFrames, which runs via `npx`).
- Python 3.11 venv in the project: `uv venv --python 3.11 .venv && uv pip install demucs stable-ts librosa soundfile "torch<2.9" "torchaudio<2.9"`
  (about 3 GB with the Whisper `medium.en` model).
- `ffmpeg`.

## What's in here

- `SKILL.md` — the workflow Claude follows, including songwriting rules and hard-won gotchas.
- `kit/` — working files to copy into each film: `align.py`, `plan.py`, `assemble.py`, `lyric-engine.js`,
  `BUILD.md` (the scene-builder brief, with `<placeholders>` to fill per film) and `example-scene.html`.
  `plan.py`, `assemble.py` and the example scene carry one film's values as worked examples; adapt them per film.
