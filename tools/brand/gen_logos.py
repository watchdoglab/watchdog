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
    (306, 980), (296, 860), (302, 740), (322, 640),     # back of neck
    (350, 560), (376, 486),                             # nape
    (390, 400), (402, 300), (420, 200), (444, 112),     # rear edge of ear to tip
    (478, 186), (506, 262), (532, 330), (556, 376),     # front edge of ear
    (604, 384), (646, 396), (680, 418),                 # forehead
    (704, 448),                                         # stop
    (762, 470), (822, 494), (872, 516), (902, 536),     # bridge of muzzle
    (920, 558), (926, 584), (916, 604),                 # nose
    (888, 616), (846, 624), (798, 634), (752, 648),     # upper lip
    (716, 668), (682, 692), (652, 716),                 # jaw to jaw angle
    (628, 752), (608, 804), (598, 884), (602, 980),     # throat to chest
]
EYE = (676, 486)
# far ear peeks out behind the skull; rendered darker for depth
FAR_EAR = [(566, 386), (588, 270), (620, 160), (648, 242), (674, 334), (690, 424)]
NOSE = "M896 538 Q930 552 928 586 Q922 610 898 608 Q884 576 896 538 Z"
MOUTH = "M914 608 L798 634 L750 646 L726 664"

# Height bumps (x, y, height, radius) that sculpt the lit form.
BUMPS = [
    (650, 440, 46, 90),    # brow ridge over the eye
    (640, 600, 40, 110),   # cheekbone / masseter
    (800, 520, 30, 120),   # crest of the muzzle
    (450, 260, 24, 80),    # cup of the ear
    (420, 760, 36, 200),   # neck muscle
]
LIGHT = np.array([0.55, -0.62, 0.56])  # from upper-right front (y grows downward)
LIGHT = LIGHT / np.linalg.norm(LIGHT)


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


def mesh(poly, seed, interior=260):
    rng = random.Random(seed)
    pts = densify(poly, 52)
    xs, ys = zip(*poly)
    added = 0
    for _ in range(40000):  # bounded: stop once the shape is full
        if added == interior:
            break
        p = (rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys)))
        # finer facets on the face, coarser down the neck
        gap = 26 if math.hypot(p[0] - EYE[0], p[1] - EYE[1]) < 220 else 40
        if inside(p, poly) and all(math.hypot(p[0] - q[0], p[1] - q[1]) > gap for q in pts):
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


def heights(arr, poly, seed):
    """Dome the shape away from its silhouette, add anatomical bumps, a little grain."""
    rng = random.Random(seed)
    segs = list(zip(poly, poly[1:] + poly[:1]))
    out = []
    for x, y in arr:
        d = min(_seg_dist(x, y, a, b) for a, b in segs)
        h = 150 * (1 - (1 - min(d, 170) / 170) ** 2)
        for bx, by, bh, br in BUMPS:
            h += bh * math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (2 * br * br))
        out.append(h + rng.uniform(-9, 9))
    return np.array(out)


def _seg_dist(x, y, a, b):
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(x - x0 - t * dx, y - y0 - t * dy)


def facets(arr, tris, dark, light, seed, poly):
    h = heights(arr, poly, seed)
    out = []
    for t in tris:
        p = [np.array([arr[i][0], arr[i][1], h[i]]) for i in t]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        n = n / (np.linalg.norm(n) or 1)
        if n[2] < 0:
            n = -n
        shade = 0.16 + 0.95 * max(0.0, float(n @ LIGHT))
        pts = " ".join("%.1f,%.1f" % (x, y) for x, y, _ in p)
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
      <g>{facets(*mesh(FAR_EAR, seed + 1, interior=10), dark, mix(dark, light, .55), seed + 1, FAR_EAR)}</g>
      <path d="{outline(FAR_EAR)}" fill="none" stroke="{edge}" stroke-opacity=".55" stroke-width="3" stroke-linejoin="round"/>
      <g>{facets(arr, tris, dark, light, seed, HEAD)}</g>
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
