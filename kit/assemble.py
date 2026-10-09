"""video/scenes.json -> video/index.html (root: audio, fonts, tokens, HUD, one host per scene)."""
import json

S = json.load(open("video/scenes.json"))
END = round(S[-1]["start"] + S[-1]["duration"], 3)
L = json.load(open("chars.json"))
QUEUED = L[1]["t0"]          # "Eleven forty-four..." — clock reads 11:44:00 here
DEEP0, DEEP1 = L[5]["t0"], L[6]["t0"]  # "Two hours deep" — the clock sprints two hours (in 1.6s, like s05)
HUD_IN = S[1]["start"]
CART_IN = [w for w in L[6]["words"] if w["w"] == "cart"][0]["t0"]   # "Made it to the cart"
CART_OUT = [w for w in L[6]["words"] if w["w"] == "bot"][0]["t0"]   # "...got a bot pack"

# Guard the two mistakes builders made 3x across films: renaming the scene's own root id, and
# giving an inner element the scene id (the host slot uses it, so GSAP then moves the whole scene).
import os, re
for sc in S:
    p = f"video/compositions/{sc['id']}.html"
    if not os.path.exists(p):
        continue
    src = open(p).read()
    assert f'id="root" data-composition-id="{sc["id"]}"' in src, f"{p}: #root data-composition-id must be {sc['id']}"
    assert not re.search(rf'\sid="{re.escape(sc["id"])}"', src), f"{p}: an inner element reuses the scene id {sc['id']}"
    # Every scene's root is #root, so a script selector "#root" hits ALL scenes (film 3 near-miss).
    for js in re.findall(r"<script>(.*?)</script>", src, re.S):
        assert "#root" not in js, f"{p}: scripts must not target #root (it matches every scene); use a scene-prefixed element"

hosts = "\n".join(
    f'      <div id="{s["id"]}" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" '
    f'data-start="{s["start"]}" data-duration="{s["duration"]}" data-track-index="1" data-width="1920" data-height="1080"></div>'
    for s in S)

html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>FILM TITLE</title>  <!-- per film -->
    <script src="assets/gsap.min.js"></script>
    <script src="lyrics-data.js"></script>
    <script src="assets/lyric-engine.js"></script>
    <style>
      @font-face {{ font-family: "Archivo"; font-weight: 900; src: url("assets/fonts/archivo-latin-900-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Archivo"; font-weight: 700; src: url("assets/fonts/archivo-latin-700-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "JetBrains Mono"; font-weight: 400; src: url("assets/fonts/jetbrains-mono-latin-400-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "JetBrains Mono"; font-weight: 700; src: url("assets/fonts/jetbrains-mono-latin-700-normal.woff2") format("woff2"); }}
      @font-face {{ font-family: "Instrument Serif"; font-style: italic; font-weight: 400; src: url("assets/fonts/instrument-serif-latin-400-italic.woff2") format("woff2"); }}
      :root {{
        --bg: #0B0F1F; --bone: #F2EEE4; --bone-50: rgba(242,238,228,0.5); --bone-20: rgba(242,238,228,0.2);
        --ghost: rgba(242,238,228,0.14); --accent: #FFD23F; --accent-glow: rgba(255,210,63,0.75);
      }}
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: var(--bg); }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--bg); color: var(--bone); }}
      .f-display {{ font-family: "Archivo", sans-serif; font-weight: 900; letter-spacing: -0.02em; }}
      .f-bold {{ font-family: "Archivo", sans-serif; font-weight: 700; }}
      .f-mono {{ font-family: "JetBrains Mono", monospace; }}
      .f-serif {{ font-family: "Instrument Serif", serif; font-style: italic; }}
      .hud {{ font-family: "JetBrains Mono", monospace; font-size: 18px; color: var(--bone-50); letter-spacing: 0.04em; }}
      .hud b {{ color: var(--accent); font-weight: 700; }}
      /* lyric engine */
      .lf-line {{ white-space: nowrap; }}
      .lf-flow .lf-w {{ display: inline-block; white-space: nowrap; }}
      .lf-sp {{ display: inline-block; white-space: pre; }}
      .lf-abs {{ position: absolute; inset: 0; }}
      .lf-c {{
        --p: 0; --g: 0; --on: var(--accent);
        display: inline-block; white-space: pre; transform-origin: 50% 70%;
        color: transparent; -webkit-background-clip: text; background-clip: text;
        background-image: linear-gradient(90deg, var(--on) 0%, var(--on) calc(var(--p) * 100%), var(--ghost) calc(var(--p) * 100%), var(--ghost) 100%);
        filter: drop-shadow(0 0 calc(var(--g) * 22px) rgba(255, 210, 63, calc(var(--g) * 0.75))); /* alpha follows --g: no tint at rest */
      }}
      #hud {{ position: absolute; inset: 0; pointer-events: none; z-index: 50; }}
      #hud .tl {{ position: absolute; left: 48px; top: 36px; }}
      #hud .tr {{ position: absolute; right: 48px; top: 36px; text-align: right; }}
      #hud .bl {{ position: absolute; left: 48px; bottom: 36px; }}
      #hud .br {{ position: absolute; right: 48px; bottom: 36px; text-align: right; }}
      #hud .corner {{ position: absolute; width: 22px; height: 22px; border-color: var(--bone-20); border-style: solid; }}
    </style>
    <script>
      // Start every font load now, so document.fonts.ready in each scene waits for real fonts
      // (otherwise it can resolve before a lazily-requested face is even requested).
      ["900 10px Archivo", "700 10px Archivo", "400 10px 'JetBrains Mono'", "700 10px 'JetBrains Mono'",
       "italic 400 10px 'Instrument Serif'"].forEach((f) => document.fonts.load(f));
    </script>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{END}" data-width="1920" data-height="1080">
      <audio id="bgm" src="assets/bgm.mp3" data-start="0" data-duration="{END}" data-track-index="11"></audio>
{hosts}
      <div id="hud" class="clip" data-start="0" data-duration="{END}" data-track-index="20">
        <div id="hud-in">
          <div class="tl hud">queue: <b>active</b> &nbsp;·&nbsp; <span id="hud-clock">11:43:50</span> ET</div>
          <div class="tr hud">cart: <b id="hud-cart">0</b> / 2</div>
          <div class="bl hud">Mega Evolution — Delta Reign · ETB</div>
          <div class="br hud">resale: <b id="hud-p">$59.99</b></div>
          <div class="corner" style="left:24px;top:24px;border-width:2px 0 0 2px"></div>
          <div class="corner" style="right:24px;top:24px;border-width:2px 2px 0 0"></div>
          <div class="corner" style="left:24px;bottom:24px;border-width:0 0 2px 2px"></div>
          <div class="corner" style="right:24px;bottom:24px;border-width:0 2px 2px 0"></div>
        </div>
      </div>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const pad = (n) => String(Math.floor(n)).padStart(2, "0");
      const clock = document.getElementById("hud-clock"), price = document.getElementById("hud-p"), cart = document.getElementById("hud-cart");
      // Clock (seconds of day): 11:44:00 when the queue line is sung, sprints 2h on "Two hours deep", then real time.
      const H = (h, m, sec) => h * 3600 + m * 60 + sec;
      const CK = [[0, H(11, 43, 50)], [{QUEUED}, H(11, 44, 0)], [{DEEP0}, H(11, 44, 15)], [{DEEP0} + 1.6, H(13, 44, 0)], [{END}, H(13, 44, 0) + ({END} - {DEEP0} - 1.6)]];
      // Resale price keyframes: MSRP until the scalpers show up, $527.97 once the price line lands.
      const PK = [[0, 59.99], [40, 59.99], [53, 149.99], [80, 214.5], [83.3, 527.97], [{END}, 527.97]];
      const interp = (K, t) => {{
        for (let i = 1; i < K.length; i++) if (t <= K[i][0]) {{
          const [a, va] = K[i - 1], [b, vb] = K[i]; const u = b > a ? (t - a) / (b - a) : 1;
          return va + (vb - va) * u * u * (3 - 2 * u);
        }}
        return K[K.length - 1][1];
      }};
      // Setter proxy: GSAP writes .t on every render/seek, which redraws the HUD (onUpdate can be skipped on seek).
      const hudProxy = {{ _t: 0, get t() {{ return this._t; }}, set t(t) {{ this._t = t; drawHud(t); }} }};
      function drawHud(t) {{
        const s = interp(CK, t);
        clock.textContent = pad(s / 3600) + ":" + pad((s % 3600) / 60) + ":" + pad(s % 60);
        price.textContent = "$" + interp(PK, t).toFixed(2);
        // s06: "Made it to the cart" puts 1 in the cart; it's gone again on "bot pack".
        cart.textContent = t >= {CART_IN} && t < {CART_OUT} ? "1" : "0";
      }}
      tl.fromTo(hudProxy, {{ t: 0 }}, {{ t: {END}, duration: {END}, ease: "none" }}, 0);
      tl.fromTo("#hud-in", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.6, ease: "power2.out" }}, {HUD_IN});  // after the intro title cards
      tl.fromTo("#hud-in", {{ opacity: 1 }}, {{ opacity: 0, duration: 1.5, ease: "power2.in", immediateRender: false }}, {END} - 6);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
open("video/index.html", "w").write(html)
print("index.html:", len(S), "scenes,", END, "s")
