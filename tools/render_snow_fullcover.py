"""DESIGN EXPLORATION — extend Pip's snow accumulation past today's max all
the way to FULLY COVERED, then read Pip as a SNOWMAN. Throwaway sheet tool;
touches NO game code.

ONE snow look only — the shipped snow_fx.py W2 "sculpted blanket": OFF body +
bright WHITE crest over the top ~18%% of each filled column + cool-blue BLUE
under-edge over the bottom ~26%%, with the CORNICE rear overhang and the sine
ripple `nb`. We do NOT invent a new finish. At full cover that recipe is wrapped
around the WHOLE dilated Pip+parcel contour so the bird is buried into one solid
white mound (no red/blue/gold/parcel showing).

ROUND 5 brings three owner requirements:

1. ACCUMULATION RAMP. `_mound_overlay(silhouette, extra)` is parameterised by
   `extra in [0,1]`. At `extra=0` it reproduces the shipped top-blanket look
   (snow on the back/top, body still visible); at `extra=1` it is the full
   enclosing white mound. As `extra` rises the snow creeps DOWN and ENVELOPS
   the body rear-first (tailwind blows left->right so the rear/left buries
   first), bottom rising, front/face last. The 3 mids are genuine progressive
   burial in the W2 style — a deeper blanket pulling down over the silhouette,
   not just a taller hat.

2. SNOWMAN ELEMENT PLACEMENT FROM THE MOUND, not the bird. We no longer pin the
   face to Pip's BEAK/EYE pixels. `_head_anchor` reads the head region off the
   dilated enclosing contour (front ~30-35%% of the span, midline between the
   top and bottom contour) and returns centre (hx,hy), radius hr, and a facing
   axis. Every snowman part — coal eyes, carrot, smile, buttons, scarf, twig
   arms, hat — is laid out relative to (hx,hy,hr) and inset so it reads ON the
   snow. We "treat it as a new snowman".

3. FULL-CLASSIC snowman: twig arms out the body sides + a per-version hat on the
   head bump, plus the canonical face (coal eyes high & close, carrot centred
   pointing out, coal-pebble smile, buttons down the front, scarf at the neck).

The technique stays numpy-free / pure pygame so it ports straight into
snow_fx.py later.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python -m tools.render_snow_fullcover
Output: docs/snow_full_cover/round_5.png
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


# ── the 5 snowman treatments (snow base IDENTICAL; vary hat/scarf/pose) ──────
def _face_common(ov, geom, *, button_eyes=False, stitch=False, glint=True,
                 smile_n=5, smile_wide=False, carrot_len=1.15, carrot_droop=0.18,
                 buttons_n=3, arms_pose="straight"):
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _head_anchor(top, bot, x_min, x_max)
    bxc, byc, _bc = _body_anchor(top, bot, x_min, x_max)
    # arms behind the body so the buttons/scarf overlay them
    _twig_arms(ov, top, bot, x_min, x_max, pose=arms_pose)
    _buttons(ov, bxc, byc, top, bot, x_min, x_max, n=buttons_n)
    _coal_eyes(ov, hx, hy, hr, facing, button=button_eyes, stitch=stitch, glint=glint)
    _coal_smile(ov, hx, hy, hr, facing, n=smile_n, wide=smile_wide)
    _carrot(ov, hx, hy, hr, facing, length_k=carrot_len, droop=carrot_droop)
    return hx, hy, hr, facing


def v1_classic(ov, geom):
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _face_common(ov, geom, smile_n=5, buttons_n=3,
                                      arms_pose="straight")
    _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, tails=1)
    _hat_top(ov, hx, hy, hr, facing, tilt=0.0)


def v2_knit(ov, geom):
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _face_common(ov, geom, button_eyes=True, stitch=True,
                                      glint=False, smile_n=4, buttons_n=3,
                                      arms_pose="straight")
    _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, tails=1, knit=True)
    _hat_beanie(ov, hx, hy, hr, facing)


def v3_minimal(ov, geom):
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _face_common(ov, geom, smile_n=3, buttons_n=2,
                                      carrot_len=1.0, arms_pose="slim")
    _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, tails=1, thin=True)
    _hat_earmuffs(ov, hx, hy, hr, facing)


def v4_hybrid(ov, geom):
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _face_common(ov, geom, button_eyes=False, glint=True,
                                      smile_n=5, buttons_n=3, arms_pose="straight")
    _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, red=PIP_SCARLET,
           white=SCARF_WHITE, tails=1)
    _hat_top(ov, hx, hy, hr, facing, tilt=0.0, band=PIP_GREEN)
    _pip_peeks(ov, hx, hy, hr, top, x_min, x_max)


def v5_jaunty(ov, geom):
    top, bot, x_min, x_max, w, h = geom
    hx, hy, hr, facing = _face_common(ov, geom, smile_n=5, smile_wide=True,
                                      carrot_len=1.28, carrot_droop=0.34,
                                      buttons_n=3, arms_pose="lively")
    _scarf(ov, hx, hy, hr, top, bot, x_min, x_max, tails=2)
    _hat_top(ov, hx, hy, hr, facing, tilt=math.radians(-16))


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


def render_chip(face_fn, target_h=28):
    """A 1x gameplay-size snowman chip (~28px tall) so small-scale legibility of
    the face/hat/arm placement can be judged. Renders the full snowman at native
    res, then scales the whole cell down to `target_h`."""
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
    scale = target_h / ch
    return pygame.transform.smoothscale(cell, (int(cw * scale), int(ch * scale))), (cw, ch)


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
VERSIONS = [
    ("V1 - Classic top-hat",
     "black top hat, round coal eyes, carrot, 5-coal smile, red-white scarf + tail, 3 buttons, straight twig arms",
     v1_classic),
    ("V2 - Knit winter",
     "red-white knit beanie + pom, matching knit scarf, flat stitch-cross button eyes, carrot, smile, buttons, twig arms",
     v2_knit),
    ("V3 - Minimal clean",
     "earmuffs, 2 coal eyes + carrot + short smile, thin scarf, 2 buttons, slim twig arms - tuned for 1x legibility",
     v3_minimal),
    ("V4 - Pip-hybrid",
     "full-classic snowman + DELIBERATE green crown tuft + blue wing-tip peek; scarf in Pip-scarlet, green hat band",
     v4_hybrid),
    ("V5 - Jaunty",
     "tilted top hat, jaunty angled carrot, wide coal-pebble grin, two-tail scarf, livelier twig arm pose - most expressive",
     v5_jaunty),
]

ACCUM = [0.0, 0.25, 0.50, 0.75, 1.0]


def main():
    label_w = 250
    gap = 8
    pad_out = 18
    title_h = 86

    _, (cw, ch) = render_reference(1.0)
    cell_w, cell_h = cw * ZOOM, ch * ZOOM

    ref_loads = [0.0, 0.35, 0.70, 1.00]
    cols_max = max(len(ref_loads), len(ACCUM), 3)
    row_h = cell_h + 30
    sheet_w = label_w + cols_max * (cell_w + gap) + pad_out * 2
    rows = 1 + 1 + len(VERSIONS)         # reference + accumulation + 5 versions
    sheet_h = title_h + rows * (row_h + gap + 30) + pad_out

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
        "Pip - snow FULL COVER -> SNOWMAN  (round 5: accumulation ramp + face from MOUND geometry + full-classic snowman)",
        True, GOLD), (pad_out, 14))
    sheet.blit(fnote.render(
        "Snow = the faithful snow_fx W2 recipe (OFF body + WHITE crest + BLUE under-edge, same cornice/ripple). _mound_overlay now "
        "ramps with extra in [0,1]: extra=0 ~ shipped top-blanket, extra=1 = full enclosing mound; the snow creeps DOWN rear-first.",
        True, DIM), (pad_out, 46))
    sheet.blit(fnote.render(
        "Snowman parts are placed from the MOUND contour via _head_anchor (front ~32% bump, midline) + body contour - NOT Pip's "
        "beak/eye pixels. Every version is full-classic: hat + twig arms + scarf at the neck pinch + coal face + buttons.",
        True, DIM), (pad_out, 64))

    y = title_h

    def cell_label(txt, x, yy, col=WLBL):
        sheet.blit(fcell.render(txt, True, col), (x + 4, yy))

    # ── reference row ──
    sheet.blit(frow.render("REFERENCE - shipped", True, GOLD), (pad_out, y + 14))
    sheet.blit(fnote.render("(real Bird.draw; anchor - do not alter)", True, DIM),
               (pad_out, y + 36))
    cx = label_w + pad_out
    for ld in ref_loads:
        cell, _ = render_reference(ld)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (90, 104, 130),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label(f"snow_load {ld:.2f}", cx, y)
        cx += cell_w + gap
    y += row_h + gap + 30

    # ── accumulation strip (shared, snow only, NO face) ──
    sheet.blit(frow.render("ACCUMULATION", True, GOLD), (pad_out, y + 14))
    sheet.blit(fnote.render("strip - snow only, no face;", True, DIM), (pad_out, y + 36))
    sheet.blit(fnote.render("rear buries first, face last", True, DIM), (pad_out, y + 52))
    cx = label_w + pad_out
    for ex in ACCUM:
        cell, _ = render_cell(ex, face_fn=None)
        panel = on_panel(cell, neutral_panel)
        sheet.blit(panel, (cx, y + 18))
        pygame.draw.rect(sheet, (110, 130, 160),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label(f"extra {ex:.2f}", cx, y, GOLD)
        cx += cell_w + gap
    y += row_h + gap + 30

    # ── version rows ──
    # Each row: [SNOWMAN dark, large] [SNOWMAN whiteout] [1x gameplay chip ~28px]
    for name, note, face_fn in VERSIONS:
        sheet.blit(frow.render(name, True, GOLD), (pad_out, y + 12))
        words = note.split(" ")
        lines = ["", "", "", ""]
        li = 0
        for wword in words:
            if len(lines[li]) > 30 and li < 3:
                li += 1
            lines[li] += wword + " "
        for k, ln in enumerate(lines):
            sheet.blit(fnote.render(ln.strip(), True, DIM), (pad_out, y + 36 + k * 16))

        cx = label_w + pad_out
        snow_cell, _ = render_cell(1.0, face_fn=face_fn)
        # cell 1: SNOWMAN, dark panel, large
        dark = on_panel(snow_cell.copy(), neutral_panel)
        sheet.blit(dark, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("SNOWMAN / dark", cx, y, GOLD)
        cx += cell_w + gap
        # cell 2: SNOWMAN, whiteout panel
        white = on_panel(snow_cell.copy(), whiteout_panel)
        sheet.blit(white, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("SNOWMAN / whiteout", cx, y, GOLD)
        cx += cell_w + gap
        # cell 3: 1x gameplay-size chip (~28px tall), centred in a cell box
        chip, _ = render_chip(face_fn, target_h=28)
        chip_box = neutral_panel(cell_w, cell_h)
        chw, chh = chip.get_size()
        chip_box.blit(chip, ((cell_w - chw) // 2, (cell_h - chh) // 2))
        # show a small 2x and 3x next to it for legibility judging
        c2 = pygame.transform.scale(chip, (chw * 2, chh * 2))
        c3 = pygame.transform.scale(chip, (chw * 3, chh * 3))
        chip_box.blit(c2, (12, cell_h - chh * 2 - 12))
        chip_box.blit(c3, (cell_w - chw * 3 - 12, cell_h - chh * 3 - 12))
        sheet.blit(chip_box, (cx, y + 18))
        pygame.draw.rect(sheet, (120, 140, 170),
                         (cx - 1, y + 17, cell_w + 2, cell_h + 2), 1)
        cell_label("1x chip (+2x/3x)", cx, y, GOLD)

        y += row_h + gap + 30

    out = os.path.join(OUT_DIR, "round_5.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
