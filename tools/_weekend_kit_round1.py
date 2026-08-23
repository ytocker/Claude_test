"""WEEKEND STREET KIT — round 1 candidate-sheet generator.

Draft drawers for the six net-new procedural pieces the approved sidewalk plan
(docs/sidewalk_overhaul/DAY_PLAN_WEEKEND.md §8 + §14) needs before the weekend
day-arc can be wired up:

  1  suoyi      — palm-fibre straw rain-cape overlay (the storm silhouette)
  2  winter     — padded coat / scarf / breath puff / tucked posture overlay set
  3  umbrella8  — 8-rib oil-paper canopy replacing the flat-disc _draw_umbrella
  4  cart       — `_cart_folded` two-wheeled market handcart, 3 load states
  5  stall_tarp — a PITCHED rain sheet roped over a stall that stays OPEN
  6  sweeper    — the morning street sweeper, bench-person body + besom broom

Everything is authored against the shipped primitives rather than beside them:
the pedestrian geometry mirrors ped_cast._draw_one's constants exactly, the tarp
is built on food_stalls._stall_shell, the cart's crate/roll/basket parts echo
props_cast.draw_dressing, the sweeper uses foreground_promenade._draw_bench_person,
and the breath puff blits weather._snow_flake straight out of the live cache. The
context strips are REAL game frames — biome sky, mountains, the baked sidewalk
floor, the ground's wet/snow state and live weather particles — so a piece is
judged against the pixels it will actually sit on.

Constraints held (same as every shipped family):
- pure pygame.draw.* on a Surface; no numpy / gfxdraw / PIL; pygbag-safe.
- TINY: adults ~18px (PED_H), so variety must live in the OUTLINE.
- Night cools toward (54,64,96); nothing self-lit past 150 luma; the gold coin
  stays the brightest pixel on the street.

Nothing here touches production game files — this is a review-sheet generator.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game import biome as _biome                       # noqa: E402
from game import draw as _draw                         # noqa: E402
from game import foreground as _fg                     # noqa: E402
from game import foreground_promenade as _fp           # noqa: E402
from game import foreground_variants as _fv            # noqa: E402
from game import animals_cast as _animals              # noqa: E402
from game import food_stalls as _food                  # noqa: E402
from game import ped_cast as _ped                      # noqa: E402
from game import weather as _wx                        # noqa: E402
from game.config import W, H, GROUND_Y                 # noqa: E402
from game import props_cast as _props                  # noqa: E402
from game.foreground_props import _mix, _shade         # noqa: E402

PED_H = _ped.PED_H          # 18
NIGHT_GLOW_CAP = 150


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _cap150(col):
    y = _luma(col)
    if y <= NIGHT_GLOW_CAP:
        return col
    k = NIGHT_GLOW_CAP / y
    return (int(col[0] * k), int(col[1] * k), int(col[2] * k))


def _retint(col, night):
    """Cloth/skin night cooling — the shipped ped_cast._retint_person curve."""
    return _ped._retint_person(col, night)


def _straw(col, night):
    """Straw cools LESS than cloth. A suoyi is soaking wet under lamp light, and
    the whole point of the piece is that its outline survives a dark storm — so
    the dry-straw tan keeps ~2/3 of its warmth where an indigo coat keeps ~45%.
    That warm-vs-cool gap, not brightness, is what carries the silhouette."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.34, 0.25 * night + 0.12))


# ── shared figure geometry — mirrors ped_cast._draw_one exactly ───────────────
#
# Every overlay below has to land on the same shoulder line, hem line and head
# centre the shipped body drawer uses, or it will float. Rather than eyeball it,
# recompute the identical constants; when these pieces fold into ped_cast the
# overlays become branches inside _draw_one and this helper disappears.

class _Geom:
    __slots__ = ("total_h", "head_r", "torso_h", "leg_h", "body_w", "ground",
                 "head_cy", "torso_top", "torso_bot")

    def __init__(self, base_y, height=1.0, build=1.0):
        self.total_h = max(7, int(PED_H * height))
        self.head_r = max(2, int(self.total_h * 0.135))
        self.torso_h = int(self.total_h * 0.44)
        self.leg_h = max(2, self.total_h - self.torso_h - self.head_r * 2)
        self.body_w = max(2, int(self.total_h * 0.27 * build))
        self.ground = int(base_y)
        self.head_cy = self.ground - self.leg_h - self.torso_h - self.head_r
        self.torso_top = self.head_cy + self.head_r
        self.torso_bot = self.torso_top + self.torso_h


def _conical_hat(surf, hx, hy, head_r, night, *, col=(198, 162, 96), drip_t=None):
    """The shipped ped_cast `hat == "conical"` cone, unchanged in construction —
    plus, in rain, a 1px brim-underside shadow and two falling drips. The shadow
    matters more than it sounds: without it the tan brim and the tan cape below
    merge into one blob at night, and the figure loses its head."""
    c = _straw(col, night)
    brim_w = int(head_r * 2.5)
    apex = (hx, hy - head_r * 1.8)
    cone = [(hx - brim_w, hy - head_r * 0.15), apex, (hx + brim_w, hy - head_r * 0.15)]
    pygame.draw.polygon(surf, c, cone)
    pygame.draw.polygon(surf, _shade(c, -34), cone, 1)
    pygame.draw.line(surf, _shade(c, -46), (hx - brim_w + 1, hy - head_r * 0.15 + 1),
                     (hx + brim_w - 1, hy - head_r * 0.15 + 1), 1)
    if drip_t is not None:
        wet = _straw((150, 170, 190), night)
        for i, ex in enumerate((hx - brim_w, hx + brim_w - 1)):
            ph = ((drip_t * 1.6) + i * 0.5) % 1.0
            dy = int(hy - head_r * 0.15 + 1 + ph * 7)
            if ph < 0.85:
                pygame.draw.line(surf, wet, (ex, dy), (ex, dy + 1), 1)


# ════════════════════════════════════════════════════════════════════════════
# PIECE 1 — SUOYI (蓑衣): the palm-fibre straw rain-cape overlay
# ════════════════════════════════════════════════════════════════════════════
#
# Research: coir/palm-fibre, pre-Qin, worn with a douli conical hat, and chosen
# over an umbrella precisely because it FREES BOTH HANDS. So this is the figure
# still carrying. The sources describe the fibre bulk as making the wearer look
# "like a clumsy hedgehog" — that is the design note: the cape is not a smooth
# trapezoid, it is a SHAGGY one, and the shag has to survive at 18px.
#
# Three devices carry it at scale, in order of importance:
#   1. a hem 12px wide on an 8px-wide body — the outline flares where every other
#      pedestrian tapers, so the class read is pure silhouette
#   2. a ragged 3px fringe that breaks the hem line into teeth, so the bottom
#      edge never reads as a drawn rectangle
#   3. shoulder spikes proud of the cape top, which is the "hedgehog" cue and the
#      only thing that distinguishes a suoyi from a plain cloak in one glance

_STRAW = (170, 150, 96)          # the existing food_stalls 'bamboo' awning tan
_STRAW_DK = (112, 96, 56)
_STRAW_HI = (198, 180, 126)


def draw_suoyi(surf, cx, base_y, night, t, *, carry="pole", height=1.0,
               build=1.0, coat=(96, 84, 70), rain=1.0):
    """One suoyi figure: feet on `base_y`, centred on `cx`. `carry` selects what
    the freed hands are doing — 'pole' (shoulder pole + two hanging bundles),
    'crate' (a crate hugged at the chest), 'none'."""
    g = _Geom(base_y, height, build)
    straw = _straw(_STRAW, night)
    straw_dk = _straw(_STRAW_DK, night)
    straw_hi = _straw(_STRAW_HI, night)
    cloth = _retint(coat, night)
    cloth_dk = _shade(cloth, -30)

    gait = math.sin(t * 1.5)

    # Legs + a stub of trouser show below the cape — without them the cape reads
    # as a bell hanging in the air rather than as something a person is wearing.
    _ped._legs(surf, cx, g.body_w, g.torso_bot, g.ground, gait, False,
               cloth_dk, _shade(cloth_dk, -30), False)
    pygame.draw.rect(surf, cloth, (cx - g.body_w + 1, g.torso_top, g.body_w * 2 - 2,
                                   g.torso_h))

    # ── the cape ──
    sh_y = g.torso_top - 1
    cape_h = 10
    hem_y = sh_y + cape_h
    ht, hb = 3, 6                       # half-width at neck / at hem

    # Deliberately ASYMMETRIC notches down each edge: a hand-bundled fibre cape
    # is never mirror-symmetric, and the asymmetry is what stops the shape
    # reading as a machine-drawn trapezoid at 3x.
    left = [(cx - ht, sh_y), (cx - ht - 2, sh_y + 3), (cx - ht - 1, sh_y + 5),
            (cx - hb, sh_y + 7), (cx - hb, hem_y)]
    right = [(cx + hb, hem_y), (cx + hb, sh_y + 8), (cx + ht + 2, sh_y + 5),
             (cx + ht + 2, sh_y + 2), (cx + ht, sh_y)]
    pygame.draw.polygon(surf, straw, left + right)
    pygame.draw.polygon(surf, straw_dk, left + right, 1)

    # Fibre strands: near-vertical 1px lines with a per-strand kink, alternating
    # dark/light so the body of the cape carries texture instead of flat fill.
    for i, sxp in enumerate(range(cx - hb + 1, cx + hb, 2)):
        col = straw_dk if i % 2 == 0 else straw_hi
        kink = (i * 5) % 3 - 1
        pygame.draw.line(surf, col, (sxp, sh_y + 2), (sxp + kink, hem_y - 1), 1)

    # Shoulder spikes — the hedgehog cue, proud of the cape top.
    for i, sxp in enumerate((cx - ht - 1, cx - 1, cx + 2, cx + ht + 1)):
        pygame.draw.line(surf, straw_dk, (sxp, sh_y), (sxp - 1, sh_y - 1 - (i % 2)), 1)

    # Ragged 3px fringe: every hem pixel gets its own tooth length, so the bottom
    # edge is a comb, not a line.
    for i, sxp in enumerate(range(cx - hb, cx + hb + 1)):
        ln = 1 + ((sxp * 7 + i * 3) % 3)
        pygame.draw.line(surf, straw_dk if i % 2 else straw,
                         (sxp, hem_y), (sxp, hem_y + ln), 1)

    # A dark neck notch so hat brim and cape shoulder never fuse into one mass.
    pygame.draw.line(surf, _shade(straw_dk, -22), (cx - 2, sh_y - 1), (cx + 2, sh_y - 1), 1)

    hx, hy = cx, g.head_cy
    skin = _retint(_ped.SKIN_TONES["tan"], night)
    pygame.draw.circle(surf, skin, (hx, hy), g.head_r)
    pygame.draw.circle(surf, _shade(skin, -28), (hx, hy), g.head_r, 1)

    # ── what the freed hands are doing ──
    if carry == "pole":
        # The pole rides ON TOP of the cape (it is laid over the shoulder), and
        # runs wider than the hem so the bundles hang clear of the straw — that
        # extra width is what puts this figure in the CARRY-WIDE outline class.
        pole = _retint((120, 88, 54), night)
        py = sh_y + 1
        x0, x1 = cx - 10, cx + 10
        pygame.draw.line(surf, pole, (x0, py + 3), (x1, py - 3), 2)
        for ex, ey in ((x0, py + 3), (x1, py - 3)):
            wrap = _retint((150, 120, 78), night)
            pygame.draw.line(surf, wrap, (ex, ey), (ex, ey + 4), 1)
            br = pygame.Rect(ex - 3, ey + 4, 6, 5)
            pygame.draw.ellipse(surf, _straw((176, 132, 78), night), br)
            pygame.draw.ellipse(surf, _shade(_straw((176, 132, 78), night), -30), br, 1)
    elif carry == "crate":
        wood = _retint((146, 104, 62), night)
        r = pygame.Rect(cx - 5, sh_y + 4, 10, 7)
        pygame.draw.rect(surf, _shade(wood, -28), r)
        pygame.draw.rect(surf, wood, r.inflate(-2, -2))
        pygame.draw.line(surf, _shade(wood, -28), (r.left, r.centery), (r.right, r.centery), 1)
        # Two straw forearms clamped over the crate so the cape reads as being
        # WORN over working arms, not draped on a rack.
        for sgn in (-1, 1):
            pygame.draw.line(surf, straw_dk, (cx + sgn * 6, sh_y + 4),
                             (cx + sgn * 4, sh_y + 8), 2)

    _conical_hat(surf, hx, hy, g.head_r, night, drip_t=t if rain > 0.4 else None)


# ════════════════════════════════════════════════════════════════════════════
# PIECE 2 — WINTER OVERLAY SET
# ════════════════════════════════════════════════════════════════════════════
#
# Four independent sub-pieces that stack: padded coat, scarf, breath puff,
# tucked posture. Each is separately switchable because the plan turns them on
# at different times (breath puffs survive into the cold predawn after the coats
# have gone).
#
# The coat's silhouette job is to go from an 8px-wide body to a 14px-wide one
# with a ROUNDED outline, because at 18px "padded" is a corner radius and a
# width, not a texture. The three stitch bands and the tucked-sleeve roll are
# what make it a quilted mianao rather than a fat rectangle.

_WINTER_COATS = {
    "indigo": ((86, 96, 140), (52, 60, 100), (206, 110, 96)),
    "rust":   ((150, 86, 70), (104, 56, 46), (214, 196, 150)),
}
_SCARVES = {
    "indigo": (200, 92, 84),
    "rust":   (94, 122, 150),
}


def _scarf(surf, cx, neck_y, night, *, col, style="stream", storm=1.0, t=0.0,
           reach=9):
    """The scarf. TWO genuinely different constructions, not one amplitude knob:

      'stream' — a horizontal ribbon torn downwind: a tapering 4-point polygon
                 riding a travelling sine, ending in a SPLIT fork. Reads as a
                 flag. This is the tailwind state and it sells the wind better
                 than any particle layer, exactly as the plan claims.
      'drape'  — a vertical fall down the chest: a folded band with a visible
                 lapped-over step and a fringed square end. Reads as cloth
                 hanging under its own weight. This is the lull state.

    Different axis, different outline, different terminal detail — swapping one
    for the other changes the figure's outline class, which is the point."""
    c = _retint(col, night)
    c_dk = _shade(c, -34)
    c_hi = _shade(c, 20)
    # neck band — shared by both states, 2px, tucked under the collar
    pygame.draw.line(surf, c, (cx - 3, neck_y), (cx + 3, neck_y), 2)
    pygame.draw.line(surf, c_dk, (cx - 3, neck_y + 1), (cx + 3, neck_y + 1), 1)

    if style == "stream":
        amp = 1.0 + 1.8 * storm
        ln = max(6, int(reach * (0.6 + 0.4 * storm)))
        top, bot = [], []
        for i in range(ln + 1):
            f = i / ln
            xx = cx + 3 + i
            yy = neck_y + math.sin(f * 5.2 - t * 6.0) * amp * f
            th = 2.0 * (1.0 - 0.45 * f)
            top.append((xx, yy - th * 0.5))
            bot.append((xx, yy + th * 0.5))
        pygame.draw.polygon(surf, c, top + bot[::-1])
        pygame.draw.lines(surf, c_dk, False, bot, 1)
        # forked tip — two prongs peeling apart, the detail that stops the tail
        # ending in a blunt pixel and reads as fabric flapping loose
        ex, ey = top[-1]
        pygame.draw.line(surf, c, (ex, ey), (ex + 3, ey - 2), 1)
        pygame.draw.line(surf, c_dk, (ex, ey + 1), (ex + 3, ey + 2), 1)
    else:  # 'drape'
        ln = max(5, int(reach * 0.7))
        bx = cx + 1
        pygame.draw.rect(surf, c, (bx - 1, neck_y + 1, 3, ln))
        pygame.draw.line(surf, c_dk, (bx + 1, neck_y + 1), (bx + 1, neck_y + ln), 1)
        # the lapped-over fold: a 1px step where the second pass of the scarf
        # crosses the first — the single cue that reads as "wrapped twice"
        pygame.draw.rect(surf, c_hi, (bx - 2, neck_y + 3, 3, 2))
        pygame.draw.line(surf, c_dk, (bx - 2, neck_y + 4), (bx, neck_y + 4), 1)
        for i in range(3):
            pygame.draw.line(surf, c_dk, (bx - 1 + i, neck_y + ln),
                             (bx - 1 + i, neck_y + ln + 1 + (i % 2)), 1)


_BREATH_PERIOD = 2.8        # plan: 2.2-3.4s per figure, phase-offset per instance
_BREATH_LIFE = 0.8


def _breath_puff(surf, x, y, t, *, phase=0.0, wind=1.0, period=_BREATH_PERIOD,
                 peak_a=110, base_a=70):
    """One breath puff, straight out of the live snowflake cache — a soft 3px
    white disc with an alpha falloff we already ship, so this costs one blit and
    zero new art. Spawned on a per-figure phase, drifting downwind, fading over
    0.8s. Uses the cache's 16-step alpha buckets, so the fade is quantised the
    same way the falling snow is and the two read as one weather system."""
    ph = ((t + phase) % period) / period
    age = ph * period
    if age > _BREATH_LIFE:
        return
    f = age / _BREATH_LIFE
    a = int((base_a + (peak_a - base_a) * (1.0 - f)) * (1.0 - f * f))
    if a < 12:
        return
    r = 1 + int(f * 1.6)
    spr = _wx._snow_flake(r, a)
    dx = int(f * 7 * wind)
    dy = -int(f * 2)
    surf.blit(spr, (int(x + dx) - spr.get_width() // 2,
                    int(y + dy) - spr.get_height() // 2))


def draw_winter_figure(surf, cx, base_y, night, t, *, coat="indigo",
                       scarf="stream", tucked=True, storm=1.0, breath=True,
                       height=1.0, build=1.0, upstream=False, phase=0.0):
    """A padded-coat winter figure. `tucked` applies the cold posture (head 1px
    down into the shoulders, stride -20%); `upstream` adds the 1px lean away
    from the wind the plan asks for on anyone walking into it."""
    g = _Geom(base_y, height, build)
    base, dark, fur = _WINTER_COATS.get(coat, _WINTER_COATS["indigo"])
    c = _retint(base, night)
    c_dk = _retint(dark, night)
    c_hi = _shade(c, 18)
    fur_c = _retint(fur, night)
    skin = _retint(_ped.SKIN_TONES["fair"], night)

    # Stride: the cold posture shortens it 20%. _legs derives swing straight from
    # `gait`, so scaling gait scales the stride and nothing else.
    stride = 0.8 if tucked else 1.0
    gait = math.sin(t * 1.5) * stride
    lean = -1 if upstream else 0
    head_drop = 1 if tucked else 0

    _ped._legs(surf, cx, g.body_w, g.torso_bot, g.ground, gait, False,
               c_dk, _shade(c_dk, -28), False)

    # ── the padded coat ──
    pad = int(g.body_w * 1.35) + 2          # +2px each side over the shipped A_PADDED
    top = g.torso_top - g.head_r // 2 + head_drop
    r = pygame.Rect(cx - pad + lean, top, pad * 2, g.torso_bot - top + 1)
    pygame.draw.rect(surf, c, r, border_radius=3)
    pygame.draw.rect(surf, c_dk, r, 1, border_radius=3)
    for q in (0.26, 0.50, 0.74):
        yy = int(r.top + r.height * q)
        pygame.draw.line(surf, c_dk, (r.left + 1, yy), (r.right - 2, yy), 1)
        pygame.draw.line(surf, c_hi, (r.left + 1, yy + 1), (r.right - 2, yy + 1), 1)

    # Hands tucked into opposite sleeves — a single horizontal sleeve ROLL across
    # the belly with a dark mouth at each end. At this size the classic posture
    # can only be a bar; the two mouths and the lit top edge are what make the
    # bar read as forearms inside cuffs rather than as a fourth stitch band.
    ry = int(r.top + r.height * 0.56)
    roll = pygame.Rect(r.left + 1, ry, r.width - 2, 3)
    pygame.draw.rect(surf, _shade(c, -18), roll)
    pygame.draw.line(surf, c_hi, (roll.left, roll.top), (roll.right - 1, roll.top), 1)
    pygame.draw.line(surf, _shade(c_dk, -14), (roll.left, roll.top + 1),
                     (roll.left + 1, roll.top + 2), 2)
    pygame.draw.line(surf, _shade(c_dk, -14), (roll.right - 2, roll.top + 1),
                     (roll.right - 1, roll.top + 2), 2)

    # ── head, then the collar OVER the chin ──
    hx = cx + lean
    hy = g.head_cy + head_drop
    pygame.draw.circle(surf, skin, (hx, hy), g.head_r)
    pygame.draw.circle(surf, _shade(skin, -28), (hx, hy), g.head_r, 1)
    cap = pygame.Rect(hx - g.head_r, hy - int(g.head_r * 1.7), g.head_r * 2,
                      int(g.head_r * 1.6))
    pygame.draw.ellipse(surf, c_dk, cap)
    pygame.draw.line(surf, fur_c, (hx - g.head_r, hy - int(g.head_r * 0.35)),
                     (hx + g.head_r, hy - int(g.head_r * 0.35)), 2)

    neck_y = hy + g.head_r - 1
    _scarf(surf, hx, neck_y, night, col=_SCARVES.get(coat, (200, 92, 84)),
           style=scarf, storm=storm, t=t)

    collar = pygame.Rect(r.left + 1, neck_y - 1, r.width - 2, 4)
    pygame.draw.ellipse(surf, fur_c, collar)
    pygame.draw.ellipse(surf, _shade(fur_c, -40), collar, 1)

    if breath:
        _breath_puff(surf, hx + g.head_r + 1, hy, t, phase=phase, wind=storm)


def draw_winter_dog(surf, cx, base_y, night, t, *, variant=0, phase=0.0,
                    storm=1.0):
    """The shipped dog, plus its own breath — lower and on a faster 1.4s cycle
    than an adult's, which is the whole difference and reads instantly as a
    smaller, quicker animal."""
    v = _fv.get("dog", variant)
    if v is not None:
        _animals.draw_dog(surf, cx, base_y, v, night, t)
    _breath_puff(surf, cx - 10, base_y - 12, t, phase=phase, wind=storm,
                 period=1.4, peak_a=92, base_a=58)


# ════════════════════════════════════════════════════════════════════════════
# PIECE 3 — THE 8-RIB OIL-PAPER UMBRELLA
# ════════════════════════════════════════════════════════════════════════════
#
# Research: the canopy is cut as TRIANGULAR SEGMENTS pegged to steamed bamboo
# ribs, so a real oil-paper umbrella is a fan of panels, not a dome. Rib lines
# alone die at 16px — a 1px line on a 1px-varied fill vanishes. So the radial
# read is carried by TWO devices at once:
#   - alternating panel VALUE between neighbouring wedges (survives downscale,
#     because it is an area cue not a line cue)
#   - the 1px rib on every boundary, which sharpens it when the figure is near
# and the hem is scalloped once per panel, so the silhouette itself counts the
# ribs even when the interior washes out.

_UMBRELLA_COLORS = _fp._UMBRELLA_COLORS


def draw_umbrella8(surf, cx, canopy_y, color_idx, *, night=0.0, scale=1.0,
                   pole_len=9, wind=0.0, ribs=8, crooked=0.0):
    """Drop-in replacement geometry for foreground_promenade._draw_umbrella.
    `crooked` tilts the whole canopy off the pole — the kid version, held wrong."""
    color = _UMBRELLA_COLORS[color_idx % len(_UMBRELLA_COLORS)]
    if night > 0.05:
        color = _cap150(_mix(color, (54, 64, 96), min(0.5, 0.4 * night + 0.15)))
    dark = _shade(color, -46)
    panel_b = _shade(color, -16)
    rib_c = _shade(color, -34)
    r = max(5, int(8 * scale))
    tilt = int(round(wind * 3.0)) + 1
    apex_x = cx + tilt + int(crooked * r * 0.5)
    cy = int(canopy_y)
    apex_y = cy - r - int(abs(crooked) * 1)

    # Rib feet, spread across the visible hem. The end feet sit on the silhouette
    # edge; the interior feet ride the front hem's shallow droop, so each panel
    # gets its own scallop and the outline itself carries the rib count.
    feet = []
    for i in range(ribs + 1):
        f = i / ribs
        xx = cx - r + 2 * r * f
        droop = math.sin(f * math.pi) * (r * 0.30)
        feet.append((xx, cy + droop))

    outline = [(cx - r, cy),
               (apex_x - int(r * 0.62), apex_y + int(r * 0.42)),
               (apex_x, apex_y),
               (apex_x + int(r * 0.62), apex_y + int(r * 0.42)),
               (cx + r, cy)]
    hem = []
    for i, (fx, fy) in enumerate(reversed(feet)):
        hem.append((fx, fy))
        if i < len(feet) - 1:
            nx, ny = list(reversed(feet))[i + 1]
            hem.append(((fx + nx) * 0.5, max(fy, ny) + 1.6))   # the scallop dip
    pygame.draw.polygon(surf, color, outline + hem)

    # Alternating panel value — the cue that survives to 1x.
    for i in range(ribs):
        if i % 2:
            continue
        pygame.draw.polygon(surf, panel_b,
                            [(apex_x, apex_y), feet[i], feet[i + 1]])
    for i in range(ribs + 1):
        pygame.draw.line(surf, rib_c, (apex_x, apex_y), feet[i], 1)
    pygame.draw.polygon(surf, dark, outline + hem, 1)

    # 2px finial + the 1px spike above it.
    pygame.draw.circle(surf, dark, (apex_x, apex_y), 1)
    pygame.draw.line(surf, dark, (apex_x, apex_y - 1), (apex_x, apex_y - 3), 1)

    hand_x = cx - 1
    pygame.draw.line(surf, _retint((110, 84, 56), night), (cx, cy + 1),
                     (hand_x, cy + int(pole_len * scale)), 1)


# ════════════════════════════════════════════════════════════════════════════
# PIECE 4 — `_cart_folded`: the two-wheeled market handcart
# ════════════════════════════════════════════════════════════════════════════

def _spoked_wheel(surf, cx, cy, r, night, *, spin=0.0, far=False):
    """NEW PRIMITIVE. A spoked cart wheel that survives at r=4.

    The trick at this size is that spokes drawn as lines inside a filled disc
    disappear — there is no room for both a rim and a gap. So the wheel is built
    inside-out: a dark IRON TYRE ring, a light interior that reads as the gap
    between spokes, three full-diameter spokes (six arms) in the rim tone, and a
    1px hub. Three, not eight: at 8px across, eight spokes fill the interior
    solid and the wheel goes back to being a disc.

    `far` draws the off-side wheel — 1px smaller, one value darker, offset by the
    caller — which is what makes a side-on cart read as TWO-wheeled."""
    iron = _retint((70, 62, 56) if not far else (54, 48, 44), night)
    wood = _retint((150, 112, 66) if not far else (116, 86, 52), night)
    hub = _retint((186, 150, 92) if not far else (140, 110, 70), night)
    pygame.draw.circle(surf, iron, (cx, cy), r)
    pygame.draw.circle(surf, wood, (cx, cy), max(1, r - 1))
    for k in range(3):
        a = spin + k * math.pi / 3.0
        dx, dy = math.cos(a) * (r - 1), math.sin(a) * (r - 1)
        pygame.draw.line(surf, iron, (cx - dx, cy - dy), (cx + dx, cy + dy), 1)
    pygame.draw.circle(surf, hub, (cx, cy), 1)


def _cart_crate(surf, x, y, w, h, night):
    """The props_cast.draw_dressing 'crates' idiom at cart scale — same slatted
    box, same two-tone, so a cart load and a kerbside crate stack are visibly
    the same town's woodwork."""
    wood = _retint((146, 104, 62), night)
    pygame.draw.rect(surf, _shade(wood, -28), (x, y, w, h))
    pygame.draw.rect(surf, wood, (x + 1, y + 1, w - 2, h - 2))
    for sxp in range(x + 3, x + w - 1, 4):
        pygame.draw.line(surf, _shade(wood, -28), (sxp, y + 1), (sxp, y + h - 2), 1)


def _rolled_awning(surf, x, y, w, night, *, col=(176, 96, 58)):
    """A rolled awning: a lying cylinder with a crisp END-CIRCLE and a spiral,
    lifted from the rolled-mat construction in draw_dressing('sacks') — the roll
    end is what stops it reading as a sausage."""
    c = _retint(col, night)
    c_dk = _shade(c, -30)
    c_hi = _shade(c, 18)
    pygame.draw.rect(surf, c_dk, (x, y, w, 5), border_radius=2)
    pygame.draw.rect(surf, c, (x + 1, y + 1, w - 2, 3), border_radius=1)
    pygame.draw.line(surf, c_hi, (x + 2, y + 1), (x + w - 3, y + 1), 1)
    end = pygame.Rect(x + w - 4, y - 1, 5, 7)
    pygame.draw.ellipse(surf, c_dk, end)
    pygame.draw.ellipse(surf, c, end.inflate(-2, -2))
    pygame.draw.line(surf, c_dk, (end.centerx, end.top + 2), (end.centerx, end.bottom - 3), 1)


def draw_cart_folded(surf, cx, base_y, night, t, *, load="loaded"):
    """A ~26px two-wheeled market handcart in one of three LOAD STATES.

    The three are not the same cart with things removed. Each has a different
    BED ANGLE, a different ground contact and a different mass distribution, so
    the three silhouettes are a bar, a wedge and a nose-down triangle:

      'loaded' — bed level at axle height, handles lifted (in transit): a pole
                 bundle laid diagonally, a rolled awning, a crate. Wheels turn.
      'half'   — TIPPED to unload: bed sloped down-left, handles up in the air,
                 the last crate sliding to the low end, a basket already on the
                 pavement. Reads as mid-action.
      'empty'  — PARKED: bed level, handles dropped to the pavement, bare slats
                 showing, the rolled mat leaned against the near wheel.
    """
    g = int(base_y)
    wood = _retint((132, 96, 56), night)
    wood_dk = _shade(wood, -30)
    wood_hi = _shade(wood, 18)

    wr = 4
    axle_x, axle_y = cx - 3, g - wr
    spin = t * 1.8 if load == "loaded" else 0.0

    # Bed geometry per state: (left end y-offset, right end y-offset) from the
    # bed line, plus where the handles run.
    if load == "half":
        bl, br = 5, -4
    else:
        bl, br = 0, 0
    bed_y = g - wr * 2 - 2
    x0, x1 = cx - 13, cx + 13
    yl, yr = bed_y + bl, bed_y + br

    # Far wheel first (behind the bed), then bed, then near wheel in front.
    _spoked_wheel(surf, axle_x + 4, axle_y - 2, wr - 1, night, spin=spin, far=True)

    bed = [(x0, yl), (x1, yr), (x1, yr + 3), (x0, yl + 3)]
    pygame.draw.polygon(surf, wood, bed)
    pygame.draw.polygon(surf, wood_dk, bed, 1)
    pygame.draw.line(surf, wood_hi, (x0 + 1, yl + 1), (x1 - 1, yr + 1), 1)
    if load == "empty":
        # Bare slats: the only state where the bed's own construction is visible,
        # which is what makes "empty" a positive read rather than an absence.
        for i in range(1, 6):
            f = i / 6.0
            sxp = int(x0 + (x1 - x0) * f)
            pygame.draw.line(surf, wood_dk, (sxp, yl + 1), (sxp, yl + 2), 1)

    # Handles / shafts.
    if load == "loaded":
        hx0, hy0 = x1 - 1, yr + 1
        hx1, hy1 = x1 + 9, yr - 4
    elif load == "half":
        hx0, hy0 = x1 - 1, yr + 1
        hx1, hy1 = x1 + 8, yr - 9
    else:
        hx0, hy0 = x1 - 1, yr + 1
        hx1, hy1 = x1 + 9, g - 1
    for off in (0, 2):
        pygame.draw.line(surf, wood_dk, (hx0, hy0 + off), (hx1, hy1 + off), 1)
    pygame.draw.line(surf, wood, (hx1 - 1, hy1), (hx1 - 1, hy1 + 2), 2)

    _spoked_wheel(surf, axle_x, axle_y, wr, night, spin=spin)

    # ── the load ──
    if load == "loaded":
        # Pole bundle laid diagonally across the bed — five 1px poles splayed at
        # slightly different angles with one binding band, so it reads as a tied
        # bundle rather than a solid wedge.
        pole = _retint((160, 132, 84), night)
        pole_dk = _shade(pole, -34)
        for i in range(5):
            pygame.draw.line(surf, pole if i % 2 else pole_dk,
                             (x0 + 1, yl - 1 - i), (x1 - 3, yr - 7 - i // 2), 1)
        band = _retint((120, 70, 56), night)
        pygame.draw.line(surf, band, (cx + 2, yr - 9), (cx + 3, yr - 3), 2)
        _rolled_awning(surf, x0 + 2, yl - 8, 12, night)
        _cart_crate(surf, cx + 4, yr - 14, 9, 7, night)
    elif load == "half":
        _cart_crate(surf, x0 + 2, yl - 7, 9, 7, night)
        weave = _retint((172, 138, 86), night)
        br_ = pygame.Rect(cx - 18, g - 7, 10, 7)
        pygame.draw.ellipse(surf, _shade(weave, -32), br_)
        pygame.draw.ellipse(surf, weave, br_.inflate(-2, -2))
        pygame.draw.ellipse(surf, _shade(weave, -32), (br_.left - 1, br_.top - 1, 12, 4))
    else:
        mat = _retint((176, 148, 92), night)
        mx = axle_x - 7
        pygame.draw.line(surf, _shade(mat, -30), (mx, g), (mx + 3, g - 13), 4)
        pygame.draw.line(surf, mat, (mx, g - 1), (mx + 3, g - 12), 2)
        pygame.draw.circle(surf, _shade(mat, -30), (mx + 3, g - 13), 2)
        pygame.draw.circle(surf, mat, (mx + 3, g - 13), 1)

    # Ground contact — a 1px shadow under whatever is actually touching down.
    sh = _mix(_retint((60, 52, 44), night), (0, 0, 0), 0.2)
    pygame.draw.line(surf, sh, (axle_x - wr, g), (axle_x + wr, g), 1)
    if load == "empty":
        pygame.draw.line(surf, sh, (hx1 - 2, g), (hx1 + 1, g), 1)


# ════════════════════════════════════════════════════════════════════════════
# PIECE 5 — `_stall_tarp`: the pitched rain sheet
# ════════════════════════════════════════════════════════════════════════════
#
# Research: vendors pitch tarps on purpose — a flat sheet POOLS and sags and
# eventually dumps, so the working answer is a taut sheet with one corner low so
# the water runs off away from the goods. That is the entire design brief for
# this piece and it is why the sheet must NOT be a flat rectangle: the slope IS
# the storytelling.
#
# The read at 1x, in order: a pale cool slab tilted against a dark stall, a
# thread of water falling off its low corner, and steam still climbing out from
# under it. That last one is the point of the whole piece — this stall is open.

_TARP_MARGIN_X = 52
_TARP_MARGIN_UP = 78
_TARP_MARGIN_DOWN = 8


def _clamped_lit(drawer):
    """The props_cast._night_clamped contract, applied to a new LIT piece.

    The tarped stall is the only member of this kit that emits light (brazier
    halo under the sheet), and an additive halo summed over an already-warm
    counter is exactly the core+halo overlap that broke the cap once before. So
    at night the whole piece — core, broth, halo — draws onto its own SRCALPHA
    layer, gets props_cast's composite luma clamp, and only then blits. Day is
    a straight-through draw, so the daylight look is byte-identical."""
    def _wrapped(surf, sx, base_y, night, t, **kw):
        if night <= 0.05:
            return drawer(surf, sx, base_y, night, t, **kw)
        layer = pygame.Surface((_TARP_MARGIN_X * 2,
                                _TARP_MARGIN_UP + _TARP_MARGIN_DOWN),
                               pygame.SRCALPHA)
        drawer(layer, _TARP_MARGIN_X, _TARP_MARGIN_UP, night, t, **kw)
        _props._clamp_surface_luma(layer)
        surf.blit(layer, (int(sx) - _TARP_MARGIN_X, int(base_y) - _TARP_MARGIN_UP))
    _wrapped.__name__ = getattr(drawer, "__name__", "drawer")
    return _wrapped


def _stall_tarp(surf, sx, base_y, night, t, *, kind="steamer", rain=1.0):
    """A tarped-over stall, built on food_stalls._stall_shell geometry (roof
    suppressed — the tarp replaces the awning, it does not sit on top of it)."""
    cy = _food._stall_shell(surf, sx, base_y, night, awning=("indigo", "cream"),
                            roof=False, sign=None)
    half_w = _food.HALF_W
    post_top = base_y - 34

    tarp = _mix((132, 148, 166), (54, 64, 96), min(0.55, 0.42 * night + 0.16))
    tarp_dk = _shade(tarp, -34)
    tarp_hi = _shade(tarp, 20)

    # The pitch. High corner upwind (left), low corner downwind (right) —
    # matching the umbrella's downwind lean so the whole street agrees on which
    # way the weather is going.
    hx, hy = sx - half_w - 5, post_top - 8
    lx, ly = sx + half_w + 6, post_top + 5
    sheet = [(hx, hy), (lx, ly), (lx, ly + 3), (hx, hy + 3)]
    pygame.draw.polygon(surf, tarp, sheet)
    pygame.draw.polygon(surf, tarp_dk, sheet, 1)
    pygame.draw.line(surf, tarp_hi, (hx + 1, hy + 1), (lx - 1, ly + 1), 1)

    # Fold creases across the sheet — short ticks perpendicular to the slope.
    # Cheap, and they stop 50px of flat colour reading as a painted plank.
    for i in range(1, 6):
        f = i / 6.0
        fx = int(hx + (lx - hx) * f)
        fy = int(hy + (ly - hy) * f)
        pygame.draw.line(surf, tarp_dk, (fx, fy + 1), (fx - 1, fy + 3), 1)

    # Lashings: rope turns at each post top, plus one taut guy line down to the
    # deck. The guy is what says "roped over", not "resting on".
    rope = _retint((196, 178, 130), night)
    for px, py in ((sx - half_w + 3, post_top), (sx + half_w - 3, post_top + 2)):
        ty = int(hy + (ly - hy) * ((px - hx) / max(1, (lx - hx))))
        for k in (-1, 1):
            pygame.draw.line(surf, rope, (px + k, ty), (px + k, ty + 5), 1)
        pygame.draw.circle(surf, _shade(rope, -30), (px, ty + 2), 1)
    pygame.draw.line(surf, rope, (hx + 1, hy + 2), (sx - half_w - 8, base_y - 1), 1)

    # Shadow under the sheet so the vendor sits in a cave, which is what makes
    # the warm steam and the lit face pop out of it.
    shade = pygame.Surface((half_w * 2 + 12, 14), pygame.SRCALPHA)
    shade.fill((14, 18, 34, 70))
    surf.blit(shade, (sx - half_w - 6, post_top + 4))

    # ── the runoff ──
    # A 1px thread of water off the low corner, drawn as travelling dashes so it
    # reads as MOVING at 60fps without a particle system, plus a bead hanging at
    # the lip and a flat splash on the paving.
    wet = _mix((176, 200, 220), (60, 74, 104), min(0.62, 0.5 * night + 0.18))
    stream_top = ly + 3
    for k in range(4):
        ph = ((t * 2.2) + k * 0.25) % 1.0
        yy = stream_top + ph * (base_y - stream_top)
        if yy < base_y - 1:
            pygame.draw.line(surf, wet, (lx, int(yy)), (lx, int(yy) + 2), 1)
    pygame.draw.circle(surf, wet, (lx, stream_top), 1)
    sp_w = 3 + int(math.sin(t * 4.4) * 1.5)
    pygame.draw.ellipse(surf, _shade(wet, -20), (lx - sp_w, base_y - 2, sp_w * 2, 3), 1)

    # ── the vendor, sitting it out ──
    shirt = _retint((92, 82, 112), night)
    shirt_dk = _shade(shirt, -22)
    hair = _retint((52, 42, 34), night)
    vx = sx - 6
    body_y = cy - 10
    _fp._draw_bench_person(surf, vx, body_y, shirt, shirt_dk, hair, night=night)
    # Arms folded: one bar plus two hand pixels tucked under the opposite elbow —
    # the "waiting it out" posture, and it costs three draws.
    pygame.draw.line(surf, shirt_dk, (vx, body_y + 4), (vx + 5, body_y + 4), 2)
    pygame.draw.circle(surf, shirt_dk, (vx, body_y + 4), 1)
    pygame.draw.circle(surf, shirt_dk, (vx + 5, body_y + 4), 1)
    # Stool under him, so he isn't hovering behind his own counter.
    stool = _retint((130, 92, 52), night)
    pygame.draw.rect(surf, _shade(stool, -26), (vx + 1, body_y + 8, 5, 4))

    # ── still cooking ──
    pot = _retint((64, 60, 62), night)
    px = sx + 10
    pygame.draw.ellipse(surf, pot, (px - 6, cy - 7, 12, 6))
    pygame.draw.ellipse(surf, _shade(pot, -22), (px - 6, cy - 7, 12, 6), 1)
    pygame.draw.ellipse(surf, _retint((150, 96, 58), night), (px - 4, cy - 7, 8, 3))
    if night > 0.05:
        _food._warm_glow(surf, px, cy - 4, radius=8, peak=44, color=(150, 92, 46))
    _food._wisp(surf, px, cy - 8, t, n=4, rise=22, spread=3.0, speed=0.5,
                peak_a=72, r0=2, sway=2.8, color=_food._steam_col(night))
    _food._wisp(surf, px - 4, cy - 7, t, n=3, rise=16, spread=2.2, speed=0.6,
                phase=0.5, peak_a=50, r0=1, sway=2.2, color=_food._steam_col(night))


draw_stall_tarp = _clamped_lit(_stall_tarp)


# ════════════════════════════════════════════════════════════════════════════
# PIECE 6 — `_sweeper`
# ════════════════════════════════════════════════════════════════════════════
#
# Research: the broom sweeping a Chinese street at 6am is a BESOM — a fan of
# split bamboo twigs wire-bound around a shaft, not a flat brush head. That fan
# is the whole silhouette gift: a splayed triangle at the end of a long diagonal
# is legible at 14px where a rectangle head is not.
#
# The gait is deliberately two frames, not a sine on everything: sweeping is an
# asymmetric PUSH then RECOVER, and giving both halves the same easing makes it
# read as a metronome instead of as work.

_SWEEP_PERIOD = 1.8


def draw_sweeper(surf, cx, base_y, night, t, *, phase=0.0, coat=(108, 118, 96),
                 pile=True):
    """The morning sweeper: the _draw_bench_person body idiom + a 14px angled
    besom on a 1.8s cycle, pushing a small pile of snow and paper."""
    g = int(base_y)
    ph = ((t + phase) % _SWEEP_PERIOD) / _SWEEP_PERIOD
    # Asymmetric cycle: 0..0.45 is the push (fast, eased out), 0.45..1 the
    # recover (slower, eased in). `k` is 0 at the top of the stroke, 1 at full
    # extension.
    if ph < 0.45:
        k = 1.0 - (1.0 - ph / 0.45) ** 2
    else:
        f = (ph - 0.45) / 0.55
        k = 1.0 - (f * f)

    shirt = _retint(coat, night)
    shirt_dk = _shade(shirt, -22)
    hair = _retint((48, 40, 32), night)

    # He faces LEFT like the rest of the cast, so the push is leftward: the body
    # pitches left into the stroke and the broom head runs out ahead of him.
    lean = -int(round(k * 2))
    body_y = g - 11 + int(round(k * 1))
    # Body offset right of `cx` so the sweeper+broom envelope straddles the anchor
    # like every other cast member — the broom is half the outline and it all
    # lives on one side of the man.
    bx = cx + 4 + lean

    # Legs: the back leg extends on the push, so the two frames differ in stance
    # width as well as in arm angle.
    leg = _shade(shirt_dk, -14)
    pygame.draw.line(surf, leg, (bx + 1, body_y + 8), (bx - 1 - int(k * 3), g), 1)
    pygame.draw.line(surf, leg, (bx + 4, body_y + 8), (bx + 5 + int(k * 2), g), 1)

    _fp._draw_bench_person(surf, bx, body_y, shirt, shirt_dk, hair, night=night)

    # ── the besom ──
    # The head STAYS ON THE DECK for the whole stroke — a broom that lifts off
    # the paving mid-sweep reads as a staff being waved. So the tip is pinned to
    # the ground line and only its reach changes; the shaft's apparent length
    # shortening as it steepens is the foreshortening, and it sells the push.
    hand_x = bx + 4 - int(k * 2)
    hand_y = body_y + 2
    tip_x = hand_x - (9 + k * 4)          # ~12px shaft at rest, ~15px at full reach
    tip_y = g - 1
    ang = math.atan2(tip_y - hand_y, tip_x - hand_x)   # screen space, hand → tip
    shaft = _retint((146, 112, 68), night)
    pygame.draw.line(surf, _shade(shaft, -30), (hand_x, hand_y + 1), (tip_x, tip_y + 1), 2)
    pygame.draw.line(surf, shaft, (hand_x, hand_y), (tip_x, tip_y), 1)
    pygame.draw.line(surf, shirt_dk, (bx + 4, body_y + 1), (hand_x, hand_y), 2)
    pygame.draw.line(surf, shirt, (bx + 1, body_y + 2), (hand_x - 2, hand_y + 1), 1)

    # Wire binding, then the twig fan: six 1px twigs splayed ~46°, alternating
    # two straw values so the fan reads as a bundle and not as a solid triangle.
    bind = _retint((120, 106, 70), night)
    pygame.draw.circle(surf, bind, (int(tip_x), int(tip_y)), 1)
    twig = _straw((172, 152, 100), night)
    twig_dk = _straw((122, 106, 66), night)
    for i in range(6):
        a = ang + math.radians(-26 + i * 10.4)
        ln = 6 - abs(i - 2.5) * 0.5
        ex = tip_x + math.cos(a) * ln
        # Twigs splay but never punch through the paving — the low ones flatten
        # along the deck instead, which is exactly what a bundle of bamboo does
        # under load and reads as bristles biting the stone.
        ey = min(float(g), tip_y + math.sin(a) * ln)
        pygame.draw.line(surf, twig if i % 2 else twig_dk,
                         (int(tip_x), int(tip_y)), (int(ex), int(ey)), 1)

    if pile:
        # The pile: a low pale mound with two dark paper flecks and one bright
        # crest pixel, sitting just ahead of the twigs and nudging forward with
        # the stroke so the sweeper is visibly moving something.
        pile_x = int(tip_x - 5 + k * 2)
        # Held a step under the paving's own value: the pile is swept-up slush and
        # litter, not a highlight, and it must never be the brightest thing on a
        # sunrise street where the coin is about to appear.
        pale = _mix((198, 202, 204), (70, 82, 108), min(0.5, 0.4 * night))
        pygame.draw.ellipse(surf, _shade(pale, -30), (pile_x - 4, g - 3, 9, 4))
        pygame.draw.ellipse(surf, pale, (pile_x - 3, g - 3, 7, 3))
        pygame.draw.line(surf, _shade(pale, 10), (pile_x - 2, g - 3), (pile_x + 1, g - 3), 1)
        for fx, fy in ((pile_x - 2, g - 2), (pile_x + 2, g - 3)):
            pygame.draw.circle(surf, _retint((150, 108, 84), night), (fx, fy), 1)
        # A dust puff at the moment of full extension.
        if k > 0.75:
            _breath_puff(surf, pile_x + 3, g - 4, (k - 0.75) * 3.2, phase=0.0,
                         wind=0.6, period=1.0, peak_a=46, base_a=26)


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERING
# ════════════════════════════════════════════════════════════════════════════

def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _wrap(surf, s, x, y, w, sz=10, col=(196, 200, 210), lh=13):
    f = _font(sz)
    words = s.split(" ")
    line = ""
    for wd in words:
        trial = (line + " " + wd).strip()
        if f.size(trial)[0] > w and line:
            surf.blit(f.render(line, True, col), (x, y))
            y += lh
            line = wd
        else:
            line = trial
    if line:
        surf.blit(f.render(line, True, col), (x, y))
        y += lh
    return y


def _gold_coin(surf, cx, cy, r=8):
    """The brightness yardstick. Nothing in this kit may out-pop it."""
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, (255, 232, 150))):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


SHEET_BG = (26, 28, 36)
PANEL_BG = (36, 39, 50)


def _zoom_cell(parent, x, y, w, h, caption, draw_fn, *, night, deck, zoom=3,
               feet_frac=0.80):
    """One 3x (or 6x) zoom cell: draw the piece at native size onto a small deck,
    scale it up NEAREST-NEIGHBOUR (never smoothscale — it would lie about the
    pixel work), and caption it."""
    iw, ih = w // zoom, h // zoom
    cell = pygame.Surface((iw, ih))
    cell.fill(deck)
    ground = int(ih * feet_frac)
    pygame.draw.rect(cell, _shade(deck, -16), (0, ground, iw, ih - ground))
    pygame.draw.line(cell, _shade(deck, 18), (0, ground), (iw, ground), 1)
    draw_fn(cell, iw // 2, ground)
    big = pygame.transform.scale(cell, (iw * zoom, ih * zoom))
    parent.blit(big, (x, y))
    pygame.draw.rect(parent, (78, 84, 104), (x, y, iw * zoom, ih * zoom), 1)
    col = (168, 200, 235) if night > 0.5 else (222, 206, 154)
    for i, line in enumerate(caption.split("\n")):
        _text(parent, line, x + 2, y + ih * zoom + 3 + i * 12, 10, col)


# ── real game-frame context strips ───────────────────────────────────────────

_WX_CACHE = {}


def _weather_for(phase, steps=260):
    """A live Weather stepped to a settled particle field for `phase`, so the
    context strips carry the real rain/snow the piece will be seen through."""
    key = round(phase, 4)
    w = _WX_CACHE.get(key)
    if w is None:
        w = _wx.Weather()
        for _ in range(steps):
            w.update(1.0 / 60.0, phase)
        _WX_CACHE[key] = w
    return w


def _context(phase, draw_fn, *, particles=True, wet=None, snow=None,
             scroll=2400.0, top=452, coin_at=(330, 470)):
    """A REAL game frame at `phase` — biome sky, mountains, the baked sidewalk
    floor and its wet/snow state — with `draw_fn` painting the piece onto the
    deck, live weather particles over the top, and the gold coin for reference.
    Cropped to the sidewalk band."""
    pal = _biome.palette_for_phase(phase)
    frame = pygame.Surface((W, H))
    sky = _draw.get_sky_surface_biome(W, H, GROUND_Y, pal, _biome.phase_bucket(phase))
    frame.blit(sky, (0, 0))
    _draw.draw_mountains(frame, scroll, GROUND_Y, W, phase=phase)

    wx = _weather_for(phase)
    wetness = wx.wetness if wet is None else wet
    snow_cover = wx.snow_cover if snow is None else snow
    _fg.draw_foreground_floor(frame, scroll, pal, phase)
    _fg.draw_ground_weather(frame, scroll, pal, wetness, snow_cover)

    draw_fn(frame, pal)

    if particles:
        wx.draw(frame)
    _gold_coin(frame, coin_at[0], coin_at[1])
    return frame.subsurface(pygame.Rect(0, top, W, H - top)).copy()


def _set_live_weather(phase):
    """Point the promenade's module-level weather state at `phase` so anything
    that leans on it (umbrella tilt, brolly gate) behaves as it would in play."""
    _fp._CUR_RAIN = _wx.rain_intensity(phase)
    _fp._CUR_SNOW = _wx.storm_intensity(phase)
    _fp._CUR_WIND = _wx.wind_intensity(phase)
    _fp._CUR_PHASE = phase


PHASE_STORM = 0.63
PHASE_SNOW = 0.87
PHASE_DUSK = 0.54
PHASE_DAY = 0.06
PHASE_SUNRISE = 0.94

T = 3.7        # a single animation time so every piece is sampled mid-motion


def _row(sheet, y, idx, title, thesis, cells, ctx, notes, *, h=250):
    """One piece per row: title + thesis on the left, 3x zoom cells in the
    middle, the 1x in-context game strip on the right."""
    pad = 14
    pygame.draw.rect(sheet, PANEL_BG, (pad, y, sheet.get_width() - pad * 2, h),
                     border_radius=6)
    pygame.draw.rect(sheet, (64, 70, 88), (pad, y, sheet.get_width() - pad * 2, h),
                     1, border_radius=6)
    _text(sheet, f"{idx}.  {title}", pad + 12, y + 8, 15, (250, 224, 150), bold=True)
    ty = _wrap(sheet, thesis, pad + 12, y + 30, 250, 10, (188, 198, 214))
    _wrap(sheet, notes, pad + 12, ty + 6, 250, 9, (140, 150, 168), lh=11)

    cx = pad + 278
    for cell in cells:
        cell(sheet, cx, y + 30)
        cx += cell.width + 10

    strip = ctx()
    sx = sheet.get_width() - pad - 12 - strip.get_width()
    sheet.blit(strip, (sx, y + 26))
    pygame.draw.rect(sheet, (86, 94, 116),
                     (sx, y + 26, strip.get_width(), strip.get_height()), 1)
    _text(sheet, "1x IN CONTEXT — real game frame (sky + mountains + baked "
                 "sidewalk + live weather)", sx, y + 26 + strip.get_height() + 3, 9,
          (150, 162, 182))
    return y + h + 10


class _Cell:
    """A deferred zoom cell so a row can lay out its own widths."""

    def __init__(self, caption, fn, *, night, deck, w=108, h=180, zoom=3,
                 feet_frac=0.80):
        self.caption = caption
        self.fn = fn
        self.night = night
        self.deck = deck
        self.width = w
        self.height = h
        self.zoom = zoom
        self.feet_frac = feet_frac

    def __call__(self, parent, x, y):
        _zoom_cell(parent, x, y, self.width, self.height, self.caption, self.fn,
                   night=self.night, deck=self.deck, zoom=self.zoom,
                   feet_frac=self.feet_frac)


def render():
    sheet_w = 1780
    rows_h = [260, 292, 236, 250, 268, 236]
    sheet_h = 74 + sum(h + 10 for h in rows_h) + 16
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill(SHEET_BG)
    _text(sheet, "WEEKEND STREET KIT — ROUND 1", 16, 12, 22, (255, 232, 170), bold=True)
    _text(sheet, "Six net-new procedural pieces for the approved weekend sidewalk "
                 "(DAY_PLAN_WEEKEND §8 + §14).  3x zoom detail (nearest-neighbour, "
                 "no smoothing) + 1x on a real game frame at the phase each piece "
                 "actually lives at.  Gold coin in every strip as the brightness "
                 "yardstick.", 16, 42, 11, (170, 180, 198))

    y = 74
    storm_night = _fp._nightf(_biome.palette_for_phase(PHASE_STORM))
    snow_night = _fp._nightf(_biome.palette_for_phase(PHASE_SNOW))
    dusk_night = _fp._nightf(_biome.palette_for_phase(PHASE_DUSK))
    day_night = _fp._nightf(_biome.palette_for_phase(PHASE_DAY))
    dawn_night = _fp._nightf(_biome.palette_for_phase(PHASE_SUNRISE))

    DECK_DAY = (176, 150, 118)
    DECK_STORM = (62, 66, 88)
    DECK_SNOW = (92, 100, 122)
    DECK_DUSK = (86, 78, 104)
    DECK_DAWN = (150, 134, 132)

    # ── 1 · SUOYI ──────────────────────────────────────────────────────────
    def _cur_pole(s, cx, gy):
        v = _fv.get("pedestrian", 30)      # ARCH 6 carrying-pole vendor, conical hat
        if v is not None:
            _ped._draw_one(s, cx, gy, _biome.palette_for_phase(PHASE_STORM), v,
                           storm_night, T)

    cells1 = [
        _Cell("CURRENT · pole vendor,\nno cape (storm)",
              lambda s, cx, gy: _cur_pole(s, cx, gy),
              night=storm_night, deck=DECK_STORM, w=126, h=174),
        _Cell("SUOYI · shoulder pole\n(the primary)",
              lambda s, cx, gy: draw_suoyi(s, cx, gy, 0.0, T, carry="pole"),
              night=0.0, deck=DECK_DAY, w=126, h=174),
        _Cell("SUOYI · storm night\n(warm straw vs cool street)",
              lambda s, cx, gy: draw_suoyi(s, cx, gy, storm_night, T, carry="pole"),
              night=storm_night, deck=DECK_STORM, w=126, h=174),
        _Cell("SUOYI · crate carry\n(hands still free)",
              lambda s, cx, gy: draw_suoyi(s, cx, gy, storm_night, T + 0.9,
                                           carry="crate"),
              night=storm_night, deck=DECK_STORM, w=126, h=174),
    ]

    def _ctx1():
        _set_live_weather(PHASE_STORM)

        def paint(frame, pal):
            n = _fp._nightf(pal)
            gy = _fp.GROUND_Y - 1
            draw_suoyi(frame, 46, gy, n, T, carry="pole")
            draw_suoyi(frame, 112, gy, n, T + 1.4, carry="crate", height=0.94)
            draw_suoyi(frame, 196, gy, n, T + 2.6, carry="pole", height=1.05,
                       build=1.08)
            v = _fv.get("pedestrian", 45)   # a shipped rain umbrella, for scale
            if v is not None:
                _ped._draw_one(frame, 262, gy, pal, v, n, T)
        return _context(PHASE_STORM, paint)

    y = _row(sheet, y, 1, "SUOYI — palm-fibre straw rain-cape",
             "The signature storm silhouette. A shaggy 12x10 trapezoid flaring "
             "where every other pedestrian tapers, a 3px ragged fringe that turns "
             "the hem into a comb, and shoulder spikes proud of the cape top (the "
             "sources' \"clumsy hedgehog\"). Worn with the shipped conical hat.",
             cells1, _ctx1,
             "Construction: cape drawn between torso and shoulder-pole so the pole "
             "rides OVER the straw. Asymmetric edge notches; per-strand kinked "
             "fibre lines; brim-underside shadow so hat and cape never fuse. "
             "Straw retints ~34% vs cloth's 55% — warm-vs-cool is the night read. "
             "Because the suoyi frees both hands, this figure is always carrying.",
             h=rows_h[0])

    # ── 2 · WINTER SET ─────────────────────────────────────────────────────
    def _cur_padded(s, cx, gy):
        v = _fv.get("pedestrian", 21)      # ARCH 4 shipped padded coat
        if v is not None:
            _ped._draw_one(s, cx, gy, _biome.palette_for_phase(PHASE_SNOW), v,
                           snow_night, T)

    def _puff_strip(s, cx, gy):
        """The breath puff's whole 0.8s life, sampled four times across one cell —
        spawn, bloom, drift, gone."""
        for i, ft in enumerate((0.02, 0.22, 0.48, 0.74)):
            xx = cx - 15 + i * 10
            pygame.draw.line(s, _shade(DECK_SNOW, -40), (xx, gy - 2), (xx, gy), 1)
            _breath_puff(s, xx, gy - 14, ft, phase=0.0, wind=1.0,
                         period=_BREATH_PERIOD)

    cells2 = [
        _Cell("CURRENT · shipped\npadded coat (A_PADDED)",
              lambda s, cx, gy: _cur_padded(s, cx, gy),
              night=snow_night, deck=DECK_SNOW, w=102, h=174),
        _Cell("COAT · +2px/side, 3 stitch\nbands, sleeve roll, collar",
              lambda s, cx, gy: draw_winter_figure(s, cx, gy, 0.0, T,
                                                   coat="indigo", scarf="stream",
                                                   breath=False),
              night=0.0, deck=DECK_DAY, w=102, h=174),
        _Cell("SCARF A · STREAM\n(ribbon + forked tip)",
              lambda s, cx, gy: draw_winter_figure(s, cx, gy, snow_night, T,
                                                   coat="indigo", scarf="stream",
                                                   storm=1.0),
              night=snow_night, deck=DECK_SNOW, w=102, h=174),
        _Cell("SCARF B · DRAPE\n(vertical fall + fringe)",
              lambda s, cx, gy: draw_winter_figure(s, cx, gy, snow_night, T + 0.6,
                                                   coat="rust", scarf="drape",
                                                   storm=0.15),
              night=snow_night, deck=DECK_SNOW, w=102, h=174),
        _Cell("POSTURE · tucked + upstream\nlean (head -1, stride -20%)",
              lambda s, cx, gy: draw_winter_figure(s, cx, gy, snow_night, T + 1.2,
                                                   coat="rust", scarf="stream",
                                                   tucked=True, upstream=True),
              night=snow_night, deck=DECK_SNOW, w=102, h=174),
        _Cell("BREATH · one 0.8s life,\n4 samples (_snow_flake cache)",
              _puff_strip, night=snow_night, deck=DECK_SNOW, w=126, h=174,
              feet_frac=0.86),
        _Cell("DOG · lower puff,\n1.4s cycle",
              lambda s, cx, gy: draw_winter_dog(s, cx, gy, snow_night, T,
                                                phase=0.3),
              night=snow_night, deck=DECK_SNOW, w=102, h=174),
    ]

    def _ctx2():
        _set_live_weather(PHASE_SNOW)

        def paint(frame, pal):
            n = _fp._nightf(pal)
            gy = _fp.GROUND_Y - 1
            draw_winter_figure(frame, 40, gy, n, T, coat="indigo",
                               scarf="stream", phase=0.0)
            draw_winter_figure(frame, 96, gy, n, T + 0.9, coat="rust",
                               scarf="drape", storm=0.2, phase=1.1, height=0.94)
            draw_winter_dog(frame, 150, gy, n, T + 0.4, phase=0.6)
            draw_winter_figure(frame, 214, gy, n, T + 1.8, coat="rust",
                               scarf="stream", upstream=True, phase=2.0)
            draw_winter_figure(frame, 268, gy, n, T + 2.5, coat="indigo",
                               scarf="stream", height=0.66, build=0.92, phase=0.7)
        return _context(PHASE_SNOW, paint)

    y = _row(sheet, y, 2, "WINTER OVERLAY SET — coat · scarf · breath · posture",
             "Four stackable sub-pieces. The coat goes 8px wide to 14px with a "
             "ROUNDED outline, because at this size \"padded\" is a width and a "
             "corner radius. The two scarf states are different CONSTRUCTIONS — a "
             "horizontal forked ribbon vs a vertical folded fall — not one "
             "amplitude knob.",
             cells2, _ctx2,
             "Hands tucked in opposite sleeves reads as one sleeve ROLL with a dark "
             "mouth at each end and a lit top edge. Collar drawn AFTER the head so "
             "it covers the chin. Breath puffs blit weather._snow_flake straight "
             "out of the live cache — one blit, no new art, and they quantise "
             "alpha the same way the falling snow does. Dogs get a lower, faster "
             "puff.",
             h=rows_h[1])

    # ── 3 · UMBRELLA ───────────────────────────────────────────────────────
    def _cur_umb(s, cx, gy):
        _fp._CUR_WIND = 0.4
        _fp._draw_umbrella(s, cx, gy - 22, 1, night=0.0, scale=1.6, pole_len=20)

    cells3 = [
        _Cell("CURRENT · flat-disc\ncanopy (3 ribs)",
              _cur_umb, night=0.0, deck=DECK_DAY, w=126, h=132, feet_frac=0.92),
        _Cell("NEW · 8 ribs, alternating\npanels, scalloped per rib",
              lambda s, cx, gy: draw_umbrella8(s, cx, gy - 22, 1, night=0.0,
                                               scale=1.6, pole_len=20, wind=0.4),
              night=0.0, deck=DECK_DAY, w=126, h=132, feet_frac=0.92),
        _Cell("NEW · dusk, night-capped\n(_UMBRELLA_COLORS kept)",
              lambda s, cx, gy: draw_umbrella8(s, cx, gy - 22, 0, night=dusk_night,
                                               scale=1.6, pole_len=20, wind=0.4),
              night=dusk_night, deck=DECK_DUSK, w=126, h=132, feet_frac=0.92),
        _Cell("NEW · storm tilt\n(rain>0.6, 4px lateral)",
              lambda s, cx, gy: draw_umbrella8(s, cx, gy - 22, 3, night=storm_night,
                                               scale=1.6, pole_len=20, wind=1.3),
              night=storm_night, deck=DECK_STORM, w=126, h=132, feet_frac=0.92),
        _Cell("NEW · kid's 6px,\nheld crooked",
              lambda s, cx, gy: draw_umbrella8(s, cx, gy - 16, 2, night=0.0,
                                               scale=1.1, pole_len=14, wind=0.3,
                                               crooked=0.8),
              night=0.0, deck=DECK_DAY, w=126, h=132, feet_frac=0.92),
        _Cell("1x TRUE SIZE — five\ncanopies as they ship",
              lambda s, cx, gy: [draw_umbrella8(s, cx - 26 + i * 13, gy - 12, i,
                                                night=dusk_night, scale=0.75,
                                                pole_len=10, wind=0.5)
                                 for i in range(5)] and None,
              night=dusk_night, deck=DECK_DUSK, w=126, h=132, feet_frac=0.92,
              zoom=1),
    ]

    def _ctx3():
        _set_live_weather(PHASE_DUSK)

        def paint(frame, pal):
            n = _fp._nightf(pal)
            gy = _fp.GROUND_Y - 1
            for i, (xx, vi) in enumerate(((44, 45), (108, 46), (176, 47),
                                          (250, 45), (312, 46))):
                v = _fv.get("pedestrian", vi)
                if v is None:
                    continue
                _ped._draw_one(frame, xx, gy, pal, v, n, T + i * 0.7)
                # Overpaint the shipped canopy with the 8-rib one at the same
                # anchor the body drawer uses, so this is a true before/after.
                g = _Geom(gy)
                draw_umbrella8(frame, xx, g.head_cy - int(g.head_r * 2.7), i,
                               night=n, scale=1.0, pole_len=9,
                               wind=_fp._CUR_WIND)
        return _context(PHASE_DUSK, paint)

    y = _row(sheet, y, 3, "8-RIB OIL-PAPER UMBRELLA",
             "The canopy is cut as triangular panels pegged to steamed bamboo "
             "ribs, so it is a fan, not a dome. Rib lines alone die at 16px, so "
             "the radial read is carried by alternating panel VALUE (an area cue) "
             "backed by the 1px rib on every boundary — and the hem scallops once "
             "per rib, so the outline counts the ribs by itself.",
             cells3, _ctx3,
             "Keeps _UMBRELLA_COLORS, the night cap and the _CUR_WIND downwind "
             "lean exactly as shipped; only the canopy geometry changes. 2px "
             "finial with a 1px spike above it. The kid variant tilts the canopy "
             "off the pole axis rather than just shrinking it.",
             h=rows_h[2])

    # ── 4 · CART ───────────────────────────────────────────────────────────
    def _wheel_detail(s, cx, gy):
        _spoked_wheel(s, cx - 7, gy - 5, 4, 0.0)
        _spoked_wheel(s, cx + 5, gy - 5, 4, 0.0, spin=0.5)
        _spoked_wheel(s, cx + 15, gy - 4, 3, 0.0, far=True)

    cells4 = [
        _Cell("WHEEL PRIMITIVE (6x)\nnear · turned · far",
              _wheel_detail, night=0.0, deck=DECK_DAY, w=150, h=96, zoom=6,
              feet_frac=0.80),
        _Cell("LOADED · bed level, handles\nup, poles + awning + crate",
              lambda s, cx, gy: draw_cart_folded(s, cx, gy, 0.0, T, load="loaded"),
              night=0.0, deck=DECK_DAY, w=150, h=132, feet_frac=0.86),
        _Cell("HALF · TIPPED to unload,\nwedge outline, basket down",
              lambda s, cx, gy: draw_cart_folded(s, cx, gy, 0.0, T, load="half"),
              night=0.0, deck=DECK_DAY, w=150, h=132, feet_frac=0.86),
        _Cell("EMPTY · PARKED, handles on\nthe deck, bare slats",
              lambda s, cx, gy: draw_cart_folded(s, cx, gy, 0.0, T, load="empty"),
              night=0.0, deck=DECK_DAY, w=150, h=132, feet_frac=0.86),
    ]

    def _ctx4():
        _set_live_weather(PHASE_DAY)

        def paint(frame, pal):
            n = _fp._nightf(pal)
            gy = _fp.GROUND_Y - 1
            draw_cart_folded(frame, 52, gy, n, T, load="loaded")
            draw_cart_folded(frame, 158, gy, n, T, load="half")
            draw_cart_folded(frame, 266, gy, n, T, load="empty")
            v = _fv.get("pedestrian", 30)
            if v is not None:
                _ped._draw_one(frame, 106, gy, pal, v, n, T)     # for scale
            v2 = _fv.get("pedestrian", 12)
            if v2 is not None:
                _ped._draw_one(frame, 212, gy, pal, v2, n, T + 1.1)
        return _context(PHASE_DAY, paint, particles=False)

    y = _row(sheet, y, 4, "`_cart_folded` — two-wheeled market handcart",
             "~26px, three load states that are three different CONSTRUCTIONS, "
             "not one cart with things deleted: a level bar in transit, a tipped "
             "wedge mid-unload, and a nose-down parked triangle. Each has its own "
             "bed angle, ground contact and mass distribution.",
             cells4, _ctx4,
             "NEW spoked-wheel primitive, built inside-out: dark iron tyre, light "
             "interior reading as the gap, THREE full-diameter spokes (eight fills "
             "an 8px disc solid), 1px hub. The off-side wheel is 1px smaller, one "
             "value darker and offset up-right — that pair is what makes a side-on "
             "cart read as two-wheeled. Crate / rolled-awning / basket / mat parts "
             "echo props_cast.draw_dressing so the town's woodwork matches.",
             h=rows_h[3])

    # ── 5 · STALL TARP ─────────────────────────────────────────────────────
    def _cur_stall(s, cx, gy):
        _food.stall_steamer(s, cx, gy, storm_night, T)

    cells5 = [
        _Cell("CURRENT · open steamer stall\nin the storm (flat awning)",
              _cur_stall, night=storm_night, deck=DECK_STORM, w=180, h=204,
              feet_frac=0.90),
        _Cell("NEW · pitched tarp, runoff off the low\ncorner, vendor folded, still steaming",
              lambda s, cx, gy: draw_stall_tarp(s, cx, gy, storm_night, T),
              night=storm_night, deck=DECK_STORM, w=180, h=204, feet_frac=0.90),
        _Cell("NEW · daylight read\n(pitch + lashings legible)",
              lambda s, cx, gy: draw_stall_tarp(s, cx, gy, 0.0, T + 0.5),
              night=0.0, deck=DECK_DAY, w=180, h=204, feet_frac=0.90),
    ]

    def _ctx5():
        _set_live_weather(PHASE_STORM)

        def paint(frame, pal):
            n = _fp._nightf(pal)
            gy = _fp.GROUND_Y - 1
            draw_stall_tarp(frame, 74, gy, n, T)
            draw_suoyi(frame, 150, gy, n, T + 1.7, carry="pole")
            draw_stall_tarp(frame, 250, gy, n, T + 0.8)
        return _context(PHASE_STORM, paint)

    y = _row(sheet, y, 5, "`_stall_tarp` — the pitched rain sheet",
             "Vendors pitch tarps on purpose: a flat sheet pools, sags and dumps, "
             "so the working answer is a taut sheet with one low corner. The slope "
             "IS the storytelling. High corner upwind, low corner downwind — the "
             "same direction the umbrellas lean, so the street agrees with itself "
             "about the weather.",
             cells5, _ctx5,
             "Built on food_stalls._stall_shell with roof=False — the tarp replaces "
             "the awning rather than sitting on it. Rope turns at both post tops "
             "plus one taut guy to the deck; fold ticks across the slope; a "
             "translucent shadow underneath so the vendor sits in a cave. Runoff is "
             "travelling 1px dashes + a hanging bead + a breathing splash ellipse. "
             "Steam and the capped brazier glow stay on: THIS STALL IS OPEN.",
             h=rows_h[4])

    # ── 6 · SWEEPER ────────────────────────────────────────────────────────
    cells6 = [
        _Cell("GAIT A · full push\n(k=1, back leg out)",
              lambda s, cx, gy: draw_sweeper(s, cx, gy, 0.0, 0.44),
              night=0.0, deck=DECK_DAWN, w=126, h=150, feet_frac=0.84),
        _Cell("GAIT B · recover\n(k=0, upright, feet in)",
              lambda s, cx, gy: draw_sweeper(s, cx, gy, 0.0, 1.62),
              night=0.0, deck=DECK_DAWN, w=126, h=150, feet_frac=0.84),
        _Cell("BESOM HEAD (6x) — split-bamboo\nfan, wire binding",
              lambda s, cx, gy: draw_sweeper(s, cx + 8, gy, 0.0, 0.44),
              night=0.0, deck=DECK_DAWN, w=180, h=126, zoom=6, feet_frac=0.86),
        _Cell("SUNRISE TINT · the correct\nfirst inhabitant of a morning",
              lambda s, cx, gy: draw_sweeper(s, cx, gy, dawn_night, 0.30),
              night=dawn_night, deck=DECK_DAWN, w=126, h=150, feet_frac=0.84),
    ]

    def _ctx6():
        _set_live_weather(PHASE_SUNRISE)

        def paint(frame, pal):
            n = _fp._nightf(pal)
            gy = _fp.GROUND_Y - 1
            draw_sweeper(frame, 54, gy, n, T, phase=0.0)
            draw_sweeper(frame, 158, gy, n, T, phase=0.9, coat=(126, 104, 92))
            draw_winter_figure(frame, 236, gy, n, T + 0.6, coat="indigo",
                               scarf="drape", storm=0.15, tucked=False, phase=0.4)
            draw_cart_folded(frame, 306, gy, n, T, load="empty")
        return _context(PHASE_SUNRISE, paint)

    y = _row(sheet, y, 6, "`_sweeper` — the morning street sweeper",
             "The broom sweeping a street at 6am is a BESOM: a fan of split "
             "bamboo twigs wire-bound to a shaft. That splayed triangle at the end "
             "of a 14px diagonal is legible where a flat brush head is not. The "
             "1.8s cycle is deliberately asymmetric — a fast eased push, a slower "
             "recover — because a symmetric sine reads as a metronome, not work.",
             cells6, _ctx6,
             "_draw_bench_person body idiom, so he matches the bench couple in "
             "scale and palette. The back leg extends on the push, so the two gait "
             "frames differ in stance width as well as arm angle. The pile nudges "
             "forward with the stroke and puffs at full extension (the breath-puff "
             "helper, reused).",
             h=rows_h[5])

    out = "/home/user/skybit/docs/sidewalk_overhaul/art/weekend_kit/round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())


def main():
    render()


if __name__ == "__main__":
    main()
