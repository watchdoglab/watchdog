"""Render the animated README art.

    python3 tools/brand/gen_banner.py

Writes:
  assets/banner.gif                    Watchdog banner (top of README)
  plugins/malinois/assets/banner.gif   Malinois banner (its README section)
  plugins/malinois/assets/icon.gif     Malinois icon (Dogs table)
  plugins/husky/assets/banner.gif      Husky banner
  plugins/husky/assets/icon.gif        Husky icon (Dogs table)
  plugins/collie/assets/banner.gif     Collie banner
  plugins/collie/assets/icon.gif       Collie icon (Dogs table)
  plugins/bloodhound/assets/banner.gif Bloodhound banner
  plugins/bloodhound/assets/icon.gif   Bloodhound icon (Dogs table)
  plugins/beagle/assets/banner.gif     Beagle banner
  plugins/beagle/assets/icon.gif       Beagle icon (Dogs table)

Needs rsvg-convert and ImageMagick (magick) on PATH. Run gen_logos.py first:
the art reuses the logo SVGs it writes.
"""
import base64
import math
import os
import re
import subprocess
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT = "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf"
FRAMES = 40
EYE = (676 - 60, 486)  # eye in logo units (gen_logos draws the head shifted 60px left)

BRANDS = {
    "watchdog": dict(
        svg="assets/logo.svg", orbit=436, eye="dot", vignette="#0b1219",
        title="WATCHDOG", title_color="#F4F8FC",
        tagline="SECURITY DOGS FOR YOUR CODE", tagline_color="#8A94A3",
        pill="14 DOGS  /  ONE PACK", pill_icon=None,
    ),
    "malinois": dict(
        svg="plugins/malinois/assets/icon.svg", orbit=440, eye="ring", vignette="#062320",
        title="MALINOIS", title_color="#E6FFFB",
        tagline="VAPT  /  BY WATCHDOG", tagline_color="#4FB3A7",
        pill="CODE  /  WEB  /  APK  /  IPA", pill_icon=None,
    ),
    "bloodhound": dict(
        svg="plugins/bloodhound/assets/icon.svg", orbit=446, eye="dot", vignette="#24160a",
        title="BLOODHOUND", title_color="#FFFBEB",
        title_size=84, title_kerning=8,  # ten letters: shrink to fit the banner
        tagline="API  /  BY WATCHDOG", tagline_color="#D9A441",
        pill="OPENAPI  /  GRAPHQL  /  REST", pill_icon=None,
    ),
    "collie": dict(
        svg="plugins/collie/assets/icon.svg", orbit=452, eye="dot", vignette="#160a2e",
        title="COLLIE", title_color="#F5F3FF",
        tagline="AI  /  BY WATCHDOG", tagline_color="#9F8AE0",
        pill="PROMPTS  /  AGENTS  /  RAG  /  MCP", pill_icon=None,
    ),
    "beagle": dict(
        svg="plugins/beagle/assets/icon.svg", orbit=452, eye="dot", vignette="#2b1706",
        title="BEAGLE", title_color="#FFF7ED",
        tagline="PRIVACY  /  BY WATCHDOG", tagline_color="#E0955F",
        pill="PII  /  LOGS  /  CONSENT", pill_icon=None,
    ),
    "rottweiler": dict(
        svg="plugins/rottweiler/assets/icon.svg", orbit=452, eye="dot", vignette="#1c1006",
        title="ROTTWEILER", title_color="#E7E5E4",
        title_size=84, title_kerning=8,
        tagline="SUPPLY CHAIN  /  BY WATCHDOG", tagline_color="#B98A5E",
        pill="LOCKFILES  /  SBOM  /  DEPS", pill_icon=None,
    ),
    "doberman": dict(
        svg="plugins/doberman/assets/icon.svg", orbit=452, eye="dot", vignette="#2a0808",
        title="DOBERMAN", title_color="#FEF2F2",
        title_size=84, title_kerning=8,
        tagline="AUTH  /  BY WATCHDOG", tagline_color="#E07A7A",
        pill="LOGIN  /  OAUTH  /  MFA", pill_icon=None,
    ),
    "shepherd": dict(
        svg="plugins/shepherd/assets/icon.svg", orbit=452, eye="dot", vignette="#06200f",
        title="SHEPHERD", title_color="#F0FDF4",
        title_size=84, title_kerning=8,
        tagline="MOBILE  /  BY WATCHDOG", tagline_color="#5FC489",
        pill="ANDROID  /  IOS  /  FLUTTER", pill_icon=None,
    ),
    "dachshund": dict(
        svg="plugins/dachshund/assets/icon.svg", orbit=452, eye="dot", vignette="#2a0610",
        title="DACHSHUND", title_color="#FFF1F2",
        title_size=84, title_kerning=8,
        tagline="DATABASE  /  BY WATCHDOG", tagline_color="#E86A84",
        pill="SQL  /  RLS  /  FIREBASE", pill_icon=None,
    ),
    "akita": dict(
        svg="plugins/akita/assets/icon.svg", orbit=452, eye="dot", vignette="#08142e",
        title="AKITA", title_color="#EFF6FF",
        tagline="SECRETS  /  BY WATCHDOG", tagline_color="#6A9EE8",
        pill="FIND  /  ROTATE  /  BLOCK", pill_icon=None,
    ),
    "pointer": dict(
        svg="plugins/pointer/assets/icon.svg", orbit=452, eye="dot", vignette="#241e04",
        title="POINTER", title_color="#FEFCE8",
        tagline="FRONTEND  /  BY WATCHDOG", tagline_color="#D9B93E",
        pill="XSS  /  CSP  /  DOM", pill_icon=None,
    ),
    "saintbernard": dict(
        svg="plugins/saintbernard/assets/icon.svg", orbit=452, eye="dot", vignette="#2a0808",
        title="SAINT BERNARD", title_color="#FEF2F2",
        title_size=84, title_kerning=8,
        tagline="INCIDENT RESPONSE  /  BY WATCHDOG", tagline_color="#E07A7A",
        pill="TIMELINE  /  BLAST RADIUS", pill_icon=None,
    ),
    "shiba": dict(
        svg="plugins/shiba/assets/icon.svg", orbit=452, eye="dot", vignette="#2a1304",
        title="SHIBA", title_color="#FFF7ED",
        tagline="WEB3  /  BY WATCHDOG", tagline_color="#E8955A",
        pill="SOLIDITY  /  DEFI  /  AUDIT", pill_icon=None,
    ),
    "pyrenees": dict(
        svg="plugins/pyrenees/assets/icon.svg", orbit=452, eye="dot", vignette="#141a24",
        title="PYRENEES", title_color="#F8FAFC",
        title_size=84, title_kerning=8,
        tagline="COMPLIANCE  /  BY WATCHDOG", tagline_color="#A3B1C6",
        pill="SOC 2  /  ISO 27001  /  PCI", pill_icon=None,
    ),
    "husky": dict(
        svg="plugins/husky/assets/icon.svg", orbit=440, eye="dot", vignette="#061a2b",
        title="HUSKY", title_color="#F0F9FF",
        tagline="CLOUD  /  BY WATCHDOG", tagline_color="#5BA8D6",
        pill="TERRAFORM  /  K8S  /  DOCKER  /  CI", pill_icon=None,
    ),
}


class Layout:
    def __init__(self, w, h, logo, lx, ly, backdrop):
        self.w, self.h, self.logo, self.lx, self.ly, self.backdrop = w, h, logo, lx, ly, backdrop
        self.s = logo / 1024
        self.cx, self.cy = lx + 512 * self.s, ly + 512 * self.s
        self.lens = 400 * self.s

    def at(self, x, y):
        return self.lx + x * self.s, self.ly + y * self.s


BANNER = Layout(1280, 400, 340, 60, 30, backdrop=True)
ICON = Layout(256, 256, 256, 0, 0, backdrop=False)


def frame_svg(i, base_uri, brand, L):
    t = i / FRAMES
    a = 2 * math.pi * t - math.pi / 2           # sweep angle, starts at 12 o'clock
    tail = a - math.radians(70)
    sx, sy = L.cx + L.lens * math.cos(a), L.cy + L.lens * math.sin(a)
    tx, ty = L.cx + L.lens * math.cos(tail), L.cy + L.lens * math.sin(tail)
    r_orbit = brand["orbit"] * L.s
    dot = (L.cx + r_orbit * math.cos(a), L.cy + r_orbit * math.sin(a))
    beat = 0.5 + 0.5 * math.cos(4 * math.pi * t)          # two beats per loop
    ex, ey = L.at(*EYE)
    if brand["eye"] == "dot":
        eye = f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{7 * L.s * 3:.1f}" fill="#fff" opacity="{0.35 + 0.65 * beat:.2f}" filter="url(#glow)"/>'
    else:  # reticle lock-on: a ring that tightens onto the eye
        r = (30 + 34 * (1 - beat)) * L.s
        eye = f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{r:.1f}" fill="none" stroke="#fff" stroke-width="{max(1.5, 4 * L.s):.1f}" opacity="{beat:.2f}" filter="url(#glow)"/>'
    back = ""
    if L.backdrop:
        grid = "".join(f'<path d="M{x} 0V{L.h}"/>' for x in range(0, L.w, 40)) + \
               "".join(f'<path d="M0 {y}H{L.w}"/>' for y in range(0, L.h, 40))
        scan_x = -200 + (L.w + 400) * t
        back = f"""<rect width="{L.w}" height="{L.h}" fill="url(#vig)"/>
  <g stroke="#2DD4BF" stroke-opacity=".06" stroke-width="1">{grid}</g>
  <rect x="{scan_x:.1f}" y="0" width="200" height="{L.h}" fill="url(#scan)"/>"""
    # On the banner the dial floats free; as an icon it keeps its own tile.
    clip = 'clip-path="url(#dial)"' if L.backdrop else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{L.w}" height="{L.h}">
  <defs>
    <radialGradient id="vig" cx="30%" cy="50%" r="80%">
      <stop offset="0" stop-color="{brand['vignette']}"/><stop offset="1" stop-color="#000"/>
    </radialGradient>
    <linearGradient id="scan" x1="0" x2="1">
      <stop offset="0" stop-color="#2DD4BF" stop-opacity="0"/>
      <stop offset=".5" stop-color="#2DD4BF" stop-opacity=".10"/>
      <stop offset="1" stop-color="#2DD4BF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sweep" gradientUnits="userSpaceOnUse" x1="{tx:.1f}" y1="{ty:.1f}" x2="{sx:.1f}" y2="{sy:.1f}">
      <stop offset="0" stop-color="#2DD4BF" stop-opacity="0"/>
      <stop offset="1" stop-color="#2DD4BF" stop-opacity=".42"/>
    </linearGradient>
    <clipPath id="dial"><circle cx="{L.cx:.1f}" cy="{L.cy:.1f}" r="{470 * L.s:.1f}"/></clipPath>
    <clipPath id="lens"><circle cx="{L.cx:.1f}" cy="{L.cy:.1f}" r="{L.lens:.1f}"/></clipPath>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="{max(1.5, 12 * L.s):.1f}" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  {back}
  <image {clip} x="{L.lx}" y="{L.ly}" width="{L.logo}" height="{L.logo}" xlink:href="{base_uri}"/>
  <g clip-path="url(#lens)">
    <path d="M{L.cx:.1f} {L.cy:.1f} L{tx:.1f} {ty:.1f} A{L.lens:.1f} {L.lens:.1f} 0 0 1 {sx:.1f} {sy:.1f} Z" fill="url(#sweep)"/>
    <path d="M{L.cx:.1f} {L.cy:.1f} L{sx:.1f} {sy:.1f}" stroke="#99f6e4" stroke-width="{max(1.2, 6 * L.s):.1f}" stroke-opacity=".8" filter="url(#glow)"/>
  </g>
  <circle cx="{dot[0]:.1f}" cy="{dot[1]:.1f}" r="{max(3, 15 * L.s):.1f}" fill="#2DD4BF" filter="url(#glow)"/>
  {eye}
</svg>"""


def run(*cmd):
    subprocess.run(cmd, check=True)


def base_png(brand, tmp):
    """The logo with its painted (static) sweep removed; the live sweep replaces it."""
    with open(os.path.join(ROOT, brand["svg"])) as f:
        svg = re.sub(r'\s*<path [^>]*fill="url\(#sweep\)"[^>]*/>', "", f.read())
    src, png = os.path.join(tmp, "base.svg"), os.path.join(tmp, "base.png")
    with open(src, "w") as f:
        f.write(svg)
    run("rsvg-convert", "-w", "1024", "-h", "1024", "-o", png, src)
    with open(png, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def text_layer(brand, path, L):
    """Wordmark, tagline and pill, drawn once and laid over every banner frame."""
    pill_w = 14 * len(brand["pill"]) + (84 if brand["pill_icon"] else 50)
    cmd = ["magick", "-size", f"{L.w}x{L.h}", "xc:none",
           "-fill", "#2a3340", "-draw", "rectangle 452,96 454,322",
           "-font", FONT, "-fill", brand["title_color"], "-pointsize", str(brand.get("title_size", 104)), "-kerning", str(brand.get("title_kerning", 18)),
           "-annotate", "+500+180", brand["title"],
           "-font", FONT, "-fill", brand["tagline_color"], "-pointsize", "28", "-kerning", "8",
           "-annotate", "+505+228", brand["tagline"],
           "-fill", "#06201d", "-stroke", "#134E48", "-strokewidth", "2",
           "-draw", f"roundrectangle 503,272 {503 + pill_w},320 24,24", "-stroke", "none"]
    text_x = 527
    if brand["pill_icon"]:
        cmd += ["(", os.path.join(ROOT, brand["pill_icon"]), "-resize", "38x38", ")",
                "-geometry", "+511+277", "-composite"]
        text_x = 560
    cmd += ["-font", FONT, "-fill", "#5EEAD4", "-pointsize", "22", "-kerning", "5",
            "-annotate", f"+{text_x}+304", brand["pill"], path]
    run(*cmd)


def render(name, L, out):
    brand = BRANDS[name]
    with tempfile.TemporaryDirectory() as tmp:
        base_uri = base_png(brand, tmp)
        text = None
        if L.backdrop:
            text = os.path.join(tmp, "text.png")
            text_layer(brand, text, L)
        frames = []
        for i in range(FRAMES):
            svg, png = os.path.join(tmp, f"f{i:02}.svg"), os.path.join(tmp, f"f{i:02}.png")
            with open(svg, "w") as f:
                f.write(frame_svg(i, base_uri, brand, L))
            run("rsvg-convert", "-o", png, svg)
            if text:
                run("magick", png, text, "-composite", png)
            frames.append(png)
        path = os.path.join(ROOT, out)
        # one shared palette for every frame, so colours do not flicker between frames
        run("magick", "-delay", "5", "-loop", "0", *frames, "-coalesce",
            "+remap", "-layers", "Optimize", path)
    print("wrote", out, os.path.getsize(path) // 1024, "KB")


if __name__ == "__main__":
    render("watchdog", BANNER, "assets/banner.gif")
    render("malinois", BANNER, "plugins/malinois/assets/banner.gif")
    render("malinois", ICON, "plugins/malinois/assets/icon.gif")
    render("husky", BANNER, "plugins/husky/assets/banner.gif")
    render("husky", ICON, "plugins/husky/assets/icon.gif")
    render("collie", BANNER, "plugins/collie/assets/banner.gif")
    render("collie", ICON, "plugins/collie/assets/icon.gif")
    render("bloodhound", BANNER, "plugins/bloodhound/assets/banner.gif")
    render("bloodhound", ICON, "plugins/bloodhound/assets/icon.gif")
    render("beagle", BANNER, "plugins/beagle/assets/banner.gif")
    render("beagle", ICON, "plugins/beagle/assets/icon.gif")
    render("rottweiler", BANNER, "plugins/rottweiler/assets/banner.gif")
    render("rottweiler", ICON, "plugins/rottweiler/assets/icon.gif")
    render("doberman", BANNER, "plugins/doberman/assets/banner.gif")
    render("doberman", ICON, "plugins/doberman/assets/icon.gif")
    render("shepherd", BANNER, "plugins/shepherd/assets/banner.gif")
    render("shepherd", ICON, "plugins/shepherd/assets/icon.gif")
    render("dachshund", BANNER, "plugins/dachshund/assets/banner.gif")
    render("dachshund", ICON, "plugins/dachshund/assets/icon.gif")
    render("akita", BANNER, "plugins/akita/assets/banner.gif")
    render("akita", ICON, "plugins/akita/assets/icon.gif")
    render("pointer", BANNER, "plugins/pointer/assets/banner.gif")
    render("pointer", ICON, "plugins/pointer/assets/icon.gif")
    render("saintbernard", BANNER, "plugins/saintbernard/assets/banner.gif")
    render("saintbernard", ICON, "plugins/saintbernard/assets/icon.gif")
    render("shiba", BANNER, "plugins/shiba/assets/banner.gif")
    render("shiba", ICON, "plugins/shiba/assets/icon.gif")
    render("pyrenees", BANNER, "plugins/pyrenees/assets/banner.gif")
    render("pyrenees", ICON, "plugins/pyrenees/assets/icon.gif")
