"""Render the animated README banner (assets/banner.gif).

    python3 tools/brand/gen_banner.py

Needs rsvg-convert and ImageMagick (magick) on PATH. Run gen_logos.py first:
the banner reuses assets/logo.png and plugins/malinois/assets/icon.png.
"""
import base64
import math
import os
import subprocess
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT = "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf"
W, H = 1280, 400
FRAMES = 40
LOGO = 340                              # logo size on the banner
LX, LY = 60, (H - LOGO) // 2            # logo top-left
S = LOGO / 1024                         # logo units -> banner px
CX, CY = LX + 512 * S, LY + 512 * S     # dial centre
LENS = 400 * S                          # dial lens radius
EYE = (LX + (676 - 60) * S, LY + 486 * S)


def frame_svg(i, logo_uri):
    t = i / FRAMES
    a = 2 * math.pi * t - math.pi / 2           # sweep angle, starts at 12 o'clock
    tail = a - math.radians(70)
    sx, sy = CX + LENS * math.cos(a), CY + LENS * math.sin(a)
    tx, ty = CX + LENS * math.cos(tail), CY + LENS * math.sin(tail)
    dot = (CX + 436 * S * math.cos(a), CY + 436 * S * math.sin(a))
    pulse = 0.35 + 0.65 * (0.5 + 0.5 * math.cos(4 * math.pi * t))
    scan_x = -200 + (W + 400) * t
    grid = "".join(f'<path d="M{x} 0V{H}" />' for x in range(0, W, 40)) + \
           "".join(f'<path d="M0 {y}H{W}" />' for y in range(0, H, 40))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}">
  <defs>
    <radialGradient id="vig" cx="30%" cy="50%" r="80%">
      <stop offset="0" stop-color="#0b1219"/><stop offset="1" stop-color="#000"/>
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
    <clipPath id="dial"><circle cx="{CX:.1f}" cy="{CY:.1f}" r="{462 * S:.1f}"/></clipPath>
    <clipPath id="lens"><circle cx="{CX:.1f}" cy="{CY:.1f}" r="{LENS:.1f}"/></clipPath>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <g stroke="#2DD4BF" stroke-opacity=".06" stroke-width="1">{grid}</g>
  <rect x="{scan_x:.1f}" y="0" width="200" height="{H}" fill="url(#scan)"/>
  <image clip-path="url(#dial)" x="{LX}" y="{LY}" width="{LOGO}" height="{LOGO}" xlink:href="{logo_uri}"/>
  <g clip-path="url(#lens)">
    <path d="M{CX:.1f} {CY:.1f} L{tx:.1f} {ty:.1f} A{LENS:.1f} {LENS:.1f} 0 0 1 {sx:.1f} {sy:.1f} Z" fill="url(#sweep)"/>
    <path d="M{CX:.1f} {CY:.1f} L{sx:.1f} {sy:.1f}" stroke="#99f6e4" stroke-width="2" stroke-opacity=".8" filter="url(#glow)"/>
  </g>
  <circle cx="{dot[0]:.1f}" cy="{dot[1]:.1f}" r="5" fill="#2DD4BF" filter="url(#glow)"/>
  <circle cx="{EYE[0]:.1f}" cy="{EYE[1]:.1f}" r="7" fill="#fff" opacity="{pulse:.2f}" filter="url(#glow)"/>
</svg>"""


def run(*cmd):
    subprocess.run(cmd, check=True)


def text_layer(path):
    """Wordmark, tagline and the Malinois pill, drawn once and laid over every frame."""
    icon = os.path.join(ROOT, "plugins/malinois/assets/icon.png")
    run("magick", "-size", f"{W}x{H}", "xc:none",
        "-fill", "#2a3340", "-draw", "rectangle 452,96 454,322",
        "-font", FONT, "-fill", "#F4F8FC", "-pointsize", "104", "-kerning", "18",
        "-annotate", "+500+180", "WATCHDOG",
        "-font", FONT, "-fill", "#8A94A3", "-pointsize", "28", "-kerning", "8",
        "-annotate", "+505+228", "SECURITY DOGS FOR YOUR CODE",
        "-fill", "#06201d", "-stroke", "#134E48", "-strokewidth", "2",
        "-draw", "roundrectangle 503,272 815,320 24,24", "-stroke", "none",
        "(", icon, "-resize", "38x38", ")", "-geometry", "+511+277", "-composite",
        "-font", FONT, "-fill", "#5EEAD4", "-pointsize", "22", "-kerning", "5",
        "-annotate", "+560+304", "MALINOIS  /  VAPT", path)


def main():
    out = os.path.join(ROOT, "assets/banner.gif")
    with tempfile.TemporaryDirectory() as tmp:
        text = os.path.join(tmp, "text.png")
        text_layer(text)
        # rsvg will not fetch file:// images, so the logo rides inline
        with open(os.path.join(ROOT, "assets/logo.png"), "rb") as f:
            logo_uri = "data:image/png;base64," + base64.b64encode(f.read()).decode()
        frames = []
        for i in range(FRAMES):
            svg, png = os.path.join(tmp, f"f{i:02}.svg"), os.path.join(tmp, f"f{i:02}.png")
            with open(svg, "w") as f:
                f.write(frame_svg(i, logo_uri))
            run("rsvg-convert", "-o", png, svg)
            run("magick", png, text, "-composite", png)
            frames.append(png)
        run("magick", "-delay", "5", "-loop", "0", *frames,
            "-coalesce", "-colors", "128", "-layers", "Optimize", out)
    print("wrote assets/banner.gif", os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
