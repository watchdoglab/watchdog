"""Render the Watchdog launch reel (1080x1920, 30 fps, ~24 s, with a synthesized soundtrack).

    python3 tools/video/reel.py            # full render -> out/watchdog-reel.mp4
    python3 tools/video/reel.py 30 200 400 # just these frames -> out/reel-frames/

Everything is cut to a 120 BPM grid: one beat = 15 frames. Needs rsvg-convert and ffmpeg.
Run tools/brand/gen_logos.py first; the dogs come from their icon.svg files.
"""
import math
import os
import random
import subprocess
import sys
import wave
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "out")
CACHE = os.path.join(OUT, "reel-cache")
W, H, FPS, BPM = 1080, 1920, 30, 120
BEAT = FPS * 60 // BPM          # 15 frames
BEATS = 48
FRAMES = BEATS * BEAT

FONTS = "/System/Library/Fonts/Supplemental/"
COND = FONTS + "DIN Condensed Bold.ttf"
DIN = FONTS + "DIN Alternate Bold.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"
TEAL = (45, 212, 191)
RED = (255, 59, 76)

DOGS = [  # name, area, three things it checks, accent
    ("MALINOIS", "VAPT", "CODE  /  WEB  /  APK  /  IPA", (45, 212, 191)),
    ("HUSKY", "CLOUD", "TERRAFORM  /  K8S  /  CI", (125, 211, 252)),
    ("COLLIE", "AI", "PROMPTS  /  AGENTS  /  MCP", (167, 139, 250)),
    ("BLOODHOUND", "API", "REST  /  GRAPHQL  /  BOLA", (245, 158, 11)),
    ("BEAGLE", "PRIVACY", "PII  /  LOGS  /  CONSENT", (251, 146, 60)),
    ("ROTTWEILER", "SUPPLY CHAIN", "LOCKFILES  /  SBOM  /  DEPS", (217, 119, 6)),
    ("DOBERMAN", "AUTH", "LOGIN  /  OAUTH  /  MFA", (239, 68, 68)),
    ("SHEPHERD", "MOBILE", "ANDROID  /  IOS  /  FLUTTER", (34, 197, 94)),
    ("DACHSHUND", "DATABASE", "SQL  /  RLS  /  FIREBASE", (225, 29, 72)),
    ("AKITA", "SECRETS", "FIND  /  ROTATE  /  BLOCK", (59, 130, 246)),
    ("POINTER", "FRONTEND", "XSS  /  CSP  /  DOM", (234, 179, 8)),
    ("SAINT BERNARD", "INCIDENT RESPONSE", "TIMELINE  /  BLAST RADIUS", (239, 68, 68)),
    ("SHIBA", "WEB3", "SOLIDITY  /  DEFI  /  AUDIT", (249, 115, 22)),
    ("PYRENEES", "COMPLIANCE", "SOC 2  /  ISO 27001  /  PCI", (203, 213, 225)),
]
SLUG = {d[0]: d[0].lower().replace(" ", "") for d in DOGS}

CODE = [
    ("const user = await db.query(", None),
    ("  `SELECT * FROM users WHERE id=${id}`);", "SQL INJECTION"),
    ("const STRIPE = 'sk_live_51Hx…';", "LEAKED KEY"),
    ("el.innerHTML = params.get('msg');", "XSS"),
    ("app.post('/run', (req, res) =>", None),
    ("  res.send(eval(req.body.expr)));", "RCE"),
    ("jwt.decode(token); // trusted", "AUTH BYPASS"),
    ("bucket.acl = 'public-read';", "DATA LEAK"),
]


# ---------- helpers ----------

def ease_out(t):
    t = min(1, max(0, t))
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = min(1, max(0, t))
    return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2


def back_out(t, s=2.2):
    t = min(1, max(0, t)) - 1
    return 1 + (s + 1) * t ** 3 + s * t ** 2


_fonts = {}


def font(path, size):
    size = max(1, int(size))
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def text_size(txt, f, spacing=0):
    w = sum(f.getlength(c) for c in txt) + spacing * (len(txt) - 1)
    a, d = f.getmetrics()
    return w, a + d


def draw_text(layer, xy, txt, f, fill, spacing=0, anchor="mm", reveal=1.0):
    """Tracked text; `reveal` 0..1 shows letters one by one."""
    d = ImageDraw.Draw(layer)
    w, h = text_size(txt, f, spacing)
    x, y = xy
    if anchor[0] == "m":
        x -= w / 2
    n = math.ceil(len(txt) * reveal)
    for c in txt[:n]:
        d.text((x, y), c, font=f, fill=fill, anchor="l" + anchor[1])
        x += f.getlength(c) + spacing


def glow(layer, radius=18, strength=2):
    """Bloom: blurred copy added under the sharp layer."""
    b = layer.filter(ImageFilter.GaussianBlur(radius))
    out = b
    for _ in range(strength - 1):
        out = Image.alpha_composite(out, b)
    return Image.alpha_composite(out, layer)


def rgba(c, a=255):
    return (*c, int(a))


def new():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def chroma(img, px):
    """RGB split for hits and glitches."""
    if px < 1:
        return img
    r, g, b, a = img.split()
    r = ImageChops.offset(r, int(px), 0)
    b = ImageChops.offset(b, -int(px), 0)
    return Image.merge("RGBA", (r, g, b, a))


def shake(img, amt, seed):
    if amt < .5:
        return img
    rng = random.Random(seed)
    return ImageChops.offset(img, rng.randint(-int(amt), int(amt)), rng.randint(-int(amt), int(amt)))


# ---------- assets ----------

def icon(slug, size):
    """Dog icon cut to its dial (no rounded tile), cached as PNG."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{slug}-{size}.png")
    if not os.path.exists(path):
        svg = os.path.join(ROOT, "assets/logo.svg" if slug == "watchdog" else f"plugins/{slug}/assets/icon.svg")
        raw = path + ".raw.png"
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", raw, svg], check=True)
        im = Image.open(raw).convert("RGBA")
        mask = Image.new("L", im.size, 0)
        r = size * 478 / 1024
        ImageDraw.Draw(mask).ellipse((size / 2 - r, size / 2 - r, size / 2 + r, size / 2 + r), fill=255)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), mask.filter(ImageFilter.GaussianBlur(2))))
        im.save(path)
        os.remove(raw)
    return Image.open(path)


_icons = {}


def get_icon(slug, size):
    key = (slug, size)
    if key not in _icons:
        _icons[key] = icon(slug, size)
    return _icons[key]


def paste_scaled(dst, im, cx, cy, scale, alpha=1.0, rot=0):
    if scale <= 0.01 or alpha <= 0.01:
        return
    w = max(1, int(im.width * scale))
    s = im.resize((w, w), Image.LANCZOS)
    if rot:
        s = s.rotate(rot, Image.BICUBIC, expand=True)
    if alpha < 1:
        s.putalpha(s.getchannel("A").point(lambda v: int(v * alpha)))
    dst.alpha_composite(s, (int(cx - s.width / 2), int(cy - s.height / 2)))


# ---------- background ----------

def background(f, accent, energy=0.0):
    """Black field, faint grid that drifts, accent vignette, film grain."""
    img = Image.new("RGBA", (W, H), (3, 5, 8, 255))
    v = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(v)
    a = 70 + 90 * energy
    for i in range(14, 0, -1):
        r = 140 * i
        d.ellipse((W / 2 - r, H * .42 - r, W / 2 + r, H * .42 + r), fill=rgba(accent, a / 14))
    img = Image.alpha_composite(img, v.filter(ImageFilter.GaussianBlur(60)))
    g = new()
    d = ImageDraw.Draw(g)
    off = (f * 2) % 90
    for x in range(-90, W + 90, 90):
        d.line((x + off * 0, 0, x, H), fill=rgba(accent, 16), width=1)
    for y in range(-90, H + 90, 90):
        d.line((0, y + off, W, y + off), fill=rgba(accent, 16), width=1)
    img = Image.alpha_composite(img, g)
    return img


def grain(img, f):
    rng = np.random.default_rng(f)
    n = rng.integers(0, 22, (H // 2, W // 2), dtype=np.uint8)
    n = Image.fromarray(n, "L").resize((W, H), Image.NEAREST)
    noise = Image.merge("RGBA", (n, n, n, Image.new("L", (W, H), 26)))
    return Image.alpha_composite(img, noise)


def scanlines(img, f, alpha=22):
    s = new()
    d = ImageDraw.Draw(s)
    for y in range(f % 4, H, 4):
        d.line((0, y, W, y), fill=(0, 0, 0, alpha))
    return Image.alpha_composite(img, s)


def letterbox_hud(img, f, label, accent, idx=None):
    """Thin HUD frame: corner brackets, timecode, label — the showreel signature."""
    h = new()
    d = ImageDraw.Draw(h)
    c, m, L = rgba(accent, 170), 54, 70
    for x, y, sx, sy in ((m, m, 1, 1), (W - m, m, -1, 1), (m, H - m, 1, -1), (W - m, H - m, -1, -1)):
        d.line((x, y, x + sx * L, y), fill=c, width=4)
        d.line((x, y, x, y + sy * L), fill=c, width=4)
    fm = font(MONO, 26)
    sec = f / FPS
    d.text((m + 6, m + 92), f"REC ● {int(sec // 60):02d}:{sec % 60:05.2f}", font=fm, fill=rgba(accent, 200))
    d.text((W - m - 6, m + 92), label, font=fm, fill=rgba(accent, 200), anchor="ra")
    if idx is not None:
        d.text((W - m - 6, H - m - 92), idx, font=fm, fill=rgba(accent, 200), anchor="rs")
    d.text((m + 6, H - m - 92), "WATCHDOG // SECURITY DOGS", font=fm, fill=rgba(accent, 140), anchor="ls")
    return Image.alpha_composite(img, h)


# ---------- scenes ----------

def scene_hook(f):
    """Beats 0-4: 'YOUR CODE' ... 'HAS HOLES.' slam."""
    b = f / BEAT
    img = background(f, RED, energy=.3 if b < 2 else .9)
    # code rain behind
    rain = new()
    d = ImageDraw.Draw(rain)
    fm = font(MONO, 30)
    rng = random.Random(7)
    for i in range(60):
        x = rng.randint(0, W)
        y = (rng.randint(0, H) + f * rng.randint(6, 22)) % (H + 200) - 100
        d.text((x, y), rng.choice(["eval(", "SELECT *", "sk_live_", "innerHTML", "0.0.0.0/0", "chmod 777", "admin:admin", "jwt.decode"]),
               font=fm, fill=rgba(RED if b >= 2 else (90, 100, 120), 70))
    img = Image.alpha_composite(img, rain.filter(ImageFilter.GaussianBlur(1)))
    t = new()
    big = font(COND, 250)
    k = ease_out((f - 2) / 8)
    draw_text(t, (W / 2, H * .40), "YOUR CODE", big, rgba((240, 244, 250), 255 * k), spacing=6)
    if b >= 2:
        hit = (f - 2 * BEAT)
        s = 1 + 0.6 * max(0, 1 - hit / 4)
        t2 = new()
        draw_text(t2, (W / 2, H * .55), "HAS HOLES.", font(COND, int(250 * s)), rgba(RED), spacing=6)
        t = Image.alpha_composite(t, glow(t2, 24, 2))
        # warning stripes
        st = new()
        d = ImageDraw.Draw(st)
        y0 = H * .66
        for x in range(-200, W + 200, 60):
            xx = x + (f * 9) % 60
            d.polygon([(xx, y0), (xx + 30, y0), (xx + 10, y0 + 40), (xx - 20, y0 + 40)], fill=rgba(RED, 200))
        img = Image.alpha_composite(img, st)
    img = Image.alpha_composite(img, t)
    if b >= 2:
        hit = f - 2 * BEAT
        img = chroma(img, 22 * max(0, 1 - hit / 6))
        img = shake(img, 30 * max(0, 1 - hit / 8), f)
        if hit < 2:
            img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (255, 255, 255, 180 - 90 * hit)))
    return letterbox_hud(img, f, "THREAT DETECTED" if b >= 2 else "SCANNING", RED if b >= 2 else (140, 150, 170))


def scene_code(f0):
    """Beats 4-8: an editor where each beat flags a real-world vuln."""
    f = f0 - 4 * BEAT
    img = background(f0, (30, 40, 60), .2)
    panel = new()
    d = ImageDraw.Draw(panel)
    x0, y0, x1 = 60, 520, W - 60
    lh = 104
    y1 = y0 + 110 + lh * len(CODE)
    intro = ease_out(f / 8)
    off = (1 - intro) * 300
    d.rounded_rectangle((x0, y0 + off, x1, y1 + off), 28, fill=(10, 14, 22, 235), outline=(60, 72, 92, 255), width=3)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 34 + i * 40, y0 + 34 + off, x0 + 58 + i * 40, y0 + 58 + off), fill=c)
    d.text((W / 2, y0 + 46 + off), "server.js", font=font(MONO, 28), fill=(140, 150, 170), anchor="mm")
    fm = font(MONO, 29)
    flagged = [i for i, (_, tag) in enumerate(CODE) if tag]
    n_on = min(len(flagged), max(0, int((f - 6) / (BEAT * 4 / len(flagged) * .9)) + 1)) if f > 6 else 0
    tags = new()
    td = ImageDraw.Draw(tags)
    for i, (line, tag) in enumerate(CODE):
        y = y0 + 110 + i * lh + off
        on = tag and flagged.index(i) < n_on
        if on:
            k = flagged.index(i)
            age = f - 6 - k * (BEAT * 4 / len(flagged) * .9)
            d.rectangle((x0 + 3, y - 10, x1 - 3, y + lh - 30), fill=(RED[0], RED[1], RED[2], 60))
            d.rectangle((x0 + 3, y - 10, x0 + 12, y + lh - 30), fill=rgba(RED))
            pw = text_size(tag, font(DIN, 30), 4)[0] + 44
            px = x1 - pw - 20 + (1 - back_out(age / 6)) * 400
            td.rounded_rectangle((px, y - 58, px + pw, y - 10), 24, fill=rgba(RED))
            draw_text(tags, (px + pw / 2, y - 34), tag, font(DIN, 30), (255, 255, 255, 255), 4)
        d.text((x0 + 40, y + 24), f"{i + 1:>2}", font=fm, fill=(70, 80, 100), anchor="lm")
        d.text((x0 + 100, y + 24), line, font=fm, fill=(255, 210, 214) if on else (200, 210, 225), anchor="lm")
    img = Image.alpha_composite(img, panel)
    img = Image.alpha_composite(img, glow(tags, 14, 1))
    # scanning beam
    sy = y0 + (y1 - y0) * ((f % BEAT) / BEAT) + off
    beam = new()
    ImageDraw.Draw(beam).rectangle((x0, sy - 3, x1, sy + 3), fill=rgba(TEAL, 230))
    img = Image.alpha_composite(img, glow(beam, 20, 2))
    t = new()
    draw_text(t, (W / 2, 300), f"{n_on} CRITICAL" if n_on else "SCANNING…", font(COND, 150), rgba(RED if n_on else (220, 230, 240)), 4)
    draw_text(t, (W / 2, 400), "BEFORE YOU EVEN SHIP", font(DIN, 40), (150, 160, 180, 255), 10)
    img = Image.alpha_composite(img, t)
    return letterbox_hud(img, f0, "STATIC ANALYSIS", RED)


def dial(layer, cx, cy, r, progress, color, f):
    d = ImageDraw.Draw(layer)
    for i in range(60):
        if i / 60 > progress:
            break
        a = math.radians(i * 6 - 90)
        r0 = r - (34 if i % 5 == 0 else 18)
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r * math.cos(a), cy + r * math.sin(a)),
               fill=rgba(color), width=8 if i % 5 == 0 else 4)
    if progress >= 1:
        d.ellipse((cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30), outline=rgba(color, 90), width=3)


def scene_reveal(f0):
    """Beats 8-12: dial draws on, logo scales in, wordmark resolves. Riser into the drop."""
    f = f0 - 8 * BEAT
    p = f / (4 * BEAT)
    img = background(f0, (40, 60, 80), .25 + .5 * p)
    cx, cy, r = W / 2, H * .40, 400
    lay = new()
    dial(lay, cx, cy, r, ease_in_out(p * 1.6), (230, 240, 252), f0)
    logo = get_icon("watchdog", 860)
    sc = .55 + .45 * ease_out((p - .25) / .5)
    paste_scaled(lay, logo, cx, cy, sc * .95, alpha=ease_out((p - .2) / .3))
    # radar sweep
    sw = new()
    a = 2 * math.pi * p * 2 - math.pi / 2
    d = ImageDraw.Draw(sw)
    for k in range(40):
        aa = a - k * .03
        d.line((cx, cy, cx + (r - 40) * math.cos(aa), cy + (r - 40) * math.sin(aa)), fill=rgba(TEAL, 140 - k * 3.4), width=10)
    lay = Image.alpha_composite(lay, sw.filter(ImageFilter.GaussianBlur(4)))
    img = Image.alpha_composite(img, glow(lay, 16, 1))
    t = new()
    draw_text(t, (W / 2, H * .72), "WATCHDOG", font(COND, 230), (244, 248, 252, 255), 22, reveal=ease_out((p - .45) / .35))
    draw_text(t, (W / 2, H * .79), "SECURITY DOGS FOR YOUR CODE", font(DIN, 42), rgba(TEAL), 10, reveal=ease_out((p - .7) / .25))
    img = Image.alpha_composite(img, glow(t, 12, 1))
    if f0 >= 12 * BEAT - 3:
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (f0 - (12 * BEAT - 3)) / 3))))
    return letterbox_hud(img, f0, "DEPLOYING PACK", TEAL)


def scene_dogs(f0):
    """Beats 12-26: the drop. One dog per beat, alternating layouts, wipe transitions."""
    f = f0 - 12 * BEAT
    i, lf = divmod(f, BEAT)
    name, area, things, acc = DOGS[i]
    slug = SLUG[name]
    img = background(f0, acc, .9 - .5 * lf / BEAT)
    # giant ghost number
    gh = new()
    draw_text(gh, (W / 2 + (lf * 6 if i % 2 else -lf * 6), H * .50), f"{i + 1:02d}", font(COND, 900), rgba(acc, 26))
    img = Image.alpha_composite(img, gh)
    up = i % 2 == 0
    icy = H * (.34 if up else .62)
    ty = H * (.68 if up else .22)
    lay = new()
    # rings that burst from the icon on the hit
    d = ImageDraw.Draw(lay)
    for k in range(3):
        rr = 380 + (lf * 28 + k * 70)
        d.ellipse((W / 2 - rr, icy - rr, W / 2 + rr, icy + rr), outline=rgba(acc, max(0, 160 - lf * 11 - k * 40)), width=6)
    sc = 1.25 - .25 * back_out(lf / 6) + .02 * lf / BEAT
    paste_scaled(lay, get_icon(slug, 760), W / 2, icy, sc, rot=(1 - ease_out(lf / 6)) * (-12 if up else 12))
    img = Image.alpha_composite(img, glow(lay, 22, 1))
    t = new()
    size = 210 if len(name) <= 8 else 160 if len(name) <= 10 else 140
    slide = (1 - ease_out(lf / 5)) * (220 if up else -220)
    draw_text(t, (W / 2 + slide, ty), name, font(COND, size), (250, 252, 255, 255), 10)
    pw = text_size(area, font(DIN, 44), 8)[0] + 70
    k = ease_out((lf - 2) / 4)
    py = ty + size * .62
    ImageDraw.Draw(t).rounded_rectangle((W / 2 - pw / 2 * k, py - 34, W / 2 + pw / 2 * k, py + 34), 34, fill=rgba(acc))
    if k > .6:
        draw_text(t, (W / 2, py + 2), area, font(DIN, 44), (5, 8, 12, 255), 8)
    draw_text(t, (W / 2, py + 92), things, font(DIN, 38), rgba(acc, 230), 6, reveal=ease_out((lf - 4) / 6))
    img = Image.alpha_composite(img, glow(t, 10, 1))
    # hit: flash + chroma + wipe from previous dog's colour
    if lf < 4:
        img = chroma(img, 18 * (1 - lf / 4))
        img = shake(img, 16 * (1 - lf / 4), f0)
    if lf < 3 and i > 0:
        prev = DOGS[i - 1][3]
        wipe = new()
        x = W * ease_in_out(lf / 3)
        ImageDraw.Draw(wipe).polygon([(x - 300, 0), (W + 400, 0), (W + 400, H), (x - 700, H)], fill=rgba(prev, 255))
        img = Image.alpha_composite(img, wipe)
    return letterbox_hud(img, f0, f"DOG {i + 1:02d} / 14", acc, idx=f"{area}")


def grid_pos(i):
    rows = [4, 4, 4, 2]
    r, c = 0, i
    while c >= rows[r]:
        c -= rows[r]
        r += 1
    n = rows[r]
    cell = 236
    x = W / 2 + (c - (n - 1) / 2) * cell
    y = H * .30 + r * cell
    return x, y


def scene_pack(f0):
    """Beats 26-32: all 14 fly into formation. '14 DOGS.' / 'ONE PACK.'"""
    f = f0 - 26 * BEAT
    p = f / (6 * BEAT)
    img = background(f0, TEAL, .5)
    lay = new()
    rng = random.Random(3)
    for i, (name, _, _, acc) in enumerate(DOGS):
        gx, gy = grid_pos(i)
        a = rng.uniform(0, 2 * math.pi)
        sx, sy = W / 2 + 700 * math.cos(a), H * .4 + 700 * math.sin(a)
        k = back_out(max(0, f - i * 1.2) / 16, 1.4)
        x, y = sx + (gx - sx) * k, sy + (gy - sy) * k
        bob = 6 * math.sin(f / 6 + i)
        paste_scaled(lay, get_icon(SLUG[name], 400), x, y + bob, .52, alpha=min(1, max(.15, (f - i * 1.2 + 3) / 5)))
    img = Image.alpha_composite(img, glow(lay, 14, 1))
    t = new()
    b = f / BEAT
    if b >= 2:
        k = back_out((f - 2 * BEAT) / 6)
        draw_text(t, (W / 2, H * .80), "14 DOGS.", font(COND, int(200 * k)), (250, 252, 255, 255), 12)
    if b >= 4:
        k = back_out((f - 4 * BEAT) / 6)
        draw_text(t, (W / 2, H * .89), "ONE PACK.", font(COND, int(200 * k)), rgba(TEAL), 12)
    img = Image.alpha_composite(img, glow(t, 14, 1))
    hit = (f - 2 * BEAT) if b < 4 else (f - 4 * BEAT)
    if b >= 2 and hit < 4:
        img = chroma(img, 14 * (1 - hit / 4))
    return letterbox_hud(img, f0, "PACK ASSEMBLED", TEAL)


def scene_stats(f0):
    """Beats 32-38: honest benchmark numbers, counted up."""
    f = f0 - 32 * BEAT
    img = background(f0, TEAL, .4)
    t = new()
    d = ImageDraw.Draw(t)
    k = ease_out(f / 30)
    found = int(245 * k)
    draw_text(t, (W / 2, H * .30), "BENCHMARKED", font(DIN, 50), rgba(TEAL), 14)
    draw_text(t, (W / 2, H * .43), f"{found}", font(COND, 420), (250, 252, 255, 255), 6)
    draw_text(t, (W / 2, H * .535), "/ 248 PLANTED BUGS FOUND", font(DIN, 52), (200, 210, 225, 255), 6)
    # progress bar
    bw = 760
    d.rounded_rectangle((W / 2 - bw / 2, H * .585, W / 2 + bw / 2, H * .585 + 18), 9, fill=(30, 40, 50, 255))
    d.rounded_rectangle((W / 2 - bw / 2, H * .585, W / 2 - bw / 2 + bw * k * 245 / 248, H * .585 + 18), 9, fill=rgba(TEAL))
    for j, (big, small) in enumerate((("14", "BENCHES"), ("3", "MODELS"), ("59/59", "CRITICALS"))):
        kk = back_out((f - 2 * BEAT - j * 5) / 8)
        if kk <= 0:
            continue
        x = W / 2 + (j - 1) * 340
        draw_text(t, (x, H * .69), big, font(COND, int(170 * kk)), rgba(TEAL), 4)
        draw_text(t, (x, H * .75), small, font(DIN, 34), (180, 190, 205, 255), 5)
    draw_text(t, (W / 2, H * .82), "OPUS 5.5 · ONE RUN PER BENCH", font(MONO, 26), (110, 120, 140, 255), 2)
    img = Image.alpha_composite(img, glow(t, 12, 1))
    return letterbox_hud(img, f0, "RESULTS", TEAL)


TYPED = ["/plugin marketplace add salahu01/watchdog", "/plugin install malinois@watchdog"]


def scene_cta(f0):
    """Beats 38-48: type the install, then the end card."""
    f = f0 - 38 * BEAT
    img = background(f0, TEAL, .35)
    if f < 5 * BEAT:
        p = new()
        d = ImageDraw.Draw(p)
        x0, y0, x1, y1 = 60, 640, W - 60, 1180
        k = ease_out(f / 8)
        d.rounded_rectangle((x0, y0 + (1 - k) * 200, x1, y1 + (1 - k) * 200), 28, fill=(8, 12, 18, 240), outline=rgba(TEAL, 160), width=3)
        d.text((x0 + 40, y0 + 50), "claude", font=font(MONO, 30), fill=rgba(TEAL))
        cps = 2.4  # characters per frame
        y = y0 + 150
        used = 0
        for line in TYPED:
            n = int(max(0, f * cps - used))
            shown = line[:n]
            d.text((x0 + 40, y), "> " + shown, font=font(MONO, 34), fill=(235, 240, 248))
            if n < len(line) and n > 0 or (line is TYPED[-1] and n >= len(line)):
                if (f // 8) % 2 == 0:
                    cw = font(MONO, 34).getlength("> " + shown)
                    d.rectangle((x0 + 44 + cw, y + 4, x0 + 64 + cw, y + 42), fill=rgba(TEAL))
            used += len(line) + 8
            y += 90
            if n >= len(line):
                d.text((x0 + 40, y), "✓ done", font=font(MONO, 30), fill=rgba(TEAL))
                y += 90
        img = Image.alpha_composite(img, glow(p, 10, 1))
        t = new()
        draw_text(t, (W / 2, 470), "TWO LINES.", font(COND, 190), (250, 252, 255, 255), 8)
        draw_text(t, (W / 2, 1330), "INSIDE CLAUDE CODE", font(DIN, 48), rgba(TEAL), 12)
        img = Image.alpha_composite(img, t)
        return letterbox_hud(img, f0, "INSTALL", TEAL)
    # end card
    e = f - 5 * BEAT
    p = e / (5 * BEAT)
    lay = new()
    dial(lay, W / 2, H * .36, 330, 1, (230, 240, 252), f0)
    paste_scaled(lay, get_icon("watchdog", 700), W / 2, H * .36, back_out(e / 10) * .95)
    img = Image.alpha_composite(img, glow(lay, 16, 1))
    t = new()
    draw_text(t, (W / 2, H * .62), "WATCHDOG", font(COND, 220), (250, 252, 255, 255), 22, reveal=ease_out(e / 10))
    draw_text(t, (W / 2, H * .685), "SECURITY THAT WATCHES WHILE YOU BUILD", font(DIN, 38), rgba(TEAL), 6, reveal=ease_out((e - 6) / 12))
    k = ease_out((e - 14) / 8)
    pw = 700
    ImageDraw.Draw(t).rounded_rectangle((W / 2 - pw / 2, H * .75 - 44, W / 2 + pw / 2, H * .75 + 44), 44,
                                         outline=rgba(TEAL, 255 * k), width=4, fill=rgba((6, 32, 29), 230 * k))
    draw_text(t, (W / 2, H * .75), "OPEN SOURCE  /  LINK IN BIO", font(DIN, 38), rgba(TEAL, 255 * k), 6)
    draw_text(t, (W / 2, H * .81), "github.com/salahu01/watchdog", font(MONO, 34), (170, 180, 195, int(255 * k)), 0)
    # pack strip
    for i, (name, *_ ) in enumerate(DOGS):
        kk = ease_out((e - 20 - i) / 6)
        paste_scaled(t, get_icon(SLUG[name], 400), W / 2 + (i - 6.5) * 68, H * .875, .16 * kk)
    img = Image.alpha_composite(img, glow(t, 10, 1))
    if p > .85:
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (0, 0, 0, int(255 * (p - .85) / .15))))
    return letterbox_hud(img, f0, "END", TEAL)


def frame(f):
    b = f / BEAT
    if b < 4:
        img = scene_hook(f)
    elif b < 8:
        img = scene_code(f)
    elif b < 12:
        img = scene_reveal(f)
    elif b < 26:
        img = scene_dogs(f)
    elif b < 32:
        img = scene_pack(f)
    elif b < 38:
        img = scene_stats(f)
    else:
        img = scene_cta(f)
    img = scanlines(img, f)
    img = grain(img, f)
    return img.convert("RGB")


def save(f, d):
    frame(f).save(os.path.join(d, f"{f:04d}.png"))


# ---------- soundtrack ----------

SR = 44100


def soundtrack(path):
    n = int(SR * FRAMES / FPS)
    out = np.zeros(n)
    spb = SR * 60 / BPM
    rng = np.random.default_rng(1)

    def at(beat):
        return int(beat * spb)

    def add(sig, beat, gain=1.0):
        s = at(beat)
        e = min(n, s + len(sig))
        out[s:e] += sig[:e - s] * gain

    def env(length, attack=.002, decay=.2):
        t = np.arange(int(SR * length)) / SR
        return np.minimum(1, t / attack) * np.exp(-t / decay)

    def kick():
        t = np.arange(int(SR * .45)) / SR
        f = 45 + 120 * np.exp(-t * 28)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(.45, .001, .16)

    def hat(length=.05):
        return rng.standard_normal(int(SR * length)) * env(length, .0005, .012) * .35

    def snare():
        t = np.arange(int(SR * .25)) / SR
        return (rng.standard_normal(len(t)) * .6 + np.sin(2 * np.pi * 190 * t) * .5) * env(.25, .001, .06)

    def impact():
        t = np.arange(int(SR * 2.2)) / SR
        boom = np.sin(2 * np.pi * np.cumsum(32 + 60 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.6)
        crash = rng.standard_normal(len(t)) * np.exp(-t * 3) * .25
        return boom + crash

    def whoosh(length=.35):
        x = rng.standard_normal(int(SR * length))
        x = np.convolve(x, np.ones(30) / 30, mode="same")
        e = np.sin(np.linspace(0, np.pi, len(x))) ** 2
        return x * e * 1.6

    def riser(beats):
        L = int(beats * spb)
        t = np.arange(L) / SR
        noise = rng.standard_normal(L)
        sweep = np.sin(2 * np.pi * np.cumsum(np.linspace(200, 1800, L)) / SR) * .25
        return (noise * .3 + sweep) * np.linspace(0, 1, L) ** 2.2

    def bass(beat, beats, note):
        L = int(beats * spb)
        t = np.arange(L) / SR
        f = 55 * 2 ** (note / 12)
        sig = np.tanh(2.2 * np.sin(2 * np.pi * f * t)) * .5
        pump = 1 - .85 * np.exp(-((t * BPM / 60) % 1) * 7)  # sidechain feel
        add(sig * pump, beat, .55)

    def blip(beat, freq, length=.08, gain=.25):
        t = np.arange(int(SR * length)) / SR
        add(np.sign(np.sin(2 * np.pi * freq * t)) * env(length, .001, .03), beat, gain)

    # hook: tension pulse then hit
    for b in (0, .5, 1, 1.5):
        blip(b, 880 if b % 1 == 0 else 660, gain=.18)
    add(impact(), 2, .9)
    add(kick(), 2, 1.0)
    # code scene: half-time kick, alert blips on each flag
    for b in range(4, 8):
        add(kick(), b, .8)
        add(hat(), b + .5)
    for k in range(5):
        blip(4 + .4 + k * .72, 1200, gain=.2)
    # reveal: riser into the drop
    add(riser(4), 8, .9)
    for b in np.arange(8, 12, .5):
        add(hat(.03), b, .6)
    # drop: four-on-the-floor, snares on 2 & 4, offbeat hats, rolling bass, whoosh per dog
    progression = [0, 0, 3, 3, 5, 5, -2, -2]
    for b in range(12, 38):
        add(kick(), b, 1.0)
        add(hat(), b + .5, 1.0)
        add(hat(.02), b + .25, .4)
        add(hat(.02), b + .75, .4)
        if b % 2 == 1:
            add(snare(), b, .55)
        bass(b, 1, progression[(b - 12) // 2 % len(progression)])
    for b in range(12, 26):
        add(whoosh(), b - .35, .5)
    add(impact(), 12, 1.0)
    add(impact(), 26, .8)
    add(impact(), 28, .5)
    add(impact(), 30, .7)
    # stats: counting ticks
    for k in range(40):
        blip(32 + k * .05, 1500 + k * 20, .02, .08)
    # CTA: typing clicks, then end hit
    for k in range(int(5 * spb / SR * FPS * 2.4 / 2)):
        if rng.random() < .8:
            add(hat(.015), 38 + k * 2 / 2.4 / BEAT, .5)
    add(riser(1), 42, .5)
    add(impact(), 43, 1.0)
    for b in range(43, 47):
        add(kick(), b, .5)
    # master: gentle compression + fade
    out = np.tanh(out * 1.1)
    fade = np.ones(n)
    fl = int(SR * 1.2)
    fade[-fl:] = np.linspace(1, 0, fl)
    out *= fade * .9
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for slug in ["watchdog"] + list(SLUG.values()):
        for s in (860, 760, 700, 400):
            icon(slug, s)
    if len(sys.argv) > 1:
        d = os.path.join(OUT, "reel-frames")
        os.makedirs(d, exist_ok=True)
        for f in map(int, sys.argv[1:]):
            save(f, d)
            print("frame", f)
        sys.exit()
    d = os.path.join(OUT, "reel-all")
    os.makedirs(d, exist_ok=True)
    with Pool() as pool:
        for k, _ in enumerate(pool.imap_unordered(lambda_f := __import__("functools").partial(save, d=d), range(FRAMES))):
            if k % 60 == 0:
                print(f"{k}/{FRAMES}", flush=True)
    audio = os.path.join(OUT, "reel.wav")
    soundtrack(audio)
    mp4 = os.path.join(OUT, "watchdog-reel.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(d, "%04d.png"),
                    "-i", audio, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    print("wrote", mp4)
