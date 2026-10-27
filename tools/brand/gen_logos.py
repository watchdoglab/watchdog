"""Generate the Watchdog and Malinois logos as low-poly faceted vector marks.

    python3 tools/brand/gen_logos.py

Writes assets/logo.svg and plugins/malinois/assets/icon.svg.
"""
import math
import os
import random

import numpy as np
from scipy.spatial import Delaunay

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Malinois profile facing right, 1024 canvas. Tall erect ears, long tapered muzzle.
HEAD = [
    (300, 980), (286, 820), (292, 690), (318, 590),     # back of neck
    (350, 500), (372, 430),                             # nape into rear ear base
    (384, 300), (410, 180), (440, 118),                 # rear ear up to tip
    (486, 200), (520, 290), (548, 372),                 # ear front edge down to skull
    (580, 384), (640, 410), (690, 452),                 # forehead to stop
    (760, 488), (830, 520), (884, 548),                 # bridge of muzzle
    (912, 572), (918, 600), (900, 620),                 # nose
    (860, 630), (800, 646), (746, 668),                 # upper lip
    (700, 690), (650, 712),                             # jaw
    (606, 760), (588, 840), (596, 980),                 # throat down to chest
]
EYE = (668, 500)
# far ear peeks out behind the skull; rendered darker for depth
FAR_EAR = [(540, 380), (566, 250), (604, 150), (632, 236), (660, 330), (676, 420)]
NOSE = "M884 552 Q922 566 918 600 Q910 622 884 618 Q872 590 884 552 Z"
MOUTH = "M904 618 L790 640 L742 646 L722 662"


def densify(poly, step):
    out = []
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) // step))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    return out


def inside(pt, poly):
    x, y = pt
    hit = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def mesh(poly, seed, interior=150):
    rng = random.Random(seed)
    pts = densify(poly, 70)
    xs, ys = zip(*poly)
    added = 0
    for _ in range(20000):  # bounded: stop once the shape is full
        if added == interior:
            break
        p = (rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys)))
        if inside(p, poly) and all(math.hypot(p[0] - q[0], p[1] - q[1]) > 38 for q in pts):
            pts.append(p)
            added += 1
    # anchor facets around the eye so the face reads
    pts += [(EYE[0] + 40 * math.cos(a), EYE[1] + 26 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]]
    arr = np.array(pts)
    tris = [t for t in Delaunay(arr).simplices if inside(arr[t].mean(axis=0), poly)]
    return arr, tris


def mix(c0, c1, t):
    t = max(0.0, min(1.0, t))
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def facets(arr, tris, dark, light, seed):
    rng = random.Random(seed)
    light_at = np.array([820.0, 260.0])  # key light upper-right, in front of the face
    out = []
    for t in tris:
        p = arr[t]
        c = p.mean(axis=0)
        d = np.linalg.norm(c - light_at) / 900
        shade = 1.05 - d + rng.uniform(-0.12, 0.12)
        pts = " ".join("%.1f,%.1f" % (x, y) for x, y in p)
        out.append('<polygon points="%s" fill="%s"/>' % (pts, mix(dark, light, shade)))
    return "\n".join(out)


def edges(arr, tris):
    seen, out = set(), []
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            k = (min(a, b), max(a, b))
            if k not in seen:
                seen.add(k)
                (x0, y0), (x1, y1) = arr[a], arr[b]
                out.append("M%.1f %.1fL%.1f %.1f" % (x0, y0, x1, y1))
    return " ".join(out)


def outline(poly):
    return "M" + " L".join("%d %d" % p for p in poly) + " Z"


def head_layer(dark, light, edge, seed, eye):
    arr, tris = mesh(HEAD, seed)
    return f"""
  <g clip-path="url(#lens)">
    <g transform="translate(-60 0)">
      <g>{facets(*mesh(FAR_EAR, seed + 1, interior=8), dark, mix(dark, light, .55), seed + 1)}</g>
      <path d="{outline(FAR_EAR)}" fill="none" stroke="{edge}" stroke-opacity=".55" stroke-width="3" stroke-linejoin="round"/>
      <g>{facets(arr, tris, dark, light, seed)}</g>
      <path d="{edges(arr, tris)}" fill="none" stroke="{edge}" stroke-opacity=".5" stroke-width="1.6"/>
      <path d="{outline(HEAD)}" fill="none" stroke="{edge}" stroke-width="5" stroke-linejoin="round" filter="url(#glow)"/>
      <path d="{NOSE}" fill="{dark}" stroke="{edge}" stroke-width="4"/>
      <path d="{MOUTH}" fill="none" stroke="{edge}" stroke-width="5" stroke-linecap="round" filter="url(#glow)"/>
      {eye}
    </g>
  </g>"""


DEFS = """
  <defs>
    <radialGradient id="bg" cx="50%" cy="42%" r="70%">
      <stop offset="0" stop-color="{bg0}"/><stop offset="1" stop-color="#000"/>
    </radialGradient>
    <clipPath id="lens"><circle cx="512" cy="512" r="400"/></clipPath>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    {extra}
  </defs>
  <rect width="1024" height="1024" rx="224" fill="url(#bg)"/>"""


def watchdog():
    """Silver dog inside a watch dial: the dog that watches."""
    ticks = []
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = 418 if i % 5 else 398
        x0, y0 = 512 + r0 * math.cos(a), 512 + r0 * math.sin(a)
        x1, y1 = 512 + 436 * math.cos(a), 512 + 436 * math.sin(a)
        ticks.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                     f'stroke-width="{7 if i % 5 == 0 else 3}"/>')
    eye = (f'<path d="M{EYE[0]-28} {EYE[1]+4} Q{EYE[0]} {EYE[1]-20} {EYE[0]+30} {EYE[1]-6} '
           f'Q{EYE[0]+4} {EYE[1]+16} {EYE[0]-28} {EYE[1]+4} Z" fill="#fff" filter="url(#glow)"/>')
    body = head_layer("#05080e", "#d6e4f5", "#eef5ff", 7, eye)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Watchdog">
{DEFS.format(bg0="#1a2230", extra="")}
  <circle cx="512" cy="512" r="400" fill="#020304"/>
{body}
  <g stroke="#f4f8fc" stroke-linecap="round" opacity=".9">{''.join(ticks)}</g>
  <circle cx="512" cy="512" r="452" fill="none" stroke="#f4f8fc" stroke-opacity=".35" stroke-width="3"/>
  <circle cx="512" cy="512" r="400" fill="none" stroke="#f4f8fc" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="76" r="9" fill="#2DD4BF" filter="url(#glow)"/>
</svg>
"""


def malinois():
    """Teal hunting dog seen through a scope: the dog that finds the target."""
    extra = """<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#2DD4BF" stop-opacity="0"/>
      <stop offset="1" stop-color="#2DD4BF" stop-opacity=".38"/>
    </linearGradient>"""
    eye = f"""<g filter="url(#glow)">
        <circle cx="{EYE[0]}" cy="{EYE[1]}" r="26" fill="none" stroke="#fff" stroke-width="4"/>
        <path d="M{EYE[0]} {EYE[1]-44}V{EYE[1]-30}M{EYE[0]} {EYE[1]+30}V{EYE[1]+44}M{EYE[0]-44} {EYE[1]}H{EYE[0]-30}M{EYE[0]+30} {EYE[1]}H{EYE[0]+44}" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
        <circle cx="{EYE[0]}" cy="{EYE[1]}" r="7" fill="#fff"/>
      </g>"""
    body = head_layer("#010d0c", "#5eead4", "#99f6e4", 11, eye)
    cross = []
    for a in (0, 90, 180, 270):
        r = math.radians(a)
        cross.append(f'<line x1="{512 + 400 * math.cos(r):.0f}" y1="{512 + 400 * math.sin(r):.0f}" '
                     f'x2="{512 + 468 * math.cos(r):.0f}" y2="{512 + 468 * math.sin(r):.0f}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Malinois">
{DEFS.format(bg0="#06302c", extra=extra)}
  <circle cx="512" cy="512" r="400" fill="#000807"/>
  <path d="M512 512 L912 512 A400 400 0 0 0 795 229 Z" fill="url(#sweep)" clip-path="url(#lens)"/>
{body}
  <g stroke="#5eead4" stroke-width="8" stroke-linecap="round" filter="url(#glow)">{''.join(cross)}</g>
  <circle cx="512" cy="512" r="400" fill="none" stroke="#5eead4" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="512" r="440" fill="none" stroke="#5eead4" stroke-opacity=".3" stroke-width="2" stroke-dasharray="4 14"/>
</svg>
"""


if __name__ == "__main__":
    for rel, svg in (("assets/logo.svg", watchdog()), ("plugins/malinois/assets/icon.svg", malinois())):
        with open(os.path.join(ROOT, rel), "w") as f:
            f.write(svg)
        print("wrote", rel)
