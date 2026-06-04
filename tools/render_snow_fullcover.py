"""DESIGN EXPLORATION — extend Pip's snow accumulation past today's max all
the way to FULLY COVERED, then read Pip as a SNOWMAN. Throwaway sheet tool;
touches NO game code.

CORRECTED DIRECTION (round 3): there is exactly ONE snow look — the shipped
snow_fx.py W2 "sculpted blanket". We do NOT invent new finishes. We take the
LITERAL per-column technique from snow_fx.get_snow_overlay (off-white body +
bright WHITE crest over the top 18%% + cool-blue BLUE under-edge over the
bottom 26%%, with the CORNICE rear overhang, the ripple `nb`, the depth `d`
with its inward `bulge`, and the rear taper) and continue it UPWARD by lifting
only the head cap until the whole silhouette — nape, crown, face, beak — is
buried under the SAME blanket. Nothing else about the snow changes.

Once fully covered, Pip reads as a snowman: a carrot nose where the beak was,
coal eyes/smile, optional buttons + a red-and-white scarf. The five versions
share the IDENTICAL faithful snow base and differ ONLY in that snowman
treatment.

The technique stays numpy-free / pure pygame so it ports straight into
snow_fx.py later.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_3.png
"""
from __future__ import annotations

import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game.entities import Bird
from game import parrot, snow_fx
from game.draw import make_gradient_surface

OUT_DIR = os.path.join(ROOT, "docs", "snow_full_cover")
os.makedirs(OUT_DIR, exist_ok=True)

# Snow palette — taken VERBATIM from snow_fx so the extended blanket is the
# shipped look, just deeper.
WHITE = snow_fx.WHITE
OFF = snow_fx.OFF
BLUE = snow_fx.BLUE
SHADOW = snow_fx.SHADOW

# Snowman material palette (drawn ON TOP of the finished snow blanket).
CARROT = (240, 130, 32)          # carrot nose body
CARROT_HI = (255, 176, 92)       # lit top edge of the carrot
CARROT_RIDGE = (196, 92, 18)     # darker segment ridges
COAL = (28, 30, 38)              # eyes / smile / buttons
COAL_HI = (96, 100, 112)         # tiny lit edge on coal
GLINT = (236, 244, 252)          # eye sparkle (same as OFF-white snow)
SCARF_RED = (212, 46, 52)        # snowman scarf red
SCARF_WHITE = (244, 248, 252)    # scarf white stripe
ROSY = (244, 176, 184)           # rosy snow cheek (V3)
PIP_GREEN = (74, 176, 96)        # macaw crown tuft peek (V4)
PIP_BLUE = (66, 132, 224)        # macaw wing-tip peek (V4)
PIP_SCARLET = (240, 55, 55)      # shipped BIRD_RED (V4 scarf)

# Silhouette landmarks on the 64x60 _REF_FRAME (level-wing), side-profile
# facing RIGHT. From parrot._build_frame_scaled: beak quad (55,21)->(61,24)->
# (58,28)->(52,26); aviator at (50,20); head ellipse centre (47,21) r12;
# crown top ~y14; neck/nape break ~x40-46.
BEAK_TIP = (61, 24)              # forward beak point — carrot tip lives here
BEAK_BASE = (52, 25)             # where the beak meets the face
EYE_PX = (49, 18)               # coal eye sits over the aviator, slightly up
CROWN_PX = (45, 15)              # top of the head
NECK_PX = (40, 31)              # neck band between head and body
CHEST_PX = (30, 38)             # chest centre for buttons

ZOOM = 6                         # sprite is 64x60; render big for detail


# ── THE faithful W2 blanket, extended to full cover ──────────────────────────
# This is snow_fx.get_snow_overlay's body verbatim, with the SINGLE sanctioned
# change: the head cap `7.0 + hi*11*(1-headfrac)` is lifted as `extra` 0->1 so
# the SAME three-line blanket (OFF body + WHITE crest over top 18%% + BLUE
# under-edge over bottom 26%%), SAME cornice, SAME ripple, SAME depth profile,
# simply keeps climbing up the face and over the beak until Pip is buried.
# extra=0 reproduces the shipped peak; extra=1 buries the whole silhouette.
def _full_cover_overlay(extra):
    top, x_min, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    if x_min < 0:
        return None
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    taper_w = 13.0
    load = 1.0
    drew = False
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        xf = x / w
        # Coverage spreads forward as `extra` grows: the shipped rear-first
        # onset threshold (0.55*xf) is relaxed so the front/beak columns reach
        # full coverage too. At extra=0 this is the shipped _cov(xf, 1.0).
        thr = 0.55 * xf * (1.0 - 0.9 * extra)
        cov = 0.0 if load <= thr else min(1.0, (load - thr) / (1.0 - thr))
        if cov <= 0.0:
            continue
        rear = 1.0 - xf
        bulge = math.exp(-((xf - 0.40) / 0.26) ** 2)        # inward hump
        d = snow_fx.MAXD * cov * (0.50 + 0.45 * rear + 0.45 * bulge)
        if xf > 0.60:
            # Shipped head cap, with its ceiling LIFTED by `extra`. (1-headfrac)
            # keeps the very beak-tip the last thing buried so the parrot
            # silhouette holds longest, then the carrot replaces it on top.
            headfrac = (xf - 0.60) / 0.40                   # 0 nape .. 1 beak
            base_cap = 7.0 + 11.0 * (1.0 - headfrac)
            cap = base_cap + extra * (16.0 + 11.0 * (1.0 - headfrac))
            d = min(d, cap)
        d *= snow_fx._smooth((x - x_min) / taper_w)         # rear-end slope
        if d < 0.6:
            continue
        over = snow_fx.CORNICE * rear * snow_fx._smooth((x - x_min) / taper_w)
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yt + d + (nb - 0.5) * 2.4
        # W2 sculpted blanket — IDENTICAL to snow_fx: clean OFF fill + bright
        # WHITE crest over the top 18%% + cool-blue BLUE under-edge bottom 26%%.
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)
        drew = True
    if not drew:
        return None
    # At full cover the front face/jaw below the top silhouette still shows the
    # bird. Run the SAME 3-line blanket DOWN the front columns so the whole
    # body fills with the shipped snow (off body + cool-blue base), enclosing
    # Pip rather than only top-capping him. Same palette, no new technique.
    if extra > 0.55:
        amt = (extra - 0.55) / 0.45
        for x in range(w):
            yt = top[x]
            if yt < 0:
                continue
            xf = x / w
            # front-weighted skim depth so the lower face/chest fills in
            depth = (10.0 + 16.0 * amt) * (0.45 + 0.6 * max(0.0, xf - 0.15))
            if depth < 1.5:
                continue
            ytop = yt + 2
            ybot = yt + depth
            pygame.draw.line(ov, (*OFF, 255), (x, int(ytop)), (x, int(ybot)), 1)
            pygame.draw.line(ov, (*BLUE, 255),
                             (x, int(ybot - depth * 0.30)), (x, int(ybot)), 1)
    return ov


def _native_size():
    _, _, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    return w, h


# ── snowman face parts (sprite-local, numpy-free) ────────────────────────────
def _carrot(ov, *, angle=0.0, length=12.0, droop=2.5):
    """Orange cone where the beak is, pointing forward/down. Darker-orange
    segment ridges + a lighter lit top edge. Covers the gold beak."""
    bx, by = BEAK_BASE
    # tip extends forward (and a little down) from the face
    tx = bx + length * math.cos(math.radians(angle)) + 3
    ty = by + length * math.sin(math.radians(angle)) + droop
    half = 3.4                                       # cone half-width at the base
    # base sits on the snow over the face; perpendicular spread
    ang = math.atan2(ty - by, tx - bx)
    nx, ny = -math.sin(ang), math.cos(ang)
    b1 = (bx + nx * half, by + ny * half)
    b2 = (bx - nx * half, by - ny * half)
    tip = (tx, ty)
    pygame.draw.polygon(ov, CARROT, [b1, tip, b2])
    pygame.draw.polygon(ov, CARROT_RIDGE, [b1, tip, b2], 1)
    # segment ridges across the cone (3 short darker arcs)
    for t in (0.30, 0.55, 0.78):
        cx = bx + (tx - bx) * t
        cy = by + (ty - by) * t
        hw = half * (1.0 - t) + 0.6
        pygame.draw.line(ov, CARROT_RIDGE,
                         (cx + nx * hw, cy + ny * hw),
                         (cx - nx * hw, cy - ny * hw), 1)
    # lit top edge
    pygame.draw.line(ov, CARROT_HI, b1, tip, 1)


def _coal_dot(ov, x, y, r, *, glint=False):
    pygame.draw.circle(ov, COAL, (int(x), int(y)), r)
    pygame.draw.circle(ov, COAL_HI, (int(x), int(y)), r, 1)
    if glint:
        pygame.draw.circle(ov, GLINT, (int(x - r * 0.4), int(y - r * 0.4)), 1)


def _coal_eye(ov, *, round_eye=True, glint=True):
    ex, ey = EYE_PX
    if round_eye:
        _coal_dot(ov, ex, ey, 3, glint=glint)
    else:
        # flat button eye with a tiny stitch cross (V2)
        pygame.draw.rect(ov, COAL, (ex - 3, ey - 3, 6, 6), border_radius=1)
        pygame.draw.line(ov, COAL_HI, (ex - 2, ey), (ex + 2, ey), 1)
        pygame.draw.line(ov, COAL_HI, (ex, ey - 2), (ex, ey + 2), 1)


def _coal_smile(ov, *, pebbles=3, wide=False):
    """Short downward arc of small coal dots below the carrot where it reads
    in the right-facing profile (in front of / below the nose base)."""
    bx, by = BEAK_BASE
    sx = bx + 4
    sy = by + 6
    span = 9 if wide else 6
    n = 5 if wide else pebbles
    for i in range(n):
        t = i / (n - 1)
        px = sx + (t - 0.5) * span
        py = sy + math.sin(t * math.pi) * 2.0       # gentle smile curve
        _coal_dot(ov, px, py, 1)


def _buttons(ov, n=2):
    cx, cy = CHEST_PX
    for i in range(n):
        _coal_dot(ov, cx + i * 1.5, cy + i * 6.5, 2)


def _scarf(ov, *, red=SCARF_RED, white=SCARF_WHITE, tails=1, thin=False):
    """Red-and-white band wrapped at the neck with a fluttering tail that
    streams left->right with the tailwind."""
    nx, ny = NECK_PX
    band_h = 4 if thin else 6
    # the wrap band across the neck (angled to follow the profile)
    for i in range(band_h):
        col = red if (i // 2) % 2 == 0 else white
        pygame.draw.line(ov, col, (nx - 7, ny - 2 + i), (nx + 8, ny - 4 + i), 1)
    # fluttering tail(s) streaming forward-down with the wind
    def _tail(y_off, ln):
        px, py = nx + 6, ny + y_off
        seg = ln
        for j in range(seg):
            t = j / seg
            wob = math.sin(t * 6.0) * 2.0           # flutter
            x0 = px + t * 14
            y0 = py + t * 9 + wob
            col = red if (j // 2) % 2 == 0 else white
            pygame.draw.line(ov, col, (x0, y0), (x0 + 2, y0 + 1), 3 if not thin else 2)
    _tail(2, 7)
    if tails > 1:
        _tail(5, 5)


def _rosy_cheeks(ov):
    cx, cy = EYE_PX
    glow = pygame.Surface((10, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*ROSY, 120), glow.get_rect())
    ov.blit(glow, (cx - 7, cy + 4))


def _cowlick(ov):
    """A small curled snow tuft on top of the crown (V5)."""
    cx, cy = CROWN_PX
    pts = [(cx, cy), (cx - 2, cy - 5), (cx + 2, cy - 7), (cx + 3, cy - 3)]
    pygame.draw.lines(ov, WHITE, False, pts, 2)
    pygame.draw.circle(ov, OFF, (cx + 3, cy - 3), 2)


def _pip_peeks(ov):
    """V4 only: a green macaw crown tuft + a blue wing-tip of Pip peek through
    the snow, tying the snowman back to the bird."""
    cx, cy = CROWN_PX
    # green crown tuft poking out of the top
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx - 4, cy), (cx - 6, cy - 6), (cx - 2, cy - 3)])
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx - 1, cy - 1), (cx, cy - 7), (cx + 3, cy - 2)])
    # blue wing-tip peeking at mid-body rear
    pygame.draw.polygon(ov, PIP_BLUE,
                        [(24, 30), (16, 33), (24, 36)])


# ── the 5 snowman treatments (snow base IDENTICAL; vary the face only) ───────
def v1_classic(ov):
    _scarf(ov, tails=1)
    _carrot(ov, angle=4, length=12, droop=2.5)
    _coal_eye(ov, round_eye=True, glint=True)
    _coal_smile(ov, pebbles=3)
    _buttons(ov, n=2)


def v2_buttons_noscarf(ov):
    _carrot(ov, angle=4, length=12, droop=2.5)
    _coal_eye(ov, round_eye=False, glint=False)     # flat button eye + stitch
    _coal_smile(ov, pebbles=3)
    _buttons(ov, n=2)


def v3_minimal_cute(ov):
    _scarf(ov, tails=1, thin=True)
    _rosy_cheeks(ov)
    _carrot(ov, angle=6, length=11, droop=2.0)
    _coal_eye(ov, round_eye=True, glint=True)       # eyes + carrot only


def v4_hybrid(ov):
    _pip_peeks(ov)                                  # green tuft + blue wing-tip
    _scarf(ov, red=PIP_SCARLET, white=SCARF_WHITE, tails=1)
    _carrot(ov, angle=4, length=12, droop=2.5)
    _coal_eye(ov, round_eye=True, glint=True)


def v5_expressive(ov):
    _cowlick(ov)
    _scarf(ov, tails=2)
    _carrot(ov, angle=10, length=13, droop=1.0)     # jaunty angled carrot
    _coal_eye(ov, round_eye=True, glint=True)
    _coal_smile(ov, wide=True)                      # wide pebble grin


# ── parcel snow: extend the shipped parcel cap to full cover too ──────────────
def parcel_overlay(mode, extra):
    """W2 snow cap on the parcel, deepened with `extra` — the same shipped
    parcel technique (snow_fx.get_parcel_snow), just thicker. Parcel stays
    visibly snow-capped in every cell."""
    top, x_min, w, h = snow_fx._parcel_topline(mode)
    if x_min < 0:
        return None
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    taper_w = 4.0
    depth = snow_fx.PARCEL_MAXD * (1.0 + 1.2 * extra)
    for x in range(w):
        yt = top[x]
        if yt < 0:
            continue
        rear = 1.0 - x / w
        te = snow_fx._smooth((x - x_min) / taper_w)
        d = depth * (0.65 + 0.5 * rear) * te
        if d < 0.6:
            continue
        nb = math.sin(x * 1.7) * 0.25 + 0.5
        y0 = yt - 0.6 * te
        y1 = yt + d + (nb - 0.5) * 1.4
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.22)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.3)), (x, int(y1)), 1)
    return ov


# ── compose one Pip cell ──────────────────────────────────────────────────────
def render_cell(extra, *, face_fn=None):
    """Bird sprite + extended W2 blanket (+ optional snowman face) + parcel +
    parcel snow. Mirrors Bird.draw's compositing order without touching game
    code. face_fn draws the snowman parts onto the snow overlay."""
    nw, nh = _native_size()
    pad = 6
    cw, ch = nw + pad * 2, nh + pad * 2 + 14
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    spr = parrot._get_frames()[snow_fx._REF_FRAME]
    bx, by = pad, pad
    parcel = parrot.get_parcel("normal")
    pw, ph = parcel.get_size()
    pcx = bx + nw / 2
    pcy = by + nh / 2 + 12
    cell.blit(spr, (bx, by))
    cell.blit(parcel, (int(pcx - pw / 2), int(pcy - ph / 2)))
    pov = parcel_overlay("normal", extra)
    if pov is not None:
        cell.blit(pov, (int(pcx - pw / 2), int(pcy - ph / 2)))
    ov = _full_cover_overlay(extra)
    if ov is not None:
        if face_fn is not None:
            face_fn(ov)                              # snowman parts on the snow
        cell.blit(ov, (bx, by))
    return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)


# ── reference row via the REAL Bird.draw ─────────────────────────────────────
def render_reference(load):
    nw, nh = _native_size()
    pad = 6
    cw, ch = nw + pad * 2, nh + pad * 2 + 14
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    b = Bird()
    b.x = pad + nw / 2
    b.y = pad + nh / 2
    b.vy = 0  # tilt_deg is derived from vy; 0 = level
    b.snow_load = load
    b.draw(cell, 0, 0)
    return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)


# ── backdrops ────────────────────────────────────────────────────────────────
def neutral_panel(w, h):
    return make_gradient_surface(w, h, [(0.0, (34, 40, 54)), (1.0, (22, 26, 36))])


def whiteout_panel(w, h):
    s = make_gradient_surface(w, h, [(0.0, (214, 224, 236)), (1.0, (188, 200, 218))])
    for i in range(int(w * h / 90)):
        x = (math.sin(i * 12.9898) * 43758.5) % 1.0 * w
        y = (math.sin(i * 78.233) * 12543.7) % 1.0 * h
        r = 1 + int((math.sin(i * 3.1) * 0.5 + 0.5) * 2)
        a = 120 + int((math.sin(i * 1.7) * 0.5 + 0.5) * 100)
        fl = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(fl, (255, 255, 255, a), (r, r), r)
        s.blit(fl, (int(x), int(y)))
    return s


def on_panel(cell, panel_fn):
    w, h = cell.get_size()
    panel = panel_fn(w, h)
    panel.blit(cell, (0, 0))
    return panel


# ── sheet layout ─────────────────────────────────────────────────────────────
VERSIONS = [
    ("V1 - Classic",
     "round coal eyes + glint, carrot, 3-coal smile, red-white scarf+tail, 2 buttons",
     v1_classic),
    ("V2 - Buttons, no scarf",
     "flat button eyes (stitch cross), carrot, coal smile, NO scarf - cleanest read",
     v2_buttons_noscarf),
    ("V3 - Minimal cute",
     "2 coal eyes + carrot + rosy cheeks + thin scarf, no mouth/buttons - most legible",
     v3_minimal_cute),
    ("V4 - Pip-snowman hybrid",
     "coal eyes + carrot BUT green crown tuft + blue wing-tip peek; Pip-scarlet scarf",
     v4_hybrid),
    ("V5 - Expressive",
     "coal eyes + jaunty carrot + wide pebble grin + 2-tail scarf + snow cowlick",
     v5_expressive),
]


def main():
    label_w = 250
    gap = 8
    pad_out = 18
    title_h = 80

    _, (cw, ch) = render_reference(1.0)
    cell_w, cell_h = cw * ZOOM, ch * ZOOM

    ref_loads = [0.0, 0.35, 0.70, 1.00]
    ref_cols = len(ref_loads)
    ver_cols = 4

    cols_max = max(ref_cols, ver_cols)
    row_h = cell_h + 30
    sheet_w = label_w + cols_max * (cell_w + gap) + pad_out * 2
    rows = 1 + len(VERSIONS)
    sheet_h = title_h + rows * (row_h + gap) + pad_out

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((14, 16, 24))

    fbig = pygame.font.SysFont("Arial", 26, bold=True)
    frow = pygame.font.SysFont("Arial", 17, bold=True)
    fnote = pygame.font.SysFont("Arial", 13)
    fcell = pygame.font.SysFont("Arial", 13, bold=True)

    GOLD = (240, 206, 120)
    WLBL = (228, 236, 248)
    DIM = (170, 184, 206)

    sheet.blit(fbig.render(
        "Pip - snow FULL COVER -> SNOWMAN  (faithful shipped W2 blanket, extended)",
        True, GOLD), (pad_out, 14))
    sheet.blit(fnote.render(
        "Snow = the LITERAL snow_fx W2 blanket (OFF body + WHITE crest + BLUE "
        "under-edge, same cornice/ripple), head cap lifted until Pip is buried. "
        "Compare each row's no-face cell to the reference snow. Then snowman face on top.",
        True, DIM), (pad_out, 48))

    y = title_h

    def cell_label(txt, x, yy, col=WLBL):
        sheet.blit(fcell.render(txt, True, col), (x + 4, yy))

    # ── reference row ──
    sheet.blit(frow.render("CURRENT - shipped", True, GOLD), (pad_out, y + 14))
    sheet.blit(fnote.render("(real Bird.draw; stops with face readable)", True, DIM),
               (pad_out, y + 36))
    cx = label_w + pad_out
    for ld in ref_loads:
        cell, _ = render_reference(ld)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label(f"load {ld:.2f}", cx, y)
        cx += cell_w + gap
    y += row_h + gap + 16

    # ── version rows ──
    # Each row: [current max load 1.00 — real Bird.draw] [FULLY covered, NO
    # face yet — proves snow matches reference] [SNOWMAN dark] [SNOWMAN whiteout]
    for name, note, face_fn in VERSIONS:
        sheet.blit(frow.render(name, True, GOLD), (pad_out, y + 12))
        words = note.split(" ")
        line1, line2, line3 = "", "", ""
        for wword in words:
            if len(line1) < 34:
                line1 += wword + " "
            elif len(line2) < 34:
                line2 += wword + " "
            else:
                line3 += wword + " "
        sheet.blit(fnote.render(line1.strip(), True, DIM), (pad_out, y + 36))
        sheet.blit(fnote.render(line2.strip(), True, DIM), (pad_out, y + 52))
        sheet.blit(fnote.render(line3.strip(), True, DIM), (pad_out, y + 68))

        cx = label_w + pad_out
        # cell 1: real shipped Bird.draw(load=1.0) — continuity anchor
        ref_cell, _ = render_reference(1.0)
        panel = on_panel(ref_cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("current max (load 1.00)", cx, y)
        cx += cell_w + gap
        # cell 2: FULLY covered, faithful W2 blanket, NO face yet
        cell, _ = render_cell(1.0, face_fn=None)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("FULLY COVERED (no face)", cx, y)
        cx += cell_w + gap
        # cell 3: SNOWMAN, dark panel
        snow_cell, _ = render_cell(1.0, face_fn=face_fn)
        dark = on_panel(snow_cell.copy(), neutral_panel)
        sheet.blit(dark, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("SNOWMAN / dark", cx, y, GOLD)
        cx += cell_w + gap
        # cell 4: SNOWMAN, whiteout panel
        white = on_panel(snow_cell.copy(), whiteout_panel)
        sheet.blit(white, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("SNOWMAN / whiteout", cx, y, GOLD)

        y += row_h + gap + 26

    out = os.path.join(OUT_DIR, "round_3.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
