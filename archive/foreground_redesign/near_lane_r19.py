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

def _near_glow(surf, cx, cy, pal, *, radius=12, color=(255, 170, 110)):
    if not _is_dark(pal):
        return
    s = _lit_intensity(pal)
    if s <= 0.02:
        return
    peak = int(sp._GLOW_PEAK * 1.0 * s)
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
        ember = _cap150((180, 90, 50))
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


def perf_juggler(surf, sx, pal, t):
    """DAY · a casual daytime BUSKER / juggler — a single performer tossing three
    balls in a small arc. Low-key morning act; no crowd, no glow."""
    night = _nightf(pal)
    robe = pr._retint_person((196, 92, 70), night)     # warm terracotta tunic
    robe_dk = pr._retint_person((150, 60, 52), night)
    hair = pr._retint_person((70, 50, 40), night)
    feet = NEAR_GROUND_Y
    hx, hy = _perf_body(surf, sx, feet, robe, robe_dk, hair, pal,
                        h=20, w=9, arms='juggle', arm_t=t * 3.0)
    # Three balls on a small juggling cascade above the hands.
    ball_cols = ((220, 200, 80), (210, 90, 90), (90, 160, 200))
    for i, col in enumerate(ball_cols):
        ph = (t * 1.6 + i / 3.0) % 1.0
        bx = sx + int(math.sin(ph * math.tau) * 9)
        by = hy - 4 - int(math.sin(ph * math.pi) * 13)
        col = pr._retint_person(col, night)
        pygame.draw.circle(surf, _shade(col, -22), (bx, by), 3)
        pygame.draw.circle(surf, col, (bx, by), 2)


def perf_musician(surf, sx, pal, t):
    """GOLDEN HOUR · a street MUSICIAN with a drum, gathering a small watching arc.
    A seated/standing drummer + a barrel drum; the crowd head-bobs around him."""
    night = _nightf(pal)
    robe = pr._retint_person((90, 110, 160), night)    # indigo musician robe
    robe_dk = pr._retint_person((58, 74, 116), night)
    hair = pr._retint_person((60, 45, 40), night)
    feet = NEAR_GROUND_Y
    # Watching arc first (behind), then the drum, then the musician in front.
    _watch_arc(surf, sx, pal, t, feet_y=feet)
    # A barrel drum on the deck before him.
    dx = sx - 13
    dy = feet
    drum = _mix((150, 60, 45), (70, 70, 96), 0.30 * night)
    pygame.draw.ellipse(surf, _shade(drum, -22), (dx - 9, dy - 16, 18, 16))
    pygame.draw.ellipse(surf, drum, (dx - 8, dy - 16, 16, 14))
    head_col = _mix((225, 205, 170), (70, 76, 100), 0.32 * night)
    pygame.draw.ellipse(surf, head_col, (dx - 7, dy - 16, 14, 5))
    pygame.draw.ellipse(surf, _shade(head_col, -24), (dx - 7, dy - 16, 14, 5), 1)
    _perf_body(surf, sx + 4, feet, robe, robe_dk, hair, pal,
               h=20, w=9, arms='drum', arm_t=t * 4.5)


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

    # Drummer + drum to the right of the lion.
    drx = sx + 30
    robe = pr._retint_person((110, 60, 70), night)
    robe_dk = pr._retint_person((74, 40, 50), night)
    hair = pr._retint_person((50, 40, 38), night)
    ddx, ddy = drx - 12, feet
    drum = _mix((160, 55, 45), (70, 70, 96), 0.34 * night)
    pygame.draw.ellipse(surf, _shade(drum, -24), (ddx - 10, ddy - 18, 20, 18))
    pygame.draw.ellipse(surf, drum, (ddx - 9, ddy - 18, 18, 15))
    dhead = _cap150((210, 150, 90)) if _is_dark(pal) else (225, 200, 160)
    pygame.draw.ellipse(surf, dhead, (ddx - 8, ddy - 18, 16, 5))
    _near_glow(surf, ddx, ddy - 14, pal, radius=11, color=(255, 150, 90))
    _perf_body(surf, drx + 4, feet, robe, robe_dk, hair, pal,
               h=21, w=9, arms='drum', arm_t=t * 6.0)

    # ── the LION (two dancers under a flowing body) ───────────────────────────
    # Rear dancer's legs under a draped cloth body; front dancer holds the head.
    bob = int(max(0.0, math.sin(t * 3.2)) * 3)        # the lion's bouncy lift
    body_y = feet - 16 - bob
    # Flowing cloth body — a long undulating drape from the head back to the rear.
    cloth = pr._retint_person((205, 70, 55), night)   # festive red
    cloth_dk = pr._retint_person((150, 45, 42), night)
    trim = pr._retint_person((230, 195, 90), night)   # gold trim
    bx0 = sx - 30                                      # tail end (behind head)
    seg_pts = []
    for i in range(7):
        tt = i / 6.0
        px = bx0 + int(tt * 30)
        wave = int(math.sin(t * 3.0 + tt * 4.0) * 3)
        py = body_y + 6 + wave + int(tt * 4)
        seg_pts.append((px, py))
    # Draped body as a thick polygon hugging the spine points + a hem.
    top = [(p[0], p[1] - 6) for p in seg_pts]
    bot = [(p[0], p[1] + 6) for p in reversed(seg_pts)]
    pygame.draw.polygon(surf, cloth_dk, top + bot)
    pygame.draw.polygon(surf, cloth, [(p[0], p[1] - 4) for p in seg_pts] +
                        [(p[0], p[1] + 4) for p in reversed(seg_pts)])
    # Scalloped gold trim along the hem.
    for px, py in seg_pts[::2]:
        pygame.draw.circle(surf, trim, (px, py + 5), 1)
    # Two pairs of dancer legs poking from under the cloth (front + rear dancer).
    leg = pr._retint_person((60, 50, 60), night)
    for lx, ph in ((sx - 24, 0.0), (sx - 18, math.pi), (sx + 2, 0.7), (sx + 8, math.pi + 0.7)):
        step = int(max(0.0, math.sin(t * 4.0 + ph)) * 3)
        pygame.draw.line(surf, leg, (lx, feet - 8), (lx + (1 if step else -1), feet), 2)

    # The lion HEAD — a bulbous decorated dome held high at the front. Kept in a
    # clear horizontal zone via the caller; here it crowns the front of the body.
    head_cx = sx + 18
    head_cy = body_y - 6 - bob
    horn = pr._retint_person((235, 200, 90), night)
    mane = pr._retint_person((215, 75, 55), night)
    mane_dk = pr._retint_person((150, 48, 44), night)
    face = pr._retint_person((245, 225, 200), night)
    # Furry mane ring behind the face.
    for ang in range(0, 360, 30):
        mx = head_cx + int(math.cos(math.radians(ang)) * 11)
        my = head_cy + int(math.sin(math.radians(ang)) * 10)
        pygame.draw.circle(surf, mane_dk, (mx, my), 3)
        pygame.draw.circle(surf, mane, (mx, my), 2)
    # Big round head.
    pygame.draw.circle(surf, _shade(face, -28), (head_cx, head_cy), 10)
    pygame.draw.circle(surf, face, (head_cx, head_cy), 9)
    # Brow ridge + two big googly eyes.
    pygame.draw.arc(surf, mane_dk, (head_cx - 9, head_cy - 9, 18, 12),
                    math.radians(200), math.radians(340), 2)
    blink = 1 if (math.sin(t * 2.0) > -0.9) else 0
    for ex in (-4, 4):
        pygame.draw.circle(surf, (245, 245, 240), (head_cx + ex, head_cy - 2), 3)
        if blink:
            pygame.draw.circle(surf, (30, 25, 30), (head_cx + ex, head_cy - 2), 2)
    # A golden horn crest + a red nose.
    pygame.draw.polygon(surf, horn, [
        (head_cx, head_cy - 9), (head_cx - 3, head_cy - 14), (head_cx + 3, head_cy - 14)])
    pygame.draw.circle(surf, pr._retint_person((220, 70, 60), night),
                       (head_cx, head_cy + 4), 3)
    # A tiny mouth line.
    pygame.draw.arc(surf, mane_dk, (head_cx - 4, head_cy + 3, 9, 6),
                    math.radians(20), math.radians(160), 1)
    # A capped warm glow off the lit head at night so it reads festive, not flat.
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
        draw_paper_lantern(surf, sx, feet_y - 44, strand=4, scale=0.7, color='red')
        # Re-cap the lantern's own (uncapped) glow by overpainting a capped halo.
        _near_glow(surf, sx, feet_y - 36, pal, radius=10, color=(255, 150, 100))


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
    # The juggler busks in the open near-left zone (clear of the lanes' centres).
    perf_juggler(surf, 36, pal, t)


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
