"""Look-dev renderer (Round 1): the WARREN EVENT sword — 10 versions.

The Warren event rolls a die for N, then spawns a TIGHT route of N pillars the
player threads. We are replacing the route's repeated pagoda pillar with a
SWORD: ONE blade design reused for every pillar of the event, and it must read
amazing / intimidating / MEAN — the marquee event in the game.

A "pillar" is a TOP obstacle + a BOTTOM obstacle with a flyable gap between:

    TOP  obstacle = a sword hanging point-DOWN from the ceiling
                    (pommel at the very top, grip, crossguard, blade,
                     TIP pointing down toward the gap).
    BOTTOM obstacle = a sword standing point-UP from the ground
                    (pommel at the very bottom, grip, crossguard, blade,
                     TIP pointing up toward the gap).

The flyable GAP sits between the two blade tips — twin blades aimed at the
player from both sides.

True game footprint honoured exactly:
    Playfield 360 x 640, GROUND_Y = 595, column width PIPE_W = 58.
    Route gap height = 172, centred at each step's gap_y. So:
        top blade fills    y = 0          .. gap_y - 86
        bottom blade fills y = gap_y + 86 .. 595
    Route spacing SP = 72 centre-to-centre (only ~14 px of air between
    58-px columns) — a deliberate RACK / WALL of blades; guards must stay
    readable, never mud.

The figure: 10 rows, one per version.
    LEFT  = a 1:1 hero close-up of ONE top+bottom twin-blade PAIR at true
            scale (so blade detail + the gap read), labelled name + palette.
    RIGHT = the version's ROUTE panorama — ~11 twin-blade pairs at true
            vertical scale (640 tall, gap 172) at true SP=72 spacing,
            following a smooth crest curve so it reads as a threadable path.

All art is procedural; supersampled (SS) then smoothscaled down for crisp
edges, the SS/compositing idiom from tools/render_dice_medallion.py.

Run (headless):
    PYTHONPATH=. python tools/render_warren_sword.py
Writes docs/warren_sword/round_1.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()
pygame.display.set_mode((1, 1))

from game import hud  # noqa: E402  vendored bold TTF + cache
from game.draw import lerp_color, _shade_c  # noqa: E402
# The LOCKED joker/clown palette — imported, not re-typed, so the swords sit in
# exactly the same family as the dice medallion that fronts the same event.
from game.dice_medallion import (  # noqa: E402
    PLUM, PLUM_DK, LIME, GOLD, GOLD_DK, CREAM, INK,
)

# ── true game footprint ──────────────────────────────────────────────────────
PIPE_W = 58
GROUND_Y = 595
PLAY_W = 360
PLAY_H = 640
GAP_H = 172
HALF_GAP = GAP_H // 2          # 86
SP = 72                        # route centre-to-centre spacing

# Day sky for contrast — a simple top→bottom blue, per the brief.
SKY_TOP = (96, 165, 230)
SKY_BOT = (175, 215, 245)

# Steel / non-joker metal ramp, shared by the five "without colours" swords.
STEEL_LO = (74, 84, 98)
STEEL_MD = (150, 162, 178)
STEEL_HI = (224, 232, 242)
STEEL_EDGE = (244, 248, 255)
IRON_DK = (40, 44, 52)
LEATHER = (74, 52, 38)
LEATHER_DK = (48, 34, 26)
BLOOD = (150, 26, 32)
BLOOD_DK = (96, 14, 20)
BONE = (236, 230, 210)
BONE_DK = (176, 168, 142)
RUST = (150, 90, 48)
ICE_LO = (150, 196, 228)
ICE_MD = (198, 228, 246)
ICE_HI = (244, 252, 255)
OBSIDIAN = (26, 24, 32)
OBSIDIAN_HI = (84, 80, 100)


# ── small helpers ─────────────────────────────────────────────────────────────

def _vgrad_poly(surf, pts, top_col, bot_col, *, outline=None, ow=2):
    """Fill a convex-ish polygon with a vertical gradient by clipping a banded
    gradient surface to the polygon via an alpha mask. Works for any blade body
    so the metal reads as a lit volume, not a flat fill. `pts` in surf space."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)), int(min(ys))
    w = max(1, int(max(xs)) - x0 + 2)
    h = max(1, int(max(ys)) - y0 + 2)
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        grad.fill(lerp_color(top_col, bot_col, i / max(1, h - 1)) + (255,),
                  (0, i, w, 1))
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    local = [(p[0] - x0, p[1] - y0) for p in pts]
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (x0, y0))
    if outline is not None:
        pygame.draw.polygon(surf, outline, pts, max(1, ow))


def _edge_glow(surf, pts, col, ss, *, alpha=140, spread=5):
    """A soft coloured glow hugging a blade edge polyline (for venom/blood/ice
    edges). Draws the polyline several times at decreasing alpha + width so the
    edge reads as emissive without a full glow-cache disc."""
    for k in range(spread, 0, -1):
        a = int(alpha * (k / spread) * 0.5)
        wln = max(1, int(k * 1.6 * ss))
        layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        if len(pts) >= 2:
            pygame.draw.lines(layer, col + (a,), False, pts, wln)
        surf.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)


def _rivet(surf, x, y, r, col):
    pygame.draw.circle(surf, _shade_c(col, -40), (int(x), int(y)), int(r))
    pygame.draw.circle(surf, _shade_c(col, 50), (int(x - r * 0.3), int(y - r * 0.3)),
                       max(1, int(r * 0.45)))


def _wrap_grip(surf, cx, top, bot, hw, base_col, ss, *, cross=True):
    """A wrapped grip column from `top` to `bot` (surf space), centred on cx,
    half-width hw. Drawn as a stack of leather/cloth bands with a darker valley
    between, plus optional cross-hatch wrap diagonals for the joker cord read."""
    base_col_dk = _shade_c(base_col, -46)
    band_h = max(3, int(5 * ss))
    y = int(top)
    i = 0
    while y < bot:
        c = base_col if i % 2 == 0 else _shade_c(base_col, -22)
        pygame.draw.rect(surf, c, (int(cx - hw), y, int(hw * 2), band_h))
        pygame.draw.line(surf, base_col_dk, (int(cx - hw), y),
                         (int(cx + hw), y), max(1, int(ss)))
        y += band_h
        i += 1
    if cross:
        step = max(4, int(7 * ss))
        for yy in range(int(top), int(bot), step):
            pygame.draw.line(surf, _shade_c(base_col, 36),
                             (int(cx - hw), yy),
                             (int(cx + hw), yy + step), max(1, int(ss)))
            pygame.draw.line(surf, _shade_c(base_col, -30),
                             (int(cx + hw), yy),
                             (int(cx - hw), yy + step), max(1, int(ss)))
    # Tidy the grip sides so the bands sit in a clean column.
    pygame.draw.line(surf, base_col_dk, (int(cx - hw), int(top)),
                     (int(cx - hw), int(bot)), max(1, int(ss)))
    pygame.draw.line(surf, base_col_dk, (int(cx + hw), int(top)),
                     (int(cx + hw), int(bot)), max(1, int(ss)))


# ── the sword frame ───────────────────────────────────────────────────────────
# Each version draws ONE oriented sword into a tall blade box. To honour the
# twin-blade layout, a single `draw_<ver>` is authored point-UP (pommel at the
# bottom of the box, tip at the top), and the TOP obstacle is produced by
# vertically flipping that same surface — so the pair is always one design
# mirrored about the gap, never two different drawings.
#
# A blade box is a SS-supersampled column. Its logical (true-px) size is
#   width  = PIPE_W + 2 * OVERHANG   (guards/quillons may overhang the column)
#   height = the obstacle's true vertical extent.
# Everything inside is laid out in true px * ss, anchored so:
#   x-centre = box centre
#   the TIP touches the box TOP edge (y=0)        -> reaches the gap edge
#   the POMMEL sits at the box BOTTOM edge.
# Geometry (fractions of the obstacle height H, true px):
#   pommel + grip + guard occupy the bottom HILT_FRAC of H; the blade fills the
#   rest up to the tip. HILT_FRAC is clamped so a SHORT bottom obstacle still
#   shows a full hilt and a LONG one just grows the blade — the silhouette the
#   player reads (a blade aimed at them) is constant.

OVERHANG = 12                  # guards may spill this far past the 58-px column
HILT_PX = 132                  # nominal hilt (pommel+grip+guard) height, true px
MIN_BLADE_PX = 40              # never let the blade shrink below this


def _box(H, ss):
    """Allocate a SS blade-box surface for an obstacle of true height H."""
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(H)) * ss
    return pygame.Surface((bw, bh), pygame.SRCALPHA), bw, bh


def _layout(bh, ss):
    """Return key y-coordinates (SS space) for a point-UP sword in a box of SS
    height bh: tip at top (y=0), pommel at the bottom. Returns
    (tip_y, blade_base_y, guard_y, grip_top_y, grip_bot_y, pommel_y)."""
    hilt = HILT_PX * ss
    if hilt > bh - MIN_BLADE_PX * ss:
        hilt = max(0, bh - MIN_BLADE_PX * ss)
    tip_y = int(0)
    guard_y = int(bh - hilt + 0.30 * hilt)   # crossguard sits above the grip
    blade_base_y = guard_y
    grip_top_y = guard_y
    pommel_y = int(bh - max(6 * ss, hilt * 0.10))
    grip_bot_y = int(pommel_y - 4 * ss)
    return tip_y, blade_base_y, guard_y, grip_top_y, grip_bot_y, pommel_y


def _blade_hw(ss):
    """Half-width of the blade base where it meets the guard (SS space). Sits a
    touch inside the column so straight blades don't fill it ear-to-ear."""
    return int((PIPE_W * 0.5 - 6) * ss)


def _guard_hw(ss):
    """Half-width of the crossguard span (SS space) — overhangs the column."""
    return int((PIPE_W * 0.5 + OVERHANG - 2) * ss)


# ── version draw functions (each authored POINT-UP) ──────────────────────────
# Signature: draw_xN(surf, bw, bh, ss) -> draws a point-up sword filling the box.

def _blade_straight(surf, cx, tip_y, base_y, hw, ss, lo, mid, hi, edge,
                    *, fuller=None, taper=0.0):
    """A straight double-edged blade: base half-width hw at base_y, tapering to a
    point at tip_y. `taper` widens the base slightly for a leaf shape. Returns
    the left + right edge polylines (SS space) for optional edge glow."""
    bw = hw * (1.0 + taper)
    left = [(cx - bw, base_y), (cx - hw * 0.18, tip_y)]
    right = [(cx + bw, base_y), (cx + hw * 0.18, tip_y)]
    body = [(cx - bw, base_y), (cx, tip_y), (cx + bw, base_y)]
    _vgrad_poly(surf, body, hi, mid, outline=_shade_c(lo, -30), ow=max(1, int(ss)))
    # Centre ridge highlight gives the blade a bevel.
    pygame.draw.polygon(surf, _shade_c(hi, 30),
                        [(cx - bw * 0.35, base_y), (cx, tip_y),
                         (cx + bw * 0.35, base_y)])
    # Bright cutting edges down both sides.
    pygame.draw.line(surf, edge, (cx - bw, base_y), (cx, tip_y), max(1, int(1.4 * ss)))
    pygame.draw.line(surf, edge, (cx + bw, base_y), (cx, tip_y), max(1, int(1.4 * ss)))
    if fuller is not None:
        pygame.draw.line(surf, fuller, (cx, base_y - int(4 * ss)),
                         (cx, tip_y + int(10 * ss)), max(2, int(3 * ss)))
    return left, right


def _crossguard(surf, cx, gy, ghw, thick, col, ss, *, curve=0.0, dk=None):
    """A horizontal crossguard centred at (cx, gy) spanning +-ghw, `thick` tall.
    `curve` bows the bar toward the blade (negative dips toward tip = up)."""
    dk = dk or _shade_c(col, -50)
    top = [(cx - ghw, gy - thick * 0.5)]
    bot = [(cx - ghw, gy + thick * 0.5)]
    n = 10
    for i in range(n + 1):
        t = i / n
        x = cx - ghw + 2 * ghw * t
        bow = math.sin(t * math.pi) * curve
        top.append((x, gy - thick * 0.5 + bow))
        bot.append((x, gy + thick * 0.5 + bow))
    poly = top + list(reversed(bot))
    pygame.draw.polygon(surf, col, poly)
    pygame.draw.polygon(surf, dk, poly, max(1, int(ss)))
    # End caps (quillon tips) as small balls.
    pygame.draw.circle(surf, col, (int(cx - ghw), int(gy)), int(thick * 0.55))
    pygame.draw.circle(surf, col, (int(cx + ghw), int(gy)), int(thick * 0.55))
    pygame.draw.circle(surf, dk, (int(cx - ghw), int(gy)), int(thick * 0.55), max(1, int(ss)))
    pygame.draw.circle(surf, dk, (int(cx + ghw), int(gy)), int(thick * 0.55), max(1, int(ss)))


def _pommel(surf, cx, py, r, col, ss, *, dk=None):
    dk = dk or _shade_c(col, -55)
    pygame.draw.circle(surf, dk, (int(cx), int(py)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(py)), int(r - ss))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.3), int(py - r * 0.3)), max(1, int(r * 0.4)))


# ---- 1. Jester Saber (joker) -------------------------------------------------
def draw_v1(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    # Curved saber: the tip sweeps to one side. Build a curved double edge.
    curve = hw * 1.7
    spine, edge_l = [], []
    n = 16
    for i in range(n + 1):
        t = i / n                       # 0 at base, 1 at tip
        y = base_y + (tip_y - base_y) * t
        sweep = math.sin(t * math.pi * 0.5) * curve
        wdt = hw * (1.0 - t)
        spine.append((cx + sweep + wdt * 0.15, y))
        edge_l.append((cx + sweep - wdt, y))
    body = spine + list(reversed(edge_l))
    _vgrad_poly(surf, body, GOLD, PLUM, outline=PLUM_DK, ow=max(1, int(ss)))
    # Lime-glow fuller running the curve.
    fuller = [(p[0] - int(2 * ss), p[1]) for p in spine]
    _edge_glow(surf, fuller, LIME, ss, alpha=150, spread=4)
    pygame.draw.lines(surf, LIME, False, fuller, max(1, int(2 * ss)))
    # Bright outer cutting edge.
    pygame.draw.lines(surf, CREAM, False, edge_l, max(1, int(1.6 * ss)))
    # GOLD guard shaped like a wide grin (a shallow up-bowed bar with curled tips).
    _crossguard(surf, cx, gy, ghw, int(11 * ss), GOLD, ss, curve=-int(7 * ss),
                dk=GOLD_DK)
    # Grin teeth notches under the guard.
    for k in range(-2, 3):
        tx = cx + k * int(7 * ss)
        pygame.draw.polygon(surf, CREAM,
                            [(tx - int(2 * ss), gy + int(5 * ss)),
                             (tx + int(2 * ss), gy + int(5 * ss)),
                             (tx, gy + int(10 * ss))])
    # Purple-wrapped grip.
    _wrap_grip(surf, cx, gbot - (gbot - gtop), gbot, int(hw * 0.5), PLUM, ss)
    _wrap_grip(surf, cx, gy + int(10 * ss), gbot, int(hw * 0.5), PLUM, ss)
    # Pommel = gold jester bell.
    br = int(hw * 0.62)
    pygame.draw.circle(surf, GOLD_DK, (cx, py), br)
    pygame.draw.circle(surf, GOLD, (cx, py), int(br - ss))
    pygame.draw.ellipse(surf, PLUM_DK, (cx - br, py + int(br * 0.3),
                                        br * 2, int(br * 0.7)))
    pygame.draw.circle(surf, GOLD, (cx, int(py + br * 0.7)), max(2, int(br * 0.28)))
    pygame.draw.circle(surf, _shade_c(GOLD, 60),
                       (int(cx - br * 0.3), int(py - br * 0.3)), max(1, int(br * 0.35)))


# ---- 2. Harlequin Greatsword (joker) -----------------------------------------
def draw_v2(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.18)      # broad blade
    ghw = _guard_hw(ss)
    body = [(cx - hw, base_y), (cx, tip_y), (cx + hw, base_y)]
    _vgrad_poly(surf, body, STEEL_HI, STEEL_MD, outline=PLUM_DK, ow=max(1, int(ss)))
    # Plum/lime diamond harlequin etch tiled down the blade, clipped to the body.
    diam = pygame.Surface((bw, bh), pygame.SRCALPHA)
    d = int(13 * ss)
    row = 0
    yy = tip_y + int(14 * ss)
    while yy < base_y:
        half = hw * (1.0 - (yy - tip_y) / max(1, (base_y - tip_y)))  # follows taper
        x = cx - half
        col_toggle = row % 2
        while x < cx + half:
            col = PLUM if ((int(x / d) + col_toggle) % 2 == 0) else LIME
            pygame.draw.polygon(diam, col + (150,),
                                [(x, yy), (x + d * 0.5, yy - d * 0.5),
                                 (x + d, yy), (x + d * 0.5, yy + d * 0.5)])
            x += d
        yy += d
        row += 1
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body)
    diam.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(diam, (0, 0))
    pygame.draw.line(surf, CREAM, (cx, base_y), (cx, tip_y + int(12 * ss)),
                     max(1, int(2 * ss)))
    pygame.draw.line(surf, STEEL_EDGE, (cx - hw, base_y), (cx, tip_y), max(1, int(1.5 * ss)))
    pygame.draw.line(surf, STEEL_EDGE, (cx + hw, base_y), (cx, tip_y), max(1, int(1.5 * ss)))
    # Gold guard with downturned quillons.
    _crossguard(surf, cx, gy, ghw, int(12 * ss), GOLD, ss, curve=int(6 * ss),
                dk=GOLD_DK)
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.42), PLUM, ss)
    _pommel(surf, cx, py, int(hw * 0.5), GOLD, ss, dk=GOLD_DK)
    # Lime jewel in the pommel.
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(hw * 0.2)))


# ---- 3. Imp Falchion (joker) -------------------------------------------------
def draw_v3(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    # Wicked falchion: a back edge that bellies out then hooks to a clipped tip.
    back, edge = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        y = base_y + (tip_y - base_y) * t
        belly = math.sin(t * math.pi) * hw * 0.9      # the wide belly
        sweep = (t ** 2) * hw * 1.2                    # tip hooks one way
        edge.append((cx - hw * 0.6 - belly + sweep, y))
        back.append((cx + hw * 0.55 + sweep, y))
    body = back + list(reversed(edge))
    _vgrad_poly(surf, body, _shade_c(PLUM, 50), PLUM_DK, outline=INK, ow=max(1, int(ss)))
    # Lime venom-glow along the cutting (edge) side.
    _edge_glow(surf, edge, LIME, ss, alpha=170, spread=6)
    pygame.draw.lines(surf, (210, 255, 190), False, edge, max(1, int(2 * ss)))
    # Plum lacquer sheen stripe.
    pygame.draw.lines(surf, _shade_c(PLUM, 70), False,
                      [(p[0] + int(4 * ss), p[1]) for p in edge], max(1, int(2 * ss)))
    # Horned guard echoing the medallion imp horns.
    pygame.draw.polygon(surf, INK,
                        [(cx - ghw, gy + int(4 * ss)), (cx - ghw - int(6 * ss), gy - int(16 * ss)),
                         (cx - ghw + int(8 * ss), gy - int(2 * ss))])   # left horn
    pygame.draw.polygon(surf, INK,
                        [(cx + ghw, gy + int(4 * ss)), (cx + ghw + int(6 * ss), gy - int(16 * ss)),
                         (cx + ghw - int(8 * ss), gy - int(2 * ss))])   # right horn
    _crossguard(surf, cx, gy, int(ghw * 0.7), int(10 * ss), GOLD, ss, dk=GOLD_DK)
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.46), PLUM_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.5), GOLD, ss, dk=GOLD_DK)
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(hw * 0.18)))


# ---- 4. Carnival Rapier (joker) ----------------------------------------------
def draw_v4(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 0.5)       # slender
    ghw = _guard_hw(ss)
    body = [(cx - hw, base_y), (cx, tip_y), (cx + hw, base_y)]
    _vgrad_poly(surf, body, STEEL_HI, STEEL_LO, outline=IRON_DK, ow=max(1, int(ss)))
    pygame.draw.line(surf, STEEL_EDGE, (cx, base_y), (cx, tip_y), max(1, int(1.4 * ss)))
    # Swept GOLD basket hilt: nested curved bars sweeping from guard to pommel.
    for k in range(3):
        off = int((6 + k * 7) * ss)
        for sgn in (-1, 1):
            arc = [(cx + sgn * int(4 * ss), gy - int(2 * ss)),
                   (cx + sgn * off, gy + int(10 * ss)),
                   (cx + sgn * int(off * 0.8), gy + int(34 * ss)),
                   (cx + sgn * int(3 * ss), gbot - int(2 * ss))]
            pygame.draw.lines(surf, GOLD, False, arc, max(1, int(2.4 * ss)))
            pygame.draw.lines(surf, GOLD_DK, False, arc, max(1, int(ss)))
    # Straight gold quillons.
    _crossguard(surf, cx, gy, ghw, int(7 * ss), GOLD, ss, dk=GOLD_DK)
    # Purple ribbon trailing from the guard.
    rib = [(cx - int(4 * ss), gy + int(2 * ss)),
           (cx - int(14 * ss), gy + int(20 * ss)),
           (cx - int(6 * ss), gy + int(40 * ss)),
           (cx - int(16 * ss), gy + int(58 * ss))]
    pygame.draw.lines(surf, PLUM, False, rib, max(2, int(4 * ss)))
    pygame.draw.lines(surf, PLUM_DK, False, rib, max(1, int(2 * ss)))
    _wrap_grip(surf, cx, gy + int(6 * ss), gbot, int(5 * ss), PLUM, ss, cross=False)
    _pommel(surf, cx, py, int(8 * ss), GOLD, ss, dk=GOLD_DK)
    # Lime jewel set in the pommel.
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(4 * ss)))
    pygame.draw.circle(surf, _shade_c(LIME, 60), (cx - int(2 * ss), py - int(2 * ss)),
                       max(1, int(2 * ss)))


# ---- 5. Fool's Cleaver (joker) -----------------------------------------------
def draw_v5(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.25)      # heavy, wide
    ghw = _guard_hw(ss)
    # Broad cleaver: near-rectangular slab narrowing to a squared chopping tip.
    body = [(cx - hw, base_y), (cx - hw * 0.9, tip_y + int(20 * ss)),
            (cx - hw * 0.45, tip_y), (cx + hw * 0.85, tip_y),
            (cx + hw, base_y)]
    _vgrad_poly(surf, body, GOLD, _shade_c(PLUM, -10), outline=PLUM_DK, ow=max(1, int(ss)))
    # Gold spine-teeth (saw) down the back (right) edge.
    bx = cx + hw
    yy = base_y - int(6 * ss)
    while yy > tip_y + int(8 * ss):
        pygame.draw.polygon(surf, GOLD,
                            [(bx, yy), (bx + int(7 * ss), yy - int(4 * ss)),
                             (bx, yy - int(9 * ss))])
        pygame.draw.polygon(surf, GOLD_DK,
                            [(bx, yy), (bx + int(7 * ss), yy - int(4 * ss)),
                             (bx, yy - int(9 * ss))], max(1, int(ss)))
        yy -= int(11 * ss)
    # Plum lacquer face with a lime crescent maker's-mark.
    pygame.draw.arc(surf, LIME, (cx - int(hw * 0.5), int(tip_y + bh * 0.18),
                                 int(hw * 0.9), int(hw * 0.9)),
                    math.pi * 0.2, math.pi * 1.1, max(2, int(3 * ss)))
    # Bright chopping edge on the front (left) side.
    pygame.draw.lines(surf, CREAM, False,
                      [(cx - hw, base_y), (cx - hw * 0.9, tip_y + int(20 * ss)),
                       (cx - hw * 0.45, tip_y)], max(2, int(2.2 * ss)))
    _crossguard(surf, cx, gy, int(ghw * 0.85), int(12 * ss), GOLD, ss, dk=GOLD_DK)
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.38), PLUM, ss)
    _pommel(surf, cx, py, int(hw * 0.42), GOLD, ss, dk=GOLD_DK)


# ---- 6. Obsidian Executioner (steel) -----------------------------------------
def draw_v6(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.15)
    ghw = _guard_hw(ss)
    # Brutal squared executioner tip — wide slab, blunt squared end (no point).
    body = [(cx - hw, base_y), (cx - hw, tip_y + int(8 * ss)),
            (cx - hw * 0.7, tip_y), (cx + hw * 0.7, tip_y),
            (cx + hw, tip_y + int(8 * ss)), (cx + hw, base_y)]
    _vgrad_poly(surf, body, OBSIDIAN_HI, OBSIDIAN, outline=(10, 9, 14),
                ow=max(1, int(ss)))
    # Blood-red groove down the centre.
    grv = [(cx, base_y - int(4 * ss)), (cx, tip_y + int(10 * ss))]
    _edge_glow(surf, grv, BLOOD, ss, alpha=120, spread=4)
    pygame.draw.line(surf, BLOOD, (cx, base_y - int(4 * ss)),
                     (cx, tip_y + int(10 * ss)), max(2, int(3 * ss)))
    pygame.draw.line(surf, BLOOD_DK, (cx, base_y - int(4 * ss)),
                     (cx, tip_y + int(10 * ss)), max(1, int(ss)))
    # Cold edge slivers on the black blade.
    pygame.draw.line(surf, OBSIDIAN_HI, (cx - hw, base_y), (cx - hw, tip_y + int(8 * ss)),
                     max(1, int(1.4 * ss)))
    pygame.draw.line(surf, OBSIDIAN_HI, (cx + hw, base_y), (cx + hw, tip_y + int(8 * ss)),
                     max(1, int(1.4 * ss)))
    # Heavy squared iron crossguard.
    pygame.draw.rect(surf, IRON_DK, (int(cx - ghw), int(gy - 7 * ss),
                                     int(ghw * 2), int(14 * ss)))
    pygame.draw.rect(surf, _shade_c(IRON_DK, 40), (int(cx - ghw), int(gy - 7 * ss),
                                                   int(ghw * 2), int(5 * ss)))
    _rivet(surf, cx - ghw + int(6 * ss), gy, int(4 * ss), STEEL_MD)
    _rivet(surf, cx + ghw - int(6 * ss), gy, int(4 * ss), STEEL_MD)
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.42), LEATHER_DK, ss)
    # Squared brutal pommel.
    pygame.draw.rect(surf, IRON_DK, (int(cx - hw * 0.36), int(py - hw * 0.36),
                                     int(hw * 0.72), int(hw * 0.72)))
    pygame.draw.rect(surf, _shade_c(IRON_DK, 50), (int(cx - hw * 0.36), int(py - hw * 0.36),
                                                   int(hw * 0.72), int(hw * 0.2)))


# ---- 7. Bone Khopesh (steel) -------------------------------------------------
def draw_v7(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    # Khopesh: straight near the guard, then a sickle hook curving to the tip.
    inner, outer = [], []
    n = 18
    for i in range(n + 1):
        t = i / n
        y = base_y + (tip_y - base_y) * t
        if t < 0.45:                                   # straight lower section
            sweep = 0.0
            wdt = hw
        else:                                          # hooking sickle
            tt = (t - 0.45) / 0.55
            sweep = -(tt ** 1.4) * hw * 2.0            # curls to one side
            wdt = hw * (1.0 - tt * 0.5)
        inner.append((cx + sweep - wdt, y))
        outer.append((cx + sweep + wdt, y))
    body = outer + list(reversed(inner))
    _vgrad_poly(surf, body, BONE, BONE_DK, outline=_shade_c(IRON_DK, 10), ow=max(1, int(ss)))
    # Sharpened inner (concave) hook edge highlighted.
    pygame.draw.lines(surf, CREAM, False, inner, max(1, int(1.8 * ss)))
    # Hairline cracks in the bone.
    for cxk, cyk in ((cx - int(6 * ss), int(base_y * 0.5)),
                     (cx + int(2 * ss), int(base_y * 0.3))):
        pygame.draw.line(surf, BONE_DK, (cxk, cyk),
                         (cxk + int(5 * ss), cyk - int(14 * ss)), max(1, int(ss)))
    # Dark iron crossguard.
    _crossguard(surf, cx, gy, int(ghw * 0.85), int(10 * ss), IRON_DK, ss,
                dk=(10, 9, 14))
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.42), LEATHER_DK, ss)
    # Skull pommel: a pale dome with two dark eye sockets + a nasal notch.
    sr = int(hw * 0.6)
    pygame.draw.circle(surf, BONE, (cx, py), sr)
    pygame.draw.circle(surf, BONE_DK, (cx, py), sr, max(1, int(ss)))
    pygame.draw.circle(surf, INK, (int(cx - sr * 0.4), int(py - sr * 0.1)), max(2, int(sr * 0.26)))
    pygame.draw.circle(surf, INK, (int(cx + sr * 0.4), int(py - sr * 0.1)), max(2, int(sr * 0.26)))
    pygame.draw.polygon(surf, INK, [(cx, int(py + sr * 0.1)),
                                    (cx - int(sr * 0.16), int(py + sr * 0.5)),
                                    (cx + int(sr * 0.16), int(py + sr * 0.5))])


# ---- 8. Polished Steel Broadsword (steel) ------------------------------------
def draw_v8(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    _blade_straight(surf, cx, tip_y, base_y, hw, ss, STEEL_LO, STEEL_MD,
                    STEEL_HI, STEEL_EDGE, fuller=_shade_c(STEEL_LO, -8), taper=0.12)
    # Clean simple cross with a slight downward sweep.
    _crossguard(surf, cx, gy, ghw, int(9 * ss), STEEL_MD, ss, curve=int(4 * ss),
                dk=IRON_DK)
    # Dark leather grip.
    _wrap_grip(surf, cx, gy + int(9 * ss), gbot, int(hw * 0.42), LEATHER, ss)
    # Round steel pommel with a ring.
    _pommel(surf, cx, py, int(hw * 0.5), STEEL_MD, ss, dk=IRON_DK)
    pygame.draw.circle(surf, _shade_c(STEEL_HI, 0), (cx, py), int(hw * 0.5), max(1, int(ss)))


# ---- 9. Serrated Warblade (steel) --------------------------------------------
def draw_v9(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    body = [(cx - hw, base_y), (cx, tip_y), (cx + hw, base_y)]
    _vgrad_poly(surf, body, _shade_c(STEEL_MD, -30), _shade_c(STEEL_LO, -10),
                outline=IRON_DK, ow=max(1, int(ss)))
    # Rust/blood wash blotches.
    for fy in (0.35, 0.6, 0.8):
        ry = int(tip_y + (base_y - tip_y) * fy)
        rw = int(hw * (1.0 - (ry - tip_y) / max(1, base_y - tip_y)) * 0.5)
        pygame.draw.circle(surf, RUST, (cx + int(rw * 0.3), ry), max(2, int(rw)))
    # Jagged sawtooth on both edges — sample the taper, push teeth outward.
    n = 14
    for sgn in (-1, 1):
        pts = []
        for i in range(n + 1):
            t = i / n
            y = base_y + (tip_y - base_y) * t
            w = hw * (1.0 - t)
            jag = (int(5 * ss) if i % 2 == 0 else 0)
            pts.append((cx + sgn * (w + jag), y))
        pygame.draw.lines(surf, STEEL_EDGE, False, pts, max(1, int(1.6 * ss)))
        # Dark tooth roots.
        pygame.draw.lines(surf, IRON_DK, False,
                          [(cx + sgn * (hw * (1.0 - i / n)), base_y + (tip_y - base_y) * (i / n))
                           for i in range(n + 1)], max(1, int(ss)))
    pygame.draw.line(surf, _shade_c(STEEL_MD, 20), (cx, base_y), (cx, tip_y + int(8 * ss)),
                     max(1, int(2 * ss)))
    # Notched gunmetal guard.
    _crossguard(surf, cx, gy, ghw, int(10 * ss), _shade_c(STEEL_LO, -6), ss, dk=IRON_DK)
    _wrap_grip(surf, cx, gy + int(10 * ss), gbot, int(hw * 0.42), LEATHER_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.46), _shade_c(STEEL_LO, -6), ss, dk=IRON_DK)
    # A blood smear on the pommel.
    pygame.draw.circle(surf, BLOOD_DK, (cx + int(3 * ss), py), max(1, int(hw * 0.16)))


# ---- 10. Crystal Glaive (steel) ----------------------------------------------
def draw_v10(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.05)
    ghw = _guard_hw(ss)
    # Faceted translucent crystal blade — a long leaf with internal facet lines.
    body = [(cx - hw, base_y), (cx - hw * 0.5, base_y - int(bh * 0.18)),
            (cx, tip_y), (cx + hw * 0.5, base_y - int(bh * 0.18)),
            (cx + hw, base_y)]
    _vgrad_poly(surf, body, ICE_HI, ICE_LO, outline=_shade_c(ICE_LO, -40), ow=max(1, int(ss)))
    # Internal facet planes — translucent shards reading as a gem.
    facets = [
        [(cx, tip_y), (cx - hw * 0.5, base_y - int(bh * 0.18)), (cx, base_y - int(bh * 0.3))],
        [(cx, tip_y), (cx + hw * 0.5, base_y - int(bh * 0.18)), (cx, base_y - int(bh * 0.3))],
        [(cx - hw, base_y), (cx - hw * 0.5, base_y - int(bh * 0.18)),
         (cx, base_y - int(bh * 0.05)), (cx, base_y)],
        [(cx + hw, base_y), (cx + hw * 0.5, base_y - int(bh * 0.18)),
         (cx, base_y - int(bh * 0.05)), (cx, base_y)],
    ]
    shades = (_shade_c(ICE_MD, 18), _shade_c(ICE_MD, -16),
              _shade_c(ICE_LO, 10), _shade_c(ICE_LO, -18))
    for f, sc in zip(facets, shades):
        pygame.draw.polygon(surf, sc, f)
        pygame.draw.polygon(surf, _shade_c(ICE_HI, 0), f, max(1, int(ss)))
    # Cold blue-white edge glow + crisp rime edge.
    _edge_glow(surf, [(cx - hw, base_y), (cx, tip_y)], (180, 220, 255), ss,
               alpha=120, spread=5)
    _edge_glow(surf, [(cx + hw, base_y), (cx, tip_y)], (180, 220, 255), ss,
               alpha=120, spread=5)
    pygame.draw.line(surf, ICE_HI, (cx - hw, base_y), (cx, tip_y), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, ICE_HI, (cx + hw, base_y), (cx, tip_y), max(1, int(1.6 * ss)))
    # Dark icy-iron guard with frost.
    _crossguard(surf, cx, gy, ghw, int(9 * ss), (96, 120, 150), ss, dk=(40, 56, 78))
    _wrap_grip(surf, cx, gy + int(9 * ss), gbot, int(hw * 0.4), (54, 70, 92), ss)
    _pommel(surf, cx, py, int(hw * 0.46), (120, 156, 196), ss, dk=(40, 56, 78))
    pygame.draw.circle(surf, ICE_HI, (cx, py), max(2, int(hw * 0.18)))


# ── version registry ──────────────────────────────────────────────────────────
VERSIONS = [
    ("Jester Saber", "joker colors", draw_v1),
    ("Harlequin Greatsword", "joker colors", draw_v2),
    ("Imp Falchion", "joker colors", draw_v3),
    ("Carnival Rapier", "joker colors", draw_v4),
    ("Fool's Cleaver", "joker colors", draw_v5),
    ("Obsidian Executioner", "steel", draw_v6),
    ("Bone Khopesh", "steel", draw_v7),
    ("Polished Steel Broadsword", "steel", draw_v8),
    ("Serrated Warblade", "steel", draw_v9),
    ("Crystal Glaive", "steel", draw_v10),
]


# ── obstacle compositing (true px) ────────────────────────────────────────────

def _render_obstacle(draw_fn, H_true, ss, *, flip):
    """Render ONE obstacle (height H_true true-px) and smoothscale to true px.
    Always authored point-UP; `flip` produces the point-DOWN ceiling sword by
    vertical-mirroring the SAME drawing, so the pair is one design about the gap.
    Returns a true-px SRCALPHA surface (PIPE_W + 2*OVERHANG) wide."""
    surf, bw, bh = _box(H_true, ss)
    draw_fn(surf, bw, bh, ss)
    out_w = PIPE_W + 2 * OVERHANG
    out_h = max(1, int(H_true))
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    if flip:
        small = pygame.transform.flip(small, False, True)
    return small


def _blit_pair(dest, draw_fn, col_cx, gap_y, ss):
    """Place a twin-blade PAIR on `dest` at column centre col_cx, gap centre
    gap_y. TOP obstacle: y=0..gap_y-HALF_GAP (point-down). BOTTOM obstacle:
    y=gap_y+HALF_GAP..GROUND_Y (point-up)."""
    top_h = max(1, gap_y - HALF_GAP)
    bot_h = max(1, GROUND_Y - (gap_y + HALF_GAP))
    x_left = int(col_cx - (PIPE_W + 2 * OVERHANG) / 2)
    top = _render_obstacle(draw_fn, top_h, ss, flip=True)
    dest.blit(top, (x_left, 0))                       # tip now points DOWN to gap
    bot = _render_obstacle(draw_fn, bot_h, ss, flip=False)
    dest.blit(bot, (x_left, gap_y + HALF_GAP))        # tip points UP to gap


def _sky(w, h):
    s = pygame.Surface((w, h))
    for i in range(h):
        s.fill(lerp_color(SKY_TOP, SKY_BOT, i / max(1, h - 1)), (0, i, w, 1))
    return s


def _ground(surf, w):
    pygame.draw.rect(surf, (84, 132, 58), (0, GROUND_Y, w, surf.get_height() - GROUND_Y))
    pygame.draw.line(surf, (60, 100, 40), (0, GROUND_Y), (w, GROUND_Y), 2)


def _crest_gap_y(step, n_steps):
    """A smooth crest route: gap centre rises to a peak mid-route then falls, so
    the panorama reads as one threadable arc. Clamped so both blades stay valid
    (gap fully on-screen above the ground)."""
    lo, hi = 150, 430
    t = step / max(1, n_steps - 1)
    arc = math.sin(t * math.pi)                       # 0..1..0 crest
    gy = hi - (hi - lo) * arc
    return int(max(HALF_GAP + 30, min(GROUND_Y - HALF_GAP - 30, gy)))


# ── sheet builder ─────────────────────────────────────────────────────────────

def main():
    SS = 4

    # Hero close-up: ONE pair on a true-scale 360x640 strip, but we only need a
    # narrow column, so the hero panel is a slice around a single column.
    HERO_W = PIPE_W + 2 * OVERHANG + 24
    HERO_H = PLAY_H

    # Route panorama: ~11 pairs at true SP spacing on a full-height strip.
    N_STEPS = 11
    ROUTE_W = SP * N_STEPS + 40
    ROUTE_H = PLAY_H

    pad = 18
    head = 88
    label_w = 0
    row_gap = 14
    name_strip = 30

    # Each row: [hero panel][gap][route panel], with a name strip on top.
    inner_gap = 22
    row_w = HERO_W + inner_gap + ROUTE_W
    row_h = name_strip + max(HERO_H, ROUTE_H)

    sheet_w = pad * 2 + row_w
    sheet_h = head + len(VERSIONS) * (row_h + row_gap) + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Warren Sword Route — Round 1: 10 versions", True, (255, 255, 255)), (pad, 14))
    sheet.blit(sub_f.render(
        "TWIN BLADES meeting at the gap: ceiling sword point-DOWN + ground sword point-UP, "
        "tips at the gap edge. True footprint (PIPE_W=58, GAP=172, GROUND_Y=595).",
        True, (200, 205, 215)), (pad, 46))
    sheet.blit(sub_f.render(
        "LEFT = 1:1 hero pair (true scale).  RIGHT = route panorama, 11 pairs at true SP=72 "
        "spacing on a crest curve.  ~5 joker-palette swords, ~5 steel.",
        True, (170, 178, 190)), (pad, 64))

    name_f = hud._font(20, True)
    tag_f = hud._font(14, True)

    for idx, (name, palette_tag, draw_fn) in enumerate(VERSIONS):
        ry = head + idx * (row_h + row_gap)
        # Name strip.
        strip = pygame.Surface((row_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        tag_col = LIME if palette_tag == "joker colors" else (150, 200, 240)
        strip.blit(name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255)), (8, 4))
        ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
        strip.blit(tag_f.render(f"({palette_tag})", True, tag_col),
                   (12 + ntxt.get_width(), 8))
        sheet.blit(strip, (pad, ry))

        body_y = ry + name_strip

        # --- hero close-up: a single centred pair, gap mid-screen ---
        hero = _sky(HERO_W, HERO_H)
        _ground(hero, HERO_W)
        _blit_pair(hero, draw_fn, HERO_W // 2, 300, SS)
        # Gap guide lines so the lethal gap reads in the review.
        pygame.draw.line(hero, (255, 255, 255), (0, 300 - HALF_GAP),
                         (HERO_W, 300 - HALF_GAP), 1)
        pygame.draw.line(hero, (255, 255, 255), (0, 300 + HALF_GAP),
                         (HERO_W, 300 + HALF_GAP), 1)
        pygame.draw.rect(hero, (10, 12, 18), hero.get_rect(), 2)
        sheet.blit(hero, (pad, body_y))

        # --- route panorama ---
        route = _sky(ROUTE_W, ROUTE_H)
        _ground(route, ROUTE_W)
        for step in range(N_STEPS):
            cx = 20 + SP // 2 + step * SP
            gy = _crest_gap_y(step, N_STEPS)
            _blit_pair(route, draw_fn, cx, gy, SS)
        pygame.draw.rect(route, (10, 12, 18), route.get_rect(), 2)
        sheet.blit(route, (pad + HERO_W + inner_gap, body_y))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_sword")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
