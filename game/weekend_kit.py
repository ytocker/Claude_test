"""The weekend street kit — art-director-approved procedural pieces.

Six pieces commissioned by the weekend day plan (docs/sidewalk_overhaul/
DAY_PLAN_WEEKEND.md §14) and matured through the design loop
(docs/sidewalk_overhaul/art/weekend_kit/, SHIP-READY at round 2):

  * draw_suoyi          — the storm's signature straw rain-cape figure
  * draw_winter_figure  — padded coat + scarf + breath puffs (snow dress)
  * draw_winter_dog     — a dog with breath in the cold
  * draw_umbrella8      — the ribbed oil-paper umbrella canopy
  * draw_cart_folded    — the market handcart (loaded / half / empty)
  * draw_stall_tarp     — a tarped-over stall, open despite the rain
  * draw_sweeper        — the first inhabitant of the morning

All values here were pixel-measured against real frames in both lanes; the
night pieces hold the glow contract (composite <= the 146 cap, coin brightest).
"""
from __future__ import annotations

import math

import pygame

from game import animals_cast as _animals
from game import food_stalls as _food
from game import ped_cast as _ped
from game import props_cast as _props
from game import weather as _wx
from game import foreground_variants as _fv
from game.foreground_props import _mix, _shade

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
    """Straw cools toward a WARM DARK, not toward the cool street.

    Cloth retints toward (54,64,96) — the night ground band — which parks a tan
    at a mid grey. Soaked palm fibre goes the other way: it darkens and stays
    brown. Mixing toward (58,46,38) buys both channels at once — the hue stays
    warm (R-B holds ~40 at full night where retinted cloth holds ~10, so the
    piece survives a colourblind viewing) and the VALUE drops clear of the bright
    577-594 band every far-lane figure is silhouetted against."""
    if night <= 0.05:
        return col
    return _mix(col, (58, 46, 38), min(0.52, 0.40 * night + 0.12))


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


def _conical_hat(surf, hx, hy, head_r, night, *, col=(198, 162, 96), drip_t=None,
                 brim_w=None, lift=0):
    """The shipped ped_cast `hat == "conical"` cone, widened and lit.

    `brim_w` defaults to head_r*3 (the shipped cone is 2.5) so the douli
    overhangs the shoulders — a wide flat triangle over a bell is an outline
    shared with nothing else in the cast. `lift` raises the brim off the crown,
    which is what buys the face rows between brim and cape.

    The cone carries the figure's SINGLE BRIGHTEST value on its left (lit) slope:
    at 18px a viewer reads "person" off the head, so the focal accent belongs
    there and not in the middle of the cape. Below it a 1px brim-underside
    shadow, without which tan brim and tan cape fuse into one mass at night."""
    c = _straw(col, night)
    if brim_w is None:
        brim_w = int(head_r * 3)
    by = hy - head_r * 0.15 - lift
    apex = (hx, hy - head_r * 1.8 - lift)
    cone = [(hx - brim_w, by), apex, (hx + brim_w, by)]
    pygame.draw.polygon(surf, c, cone)
    # Lit slope: upwind side of the cone catches what light there is.
    pygame.draw.line(surf, _cap150(_shade(c, 34)), (hx - brim_w + 2, by - 1),
                     (apex[0] - 1, apex[1] + 2), 1)
    pygame.draw.polygon(surf, _shade(c, -34), cone, 1)
    pygame.draw.line(surf, _shade(c, -50), (hx - brim_w + 1, by + 1),
                     (hx + brim_w - 1, by + 1), 1)
    if drip_t is not None:
        wet = _straw((150, 170, 190), night)
        for i, ex in enumerate((hx - brim_w, hx + brim_w - 1)):
            ph = ((drip_t * 1.6) + i * 0.5) % 1.0
            dy = int(by + 1 + ph * 7)
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
# This is its own ARCHETYPE, not an accessory flag: the cape replaces the torso
# shape, moves the hem line, changes how much leg is exposed and constrains what
# the hands can carry — four things at once, which is what an arch key is for.
#
# Four devices carry it at scale, in order of importance:
#   1. a hem 13px wide on an 8px-wide body — the outline FLARES where every other
#      pedestrian tapers, so the class read is pure silhouette
#   2. a THREE-BAND value structure — 2px lit shoulder / mid body / dark fringe
#      comb — running across the shape, never down it. Vertical 1px alternation
#      at this size is temporal aliasing: a 160px/s scroll turns it into crawl.
#   3. shoulder spikes proud of the cape top, the "hedgehog" cue that separates a
#      suoyi from a plain cloak in one glance
#   4. a wide douli overhanging the narrow shoulders, so the outline is two
#      stacked triangles — a shape nothing else in the game makes

# Base tan pitched so the night retint lands the cape BODY at L 85-95: below the
# 173-luma storm band the far lane silhouettes it against, and equally clear of
# the 56-luma near deck in the other direction.
_STRAW = (150, 132, 84)
_STRAW_DK = (104, 88, 52)        # fringe comb + outline
_STRAW_MID = (132, 114, 70)      # the second interior value (<=22 luma under body)
_STRAW_HI = (186, 168, 116)      # the 2px shoulder catch-light


def draw_suoyi(surf, cx, base_y, night, t, *, carry="crate", height=1.0,
               build=1.0, coat=(96, 84, 70), rain=1.0):
    """One suoyi figure: feet on `base_y`, centred on `cx`. `carry` selects what
    the freed hands are doing — 'crate' (a crate hugged at the chest; the primary,
    because it leaves the cape's flare completely unobstructed), 'pole' (the ~30%
    secondary: a short shoulder pole with the bundles hung ABOVE the hem), 'none'."""
    g = _Geom(base_y, height, build)
    straw = _straw(_STRAW, night)
    straw_dk = _straw(_STRAW_DK, night)
    straw_mid = _straw(_STRAW_MID, night)
    straw_hi = _straw(_STRAW_HI, night)
    cloth = _retint(coat, night)
    cloth_dk = _shade(cloth, -30)

    gait = math.sin(t * 1.5)

    # Legs + a stub of trouser show below the cape — without them the cape reads
    # as a bell hanging in the air rather than as something a person is worn by.
    _ped._legs(surf, cx, g.body_w, g.torso_bot, g.ground, gait, False,
               cloth_dk, _shade(cloth_dk, -30), False)
    pygame.draw.rect(surf, cloth, (cx - g.body_w + 1, g.torso_top, g.body_w * 2 - 2,
                                   g.torso_h))

    # ── the cape ──
    # Shoulder line sits one row BELOW the head's bottom so the face is not
    # swallowed, and the cape is short enough that the hem clears the knee: the
    # flare read lives at the WAIST, so the shin can stay free to stride.
    sh_y = g.torso_top + 1
    cape_h = 7
    hem_y = sh_y + cape_h
    ht, hb = 3, 6                       # half-width at neck / at hem

    # Deliberately ASYMMETRIC notches down each edge: a hand-bundled fibre cape
    # is never mirror-symmetric, and the asymmetry is what stops the shape
    # reading as a machine-drawn trapezoid at 3x.
    left = [(cx - ht, sh_y), (cx - ht - 2, sh_y + 2), (cx - ht - 1, sh_y + 4),
            (cx - hb, sh_y + 5), (cx - hb, hem_y)]
    right = [(cx + hb, hem_y), (cx + hb, sh_y + 6), (cx + ht + 2, sh_y + 4),
             (cx + ht + 2, sh_y + 1), (cx + ht, sh_y)]
    pygame.draw.polygon(surf, straw, left + right)

    # Interior: TWO values only, and they band HORIZONTALLY. The lower third of
    # the cape sits one step down from the body — fibre hanging in shadow under
    # its own bulk — so the texture is a value band the eye integrates at 1x,
    # not a 1px comb that shimmers under scroll.
    pygame.draw.polygon(surf, straw_mid, [
        (cx - hb + 1, hem_y - 2), (cx + hb - 1, hem_y - 2),
        (cx + hb - 1, hem_y - 1), (cx - hb + 1, hem_y - 1)])
    # Two short dark seams break the band without ever alternating pixel-to-pixel.
    for sxp in (cx - 2, cx + 3):
        pygame.draw.line(surf, straw_dk, (sxp, sh_y + 3), (sxp, hem_y - 1), 1)

    # The cape's single bright value: a 2px catch-light across the shoulder top,
    # where a cape actually takes light. Still one step under the hat's lit cone,
    # which is where the figure's brightest pixel belongs.
    pygame.draw.line(surf, straw_hi, (cx - ht - 1, sh_y), (cx + ht + 1, sh_y), 1)
    pygame.draw.line(surf, straw_hi, (cx - ht, sh_y + 1), (cx + ht, sh_y + 1), 1)

    pygame.draw.polygon(surf, straw_dk, left + right, 1)

    # Shoulder spikes — the hedgehog cue, proud of the cape top.
    for i, sxp in enumerate((cx - ht - 1, cx - 1, cx + 2, cx + ht + 1)):
        pygame.draw.line(surf, straw_dk, (sxp, sh_y), (sxp - 1, sh_y - 1 - (i % 2)), 1)

    # Ragged 1-2px fringe: every hem pixel gets its own tooth length, so the
    # bottom edge is a comb, not a line — and it is the DARK band of the three,
    # which is what keeps the hem readable against a bright far-lane deck.
    for i, sxp in enumerate(range(cx - hb, cx + hb + 1)):
        ln = 2 if i % 3 else 1
        pygame.draw.line(surf, straw_dk, (sxp, hem_y), (sxp, hem_y + ln - 1), 1)

    hx, hy = cx, g.head_cy
    skin = _retint(_ped.SKIN_TONES["tan"], night)
    pygame.draw.circle(surf, skin, (hx, hy), g.head_r)
    pygame.draw.circle(surf, _shade(skin, -28), (hx, hy), g.head_r, 1)
    # Neck notch pulled UP against the jaw so it shades the throat instead of
    # eating the face rows the brim lift just bought.
    pygame.draw.line(surf, _shade(straw_dk, -22), (cx - 1, sh_y - 1), (cx + 1, sh_y - 1), 1)

    # ── what the freed hands are doing ──
    if carry == "pole":
        # The pole rides ON TOP of the cape and is deliberately SHORT (±8, near
        # the shipped A_POLE reach): a wider one puts the bundles straight through
        # the cape's flare, which is the only silhouette this piece has. The
        # bundles hang from the raised end of the pole so they clear the hem.
        pole = _retint((120, 88, 54), night)
        py = sh_y - 3
        x0, x1 = cx - 8, cx + 8
        pygame.draw.line(surf, pole, (x0, py + 2), (x1, py - 2), 2)
        for ex, ey in ((x0, py + 2), (x1, py - 2)):
            wrap = _retint((150, 120, 78), night)
            pygame.draw.line(surf, wrap, (ex, ey), (ex, ey + 1), 1)
            br = pygame.Rect(ex - 2, ey + 2, 5, 4)
            pygame.draw.ellipse(surf, _straw((176, 132, 78), night), br)
            pygame.draw.ellipse(surf, _shade(_straw((176, 132, 78), night), -30), br, 1)
    elif carry == "crate":
        # Held at the CHEST, clear of the hem: the fringe comb is the piece's
        # bottom edge and nothing may sit on it.
        wood = _retint((146, 104, 62), night)
        r = pygame.Rect(cx - 4, sh_y + 2, 8, 4)
        pygame.draw.rect(surf, _shade(wood, -28), r)
        pygame.draw.rect(surf, wood, r.inflate(-2, -2))
        pygame.draw.line(surf, _shade(wood, -28), (r.left, r.centery), (r.right, r.centery), 1)
        # Two straw forearms clamped over the crate so the cape reads as being
        # WORN over working arms, not draped on a rack.
        for sgn in (-1, 1):
            pygame.draw.line(surf, straw_dk, (cx + sgn * 6, sh_y + 2),
                             (cx + sgn * 4, sh_y + 5), 2)

    # brim_w = head_r*3 (13px across at height 1.0) over 7-10px shoulders, and
    # the brim lifted clear of the crown so three face rows survive under it.
    _conical_hat(surf, hx, hy, g.head_r, night, lift=2,
                 drip_t=t if rain > 0.4 else None)


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


_BREATH_RIM = (58, 74, 104)     # cool dark, the standard keyline under white VFX
_BREATH_CACHE = {}


def _breath_sprite(r, a):
    """A rimmed breath puff, cached on the same (radius, 16-step alpha) key the
    snowflake cache uses — so this stays one blit per puff, and the rim never
    costs a per-frame alpha surface. The keyline goes on its own layer because
    the deck it lands on is an opaque Surface: a 4-tuple straight into
    pygame.draw would come out solid."""
    abucket = max(16, min(255, (int(a) // 16) * 16))
    key = (int(r), abucket)
    hit = _BREATH_CACHE.get(key)
    if hit is not None:
        return hit
    core = _wx._snow_flake(r, abucket)
    d = max(core.get_width(), (r + 1) * 2 + 2)
    spr = pygame.Surface((d, d), pygame.SRCALPHA)
    c = d // 2
    pygame.draw.circle(spr, (*_BREATH_RIM, min(190, int(abucket * 0.8))),
                       (c, c), r + 1, 1)
    spr.blit(core, (c - core.get_width() // 2, c - core.get_height() // 2))
    _BREATH_CACHE[key] = spr
    return spr


def _tinted_flake(r, a, tint):
    """The same cached disc, multiplied down to a dust tone. Swept grit lifting off
    a 225-luma sunrise deck must composite DARKER than the paving it came from —
    a white particle over a bright deck brightens it, and the coin owns the top of
    this street's range at every hour."""
    abucket = max(16, min(255, (int(a) // 16) * 16))
    key = (int(r), abucket, tint)
    hit = _BREATH_CACHE.get(key)
    if hit is not None:
        return hit
    spr = _wx._snow_flake(r, abucket).copy()
    spr.fill((*tint, 255), special_flags=pygame.BLEND_RGB_MULT)
    _BREATH_CACHE[key] = spr
    return spr


def _breath_puff(surf, x, y, t, *, phase=0.0, wind=1.0, period=_BREATH_PERIOD,
                 peak_a=150, base_a=96, rim=True, tint=None):
    """One breath puff: the live snowflake cache's soft white disc inside a 1px
    cool-dark rim.

    Three things this has to survive. It spawns OVER the figure's own dark hat
    and collar (the caller passes the head centre, not open air beside it), so
    its first and brightest frames have something to be white against — then it
    drifts clear as it fades, which is also how breath actually behaves. The 1px
    rim is what keeps it legible once it HAS drifted clear, because the snow-band
    backdrop it drifts onto measures 211 luma and a bare white disc on that is
    nothing. And the radius peaks EARLY then shrinks into the fade: a cloud that
    grows as it dies reads as a smoke ring, not as a breath dispersing.

    The core is still one cached blit with alpha quantised in the same 16-step
    buckets as the falling snow, so puff and snowfall stay one weather system."""
    ph = ((t + phase) % period) / period
    age = ph * period
    if age > _BREATH_LIFE:
        return
    f = age / _BREATH_LIFE
    a = int((base_a + (peak_a - base_a) * (1.0 - f)) * (1.0 - f * f))
    if a < 12:
        return
    # 1 → 3 → 1: a fast bloom in the first quarter, then a shrinking fade.
    r = 1 + int(round(3.0 * math.sin(min(1.0, f * 1.35) * math.pi) ** 0.7)) if f > 0.02 else 1
    r = max(1, min(3, r))
    if tint is not None:
        spr = _tinted_flake(r, a, tint)
    else:
        spr = _breath_sprite(r, a) if rim else _wx._snow_flake(r, a)
    dx = int(f * 9 * wind)
    dy = -int(f * 3)
    px, py = int(x + dx), int(y + dy)
    surf.blit(spr, (px - spr.get_width() // 2, py - spr.get_height() // 2))


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
    # A wider torso alone does NOT make a new silhouette class: put the hem in
    # the same place as a shipped tunic and the outline still tapers where every
    # other pedestrian's does. So the mianao's hem drops 3px BELOW torso_bot,
    # over the thigh, and ends SQUARE — the taper point moves down the figure,
    # which is the actual class change, and it is also what a padded coat does.
    pad = int(g.body_w * 1.35) + 2          # +2px each side over the shipped A_PADDED
    top = g.torso_top - g.head_r // 2 + head_drop
    hem_drop = 3
    r = pygame.Rect(cx - pad + lean, top, pad * 2,
                    g.torso_bot - top + 1 + hem_drop)
    pygame.draw.rect(surf, c, r, border_top_left_radius=3, border_top_right_radius=3)
    pygame.draw.rect(surf, c_dk, r, 1, border_top_left_radius=3,
                     border_top_right_radius=3)
    # Two bands, not three: six 1px lines in a 10px torso is a stripe fill and
    # the base colour never survives it. Two lets the coat's own tone hold the
    # middle, which is what makes the quilting read as relief rather than as
    # corduroy.
    for q in (0.30, 0.62):
        yy = int(r.top + r.height * q)
        pygame.draw.line(surf, c_dk, (r.left + 1, yy), (r.right - 2, yy), 1)
        pygame.draw.line(surf, c_hi, (r.left + 1, yy + 1), (r.right - 2, yy + 1), 1)
    # 1px hem band: the lit edge of the padded roll at the bottom of the coat,
    # and the thing that keeps the new squared hem from reading as a crop.
    pygame.draw.line(surf, c_hi, (r.left + 1, r.bottom - 2), (r.right - 2, r.bottom - 2), 1)
    pygame.draw.line(surf, _shade(c_dk, -18), (r.left + 1, r.bottom - 1),
                     (r.right - 2, r.bottom - 1), 1)

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
    # Cap sits ON the crown and the collar sits UNDER the jaw, so the cap's fur
    # line and the collar's fur line don't close on each other: every other
    # member of this cast reads as a person at 18px because a couple of rows of
    # face survive, and this one has to as well.
    hx = cx + lean
    hy = g.head_cy + head_drop
    pygame.draw.circle(surf, skin, (hx, hy), g.head_r)
    pygame.draw.circle(surf, _shade(skin, -28), (hx, hy), g.head_r, 1)
    cap = pygame.Rect(hx - g.head_r, hy - g.head_r * 2, g.head_r * 2,
                      int(g.head_r * 1.5))
    pygame.draw.ellipse(surf, c_dk, cap)
    pygame.draw.line(surf, fur_c, (hx - g.head_r, cap.bottom - 1),
                     (hx + g.head_r, cap.bottom - 1), 1)

    neck_y = hy + g.head_r
    _scarf(surf, hx, neck_y, night, col=_SCARVES.get(coat, (200, 92, 84)),
           style=scarf, storm=storm, t=t)

    collar = pygame.Rect(r.left + 1, neck_y, r.width - 2, 3)
    pygame.draw.ellipse(surf, fur_c, collar)
    pygame.draw.ellipse(surf, _shade(fur_c, -40), collar, 1)

    if breath:
        # Spawned ON the head — over the dark cap and collar — so the puff's
        # brightest frames have contrast, then it drifts clear as it fades.
        _breath_puff(surf, hx, hy, t, phase=phase, wind=storm)


def draw_winter_dog(surf, cx, base_y, night, t, *, variant=0, phase=0.0,
                    storm=1.0):
    """The shipped dog, plus its own breath — lower and on a faster 1.4s cycle
    than an adult's, which is the whole difference and reads instantly as a
    smaller, quicker animal."""
    v = _fv.get("dog", variant)
    if v is not None:
        _animals.draw_dog(surf, cx, base_y, v, night, t)
    # Muzzle-height and on a faster cycle than an adult's — same spawn-on-the-dark
    # rule, which for a dog means the head itself rather than the air in front.
    _breath_puff(surf, cx - 8, base_y - 11, t, phase=phase, wind=storm,
                 period=1.4, peak_a=132, base_a=84)


# ════════════════════════════════════════════════════════════════════════════
# PIECE 3 — THE 6-RIB OIL-PAPER UMBRELLA
# ════════════════════════════════════════════════════════════════════════════
#
# Research: the canopy is cut as TRIANGULAR SEGMENTS pegged to steamed bamboo
# ribs, so a real oil-paper umbrella is a fan of panels, not a dome.
#
# But the canopy is 17px across and 8px tall, and arithmetic decides how many
# ribs it can hold: 8 ribs is 2.1px of panel at the hem and 0 at the apex, which
# is not a renderable panel — it is a rib line touching a rib line. SIX ribs give
# ~2.8px at the hem and, crucially, room for an alternating panel FILL to exist
# between them. Three devices, in the order they survive downscaling:
#
#   1. panel VALUE — an AREA cue, so it is the one that reaches 1x. TWO of the
#      six wedges take a -20 step and the other four stay base, which keeps the
#      base colour the dominant tone: these are the rain chapter's only colour
#      accents and a darker canopy is a worse umbrella. Two shaded panels either
#      side of a lit centre is also how a tilted dome actually takes light.
#   2. hem scallops once per rib, so the SILHOUETTE counts the ribs even when the
#      interior washes out entirely. This is the part of round 1 that worked.
#   3. rib lines — last and weakest, so they are drawn ONLY on the four
#      boundaries of the two shaded wedges (never across a panel's interior,
#      which is what erased the panels last round) and only over the outer 45% of
#      the radius, because the inner 55% is where a radial fan's ribs converge
#      into a blot. Four visible lines, not nine.

def _umbrella_colors():
    # deferred: foreground_promenade imports THIS module, so the palette is
    # looked up at call time rather than import time to avoid the cycle
    from game import foreground_promenade as _fp
    return _fp._UMBRELLA_COLORS
_UMB_SHADED = (1, 4)        # the two wedges that take the -20 step


def draw_umbrella8(surf, cx, canopy_y, color_idx, *, night=0.0, scale=1.0,
                   pole_len=9, wind=0.0, ribs=6, crooked=0.0, color=None):
    """Drop-in replacement geometry for foreground_promenade._draw_umbrella.
    `crooked` tilts the whole canopy off the pole — the kid version, held wrong.
    `color` overrides the shared palette (a ped pool row's own canopy hue)."""
    if color is None:
        color = _umbrella_colors()[color_idx % len(_umbrella_colors())]
    if night > 0.05:
        color = _cap150(_mix(color, (54, 64, 96), min(0.5, 0.4 * night + 0.15)))
    dark = _shade(color, -46)
    panel_b = _shade(color, -20)
    rib_c = _shade(color, -32)
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
            hem.append(((fx + nx) * 0.5, max(fy, ny) + 1.4))   # the scallop dip
    pygame.draw.polygon(surf, color, outline + hem)

    # Two shaded wedges, pulled 14% short of the hem so the scalloped bottom edge
    # stays base colour and the canopy doesn't read as bottom-heavy.
    def _short(p):
        return (apex_x + (p[0] - apex_x) * 0.86, apex_y + (p[1] - apex_y) * 0.86)

    for i in _UMB_SHADED:
        pygame.draw.polygon(surf, panel_b,
                            [(apex_x, apex_y), _short(feet[i]), _short(feet[i + 1])])

    # Ribs only where a shaded panel already has an edge: a crease ON a value
    # boundary sharpens it, a crease across a panel destroys it.
    for i in (1, 2, 4, 5):
        fx, fy = feet[i]
        pygame.draw.line(surf, rib_c,
                         (apex_x + (fx - apex_x) * 0.55, apex_y + (fy - apex_y) * 0.55),
                         (fx, fy), 1)
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
    1px hub in the SAME wood tone as the spokes. The hub is the least important
    feature on the cart and must not be its brightest pixel; the one bright value
    the cart gets belongs on the bed's top edge, which is the plane a player is
    actually reading.

    The wheel does NOT spin. `spin` is kept as a parameter for a future in-transit
    pose, but a 6-fold-symmetric 8px wheel repeats every 0.58s at any believable
    rate — that is sparkle, not rotation — and the cart is pinned to a deck that
    scrolls with it, so a turning wheel is a lie the eye catches.

    `far` draws the off-side wheel — 1px smaller, one value darker, offset by the
    caller — which is what makes a side-on cart read as TWO-wheeled."""
    iron = _retint((70, 62, 56) if not far else (54, 48, 44), night)
    wood = _retint((150, 112, 66) if not far else (116, 86, 52), night)
    pygame.draw.circle(surf, iron, (cx, cy), r)
    pygame.draw.circle(surf, wood, (cx, cy), max(1, r - 1))
    for k in range(3):
        a = spin + k * math.pi / 3.0
        dx, dy = math.cos(a) * (r - 1), math.sin(a) * (r - 1)
        pygame.draw.line(surf, iron, (cx - dx, cy - dy), (cx + dx, cy + dy), 1)
    pygame.draw.circle(surf, _shade(wood, -10), (cx, cy), 1)


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
                 bundle laid diagonally, a rolled awning, a crate, all RESTING
                 ON the bed line.
      'half'   — TIPPED to unload at ~28 deg: bed sloped down-left, handles up in
                 the air on a thick keyed shaft, the last crate sliding to the low
                 end with the basket already landed against it. Reads as
                 mid-action, and the diagonal is a MASS, not a hairline.
      'empty'  — PARKED: bed level, handles dropped to the pavement, bare slats
                 showing, the rolled mat leaned against the near wheel.
    """
    g = int(base_y)
    wood = _retint((132, 96, 56), night)
    wood_dk = _shade(wood, -30)
    wood_hi = _shade(wood, 18)

    wr = 4
    axle_x, axle_y = cx - 3, g - wr
    spin = 0.0

    # Bed geometry per state: (left end y-offset, right end y-offset) from the
    # bed line, plus where the handles run. HALF's slope is ~28 deg over the 26px
    # bed — steep enough that the tip reads as a tip and not as a wonky cart.
    if load == "half":
        bl, br = 8, -6
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
    # The cart's ONE bright value, on the plane the eye actually reads: the top
    # edge of the bed. Everything else — hub included — sits under it.
    pygame.draw.line(surf, wood_hi, (x0 + 1, yl), (x1 - 1, yr), 1)
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
        hx1, hy1 = x1 + 6, yr - 9
    else:
        hx0, hy0 = x1 - 1, yr + 1
        hx1, hy1 = x1 + 9, g - 1
    if load == "half":
        # 2px shaft with its own dark keyline: a raised handle has to be MASS.
        # A 1px diagonal thread over a 20px blob is exactly the detail that
        # disappears first against foliage at 1x.
        for off in (0, 3):
            pygame.draw.line(surf, wood, (hx0, hy0 + off), (hx1, hy1 + off), 2)
            pygame.draw.line(surf, wood_dk, (hx0, hy0 + off + 1), (hx1, hy1 + off + 1), 1)
    else:
        for off in (0, 2):
            pygame.draw.line(surf, wood_dk, (hx0, hy0 + off), (hx1, hy1 + off), 1)
    pygame.draw.line(surf, wood, (hx1 - 1, hy1), (hx1 - 1, hy1 + 2), 2)

    _spoked_wheel(surf, axle_x, axle_y, wr, night, spin=spin)

    # ── the load ──
    if load == "loaded":
        # Pole bundle laid diagonally across the bed — five 1px poles splayed at
        # slightly different angles with one binding band, so it reads as a tied
        # bundle rather than a solid wedge.
        # Everything sits 2px lower than it did: the load RESTS on the bed line.
        # A gap band between a load and its bed is the one thing that makes a
        # cart look like unrelated objects stacked in the air.
        pole = _retint((160, 132, 84), night)
        pole_dk = _shade(pole, -34)
        for i in range(5):
            pygame.draw.line(surf, pole if i % 2 else pole_dk,
                             (x0 + 1, yl + 1 - i), (x1 - 3, yr - 5 - i // 2), 1)
        band = _retint((120, 70, 56), night)
        pygame.draw.line(surf, band, (cx + 2, yr - 7), (cx + 3, yr - 1), 2)
        _rolled_awning(surf, x0 + 2, yl - 6, 12, night)
        _cart_crate(surf, cx + 4, yr - 12, 9, 7, night)
    elif load == "half":
        _cart_crate(surf, x0 + 2, yl - 7, 9, 7, night)
        # The basket has ALREADY landed, against the low end of the bed — not
        # parked three pixels clear of it. Attached, the envelope stays ~30px and
        # the pair reads as one action; detached it read as a separate prop.
        weave = _retint((172, 138, 86), night)
        br_ = pygame.Rect(x0 - 1, g - 7, 10, 7)
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


_LIT_KIT_CACHE = {}
_LIT_KIT_CACHE_CAP = 128


def _clamped_lit(drawer):
    """The props_cast._night_clamped contract, applied to a new LIT piece.

    The tarped stall is the only member of this kit that emits light (brazier
    halo under the sheet), and an additive halo summed over an already-warm
    counter is exactly the core+halo overlap that broke the cap once before. So
    at night the whole piece — core, broth, halo — draws onto its own SRCALPHA
    layer, gets props_cast's composite luma clamp, and only then blits. Day is
    a straight-through draw, so the daylight look is byte-identical."""
    name = getattr(drawer, "__name__", "drawer")

    def _wrapped(surf, sx, base_y, night, t, **kw):
        if night <= 0.05:
            return drawer(surf, sx, base_y, night, t, **kw)
        # Baked, like props_cast._night_clamped: the per-pixel clamp costs ~3 ms
        # a call, so the lit layer renders once per (variant kwargs, night step,
        # flicker frame) and replays from a small FIFO cache.
        nq = min(20, int(night * 20 + 0.5))
        tq = int(t * 8) % 16
        key = (name, tuple(sorted((k, round(v, 2) if isinstance(v, float) else v)
                                  for k, v in kw.items())), nq, tq)
        layer = _LIT_KIT_CACHE.get(key)
        if layer is None:
            layer = pygame.Surface((_TARP_MARGIN_X * 2,
                                    _TARP_MARGIN_UP + _TARP_MARGIN_DOWN),
                                   pygame.SRCALPHA)
            drawer(layer, _TARP_MARGIN_X, _TARP_MARGIN_UP, nq / 20.0, tq / 8.0, **kw)
            _props._clamp_surface_luma(layer)
            if len(_LIT_KIT_CACHE) >= _LIT_KIT_CACHE_CAP:
                _LIT_KIT_CACHE.pop(next(iter(_LIT_KIT_CACHE)))
            _LIT_KIT_CACHE[key] = layer
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
    # 4px, with a HARD three-band ramp down the thickness: 1px lit top edge, 2px
    # body, 1px shade(-40) underside. At 3px the lit line sat directly on the dark
    # outline and the two fought; a three-band ramp reads as a taut plane at every
    # phase and — the part that matters — gives the low corner a real edge against
    # the paving it is sloping toward, where the sheet and the day deck are only
    # ~27 luma apart.
    sheet = [(hx, hy), (lx, ly), (lx, ly + 4), (hx, hy + 4)]
    pygame.draw.polygon(surf, tarp, sheet)
    pygame.draw.line(surf, tarp_hi, (hx, hy), (lx, ly), 1)
    pygame.draw.line(surf, _shade(tarp, -40), (hx, hy + 3), (lx, ly + 3), 1)

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
    # Water ACCELERATES: the dashes taper from 3px to 1px as they fall and shed
    # ~30% of their alpha on the way, so the thread reads as one stream speeding
    # up rather than as a dashed line someone drew.
    wet = _mix((176, 200, 220), (60, 74, 104), min(0.62, 0.5 * night + 0.18))
    stream_top = ly + 4
    fall = max(1, base_y - stream_top)
    for k in range(4):
        ph = ((t * 2.2) + k * 0.25) % 1.0
        yy = stream_top + ph * fall
        if yy >= base_y - 1:
            continue
        h = 3 if ph < 0.35 else (2 if ph < 0.68 else 1)
        a = int(255 * (1.0 - 0.30 * ph))
        dash = pygame.Surface((1, h), pygame.SRCALPHA)
        dash.fill((*wet, a))
        surf.blit(dash, (lx, int(yy)))
    pygame.draw.circle(surf, wet, (lx, stream_top), 1)
    sp_w = 3 + int(math.sin(t * 4.4) * 1.5)
    pygame.draw.ellipse(surf, _shade(wet, -20), (lx - sp_w, base_y - 2, sp_w * 2, 3), 1)

    # ── the vendor, sitting it out ──
    shirt = _retint((92, 82, 112), night)
    shirt_dk = _shade(shirt, -22)
    hair = _retint((52, 42, 34), night)
    vx = sx - 6
    body_y = cy - 10
    # deferred for the same import-cycle reason as _umbrella_colors()
    from game import foreground_promenade as _fp
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
    # The cook-top is the ONLY thing that varies by stall kind. The sheet above it
    # is byte-identical across all five, on purpose: a per-kind tarp buys nothing
    # at 1x and costs the read that the whole street agrees about the weather.
    px = sx + 10
    if kind == "steamer":
        bam = _retint((188, 156, 96), night)
        for i in range(3):
            rim = pygame.Rect(px - 6, cy - 6 - i * 4, 12, 5)
            pygame.draw.ellipse(surf, bam, rim)
            pygame.draw.ellipse(surf, _shade(bam, -34), rim, 1)
        top_y = cy - 6 - 2 * 4
    elif kind == "wok":
        pan = _retint((58, 54, 56), night)
        pygame.draw.ellipse(surf, pan, (px - 8, cy - 7, 16, 7))
        pygame.draw.ellipse(surf, _shade(pan, -22), (px - 8, cy - 7, 16, 7), 1)
        pygame.draw.line(surf, _shade(pan, 20), (px - 6, cy - 6), (px + 6, cy - 6), 1)
        top_y = cy - 7
    else:                                   # cauldron / tea / grill all read as a pot
        pot = _retint((64, 60, 62), night)
        pygame.draw.ellipse(surf, pot, (px - 6, cy - 7, 12, 6))
        pygame.draw.ellipse(surf, _shade(pot, -22), (px - 6, cy - 7, 12, 6), 1)
        pygame.draw.ellipse(surf, _retint((150, 96, 58), night), (px - 4, cy - 7, 8, 3))
        top_y = cy - 7
    if night > 0.05:
        _food._warm_glow(surf, px, cy - 4, radius=8, peak=44, color=(150, 92, 46))
    _food._wisp(surf, px, top_y - 1, t, n=4, rise=22, spread=3.0, speed=0.5,
                peak_a=72, r0=2, sway=2.8, color=_food._steam_col(night))
    _food._wisp(surf, px - 4, top_y, t, n=3, rise=16, spread=2.2, speed=0.6,
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
#
# He is built on ped_cast._draw_one — a STANDING body at full cast scale, with the
# besom as a `sweep` accessory. The bench-person idiom was wrong for him twice
# over: it is a SEATED construction, and it rendered him as an 11px hunched blob
# next to an 18px cast. He is the first inhabitant of an empty morning street,
# which is a hero moment, and hero moments do not get the short body.

_SWEEP_PERIOD = 1.3          # a real work rhythm; 1.8s read as pottering


def _sweeper_variant(coat):
    """The sweeper's own ped_cast variant. In integration this is one more row in
    _build_pool with acc=('sweep',) and the besom block lives inside _draw_one
    next to A_POLE — same geometry constants, same retint, same night cap."""
    dark = _shade(coat, -42)
    return _fv.Variant(
        palette={"coat": coat, "coat_dk": dark, "trousers": _shade(coat, -54),
                 "hair": (48, 40, 32), "skin": "tan", "hat": "cloth",
                 "hat_c": (120, 112, 92)},
        pose=frozenset(), accessory=frozenset(("sweep",)),
        attrs={"arch": _ped.A_TUNIC, "height": 1.0, "stoop": 0.16, "build": 1.0})


def draw_sweeper(surf, cx, base_y, night, t, *, phase=0.0, coat=(108, 118, 96),
                 pile=True, pal=None):
    """The morning sweeper: a full-scale ped_cast body + a ~14px angled besom on a
    1.3s cycle, pushing a low pile of swept slush."""
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

    # A 1px vertical bob on the push. The weight shift is what makes sweeping
    # legible at this size — without it the arms move and the man does not.
    bob = 1 if k > 0.55 else 0
    gm = _Geom(g + bob)
    # He faces LEFT like the rest of the cast, so the push is leftward and the
    # body is anchored right of `cx`: the broom is half the outline and all of it
    # lives on one side of the man.
    bx = cx + 5 - int(round(k * 2))

    from game import biome as _biome
    _ped._draw_one(surf, bx, g + bob, pal or _biome.palette_for_phase(0.06),
                   _sweeper_variant(coat), night, t * 1.1 + phase)

    # ── the besom ──
    # The head STAYS ON THE DECK for the whole stroke — a broom that lifts off
    # the paving mid-sweep reads as a staff being waved. So the tip is pinned to
    # the ground line and only its reach changes; the shaft's apparent length
    # shortening as it steepens is the foreshortening, and it sells the push.
    # Head travel is ~10px over 1.3s: at 6px it read as fidgeting, not as work.
    hand_x = bx + 2 - int(k * 2)
    hand_y = gm.torso_top + gm.head_r + bob
    tip_x = hand_x - (8 + k * 5.5)
    tip_y = g - 1
    ang = math.atan2(tip_y - hand_y, tip_x - hand_x)   # screen space, hand → tip
    shaft = _retint((146, 112, 68), night)
    pygame.draw.line(surf, _shade(shaft, -30), (hand_x, hand_y + 1), (tip_x, tip_y + 1), 2)
    pygame.draw.line(surf, shaft, (hand_x, hand_y), (tip_x, tip_y), 1)
    pygame.draw.line(surf, shirt_dk, (bx + 2, gm.torso_top + 1 + bob), (hand_x, hand_y), 2)
    pygame.draw.line(surf, shirt, (bx - 1, gm.torso_top + 2 + bob), (hand_x - 2, hand_y + 1), 1)

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
        # The pile is swept-up slush and litter: a DULL mound, one clear step
        # UNDER the paving's own value (a sunrise deck means ~164), with no crest
        # highlight at all. Round 1 made it the second-brightest object on the
        # street, which is a place the coin is entitled to and a mound of dirty
        # snow is not.
        #
        # It also sits 3px further left, fully clear of the twig fan: fan and pile
        # overlapping in x merged into one blob at 1x and ate the besom read the
        # whole piece is banking on.
        pile_x = int(tip_x - 9 + k * 2)
        pale = _mix((142, 144, 148), (70, 82, 108), min(0.5, 0.4 * night))
        pygame.draw.ellipse(surf, _shade(pale, -30), (pile_x - 4, g - 3, 8, 4))
        pygame.draw.ellipse(surf, pale, (pile_x - 3, g - 3, 6, 3))
        for fx, fy in ((pile_x - 2, g - 2), (pile_x + 2, g - 3)):
            pygame.draw.circle(surf, _retint((150, 108, 84), night), (fx, fy), 1)
        # A dust puff at the moment of full extension — held faint, because a
        # sunrise deck already measures 225 luma and the coin owns the top of the
        # range on this street at every hour.
        if k > 0.75:
            _breath_puff(surf, pile_x + 3, g - 4, (k - 0.75) * 3.2, phase=0.0,
                         wind=0.6, period=1.0, peak_a=64, base_a=36, rim=False,
                         tint=(168, 158, 140))





def weekend_dress(variant, rain, snow):
    """The weather-dress substitution for a pedestrian pool variant: in a real
    storm some of the rain-only rows trade their look for the suoyi straw cape
    (the figure still working, both hands free), and in snow most of the
    snow-only rows become full padded-coat winter figures. Keyed to the row's
    own weather weights + a per-variant hash, so the decision is stable for a
    latched slot and only weather-locked rows ever substitute."""
    p = _fv.pool("pedestrian")
    if not p:
        return None
    v = p[variant % len(p)]
    ww = v.weather_weights
    if not ww or ww.get(_fv.WB_CLEAR, 1.0) > 0.0:
        return None                     # all-weather rows keep their own look
    h = variant * 0x9E3779B1
    h ^= h >> 15
    h = (h * 0x2C1B3C6D) & 0xFFFFFFFF
    if snow >= 0.35 and ww.get(_fv.WB_SNOW, 0.0) > 0.0:
        return "winter" if (h % 100) < 76 else None
    if rain >= 0.5 and ww.get(_fv.WB_RAIN, 0.0) > 0.0:
        return "suoyi" if (h % 100) < 55 else None
    return None
