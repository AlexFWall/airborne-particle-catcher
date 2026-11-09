"""Build a printable card carrying the repository QR code, as vector SVG and 300 dpi PNG.

Laid out in millimetres so the card prints at a known physical size: a 62 mm QR
symbol reads reliably from about a metre, which suits a poster or a noticeboard.
The PNG is drawn directly rather than rasterised from the SVG, because macOS
carries no SVG rasteriser that preserves a non-square page.
"""
import segno
from PIL import Image, ImageDraw, ImageFont

URL = "https://github.com/AlexFWall/airborne-particle-catcher"
OUT = "/Users/wall0536/Documents/Projects/TauberTrap3D/airborne-particle-catcher/qr"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
DPI = 300

CARD_W, CARD_H = 90.0, 125.0
QR_SIDE, QR_Y = 62.0, 32.0

qr = segno.make(URL, error="h")
matrix = [[bool(c) for c in row] for row in qr.matrix]
n = len(matrix)
module = QR_SIDE / n
qr_x = (CARD_W - QR_SIDE) / 2

# (text, baseline y, size, bold, colour) in millimetres
LINES = [
    ("Airborne Particle Catcher", 13.0, 5.9, True, "#111111"),
    ("3D-printable Tauber pollen trap", 20.0, 3.8, False, "#111111"),
    ("Scan to download the print files", 26.4, 3.8, True, "#111111"),
    ("github.com/AlexFWall/", QR_Y + QR_SIDE + 8.0, 3.3, False, "#444444"),
    ("airborne-particle-catcher", QR_Y + QR_SIDE + 12.6, 3.3, False, "#444444"),
    ("Free and open source", CARD_H - 10.0, 3.0, False, "#666666"),
    ("CERN-OHL-S v2", CARD_H - 6.0, 3.0, False, "#666666"),
]

# --- vector SVG, for printing at any size ---
squares = "".join(
    f"M{qr_x + c * module:.4f} {QR_Y + r * module:.4f}h{module:.4f}v{module:.4f}h-{module:.4f}z"
    for r, row in enumerate(matrix) for c, dark in enumerate(row) if dark
)
def svg_text(t, y, size, bold, fill):
    weight = ' font-weight="700"' if bold else ""
    return f'<text x="{CARD_W/2}" y="{y}" font-size="{size}"{weight} fill="{fill}">{t}</text>'


texts = "\n    ".join(svg_text(*line) for line in LINES)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}mm" height="{CARD_H}mm"
     viewBox="0 0 {CARD_W} {CARD_H}">
  <rect width="{CARD_W}" height="{CARD_H}" fill="#ffffff"/>
  <g font-family="Helvetica, Arial, sans-serif" text-anchor="middle">
    {texts}
  </g>
  <path d="{squares}" fill="#000000" shape-rendering="crispEdges"/>
</svg>
'''
with open(f"{OUT}/airborne-particle-catcher-card.svg", "w") as f:
    f.write(svg)

# --- 300 dpi PNG, for slides and printers that will not take SVG ---
px = lambda mm: round(mm / 25.4 * DPI)
img = Image.new("RGB", (px(CARD_W), px(CARD_H)), "white")
draw = ImageDraw.Draw(img)

for r, row in enumerate(matrix):
    for c, dark in enumerate(row):
        if dark:
            x0, y0 = px(qr_x + c * module), px(QR_Y + r * module)
            draw.rectangle([x0, y0, px(qr_x + (c + 1) * module) - 1,
                            px(QR_Y + (r + 1) * module) - 1], fill="black")

for t, y, size, bold, fill in LINES:
    # Arial's em square puts the cap height at roughly 0.716 em, so a font sized
    # in pixels from the millimetre size lands the baseline where the SVG puts it.
    f = ImageFont.truetype(FONT_BOLD if bold else FONT, px(size))
    draw.text((px(CARD_W / 2), px(y)), t, font=f, fill=fill, anchor="ms")

img.save(f"{OUT}/airborne-particle-catcher-card.png", dpi=(DPI, DPI))
print(f"{CARD_W:.0f} x {CARD_H:.0f} mm, {n}x{n} modules at {module:.3f} mm, "
      f"QR {QR_SIDE:.0f} mm, PNG {img.size[0]}x{img.size[1]} px at {DPI} dpi")
