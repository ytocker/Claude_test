"""Food-market stall structures for the daytime FOOD-MARKET beat.

Five far-lane booth structures the cast works at — bamboo STEAMER, soup CAULDRON,
skewer GRILL, stir-fry WOK, tea/drinks URN — each the shared draw_kiosk-style
temple booth (posts + striped awning + counter + back wall) carrying a distinct
cooking apparatus with its own ANIMATED steam/smoke. Art-director SHIP-READY
(docs/sidewalk_overhaul/food_stalls/round_2.png).

The user asked for a real food market: a steaming stall, a soup cauldron, a
barbecue grill. The day_cast vendor pool's fanning + ladling poses are stationed
at the grill + cauldron so the cast reads as working the stalls.

Steam/smoke are translucent puffs that visibly CLIMB and fade with t (rising
motion, not a static smudge). Coals/flame/embers are warm but _cap150-clamped so
nothing out-pops the gold coin or breaks the night-glow ceiling. Pure-Pygame /
pygbag-safe (draw.* + Surface, BLEND_RGB_ADD for soft glow). Night cooling via
ped_cast._retint_person.
"""
from __future__ import annotations

import math

import pygame

from game.foreground_props import _mix, _shade, _clamp
from game.ped_cast import _retint_person as _retint

NIGHT_GLOW_CAP = 150
HALF_W = 22


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _cap150(col):
    """Hold a lit ember/flame/glow under the 150 luma ceiling without flattening
    hue — the contract that keeps the gold coin the brightest object."""
    y = _luma(col)
    if y <= NIGHT_GLOW_CAP:
        return col
    k = NIGHT_GLOW_CAP / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


def _wisp(surf, x, y0, t, *, n=3, rise=20, spread=3.0, speed=0.55, phase=0.0,
          color=(232, 232, 236), peak_a=70, r0=2, sway=2.4):
    """A rising column of `n` translucent puffs reading as RISING MOTION: each
    puff eases up the full `rise` while fattening + drifting, and fades over its
    top third so it visibly dissipates at the crest. Cool/pale = steam; warm + low
    alpha = thin smoke."""
    for i in range(n):
        ph = ((t * speed) + phase + i / n) % 1.0
        climb = 1.0 - (1.0 - ph) * (1.0 - ph)
        yy = y0 - climb * rise
        xx = x + math.sin(ph * math.pi * 1.6 + i * 1.3 + t * 0.7) * sway
        if ph < 0.18:
            a = peak_a * (ph / 0.18)
        else:
            a = peak_a * (1.0 - (ph - 0.18) / 0.82) ** 1.4
        if a < 4:
            continue
        rr = int(r0 + ph * spread)
        d = rr * 2 + 2
        layer = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*color, int(a)), (rr + 1, rr + 1), rr)
        pygame.draw.circle(layer, (*color, int(a * 0.5)), (rr + 1, rr + 1), max(1, rr - 1))
        surf.blit(layer, (int(xx) - rr - 1, int(yy) - rr - 1))


def _warm_glow(surf, cx, cy, *, radius, peak, color):
    """A small capped additive halo for coals/flame — held low + capped so even
    over the lit ember it stays under 150 luma and below the coin."""
    col = _cap150(color)
    d = radius * 2 + 2
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for rr in range(radius, 0, -1):
        a = int(peak * (rr / radius) * (1.0 - rr / radius) * 4.0)
        if a <= 0:
            continue
        k = rr / radius
        c = (int(col[0] * (0.5 + 0.5 * (1 - k))),
             int(col[1] * (0.5 + 0.5 * (1 - k))),
             int(col[2] * (0.5 + 0.5 * (1 - k))))
        pygame.draw.circle(g, (*c, min(255, a)), (radius + 1, radius + 1), rr)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


def _cool(col, night):
    """Retint + a second pull for anything still over the cap. Pale materials —
    ice, glazed porcelain, a bone-white lid — survive the generic night cooling
    above 150 and start competing with the coin unless they get this."""
    c = _retint(col, night)
    return _cap150(c) if night > 0.05 else c


def _steam_col(night):
    # By day steam cools toward the sky; at night it warms instead — lit from
    # below by the stall's own lanterns, the cheapest night-market cue there is.
    if night > 0.4:
        return _mix((236, 230, 218), (214, 168, 110), min(1.0, (night - 0.4) * 1.4))
    return _mix((236, 238, 240), (150, 170, 200), 0.35 + 0.4 * night)


def _smoke_col(night):
    return _mix((200, 190, 180), (120, 120, 130), 0.4 + 0.3 * night)


# ── shared booth shell (matched to draw_kiosk) ────────────────────────────────

def _flat_awning(surf, sx, post_top, half_w, night, awning):
    aw = half_w + 1
    ay = post_top - 4
    palette = {
        "terra": (198, 86, 66), "cream": (236, 224, 204),
        "bamboo": (170, 150, 96), "indigo": (86, 104, 150),
        "jade": (108, 150, 120), "rust": (176, 96, 58),
        # round-3 family expansion — one new pair per new stall so no two
        # booths in a strip wear the same cloth
        "plum": (132, 80, 92), "wheat": (214, 196, 158),
        "ochre": (192, 148, 70), "ink": (62, 70, 86),
        "clay": (172, 124, 96), "slate": (104, 116, 126),
        "moss": (114, 124, 84), "teal": (84, 130, 134),
    }
    a_name, b_name = awning
    dimk = min(0.72, 1.3 * night)
    col_a = _mix(palette[a_name], (70, 70, 96), min(0.6, 0.9 * night))
    col_b = _mix(palette[b_name], (74, 80, 104), dimk)
    pygame.draw.rect(surf, _mix((110, 80, 50), (60, 66, 92), 0.3 * night),
                     (sx - aw - 1, ay - 2, aw * 2 + 2, 2))
    for i, ax in enumerate(range(sx - aw, sx + aw, 6)):
        col = col_a if i % 2 == 0 else col_b
        pygame.draw.polygon(surf, col, [
            (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])


def _stall_shell(surf, sx, base_y, night, *, awning=("terra", "cream"),
                 counter_h=15, post_top_off=34, roof=True, sign=None,
                 openness=1.0):
    """The shared booth shell, in three assembly states so the market can be seen
    being BUILT and struck (the weekend plan's setup/close-down choreography):
      openness < 0.25 — skeleton: two posts + the crossbar, awning still rolled
      openness < 0.50 — frame: + counter, awning still a rolled tube, no wall/sign
      openness >= 0.50 — the full stall (awning unrolled, wall, sign)"""
    half_w = HALF_W
    post_top = base_y - post_top_off
    post = _mix((92, 64, 40), (60, 66, 92), 0.30 * night)
    post_dk = _shade(post, -20)
    for px in (sx - half_w + 3, sx + half_w - 3):
        pygame.draw.rect(surf, post, (px - 1, post_top, 3, base_y - post_top))
        pygame.draw.line(surf, post_dk, (px + 1, post_top), (px + 1, base_y), 1)
    if openness >= 0.5:
        wall = _mix((150, 132, 110), (150, 124, 96), 0.5)
        wall = _mix(wall, (56, 62, 88), 0.32 * night)
        pygame.draw.rect(surf, _shade(wall, -10),
                         (sx - half_w + 4, post_top + 2, (half_w - 4) * 2, 13))
    if roof:
        if openness >= 0.5:
            _flat_awning(surf, sx, post_top, half_w, night, awning)
        else:
            # crossbar + the awning as a rolled tube waiting to be unfurled
            aw = half_w + 1
            ay = post_top - 4
            pygame.draw.rect(surf, _mix((110, 80, 50), (60, 66, 92), 0.3 * night),
                             (sx - aw - 1, ay - 2, aw * 2 + 2, 2))
            roll = _mix((198, 86, 66), (70, 70, 96), min(0.6, 0.9 * night))
            pygame.draw.rect(surf, _shade(roll, -14), (sx - aw + 2, ay, aw * 2 - 4, 3))
            pygame.draw.line(surf, _shade(roll, 14), (sx - aw + 2, ay), (sx + aw - 3, ay), 1)
    cy = base_y - counter_h
    if openness >= 0.25:
        counter = _mix((120, 84, 52), (60, 66, 92), 0.30 * night)
        counter_lt = _shade(counter, 16)
        pygame.draw.rect(surf, counter, (sx - half_w + 1, cy, (half_w - 1) * 2, counter_h))
        pygame.draw.rect(surf, counter_lt, (sx - half_w + 1, cy, (half_w - 1) * 2, 2))
        pygame.draw.rect(surf, _shade(counter, -22),
                         (sx - half_w + 1, base_y - 4, (half_w - 1) * 2, 4))
    if sign and openness >= 0.5:
        col = _cap150(_retint(sign, night))
        bx = sx - half_w + 6
        by = post_top + 1
        pygame.draw.rect(surf, col, (bx - 2, by, 5, 12))
        pygame.draw.rect(surf, _shade(col, -30), (bx - 2, by, 5, 12), 1)
        pygame.draw.line(surf, _shade(col, 24), (bx, by + 3), (bx, by + 9), 1)
    return cy


# ── the five stalls — (surf, sx, base_y, night, t) ────────────────────────────

def stall_steamer(surf, sx, base_y, night, t, openness=1.0):
    cy = _stall_shell(surf, sx, base_y, night, awning=("terra", "cream"), sign=(190, 150, 90), openness=openness)
    if openness < 0.5:
        return
    stove = _retint((86, 70, 60), night)
    pygame.draw.rect(surf, stove, (sx - 10, cy - 6, 20, 6))
    pygame.draw.rect(surf, _shade(stove, -20), (sx - 10, cy - 6, 20, 6), 1)
    pygame.draw.line(surf, _shade(stove, 18), (sx - 9, cy - 5), (sx + 9, cy - 5), 1)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 3, radius=7, peak=46, color=(150, 96, 50))
    bamboo = _retint((188, 156, 96), night)
    bamboo_d = _shade(bamboo, -34)
    bamboo_hi = _shade(bamboo, 18)
    bx = sx - 11
    bw = 22
    by = cy - 6
    for i in range(4):
        band_y = by - 5 - i * 5
        rim = pygame.Rect(bx + 1, band_y, bw - 2, 6)
        pygame.draw.ellipse(surf, bamboo, rim)
        pygame.draw.ellipse(surf, bamboo_d, rim, 1)
        pygame.draw.line(surf, bamboo_hi, (rim.left + 1, band_y + 1), (rim.right - 1, band_y + 1), 1)
        pygame.draw.line(surf, bamboo_d, (rim.left + 1, band_y + 4), (rim.right - 1, band_y + 4), 1)
        _wisp(surf, sx - 5 + i * 3, band_y, t, n=2, rise=10, spread=2.0,
              speed=0.6, phase=i * 0.3, peak_a=46, r0=1, sway=2.0, color=_steam_col(night))
    lid_y = by - 5 - 4 * 5
    pygame.draw.ellipse(surf, bamboo, (bx + 1, lid_y - 2, bw - 2, 7))
    pygame.draw.arc(surf, bamboo_hi, (bx + 3, lid_y - 5, bw - 6, 9), math.radians(20), math.radians(160), 2)
    pygame.draw.circle(surf, bamboo_d, (sx, lid_y - 2), 1)
    _wisp(surf, sx, lid_y - 2, t, n=4, rise=26, spread=3.4, speed=0.5,
          phase=0.1, peak_a=78, r0=2, sway=3.0, color=_steam_col(night))
    _wisp(surf, sx + 4, lid_y - 1, t, n=3, rise=20, spread=2.6, speed=0.55,
          phase=0.5, peak_a=58, r0=2, sway=2.6, color=_steam_col(night))


def stall_cauldron(surf, sx, base_y, night, t, openness=1.0):
    cy = _stall_shell(surf, sx, base_y, night, awning=("indigo", "cream"), sign=(168, 96, 80), openness=openness)
    if openness < 0.5:
        return
    brick = _retint((150, 96, 70), night)
    pygame.draw.rect(surf, brick, (sx - 13, cy - 8, 26, 8))
    pygame.draw.rect(surf, _shade(brick, -22), (sx - 13, cy - 8, 26, 8), 1)
    for bxx in range(sx - 11, sx + 12, 7):
        pygame.draw.line(surf, _shade(brick, -16), (bxx, cy - 8), (bxx, cy), 1)
    pygame.draw.line(surf, _shade(brick, -16), (sx - 12, cy - 4), (sx + 12, cy - 4), 1)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 2, radius=8, peak=52, color=(150, 92, 46))
    pygame.draw.ellipse(surf, _cap150((128, 70, 36) if night > 0.05 else (70, 44, 30)),
                        (sx - 5, cy - 4, 10, 3))
    pot = _retint((64, 60, 62), night)
    pot_d = _shade(pot, -22)
    pot_hi = _shade(pot, 22)
    py = cy - 8
    belly = pygame.Rect(sx - 16, py - 11, 32, 14)
    pygame.draw.ellipse(surf, pot, belly)
    pygame.draw.ellipse(surf, pot_d, belly, 1)
    pygame.draw.arc(surf, pot_hi, belly, math.radians(20), math.radians(80), 1)
    broth = _retint((150, 96, 58), night)
    rim = pygame.Rect(sx - 14, py - 12, 28, 7)
    pygame.draw.ellipse(surf, _shade(pot, -10), rim)
    pygame.draw.ellipse(surf, broth, rim.inflate(-3, -2))
    for k, ph in ((-4, 0.0), (5, 0.5), (1, 0.8)):
        fy = py - 9 + int(math.sin(t * 2.0 + ph * 6) * 0.6)
        pygame.draw.circle(surf, _retint((196, 150, 92), night), (sx + k, fy), 1)
    ladle = _retint((150, 120, 70), night)
    pygame.draw.line(surf, ladle, (sx + 9, py - 11), (sx + 16, py - 19), 1)
    pygame.draw.circle(surf, _shade(ladle, 14), (sx + 16, py - 19), 1)
    _wisp(surf, sx - 4, py - 11, t, n=4, rise=30, spread=3.6, speed=0.5,
          phase=0.0, peak_a=80, r0=2, sway=3.4, color=_steam_col(night))
    _wisp(surf, sx + 5, py - 11, t, n=3, rise=25, spread=3.0, speed=0.58,
          phase=0.5, peak_a=62, r0=2, sway=3.0, color=_steam_col(night))


def stall_grill(surf, sx, base_y, night, t, openness=1.0):
    cy = _stall_shell(surf, sx, base_y, night, awning=("rust", "cream"), sign=(176, 110, 70), openness=openness)
    if openness < 0.5:
        return
    metal = _retint((52, 50, 56), night)
    metal_d = _shade(metal, -16)
    trough = pygame.Rect(sx - 17, cy - 10, 34, 8)
    pygame.draw.rect(surf, metal, trough)
    pygame.draw.rect(surf, metal_d, trough, 1)
    pygame.draw.line(surf, _shade(metal, 14), (trough.left + 1, trough.top + 1),
                     (trough.right - 1, trough.top + 1), 1)
    for lx in (sx - 15, sx + 14):
        pygame.draw.line(surf, metal_d, (lx, cy - 2), (lx, cy + 3), 1)
    ash = _retint((34, 30, 34), night)
    pygame.draw.rect(surf, ash, (sx - 15, cy - 8, 30, 4))
    if night > 0.05:
        _warm_glow(surf, sx, cy - 6, radius=12, peak=54, color=(150, 84, 40))
    coal_hot = (148, 80, 34) if night > 0.05 else (150, 88, 38)
    coal_dk = _shade(coal_hot, -34)
    for j, kx in enumerate((-9, 0, 9)):
        pulse = 0.55 + 0.45 * math.sin(t * 3.0 + j * 1.9)
        col = _cap150(_mix(coal_dk, coal_hot, pulse))
        pygame.draw.rect(surf, col, (sx + kx - 1, cy - 7, 3, 2))
        pygame.draw.circle(surf, _cap150(_mix(coal_hot, (150, 110, 60), pulse)), (sx + kx, cy - 7), 1)
    char = _retint((40, 32, 30), night)
    meat = _retint((128, 80, 58), night)
    meat_hi = _shade(meat, 18)
    for kx, lift in ((-9, 0), (0, -1), (9, 0)):
        sxp = sx + kx
        sky = cy - 10 + lift
        pygame.draw.line(surf, char, (sxp - 7, sky + 1), (sxp + 7, sky + 1), 2)
        for mi, mx in enumerate((sxp - 4, sxp, sxp + 4)):
            mc = meat if (mi + kx) % 2 == 0 else _shade(meat, -16)
            pygame.draw.rect(surf, mc, (mx - 1, sky - 2, 3, 3))
            pygame.draw.line(surf, meat_hi, (mx - 1, sky - 2), (mx + 1, sky - 2), 1)
    smoke = _smoke_col(night)
    _wisp(surf, sx - 6, cy - 11, t, n=3, rise=28, spread=2.6, speed=0.62,
          phase=0.0, peak_a=46, r0=1, sway=3.2, color=smoke)
    _wisp(surf, sx + 5, cy - 11, t, n=3, rise=24, spread=2.4, speed=0.7,
          phase=0.4, peak_a=40, r0=1, sway=3.0, color=smoke)
    for i in range(3):
        ph = (t * 0.8 + i * 0.4) % 1.0
        ex = sx - 4 + i * 5 + int(math.sin(ph * 6 + i) * 3)
        ey = cy - 11 - int(ph * 16)
        a = int(120 * (1.0 - ph))
        if a > 8:
            # BLEND_RGB_ADD ignores alpha, so capping the SOURCE colour does
            # not cap the SUM — the ember used to add its full value onto an
            # already-lit deck and climb well past the night ceiling. Pre-scale
            # the RGB by the fade instead, so the ember dims as it rises.
            k = a / 255.0
            er, eg, eb = _cap150((150, 90, 40))
            lay = pygame.Surface((2, 2))
            lay.fill((int(er * k), int(eg * k), int(eb * k)))
            surf.blit(lay, (ex, ey), special_flags=pygame.BLEND_RGB_ADD)


def stall_wok(surf, sx, base_y, night, t, openness=1.0):
    cy = _stall_shell(surf, sx, base_y, night, awning=("jade", "cream"), sign=(150, 120, 70), openness=openness)
    if openness < 0.5:
        return
    stove = _retint((70, 64, 64), night)
    stove_d = _shade(stove, -20)
    pygame.draw.polygon(surf, stove, [(sx - 8, cy - 9), (sx + 8, cy - 9), (sx + 11, cy), (sx - 11, cy)])
    pygame.draw.polygon(surf, stove_d, [(sx - 8, cy - 9), (sx + 8, cy - 9), (sx + 11, cy), (sx - 11, cy)], 1)
    flick = math.sin(t * 11.0) * 0.5 + math.sin(t * 7.3) * 0.5
    fh = int(4 + flick * 2)
    if night > 0.05:
        _warm_glow(surf, sx, cy - 9, radius=11, peak=56, color=(150, 88, 40))
    for fx, fhh, col in ((sx - 4, fh, (148, 78, 30)), (sx + 3, fh + 1, (150, 92, 38)), (sx, fh + 2, (146, 100, 44))):
        col = _cap150(col if night > 0.05 else _shade(col, -30))
        pygame.draw.polygon(surf, col, [(fx - 2, cy - 9), (fx + 2, cy - 9), (fx, cy - 9 - fhh)])
    wok = _retint((48, 46, 52), night)
    wok_hi = _shade(wok, 24)
    belly = pygame.Rect(sx - 13, cy - 16, 26, 11)
    pygame.draw.ellipse(surf, wok, belly)
    pygame.draw.ellipse(surf, _shade(wok, -22), belly, 1)
    pygame.draw.arc(surf, wok_hi, belly, math.radians(20), math.radians(90), 1)
    rim_pts = [(sx - 12, cy - 14), (sx - 4, cy - 17), (sx + 6, cy - 18),
               (sx + 12, cy - 16), (sx + 5, cy - 14), (sx - 5, cy - 13)]
    pygame.draw.polygon(surf, _shade(wok, -8), rim_pts)
    food = _retint((176, 138, 84), night)
    pygame.draw.ellipse(surf, food, (sx - 6, cy - 16, 14, 4))
    for k, ph in ((-4, 0.0), (3, 0.4), (6, 0.7)):
        pygame.draw.circle(surf, _retint((196, 100, 80), night),
                           (sx + k, cy - 16 + int(math.sin(t * 2 + ph * 6))), 1)
    hcol = _retint((118, 90, 60), night)
    hx0, hy0 = sx - 12, cy - 14
    hx1, hy1 = sx - 26, cy - 22
    pygame.draw.line(surf, _shade(hcol, -24), (hx0, hy0 + 1), (hx1, hy1 + 1), 3)
    pygame.draw.line(surf, hcol, (hx0, hy0), (hx1, hy1), 2)
    pygame.draw.line(surf, _shade(hcol, 20), (hx0, hy0 - 1), (hx1 + 2, hy1), 1)
    pygame.draw.circle(surf, _shade(hcol, -16), (hx1, hy1), 2)
    _wisp(surf, sx, cy - 18, t, n=4, rise=28, spread=3.2, speed=0.52,
          phase=0.0, peak_a=74, r0=2, sway=3.4, color=_steam_col(night))
    _wisp(surf, sx - 4, cy - 17, t, n=3, rise=22, spread=2.4, speed=0.62,
          phase=0.5, peak_a=54, r0=1, sway=2.8, color=_steam_col(night))


def stall_tea(surf, sx, base_y, night, t, openness=1.0):
    cy = _stall_shell(surf, sx, base_y, night, awning=("bamboo", "indigo"), sign=(176, 96, 80), openness=openness)
    if openness < 0.5:
        return
    if night > 0.05:
        _warm_glow(surf, sx - 6, cy - 3, radius=6, peak=40, color=(150, 92, 46))
    warmer = _retint((92, 76, 64), night)
    pygame.draw.rect(surf, warmer, (sx - 11, cy - 4, 12, 4))
    pygame.draw.rect(surf, _shade(warmer, -20), (sx - 11, cy - 4, 12, 4), 1)
    brass = _retint((176, 142, 78), night)
    brass_d = _shade(brass, -34)
    brass_hi = _shade(brass, 26)
    ux = sx - 5
    body = pygame.Rect(ux - 6, cy - 22, 12, 18)
    pygame.draw.ellipse(surf, brass, body)
    pygame.draw.ellipse(surf, brass_d, body, 1)
    pygame.draw.line(surf, brass_hi, (ux - 2, cy - 20), (ux - 2, cy - 8), 1)
    pygame.draw.ellipse(surf, _shade(brass, -10), (ux - 6, cy - 24, 12, 5))
    pygame.draw.circle(surf, brass_hi, (ux, cy - 24), 1)
    pygame.draw.lines(surf, _shade(brass, -18), False,
                      [(ux + 5, cy - 13), (ux + 11, cy - 18), (ux + 14, cy - 24), (ux + 13, cy - 28)], 3)
    pygame.draw.lines(surf, brass, False,
                      [(ux + 5, cy - 14), (ux + 11, cy - 18), (ux + 14, cy - 24), (ux + 13, cy - 27)], 2)
    pygame.draw.circle(surf, brass_hi, (ux + 13, cy - 27), 1)
    pygame.draw.arc(surf, brass_d, (ux - 9, cy - 18, 5, 9), math.radians(60), math.radians(300), 1)
    cup = _retint((210, 200, 180), night)
    pygame.draw.ellipse(surf, cup, (sx + 8, cy - 5, 8, 4))
    pygame.draw.ellipse(surf, _shade(cup, -30), (sx + 8, cy - 5, 8, 4), 1)
    pygame.draw.line(surf, _shade(cup, 16), (sx + 10, cy - 4), (sx + 14, cy - 4), 1)
    _wisp(surf, ux + 13, cy - 28, t, n=3, rise=24, spread=2.2, speed=0.55,
          phase=0.0, peak_a=58, r0=1, sway=2.6, color=_steam_col(night))


# Stall kinds → drawer, and the day_cast vendor pose (pool index) that works it.
def stall_duck(surf, sx, base_y, night, t, *, openness=1.0):
    """S6 ROAST-DUCK / CHAR-SIU HANGING CABINET — awning plum/wheat, vendor pose
    CHOP (day_cast vendor idx 6).

    The market's first TALL ENCLOSED silhouette: a glazed vitrine standing on the
    counter, birds hanging on hooks from its top rail. Every other stall is an
    open cooking surface with its heat on show; this one puts the food behind
    glass and lights it from inside, so at night it is the only stall that reads
    as a WINDOW — an upright bright rectangle in a row of glowing puddles. The
    cleaver-and-board at the right edge is the pose hand-off: the chopping vendor
    slots in with no new cast art."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("plum", "wheat"),
                      sign=(168, 78, 70), openness=openness)
    if openness < 0.5:
        return
    # The cabinet sits left of centre so the hanging sign, the awning stripes and
    # the vendor's right-hand chopping space all stay unblocked.
    bx = sx - 13
    bw = 20
    bh = 30
    by = cy - bh
    frame = _retint((78, 60, 46), night)
    glass = _mix(_retint((96, 108, 112), night), (40, 48, 64), 0.35)
    pygame.draw.rect(surf, frame, (bx, by, bw, bh))
    pygame.draw.rect(surf, _shade(frame, -22), (bx, by, bw, bh), 1)
    pygame.draw.rect(surf, glass, (bx + 2, by + 3, bw - 4, bh - 6))
    # the interior lamp — capped, and small enough that it lights the birds
    # rather than becoming a lantern of its own
    if night > 0.05:
        _warm_glow(surf, bx + bw // 2, by + 10, radius=8, peak=36, color=(150, 104, 56))
    lamp = _cap150(_retint((196, 156, 96), night))
    pygame.draw.line(surf, lamp, (bx + 3, by + 4), (bx + bw - 4, by + 4), 1)
    rail = _retint((150, 136, 104), night)
    pygame.draw.line(surf, rail, (bx + 3, by + 7), (bx + bw - 4, by + 7), 1)
    # three lacquered birds on hooks, swaying a hair out of phase — the cabinet
    # is glass, so its only motion has to come from what hangs inside it
    duck = _cap150(_retint((156, 84, 48), night))
    duck_d = _shade(duck, -34)
    duck_hi = _shade(duck, 20)
    for i in range(3):
        dx = bx + 5 + i * 5 + int(math.sin(t * 1.1 + i * 1.7) * 1.2)
        dy = by + 9
        pygame.draw.line(surf, rail, (dx, by + 7), (dx, dy + 1), 1)
        pygame.draw.ellipse(surf, duck, (dx - 2, dy, 5, 11))
        pygame.draw.ellipse(surf, duck_d, (dx - 2, dy, 5, 11), 1)
        pygame.draw.line(surf, duck_hi, (dx - 1, dy + 2), (dx - 1, dy + 7), 1)
        pygame.draw.circle(surf, duck_d, (dx + 2, dy + 10), 1)
    # glass reflection: a single diagonal, the cheapest "this is glazed" cue
    pygame.draw.line(surf, _shade(glass, 26), (bx + 4, by + bh - 6), (bx + bw - 6, by + 6), 1)
    pygame.draw.line(surf, _shade(frame, 14), (bx + 1, by + 1), (bx + 1, by + bh - 2), 1)
    # chopping board + cleaver at the counter's right — the CHOP pose's props
    board = _retint((150, 118, 78), night)
    pygame.draw.rect(surf, board, (sx + 8, cy - 3, 13, 3))
    pygame.draw.rect(surf, _shade(board, -26), (sx + 8, cy - 3, 13, 3), 1)
    meat = _cap150(_retint((160, 96, 62), night))
    pygame.draw.rect(surf, meat, (sx + 10, cy - 5, 5, 2))
    blade = _cool((168, 176, 184), night)
    pygame.draw.rect(surf, blade, (sx + 16, cy - 8, 5, 3))
    pygame.draw.line(surf, _retint((110, 86, 60), night), (sx + 20, cy - 7), (sx + 22, cy - 9), 1)
    # a stub roof vent — the cabinet still breathes, so the stall animates even
    # though nothing in it is boiling
    vent = _retint((86, 78, 70), night)
    pygame.draw.rect(surf, vent, (bx + 4, by - 3, 5, 3))
    _wisp(surf, bx + 6, by - 3, t, n=2, rise=16, spread=1.8, speed=0.42,
          phase=0.2, peak_a=34, r0=1, sway=2.0, color=_smoke_col(night))


def stall_griddle(surf, sx, base_y, night, t, *, openness=1.0):
    """S7 FLAT GRIDDLE (jianbing / pot-sticker pan) — awning ochre/ink, vendor
    pose POUR (day_cast vendor idx 7).

    The family's FLATTEST apparatus and the only one that stays entirely under
    the awning line: a wide low iron disc read as a shallow ellipse, a domed lid
    tipped up on its edge, and a batter rake that sweeps an arc with t. Where the
    steamer and the boiler are columns, this stall is a horizon — and its steam
    matches, a broad low SHEET of short wisps instead of a plume, so it reads
    differently in motion as well as in outline. The pouring vendor's vertical
    batter stream is the only tall thing here, by design."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("ochre", "ink"),
                      sign=(190, 150, 90), openness=openness)
    if openness < 0.5:
        return
    stove = _retint((84, 72, 64), night)
    pygame.draw.rect(surf, stove, (sx - 15, cy - 7, 30, 7))
    pygame.draw.rect(surf, _shade(stove, -22), (sx - 15, cy - 7, 30, 7), 1)
    if night > 0.05:
        _warm_glow(surf, sx - 2, cy - 3, radius=7, peak=36, color=(150, 92, 44))
    mouth = _cap150(_retint((140, 78, 40), night)) if night > 0.05 else _retint((74, 48, 34), night)
    pygame.draw.rect(surf, mouth, (sx - 6, cy - 5, 9, 3))
    # the plate: one broad shallow ellipse, deliberately wider than any other
    # apparatus in the family and barely taller than the counter lip
    iron = _retint((60, 58, 62), night)
    plate = pygame.Rect(sx - 18, cy - 12, 36, 9)
    pygame.draw.ellipse(surf, iron, plate)
    pygame.draw.ellipse(surf, _shade(iron, -20), plate, 1)
    pygame.draw.arc(surf, _shade(iron, 22), plate, math.radians(10), math.radians(170), 1)
    crepe = _cool((216, 198, 148), night)
    pygame.draw.ellipse(surf, crepe, (sx - 11, cy - 11, 21, 6))
    pygame.draw.ellipse(surf, _shade(crepe, -30), (sx - 11, cy - 11, 21, 6), 1)
    # the folded half, so the plate shows a crepe mid-service rather than a disc
    fill = _cool((196, 152, 96), night)
    pygame.draw.polygon(surf, fill, [(sx + 1, cy - 11), (sx + 9, cy - 10),
                                     (sx + 6, cy - 6), (sx, cy - 7)])
    pygame.draw.line(surf, _shade(fill, -28), (sx + 1, cy - 11), (sx + 6, cy - 6), 1)
    # the rake: a wooden T that sweeps the batter round the plate with t — the
    # apparatus's own motion, so the stall lives even with no vendor attached
    ang = math.sin(t * 1.5) * 1.05
    rx = sx - 4 + int(math.cos(ang) * 8)
    ry = cy - 9 + int(math.sin(ang) * 2)
    wood = _retint((146, 116, 78), night)
    pygame.draw.line(surf, _shade(wood, -26), (rx, ry), (sx + 12, cy - 20), 2)
    pygame.draw.line(surf, wood, (rx - 2, ry), (rx + 2, ry), 2)
    # the lid tipped on its edge at the left — a half-dome, the one curve that
    # breaks the horizontal
    lid = _retint((150, 142, 128), night)
    pygame.draw.arc(surf, lid, (sx - 21, cy - 19, 11, 16), math.radians(20), math.radians(200), 2)
    pygame.draw.line(surf, _shade(lid, -30), (sx - 20, cy - 11), (sx - 12, cy - 12), 1)
    pygame.draw.circle(surf, _shade(lid, 18), (sx - 16, cy - 19), 1)
    # spatula + scraper standing in a jar at the right
    jar = _retint((120, 110, 96), night)
    pygame.draw.rect(surf, jar, (sx + 14, cy - 6, 6, 6))
    pygame.draw.rect(surf, _shade(jar, -24), (sx + 14, cy - 6, 6, 6), 1)
    tool = _cool((172, 178, 184), night)
    pygame.draw.line(surf, tool, (sx + 16, cy - 6), (sx + 15, cy - 15), 1)
    pygame.draw.line(surf, _retint((140, 112, 76), night), (sx + 18, cy - 6), (sx + 20, cy - 14), 1)
    # a LOW WIDE steam sheet: four short offset wisps across the plate, so the
    # vapour hugs the iron instead of forming a column
    sc = _steam_col(night)
    for i, ox in enumerate((-12, -5, 3, 10)):
        _wisp(surf, sx + ox, cy - 12, t, n=2, rise=11 + (i % 2) * 3, spread=2.6,
              speed=0.66, phase=i * 0.27, peak_a=38, r0=1, sway=3.0, color=sc)


def stall_claypot(surf, sx, base_y, night, t, *, openness=1.0):
    """S8 CLAY-POT BANK — awning clay/slate, vendor pose WEIGH (day_cast vendor
    idx 1).

    REPETITION is the silhouette. Five small lidded pots dropped into a
    multi-hole stove make a crenellated row of domes — a rhythm no other stall
    in the market has, since every other apparatus is one big object. The steam
    matches: five little offset wisps that read as a keyboard rather than a
    plume, and one lid at a time chatters up off its rim on a slow cycle, which
    is the whole stall's animation and the reason it never reads static."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("clay", "slate"),
                      sign=(150, 120, 70), openness=openness)
    if openness < 0.5:
        return
    stove = _retint((132, 106, 86), night)
    pygame.draw.rect(surf, stove, (sx - 19, cy - 9, 38, 9))
    pygame.draw.rect(surf, _shade(stove, -24), (sx - 19, cy - 9, 38, 9), 1)
    pygame.draw.line(surf, _shade(stove, -16), (sx - 18, cy - 4), (sx + 18, cy - 4), 1)
    xs = (-14, -7, 0, 7, 14)
    # three low burner halos rather than one stove-wide wash: the stall's read is
    # separate fires along the bank, and holding each halo faint keeps their
    # additive overlap under the night cap where one broad wash ran hot.
    if night > 0.05:
        for ox in (-11, 0, 11):
            _warm_glow(surf, sx + ox, cy - 5, radius=5, peak=10, color=(150, 88, 42))
    hot = _cap150((146, 82, 38)) if night > 0.05 else _retint((78, 50, 36), night)
    pot = _retint((122, 88, 70), night)
    pot_d = _shade(pot, -28)
    lid = _retint((146, 116, 92), night)
    chatter = int(t * 1.4) % 5
    for i, ox in enumerate(xs):
        px = sx + ox
        # the fire showing through each burner ring, so the stove reads as five
        # separate flames rather than one hot block
        pygame.draw.rect(surf, hot, (px - 2, cy - 9, 5, 2))
        pygame.draw.ellipse(surf, pot_d, (px - 4, cy - 11, 9, 4))
        body = pygame.Rect(px - 4, cy - 14, 9, 6)
        pygame.draw.ellipse(surf, pot, body)
        pygame.draw.ellipse(surf, pot_d, body, 1)
        lift = 1 if i == chatter else 0
        ly = cy - 17 - lift
        pygame.draw.arc(surf, lid, (px - 4, ly, 9, 8), math.radians(10), math.radians(170), 2)
        pygame.draw.line(surf, _shade(lid, -30), (px - 4, ly + 4), (px + 4, ly + 4), 1)
        pygame.draw.circle(surf, _shade(lid, 20), (px, ly + 1), 1)
        _wisp(surf, px, ly + 1, t, n=2, rise=13 + lift * 5, spread=1.8,
              speed=0.5 + i * 0.04, phase=i * 0.21,
              peak_a=42 if lift else 30, r0=1, sway=1.8, color=_steam_col(night))
    # a rice paddle + a small bowl stack, so the counter reads as a portioning
    # bench (which is what the WEIGH pose is doing above it)
    bowl = _cool((208, 198, 178), night)
    for k in range(2):
        pygame.draw.ellipse(surf, bowl, (sx + 12, cy - 4 - k * 3, 8, 4))
        pygame.draw.ellipse(surf, _shade(bowl, -34), (sx + 12, cy - 4 - k * 3, 8, 4), 1)


def stall_roaster(surf, sx, base_y, night, t, *, openness=1.0):
    """S9 DRUM ROASTER (chestnuts / sweet potato) — awning moss/ochre, vendor
    pose STACK (day_cast vendor idx 4, the one carrying a basket).

    The only HORIZONTAL CYLINDER in the market and the only genuinely ROTATING
    machine: a hooped barrel slung in a cradle over a firebox, its crank turning
    on t and its hoop bands travelling around the shell so the drum reads as
    revolving rather than as a log. Against four squat stoves and two columns, a
    lying-down barrel with a wheel on its end is an instantly separate outline,
    and the stub chimney gives it sooty smoke — the only smoke besides the
    skewer grill's, and pitched lower and lazier."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("moss", "ochre"),
                      sign=(176, 110, 70), openness=openness)
    if openness < 0.5:
        return
    fire = _retint((92, 76, 66), night)
    pygame.draw.rect(surf, fire, (sx - 15, cy - 8, 27, 8))
    pygame.draw.rect(surf, _shade(fire, -22), (sx - 15, cy - 8, 27, 8), 1)
    if night > 0.05:
        _warm_glow(surf, sx - 3, cy - 4, radius=8, peak=34, color=(150, 90, 44))
    flick = 0.5 + 0.5 * math.sin(t * 5.2)
    mouth = _cap150(_mix((92, 54, 32), (148, 86, 40), flick)) if night > 0.05 \
        else _retint((80, 52, 36), night)
    pygame.draw.rect(surf, mouth, (sx - 10, cy - 6, 10, 4))
    # the cradle the drum turns in
    cradle = _retint((70, 64, 62), night)
    for ox in (-13, 9):
        pygame.draw.line(surf, cradle, (sx + ox, cy - 8), (sx + ox, cy - 15), 2)
    # the barrel: a body block closed by an end-cap ellipse, so it reads as a
    # cylinder seen three-quarters rather than a flat box
    drum = _retint((96, 84, 78), night)
    drum_d = _shade(drum, -26)
    drum_hi = _shade(drum, 20)
    dy = cy - 26
    pygame.draw.rect(surf, drum, (sx - 15, dy, 25, 15))
    pygame.draw.ellipse(surf, _shade(drum, -8), (sx + 5, dy, 11, 15))
    pygame.draw.ellipse(surf, drum_d, (sx + 5, dy, 11, 15), 1)
    pygame.draw.line(surf, drum_hi, (sx - 14, dy + 2), (sx + 8, dy + 2), 1)
    pygame.draw.line(surf, drum_d, (sx - 15, dy + 14), (sx + 9, dy + 14), 1)
    # hoop bands that TRAVEL with t — the rotation cue that costs three lines
    off = (t * 7.0) % 8
    for k in range(4):
        hx = int(sx - 14 + (off + k * 8) % 25)
        pygame.draw.line(surf, drum_d, (hx, dy + 1), (hx, dy + 14), 1)
    pygame.draw.ellipse(surf, _shade(drum, 6), (sx + 8, dy + 4, 5, 7))
    # the crank: an axle, an arm on a radius, a knob — one real revolution/sec
    ax, ay = sx + 16, dy + 7
    a = t * 2.4
    hx2 = int(ax + math.cos(a) * 5)
    hy2 = int(ay + math.sin(a) * 5)
    steel = _cool((150, 156, 162), night)
    pygame.draw.circle(surf, _shade(steel, -40), (ax, ay), 2)
    pygame.draw.line(surf, steel, (ax, ay), (hx2, hy2), 2)
    pygame.draw.circle(surf, _retint((120, 92, 60), night), (hx2, hy2), 2)
    # stub chimney at the drum's shoulder + its slow sooty ribbon
    ch = _retint((74, 70, 68), night)
    pygame.draw.rect(surf, ch, (sx - 12, dy - 6, 5, 6))
    pygame.draw.rect(surf, _shade(ch, -24), (sx - 12, dy - 6, 5, 6), 1)
    _wisp(surf, sx - 10, dy - 6, t, n=3, rise=22, spread=2.8, speed=0.44,
          phase=0.1, peak_a=36, r0=1, sway=3.2, color=_smoke_col(night))
    # a tray of roasted chestnuts on the counter front — the STACK vendor's goods
    tray = _retint((126, 98, 66), night)
    pygame.draw.ellipse(surf, tray, (sx - 21, cy - 5, 14, 5))
    pygame.draw.ellipse(surf, _shade(tray, -28), (sx - 21, cy - 5, 14, 5), 1)
    nut = _cap150(_retint((118, 74, 44), night))
    for k, (nx, ny) in enumerate(((-18, -5), (-15, -6), (-12, -5), (-16, -4))):
        pygame.draw.circle(surf, nut if k % 2 else _shade(nut, -18), (sx + nx, cy + ny), 1)


def stall_ice(surf, sx, base_y, night, t, *, openness=1.0):
    """S10 SHAVED ICE / cold sweets — awning teal/wheat, vendor pose SIGN
    (day_cast vendor idx 5, the one holding a price board).

    The market's COLD stall, and its whole reason to exist is contrast: no
    steam, no flame, no warm glow anywhere in the drawer. In a row where every
    silhouette is topped by rising vapour, the one stall with nothing above it
    is the beat that makes the others read as hot. Its motion is inverted too —
    a hand crank turning over a clamped ice block and flecks of snow falling DOWN
    into the bowl, the only downward motion in the family. The syrup bottles are
    the one place the row gets a clean saturated accent, and they are the whole
    stall's colour story, which is why the flavour-board vendor is the match."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("teal", "wheat"),
                      sign=(96, 142, 150), openness=openness)
    if openness < 0.5:
        return
    mx = sx - 7
    iron = _retint((78, 104, 100), night)
    iron_d = _shade(iron, -28)
    iron_hi = _shade(iron, 18)
    # cast-iron pedestal: foot plate, column, blade housing — heavy and squat so
    # the crank above it reads as the working part
    pygame.draw.rect(surf, iron, (mx - 9, cy - 4, 18, 4))
    pygame.draw.rect(surf, iron_d, (mx - 9, cy - 4, 18, 4), 1)
    pygame.draw.rect(surf, iron, (mx - 4, cy - 15, 9, 11))
    pygame.draw.rect(surf, iron_d, (mx - 4, cy - 15, 9, 11), 1)
    pygame.draw.line(surf, iron_hi, (mx - 3, cy - 14), (mx - 3, cy - 5), 1)
    pygame.draw.rect(surf, _shade(iron, -10), (mx - 8, cy - 21, 17, 6))
    pygame.draw.rect(surf, iron_d, (mx - 8, cy - 21, 17, 6), 1)
    # the ice block clamped under the head — pale, but cooled + capped so the one
    # near-white object in the market never competes with the coin at night
    ice = _cool((190, 208, 216), night)
    pygame.draw.polygon(surf, ice, [(mx - 6, cy - 21), (mx + 5, cy - 21),
                                    (mx + 7, cy - 27), (mx - 4, cy - 27)])
    pygame.draw.polygon(surf, _shade(ice, -40), [(mx - 6, cy - 21), (mx + 5, cy - 21),
                                                 (mx + 7, cy - 27), (mx - 4, cy - 27)], 1)
    pygame.draw.line(surf, _shade(ice, 16), (mx - 3, cy - 26), (mx + 5, cy - 26), 1)
    # the crank: a shaft over the block with an arm that really goes round
    a = t * 2.0
    cxp, cyp = mx + 8, cy - 26
    hx = int(cxp + math.cos(a) * 5)
    hy = int(cyp + math.sin(a) * 4)
    steel = _cool((150, 158, 164), night)
    pygame.draw.line(surf, steel, (mx - 1, cy - 27), (cxp, cyp), 2)
    pygame.draw.line(surf, steel, (cxp, cyp), (hx, hy), 2)
    pygame.draw.circle(surf, _retint((122, 94, 62), night), (hx, hy), 2)
    # the bowl of shaved snow under the blade + the flecks falling into it
    bowl = _cool((186, 196, 202), night)
    pygame.draw.ellipse(surf, bowl, (mx - 7, cy - 8, 14, 5))
    pygame.draw.ellipse(surf, _shade(bowl, -38), (mx - 7, cy - 8, 14, 5), 1)
    snow = _cool((202, 214, 220), night)
    pygame.draw.ellipse(surf, snow, (mx - 5, cy - 11, 11, 5))
    syrup_top = _cap150(_retint((186, 76, 84), night))
    pygame.draw.arc(surf, syrup_top, (mx - 4, cy - 12, 8, 5), math.radians(10), math.radians(160), 2)
    for i in range(3):
        ph = ((t * 0.9) + i / 3.0) % 1.0
        fy = cy - 20 + ph * 9
        fx = mx - 3 + i * 3 + math.sin(ph * 5 + i) * 1.2
        aa = int(150 * (1.0 - ph * 0.7))
        lay = pygame.Surface((2, 2), pygame.SRCALPHA)
        lay.fill((*_cool((198, 210, 216), night), aa))
        surf.blit(lay, (int(fx), int(fy)))
    # three syrup bottles — the row's only clean colour accent, capped at night
    for i, col in enumerate(((178, 66, 74), (196, 148, 60), (86, 140, 104))):
        bx = sx + 9 + i * 5
        body = _cap150(_retint(col, night))
        pygame.draw.rect(surf, body, (bx, cy - 11, 4, 8))
        pygame.draw.rect(surf, _shade(body, -34), (bx, cy - 11, 4, 8), 1)
        pygame.draw.line(surf, _shade(body, 26), (bx + 1, cy - 10), (bx + 1, cy - 5), 1)
        pygame.draw.rect(surf, _cool((190, 190, 184), night), (bx + 1, cy - 14, 2, 3))


def stall_boiler(surf, sx, base_y, night, t, *, openness=1.0):
    """S11 NOODLE BOILER — awning ink/wheat, vendor pose WOK (day_cast vendor
    idx 8, the wide-vessel-held-out arm).

    A tall STRAIGHT-SIDED stock column — pointedly not the cauldron's wide
    ellipse belly — under a GANTRY RAIL of long-handled strainer baskets that
    dip into the boil on their own cycle. The gantry is the point: an ordered
    row of hanging teardrops on a bar is a silhouette the market does not
    otherwise own, and it sits above the pot where every other stall has open
    sky. It also keeps this stall firmly in the BOILING-AND-SERVING register:
    bowls stacked, chopsticks in a jar, no dough, no arms-wide showman — the
    festival's hand-pulled-noodle theatre stays the performance, this stays the
    kitchen."""
    cy = _stall_shell(surf, sx, base_y, night, awning=("ink", "wheat"),
                      sign=(198, 188, 166), openness=openness)
    if openness < 0.5:
        return
    px = sx - 5
    stove = _retint((80, 72, 68), night)
    pygame.draw.rect(surf, stove, (px - 11, cy - 6, 22, 6))
    pygame.draw.rect(surf, _shade(stove, -22), (px - 11, cy - 6, 22, 6), 1)
    if night > 0.05:
        _warm_glow(surf, px, cy - 3, radius=7, peak=36, color=(150, 92, 46))
    ring = _cap150((142, 80, 38)) if night > 0.05 else _retint((76, 50, 34), night)
    pygame.draw.rect(surf, ring, (px - 6, cy - 5, 12, 2))
    # the column: straight sides, a hoop band, a heavy rim — a cylinder, where
    # the shipped cauldron is a sphere
    steel = _retint((92, 96, 104), night)
    steel_d = _shade(steel, -30)
    ty = cy - 26
    pygame.draw.rect(surf, steel, (px - 9, ty, 19, 20))
    pygame.draw.rect(surf, steel_d, (px - 9, ty, 19, 20), 1)
    pygame.draw.line(surf, _shade(steel, 22), (px - 7, ty + 3), (px - 7, cy - 8), 1)
    pygame.draw.line(surf, steel_d, (px - 9, ty + 11), (px + 9, ty + 11), 1)
    pygame.draw.ellipse(surf, _shade(steel, -12), (px - 10, ty - 3, 21, 7))
    broth = _retint((166, 142, 96), night)
    pygame.draw.ellipse(surf, broth, (px - 8, ty - 2, 17, 5))
    for k, ph in ((-4, 0.0), (2, 0.45), (6, 0.8)):
        by = ty + int(math.sin(t * 3.2 + ph * 6) * 0.8)
        pygame.draw.circle(surf, _cool((208, 190, 148), night), (px + k, by), 1)
    # the gantry: two uprights, a rail, three baskets on long handles, each
    # dipping on its own phase so one is always down in the water
    post = _retint((104, 82, 58), night)
    rail_y = cy - 32
    for ox in (-15, 15):
        pygame.draw.line(surf, post, (sx + ox, cy - 2), (sx + ox, rail_y), 1)
    pygame.draw.line(surf, _shade(post, 14), (sx - 15, rail_y), (sx + 15, rail_y), 2)
    wire = _cool((146, 150, 156), night)
    wire_d = _shade(wire, -40)
    for i, ox in enumerate((-9, 0, 9)):
        dip = int((math.sin(t * 1.6 + i * 2.1) * 0.5 + 0.5) * 7)
        hx = sx + ox
        top = rail_y + 1
        bot = rail_y + 12 + dip
        pygame.draw.line(surf, wire_d, (hx, top), (hx, bot), 1)
        pygame.draw.arc(surf, wire, (hx - 4, bot - 3, 9, 8), math.radians(190), math.radians(350), 2)
        pygame.draw.line(surf, wire_d, (hx - 4, bot + 1), (hx + 4, bot + 1), 1)
        if dip > 4:
            pygame.draw.line(surf, _cool((208, 196, 158), night), (hx - 2, bot + 2), (hx + 2, bot + 2), 1)
    # bowls + a chopstick jar at the right: this is a SERVING counter
    bowl = _cool((206, 198, 180), night)
    for k in range(3):
        pygame.draw.ellipse(surf, bowl, (sx + 8, cy - 5 - k * 3, 9, 4))
        pygame.draw.ellipse(surf, _shade(bowl, -36), (sx + 8, cy - 5 - k * 3, 9, 4), 1)
    jar = _retint((118, 100, 78), night)
    pygame.draw.rect(surf, jar, (sx + 17, cy - 8, 5, 8))
    pygame.draw.rect(surf, _shade(jar, -26), (sx + 17, cy - 8, 5, 8), 1)
    stick = _retint((176, 154, 112), night)
    for k, dxs in enumerate((-1, 0, 2)):
        pygame.draw.line(surf, stick, (sx + 19, cy - 8), (sx + 19 + dxs, cy - 14), 1)
    _wisp(surf, px - 3, ty - 3, t, n=4, rise=27, spread=3.4, speed=0.5,
          phase=0.0, peak_a=66, r0=2, sway=3.2, color=_steam_col(night))
    _wisp(surf, px + 5, ty - 2, t, n=3, rise=21, spread=2.6, speed=0.6,
          phase=0.45, peak_a=48, r0=2, sway=2.8, color=_steam_col(night))


# ════════════════════════════════════════════════════════════════════════════
# THE SHIPPED FIVE — imported live from the game so the sheet compares the new
# six against exactly what is on screen today, not against a stale copy.
# ════════════════════════════════════════════════════════════════════════════

from game import food_stalls as _fs  # noqa: E402


STALLS = {
    "steamer":  (stall_steamer, 0),    # V1 calling
    "cauldron": (stall_cauldron, 3),   # V4 ladling
    "grill":    (stall_grill, 2),      # V3 fanning
    "wok":      (stall_wok, 2),        # V3 fanning
    "tea":      (stall_tea, 0),        # V1 calling
    # Round-3 expansion. Each takes a vendor pose the original five never
    # used, so a market row varies its WORKERS as well as its apparatus.
    "duck":     (stall_duck, 6),       # V7 chopping
    "griddle":  (stall_griddle, 7),    # V8 pouring
    "claypot":  (stall_claypot, 1),    # V2 weighing
    "roaster":  (stall_roaster, 4),    # V5 stacking
    "ice":      (stall_ice, 5),        # V6 signing
    "boiler":   (stall_boiler, 8),     # V9 wok-tossing
}
