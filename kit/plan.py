"""Scene list -> video/scenes.json + window.BEATS/DOWNBEATS appended to video/lyrics-data.js.

Each cut is snapped to the latest beat at or before the target time (target = first line's
start minus a small lead), so cuts land on the music and the ghost text is up before it's sung.
"""
import json, math

L = json.load(open("chars.json"))
A = json.load(open("video/audiomap.json"))
beats, downs = A["grid"]["beats_sec"], A["grid"]["downbeats_sec"]
END = 169.0  # audio fades out at 168.0 (cut before the sung instructions); 1s end card

# (id, lines it carries, explicit start or None = before first line, one-line concept)
SCENES = [
    ("s00-intro",      [0],  0.0,  "Browser tab opens on a queue page, lone spinner; hook typed in the URL bar, 'gone' erases itself"),
    ("s01-wednesday",  [1],  None, "Desk calendar flips to WED, clock snaps to 11:44, LIVE pill"),
    ("s02-queue",      [2],  None, "Queue page recreation: 'You are currently in line', position box empty, '?' wait time"),
    ("s03-magikarp",   [3],  None, "Retro game text box: MAGIKARP used SPLASH! But nothing happened. Cursor mashing F5"),
    ("s04-snorlax",    [4],  None, "Giant sleeping silhouette across a server rack / route sign CHECKOUT"),
    ("s05-godpack",    [5],  None, "Clock spins 11:44->13:44; a booster pack glows with halo rays"),
    ("s06-botpack",    [6],  None, "Halo snaps off: the pack turns into a robot face / CAPTCHA grid"),
    ("s07-refresh",    [7, 8], None, "Pre-chorus A: cursor trembling over refresh; praying hands progress bar"),
    ("s08-next",       [9, 10], None, "Pre-chorus B: 'I'm next' bar jumps 3x; Add to Cart drains to grey"),
    ("s09-hook1",      [11, 12], None, "Chorus hook: huge kinetic GOTTA CATCH 'EM ALL, 'gone' clears a shelf"),
    ("s10-stock1",     [13, 14, 15], None, "Robot arm grabs the box; stock ticker of the box price shoots up; gone"),
    ("s11-post1",      [16, 17, 18, 19], None, "Post-chorus chant: SOLD OUT stamps; professor-style text box 'time and place... not now'; oh oh oh rings"),
    ("s12-rocket",     [20, 21], None, "Villain-duo spotlight, counter 2->28; crate blasts off, twinkle star"),
    ("s13-scale",      [22, 23], None, "Jeweler's scale weighing packs; heavy into backpack, light onto shelf 'for sale'"),
    ("s14-logan",      [24], None, "Livestream frame, sealed box cut open, toy-soldier silhouettes spill out"),
    ("s15-price",      [25], None, "Price tag $59.99 flips like an odometer to $527.97"),
    ("s16-chair",      [26], None, "Camping chair at dawn outside store doors, cardboard sign FAIR MARKET VALUE"),
    ("s17-moonbreon",  [27], None, "Moonlit rooftop cat silhouette under a crescent, pan down to an empty shelf"),
    ("s18-pre2",       [28, 29, 30, 31], None, "Pre-chorus 2: queue UI glitching harder, bar resets to 0"),
    ("s19-hook2",      [32, 33], None, "Chorus 2 hook over a rocketing resale chart"),
    ("s20-stock2",     [34, 35, 36], None, "Boxes fly off the shelf on each word; gone"),
    ("s21-slab",       [37, 38], None, "Bridge: graded slab under museum glass, dragon silhouette inside, glass glint"),
    ("s22-rip",        [39], None, "Booster close-up, tear line glows, holo shine sweeps a card"),
    ("s23-1999",       [40], None, "Warm memory: tree lights, kid's hands, fan of first-gen-style cards, CRT glow"),
    ("s24-final1a",    [41, 42], None, "Final chorus 1 hook: everything returns at max"),
    ("s25-final1b",    [43, 44, 45], None, "Final chorus 1 payoff: shelves, carts, scale, chair montage"),
    ("s26-final2a",    [46, 47], None, "Final chorus 2 hook: biggest type of the film"),
    ("s27-final2b",    [48, 49, 50], None, "Final chorus 2 payoff: full-frame volt flash on the last gone"),
    ("s28-outro",      [51, 52], None, "Healing-machine chime + nurse-hat silhouette; spinner freezes; end card"),
]

def snap(t, lo):
    """Latest beat in [max(lo, t-0.4), t]; else max(lo, t). Never cuts before lo."""
    cands = [b for b in beats if max(lo, t - 0.4) <= b <= t]
    # Round UP so a cut can never land a few ms before the previous line finishes.
    return math.ceil((cands[-1] if cands else max(lo, t)) * 1000) / 1000

starts = []
for sid, lines, start, _ in SCENES:
    if start is None:
        first = lines[0]
        prev_end = min(L[first - 1]["t1"], L[first]["t0"]) if first > 0 else 0.0  # lines can overlap by ms
        start = snap(L[first]["t0"] - 0.25, prev_end)
    starts.append(start)
starts[0] = 0.0
# scenes.lock.json (written once scenes are being built): keep approved cut times so rebuilt
# timing data never shifts scenes whose builders already hard-coded their durations.
import os
if os.path.exists("scenes.lock.json"):
    lock = {x["id"]: x["start"] for x in json.load(open("scenes.lock.json"))}
    starts = [lock.get(sid, st) for (sid, _, _, _), st in zip(SCENES, starts)]
# A held line-ending word that runs past its scene's cut is compressed to finish 20ms before it.
for i, (sid, lines, _, _) in enumerate(SCENES):
    e = starts[i + 1] if i + 1 < len(SCENES) else END
    for li in lines:
        w = L[li]["words"][-1]
        if w["t1"] > e - 0.02 and w["t0"] < e - 0.1:
            a, k = w["t0"], (e - 0.02 - w["t0"]) / (w["t1"] - w["t0"])
            for c in w["chars"]:
                c["t0"], c["t1"] = round(a + (c["t0"] - a) * k, 3), round(a + (c["t1"] - a) * k, 3)
            w["t1"] = L[li]["t1"] = round(e - 0.02, 3)
            print(f"compressed held '{w['w']}' (line {li}) to end at {e - 0.02:.2f} (scene cut)")
json.dump(L, open("chars.json", "w"), indent=1)
out = []
for i, (sid, lines, _, concept) in enumerate(SCENES):
    s = starts[i]
    e = starts[i + 1] if i + 1 < len(SCENES) else END
    for li in lines:
        assert s <= L[li]["t0"] and L[li]["t1"] <= e + 0.01, f"{sid}: line {li} outside [{s},{e}]"
    out.append({"id": sid, "start": s, "duration": round(e - s, 3), "lines": lines, "concept": concept})
    print(f"{sid:15} {s:7.2f} +{e - s:5.2f}  lines {lines}  {concept}")
json.dump(out, open("video/scenes.json", "w"), indent=1)

hits = json.load(open("vocal_hits.json")) if os.path.exists("vocal_hits.json") else {}
js = "window.LYRICS = " + json.dumps(L) + ";\nwindow.VOCAL_HITS = " + json.dumps(hits) + ";"
js += "\nwindow.BEATS = " + json.dumps([round(b, 3) for b in beats]) + ";\n"
js += "window.DOWNBEATS = " + json.dumps([round(b, 3) for b in downs]) + ";\n"
js += "window.SCENES = " + json.dumps({s["id"]: s["start"] for s in out}) + ";\n"
open("video/lyrics-data.js", "w").write(js)
