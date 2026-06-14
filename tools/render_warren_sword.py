"""Look-dev renderer (Round 2): the WARREN EVENT sword — 10 versions.

Round-2 brief: at the tight SP=72 route spacing the ONE job is to make the
threadable sky-gap between the two facing blade TIPS instantly obvious. Three
non-negotiable GATES drive EVERY version (all 10 must pass):
  1. GAP READABILITY — the sky-gap is the brightest, sharpest horizontal band
     in the column. Every blade taper ends in a HARD point with a strong value
     break (DARK body -> BRIGHT gap). No curved "wavy hedge" tips: every blade
     here is straightened so its central axis is vertical and the apex is a
     true point that meets the sky as a hard dark->light edge.
  2. DAY-SKY CONTRAST — the blade BODY value differs from the day-sky blue by
     well over ~20%. Pale/icy/joker bodies get an OPAQUE dark core and a hard
     dark (or hard cold-white) keyline so they always hold a silhouette.
  3. DE-NOISE FOR SCALE — read at ~30-40px wide in motion: 2-3 LARGE bold
     elements per pattern. No fine harlequin grids, no fine serration combs,
     no swept basket hilts, no fine bone texture.

Key direction (predicted winner): the Plum & Lime joker palette run AS A SKIN
over the strongest STEEL silhouettes — same brutal shape, with vs without joker
colours. Joker treatment = DESATURATED plum body, acid LIME as an ACCENT only
(a glow line / jewel, never a fill), GOLD as metal (guard/rivets), not bling.
The skinning is literal: the steel silhouette builders (a hard-taper straight
blade + a squared executioner slab + a chunky-serration blade) take a PALETTE
argument, so a steel sword and its joker twin are the SAME geometry call with a
different colour pack — only the groove/edge accent and guard metal change.

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
            scale (so blade detail + the gap read), labelled name + tag.
    RIGHT = the version's day-sky ROUTE panorama — 11 twin-blade pairs at true
            vertical scale (640 tall, gap 172) at true SP=72 spacing.
    For the TOP 3 (cells 1, 5, 6) a third NIGHT-sky route strip is appended
    so the red groove / lime glow / plum body read in both biomes.

All art is procedural; supersampled (SS) then smoothscaled down for crisp
edges, the SS/compositing idiom from tools/render_dice_medallion.py.

Run (headless):
    PYTHONPATH=. python tools/render_warren_sword.py
Writes docs/warren_sword/round_2.png.
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
# Night sky for the top-3 second-biome check (red groove / lime glow / plum must
# still read against a dark gradient, not just day blue).
NIGHT_TOP = (5, 8, 30)
NIGHT_BOT = (35, 55, 115)

# Steel / non-joker metal ramp, shared by the steel swords.
STEEL_LO = (74, 84, 98)
STEEL_MD = (150, 162, 178)
STEEL_HI = (224, 232, 242)
STEEL_EDGE = (244, 248, 255)
IRON_DK = (40, 44, 52)
LEATHER = (74, 52, 38)
LEATHER_DK = (48, 34, 26)
BLOOD = (170, 28, 34)
BLOOD_DK = (96, 14, 20)
RUST = (150, 90, 48)
# Gunmetal (darker, cooler steel for the warblades — holds value on day sky).
GUN_LO = (44, 50, 60)
GUN_MD = (96, 106, 122)
GUN_HI = (170, 182, 200)
# Salvaged crystal: OPAQUE dark-blue core + hard cold-white rim (GATE 2). The
# body is deliberately DARK so it reads as a silhouette, not a translucent wash.
ICE_CORE = (30, 52, 96)        # opaque dark-blue body (NOT a pale tint)
ICE_MD = (60, 96, 156)
ICE_HI = (150, 196, 240)
ICE_RIM = (224, 244, 255)      # hard cold-white keyline
ICE_DK = (14, 26, 56)
OBSIDIAN = (24, 22, 30)
OBSIDIAN_HI = (74, 70, 92)
OBSIDIAN_DK = (9, 8, 13)
# Desaturated plum body for joker blades — darkened ~15% vs the medallion plum
# so it clears the day-sky blue by well over 20% (GATE 2).
PLUM_BODY = _shade_c(PLUM, -18)
PLUM_BODY_DK = _shade_c(PLUM_DK, -10)
PLUM_LAC = _shade_c(PLUM, 28)  # lacquer sheen highlight (kept narrow)
GUNPLUM_LO = (46, 36, 60)      # gunmetal-plum for the joker warblade
GUNPLUM_HI = (108, 84, 138)


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
    """A soft coloured glow hugging a blade edge polyline (lime / blood / ice).
    Draws the polyline several times at decreasing alpha + width so the edge
    reads as emissive without a full glow-cache disc. ADD-blended so it pops on
    both day and night sky."""
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


def _wrap_grip(surf, cx, top, bot, hw, base_col, ss):
    """A wrapped grip column from `top` to `bot` (surf space), centred on cx,
    half-width hw. Drawn as a stack of two-tone bands — kept LARGE/bold (GATE 3),
    no fine cross-hatch — so the grip reads as a clean dark column under the
    blade and never competes with the gap."""
    base_col_dk = _shade_c(base_col, -46)
    band_h = max(4, int(7 * ss))
    y = int(top)
    i = 0
    while y < bot:
        c = base_col if i % 2 == 0 else _shade_c(base_col, -26)
        pygame.draw.rect(surf, c, (int(cx - hw), y, int(hw * 2), band_h))
        pygame.draw.line(surf, base_col_dk, (int(cx - hw), y),
                         (int(cx + hw), y), max(1, int(ss)))
        y += band_h
        i += 1
    pygame.draw.line(surf, base_col_dk, (int(cx - hw), int(top)),
                     (int(cx - hw), int(bot)), max(1, int(ss)))
    pygame.draw.line(surf, base_col_dk, (int(cx + hw), int(top)),
                     (int(cx + hw), int(bot)), max(1, int(ss)))


# ── the sword frame ───────────────────────────────────────────────────────────
# Each version draws ONE oriented sword into a tall blade box, authored point-UP
# (pommel at the bottom of the box, tip at the top); the TOP obstacle is the
# SAME surface vertically flipped — the pair is always one design mirrored about
# the gap, never two drawings.
#
# A blade box is a SS-supersampled column. Logical (true-px) size is
#   width  = PIPE_W + 2 * OVERHANG   (guards/quillons may overhang the column)
#   height = the obstacle's true vertical extent.
# Layout anchors: x-centre = box centre; TIP touches box TOP (y=0) -> reaches the
# gap edge; POMMEL sits at box BOTTOM.

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


# ── shared STEEL silhouette builders (taken as palette packs so a steel sword
#    and its joker twin are the SAME geometry call) ────────────────────────────

def _hard_taper_blade(surf, cx, tip_y, base_y, hw, ss, lo, mid, hi, edge, ol,
                      *, taper=0.0, groove=None, groove_w=3.0, groove_glow=None):
    """A STRAIGHT double-edged blade on a vertical axis tapering to a HARD point
    at tip_y (GATE 1). The body polygon's apex IS the box top, so the dark body
    meets the bright sky as a single razor edge with no blunt cap and no bright
    nub. `ol` is the hard silhouette keyline (dark or cold-white) for GATE 2.
    Optional centre `groove` (with optional emissive `groove_glow`) is kept to
    ONE thin line so it survives night biome (GATE 3)."""
    bw = hw * (1.0 + taper)
    body = [(cx - bw, base_y), (cx, tip_y), (cx + bw, base_y)]
    _vgrad_poly(surf, body, hi, mid, outline=ol, ow=max(2, int(1.6 * ss)))
    # Centre bevel ridge — one bold light wedge, reads at scale.
    pygame.draw.polygon(surf, _shade_c(hi, 24),
                        [(cx - bw * 0.30, base_y), (cx, tip_y),
                         (cx + bw * 0.30, base_y)])
    # Bright cutting edges, stopping just shy of the apex so the apex stays a
    # clean dark->sky break instead of a bright dot.
    pygame.draw.line(surf, edge, (cx - bw, base_y),
                     (cx, tip_y + int(3 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, edge, (cx + bw, base_y),
                     (cx, tip_y + int(3 * ss)), max(1, int(1.6 * ss)))
    if groove is not None:
        if groove_glow is not None:
            _edge_glow(surf, [(cx, base_y - int(4 * ss)), (cx, tip_y + int(16 * ss))],
                       groove_glow, ss, alpha=130, spread=4)
        pygame.draw.line(surf, groove, (cx, base_y - int(4 * ss)),
                         (cx, tip_y + int(16 * ss)), max(2, int(groove_w * ss)))


def _executioner_slab(surf, cx, tip_y, base_y, hw, ss, lo, hi, ol, edge_hi,
                      *, groove, groove_glow=None):
    """The hero executioner silhouette: a broad faceted slab that pinches to a
    HARD chamfered point (NOT a blunt square) so the gap stays sharp (GATE 1).
    Big flat side facets, one thin centre groove. Palette-packed so the steel
    cell 1 and the joker cell 5 are this exact geometry with a colour swap."""
    # The blade tapers in slightly then drives to a near-point: two long facets
    # meeting at a tight chamfer makes a hard dark->sky break at the tip.
    tipw = hw * 0.22
    body = [(cx - hw, base_y),
            (cx - hw * 0.86, tip_y + int(36 * ss)),
            (cx - tipw, tip_y),
            (cx + tipw, tip_y),
            (cx + hw * 0.86, tip_y + int(36 * ss)),
            (cx + hw, base_y)]
    _vgrad_poly(surf, body, hi, lo, outline=ol, ow=max(2, int(1.6 * ss)))
    # Two bold facet shades split down the centre (large shapes, GATE 3).
    pygame.draw.polygon(surf, _shade_c(hi, 16),
                        [(cx - hw, base_y), (cx - hw * 0.86, tip_y + int(36 * ss)),
                         (cx - tipw, tip_y), (cx, tip_y),
                         (cx, base_y)])
    pygame.draw.polygon(surf, _shade_c(lo, 18),
                        [(cx + hw, base_y), (cx + hw * 0.86, tip_y + int(36 * ss)),
                         (cx + tipw, tip_y), (cx, tip_y),
                         (cx, base_y)])
    # Hard edge slivers down the chamfer so the silhouette has a crisp rim.
    pygame.draw.line(surf, edge_hi, (cx - hw, base_y),
                     (cx - tipw, tip_y), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, edge_hi, (cx + hw, base_y),
                     (cx + tipw, tip_y), max(1, int(1.6 * ss)))
    # ONE restrained thin centre groove (survives night biome).
    if groove_glow is not None:
        _edge_glow(surf, [(cx, base_y - int(4 * ss)), (cx, tip_y + int(20 * ss))],
                   groove_glow, ss, alpha=120, spread=3)
    pygame.draw.line(surf, groove, (cx, base_y - int(4 * ss)),
                     (cx, tip_y + int(20 * ss)), max(2, int(2.4 * ss)))


def _serrated_blade(surf, cx, tip_y, base_y, hw, ss, lo, mid, hi, edge, ol,
                    *, teeth=5, tooth_col=None, groove=None, groove_glow=None):
    """A straight blade whose edges are cut into a FEW big chunky teeth (GATE 3:
    ~5 large teeth, not a fine comb). The TIP itself is left CLEAN and points to
    a hard apex so the gap stays bright (GATE 1). Teeth only bite the lower 2/3
    of each edge. Optional `tooth_col` gilds the tooth tips (joker gold)."""
    body = [(cx - hw, base_y), (cx, tip_y), (cx + hw, base_y)]
    _vgrad_poly(surf, body, hi, mid, outline=ol, ow=max(2, int(1.6 * ss)))
    pygame.draw.polygon(surf, _shade_c(hi, 20),
                        [(cx - hw * 0.28, base_y), (cx, tip_y),
                         (cx + hw * 0.28, base_y)])
    # Big triangular teeth notched OUT of each edge, lower 2/3 only; the top
    # third (the tip) is a clean straight taper into the apex.
    clean_top = tip_y + (base_y - tip_y) * 0.34
    for sgn in (-1, 1):
        for i in range(teeth):
            t0 = i / teeth
            t1 = (i + 1) / teeth
            y0 = clean_top + (base_y - clean_top) * t0
            y1 = clean_top + (base_y - clean_top) * t1
            ym = (y0 + y1) * 0.5
            w0 = hw * (1.0 - (y0 - tip_y) / max(1, base_y - tip_y))
            w1 = hw * (1.0 - (y1 - tip_y) / max(1, base_y - tip_y))
            wm = hw * (1.0 - (ym - tip_y) / max(1, base_y - tip_y))
            tooth = [(cx + sgn * w0, y0),
                     (cx + sgn * (wm + 8 * ss), ym),
                     (cx + sgn * w1, y1)]
            pygame.draw.polygon(surf, mid, tooth)
            pygame.draw.polygon(surf, ol, tooth, max(1, int(ss)))
            if tooth_col is not None:
                pygame.draw.line(surf, tooth_col,
                                 (cx + sgn * w0, y0),
                                 (cx + sgn * (wm + 8 * ss), ym), max(1, int(1.4 * ss)))
    # Clean bright edge on the upper (tip) third only — keeps the apex sharp.
    pygame.draw.line(surf, edge, (cx, tip_y + int(3 * ss)),
                     (cx - hw * 0.66, clean_top), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, edge, (cx, tip_y + int(3 * ss)),
                     (cx + hw * 0.66, clean_top), max(1, int(1.6 * ss)))
    if groove is not None:
        if groove_glow is not None:
            _edge_glow(surf, [(cx, base_y - int(4 * ss)), (cx, tip_y + int(16 * ss))],
                       groove_glow, ss, alpha=130, spread=4)
        pygame.draw.line(surf, groove, (cx, base_y - int(4 * ss)),
                         (cx, tip_y + int(16 * ss)), max(2, int(2.4 * ss)))


# ── version draw functions (each authored POINT-UP) ──────────────────────────
# Signature: draw_xN(surf, bw, bh, ss) -> draws a point-up sword filling the box.

# ---- 1. Obsidian Executioner [HERO BASELINE] (steel) -------------------------
# KEEP: black faceted blade, hard tip, riveted iron guard. The blood-red groove
# is a single RESTRAINED thin line (no bloom) so it survives the night biome.
def draw_v1(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.12)
    ghw = _guard_hw(ss)
    _executioner_slab(surf, cx, tip_y, base_y, hw, ss, OBSIDIAN, OBSIDIAN_HI,
                       OBSIDIAN_DK, OBSIDIAN_HI, groove=BLOOD, groove_glow=None)
    # Heavy squared iron crossguard with two big rivets (2 bold elements).
    pygame.draw.rect(surf, IRON_DK, (int(cx - ghw), int(gy - 8 * ss),
                                     int(ghw * 2), int(16 * ss)))
    pygame.draw.rect(surf, _shade_c(IRON_DK, 44), (int(cx - ghw), int(gy - 8 * ss),
                                                   int(ghw * 2), int(5 * ss)))
    pygame.draw.rect(surf, OBSIDIAN_DK, (int(cx - ghw), int(gy - 8 * ss),
                                         int(ghw * 2), int(16 * ss)), max(1, int(ss)))
    _rivet(surf, cx - ghw + int(8 * ss), gy, int(5 * ss), STEEL_MD)
    _rivet(surf, cx + ghw - int(8 * ss), gy, int(5 * ss), STEEL_MD)
    _wrap_grip(surf, cx, gy + int(9 * ss), gbot, int(hw * 0.40), LEATHER_DK, ss)
    # Squared brutal pommel.
    pr = int(hw * 0.40)
    pygame.draw.rect(surf, IRON_DK, (int(cx - pr), int(py - pr), int(pr * 2), int(pr * 2)))
    pygame.draw.rect(surf, _shade_c(IRON_DK, 50), (int(cx - pr), int(py - pr),
                                                   int(pr * 2), int(pr * 0.6)))
    pygame.draw.rect(surf, OBSIDIAN_DK, (int(cx - pr), int(py - pr),
                                         int(pr * 2), int(pr * 2)), max(1, int(ss)))


# ---- 2. Serrated Warblade (steel) --------------------------------------------
# Chunky 5-tooth serration (count cut ~40%, each tooth bigger). Rust/blood on
# guard + lower blade only; tip stays CLEAN so the gap reads bright.
def draw_v2(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    _serrated_blade(surf, cx, tip_y, base_y, hw, ss, GUN_LO, GUN_MD, GUN_HI,
                    STEEL_EDGE, IRON_DK, teeth=5,
                    groove=_shade_c(GUN_MD, 16), groove_glow=None)
    # Rust wash only on the LOWER blade (near the guard), never near the tip.
    for fy in (0.78, 0.9):
        ry = int(tip_y + (base_y - tip_y) * fy)
        rw = int(hw * (1.0 - (ry - tip_y) / max(1, base_y - tip_y)) * 0.6)
        pygame.draw.circle(surf, RUST, (cx + int(rw * 0.2), ry), max(2, int(rw)))
    # Notched gunmetal guard, rust-touched.
    _crossguard(surf, cx, gy, ghw, int(11 * ss), GUN_LO, ss, dk=IRON_DK)
    pygame.draw.circle(surf, RUST, (int(cx - ghw + 6 * ss), int(gy)), max(2, int(3 * ss)))
    _wrap_grip(surf, cx, gy + int(10 * ss), gbot, int(hw * 0.42), LEATHER_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.46), GUN_LO, ss, dk=IRON_DK)
    pygame.draw.circle(surf, BLOOD_DK, (cx + int(3 * ss), py), max(1, int(hw * 0.16)))


# ---- 3. Headsman's Greatsword [NEW] (steel) ----------------------------------
# Broad dark steel, HARD straight taper to a sharp point, heavy steel cross.
# A clean mean shape with high day-sky contrast (darkened steel body).
def draw_v3(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.22)     # broad
    ghw = _guard_hw(ss)
    _hard_taper_blade(surf, cx, tip_y, base_y, hw, ss,
                      _shade_c(STEEL_LO, -18), _shade_c(STEEL_MD, -30),
                      _shade_c(STEEL_HI, -28), STEEL_EDGE, IRON_DK,
                      taper=0.06, groove=_shade_c(STEEL_LO, -34), groove_w=3.4)
    # Heavy plain steel cross — one bold bar, slight downturn, big square block
    # centre boss (2 bold elements).
    _crossguard(surf, cx, gy, ghw, int(13 * ss), _shade_c(STEEL_MD, -16), ss,
                curve=int(5 * ss), dk=IRON_DK)
    pygame.draw.rect(surf, _shade_c(STEEL_MD, -6),
                     (int(cx - 9 * ss), int(gy - 9 * ss), int(18 * ss), int(18 * ss)))
    pygame.draw.rect(surf, IRON_DK,
                     (int(cx - 9 * ss), int(gy - 9 * ss), int(18 * ss), int(18 * ss)),
                     max(1, int(ss)))
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.34), LEATHER, ss)
    _pommel(surf, cx, py, int(hw * 0.42), _shade_c(STEEL_MD, -10), ss, dk=IRON_DK)


# ---- 4. Crystal Glaive [SALVAGE] (steel) -------------------------------------
# Ice concept SALVAGED: an OPAQUE DARK-BLUE core + a hard COLD-WHITE rim keyline
# so it holds a silhouette on day sky (GATE 2). Straight, hard apex (GATE 1).
def draw_v4(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    # Dark opaque body first (the silhouette), then big facet wedges, then the
    # hard cold-white rim. No translucency anywhere.
    body = [(cx - hw, base_y), (cx, tip_y), (cx + hw, base_y)]
    _vgrad_poly(surf, body, ICE_MD, ICE_CORE, outline=ICE_DK, ow=max(2, int(1.8 * ss)))
    # TWO big facet planes (left dark, right lit) — bold, reads at scale.
    pygame.draw.polygon(surf, _shade_c(ICE_CORE, 12),
                        [(cx - hw, base_y), (cx, tip_y), (cx, base_y)])
    pygame.draw.polygon(surf, _shade_c(ICE_MD, 14),
                        [(cx + hw, base_y), (cx, tip_y), (cx, base_y)])
    # One bold cold highlight wedge down the centre ridge.
    pygame.draw.polygon(surf, ICE_HI,
                        [(cx - hw * 0.18, base_y), (cx, tip_y),
                         (cx + hw * 0.18, base_y)])
    # Hard cold-white rim keyline (the GATE-2 fix) + restrained edge glow.
    _edge_glow(surf, [(cx - hw, base_y), (cx, tip_y)], (150, 200, 255), ss,
               alpha=90, spread=3)
    _edge_glow(surf, [(cx + hw, base_y), (cx, tip_y)], (150, 200, 255), ss,
               alpha=90, spread=3)
    pygame.draw.line(surf, ICE_RIM, (cx - hw, base_y), (cx, tip_y + int(3 * ss)),
                     max(1, int(1.8 * ss)))
    pygame.draw.line(surf, ICE_RIM, (cx + hw, base_y), (cx, tip_y + int(3 * ss)),
                     max(1, int(1.8 * ss)))
    # Dark icy-iron guard so the hilt reads dark against day sky too.
    _crossguard(surf, cx, gy, ghw, int(10 * ss), (52, 78, 116), ss, dk=ICE_DK)
    _wrap_grip(surf, cx, gy + int(9 * ss), gbot, int(hw * 0.40), (34, 50, 78), ss)
    _pommel(surf, cx, py, int(hw * 0.46), (70, 104, 150), ss, dk=ICE_DK)
    pygame.draw.circle(surf, ICE_RIM, (cx, py), max(2, int(hw * 0.18)))


# ---- 5. Executioner — JOKER SKIN [hero hybrid] (joker) -----------------------
# The cell-1 Executioner SILHOUETTE re-skinned: plum-lacquer body, gold riveted
# guard, a LIME-glow groove in place of the red. Same _executioner_slab geometry
# call as cell 1 — only the colour pack changes. The AD's predicted winner.
def draw_v5(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.12)
    ghw = _guard_hw(ss)
    _executioner_slab(surf, cx, tip_y, base_y, hw, ss, PLUM_BODY_DK, PLUM_BODY,
                       PLUM_DK, PLUM_LAC, groove=LIME, groove_glow=LIME)
    # GOLD riveted guard (gold as METAL, not bling) — mirrors cell-1 iron guard.
    pygame.draw.rect(surf, GOLD_DK, (int(cx - ghw), int(gy - 8 * ss),
                                     int(ghw * 2), int(16 * ss)))
    pygame.draw.rect(surf, GOLD, (int(cx - ghw), int(gy - 8 * ss),
                                  int(ghw * 2), int(6 * ss)))
    pygame.draw.rect(surf, PLUM_DK, (int(cx - ghw), int(gy - 8 * ss),
                                     int(ghw * 2), int(16 * ss)), max(1, int(ss)))
    _rivet(surf, cx - ghw + int(8 * ss), gy, int(5 * ss), GOLD)
    _rivet(surf, cx + ghw - int(8 * ss), gy, int(5 * ss), GOLD)
    _wrap_grip(surf, cx, gy + int(9 * ss), gbot, int(hw * 0.40), PLUM_DK, ss)
    # Squared gold pommel with a single lime jewel (one accent).
    pr = int(hw * 0.40)
    pygame.draw.rect(surf, GOLD_DK, (int(cx - pr), int(py - pr), int(pr * 2), int(pr * 2)))
    pygame.draw.rect(surf, GOLD, (int(cx - pr), int(py - pr), int(pr * 2), int(pr * 0.6)))
    pygame.draw.rect(surf, PLUM_DK, (int(cx - pr), int(py - pr),
                                     int(pr * 2), int(pr * 2)), max(1, int(ss)))
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(pr * 0.42)))


# ---- 6. Harlequin Greatsword (joker) -----------------------------------------
# The broad greatsword shape (cell-3 _hard_taper geometry) skinned with ONE bold
# plum/lime split down the fuller (NOT a fine grid) + 3 LARGE diamonds, gold
# quillons. Plum darkened ~15% for day-sky contrast.
def draw_v6(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.22)
    ghw = _guard_hw(ss)
    _hard_taper_blade(surf, cx, tip_y, base_y, hw, ss,
                      PLUM_BODY_DK, PLUM_BODY, _shade_c(PLUM, 6), PLUM_LAC, PLUM_DK,
                      taper=0.06, groove=None)
    # ONE bold split down the fuller: left half plum, right half a lime line —
    # the harlequin read at scale without a fine grid.
    pygame.draw.line(surf, LIME, (cx, base_y - int(6 * ss)),
                     (cx, tip_y + int(16 * ss)), max(2, int(3 * ss)))
    _edge_glow(surf, [(cx, base_y - int(6 * ss)), (cx, tip_y + int(16 * ss))],
               LIME, ss, alpha=110, spread=3)
    # THREE large alternating diamonds straddling the fuller (big, bold).
    for i, dc in enumerate((LIME, PLUM_LAC, LIME)):
        t = 0.36 + i * 0.18
        dy = tip_y + (base_y - tip_y) * t
        dw = hw * (1.0 - (dy - tip_y) / max(1, base_y - tip_y)) * 0.5
        pygame.draw.polygon(surf, dc,
                            [(cx, dy - dw), (cx + dw, dy),
                             (cx, dy + dw), (cx - dw, dy)])
        pygame.draw.polygon(surf, PLUM_DK,
                            [(cx, dy - dw), (cx + dw, dy),
                             (cx, dy + dw), (cx - dw, dy)], max(1, int(ss)))
    # Gold quillons (downturned) + square boss to echo the steel greatsword.
    _crossguard(surf, cx, gy, ghw, int(13 * ss), GOLD, ss, curve=int(6 * ss),
                dk=GOLD_DK)
    pygame.draw.rect(surf, GOLD,
                     (int(cx - 9 * ss), int(gy - 9 * ss), int(18 * ss), int(18 * ss)))
    pygame.draw.rect(surf, PLUM_DK,
                     (int(cx - 9 * ss), int(gy - 9 * ss), int(18 * ss), int(18 * ss)),
                     max(1, int(ss)))
    pygame.draw.circle(surf, LIME, (cx, gy), max(2, int(4 * ss)))
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.34), PLUM_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.42), GOLD, ss, dk=GOLD_DK)
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(hw * 0.18)))


# ---- 7. Warblade — JOKER SKIN (joker) ----------------------------------------
# The serrated shape (cell-2 _serrated_blade geometry) in gunmetal-plum with a
# lime-glow edge + gold-tipped teeth. Same builder call as cell 2; colour swap.
def draw_v7(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    _serrated_blade(surf, cx, tip_y, base_y, hw, ss, GUNPLUM_LO, GUNPLUM_HI,
                    _shade_c(GUNPLUM_HI, 24), CREAM, PLUM_DK, teeth=5,
                    tooth_col=GOLD, groove=LIME, groove_glow=LIME)
    # Lime-glow edge slivers (the accent) on the clean upper third.
    clean_top = tip_y + (base_y - tip_y) * 0.34
    _edge_glow(surf, [(cx, tip_y + int(3 * ss)), (cx - hw * 0.66, clean_top)],
               LIME, ss, alpha=120, spread=3)
    _edge_glow(surf, [(cx, tip_y + int(3 * ss)), (cx + hw * 0.66, clean_top)],
               LIME, ss, alpha=120, spread=3)
    # Gold guard + plum grip + gold pommel.
    _crossguard(surf, cx, gy, ghw, int(11 * ss), GOLD, ss, dk=GOLD_DK)
    _wrap_grip(surf, cx, gy + int(10 * ss), gbot, int(hw * 0.42), PLUM_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.46), GOLD, ss, dk=GOLD_DK)
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(hw * 0.18)))


# ---- 8. Fool's Cleaver (joker) -----------------------------------------------
# Heavy chopper; belly THINNED ~15% so two facing cleavers don't choke the gap;
# tip sharpened to a HARD point. Gold saw-spine (few big teeth), plum body, lime
# crescent mark.
def draw_v8(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)     # thinned vs round-1 (was 1.25)
    ghw = _guard_hw(ss)
    # Cleaver slab: a slight belly on the cutting (left) side that pulls IN to a
    # hard point at the tip — straight enough that the apex is a clean break.
    edge_l = [(cx - hw, base_y),
              (cx - hw * 0.96, base_y - int(bh * 0.30)),
              (cx - hw * 0.34, tip_y + int(10 * ss)),
              (cx, tip_y)]
    back_r = [(cx, tip_y), (cx + hw * 0.62, tip_y + int(14 * ss)),
              (cx + hw, base_y)]
    body = edge_l + back_r
    _vgrad_poly(surf, body, PLUM_BODY, PLUM_BODY_DK, outline=PLUM_DK, ow=max(2, int(1.6 * ss)))
    # Plum lacquer sheen — one bold stripe down the body.
    pygame.draw.line(surf, PLUM_LAC, (cx - hw * 0.2, base_y - int(8 * ss)),
                     (cx - hw * 0.05, tip_y + int(20 * ss)), max(2, int(3 * ss)))
    # Gold saw-spine: a FEW big teeth on the back (right) edge only.
    bx = cx + hw
    n_teeth = 4
    for i in range(n_teeth):
        t0 = 0.12 + i * 0.20
        y0 = base_y + (tip_y - base_y) * t0
        sx = cx + hw * (1.0 - (y0 - tip_y) / max(1, base_y - tip_y)) * 0.62 + hw * 0.38
        pygame.draw.polygon(surf, GOLD,
                            [(sx, y0), (sx + int(9 * ss), y0 - int(6 * ss)),
                             (sx, y0 - int(13 * ss))])
        pygame.draw.polygon(surf, GOLD_DK,
                            [(sx, y0), (sx + int(9 * ss), y0 - int(6 * ss)),
                             (sx, y0 - int(13 * ss))], max(1, int(ss)))
    # Lime crescent maker's-mark (one accent), away from the tip.
    pygame.draw.arc(surf, LIME, (int(cx - hw * 0.45), int(base_y - bh * 0.34),
                                 int(hw * 0.9), int(hw * 0.9)),
                    math.pi * 0.25, math.pi * 1.15, max(2, int(3 * ss)))
    # Bright chopping edge on the front (left) side, into a hard apex.
    pygame.draw.lines(surf, CREAM, False,
                      [(cx - hw, base_y), (cx - hw * 0.96, base_y - int(bh * 0.30)),
                       (cx - hw * 0.34, tip_y + int(10 * ss)), (cx, tip_y + int(3 * ss))],
                      max(2, int(2.0 * ss)))
    _crossguard(surf, cx, gy, int(ghw * 0.9), int(12 * ss), GOLD, ss, dk=GOLD_DK)
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.40), PLUM_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.42), GOLD, ss, dk=GOLD_DK)
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(hw * 0.16)))


# ---- 9. Jester Saber (joker) -------------------------------------------------
# STRAIGHTENED noticeably (executioner's curve, not a sabre arc) for a clean gap;
# the bell pommel + grin-guard SHRUNK so it reads MEAN not cute. Plum blade,
# lime fuller, gold metal.
def draw_v9(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    # Very slight one-sided lean (executioner's curve): the spine drifts only a
    # touch so the central axis stays near-vertical and the apex is a hard point.
    lean = hw * 0.45
    spine, edge_l = [], []
    n = 14
    for i in range(n + 1):
        t = i / n                       # 0 base, 1 tip
        y = base_y + (tip_y - base_y) * t
        sweep = (t ** 1.6) * lean
        wdt = hw * (1.0 - t)
        spine.append((cx + sweep + wdt * 0.10, y))
        edge_l.append((cx + sweep - wdt, y))
    body = spine + list(reversed(edge_l))
    _vgrad_poly(surf, body, PLUM_BODY, PLUM_BODY_DK, outline=PLUM_DK, ow=max(2, int(1.6 * ss)))
    # Lime fuller following the gentle lean — ONE bold glow line.
    fuller = [((p[0] + spine[i][0]) * 0.5, p[1]) for i, p in enumerate(edge_l)]
    _edge_glow(surf, fuller, LIME, ss, alpha=130, spread=4)
    pygame.draw.lines(surf, LIME, False, fuller, max(2, int(2.4 * ss)))
    # Bright cutting edge, stopping shy of the apex for a clean dark->sky break.
    pygame.draw.lines(surf, CREAM, False, edge_l[1:], max(1, int(1.8 * ss)))
    # SMALL gold guard (shrunk grin) — a plain narrow bar, no curl, no teeth.
    _crossguard(surf, cx, gy, int(ghw * 0.78), int(9 * ss), GOLD, ss, dk=GOLD_DK)
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.42), PLUM_DK, ss)
    # SMALL gold pommel with a lime jewel — no oversized bell.
    _pommel(surf, cx, py, int(hw * 0.40), GOLD, ss, dk=GOLD_DK)
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(hw * 0.16)))


# ---- 10. Ringmaster's Greatsword [WILDCARD] (joker) --------------------------
# Designer's pick: a gold/plum greatsword with imp-horn quillons + a lime-jewel
# pommel. Hard straight taper to a sharp apex (GATE 1), darkened plum body for
# day-sky contrast (GATE 2), only big bold elements (GATE 3).
def draw_v10(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.10)
    ghw = _guard_hw(ss)
    _hard_taper_blade(surf, cx, tip_y, base_y, hw, ss,
                      PLUM_BODY_DK, PLUM_BODY, _shade_c(PLUM, 4), PLUM_LAC, PLUM_DK,
                      taper=0.04, groove=GOLD, groove_w=3.0)
    # The gold groove gets a lime glow only at its lower third (a single accent
    # zone) so lime stays an accent, not a fill.
    _edge_glow(surf, [(cx, base_y - int(6 * ss)),
                      (cx, base_y - int((base_y - tip_y) * 0.42))],
               LIME, ss, alpha=110, spread=3)
    # Imp-horn quillons: two big gold horns curling UP toward the blade from a
    # gold bar — bold ringmaster silhouette.
    _crossguard(surf, cx, gy, int(ghw * 0.72), int(11 * ss), GOLD, ss, dk=GOLD_DK)
    for sgn in (-1, 1):
        horn = [(cx + sgn * int(ghw * 0.6), gy + int(2 * ss)),
                (cx + sgn * ghw, gy - int(6 * ss)),
                (cx + sgn * int(ghw * 0.9), gy - int(22 * ss))]
        pygame.draw.lines(surf, GOLD, False, horn, max(2, int(4 * ss)))
        pygame.draw.lines(surf, GOLD_DK, False, horn, max(1, int(1.6 * ss)))
    _wrap_grip(surf, cx, gy + int(9 * ss), gbot, int(hw * 0.36), PLUM_DK, ss)
    # Gold pommel set with a big lime jewel (the lime-jewel pommel).
    _pommel(surf, cx, py, int(hw * 0.46), GOLD, ss, dk=GOLD_DK)
    pygame.draw.circle(surf, _shade_c(LIME, -10), (cx, py), max(2, int(hw * 0.24)))
    pygame.draw.circle(surf, LIME, (cx, py), max(2, int(hw * 0.18)))
    pygame.draw.circle(surf, CREAM, (int(cx - hw * 0.06), int(py - hw * 0.06)),
                       max(1, int(hw * 0.07)))


# ── version registry ──────────────────────────────────────────────────────────
# (name, tag, draw_fn, gate-fix note). The TOP 3 (1, 5, 6) also get a night strip.
VERSIONS = [
    ("Obsidian Executioner", "steel", draw_v1,
     "HERO BASELINE: hard chamfered tip + thin restrained blood groove"),
    ("Serrated Warblade", "steel", draw_v2,
     "5 chunky teeth (de-noised), clean tip, rust on lower blade only"),
    ("Headsman's Greatsword", "steel", draw_v3,
     "NEW: broad dark steel, hard straight taper, heavy cross"),
    ("Crystal Glaive", "steel", draw_v4,
     "SALVAGE: opaque dark-blue core + hard cold-white rim (GATE 2)"),
    ("Executioner — JOKER SKIN", "joker", draw_v5,
     "HERO HYBRID: cell-1 silhouette + plum lacquer / gold guard / LIME groove"),
    ("Harlequin Greatsword", "joker", draw_v6,
     "cell-3 shape + ONE plum/lime fuller split + 3 big diamonds"),
    ("Warblade — JOKER SKIN", "joker", draw_v7,
     "cell-2 shape + gunmetal-plum + lime-glow edge + gold-tip teeth"),
    ("Fool's Cleaver", "joker", draw_v8,
     "belly thinned ~15%, hard tip, gold saw-spine, lime crescent"),
    ("Jester Saber", "joker", draw_v9,
     "STRAIGHTENED to executioner-curve, shrunk grin/bell -> reads MEAN"),
    ("Ringmaster's Greatsword", "joker", draw_v10,
     "WILDCARD: hard-taper gold/plum, imp-horn quillons, lime-jewel pommel"),
]
TOP3 = {0, 4, 5}               # cells 1, 5, 6 get an extra NIGHT route strip


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


def _blit_pair(dest, draw_fn, col_cx, gap_y, ss, *, ground_y=GROUND_Y):
    """Place a twin-blade PAIR on `dest` at column centre col_cx, gap centre
    gap_y. TOP obstacle: y=0..gap_y-HALF_GAP (point-down). BOTTOM obstacle:
    y=gap_y+HALF_GAP..ground_y (point-up)."""
    top_h = max(1, gap_y - HALF_GAP)
    bot_h = max(1, ground_y - (gap_y + HALF_GAP))
    x_left = int(col_cx - (PIPE_W + 2 * OVERHANG) / 2)
    top = _render_obstacle(draw_fn, top_h, ss, flip=True)
    dest.blit(top, (x_left, 0))                       # tip now points DOWN to gap
    bot = _render_obstacle(draw_fn, bot_h, ss, flip=False)
    dest.blit(bot, (x_left, gap_y + HALF_GAP))        # tip points UP to gap


def _sky(w, h, top, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        s.fill(lerp_color(top, bot, i / max(1, h - 1)), (0, i, w, 1))
    return s


def _ground(surf, w, *, night=False):
    col = (28, 60, 30) if night else (84, 132, 58)
    line = (16, 40, 20) if night else (60, 100, 40)
    pygame.draw.rect(surf, col, (0, GROUND_Y, w, surf.get_height() - GROUND_Y))
    pygame.draw.line(surf, line, (0, GROUND_Y), (w, GROUND_Y), 2)


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

def _route_panel(draw_fn, w, h, ss, *, night):
    """One route panorama: 11 pairs on a crest curve, day or night sky."""
    top, bot = (NIGHT_TOP, NIGHT_BOT) if night else (SKY_TOP, SKY_BOT)
    route = _sky(w, h, top, bot)
    _ground(route, w, night=night)
    n_steps = 11
    for step in range(n_steps):
        cx = 20 + SP // 2 + step * SP
        gy = _crest_gap_y(step, n_steps)
        _blit_pair(route, draw_fn, cx, gy, ss)
    pygame.draw.rect(route, (10, 12, 18), route.get_rect(), 2)
    return route


def main():
    SS = 4

    HERO_W = PIPE_W + 2 * OVERHANG + 24
    HERO_H = PLAY_H

    N_STEPS = 11
    ROUTE_W = SP * N_STEPS + 40
    NIGHT_W = ROUTE_W            # night strip uses the same crest layout
    ROUTE_H = PLAY_H

    pad = 18
    head = 92
    row_gap = 14
    name_strip = 30
    inner_gap = 22

    # A row holds the hero, the day route, and — for the top 3 — a night route.
    base_row_w = HERO_W + inner_gap + ROUTE_W
    top3_row_w = base_row_w + inner_gap + NIGHT_W
    row_w = top3_row_w          # sheet is sized to the widest row
    row_h = name_strip + max(HERO_H, ROUTE_H)

    sheet_w = pad * 2 + row_w
    sheet_h = head + len(VERSIONS) * (row_h + row_gap) + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Warren Sword Route — Round 2", True, (255, 255, 255)), (pad, 14))
    sheet.blit(sub_f.render(
        "GATES on ALL 10: (1) sky-gap = brightest/sharpest band — hard tips, dark body->bright gap; "
        "(2) blade body clears day-sky blue by >20%; (3) de-noised, 2-3 big bold elements only.",
        True, (205, 210, 220)), (pad, 48))
    sheet.blit(sub_f.render(
        "LEFT = 1:1 hero pair (true scale).  MID = day-sky route (11 pairs, SP=72 crest).  "
        "TOP 3 (1,5,6) add a NIGHT route strip.  Joker = plum body / lime accent / gold metal.",
        True, (170, 178, 190)), (pad, 68))

    name_f = hud._font(20, True)
    tag_f = hud._font(14, True)
    fix_f = hud._font(13, False)

    for idx, (name, palette_tag, draw_fn, fix) in enumerate(VERSIONS):
        ry = head + idx * (row_h + row_gap)
        is_top3 = idx in TOP3
        strip_w = top3_row_w if is_top3 else base_row_w
        # Name strip with name + (tag) + gate-fix note.
        strip = pygame.Surface((strip_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        tag_col = LIME if palette_tag == "joker" else (150, 200, 240)
        ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
        strip.blit(ntxt, (8, 4))
        tagtxt = tag_f.render(f"({palette_tag})", True, tag_col)
        strip.blit(tagtxt, (12 + ntxt.get_width(), 9))
        strip.blit(fix_f.render(fix, True, (188, 194, 206)),
                   (20 + ntxt.get_width() + tagtxt.get_width(), 10))
        sheet.blit(strip, (pad, ry))

        body_y = ry + name_strip

        # --- hero close-up ---
        hero = _sky(HERO_W, HERO_H, SKY_TOP, SKY_BOT)
        _ground(hero, HERO_W)
        _blit_pair(hero, draw_fn, HERO_W // 2, 300, SS)
        pygame.draw.line(hero, (255, 255, 255), (0, 300 - HALF_GAP),
                         (HERO_W, 300 - HALF_GAP), 1)
        pygame.draw.line(hero, (255, 255, 255), (0, 300 + HALF_GAP),
                         (HERO_W, 300 + HALF_GAP), 1)
        pygame.draw.rect(hero, (10, 12, 18), hero.get_rect(), 2)
        sheet.blit(hero, (pad, body_y))

        # --- day route ---
        day = _route_panel(draw_fn, ROUTE_W, ROUTE_H, SS, night=False)
        sheet.blit(day, (pad + HERO_W + inner_gap, body_y))

        # --- night route (top 3 only) ---
        if is_top3:
            night = _route_panel(draw_fn, NIGHT_W, ROUTE_H, SS, night=True)
            sheet.blit(night, (pad + HERO_W + inner_gap + ROUTE_W + inner_gap, body_y))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_sword")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_2.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
