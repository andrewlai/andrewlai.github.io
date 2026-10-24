"""Draw the three matching 16:9 project illustrations as SVG.

Writes assets/img/projects/src/*.svg. To refresh the JPGs used on the site,
render each SVG at 1600x900 (e.g. with Playwright/Chromium) and save it as
assets/img/projects/<name>.jpg.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img" / "projects" / "src"
W, H = 1600, 900

TEAL = "#2698ba"
TEAL_D = "#1b6f88"
TEAL_L = "#cfeaf2"
PURPLE = "#8e44ad"
PURPLE_L = "#e8d5f0"
ROSE = "#e8a0a8"
ROSE_D = "#c86470"
RBC = "#d9636f"
INK = "#2c3e50"
BG1, BG2 = "#f6fbfd", "#e9f4f8"

DEFS = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG2}"/>
  </linearGradient>
  <linearGradient id="vessel" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f6c9cd"/><stop offset="0.5" stop-color="#fbe3e5"/><stop offset="1" stop-color="#f6c9cd"/>
  </linearGradient>
  <radialGradient id="evfill" cx="0.4" cy="0.35" r="0.7">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{TEAL_L}"/>
  </radialGradient>
  <radialGradient id="evfillp" cx="0.4" cy="0.35" r="0.7">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{PURPLE_L}"/>
  </radialGradient>
  <radialGradient id="rbc" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#b8434f"/><stop offset="0.55" stop-color="{RBC}"/><stop offset="1" stop-color="#e98089"/>
  </radialGradient>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#1b6f88" flood-opacity="0.15"/>
  </filter>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="{TEAL_D}"/>
  </marker>
</defs>
"""


def ev(x, y, r, purple=False, rot=0):
    """Extracellular vesicle: bilayer sphere with surface proteins and cargo dots."""
    col = PURPLE if purple else TEAL
    fill = "url(#evfillp)" if purple else "url(#evfill)"
    parts = [f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot})">']
    parts.append(f'<circle r="{r}" fill="{fill}" stroke="{col}" stroke-width="{max(2.5, r*0.14):.1f}"/>')
    parts.append(f'<circle r="{r*0.76:.1f}" fill="none" stroke="{col}" stroke-opacity="0.5" stroke-width="{max(1.5, r*0.07):.1f}"/>')
    n = 6 if r < 20 else 9
    for i in range(n):
        a = 2 * math.pi * (i + 0.3) / n
        px, py = r * math.cos(a), r * math.sin(a)
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{max(2.6, r*0.2):.1f}" fill="{col}"/>')

    if r > 14:
        parts.append(f'<circle cx="{-r*0.25:.1f}" cy="{r*0.15:.1f}" r="{r*0.16:.1f}" fill="{col}" opacity="0.55"/>')
        parts.append(f'<circle cx="{r*0.3:.1f}" cy="{-r*0.1:.1f}" r="{r*0.11:.1f}" fill="{ROSE_D}" opacity="0.6"/>')
        parts.append(f'<circle cx="{r*0.05:.1f}" cy="{r*0.42:.1f}" r="{r*0.09:.1f}" fill="#e0a43a" opacity="0.7"/>')
    parts.append("</g>")
    return "".join(parts)


def rbc(x, y, s=1.0, rot=0):
    return (
        f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot}) scale({s})">'
        f'<ellipse rx="34" ry="21" fill="url(#rbc)"/>'
        f'<ellipse rx="15" ry="8" fill="#b8434f" opacity="0.35"/></g>'
    )


def vessel(y0, y1, x0=-250, x1=W + 250, seed=1, rbcs=9, evs=10, ev_purple_frac=0.4, evx=None):
    rnd = random.Random(seed)
    out = [
        f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="url(#vessel)"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{ROSE}" stroke-width="10"/>',
        f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{ROSE}" stroke-width="10"/>',
    ]
    for i in range(rbcs):
        x = x0 + (i + 0.5) * (x1 - x0) / rbcs + rnd.uniform(-30, 30)
        y = rnd.uniform(y0 + 35, y1 - 35)
        out.append(rbc(x, y, rnd.uniform(0.85, 1.05), rnd.uniform(-25, 25)))
    lo, hi = evx or (x0, x1)
    for i in range(evs):
        x = lo + (i + 0.5) * (hi - lo) / evs + rnd.uniform(-25, 25)
        y = rnd.uniform(y0 + 25, y1 - 25)
        out.append(ev(x, y, rnd.uniform(9, 14), rnd.random() < ev_purple_frac, rnd.uniform(0, 90)))
    return "".join(out)


def arrow(x0, y0, x1, y1, curve=0):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - curve
    return (
        f'<path d="M{x0},{y0} Q{mx},{my} {x1},{y1}" fill="none" stroke="{TEAL_D}" stroke-width="5" '
        f'stroke-linecap="round" stroke-dasharray="2 12" marker-end="url(#arrow)"/>'
    )


def svg(body, zoom=1.0, cx=W / 2, cy=H / 2):
    t = f"translate({W/2},{H/2}) scale({zoom}) translate({-cx},{-cy})"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f'{DEFS}<rect width="{W}" height="{H}" fill="url(#bg)"/><g transform="{t}">{body}</g></svg>'
    )


def blood_tube(x, y, s=1.0):
    return f"""<g transform="translate({x},{y}) scale({s})" filter="url(#soft)">
      <rect x="-48" y="-40" width="96" height="300" rx="46" fill="#ffffff" stroke="{INK}" stroke-opacity="0.35" stroke-width="5"/>
      <path d="M-43,90 L43,90 L43,214 Q43,256 0,256 Q-43,256 -43,214 Z" fill="#b8434f"/>
      <path d="M-43,60 L43,60 L43,92 L-43,92 Z" fill="#f2d27a" opacity="0.9"/>
      <rect x="-58" y="-88" width="116" height="64" rx="12" fill="{PURPLE}"/>
      <rect x="-58" y="-40" width="116" height="14" fill="{PURPLE}" opacity="0.6"/>
      {ev(-14, 74, 9)}{ev(18, 70, 8, True)}
    </g>"""


def magnifier(x, y, r=120):
    return f"""<g transform="translate({x},{y})" filter="url(#soft)">
      <line x1="{r*0.72}" y1="{r*0.72}" x2="{r*1.55}" y2="{r*1.55}" stroke="{INK}" stroke-width="26" stroke-linecap="round"/>
      <circle r="{r}" fill="#ffffff" stroke="{INK}" stroke-width="16"/>
      {ev(0, 0, r*0.62)}
      <g font-family="DejaVu Sans, Arial" font-weight="bold" fill="{TEAL_D}"></g>
    </g>"""


# ----------------------------------------------------------------- 1. ovarian cancer
def ovarian():
    b = []
    # vessel across the lower half
    b.append(vessel(560, 760, seed=3, rbcs=10, evs=0))
    # uterus + tube + ovary (stylised) top-left
    b.append(f"""<g transform="translate(500,300)" filter="url(#soft)">
      <path d="M-120,-40 C-180,-110 -260,-120 -300,-60" fill="none" stroke="{ROSE_D}" stroke-width="22" stroke-linecap="round"/>
      <path d="M-300,-60 C-320,-30 -330,-10 -335,0" fill="none" stroke="{ROSE_D}" stroke-width="10" stroke-linecap="round"/>
      <path d="M-120,-60 C-60,-80 60,-80 120,-60 C120,40 60,120 30,160 L-30,160 C-60,120 -120,40 -120,-60 Z" fill="{ROSE}" stroke="{ROSE_D}" stroke-width="6"/>
      <path d="M-60,-30 C-20,-40 20,-40 60,-30 C55,40 20,90 0,110 C-20,90 -55,40 -60,-30 Z" fill="#f6c9cd"/>
      <ellipse cx="-250" cy="40" rx="80" ry="55" fill="#f3b8be" stroke="{ROSE_D}" stroke-width="6"/>
      <circle cx="-275" cy="30" r="12" fill="#fbe3e5"/><circle cx="-235" cy="62" r="9" fill="#fbe3e5"/>
      <path d="M-215,0 C-190,-30 -150,-25 -150,10 C-120,20 -130,70 -165,72 C-175,105 -230,100 -225,70 C-255,55 -245,15 -215,0 Z" fill="{PURPLE}" opacity="0.9"/>
      <circle cx="-185" cy="35" r="7" fill="#ffffff" opacity="0.5"/><circle cx="-200" cy="62" r="5" fill="#ffffff" opacity="0.5"/>
    </g>""")
    # EVs streaming from tumour into vessel
    for i, (x, y, r) in enumerate([(360, 420, 13), (400, 470, 11), (375, 520, 12), (430, 560, 10), (470, 610, 12), (540, 650, 11), (470, 625, 13), (560, 660, 12), (650, 630, 11), (740, 660, 12), (830, 640, 13), (920, 670, 11)]):
        b.append(ev(x, y, r, purple=(i % 3 != 1), rot=i * 25))
    b.append(arrow(320, 395, 345, 470, curve=-20))
    # blood tube centre-right
    b.append(blood_tube(1080, 250, 1.0))
    b.append(arrow(960, 600, 1030, 470, curve=40))
    # magnifier right
    b.append(magnifier(1370, 330, 125))
    b.append(arrow(1150, 300, 1225, 320, curve=20))
    return svg("".join(b), zoom=1.04, cx=875, cy=465)


# ------------------------------------------------------------- 2. pregnancy / placenta
def pregnancy():
    b = []
    b.append(vessel(600, 780, seed=7, rbcs=11, evs=0))
    # placenta disc with villous tree (left)
    rnd = random.Random(11)
    villi = []

    def branch(x, y, ang, length, depth):
        if depth == 0:
            villi.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{ROSE_D}" opacity="0.8"/>')
            return
        x2 = x + length * math.cos(math.radians(ang))
        y2 = y + length * math.sin(math.radians(ang))
        villi.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{ROSE_D}" stroke-width="{depth*2.6:.1f}" stroke-linecap="round"/>')
        for d in (-28, 26):
            branch(x2, y2, ang + d + rnd.uniform(-8, 8), length * 0.72, depth - 1)

    for a in range(35, 150, 22):
        branch(330, 210, a, 70, 4)
    b.append(f"""<g filter="url(#soft)">
      <path d="M120,260 C120,150 540,150 540,260 C540,420 470,470 330,470 C190,470 120,420 120,260 Z" fill="{ROSE}" stroke="{ROSE_D}" stroke-width="7"/>
      <path d="M150,262 C160,190 500,190 510,262" fill="none" stroke="#f6c9cd" stroke-width="14"/>
      {''.join(villi)}
      <path d="M330,210 C330,140 300,110 330,60 C360,10 330,-20 345,-40" fill="none" stroke="{TEAL_D}" stroke-width="22" stroke-linecap="round"/>
      <path d="M330,210 C330,140 300,110 330,60 C360,10 330,-20 345,-40" fill="none" stroke="{TEAL_L}" stroke-width="8" stroke-linecap="round" stroke-dasharray="14 12"/>
    </g>""")
    # EVs leaving placenta into maternal blood
    for i, (x, y, r) in enumerate([(300, 500, 12), (360, 540, 11), (330, 590, 13), (420, 640, 12), (520, 670, 11), (620, 650, 13), (720, 690, 12), (820, 660, 11), (930, 700, 12), (1040, 670, 13)]):
        b.append(ev(x, y, r, purple=(i % 2 == 0), rot=i * 30))
    b.append(arrow(470, 470, 520, 600, curve=-30))
    # target tissues on the right: adipocytes + endothelium
    adip = []
    for cx, cy, r in [(1230, 260, 70), (1360, 230, 62), (1330, 350, 72), (1200, 390, 60), (1460, 320, 58), (1460, 440, 55), (1330, 470, 52)]:
        adip.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff6dc" stroke="#e0a43a" stroke-width="6"/>')
        adip.append(f'<ellipse cx="{cx + r*0.55:.0f}" cy="{cy + r*0.35:.0f}" rx="{r*0.2:.0f}" ry="{r*0.12:.0f}" fill="#e0a43a" opacity="0.8"/>')
    b.append(f'<g filter="url(#soft)">{"".join(adip)}</g>')
    b.append(ev(1270, 320, 14, True, 10))
    b.append(ev(1400, 400, 13, False, 40))
    b.append(arrow(1120, 640, 1200, 470, curve=40))
    return svg("".join(b), zoom=1.05, cx=822, cy=430)


# ----------------------------------------------------------------- 3. methods workflow
def methods():
    b = []
    y = 470
    # 1 plasma tube
    b.append(f"""<g transform="translate(150,{y-170})" filter="url(#soft)">
      <rect x="-42" y="0" width="84" height="290" rx="40" fill="#ffffff" stroke="{INK}" stroke-opacity="0.35" stroke-width="5"/>
      <path d="M-37,120 L37,120 L37,250 Q37,285 0,285 Q-37,285 -37,250 Z" fill="#f2d27a"/>
      <rect x="-52" y="-46" width="104" height="58" rx="11" fill="{PURPLE}"/>
      {ev(-12,170,9)}{ev(14,215,8,True)}{ev(-8,250,7)}
    </g>""")
    b.append(arrow(215, y, 300, y))
    # 2 SEC column
    beads = "".join(
        f'<circle cx="{-30 + (i % 4) * 20 + (10 if (i // 4) % 2 else 0)}" cy="{40 + (i // 4) * 20}" r="9" fill="{TEAL_L}" stroke="{TEAL}" stroke-width="2"/>'
        for i in range(44)
    )
    b.append(f"""<g transform="translate(395,{y-230})" filter="url(#soft)">
      <rect x="-50" y="0" width="100" height="270" rx="10" fill="#ffffff" stroke="{INK}" stroke-opacity="0.35" stroke-width="5"/>
      <g clip-path="inset(0)">{beads}</g>
      <path d="M-50,270 L-12,330 L12,330 L50,270 Z" fill="#ffffff" stroke="{INK}" stroke-opacity="0.35" stroke-width="5"/>
      <rect x="-8" y="330" width="16" height="50" fill="#ffffff" stroke="{INK}" stroke-opacity="0.35" stroke-width="4"/>
      {ev(0, 420, 13)}
    </g>""")
    # 2b magnetic beads capturing EVs
    b.append(f"""<g transform="translate(600,{y})" filter="url(#soft)">
      <circle r="58" fill="#7f8c8d"/><circle cx="-18" cy="-20" r="16" fill="#ffffff" opacity="0.35"/>
      {ev(0,-78,15)}{ev(70,-30,14,True)}{ev(62,48,15)}{ev(-12,80,14,True)}{ev(-72,26,14)}{ev(-60,-55,13,True)}
    </g>""")
    b.append(arrow(470, y, 515, y))
    b.append(arrow(700, y, 805, y))
    # 4 mass spectrometer
    b.append(f"""<g transform="translate(820,{y-150})" filter="url(#soft)">
      <rect x="0" y="0" width="250" height="300" rx="24" fill="#ffffff" stroke="{INK}" stroke-opacity="0.35" stroke-width="5"/>
      <rect x="22" y="24" width="206" height="60" rx="10" fill="{INK}"/>
      <rect x="34" y="38" width="120" height="10" rx="5" fill="{TEAL}"/>
      <rect x="34" y="56" width="80" height="10" rx="5" fill="{TEAL_L}"/>
      <ellipse cx="125" cy="180" rx="70" ry="40" fill="none" stroke="{TEAL}" stroke-width="10"/>
      <ellipse cx="125" cy="180" rx="22" ry="12" fill="{TEAL_D}"/>
      <rect x="22" y="250" width="206" height="26" rx="8" fill="{TEAL_L}"/>
    </g>""")
    b.append(arrow(1080, y, 1140, y))
    # 5 data: spectrum + heatmap on a screen
    peaks = []
    rnd = random.Random(9)
    for i in range(16):
        h = rnd.choice([30, 45, 60, 80, 110, 150, 40, 25])
        x = 1175 + i * 12
        peaks.append(f'<line x1="{x}" y1="{y-20}" x2="{x}" y2="{y-20-h}" stroke="{TEAL_D}" stroke-width="5" stroke-linecap="round"/>')
    cells = []
    palette = ["#2698ba", "#7cc3d8", "#cfeaf2", "#f3d9ef", "#c77dbb", "#8e44ad"]
    for r in range(4):
        for c in range(8):
            cells.append(f'<rect x="{1172 + c*24}" y="{y + 20 + r*24}" width="22" height="22" rx="3" fill="{rnd.choice(palette)}"/>')
    b.append(f"""<g filter="url(#soft)">
      <rect x="1150" y="{y-200}" width="240" height="340" rx="20" fill="#ffffff" stroke="{INK}" stroke-opacity="0.35" stroke-width="5"/>
    </g>
    <line x1="1168" y1="{y-18}" x2="1370" y2="{y-18}" stroke="{INK}" stroke-opacity="0.4" stroke-width="3"/>
    {''.join(peaks)}{''.join(cells)}""")
    return svg("".join(b), zoom=1.16, cx=742, cy=475)


if __name__ == "__main__":
    for name, fn in [("project_ovarian_cancer", ovarian), ("project_pregnancy", pregnancy), ("project_methods", methods)]:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", name)
