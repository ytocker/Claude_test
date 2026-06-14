"""Look-dev renderer (Round 6): the WARREN EVENT prop — BROADENED + RE-POSED.

ROUND 6 broadens the concept beyond swords and fixes the lean pose. Two changes
drove this round:
  (1) BROADEN — the clown can hold ANYTHING interesting. ~15 holistic props now
      span FOUR families (~4/4/4/3): A SWORDS & BLADES (the round-5 winners,
      re-posed), B STAFFS & SCEPTERS, C CLOWN PROPS, D MYSTIC & MENACING. Each
      is a COMPLETE, structurally distinct object, authored gap-facing-end UP so
      the route flip scaffolding plants it correctly.
  (2) FIX THE POSE — round 5 held the sword awkwardly upward behind the head. The
      new pose stands the prop VERTICALLY with its bottom tip resting ON THE
      GROUND beside the clown; the near/lower gloved hand grips it near the top
      (a relaxed showman LEAN, weight resting on the prop) while the OTHER hand
      still presents the floating power-up die up high. The pose is IDENTICAL
      every row; only the prop changes.

The three gameplay GATES still drive every prop at ROUTE scale (~30-40 px wide):
  1. GAP READABILITY — the gap-facing END is a clean readable terminus (point,
     finial, orb, hook, prongs, star) with a hard dark-body→bright-gap value
     break; even BLUNT-topped props (lollipop, orb, knob cane) are shaped + dark-
     rimmed so the sky-gap stays the brightest, sharpest band.
  2. DAY-SKY CONTRAST — median BODY luma under ~140 against the ~190 day sky
     (round-5 ran hot at 165-172; highlight ramps pulled down ~15-20%). Opaque
     dark cores; no pale-on-blue.
  3. DE-NOISE — 2-3 bold elements per prop in the route silhouette; the LEFT
     leaned hero shot may carry finer detail than the tiled RIGHT version.

Prior lineage (Round 5): the WARREN EVENT sword — CONCEPT REDESIGN.

Rounds 1-4 (35 swords) were ALL rejected for one root reason finally pinned
down: every version was the SAME silhouette recolored. The old code piped all
blades through one shared `_hilt_basic()` (crossguard + grip + pommel), so only
the BLADE re-colored — the handle and base never changed. The clown was never
shown holding the weapon, so the swords read as abstract pillars, not as the
ONE complete sword the clown carries and the route is filled with.

NEW DIRECTION: the clown holds a single COMPLETE believable weapon and the
route is that SAME weapon tiled. So each of the 12 designs is a HOLISTIC sword —
a distinct BLADE FORM **and** GUARD **and** GRIP **and** POMMEL composed as one
coherent weapon. NO two share a hilt or a profile; no recolors. The 12 span
three registers (~4 each):
  CARTOON   — playful, tied to the clown's Plum & Lime world.
  REALISTIC — four DIFFERENT real sword families (falchion / saber / leaf /
              greatsword), not one blade recolored.
  FANTASY   — dramatic hero/boss weapons.

The STRUCTURAL FIX: each sword has its OWN complete draw function that builds a
distinct blade silhouette + its OWN crossguard + grip + pommel. The small
reusable PRIMITIVES (`_vgrad_poly`, `_edge_glow`, `_glow_disc`, `_rivet`,
`_wrap_grip`, plus new `_disc_pommel`, `_ball_pommel`, `_facet_gem`,
`_ribbed_grip`, `_candy_twist`, `_bone_grip`, `_crossguard`) are COMPOSED into
12 genuinely different weapons — different guard TYPES (cross / basket / disc /
swept / winged / bell / jaw), grips (wrapped / ribbed / candy-twist / bone /
vertebra), pommels (round / faceted gem / crown / balloon / skull / horned).

The figure: 12 ROWS, each TWO panels.
  LEFT  — THE CLOWN HOLDING THIS SWORD. The REAL game jester (`build_jester`
          + `JESTERS[-1]`, exactly as `game/warren_demo.py` builds the hero
          clown) with THIS sword gripped in its raised gloved hand, a few
          fingers + thumb drawn OVER the hilt so it reads as truly held.
  RIGHT — THE ROUTE FILLED WITH IT. The true-geometry day-sky panorama: every
          pillar is THIS sword — bottom obstacle a full sword point-UP from the
          ground, top obstacle the same sword point-DOWN from the ceiling, a
          flyable sky-gap between the two tips.

The three gameplay GATES drive EVERY version at ROUTE scale (~30-40 px wide):
  1. GAP READABILITY — the sky-gap between the two tips is the brightest /
     sharpest band; a hard dark-body -> bright-gap value break; sharp tips.
  2. DAY-SKY CONTRAST — weapon BODY luma well under the ~173 day sky (aim <120);
     opaque dark cores, never pale/translucent on blue.
  3. DE-NOISE — 2-3 bold elements per weapon at route scale. Fine hilt ornament
     is fine on the LEFT clown hero shot but must NOT fizz in the RIGHT route
     panorama — the held version can carry more detail than the tiled version.

All art is procedural; supersampled then smoothscaled for crisp edges. The
box / flip / panorama scaffolding (`_box`, `_render_obstacle`, `_blit_pair`,
`_route_panel`) is carried from round 2/4 unchanged — only the 12 weapons + the
held-clown panel are new.

Run (headless):
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYTHONPATH=. \
        python tools/render_warren_sword.py
Writes docs/warren_sword/round_6.png.
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
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

# Day sky for contrast — a simple top→bottom blue (~173 luma).
SKY_TOP = (96, 165, 230)
SKY_BOT = (175, 215, 245)

# Plum & Lime clown world palette (so the cartoon swords tie to the hero clown).
PLUM = (96, 44, 150)
PLUM_DK = (66, 28, 110)
LIME = (132, 218, 116)
LIME_DK = (74, 150, 70)
GOLD = (250, 205, 72)
GOLD_HI = (255, 236, 150)
GOLD_DK = (176, 130, 30)
GOLD_SHADOW = (110, 78, 22)
CREAM = (255, 248, 224)
INK = (28, 22, 30)

# Neutral dark hilt metals (always hold value on blue).
IRON_DK = (40, 44, 52)
IRON_MD = (78, 84, 96)
IRON_HI = (150, 158, 172)
STEEL_DK = (52, 58, 70)
STEEL_MD = (104, 112, 128)
STEEL_HI = (176, 184, 200)
LEATHER = (74, 52, 38)
LEATHER_DK = (48, 34, 26)
LEATHER_HI = (118, 86, 58)
BRONZE_LO = (72, 46, 20)
BRONZE_MD = (132, 90, 40)
BRONZE_HI = (180, 134, 66)
BONE = (224, 214, 184)
BONE_DK = (150, 138, 108)


# ════════════════════════════════════════════════════════════════════════════
#  REUSABLE PRIMITIVES — kept small + composable. EACH sword COMPOSES these into
#  its OWN guard + grip + pommel; nothing routes through a shared hilt.
# ════════════════════════════════════════════════════════════════════════════

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
    """A radial ADD glow disc (for a gem / eye / rune highlight)."""
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


def _wrap_grip(surf, cx, top, bot, hw, base_col, ss, *, diag=False):
    """A wrapped grip column drawn as bold bands (no fine cross-hatch). `diag`
    skews the band seams into leather-wrap diagonals for a corded read."""
    base_col_dk = _shade_c(base_col, -46)
    band_h = max(4, int(7 * ss))
    y = int(top)
    i = 0
    while y < bot:
        c = base_col if i % 2 == 0 else _shade_c(base_col, -26)
        pygame.draw.rect(surf, c, (int(cx - hw), y, int(hw * 2), band_h))
        if diag:
            pygame.draw.line(surf, base_col_dk, (int(cx - hw), y),
                             (int(cx + hw), y + band_h), max(1, int(ss)))
        else:
            pygame.draw.line(surf, base_col_dk, (int(cx - hw), y),
                             (int(cx + hw), y), max(1, int(ss)))
        y += band_h
        i += 1
    pygame.draw.line(surf, base_col_dk, (int(cx - hw), int(top)),
                     (int(cx - hw), int(bot)), max(1, int(ss)))
    pygame.draw.line(surf, base_col_dk, (int(cx + hw), int(top)),
                     (int(cx + hw), int(bot)), max(1, int(ss)))


def _ribbed_grip(surf, cx, top, bot, hw, base_col, ss):
    """A wire-bound RIBBED grip: a dark column ringed with bold lit bands, so the
    grip reads as twisted metal wire rather than flat leather."""
    pygame.draw.rect(surf, _shade_c(base_col, -40), (int(cx - hw), int(top),
                                                     int(hw * 2), int(bot - top)))
    band_h = max(3, int(5 * ss))
    y = int(top)
    while y < bot:
        pygame.draw.line(surf, _shade_c(base_col, 40), (int(cx - hw), y),
                         (int(cx + hw), y - max(1, int(2 * ss))), max(1, int(2 * ss)))
        y += band_h
    pygame.draw.line(surf, _shade_c(base_col, 60), (int(cx - hw * 0.5), int(top)),
                     (int(cx - hw * 0.5), int(bot)), max(1, int(ss)))


def _candy_twist(surf, cx, top, bot, hw, col_a, col_b, ss):
    """A barber-pole CANDY-TWIST grip: alternating diagonal stripes of two
    colours spiralling up the grip — the cartoon hero grip."""
    pygame.draw.rect(surf, _shade_c(col_a, -30), (int(cx - hw), int(top),
                                                  int(hw * 2), int(bot - top)))
    stripe = max(4, int(6 * ss))
    n = int((bot - top) / stripe) + 3
    for i in range(-2, n):
        y0 = top + i * stripe
        col = col_a if i % 2 == 0 else col_b
        quad = [(cx - hw, y0), (cx + hw, y0 - hw * 1.4),
                (cx + hw, y0 - hw * 1.4 + stripe), (cx - hw, y0 + stripe)]
        # Clip to the grip column via a mask so the diagonals stay inside.
        pygame.draw.polygon(surf, col, quad)
    # Re-clip: redraw the column outline so spill past the sides is hidden by a
    # second pass of side rails the blade base/pommel will overlap anyway.
    pygame.draw.rect(surf, _shade_c(col_a, -55), (int(cx - hw), int(top),
                                                  int(hw * 2), int(bot - top)),
                     max(1, int(1.6 * ss)))
    pygame.draw.line(surf, _shade_c(CREAM, 0), (int(cx - hw * 0.5), int(top)),
                     (int(cx - hw * 0.5), int(bot)), max(1, int(ss)))


def _bone_grip(surf, cx, top, bot, hw, ss, *, vertebra=False):
    """A carved BONE grip: a pale ivory column with dark sockets. `vertebra`
    stacks fat rounded bone segments (the demon-blade spine grip) instead of a
    smooth shaft."""
    if vertebra:
        seg_h = max(6, int(11 * ss))
        y = int(top)
        i = 0
        while y < bot:
            ch = min(seg_h, int(bot) - y)
            r = hw
            pygame.draw.ellipse(surf, BONE_DK, (int(cx - r), y, int(r * 2), ch + 2))
            pygame.draw.ellipse(surf, BONE, (int(cx - r + ss), y, int(r * 2 - 2 * ss), ch))
            pygame.draw.line(surf, _shade_c(BONE_DK, -30), (int(cx - r), y),
                             (int(cx + r), y), max(1, int(1.4 * ss)))
            y += seg_h
            i += 1
    else:
        pygame.draw.rect(surf, BONE_DK, (int(cx - hw), int(top),
                                         int(hw * 2), int(bot - top)))
        pygame.draw.rect(surf, BONE, (int(cx - hw + ss), int(top),
                                      int(hw * 2 - 2 * ss), int(bot - top)))
        for t in (0.28, 0.6):
            sy = top + (bot - top) * t
            pygame.draw.circle(surf, _shade_c(BONE_DK, -40), (int(cx), int(sy)),
                               max(2, int(hw * 0.35)))


def _crossguard(surf, cx, gy, ghw, thick, col, ss, *, curve=0.0, dk=None,
                quillon_r=0.55):
    """A horizontal crossguard centred at (cx, gy) spanning +-ghw, `thick` tall,
    with knobbed quillon ends. `curve` bows the bar; `quillon_r` scales the end
    knobs (0 disables them)."""
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
    if quillon_r > 0:
        for sgn in (-1, 1):
            pygame.draw.circle(surf, col, (int(cx + sgn * ghw), int(gy)),
                               int(thick * quillon_r))
            pygame.draw.circle(surf, dk, (int(cx + sgn * ghw), int(gy)),
                               int(thick * quillon_r), max(1, int(ss)))
            pygame.draw.circle(surf, _shade_c(col, 50),
                               (int(cx + sgn * ghw - thick * 0.2),
                                int(gy - thick * 0.2)), max(1, int(thick * 0.22)))


def _ball_pommel(surf, cx, py, r, col, ss, *, dk=None, glossy=False):
    dk = dk or _shade_c(col, -55)
    pygame.draw.circle(surf, dk, (int(cx), int(py)), int(r))
    pygame.draw.circle(surf, col, (int(cx), int(py)), int(r - ss))
    pygame.draw.circle(surf, _shade_c(col, 55),
                       (int(cx - r * 0.3), int(py - r * 0.3)), max(1, int(r * 0.4)))
    if glossy:
        # A hot specular spot + a soft crescent so it reads as a glossy balloon.
        pygame.draw.circle(surf, (255, 255, 255),
                           (int(cx - r * 0.34), int(py - r * 0.38)),
                           max(1, int(r * 0.2)))


def _disc_pommel(surf, cx, py, r, col, ss, *, dk=None):
    """A flat wheel/disc pommel seen edge-on — a squat oval, the realistic
    medieval pommel, distinct from the round ball."""
    dk = dk or _shade_c(col, -55)
    rect = pygame.Rect(int(cx - r), int(py - r * 0.62), int(r * 2), int(r * 1.24))
    pygame.draw.ellipse(surf, dk, rect)
    pygame.draw.ellipse(surf, col, rect.inflate(-int(2 * ss), -int(2 * ss)))
    pygame.draw.circle(surf, _shade_c(col, 45),
                       (int(cx - r * 0.3), int(py - r * 0.2)), max(1, int(r * 0.3)))
    pygame.draw.circle(surf, dk, (int(cx), int(py)), max(2, int(r * 0.22)))


def _facet_gem(surf, cx, cy, r, col, hi, dk, ss):
    """A faceted oval gem: a dark setting, two big facet halves, a hot glint."""
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


# ── the sword frame (carried from round 2/4) ─────────────────────────────────
OVERHANG = 12                  # guards may spill this far past the 58-px column
HILT_PX = 138                  # nominal hilt height, true px
MIN_BLADE_PX = 40


def _box(H, ss):
    bw = (PIPE_W + 2 * OVERHANG) * ss
    bh = max(1, int(H)) * ss
    return pygame.Surface((bw, bh), pygame.SRCALPHA), bw, bh


def _layout(bh, ss, *, hilt_px=HILT_PX):
    """Key y-coords (SS space) for a point-UP sword in a box of SS height bh:
    tip at top (y=0), pommel at the bottom. Returns
    (tip_y, blade_base_y, guard_y, grip_top_y, grip_bot_y, pommel_y)."""
    hilt = hilt_px * ss
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


def _straight_body(cx, tip_y, base_y, hw, *, taper=0.0):
    """The canonical hard-taper double-edged silhouette (apex == box top so the
    dark body meets bright sky as a single razor break — GATE 1)."""
    bw = hw * (1.0 + taper)
    return [(cx - bw, base_y), (cx, tip_y), (cx + bw, base_y)], bw


def _curved_body(cx, tip_y, base_y, hw, *, bow=0.30, edge=1.0):
    """A single-edged CURVED (saber/falchion) silhouette: the back spine bows
    one way, the cutting edge swells then sweeps to the same hard tip. `bow` is
    the sideways curve of the tip; `edge` swells the belly. Returns (pts, bw)."""
    span = base_y - tip_y
    bw = hw
    spine, edgep = [], []
    n = 14
    for i in range(n + 1):
        t = i / n                       # 0 at base, 1 at tip
        y = base_y - span * t
        arc = math.sin(t * math.pi)     # 0 at ends, 1 mid
        cxt = cx + bow * hw * (t ** 1.3)   # whole blade leans toward the tip side
        bwt = hw * (1.0 - t * 0.92) + edge * hw * 0.5 * arc * (1 - t * 0.4)
        spine.append((cxt - bw * 0.32 - bwt * 0.18, y))   # back (spine) side
        edgep.append((cxt + bwt, y))                      # cutting (belly) side
    tip = (cx + bow * hw, tip_y)
    pts = spine + [tip] + list(reversed(edgep))
    return pts, bw


# ════════════════════════════════════════════════════════════════════════════
#  CARTOON REGISTER (tied to Plum & Lime) — 4 weapons
# ════════════════════════════════════════════════════════════════════════════

# ---- 1. Candy-Twist Cutlass -------------------------------------------------
# A fat curved TOON blade, a spiral red/cream barber-pole candy grip, a big
# round candy pommel, a curled-S brass guard. The grip + pommel are pure candy.
CANDY_RED = (214, 54, 64)
CANDY_RED_DK = (150, 28, 38)
CANDY_CREAM = (255, 244, 226)
# Toon steel keyed DARK at the core so the blade BODY clears the ~173 day sky
# (GATE 2) — the bright sheen lives only as a thin top-lit band + the fuller, so
# the body still reads as playful polished steel without washing out on blue.
TOON_STEEL_HI = (150, 170, 200)
TOON_STEEL_MD = (96, 116, 146)
TOON_STEEL_LO = (40, 54, 78)
BRASS = (236, 188, 86)
BRASS_DK = (170, 120, 40)


def sword_01(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.12)
    ghw = _guard_hw(ss)
    # A fat curved toon cutlass blade — bellied single edge to a hard tip.
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.34, edge=0.55)
    _vgrad_poly(surf, body, TOON_STEEL_HI, TOON_STEEL_LO, outline=(30, 40, 58),
                ow=max(2, int(2.2 * ss)))
    # One bold dark fuller groove following the curve (the single body accent).
    span = base_y - tip_y
    fuller = [(cx + 0.34 * hw * (t ** 1.3) - hw * 0.05, base_y - span * t)
              for t in (0.08, 0.4, 0.72, 0.92)]
    pygame.draw.lines(surf, TOON_STEEL_MD, False, fuller, max(2, int(2.2 * ss)))
    # Curled-S brass guard (a fat cartoon swoop, knobbed ends).
    _crossguard(surf, cx, gy, ghw, int(13 * ss), BRASS, ss, curve=int(7 * ss),
                dk=BRASS_DK, quillon_r=0.7)
    pygame.draw.arc(surf, BRASS, (int(cx - ghw), int(gy - 4 * ss),
                                  int(ghw * 1.1), int(20 * ss)),
                    math.pi * 0.1, math.pi * 0.9, max(2, int(3 * ss)))
    # Spiral red/cream BARBER-POLE candy grip.
    _candy_twist(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.42),
                 CANDY_RED, CANDY_CREAM, ss)
    # Big round glossy CANDY pommel (a peppermint swirl).
    pr = int(hw * 0.52)
    _ball_pommel(surf, cx, py, pr, CANDY_CREAM, ss, dk=CANDY_RED_DK, glossy=True)
    for k in range(5):
        a = k * math.tau / 5 - math.pi / 2
        pygame.draw.line(surf, CANDY_RED, (cx, py),
                         (cx + math.cos(a) * pr * 0.8, py + math.sin(a) * pr * 0.8),
                         max(2, int(2.2 * ss)))


# ---- 2. Jester-Bell Sabre ---------------------------------------------------
# A playful curved sabre whose GUARD is a row of gold jester bells; a lime
# tassel hangs off the pommel, the grip is plum-wrapped. Pure clown costume.
def sword_02(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.0)
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.26, edge=0.30)
    _vgrad_poly(surf, body, (150, 168, 196), (48, 64, 92), outline=(28, 38, 56),
                ow=max(2, int(2.0 * ss)))
    # Lit cutting edge sweeping to the hard tip (the bright back-edge beat) — kept
    # as a THIN bright sliver so the body luma stays dark on day-blue (GATE 2).
    span = base_y - tip_y
    edge = [(cx + 0.26 * hw * (t ** 1.3) + hw * (1.0 - t * 0.9), base_y - span * t)
            for t in (0.05, 0.4, 0.7, 0.95)]
    pygame.draw.lines(surf, (224, 234, 246), False, edge, max(1, int(1.6 * ss)))
    # GUARD = a row of gold jester BELLS strung across the crossguard.
    nb = 5
    pygame.draw.line(surf, GOLD_DK, (cx - ghw, gy), (cx + ghw, gy), max(2, int(3 * ss)))
    for i in range(nb):
        t = (i + 0.5) / nb
        bx = cx - ghw + 2 * ghw * t
        br = int(7 * ss)
        pygame.draw.circle(surf, GOLD_DK, (int(bx), int(gy + 3 * ss)), br + 1)
        pygame.draw.circle(surf, GOLD, (int(bx), int(gy + 3 * ss)), br)
        pygame.draw.circle(surf, GOLD_HI, (int(bx - br * 0.3), int(gy + 3 * ss - br * 0.3)),
                           max(1, int(br * 0.4)))
        pygame.draw.line(surf, GOLD_DK, (int(bx - br * 0.5), int(gy + 6 * ss)),
                         (int(bx + br * 0.5), int(gy + 6 * ss)), max(1, int(ss)))
    # Plum-wrapped grip.
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.38), PLUM, ss, diag=True)
    # Gold ball pommel with a LIME tassel hanging off it.
    pr = int(hw * 0.42)
    _ball_pommel(surf, cx, py, pr, GOLD, ss, dk=GOLD_DK)
    for k in (-1, 0, 1):
        tx = cx + k * int(4 * ss)
        pygame.draw.line(surf, LIME, (tx, py + pr), (tx + k * int(2 * ss), py + pr + int(16 * ss)),
                         max(2, int(2.4 * ss)))
    pygame.draw.circle(surf, LIME_DK, (cx, int(py + pr + 16 * ss)), int(5 * ss))
    pygame.draw.circle(surf, LIME, (cx, int(py + pr + 15 * ss)), int(4 * ss))


# ---- 3. Balloon-Pommel Shortsword -------------------------------------------
# A chunky toon shortsword: a short broad straight blade, a HUGE glossy balloon-
# round pommel (a clown's balloon), a gloved-friendly fat plum grip, lime guard.
def sword_03(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.16)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.06)
    _vgrad_poly(surf, body, (148, 166, 194), (46, 62, 90), outline=(26, 38, 56),
                ow=max(2, int(2.4 * ss)))
    # One NARROW bright centre stripe to a hard apex (chunky toon read) — kept
    # slim so most of the body stays dark against the day sky (GATE 2).
    pygame.draw.polygon(surf, (224, 234, 246),
                        [(cx - bwid * 0.12, base_y - int(6 * ss)),
                         (cx, tip_y + int(12 * ss)),
                         (cx + bwid * 0.12, base_y - int(6 * ss))])
    # A fat rounded LIME guard (a soft toon crossbar, balloon-knot ends).
    pygame.draw.rect(surf, LIME, (int(cx - ghw), int(gy - 8 * ss),
                                  int(ghw * 2), int(16 * ss)),
                     border_radius=int(8 * ss))
    pygame.draw.rect(surf, LIME_DK, (int(cx - ghw), int(gy - 8 * ss),
                                     int(ghw * 2), int(16 * ss)),
                     max(2, int(2 * ss)), border_radius=int(8 * ss))
    pygame.draw.line(surf, _shade_c(LIME, 40), (int(cx - ghw + 4 * ss), int(gy - 5 * ss)),
                     (int(cx + ghw - 4 * ss), int(gy - 5 * ss)), max(1, int(2 * ss)))
    # Fat plum gloved-friendly grip.
    _wrap_grip(surf, cx, gy + int(10 * ss), gbot - int(2 * ss), int(hw * 0.46), PLUM, ss)
    # HUGE glossy BALLOON pommel — the hero feature, with a tied knot beneath.
    pr = int(hw * 0.78)
    bcy = int(py + pr * 0.2)
    pygame.draw.circle(surf, _shade_c(CANDY_RED, -40), (cx, bcy), pr + int(ss))
    pygame.draw.circle(surf, CANDY_RED, (cx, bcy), pr)
    _glow_disc(surf, cx - pr * 0.3, bcy - pr * 0.3, int(pr * 0.7), (255, 220, 200),
               ss, alpha=90)
    pygame.draw.circle(surf, (255, 245, 240), (int(cx - pr * 0.34), int(bcy - pr * 0.38)),
                       max(2, int(pr * 0.24)))
    pygame.draw.polygon(surf, CANDY_RED_DK,
                        [(cx - int(4 * ss), bcy + pr - int(2 * ss)),
                         (cx + int(4 * ss), bcy + pr - int(2 * ss)),
                         (cx, bcy + pr + int(6 * ss))])


# ---- 4. Foam-Wobble Greatsword ----------------------------------------------
# An oversized SOFT wobbly cartoon greatsword: a bouncy bulged blade with rounded
# wobble edges, a plum-wrapped two-hand grip, lime ric-rac guard, gold gem
# pommel. Bouncy proportions, the playful "big foam prop" sword.
def sword_04(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss, hilt_px=150)
    hw = int(_blade_hw(ss) * 1.18)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # A WOBBLY bulged blade: edges bow out then pinch, ending in a soft-but-
    # pointed tip. Built as a smooth wavy silhouette (kept low-frequency so it
    # reads as ONE bouncy shape, not fizz).
    left, right = [], []
    n = 12
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        wob = math.sin(t * math.pi * 1.5) * 0.16
        w = hw * (1.0 - t * 0.86) * (1.0 + wob)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + [(cx, tip_y)] + list(reversed(right))
    _vgrad_poly(surf, body, (150, 168, 196), (52, 70, 100), outline=(30, 44, 64),
                ow=max(3, int(3.0 * ss)))
    # One NARROW soft highlight riding the upper blade (the foam-prop sheen) —
    # slim so the body luma stays dark on day-blue (GATE 2).
    pygame.draw.polygon(surf, (228, 238, 248),
                        [(cx - hw * 0.1, base_y - span * 0.35),
                         (cx, tip_y + int(16 * ss)),
                         (cx + hw * 0.1, base_y - span * 0.35)])
    # Lime ric-rac (wavy) guard — a soft scalloped crossbar.
    gy0 = gy
    pts_t, pts_b = [], []
    for i in range(9):
        t = i / 8
        x = cx - ghw + 2 * ghw * t
        yy = gy0 + math.sin(t * math.pi * 4) * int(4 * ss)
        pts_t.append((x, yy - int(7 * ss)))
        pts_b.append((x, yy + int(7 * ss)))
    pygame.draw.polygon(surf, LIME, pts_t + list(reversed(pts_b)))
    pygame.draw.polygon(surf, LIME_DK, pts_t + list(reversed(pts_b)), max(2, int(2 * ss)))
    # Plum two-hand wrapped grip (longer).
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.40), PLUM, ss, diag=True)
    # Gold faceted-gem pommel.
    _ball_pommel(surf, cx, py, int(hw * 0.5), GOLD, ss, dk=GOLD_DK)
    _facet_gem(surf, cx, py, int(hw * 0.26), CANDY_RED, (255, 150, 150),
               CANDY_RED_DK, ss)


# ════════════════════════════════════════════════════════════════════════════
#  REALISTIC REGISTER — 4 DIFFERENT forged sword families
# ════════════════════════════════════════════════════════════════════════════

# ---- 5. Cleaver Falchion ----------------------------------------------------
# A broad single-edge FALCHION: a heavy clip-point chopping blade, a simple iron
# cross, a plain leather grip, a flat iron DISC pommel. Honest working steel.
def sword_05(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.14)
    ghw = int(_guard_hw(ss) * 0.86)
    span = base_y - tip_y
    # Broad falchion: a near-straight back spine, a belly that swells toward the
    # tip then clips back to a hard point (the cleaver profile).
    spine, belly = [], []
    n = 12
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        # belly swells in the lower-mid, clips in near the tip
        bell = hw * (0.70 + 0.55 * math.sin(min(1, t * 1.15) * math.pi * 0.8))
        bell *= (1.0 - max(0, t - 0.78) * 3.2)
        spine.append((cx - hw * 0.48, y))
        belly.append((cx + max(0, bell), y))
    tip = (cx - hw * 0.10, tip_y)
    body = spine + [tip] + list(reversed(belly))
    _vgrad_poly(surf, body, STEEL_HI, STEEL_DK, outline=(26, 30, 38),
                ow=max(2, int(2.0 * ss)))
    # One bold fuller line near the spine + a lit back-edge (2 bold beats).
    pygame.draw.line(surf, STEEL_MD, (cx - hw * 0.30, base_y - int(8 * ss)),
                     (cx - hw * 0.18, tip_y + int(span * 0.22)), max(2, int(2.2 * ss)))
    pygame.draw.line(surf, (220, 228, 240), (cx - hw * 0.48, base_y),
                     (cx - hw * 0.10, tip_y + int(4 * ss)), max(2, int(2.0 * ss)))
    # Simple straight iron cross.
    _crossguard(surf, cx, gy, ghw, int(10 * ss), IRON_MD, ss, dk=IRON_DK,
                quillon_r=0.35)
    # Plain leather grip.
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.36), LEATHER, ss)
    # Flat iron DISC pommel.
    _disc_pommel(surf, cx, py, int(hw * 0.46), IRON_MD, ss, dk=IRON_DK)


# ---- 6. Basket-Hilt Saber ---------------------------------------------------
# A curved cavalry SABER with a woven steel BASKET guard wrapping the hand, a
# wire-RIBBED grip, a teardrop steel pommel. The guard is the signature.
def sword_06(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 0.92)
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.30, edge=0.18)
    _vgrad_poly(surf, body, STEEL_HI, STEEL_DK, outline=(26, 30, 38),
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    edge = [(cx + 0.30 * hw * (t ** 1.3) + hw * (1.0 - t * 0.9), base_y - span * t)
            for t in (0.05, 0.4, 0.7, 0.95)]
    pygame.draw.lines(surf, (224, 232, 244), False, edge, max(2, int(2.0 * ss)))
    # The woven steel BASKET guard: a domed cage of bold curved bars wrapping the
    # grip from the crossbar down to the pommel. Kept to a few BOLD ribs (de-noise).
    pygame.draw.line(surf, IRON_DK, (cx - ghw, gy), (cx + ghw, gy), max(2, int(3 * ss)))
    cage_top, cage_bot = gy - int(2 * ss), gbot
    for sgn in (-1, 1):
        outer = pygame.Rect(int(cx - ghw if sgn < 0 else cx),
                            int(cage_top), int(ghw), int(cage_bot - cage_top))
        for k, col in ((0, IRON_DK), (1, IRON_MD)):
            r = outer.inflate(-int(k * 3 * ss), -int(k * 3 * ss))
            pygame.draw.arc(surf, col, r,
                            (math.pi * 1.5 if sgn < 0 else math.pi),
                            (math.tau if sgn < 0 else math.pi * 1.5),
                            max(2, int(3 * ss - k * ss)))
        # Two cross-ribs spanning the cage so it reads woven, not a single hoop.
        for t in (0.34, 0.66):
            ay = cage_top + (cage_bot - cage_top) * t
            ax = cx + sgn * ghw * (1.0 - t * 0.5)
            pygame.draw.line(surf, IRON_MD, (cx, ay), (ax, ay - int(3 * ss)),
                             max(1, int(1.8 * ss)))
    # Wire-RIBBED grip behind the basket.
    _ribbed_grip(surf, cx, gy + int(6 * ss), gbot, int(hw * 0.30), STEEL_MD, ss)
    # Teardrop steel pommel cap.
    pr = int(hw * 0.40)
    pygame.draw.polygon(surf, IRON_DK,
                        [(cx, py - pr), (cx + pr, py + pr * 0.3), (cx, py + pr),
                         (cx - pr, py + pr * 0.3)])
    pygame.draw.polygon(surf, IRON_MD,
                        [(cx, py - pr + ss), (cx + pr - ss, py + pr * 0.3), (cx, py + pr - ss),
                         (cx - pr + ss, py + pr * 0.3)])
    pygame.draw.circle(surf, IRON_HI, (int(cx - pr * 0.3), int(py - pr * 0.2)),
                       max(1, int(pr * 0.24)))


# ---- 7. Leaf-Blade Shortsword -----------------------------------------------
# A bronze-age LEAF blade: a wide leaf-shaped silhouette swelling mid-blade to a
# point, a small flared bronze guard, a riveted bronze grip, a crescent pommel.
def sword_07(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)
    ghw = int(_guard_hw(ss) * 0.78)
    span = base_y - tip_y
    # Leaf silhouette: narrow at the base, swelling to a wide belly ~60% up, then
    # a graceful taper to a hard point.
    left, right = [], []
    n = 14
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        leaf = math.sin(min(1, t * 1.04) * math.pi) ** 0.7
        w = hw * (0.34 + 0.72 * leaf)
        left.append((cx - w, y))
        right.append((cx + w, y))
    body = left + [(cx, tip_y)] + list(reversed(right))
    # Tip-dark gradient so the gap-facing tip stays dark (GATE 1/2); the warm
    # bronze sheen lives on the raised midrib, not the broad body fill.
    _vgrad_poly(surf, body, BRONZE_LO, BRONZE_MD, outline=(48, 30, 14),
                ow=max(2, int(2.0 * ss)))
    # A bold raised midrib down the centre to a hard apex (the leaf's spine).
    pygame.draw.polygon(surf, BRONZE_HI,
                        [(cx - hw * 0.12, base_y), (cx, tip_y + int(6 * ss)),
                         (cx + hw * 0.12, base_y)])
    pygame.draw.line(surf, (230, 196, 120), (cx, base_y - int(8 * ss)),
                     (cx, tip_y + int(10 * ss)), max(1, int(1.4 * ss)))
    # Small flared bronze guard (a shallow crescent hugging the leaf base).
    pygame.draw.arc(surf, BRONZE_MD, (int(cx - ghw), int(gy - 9 * ss),
                                      int(ghw * 2), int(20 * ss)),
                    math.pi, math.tau, max(3, int(4 * ss)))
    pygame.draw.line(surf, BRONZE_LO, (cx - ghw, gy + int(2 * ss)),
                     (cx + ghw, gy + int(2 * ss)), max(2, int(2.4 * ss)))
    # Riveted bronze grip (two bold rivets).
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.34), BRONZE_LO, ss)
    for t in (0.3, 0.7):
        _rivet(surf, cx, gy + int(8 * ss) + (gbot - gy - int(8 * ss)) * t,
               int(hw * 0.14), BRONZE_HI)
    # Crescent bronze pommel cap.
    pr = int(hw * 0.44)
    pygame.draw.arc(surf, BRONZE_LO, (int(cx - pr), int(py - pr), int(pr * 2), int(pr * 2)),
                    math.pi * 0.1, math.pi * 0.9, max(3, int(5 * ss)))
    pygame.draw.circle(surf, BRONZE_MD, (cx, int(py - pr * 0.2)), int(pr * 0.5))
    pygame.draw.circle(surf, BRONZE_HI, (int(cx - pr * 0.2), int(py - pr * 0.4)),
                       max(1, int(pr * 0.22)))


# ---- 8. Two-Hand War-Blade --------------------------------------------------
# A long double-edge GREATSWORD: a long ricasso, parrying SIDE-RINGS above the
# guard, a long two-hand wrapped grip, a heavy pear pommel. Reads as the big
# longsword family, distinct from the other three.
def sword_08(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss, hilt_px=156)
    hw = int(_blade_hw(ss) * 0.96)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # Long slender double-edge blade with a long ricasso (parallel near the base).
    ric = base_y - int(span * 0.14)
    body = [(cx - hw, base_y), (cx - hw, ric),
            (cx - hw * 1.02, base_y - span * 0.5), (cx, tip_y),
            (cx + hw * 1.02, base_y - span * 0.5), (cx + hw, ric),
            (cx + hw, base_y)]
    _vgrad_poly(surf, body, STEEL_HI, STEEL_DK, outline=(24, 28, 36),
                ow=max(2, int(2.0 * ss)))
    # Long central fuller groove + bright edges (2 bold beats).
    pygame.draw.line(surf, STEEL_MD, (cx, ric - int(4 * ss)),
                     (cx, tip_y + int(span * 0.30)), max(2, int(2.4 * ss)))
    pygame.draw.line(surf, (220, 228, 240), (cx - hw, ric),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (220, 228, 240), (cx + hw, ric),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    # Parrying SIDE-RINGS above the straight guard (the longsword signature).
    for sgn in (-1, 1):
        rcx = cx + sgn * int(hw * 0.7)
        pygame.draw.circle(surf, IRON_DK, (rcx, gy - int(10 * ss)), int(8 * ss),
                           max(2, int(2.6 * ss)))
        pygame.draw.circle(surf, IRON_MD, (rcx, gy - int(10 * ss)), int(8 * ss),
                           max(1, int(1.4 * ss)))
    # Long straight steel cross.
    _crossguard(surf, cx, gy, ghw, int(9 * ss), IRON_MD, ss, dk=IRON_DK,
                quillon_r=0.4)
    # Long two-hand wrapped grip with a centre knot ring.
    _wrap_grip(surf, cx, gy + int(8 * ss), gbot, int(hw * 0.32), LEATHER_DK, ss, diag=True)
    midg = (gy + gbot) / 2
    pygame.draw.line(surf, IRON_MD, (cx - hw * 0.34, midg), (cx + hw * 0.34, midg),
                     max(2, int(2.4 * ss)))
    # Heavy pear pommel.
    pr = int(hw * 0.46)
    pygame.draw.polygon(surf, IRON_DK,
                        [(cx, py - pr * 1.1), (cx + pr, py), (cx, py + pr),
                         (cx - pr, py)])
    pygame.draw.polygon(surf, IRON_MD,
                        [(cx, py - pr * 1.1 + ss), (cx + pr - ss, py), (cx, py + pr - ss),
                         (cx - pr + ss, py)])
    pygame.draw.circle(surf, IRON_HI, (int(cx - pr * 0.3), int(py - pr * 0.3)),
                       max(1, int(pr * 0.24)))


# ════════════════════════════════════════════════════════════════════════════
#  FANTASY REGISTER — 4 dramatic hero/boss weapons
# ════════════════════════════════════════════════════════════════════════════

# ---- 9. Winged-Guard Relic --------------------------------------------------
# A gold hero relic: a gem-CORE blade, a swept golden WING crossguard (feathered
# wings sweeping up toward the blade), a CROWN pommel. Holy-loot.
GREL_LO = (70, 48, 16)
GREL_MD = (132, 100, 40)
GREL_HI = (224, 188, 96)
SAPPHIRE = (66, 120, 220)
SAPPHIRE_HI = (160, 200, 255)
SAPPHIRE_DK = (28, 56, 130)


def sword_09(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.03)
    _vgrad_poly(surf, body, GREL_HI, GREL_LO, outline=GOLD_SHADOW,
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    # A sapphire GEM-CORE channel running up the blade to a hard apex.
    pygame.draw.polygon(surf, SAPPHIRE_DK,
                        [(cx - bwid * 0.18, base_y - int(6 * ss)),
                         (cx, tip_y + int(14 * ss)),
                         (cx + bwid * 0.18, base_y - int(6 * ss))])
    pygame.draw.polygon(surf, SAPPHIRE,
                        [(cx - bwid * 0.1, base_y - int(8 * ss)),
                         (cx, tip_y + int(20 * ss)),
                         (cx + bwid * 0.1, base_y - int(8 * ss))])
    pygame.draw.line(surf, GOLD_HI, (cx - bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.6 * ss)))
    pygame.draw.line(surf, GOLD_HI, (cx + bwid, base_y), (cx, tip_y + int(4 * ss)),
                     max(1, int(1.6 * ss)))
    # Swept golden WING crossguard: two feathered wings sweeping UP toward the
    # blade. A few BOLD feather lobes per wing (de-noised), gold with dark keylines.
    for sgn in (-1, 1):
        base = (cx + sgn * int(8 * ss), gy + int(2 * ss))
        wing = [base,
                (cx + sgn * ghw * 0.55, gy - int(6 * ss)),
                (cx + sgn * ghw, gy - int(14 * ss)),
                (cx + sgn * ghw * 0.92, gy + int(2 * ss)),
                (cx + sgn * ghw * 0.6, gy + int(8 * ss)),
                (cx + sgn * int(8 * ss), gy + int(10 * ss))]
        pygame.draw.polygon(surf, GREL_MD, wing)
        pygame.draw.polygon(surf, GOLD_DK, wing, max(2, int(2 * ss)))
        for k in (0.45, 0.7, 0.92):
            fx = cx + sgn * ghw * k
            pygame.draw.line(surf, GOLD_HI, (fx, gy - int(2 * ss)),
                             (fx, gy - int(10 * ss) * (k)), max(1, int(1.6 * ss)))
    # Gold wrapped grip.
    _wrap_grip(surf, cx, gy + int(11 * ss), gbot, int(hw * 0.36), GREL_MD, ss)
    # CROWN pommel: a ring of gold points crowning the base, a gem set in front.
    pr = int(hw * 0.5)
    pygame.draw.circle(surf, GOLD_DK, (cx, py), pr)
    pygame.draw.circle(surf, GOLD, (cx, py), int(pr - ss))
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.5
        bx = cx + math.cos(a) * pr
        by2 = py + math.sin(a) * pr
        pygame.draw.polygon(surf, GOLD,
                            [(bx - int(3 * ss), by2), (bx + int(3 * ss), by2),
                             (bx + math.cos(a) * int(7 * ss),
                              by2 + math.sin(a) * int(7 * ss))])
        pygame.draw.polygon(surf, GOLD_DK,
                            [(bx - int(3 * ss), by2), (bx + int(3 * ss), by2),
                             (bx + math.cos(a) * int(7 * ss),
                              by2 + math.sin(a) * int(7 * ss))], max(1, int(ss)))
    _facet_gem(surf, cx, py + int(2 * ss), int(pr * 0.5), SAPPHIRE, SAPPHIRE_HI,
               SAPPHIRE_DK, ss)


# ---- 10. Rune Greatsword ----------------------------------------------------
# A dark forged greatsword with ONE bold glowing RUNE in the fuller, an angular
# anvil guard, a charcoal ribbed grip, a faceted gem pommel. Brooding boss steel.
RUNE_BODY_HI = (78, 84, 102)
RUNE_BODY_LO = (26, 28, 38)
RUNE_GLOW = (120, 220, 255)
RUNE_HOT = (220, 248, 255)


def sword_10(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss, hilt_px=148)
    hw = int(_blade_hw(ss) * 1.08)
    ghw = _guard_hw(ss)
    body, bwid = _straight_body(cx, tip_y, base_y, hw, taper=0.04)
    _vgrad_poly(surf, body, RUNE_BODY_HI, RUNE_BODY_LO, outline=(12, 14, 20),
                ow=max(2, int(2.2 * ss)))
    span = base_y - tip_y
    # ONE bold glowing rune locked to the lower-mid fuller (a chevron + bar).
    ry = base_y - int(span * 0.34)
    rw = bwid * (1.0 - (ry - tip_y) / span) * 0.5
    glyph = [(cx - rw, ry - int(9 * ss)), (cx, ry - int(1 * ss)),
             (cx + rw, ry - int(9 * ss))]
    _edge_glow(surf, glyph, RUNE_GLOW, ss, alpha=180, spread=6)
    pygame.draw.lines(surf, RUNE_HOT, False, glyph, max(2, int(2.4 * ss)))
    _edge_glow(surf, [(cx, ry - int(2 * ss)), (cx, ry + int(10 * ss))], RUNE_GLOW,
               ss, alpha=160, spread=5)
    pygame.draw.line(surf, RUNE_HOT, (cx, ry - int(2 * ss)), (cx, ry + int(10 * ss)),
                     max(2, int(2.2 * ss)))
    # A thin cool edge-light to a hard apex.
    pygame.draw.line(surf, (150, 170, 200), (cx - bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    pygame.draw.line(surf, (150, 170, 200), (cx + bwid, base_y),
                     (cx, tip_y + int(4 * ss)), max(1, int(1.6 * ss)))
    # Angular ANVIL guard: a hard chevron block with down-swept tips.
    guard = [(cx - ghw, gy - int(2 * ss)), (cx + ghw, gy - int(2 * ss)),
             (cx + ghw * 0.6, gy + int(13 * ss)), (cx + int(5 * ss), gy + int(6 * ss)),
             (cx - int(5 * ss), gy + int(6 * ss)), (cx - ghw * 0.6, gy + int(13 * ss))]
    pygame.draw.polygon(surf, (54, 58, 70), guard)
    pygame.draw.polygon(surf, (16, 18, 26), guard, max(2, int(2.2 * ss)))
    pygame.draw.line(surf, (96, 102, 120), (cx - ghw + int(3 * ss), gy),
                     (cx + ghw - int(3 * ss), gy), max(1, int(1.8 * ss)))
    # Charcoal ribbed grip.
    _ribbed_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (44, 46, 58), ss)
    # Faceted glowing gem pommel.
    pr = int(hw * 0.46)
    pygame.draw.polygon(surf, (20, 22, 30),
                        [(cx, py - pr), (cx + pr, py), (cx, py + pr), (cx - pr, py)])
    _facet_gem(surf, cx, py, int(pr * 0.6), RUNE_GLOW, RUNE_HOT, (30, 80, 110), ss)


# ---- 11. Crystal Saber ------------------------------------------------------
# An opaque dark-CRYSTAL curved saber: a faceted amethyst blade, a JAGGED raw
# natural-crystal guard, a candy-twist-free shard grip, a raw-gem cluster pommel.
XTAL_CORE = (34, 22, 56)
XTAL_A = (120, 70, 200)
XTAL_B = (78, 48, 150)
XTAL_HI = (210, 180, 255)
XTAL_DK = (18, 12, 32)


def sword_11(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.04)
    ghw = _guard_hw(ss)
    body, bwid = _curved_body(cx, tip_y, base_y, hw, bow=0.22, edge=0.22)
    _vgrad_poly(surf, body, XTAL_A, XTAL_CORE, outline=XTAL_DK,
                ow=max(2, int(2.0 * ss)))
    span = base_y - tip_y
    # Big angular crystal facets stacked up the blade (alternating two tones).
    cuts = [0.0, 0.34, 0.62, 1.0]
    tones = [XTAL_B, XTAL_A, XTAL_B]
    for i in range(len(cuts) - 1):
        y0 = base_y - span * cuts[i]
        y1 = base_y - span * cuts[i + 1]
        cx0 = cx + 0.22 * hw * (cuts[i] ** 1.3)
        cx1 = cx + 0.22 * hw * (cuts[i + 1] ** 1.3)
        w0 = hw * (1.0 - cuts[i] * 0.9)
        w1 = hw * (1.0 - cuts[i + 1] * 0.9)
        pygame.draw.polygon(surf, _shade_c(tones[i], -24),
                            [(cx0 - w0 * 0.4, y0), (cx0 + w0, y0),
                             (cx1 + w1, y1), (cx1 - w1 * 0.4, y1)])
        pygame.draw.line(surf, XTAL_HI, (cx0 - w0 * 0.4, y0), (cx1 - w1 * 0.4, y1),
                         max(1, int(1.6 * ss)))
    # A bright crystalline ridge to a hard apex.
    pygame.draw.line(surf, (255, 255, 255), (cx + 0.22 * hw, tip_y + int(3 * ss)),
                     (cx + hw * 0.1, base_y - int(8 * ss)), max(2, int(2.0 * ss)))
    # JAGGED raw-crystal guard: a cluster of angular shards instead of a bar.
    for sgn in (-1, 1):
        shard = [(cx + sgn * int(6 * ss), gy + int(8 * ss)),
                 (cx + sgn * ghw * 0.5, gy - int(6 * ss)),
                 (cx + sgn * ghw, gy + int(2 * ss)),
                 (cx + sgn * ghw * 0.7, gy + int(12 * ss))]
        pygame.draw.polygon(surf, XTAL_B, shard)
        pygame.draw.polygon(surf, XTAL_DK, shard, max(2, int(2 * ss)))
        pygame.draw.line(surf, XTAL_HI, (cx + sgn * ghw * 0.5, gy - int(6 * ss)),
                         (cx + sgn * ghw * 0.6, gy + int(10 * ss)), max(1, int(1.6 * ss)))
    # Dark shard grip.
    _wrap_grip(surf, cx, gy + int(12 * ss), gbot, int(hw * 0.32), (40, 28, 60), ss)
    # Raw-gem cluster pommel.
    pr = int(hw * 0.46)
    _glow_disc(surf, cx, py, int(pr * 1.1), XTAL_A, ss, alpha=110)
    for (dx, dy, rr) in ((0, 0, 0.9), (-0.5, 0.3, 0.5), (0.5, 0.35, 0.5),
                         (0, -0.5, 0.45)):
        gx, gy2 = cx + dx * pr, py + dy * pr
        pygame.draw.polygon(surf, XTAL_A,
                            [(gx, gy2 - pr * rr), (gx + pr * rr * 0.7, gy2),
                             (gx, gy2 + pr * rr), (gx - pr * rr * 0.7, gy2)])
        pygame.draw.polygon(surf, XTAL_DK,
                            [(gx, gy2 - pr * rr), (gx + pr * rr * 0.7, gy2),
                             (gx, gy2 + pr * rr), (gx - pr * rr * 0.7, gy2)],
                            max(1, int(1.4 * ss)))
    pygame.draw.circle(surf, (255, 255, 255), (int(cx - pr * 0.2), int(py - pr * 0.2)),
                       max(1, int(pr * 0.18)))


# ---- 12. Bone / Demon Blade -------------------------------------------------
# A carved BONE blade with a fanged DEMON-SKULL guard, a VERTEBRA grip, a HORNED
# skull pommel. The monstrous boss weapon — pure bone, no metal.
# Bone keyed so the blade BODY (the lower core of the gradient) sits dark on
# day-blue (GATE 2); the pale ivory lives on the spine highlight + the skull/grip
# furniture, not the broad blade fill.
DEMON_BONE_HI = (172, 162, 134)
DEMON_BONE_LO = (74, 66, 48)
DEMON_BONE_KEY = (40, 34, 24)
DEMON_RED = (200, 40, 44)
DEMON_HOT = (255, 120, 80)


def sword_12(surf, bw, bh, ss):
    cx = bw // 2
    tip_y, base_y, gy, gtop, gbot, py = _layout(bh, ss)
    hw = int(_blade_hw(ss) * 1.06)
    ghw = _guard_hw(ss)
    span = base_y - tip_y
    # Carved bone blade: a serrated/clawed single-edge silhouette to a hard hook
    # point — but kept BOLD (few big serrations) so it doesn't fizz at route scale.
    back, edge = [], []
    n = 6
    for i in range(n + 1):
        t = i / n
        y = base_y - span * t
        back.append((cx - hw * (0.5 - t * 0.4), y))
    # a few big claw serrations on the cutting edge
    serr = [(cx + hw, base_y), (cx + hw * 0.9, base_y - span * 0.18),
            (cx + hw * 1.0, base_y - span * 0.30), (cx + hw * 0.7, base_y - span * 0.46),
            (cx + hw * 0.82, base_y - span * 0.58), (cx + hw * 0.5, base_y - span * 0.74),
            (cx + hw * 0.55, base_y - span * 0.84)]
    body = back + [(cx + hw * 0.1, tip_y)] + list(reversed(serr))
    # Tip-dark gradient: the gap-facing tip end is the DARK key so the dark-body→
    # bright-gap break stays hard (GATE 1) and the body luma clears day-blue.
    _vgrad_poly(surf, body, DEMON_BONE_LO, DEMON_BONE_HI, outline=DEMON_BONE_KEY,
                ow=max(2, int(2.2 * ss)))
    # A dark marrow groove down the bone (the single bold body accent).
    pygame.draw.line(surf, DEMON_BONE_KEY, (cx - hw * 0.05, base_y - int(8 * ss)),
                     (cx + hw * 0.06, tip_y + int(span * 0.2)), max(2, int(2.4 * ss)))
    # A THIN ivory back-spine sliver (kept slim so the body stays dark on blue).
    pygame.draw.line(surf, (224, 216, 192), (cx - hw * 0.5, base_y),
                     (cx + hw * 0.1, tip_y + int(4 * ss)), max(1, int(1.4 * ss)))
    # Fanged DEMON-SKULL guard: a wide bone skull the blade erupts from, two glowing
    # eyes, a row of big fangs, swept horns at the ends.
    sk_w = ghw
    sk_h = int(20 * ss)
    skull = [(cx - sk_w, gy - int(2 * ss)), (cx - sk_w * 0.5, gy - sk_h * 0.7),
             (cx + sk_w * 0.5, gy - sk_h * 0.7), (cx + sk_w, gy - int(2 * ss)),
             (cx + sk_w * 0.6, gy + sk_h * 0.7), (cx - sk_w * 0.6, gy + sk_h * 0.7)]
    pygame.draw.polygon(surf, DEMON_BONE_HI, skull)
    pygame.draw.polygon(surf, DEMON_BONE_KEY, skull, max(2, int(2.2 * ss)))
    # Swept horns at the guard ends.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, DEMON_BONE_LO,
                            [(cx + sgn * sk_w * 0.9, gy - int(2 * ss)),
                             (cx + sgn * sk_w * 1.05, gy - int(14 * ss)),
                             (cx + sgn * sk_w * 0.7, gy - int(4 * ss))])
        pygame.draw.polygon(surf, DEMON_BONE_KEY,
                            [(cx + sgn * sk_w * 0.9, gy - int(2 * ss)),
                             (cx + sgn * sk_w * 1.05, gy - int(14 * ss)),
                             (cx + sgn * sk_w * 0.7, gy - int(4 * ss))], max(1, int(ss)))
    # Glowing eyes.
    for sgn in (-1, 1):
        ex = cx + sgn * sk_w * 0.38
        _glow_disc(surf, ex, gy - int(2 * ss), int(5 * ss), DEMON_HOT, ss, alpha=150)
        pygame.draw.circle(surf, DEMON_RED, (int(ex), int(gy - 2 * ss)), int(4 * ss))
        pygame.draw.circle(surf, (20, 8, 8), (int(ex), int(gy - 2 * ss)), int(2 * ss))
    # A row of big fangs across the jaw.
    for i in range(4):
        t = (i + 0.5) / 4
        fx = cx - sk_w * 0.55 + sk_w * 1.1 * t
        pygame.draw.polygon(surf, (250, 244, 224),
                            [(fx - int(4 * ss), gy + sk_h * 0.4),
                             (fx + int(4 * ss), gy + sk_h * 0.4),
                             (fx, gy + sk_h * 0.4 + int(10 * ss))])
    # VERTEBRA grip (stacked bone segments).
    _bone_grip(surf, cx, gy + int(sk_h * 0.7), gbot, int(hw * 0.34), ss, vertebra=True)
    # HORNED skull pommel.
    pr = int(hw * 0.5)
    pygame.draw.circle(surf, DEMON_BONE_LO, (cx, py), pr)
    pygame.draw.circle(surf, DEMON_BONE_HI, (cx, int(py - ss)), int(pr - ss))
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, DEMON_BONE_LO,
                            [(cx + sgn * pr * 0.7, py - pr * 0.4),
                             (cx + sgn * pr * 1.3, py - pr * 1.0),
                             (cx + sgn * pr * 0.85, py - pr * 0.1)])
        pygame.draw.polygon(surf, DEMON_BONE_KEY,
                            [(cx + sgn * pr * 0.7, py - pr * 0.4),
                             (cx + sgn * pr * 1.3, py - pr * 1.0),
                             (cx + sgn * pr * 0.85, py - pr * 0.1)], max(1, int(ss)))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, (20, 8, 8), (int(cx + sgn * pr * 0.4), int(py)),
                           max(2, int(pr * 0.22)))
    pygame.draw.polygon(surf, (20, 8, 8),
                        [(cx, py + pr * 0.3), (cx + int(3 * ss), py + pr * 0.7),
                         (cx - int(3 * ss), py + pr * 0.7)])


# ════════════════════════════════════════════════════════════════════════════
#  BROADENED ROUND-6 PROPS — STAFFS · CLOWN PROPS · MYSTIC
#  Every prop is authored TIP/FINIAL-UP in the box (gap-facing end at y=0, the
#  bottom resting end at the box bottom) so the existing route flip scaffolding
#  plants it point-UP from the ground and point-DOWN from the ceiling unchanged.
#  Bodies are keyed DARK (median luma < ~140 on the ~190 day sky): the shaft fill
#  is a dark core with only a SLIM lit rail, and finials carry the value break.
# ════════════════════════════════════════════════════════════════════════════

# Dark woods / staves that always hold value on day-blue.
WOOD_HI = (120, 92, 58)
WOOD_MD = (84, 62, 38)
WOOD_LO = (48, 34, 20)
WOOD_KEY = (30, 20, 12)
ROD_HI = (150, 158, 172)
ROD_MD = (78, 84, 96)
ROD_LO = (40, 44, 52)


def _shaft(surf, cx, top_y, bot_y, hw, ss, hi, md, lo, *, gnarl=0.0, key=None):
    """A vertical staff/cane SHAFT as a dark volume: a `lo`→`md` body gradient
    with a single SLIM lit rail down the lit side, so the body stays dark on the
    day sky while still reading round. `gnarl` waggles the silhouette into a
    knobbed wizard rod; 0 keeps it a clean straight cane."""
    key = key or _shade_c(lo, -40)
    span = max(1, bot_y - top_y)
    left, right = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        y = top_y + span * t
        wob = math.sin(t * math.pi * 3.0) * gnarl * hw
        left.append((cx - hw + wob, y))
        right.append((cx + hw + wob, y))
    body = left + list(reversed(right))
    _vgrad_poly(surf, body, md, lo, outline=key, ow=max(2, int(2.0 * ss)))
    # One slim lit rail down the lit (left) side — kept thin so the body luma
    # stays dark on day-blue.
    rail = [(p[0] + hw * 0.32, p[1]) for p in left]
    pygame.draw.lines(surf, hi, False, rail, max(1, int(1.6 * ss)))


def _bind_rings(surf, cx, ys, hw, ss, col):
    """A couple of bold binding rings around a shaft (a 2-3 bold-element accent)."""
    for y in ys:
        pygame.draw.line(surf, _shade_c(col, -40), (cx - hw - int(1.5 * ss), y),
                         (cx + hw + int(1.5 * ss), y), max(2, int(3 * ss)))
        pygame.draw.line(surf, _shade_c(col, 30), (cx - hw, y - int(ss)),
                         (cx + hw, y - int(ss)), max(1, int(1.4 * ss)))


# ════════════════════════════════════════════════════════════════════════════
#  FAMILY B — STAFFS & SCEPTERS (gap-facing FINIAL at box top)
# ════════════════════════════════════════════════════════════════════════════

# ---- 13. Wizard Orb Staff ---------------------------------------------------
# A gnarled dark rod with a glowing crystal ORB clutched in a claw finial. The
# orb's hard rim is the gap terminus: a dark claw frames a bright cyan core so
# the blunt round top still reads as a clean, contrast-y gap end.
ORB_CORE = (40, 120, 150)
ORB_GLOW = (120, 226, 245)
ORB_HOT = (224, 250, 255)


def prop_13(surf, bw, bh, ss):
    cx = bw // 2
    finial_r = int(15 * ss)
    fy = finial_r + int(8 * ss)            # orb centre sits just below the top
    shaft_top = fy + int(finial_r * 0.4)
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(7 * ss), ss,
           WOOD_HI, WOOD_MD, WOOD_LO, gnarl=0.10)
    _bind_rings(surf, cx, [bh * 0.55, bh * 0.8], int(7.5 * ss), ss, GOLD_DK)
    # Dark claw prongs clutching the orb (the value-break frame around the blunt
    # round top so the gap stays readable).
    for sgn in (-1, 0, 1):
        bx = cx + sgn * finial_r * 0.7
        prong = [(cx + sgn * int(3 * ss), shaft_top + int(2 * ss)),
                 (bx, fy + finial_r * 0.2),
                 (bx + sgn * int(4 * ss), fy - finial_r * 0.5)]
        pygame.draw.lines(surf, WOOD_LO, False, prong, max(3, int(4 * ss)))
        pygame.draw.lines(surf, WOOD_KEY, False, prong, max(1, int(1.4 * ss)))
    # The glowing orb finial — a dark rim, a saturated core, a hot glint.
    _glow_disc(surf, cx, fy, int(finial_r * 1.3), ORB_GLOW, ss, alpha=150)
    pygame.draw.circle(surf, (18, 36, 46), (cx, int(fy)), finial_r)
    pygame.draw.circle(surf, ORB_CORE, (cx, int(fy)), int(finial_r - ss))
    pygame.draw.circle(surf, ORB_GLOW, (cx, int(fy)), int(finial_r * 0.55))
    pygame.draw.circle(surf, ORB_HOT, (int(cx - finial_r * 0.3), int(fy - finial_r * 0.3)),
                       max(2, int(finial_r * 0.26)))


# ---- 14. Jester Marotte -----------------------------------------------------
# A fool's-head bauble SCEPTER: a plum rod topped by a tiny belled jester head
# (the fool's own face on a stick), the on-theme clown prop. The little head's
# pointed cap tips read as the gap terminus.
def prop_14(surf, bw, bh, ss):
    cx = bw // 2
    hr = int(13 * ss)
    hy = int(20 * ss)                      # tiny head centre
    shaft_top = hy + hr
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           _shade_c(PLUM, 40), PLUM, PLUM_DK)
    _bind_rings(surf, cx, [bh * 0.6], int(6.5 * ss), ss, GOLD_DK)
    # Two little belled cap points making the gap-facing terminus (pointed, so a
    # clean readable end), one plum one lime.
    for sgn, col in ((-1, PLUM_DK), (1, LIME_DK)):
        tip = (cx + sgn * int(12 * ss), int(3 * ss))
        pygame.draw.polygon(surf, col,
                            [(cx - int(4 * ss), hy - hr * 0.4),
                             (cx + int(4 * ss), hy - hr * 0.4), tip])
        pygame.draw.polygon(surf, _shade_c(col, -50),
                            [(cx - int(4 * ss), hy - hr * 0.4),
                             (cx + int(4 * ss), hy - hr * 0.4), tip], max(1, int(ss)))
        pygame.draw.circle(surf, GOLD, tip, max(2, int(3 * ss)))
        pygame.draw.circle(surf, GOLD_DK, tip, max(2, int(3 * ss)), max(1, int(ss)))
    # The tiny fool's head (cream face) — bold + simple so it reads at route scale.
    pygame.draw.circle(surf, _shade_c(CREAM, -50), (cx, int(hy)), hr)
    pygame.draw.circle(surf, CREAM, (cx, int(hy)), int(hr - ss))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, INK, (int(cx + sgn * hr * 0.4), int(hy - hr * 0.1)),
                           max(2, int(2.2 * ss)))
    pygame.draw.circle(surf, CANDY_RED, (cx, int(hy + hr * 0.2)), max(2, int(2.6 * ss)))
    pygame.draw.arc(surf, INK, (int(cx - hr * 0.5), int(hy + hr * 0.1),
                                int(hr), int(hr * 0.7)),
                    math.pi * 0.15, math.pi * 0.85, max(2, int(2 * ss)))


# ---- 15. Shepherd's Crook ---------------------------------------------------
# A long pale-wood crook whose hooked top is the gap terminus — the hook curls
# IN so the inner mouth of the hook reads as a clean dark-on-bright end.
CROOK_HI = (176, 150, 110)
CROOK_MD = (120, 96, 62)
CROOK_LO = (70, 54, 32)


def prop_15(surf, bw, bh, ss):
    cx = bw // 2
    hook_h = int(46 * ss)
    _shaft(surf, cx, hook_h, bh - int(4 * ss), int(6 * ss), ss,
           CROOK_HI, CROOK_MD, CROOK_LO)
    # The hook: a bold C curling from the shaft top up and back round. Drawn as a
    # thick dark arc with a slim lit inner rail so the hook reads as one bold
    # element, the curl mouth a clean terminus.
    hw = int(6 * ss)
    rad = int(16 * ss)
    cxh = cx + int(2 * ss)
    cyh = hook_h - int(4 * ss)
    rect = pygame.Rect(int(cxh - rad), int(cyh - rad), int(rad * 2), int(rad * 2))
    pygame.draw.arc(surf, CROOK_LO, rect, math.pi * 0.15, math.pi * 1.95, hw + int(2 * ss))
    pygame.draw.arc(surf, CROOK_MD, rect, math.pi * 0.15, math.pi * 1.95, hw)
    pygame.draw.arc(surf, CROOK_HI, rect.inflate(-int(3 * ss), -int(3 * ss)),
                    math.pi * 0.7, math.pi * 1.6, max(1, int(1.6 * ss)))
    # A bold leather binding band where hook meets shaft.
    _bind_rings(surf, cx, [hook_h + int(6 * ss), bh * 0.62], int(6.5 * ss), ss,
                LEATHER_DK)


# ---- 16. Skull-Topped Gold Rod ----------------------------------------------
# An ornate dark-gold scepter rod with a bone SKULL finial crowned by a faceted
# gem. The skull's domed cranium + the gem catch are the gap terminus.
def prop_16(surf, bw, bh, ss):
    cx = bw // 2
    sk_r = int(14 * ss)
    sy = int(20 * ss)
    shaft_top = sy + sk_r
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(6 * ss), ss,
           GOLD_DK, GOLD_SHADOW, _shade_c(GOLD_SHADOW, -30))
    _bind_rings(surf, cx, [bh * 0.5, bh * 0.78], int(6.5 * ss), ss, GOLD)
    # Collar of gold points beneath the skull.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, GOLD_DK,
                            [(cx + sgn * int(4 * ss), shaft_top + int(4 * ss)),
                             (cx + sgn * int(13 * ss), shaft_top + int(2 * ss)),
                             (cx + sgn * int(7 * ss), shaft_top - int(8 * ss))])
    # Bone skull finial — a domed cranium (clean rounded terminus), dark eye
    # sockets, a small jaw, crowned by a faceted gem catch for the hard value pop.
    pygame.draw.circle(surf, BONE_DK, (cx, int(sy)), sk_r)
    pygame.draw.circle(surf, BONE, (cx, int(sy - ss)), int(sk_r - ss))
    for sgn in (-1, 1):
        pygame.draw.circle(surf, (24, 18, 16), (int(cx + sgn * sk_r * 0.42), int(sy + ss)),
                           max(2, int(sk_r * 0.28)))
    pygame.draw.polygon(surf, (24, 18, 16),
                        [(cx, int(sy + sk_r * 0.45)),
                         (cx + int(3 * ss), int(sy + sk_r * 0.75)),
                         (cx - int(3 * ss), int(sy + sk_r * 0.75))])
    pygame.draw.rect(surf, BONE_DK, (int(cx - sk_r * 0.5), int(sy + sk_r * 0.7),
                                     int(sk_r), int(5 * ss)))
    _facet_gem(surf, cx, int(sy - sk_r * 0.65), int(5 * ss), CANDY_RED,
               (255, 150, 150), CANDY_RED_DK, ss)


# ════════════════════════════════════════════════════════════════════════════
#  FAMILY C — CLOWN PROPS (gap-facing end at box top)
# ════════════════════════════════════════════════════════════════════════════

# ---- 17. Candy Cane ---------------------------------------------------------
# A red/white spiral cane with the hooked top as the gap terminus. The stripes
# are kept BOLD (few fat diagonals) so they never fizz; the body reads dark via
# deep candy-red cores between the cream stripes + a dark keyline.
CANE_RED = (190, 40, 50)
CANE_RED_DK = (120, 22, 30)
CANE_CREAM = (244, 236, 220)


def _candy_band(surf, cx, top_y, bot_y, hw, ss, *, red=CANE_RED, cream=CANE_CREAM,
                vert=True):
    """A barber-pole striped column/segment kept DARK overall: deep-red cores
    with fewer, slimmer cream diagonals + a dark keyline, so the body luma stays
    under the day sky. Clipped to the column rect via a mask."""
    w = int(hw * 2)
    h = max(1, int(bot_y - top_y))
    seg = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    seg.fill(red + (255,))
    stripe = max(4, int(8 * ss))
    for i in range(-2, (w + h) // stripe + 3):
        x0 = i * stripe
        pygame.draw.polygon(seg, cream + (255,),
                            [(x0, 0), (x0 + stripe // 2, 0),
                             (x0 + stripe // 2 - h, h), (x0 - h, h)])
    # Re-darken the RGB only (NOT alpha — BLEND_RGB_SUB leaves the band fully
    # opaque) so the cream reads cooler/darker and the whole band median sits
    # below the day sky, while the column stays a solid dark obstacle.
    seg.fill((60, 60, 60), special_flags=pygame.BLEND_RGB_SUB)
    mask = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (1, 0, w, h),
                     border_radius=int(hw))
    seg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(seg, (int(cx - hw), int(top_y)))
    pygame.draw.rect(surf, CANE_RED_DK, (int(cx - hw), int(top_y), w, h),
                     max(1, int(1.6 * ss)), border_radius=int(hw))


def prop_17(surf, bw, bh, ss):
    cx = bw // 2
    hw = int(7 * ss)
    hook_h = int(40 * ss)
    rad = int(15 * ss)
    cxh = cx + int(2 * ss)
    cyh = hook_h - int(2 * ss)
    # Straight striped shaft.
    _candy_band(surf, cx, hook_h, bh - int(4 * ss), hw, ss)
    # Hooked top — a thick striped arc. Draw a dark base arc then a few bold
    # cream stripe ticks across it so the hook reads candy without fizz.
    rect = pygame.Rect(int(cxh - rad), int(cyh - rad), int(rad * 2), int(rad * 2))
    pygame.draw.arc(surf, CANE_RED_DK, rect, math.pi * 0.1, math.pi * 1.95,
                    int(hw * 2 + 2 * ss))
    pygame.draw.arc(surf, CANE_RED, rect, math.pi * 0.1, math.pi * 1.95, int(hw * 2))
    for k in range(7):
        a = math.pi * 0.2 + k * (math.pi * 1.6 / 6)
        x0 = cxh + math.cos(a) * (rad)
        y0 = cyh + math.sin(a) * (rad)
        pygame.draw.line(surf, CANE_CREAM,
                         (x0 + math.cos(a) * hw, y0 + math.sin(a) * hw),
                         (x0 - math.cos(a) * hw, y0 - math.sin(a) * hw),
                         max(2, int(2.6 * ss)))
    pygame.draw.arc(surf, CANE_RED_DK, rect, math.pi * 0.1, math.pi * 1.95,
                    max(1, int(1.6 * ss)))


# ---- 18. Giant Lollipop -----------------------------------------------------
# A big swirl DISC on a striped stick. A fat round top is the worst case for gap
# readability, so the disc is given a hard dark rim + a tight bright swirl core
# and the disc is kept NARROW enough (and dark-rimmed) that the sky-gap above its
# crown still reads as the brightest band.
LOLLI_A = (224, 96, 120)
LOLLI_B = (255, 232, 210)
LOLLI_RIM = (96, 30, 50)


def prop_18(surf, bw, bh, ss):
    cx = bw // 2
    disc_r = int(17 * ss)
    dy = disc_r + int(6 * ss)
    stick_top = dy + int(disc_r * 0.4)
    # A DARK candy-red stick (not a pale white one — a cream stick would wash on
    # the day sky, failing GATE 2), bound with cream rings for the candy read.
    _shaft(surf, cx, stick_top, bh - int(4 * ss), int(5 * ss), ss,
           CANE_RED, CANE_RED_DK, _shade_c(CANE_RED_DK, -30))
    _bind_rings(surf, cx, [bh * 0.5, bh * 0.72], int(5.5 * ss), ss, CANE_CREAM)
    # The swirl disc: a hard DARK rim (the value break that keeps the gap above it
    # reading), then a bold two-tone spiral kept LOW-frequency (a few fat arms).
    pygame.draw.circle(surf, LOLLI_RIM, (cx, int(dy)), disc_r + int(ss))
    pygame.draw.circle(surf, LOLLI_A, (cx, int(dy)), disc_r)
    arms = 5
    for k in range(arms):
        a0 = k * math.tau / arms
        pts = []
        for j in range(7):
            t = j / 6
            ang = a0 + t * 2.0
            rr = disc_r * t
            pts.append((cx + math.cos(ang) * rr, dy + math.sin(ang) * rr))
        pygame.draw.lines(surf, LOLLI_B, False, pts, max(2, int(3 * ss)))
    pygame.draw.circle(surf, LOLLI_RIM, (cx, int(dy)), disc_r, max(2, int(2.4 * ss)))
    pygame.draw.circle(surf, (255, 250, 244), (int(cx - disc_r * 0.35),
                                               int(dy - disc_r * 0.35)),
                       max(2, int(disc_r * 0.18)))


# ---- 19. Ringmaster Cane ----------------------------------------------------
# A black/gold show cane with a round gold KNOB top. The blunt knob is shaped
# with a hard dark underside + a tight specular so the gap still reads; a gold
# collar bands it.
CANE_BLACK = (34, 32, 40)
CANE_BLACK_HI = (78, 76, 88)


def prop_19(surf, bw, bh, ss):
    cx = bw // 2
    knob_r = int(11 * ss)
    ky = knob_r + int(6 * ss)
    shaft_top = ky + int(knob_r * 0.6)
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(5.5 * ss), ss,
           CANE_BLACK_HI, CANE_BLACK, _shade_c(CANE_BLACK, -18))
    # Gold bands striping the black cane (the bold show accent).
    for yt in (0.34, 0.55, 0.76):
        _bind_rings(surf, cx, [shaft_top + (bh - shaft_top) * yt], int(6 * ss), ss, GOLD)
    # Gold collar + round knob. A dark crescent across the knob's lower half is
    # the value break that keeps the gap above the knob reading bright.
    pygame.draw.rect(surf, GOLD_DK, (int(cx - knob_r * 0.7), int(shaft_top - 3 * ss),
                                     int(knob_r * 1.4), int(6 * ss)))
    pygame.draw.circle(surf, GOLD_DK, (cx, int(ky)), knob_r)
    pygame.draw.circle(surf, GOLD, (cx, int(ky - ss)), int(knob_r - ss))
    pygame.draw.circle(surf, GOLD_SHADOW, (cx, int(ky + knob_r * 0.35)),
                       int(knob_r * 0.7))
    pygame.draw.circle(surf, GOLD, (cx, int(ky - ss)), int(knob_r - ss),
                       max(1, int(ss)))
    pygame.draw.circle(surf, GOLD_HI, (int(cx - knob_r * 0.32), int(ky - knob_r * 0.34)),
                       max(2, int(knob_r * 0.26)))


# ---- 20. Furled Parasol -----------------------------------------------------
# A closed plum/lime parasol: a tight furled bundle tapering to a POINTED ferrule
# at the top — a clean sharp terminus — with a curved cane handle at the bottom.
def prop_20(surf, bw, bh, ss):
    cx = bw // 2
    tip_y = int(4 * ss)
    bundle_bot = bh - int(40 * ss)
    hw = int(9 * ss)
    # Furled bundle: a long dark taper from a pointed ferrule down to the handle,
    # built as a few bold vertical rib facets (plum / lime alternating, dark).
    ribs = 4
    for i in range(ribs):
        t0 = i / ribs - 0.5
        col = PLUM_DK if i % 2 == 0 else LIME_DK
        x0 = cx + t0 * hw * 1.8
        poly = [(cx, tip_y), (x0 + hw * 0.5, bundle_bot - int(6 * ss)),
                (x0 + hw * 0.5 + hw / ribs, bundle_bot - int(6 * ss))]
        pygame.draw.polygon(surf, col, poly)
    # Overlay a single bold dark spine + a slim lit edge so it reads as ONE furled
    # bundle, not stripes.
    spine = [(cx - hw, bundle_bot - int(6 * ss)), (cx, tip_y),
             (cx + hw, bundle_bot - int(6 * ss))]
    pygame.draw.polygon(surf, _shade_c(PLUM_DK, -30), spine, max(2, int(2.2 * ss)))
    pygame.draw.line(surf, LIME, (cx, tip_y + int(6 * ss)),
                     (cx - hw * 0.5, bundle_bot - int(20 * ss)), max(1, int(1.6 * ss)))
    # Pointed metal ferrule terminus.
    pygame.draw.polygon(surf, ROD_HI, [(cx, tip_y), (cx - int(3 * ss), tip_y + int(12 * ss)),
                                       (cx + int(3 * ss), tip_y + int(12 * ss))])
    pygame.draw.polygon(surf, ROD_LO, [(cx, tip_y), (cx - int(3 * ss), tip_y + int(12 * ss)),
                                       (cx + int(3 * ss), tip_y + int(12 * ss))],
                        max(1, int(ss)))
    # A gold tie-band cinching the furl.
    _bind_rings(surf, cx, [bundle_bot - int(20 * ss)], hw, ss, GOLD)
    # Dark cane shaft + a curved handle at the bottom (the resting end).
    _shaft(surf, cx, bundle_bot - int(6 * ss), bh - int(18 * ss), int(5 * ss), ss,
           WOOD_HI, WOOD_MD, WOOD_LO)
    rad = int(10 * ss)
    rect = pygame.Rect(int(cx - rad * 2), int(bh - int(20 * ss)), int(rad * 2), int(rad * 2))
    pygame.draw.arc(surf, WOOD_MD, rect, math.pi * 1.5, math.tau, max(3, int(4 * ss)))


# ════════════════════════════════════════════════════════════════════════════
#  FAMILY D — MYSTIC & MENACING (gap-facing end at box top)
# ════════════════════════════════════════════════════════════════════════════

# ---- 21. Trident ------------------------------------------------------------
# A dark iron trident: three sharp prongs (the gap terminus reads as a trio of
# clean points), a swept crossbar, a wrapped haft.
def prop_21(surf, bw, bh, ss):
    cx = bw // 2
    bar_y = int(40 * ss)
    hw = int(6 * ss)
    _shaft(surf, cx, bar_y, bh - int(4 * ss), hw, ss, ROD_HI, ROD_MD, ROD_LO)
    _wrap_grip(surf, cx, bh * 0.45, bh - int(8 * ss), int(hw * 0.9), LEATHER, ss,
               diag=True)
    # Three prongs rising to sharp points (the trident head). Centre tallest.
    for sgn, h_mul, x_mul in ((-1, 0.7, 1.0), (0, 1.0, 0.0), (1, 0.7, 1.0)):
        px = cx + sgn * int(13 * ss) * x_mul
        tipy = bar_y - int(34 * ss) * h_mul
        prong = [(px - int(4 * ss), bar_y), (px, tipy), (px + int(4 * ss), bar_y)]
        _vgrad_poly(surf, prong, ROD_MD, ROD_LO, outline=(18, 20, 26),
                    ow=max(1, int(1.6 * ss)))
        pygame.draw.line(surf, ROD_HI, (px, tipy + int(3 * ss)),
                         (px - int(2 * ss), bar_y), max(1, int(1.4 * ss)))
    # Swept crossbar the prongs root into.
    bar = [(cx - int(16 * ss), bar_y + int(2 * ss)), (cx + int(16 * ss), bar_y + int(2 * ss)),
           (cx + int(12 * ss), bar_y + int(10 * ss)), (cx - int(12 * ss), bar_y + int(10 * ss))]
    pygame.draw.polygon(surf, ROD_LO, bar)
    pygame.draw.polygon(surf, (18, 20, 26), bar, max(2, int(2 * ss)))
    pygame.draw.line(surf, ROD_HI, (cx - int(14 * ss), bar_y + int(4 * ss)),
                     (cx + int(14 * ss), bar_y + int(4 * ss)), max(1, int(1.4 * ss)))


# ---- 22. Star Wand ----------------------------------------------------------
# A slender dark wand tipped with a glowing five-point STAR — the star's sharp
# upper points are the gap terminus, framed by its own glow.
STAR_GLOW = (255, 232, 120)
STAR_HOT = (255, 250, 220)


def prop_22(surf, bw, bh, ss):
    cx = bw // 2
    star_r = int(15 * ss)
    sy = star_r + int(8 * ss)
    shaft_top = sy + int(star_r * 0.5)
    _shaft(surf, cx, shaft_top, bh - int(4 * ss), int(4.5 * ss), ss,
           CANE_BLACK_HI, CANE_BLACK, _shade_c(CANE_BLACK, -18))
    # A couple of bold gold bands so the slim wand still carries 2-3 elements.
    _bind_rings(surf, cx, [bh * 0.5, bh * 0.74], int(5 * ss), ss, GOLD)
    # Glowing five-point star finial — built from its outer + inner radii points.
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = star_r if k % 2 == 0 else star_r * 0.42
        pts.append((cx + math.cos(a) * rr, sy + math.sin(a) * rr))
    _glow_disc(surf, cx, sy, int(star_r * 1.4), STAR_GLOW, ss, alpha=150)
    pygame.draw.polygon(surf, GOLD_DK, pts)
    pygame.draw.polygon(surf, STAR_GLOW, [(cx + (p[0] - cx) * 0.82, sy + (p[1] - sy) * 0.82)
                                          for p in pts])
    pygame.draw.polygon(surf, GOLD_SHADOW, pts, max(1, int(1.6 * ss)))
    pygame.draw.circle(surf, STAR_HOT, (cx, int(sy)), max(2, int(star_r * 0.22)))


# ---- 23. Flaming Torch ------------------------------------------------------
# A dark torch wrapped in cloth, crowned by a bold FLAME. The flame's pointed
# tongue is the gap terminus; the flame body is kept opaque + dark-cored at the
# base so it never washes pale on the day sky, hot only at the very tip.
FLAME_LO = (180, 60, 24)
FLAME_MD = (236, 130, 36)
FLAME_HI = (255, 214, 96)


def prop_23(surf, bw, bh, ss):
    cx = bw // 2
    flame_top = int(4 * ss)
    bowl_y = int(46 * ss)
    _shaft(surf, cx, bowl_y, bh - int(4 * ss), int(7 * ss), ss,
           WOOD_HI, WOOD_MD, WOOD_LO)
    # Cloth wrap bindings on the haft (bold criss-cross feel via a couple rings).
    _bind_rings(surf, cx, [bh * 0.55, bh * 0.72, bh * 0.88], int(7.5 * ss), ss,
                LEATHER_DK)
    # Dark pitch bowl the flame rises from.
    pygame.draw.polygon(surf, (40, 30, 22),
                        [(cx - int(12 * ss), bowl_y), (cx + int(12 * ss), bowl_y),
                         (cx + int(8 * ss), bowl_y - int(8 * ss)),
                         (cx - int(8 * ss), bowl_y - int(8 * ss))])
    # Flame: bold layered tongues. Outer dark-orange body to a single pointed tip
    # (the terminus), then a slimmer mid + a hot core kept small so the bulk of
    # the flame body stays dark on day-blue.
    outer = [(cx - int(11 * ss), bowl_y - int(6 * ss)),
             (cx - int(6 * ss), bowl_y - int(24 * ss)),
             (cx - int(8 * ss), bowl_y - int(34 * ss)),
             (cx, flame_top),
             (cx + int(7 * ss), bowl_y - int(30 * ss)),
             (cx + int(5 * ss), bowl_y - int(18 * ss)),
             (cx + int(11 * ss), bowl_y - int(6 * ss))]
    _vgrad_poly(surf, outer, FLAME_MD, FLAME_LO, outline=(120, 36, 14),
                ow=max(2, int(2 * ss)))
    mid = [(cx - int(6 * ss), bowl_y - int(8 * ss)),
           (cx - int(2 * ss), flame_top + int(16 * ss)),
           (cx + int(2 * ss), flame_top + int(10 * ss)),
           (cx + int(5 * ss), bowl_y - int(10 * ss))]
    pygame.draw.polygon(surf, FLAME_HI, mid)
    _glow_disc(surf, cx, bowl_y - int(20 * ss), int(14 * ss), FLAME_MD, ss, alpha=90)


# ── version registry ──────────────────────────────────────────────────────────
# (name, family, one-line distinct note, draw_fn). ~15 rows across FOUR families
# (~4/4/4/3): A SWORDS & BLADES · B STAFFS & SCEPTERS · C CLOWN PROPS ·
# D MYSTIC & MENACING. Every prop is a COMPLETE, structurally distinct object,
# authored gap-facing-end UP so the route flip scaffolding plants it correctly.
VERSIONS = [
    # A — SWORDS & BLADES (round-5 winners, re-posed point-on-ground)
    ("Bone / Demon Blade", "BLADES",
     "clawed BONE blade · fanged DEMON-SKULL guard · VERTEBRA grip · glowing red eyes (round-5 hero)",
     sword_12),
    ("Cleaver Falchion", "BLADES",
     "broad single-edge CLIP-POINT chopper · simple iron cross · leather grip · flat DISC pommel",
     sword_05),
    ("Crystal Saber", "BLADES",
     "opaque AMETHYST faceted curved blade · jagged raw-shard guard · raw-gem cluster pommel",
     sword_11),
    ("Rune Greatsword", "BLADES",
     "dark forged blade · ONE glowing CYAN rune · angular anvil guard · faceted gem pommel",
     sword_10),
    # B — STAFFS & SCEPTERS
    ("Wizard Orb Staff", "STAFFS",
     "gnarled dark rod · glowing crystal ORB clutched in a claw finial · gold bind rings",
     prop_13),
    ("Jester Marotte", "STAFFS",
     "fool's-head bauble scepter · tiny belled jester head on a plum stick · on-theme",
     prop_14),
    ("Shepherd's Crook", "STAFFS",
     "long pale-wood staff · bold hooked CROOK top (curl-mouth terminus) · leather binds",
     prop_15),
    ("Skull-Topped Gold Rod", "STAFFS",
     "ornate dark-gold scepter · bone SKULL finial · gem catch · gold point collar",
     prop_16),
    # C — CLOWN PROPS
    ("Candy Cane", "CLOWN PROPS",
     "red/white SPIRAL cane · hooked candy top · bold low-freq stripes (kept dark)",
     prop_17),
    ("Giant Lollipop", "CLOWN PROPS",
     "big SWIRL disc on a striped stick · hard dark rim so the blunt top still reads the gap",
     prop_18),
    ("Ringmaster Cane", "CLOWN PROPS",
     "black/gold show cane · round gold KNOB top · dark-underside knob keeps gap readable",
     prop_19),
    ("Furled Parasol", "CLOWN PROPS",
     "closed plum/lime parasol · tight furl to a POINTED ferrule · curved cane handle",
     prop_20),
    # D — MYSTIC & MENACING
    ("Trident", "MYSTIC",
     "dark iron trident · THREE sharp prongs terminus · swept crossbar · wrapped haft",
     prop_21),
    ("Star Wand", "MYSTIC",
     "slender dark wand · glowing five-point STAR finial · gold bands · sharp star points",
     prop_22),
    ("Flaming Torch", "MYSTIC",
     "dark cloth-wrapped torch · bold FLAME with one pointed tongue · dark-cored, hot tip",
     prop_23),
]


# ════════════════════════════════════════════════════════════════════════════
#  ROUTE PANORAMA — true px, carried from round 2/4 unchanged
# ════════════════════════════════════════════════════════════════════════════

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
    dest.blit(top, (x_left, 0))                       # tip points DOWN to the gap
    bot = _render_obstacle(draw_fn, bot_h, ss, flip=False)
    dest.blit(bot, (x_left, gap_y + HALF_GAP))        # tip points UP to the gap


def _sky(w, h, top, bot):
    s = pygame.Surface((w, h))
    for i in range(h):
        s.fill(lerp_color(top, bot, i / max(1, h - 1)), (0, i, w, 1))
    return s


def _ground(surf, w):
    pygame.draw.rect(surf, (84, 132, 58), (0, GROUND_Y, w, surf.get_height() - GROUND_Y))
    pygame.draw.line(surf, (60, 100, 40), (0, GROUND_Y), (w, GROUND_Y), 2)


def _crest_gap_y(step, n_steps):
    lo, hi = 150, 430
    t = step / max(1, n_steps - 1)
    arc = math.sin(t * math.pi)
    gy = hi - (hi - lo) * arc
    return int(max(HALF_GAP + 30, min(GROUND_Y - HALF_GAP - 30, gy)))


def _route_panel(draw_fn, w, h, ss):
    route = _sky(w, h, SKY_TOP, SKY_BOT)
    _ground(route, w)
    n_steps = 11
    for step in range(n_steps):
        cx = 20 + SP // 2 + step * SP
        gy = _crest_gap_y(step, n_steps)
        _blit_pair(route, draw_fn, cx, gy, ss)
    pygame.draw.rect(route, (10, 12, 18), route.get_rect(), 2)
    return route


# ════════════════════════════════════════════════════════════════════════════
#  THE CLOWN LEANING ON THE GROUNDED PROP — left panel
# ════════════════════════════════════════════════════════════════════════════

from tools.render_jester_variants import (  # noqa: E402
    build_jester, JESTERS, draw_cupped_die, _mitt_thumb,
)
from tools.render_clown_dice import (  # noqa: E402
    _shade, _arm, VIEW_W, VIEW_H, VIEW_FEET_Y, SS as CLOWN_SS,
)
from tools.render_warren_mockup import shaped_palette  # noqa: E402
from tools.render_clown_dice import DAY_PHASE  # noqa: E402

# The clown's down-arm geometry baked into build_jester (warren_demo hero spec):
# hip_y = feet_y - 84, the near/down shoulder r_sh = (hip_cx + 25, hip_y - 50),
# hip_cx = cx + hip_dx with hip_dx = -6. We re-derive these to RE-POSE the down
# arm onto the grounded prop after build_jester paints its default down arm.
_HIP_DX = -6
_HIP_OFF = 84


def _grounded_prop_surface(draw_fn, prop_px, ss):
    """Render ONE complete prop (gap-facing end UP, resting end at the box
    bottom) into its own tight box at hero scale, for the clown to LEAN on with
    the prop's bottom tip planted on the ground. The held/leaned LEFT version can
    carry finer detail than the tiled route version (brief: held > tiled).
    Returns a 1x surface + its (w, h)."""
    H = prop_px
    surf, bw, bh = _box(H, ss)
    draw_fn(surf, bw, bh, ss)
    out_w = PIPE_W + 2 * OVERHANG
    return pygame.transform.smoothscale(surf, (out_w, H)), out_w, H


def render_clown_panel(draw_fn, idx):
    """The REAL hero Plum & Lime jester (exactly as warren_demo builds it) in the
    FIXED round-6 lean pose: the prop stands VERTICALLY beside the clown with its
    bottom tip planted ON the ground, the near/lower gloved hand grips it near the
    top (a relaxed showman lean, weight resting on the prop), while the OTHER hand
    still presents the floating power-up die up high. The pose is identical every
    row; only the prop changes. Returns a VIEW_W x VIEW_H surface."""
    spec = dict(JESTERS[-1][1])
    spec.pop("no_shadow", None)
    ss = CLOWN_SS
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * ss, VIEW_H * ss
    big = pygame.Surface((bw, bh))

    # Day-clearing sky + a sliver of grass (the warren clearing read).
    ground_y = VIEW_FEET_Y + 4        # the ground line the prop rests ON
    g_y = int(ground_y * ss)
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'], palette['sky_bot'], t),
                         (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'], palette['ground_mid'], t),
                         (0, y), (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    jester_cx = VIEW_W // 2 - 10
    feet_y = VIEW_FEET_Y

    # The OTHER (raised) hand presents the floating die high in the upper sky. The
    # die itself is drawn AFTER, up-left of the head, with the raised arm pointing
    # at it (the approved presenter read).
    die_x = jester_cx - 40
    die_base_y = 34
    hand_up = (die_x + 10, 80)
    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    # --- the GROUNDED prop the clown leans on -------------------------------
    # Stand the prop vertically to the clown's near (right) side, bottom tip ON
    # the ground line, slightly angled like a cane so the lean reads relaxed. The
    # prop is rendered gap-end-UP, so its bottom edge is the resting tip.
    hip_y = feet_y - _HIP_OFF
    hip_cx = jester_cx + _HIP_DX
    prop_px = 150                      # finial near head height, tip on the ground
    p_ss = 4
    prop, p_w, p_h = _grounded_prop_surface(draw_fn, prop_px, p_ss)
    rot = -7                           # slight cane lean (top tips toward the clown)
    rotated = pygame.transform.rotate(prop, rot)
    # Plant the bottom-centre of the prop on the ground, set out to the clown's
    # near side. We compute where the unrotated bottom-centre lands post-rotation.
    foot_local = (p_w / 2, p_h - 2)
    cxr, cyr = p_w / 2, p_h / 2
    rad = math.radians(rot)
    dx = foot_local[0] - cxr
    dy = foot_local[1] - cyr
    rfx = cxr + (dx * math.cos(rad) + dy * math.sin(rad))
    rfy = cyr + (-dx * math.sin(rad) + dy * math.cos(rad))
    rfx += (rotated.get_width() - p_w) / 2
    rfy += (rotated.get_height() - p_h) / 2
    plant_x = jester_cx + 30           # plant point on the ground beside the clown
    plant_y = ground_y - 1
    prop_ox = int(plant_x - rfx)
    prop_oy = int(plant_y - rfy)
    layer.blit(rotated, (prop_ox, prop_oy))

    # The GRIP point on the prop's upper shaft (where the gloved hand wraps). It
    # is the unrotated point ~30% down from the top, mapped through the rotation +
    # blit offset so it lands ON the prop's upper shaft in panel space.
    grip_local = (p_w / 2, p_h * 0.30)
    gdx = grip_local[0] - cxr
    gdy = grip_local[1] - cyr
    rgx = cxr + (gdx * math.cos(rad) + gdy * math.sin(rad))
    rgy = cyr + (-gdx * math.sin(rad) + gdy * math.cos(rad))
    rgx += (rotated.get_width() - p_w) / 2
    rgy += (rotated.get_height() - p_h) / 2
    grip_x = prop_ox + rgx
    grip_y = prop_oy + rgy

    # --- RE-POSE the near/lower arm onto the grip (a confident showman lean) ---
    # build_jester already painted a default down arm into the hip; redraw OVER it
    # so a gloved hand rests on the grounded prop, resting weight. Use the same
    # _arm + _mitt_thumb kit so the limb matches the figure exactly. The shoulder
    # is the hard-coded down shoulder r_sh = (hip_cx + 25, hip_y - 50).
    r_sh = (hip_cx + 25, hip_y - 50)
    grip_hand = (int(grip_x), int(grip_y))
    light = spec["light"]
    _arm(layer, r_sh, grip_hand, 8, light)
    _mitt_thumb(layer, grip_hand, 7, (250, 250, 252), side=1)

    # --- the floating power-up die, presented up high by the raised hand -------
    pulse = idx * 1.7 + 2.0
    draw_cupped_die(layer, die_x, die_base_y, pulse, show_inset=(idx % 5 == 0))

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


# ════════════════════════════════════════════════════════════════════════════
#  GATE-2 METER — median BODY luma of a prop at route scale
# ════════════════════════════════════════════════════════════════════════════

def _median_body_luma(draw_fn, ss, *, body_px=240):
    """Render ONE prop into a route-scale tile and return the MEDIAN perceptual
    luma of its opaque body pixels (the gap-facing END + finial highlights are a
    minority of pixels, so the median tracks the BODY). GATE 2 aims < ~140 vs the
    ~190 day sky. Measured on the route-tile render (the tiled version the player
    actually threads), not the finer LEFT hero shot."""
    small = _render_obstacle(draw_fn, body_px, ss, flip=False)
    small.lock()
    vals = []
    w, h = small.get_size()
    # Sample on a stride so the meter is fast but representative.
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = small.get_at((x, y))
            if a < 200:
                continue
            vals.append(0.299 * r + 0.587 * g + 0.114 * b)
    small.unlock()
    if not vals:
        return 0.0
    vals.sort()
    return vals[len(vals) // 2]


# ════════════════════════════════════════════════════════════════════════════
#  THE SHEET — ~15 rows, each = clown-leaning (left) + route panorama (right)
# ════════════════════════════════════════════════════════════════════════════

def main():
    SS = 4

    clown_w, clown_h = VIEW_W, VIEW_H
    N_STEPS = 11
    ROUTE_W = SP * N_STEPS + 40
    ROUTE_H = PLAY_H

    pad = 18
    head = 104
    row_gap = 14
    name_strip = 30
    inner_gap = 22

    # The route panel is the tall one (640); scale the clown panel up to match its
    # height so both panels in a row sit on the same baseline.
    clown_scale = ROUTE_H / clown_h
    clown_dw = int(clown_w * clown_scale)
    clown_dh = ROUTE_H

    row_w = clown_dw + inner_gap + ROUTE_W
    row_h = name_strip + ROUTE_H

    sheet_w = pad * 2 + row_w
    sheet_h = head + len(VERSIONS) * (row_h + row_gap) + pad
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((26, 28, 36))

    title_f = hud._font(30, True)
    sub_f = hud._font(15, True)
    sheet.blit(title_f.render(
        "Warren Prop Route — Round 6 (BROADENED: ~15 props, 4 families · NEW lean-on-grounded-prop pose)",
        True, (255, 255, 255)), (pad, 14))
    sheet.blit(sub_f.render(
        "POSE: prop stands VERTICALLY, bottom tip on the GROUND beside the clown; the near gloved hand "
        "grips it near the top (relaxed showman LEAN) while the OTHER hand presents the floating die up high.",
        True, (205, 210, 220)), (pad, 48))
    sheet.blit(sub_f.render(
        "Families: BLADES (round-5 winners) · STAFFS & SCEPTERS · CLOWN PROPS · MYSTIC & MENACING.  "
        "LEFT = the REAL hero clown LEANING on this prop · RIGHT = the route FILLED with it.",
        True, (170, 178, 190)), (pad, 70))

    name_f = hud._font(19, True)
    reg_f = hud._font(13, True)
    note_f = hud._font(13, False)

    for idx, (name, register, note, draw_fn) in enumerate(VERSIONS):
        ry = head + idx * (row_h + row_gap)
        strip = pygame.Surface((row_w, name_strip), pygame.SRCALPHA)
        strip.fill((18, 20, 28, 220))
        reg_col = ((150, 200, 235) if register == "BLADES" else
                   (250, 200, 120) if register == "STAFFS" else
                   (250, 150, 90) if register == "CLOWN PROPS" else
                   (210, 150, 250))
        ntxt = name_f.render(f"{idx + 1}. {name}", True, (255, 255, 255))
        strip.blit(ntxt, (8, 5))
        rtxt = reg_f.render(f"[{register}]", True, reg_col)
        strip.blit(rtxt, (12 + ntxt.get_width(), 9))
        strip.blit(note_f.render(note, True, (188, 194, 206)),
                   (20 + ntxt.get_width() + rtxt.get_width(), 9))
        sheet.blit(strip, (pad, ry))

        body_y = ry + name_strip

        # --- LEFT: the clown LEANING on this grounded prop + presenting the die ---
        clown = render_clown_panel(draw_fn, idx)
        clown = pygame.transform.smoothscale(clown, (clown_dw, clown_dh))
        pygame.draw.rect(clown, (10, 12, 18), clown.get_rect(), 2)
        sheet.blit(clown, (pad, body_y))

        # --- RIGHT: the route filled with this prop ---
        route = _route_panel(draw_fn, ROUTE_W, ROUTE_H, SS)
        sheet.blit(route, (pad + clown_dw + inner_gap, body_y))

        # Measure + print the median BODY luma of this prop at route scale (GATE 2:
        # aim < 140 against the ~190 day sky).
        luma = _median_body_luma(draw_fn, SS)
        print(f"  {idx + 1:2d}. {name:<22s} [{register:<11s}] median body luma = {luma:5.1f}"
              + ("  OK<140" if luma < 140 else "  HOT>=140"))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "warren_sword")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_6.png")
    pygame.image.save(sheet, out_path)
    print("wrote", out_path, f"({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
