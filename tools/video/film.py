"""The directed cut: explainer.py's shots + narrated script, voiceover, captions and ducked music.

    python3 tools/video/film.py                 # -> out/watchdog-film.mp4
    python3 tools/video/film.py 100 400         # preview frames -> out/film-frames/
    VOICE="Ava (Premium)" python3 tools/video/film.py   # any installed `say` voice

The director is SCRIPT: each shot's narration sets how long the shot runs. Shot animations from
explainer.py are time-stretched so their beats land under the line that describes them.
"""
import hashlib
import os
import subprocess
import sys
import wave
from functools import partial
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import explainer as X  # noqa: E402
from reel import OUT, SLUG, ease_in_out, ease_out, icon  # noqa: E402

VOICE = os.environ.get("VOICE", "Daniel")
RATE = os.environ.get("RATE", "182")
LEAD, TAIL = 0.35, 0.55  # silence before / after each line inside its shot

# shot (from explainer.py), narration. Read as one continuous voice.
SCRIPT = [
    ("ship", "You ship fast. Claude writes half your code."),
    ("line", "But one line like this... can quietly leak every user in your database."),
    ("intro", "So we built..."),
    ("brand", "Watchdog. A pack of security dogs that live inside Claude Code."),
    ("watch", "Ask Claude for a new endpoint. Malinois is already watching, "
              "and catches the SQL injection before it ships."),
    ("fix", "Then it shows you exactly how to fix it. One line. Done."),
    ("pack", "Fourteen dogs, each guarding one part of your product. "
             "API, cloud, AI, logins, mobile, databases, and more."),
    ("tested", "Tested on 248 planted bugs, they found 245. Including every critical one."),
    ("cta", "Watchdog is free and open source. One line to install. Link in bio."),
]
DESIGN = {name: (s, e) for name, s, e in X.SCENES}  # each shot's designed timing in explainer.py
SR = 44100
VO_DIR = os.path.join(OUT, "vo")


def vo(line):
    """Synthesize one line (cached by voice+rate+text); returns a mono float array at SR."""
    os.makedirs(VO_DIR, exist_ok=True)
    key = hashlib.sha1(f"{VOICE}|{RATE}|{line}".encode()).hexdigest()[:12]
    wav = os.path.join(VO_DIR, key + ".wav")
    if not os.path.exists(wav):
        aiff = wav[:-4] + ".aiff"
        subprocess.run(["say", "-v", VOICE, "-r", RATE, "-o", aiff, line], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", aiff, "-ar", str(SR), "-ac", "1", wav], check=True)
        os.remove(aiff)
    with wave.open(wav) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768


# ---------- the director: build the timeline from the narration ----------

SHOTS = []  # (name, start, end, vo_start, vo_len, line)
t = 0.0
for name, line in SCRIPT:
    n = len(vo(line)) / SR
    ds, de = DESIGN[name]
    length = max(de - ds, LEAD + n + TAIL)
    SHOTS.append((name, t, t + length, t + LEAD, n, line))
    t += length
TOTAL = t + 0.8
FRAMES = int(TOTAL * X.FPS)


def captions():
    """Split each line into short phrases and time them by character position (no word timings from `say`)."""
    out = []
    for _, _, _, v0, n, line in SHOTS:
        # phrases end at punctuation; long phrases split into balanced halves
        chunks, cur = [], []
        for w in line.replace("...", "…").split():
            cur.append(w)
            if w[-1] in ".,:…":
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)
        out_chunks = []
        while chunks:
            c = chunks.pop(0)
            if len(" ".join(c)) > 26 and len(c) > 1:
                mid = min(range(1, len(c)), key=lambda i: abs(len(" ".join(c[:i])) - len(" ".join(c[i:]))))
                chunks[:0] = [c[:mid], c[mid:]]
            else:
                out_chunks.append(" ".join(c))
        chunks = out_chunks
        total = sum(len(c) + 1 for c in chunks)
        pos = 0
        for c in chunks:
            a = v0 + n * pos / total
            pos += len(c) + 1
            out.append((a, v0 + n * pos / total, c))
    return out


CAPS = captions()


def caption(img, t):
    for a, b, c in CAPS:
        if a <= t < b + .05:
            k = ease_out((t - a) / .12)
            f = X.sf(50, "Bold")
            w = f.getlength(c)
            y = X.H * .9 + (1 - k) * 14
            layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            d.rounded_rectangle((X.W / 2 - w / 2 - 34, y - 46, X.W / 2 + w / 2 + 34, y + 46), 46,
                                fill=(17, 17, 20, int(225 * k)))
            d.text((X.W / 2, y), c, font=f, fill=(255, 255, 255, int(255 * k)), anchor="mm")
            img.alpha_composite(layer)
            return


def frame(f):
    t = f / X.FPS
    img = X.base(t)
    for name, s, e, *_ in SHOTS:
        if s - .05 <= t <= e + .05:
            ds, de = DESIGN[name]
            # stretch the designed shot over the directed length
            k = (de - ds) / (e - s)
            getattr(X, "scene_" + name)(img, ds + (t - s) * k, ds, de)
    caption(img, t)
    if t > TOTAL - .8:
        img.alpha_composite(Image.new("RGBA", img.size, (250, 250, 252, int(255 * ease_in_out((t - TOTAL + .8) / .8)))))
    return img.convert("RGB")


def save(f, d):
    frame(f).save(os.path.join(d, f"{f:04d}.png"))


# ---------- mix: music bed ducked under the voice ----------

def mix(path):
    n = int(SR * TOTAL)
    voice = np.zeros(n)
    for name, line in SCRIPT:
        shot = next(s for s in SHOTS if s[0] == name)
        v = vo(line)
        a = int(shot[3] * SR)
        voice[a:a + len(v)] += v[:n - a]
    music = np.zeros(n)

    def add(sig, at, gain):
        s = int(at * SR)
        e = min(n, s + len(sig))
        if s < n:
            music[s:e] += sig[:e - s] * gain

    note = lambda m: 440 * 2 ** ((m - 69) / 12)

    def pluck(m, length=1.6):
        tt = np.arange(int(SR * length)) / SR
        f = note(m)
        return (np.sin(2 * np.pi * f * tt) + .35 * np.sin(4 * np.pi * f * tt)) * np.minimum(1, tt / .004) * np.exp(-tt * 3.2)

    chords = [[48, 55, 64, 71, 74], [45, 52, 60, 67, 71], [41, 48, 57, 64, 67], [43, 50, 59, 64, 69]]
    span = 3.75
    for k in range(int(TOTAL / span) + 1):
        tt = np.arange(int(SR * (span + 1.2))) / SR
        s = sum(np.sin(2 * np.pi * note(m) * tt + j) + .5 * np.sin(2 * np.pi * note(m) * 1.003 * tt) for j, m in enumerate(chords[k % 4]))
        env = np.minimum(1, tt / 1.2) * np.minimum(1, (span + 1.2 - tt) / 1.2)
        add(s / 5 * env, k * span, .12)
    brand = next(s for s in SHOTS if s[0] == "brand")[1]
    for b in np.arange(brand, TOTAL - 2, .6):  # soft pulse from the reveal on
        tt = np.arange(int(SR * .3)) / SR
        add(np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-tt * 30)) / SR) * np.exp(-tt * 12), b, .45)
    melody = [76, 79, 83, 81, 79, 76, 74, 79, 84]
    for i, (name, s, *_r) in enumerate(SHOTS):
        add(pluck(melody[i % len(melody)]), s, .28)
    for name, s, e, *_r in SHOTS:  # sparkle on the catch and the fix
        if name in ("watch", "fix"):
            ds, de = DESIGN[name]
            cue = {"watch": 3.0, "fix": 1.9}[name]
            add(pluck(91, .8), s + cue * (e - s) / (de - ds), .2)
    add(sum(pluck(m, 3.5) for m in (60, 64, 67, 72, 76)), SHOTS[-1][1], .16)
    # duck: music drops to 30% while the voice speaks, with smooth release
    env = np.convolve(np.abs(voice) > .01, np.ones(SR // 5) / (SR // 5), mode="same")
    music *= 1 - .7 * np.clip(env * 3, 0, 1)
    out = np.tanh(voice * 1.25 + music * .9) * .92
    fl = SR
    out[-fl:] *= np.linspace(1, 0, fl)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    for slug in ["watchdog"] + list(SLUG.values()):
        icon(slug, 400)
        icon(slug, 700)
    for name, s, e, v0, n, line in SHOTS:
        print(f"{s:5.1f}-{e:5.1f}  {name:7}  {line}")
    if len(sys.argv) > 1:
        d = os.path.join(OUT, "film-frames")
        os.makedirs(d, exist_ok=True)
        for f in map(int, sys.argv[1:]):
            save(f, d)
        sys.exit()
    d = os.path.join(OUT, "film-all")
    os.makedirs(d, exist_ok=True)
    for old in os.listdir(d):
        os.remove(os.path.join(d, old))
    with Pool() as pool:
        list(pool.imap_unordered(partial(save, d=d), range(FRAMES), chunksize=8))
    audio = os.path.join(OUT, "film.wav")
    mix(audio)
    mp4 = os.path.join(OUT, "watchdog-film.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(X.FPS), "-i", os.path.join(d, "%04d.png"),
                    "-i", audio, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    print("wrote", mp4, f"({TOTAL:.1f}s)")
