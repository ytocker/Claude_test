"""DESIGN EXPLORATION — extend Pip's snow accumulation past today's max all
the way to FULLY COVERED, then read Pip as a SNOWMAN. Throwaway sheet tool;
touches NO game code.

ONE snow look only — the shipped snow_fx.py W2 "sculpted blanket": OFF body +
bright WHITE crest over the top ~18%% of each filled column + cool-blue BLUE
under-edge over the bottom ~26%%, with the CORNICE rear overhang and the sine
ripple `nb`. We do NOT invent a new finish. At full cover that recipe is wrapped
around the enclosing contour so the bird is buried into one solid white mound
(no red/blue/gold/parcel showing).

ROUND 6 is a 3-DIRECTION STRUCTURE COMPARISON. Round 5 went full-classic on
Pip's HORIZONTAL lying-down mound and the classic kit scattered (a vertical
snowman's parts don't map onto a horizontal lump). The owner asked to "try all
options and show me" and noted the snowman renders LARGER than the bird (~1.6-2x).
So we hold ONE shared face treatment constant and vary ONLY the structure:

  A · Head-concentrated — snowman identity packed into the HEAD bump only
      (hat + eyes + carrot + smile + scarf at the neck). Body stays a clean
      white W2 mound. NO body buttons, NO twig arms.
  B · Full-classic (horizontal) — the round-5 approach kept for comparison:
      shared face on the head + buttons down the horizontal body front + two
      twig arms out the sides, rooted on the body contour.
  C · Reshaped upright — at full cover the snow is rebuilt into an UPRIGHT
      STACKED snowman silhouette (head ball + larger body ball, sized to
      contain Pip), taller than the bird. The faithful W2 shading is applied
      per-column to this new stacked contour, then the full vertical kit fits
      naturally: hat on the head ball, face on the head ball, scarf at the
      head/body neck, buttons down the body ball, twig arms out the body sides.

The SHARED face treatment (identical in A/B/C): black top-hat (hard flat brim +
red band) + 2 coal eyes + carrot below-and-between the eyes pointing forward +
a 3-dot downward coal smile arc directly under the carrot + one red-white scarf
band at the neck + V4's deliberate macaw peek (green crown tuft + a blue
wing-tip). The face is a TIGHT cluster on the head so it reads as a face at
large size — never bars down the chest.

The ACCUMULATION STRIP (extra 0/.25/.50/.75/1.0, snow only, rear-first burial)
is FROZEN per the art-director — kept exactly as round 5.

The technique stays numpy-free / pure pygame so it ports straight into
snow_fx.py later.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_6.png
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
TWIG = (122, 86, 54)             # bare-branch arm
TWIG_HI = (158, 120, 82)         # lit twig edge
SCARF_RED = (212, 46, 52)        # snowman scarf red
SCARF_WHITE = (244, 248, 252)    # scarf white stripe
KNIT_RED = (206, 64, 70)         # V2 knit beanie/scarf red
KNIT_WHITE = (238, 240, 246)     # V2 knit white
HAT_BLACK = (30, 32, 42)         # top-hat felt
HAT_HI = (70, 74, 90)            # hat lit edge
HAT_BAND = (196, 60, 64)         # top-hat band
PIP_GREEN = (74, 176, 96)        # macaw crown tuft peek (V4)
PIP_BLUE = (66, 132, 224)        # macaw wing-tip peek (V4)
PIP_SCARLET = (240, 55, 55)      # shipped BIRD_RED (V4 scarf)

ZOOM = 6                         # sprite is 68x64; render big for detail


# ── per-column envelope of a combined alpha silhouette ───────────────────────
# The snow must ENCLOSE the whole shape, so we work from the top AND bottom of
# the combined Pip(+parcel) alpha mask. `_envelope` returns, per column, the
# first/last opaque row of a composited surface (the rounded snow-lump outer
# contour after dilation).
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


# ── THE faithful W2 blanket, now ramping from top-blanket to full enclosure ──
# Round-5: a single `extra in [0,1]` morphs the SAME W2 recipe from the shipped
# top-blanket (extra=0) to the full enclosing mound (extra=1). The lower edge of
# each filled column is a linear blend between the silhouette TOPLINE (a shallow
# blanket sitting on the back/top, body visible below) and the silhouette
# BOTTOM contour (the bird fully wrapped). The blend per column is gated so the
# REAR (left) columns reach full burial first and the FRONT (face) columns last,
# matching the left->right tailwind. The palette/proportions (OFF body, WHITE
# crest over top 18%, BLUE under-edge over bottom 26%, cornice, ripple) are
# IDENTICAL to snow_fx all the way along the ramp.
def _mound_overlay(silhouette, extra=1.0):
    extra = max(0.0, min(1.0, extra))
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

        # Per-column burial fraction. extra grows it; the rear (left) buries
        # first. At extra=0 the blanket only reaches a shallow depth below the
        # topline (the shipped look); at extra=1 every column reaches the bottom
        # contour. The `gate` shifts the onset later for front columns so the
        # snow visibly creeps down rear->front as extra rises.
        gate = 0.62 * xf                                     # front lags behind
        if extra <= gate:
            cov = 0.0
        else:
            cov = (extra - gate) / max(1e-3, 1.0 - gate)
        cov = snow_fx._smooth(cov)

        col_h = yb - yt
        # At extra=0 we still want the shipped shallow blanket on the back/top,
        # so even a zero-cov column shows a thin cap (rear-weighted, head-capped
        # like snow_fx). This is the BASE blanket the ramp deepens.
        base = (0.16 + 0.30 * rear) * col_h
        if xf > 0.62:                                        # keep the face cap thin
            base = min(base, 0.16 * col_h)
        # The lower edge sweeps from the base blanket down to the full bottom
        # contour as cov->1.
        depth = base + (col_h - base) * cov

        te = snow_fx._smooth((x - x_min) / taper_w)
        over = snow_fx.CORNICE * rear * te                   # cornice overhang
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yt + depth + (nb - 0.5) * 2.4
        d = y1 - y0
        if d < 1.0:
            continue
        # W2 sculpted blanket — IDENTICAL palette/proportions to snow_fx: clean
        # OFF fill + bright WHITE crest over the top 18% + cool-blue BLUE
        # under-edge over bottom 26%.
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)
        drew = True
    if not drew:
        return None
    return ov, (top, bot, x_min, x_max, w, h)


def _native_size():
    _, _, w, h = snow_fx._topline(snow_fx._REF_FRAME)
    return w, h


# ── C · UPRIGHT STACKED-SNOWMAN contour (numpy-free) ─────────────────────────
# Direction C rejects the horizontal lying-down lump entirely: at full cover we
# REBUILD the snow as a classic two-ball vertical snowman. Two filled circles
# (a small head ball stacked on a larger body ball) are unioned into one
# per-column top/bot contour, sized to comfortably CONTAIN Pip (taller than the
# bird is wide — fine, the snowman renders ~1.7x the bird). The exact same W2
# per-column recipe (OFF fill + WHITE crest top 18% + BLUE under-edge bottom 26%
# + a soft cornice + sine ripple) is then run down this stacked contour, so it
# still reads as the shipped SNOW finish — just shaped like a snowman, upright,
# with a real neck pinch for the scarf and a body ball front for the buttons.
def _stacked_overlay(cw, ch):
    """Return (overlay_surface, geom) for an upright stacked snowman sized to
    sit inside a (cw,ch) cell. geom mirrors _mound_overlay so every snowman
    part helper works unchanged. The neck pinch between the two balls gives a
    genuine head/body junction for the scarf."""
    cx = cw * 0.52                                          # slight left bias: room for arms
    # body ball sits low, head ball stacked on top; both fit the cell height.
    body_r = ch * 0.255
    head_r = body_r * 0.62
    body_cy = ch * 0.62
    # overlap the two balls so they fuse with a neck pinch rather than a gap.
    head_cy = body_cy - (body_r + head_r) * 0.78
    span_r = body_r                                         # widest extent for the envelope

    top = [-1.0] * cw
    bot = [-1.0] * cw
    x_min, x_max = -1, -1
    for x in range(cw):
        ys = []
        for (ccx, ccy, rr) in ((cx, body_cy, body_r), (cx, head_cy, head_r)):
            dx = x - ccx
            if abs(dx) <= rr:
                dy = math.sqrt(max(0.0, rr * rr - dx * dx))
                ys.append((ccy - dy, ccy + dy))
        if not ys:
            continue
        t = min(y0 for y0, _ in ys)
        b = max(y1 for _, y1 in ys)
        top[x] = t
        bot[x] = b
        if x_min < 0:
            x_min = x
        x_max = x
    if x_min < 0:
        return None
    # smooth the union seam (the neck) so the two circles read as one snow body.
    for _ in range(2):
        st, sb = list(top), list(bot)
        for x in range(x_min, x_max + 1):
            if top[x] < 0:
                continue
            ts = [top[k] for k in (x - 1, x, x + 1) if 0 <= k < cw and top[k] >= 0]
            bs = [bot[k] for k in (x - 1, x, x + 1) if 0 <= k < cw and bot[k] >= 0]
            st[x] = sum(ts) / len(ts)
            sb[x] = sum(bs) / len(bs)
        top, bot = st, sb

    ov = pygame.Surface((cw, ch), pygame.SRCALPHA)
    span = max(1.0, float(x_max - x_min))
    taper_w = 13.0
    for x in range(cw):
        yt = top[x]
        yb = bot[x]
        if yt < 0 or yb < 0 or yb <= yt:
            continue
        xf = (x - x_min) / span
        rear = 1.0 - xf
        te = snow_fx._smooth((x - x_min) / taper_w)
        over = snow_fx.CORNICE * rear * te
        nb = (math.sin(x * 1.26) + math.sin(x * 0.34)) * 0.25 + 0.5
        y0 = yt - over
        y1 = yb + (nb - 0.5) * 2.4
        d = y1 - y0
        if d < 1.0:
            continue
        # IDENTICAL W2 recipe to snow_fx / _mound_overlay, run down the upright
        # stacked contour: OFF fill + WHITE crest top 18% + BLUE under-edge 26%.
        pygame.draw.line(ov, (*OFF, 255), (x, int(y0)), (x, int(y1)), 1)
        pygame.draw.line(ov, (*WHITE, 255), (x, int(y0)), (x, int(y0 + d * 0.18)), 1)
        pygame.draw.line(ov, (*BLUE, 255), (x, int(y1 - d * 0.26)), (x, int(y1)), 1)
    geom = ([int(t) if t >= 0 else -1 for t in top],
            [int(b) if b >= 0 else -1 for b in bot], x_min, x_max, cw, ch)
    # carry the analytic anchors so the upright kit seats on the real ball
    # centres (not the contour-bump heuristic, which assumes a horizontal lump).
    anchors = {
        "hx": cx, "hy": head_cy, "hr": head_r,
        "bx": cx, "by": body_cy, "br": body_r,
        "neck_y": (head_cy + head_r * 0.55),
    }
    return ov, geom, anchors


# ── head anchor derived from the MOUND geometry (NOT the bird landmarks) ──────
# We treat the finished mound as a fresh snowman. The head is the FRONT bump of
# the enclosing contour (Pip faces RIGHT, so the head is the right side). We
# read the front ~32% of the span, take the contour midline there, and size the
# head from the local thickness of the mound. Everything downstream (eyes, nose,
# smile, scarf, buttons, arms, hat) is placed relative to this anchor + the body
# centroid, so nothing depends on where Pip's beak/eye pixels were.
def _head_anchor(top, bot, x_min, x_max):
    span = x_max - x_min
    # The dilated Pip+parcel mound is one rounded lump with no real neck pinch,
    # so we DEFINE the snowman head as the upper-front portion of the bump:
    # forward in x (Pip faces right) and seated against the SNOW TOPLINE there.
    # The radius is a fraction of the local mound thickness, deliberately kept
    # small (~a third of the mound height) so the head reads as a head, not half
    # the body — and so the hat/scarf/face scale sensibly.
    hx = x_min + span * 0.74
    cx = int(max(x_min, min(x_max, hx)))
    while cx <= x_max and (top[cx] < 0 or bot[cx] < 0):
        cx += 1
    if top[cx] < 0:
        cx = (x_min + x_max) // 2
    thick = max(10.0, bot[cx] - top[cx])
    hr = max(6.0, min(thick * 0.34, span * 0.20))
    # seat the head against the snow topline at the bump (centre one radius down)
    hy = top[cx] + hr + 1.0
    # facing axis points forward/right and slightly down (carrot droop direction)
    facing = math.radians(7.0)
    return hx, hy, hr, facing


def _body_anchor(top, bot, x_min, x_max):
    """Centre of the rear/lower body mass — front-centre column used for buttons
    and the rooting band for the arms. Derived from the contour, not Pip."""
    span = x_max - x_min
    bxc = x_min + span * 0.46
    cx = int(bxc)
    cx = max(x_min, min(x_max, cx))
    while cx > x_min and (top[cx] < 0 or bot[cx] < 0):
        cx -= 1
    byc = (top[cx] + bot[cx]) * 0.5
    return bxc, byc, cx


# ── snowman parts, ALL placed from (hx,hy,hr) or the body contour ────────────
def _coal_dot(ov, x, y, r, *, glint=False):
    pygame.draw.circle(ov, COAL, (int(round(x)), int(round(y))), int(r))
    if r >= 2:
        pygame.draw.circle(ov, COAL_HI, (int(round(x)), int(round(y))), int(r), 1)
    if glint:
        pygame.draw.circle(ov, GLINT, (int(round(x - r * 0.4)), int(round(y - r * 0.4))), 1)


def _coal_eyes(ov, hx, hy, hr, facing, *, button=False, stitch=False, glint=True):
    """Two coals in the UPPER third of the head, close together (~0.5*hr apart),
    symmetric about the facing axis. The pair sits forward on the bump (toward
    the carrot side) so it reads as a face turned right."""
    fx, fy = math.cos(facing), math.sin(facing)
    px, py = -fy, fx                                        # perpendicular (vertical-ish)
    # eye band centre: forward of head centre, in the upper third
    ecx = hx + fx * hr * 0.20 - 0.0
    ecy = hy - hr * 0.42
    sep = hr * 0.27
    r = max(2.0, hr * 0.18)
    for s in (+1, -1):
        ex = ecx + px * sep * s * 0.0 + s * sep   # spread horizontally across the face
        ey = ecy
        if button:
            rr = int(max(2, r))
            pygame.draw.rect(ov, COAL, (int(ex - rr), int(ey - rr), rr * 2, rr * 2),
                             border_radius=1)
            if stitch:
                pygame.draw.line(ov, COAL_HI, (ex - rr + 1, ey), (ex + rr - 1, ey), 1)
                pygame.draw.line(ov, COAL_HI, (ex, ey - rr + 1), (ex, ey + rr - 1), 1)
        else:
            _coal_dot(ov, ex, ey, r, glint=glint)


def _carrot(ov, hx, hy, hr, facing, *, length_k=1.15, droop=0.18):
    """Orange cone rooted at HEAD CENTRE, just below/between the eyes, pointing
    OUTWARD (forward/right). Length ~1.0-1.3*hr. Darker segment ridges + a lit
    top edge — the snowman's single strongest read."""
    ang = facing + droop
    fx, fy = math.cos(ang), math.sin(ang)
    # root sits at the front face of the head, a hair below the eye band
    rx = hx + math.cos(facing) * hr * 0.18
    ry = hy + hr * 0.02
    length = hr * length_k
    tx = rx + fx * length
    ty = ry + fy * length
    half = max(2.4, hr * 0.30)
    nx, ny = -fy, fx                                        # cone base normal
    b1 = (rx + nx * half, ry + ny * half)
    b2 = (rx - nx * half, ry - ny * half)
    tip = (tx, ty)
    pygame.draw.polygon(ov, CARROT, [b1, tip, b2])
    pygame.draw.polygon(ov, CARROT_RIDGE, [b1, tip, b2], 1)
    for t in (0.32, 0.58, 0.80):
        cx = rx + (tx - rx) * t
        cy = ry + (ty - ry) * t
        hw = half * (1.0 - t) + 0.5
        pygame.draw.line(ov, CARROT_RIDGE,
                         (cx + nx * hw, cy + ny * hw),
                         (cx - nx * hw, cy - ny * hw), 1)
    pygame.draw.line(ov, CARROT_HI, b1, tip, 1)


def _coal_smile(ov, hx, hy, hr, facing, *, n=5, wide=False):
    """3-5 small coals in a downward arc in the LOWER third of the head."""
    fx, fy = math.cos(facing), math.sin(facing)
    scx = hx + fx * hr * 0.16
    scy = hy + hr * 0.46
    span = hr * (1.10 if wide else 0.85)
    n = max(3, n)
    for i in range(n):
        t = i / (n - 1)
        px = scx + (t - 0.5) * span
        py = scy + math.sin(t * math.pi) * (hr * 0.16)     # smile droop arc
        _coal_dot(ov, px, py, max(1.0, hr * 0.085))


def _buttons(ov, bxc, byc, top, bot, x_min, x_max, *, n=3):
    """Vertical line of coals down the FRONT-CENTRE of the BODY mass, spaced
    along the contour midline (derived from the contour, not Pip's belly)."""
    span = x_max - x_min
    bx = x_min + span * 0.50
    cx = int(max(x_min, min(x_max, bx)))
    while cx <= x_max and (top[cx] < 0 or bot[cx] < 0):
        cx += 1
    if top[cx] < 0:
        return
    midy = (top[cx] + bot[cx]) * 0.5
    botc = bot[cx]
    r = 2
    for i in range(n):
        t = (i + 0.6) / (n + 0.3)
        py = midy + (botc - midy) * t * 0.9
        _coal_dot(ov, cx, py, r)


def _twig_arms(ov, top, bot, x_min, x_max, *, pose="straight"):
    """Two thin bare-branch arms poking out the SIDES of the body, rooted on the
    body contour, with 1-2 small forks. Derived from the contour. `pose` varies
    the spread."""
    span = x_max - x_min
    # rooting column: mid-body, where the mound is thickest
    rootx = int(x_min + span * 0.42)
    rootx = max(x_min, min(x_max, rootx))
    while rootx <= x_max and (top[rootx] < 0 or bot[rootx] < 0):
        rootx += 1
    if top[rootx] < 0:
        return
    midy = (top[rootx] + bot[rootx]) * 0.5

    def branch(sx, sy, ang, ln, forks):
        ex = sx + math.cos(ang) * ln
        ey = sy + math.sin(ang) * ln
        pygame.draw.line(ov, TWIG, (sx, sy), (ex, ey), 2)
        pygame.draw.line(ov, TWIG_HI, (sx, sy), ((sx + ex) / 2, (sy + ey) / 2), 1)
        for fk in forks:
            fr = ln * 0.5
            mx = sx + (ex - sx) * fk
            my = sy + (ey - sy) * fk
            fang = ang + math.radians(34)
            pygame.draw.line(ov, TWIG, (mx, my),
                             (mx + math.cos(fang) * fr * 0.5,
                              my + math.sin(fang) * fr * 0.5), 1)
            fang2 = ang - math.radians(30)
            pygame.draw.line(ov, TWIG, (mx, my),
                             (mx + math.cos(fang2) * fr * 0.5,
                              my + math.sin(fang2) * fr * 0.5), 1)

    # rear (left) arm roots near the back-third side of the body
    rear_x = x_min + span * 0.24
    rcx = int(max(x_min, min(x_max, rear_x)))
    while rcx <= x_max and (top[rcx] < 0 or bot[rcx] < 0):
        rcx += 1
    rmidy = (top[rcx] + bot[rcx]) * 0.5 if top[rcx] >= 0 else midy
    # front (right) arm roots forward, on the LOWER body so it clears the scarf
    front_x = x_min + span * 0.56
    fcx = int(max(x_min, min(x_max, front_x)))
    while fcx <= x_max and (top[fcx] < 0 or bot[fcx] < 0):
        fcx += 1
    fmidy = ((top[fcx] + bot[fcx]) * 0.5 + bot[fcx]) * 0.5 if top[fcx] >= 0 else midy

    if pose == "lively":
        # one arm up-forward, one out-back-down for an animated stance
        branch(fcx, fmidy, math.radians(28), span * 0.30, [0.55])
        branch(rcx - 1, rmidy - 1, math.radians(170), span * 0.32, [0.5])
    elif pose == "slim":
        branch(fcx, fmidy, math.radians(14), span * 0.26, [0.6])
        branch(rcx - 1, rmidy, math.radians(192), span * 0.28, [])
    else:  # straight
        branch(fcx, fmidy, math.radians(20), span * 0.28, [0.55])
        branch(rcx - 1, rmidy, math.radians(194), span * 0.32, [0.55])


def _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, *, red=SCARF_RED,
           white=SCARF_WHITE, tails=1, thin=False, knit=False):
    """Band wrapped at the NECK — just below the head circle, where the head
    meets the body — with a hanging tail that streams left->right (forward) with
    the wind. The neck position is derived from the head anchor (one radius below
    centre) and the band width scales with hr so it never balloons to the whole
    mound thickness."""
    # neck sits at the BASE of the head (below the smile), wrapping the head/body
    # junction as a COMPACT band of short across-stripes stacked down a little —
    # narrow, so it reads as a scarf round a neck, never a wide flag. Width and
    # length both scale with hr, and it sits clear below the face.
    nx = hx - hr * 0.34
    ny = hy + hr * 1.08
    half_w = hr * (0.46 if not thin else 0.36)             # narrow neck wrap
    band_len = hr * (0.55 if not thin else 0.42)
    rw = red if not knit else KNIT_RED
    ww = white if not knit else KNIT_WHITE
    nseg = max(3, int(band_len + 2))
    for i in range(nseg):
        t = i / max(1, nseg - 1)
        col = rw if (i // 2) % 2 == 0 else ww
        cyy = ny - band_len * 0.5 + t * band_len
        cxx = nx + t * hr * 0.18                           # slight forward lean
        pygame.draw.line(ov, col, (cxx - half_w, cyy), (cxx + half_w, cyy), 1)
    if knit:
        # a couple of light ribbing ticks, not a full picket fence
        dk = (max(0, rw[0] - 30), max(0, rw[1] - 20), max(0, rw[2] - 20))
        for tx in (nx - half_w * 0.5, nx, nx + half_w * 0.5):
            pygame.draw.line(ov, dk, (tx, ny - band_len * 0.5), (tx, ny + band_len * 0.5), 1)

    # short hanging tail streams forward/down (left->right tailwind)
    def _tail(x_off, ln):
        px = nx + half_w * 0.5 + x_off
        py = ny + band_len * 0.5
        for j in range(ln):
            t = j / ln
            wob = math.sin(t * 6.0) * 1.2                  # flutter
            x0 = px + t * (hr * 0.85)                       # forward
            y0 = py + t * (hr * 0.55) + wob
            col = rw if (j // 2) % 2 == 0 else ww
            pygame.draw.line(ov, col, (x0, y0), (x0 + 2, y0 + 1), 2 if thin else 3)
    _tail(0, 6)
    if tails > 1:
        _tail(-2, 5)


def _hat_top(ov, hx, hy, hr, facing, *, tilt=0.0, band=HAT_BAND):
    """Black top hat seated on the head bump, following the head curve. `tilt`
    in radians rotates the whole hat for the jaunty version."""
    ct, st = math.cos(tilt), math.sin(tilt)
    # seat the brim on the head's upper curve (a touch above centre toward front)
    seat_x = hx + hr * 0.10
    seat_y = hy - hr * 0.42

    def rot(dx, dy):
        return (seat_x + dx * ct - dy * st, seat_y + dx * st + dy * ct)

    brim_w = hr * 1.35
    brim_h = hr * 0.20
    crown_w = hr * 0.92
    crown_h = hr * 1.05
    # brim (sits on the head curve)
    bpts = [rot(-brim_w, brim_h), rot(brim_w, brim_h),
            rot(brim_w, -brim_h * 0.2), rot(-brim_w, -brim_h * 0.2)]
    pygame.draw.polygon(ov, HAT_BLACK, bpts)
    # crown
    cpts = [rot(-crown_w, 0), rot(crown_w, 0),
            rot(crown_w, -crown_h), rot(-crown_w, -crown_h)]
    pygame.draw.polygon(ov, HAT_BLACK, cpts)
    # band
    band_pts = [rot(-crown_w, -crown_h * 0.18), rot(crown_w, -crown_h * 0.18),
                rot(crown_w, -crown_h * 0.40), rot(-crown_w, -crown_h * 0.40)]
    pygame.draw.polygon(ov, band, band_pts)
    # lit left edge
    pygame.draw.line(ov, HAT_HI, rot(-crown_w, 0), rot(-crown_w, -crown_h), 1)
    pygame.draw.line(ov, HAT_HI, rot(-crown_w, -crown_h), rot(crown_w, -crown_h), 1)


def _hat_beanie(ov, hx, hy, hr, facing):
    """Red-white knit beanie with a pom, hugging the head curve (V2). A small
    half-dome cap seated on the head top, NOT a full balloon over the face."""
    cx = hx + hr * 0.10
    cap_top = hy - hr * 1.05                                # crown of the cap
    cap_bot = hy - hr * 0.30                                # brim sits high on head
    bw = hr * 0.98
    ch = cap_bot - cap_top
    # dome: draw as a clipped ellipse top-half via stacked horizontal stripes
    for i, yy in enumerate(range(int(cap_top), int(cap_bot))):
        t = (yy - cap_top) / max(1.0, ch)
        half = bw * math.sin(min(1.0, t + 0.12) * math.pi * 0.5)
        col = KNIT_WHITE if (i // 2) % 2 == 0 else KNIT_RED
        pygame.draw.line(ov, col, (cx - half, yy), (cx + half, yy), 1)
    # folded brim band at the base
    pygame.draw.line(ov, KNIT_WHITE, (cx - bw, cap_bot), (cx + bw, cap_bot - 1), 3)
    # pom on top
    pygame.draw.circle(ov, KNIT_WHITE, (int(cx), int(cap_top)), int(max(2, hr * 0.24)))


def _hat_earmuffs(ov, hx, hy, hr, facing):
    """Minimal earmuffs band over the crown (V3) — a slim headband arc hugging
    the head top with a muff on each side."""
    cx = hx + hr * 0.08
    cy = hy - hr * 0.40
    pygame.draw.arc(ov, (96, 102, 120),
                    pygame.Rect(int(cx - hr * 0.78), int(cy - hr * 0.55),
                                int(hr * 1.56), int(hr * 1.0)),
                    math.radians(15), math.radians(165), 3)
    rmuff = int(max(2, hr * 0.26))
    for s in (+1, -1):
        ex = cx + s * hr * 0.72
        ey = cy + hr * 0.05
        pygame.draw.circle(ov, (74, 80, 96), (int(ex), int(ey)), rmuff)
        pygame.draw.circle(ov, (118, 124, 140), (int(ex), int(ey)), rmuff, 1)


def _pip_peeks(ov, hx, hy, hr, top, x_min, x_max):
    """V4 only: a deliberate, OBVIOUS Pip wink on the otherwise-buried mound — a
    small green macaw crown tuft poking out the top of the head + a 2-3px blue
    wing-tip peek on the upper back of the mound. Placed from the head anchor +
    rear contour, not Pip's pixels."""
    # green crown tuft pokes out from UNDER the hat brim at the front of the head
    # so it reads as an obvious Pip wink, not lost behind the felt.
    cx = hx + hr * 0.45
    cy = hy - hr * 0.30
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx - 2, cy + 3), (cx - 1, cy - 4), (cx + 2, cy + 1)])
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx + 1, cy + 3), (cx + 3, cy - 3), (cx + 5, cy + 2)])
    # blue wing-tip on the rear/back of the mound (left side)
    span = x_max - x_min
    wx = int(x_min + span * 0.30)
    wx = max(x_min, min(x_max, wx))
    while wx <= x_max and top[wx] < 0:
        wx += 1
    wy = top[wx] + 4 if top[wx] >= 0 else hy
    pygame.draw.polygon(ov, PIP_BLUE,
                        [(wx, wy), (wx - 5, wy + 2), (wx, wy + 3)])


# ── THE ONE SHARED FACE TREATMENT (identical across A/B/C) ───────────────────
# Round 6 holds the kit constant so STRUCTURE is the only variable. The shared
# treatment is round-5's V4 read: black flat-brim top-hat + red band, 2 round
# coal eyes, carrot below-and-between the eyes, a 3-dot downward coal smile arc
# directly under the carrot, one red-white scarf band at the neck, and V4's
# deliberate macaw peek (green crown tuft + blue wing-tip). The face is a TIGHT
# cluster on the HEAD in every direction — only buttons/arms differ by structure.
def _shared_head_face(ov, hx, hy, hr, facing):
    """Draw the head-only kit (eyes + carrot + smile + hat + green tuft) as a
    tight face cluster. Shared verbatim by A, B and C."""
    _coal_eyes(ov, hx, hy, hr, facing, button=False, glint=True)
    _carrot(ov, hx, hy, hr, facing, length_k=1.15, droop=0.18)
    _coal_smile(ov, hx, hy, hr, facing, n=3)
    _hat_top(ov, hx, hy, hr, facing, tilt=0.0, band=PIP_GREEN)


def dir_a_head(ov, geom):
    """A · Head-concentrated. Snowman identity lives in the HEAD bump only; the
    body stays a clean white W2 mound. No buttons, no arms."""
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _head_anchor(top, bot, x_min, x_max)
    _shared_head_face(ov, hx, hy, hr, facing)
    _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, red=PIP_SCARLET,
           white=SCARF_WHITE, tails=1)
    _pip_peeks(ov, hx, hy, hr, top, x_min, x_max)


def dir_b_classic(ov, geom):
    """B · Full-classic on the HORIZONTAL mound (round-5 approach, for
    comparison). Shared face on the head + buttons down the front-centre of the
    horizontal body + two twig arms rooted on the body contour sides."""
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _head_anchor(top, bot, x_min, x_max)
    bxc, byc, _bc = _body_anchor(top, bot, x_min, x_max)
    # arms first so buttons/scarf overlay their roots
    _twig_arms(ov, top, bot, x_min, x_max, pose="straight")
    _buttons(ov, bxc, byc, top, bot, x_min, x_max, n=3)
    _shared_head_face(ov, hx, hy, hr, facing)
    _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, red=PIP_SCARLET,
           white=SCARF_WHITE, tails=1)
    _pip_peeks(ov, hx, hy, hr, top, x_min, x_max)


def dir_c_upright(ov, geom, anchors):
    """C · Reshaped UPRIGHT stacked snowman. Parts seat on the analytic ball
    centres (not the horizontal-bump heuristic): hat + face on the head ball,
    scarf at the neck pinch, buttons down the body ball front, twig arms out the
    body ball sides. The vertical kit fits because the contour is now vertical."""
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr = anchors["hx"], anchors["hy"], anchors["hr"]
    bx, by, br = anchors["bx"], anchors["by"], anchors["br"]
    facing = math.radians(7.0)
    # twig arms straight out the body ball's sides, drawn first so scarf/buttons
    # overlay the roots; rooted at the body ball equator.
    _twig_arms_upright(ov, bx, by, br)
    # buttons march down the front-centre of the body ball.
    _buttons_upright(ov, bx, by, br)
    # tight face cluster + hat on the head ball.
    _shared_head_face(ov, hx, hy, hr, facing)
    # scarf wraps the genuine neck pinch between the two balls.
    _scarf_upright(ov, hx, hy, hr, anchors["neck_y"])
    # the deliberate macaw peek: green tuft under the brim + blue wing-tip on
    # the body ball's rear shoulder.
    _pip_peeks_upright(ov, hx, hy, hr, bx, by, br)


# ── C-specific part placements (seat on the analytic two-ball geometry) ──────
def _buttons_upright(ov, bx, by, br, *, n=3):
    """Vertical column of coals down the FRONT-CENTRE of the body ball."""
    for i in range(n):
        t = (i + 0.5) / n
        py = by - br * 0.55 + t * br * 1.15
        _coal_dot(ov, bx, py, max(2, int(br * 0.09)))


def _twig_arms_upright(ov, bx, by, br):
    """Two bare-branch arms out the upper body ball, angled up-and-out with a
    fork each, rooted on the body ball's equator so they read as planted."""
    def branch(sx, sy, ang, ln, forks):
        ex = sx + math.cos(ang) * ln
        ey = sy + math.sin(ang) * ln
        pygame.draw.line(ov, TWIG, (sx, sy), (ex, ey), 2)
        pygame.draw.line(ov, TWIG_HI, (sx, sy), ((sx + ex) / 2, (sy + ey) / 2), 1)
        for fk in forks:
            mx = sx + (ex - sx) * fk
            my = sy + (ey - sy) * fk
            for da in (math.radians(32), math.radians(-28)):
                fr = ln * 0.42
                pygame.draw.line(ov, TWIG, (mx, my),
                                 (mx + math.cos(ang + da) * fr,
                                  my + math.sin(ang + da) * fr), 1)
    ry = by - br * 0.30
    branch(bx + br * 0.80, ry, math.radians(-22), br * 1.05, [0.6])    # right arm up-out
    branch(bx - br * 0.80, ry, math.radians(180 + 26), br * 1.10, [0.6])  # left arm up-out


def _scarf_upright(ov, hx, hy, hr, neck_y):
    """Red-white scarf band wrapping the neck pinch, with a short forward tail."""
    half_w = hr * 0.95
    band_h = hr * 0.34
    rw, ww = PIP_SCARLET, SCARF_WHITE
    nseg = max(3, int(band_h + 2))
    for i in range(nseg):
        t = i / max(1, nseg - 1)
        col = rw if (i // 2) % 2 == 0 else ww
        yy = neck_y - band_h * 0.5 + t * band_h
        # narrow toward the neck pinch so it hugs the junction
        hw = half_w * (0.78 + 0.22 * math.sin(t * math.pi))
        pygame.draw.line(ov, col, (hx - hw, yy), (hx + hw, yy), 1)
    # short tail streaming forward/down with the tailwind
    px = hx + half_w * 0.55
    py = neck_y + band_h * 0.5
    for j in range(7):
        t = j / 7.0
        x0 = px + t * hr * 0.9
        y0 = py + t * hr * 0.7 + math.sin(t * 6.0) * 1.2
        col = rw if (j // 2) % 2 == 0 else ww
        pygame.draw.line(ov, col, (x0, y0), (x0 + 2, y0 + 1), 3)


def _pip_peeks_upright(ov, hx, hy, hr, bx, by, br):
    """V4 macaw wink for the upright build: green crown tuft poking from under
    the hat brim + a blue wing-tip peek on the body ball's rear shoulder."""
    cx = hx + hr * 0.45
    cy = hy - hr * 0.28
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx - 2, cy + 3), (cx - 1, cy - 4), (cx + 2, cy + 1)])
    pygame.draw.polygon(ov, PIP_GREEN,
                        [(cx + 1, cy + 3), (cx + 3, cy - 3), (cx + 5, cy + 2)])
    wx = bx - br * 0.78
    wy = by - br * 0.42
    pygame.draw.polygon(ov, PIP_BLUE,
                        [(wx, wy), (wx - 6, wy + 2), (wx, wy + 4)])


# ── compose one Pip cell ──────────────────────────────────────────────────────
def render_cell(extra, *, face_fn=None):
    """Bird sprite + parcel composited, then the combined silhouette is buried
    under one W2 snow mound at burial level `extra`, and (optionally) the snowman
    face/hat/arms drawn from the mound contour. Mirrors Bird.draw's compositing
    order without touching game code."""
    nw, nh = _native_size()
    pad = 8
    cw, ch = nw + pad * 2, nh + pad * 2 + 18
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    spr = parrot._get_frames()[snow_fx._REF_FRAME]
    bx, by = pad, pad
    parcel = parrot.get_parcel("normal")
    pw, ph = parcel.get_size()
    px = int(bx + nw / 2 - pw / 2)
    py = int(by + nh / 2 + 12 - ph / 2)

    sil = pygame.Surface((cw, ch), pygame.SRCALPHA)
    sil.blit(spr, (bx, by))
    sil.blit(parcel, (px, py))

    # At partial burial the bird body should still be visible UNDER the blanket,
    # so we DO blit the sprite first for extra<1. At full cover we draw only the
    # opaque mound so no bird colour can survive even at AA edges.
    if extra < 0.999:
        cell.blit(spr, (bx, by))
        cell.blit(parcel, (px, py))

    result = _mound_overlay(sil, extra)
    if result is None:
        return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)
    ov, geom = result
    if face_fn is not None and extra >= 0.999:
        face_surf = pygame.Surface((cw, ch), pygame.SRCALPHA)
        face_fn(face_surf, geom)
        ov.blit(face_surf, (0, 0))
    cell.blit(ov, (0, 0))
    return pygame.transform.scale(cell, (cw * ZOOM, ch * ZOOM)), (cw, ch)


# ── A / B render: the horizontal buried mound + the chosen kit ───────────────
def render_mound_cell(face_fn):
    """Full-cover horizontal mound (extra=1) with the A or B kit drawn from the
    mound contour. Returns the native cell + its size (un-zoomed) so callers can
    scale to whatever hero size they need."""
    nw, nh = _native_size()
    pad = 8
    cw, ch = nw + pad * 2, nh + pad * 2 + 18
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    spr = parrot._get_frames()[snow_fx._REF_FRAME]
    bx, by = pad, pad
    parcel = parrot.get_parcel("normal")
    pw, ph = parcel.get_size()
    px = int(bx + nw / 2 - pw / 2)
    py = int(by + nh / 2 + 12 - ph / 2)
    sil = pygame.Surface((cw, ch), pygame.SRCALPHA)
    sil.blit(spr, (bx, by))
    sil.blit(parcel, (px, py))
    result = _mound_overlay(sil, 1.0)
    if result is not None:
        ov, geom = result
        fsurf = pygame.Surface((cw, ch), pygame.SRCALPHA)
        face_fn(fsurf, geom)
        ov.blit(fsurf, (0, 0))
        cell.blit(ov, (0, 0))
    return cell, (cw, ch)


# ── C render: the rebuilt UPRIGHT stacked-snowman contour + the full kit ─────
# Direction C does NOT bury the bird silhouette — it replaces the contour with a
# procedural two-ball stacked snowman (taller than the bird, ~1.7x), then runs
# the same W2 recipe down it. We size the cell TALL so the upright build is not
# clipped, and seat the kit on the analytic ball anchors.
def render_stacked_cell():
    """Full upright stacked snowman (head ball + body ball) with the shared kit,
    rendered into a portrait cell. Returns the native cell + its size."""
    nw, nh = _native_size()
    pad = 8
    # portrait cell: the upright snowman is taller than the bird is wide.
    cw = nw + pad * 2
    ch = int((nw + pad * 2) * 1.42) + 18
    cell = pygame.Surface((cw, ch), pygame.SRCALPHA)
    built = _stacked_overlay(cw, ch - 14)
    if built is not None:
        ov, geom, anchors = built
        fsurf = pygame.Surface((cw, ch), pygame.SRCALPHA)
        dir_c_upright(fsurf, geom, anchors)
        cell.blit(ov, (0, 0))
        cell.blit(fsurf, (0, 0))
    return cell, (cw, ch)


# ── reference row via the REAL Bird.draw ─────────────────────────────────────
def render_reference(load):
    nw, nh = _native_size()
    pad = 8
    cw, ch = nw + pad * 2, nh + pad * 2 + 18
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
# Round 6 holds ONE shared face treatment constant and varies ONLY the structure
# across three direction rows (A / B / C).
DIRECTIONS = [
    ("A - Head-concentrated",
     "Snowman identity lives in the HEAD bump only: hat + eyes + carrot + smile + scarf at the neck. "
     "Body stays a clean white W2 mound. NO body buttons, NO twig arms.",
     "mound", dir_a_head),
    ("B - Full-classic (horizontal)",
     "Round-5 approach, kept for comparison: the shared face on the head PLUS buttons down the front of the "
     "horizontal body + two twig arms rooted on the body contour sides.",
     "mound", dir_b_classic),
    ("C - Reshaped UPRIGHT",
     "At full cover the snow is REBUILT into an upright stacked snowman (head ball + larger body ball, taller "
     "than the bird). Same W2 shading; the full vertical kit fits: hat + face on the head, scarf at the neck "
     "pinch, buttons down the body, twig arms out the sides.",
     "stacked", None),
]

ACCUM = [0.0, 0.25, 0.50, 0.75, 1.0]

# Hero cells render LARGE — the snowman is expected to read bigger than the bird.
HERO_ZOOM = 8


def _fit_into(cell, box_w, box_h, panel_fn):
    """Centre `cell` (native res, scaled up by HERO_ZOOM) onto a panel of size
    (box_w, box_h). Keeps the upright C cell from being stretched vs the wide
    A/B cell — both share the same hero pixel scale, just different aspect."""
    cw, ch = cell.get_size()
    scaled = pygame.transform.scale(cell, (cw * HERO_ZOOM, ch * HERO_ZOOM))
    sw, sh = scaled.get_size()
    if sw > box_w or sh > box_h:
        k = min(box_w / sw, box_h / sh)
        scaled = pygame.transform.smoothscale(scaled, (int(sw * k), int(sh * k)))
        sw, sh = scaled.get_size()
    panel = panel_fn(box_w, box_h)
    panel.blit(scaled, ((box_w - sw) // 2, (box_h - sh) // 2))
    return panel


def main():
    label_w = 264
    gap = 10
    pad_out = 18
    title_h = 96

    # reference / accumulation small cells use ZOOM; hero direction cells are LARGE
    _, (rcw, rch) = render_reference(1.0)
    small_w, small_h = rcw * ZOOM, rch * ZOOM

    ref_loads = [0.0, 0.35, 0.70, 1.00]
    cols_max = max(len(ref_loads), len(ACCUM))

    # hero cell box: tall enough for the upright C build at HERO_ZOOM.
    _, (ccw, cch) = render_stacked_cell()
    hero_h = cch * HERO_ZOOM + 12
    # three hero cells across must fit the same row width as the small strips.
    strip_w = cols_max * (small_w + gap)
    hero_w = (strip_w - 2 * gap) // 3

    small_row_h = small_h + 30
    hero_row_h = hero_h + 44

    sheet_w = label_w + strip_w + pad_out * 2
    sheet_h = (title_h
               + 2 * (small_row_h + gap + 30)     # reference + accumulation
               + 3 * (hero_row_h + gap + 30)       # A / B / C
               + pad_out)

    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((14, 16, 24))

    fbig = pygame.font.SysFont("Arial", 25, bold=True)
    frow = pygame.font.SysFont("Arial", 18, bold=True)
    fnote = pygame.font.SysFont("Arial", 13)
    fcell = pygame.font.SysFont("Arial", 13, bold=True)

    GOLD = (240, 206, 120)
    WLBL = (228, 236, 248)
    DIM = (170, 184, 206)

    sheet.blit(fbig.render(
        "Pip snow FULL COVER -> SNOWMAN  -  ROUND 6: 3-DIRECTION STRUCTURE COMPARISON (A / B / C)",
        True, GOLD), (pad_out, 14))
    sheet.blit(fnote.render(
        "ONE shared face treatment in all three (black top-hat + red/green band, 2 coal eyes, carrot below-and-between the eyes, "
        "3-dot smile arc, red-white scarf at the neck, macaw peek: green crown tuft + blue wing-tip). STRUCTURE is the only variable.",
        True, DIM), (pad_out, 46))
    sheet.blit(fnote.render(
        "Snow stays the faithful snow_fx W2 recipe (OFF body + WHITE crest top 18% + BLUE under-edge bottom 26% + cornice + ripple). "
        "ACCUMULATION strip below is FROZEN (round 5). Hero cells render LARGE; the in-game chip renders at ~1.7x the normal bird.",
        True, DIM), (pad_out, 64))

    y = title_h

    def cell_label(txt, x, yy, col=WLBL):
        sheet.blit(fcell.render(txt, True, col), (x + 4, yy))

    def wrap_note(txt, x, yy, maxchars=34, n=5):
        words = txt.split(" ")
        lines = [""] * n
        li = 0
        for wword in words:
            if len(lines[li]) > maxchars and li < n - 1:
                li += 1
            lines[li] += wword + " "
        for k, ln in enumerate(lines):
            if ln.strip():
                sheet.blit(fnote.render(ln.strip(), True, DIM), (x, yy + k * 16))

    # ── reference row ──
    sheet.blit(frow.render("REFERENCE - shipped", True, GOLD), (pad_out, y + 14))
    sheet.blit(fnote.render("real Bird.draw; anchor,", True, DIM), (pad_out, y + 38))
    sheet.blit(fnote.render("do not alter", True, DIM), (pad_out, y + 54))
    cx = label_w + pad_out
    for ld in ref_loads:
        cell, _ = render_reference(ld)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, small_w + 2, small_h + 2), 1)
        cell_label(f"snow_load {ld:.2f}", cx, y)
        cx += small_w + gap
    y += small_row_h + gap + 30

    # ── accumulation strip (FROZEN; snow only, NO face) ──
    sheet.blit(frow.render("ACCUMULATION", True, GOLD), (pad_out, y + 14))
    sheet.blit(fnote.render("FROZEN (round 5) - snow", True, DIM), (pad_out, y + 38))
    sheet.blit(fnote.render("only; rear buries first,", True, DIM), (pad_out, y + 54))
    sheet.blit(fnote.render("face last", True, DIM), (pad_out, y + 70))
    cx = label_w + pad_out
    for ex in ACCUM:
        cell, _ = render_cell(ex, face_fn=None)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (110, 130, 160),
                         (cx - 1, y + 17, small_w + 2, small_h + 2), 1)
        cell_label(f"extra {ex:.2f}", cx, y, GOLD)
        cx += small_w + gap
    y += small_row_h + gap + 30

    # ── three DIRECTION rows: each [hero dark] [hero whiteout] [in-game ~1.7x] ──
    nw, _nh = _native_size()
    chip_h = int(_nh * 1.7)              # in-game snowman renders ~1.7x the bird
    for name, note, kind, face_fn in DIRECTIONS:
        sheet.blit(frow.render(name, True, GOLD), (pad_out, y + 12))
        wrap_note(note, pad_out, y + 40)

        if kind == "mound":
            cell, _ = render_mound_cell(face_fn)
        else:
            cell, _ = render_stacked_cell()

        cx = label_w + pad_out
        # cell 1: hero on dark
        sheet.blit(_fit_into(cell.copy(), hero_w, hero_h, neutral_panel),
                   (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, hero_w + 2, hero_h + 2), 1)
        cell_label("SNOWMAN / dark (LARGE)", cx, y, GOLD)
        cx += hero_w + gap
        # cell 2: hero on whiteout (silhouette must survive the white sky)
        sheet.blit(_fit_into(cell.copy(), hero_w, hero_h, whiteout_panel),
                   (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, hero_w + 2, hero_h + 2), 1)
        cell_label("SNOWMAN / whiteout (LARGE)", cx, y, GOLD)
        cx += hero_w + gap
        # cell 3: expected in-game size on a sky bg - a 1.0x reference bird on the
        # left and the snowman at ~1.7x the bird beside it, sharing one world
        # scale so the size relationship reads honestly.
        chip_box = make_gradient_surface(hero_w, hero_h,
                                         [(0.0, (132, 178, 226)), (1.0, (180, 210, 238))])
        # pick a world scale where the 1.0x bird is a comfortable on-sheet size
        # and the 1.7x snowman still fits the box height (C is the tallest).
        cw0, ch0 = cell.get_size()
        world = (hero_h - 28) / (ch0 * 1.7)          # native px -> sheet px
        world = min(world, (hero_h * 0.30) / float(_nh))
        # 1.0x bird (native cell scaled by `world`)
        bnat = render_reference(0.0)[0]
        bnat = pygame.transform.smoothscale(bnat, (rcw, rch))   # de-zoom to native
        bird_chip = pygame.transform.smoothscale(
            bnat, (max(1, int(rcw * world)), max(1, int(rch * world))))
        bsw, bsh = bird_chip.get_size()
        # snowman at ~1.7x the bird (same world scale * 1.7)
        sscale = world * 1.7
        chip = pygame.transform.smoothscale(
            cell, (max(1, int(cw0 * sscale)), max(1, int(ch0 * sscale))))
        chw, chh = chip.get_size()
        baseline = hero_h - 16
        chip_box.blit(bird_chip, (18, baseline - bsh))
        chip_box.blit(chip, (18 + bsw + 22, baseline - chh))
        sheet.blit(chip_box, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, hero_w + 2, hero_h + 2), 1)
        cell_label("in-game ~1.7x bird (vs bird)", cx, y, GOLD)

        y += hero_row_h + gap + 30

    out = os.path.join(OUT_DIR, "round_6.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
