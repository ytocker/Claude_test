"""Round-17 LIVING PROMENADE — a day->night ESCALATION of one promenade.

Rounds 14-16 presented the sidewalk dressing as five separate STYLES. The
corrected intent: those are really the SAME promenade with layers stacked on.
So round 17 turns the layers into a gradual time-of-day escalation — each phase
is its own EVENT, sparse by day -> a full festival by night — and POPULATES the
walk with LIVING characters (sheep, dog, kids, an old man, a vendor) so the
world feels inhabited rather than decorated.

Four phase events, escalating:

  DAY    Pastoral morning — planters + prayer-flag bunting + a kiosk just
         opening; sheep flock grazing, a running dog, kids, a wishing well.
         Few/no lights.
  GOLDEN Afternoon promenade — lamp posts up, a lantern garland being strung,
         a busy kiosk; the old man on a bench with a companion, kids, the dog.
         Warm amber, still unlit.
  DUSK   Lamps lighting — lamps + fairy lights JUST beginning to glow, the
         kiosk lantern lit, planters; a couple of strolling figures, a napper.
  NIGHT  Festival — lantern garland + fairy lights + lamp posts all glowing
         (capped), a campfire, the kiosk glowing; a few cozy figures.

Dressing primitives are recombined from sidewalk_props_r15 (lamp posts, lantern
garland, fairy lights, planters); prayer-flag bunting comes from
game.pillar_variants. The KIDS, OLD MAN and KIOSK are net-new here.

Glow contract preserved: capped under the coin (NIGHT_LUMA_CAP), gated to a dark
sky, and given a gentle dusk->night fade-in so dusk reads "lamps just lighting"
rather than dead-then-on. DAY/GOLDEN are unlit shells.

Pure-Pygame / pygbag-safe (fill, blit, draw.*, SRCALPHA, BLEND_RGB_ADD only).
No numpy / gfxdraw / per-frame surfarray. Nothing here is written into game/.
"""
from __future__ import annotations

import math

import pygame

import sidewalk_props_r15 as sp
from game.pillar_variants import draw_prayer_flags

# Read-only access to the live ambient characters — instantiated, stepped a few
# frames to a pleasant gait, then drawn at a chosen world-x.
from game.ambient import (
    _SheepPack, _RunningDog, _WishingWell, _Bench, _Napper, _Campfire,
    _draw_bench_person,
)

GROUND_Y = sp.GROUND_Y  # 595 — the sidewalk top edge; feet rest here.

_mix = sp._mix
_shade = sp._shade
_clamp = sp._clamp
_nightf = sp._nightf


# ── glow gate: a gentle dusk->night fade-in (own gate, not r15's) ─────────────
#
# r15's _add_lamp_glow only begins above night-ness 0.45, which leaves DUSK
# (night ~0.38) dead. The DUSK event is supposed to read "lamps JUST lighting",
# so the promenade uses its own gate that starts as soon as the sky is dark and
# rises smoothly into the full night festival. The additive peak stays the r15
# cap so a coin is still the brightest object on screen.

def _glow_strength(pal):
    """0 by day, a small lift at dusk, full at night. Gated to a dark sky so the
    bright DAY/GOLDEN cells stay unlit shells."""
    if not sp._is_dark_sky(pal):
        return 0.0
    night = _nightf(pal)
    # Dusk (~0.38) -> ~0.34 strength; night (~0.97) -> 1.0. A floor so the very
    # first lit phase still reads as "coming on".
    return max(0.0, min(1.0, (night - 0.30) / 0.62))


def _glow(surf, cx, cy, pal, *, radius=14, color=(255, 196, 110), scale=1.0):
    """Capped warm halo with the promenade's own dusk->night strength curve."""
    s = _glow_strength(pal)
    if s <= 0.02:
        return
    peak = int(sp._GLOW_PEAK * scale * s)
    if peak <= 1:
        return
    g = sp._warm_glow(radius, color, peak)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ══════════════════════════════════════════════════════════════════════════
# NEW characters
# ══════════════════════════════════════════════════════════════════════════
#
# All live in the lower promenade band (feet at GROUND_Y) and are kept clear of
# the bird lane (x≈48..188) and the pillar lane (x≈212..320) by their chosen
# world-x anchors. They borrow the _draw_bench_person body idiom so the new
# people match the existing bench couple in scale and palette.


def _retint_person(col, night):
    """Cool a clothing colour toward the night ground band so a new figure sits
    in the same value family as the retinted floor (matches the bench tint)."""
    if night <= 0.05:
        return col
    return _mix(col, (60, 70, 100), 0.34 * night)


def draw_kids(surf, sx, pal, *, t=0.0, n=3):
    """2-3 small walking/playing children: shorter, rounder, brighter-clothed
    than the bench adults. Built from a scaled-down _draw_bench_person idiom — a
    little body block + round head + simple hair — with a playful gait bob and a
    couple of stubby running legs so they read as kids at play, not statues."""
    night = _nightf(pal)
    skin = _retint_person((235, 195, 150), night)
    # Bright primary clothes so the kids pop against the muted shan-shui floor.
    kit = [
        ((235, 95, 90), (175, 55, 60), (90, 55, 35)),    # red shirt
        ((90, 165, 220), (50, 110, 165), (60, 45, 35)),  # blue shirt
        ((250, 200, 70), (200, 150, 40), (70, 50, 35)),  # yellow shirt
    ]
    spread = (-14, 6, 22)
    for i in range(n):
        dx = spread[i]
        shirt, shirt_dk, hair = (_retint_person(c, night) for c in kit[i])
        # Each kid runs on its own phase so the trio reads as alive.
        gait = math.sin(t * 6.0 + i * 1.7)
        lift = -max(0.0, gait) * 1.5  # only the up-swing lifts
        bx = sx + dx
        feet_y = GROUND_Y - 1 + int(round(lift))
        body_h = 6           # shorter than the adult 8 -> reads as a child
        body_w = 5
        body_y = feet_y - body_h - 3
        # Rounder torso (filled ellipse, not a hard rect) + bright shirt.
        pygame.draw.ellipse(surf, shirt, (bx, body_y, body_w, body_h + 1))
        pygame.draw.ellipse(surf, shirt_dk, (bx, body_y, body_w, body_h + 1), 1)
        # Bigger head relative to body — the universal "child" cue.
        hx, hy = bx + body_w // 2, body_y - 3
        pygame.draw.circle(surf, skin, (hx, hy), 3)
        pygame.draw.polygon(surf, hair, [(hx - 3, hy), (hx + 3, hy), (hx, hy - 4)])
        pygame.draw.circle(surf, (30, 20, 15), (hx - 1, hy), 0)
        pygame.draw.circle(surf, (30, 20, 15), (hx + 1, hy), 0)
        # Two stubby running legs, swinging opposite phase.
        leg = _shade(shirt_dk, -18)
        swing = int(round(gait * 2))
        pygame.draw.line(surf, leg, (bx + 1, body_y + body_h),
                         (bx + 1 - swing, feet_y), 1)
        pygame.draw.line(surf, leg, (bx + body_w - 1, body_y + body_h),
                         (bx + body_w - 1 + swing, feet_y), 1)
        # The lead kid reaches an arm up (chasing / waving) — playful gesture.
        if i == 0:
            pygame.draw.line(surf, shirt, (bx + body_w - 1, body_y + 1),
                             (bx + body_w + 2, body_y - 2 - max(0, swing)), 1)


def draw_old_man(surf, sx, pal, *, t=0.0, seated_bench=False):
    """A distinct elderly figure for the temple world: grey hair + a short grey
    beard, a slightly stooped posture, a dark robe, and a walking cane. Adapts
    the _draw_bench_person body idiom with the cane and grey colours. When
    `seated_bench` he sits a touch lower (resting on the bench seat)."""
    night = _nightf(pal)
    skin = _retint_person((226, 190, 150), night)
    robe = _retint_person((96, 86, 96), night)        # muted plum-grey robe
    robe_dk = _retint_person((64, 56, 66), night)
    grey = _retint_person((205, 205, 200), night)      # grey hair/beard
    cane_c = _retint_person((120, 84, 52), night)

    feet_y = GROUND_Y - 1
    body_h = 9 if not seated_bench else 8
    body_w = 6
    body_y = feet_y - body_h - (3 if not seated_bench else 1)
    # Stooped torso — a slightly forward-leaning robe block.
    lean = 1
    pygame.draw.polygon(surf, robe, [
        (sx, body_y + 1), (sx + body_w, body_y),
        (sx + body_w + lean, body_y + body_h), (sx - lean, body_y + body_h)])
    pygame.draw.polygon(surf, robe_dk, [
        (sx, body_y + 1), (sx + body_w, body_y),
        (sx + body_w + lean, body_y + body_h), (sx - lean, body_y + body_h)], 1)
    # Head tipped forward (the stoop), grey hair cap + a short beard.
    hx, hy = sx + body_w // 2 + lean, body_y - 2
    pygame.draw.circle(surf, skin, (hx, hy), 3)
    pygame.draw.polygon(surf, grey, [(hx - 3, hy - 1), (hx + 3, hy - 1), (hx, hy - 4)])
    pygame.draw.line(surf, grey, (hx - 2, hy + 2), (hx + 2, hy + 2), 1)  # beard
    pygame.draw.circle(surf, (30, 20, 15), (hx + 1, hy), 0)
    if not seated_bench:
        # A walking cane in the leading hand, tapping in a slow gait.
        tap = int(round(math.sin(t * 1.3) * 1))
        cx0 = sx + body_w + 2
        pygame.draw.line(surf, cane_c, (cx0, body_y + 3),
                         (cx0 + 2 + tap, feet_y), 1)
        # Two robe-hem feet shuffling.
        pygame.draw.line(surf, robe_dk, (sx + 1, body_y + body_h),
                         (sx + 1, feet_y), 1)
        pygame.draw.line(surf, robe_dk, (sx + body_w - 1, body_y + body_h),
                         (sx + body_w - 1 + tap, feet_y), 1)


def draw_strollers(surf, sx, pal, *, t=0.0):
    """A couple of strolling adults for the quiet DUSK event — the bench-person
    idiom walking, with a slow gait and a small head bob. Calm, unhurried."""
    night = _nightf(pal)
    pairs = [((180, 120, 170), (130, 80, 120), (70, 50, 40)),   # plum coat
             ((90, 140, 165), (55, 95, 115), (60, 45, 35))]      # teal coat
    for i, (shirt, shirt_dk, hair) in enumerate(pairs):
        shirt, shirt_dk, hair = (_retint_person(c, night) for c in (shirt, shirt_dk, hair))
        dx = -8 + i * 14
        gait = math.sin(t * 2.2 + i * 1.1)
        feet_y = GROUND_Y - 1 - int(round(max(0.0, gait) * 0.8))
        body_y = feet_y - 8 - 3
        _draw_bench_person(surf, sx + dx, body_y, shirt, shirt_dk, hair)
        # Walking legs under the body block.
        leg = _shade(shirt_dk, -16)
        sw = int(round(gait * 2))
        pygame.draw.line(surf, leg, (sx + dx + 1, body_y + 8),
                         (sx + dx + 1 - sw, feet_y), 1)
        pygame.draw.line(surf, leg, (sx + dx + 4, body_y + 8),
                         (sx + dx + 4 + sw, feet_y), 1)


# ── KIOSK / vendor stall: a pagoda-roofed market stall ───────────────────────
#
# Net-new. A small temple-market stall: a tiered curved pagoda roof, a striped
# awning, a counter with goods, a hanging paper lantern, and (optionally) a tiny
# vendor head behind the counter. World-anchored on the sidewalk at GROUND_Y,
# kept narrow so it slots into a clear strip without crowding the bird/pillar
# lanes. Its "open-ness" escalates: shutter down by day, goods + awning by
# golden, the lantern lit at dusk/night.

def _pagoda_roof(surf, cx, ridge_y, half_w, pal, *, tiers=2):
    """A tiered, upswept temple roof. Each tier is a low trapezoid with curled
    eave tips drawn as short up-flicks, in the stage stone tones so it belongs to
    the pagoda pillar's masonry family."""
    night = _nightf(pal)
    tile = _mix(pal.get('stone_dark', (95, 80, 70)), (120, 96, 78), 0.5)
    tile = _mix(tile, (54, 60, 86), 0.32 * night)
    tile_lt = _shade(tile, 18)
    ridge = _shade(tile, -22)
    y = ridge_y
    hw = half_w
    for ti in range(tiers):
        eave_y = y + 7
        # Roof slab as a trapezoid wider at the eave.
        pygame.draw.polygon(surf, tile, [
            (cx - hw * 0.4, y), (cx + hw * 0.4, y),
            (cx + hw, eave_y), (cx - hw, eave_y)])
        pygame.draw.line(surf, tile_lt, (cx - hw * 0.4, y), (cx + hw * 0.4, y), 1)
        # Upswept eave tips (the temple curl).
        pygame.draw.line(surf, ridge, (cx - hw, eave_y), (cx - hw - 2, eave_y - 3), 2)
        pygame.draw.line(surf, ridge, (cx + hw, eave_y), (cx + hw + 2, eave_y - 3), 2)
        y = eave_y - 1
        hw = int(hw * 0.78)
    # A small finial knob on the ridge.
    pygame.draw.circle(surf, _shade(tile_lt, 10), (int(cx), int(ridge_y - 2)), 1)


def draw_kiosk(surf, sx, pal, *, t=0.0, openness=1.0):
    """A pagoda-roofed vendor stall on the sidewalk. `openness` 0..1 escalates
    the read: 0 -> just opening (low shutter, no goods), 1 -> fully open (awning
    out, goods on the counter, a vendor, a lit hanging lantern at night)."""
    night = _nightf(pal)
    base_y = GROUND_Y - 1
    half_w = 22
    counter_h = 16
    post_top = base_y - 34   # counter + a head-height opening under the roof

    # Two corner posts (timber).
    post = _mix((92, 64, 40), (60, 66, 92), 0.30 * night)
    post_dk = _shade(post, -20)
    for px in (sx - half_w + 3, sx + half_w - 3):
        pygame.draw.rect(surf, post, (px - 1, post_top, 3, base_y - post_top))
        pygame.draw.line(surf, post_dk, (px + 1, post_top), (px + 1, base_y), 1)

    # Back wall panel between posts (so the stall reads as enclosed, not a frame).
    wall = _mix(pal.get('stone_mid', (150, 132, 110)), (150, 124, 96), 0.5)
    wall = _mix(wall, (56, 62, 88), 0.32 * night)
    pygame.draw.rect(surf, _shade(wall, -10),
                     (sx - half_w + 4, post_top + 2, (half_w - 4) * 2, 14))

    # The pagoda roof crowning the posts.
    _pagoda_roof(surf, sx, post_top - 8, half_w + 2, pal, tiers=2)

    # Counter / shop front.
    counter = _mix((120, 84, 52), (60, 66, 92), 0.30 * night)
    counter_lt = _shade(counter, 16)
    cy = base_y - counter_h
    pygame.draw.rect(surf, counter, (sx - half_w + 1, cy, (half_w - 1) * 2, counter_h))
    pygame.draw.rect(surf, counter_lt, (sx - half_w + 1, cy, (half_w - 1) * 2, 2))
    pygame.draw.rect(surf, _shade(counter, -22),
                     (sx - half_w + 1, base_y - 4, (half_w - 1) * 2, 4))

    if openness > 0.25:
        # A striped awning rolled out over the counter (the "open for business"
        # cue). Two-tone scalloped valance.
        aw = half_w + 1
        ay = cy - 5
        stripe_a = _mix((210, 70, 60), (70, 70, 96), 0.30 * night)
        stripe_b = _mix((240, 228, 210), (90, 96, 120), 0.34 * night)
        for i, ax in enumerate(range(sx - aw, sx + aw, 6)):
            col = stripe_a if i % 2 == 0 else stripe_b
            pygame.draw.polygon(surf, col, [
                (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])

    if openness > 0.5:
        # Goods on the counter — a few coloured produce/jar lumps so it reads as
        # a market stall, not an empty booth.
        goods = [((230, 120, 60), 3), ((90, 160, 90), 2), ((220, 200, 90), 3),
                 ((200, 80, 90), 2)]
        gx = sx - half_w + 6
        for col, r in goods:
            col = _mix(col, (60, 70, 100), 0.32 * night)
            pygame.draw.circle(surf, _shade(col, -16), (gx, cy - 1), r)
            pygame.draw.circle(surf, col, (gx, cy - 2), r - 1)
            gx += r + 5
        # A tiny vendor head peeking over the counter behind the goods.
        vx = sx + half_w - 9
        skin = _retint_person((226, 190, 150), night)
        pygame.draw.circle(surf, skin, (vx, cy - 4), 3)
        pygame.draw.polygon(surf, _retint_person((70, 50, 40), night),
                            [(vx - 3, cy - 4), (vx + 3, cy - 4), (vx, cy - 8)])

    # A hanging paper lantern under the eave — lit (capped) once the sky darkens.
    lx = sx + half_w - 7
    ly = post_top - 1
    lan_dark = _mix((170, 40, 40), _shade((170, 40, 40), -40), 0.6 * night)
    lan_lit = (sp._clamp_night((250, 110, 80))[:3] if sp._is_dark_sky(pal)
               else (230, 120, 90))
    pygame.draw.line(surf, (50, 35, 25), (lx, ly), (lx, ly + 4), 1)
    body = pygame.Rect(lx - 4, ly + 4, 8, 10)
    pygame.draw.ellipse(surf, lan_dark, body)
    pygame.draw.ellipse(surf, lan_lit, body.inflate(-3, -2))
    _glow(surf, lx, ly + 9, pal, radius=10, color=(255, 150, 110), scale=0.7)


# ══════════════════════════════════════════════════════════════════════════
# Phase events — each recombines dressing layers + a living cast. Painters take
# (surf, w, gy, h, scroll, pal, t) so the characters can show a gait frame.
# ══════════════════════════════════════════════════════════════════════════
#
# Anchor strategy: the cream pillar sits at the right (base x≈244); the bird
# flies at x≈90. Static dressing uses r15's lane gates. Characters are placed by
# their own clear-zone anchors in the lower band — most live left of the bird
# lane (far left, x<46) or in the mid promenade gap (x≈150..200), never on the
# bird column or the pillar base.

# Character clear zones in the lower band. The bird-lane character ban is a touch
# narrower than the tall-prop ban (characters are short and sit below the bird),
# but we still keep their CENTRES out of x≈70..110 and the pillar base.
def _char_x_ok(sx, half=14):
    if 70 - half < sx < 116 + half:        # bird column
        return False
    if 222 - half < sx < 312 + half:       # pillar base
        return False
    return True


def _stepped(cls, pal, frames, x, *, rng_seed=7):
    """Instantiate an ambient character, step it a few sim frames to a pleasant
    gait, and pin it to screen-x `x` so it can be drawn statically on the sheet
    (a still sheet can't animate; one good frame is enough to read the motion)."""
    import random as _random
    obj = cls(pal, _random.Random(rng_seed))
    obj.x = float(x)
    for _ in range(frames):
        obj.update(1 / 60.0, 0.0)   # no scroll: hold the pinned x, advance gait
        obj.x = float(x)
    return obj


def phase_day(surf, w, gy, h, scroll, pal, t):
    """DAY · Pastoral Morning. Sparse dressing: planters + prayer-flag bunting +
    a kiosk just opening. Living: a grazing sheep flock, a running dog, kids, a
    wishing well. Bright, calm, essentially unlit."""
    # Prayer-flag bunting strung high across the promenade (the morning festival
    # cue) — drawn as repeating spans so it wraps with the world.
    for xl, xr in sp._garland_spans(scroll, w, period=150, x0=20):
        draw_prayer_flags(surf, int(xl), GROUND_Y - 118, int(xr), GROUND_Y - 116, n=5)
    # A couple of planters, no lamps yet.
    for sx, k in sp._world_xs(scroll, w, 250, x0=150):
        if sp._ground_clear(sx, 12):
            sp._draw_planter(surf, sx, pal, kind='shrub')
    # Kiosk just opening (low openness) in the mid-left clear strip.
    draw_kiosk(surf, 40, pal, t=t, openness=0.2)
    # Living cast (drawn after dressing so characters read in front):
    well = _stepped(_WishingWell, pal, 20, 158)
    if _char_x_ok(158, 14):
        well.draw(surf)
    flock = _stepped(_SheepPack, pal, 40, 196)
    flock.draw(surf)                       # flock spans the mid band, low + short
    dog = _stepped(_RunningDog, pal, 30, 150)
    dog.draw(surf)
    draw_kids(surf, 200, pal, t=t, n=3)    # kids playing past the pillar's left


def phase_golden(surf, w, gy, h, scroll, pal, t):
    """GOLDEN HOUR · Afternoon Promenade. Mid dressing: lamp posts up, a lantern
    garland being strung, a busy kiosk. Living: the old man on a bench with a
    companion, kids, the dog. Warm amber, still unlit."""
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 96,
                             period=150, sag=22, per_span=2)
    for sx, k in sp._world_xs(scroll, w, 250, x0=20):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=160):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    for sx, k in sp._world_xs(scroll, w, 250, x0=125):
        if sp._ground_clear(sx, 12):
            sp._draw_planter(surf, sx, pal, kind='shrub')
    draw_kiosk(surf, 40, pal, t=t, openness=1.0)   # busy, fully open
    # The old man seated on a bench with a chatting companion, in the mid strip.
    bench = _stepped(_Bench, pal, 20, 168)
    if _char_x_ok(168, 22):
        # Draw just the bench sprite, then place the old man + a companion on it.
        bench._blit_sprite(surf)
        # Match _Bench.draw: sprite is 42x28, top at GROUND_Y-27, seat at +19.
        seat_y = (GROUND_Y - 27) + 19
        draw_old_man(surf, 158, pal, t=t, seated_bench=True)
        night = _nightf(pal)
        comp = tuple(_retint_person(c, night) for c in
                     ((215, 85, 100), (175, 50, 70), (80, 50, 30)))
        _draw_bench_person(surf, 174, seat_y - 8, *comp)
    dog = _stepped(_RunningDog, pal, 30, 150)
    dog.draw(surf)
    draw_kids(surf, 200, pal, t=t, n=2)


def phase_dusk(surf, w, gy, h, scroll, pal, t):
    """DUSK · Lamps Lighting. Lamps + fairy lights JUST beginning to glow (gated
    to the now-dark sky), the kiosk lantern lit, planters. Living: a couple of
    strolling figures + a napper resting. Lavender, quieter."""
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 92,
                          period=210, sag=26, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=24):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=94, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=158):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=88, lantern='glass')
    for sx, k in sp._world_xs(scroll, w, 250, x0=128):
        if sp._ground_clear(sx, 12):
            sp._draw_planter(surf, sx, pal, kind='conifer')
    draw_kiosk(surf, 40, pal, t=t, openness=0.8)
    napper = _stepped(_Napper, pal, 24, 156)
    if _char_x_ok(156, 17):
        napper.draw(surf)
    draw_strollers(surf, 196, pal, t=t)


def phase_night(surf, w, gy, h, scroll, pal, t):
    """NIGHT · Festival. Full festival: lantern garland + fairy lights + lamp
    posts all glowing (capped), a campfire, the kiosk glowing. Living: a few
    cozy figures. The payoff cell."""
    sp._draw_lantern_garland(surf, w, scroll, pal, top_y=GROUND_Y - 98,
                             period=118, sag=24, per_span=3)
    sp._draw_fairy_lights(surf, w, scroll, pal, top_y=GROUND_Y - 78,
                          period=200, sag=22, per_span=5)
    for sx, k in sp._world_xs(scroll, w, 250, x0=18):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=96, lantern='red')
    for sx, k in sp._world_xs(scroll, w, 250, x0=152):
        if sp._post_ok(sx):
            sp._draw_lamp_post(surf, sx, pal, style='ornate', height=90, lantern='gold')
    for sx, k in sp._world_xs(scroll, w, 250, x0=126):
        if sp._ground_clear(sx, 12):
            sp._draw_planter(surf, sx, pal, kind='conifer')
    draw_kiosk(surf, 40, pal, t=t, openness=1.0)
    # A campfire warms the mid strip (the live _Campfire carries its own capped
    # additive halo + flicker, world-anchored at SCROLL_MULT=0.7).
    fire = _Campfire(pal)
    fire.x = float(150)
    for _ in range(40):
        fire.update(1 / 60.0, 0.0)
        fire.x = float(150)
    if _char_x_ok(150, 12):
        fire.draw(surf)
    # A couple of cozy figures gathered near the fire / strolling home.
    draw_strollers(surf, 196, pal, t=t)


# (label, painter)
PHASES_R17 = [
    ("DAY · Pastoral Morning", phase_day),
    ("GOLDEN HOUR · Afternoon Promenade", phase_golden),
    ("DUSK · Lamps Lighting", phase_dusk),
    ("NIGHT · Festival", phase_night),
]
