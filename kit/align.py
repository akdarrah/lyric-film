"""Lyrics -> per-letter timing (chars.json + video/lyrics-data.js).

Forced-aligns the known lyrics (suno.md) against vocals.wav, extends word ends while the
voice keeps sounding (held notes get clipped by aligners), finds held notes with pyin, and
spreads each word's letters over time: consonants fast, the held vowel stretched.
"""
import json, os, re, sys
import numpy as np, librosa, stable_whisper

HOP = 256
SR = 22050
VOWELS = set("aeiouyAEIOUY")
HELD_MIN = 0.35  # seconds of steady pitch that counts as a held note

def lyric_lines():
    # sung.md (lyrics exactly as the chosen take sings them) overrides suno.md when present.
    md = open("sung.md").read() if os.path.exists("sung.md") else open("suno.md").read()
    body = md.split("## Lyrics", 1)[1].split("## After", 1)[0]
    lines, section = [], None
    for raw in body.splitlines():
        s = raw.strip()
        if not s or s.startswith("(") or s.startswith("```") or s.startswith("---"):
            continue
        if s.startswith("["):
            section = s.strip("[]")
            continue
        lines.append({"text": s, "section": section})
    return lines

def align(lines):
    import os
    if os.path.exists("words_raw.json"):
        return json.load(open("words_raw.json"))
    model = stable_whisper.load_model("medium.en")
    text = "\n".join(l["text"] for l in lines)
    res = model.align("vocals.wav", text, language="en", original_split=True)
    words = [w for seg in res.segments for w in seg.words]
    # Map aligned words back to lyric characters by walking non-space chars in order.
    flat = [(li, ch) for li, l in enumerate(lines) for ch in l["text"]]
    out, k = [], 0
    for w in words:
        wt = w.word.strip()
        while k < len(flat) and flat[k][1].isspace():
            k += 1
        li = flat[k][0]
        got = "".join(c for _, c in flat[k:k + len(wt)])
        assert got == wt, f"alignment text drift: {got!r} != {wt!r}"
        out.append({"w": wt, "line": li, "t0": float(w.start), "t1": float(w.end)})
        k += len(wt)
    json.dump(out, open("words_raw.json", "w"), indent=1)
    return out

def repair(words, lines):
    """Fix the two failure modes forced alignment has on sung vocals."""
    # 1. A gap > 2s inside one line means the aligner dragged a word into an ad-lib.
    #    Re-align that line alone in a tight window ending 1.5s after the pre-gap word.
    model = None
    for li, l in enumerate(lines):
        ws = [w for w in words if w["line"] == li]
        gaps = [k for k in range(1, len(ws)) if ws[k]["t0"] - ws[k - 1]["t1"] > 2.0]
        if not gaps:
            continue
        a, b = ws[0]["t0"] - 0.2, ws[gaps[0] - 1]["t1"] + 1.5
        model = model or stable_whisper.load_model("medium.en")
        y, _ = librosa.load("vocals.wav", sr=16000, offset=a, duration=b - a)
        res = model.align(y, l["text"], language="en")
        new = [w for seg in res.segments for w in seg.words]
        assert [w.word.strip() for w in new] == [w["w"] for w in ws], "realign word mismatch"
        for w, n in zip(ws, new):
            w["t0"], w["t1"] = a + float(n.start), a + float(n.end)
        print(f"realigned line {li} in [{a:.2f},{b:.2f}]")
    # 2. Runs of (near) zero-length words: give them real time. Borrow the silence before the run
    #    (back to the previous word's end, max 1s); if that's still too tight, merge in the
    #    neighbouring word (next in the line, else previous) and split the span by letter count.
    i = 0
    while i < len(words):
        if words[i]["t1"] - words[i]["t0"] >= 0.08:
            i += 1; continue
        j = i
        while j + 1 < len(words) and words[j + 1]["line"] == words[i]["line"] and words[j + 1]["t1"] - words[j + 1]["t0"] < 0.08:
            j += 1
        run = list(range(i, j + 1))
        prev_end = words[i - 1]["t1"] if i > 0 else 0.0
        start = max(prev_end, words[i]["t0"] - 1.0)
        end = words[j]["t1"]
        if end - start < 0.12 * len(run):
            if j + 1 < len(words) and words[j + 1]["line"] == words[i]["line"]:
                run.append(j + 1); end = words[j + 1]["t1"]
            elif i > 0 and words[i - 1]["line"] == words[i]["line"]:
                run.insert(0, i - 1); start = words[i - 1]["t0"]
        tot = sum(len(words[k]["w"]) for k in run)
        t = start
        for k in run:
            d = (end - start) * len(words[k]["w"]) / tot
            words[k]["t0"], words[k]["t1"] = t, t + d
            t += d
        i = j + 1
    return words

def vocal_hits(windows):
    """Onset times of wordless vocals (chops / 'oh's) so interlude scenes can sync to them."""
    y, _ = librosa.load("vocals.wav", sr=SR)
    on = librosa.onset.onset_detect(y=y, sr=SR, hop_length=HOP, units="time", backtrack=False)
    return {name: [round(float(t), 3) for t in on if a <= t < b] for name, (a, b) in windows.items()}

def acoustic(words):
    y, _ = librosa.load("vocals.wav", sr=SR)
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    f0, voiced, _ = librosa.pyin(y, fmin=120, fmax=1100, sr=SR, hop_length=HOP)
    t = lambda i: i * HOP / SR
    fi = lambda s: int(s * SR / HOP)
    thr = np.percentile(rms[rms > 0], 40)
    for i, w in enumerate(words):
        # Aligners often start a word in the silence before it (esp. line-openers after a gap):
        # move t0 forward to where the voice is actually sounding (max 70% of the word).
        d = w["t1"] - w["t0"]
        j0, lim = fi(w["t0"]), fi(w["t0"] + max(0.0, min(0.7 * d, d - 0.04 * len(w["w"]))))  # keep ~40ms/letter
        while j0 < lim and rms[j0] <= thr:
            j0 += 1
        w["t0"] = t(j0)
        song_end = json.load(open("film.json")).get("song_end", len(y) / SR) if os.path.exists("film.json") else len(y) / SR
        nxt = words[i + 1]["t0"] if i + 1 < len(words) else song_end  # film.json song_end: trim point
        # Extend the end while the voice is still sounding (cap at the next word).
        last_in_line = i + 1 >= len(words) or words[i + 1]["line"] != w["line"]
        # Tested on film 2: any looser rule (pitched OR half-loud, or a mix) chains into backing
        # vocals/reverb tails and makes fills lag the lead voice. Loudness-only matches pyin.
        sounding = lambda j: rms[j] > thr
        j = fi(w["t1"])
        while j < len(rms) - 1 and t(j) < nxt - 0.02 and sounding(j):
            j += 1
        w["t1"] = max(w["t1"], min(t(j), nxt - 0.02))
        # Held = longest run of voiced frames with pitch within 1 semitone of its start.
        a, b = fi(w["t0"]), fi(w["t1"])
        best, run_start = (0, a, a), None
        for k in range(a, b + 1):
            ok = k < len(voiced) and voiced[k]
            if ok and run_start is not None and abs(12 * np.log2(f0[k] / f0[run_start])) > 1.0:
                run_start = k
            elif ok and run_start is None:
                run_start = k
            elif not ok:
                run_start = None
            if run_start is not None and k - run_start > best[0]:
                best = (k - run_start, run_start, k)
        w["held"] = t(best[0]) >= HELD_MIN
        if w["held"]:
            w["h0"], w["h1"] = t(best[1]), t(best[2])
        elif last_in_line and w["t1"] - w["t0"] >= 0.7:
            # A long line-final word whose pitch moves (belt/melisma) is still a held note.
            w["held"] = True
            w["h0"], w["h1"] = w["t0"] + min(0.15, 0.25 * (w["t1"] - w["t0"])), w["t1"]
    # Final ordering pass: aligner overlaps + end-extension can let a word run past the next one's
    # start, which puts letters out of order. Each word starts after the previous starts, and ends
    # no later than the next one starts.
    for i in range(1, len(words)):
        words[i]["t0"] = max(words[i]["t0"], words[i - 1]["t0"] + 0.03)
    for i in range(len(words) - 1):
        words[i]["t1"] = max(words[i]["t0"] + 0.03, min(words[i]["t1"], words[i + 1]["t0"]))
        if words[i].get("held"):
            words[i]["h1"] = min(words[i]["h1"], words[i]["t1"]); words[i]["h0"] = min(words[i]["h0"], words[i]["h1"])
    return words

def syllables(word):
    """Split into chunks: each = consonants + vowel group (last chunk keeps trailing coda)."""
    chunks = re.findall(r"[^aeiouyAEIOUY]*[aeiouyAEIOUY]+", word)
    if not chunks:
        return [word]
    rest = word[len("".join(chunks)):]
    chunks[-1] += rest
    return chunks

def letters(w):
    word, t0, t1 = w["w"], w["t0"], w["t1"]
    out = []
    if w["held"]:
        # Letters up to the held vowel fill before h0; vowel spreads over the hold; coda after.
        groups = list(re.finditer(r"[aeiouyAEIOUY]+", word))
        m = groups[-1] if groups else None
        # Silent final e (data-BASE, ma-CHINE, in-CLUDES): the sung hold is the vowel before it.
        if len(groups) > 1 and re.search(r"[^aeiouy]e[sd]?\W*$", word.lower()) and m.group() == "e":
            m = groups[-2]
        if m is None:
            m = re.match(r".*", word)
        pre, vow, coda = word[:m.start()], word[m.start():m.end()], word[m.end():]
        h0 = max(t0 + 0.04 * len(pre), min(w["h0"], t1 - 0.1))
        h0 = min(h0, t0 + 0.8 * (t1 - t0))  # short held words: the hold can't start after the word ends
        coda_t = min(0.08 * len(coda), (t1 - h0) * 0.25)
        h1 = t1 - coda_t
        segs = [(pre, t0, h0), (vow, h0, h1), (coda, h1, t1)]
    else:
        segs = [(word, t0, t1)]
    for s, a, b in segs:
        if not s:
            continue
        weights = [2.0 if c in VOWELS else (0.3 if not c.isalnum() else 1.0) for c in s]
        tot = sum(weights)
        acc = a
        for c, wt in zip(s, weights):
            d = (b - a) * wt / tot
            out.append({"c": c, "t0": round(acc, 3), "t1": round(acc + d, 3)})
            acc += d
    return out

def build():
    lines = lyric_lines()
    words = acoustic(repair(align(lines), lines))
    data = []
    for li, l in enumerate(lines):
        ws = [w for w in words if w["line"] == li]
        data.append({
            "i": li, "text": l["text"], "section": l["section"],
            "t0": round(ws[0]["t0"], 3), "t1": round(ws[-1]["t1"], 3),
            "words": [{"w": w["w"], "t0": round(w["t0"], 3), "t1": round(w["t1"], 3),
                       "held": bool(w["held"]), "chars": letters(w)} for w in ws],
        })
    check(data)
    json.dump(data, open("chars.json", "w"), indent=1)
    # Wordless vocal sections (ad-libs, chops) per film: hits.json = {"name": [t0, t1], ...},
    # plus optional {"name": {"extra": [...]}} pitch-change points for legato syllables.
    cfg = json.load(open("hits.json")) if os.path.exists("hits.json") else {}
    hits = vocal_hits({k: v["window"] if isinstance(v, dict) else v for k, v in cfg.items()})
    for k, v in cfg.items():
        if isinstance(v, dict) and v.get("extra"):
            hits[k] = sorted(set(hits[k] + v["extra"]))
    json.dump(hits, open("vocal_hits.json", "w"))
    open("video/lyrics-data.js", "w").write(
        "window.LYRICS = " + json.dumps(data) + ";\nwindow.VOCAL_HITS = " + json.dumps(hits) + ";\n")
    print({k: len(v) for k, v in hits.items()}, "vocal hits")
    for l in data:
        held = [w["w"] for w in l["words"] if w["held"]]
        print(f'{l["i"]:2} {l["t0"]:7.2f}-{l["t1"]:7.2f}  {l["text"]}' + (f'   HELD: {held}' if held else ""))

def check(data):
    prev = 0.0
    for l in data:
        assert "".join(c["c"] for w in l["words"] for c in w["chars"]) == l["text"].replace(" ", ""), l["text"]
        for w in l["words"]:
            for c in w["chars"]:
                assert c["t0"] >= prev - 1e-3, f"non-monotonic at {l['text']!r}/{w['w']}"
                assert c["t1"] - c["t0"] >= 0.005 or not c["c"].isalnum(), f"letter too short {w['w']}"
                prev = c["t0"]

if __name__ == "__main__":
    build()
