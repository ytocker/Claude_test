"""Look-dev renderer (Round 4): the WARREN EVENT sword — final polish.

Round 3's concept-direction set LANDED; the art-director crowned a lead set
and called for tightening, not rebuilding. Round 4 carries forward the 6 crown
picks + 6 strong keepers (each with a targeted FIX) and REPLACES the 3 that
washed out / died small (Grin, Frost, Winged Crown) with 3 new DARK-FILL
concepts (Molten / Tribal Totem / Wraith), all body luma well under ~120 so
they hold hard on day-sky blue. 15 rows, grouped by direction.

Round-3 lineage notes (kept for context): Rounds 1-2 were 20 literal
metal-weapon archetypes and NONE landed. Round 3 abandoned that "which
historical blade" axis and explored swords as CONCEPTS across four directions:

  A) FANTASTICAL / ELEMENTAL — the blade IS energy: flame, frost, lightning,
     void-rune. Each gets an OPAQUE DARK CORE (never a translucent wash) so
     the silhouette holds on day-sky blue.
  B) CHARACTERFUL / LIVING — the sword has a face/personality: a grin worked
     into the steel, a single watching eye, a fanged maw-guard with the blade
     as a tongue, a scaled serpent-body blade.
  C) LEGENDARY / ORNATE — jeweled boss-loot: a gem-core greatblade, a winged
     crown-pommel relic, BOLD gold filigree, a cut-prism crystal blade.
  D) STYLIZED / ICONIC — emoji-clean graphic shapes, max readability: a flat
     2-tone icon, a chunky faceted poly, a neon-outline blade.

The same THREE gameplay GATES from round 2 still drive EVERY version (these
are gameplay, not taste — all 15 must pass):
  1. GAP READABILITY — the sky-gap between the two facing blade TIPS is the
     brightest, sharpest horizontal band in the column. Every taper ends in a
     HARD point with a strong DARK-body -> BRIGHT-gap value break. No curved
     or bulbous tips that blur the gap.
  2. DAY-SKY CONTRAST — the blade BODY luminance sits well clear of the day
     sky (~173 luma); aim ~80% darker. Every glow / ice / gem gets an OPAQUE
     DARK CORE so the silhouette never washes out on blue.
  3. DE-NOISE AT SCALE — in motion a blade is ~30-40 px wide: at most 2-3 BOLD
     elements per blade. No fine grids / combs / dense filigree that fizz.

The Warren event rolls a die for N, then spawns a TIGHT route of N pillars the
player threads. We are replacing the route's repeated pillar with a SWORD: ONE
blade design reused for every pillar of the event, and it must read amazing /
appealing — the marquee event in the game.

A "pillar" is a TOP obstacle + a BOTTOM obstacle with a flyable gap between:
    TOP    obstacle = a sword hanging point-DOWN from the ceiling.
    BOTTOM obstacle = a sword standing point-UP from the ground.
The flyable GAP sits between the two blade tips — twin blades aimed at the
player from both sides; the pair is always ONE design mirrored about the gap.

True game footprint honoured exactly:
    Playfield 360 x 640, GROUND_Y = 595, column width PIPE_W = 58.
    Route gap height = 172, centred at each step's gap_y. So:
        top blade fills    y = 0          .. gap_y - 86
        bottom blade fills y = gap_y + 86 .. 595
    Route spacing SP = 72 centre-to-centre (only ~14 px of air between
    58-px columns) — a deliberate RACK / WALL of blades.

The figure: 15 rows, one per version.
    LEFT  = a 1:1 hero close-up of ONE top+bottom twin-blade PAIR at true
            scale (so blade detail + the gap read), labelled name + DIRECTION
            + TONE.
    MID   = the version's day-sky ROUTE panorama — 11 twin-blade pairs at true
            vertical scale (640 tall, gap 172) at true SP=72 spacing.
    RIGHT = for ~3 of the strongest picks a NIGHT-sky route strip is appended
            so the emissive cores read in both biomes.

All art is procedural; supersampled (SS) then smoothscaled down for crisp
edges. The box / layout / compositing / panorama scaffolding is carried over
from round 2 unchanged — only the 15 draw functions are new.

Run (headless):
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=. \
        python tools/render_warren_sword.py
Writes docs/warren_sword/round_4.png.
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

# ── true game footprint ──────────────────────────────────────────────────────
PIPE_W = 58
GROUND_Y = 595
PLAY_W = 360
PLAY_H = 640
GAP_H = 172
HALF_GAP = GAP_H // 2          # 86
SP = 72                        # route centre-to-centre spacing

# Day sky for contrast — a simple top→bottom blue, per the brief (~173 luma).
SKY_TOP = (96, 165, 230)
SKY_BOT = (175, 215, 245)
# Night sky for the strongest-pick second-biome check.
NIGHT_TOP = (5, 8, 30)
NIGHT_BOT = (35, 55, 115)

# Neutral dark hilt metals shared across directions (always hold value on blue).
IRON_DK = (40, 44, 52)
IRON_MD = (78, 84, 96)
LEATHER = (74, 52, 38)
LEATHER_DK = (48, 34, 26)
GOLD = (228, 182, 70)
GOLD_HI = (255, 232, 150)
GOLD_DK = (150, 108, 32)
GOLD_SHADOW = (92, 64, 22)
CREAM = (245, 236, 210)


# ── small helpers (carried from round 2) ─────────────────────────────────────

def _vgrad_poly(surf, pts, top_col, bot_col, *, outline=None, ow=2):
    """Fill a polygon with a vertical gradient via an alpha-masked gradient band,
    so a blade body reads as a lit volume rather than a flat fill."""
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
    """A soft emissive glow hugging a polyline; ADD-blended so the edge reads as
    lit on both day and night sky without a full glow-cache disc."""
    for k in range(spread, 0, -1):
        a = int(alpha * (k / spread) * 0.5)
        wln = max(1, int(k * 1.6 * ss))
        layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        if len(pts) >= 2:
            pygame.draw.lines(layer, col + (a,), False, pts, wln)
        surf.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)


def _glow_disc(surf, cx, cy, r, col, ss, *, alpha=150, falloff=1.8):
    """A radial ADD glow disc (for a gem / eye / pommel jewel highlight)."""
    rr = max(1, int(r))
    g = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
    for ri in range(rr, 0, -1):
        t = (ri / rr) ** falloff
        a = int(alpha * (1 - t))
        pygame.draw.circle(g, col + (max(0, a),), (rr + 1, rr + 1), ri)
    surf.blit(g, (int(cx) - rr - 1, int(cy) - rr - 1), special_flags=pygame.BLEND_ADD)


def _rivet(surf, x, y, r, col):
    pygame.draw.circle(surf, _shade_c(col, -40), (int(x), int(y)), int(r))
    pygame.draw.circle(surf, _shade_c(col, 50), (int(x - r * 0.3), int(y - r * 0.3)),
                       max(1, int(r * 0.45)))


def _wrap_grip(surf, cx, top, bot, hw, base_col, ss):
    """A wrapped grip column drawn as bold two-tone bands (no fine cross-hatch),
    so the grip reads as a clean dark column under the blade."""
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


# ── the sword frame (carried from round 2) ───────────────────────────────────
OVERHANG = 12                  # guards may spill this far past the 58-px column
HILT_PX = 132                  # nominal hilt height, true px
MIN_BLADE_PX = 40
BLOOD = (170, 28, 34)


def _box(H, ss):
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(H)) * ss
    return pygame.Surface((bw, bh), pygame.SRCALPHA), bw, bh


def _layout(bh, ss):
    """Key y-coords (SS space) for a point-UP sword in a box of SS height bh:
    tip at top (y=0), pommel at the bottom."""
    hilt = HILT_PX * ss
    if hilt > bh - MIN_BLADE_PX * ss:
        hilt = max(0, bh - MIN_BLADE_PX * ss)
    tip_y = int(0)
    guard_y = int(bh - hilt + 0.30 * hilt)
    blade_base_y = guard_y
    grip_top_y = guard_y
    pommel_y = int(bh - max(6 * ss, hilt * 0.10))
    grip_bot_y = int(pommel_y - 4 * ss)
    return tip_y, blade_base_y, guard_y, grip_top_y, grip_bot_y, pommel_y


def _blade_hw(ss):
    return int((PIPE_W * 0.5 - 6) * ss)


def _guard_hw(ss):
    return int((PIPE_W * 0.5 + OVERHANG - 2) * ss)


def _crossguard(surf, cx, gy, ghw, thick, col, ss, *, curve=0.0, dk=None):
    """A horizontal crossguard centred at (cx, gy) spanning +-ghw, `thick` tall."""
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


def _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, *, metal=GOLD,
                metal_dk=GOLD_DK, grip=LEATHER_DK, jewel=None, curve=0.0,
                gthick=11):
    """A shared, restrained hilt: one bold crossguard, a wrapped grip, a round
    pommel (optionally jewelled). Keeps every version's grip-furniture from
    re-inventing the wheel so the blade body is where the character lives."""
    _crossguard(surf, cx, gy, ghw, int(gthick * ss), metal, ss, curve=curve,
                dk=metal_dk)
    _wrap_grip(surf, cx, gy + int(9 * ss), gbot, int(hw * 0.40), grip, ss)
    _pommel(surf, cx, py, int(hw * 0.46), metal, ss, dk=metal_dk)
    if jewel is not None:
        pygame.draw.circle(surf, jewel, (cx, py), max(2, int(hw * 0.18)))


def _straight_body(cx, tip_y, base_y, hw, *, taper=0.0):
    """The canonical hard-taper double-edged silhouette polygon (apex == box top
    so the dark body meets bright sky as a single razor break — GATE 1)."""
    bw = hw * (1.0 + taper)
    return [(cx - bw, base_y), (cx, tip_y), (cx + bw, base_y)], bw


# ════════════════════════════════════════════════════════════════════════════
#  DIRECTION A — FANTASTICAL / ELEMENTAL
#  The blade IS energy. Each carries an OPAQUE DARK CORE so the silhouette holds
#  on day blue (GATE 2); the elemental colour lives on the EDGES / a centre vein.
# ════════════════════════════════════════════════════════════════════════════

# ---- 1. Flame Blade — DIRECTION A / MEAN ------------------------------------
# A near-black molten blade: a charcoal core, a glowing ember CRACK up the
# centre, and fire licking only the EDGES (a few big tongues, not a wash). The
# tip is a hard point so the gap stays a clean dark->sky break.
EMBER_CORE = (28, 16, 12)      # opaque charred core
EMBER_MD = (60, 28, 18)
EMBER_HOT = (255, 150, 36)
EMBER_WHITE = (255, 232, 150)
FIRE_DK = (120, 36, 14)


def draw_v1(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.04)
    _vgrad_poly(surf, body, EMBER_MD, EMBER_CORE, outline=(14, 8, 6),
                ow=max(2, int(1.8 * ss)))
    # A glowing ember crack up the centre — ONE bold vein, hot core + glow.
    crack = [(cx, base_y - int(6 * ss)),
             (cx - int(4 * ss), base_y - int((base_y - tip_y) * 0.36)),
             (cx + int(3 * ss), base_y - int((base_y - tip_y) * 0.62)),
             (cx, tip_y + int(18 * ss))]
    _edge_glow(surf, crack, EMBER_HOT, ss, alpha=170, spread=5)
    pygame.draw.lines(surf, EMBER_WHITE, False, crack, max(2, int(2.0 * ss)))
    # Fire licking the EDGES: a few big flame tongues riding each cutting edge.
    for sgn in (-1, 1):
        n = 4
        for i in range(n):
            t = 0.16 + i * 0.20
            ey = base_y + (tip_y - base_y) * t
            ew = bwid * (1.0 - (ey - tip_y) / max(1, base_y - tip_y))
            ex = cx + sgn * ew
            lick = [(ex, ey + int(8 * ss)),
                    (ex + sgn * int(9 * ss), ey - int(2 * ss)),
                    (ex - int(1 * ss), ey - int(12 * ss))]
            _edge_glow(surf, lick, EMBER_HOT, ss, alpha=150, spread=4)
            pygame.draw.lines(surf, FIRE_DK, False, lick, max(1, int(1.6 * ss)))
    # Hot edge slivers into the apex, stopping just shy so the apex stays sharp.
    pygame.draw.line(surf, EMBER_HOT, (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, EMBER_HOT, (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=(64, 40, 28),
                metal_dk=(28, 16, 10), grip=(40, 22, 14),
                jewel=EMBER_HOT, curve=int(4 * ss))
    _glow_disc(surf, cx, py, int(hw * 0.3), EMBER_HOT, ss, alpha=130)


# ---- 2. Tribal Totem Blade — DIRECTION B / PLAYFUL-MEAN ---------------------
# REPLACES Frost (washed out on day sky). A dark carved-WOOD blade — a living
# character in the totem-mask key — carrying ONE bold painted glyph/mask mark
# in its lower third. One big graphic mark (NOT a face), so it survives small
# where Grin's face died. Body luma kept well under ~120 on the dark wood.
WOOD_LO = (40, 26, 18)         # deep carved-wood core
WOOD_MD = (74, 50, 32)
WOOD_HI = (108, 76, 48)
WOOD_KEY = (22, 13, 8)
PAINT_RED = (208, 60, 44)      # tribal ochre-red paint
PAINT_BONE = (232, 216, 176)   # bone-white paint
PAINT_TEAL = (60, 168, 150)


def draw_v2(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.08)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.03)
    _vgrad_poly(surf, body, WOOD_MD, WOOD_LO, outline=WOOD_KEY,
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    # Two long wood-grain gouges riding the body (the carved-plank read) — bold,
    # not a comb, so the wood reads without fizz.
    for sgn in (-1, 1):
        pygame.draw.line(surf, WOOD_KEY,
                         (cx + sgn * bwid * 0.42, base_y - int(6 * ss)),
                         (cx + sgn * int(2 * ss), tip_y + int(span * 0.30)),
                         max(1, int(1.6 * ss)))
        pygame.draw.line(surf, WOOD_HI,
                         (cx + sgn * bwid * 0.42, base_y - int(9 * ss)),
                         (cx + sgn * int(3 * ss), tip_y + int(span * 0.32)),
                         max(1, int(1.4 * ss)))
    # The ONE hero mark: a bold painted totem-MASK glyph in the lower third —
    # a chevron brow, two slit eyes, a fanged bar. One big graphic, reads small.
    my = base_y - int(span * 0.24)
    mw = bwid * (1.0 - (my - tip_y) / max(1, base_y - tip_y)) * 0.78
    pygame.draw.lines(surf, PAINT_RED, False,
                      [(cx - mw, my - int(11 * ss)), (cx, my - int(2 * ss)),
                       (cx + mw, my - int(11 * ss))], max(3, int(3.4 * ss)))
    for sgn in (-1, 1):
        pygame.draw.line(surf, PAINT_BONE,
                         (cx + sgn * mw * 0.52, my + int(1 * ss)),
                         (cx + sgn * mw * 0.18, my + int(1 * ss)), max(3, int(3.2 * ss)))
    # A small teal under-bar finishes the mask (the third paint colour, restrained).
    pygame.draw.line(surf, PAINT_TEAL, (cx - mw * 0.5, my + int(9 * ss)),
                     (cx + mw * 0.5, my + int(9 * ss)), max(2, int(2.6 * ss)))
    # Bone-painted cutting edges into a hard apex (keeps the gap break crisp).
    pygame.draw.line(surf, PAINT_BONE, (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, PAINT_BONE, (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=(96, 66, 40),
                metal_dk=WOOD_KEY, grip=(46, 30, 20), jewel=PAINT_RED,
                curve=int(4 * ss))


# ---- 3. Lightning Blade — DIRECTION A / COOL-EPIC ---------------------------
# Dark gunmetal blade with a jagged electric-yellow ARC blasting down the
# fuller — one bold zig-zag bolt + glow. Storm-grey body holds value on blue.
STORM_LO = (38, 42, 54)
STORM_MD = (74, 82, 100)
STORM_HI = (132, 144, 166)
BOLT = (255, 238, 88)
BOLT_HOT = (255, 252, 200)
BOLT_DK = (90, 96, 120)


def draw_v3(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.0)
    _vgrad_poly(surf, body, STORM_HI, STORM_LO, outline=(18, 20, 28),
                ow=max(2, int(1.8 * ss)))
    pygame.draw.polygon(surf, _shade_c(STORM_HI, 18),
                        [(cx - bwid * 0.26, base_y), (cx, tip_y),
                         (cx + bwid * 0.26, base_y)])
    # The bolt: a jagged zig-zag down the fuller (ONE bold element). Glow first,
    # then a hot white core so it reads as electric, not painted-on.
    span = base_y - tip_y
    bolt = [(cx, base_y - int(6 * ss)),
            (cx - int(7 * ss), base_y - int(span * 0.24)),
            (cx + int(8 * ss), base_y - int(span * 0.44)),
            (cx - int(6 * ss), base_y - int(span * 0.64)),
            (cx + int(4 * ss), base_y - int(span * 0.80)),
            (cx, tip_y + int(16 * ss))]
    _edge_glow(surf, bolt, BOLT, ss, alpha=180, spread=6)
    pygame.draw.lines(surf, BOLT, False, bolt, max(2, int(2.6 * ss)))
    pygame.draw.lines(surf, BOLT_HOT, False, bolt, max(1, int(1.2 * ss)))
    # Hard bright edges into the apex.
    pygame.draw.line(surf, STORM_HI, (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, STORM_HI, (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=STORM_MD,
                metal_dk=(20, 22, 30), grip=(34, 36, 46), jewel=BOLT)
    _glow_disc(surf, cx, py, int(hw * 0.28), BOLT, ss, alpha=120)


# ---- 4. Void Rune Blade — DIRECTION A / MEAN --------------------------------
# Near-black blade with TWO glowing purple rune sigils and a thin magenta energy
# edge. Bold runes (a chevron + a ring), nothing fine, so it survives scale.
VOID_CORE = (16, 12, 28)       # opaque near-black violet core
VOID_MD = (40, 28, 64)
VOID_HI = (78, 56, 116)
RUNE = (186, 96, 255)
RUNE_HOT = (236, 196, 255)
VOID_EDGE = (150, 70, 230)


def draw_v4(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.03)
    _vgrad_poly(surf, body, VOID_MD, VOID_CORE, outline=(8, 6, 14),
                ow=max(2, int(1.8 * ss)))
    pygame.draw.polygon(surf, _shade_c(VOID_HI, -6),
                        [(cx - bwid * 0.22, base_y), (cx, tip_y),
                         (cx + bwid * 0.22, base_y)])
    span = base_y - tip_y
    # Exactly ONE rune sigil, locked to the blade's UPPER THIRD (nearer the tip):
    # a glowing ring crossed by a bar. At route scale two stacked runes blobbed
    # into a mid-blade smear, so the design now carries a single hero sigil.
    ry2 = base_y - int(span * 0.66)
    rr = int(bwid * (1.0 - (ry2 - tip_y) / max(1, base_y - tip_y)) * 0.46)
    _glow_disc(surf, cx, ry2, rr + int(3 * ss), RUNE, ss, alpha=150)
    pygame.draw.circle(surf, RUNE_HOT, (cx, ry2), rr, max(2, int(2.0 * ss)))
    pygame.draw.line(surf, RUNE_HOT, (cx, ry2 - int(rr * 0.5)),
                     (cx, ry2 + int(rr * 0.5)), max(1, int(1.6 * ss)))
    # Thin magenta energy edge into the apex (the glowing cutting edge).
    _edge_glow(surf, [(cx - bwid, base_y), (cx, tip_y)], VOID_EDGE, ss,
               alpha=120, spread=3)
    _edge_glow(surf, [(cx + bwid, base_y), (cx, tip_y)], VOID_EDGE, ss,
               alpha=120, spread=3)
    pygame.draw.line(surf, RUNE_HOT, (cx - bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.4 * ss)))
    pygame.draw.line(surf, RUNE_HOT, (cx + bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.4 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=(46, 34, 64),
                metal_dk=(18, 12, 28), grip=(26, 18, 38), jewel=RUNE)
    _glow_disc(surf, cx, py, int(hw * 0.3), RUNE, ss, alpha=140)


# ════════════════════════════════════════════════════════════════════════════
#  DIRECTION B — CHARACTERFUL / LIVING
#  The sword has a personality. The face/feature is ONE bold graphic worked into
#  the blade; the silhouette stays a hard-pointed blade so the gap holds.
# ════════════════════════════════════════════════════════════════════════════

# ---- 5. Molten Obsidian Blade — DIRECTION A / MEAN --------------------------
# REPLACES Grin (face died at route scale). A near-BLACK obsidian blade split by
# ONE thin glowing lava crack up the centre — Void's mean energy in a WARM key.
# Reads DISTINCT from #1 Flame: Flame is full fire tongues on the edges; this is
# a single restrained molten seam on pure black. Body luma very low (GATE 2).
OBS_CORE = (14, 11, 12)        # opaque obsidian black
OBS_MD = (30, 24, 26)
OBS_HI = (58, 48, 52)          # cool stony sheen, still far under sky luma
LAVA = (255, 122, 30)
LAVA_HOT = (255, 226, 150)
LAVA_DK = (150, 44, 14)


def draw_v5(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.03)
    _vgrad_poly(surf, body, OBS_MD, OBS_CORE, outline=(6, 5, 6),
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    # One cool stony glint plane catches the light so the black reads as polished
    # obsidian, not a flat void — a single facet, no fizz.
    pygame.draw.polygon(surf, OBS_HI,
                        [(cx - bwid * 0.36, base_y), (cx, tip_y),
                         (cx - bwid * 0.06, base_y)])
    # The ONE molten crack: a thin jagged glowing seam up the centre. Glow first,
    # then a hot white-orange core so it reads as live lava in the black.
    crack = [(cx, base_y - int(6 * ss)),
             (cx + int(3 * ss), base_y - int(span * 0.28)),
             (cx - int(3 * ss), base_y - int(span * 0.52)),
             (cx + int(2 * ss), base_y - int(span * 0.74)),
             (cx, tip_y + int(16 * ss))]
    _edge_glow(surf, crack, LAVA, ss, alpha=180, spread=6)
    pygame.draw.lines(surf, LAVA, False, crack, max(2, int(2.2 * ss)))
    pygame.draw.lines(surf, LAVA_HOT, False, crack, max(1, int(1.0 * ss)))
    # Two short branch cracks off the seam (small molten veins, kept minimal).
    for sgn, t0 in ((-1, 0.40), (1, 0.62)):
        by0 = base_y - int(span * t0)
        bx0 = cx + (3 if t0 < 0.5 else -3) * ss
        bend = [(bx0, by0), (cx + sgn * int(9 * ss), by0 - int(8 * ss))]
        _edge_glow(surf, bend, LAVA, ss, alpha=130, spread=3)
        pygame.draw.lines(surf, LAVA, False, bend, max(1, int(1.4 * ss)))
    # Faint warm glow just inside the cutting edges (the blade radiating heat),
    # stopping shy of the apex so the dark->gap break stays razor-hard.
    pygame.draw.line(surf, LAVA_DK, (cx - bwid, base_y),
                     (cx, tip_y + int(10 * ss)), max(1, int(1.4 * ss)))
    pygame.draw.line(surf, LAVA_DK, (cx + bwid, base_y),
                     (cx, tip_y + int(10 * ss)), max(1, int(1.4 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=(40, 30, 28),
                metal_dk=(16, 12, 12), grip=(28, 20, 18), jewel=LAVA,
                curve=int(4 * ss))
    _glow_disc(surf, cx, py, int(hw * 0.3), LAVA, ss, alpha=130)


# ---- 6. Eye Blade — DIRECTION B / PLAYFUL-MEAN ------------------------------
# A single watching eye set in a dark steel blade: a big iris that follows the
# player, heavy lash spikes, a few blood veins. Clean dark blade so the silhou-
# ette and tip hold.
EYE_BODY = (44, 50, 64)
EYE_BODY_HI = (96, 104, 124)
EYE_WHITE = (236, 230, 220)
EYE_IRIS = (60, 170, 220)
EYE_IRIS_DK = (24, 80, 130)
EYE_PUPIL = (16, 14, 22)
EYE_VEIN = (200, 70, 70)


def draw_v6(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.08)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.02)
    _vgrad_poly(surf, body, EYE_BODY_HI, EYE_BODY, outline=(16, 18, 26),
                ow=max(2, int(1.8 * ss)))
    pygame.draw.polygon(surf, _shade_c(EYE_BODY_HI, 16),
                        [(cx - bwid * 0.20, base_y), (cx, tip_y),
                         (cx + bwid * 0.20, base_y)])
    span = base_y - tip_y
    # The eye sits in the lower-mid blade. A pointed-oval sclera (almond eye).
    ey = base_y - int(span * 0.28)
    ew = bwid * (1.0 - (ey - tip_y) / max(1, base_y - tip_y)) * 0.92
    eh = ew * 0.62
    sclera = [(cx - ew, ey), (cx, ey - eh), (cx + ew, ey), (cx, ey + eh)]
    pygame.draw.polygon(surf, EYE_WHITE, sclera)
    pygame.draw.polygon(surf, (16, 18, 26), sclera, max(1, int(1.4 * ss)))
    # A few blood veins reaching in from the corners.
    for sgn in (-1, 1):
        pygame.draw.line(surf, EYE_VEIN, (cx + sgn * ew, ey),
                         (cx + sgn * ew * 0.4, ey - eh * 0.4), max(1, int(1.2 * ss)))
        pygame.draw.line(surf, EYE_VEIN, (cx + sgn * ew, ey),
                         (cx + sgn * ew * 0.5, ey + eh * 0.5), max(1, int(1.2 * ss)))
    # The iris + pupil with a glow so the eye reads as alive.
    ir = int(eh * 0.86)
    _glow_disc(surf, cx, ey, ir + int(2 * ss), EYE_IRIS, ss, alpha=110)
    pygame.draw.circle(surf, EYE_IRIS_DK, (cx, ey), ir)
    pygame.draw.circle(surf, EYE_IRIS, (cx, ey), int(ir * 0.78))
    pygame.draw.circle(surf, EYE_PUPIL, (cx, ey), int(ir * 0.42))
    pygame.draw.circle(surf, EYE_WHITE, (int(cx - ir * 0.3), int(ey - ir * 0.3)),
                       max(1, int(ir * 0.18)))
    # Lash spikes dropped — at 1x they read as fizz. The single cyan iris + the
    # corner blood-veins now carry the "watching eye" read on their own.
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=IRON_MD,
                metal_dk=IRON_DK, grip=(30, 30, 40), jewel=EYE_IRIS)


# ---- 7. Maw Blade — DIRECTION B / MEAN --------------------------------------
# A beast-mouth GUARD: a fanged jaw crossguard whose open maw the blade erupts
# from like a tongue/fang. The blade itself is a clean dark fang to a hard point;
# the character lives in the toothy guard.
MAW_HIDE = (62, 40, 50)
MAW_HIDE_DK = (34, 20, 28)
FANG = (236, 224, 196)
FANG_DK = (150, 120, 80)
TONGUE_LO = (60, 30, 36)
TONGUE_HI = (150, 60, 70)


def draw_v7(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 0.94)
    ghw = _guard_hw(ss)
    # The blade as a fang/tongue: a deep-red tongue core with a bony fang ridge.
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.0)
    # Thicken the dark-maroon spine ~30% (darker key, heavier outline) so the
    # cream fang ridge sits on a bolder dark body and the cream tip-half does
    # not soften into the bright gap band.
    _vgrad_poly(surf, body, _shade_c(TONGUE_HI, -22), _shade_c(TONGUE_LO, -14),
                outline=(16, 8, 12), ow=max(2, int(2.4 * ss)))
    # A bony fang ridge down the centre — NARROWED ~30% so more dark spine reads.
    pygame.draw.polygon(surf, FANG,
                        [(cx - bwid * 0.14, base_y), (cx, tip_y),
                         (cx + bwid * 0.14, base_y)])
    pygame.draw.line(surf, FANG, (cx - bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.6 * ss)))
    pygame.draw.line(surf, FANG, (cx + bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.6 * ss)))
    # The beast-maw guard: a wide hide-coloured jaw block the blade rises out of.
    jaw_y = gy
    jw = ghw
    jh = int(20 * ss)
    pygame.draw.polygon(surf, MAW_HIDE,
                        [(cx - jw, jaw_y + jh * 0.4),
                         (cx - jw * 0.6, jaw_y - jh * 0.7),
                         (cx + jw * 0.6, jaw_y - jh * 0.7),
                         (cx + jw, jaw_y + jh * 0.4),
                         (cx + jw * 0.7, jaw_y + jh),
                         (cx - jw * 0.7, jaw_y + jh)])
    pygame.draw.polygon(surf, MAW_HIDE_DK,
                        [(cx - jw, jaw_y + jh * 0.4),
                         (cx - jw * 0.6, jaw_y - jh * 0.7),
                         (cx + jw * 0.6, jaw_y - jh * 0.7),
                         (cx + jw, jaw_y + jh * 0.4),
                         (cx + jw * 0.7, jaw_y + jh),
                         (cx - jw * 0.7, jaw_y + jh)], max(1, int(1.6 * ss)))
    # A dark gullet behind the blade root.
    pygame.draw.ellipse(surf, (20, 8, 12),
                        (int(cx - jw * 0.5), int(jaw_y - jh * 0.2),
                         int(jw), int(jh * 0.9)))
    # Big upper + lower fangs ringing the maw (a few bold triangles).
    nfang = 4
    for i in range(nfang):
        t = (i + 0.5) / nfang
        fxp = cx - jw * 0.7 + 1.4 * jw * t
        # upper fang points down toward the gap-side
        pygame.draw.polygon(surf, FANG,
                            [(fxp - int(5 * ss), jaw_y - jh * 0.5),
                             (fxp + int(5 * ss), jaw_y - jh * 0.5),
                             (fxp, jaw_y - jh * 0.5 + int(12 * ss))])
        # lower fang points up
        pygame.draw.polygon(surf, FANG,
                            [(fxp - int(5 * ss), jaw_y + jh * 0.6),
                             (fxp + int(5 * ss), jaw_y + jh * 0.6),
                             (fxp, jaw_y + jh * 0.6 - int(12 * ss))])
    # Two glaring eyes on the jaw block.
    for sgn in (-1, 1):
        pygame.draw.circle(surf, (240, 200, 60),
                           (int(cx + sgn * jw * 0.55), int(jaw_y - jh * 0.5)),
                           max(2, int(3.5 * ss)))
        pygame.draw.circle(surf, (20, 10, 8),
                           (int(cx + sgn * jw * 0.55), int(jaw_y - jh * 0.5)),
                           max(1, int(1.6 * ss)))
    _wrap_grip(surf, cx, jaw_y + jh, gbot, int(hw * 0.42), MAW_HIDE_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.46), MAW_HIDE, ss, dk=(20, 10, 14))
    pygame.draw.circle(surf, (240, 200, 60), (cx, py), max(2, int(hw * 0.16)))


# ---- 8. Serpent Blade — DIRECTION B / COOL ----------------------------------
# The blade is a living scaled snake: a green serpent body forming a straight
# blade, a row of big scale chevrons down the centre, a hooded snake-head guard.
SNAKE_LO = (24, 70, 48)
SNAKE_MD = (52, 134, 84)
SNAKE_HI = (120, 200, 130)
SNAKE_BELLY = (200, 224, 160)
SNAKE_DK = (14, 40, 28)
SNAKE_EYE = (240, 196, 40)


def draw_v8(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.0)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.02)
    _vgrad_poly(surf, body, SNAKE_MD, SNAKE_LO, outline=SNAKE_DK,
                ow=max(2, int(1.8 * ss)))
    span = base_y - tip_y
    # A pale belly ridge down the centre (one bold light wedge).
    pygame.draw.polygon(surf, SNAKE_BELLY,
                        [(cx - bwid * 0.16, base_y), (cx, tip_y),
                         (cx + bwid * 0.16, base_y)])
    # A row of big scale chevrons riding the body — cut from ~6 to 4 BOLD Vs,
    # wider-spaced, so the scales read as a few graphic marks instead of fizz.
    nsc = 4
    for i in range(nsc):
        t = 0.18 + i * 0.21
        sy = tip_y + span * t
        sw = bwid * (1.0 - (sy - tip_y) / max(1, base_y - tip_y)) * 0.7
        pygame.draw.lines(surf, SNAKE_DK, False,
                          [(cx - sw, sy - int(6 * ss)), (cx, sy + int(4 * ss)),
                           (cx + sw, sy - int(6 * ss))], max(2, int(2.0 * ss)))
        pygame.draw.lines(surf, SNAKE_HI, False,
                          [(cx - sw, sy - int(9 * ss)), (cx, sy + int(1 * ss)),
                           (cx + sw, sy - int(9 * ss))], max(1, int(1.4 * ss)))
    # Bright edges into a hard apex.
    pygame.draw.line(surf, SNAKE_HI, (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, SNAKE_HI, (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    # Hooded snake-head guard: a flared cobra hood spanning the crossguard, with
    # two eyes — the head is the guard.
    hood = [(cx - ghw, gy + int(2 * ss)),
            (cx - ghw * 0.7, gy - int(10 * ss)),
            (cx, gy - int(6 * ss)),
            (cx + ghw * 0.7, gy - int(10 * ss)),
            (cx + ghw, gy + int(2 * ss)),
            (cx + ghw * 0.55, gy + int(12 * ss)),
            (cx - ghw * 0.55, gy + int(12 * ss))]
    pygame.draw.polygon(surf, SNAKE_MD, hood)
    pygame.draw.polygon(surf, SNAKE_DK, hood, max(1, int(1.6 * ss)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, SNAKE_EYE,
                           (int(cx + sgn * ghw * 0.45), int(gy + int(2 * ss))),
                           max(2, int(3.5 * ss)))
        pygame.draw.circle(surf, SNAKE_DK,
                           (int(cx + sgn * ghw * 0.45), int(gy + int(2 * ss))),
                           max(1, int(1.4 * ss)))
    _wrap_grip(surf, cx, gy + int(13 * ss), gbot, int(hw * 0.40), SNAKE_DK, ss)
    _pommel(surf, cx, py, int(hw * 0.46), SNAKE_MD, ss, dk=SNAKE_DK)
    pygame.draw.circle(surf, SNAKE_EYE, (cx, py), max(2, int(hw * 0.16)))


# ════════════════════════════════════════════════════════════════════════════
#  DIRECTION C — LEGENDARY / ORNATE
#  Jeweled boss-loot relics. Gold furniture, faceted gems, BOLD scrollwork —
#  never fine fizz. The blade silhouette stays hard-pointed for the gap.
# ════════════════════════════════════════════════════════════════════════════

def _facet_gem(surf, cx, cy, r, col, hi, dk, ss):
    """A faceted oval gem: a dark setting ring, two big facet halves, a hot
    glint. Bold + readable at scale (no fine cut lines)."""
    pts = [(cx, cy - r), (cx + r * 0.85, cy - r * 0.4),
           (cx + r * 0.85, cy + r * 0.4), (cx, cy + r),
           (cx - r * 0.85, cy + r * 0.4), (cx - r * 0.85, cy - r * 0.4)]
    _glow_disc(surf, cx, cy, int(r * 1.2), col, ss, alpha=120)
    pygame.draw.polygon(surf, dk, pts)
    pygame.draw.polygon(surf, col,
                        [(cx, cy - r), (cx + r * 0.85, cy - r * 0.4),
                         (cx, cy + r * 0.2)])
    pygame.draw.polygon(surf, hi,
                        [(cx, cy - r), (cx - r * 0.85, cy - r * 0.4),
                         (cx, cy + r * 0.2)])
    pygame.draw.polygon(surf, (255, 255, 255), pts, max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, (255, 255, 255), (int(cx - r * 0.3), int(cy - r * 0.4)),
                       max(1, int(r * 0.16)))


# ---- 9. Gem-Core Greatblade — DIRECTION C / EPIC ----------------------------
# A broad gold blade with a huge faceted RUBY set into the fuller. Dark gold
# body holds value; the gem is the one bold accent.
# Darkened ~1.5 value steps toward Filigree's bronze so the day-sky body-vs-sky
# contrast lifts from ~38% toward 55%+; the ruby + central highlight ridge still
# read it as gleaming boss-loot, just keyed lower.
GOLDBLADE_LO = (58, 38, 12)
GOLDBLADE_MD = (98, 72, 26)
GOLDBLADE_HI = (160, 130, 62)
RUBY = (224, 44, 60)
RUBY_HI = (255, 140, 150)
RUBY_DK = (120, 16, 30)


def draw_v9(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.20)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.05)
    _vgrad_poly(surf, body, GOLDBLADE_MD, GOLDBLADE_LO, outline=GOLD_SHADOW,
                ow=max(2, int(1.8 * ss)))
    pygame.draw.polygon(surf, GOLDBLADE_HI,
                        [(cx - bwid * 0.22, base_y), (cx, tip_y),
                         (cx + bwid * 0.22, base_y)])
    pygame.draw.line(surf, GOLD_HI, (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, GOLD_HI, (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    span = base_y - tip_y
    # The big ruby set into the lower fuller (the one bold accent).
    gy0 = base_y - int(span * 0.28)
    gr = int(bwid * 0.5)
    _facet_gem(surf, cx, gy0, gr, RUBY, RUBY_HI, RUBY_DK, ss)
    # An ornate gold collar where the blade meets the guard.
    pygame.draw.rect(surf, GOLD, (int(cx - bwid * 0.5), int(base_y - int(8 * ss)),
                                  int(bwid), int(8 * ss)))
    pygame.draw.rect(surf, GOLD_DK, (int(cx - bwid * 0.5), int(base_y - int(8 * ss)),
                                     int(bwid), int(8 * ss)), max(1, int(ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=GOLD,
                metal_dk=GOLD_DK, grip=(92, 28, 32), jewel=None,
                curve=int(5 * ss), gthick=13)
    _facet_gem(surf, cx, py, int(hw * 0.3), RUBY, RUBY_HI, RUBY_DK, ss)


# ---- 10. Wraith Blade — DIRECTION D / COOL ----------------------------------
# REPLACES Winged Crown (steel body washed out on day sky). The INVERSE of #15
# Neon: a matte near-BLACK silhouette with a single thin WHITE edge-light down
# ONE side only — pure shadow shape, no fill glow. Iconic + ice-cold. Body luma
# floor (GATE 2); the lone hard white rim makes the silhouette snap on blue.
WRAITH_FILL = (15, 16, 22)     # matte near-black body
WRAITH_MD = (26, 28, 36)
WRAITH_EDGE = (244, 248, 255)  # the single white edge-light
WRAITH_DIM = (70, 78, 96)      # the unlit (shadow) side rim
WRAITH_GUARD = (20, 22, 30)


def draw_v10(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.0)
    # Matte body, very faint vertical lift so it isn't a dead flat block.
    _vgrad_poly(surf, body, WRAITH_MD, WRAITH_FILL, outline=(6, 7, 10),
                ow=max(2, int(2.0 * ss)))
    # The whole identity: ONE crisp white edge-light down the LEFT cutting edge,
    # carried hard into the apex. The right edge stays a dim shadow rim only —
    # pure silhouette lit from one side, the inverse of Neon's full-outline glow.
    pygame.draw.line(surf, WRAITH_EDGE, (cx - bwid, base_y),
                     (cx, tip_y + int(3 * ss)), max(2, int(2.8 * ss)))
    pygame.draw.line(surf, WRAITH_DIM, (cx + bwid, base_y),
                     (cx, tip_y + int(5 * ss)), max(1, int(1.4 * ss)))
    # A single thin white sliver tracing just inside the lit edge sells the
    # rim-light volume — one bold accent, nothing else on the body.
    pygame.draw.line(surf, WRAITH_EDGE,
                     (cx - bwid * 0.78, base_y - int(8 * ss)),
                     (cx - int(2 * ss), tip_y + int(20 * ss)), max(1, int(1.2 * ss)))
    # Dark guard, lit only on the same left side so the rim-light reads consistent.
    grect = [(cx - ghw, gy - int(6 * ss)), (cx + ghw, gy - int(6 * ss)),
             (cx + ghw, gy + int(6 * ss)), (cx - ghw, gy + int(6 * ss))]
    pygame.draw.polygon(surf, WRAITH_GUARD, grect)
    pygame.draw.polygon(surf, (8, 9, 12), grect, max(1, int(1.6 * ss)))
    pygame.draw.line(surf, WRAITH_EDGE, (cx - ghw, gy - int(6 * ss)),
                     (cx - ghw, gy + int(6 * ss)), max(2, int(2.2 * ss)))
    pygame.draw.line(surf, WRAITH_EDGE, (cx - ghw, gy - int(6 * ss)),
                     (cx + ghw, gy - int(6 * ss)), max(1, int(1.4 * ss)))
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.38), WRAITH_GUARD, ss)
    pr = int(hw * 0.44)
    pygame.draw.circle(surf, WRAITH_FILL, (cx, py), pr)
    pygame.draw.circle(surf, (8, 9, 12), (cx, py), pr, max(1, int(1.6 * ss)))
    # Left-side crescent rim-light on the pommel — same single light direction.
    pygame.draw.arc(surf, WRAITH_EDGE,
                    (int(cx - pr), int(py - pr), int(pr * 2), int(pr * 2)),
                    math.pi * 0.55, math.pi * 1.45, max(2, int(2.0 * ss)))


# ---- 11. Filigree Gold Blade — DIRECTION C / EPIC ---------------------------
# A dark-gold blade carved with BOLD scrollwork: two big symmetric S-scrolls and
# a central diamond. Engraved, not fizzy — every scroll is a fat stroke.
FILI_LO = (104, 72, 22)        # dark engraved gold
FILI_MD = (172, 132, 52)
FILI_HI = (236, 200, 110)
SCROLL_DK = (78, 50, 14)
SCROLL_HI = (255, 228, 150)


def draw_v11(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.08)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.03)
    _vgrad_poly(surf, body, FILI_MD, FILI_LO, outline=SCROLL_DK,
                ow=max(2, int(1.8 * ss)))
    pygame.draw.polygon(surf, FILI_HI,
                        [(cx - bwid * 0.16, base_y), (cx, tip_y),
                         (cx + bwid * 0.16, base_y)])
    span = base_y - tip_y
    # A central engraved diamond cartouche.
    dy = base_y - int(span * 0.30)
    dw = int(bwid * 0.42)
    pygame.draw.polygon(surf, SCROLL_DK,
                        [(cx, dy - dw), (cx + dw * 0.6, dy),
                         (cx, dy + dw), (cx - dw * 0.6, dy)])
    pygame.draw.polygon(surf, SCROLL_HI,
                        [(cx, dy - dw), (cx + dw * 0.6, dy),
                         (cx, dy + dw), (cx - dw * 0.6, dy)], max(2, int(2.0 * ss)))
    # MAX 2 scroll pairs on the body (one above, one below the cartouche), each
    # a BOLD symmetric S-arc. The diamond cartouche stays the single hero mark;
    # more scrolls than this fizzed at route scale.
    for off in (0.50, 0.66):
        for sgn in (-1, 1):
            syc = base_y - int(span * off)
            sw = bwid * (1.0 - (syc - tip_y) / max(1, base_y - tip_y)) * 0.55
            rect = (int(cx + sgn * sw * 0.2 - sw * 0.5),
                    int(syc - sw * 0.5), int(sw), int(sw))
            pygame.draw.arc(surf, SCROLL_DK, rect, 0, math.pi * 1.3,
                            max(2, int(3.0 * ss)))
            pygame.draw.arc(surf, SCROLL_HI, rect, 0, math.pi * 1.3,
                            max(1, int(1.8 * ss)))
    # Bright engraved edges into a hard apex.
    pygame.draw.line(surf, SCROLL_HI, (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, SCROLL_HI, (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=GOLD,
                metal_dk=GOLD_DK, grip=(60, 44, 22), jewel=RUBY if False else None,
                curve=int(4 * ss))
    _facet_gem(surf, cx, py, int(hw * 0.28), RUBY, RUBY_HI, RUBY_DK, ss)


# ---- 12. Crystal Prism Blade — DIRECTION C / COOL-EPIC ----------------------
# A cut-gem prismatic blade: an OPAQUE dark-violet core with big angular prism
# facets in a rainbow of cool jewel tones (amethyst / sapphire / teal). Hard
# faceted point.
PRISM_CORE = (28, 20, 44)      # opaque dark violet core
PRISM_A = (120, 70, 200)       # amethyst facet
PRISM_B = (60, 110, 210)       # sapphire facet
PRISM_C = (60, 190, 200)       # teal facet
PRISM_HI = (220, 220, 255)
PRISM_DK = (14, 10, 26)


def draw_v12(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.02)
    _vgrad_poly(surf, body, PRISM_A, PRISM_CORE, outline=PRISM_DK,
                ow=max(2, int(1.8 * ss)))
    span = base_y - tip_y
    # Big angular prism facets stacked up the blade, alternating jewel tones.
    # The TIP-most band (last) is now violet, not sapphire-blue, so no facet
    # sits near the day-sky luma right where it meets the bright gap band.
    cuts = [0.0, 0.30, 0.54, 0.74, 1.0]
    tones = [PRISM_B, PRISM_C, PRISM_A, PRISM_A]
    for i in range(len(cuts) - 1):
        y0 = base_y - span * cuts[i]
        y1 = base_y - span * cuts[i + 1]
        w0 = bwid * (1.0 - (base_y - y0) / span)
        w1 = bwid * (1.0 - (base_y - y1) / span)
        # left half facet (dark) and right half facet (lit) per band — 2 shapes.
        pygame.draw.polygon(surf, _shade_c(tones[i], -30),
                            [(cx - w0, y0), (cx, y0), (cx, y1), (cx - w1, y1)])
        pygame.draw.polygon(surf, tones[i],
                            [(cx + w0, y0), (cx, y0), (cx, y1), (cx + w1, y1)])
        pygame.draw.line(surf, PRISM_HI, (cx - w0, y0), (cx - w1, y1),
                         max(1, int(1.2 * ss)))
    # A bright central ridge into a hard apex.
    pygame.draw.polygon(surf, PRISM_HI,
                        [(cx - bwid * 0.10, base_y), (cx, tip_y),
                         (cx + bwid * 0.10, base_y)])
    # Thickened white rim keyline so the faceted silhouette reads crisp on blue.
    pygame.draw.line(surf, (255, 255, 255), (cx + bwid, base_y),
                     (cx, tip_y + int(3 * ss)), max(2, int(2.6 * ss)))
    pygame.draw.line(surf, (255, 255, 255), (cx - bwid, base_y),
                     (cx, tip_y + int(3 * ss)), max(2, int(2.6 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=(70, 60, 100),
                metal_dk=PRISM_DK, grip=(34, 28, 52), jewel=PRISM_HI)
    _glow_disc(surf, cx, py, int(hw * 0.28), PRISM_A, ss, alpha=120)


# ════════════════════════════════════════════════════════════════════════════
#  DIRECTION D — STYLIZED / ICONIC
#  Bold simple graphic shapes, less realism, max readability — emoji-clean.
# ════════════════════════════════════════════════════════════════════════════

# ---- 13. Flat Icon Sword — DIRECTION D / PLAYFUL ----------------------------
# Emoji-clean: a flat slate-blue blade silhouette, ONE bold cream centre stripe,
# a flat teal guard. No gradient, no glow — pure graphic shape.
ICON_BLADE = (66, 88, 120)
ICON_BLADE_DK = (34, 48, 72)
ICON_STRIPE = (224, 234, 246)
# Teal guard — matches Skybit's HUD accent and pops as the complement of the
# slate-blue blade, so the furniture is the colour beat instead of generic gold.
ICON_GUARD = (44, 196, 188)
ICON_GUARD_DK = (24, 120, 116)


def draw_v13(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.02)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.0)
    # Flat fill + a fat dark keyline — no gradient.
    pygame.draw.polygon(surf, ICON_BLADE, body)
    pygame.draw.polygon(surf, ICON_BLADE_DK, body, max(2, int(2.4 * ss)))
    # ONE bold cream centre stripe (the single accent), widened ~40% so it holds
    # as a confident graphic beat, stopping shy of the apex.
    pygame.draw.polygon(surf, ICON_STRIPE,
                        [(cx - bwid * 0.224, base_y - int(6 * ss)),
                         (cx, tip_y + int(14 * ss)),
                         (cx + bwid * 0.224, base_y - int(6 * ss))])
    # Flat guard bar + round pommel, all flat colour.
    pygame.draw.rect(surf, ICON_GUARD, (int(cx - ghw), int(gy - 7 * ss),
                                        int(ghw * 2), int(14 * ss)),
                     border_radius=int(6 * ss))
    pygame.draw.rect(surf, ICON_GUARD_DK, (int(cx - ghw), int(gy - 7 * ss),
                                           int(ghw * 2), int(14 * ss)),
                     max(2, int(2.0 * ss)), border_radius=int(6 * ss))
    pygame.draw.rect(surf, ICON_GUARD_DK, (int(cx - hw * 0.32), int(gy + 6 * ss),
                                           int(hw * 0.64), int(gbot - gy - 6 * ss)),
                     border_radius=int(4 * ss))
    pygame.draw.rect(surf, ICON_GUARD, (int(cx - hw * 0.32 + 2 * ss), int(gy + 6 * ss),
                                        int(hw * 0.64 - 4 * ss), int(gbot - gy - 6 * ss)),
                     border_radius=int(4 * ss))
    pr = int(hw * 0.5)
    pygame.draw.circle(surf, ICON_GUARD_DK, (cx, py), pr)
    pygame.draw.circle(surf, ICON_GUARD, (cx, py), int(pr - 2 * ss))


# ---- 14. Chunky Geo Blade — DIRECTION D / COOL ------------------------------
# Angular faceted poly shape in 2 flat colours: a low-poly crystal blade, a
# dark-teal core and a bright-mint lit half split hard down the centre.
GEO_DK = (28, 70, 78)
GEO_LIT = (90, 210, 190)
GEO_KEY = (16, 40, 46)
GEO_GUARD = (44, 52, 64)


def draw_v14(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.08)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # A faceted low-poly silhouette: a mid-blade shoulder then a hard taper.
    shy = base_y - int(span * 0.42)
    shw = hw
    twk = hw * 0.62
    left = [(cx - shw * 0.74, base_y), (cx - shw, shy),
            (cx - twk, base_y - int(span * 0.72)), (cx, tip_y)]
    right = [(cx, tip_y), (cx + twk, base_y - int(span * 0.72)),
             (cx + shw, shy), (cx + shw * 0.74, base_y)]
    body = left + right
    # Split the facet TIP-vs-BASE (not left/right) so the DARK-teal half is
    # always the gap-facing (tip) end on BOTH orientations — the bright mint
    # half never borders the sky-gap directly. `flip` swaps top/bottom but not
    # this tip-down dark band, so it holds for the hanging and standing blade.
    splity = base_y - int(span * 0.50)
    sw_split = shw * (1.0 - (base_y - splity) / span)
    tip_band = [(cx, tip_y), (cx + twk, base_y - int(span * 0.72)),
                (cx + sw_split, splity), (cx - sw_split, splity),
                (cx - twk, base_y - int(span * 0.72))]
    base_band = [(cx - sw_split, splity), (cx + sw_split, splity),
                 (cx + shw, shy), (cx + shw * 0.74, base_y),
                 (cx - shw * 0.74, base_y), (cx - shw, shy)]
    pygame.draw.polygon(surf, GEO_LIT, base_band)
    pygame.draw.polygon(surf, GEO_DK, tip_band)
    pygame.draw.polygon(surf, GEO_KEY, body, max(2, int(2.4 * ss)))
    pygame.draw.line(surf, GEO_KEY, (cx - sw_split, splity),
                     (cx + sw_split, splity), max(2, int(2.0 * ss)))
    # One bold facet line per band (de-noised).
    pygame.draw.line(surf, _shade_c(GEO_DK, 26), (cx, tip_y + int(8 * ss)),
                     (cx + sw_split * 0.6, splity), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, _shade_c(GEO_LIT, 30), (cx - shw, shy),
                     (cx, base_y - int(span * 0.12)), max(1, int(1.6 * ss)))
    # Flat angular guard (a chevron block) + chunky pommel.
    pygame.draw.polygon(surf, GEO_GUARD,
                        [(cx - ghw, gy - int(4 * ss)), (cx + ghw, gy - int(4 * ss)),
                         (cx + ghw * 0.7, gy + int(12 * ss)),
                         (cx - ghw * 0.7, gy + int(12 * ss))])
    pygame.draw.polygon(surf, GEO_KEY,
                        [(cx - ghw, gy - int(4 * ss)), (cx + ghw, gy - int(4 * ss)),
                         (cx + ghw * 0.7, gy + int(12 * ss)),
                         (cx - ghw * 0.7, gy + int(12 * ss))], max(2, int(2.0 * ss)))
    _wrap_grip(surf, cx, gy + int(13 * ss), gbot, int(hw * 0.40), GEO_GUARD, ss)
    pr = int(hw * 0.48)
    pygame.draw.polygon(surf, GEO_LIT,
                        [(cx, py - pr), (cx + pr, py), (cx, py + pr), (cx - pr, py)])
    pygame.draw.polygon(surf, GEO_KEY,
                        [(cx, py - pr), (cx + pr, py), (cx, py + pr), (cx - pr, py)],
                        max(2, int(2.0 * ss)))


# ---- 15. Neon Outline Blade — DIRECTION D / COOL ----------------------------
# Dark near-black fill + a single bright NEON-cyan outline stroke that glows —
# a synthwave icon. The neon traces the silhouette + one centre line.
# Warmed ~5% toward teal (green-biased cyan) so the neon stroke is visibly its
# own colour rather than reading identical to the HUD's pure-cyan timers.
NEON_FILL = (16, 14, 26)
NEON = (48, 236, 214)
NEON_HOT = (196, 255, 248)
NEON_GUARD_FILL = (22, 20, 34)


def draw_v15(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.0)
    pygame.draw.polygon(surf, NEON_FILL, body)
    # The neon silhouette stroke (glow then hot core) — the whole identity.
    outline = [(cx - bwid, base_y), (cx, tip_y), (cx + bwid, base_y)]
    _edge_glow(surf, outline + [outline[0]], NEON, ss, alpha=170, spread=6)
    pygame.draw.lines(surf, NEON, True, outline, max(2, int(2.4 * ss)))
    pygame.draw.lines(surf, NEON_HOT, True, outline, max(1, int(1.0 * ss)))
    # One neon centre line (the single internal accent).
    centre = [(cx, base_y - int(6 * ss)), (cx, tip_y + int(16 * ss))]
    _edge_glow(surf, centre, NEON, ss, alpha=130, spread=4)
    pygame.draw.lines(surf, NEON, False, centre, max(2, int(2.0 * ss)))
    # Neon guard: a dark bar with a neon outline.
    grect = [(cx - ghw, gy - int(6 * ss)), (cx + ghw, gy - int(6 * ss)),
             (cx + ghw, gy + int(6 * ss)), (cx - ghw, gy + int(6 * ss))]
    pygame.draw.polygon(surf, NEON_GUARD_FILL, grect)
    _edge_glow(surf, grect + [grect[0]], NEON, ss, alpha=140, spread=4)
    pygame.draw.lines(surf, NEON, True, grect, max(2, int(2.0 * ss)))
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.38), NEON_GUARD_FILL, ss)
    pr = int(hw * 0.42)
    pygame.draw.circle(surf, NEON_FILL, (cx, py), pr)
    _glow_disc(surf, cx, py, pr + int(2 * ss), NEON, ss, alpha=150)
    pygame.draw.circle(surf, NEON, (cx, py), pr, max(2, int(2.0 * ss)))
    pygame.draw.circle(surf, NEON_HOT, (cx, py), int(pr * 0.4))


# ── version registry ──────────────────────────────────────────────────────────
# (name, direction, tone, draw_fn, note). 15 rows grouped by DIRECTION; the
# crown set + strong keepers carried forward with their Round-4 FIX, plus the 3
# new dark-fill replacements. NIGHT picks get an extra night strip.
VERSIONS = [
    # ── A · ELEMENTAL ─────────────────────────────────────────────────────────
    ("Flame Blade", "A · Elemental", "MEAN", draw_v1,
     "KEEP: charred opaque core, ember crack, fire tongues on the edges"),
    ("Lightning Blade", "A · Elemental", "COOL/EPIC", draw_v3,
     "KEEP: storm-grey body, jagged electric-yellow bolt down the fuller"),
    ("Void Rune Blade", "A · Elemental", "MEAN", draw_v4,
     "CROWN: near-black core, ONE rune sigil locked to the upper third"),
    ("Molten Obsidian Blade", "A · Elemental", "MEAN", draw_v5,
     "NEW: near-black obsidian, ONE thin glowing lava crack (warm-key, vs Flame)"),
    # ── B · LIVING ────────────────────────────────────────────────────────────
    ("Tribal Totem Blade", "B · Living", "PLAYFUL/MEAN", draw_v2,
     "NEW: dark carved-wood blade, ONE bold painted totem-mask glyph"),
    ("Eye Blade", "B · Living", "PLAYFUL/MEAN", draw_v6,
     "FIX: lash spikes cut — single cyan iris + veins carry it"),
    ("Maw Blade", "B · Living", "MEAN", draw_v7,
     "CROWN: fanged maw guard, dark-maroon spine thickened ~30%"),
    ("Serpent Blade", "B · Living", "COOL", draw_v8,
     "FIX: scale chevrons cut to 4 bold Vs (de-fizzed)"),
    # ── C · ORNATE ────────────────────────────────────────────────────────────
    ("Gem-Core Greatblade", "C · Ornate", "EPIC", draw_v9,
     "FIX: gold body darkened toward bronze (body-vs-sky contrast lifted)"),
    ("Filigree Gold Blade", "C · Ornate", "EPIC", draw_v11,
     "CROWN: dark-gold, MAX 2 S-scroll pairs + single diamond cartouche"),
    ("Crystal Prism Blade", "C · Ornate", "COOL/EPIC", draw_v12,
     "FIX: tip facet swapped to violet, white rim thickened"),
    # ── D · ICONIC ────────────────────────────────────────────────────────────
    ("Flat Icon Sword", "D · Iconic", "PLAYFUL", draw_v13,
     "CROWN: flat slate blade, TEAL guard, cream stripe widened ~40%"),
    ("Chunky Geo Blade", "D · Iconic", "COOL", draw_v14,
     "CROWN: low-poly facets, dark-teal half always the sky-facing edge"),
    ("Wraith Blade", "D · Iconic", "COOL", draw_v10,
     "NEW: matte near-black silhouette, single white edge-light (inverse of Neon)"),
    ("Neon Outline Blade", "D · Iconic", "COOL", draw_v15,
     "CROWN (lead): dark fill + single neon stroke, warmed ~5% toward teal"),
]
# The most emissive picks get an extra NIGHT route strip so the glowing cores
# read in both biomes: Flame, Void-Rune, the new Molten, and Neon (the lead).
NIGHT = {0, 2, 3, 14}


# ── obstacle compositing (true px) — carried from round 2 ─────────────────────

def _render_obstacle(draw_fn, H_true, ss, *, flip):
    surf, bw, bh = _box(H_true, ss)
    draw_fn(surf, bw, bh, ss)
    out_w = PIPE_W + 2 * OVERHANG
    out_h = max(1, int(H_true))
    small = pygame.transform.smoothscale(surf, (out_w, out_h))
    if flip:
        small = pygame.transform.flip(small, False, True)
    return small


def _blit_pair(dest, draw_fn, col_cx, gap_y, ss, *, ground_y=GROUND_Y):
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
    lo, hi = 150, 430
    t = step / max(1, n_steps - 1)
    arc = math.sin(t * math.pi)
    gy = hi - (hi - lo) * arc
    return int(max(HALF_GAP + 30, min(GROUND_Y - HALF_GAP - 30, gy)))


def _route_panel(draw_fn, w, h, ss, *, night):
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
    NIGHT_W = ROUTE_W
    ROUTE_H = PLAY_H

    pad = 18
    head = 96
    row_gap = 14
    name_strip = 30
    inner_gap = 22

    base_row_w = HERO_W + inner_gap + ROUTE_W
    night_row_w = base_row_w + inner_gap + NIGHT_W
    row_w = night_row_w
    row_h = name_strip + max(HERO_H, ROUTE_H)

    sheet_w = pad * 2 + row_w
    sheet_h = head + len(VERSIONS) * (row_h + row_gap) + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Warren Sword Route — Round 4 (FINAL POLISH: crown set + keepers + 3 new dark-fills)",
        True, (255, 255, 255)), (pad, 14))
    sheet.blit(sub_f.render(
        "Directions: A Elemental (flame/lightning/void/MOLTEN) · B Living (TOTEM/eye/maw/serpent) · "
        "C Ornate (gem/filigree/prism) · D Iconic (flat/geo/WRAITH/neon).  NEW dark-fills in CAPS.",
        True, (205, 210, 220)), (pad, 48))
    sheet.blit(sub_f.render(
        "GATES on ALL 15: (1) sky-gap brightest/sharpest band, hard tips · (2) opaque dark core, body clears day-blue · "
        "(3) de-noised, 2-3 bold elements.  LEFT 1:1 hero · MID day route · RIGHT night strip (3 picks).",
        True, (170, 178, 190)), (pad, 70))

    name_f = hud._font(19, True)
    dir_f = hud._font(13, True)
    fix_f = hud._font(13, False)

    for idx, (name, direction, tone, draw_fn, fix) in enumerate(VERSIONS):
        ry = head + idx * (row_h + row_gap)
        is_night = idx in NIGHT
        strip_w = night_row_w if is_night else base_row_w
        strip = pygame.Surface((strip_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        # Tone colour-codes the chip: mean=red, epic=gold, cool=cyan, playful=lime.
        tl = tone.lower()
        tone_col = ((230, 80, 80) if "mean" in tl else
                    (240, 200, 90) if "epic" in tl else
                    (110, 220, 110) if "playful" in tl else
                    (110, 200, 235))
        ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
        strip.blit(ntxt, (8, 5))
        dtxt = dir_f.render(f"[{direction}]", True, (180, 188, 200))
        strip.blit(dtxt, (12 + ntxt.get_width(), 9))
        ttxt = dir_f.render(tone, True, tone_col)
        strip.blit(ttxt, (18 + ntxt.get_width() + dtxt.get_width(), 9))
        strip.blit(fix_f.render(fix, True, (188, 194, 206)),
                   (26 + ntxt.get_width() + dtxt.get_width() + ttxt.get_width(), 9))
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

        # --- night route (selected picks) ---
        if is_night:
            night = _route_panel(draw_fn, NIGHT_W, ROUTE_H, SS, night=True)
            sheet.blit(night, (pad + HERO_W + inner_gap + ROUTE_W + inner_gap, body_y))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_sword")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_4.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
