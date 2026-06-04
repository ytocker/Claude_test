"""DESIGN EXPLORATION — extend Pip's snow accumulation past today's max all
the way to FULLY COVERED, then read Pip as a SNOWMAN. Throwaway sheet tool;
touches NO game code.

CORRECTED DIRECTION (round 4): there is exactly ONE snow look — the shipped
snow_fx.py W2 "sculpted blanket". We do NOT invent new finishes. We take the
LITERAL per-column technique from snow_fx.get_snow_overlay (off-white body +
bright WHITE crest over the top 18%% + cool-blue BLUE under-edge over the
bottom 26%%, with the CORNICE rear overhang and the ripple `nb`) and apply it
to the WHOLE ENCLOSING CONTOUR of Pip+parcel, not just the topline blanket.

Round 3 only draped a top-blanket on the silhouette's topline, leaving a hard
band of red belly + blue wing + gold beak + orange parcel exposed below it —
it failed "fully covered". Round 4 fix (the gate): at full load we take the
combined Pip(+parcel) alpha mask, dilate/smooth it a few px into a rounded
snow-lump outer contour, fill the ENTIRE contour OFF-white, then shade each
filled column with the SAME W2 recipe — WHITE crest over the top ~18%%, BLUE
under-edge over the bottom ~26%%, cornice rear overhang, sine ripple on the
top edge. The result is a clean white parrot-shaped mound with NO bird colour
showing anywhere; the snowman face is then drawn on top of that mound.

Once fully covered, Pip reads as a snowman: a carrot nose where the beak was,
coal eyes/smile, optional buttons + a red-and-white scarf. The five versions
share the IDENTICAL faithful snow base and differ ONLY in that snowman
treatment.

The technique stays numpy-free / pure pygame so it ports straight into
snow_fx.py later.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_4.png
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
#
# Round-4 snowman geometry: the carrot ROOT sits where the beak met the face,
# and the coal eye sits JUST above/behind that root so eye + carrot read as one
# tight triangle on the white head. Accessories land on the SNOW (neck pinch /
# white belly), never on bird colour (it's all buried now anyway).
BEAK_BASE = (51, 25)             # carrot root — base of the nose on the head
EYE_PX = (47, 22)               # coal eye just above/behind the carrot root
CROWN_PX = (45, 14)              # top of the head mound
NECK_PX = (42, 30)              # snow waist (pinch) between head and body
CHEST_PX = (33, 36)             # belly centre for buttons, below the neck

ZOOM = 6                         # sprite is 64x60; render big for detail


# ── per-column envelope of a combined alpha silhouette ───────────────────────
# Round-4 gate: the snow must ENCLOSE the whole shape, so we work from the top
# AND bottom of the combined Pip(+parcel) alpha mask rather than only the
# topline. `_envelope` returns, per column, the first/last opaque row of a
# composited surface (the rounded snow-lump outer contour after dilation).
def _envelope(surf, thresh=50):
    w, h = surf.get_size()
    mask = pygame.mask.from_surface(surf, thresh)
    top = [-1] * w
    bot = [-1] * w
    x_min, x_max = -1, -1
    for x in range(w):
        for y in range(h):
            if mask.get_at((x, y)):
                top[x] = y
                if x_min < 0:
                    x_min = x
                x_max = x
                break
        if top[x] < 0:
            continue
        for y in range(h - 1, top[x] - 1, -1):
            if mask.get_at((x, y)):
                bot[x] = y
                break
    return top, bot, x_min, x_max, w, h


def _dilate_envelope(top, bot, x_min, x_max, w, h, grow=2, smooth=2):
    """Grow the silhouette a few px outward and round its corners so the snow
    reads as one soft snow-lump, not a tight shrink-wrap of the bird. We pad
    each column's top up / bottom down by `grow`, pull the empty columns just
    outside the shape inward to the nearest filled neighbour (so the rear point
    and beak round off), then box-smooth the top/bottom lines `smooth` times."""
    ntop = list(top)
    nbot = list(bot)
    # extend the occupied span outward by `grow` columns at each horizontal end
    nx_min = max(0, x_min - grow)
    nx_max = min(w - 1, x_max + grow)
    for x in range(nx_min, nx_max + 1):
        if top[x] >= 0:
            ntop[x] = top[x] - grow
            nbot[x] = bot[x] + grow
        else:
            # column just outside the shape: borrow the nearest filled edge so
            # the contour closes over the tips with a rounded shoulder
            lo = next((top[k] for k in range(x, nx_max + 1) if top[k] >= 0), -1)
            hi = next((top[k] for k in range(x, -1, -1) if top[k] >= 0), -1)
            lb = next((bot[k] for k in range(x, nx_max + 1) if bot[k] >= 0), -1)
            hb = next((bot[k] for k in range(x, -1, -1) if bot[k] >= 0), -1)
            t = max(t0 for t0 in (lo, hi) if t0 >= 0) if (lo >= 0 or hi >= 0) else -1
            bvals = [v for v in (lb, hb) if v >= 0]
            b = min(bvals) if bvals else -1
            if t >= 0 and b >= 0:
                mid = (t + b) * 0.5
                ntop[x] = int(mid - 1)
                nbot[x] = int(mid + 1)
    for _ in range(smooth):
        st, sb = list(ntop), list(nbot)
        for x in range(nx_min, nx_max + 1):
            if ntop[x] < 0:
                continue
            ts = [ntop[k] for k in (x - 1, x, x + 1)
                  if 0 <= k < w and ntop[k] >= 0]
            bs = [nbot[k] for k in (x - 1, x, x + 1)
                  if 0 <= k < w and nbot[k] >= 0]
            st[x] = sum(ts) / len(ts)
            sb[x] = sum(bs) / len(bs)
        ntop, nbot = st, sb
    return ntop, nbot, nx_min, nx_max


# ── THE faithful W2 blanket, now wrapping the WHOLE enclosing contour ─────────
# We keep the shipped W2 recipe verbatim (OFF body + WHITE crest over the top
# 18%% of each filled column + cool-blue BLUE under-edge over the bottom 26%%,
# the CORNICE rear overhang, the ripple `nb`) but apply it down the FULL height
# of every column of the dilated Pip+parcel envelope. That buries the entire
# silhouette under one solid white snow mound — no bird colour shows through.
def _mound_overlay(silhouette):
    top, bot, x_min, x_max, w, h = _envelope(silhouette)
    if x_min < 0:
        return None
    top, bot, x_min, x_max = _dilate_envelope(top, bot, x_min, x_max, w, h)
    ov = pygame.Surface((w, h), pygame.SRCALPHA)
    span = max(1.0, float(x_max - x_min))
    taper_w = 13.0
    drew = False
    for x in range(w):
        yt = top[x]
        yb = bot[x]
        if yt < 0 or yb < 0 or yb <= yt:
            continue
        xf = (x - x_min) / span                              # 0 rear .. 1 front
        rear = 1.0 - xf
        # rear end still tapers to a rounded point (W2 cornice/slope cue)
        te = snow_fx._smooth((x - x_min) / taper_w)
        over = snow_fx.CORNICE * rear * te                   # cornice overhang
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yb + (nb - 0.5) * 2.4
        d = y1 - y0
        if d < 1.0:
            continue
        # W2 sculpted blanket — IDENTICAL palette/proportions to snow_fx, only
        # now spanning the full enclosing column: clean OFF fill + bright WHITE
        # crest over the top 18%% + cool-blue BLUE under-edge over bottom 26%%.
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)
        drew = True
    if not drew:
        return None
    return ov


def _native_size():
    _, _, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    return w, h


# ── snowman face parts (sprite-local + (ox,oy) cell offset, numpy-free) ──────
# Every part takes an `ox,oy` so the landmarks (in _REF_FRAME sprite space) land
# on the mound, which lives in cell space. Faces draw ON the finished white
# mound; the eye sits with the carrot root, accessories sit on the snow.
def _carrot(ov, ox, oy, *, angle=6.0, length=12.0, droop=2.0):
    """Orange cone rooted at the nose, pointing forward/down. Darker segment
    ridges + a lit top edge. It is the snowman's single strongest read."""
    bx, by = BEAK_BASE[0] + ox, BEAK_BASE[1] + oy
    tx = bx + length * math.cos(math.radians(angle)) + 3
    ty = by + length * math.sin(math.radians(angle)) + droop
    half = 3.4
    ang = math.atan2(ty - by, tx - bx)
    nx, ny = -math.sin(ang), math.cos(ang)
    b1 = (bx + nx * half, by + ny * half)
    b2 = (bx - nx * half, by - ny * half)
    tip = (tx, ty)
    pygame.draw.polygon(ov, CARROT, [b1, tip, b2])
    pygame.draw.polygon(ov, CARROT_RIDGE, [b1, tip, b2], 1)
    for t in (0.30, 0.55, 0.78):
        cx = bx + (tx - bx) * t
        cy = by + (ty - by) * t
        hw = half * (1.0 - t) + 0.6
        pygame.draw.line(ov, CARROT_RIDGE,
                         (cx + nx * hw, cy + ny * hw),
                         (cx - nx * hw, cy - ny * hw), 1)
    pygame.draw.line(ov, CARROT_HI, b1, tip, 1)


def _coal_dot(ov, x, y, r, *, glint=False):
    pygame.draw.circle(ov, COAL, (int(x), int(y)), r)
    pygame.draw.circle(ov, COAL_HI, (int(x), int(y)), r, 1)
    if glint:
        pygame.draw.circle(ov, GLINT, (int(x - r * 0.4), int(y - r * 0.4)), 1)


def _coal_eye(ov, ox, oy, *, round_eye=True, glint=True, pair=False):
    """Coal eye just above/behind the carrot root so eye + nose read as one
    tight triangle on the white head. `pair` adds a small second coal behind it
    (the far eye in three-quarter read) for the cute cluster versions."""
    ex, ey = EYE_PX[0] + ox, EYE_PX[1] + oy
    if round_eye:
        _coal_dot(ov, ex, ey, 3, glint=glint)
        if pair:
            _coal_dot(ov, ex - 6, ey + 1, 2, glint=glint)   # far eye, smaller
    else:
        # flat black button eye with a tiny stitch cross (V2 lead)
        pygame.draw.rect(ov, COAL, (int(ex - 3), int(ey - 3), 6, 6), border_radius=1)
        pygame.draw.line(ov, COAL_HI, (ex - 2, ey), (ex + 2, ey), 1)
        pygame.draw.line(ov, COAL_HI, (ex, ey - 2), (ex, ey + 2), 1)
        if pair:
            pygame.draw.rect(ov, COAL, (int(ex - 9), int(ey - 2), 4, 4), border_radius=1)


def _brow(ov, ox, oy, tilt=1.0):
    """ONE subtle brow stroke above the eye (V5) for a touch of expression."""
    ex, ey = EYE_PX[0] + ox, EYE_PX[1] + oy
    pygame.draw.line(ov, COAL, (ex - 3, ey - 5 + tilt), (ex + 3, ey - 5 - tilt), 1)


def _coal_smile(ov, ox, oy, *, pebbles=3, wide=False):
    """Short upward smile of small coal dots below the carrot root."""
    bx, by = BEAK_BASE[0] + ox, BEAK_BASE[1] + oy
    sx = bx + 3
    sy = by + 7
    span = 9 if wide else 6
    n = 5 if wide else pebbles
    for i in range(n):
        t = i / (n - 1)
        px = sx + (t - 0.5) * span
        py = sy + math.sin(t * math.pi) * 2.0       # gentle smile curve
        _coal_dot(ov, px, py, 1)


def _buttons(ov, ox, oy, n=2):
    """Vertical coal buttons down the WHITE belly, below the neck pinch."""
    cx, cy = CHEST_PX[0] + ox, CHEST_PX[1] + oy
    for i in range(n):
        _coal_dot(ov, cx - i * 0.8, cy + i * 6.0, 2)


def _scarf(ov, ox, oy, *, red=SCARF_RED, white=SCARF_WHITE, tails=1, thin=False):
    """Red-and-white band wrapped at the WHITE neck pinch (between head and
    body) with a fluttering tail streaming forward with the tailwind. Lands on
    snow, never on the buried red belly."""
    nx, ny = NECK_PX[0] + ox, NECK_PX[1] + oy
    band_h = 4 if thin else 6
    for i in range(band_h):
        col = red if (i // 2) % 2 == 0 else white
        pygame.draw.line(ov, col, (nx - 7, ny - 2 + i), (nx + 8, ny - 4 + i), 1)

    def _tail(y_off, ln):
        px, py = nx + 6, ny + y_off
        for j in range(ln):
            t = j / ln
            wob = math.sin(t * 6.0) * 2.0           # flutter
            x0 = px + t * 13
            y0 = py + t * 9 + wob
            col = red if (j // 2) % 2 == 0 else white
            pygame.draw.line(ov, col, (x0, y0), (x0 + 2, y0 + 1), 2 if thin else 3)
    _tail(2, 7)
    if tails > 1:
        _tail(5, 5)


def _rosy_cheeks(ov, ox, oy):
    cx, cy = EYE_PX[0] + ox, EYE_PX[1] + oy
    glow = pygame.Surface((10, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*ROSY, 120), glow.get_rect())
    ov.blit(glow, (int(cx - 7), int(cy + 4)))


def _cowlick(ov, ox, oy):
    """A small curled snow tuft on top of the crown (V5)."""
    cx, cy = CROWN_PX[0] + ox, CROWN_PX[1] + oy
    pts = [(cx, cy), (cx - 2, cy - 5), (cx + 2, cy - 7), (cx + 3, cy - 3)]
    pygame.draw.lines(ov, WHITE, False, pts, 2)
    pygame.draw.circle(ov, OFF, (int(cx + 3), int(cy - 3)), 2)


def _pip_peeks(ov, ox, oy):
    """V4 only: a deliberate, OBVIOUS Pip wink on the otherwise-buried mound —
    a small green macaw crown tuft + a 2-3px blue wing-tip. Everything else
    stays white so it reads as an intentional peek, not unfinished snow."""
    cx, cy = CROWN_PX[0] + ox, CROWN_PX[1] + oy
    # green crown tuft cleanly poking out of the top of the head
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx - 3, cy + 1), (cx - 5, cy - 6), (cx - 1, cy - 2)])
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx, cy), (cx + 1, cy - 7), (cx + 4, cy - 1)])
    # tiny blue wing-tip peek on the upper back of the mound
    bx, byy = 30 + ox, 30 + oy
    pygame.draw.polygon(ov, PIP_BLUE,
                        [(bx, byy), (bx - 5, byy + 2), (bx, byy + 3)])


# ── the 5 snowman treatments (snow base IDENTICAL; vary the face only) ───────
def v1_classic(ov, ox, oy):
    _scarf(ov, ox, oy, tails=1)
    _buttons(ov, ox, oy, n=2)
    _carrot(ov, ox, oy, angle=4, length=12, droop=2.0)
    _coal_eye(ov, ox, oy, round_eye=True, glint=True, pair=True)
    _coal_smile(ov, ox, oy, pebbles=3)


def v2_buttons_noscarf(ov, ox, oy):
    _buttons(ov, ox, oy, n=3)
    _carrot(ov, ox, oy, angle=4, length=12, droop=2.0)
    _coal_eye(ov, ox, oy, round_eye=False, glint=False, pair=True)   # two flat button eyes
    _coal_smile(ov, ox, oy, pebbles=3)


def v3_minimal_cute(ov, ox, oy):
    _scarf(ov, ox, oy, tails=1, thin=True)
    _rosy_cheeks(ov, ox, oy)
    _carrot(ov, ox, oy, angle=6, length=11, droop=2.0)
    _coal_eye(ov, ox, oy, round_eye=True, glint=True, pair=True)     # 2-coal + carrot cluster


def v4_hybrid(ov, ox, oy):
    _pip_peeks(ov, ox, oy)                                # deliberate green tuft + blue tip
    _scarf(ov, ox, oy, red=PIP_SCARLET, white=SCARF_WHITE, tails=1)
    _carrot(ov, ox, oy, angle=4, length=12, droop=2.0)
    _coal_eye(ov, ox, oy, round_eye=False, glint=False)   # V2-style face


def v5_expressive(ov, ox, oy):
    _cowlick(ov, ox, oy)
    _scarf(ov, ox, oy, tails=2)
    _carrot(ov, ox, oy, angle=12, length=13, droop=0.5)   # jaunty angled carrot
    _coal_eye(ov, ox, oy, round_eye=False, glint=False)   # V2 simplicity
    _brow(ov, ox, oy, tilt=1.5)                           # ONE subtle brow tilt
    _coal_smile(ov, ox, oy, pebbles=3)


# ── compose one Pip cell ──────────────────────────────────────────────────────
def render_cell(extra, *, face_fn=None):
    """Bird sprite + parcel composited, then — at full cover — the ENTIRE
    combined silhouette is buried under one solid W2 snow mound, and the
    snowman face is drawn on top. Mirrors Bird.draw's compositing order without
    touching game code. face_fn draws the snowman parts onto the snow mound."""
    nw, nh = _native_size()
    pad = 6
    cw, ch = nw + pad * 2, nh + pad * 2 + 14
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    spr = parrot._get_frames()[snow_fx._REF_FRAME]
    bx, by = pad, pad
    parcel = parrot.get_parcel("normal")
    pw, ph = parcel.get_size()
    px = int(bx + nw / 2 - pw / 2)
    py = int(by + nh / 2 + 12 - ph / 2)

    # Build the COMBINED Pip+parcel alpha silhouette in cell-local space, then
    # bury it under one W2 mound. We deliberately do NOT blit the bird/parcel
    # into the final cell at full cover — only the opaque white mound — so NO
    # red/blue/gold/parcel colour can survive even at antialiased edges.
    sil = pygame.Surface((cw, ch), pygame.SRCALPHA)
    sil.blit(spr, (bx, by))
    sil.blit(parcel, (px, py))
    ov = _mound_overlay(sil)
    if ov is not None:
        if face_fn is not None:
            # face landmarks are in _REF_FRAME sprite-local coords; the sprite
            # sits at (pad, pad), so shift the face onto the mound to match.
            face_surf = pygame.Surface((cw, ch), pygame.SRCALPHA)
            face_fn(face_surf, ox=bx, oy=by)
            ov.blit(face_surf, (0, 0))
        cell.blit(ov, (0, 0))
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
     "round coal eye by carrot root, 3-coal smile, red-white scarf at neck pinch, belly buttons",
     v1_classic),
    ("V2 - Buttons, no scarf",
     "flat button eye + stitch by carrot, coal smile, 3 belly buttons, NO scarf - cleanest read",
     v2_buttons_noscarf),
    ("V3 - Minimal cute",
     "tight carrot + coal eye cluster + rosy snow cheek + thin scarf, no buttons - most legible",
     v3_minimal_cute),
    ("V4 - Pip-snowman hybrid",
     "V2 face on white mound + DELIBERATE green crown tuft + blue wing-tip peek; Pip-scarlet scarf",
     v4_hybrid),
    ("V5 - Expressive",
     "V2 simplicity + ONE brow tilt + jaunty angled carrot + 2-tail scarf + snow cowlick",
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
        "Pip - snow FULL COVER -> SNOWMAN  (round 4: W2 mound ENCLOSES the whole silhouette)",
        True, GOLD), (pad_out, 14))
    sheet.blit(fnote.render(
        "Snow = the LITERAL snow_fx W2 recipe (OFF body + WHITE crest + BLUE under-edge, "
        "same cornice/ripple) now wrapping the FULL dilated Pip+parcel contour. The 'FULLY "
        "COVERED' cell is a clean white parrot-shaped mound - NO red/blue/gold/parcel shows. "
        "Then the snowman face goes on top: eye by the carrot root, accessories on the snow.",
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

    out = os.path.join(OUT_DIR, "round_4.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
