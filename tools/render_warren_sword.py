"""Look-dev renderer (Round 3): the WARREN EVENT sword — 15 NEW versions.

Round-3 brief is a FRESH START. Rounds 1-2 were 20 literal metal-weapon
archetypes (saber / greatsword / falchion / executioner / joker-skin steel
…) and NONE landed. This round abandons that whole "which historical blade"
axis and explores swords as CONCEPTS across four creative directions:

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
Writes docs/warren_sword/round_3.png.
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


# ---- 2. Frost Blade — DIRECTION A / COOL-EPIC -------------------------------
# Solid ICE: an opaque deep-teal core (NOT a translucent tint), big internal
# facet planes, frozen cracks, and a hard cold-white rim keyline so the
# silhouette reads on blue. Hard point.
FROST_CORE = (22, 54, 78)      # opaque deep teal core
FROST_MD = (46, 110, 150)
FROST_HI = (150, 214, 240)
FROST_RIM = (228, 248, 255)
FROST_DK = (12, 30, 50)


def draw_v2(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.02)
    _vgrad_poly(surf, body, FROST_MD, FROST_CORE, outline=FROST_DK,
                ow=max(2, int(1.8 * ss)))
    # Two big internal facet planes (left dark, right lit) — bold, reads small.
    pygame.draw.polygon(surf, _shade_c(FROST_CORE, 14),
                        [(cx - bwid, base_y), (cx, tip_y), (cx, base_y)])
    pygame.draw.polygon(surf, _shade_c(FROST_MD, 12),
                        [(cx + bwid, base_y), (cx, tip_y), (cx, base_y)])
    # One bold cold highlight wedge down the centre ridge.
    pygame.draw.polygon(surf, FROST_HI,
                        [(cx - bwid * 0.16, base_y), (cx, tip_y),
                         (cx + bwid * 0.16, base_y)])
    # A couple of big frozen cracks branching off the ridge (2 bold elements).
    for sgn, t0 in ((-1, 0.44), (1, 0.66)):
        cy0 = base_y + (tip_y - base_y) * t0
        cw = bwid * (1.0 - (cy0 - tip_y) / max(1, base_y - tip_y))
        pygame.draw.line(surf, FROST_HI, (cx, cy0),
                         (cx + sgn * cw * 0.7, cy0 - int(10 * ss)), max(1, int(1.4 * ss)))
    # Hard cold-white rim keyline + a faint cold edge glow (kept restrained).
    _edge_glow(surf, [(cx - bwid, base_y), (cx, tip_y)], (150, 210, 255), ss,
               alpha=80, spread=3)
    _edge_glow(surf, [(cx + bwid, base_y), (cx, tip_y)], (150, 210, 255), ss,
               alpha=80, spread=3)
    pygame.draw.line(surf, FROST_RIM, (cx - bwid, base_y), (cx, tip_y + int(3 * ss)),
                     max(1, int(1.8 * ss)))
    pygame.draw.line(surf, FROST_RIM, (cx + bwid, base_y), (cx, tip_y + int(3 * ss)),
                     max(1, int(1.8 * ss)))
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=(54, 92, 122),
                metal_dk=FROST_DK, grip=(30, 50, 72), jewel=FROST_RIM)


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
    # Rune 1: a bold chevron sigil lower on the blade.
    ry1 = base_y - int(span * 0.30)
    rw1 = bwid * (1.0 - (ry1 - tip_y) / max(1, base_y - tip_y)) * 0.55
    chev = [(cx - rw1, ry1 - int(7 * ss)), (cx, ry1 + int(5 * ss)),
            (cx + rw1, ry1 - int(7 * ss))]
    _edge_glow(surf, chev, RUNE, ss, alpha=170, spread=5)
    pygame.draw.lines(surf, RUNE_HOT, False, chev, max(2, int(2.2 * ss)))
    # Rune 2: a glowing ring sigil higher up.
    ry2 = base_y - int(span * 0.58)
    rr = int(bwid * 0.34)
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

# ---- 5. Grin Blade — DIRECTION B / PLAYFUL ----------------------------------
# A wicked grinning face worked into a steel blade: two angry brow-slit eyes and
# a big toothy grin near the guard. Clean steel above so the tip/gap stays sharp.
# Darkened gunmetal steel for the Living/Ornate steel bodies — kept cool +
# polished but pulled well under day-sky luma so the silhouette holds on blue
# without a wash (GATE 2); the highlight ridge supplies the "polished" read.
STEEL_LO = (44, 52, 66)
STEEL_MD = (92, 104, 124)
STEEL_HI = (170, 184, 206)
STEEL_EDGE = (236, 244, 255)
GRIN_INK = (16, 20, 28)
GRIN_RED = (224, 56, 60)


def draw_v5(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.10)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.02)
    _vgrad_poly(surf, body, STEEL_HI, STEEL_LO, outline=GRIN_INK,
                ow=max(2, int(1.8 * ss)))
    pygame.draw.polygon(surf, _shade_c(STEEL_HI, 16),
                        [(cx - bwid * 0.22, base_y), (cx, tip_y),
                         (cx + bwid * 0.22, base_y)])
    span = base_y - tip_y
    # The grin sits in the lower-middle of the blade (the widest readable zone).
    fy = base_y - int(span * 0.26)
    fw = bwid * (1.0 - (fy - tip_y) / max(1, base_y - tip_y))
    # Two slanted angry eyes (brow slits) above the mouth.
    ey = fy - int(span * 0.10)
    ew = fw * 0.9
    for sgn in (-1, 1):
        eyex = cx + sgn * ew * 0.42
        pygame.draw.polygon(surf, GRIN_INK,
                            [(eyex - sgn * int(6 * ss), ey - int(5 * ss)),
                             (eyex + sgn * int(7 * ss), ey + int(2 * ss)),
                             (eyex - sgn * int(2 * ss), ey + int(4 * ss))])
    # The big toothy grin: a curved dark mouth with a few zig-zag teeth.
    mw = fw * 0.82
    mouth_top = []
    mouth_bot = []
    n = 8
    for i in range(n + 1):
        t = i / n
        mx = cx - mw + 2 * mw * t
        sag = math.sin(t * math.pi) * int(10 * ss)
        mouth_top.append((mx, fy - int(4 * ss) + sag * 0.4))
        mouth_bot.append((mx, fy + int(7 * ss) + sag))
    pygame.draw.polygon(surf, GRIN_INK, mouth_top + list(reversed(mouth_bot)))
    # Zig-zag teeth across the grin (a few big triangles, not a comb).
    nteeth = 5
    for i in range(nteeth):
        t = (i + 0.5) / nteeth
        mx = cx - mw + 2 * mw * t
        sag = math.sin(t * math.pi) * int(10 * ss)
        ty0 = fy - int(3 * ss) + sag * 0.4
        pygame.draw.polygon(surf, CREAM,
                            [(mx - int(5 * ss), ty0),
                             (mx + int(5 * ss), ty0),
                             (mx, ty0 + int(9 * ss) + sag * 0.5)])
    _hilt_basic(surf, cx, gy, gbot, py, hw, ghw, ss, metal=IRON_MD,
                metal_dk=IRON_DK, grip=LEATHER_DK, jewel=GRIN_RED)


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
    # Heavy lash spikes around the top of the eye (a few bold spikes).
    for k in range(-2, 3):
        a = math.pi * 1.5 + k * 0.34
        lx = cx + math.cos(a) * ew
        ly = ey + math.sin(a) * eh
        pygame.draw.line(surf, (16, 18, 26), (lx, ly),
                         (lx + math.cos(a) * int(9 * ss), ly + math.sin(a) * int(9 * ss)),
                         max(2, int(2.0 * ss)))
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
    _vgrad_poly(surf, body, TONGUE_HI, TONGUE_LO, outline=(20, 10, 14),
                ow=max(2, int(1.8 * ss)))
    # A bony fang ridge down the centre (one bold light wedge) + bright edges.
    pygame.draw.polygon(surf, FANG,
                        [(cx - bwid * 0.20, base_y), (cx, tip_y),
                         (cx + bwid * 0.20, base_y)])
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
    # A row of big scale chevrons riding the body (a few bold Vs, de-noised).
    nsc = 5
    for i in range(nsc):
        t = 0.14 + i * 0.16
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
GOLDBLADE_LO = (120, 84, 28)
GOLDBLADE_MD = (190, 150, 60)
GOLDBLADE_HI = (244, 214, 120)
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


# ---- 10. Winged Crown Relic — DIRECTION C / EPIC ----------------------------
# A polished light-steel blade with an ORNATE gold guard: two swept golden wings
# and a small crown boss, a sapphire pommel. Boss-loot silhouette.
# Darkened polished steel for the relic body — the gold furniture carries the
# "shiny" read, so the blade itself is pulled under day-sky luma (GATE 2) while
# its bright central ridge keeps the polished highlight.
RELIC_LO = (78, 90, 108)
RELIC_MD = (130, 144, 164)
RELIC_HI = (220, 230, 244)
SAPPHIRE = (60, 110, 230)
SAPPHIRE_HI = (150, 190, 255)
SAPPHIRE_DK = (24, 50, 130)


def draw_v10(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = _blade_hw(ss)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.0)
    _vgrad_poly(surf, body, RELIC_MD, RELIC_LO, outline=(40, 48, 60),
                ow=max(2, int(1.8 * ss)))
    pygame.draw.polygon(surf, RELIC_HI,
                        [(cx - bwid * 0.24, base_y), (cx, tip_y),
                         (cx + bwid * 0.24, base_y)])
    pygame.draw.line(surf, (255, 255, 255), (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (255, 255, 255), (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    # A small gold sapphire-set boss at the blade root.
    _facet_gem(surf, cx, base_y - int(2 * ss), int(bwid * 0.34),
               SAPPHIRE, SAPPHIRE_HI, SAPPHIRE_DK, ss)
    # Two swept golden WINGS forming the crossguard.
    for sgn in (-1, 1):
        wing = [(cx + sgn * int(6 * ss), gy + int(2 * ss)),
                (cx + sgn * ghw * 0.6, gy - int(10 * ss)),
                (cx + sgn * ghw, gy - int(4 * ss)),
                (cx + sgn * ghw * 0.92, gy + int(8 * ss)),
                (cx + sgn * ghw * 0.5, gy + int(10 * ss))]
        pygame.draw.polygon(surf, GOLD, wing)
        pygame.draw.polygon(surf, GOLD_DK, wing, max(1, int(1.4 * ss)))
        # feather lines (a few bold strokes, not fine barbs).
        for f in range(3):
            t = 0.4 + f * 0.2
            pygame.draw.line(surf, GOLD_DK,
                             (cx + sgn * ghw * 0.3, gy - int(2 * ss)),
                             (cx + sgn * ghw * (0.6 + t * 0.35),
                              gy - int(6 * ss) + f * int(5 * ss)),
                             max(1, int(1.2 * ss)))
    # A small gold crown boss at the guard centre (3 points).
    cb = int(10 * ss)
    pygame.draw.polygon(surf, GOLD,
                        [(cx - cb, gy + cb), (cx - cb, gy - int(2 * ss)),
                         (cx - cb * 0.5, gy - cb), (cx, gy - int(2 * ss)),
                         (cx + cb * 0.5, gy - cb), (cx + cb, gy - int(2 * ss)),
                         (cx + cb, gy + cb)])
    pygame.draw.polygon(surf, GOLD_DK,
                        [(cx - cb, gy + cb), (cx - cb, gy - int(2 * ss)),
                         (cx - cb * 0.5, gy - cb), (cx, gy - int(2 * ss)),
                         (cx + cb * 0.5, gy - cb), (cx + cb, gy - int(2 * ss)),
                         (cx + cb, gy + cb)], max(1, int(1.4 * ss)))
    _wrap_grip(surf, cx, gy + cb + int(2 * ss), gbot, int(hw * 0.40),
               (70, 60, 40), ss)
    _pommel(surf, cx, py, int(hw * 0.46), GOLD, ss, dk=GOLD_DK)
    _facet_gem(surf, cx, py, int(hw * 0.26), SAPPHIRE, SAPPHIRE_HI, SAPPHIRE_DK, ss)


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
    # Two big symmetric S-scrolls flanking the diamond (BOLD strokes, few arcs).
    for sgn in (-1, 1):
        for off, scr in ((0.50, SCROLL_HI), (0.66, SCROLL_HI)):
            syc = base_y - int(span * off)
            sw = bwid * (1.0 - (syc - tip_y) / max(1, base_y - tip_y)) * 0.55
            rect = (int(cx + sgn * sw * 0.2 - sw * 0.5),
                    int(syc - sw * 0.5), int(sw), int(sw))
            pygame.draw.arc(surf, SCROLL_DK, rect, 0, math.pi * 1.3,
                            max(2, int(2.6 * ss)))
            pygame.draw.arc(surf, scr, rect, 0, math.pi * 1.3, max(1, int(1.6 * ss)))
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
    cuts = [0.0, 0.30, 0.54, 0.74, 1.0]
    tones = [PRISM_B, PRISM_C, PRISM_A, PRISM_B]
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
    pygame.draw.line(surf, (255, 255, 255), (cx + bwid, base_y),
                     (cx, tip_y + int(3 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, PRISM_HI, (cx - bwid, base_y),
                     (cx, tip_y + int(3 * ss)), max(1, int(1.6 * ss)))
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
ICON_GUARD = (244, 176, 64)
ICON_GUARD_DK = (176, 116, 30)


def draw_v13(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.02)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.0)
    # Flat fill + a fat dark keyline — no gradient.
    pygame.draw.polygon(surf, ICON_BLADE, body)
    pygame.draw.polygon(surf, ICON_BLADE_DK, body, max(2, int(2.4 * ss)))
    # ONE bold cream centre stripe (the single accent), stopping shy of the apex.
    pygame.draw.polygon(surf, ICON_STRIPE,
                        [(cx - bwid * 0.16, base_y - int(6 * ss)),
                         (cx, tip_y + int(14 * ss)),
                         (cx + bwid * 0.16, base_y - int(6 * ss))])
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
    # Two flat colour halves split hard down the centre (low-poly read).
    pygame.draw.polygon(surf, GEO_DK, left + [(cx, base_y)])
    pygame.draw.polygon(surf, GEO_LIT, [(cx, base_y)] + right)
    pygame.draw.polygon(surf, GEO_KEY, body, max(2, int(2.4 * ss)))
    pygame.draw.line(surf, GEO_KEY, (cx, tip_y + int(6 * ss)), (cx, base_y),
                     max(2, int(2.0 * ss)))
    # A couple of bold facet lines on each half (de-noised, just 1 each).
    pygame.draw.line(surf, _shade_c(GEO_DK, 26), (cx - shw, shy),
                     (cx, base_y - int(span * 0.2)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, _shade_c(GEO_LIT, 30), (cx + shw, shy),
                     (cx, base_y - int(span * 0.2)), max(1, int(1.6 * ss)))
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
NEON_FILL = (16, 14, 26)
NEON = (60, 240, 240)
NEON_HOT = (200, 255, 255)
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
# (name, direction, tone, draw_fn, note). NIGHT picks get an extra night strip.
VERSIONS = [
    ("Flame Blade", "A · Elemental", "MEAN", draw_v1,
     "charred opaque core, ember crack, fire licking the edges"),
    ("Frost Blade", "A · Elemental", "COOL/EPIC", draw_v2,
     "solid ice, opaque teal core, frozen cracks, cold-white rim"),
    ("Lightning Blade", "A · Elemental", "COOL/EPIC", draw_v3,
     "storm-grey body, jagged electric-yellow bolt down the fuller"),
    ("Void Rune Blade", "A · Elemental", "MEAN", draw_v4,
     "near-black core, two glowing rune sigils, magenta energy edge"),
    ("Grin Blade", "B · Living", "PLAYFUL", draw_v5,
     "wicked toothy grin + angry brow-slit eyes worked in steel"),
    ("Eye Blade", "B · Living", "PLAYFUL/MEAN", draw_v6,
     "single watching iris, lash spikes, blood veins"),
    ("Maw Blade", "B · Living", "MEAN", draw_v7,
     "fanged beast-mouth guard, blade as a bony tongue/fang"),
    ("Serpent Blade", "B · Living", "COOL", draw_v8,
     "scaled snake-body blade, big scale chevrons, cobra-hood guard"),
    ("Gem-Core Greatblade", "C · Ornate", "EPIC", draw_v9,
     "broad gold blade, huge faceted ruby set in the fuller"),
    ("Winged Crown Relic", "C · Ornate", "EPIC", draw_v10,
     "polished steel, gold wings + crown guard, sapphire pommel"),
    ("Filigree Gold Blade", "C · Ornate", "EPIC", draw_v11,
     "dark-gold blade, BOLD S-scrolls + diamond cartouche, ruby pommel"),
    ("Crystal Prism Blade", "C · Ornate", "COOL/EPIC", draw_v12,
     "opaque violet core, big angular jewel-tone prism facets"),
    ("Flat Icon Sword", "D · Iconic", "PLAYFUL", draw_v13,
     "emoji-clean flat slate blade, one cream stripe, teal guard"),
    ("Chunky Geo Blade", "D · Iconic", "COOL", draw_v14,
     "low-poly faceted shape, 2 flat colours split hard"),
    ("Neon Outline Blade", "D · Iconic", "COOL", draw_v15,
     "dark fill + single bright neon-cyan glowing outline stroke"),
]
# The strongest picks (one per direction-ish) get an extra NIGHT route strip so
# the emissive cores read in both biomes: Flame, Void-Rune, Neon.
NIGHT = {0, 3, 14}


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
        "Warren Sword Route — Round 3 (FRESH START: 15 new swords, 4 directions)",
        True, (255, 255, 255)), (pad, 14))
    sheet.blit(sub_f.render(
        "Directions: A Elemental (flame/frost/lightning/void) · B Living (grin/eye/maw/serpent) · "
        "C Ornate (gem/crown/filigree/prism) · D Iconic (flat/geo/neon).",
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
    out_path = os.path.join(out_dir, "round_3.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
