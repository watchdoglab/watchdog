"""Apple-style explainer reel for Watchdog (1080x1920, 30 fps, 30 s, soft soundtrack).

    python3 tools/video/explainer.py            # -> out/watchdog-explainer.mp4
    python3 tools/video/explainer.py 60 300     # preview frames -> out/explainer-frames/

Story, one idea per screen: you ship fast -> one line leaks your users -> Introducing Watchdog ->
it flags the bug inside Claude Code -> shows the fix -> 14 dogs -> tested -> install.
Shares helpers (fonts, icons, easing) with reel.py.
"""
import math
import os
import subprocess
import sys
import wave
from functools import partial
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from reel import DOGS, OUT, SLUG, back_out, ease_in_out, ease_out, font, get_icon, icon, paste_scaled  # noqa: E402

W, H, FPS = 1080, 1920, 30
SECONDS = 30
FRAMES = SECONDS * FPS
SF = "/System/Library/Fonts/SFNS.ttf"
MONO = "/System/Library/Fonts/SFNSMono.ttf"
INK = (17, 17, 20)
GREY = (110, 112, 120)
RED = (230, 57, 70)
GREEN = (22, 163, 74)
TEAL = (13, 148, 136)
BG = (250, 250, 252)

# (start, end) seconds of each scene
SCENES = [
    ("ship", 0.0, 2.6),
    ("line", 2.6, 6.4),
    ("intro", 6.4, 8.2),
    ("brand", 8.2, 11.0),
    ("watch", 11.0, 17.0),
    ("fix", 17.0, 20.4),
    ("pack", 20.4, 24.4),
    ("tested", 24.4, 27.0),
    ("cta", 27.0, 30.0),
]


def sf(size, weight="Bold"):
    """SF Pro at a named weight (variable font)."""
    f = font(SF, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def fade(t, start, end, fin=.45, fout=.35):
    """0..1 visibility of something shown from start to end (seconds), with rise-in / fade-out."""
    if t < start or t > end:
        return 0.0
    return min(ease_out((t - start) / fin), 1 - ease_in_out((t - (end - fout)) / fout) if t > end - fout else 1)


def text(img, xy, s, f, color, a=1.0, rise=0.0, anchor="mm"):
    if a <= 0:
        return
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((xy[0], xy[1] + rise), s, font=f, fill=(*color, int(255 * a)), anchor=anchor)
    img.alpha_composite(layer)


def headline(img, t, lines, start, end, y=H * .5, size=104, color=INK, stagger=.18, weight="Bold"):
    """Each line rises in on its own beat; all fade together."""
    f = sf(size, weight)
    for i, (s, c) in enumerate(l if isinstance(l, tuple) else (l, color) for l in lines):
        a = fade(t, start + i * stagger, end)
        text(img, (W / 2, y + i * size * 1.18), s, f, c, a, rise=(1 - ease_out((t - start - i * stagger) / .5)) * 40)


def card(img, box, a=1.0, radius=36, fill=(255, 255, 255), shadow=50):
    """White card with a soft drop shadow."""
    if a <= 0:
        return
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 24, x1, y1 + 24), radius, fill=(20, 24, 40, int(shadow * a)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
    c = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(c).rounded_rectangle(box, radius, fill=(*fill, int(255 * a)), outline=(228, 230, 236, int(255 * a)), width=2)
    img.alpha_composite(c)


def base(t):
    """Soft white with a slow, faint colour bloom."""
    g = Image.new("RGB", (W // 4, H // 4), BG)  # blurred at quarter size: soft and fast
    d = ImageDraw.Draw(g)
    cx = W * (.5 + .25 * math.sin(t * .35))
    cy = H * (.45 + .1 * math.cos(t * .27))
    q = lambda *v: [x / 4 for x in v]
    d.ellipse(q(cx - 700, cy - 700, cx + 700, cy + 700), fill=(226, 250, 244))
    d.ellipse(q(W - cx - 500, H - cy - 600, W - cx + 500, H - cy + 400), fill=(235, 238, 255))
    return g.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BICUBIC).convert("RGBA")


CODE = [
    ("app.get('/users', async (req, res) => {", None),
    ("  const rows = await db.query(", None),
    ("    `SELECT * FROM users WHERE id = ${req.query.id}`", "bad"),
    ("  );", None),
    ("  res.json(rows);", None),
    ("});", None),
]
FIXED = "    'SELECT * FROM users WHERE id = $1', [id]"


def code_card(img, t, top, a, highlight=0.0, fixed=0.0, scale=1.0):
    x0, x1 = 70, W - 70
    lh = 62
    y1 = top + 100 + lh * len(CODE) + 30
    card(img, (x0, top, x1, y1), a)
    if a <= 0:
        return
    d = ImageDraw.Draw(img)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 34 + i * 34, top + 36, x0 + 54 + i * 34, top + 56), fill=(*c, int(255 * a)))
    text(img, (W / 2, top + 46), "server.js", sf(28, "Semibold"), GREY, a)
    fm = font(MONO, 27)
    for i, (line, tag) in enumerate(CODE):
        y = top + 100 + i * lh
        if tag:
            if highlight > 0:
                hl = Image.new("RGBA", img.size, (0, 0, 0, 0))
                col = RED if fixed < .5 else GREEN
                k = highlight if fixed < .5 else 1
                ImageDraw.Draw(hl).rounded_rectangle((x0 + 16, y - 8, x0 + 16 + (x1 - x0 - 32) * k, y + lh - 14), 12,
                                                     fill=(*col, int(34 * a)))
                img.alpha_composite(hl)
            if fixed > 0:
                text(img, (x0 + 40, y + 18), line, fm, RED, a * (1 - fixed), anchor="lm")
                text(img, (x0 + 40, y + 18), FIXED, fm, GREEN, a * fixed, rise=(1 - fixed) * 20, anchor="lm")
                continue
        col = RED if tag and highlight > .3 else (40, 44, 52)
        text(img, (x0 + 40, y + 18), line, fm, col, a, anchor="lm")


def alert(img, t, y, a, title, body, fix):
    """The Watchdog finding, as it appears inside Claude Code."""
    if a <= 0:
        return
    x0, x1 = 70, W - 70
    h = 300
    off = (1 - back_out(min(1, a * 1.4))) * 120
    card(img, (x0, y + off, x1, y + h + off), a, fill=(255, 255, 255))
    stripe = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(stripe).rounded_rectangle((x0, y + off, x0 + 14, y + h + off), 7, fill=(*RED, int(255 * a)))
    img.alpha_composite(stripe)
    paste_scaled(img, get_icon("malinois", 400), x0 + 92, y + 78 + off, .26, alpha=a)
    text(img, (x0 + 150, y + 58 + off), "Malinois", sf(34, "Bold"), INK, a, anchor="lm")
    text(img, (x0 + 150, y + 98 + off), "CRITICAL  ·  server.js:3", sf(28, "Semibold"), RED, a, anchor="lm")
    text(img, (x0 + 50, y + 170 + off), title, sf(40, "Bold"), INK, a, anchor="lm")
    text(img, (x0 + 50, y + 222 + off), body, sf(30, "Regular"), GREY, a, anchor="lm")


def scene_ship(img, t, s, e):
    headline(img, t, ["You ship fast."], s + .1, e, y=H * .47, size=120)


def scene_line(img, t, s, e):
    p = t - s
    headline(img, t, ["But one line like this…"], s, s + 1.9, y=H * .25, size=84)
    headline(img, t, [("…can leak every user.", RED)], s + 1.9, e, y=H * .25, size=84)
    a = fade(t, s + .3, e, fin=.6)
    hl = ease_out((p - 1.2) / .6)
    code_card(img, t, int(H * .36 + (1 - ease_out(p / .7)) * 80), a, highlight=hl)


def scene_intro(img, t, s, e):
    headline(img, t, ["Introducing"], s + .1, e, y=H * .48, size=96, color=GREY, weight="Semibold")


def scene_brand(img, t, s, e):
    p = t - s
    a = fade(t, s, e)
    paste_scaled(img, get_icon("watchdog", 700), W / 2, H * .38, .62 + .08 * ease_out(p / 1.2), alpha=a)
    text(img, (W / 2, H * .58), "Watchdog", sf(140, "Bold"), INK, fade(t, s + .35, e), rise=(1 - ease_out((p - .35) / .5)) * 40)
    text(img, (W / 2, H * .645), "Security dogs for Claude Code", sf(50, "Medium"), GREY, fade(t, s + .6, e),
         rise=(1 - ease_out((p - .6) / .5)) * 30)


def terminal(img, t, s, top, a, typed, reply_a):
    x0, x1 = 70, W - 70
    card(img, (x0, top, x1, top + 400), a, fill=(255, 255, 255))
    if a <= 0:
        return
    text(img, (x0 + 46, top + 56), "Claude Code", sf(30, "Bold"), (204, 120, 92), a, anchor="lm")
    ImageDraw.Draw(img).line((x0 + 30, top + 100, x1 - 30, top + 100), fill=(236, 238, 242, int(255 * a)), width=2)
    prompt = "> add an endpoint to get a user by id"
    n = int(len(prompt) * typed)
    text(img, (x0 + 46, top + 160), prompt[:n] + ("▌" if typed < 1 else ""), font(MONO, 30), INK, a, anchor="lm")
    text(img, (x0 + 46, top + 240), "● Writing server.js…", sf(30, "Medium"), GREY, a * reply_a, anchor="lm")
    text(img, (x0 + 46, top + 300), "+ app.get('/users', …)", font(MONO, 28), GREEN, a * reply_a, anchor="lm")


def scene_watch(img, t, s, e):
    p = t - s
    headline(img, t, ["It watches", "while you code."], s, e, y=H * .13, size=92)
    a = fade(t, s + .2, e)
    terminal(img, t, s, int(H * .26), a, typed=ease_in_out((p - .5) / 1.6), reply_a=ease_out((p - 2.3) / .4))
    alert(img, t, int(H * .50), fade(t, s + 3.0, e, fin=.5), "SQL injection",
          "User input goes straight into the query.", "")
    if p > 3.0:
        text(img, (W / 2, H * .73), "Caught before it ships.", sf(56, "Semibold"), RED, fade(t, s + 3.6, e))


def scene_fix(img, t, s, e):
    p = t - s
    headline(img, t, ["And shows you the fix."], s, e, y=H * .22, size=80)
    fx = ease_in_out((p - 1.0) / .8)
    code_card(img, t, int(H * .32), fade(t, s, e), highlight=1, fixed=fx)
    if p > 1.9:
        k = back_out((p - 1.9) / .5)
        r = 70 * k
        badge = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(badge)
        cx, cy = W / 2, H * .72
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*GREEN, 255))
        if k > .6:
            d.line((cx - 30, cy, cx - 8, cy + 24, cx + 34, cy - 26), fill=(255, 255, 255, 255), width=12, joint="curve")
        img.alpha_composite(badge)
        text(img, (W / 2, H * .79), "Fixed in seconds.", sf(52, "Semibold"), GREEN, fade(t, s + 2.1, e))


def scene_pack(img, t, s, e):
    p = t - s
    headline(img, t, ["14 dogs.", ("Each guards one part.", GREY)], s, e, y=H * .13, size=80)
    cols, cell = 3, 300
    for i, (name, area, _, _) in enumerate(DOGS[:12]):
        r, c = divmod(i, cols)
        x = W / 2 + (c - 1) * cell
        y = H * .32 + r * 330
        a = fade(t, s + .4 + i * .09, e, fin=.4)
        paste_scaled(img, get_icon(SLUG[name], 400), x, y + (1 - ease_out((p - .4 - i * .09) / .4)) * 40, .5 * (.85 + .15 * a), alpha=a)
        text(img, (x, y + 130), area if area in ("AI", "API", "VAPT") else area.title(), sf(34, "Semibold"), INK, a)
    text(img, (W / 2, H * .94), "+ Web3 and Compliance", sf(34, "Medium"), GREY, fade(t, s + 1.6, e))


def scene_tested(img, t, s, e):
    p = t - s
    k = ease_out((p - .2) / 1.2)
    text(img, (W / 2, H * .30), "Tested on", sf(64, "Semibold"), GREY, fade(t, s, e))
    text(img, (W / 2, H * .38), "248 planted bugs.", sf(96, "Bold"), INK, fade(t, s + .15, e))
    text(img, (W / 2, H * .53), f"{int(245 * k)}", sf(300, "Bold"), TEAL, fade(t, s + .4, e))
    text(img, (W / 2, H * .64), "found.", sf(96, "Bold"), INK, fade(t, s + .6, e))
    text(img, (W / 2, H * .72), "Every critical one.", sf(52, "Medium"), GREY, fade(t, s + 1.2, e))


def scene_cta(img, t, s, e):
    p = t - s
    a = fade(t, s, e + 1, fout=.01)
    paste_scaled(img, get_icon("watchdog", 700), W / 2, H * .27, .42 * (.9 + .1 * ease_out(p / .8)), alpha=a)
    text(img, (W / 2, H * .41), "Watchdog", sf(120, "Bold"), INK, a)
    text(img, (W / 2, H * .465), "Free and open source.", sf(54, "Medium"), GREY, fade(t, s + .3, e + 1, fout=.01))
    ca = fade(t, s + .6, e + 1, fout=.01)
    card(img, (90, int(H * .53), W - 90, int(H * .53) + 220), ca)
    text(img, (W / 2, H * .53 + 70), "Add it to Claude Code:", sf(32, "Semibold"), GREY, ca)
    text(img, (W / 2, H * .53 + 140), "/plugin marketplace add salahu01/watchdog", font(MONO, 30), INK, ca)
    text(img, (W / 2, H * .70), "github.com/salahu01/watchdog", sf(42, "Semibold"), TEAL, fade(t, s + 1.0, e + 1, fout=.01))
    text(img, (W / 2, H * .75), "Link in bio", sf(38, "Medium"), GREY, fade(t, s + 1.2, e + 1, fout=.01))


def frame(f):
    t = f / FPS
    img = base(t)
    for name, s, e in SCENES:
        if s - .05 <= t <= e + .05:
            globals()["scene_" + name](img, t, s, e)
    return img.convert("RGB")


def save(f, d):
    frame(f).save(os.path.join(d, f"{f:04d}.png"))


# ---------- soft soundtrack: warm pad + plucks on each new line ----------

SR = 44100


def soundtrack(path):
    n = SR * SECONDS
    out = np.zeros(n)
    t_all = np.arange(n) / SR

    def add(sig, at, gain):
        s = int(at * SR)
        e = min(n, s + len(sig))
        out[s:e] += sig[:e - s] * gain

    def note(midi):
        return 440 * 2 ** ((midi - 69) / 12)

    def pluck(midi, length=1.6):
        t = np.arange(int(SR * length)) / SR
        f = note(midi)
        s = np.sin(2 * np.pi * f * t) + .35 * np.sin(4 * np.pi * f * t) + .12 * np.sin(6 * np.pi * f * t)
        return s * np.minimum(1, t / .004) * np.exp(-t * 3.2)

    def pad(chord, start, length):
        t = np.arange(int(SR * length)) / SR
        s = sum(np.sin(2 * np.pi * note(m) * t + k) + .5 * np.sin(2 * np.pi * note(m) * 1.003 * t) for k, m in enumerate(chord))
        env = np.minimum(1, t / 1.2) * np.minimum(1, (length - t) / 1.2)
        add(s / len(chord) * env, start, .10)

    # chords: Cmaj9 - Am9 - Fmaj9 - G6, two seconds-ish each, looping
    chords = [[48, 55, 64, 71, 74], [45, 52, 60, 67, 71], [41, 48, 57, 64, 67], [43, 50, 59, 64, 69]]
    span = 3.75
    for k in range(int(SECONDS / span) + 1):
        pad(chords[k % 4], k * span, span + 1.2)
    # gentle pulse: soft kick from the reveal on
    for b in np.arange(8.2, 27, .6):
        tt = np.arange(int(SR * .3)) / SR
        add(np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 12), b, .35)
    # a pluck on each scene / line change
    melody = [76, 79, 83, 81, 79, 76, 74, 79, 84, 83, 79, 76]
    cues = [.1, 2.6, 4.5, 6.4, 8.2, 8.55, 11.0, 14.0, 17.0, 18.0, 19.0, 20.4, 24.4, 25.0, 27.0, 27.6]
    for i, c in enumerate(cues):
        add(pluck(melody[i % len(melody)]), c, .22)
    # sparkle when the bug is caught and when it's fixed
    for c, m in ((14.0, 88), (18.9, 91), (19.0, 95)):
        add(pluck(m, .8), c, .15)
    # soft whoosh into the brand
    w = np.random.default_rng(2).standard_normal(int(SR * .9))
    w = np.convolve(w, np.ones(60) / 60, mode="same") * np.sin(np.linspace(0, np.pi, len(w))) ** 2
    add(w * 3, 7.6, .5)
    # end chord
    add(sum(pluck(m, 3.5) for m in (60, 64, 67, 72, 76)), 27.0, .14)
    out = np.tanh(out * 1.4) * .85
    fl = SR * 2
    out[-fl:] *= np.linspace(1, 0, fl)
    with wave.open(path, "wb") as w_:
        w_.setnchannels(1)
        w_.setsampwidth(2)
        w_.setframerate(SR)
        w_.writeframes((out * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    for slug in ["watchdog"] + list(SLUG.values()):
        icon(slug, 400)
        icon(slug, 700)
    if len(sys.argv) > 1:
        d = os.path.join(OUT, "explainer-frames")
        os.makedirs(d, exist_ok=True)
        for f in map(int, sys.argv[1:]):
            save(f, d)
        sys.exit()
    d = os.path.join(OUT, "explainer-all")
    os.makedirs(d, exist_ok=True)
    with Pool() as pool:
        list(pool.imap_unordered(partial(save, d=d), range(FRAMES), chunksize=8))
    audio = os.path.join(OUT, "explainer.wav")
    soundtrack(audio)
    mp4 = os.path.join(OUT, "watchdog-explainer.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(d, "%04d.png"),
                    "-i", audio, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    print("wrote", mp4)
