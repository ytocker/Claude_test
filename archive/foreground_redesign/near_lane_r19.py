"""Round-19 NEAR / FRONT ACTIVITY LANE — a second, CLOSER lane of promenade life.

Round 17 set the promenade cast at the FAR edge of the sidewalk (feet at
GROUND_Y=595). Round 18 embedded surface detail into the floor body. The walk now
has depth to spend: this round populates the NEAR / FRONT edge of the sidewalk —
feet at y≈636-640, down at the screen bottom — with a LARGER, closer band of life
that scrolls a touch FASTER and OCCLUDES the far lane, so the promenade reads as a
busy thing seen at multiple distances rather than a single flat row.

What makes the depth read (the contract the art-director gates):

  * SCALE — near figures are rendered ~1.6-1.8x the far cast, so a near pedestrian
    beside a far one instantly says "closer", not "a second identical row".
  * FEET LOWER — the near band's deck sits at NEAR_GROUND_Y (≈638), a full ~43px
    below the far deck; near figures (and the near dog) clip naturally at the
    screen bottom, the way a foreground subject does.
  * FASTER PARALLAX — the far props track at PROP_MULT=0.20; the near lane anchors
    at NEAR_MULT=0.35 so it slides past faster, the classic near-vs-far cue.
  * OCCLUSION — the near lane is painted AFTER the far lane / props and BEFORE the
    gameplay actors, so near figures cover the far cast's feet (real depth, not a
    transparent overlay). Within the near lane we still draw back-to-front.

The cast functions are the r17 ones (`draw_kids`, `draw_old_man`, `draw_strollers`,
`draw_flock`) and the live `_RunningDog`, lifted READ-ONLY and rendered onto a
scratch surface that we scale up with NEAREST so the pixels stay crisp, then drop
at the near deck. The PERFORMANCES — a day busker/juggler, a golden-hour street
musician + watching arc, a dusk stilt-walker, and the NIGHT festival LION DANCE +
drummer — are net-new procedural, built from the bench-person body idiom and
lift-only `max(0,sin)` gaits, kept on-theme (Chinese temple festival).

Lane clearance: TALL near elements (banner pole, lion head, stilt-walker) are kept
OUT of the bird lane (x≈48-188) and the pillar lane (x≈212-320); SHORT near life
(pedestrians, dog, low plants) may sit under those lanes since it stays low and the
bird flies high (y≈30-430). Coin + parrot draw last and stay on top / brightest.

Night glow is capped ≤ NIGHT_GLOW_CAP (150) and gated to a dark sky, reusing the
promenade's `_cap150` / `_lit_intensity`; day/golden emit no glow (no white pool).
Everything is retinted per biome `pal`. World-anchored on the same `_world_xs`
idiom as the far props (no jitter / seam at the scroll wrap).

Pure-Pygame / pygbag-safe (fill, blit, draw.*, SRCALPHA, BLEND_RGB_ADD, and
transform.scale with NEAREST). No numpy / gfxdraw / per-frame surfarray. Nothing
here is written into game/.
"""
from __future__ import annotations

import math
import random

import pygame

import sidewalk_props_r15 as sp
import promenade_r17 as pr
from game.ambient import _RunningDog
from game.draw import draw_side_shrub, draw_wuling_pine
from game.pillar_variants import (
    draw_cascading_vine, draw_paper_lantern, draw_cairn,
    draw_darchog_pole, draw_incense_smoke,
)

GROUND_Y = sp.GROUND_Y               # 595 — the FAR deck (r17 cast feet).
NEAR_GROUND_Y = GROUND_Y + 43        # 638 — the NEAR deck; figures clip at bottom.
NEAR_MULT = 0.35                     # faster than the far props (0.20) -> "closer".

# Reuse the promenade's night contract verbatim so the near lights obey the same
# ceiling and the coin stays the single brightest object.
_cap150 = pr._cap150
_lit_intensity = pr._lit_intensity
_is_dark = sp._is_dark_sky
_nightf = sp._nightf
_mix = sp._mix
_shade = sp._shade

NIGHT_GLOW_CAP = pr.NIGHT_GLOW_CAP   # 150


# ── lane-clearance gates for TALL near props ──────────────────────────────────
#
# The bird flies at x≈90 with the coin out to ~168; the cream pillar base sits at
# x≈244. A tall near element (banner pole, lion head crest, stilt-walker) must not
# climb into either corridor. SHORT near life is exempt — it lives below the bird
# and is allowed to pass under the lanes.

_BIRD_LANE = (48, 188)
_PILLAR_LANE = (212, 320)


def _tall_ok(sx, half_w=10):
    """True only where a TALL near element clears both the bird and pillar lanes."""
    for lo, hi in (_BIRD_LANE, _PILLAR_LANE):
        if sx + half_w > lo and sx - half_w < hi:
            return False
    return True


# ── near-anchored placement: same world-x idiom as the far props, faster mult ──

def _near_xs(scroll, w, period, x0, margin=80):
    """Screen-x of a near element repeated every `period` world-px at NEAR_MULT,
    so the near lane parallaxes faster than the far lane and tiles seamlessly at
    the scroll wrap (no jitter / seam)."""
    yield from sp._world_xs(scroll, w, period, x0, mult=NEAR_MULT, margin=margin)


# ── warm capped glow for the near performers (drum / lantern halos) ───────────
#
# Net-new lit accents (festival drum face, performer lanterns) need their own
# halo since they aren't r15 lamp heads. Reuse the promenade's cached warm-glow +
# the 150 cap + the dusk->night intensity so a near light can never rival the coin.

# Performer SOLID highlights (lion sclera, drum heads, lit cores) are not glow
# blits — they're opaque pixels that out-shone the coin when left near-white. This
# pulls any such highlight to <= NIGHT_GLOW_CAP *luma* (not per-channel) at night
# while keeping a warm/ivory hue, so the brightest near-life pixel stays under the
# coin yet still reads as a lit accent rather than flat grey.

def _cap_lum(color, pal, *, cap=NIGHT_GLOW_CAP, warm=True):
    # The cap is set BELOW NIGHT_GLOW_CAP so that when a capped highlight also takes
    # the performer's additive warm halo on top, the summed pixel still lands under
    # the ceiling and the coin stays the single brightest object.
    cap = min(cap, 138)
    if not _is_dark(pal):
        return color
    r, g, b = color
    if warm:
        # An ivory/amber target so a capped highlight reads warm, never blue-white.
        r, g, b = min(r, 150), min(g, 134), min(b, 112)
    lum = 0.2126 * r + 0.7152 * g + 0.1145 * b
    if lum > cap and lum > 0:
        f = cap / lum
        r, g, b = int(r * f), int(g * f), int(b * f)
    return (r, g, b)


# The lion's IVORY fangs + mouth lip are the one near-life accent the art-director
# gates to read crisp on EVERY base. The generic _cap_lum path caps at 138 luma and
# leaves the fangs reading flat against the cool grey-taupe scene. These two helpers
# hold a WARM ivory at the fang allowance (~145 luma — still far under the coin's
# ~248) and do NOT over-retint toward the cool night, so the fangs/lip pop the same
# on terracotta and grey-taupe. Day/golden are untouched (returned verbatim).

def _warm_ivory_cap(color, pal, cap):
    if not _is_dark(pal):
        return color
    r, g, b = color
    # A warmer ivory clamp than _cap_lum (higher green/blue ceiling) so the fang
    # stays ivory, not olive, when it lands at the slightly higher fang luma.
    r, g, b = min(r, 168), min(g, 150), min(b, 126)
    lum = 0.2126 * r + 0.7152 * g + 0.1145 * b
    if lum > cap and lum > 0:
        f = cap / lum
        r, g, b = int(r * f), int(g * f), int(b * f)
    return (r, g, b)


def _fang_ivory(pal):
    # A WARMER ivory source (more red, less green/blue) so that at the SAME ~144
    # luma cap the fang reads as a warm tooth that separates from the cool grey-
    # taupe surroundings just as crisply as it does on terracotta — the flat read
    # on the cool base was a hue/contrast issue, not a value one, so the cap stays.
    return _warm_ivory_cap((196, 170, 138), pal, cap=144)


def _lip_ivory(pal):
    return _warm_ivory_cap((186, 162, 128), pal, cap=142)


def _near_glow(surf, cx, cy, pal, *, radius=12, color=(255, 170, 110)):
    if not _is_dark(pal):
        return
    s = _lit_intensity(pal)
    if s <= 0.02:
        return
    # A touch below the promenade peak so the bloom CORE (its centre add summed onto
    # the lit prop beneath) still lands under the cap and the coin stays brightest.
    peak = int(sp._GLOW_PEAK * 0.46 * s)
    if peak <= 1:
        return
    g = sp._warm_glow(radius, _cap150(color), peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ── scale an r17 cast fn up to near size by rendering it onto a scratch deck ───
#
# The r17 cast fns (draw_kids/old_man/strollers/flock) draw at the fixed module
# GROUND_Y onto whatever surface they're handed. To get a LARGER, NEAREST-crisp
# near figure we render the fn onto a tall scratch surface whose own GROUND_Y line
# sits near the bottom, scale the result up, and blit so the figure's feet land at
# the near deck. NEAREST keeps the pixel art crisp at the enlarged size.

# A scratch tile tall enough to hold a standing cast figure (heads reach ~30px
# above the deck) plus headroom for a raised arm / cane.
_SCRATCH_H = 56
_SCRATCH_W = 96


def _scaled_cast(surf, cast_fn, sx, pal, scale, *, t=0.0, feet_y=NEAR_GROUND_Y, **kw):
    """Render an r17 cast fn at 1x onto a scratch surface (its feet on the scratch
    deck), scale up by `scale` with NEAREST, and blit so the scaled feet land on
    `feet_y`. The cast fns read pr.GROUND_Y; we point that at the scratch deck for
    the duration so the figure sits where we can crop it cleanly."""
    scratch = pygame.Surface((_SCRATCH_W, _SCRATCH_H), pygame.SRCALPHA)
    deck = _SCRATCH_H - 1                 # scratch deck near the bottom edge
    saved = pr.GROUND_Y
    pr.GROUND_Y = deck
    try:
        cast_fn(scratch, _SCRATCH_W // 2, pal, t=t, **kw)
    finally:
        pr.GROUND_Y = saved
    # A LARGE near figure shouldn't pull focus from the parrot: knock its brightest
    # fabric (the r17 cast's near-white ~248) down ~6% so it sits below the actors.
    # Subtle whole-figure multiply (sheep/balls draw separately and stay bright).
    scratch.fill((240, 240, 240, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sw = max(1, int(_SCRATCH_W * scale))
    sh = max(1, int(_SCRATCH_H * scale))
    big = pygame.transform.scale(scratch, (sw, sh))
    # Scaled feet sit at (deck*scale) from the scratch top; align that to feet_y.
    feet_in_big = int((deck + 1) * scale)
    surf.blit(big, (sx - sw // 2, feet_y - feet_in_big))


def _near_dog(surf, sx, pal, *, t=0.0, scale=1.7, feet_y=NEAR_GROUND_Y):
    """The live running dog, enlarged with NEAREST and dropped at the near deck so
    it trots across the FRONT of the promenade, occluding the far cast."""
    dog = pr._stepped(_RunningDog, pal, 30, _SCRATCH_W // 2)
    frame = dog._frames[int(t * 9) % 2]
    night = _nightf(pal)
    if night > 0.05:
        frame = frame.copy()
        k = int(255 * (1 - 0.40 * night))
        kb = int(255 * (1 - 0.30 * night))
        frame.fill((k, k, kb, 255), special_flags=pygame.BLEND_RGBA_MULT)
    sw, sh = frame.get_size()
    big = pygame.transform.scale(frame, (int(sw * scale), int(sh * scale)))
    bw, bh = big.get_size()
    surf.blit(big, (sx - bw // 2, feet_y - bh + 1))


# ── near greenery / ornaments (parametric game helpers, retinted, night-capped)─

def _fol(pal, night):
    """Foliage sub-palette cooled toward night so near plants match the deck."""
    return {
        'foliage_dark': _mix(pal.get('foliage_dark', (35, 75, 35)), (40, 56, 86), 0.3 * night),
        'foliage_mid': _mix(pal.get('foliage_mid', (60, 115, 50)), (46, 64, 94), 0.3 * night),
        'foliage_top': _mix(pal.get('foliage_top', (90, 150, 70)), (60, 80, 110), 0.3 * night),
    }


def _near_planter(surf, sx, pal, *, feet_y=NEAR_GROUND_Y, w=26):
    """A LARGER potted planter for the front edge — the r15 box idiom, scaled up,
    feet on the near deck so it reads as a closer pot than the far planters."""
    night = _nightf(pal)
    box_h = 13
    by = feet_y
    box = _mix(pal.get('stone_mid', (150, 132, 110)), (150, 120, 92), 0.5)
    box = _mix(box, (60, 70, 100), 0.30 * night)
    pygame.draw.rect(surf, _shade(box, -18), (sx - w // 2, by - box_h, w, box_h))
    pygame.draw.rect(surf, box, (sx - w // 2 + 1, by - box_h, w - 2, box_h - 2))
    pygame.draw.rect(surf, _shade(box, 16), (sx - w // 2 + 1, by - box_h, w - 2, 2))
    draw_side_shrub(surf, sx, by - box_h - 3, _fol(pal, night), scale=1.9)


def _near_pine(surf, sx, pal, *, feet_y=NEAR_GROUND_Y, height=34):
    """A near Wuling pine in a tub — a taller piece of front greenery. Only placed
    in a clear horizontal zone since it climbs higher than a planter."""
    night = _nightf(pal)
    by = feet_y
    tub = _mix((120, 84, 52), (70, 76, 96), 0.32 * night)
    pygame.draw.rect(surf, _shade(tub, -20), (sx - 7, by - 9, 14, 9))
    pygame.draw.rect(surf, tub, (sx - 6, by - 9, 12, 7))
    draw_wuling_pine(surf, sx, by - 8, height, _fol(pal, night))


def _near_vine_lantern(surf, sx, pal, *, feet_y=NEAR_GROUND_Y):
    """A near tub with a cascading vine spilling over the front edge — pure decor
    that reads as a closer detail than the far vine trails."""
    night = _nightf(pal)
    by = feet_y
    pot = _mix((120, 84, 52), (70, 76, 96), 0.32 * night)
    pygame.draw.rect(surf, _shade(pot, -18), (sx - 7, by - 11, 14, 11))
    pygame.draw.rect(surf, pot, (sx - 6, by - 11, 12, 9))
    if _is_dark(pal):
        # draw_cascading_vine paints a hardcoded (255,180,120) leaf-tip highlight
        # that out-spiked the night cap. Render it on a scratch and knock its
        # brightness down so no decor leaf rivals the coin at night.
        sc = pygame.Surface((40, 36), pygame.SRCALPHA)
        draw_cascading_vine(sc, 20, 4, 16, _fol(pal, night))
        sc.fill((150, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(sc, (sx - 20, by - 16))
    else:
        draw_cascading_vine(surf, sx, by - 12, 16, _fol(pal, night))


def _near_brazier(surf, sx, pal, *, feet_y=NEAR_GROUND_Y, t=0.0):
    """A festival incense urn / brazier on the front edge — a squat stone bowl with
    a thread of incense smoke (and a small capped ember glow at night). On-theme
    temple dressing; kept short so it can sit under the lanes."""
    night = _nightf(pal)
    by = feet_y
    bowl = _mix(pal.get('stone_dark', (95, 80, 70)), (120, 96, 78), 0.5)
    bowl = _mix(bowl, (54, 60, 86), 0.32 * night)
    pygame.draw.ellipse(surf, _shade(bowl, -22), (sx - 9, by - 12, 18, 12))
    pygame.draw.ellipse(surf, bowl, (sx - 8, by - 12, 16, 9))
    pygame.draw.ellipse(surf, _shade(bowl, -30), (sx - 6, by - 11, 12, 4))
    if _is_dark(pal):
        # Ember core kept low (cap_lum) so the additive halo over it never spikes.
        ember = _cap_lum((150, 78, 46), pal)
        pygame.draw.ellipse(surf, ember, (sx - 4, by - 11, 8, 3))
        _near_glow(surf, sx, by - 10, pal, radius=9, color=(255, 150, 90))
    draw_incense_smoke(surf, sx, by - 12, length=18)


# ══════════════════════════════════════════════════════════════════════════
# Net-new PERFORMERS. All are built from the bench-person body idiom + lift-only
# gaits so they belong to the r17 cast's value family but read at the larger near
# scale. Each takes (surf, sx, pal, t) with feet on the near deck.
# ══════════════════════════════════════════════════════════════════════════

def _perf_body(surf, x, feet_y, robe, robe_dk, hair, pal, *, h=18, w=9,
               lean=0, arms='down', arm_t=0.0):
    """A larger standing performer torso + head with posable arms. Mirrors the
    bench-person idiom (block torso, round head, hair cap) at near scale, retinted
    per night so a face never out-shines the cap. Returns (head_x, head_y) so a
    caller can add a hat / crest. `arms`: 'down' | 'up' | 'drum' | 'juggle'."""
    night = _nightf(pal)
    skin = pr._retint_person((232, 192, 150), night)
    body_y = feet_y - h
    # Robe as a wedge so the near figure has weight; lean tips the shoulders.
    pygame.draw.polygon(surf, robe, [
        (x - w // 2 + lean, body_y), (x + w // 2 + lean, body_y),
        (x + w // 2 + 1, feet_y), (x - w // 2 - 1, feet_y)])
    pygame.draw.polygon(surf, robe_dk, [
        (x - w // 2 + lean, body_y), (x + w // 2 + lean, body_y),
        (x + w // 2 + 1, feet_y), (x - w // 2 - 1, feet_y)], 1)
    hx, hy = x + lean, body_y - 4
    pygame.draw.circle(surf, skin, (hx, hy), 4)
    pygame.draw.arc(surf, hair, (hx - 4, hy - 5, 9, 9),
                    math.radians(0), math.radians(180), 3)
    pygame.draw.circle(surf, (30, 20, 15), (hx - 1, hy), 0)
    pygame.draw.circle(surf, (30, 20, 15), (hx + 1, hy), 0)
    # Legs.
    leg = _shade(robe_dk, -14)
    pygame.draw.line(surf, leg, (x - 2 + lean, feet_y - 5), (x - 3, feet_y), 2)
    pygame.draw.line(surf, leg, (x + 2 + lean, feet_y - 5), (x + 3, feet_y), 2)
    # Arms per pose.
    sh_y = body_y + 3
    swing = max(0.0, math.sin(arm_t))
    if arms == 'up':
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            pygame.draw.line(surf, robe, (ax, sh_y),
                             (ax + dx * 4, sh_y - 7 - int(swing * 3)), 2)
    elif arms == 'drum':
        for dx, ph in ((-1, 0.0), (1, math.pi)):
            ax = x + (w // 2) * dx + lean
            lift = int(max(0.0, math.sin(arm_t + ph)) * 4)
            pygame.draw.line(surf, robe, (ax, sh_y),
                             (ax + dx * 5, sh_y + 4 - lift), 2)
    elif arms == 'juggle':
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            pygame.draw.line(surf, robe, (ax, sh_y), (ax + dx * 5, sh_y - 4), 2)
    else:  # down
        for dx in (-1, 1):
            ax = x + (w // 2) * dx + lean
            pygame.draw.line(surf, robe, (ax, sh_y), (ax + dx * 3, sh_y + 6), 2)
    return hx, hy


def _watch_arc(surf, sx, pal, t, *, feet_y=NEAR_GROUND_Y):
    """A small head-bobbing crowd watching a near performer — scaled r17 cast
    arranged in a shallow arc facing inward. Reused for golden/dusk/night so the
    'crowd grows' escalation reads. Kept SHORT so it may sit under the lanes."""
    # A few kids + an elder + strollers, spread either side of the performer.
    _scaled_cast(surf, pr.draw_kids, sx - 30, pal, 1.45, t=t, n=2, feet_y=feet_y)
    _scaled_cast(surf, pr.draw_old_man, sx + 30, pal, 1.5, t=t,
                 seated_bench=False, feet_y=feet_y)


def _seated_spectator(surf, x, feet_y, robe, robe_dk, hair, pal, *,
                      lean=0, raise_arm=False, t=0.0, face=1, gesture='cheer'):
    """A small spectator SEATED on the deck (knees forward), used to give a gathered
    crowd a couple of LOWER figures so it reads 'an audience sat watching the act'
    rather than people walking past. `lean` tips the torso/head toward the act and
    `raise_arm` adds an arm lifted toward the performer (direction `face`: +1=right)
    so the pose reads unambiguously as 'audience facing the act'. `gesture`:
    'cheer' (high bobbing arm) | 'point' (a lower forearm reaching toward the act)
    — two distinct silhouettes so the pair don't read as identical clones."""
    night = _nightf(pal)
    skin = pr._retint_person((232, 192, 150), night)
    seat_y = feet_y - 2
    # Folded legs as a low wedge on the deck.
    pygame.draw.polygon(surf, _shade(robe_dk, -10), [
        (x - 6, seat_y), (x + 6, seat_y), (x + 4, seat_y - 4), (x - 4, seat_y - 4)])
    # Compact torso + head, sitting low; the torso top shifts by `lean` so the
    # shoulders + head tip toward the act (a clear facing cue, not a flat block).
    pygame.draw.polygon(surf, robe, [
        (x - 4 + lean, seat_y - 12), (x + 4 + lean, seat_y - 12),
        (x + 4, seat_y - 3), (x - 4, seat_y - 3)])
    pygame.draw.polygon(surf, robe_dk, [
        (x - 4 + lean, seat_y - 12), (x + 4 + lean, seat_y - 12),
        (x + 4, seat_y - 3), (x - 4, seat_y - 3)], 1)
    hx = x + lean
    pygame.draw.circle(surf, skin, (hx, seat_y - 15), 3)
    pygame.draw.arc(surf, hair, (hx - 3, seat_y - 19, 7, 7),
                    math.radians(0), math.radians(180), 2)
    if raise_arm:
        sh_y = seat_y - 10
        if gesture == 'point':
            # A lower forearm reaching out toward the performer with a skin-toned
            # hand at the tip — a clear "looking that way" cue distinct from a
            # raised cheer, so the two seated figures read as separate poses.
            ex, ey = hx + face * 7, sh_y - 1
            pygame.draw.line(surf, robe, (hx, sh_y), (ex, ey), 2)
            pygame.draw.circle(surf, skin, (ex, ey), 1)
        else:
            # An arm lifted toward the performer (a small cheer), bobbing gently so
            # the gathered crowd reads as actively watching the act.
            wave = int(max(0.0, math.sin(t * 3.0)) * 2)
            ex, ey = hx + face * 5, sh_y - 6 - wave
            pygame.draw.line(surf, robe, (hx, sh_y), (ex, ey), 2)
            pygame.draw.circle(surf, skin, (ex, ey), 1)


def _gathered_crowd(surf, sx, pal, t, *, feet_y=NEAR_GROUND_Y):
    """A TIGHT, performer-FACING audience clustered to the LEFT of the act (so all
    heads turn toward the performer on the right). The differentiator from the
    day/dusk foot traffic is the CLUSTERING + uniform facing + a couple of LOWER
    seated figures. Built from scaled r17 cast + two seated spectators."""
    night = _nightf(pal)
    rb = pr._retint_person((120, 110, 150), night)
    rb_dk = pr._retint_person((78, 72, 108), night)
    hr = pr._retint_person((58, 46, 42), night)
    # Back row: standing figures packed close, all on the performer's left, so the
    # group leans/looks toward the act rather than spreading symmetrically.
    _scaled_cast(surf, pr.draw_kids, sx - 40, pal, 1.5, t=t, n=2, feet_y=feet_y)
    _scaled_cast(surf, pr.draw_old_man, sx - 22, pal, 1.55, t=t,
                 seated_bench=False, feet_y=feet_y)
    _scaled_cast(surf, pr.draw_strollers, sx - 56, pal, 1.45, t=t, feet_y=feet_y)
    # Front row: two LOWER seated spectators close in, reading as the near edge of
    # a gathered audience facing the performer. Both lean RIGHT toward the act (it
    # sits at sx, to their right) with a stronger head-tip, and EACH gestures toward
    # the performer in a DISTINCT pose (one high cheer, one reaching point) so the
    # "audience facing the act" read lands instantly and the pair don't clone.
    _seated_spectator(surf, sx - 30, feet_y, rb, rb_dk, hr, pal,
                      lean=3, raise_arm=True, t=t, face=1, gesture='cheer')
    _seated_spectator(surf, sx - 14,
                      feet_y, pr._retint_person((150, 90, 80), night),
                      pr._retint_person((100, 56, 50), night), hr, pal,
                      lean=3, raise_arm=True, t=t, face=1, gesture='point')


def perf_juggler(surf, sx, pal, t):
    """DAY · a casual daytime BUSKER / juggler — a single performer tossing three
    balls in a small arc, with 1-2 near onlookers half-facing him so it reads
    'busking', not a lone figure. Low-key morning act; no crowd, no glow."""
    night = _nightf(pal)
    robe = pr._retint_person((196, 92, 70), night)     # warm terracotta tunic
    robe_dk = pr._retint_person((150, 60, 52), night)
    hair = pr._retint_person((70, 50, 40), night)
    feet = NEAR_GROUND_Y
    # A couple of onlookers stand to the RIGHT, half-facing the juggler, so the act
    # reads as busking. Kept tight beside him, clear of the gameplay lanes.
    _scaled_cast(surf, pr.draw_old_man, sx + 30, pal, 1.45, t=t,
                 seated_bench=False, feet_y=feet)
    _scaled_cast(surf, pr.draw_kids, sx + 46, pal, 1.4, t=t, n=2, feet_y=feet)
    hx, hy = _perf_body(surf, sx, feet, robe, robe_dk, hair, pal,
                        h=20, w=9, arms='juggle', arm_t=t * 3.0)
    # Three balls on a small juggling cascade above the hands. Sized a touch
    # bigger (r=5 outer / 4 fill) and pushed to hot, fully-saturated primaries so
    # the arc reads as juggling MOTION at 1x rather than as stray confetti — a
    # juggling ball wants to read as a deliberate prop, not a paving fleck.
    ball_cols = ((255, 176, 16), (240, 44, 40), (32, 132, 248))
    for i, col in enumerate(ball_cols):
        ph = (t * 1.6 + i / 3.0) % 1.0
        bx = sx + int(math.sin(ph * math.tau) * 9)
        by = hy - 4 - int(math.sin(ph * math.pi) * 13)
        col = pr._retint_person(col, night)
        pygame.draw.circle(surf, _shade(col, -24), (bx, by), 5)
        pygame.draw.circle(surf, col, (bx, by), 4)
        # A hot 2px highlight so each ball reads round, lit and tracking through
        # the cascade rather than as a flat dot.
        pygame.draw.circle(surf, _shade(col, 48), (bx - 1, by - 1), 2)


def perf_musician(surf, sx, pal, t):
    """GOLDEN HOUR · a street MUSICIAN pulled INTO the near lane (forward + larger),
    SEATED behind a visible barrel drum, with a TIGHT performer-FACING crowd
    gathered to his left. The clustering + uniform facing distinguishes this act
    from the day/dusk foot traffic."""
    night = _nightf(pal)
    robe = pr._retint_person((90, 110, 160), night)    # indigo musician robe
    robe_dk = pr._retint_person((58, 74, 116), night)
    hair = pr._retint_person((60, 45, 40), night)
    feet = NEAR_GROUND_Y
    # The gathered audience (behind), clustered on the performer's left + facing in.
    _gathered_crowd(surf, sx, pal, t, feet_y=feet)
    # A SEATED musician (lower torso, knees forward) on the deck behind a big drum.
    skin = pr._retint_person((232, 192, 150), night)
    seat_y = feet - 2
    pygame.draw.polygon(surf, _shade(robe_dk, -10), [
        (sx + 2, seat_y), (sx + 14, seat_y), (sx + 12, seat_y - 5), (sx + 4, seat_y - 5)])
    pygame.draw.rect(surf, robe, (sx + 3, seat_y - 16, 9, 12))
    pygame.draw.rect(surf, robe_dk, (sx + 3, seat_y - 16, 9, 12), 1)
    hx, hy = sx + 7, seat_y - 19
    pygame.draw.circle(surf, skin, (hx, hy), 4)
    pygame.draw.arc(surf, hair, (hx - 4, hy - 5, 9, 9),
                    math.radians(0), math.radians(180), 3)
    # A LARGER barrel drum/gong stood on the deck in front of the seated musician.
    dx, dy = sx - 4, feet
    drum = _mix((150, 60, 45), (70, 70, 96), 0.30 * night)
    pygame.draw.ellipse(surf, _shade(drum, -24), (dx - 11, dy - 20, 22, 20))
    pygame.draw.ellipse(surf, drum, (dx - 10, dy - 19, 20, 18))
    head_col = _cap_lum((205, 182, 145), pal)
    pygame.draw.ellipse(surf, head_col, (dx - 9, dy - 19, 18, 6))
    pygame.draw.ellipse(surf, _shade(head_col, -26), (dx - 9, dy - 19, 18, 6), 1)
    tack = _cap_lum((180, 150, 90), pal)
    for ti in range(-2, 3):
        pygame.draw.circle(surf, tack, (dx + ti * 5, dy - 12), 1)
    # His hands beat the near drum head (mid-swing).
    for ph in (0.0, math.pi):
        lift = int(max(0.0, math.sin(t * 4.5 + ph)) * 5)
        hxh = dx + (4 if ph else -4)
        pygame.draw.line(surf, robe, (sx + 5, seat_y - 12),
                         (hxh, dy - 18 - lift), 2)
    _near_glow(surf, dx, dy - 12, pal, radius=10, color=(255, 150, 90))


def perf_stilt(surf, sx, pal, t):
    """DUSK · the crowd grows and a STILT-WALKER warms up as the lamps light — a
    tall robed figure on stilts (kept in a clear zone since it's tall). A small
    watching arc gathers below."""
    night = _nightf(pal)
    robe = pr._retint_person((150, 70, 130), night)    # festival magenta
    robe_dk = pr._retint_person((100, 44, 92), night)
    hair = pr._retint_person((60, 45, 40), night)
    feet = NEAR_GROUND_Y
    _watch_arc(surf, sx, pal, t, feet_y=feet)
    # Stilts: two tall poles from the deck up to a raised body.
    stilt_h = 24
    sway = int(math.sin(t * 1.6) * 1)
    body_feet = feet - stilt_h
    pole = _shade((110, 78, 48), -10)
    for dx in (-3, 3):
        pygame.draw.line(surf, pole, (sx + dx + sway, body_feet),
                         (sx + dx, feet), 2)
    _perf_body(surf, sx + sway, body_feet, robe, robe_dk, hair, pal,
               h=18, w=8, arms='up', arm_t=t * 2.0)


def perf_lion_dance(surf, sx, pal, t):
    """NIGHT · the festival peak — a two-person LION DANCE + a drummer + a bigger
    crowd. The lion is a bulbous decorated head (carried high by a front dancer)
    trailing a flowing cloth body over a rear dancer; a drummer keeps time beside
    it. Net-new procedural, on-theme, lit accents capped + gated."""
    night = _nightf(pal)
    feet = NEAR_GROUND_Y
    # The bigger crowd flanks the act (behind, drawn first).
    _scaled_cast(surf, pr.draw_strollers, sx - 44, pal, 1.5, t=t, feet_y=feet)
    _scaled_cast(surf, pr.draw_kids, sx - 64, pal, 1.55, t=t, n=3, feet_y=feet)
    _scaled_cast(surf, pr.draw_old_man, sx + 48, pal, 1.55, t=t,
                 seated_bench=False, feet_y=feet)

    # Drummer + drum to the right of the lion — an EXPLICIT round drum stood in
    # FRONT of the elder with a stick caught mid-swing, so the lion dance's audio
    # source is legible rather than a robed bystander.
    drx = sx + 32
    robe = pr._retint_person((110, 60, 70), night)
    robe_dk = pr._retint_person((74, 40, 50), night)
    hair = pr._retint_person((50, 40, 38), night)
    _perf_body(surf, drx, feet, robe, robe_dk, hair, pal,
               h=21, w=9, arms='drum', arm_t=t * 6.0)
    # The drum body sits on the deck in front of the drummer (round shell + heads).
    ddx, ddy = drx - 10, feet - 1
    shell = _mix((160, 55, 45), (70, 70, 96), 0.34 * night)
    pygame.draw.ellipse(surf, _shade(shell, -28), (ddx - 9, ddy - 17, 18, 17))
    pygame.draw.ellipse(surf, shell, (ddx - 8, ddy - 16, 16, 15))
    for hy in (ddy - 16, ddy - 3):
        head = _cap_lum((200, 178, 140), pal)
        pygame.draw.ellipse(surf, head, (ddx - 8, hy, 16, 5))
        pygame.draw.ellipse(surf, _shade(shell, -34), (ddx - 8, hy, 16, 5), 1)
    # Brass tacks around the rim — capped so they never spike over the cap.
    tack = _cap_lum((180, 150, 90), pal)
    for ti in range(-2, 3):
        pygame.draw.circle(surf, tack, (ddx + ti * 4, ddy - 9), 1)
    # A drumstick caught mid-swing above the near head.
    stick = pr._retint_person((180, 140, 95), night)
    swing = int(max(0.0, math.sin(t * 6.0)) * 6)
    pygame.draw.line(surf, stick, (ddx + 4, ddy - 16),
                     (ddx + 10, ddy - 20 - swing), 2)
    _near_glow(surf, ddx, ddy - 9, pal, radius=11, color=(255, 150, 90))

    # ── the LION DANCE (two dancers under a flowing body) ─────────────────────
    # The silhouette must read as a Chinese temple lion, not a round mascot: a
    # ridged horned head, a scalloped frilled mane, a gaping lip-lined mouth, and
    # a long trailing cloth body with a SECOND pair of legs behind the front pair.
    bob = int(max(0.0, math.sin(t * 3.2)) * 3)        # the lion's bouncy lift
    body_y = feet - 16 - bob
    cloth = pr._retint_person((205, 70, 55), night)   # festive red drape
    cloth_dk = pr._retint_person((150, 45, 42), night)
    trim = _cap_lum((230, 195, 90), pal)              # gold hem (capped at night)
    # The trailing cloth body runs from BEHIND (tail, left) up to the head (right);
    # a long undulating drape so the two dancers clearly share one costume.
    bx0 = sx - 36                                      # tail end (behind head)
    seg_pts = []
    for i in range(8):
        tt = i / 7.0
        px = bx0 + int(tt * 36)
        wave = int(math.sin(t * 3.0 + tt * 4.0) * 3)
        py = body_y + 7 + wave + int(tt * 3)
        seg_pts.append((px, py))
    top = [(p[0], p[1] - 7) for p in seg_pts]
    bot = [(p[0], p[1] + 7) for p in reversed(seg_pts)]
    pygame.draw.polygon(surf, cloth_dk, top + bot)
    pygame.draw.polygon(surf, cloth, [(p[0], p[1] - 5) for p in seg_pts] +
                        [(p[0], p[1] + 5) for p in reversed(seg_pts)])
    # A scalloped gold hem (a run of small arcs) so the drape reads "costume".
    for px, py in seg_pts:
        pygame.draw.circle(surf, trim, (px, py + 6), 2)
        pygame.draw.circle(surf, _shade(trim, -30), (px, py + 6), 2, 1)
    # A frilled tail tuft at the back end.
    for fa in (-30, 0, 30):
        fx = bx0 - 3 + int(math.cos(math.radians(fa)) * 5)
        fy = seg_pts[0][1] + int(math.sin(math.radians(fa)) * 5)
        pygame.draw.circle(surf, trim, (fx, fy), 2)
    # TWO pairs of dancer legs from under the cloth: a REAR pair (back/left) and a
    # FRONT pair (under the head), so it clearly reads "two people in one costume".
    leg = pr._retint_person((58, 48, 58), night)
    legpx = _cap_lum((150, 120, 70), pal)             # gold trouser cuffs (capped)
    for lx, ph, back in ((sx - 26, 0.0, True), (sx - 20, math.pi, True),
                         (sx + 6, 0.7, False), (sx + 12, math.pi + 0.7, False)):
        step = int(max(0.0, math.sin(t * 4.0 + ph)) * 3)
        fy = feet - (10 if back else 9)
        pygame.draw.line(surf, leg, (lx, fy), (lx + (1 if step else -1), feet - 1), 3)
        pygame.draw.line(surf, legpx, (lx, feet - 2), (lx + (1 if step else -1), feet), 3)

    # ── the lion HEAD — a wide ridged horned mask with a scalloped frill mane and
    # a gaping mouth, held high at the FRONT (right) of the body. ───────────────
    head_cx = sx + 22
    head_cy = body_y - 7 - bob
    # Festival accents are routed through _cap_lum so even the bright gold/ivory
    # mask never spikes a near-life pixel over the cap at night (warm bloom only).
    horn = _cap_lum((235, 200, 90), pal)
    horn_dk = _cap_lum((180, 145, 60), pal)
    face = _cap_lum((225, 205, 170), pal)   # ivory mask, not white
    face_dk = _cap_lum((175, 150, 120), pal)
    green = _cap_lum((70, 150, 110), pal)
    red = _cap_lum((210, 70, 60), pal)
    gold = _cap_lum((230, 190, 90), pal)
    # (b) the SCALLOPED MANE — an arc of small gold/green/red frill triangles
    # ringing the face (front-facing half-ring, densest over the brow).
    frill_cols = (gold, green, red)
    for k, ang in enumerate(range(-150, 151, 22)):
        rad = math.radians(ang)
        mx = head_cx + int(math.cos(rad) * 13)
        my = head_cy + int(math.sin(rad) * 12)
        c = frill_cols[k % 3]
        pygame.draw.polygon(surf, _shade(c, -28), [
            (mx - 3, my + 2), (mx + 3, my + 2),
            (mx + int(math.cos(rad) * 5), my + int(math.sin(rad) * 5))])
        pygame.draw.polygon(surf, c, [
            (mx - 2, my + 1), (mx + 2, my + 1),
            (mx + int(math.cos(rad) * 4), my + int(math.sin(rad) * 4))])
    # (a) a WIDER ridged head: a flat-topped dome wider than tall, with a raised
    # brow bump, not a soft circle.
    pygame.draw.ellipse(surf, face_dk, (head_cx - 12, head_cy - 9, 24, 19))
    pygame.draw.ellipse(surf, face, (head_cx - 11, head_cy - 8, 22, 16))
    # The brow ridge — a darker raised band across the upper face.
    pygame.draw.arc(surf, face_dk, (head_cx - 11, head_cy - 9, 22, 14),
                    math.radians(195), math.radians(345), 3)
    # A central HORN/brow bump on top (gold, ridged).
    pygame.draw.polygon(surf, horn_dk, [
        (head_cx - 3, head_cy - 7), (head_cx + 3, head_cy - 7),
        (head_cx + 1, head_cy - 16), (head_cx - 1, head_cy - 16)])
    pygame.draw.polygon(surf, horn, [
        (head_cx - 2, head_cy - 8), (head_cx + 2, head_cy - 8),
        (head_cx, head_cy - 15)])
    pygame.draw.circle(surf, horn, (head_cx, head_cy - 15), 2)
    # Two side ear/horn nubs flanking the brow.
    for ex in (-9, 9):
        pygame.draw.circle(surf, gold, (head_cx + ex, head_cy - 6), 2)
        pygame.draw.circle(surf, _shade(gold, -30), (head_cx + ex, head_cy - 6), 2, 1)
    # The eyes — capped IVORY/amber sclera (never white) under a heavy brow, with a
    # dark pupil so they read as carved festival-mask eyes.
    eye = _cap_lum((150, 138, 112), pal)
    for ex in (-5, 5):
        pygame.draw.circle(surf, _shade(eye, -34), (head_cx + ex, head_cy - 2), 3)
        pygame.draw.circle(surf, eye, (head_cx + ex, head_cy - 2), 2)
        pygame.draw.circle(surf, (28, 22, 26), (head_cx + ex, head_cy - 1), 1)
    # (c) a GAPING MOUTH — a dark notch with a red/gold lip line; the jaw bounces a
    # touch with the bob so it reads "snapping".
    jaw = 2 + int(max(0.0, math.sin(t * 3.2 + 0.5)) * 2)
    pygame.draw.polygon(surf, (26, 18, 22), [
        (head_cx - 8, head_cy + 4), (head_cx + 8, head_cy + 4),
        (head_cx + 6, head_cy + 6 + jaw), (head_cx - 6, head_cy + 6 + jaw)])
    pygame.draw.line(surf, red, (head_cx - 8, head_cy + 4),
                     (head_cx + 8, head_cy + 4), 2)
    pygame.draw.line(surf, _lip_ivory(pal), (head_cx - 6, head_cy + 6 + jaw),
                     (head_cx + 6, head_cy + 6 + jaw), 1)
    # Two ivory fangs at the lip. The plain _cap_lum path over-retints these toward
    # the cool night and lands them ~138 luma, which reads crisp on terracotta but
    # flat on the cool base. _fang_ivory holds a warm ivory at the fang allowance
    # (~145 luma, still well under the coin's ~248) and seats each fang on a dark
    # gum line so it pops the same on the grey-taupe base.
    fang = _fang_ivory(pal)
    # A deep, near-black warm gum seat (independent of the fang shade so it bites
    # the same on the cool base) plus a 1px warm tip highlight, so each ivory fang
    # carries its OWN value range and stays crisp against cool-grey surroundings —
    # not just relying on the mask behind it for contrast.
    fang_sh = (30, 20, 18)
    fang_lt = _warm_ivory_cap((214, 188, 152), pal, cap=144)
    for fx in (-4, 4):
        pts = [(head_cx + fx - 1, head_cy + 4), (head_cx + fx + 1, head_cy + 4),
               (head_cx + fx, head_cy + 6)]
        pygame.draw.polygon(surf, fang_sh, [
            (p[0], p[1] + 1) for p in pts])     # dark seat for crisp separation
        pygame.draw.polygon(surf, fang, pts)
        # A 1px brighter ivory along the fang's lit top edge gives it internal
        # value range so it reads carved, not a flat blob, on either base.
        pygame.draw.line(surf, fang_lt, (head_cx + fx - 1, head_cy + 4),
                         (head_cx + fx + 1, head_cy + 4), 1)
    # A red nose bridge above the mouth.
    pygame.draw.circle(surf, red, (head_cx, head_cy + 2), 2)
    # A capped warm glow off the lit mask at night so it reads festive, not flat.
    _near_glow(surf, head_cx, head_cy, pal, radius=14, color=(255, 160, 100))


# ── a tall festival BANNER pole for the night/dusk near edge (clear zone only) ─

def _near_banner(surf, sx, pal, *, feet_y=NEAR_GROUND_Y):
    """A near darchog-style banner pole at the front edge — a vertical accent that
    only stands in a clear horizontal zone (it's tall). Banner colour warms by
    biome; lantern at the top is capped + gated at night."""
    night = _nightf(pal)
    banner = _mix((190, 60, 50), (70, 64, 96), 0.30 * night)
    draw_darchog_pole(surf, sx, feet_y, 40, banner)
    if _is_dark(pal):
        # draw_darchog_pole tops the pole with an uncapped gold finial (220,180,60)
        # that spiked over the night cap; overpaint it capped at night.
        pygame.draw.circle(surf, _cap_lum((210, 175, 90), pal), (sx, feet_y - 40), 2)
        # A small paper lantern hung at the pole top, drawn from scratch with a
        # CAPPED warm shell so its core never out-shines the coin (the game helper
        # paints an uncapped near-white core + bright body that spiked the cap).
        lcy = feet_y - 40
        shell = _cap_lum((150, 70, 60), pal)
        shell_lt = _cap_lum((150, 96, 80), pal)
        pygame.draw.line(surf, (40, 30, 25), (sx, lcy), (sx, lcy + 3), 1)
        pygame.draw.ellipse(surf, shell, (sx - 4, lcy + 3, 8, 11))
        pygame.draw.ellipse(surf, shell_lt, (sx - 3, lcy + 4, 6, 9))
        pygame.draw.rect(surf, (50, 34, 26), (sx - 3, lcy + 3, 6, 2))
        pygame.draw.rect(surf, (50, 34, 26), (sx - 3, lcy + 12, 6, 2))
        _near_glow(surf, sx, lcy + 8, pal, radius=10, color=(255, 150, 100))


# ══════════════════════════════════════════════════════════════════════════
# Per-phase near-lane painters. General near life in every phase + the phase's
# performance, drawn back-to-front within the lane. World-anchored at NEAR_MULT.
# ══════════════════════════════════════════════════════════════════════════

def _general_pedestrians(surf, w, scroll, pal, t):
    """A couple of LARGER pedestrians crossing the front edge + the near dog. These
    are SHORT, so they may pass under the bird/pillar lanes. World-anchored so they
    parallax with the near lane and tile at the wrap."""
    # Two repeating pedestrian anchors at distinct periods so they don't lockstep.
    for sx, k in _near_xs(scroll, w, 196, x0=20):
        _scaled_cast(surf, pr.draw_strollers, sx, pal, 1.6, t=t)
    for sx, k in _near_xs(scroll, w, 224, x0=150):
        _scaled_cast(surf, pr.draw_kids, sx, pal, 1.55, t=t, n=2)
    # The near dog trots across the front on its own anchor.
    for sx, k in _near_xs(scroll, w, 300, x0=96):
        _near_dog(surf, sx, pal, t=t, scale=1.7)


def _general_greenery(surf, w, scroll, pal, t):
    """Low near plants on the front edge — larger planters + a vine tub + the odd
    pine. Short greenery may sit under the lanes; the taller pine is gated to a
    clear zone."""
    for sx, k in _near_xs(scroll, w, 260, x0=60):
        _near_planter(surf, sx, pal)
    for sx, k in _near_xs(scroll, w, 320, x0=200):
        _near_vine_lantern(surf, sx, pal)
    for sx, k in _near_xs(scroll, w, 300, x0=12):
        if _tall_ok(sx, 12):
            _near_pine(surf, sx, pal)


def phase_day(surf, w, gy, h, scroll, pal, t):
    """DAY · Pastoral Morning. Front edge: larger pedestrians + dog + planters; the
    performance is a casual BUSKER / juggler in a clear mid-left zone. No glow."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    # The juggler busks in the open near-left zone, nudged IN from the cell edge
    # so the ball arc doesn't crowd the border (clear of the lanes' centres).
    perf_juggler(surf, 44, pal, t)


def phase_golden(surf, w, gy, h, scroll, pal, t):
    """GOLDEN HOUR · Promenade. Front edge fills out: a STREET MUSICIAN with a small
    head-bobbing watching arc. Warm, still unlit."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    perf_musician(surf, 38, pal, t)


def phase_dusk(surf, w, gy, h, scroll, pal, t):
    """DUSK · Lamps Lighting. The crowd grows and a STILT-WALKER warms up as the
    lamps come on; a near banner pole lights in the clear left zone. Brazier glows."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    for sx, k in _near_xs(scroll, w, 340, x0=30):
        if _tall_ok(sx, 6):
            _near_banner(surf, sx, pal)
    for sx, k in _near_xs(scroll, w, 300, x0=120):
        _near_brazier(surf, sx, pal, t=t)
    perf_stilt(surf, 40, pal, t)


def phase_night(surf, w, gy, h, scroll, pal, t):
    """NIGHT · Festival. The peak: the full LION DANCE + drummer + a bigger crowd on
    the front edge, braziers + a banner glowing (all capped, gated). The coin +
    parrot still draw after this and stay brightest."""
    _general_greenery(surf, w, scroll, pal, t)
    _general_pedestrians(surf, w, scroll, pal, t)
    for sx, k in _near_xs(scroll, w, 340, x0=30):
        if _tall_ok(sx, 6):
            _near_banner(surf, sx, pal)
    for sx, k in _near_xs(scroll, w, 280, x0=110):
        _near_brazier(surf, sx, pal, t=t)
    # The lion dance owns the near-left festival zone, kept clear of the lanes.
    perf_lion_dance(surf, 44, pal, t)


# Dispatch by phase NAME (day/golden/dusk/night) — the render harness derives the
# name per column from the PHASES list.
_DISPATCH = {
    "day": phase_day,
    "golden": phase_golden,
    "dusk": phase_dusk,
    "night": phase_night,
}


def add_near_lane(surf, w, gy, h, scroll, pal, phase_name, t):
    """Paint the NEAR / FRONT activity lane on top of the far lane (and under the
    gameplay actors). Dispatches general near life + the phase's performance."""
    painter = _DISPATCH.get(phase_name, phase_day)
    painter(surf, w, gy, h, scroll, pal, t)
