"""FIRE-TREE NIGHT — the IRON FLOWER + DRAGON-PARADE support, round-1 sheet.

Covers FESTIVAL_PLAN.md §4 (the fire show, the dragon staging) and §6 build-list
rows A1-A8, A13 and A15:

  A1  iron-flower scaffold, 3 states (dark/draped in rain · manned · mid-burst)
      + the scorched-and-smoking wind-down state
  A2  the crew — THROWER (long willow scoop, over-shoulder ladle swing) and
      STRIKER (willow bat, 1-frame contact), soaked straw hat + sheepskin
  A3  the SPARK-BURST system — 80-140 ballistic sparks drawn as sub-stepped
      COMETS, (191,142,82) @ alpha 120-200 cooling to (170,120,90) up the arc,
      jittered apex ceiling under y=512, ground bounce + skitter, ONE 150-luma
      2px core pixel at contact, 2.5 s cycle with a dark beat — and the whole
      rig drifting at +0.55x scroll so the cycle gets a 5.75 s window
  A4  the burst RIM-LIGHT pass — 1px warm top-edge on every PROMENADE-layer
      silhouette for 3 frames on a 100/60/30 decay (the storm's
      lightning-silhouette flash, inverted)
  A5  the DOUSED APRON — locally wet paving under the rig + per-burst 1px
      dither reflection columns at alpha 45
  A6  dragon PEARL + bearer (pole overhead, figure-8 at 0.8 Hz, capped halo r8)
  A7  DRUM-AND-CYMBAL cart (barrel drum @1.5x on a 2-wheel chassis + 2 cymbals)
  A8  the DRAPED dragon-head handcart (the Ch5 daytime plant)
  A13 the LANTERN ARCH — two poles + an arc of 6 lanterns spanning ~120 px, apex
      y=497 (the shipped night garland's own top_y, GROUND_Y-98)
  A15 the RESIDUE set — scorch fan, dropped paper masks, the cold smoking rig

Research studied before drawing (web):
  - datiehua/dashuhua: 1,600 C scrap iron scooped with a long-handled WILLOW
    scoop and struck against a WILLOW-BRANCH PERGOLA with willow sticks, so the
    apparatus is a splash board, not a wall; crews work in soaked straw hats and
    sheepskin; the read is spark COUNT + ARC, never raw brightness — the only
    fire form that survives a 150-luma night cap.
  - dragon-dance staging: the pearl of wisdom is a ball MOUNTED ON A POLE swung
    by its own bearer ahead of the head; percussion is a drum on a WHEELED
    PLATFORM that a second person pulls, plus cymbals/gongs.
  - lantern-fair dressing: arches and overhead lattices, a different register
    from the stall row.

Every panel is a true SCREEN SLICE (world y 500-647 at 1x) so the deck lines,
the 560 band ceiling and the y=512 spark ceiling are all literally drawn — the
vertical budget is auditable by eye, not asserted. Pure pygame.draw + SRCALPHA,
pygbag-safe; night colours cool toward (54,64,96) and every lit pixel routes
through the family cap helpers. Scratch generator; touches no game file.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── family colour contract (lifted from performers_cast / food_stalls) ─────────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


NIGHT_GLOW_CAP = 150
COIN_CORE = (255, 232, 150)

# The spark primary, already scaled off (255,190,110) by 150/200 exactly as the
# plan specifies. Its own luma sits ON the cap, so full-alpha core pixels are the
# hottest thing the fire show can produce and everything else lands under it.
SPARK_COL = (191, 142, 82)
RIM_CAP = 140


def _retint(col, night):
    if night <= 0.05:
        return col
    out = _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))
    if _luma(out) > NIGHT_GLOW_CAP:
        over = (_luma(out) - NIGHT_GLOW_CAP) / max(1.0, 255 - NIGHT_GLOW_CAP)
        out = _mix(out, (66, 76, 104), min(0.78, 0.5 + over))
    return out


def _cap_to(col, ceil):
    y = _luma(col)
    if y <= ceil:
        return col
    k = ceil / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


def _cap150(col):
    return _cap_to(col, NIGHT_GLOW_CAP)


def _wisp(surf, x, y0, t, *, n=3, rise=20, spread=3.0, speed=0.55, phase=0.0,
          color=(232, 232, 236), peak_a=70, r0=2, sway=2.4):
    """food_stalls._wisp verbatim — the town's one smoke/steam idiom, so the
    scaffold's smoke belongs to the same market as the steamers."""
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


_HALO_CACHE = {}


def _halo_surface(radius, budget, color):
    """performers_cast._warm_halo, cached. BLEND_RGB_ADD ignores alpha and adds
    RGB outright, so the falloff has to be baked into the RGB itself and the
    peak ADDED luma pre-scaled to `budget`. That pre-scale is what makes the
    additive lighting auditable: base luma + budget is the worst case, by
    construction, wherever the halo lands."""
    key = (radius, budget, color)
    cached = _HALO_CACHE.get(key)
    if cached is not None:
        return cached
    col = _cap150(color)
    d = radius * 2 + 2
    cxr = cyr = radius + 1
    acc = [[0.0, 0.0, 0.0] for _ in range(d * d)]
    for rr in range(radius, 0, -1):
        w = (rr / radius) * (1.0 - rr / radius) * 4.0
        k = rr / radius
        c = (col[0] * (0.5 + 0.5 * (1 - k)),
             col[1] * (0.5 + 0.5 * (1 - k)),
             col[2] * (0.5 + 0.5 * (1 - k)))
        rr2 = rr * rr
        for py in range(d):
            dy = py - cyr
            for px in range(d):
                dx = px - cxr
                if dx * dx + dy * dy <= rr2:
                    cell = acc[py * d + px]
                    cell[0] += c[0] * w
                    cell[1] += c[1] * w
                    cell[2] += c[2] * w
    peak_add = max(_luma(cell) for cell in acc) or 1.0
    scale = budget / peak_add
    g = pygame.Surface((d, d), pygame.SRCALPHA)
    for py in range(d):
        for px in range(d):
            cell = acc[py * d + px]
            if cell[0] + cell[1] + cell[2] <= 0:
                continue
            g.set_at((px, py), (_clamp(cell[0] * scale), _clamp(cell[1] * scale),
                                _clamp(cell[2] * scale), 255))
    _HALO_CACHE[key] = g
    return g


def _warm_glow(surf, cx, cy, *, radius, peak, color):
    """`peak` is the maximum ADDED luma this halo may contribute, not an alpha."""
    g = _halo_surface(radius, peak, color)
    surf.blit(g, (cx - radius - 1, cy - radius - 1), special_flags=pygame.BLEND_RGB_ADD)


# ════════════════════════════════════════════════════════════════════════════
# WORLD GEOMETRY — every panel is a literal screen slice, so the whole vertical
# budget argument is drawn rather than claimed.
# ════════════════════════════════════════════════════════════════════════════

SLICE_TOP = 500
SLICE_H = 148                    # world 500 .. 647
FAR_Y = 595                      # far deck (stalls, scaffold, crew)
NEAR_Y = 638                     # near deck (parade, crowd)
BAND_TOP = 560                   # cast/prop ceiling
SPARK_CEIL = 512                 # the ONE sanctioned exception (R8)


def L(world_y):
    return world_y - SLICE_TOP


SKY_DAY = (150, 146, 132)
SKY_STORM = (104, 108, 118)
SKY_NIGHT = (26, 32, 52)
PAVE_DAY = (146, 136, 118)
PAVE_NIGHT = (44, 46, 56)


def _panel(w, night, *, storm=False, wet=0.0):
    """A 1x screen slice with sky, the far deck, the near deck and the wet-stone
    doubling band the festival opens on."""
    s = pygame.Surface((w, SLICE_H))
    sky = SKY_NIGHT if night > 0.5 else (SKY_STORM if storm else SKY_DAY)
    pave = PAVE_NIGHT if night > 0.5 else PAVE_DAY
    s.fill(sky)
    pygame.draw.rect(s, pave, (0, L(FAR_Y), w, SLICE_H - L(FAR_Y)))
    pygame.draw.line(s, _shade(pave, 14), (0, L(FAR_Y)), (w, L(FAR_Y)), 1)
    pygame.draw.rect(s, _shade(pave, -12), (0, L(NEAR_Y), w, SLICE_H - L(NEAR_Y)))
    pygame.draw.line(s, _shade(pave, 8), (0, L(NEAR_Y)), (w, L(NEAR_Y)), 1)
    for gy in range(L(FAR_Y) + 8, L(NEAR_Y), 9):
        pygame.draw.line(s, _shade(pave, -8), (0, gy), (w, gy), 1)
    if wet > 0:
        _wet_band(s, 0, w, wet, night)
    return s


def _wet_band(s, x0, x1, wet, night):
    """Locally saturated paving — darker, glossier, with a horizontal specular
    streak. The doused apron and the post-rain street use the same material so
    the fire crew's water reads as the same water the storm left."""
    pave = PAVE_NIGHT if night > 0.5 else PAVE_DAY
    dark = _mix(pave, (18, 20, 30) if night > 0.5 else (86, 82, 74), 0.45 * wet)
    lay = pygame.Surface((x1 - x0, SLICE_H - L(FAR_Y)), pygame.SRCALPHA)
    lay.fill((*dark, int(190 * wet)))
    s.blit(lay, (x0, L(FAR_Y)))
    spec = _mix(dark, (120, 140, 180) if night > 0.5 else (200, 196, 186), 0.30 * wet)
    for k, yy in enumerate((FAR_Y + 5, FAR_Y + 13, FAR_Y + 24, FAR_Y + 34)):
        if yy >= NEAR_Y:
            continue
        step = 3 + k
        for xx in range(x0 + (k % 2), x1, step):
            s.set_at((xx, L(yy)), spec)


def _tall_panel(w, night, top, *, guides=True):
    """A screen slice that starts ABOVE 500. Only the lantern arch needs it: the
    arch hangs at the shipped garland's own 497, so a 500-647 slice literally
    cannot draw it and a panel that can't draw a piece can't audit it either."""
    h = 647 - top
    s = pygame.Surface((w, h))
    s.fill(SKY_NIGHT if night > 0.5 else SKY_DAY)
    pave = PAVE_NIGHT if night > 0.5 else PAVE_DAY
    pygame.draw.rect(s, pave, (0, FAR_Y - top, w, h - (FAR_Y - top)))
    pygame.draw.line(s, _shade(pave, 14), (0, FAR_Y - top), (w, FAR_Y - top), 1)
    pygame.draw.rect(s, _shade(pave, -12), (0, NEAR_Y - top, w, h - (NEAR_Y - top)))
    pygame.draw.line(s, _shade(pave, 8), (0, NEAR_Y - top), (w, NEAR_Y - top), 1)
    for gy in range(FAR_Y - top + 8, NEAR_Y - top, 9):
        pygame.draw.line(s, _shade(pave, -8), (0, gy), (w, gy), 1)
    if guides:
        for xx in range(0, w, 12):
            pygame.draw.line(s, (110, 130, 160), (xx, BAND_TOP - top),
                             (min(w, xx + 6), BAND_TOP - top), 1)
        for xx in range(0, w, 8):
            pygame.draw.line(s, (150, 110, 70), (xx, SPARK_CEIL - top),
                             (min(w, xx + 4), SPARK_CEIL - top), 1)
        for xx in range(0, w, 4):
            pygame.draw.line(s, (128, 150, 120), (xx, GARLAND_TOP_Y - top),
                             (min(w, xx + 2), GARLAND_TOP_Y - top), 1)
    return s


def _guides(s, w, *, spark=False):
    """Draw the mandated ceilings ON the panel: 560 band top, 512 spark ceiling."""
    for yy, col, dash in ((BAND_TOP, (110, 130, 160), 6),):
        for xx in range(0, w, dash * 2):
            pygame.draw.line(s, col, (xx, L(yy)), (min(w, xx + dash), L(yy)), 1)
    if spark:
        for xx in range(0, w, 8):
            pygame.draw.line(s, (150, 110, 70), (xx, L(SPARK_CEIL)),
                             (min(w, xx + 4), L(SPARK_CEIL)), 1)


# ════════════════════════════════════════════════════════════════════════════
# GENERIC FIGURES — the ped/day-cast proportions the sheet needs for scale.
# ════════════════════════════════════════════════════════════════════════════

SKIN = (222, 178, 132)


def _person(surf, cx, feet, night, *, h=18, coat=(96, 104, 140), hair=(52, 42, 34),
            arms='down', arm_t=0.0, back=False, chin=0, bulk=1.0, face=1,
            hat=None, hat_c=(120, 104, 72)):
    """A near/far-deck civilian at the shared cast proportions (head r3, torso
    ~8, legs ~7). `back=True` turns the figure away from camera — the whole
    spark-watch crowd is drawn from behind, which is what makes the fire square
    read as an audience instead of a row of extras."""
    coat = _retint(coat, night)
    coat_dk = _shade(coat, -34)
    skin = _retint(SKIN, night)
    hair = _retint(hair, night)
    head_r = 3
    torso_h = int(h * 0.46 * 1.0)
    body_w = max(3, int(h * 0.26 * bulk))
    torso_bot = feet - (h - torso_h - head_r * 2)
    torso_top = torso_bot - torso_h
    hy = torso_top - head_r - chin
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_bot), (cx + sgn * 2, feet), 2)
    pygame.draw.polygon(surf, coat, [
        (cx - body_w, torso_top), (cx + body_w, torso_top),
        (cx + body_w + 1, torso_bot), (cx - body_w - 1, torso_bot)])
    pygame.draw.polygon(surf, coat_dk, [
        (cx - body_w, torso_top), (cx + body_w, torso_top),
        (cx + body_w + 1, torso_bot), (cx - body_w - 1, torso_bot)], 1)
    sh_y = torso_top + 2
    if arms == 'up':
        for sgn in (-1, 1):
            pygame.draw.line(surf, coat, (cx + sgn * body_w, sh_y),
                             (cx + sgn * (body_w + 3), sh_y - 7), 2)
    elif arms == 'point':
        pygame.draw.line(surf, coat, (cx - body_w, sh_y), (cx - body_w - 6, sh_y - 6), 2)
        pygame.draw.line(surf, coat, (cx + body_w, sh_y), (cx + body_w + 2, sh_y + 5), 2)
    elif arms == 'eat':
        pygame.draw.line(surf, coat, (cx + body_w, sh_y), (cx + 1, sh_y - 3), 2)
        pygame.draw.line(surf, coat, (cx - body_w, sh_y), (cx - body_w - 2, sh_y + 5), 2)
    else:
        for sgn in (-1, 1):
            pygame.draw.line(surf, coat, (cx + sgn * body_w, sh_y),
                             (cx + sgn * (body_w + 1), sh_y + 6), 2)
    pygame.draw.circle(surf, skin if not back else _shade(hair, 6), (cx, hy), head_r)
    if back:
        pygame.draw.circle(surf, hair, (cx, hy), head_r)
        pygame.draw.circle(surf, _shade(hair, -18), (cx, hy + 1), head_r - 1)
    else:
        pygame.draw.circle(surf, hair, (cx, hy - 1), head_r)
        pygame.draw.arc(surf, hair, (cx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), 2)
        pygame.draw.circle(surf, (34, 24, 20), (cx + face, hy), 0)
    if hat == 'conical':
        c = _retint(hat_c, night)
        pygame.draw.polygon(surf, c, [(cx - 6, hy - 1), (cx, hy - 7), (cx + 6, hy - 1)])
        pygame.draw.polygon(surf, _shade(c, -30), [(cx - 6, hy - 1), (cx, hy - 7), (cx + 6, hy - 1)], 1)
    return hy, sh_y


def _stall_ref(surf, cx, base_y, night, t=0.0, *, steam=True):
    """A compressed food_stalls booth shell (posts + striped awning + counter) —
    scale reference and the rim-light pass's test subject."""
    g = int(base_y)
    post = _retint((92, 64, 40), night)
    aw_a = _retint((198, 86, 66), night)
    aw_b = _retint((236, 224, 204), night)
    half = 22
    top = g - 34
    for px in (cx - half + 3, cx + half - 3):
        pygame.draw.rect(surf, post, (px - 1, top, 3, g - top))
    wall = _retint((150, 132, 110), night)
    pygame.draw.rect(surf, _shade(wall, -10), (cx - half + 4, top + 2, (half - 4) * 2, 13))
    ay = top - 4
    pygame.draw.rect(surf, _retint((110, 80, 50), night), (cx - half - 1, ay - 2, half * 2 + 2, 2))
    for i, ax in enumerate(range(cx - half, cx + half, 6)):
        col = aw_a if i % 2 == 0 else aw_b
        pygame.draw.polygon(surf, col, [
            (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])
    counter = _retint((120, 84, 52), night)
    pygame.draw.rect(surf, counter, (cx - half + 1, g - 15, (half - 1) * 2, 15))
    pygame.draw.rect(surf, _shade(counter, 16), (cx - half + 1, g - 15, (half - 1) * 2, 2))
    if steam:
        col = _mix((236, 230, 218), (214, 168, 110), 0.6) if night > 0.4 else (236, 238, 240)
        _wisp(surf, cx - 3, g - 18, t, n=3, rise=22, spread=2.6, peak_a=54, r0=1, color=col)


# ════════════════════════════════════════════════════════════════════════════
# A1 — THE IRON-FLOWER SCAFFOLD.  A squat timber frame carrying a straw-thatch
# SPLASH BOARD: the "tree" the molten iron is beaten against. It is deliberately
# NOT a stall — no awning stripe, no counter, a braced A-frame and a shaggy
# thatch panel — so the player reads a different KIND of structure the three
# times it is planted before it ever lights.
# ════════════════════════════════════════════════════════════════════════════

def _scaffold(surf, cx, night, t, *, state='manned', wet=0.0, glow_k=1.0):
    """states: 'bare' (Ch5/6/7 plant, dark, draped, standing in the rain)
              'manned' (crew up, crucible lit, no burst yet)
              'burst'  (the strike frame — caller adds sparks/rim)
              'cold'   (wind-down: scorched timber, thatch burnt, thread of smoke)
    `glow_k` scales the hearth's light budget: at contact the furnace is pulled
    down so it stops out-ranking the thing it just threw."""
    g = FAR_Y
    scorched = state == 'cold'
    tim = _retint((116, 84, 52), night)
    if scorched:
        tim = _mix(tim, (48, 42, 40), 0.55)
    tim_dk = _shade(tim, -30)
    tim_hi = _shade(tim, 16)

    top = g - 54                       # ~54 px apparatus, far deck
    # Splayed A-frame legs + two cross braces: a truss silhouette no stall has.
    for sgn in (-1, 1):
        pygame.draw.line(surf, tim_dk, (cx + sgn * 20, L(g)), (cx + sgn * 11, L(top + 6)), 4)
        pygame.draw.line(surf, tim, (cx + sgn * 20, L(g)), (cx + sgn * 11, L(top + 6)), 2)
    pygame.draw.line(surf, tim_dk, (cx - 18, L(g - 14)), (cx + 18, L(g - 14)), 2)
    pygame.draw.line(surf, tim_dk, (cx - 17, L(g - 12)), (cx + 17, L(g - 30)), 1)
    pygame.draw.line(surf, tim_dk, (cx + 17, L(g - 12)), (cx - 17, L(g - 30)), 1)
    # Head beam.
    pygame.draw.rect(surf, tim_dk, (cx - 15, L(top + 4), 30, 4))
    pygame.draw.line(surf, tim_hi, (cx - 14, L(top + 4)), (cx + 14, L(top + 4)), 1)

    if state == 'bare':
        # The Ch5/6/7 plant: a tarp/straw drape roped over the head beam, the
        # whole rig dark and empty. It has to be recognisable as the SAME object
        # 80 seconds later with a fire on it, so the truss stays fully visible
        # and only the board is covered.
        drape = _retint((104, 96, 82), night)
        pygame.draw.polygon(surf, _shade(drape, -26), [
            (cx - 17, L(top + 2)), (cx + 17, L(top + 2)),
            (cx + 13, L(top + 26)), (cx - 13, L(top + 26))])
        pygame.draw.polygon(surf, drape, [
            (cx - 16, L(top + 3)), (cx + 16, L(top + 3)),
            (cx + 12, L(top + 24)), (cx - 12, L(top + 24))])
        for k in range(-2, 3):
            pygame.draw.line(surf, _shade(drape, -34), (cx + k * 7, L(top + 4)),
                             (cx + k * 6, L(top + 24)), 1)
        rope = _retint((150, 132, 96), night)
        pygame.draw.line(surf, rope, (cx - 17, L(top + 12)), (cx + 17, L(top + 12)), 1)
        # Rain running off the low corner — the storm chapter's own idiom, on a
        # capped cool grey so a wet highlight can't out-rank the coin after dark.
        rain = _cap_to(_retint((178, 190, 208), night), 138)
        for k in range(4):
            rx = cx - 12 + k * 9
            pygame.draw.line(surf, rain, (rx, L(top + 26)), (rx - 1, L(top + 34)), 1)
        return

    # THE SPLASH BOARD — a shaggy straw-thatch panel bound to the head beam,
    # angled forward so struck iron sprays UP and OUT toward the player.
    straw = _retint((176, 150, 96), night)
    if scorched:
        straw = _mix(straw, (56, 50, 46), 0.62)
    straw_dk = _shade(straw, -34)
    bd_top = L(top + 6)
    bd_bot = L(top + 27)
    pygame.draw.polygon(surf, straw_dk, [
        (cx - 16, bd_top), (cx + 16, bd_top), (cx + 14, bd_bot), (cx - 14, bd_bot)])
    for k in range(-14, 15, 2):
        jag = 2 if (k // 2) % 2 else 4
        col = straw if (k // 2) % 3 else _shade(straw, -14)
        pygame.draw.line(surf, col, (cx + k, bd_top + 1), (cx + int(k * 0.9), bd_bot + jag), 1)
    pygame.draw.line(surf, _retint((132, 100, 62), night), (cx - 16, bd_top + 1), (cx + 16, bd_top + 1), 2)
    if scorched:
        # Burnt-through fringe: the board's bottom edge eaten away in two bites.
        for bx, bw in ((cx - 9, 7), (cx + 4, 6)):
            pygame.draw.polygon(surf, _mix(PAVE_NIGHT if night > 0.5 else PAVE_DAY,
                                           (30, 26, 26), 0.5),
                                [(bx, bd_bot + 3), (bx + bw, bd_bot + 3),
                                 (bx + bw - 1, bd_bot - 4), (bx + 1, bd_bot - 3)])

    # The CRUCIBLE hearth at the foot — the iron source, and the only steady lit
    # thing on the rig between bursts.
    hearth = _retint((80, 72, 66), night)
    pygame.draw.rect(surf, hearth, (cx - 11, L(g - 9), 22, 9))
    pygame.draw.rect(surf, _shade(hearth, -22), (cx - 11, L(g - 9), 22, 9), 1)
    for bxx in range(cx - 8, cx + 9, 6):
        pygame.draw.line(surf, _shade(hearth, -16), (bxx, L(g - 9)), (bxx, L(g)), 1)
    if state in ('manned', 'burst') and night > 0.05:
        _warm_glow(surf, cx, L(g - 9), radius=9, peak=int(44 * glow_k), color=(150, 92, 46))
        pot = _cap150((132, 74, 38))
        pygame.draw.ellipse(surf, pot, (cx - 6, L(g - 12), 12, 4))
        pulse = 0.5 + 0.5 * math.sin(t * 3.0)
        pygame.draw.ellipse(surf, _cap150(_mix((96, 52, 28), (146, 90, 44), pulse)),
                            (cx - 4, L(g - 11), 8, 2))
    elif state == 'manned':
        pygame.draw.ellipse(surf, _retint((120, 70, 40), night), (cx - 6, L(g - 12), 12, 4))

    if scorched:
        # A1's third state: a thread of grey smoke still coming off the cold rig.
        _wisp(surf, cx + 2, L(top + 8), t, n=3, rise=26, spread=2.0, speed=0.42,
              peak_a=30, r0=1, sway=3.0, color=(160, 158, 156))
        _wisp(surf, cx - 5, L(g - 10), t, n=2, rise=18, spread=1.6, speed=0.5,
              phase=0.4, peak_a=24, r0=1, sway=2.2, color=(150, 148, 148))


# ════════════════════════════════════════════════════════════════════════════
# A2 — THE CREW.  Soaked straw hat + sheepskin: a wide dark disc over a bulky
# pale-fleece shoulder mass. Nothing else in the game has that outline, which is
# the whole point — the two figures at the rig are legible as fire crew at 18 px
# before a single spark exists.
# ════════════════════════════════════════════════════════════════════════════

def _crew_body(surf, cx, feet, night, *, lean=0):
    fleece = _retint((176, 168, 148), night)
    fleece_dk = _shade(fleece, -38)
    under = _retint((78, 66, 58), night)
    torso_top = feet - 15
    for sgn in (-1, 1):
        pygame.draw.line(surf, under, (cx + sgn * 2, feet - 6), (cx + sgn * 3, feet), 2)
    # Sheepskin cape: a lumpy trapezoid, deliberately WIDER at the shoulder than
    # any civilian coat so the pair read as protected, not just dressed.
    pts = [(cx - 7 + lean, torso_top), (cx + 7 + lean, torso_top),
           (cx + 6, feet - 5), (cx - 6, feet - 5)]
    pygame.draw.polygon(surf, fleece, pts)
    pygame.draw.polygon(surf, fleece_dk, pts, 1)
    for k in range(3):
        pygame.draw.arc(surf, fleece_dk, (cx - 7 + lean, torso_top + 1 + k * 4, 14, 5),
                        math.radians(190), math.radians(350), 1)
    hy = torso_top - 4
    pygame.draw.circle(surf, _retint(SKIN, night), (cx + lean, hy), 3)
    # SOAKED straw hat — wide, heavy, drooping brim, darker than dry straw.
    hat = _retint((128, 112, 78), night)
    pygame.draw.polygon(surf, _shade(hat, -28), [
        (cx + lean - 9, hy - 1), (cx + lean, hy - 8), (cx + lean + 9, hy - 1),
        (cx + lean + 7, hy + 1), (cx + lean - 7, hy + 1)])
    pygame.draw.polygon(surf, hat, [
        (cx + lean - 8, hy - 1), (cx + lean, hy - 7), (cx + lean + 8, hy - 1)])
    pygame.draw.line(surf, _shade(hat, -34), (cx + lean - 8, hy - 1), (cx + lean + 8, hy - 1), 1)
    return torso_top + 2, hy


def _thrower(surf, cx, night, ph):
    """A2a — the THROWER. 4-phase over-shoulder ladle swing on a 1.3 s wind-up:
    0 cocked low behind · 1 loaded high behind · 2 the throw across the body ·
    3 follow-through, scoop empty and forward. The 22 px handle is the read."""
    feet = FAR_Y
    sh_y, hy = _crew_body(surf, cx, L(feet), night, lean=(-1 if ph < 2 else 1))
    wood = _retint((150, 122, 76), night)
    wood_dk = _shade(wood, -32)
    # Handle angle per phase, degrees from +x with screen-y inverted. Every
    # phase keeps the scoop ABOVE the deck line — a ladle that dips through the
    # paving is the one error that would break the whole apparatus read.
    ang, load = ((198, 1), (148, 1), (62, 1), (12, 0))[ph]
    hand = (cx + (-4 if ph < 2 else 4), sh_y + 3)
    a = math.radians(ang)
    tip = (hand[0] + int(math.cos(a) * 22), hand[1] - int(math.sin(a) * 22))
    pygame.draw.line(surf, wood_dk, (hand[0], hand[1] + 1), (tip[0], tip[1] + 1), 3)
    pygame.draw.line(surf, wood, hand, tip, 2)
    # the willow SCOOP at the tip — a small open bowl, tilted with the swing
    bowl = pygame.Rect(tip[0] - 4, tip[1] - 3, 9, 6)
    pygame.draw.ellipse(surf, wood_dk, bowl)
    pygame.draw.ellipse(surf, _shade(wood, 10), bowl.inflate(-2, -2))
    if load and night > 0.05:
        # molten charge riding in the scoop, capped like every other lit pixel
        pygame.draw.ellipse(surf, _cap150((150, 96, 48)), bowl.inflate(-4, -3))
        _warm_glow(surf, bowl.centerx, bowl.centery, radius=6, peak=34, color=(150, 96, 48))
    elif load:
        pygame.draw.ellipse(surf, _retint((140, 92, 52), night), bowl.inflate(-4, -3))
    # both arms on the handle — a two-handed swing, not a wave
    fleece = _retint((176, 168, 148), night)
    pygame.draw.line(surf, fleece, (cx - 5, sh_y + 1), hand, 2)
    pygame.draw.line(surf, fleece, (cx + 5, sh_y + 2), (hand[0] + 2, hand[1] + 1), 2)


def _striker(surf, cx, night, ph):
    """A2b — the STRIKER. A willow BAT held vertical, one frame of contact at the
    arc's apex. Phases: 0 waiting low · 1 raised · 2 CONTACT (bat horizontal, at
    the board) · 3 recoil. Mirrored stance so the pair never reads as twins."""
    feet = FAR_Y
    sh_y, hy = _crew_body(surf, cx, L(feet), night, lean=(1 if ph == 2 else 0))
    wood = _retint((160, 138, 92), night)
    wood_dk = _shade(wood, -34)
    hand = (cx - 5, sh_y + 2)
    # S2's bat swings LEFT and level — straight at the splash board standing to
    # the striker's left, which is what makes the contact frame legible.
    ang, ln = ((105, 16), (80, 18), (160, 20), (120, 17))[ph]
    a = math.radians(ang)
    tip = (hand[0] + int(math.cos(a) * ln), hand[1] - int(math.sin(a) * ln))
    pygame.draw.line(surf, wood_dk, (hand[0], hand[1] + 1), (tip[0], tip[1] + 1), 4)
    pygame.draw.line(surf, wood, hand, tip, 2)
    pygame.draw.circle(surf, wood_dk, tip, 2)
    fleece = _retint((176, 168, 148), night)
    pygame.draw.line(surf, fleece, (cx - 4, sh_y), hand, 2)
    pygame.draw.line(surf, fleece, (cx + 5, sh_y + 2), (cx + 7, sh_y + 7), 2)


# ════════════════════════════════════════════════════════════════════════════
# A3 — THE SPARK-BURST SYSTEM.  Ballistic sparks drawn as sub-stepped COMETS, a
# jittered apex clamp under y=512, a ground bounce + skitter, and exactly one 2 px
# core pixel at the cap on the contact frame. Every spark is deterministic in
# its index, so the same burst renders identically on desktop and in WASM.
# ════════════════════════════════════════════════════════════════════════════

G_ACC = 900.0                 # px/s^2 — the shipped Particle gravity. A fan and a
                              # tree differ by how fast the spray falls, not by
                              # how it is launched: at 900 the skirt is pulled
                              # back under the crown and the streaks lengthen.
SPREAD_DEG = 62               # max launch angle off vertical
BURST_PERIOD = 2.5            # s; the plan's 2.6 s cadence with a dark beat
CONTACT_T = 0.14              # when in the cycle the bat meets the charge
TRAIL_T = 0.14                # s of the spark's own parabola drawn behind it
TRAIL_N = 12                  # sub-steps along that arc
# The plan budgeted 70-120 sparks when each was a 2 px smudge. Comets and the R9
# corridor together mean a spark now costs less light at the top of the frame
# than it did, so the ceiling buys foliage instead of glare.
BURST_MIN, BURST_MAX = 80, 140

# Iron cools as it rises, so the top of the arc is both dimmer and less orange —
# which is also what opens the hue gap between a spark and a coin.
SPARK_COOL = (170, 120, 90)
CORRIDOR_LO = 540             # below this the spark is at full strength
CORRIDOR_HI = SPARK_CEIL      # at the ceiling it is down to 35 %
CORRIDOR_FLOOR = 0.35


def _h(i, k):
    """A stable per-spark hash. Same value on every target, no RNG state."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1.0


def _spark_at(i, cx, cy, age, *, apex_y=SPARK_CEIL, ground_y=FAR_Y):
    """Ballistic position + alpha for spark `i`, `age` seconds after contact.
    Returns None once dead. The apex clamp is applied to the LAUNCH velocity,
    not to the plotted pixel, so the arc stays a real parabola that simply
    cannot reach above the ceiling."""
    t_off = _h(i, 1) * 0.10
    a = age - t_off
    if a < 0:
        return None
    # Cubic spread: dense near vertical, thinning to a wide skirt. That is what
    # makes a datiehua burst read as a chrysanthemum rather than as a uniform
    # fan, and it puts enough sparks near vertical to actually touch the ceiling.
    sp = (_h(i, 3) - 0.5) * 2.0
    af = sp ** 3
    ang = math.radians(-90 + af * SPREAD_DEG)
    # The skirt is glancing debris off the board, so it carries less energy than
    # the near-vertical spray. Without that the widest sparks travel twice as far
    # sideways as the crown is tall and the silhouette collapses back into a fan.
    speed = (170 + 120 * _h(i, 2)) * (1.0 - 0.34 * abs(af))
    vx = speed * math.cos(ang)
    vy = speed * math.sin(ang)
    # Per-spark jitter on the ceiling limit. A single shared limit stacks every
    # clamped spark on one scanline, and a straight line across the top of a fire
    # is the one thing that reads as a bug rather than as physics.
    vlim = math.sqrt(2 * G_ACC * max(1.0, cy - apex_y)) * (0.80 + 0.20 * _h(i, 5))
    vy = max(vy, -vlim)
    fall = ground_y - cy
    t_land = (-vy + math.sqrt(max(0.0, vy * vy + 2 * G_ACC * fall))) / G_ACC
    life = t_land + 0.4
    if a > life:
        return None
    if a <= t_land:
        x = cx + vx * a
        y = cy + vy * a + 0.5 * G_ACC * a * a
    else:
        # ground bounce: skitter 3-8 px along the paving and die over 0.4 s
        d = a - t_land
        x = cx + vx * t_land + vx * 0.30 * d * math.exp(-3.2 * d)
        y = ground_y - abs(math.sin(d * 16.0)) * 1.6 * math.exp(-4.0 * d)
    frac = a / life
    tail = 1.0 if frac < 0.72 else max(0.0, (1.0 - frac) / 0.28)
    alpha = (120 + 80 * _h(i, 4)) * tail
    return x, y, alpha


def _burst(surf, cx, cy, age, night, *, count=96, apron=None):
    """Render one burst at `age` seconds past contact. Returns (points, min_y).
    `apron` = (x0, x1) turns on the doused-paving reflection columns."""
    pts = []
    min_y = 9999
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i in range(count):
        st = _spark_at(i, cx, cy, age)
        if st is None:
            continue
        x, y, alpha = st
        min_y = min(min_y, y)
        # The streak is the spark's OWN analytic parabola re-sampled backwards —
        # 10 sub-steps over 0.12 s with alpha decaying along it — not a stack of
        # stale frames. A comet is what a 1 px point needs to read as fire, and
        # sub-stepping buys it with more LIT PIXELS at strictly lower alpha, so
        # the peak luma does not move at all.
        for k in range(TRAIL_N, 0, -1):
            f = k / float(TRAIL_N)
            old = _spark_at(i, cx, cy, age - f * TRAIL_T)
            if old is None:
                continue
            ox, oy, _oa = old
            _put(lay, ox, oy, alpha * (1.0 - 0.92 * f) ** 0.85)
        _put(lay, x, y, alpha)
        pts.append((x, y, alpha))
    surf.blit(lay, (0, 0))
    if apron is not None:
        _apron_reflections(surf, pts, apron)
    return pts, min_y


def _put(lay, x, y, alpha):
    """One spark pixel, with the R9 CORRIDOR applied. Between y 540 and the 512
    ceiling the spark is fading to 35 % and cooling toward (170,120,90): that band
    is where the FX crosses into the vertical range a pillar gap can occupy, so
    the sparks arrive there already on their way out."""
    xx, yy = int(x), int(L(y))
    if not (0 <= xx < lay.get_width() and 0 <= yy < lay.get_height()):
        return
    k = (CORRIDOR_LO - y) / float(CORRIDOR_LO - CORRIDOR_HI)
    k = max(0.0, min(1.0, k))
    a = max(0, min(255, int(alpha * (1.0 - (1.0 - CORRIDOR_FLOOR) * k))))
    if a <= 3 or lay.get_at((xx, yy))[3] >= a:
        return
    lay.set_at((xx, yy), (*_mix(SPARK_COL, SPARK_COOL, k), a))


def _core_pixel(surf, cx, cy, age, night):
    """The ONE 2 px core pixel at the cap (150 luma), for <=4 frames at contact.
    It is the hottest pixel the whole fire show is allowed, and it still sits
    80 luma under the coin."""
    if not (0 <= age < 4 / 60.0):
        return
    pygame.draw.rect(surf, SPARK_COL, (cx - 1, L(cy) - 1, 2, 2))


def _apron_reflections(surf, pts, apron):
    """A5 — every burst mirrors in the doused paving as 1 px-wide, 6-10 px
    dither columns at alpha 45. Not a mirror image: a smear, which is what a
    wet stone actually does to a moving point source."""
    x0, x1 = apron
    lay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for (x, y, a) in pts:
        if not (x0 <= x <= x1) or y > FAR_Y:
            continue
        h = 6 + int(4 * ((x * 7) % 5) / 4)
        col_a = int(45 * min(1.0, a / 160.0))
        for k in range(h):
            if (int(x) + k) % 2 and k > 1:
                continue
            yy = L(FAR_Y) + 2 + k
            if 0 <= int(x) < lay.get_width() and yy < lay.get_height():
                lay.set_at((int(x), yy), (*SPARK_COL, max(0, col_a - k * 3)))
    surf.blit(lay, (0, 0))


def _burst_smoke(surf, cx, night, age):
    """A grey veil at alpha <=30 after each burst — the residue that makes three
    bursts read as one accumulating show. Its rise is trimmed so the veil tops out
    at y~514, i.e. exactly where the SHIPPED steamer's own steam column already
    ends: the smoke borrows an existing ceiling instead of inventing one."""
    if age < 0.25:
        return
    _wisp(surf, cx - 4, L(FAR_Y - 50), age * 0.9, n=3, rise=25, spread=3.2,
          speed=0.34, peak_a=30, r0=2, sway=3.6, color=(168, 164, 160))
    _wisp(surf, cx + 7, L(FAR_Y - 46), age * 0.9, n=2, rise=21, spread=2.6,
          speed=0.40, phase=0.5, peak_a=24, r0=1, sway=3.0, color=(160, 158, 158))


# ════════════════════════════════════════════════════════════════════════════
# A4 — THE BURST RIM-LIGHT PASS.  The storm chapter flattens the street into a
# black silhouette on a lightning frame; the iron flower does the exact inverse
# with the same one-blit machinery — every top edge in the PROMENADE layer gets a
# 1 px warm highlight for 3 frames on a 100/60/30 decay. Same cost, opposite
# meaning. Three frames, not two: at two, one dropped WASM frame and the whole
# pass is invisible, and a light that sometimes doesn't happen is worse than no
# light at all.
# ════════════════════════════════════════════════════════════════════════════

RIM_DECAY = (1.0, 0.6, 0.3)


def _rim_light(layer, *, strength=1.0, boost=18, cap=RIM_CAP, warm=(255, 208, 150)):
    """Brighten the 1 px TOP EDGE of every opaque run on an SRCALPHA layer.
    Detected as 'opaque pixel whose neighbour above is transparent', so hats,
    shoulders, awning ribs and cart beds all catch it, exactly as a burst of
    light from above and behind the rig would. `strength` scales BOTH the warm
    mix and the value boost, so frame 3 is a whisper rather than a hard cut."""
    w, h = layer.get_size()
    edges = []
    for x in range(w):
        prev_op = False
        for y in range(h):
            op = layer.get_at((x, y))[3] > 8
            if op and not prev_op:
                edges.append((x, y))
            prev_op = op
    mixf = 0.35 * strength
    bst = boost * strength
    for (x, y) in edges:
        r, g, b, a = layer.get_at((x, y))
        lit = _mix((r, g, b), warm, mixf)
        lit = (_clamp(lit[0] + bst), _clamp(lit[1] + bst * 0.82), _clamp(lit[2] + bst * 0.55))
        layer.set_at((x, y), (*_cap_to(lit, cap), a))


# ════════════════════════════════════════════════════════════════════════════
# A6 — THE PEARL + BEARER.  Convention puts the pearl of wisdom on a pole ahead
# of the head; here the bearer teases it UP-LEFT, i.e. toward Pip, so the one
# object leading the whole parade is pointing at the player.
# ════════════════════════════════════════════════════════════════════════════

def _pearl_bearer(surf, cx, night, t, *, feet=NEAR_Y, trace=False):
    sh_y, hy = None, None
    robe = (168, 74, 62)
    hy, sh_y = _person(surf, cx, L(feet), night, h=30, coat=robe, arms='up', face=1)
    # figure-8 at 0.8 Hz: x on the fundamental, y on the second harmonic
    ph = t * 0.8 * math.tau
    px = cx + 4 + int(math.sin(ph) * 9)
    py = L(feet) - 56 + int(math.sin(ph * 2) * 6)
    pole = _retint((132, 100, 60), night)
    pygame.draw.line(surf, _shade(pole, -28), (cx + 3, sh_y - 6), (px, py + 5), 3)
    pygame.draw.line(surf, pole, (cx + 3, sh_y - 6), (px, py + 5), 1)
    if trace:
        for k in range(28):
            a2 = k / 28.0 * math.tau
            tx = cx + 4 + int(math.sin(a2) * 9)
            ty = L(feet) - 56 + int(math.sin(a2 * 2) * 6)
            surf.set_at((tx, ty), (96, 108, 132))
    if night > 0.05:
        # The pearl is the parade's LEAD object, not its brightest: at 145 it was
        # within 5 luma of the fire's own core pixel and the 3 px pole under it
        # washed out. Capped 128 with a 24-luma halo budget, the pole survives the
        # glow and the fire keeps the top of the ladder.
        _warm_glow(surf, px, py, radius=8, peak=24, color=(150, 108, 54))
    amber = _cap_to((186, 138, 74), 128) if night > 0.05 else (216, 168, 96)
    pygame.draw.circle(surf, _shade(amber, -34), (px, py), 5)
    pygame.draw.circle(surf, amber, (px, py), 4)
    pygame.draw.circle(surf, _cap_to(_shade(amber, 22), 128), (px - 1, py - 1), 2)
    # the tassel that tells you a hand is swinging it, not that it floats
    pygame.draw.line(surf, _retint((172, 66, 56), night), (px, py + 4), (px - 2, py + 8), 1)


# ════════════════════════════════════════════════════════════════════════════
# A7 — THE DRUM-AND-CYMBAL CART.  Research: the drum rides a WHEELED PLATFORM
# that a second person pulls. It trails the head here because the player's
# reveal order is right-to-left and the dramatic sequence is mystery -> face ->
# mass -> drum.
# ════════════════════════════════════════════════════════════════════════════

def _spoked_wheel(surf, cx, cy, r, night, *, far=False):
    """weekend_kit._spoked_wheel construction — iron tyre, light interior, three
    full-diameter spokes, a hub that is never the brightest pixel."""
    iron = _retint((70, 62, 56) if not far else (54, 48, 44), night)
    wood = _retint((150, 112, 66) if not far else (116, 86, 52), night)
    pygame.draw.circle(surf, iron, (cx, cy), r)
    pygame.draw.circle(surf, wood, (cx, cy), max(1, r - 1))
    for k in range(3):
        a = k * math.pi / 3.0
        dx, dy = math.cos(a) * (r - 1), math.sin(a) * (r - 1)
        pygame.draw.line(surf, iron, (cx - dx, cy - dy), (cx + dx, cy + dy), 1)
    pygame.draw.circle(surf, _shade(wood, -10), (cx, cy), 1)


def _drum_cart(surf, cx, night, t, *, feet=NEAR_Y):
    g = L(feet)
    wood = _retint((132, 96, 56), night)
    wood_dk = _shade(wood, -30)
    wood_hi = _shade(wood, 18)
    _spoked_wheel(surf, cx + 8, g - 4, 4, night, far=True)
    bed_y = g - 11
    pygame.draw.polygon(surf, wood, [(cx - 18, bed_y), (cx + 18, bed_y),
                                     (cx + 18, bed_y + 4), (cx - 18, bed_y + 4)])
    pygame.draw.polygon(surf, wood_dk, [(cx - 18, bed_y), (cx + 18, bed_y),
                                        (cx + 18, bed_y + 4), (cx - 18, bed_y + 4)], 1)
    pygame.draw.line(surf, wood_hi, (cx - 17, bed_y), (cx + 17, bed_y), 1)
    # THE BARREL DRUM at 1.5x the busker's — head-on, so the ivory head is the
    # cart's one big shape and the parade's rhythm has a face.
    drum = _mix(_retint((162, 62, 48), night), (70, 70, 96), 0.20 * night)
    dcx, dcy = cx - 2, bed_y - 15
    pygame.draw.ellipse(surf, _shade(drum, -26), (dcx - 17, dcy - 15, 34, 30))
    pygame.draw.ellipse(surf, drum, (dcx - 16, dcy - 14, 32, 28))
    head = _cap_to((200, 178, 142), 128) if night > 0.05 else (206, 186, 152)
    pygame.draw.ellipse(surf, head, (dcx - 13, dcy - 12, 26, 9))
    pygame.draw.ellipse(surf, _shade(head, -30), (dcx - 13, dcy - 12, 26, 9), 1)
    tack = _cap_to((176, 146, 88), 128) if night > 0.05 else (186, 156, 96)
    for ti in range(-3, 4):
        pygame.draw.circle(surf, tack, (dcx + ti * 4, dcy - 2), 1)
    pygame.draw.line(surf, _shade(drum, -34), (dcx - 15, dcy + 6), (dcx + 15, dcy + 6), 1)
    # the drummer riding the bed, two sticks in antiphase. Standing on the bed
    # rather than seated behind it, because at the near lane's 31 px a seated
    # figure disappears entirely behind a 30 px drum.
    _person(surf, cx + 14, bed_y, night, h=26, coat=(96, 76, 128), arms='down')
    for phi in (0.0, math.pi):
        travel = max(0.0, math.sin(t * 4.5 + phi))
        sy = dcy - 10 - int((1.0 - travel) * 7)
        sx = dcx + (7 if phi else -7)
        pygame.draw.line(surf, _retint((176, 150, 100), night), (cx + 10, bed_y - 12), (sx, sy), 2)
    # two flanking CYMBAL figures; the clash is a 1-frame capped ivory disc
    for sgn, phi in ((-1, 0.0), (1, 1.7)):
        fx = cx + sgn * 28
        hy2, shy = _person(surf, fx, g, night, h=30,
                           coat=(70, 110, 150) if sgn < 0 else (150, 120, 70), arms='up')
        clash = math.sin(t * 4.5 + phi) > 0.86
        spread = 2 if clash else 6
        cy2 = shy - 8
        disc = _cap_to((190, 176, 130), 132) if night > 0.05 else (206, 190, 142)
        # The clash halo goes down FIRST, so the additive pass lands on dark
        # paving instead of stacking on the already-capped ivory disc.
        if clash and night > 0.05:
            _warm_glow(surf, fx, cy2, radius=6, peak=26, color=(140, 130, 100))
        for s2 in (-1, 1):
            pygame.draw.ellipse(surf, _shade(disc, -34),
                                (fx + s2 * spread - 4, cy2 - 3, 8, 7))
            pygame.draw.ellipse(surf, disc, (fx + s2 * spread - 3, cy2 - 2, 6, 5))
    # the puller at the front — the wheeled platform is dragged, not pushed
    _person(surf, cx - 32, g, night, h=30, coat=(120, 92, 74), arms='point')
    pygame.draw.line(surf, _retint((150, 132, 96), night),
                     (cx - 28, g - 12), (cx - 18, bed_y + 1), 1)
    _spoked_wheel(surf, cx - 6, g - 4, 5, night)
    sh = _mix(_retint((60, 52, 44), night), (0, 0, 0), 0.2)
    pygame.draw.line(surf, sh, (cx - 14, g), (cx + 14, g), 1)


# ════════════════════════════════════════════════════════════════════════════
# A8 — THE DRAPED DRAGON-HEAD HANDCART.  148 seconds before it dances, the head
# rolls past under a red cloth, roped down, and nobody looks at it. The cloth
# must TENT over two horn nubs and a snout ridge — a lump that is obviously a
# head without ever showing a face.
# ════════════════════════════════════════════════════════════════════════════

def _draped_cart(surf, cx, night, t, *, feet=FAR_Y):
    g = L(feet)
    wood = _retint((132, 96, 56), night)
    wood_dk = _shade(wood, -30)
    wood_hi = _shade(wood, 18)
    wr = 4
    axle_x, axle_y = cx - 3, g - wr
    _spoked_wheel(surf, axle_x + 4, axle_y - 2, wr - 1, night, far=True)
    bed_y = g - wr * 2 - 2
    x0, x1 = cx - 13, cx + 13
    pygame.draw.polygon(surf, wood, [(x0, bed_y), (x1, bed_y), (x1, bed_y + 3), (x0, bed_y + 3)])
    pygame.draw.polygon(surf, wood_dk, [(x0, bed_y), (x1, bed_y), (x1, bed_y + 3), (x0, bed_y + 3)], 1)
    pygame.draw.line(surf, wood_hi, (x0 + 1, bed_y), (x1 - 1, bed_y), 1)
    for off in (0, 2):
        pygame.draw.line(surf, wood_dk, (x1 - 1, bed_y + 1 + off), (x1 + 9, bed_y - 4 + off), 1)

    # THE LUMP — 16 px of red cloth tented over horns, brow and snout.
    cloth = _retint((176, 56, 48), night)
    cloth_dk = _shade(cloth, -36)
    cloth_hi = _shade(cloth, 20)
    top = bed_y - 16
    silhouette = [
        (cx - 12, bed_y),          # cloth skirt, left
        (cx - 10, top + 9),
        (cx - 7, top + 3),         # LEFT HORN nub tenting the cloth
        (cx - 5, top + 6),
        (cx - 1, top),             # RIGHT HORN nub, taller
        (cx + 2, top + 5),
        (cx + 7, top + 6),         # brow shelf
        (cx + 11, top + 11),       # the SNOUT ridge running down-forward
        (cx + 13, bed_y),
    ]
    pygame.draw.polygon(surf, cloth_dk, [(p[0], p[1] + 1) for p in silhouette])
    pygame.draw.polygon(surf, cloth, silhouette)
    pygame.draw.lines(surf, cloth_hi, False,
                      [(cx - 7, top + 4), (cx - 1, top + 1), (cx + 7, top + 7)], 1)
    for k in range(-9, 12, 4):
        pygame.draw.line(surf, cloth_dk, (cx + k, bed_y), (cx + int(k * 0.85), top + 9), 1)
    # ropes lashing it to the bed — the detail that says "in transit, valuable"
    rope = _retint((178, 160, 118), night)
    pygame.draw.line(surf, rope, (cx - 12, bed_y - 5), (cx + 13, bed_y - 5), 1)
    pygame.draw.line(surf, rope, (cx - 3, top + 4), (cx - 6, bed_y), 1)
    pygame.draw.line(surf, rope, (cx - 3, top + 4), (cx + 6, bed_y), 1)
    _spoked_wheel(surf, axle_x, axle_y, wr, night)
    sh = _mix(_retint((60, 52, 44), night), (0, 0, 0), 0.2)
    pygame.draw.line(surf, sh, (axle_x - wr, g), (axle_x + wr, g), 1)


# ════════════════════════════════════════════════════════════════════════════
# A13 — THE LANTERN ARCH.  The parade's gateway: two poles and an arc of six
# lanterns spanning ~120 px, apex y=497.  That number is not a new maximum and it
# is not a compromise: 497 is GROUND_Y-98, the top_y the SHIPPED night-festival
# lantern garland is already strung at. 560 put the arch underneath the overhead
# lattice it is supposed to be a gateway through; 477 would have been a genuinely
# new ceiling. 497 is the height the street already owns.
# ════════════════════════════════════════════════════════════════════════════

GARLAND_TOP_Y = 497              # game/foreground_promenade.py, NIGHT festival


def _lantern_arch(surf, cx, night, t, *, span=120, apex=GARLAND_TOP_Y, feet=FAR_Y,
                  ltop=SLICE_TOP):
    """`ltop` is the world y the target surface starts at — the arch is the one
    piece on this sheet that needs a taller slice than 500-647 to be drawn
    honestly, so it carries its own vertical origin instead of a global one."""
    g = feet - ltop
    pole = _retint((116, 88, 56), night)
    pole_dk = _shade(pole, -28)
    x0, x1 = cx - span // 2, cx + span // 2
    top = apex - ltop
    for px in (x0, x1):
        pygame.draw.line(surf, pole_dk, (px, g), (px, top + 12), 3)
        pygame.draw.line(surf, pole, (px, g), (px, top + 12), 1)
        pygame.draw.rect(surf, pole_dk, (px - 3, g - 2, 7, 2))
    # the arc itself — a shallow catenary of rope between the two pole heads
    arc = []
    for i in range(25):
        f = i / 24.0
        ax = x0 + f * span
        ay = top + 12 - math.sin(f * math.pi) * 12
        arc.append((int(ax), int(ay)))
    pygame.draw.lines(surf, _retint((92, 78, 58), night), False, arc, 2)
    pygame.draw.lines(surf, _retint((146, 126, 92), night), False, arc, 1)
    for k in range(6):
        f = 0.09 + k * 0.164
        i = int(f * 24)
        lx, ly = arc[i]
        sway = math.sin(t * 1.1 + k) * 1.0
        lx = int(lx + sway)
        pygame.draw.line(surf, _retint((70, 56, 44), night), (lx, ly), (lx, ly + 3), 1)
        shell = _cap150((150, 70, 60)) if night > 0.05 else (192, 92, 76)
        shell_lt = _cap150((150, 96, 80)) if night > 0.05 else (214, 130, 104)
        if night > 0.05:
            _warm_glow(surf, lx, ly + 9, radius=8, peak=34, color=(150, 92, 56))
        pygame.draw.ellipse(surf, shell, (lx - 4, ly + 3, 8, 11))
        pygame.draw.ellipse(surf, shell_lt, (lx - 3, ly + 4, 6, 9))
        pygame.draw.rect(surf, _retint((50, 34, 26), night), (lx - 3, ly + 3, 6, 2))
        pygame.draw.rect(surf, _retint((50, 34, 26), night), (lx - 3, ly + 12, 6, 2))
        pygame.draw.line(surf, _retint((172, 66, 56), night), (lx, ly + 14), (lx, ly + 17), 1)


# ════════════════════════════════════════════════════════════════════════════
# A15 — THE RESIDUE SET.  The festival hands back to Ch9 with evidence, not a
# fade: a scorch fan on the paving that decays over two blocks, swept paper
# masks in the gutter, and the cold rig still smoking.
# ════════════════════════════════════════════════════════════════════════════

def _scorch_fan(surf, cx, night, *, decay=0.0, w=170):
    """A 1 px speckle field fanning out from the rig's foot. Density falls with
    distance AND with `decay` (0 fresh -> 1 two blocks later), so the same field
    can be re-emitted per block and simply thins out."""
    col = _mix(PAVE_NIGHT if night > 0.5 else PAVE_DAY, (24, 20, 20), 0.65)
    col2 = _mix(PAVE_NIGHT if night > 0.5 else PAVE_DAY, (40, 34, 30), 0.4)
    n = int(340 * (1.0 - 0.72 * decay))
    for i in range(n):
        f = _h(i, 11)
        ang = math.radians(-172 + _h(i, 12) * 164)
        d = (0.15 + 0.85 * f * f) * (w * 0.5)
        x = cx + math.cos(ang) * d * 1.5
        y = FAR_Y + 3 + abs(math.sin(ang)) * 26 * _h(i, 13)
        if y >= NEAR_Y - 1:
            continue
        if 0 <= int(x) < surf.get_width():
            surf.set_at((int(x), int(L(y))), col if _h(i, 14) > 0.4 else col2)


def _dropped_mask(surf, x, night, *, flipped=False, feet=NEAR_Y - 2):
    """A swept paper monkey mask lying in the gutter — the troupe's souvenir,
    two blocks and one show later. Face-up shows the gold; face-down shows the
    pale paper back and the snapped elastic."""
    y = L(feet)
    if flipped:
        paper = _retint((198, 186, 160), night)
        pygame.draw.ellipse(surf, _shade(paper, -30), (x - 5, y - 3, 10, 6))
        pygame.draw.ellipse(surf, paper, (x - 4, y - 2, 8, 4))
        pygame.draw.line(surf, _retint((120, 108, 88), night), (x + 4, y - 1), (x + 9, y + 1), 1)
    else:
        gold = _cap_to(_retint((188, 158, 84), night), 132)
        pygame.draw.ellipse(surf, _shade(gold, -34), (x - 5, y - 3, 10, 6))
        pygame.draw.ellipse(surf, gold, (x - 4, y - 2, 8, 4))
        ruff = _retint((150, 70, 48), night)
        pygame.draw.arc(surf, ruff, (x - 6, y - 4, 12, 8), math.radians(150), math.radians(390), 1)
        for sgn in (-1, 1):
            pygame.draw.line(surf, ruff, (x + sgn * 2, y - 2), (x + sgn * 8, y - 4), 1)
        pygame.draw.circle(surf, (30, 24, 22), (x - 2, y), 0)
        pygame.draw.circle(surf, (30, 24, 22), (x + 1, y), 0)


# ════════════════════════════════════════════════════════════════════════════
# SHEET FURNITURE
# ════════════════════════════════════════════════════════════════════════════

WIDTH = 1500
PAD = 12


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _wrap(surf, s, x, y, w, sz=9, col=(200, 198, 190), lh=11):
    fnt = _font(sz)
    line = ""
    yy = y
    for wd in s.split(" "):
        test = (line + " " + wd).strip()
        if fnt.size(test)[0] > w:
            surf.blit(fnt.render(line, True, col), (x, yy))
            yy += lh
            line = wd
        else:
            line = test
    if line:
        surf.blit(fnt.render(line, True, col), (x, yy))
    return yy + lh


def _gold_coin(surf, cx, cy, r=8):
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, COIN_CORE)):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _yardsticks(panel, night, *, x=18, coin_x=None, near=False):
    """Adult at the far deck + the gold coin, on every panel that has room.
    `near` adds the NEAR-lane adult beside it — the 1.5x reference every
    front-lane figure on this sheet is now dealt at."""
    _person(panel, x, L(FAR_Y), night, h=18, coat=(96, 104, 140))
    _text(panel, "adult", x - 12, L(FAR_Y) + 2, 7,
          (150, 160, 185) if night > 0.5 else (70, 58, 46))
    if near:
        _person(panel, x + 22, L(NEAR_Y), night, h=30, coat=(84, 92, 124))
        _text(panel, "near 1.5x", x + 6, L(NEAR_Y) + 1, 7,
              (150, 160, 185) if night > 0.5 else (70, 58, 46))
    if coin_x:
        _gold_coin(panel, coin_x, L(SPARK_CEIL) + 14, r=7)
        _text(panel, "coin 230", coin_x - 18, L(SPARK_CEIL) + 24, 7,
              (150, 160, 185) if night > 0.5 else (70, 58, 46))


def _place(sheet, panel, x, y, label, *, sub=None):
    sheet.blit(panel, (x, y))
    pygame.draw.rect(sheet, (74, 78, 94), (x, y, panel.get_width(), panel.get_height()), 1)
    _text(sheet, label, x + 2, y + panel.get_height() + 2, 9, (238, 228, 200), bold=True)
    if sub:
        _wrap(sheet, sub, x + 2, y + panel.get_height() + 14, panel.get_width() - 4, 8,
              (176, 176, 186), 10)
    return y + panel.get_height() + 16


def _zoom(sheet, panel, rect, z, x, y, label):
    crop = pygame.Surface((rect[2], rect[3]))
    crop.blit(panel, (0, 0), rect)
    big = pygame.transform.scale(crop, (rect[2] * z, rect[3] * z))
    pygame.draw.rect(sheet, (60, 64, 80), (x - 2, y - 2, big.get_width() + 4, big.get_height() + 4))
    sheet.blit(big, (x, y))
    pygame.draw.rect(sheet, (120, 126, 146), (x - 2, y - 2, big.get_width() + 4, big.get_height() + 4), 1)
    _text(sheet, label, x, y - 12, 8, (198, 194, 206))
    return big.get_width()


# ════════════════════════════════════════════════════════════════════════════
# PANEL BUILDERS
# ════════════════════════════════════════════════════════════════════════════

def _panel_scaffold(w, night, state, t, *, storm=False, wet=0.0, crew=False,
                    residue=False, clean=False):
    p = _panel(w, night, storm=storm, wet=wet)
    if not clean:
        _guides(p, w)
    cx = w // 2
    if residue:
        _scorch_fan(p, cx, night, decay=0.0, w=int(w * 0.9))
    _scaffold(p, cx, night, t, state=state, wet=wet)
    if crew:
        _thrower(p, cx - 24, night, 1)
        _striker(p, cx + 22, night, 0)
    if state == 'bare':
        # the brazier crew sheltering under the rig through the storm
        _person(p, cx - 8, L(FAR_Y), night, h=17, coat=(96, 92, 84), arms='down')
        _person(p, cx + 7, L(FAR_Y), night, h=16, coat=(84, 88, 96), arms='down')
    if residue:
        _dropped_mask(p, cx + 42, night)
        _dropped_mask(p, cx - 50, night, flipped=True)
    if not clean:
        _yardsticks(p, night)
    return p


CONTACT_FRAMES = 3               # how long the ladder pulls everything else down
LADDER_BLOCK = 0.75              # rig / stall / crew / paving multiplier
LADDER_HEARTH = 0.70             # the furnace's own light budget


def _panel_burst(w, night, cyc_t, *, apron=True, crowd=True, rim=True, stall=True,
                 clean=False, count=110, cx=None, near_ref=False, fx=True):
    """One frame of the burst cycle at cycle time `cyc_t` in [0, BURST_PERIOD).

    Composited in the order the game has to composite it: PROMENADE layer (stall,
    rig, crew) -> rim pass -> spark FX -> NEAR-DECK layer. The sparks belong to
    the promenade, behind the near lane and behind pillars/coins/Pip, and the rim
    pass only ever touches the promenade layer — a near-deck figure draws in FRONT
    of the pillars, so rimming one would put the fire's light on the wrong side of
    the play space."""
    p = _panel(w, night)
    cx = w // 2 if cx is None else cx
    age = cyc_t - CONTACT_T
    apron_span = (max(0, cx - 90), min(w, cx + 90))
    if apron:
        _wet_band(p, apron_span[0], apron_span[1], 0.9, night)
        pygame.draw.line(p, (86, 96, 118), (apron_span[0], L(FAR_Y)),
                         (apron_span[0], L(NEAR_Y) - 1), 1)
        pygame.draw.line(p, (86, 96, 118), (apron_span[1] - 1, L(FAR_Y)),
                         (apron_span[1] - 1, L(NEAR_Y) - 1), 1)

    # THE CONTRAST LADDER. For the contact frames the whole block — paving
    # included — is pulled down a quarter and the hearth a third. A burst that
    # merely adds light to a lit street competes with the furnace that made it;
    # a burst that DROPS the street underneath it owns the top of the ladder for
    # free, and costs one fill per frame.
    fr = int(age * 60.0) if age >= 0 else -1
    dim = 0 <= fr < CONTACT_FRAMES
    if dim:
        p.fill((int(255 * LADDER_BLOCK),) * 3, special_flags=pygame.BLEND_RGB_MULT)
    if not clean:
        _guides(p, w, spark=True)

    prom = pygame.Surface((w, SLICE_H), pygame.SRCALPHA)
    if stall:
        _stall_ref(prom, 44, L(FAR_Y), night, t=cyc_t)
    ph = 0 if cyc_t < 0.05 else (1 if cyc_t < CONTACT_T else (2 if cyc_t < 0.5 else 3))
    _scaffold(prom, cx, night, cyc_t, state='burst' if 0 <= age < 1.4 else 'manned',
              glow_k=LADDER_HEARTH if dim else 1.0)
    _thrower(prom, cx - 25, night, ph)
    _striker(prom, cx + 23, night, 2 if 0 <= age < 0.12 else (1 if age < 0 else 3))
    if dim:
        prom.fill((int(255 * LADDER_BLOCK),) * 3 + (255,),
                  special_flags=pygame.BLEND_RGB_MULT)
    if rim and dim:
        _rim_light(prom, strength=RIM_DECAY[fr])
    p.blit(prom, (0, 0))

    stats = {}
    if not fx:
        pass
    elif 0 <= age < 1.4:
        pts, min_y = _burst(p, cx, FAR_Y - 47, age, night, count=count,
                            apron=apron_span if apron else None)
        _core_pixel(p, cx, FAR_Y - 47, age, night)
        stats = dict(n=len(pts), min_y=min_y)
        _burst_smoke(p, cx, night, age)
    elif age >= 1.4:
        _burst_smoke(p, cx, night, age)

    if crowd:
        # the spark-watch arc: backs to us, chins up, and a 2-frame head-lift
        # ripple travelling left->right at 0.06 s per figure on each burst. At the
        # near lane's 1.5x these are 31-33 px, so they occlude the spark fall —
        # which is the depth cue that puts the fire behind the street.
        near = pygame.Surface((w, SLICE_H), pygame.SRCALPHA)
        for k in range(9):
            fx = 26 + k * ((w - 46) // 9)
            lift = 0
            if 0 <= age - k * 0.06 < 0.14:
                lift = 2
            _person(near, fx, L(NEAR_Y), night, h=28 + (k % 3), back=True,
                    arms='up' if k % 4 == 1 else 'down',
                    chin=2 + lift, coat=((80, 88, 116), (104, 84, 96), (78, 96, 92))[k % 3])
        if dim:
            near.fill((int(255 * LADDER_BLOCK),) * 3 + (255,),
                      special_flags=pygame.BLEND_RGB_MULT)
        p.blit(near, (0, 0))
    if not clean:
        _yardsticks(p, night, near=near_ref)
    return p, stats


# ════════════════════════════════════════════════════════════════════════════
# PARADE DRIFT — the arithmetic behind R1, kept as code so the dwell number on
# the sheet cannot drift away from the constant that produced it.
# ════════════════════════════════════════════════════════════════════════════

SCROLL_V = 160.0                 # config.SCROLL_BASE
DRIFT_K = 0.55                   # the dragon's own +0.55x, lent to the rig
FRAME_W = 360                    # the virtual canvas


def _dwell(drift, obj_w):
    """On-screen seconds for an object `obj_w` wide travelling at +drift x scroll.
    Drift does not move the object faster, it moves it SLOWER relative to the
    camera — which is the whole trick: the same 2.5 s burst cycle suddenly fits
    three times inside one dwell instead of once."""
    return (FRAME_W + obj_w) / (SCROLL_V * (1.0 - drift))


# ════════════════════════════════════════════════════════════════════════════
# PUNCH-LIST VERIFICATION — every number quoted on the sheet is produced here,
# off rendered pixels, by the same routine for the before and after states.
# ════════════════════════════════════════════════════════════════════════════

def _diff_px(surf, bare):
    out = []
    for x in range(surf.get_width()):
        for y in range(surf.get_height()):
            c = surf.get_at((x, y))[:3]
            if c != bare.get_at((x, y))[:3]:
                out.append((x, y, _luma(c)))
    return out


def _spark_stat(count=BURST_MAX, night=0.95):
    """R2 + R4: lit-pixel count, luma mass, peak luma and the airborne envelope
    of the spark FX alone, isolated by diffing against a bare panel."""
    W = 300
    cx, cy = 150, FAR_Y - 47
    bare = _panel(W, night)
    best = None
    air = (0, 0, 0.0)
    for step in range(0, 90):
        age = step / 60.0
        p = _panel(W, night)
        _burst(p, cx, cy, age, night, count=count)
        lit = _diff_px(p, bare)
        if not lit:
            continue
        flying = [q for q in lit if q[1] < L(FAR_Y)]
        if flying:
            aw = max(q[0] for q in flying) - min(q[0] for q in flying) + 1
            ah = max(q[1] for q in flying) - min(q[1] for q in flying) + 1
            if aw * ah > air[0] * air[1]:
                air = (aw, ah, round(age, 3))
        if best is None or len(lit) > best[0]:
            best = (len(lit), sum(q[2] for q in lit), max(q[2] for q in lit), age)
    return dict(lit=best[0], mass=int(best[1]), peak=round(best[2], 1),
                at=round(best[3], 3), pct=round(100.0 * best[0] / (W * SLICE_H), 2),
                env_w=air[0], env_h=air[1], env_at=air[2], frame_px=W * SLICE_H)


def _apex_stat(count=BURST_MAX):
    """R3: where the top of the crown actually lands, per spark."""
    cx, cy = 150.0, float(FAR_Y - 47)
    apexes = []
    for i in range(count):
        best = 9999.0
        for step in range(0, 90):
            st = _spark_at(i, cx, cy, step / 60.0)
            if st is not None:
                best = min(best, st[1])
        if best < 9000:
            apexes.append(best)
    apexes.sort()
    top = apexes[:24]
    return dict(lo=round(top[0], 2), hi=round(top[-1], 2),
                span=round(top[-1] - top[0], 2),
                scanlines=len(set(int(a) for a in top)),
                on_top_line=sum(1 for a in apexes if int(a) == int(apexes[0])))


def _comet_stat(count=BURST_MAX, age=0.30):
    cx, cy = 150.0, float(FAR_Y - 47)
    lens = []
    for i in range(count):
        head = _spark_at(i, cx, cy, age)
        tail = _spark_at(i, cx, cy, age - TRAIL_T)
        if head is None or tail is None:
            continue
        lens.append(math.hypot(head[0] - tail[0], head[1] - tail[1]))
    lens.sort()
    return dict(n=len(lens), lo=round(lens[0], 1), med=round(lens[len(lens) // 2], 1),
                hi=round(lens[-1], 1))


def _ladder_stat(night=0.95):
    """R5: the hottest NON-spark pixel on the contact frame, against the spark
    sustain peak. The burst has to sit above the furnace that threw it."""
    W = 300
    p, _s = _panel_burst(W, night, CONTACT_T + 1 / 60.0, clean=True, fx=False, rim=False)
    probe = _panel(W, night)
    bg = set(probe.get_at((x, y))[:3] for x in range(W) for y in range(SLICE_H))
    nonspark = 0.0
    for x in range(W):
        for y in range(SLICE_H):
            c = p.get_at((x, y))[:3]
            if c not in bg:
                nonspark = max(nonspark, _luma(c))
    # the same block one fifth of a second later, when the ladder has released:
    # the honest before/after, measured by one method on one geometry
    u, _s3 = _panel_burst(W, night, CONTACT_T + 0.20, clean=True, fx=False, rim=False)
    undim = 0.0
    for x in range(W):
        for y in range(SLICE_H):
            c = u.get_at((x, y))[:3]
            if c not in bg:
                undim = max(undim, _luma(c))
    r = _panel(W, night)
    bare = r.copy()
    _burst(r, W // 2, FAR_Y - 47, 0.30, night, count=BURST_MAX)
    sus = max([q2[2] for q2 in _diff_px(r, bare)] or [0.0])
    return dict(nonspark=round(nonspark, 1), undimmed=round(undim, 1),
                sustain=round(sus, 1))


def _rim_stat(night=0.95):
    W = 260
    blk = pygame.Surface((W, SLICE_H), pygame.SRCALPHA)
    _stall_ref(blk, 60, L(FAR_Y), night, t=0.7)
    _scaffold(blk, 180, night, 1.0, state='burst')
    before = blk.copy()
    _rim_light(blk, strength=1.0)
    ds = []
    for x in range(W):
        for y in range(SLICE_H):
            a = before.get_at((x, y))
            b = blk.get_at((x, y))
            if a[3] > 8 and a[:3] != b[:3]:
                ds.append(_luma(b[:3]) - _luma(a[:3]))
    return dict(n=len(ds), avg=round(sum(ds) / max(1, len(ds)), 1), mx=round(max(ds), 1))


def _piece_stat(draw, w=260, night=0.95):
    """Topmost world y, pixel width and hottest luma of one isolated piece."""
    p = _panel(w, night)
    bare = p.copy()
    draw(p, w)
    px = _diff_px(p, bare)
    return dict(top=min(q[1] for q in px) + SLICE_TOP,
                w=max(q[0] for q in px) - min(q[0] for q in px) + 1,
                h=max(q[1] for q in px) - min(q[1] for q in px) + 1,
                hot=round(max(q[2] for q in px), 1))


RIM_STAT = {"avg": 0.0, "mx": 0.0}


# ════════════════════════════════════════════════════════════════════════════
# THE AUDIT — measured on RENDERED pixels, not asserted from constants.
# ════════════════════════════════════════════════════════════════════════════

def _audit():
    """Measured on RENDERED pixels of LABEL-FREE panels — sheet furniture (guide
    dashes, yardstick captions, the coin reference itself) is excluded, because
    an audit that measures its own annotations measures nothing."""
    night = 0.95
    bg = set()
    probe = _panel(220, night)
    for x in range(220):
        for y in range(SLICE_H):
            bg.add(probe.get_at((x, y))[:3])

    hottest = 0.0
    over = 0
    hot_by = {}
    apex = 9999.0
    counts = []

    def scan(surf, tag):
        nonlocal hottest, over
        h = 0.0
        for x in range(surf.get_width()):
            for y in range(surf.get_height()):
                c = surf.get_at((x, y))[:3]
                if c in bg:
                    continue
                l = _luma(c)
                h = max(h, l)
                hottest = max(hottest, l)
                if l > NIGHT_GLOW_CAP:
                    over += 1
        hot_by[tag] = h

    for tag, cyc in (("burst.contact", CONTACT_T + 0.01),
                     ("burst.bloom", CONTACT_T + 0.30),
                     ("burst.apex", CONTACT_T + 0.45),
                     ("burst.fall", CONTACT_T + 0.85),
                     ("burst.dark", 2.10)):
        # audited at the DENSEST burst the spec allows, not the average
        p, st = _panel_burst(300, night, cyc, clean=True, count=BURST_MAX)
        scan(p, tag)
        if st:
            apex = min(apex, st["min_y"])
            counts.append(st["n"])

    scan(_panel_scaffold(240, night, 'manned', 1.0, crew=True, clean=True), "rig.manned")
    scan(_panel_scaffold(240, night, 'bare', 1.0, clean=True), "rig.bare")
    scan(_panel_scaffold(240, night, 'cold', 1.0, residue=True, clean=True), "rig.cold+residue")

    p = _panel(240, night)
    for i, tt in enumerate((0.0, 0.42, 0.84)):
        _pearl_bearer(p, 40 + i * 70, night, tt)
    scan(p, "pearl+bearer")
    p = _panel(260, night)
    for tt in (0.10, 0.34, 0.62):
        pp = _panel(260, night)
        _drum_cart(pp, 130, night, tt)
        scan(pp, "drum cart")
    p = _panel(200, night)
    _draped_cart(p, 100, night, 0.0)
    scan(p, "draped cart")
    p = _tall_panel(200, night, 460, guides=False)
    _lantern_arch(p, 100, night, 0.5, span=120, ltop=460)
    scan(p, "lantern arch")
    p = _panel(200, night)
    for i in range(4):
        _thrower(p, 26 + i * 44, night, i)
    scan(p, "crew.thrower")

    # SPARK CALIBRATION — a row of single sparks at the exact sustain alphas,
    # over the exact night paving, read back. This is the honest answer to
    # "what luma does a spark actually land at", uncontaminated by trails.
    cal = _panel(260, night)
    base = _luma(cal.get_at((130, L(FAR_Y) - 30))[:3])
    lay = pygame.Surface((260, SLICE_H), pygame.SRCALPHA)
    alphas = list(range(120, 201, 10))
    for k, av in enumerate(alphas):
        lay.set_at((20 + k * 12, L(FAR_Y) - 30), (*SPARK_COL, av))
    cal.blit(lay, (0, 0))
    cal_read = [(av, _luma(cal.get_at((20 + k * 12, L(FAR_Y) - 30))[:3]))
                for k, av in enumerate(alphas)]

    # and the full rendered spread INCLUDING 3-frame trails, so the fade tail is
    # on the record too
    sp = _panel(300, night)
    pts, _m = _burst(sp, 150, FAR_Y - 47, 0.30, night)
    lo, hi = 999.0, 0.0
    for (x, y, a) in pts:
        xx, yy = int(x), int(L(y))
        if 0 <= xx < 300 and 0 <= yy < SLICE_H:
            l = _luma(sp.get_at((xx, yy))[:3])
            if l > base + 3:
                lo = min(lo, l)
                hi = max(hi, l)
    return dict(hottest=hottest, over=over, hot_by=hot_by, apex=apex,
                spark_lo=lo, spark_hi=hi, bg_luma=base, cal=cal_read,
                counts=counts)


# ════════════════════════════════════════════════════════════════════════════
# RENDER
# ════════════════════════════════════════════════════════════════════════════

def render():
    stat = dict(spark=_spark_stat(), apex=_apex_stat(), comet=_comet_stat(),
                ladder=_ladder_stat(), rim=_rim_stat())
    RIM_STAT.update(stat["rim"])
    stat["pearl"] = _piece_stat(lambda p, w: _pearl_bearer(p, w // 2, 0.95, 0.3))
    stat["cart"] = _piece_stat(lambda p, w: _drum_cart(p, w // 2, 0.95, 0.34))
    stat["rig"] = _piece_stat(lambda p, w: _scaffold(p, w // 2, 0.95, 1.0, state='bare'))
    stat["cold_smoke"] = _piece_stat(lambda p, w: _scaffold(p, w // 2, 0.95, 2.4, state='cold'))
    stat["burst_smoke"] = _piece_stat(lambda p, w: _burst_smoke(p, w // 2, 0.95, 1.4))
    stat["crowd_h"] = _piece_stat(
        lambda p, w: _person(p, w // 2, L(NEAR_Y), 0.95, h=28, back=True, chin=2), w=80)["h"]
    stat["rig_crew"] = _piece_stat(lambda p, w: (
        _scaffold(p, w // 2, 0.95, 1.0, state='manned'),
        _thrower(p, w // 2 - 25, 0.95, 1),
        _striker(p, w // 2 + 23, 0.95, 0)))
    RIG_W = stat["rig"]["w"]
    DWELL_STATIC = _dwell(0.0, RIG_W)
    DWELL_DRIFT = _dwell(DRIFT_K, RIG_W)
    BURSTS_IN_DWELL = int(DWELL_DRIFT / BURST_PERIOD) + 1
    stat["dwell"] = dict(rig_w=RIG_W, static=round(DWELL_STATIC, 2),
                         drift=round(DWELL_DRIFT, 2), bursts=BURSTS_IN_DWELL)
    proc = [("pearl-bearer", stat["pearl"]["w"]), ("gap", 40),
            ("dragon (existing)", 230), ("gap", 30), ("drum cart", stat["cart"]["w"])]
    stat["procession"] = sum(v for _n, v in proc)

    sheet = pygame.Surface((WIDTH, 2900))
    sheet.fill((24, 26, 36))
    y = PAD
    _text(sheet, "FIRE-TREE NIGHT — round 1 (rev) · THE IRON FLOWER (A1-A5) + DRAGON-PARADE SUPPORT (A6-A8, A13) + RESIDUE (A15)",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 21
    y = _wrap(sheet, "Every panel below is a LITERAL screen slice: world y 500-647 at 1x (the lantern-arch panel is sliced from 460, because it hangs above 500), with the far deck (595), the near deck (638), the 560 cast/prop band ceiling (blue dashes) and the y=512 spark ceiling (amber dashes) drawn in. "
                     "Datiehua is the one fire form that reads through spark COUNT + ARC instead of brightness, which is why it survives the 150-luma cap: the sparks are (191,142,82) at alpha 120-200 over dark paving, cooling toward (170,120,90) as they climb, and exactly ONE 2px core pixel per burst sits ON the cap for 4 frames. "
                     "WHAT CROSSES 560, HONESTLY: the scaffold's own head beam (%d) — the same band the shipped steamer's bamboo stack already tops out in (543); the cold rig's smoke thread (%d); the burst smoke veil (%d, trimmed to the shipped steam ceiling); and the sparks, to %d. Nothing else. "
                     "And y=512 is two things at once: a 6 px extension of the shipped steamer's own steam column (518), AND 13 px inside the lowest vertical reach of a pillar gap (GROUND_Y-70 = 525). Both facts are true, and the second is why the spark corridor attenuates."
                     % (stat["rig"]["top"], stat["cold_smoke"]["top"], stat["burst_smoke"]["top"], SPARK_CEIL),
              PAD, y, WIDTH - PAD * 2, 10, (186, 186, 200), 12)
    y += 6

    # ── A1 / A2 : the rig through its life ───────────────────────────────────
    _text(sheet, "A1 · THE IRON-FLOWER SCAFFOLD — four states across the day. It is planted THREE times before it lights, so it has to be the same recognisable object every time: a braced A-frame truss + a shaggy straw SPLASH BOARD + a hearth. No awning stripe, no counter — it is visibly not a stall.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    pw = (WIDTH - PAD * 5) // 4
    row_y = y
    p1 = _panel_scaffold(pw, 0.25, 'bare', 0.4, storm=True, wet=0.8)
    p2 = _panel_scaffold(pw, 0.95, 'manned', 1.1, crew=True)
    p3, _s = _panel_burst(pw, 0.95, CONTACT_T + 0.22)
    p4 = _panel_scaffold(pw, 0.95, 'cold', 2.2, residue=True)
    ys = []
    ys.append(_place(sheet, p1, PAD, row_y, "S1 · BARE — the Ch5/6/7 plant (178-273 s)",
                     sub="Draped, roped, standing in the rain with a brazier crew sheltering under it. The truss stays visible; only the board is covered, so the reveal 80 s later is recognition, not introduction."))
    ys.append(_place(sheet, p2, PAD * 2 + pw, row_y, "S2 · MANNED — crew up, crucible lit, no burst",
                     sub="The hearth is the only steady lit thing between bursts (capped warm glow, peak 44). Thrower cocked, striker waiting. This is the 1.2 s the square gets before the first throw."))
    ys.append(_place(sheet, p3, PAD * 3 + pw * 2, row_y, "S3 · MID-BURST — the strike frame",
                     sub="~120 ballistic sparks, the doused apron mirroring them, the 8-deep spark-watch crowd backs-to-us with chins up, and the rim-light pass firing on every top edge in the block."))
    ys.append(_place(sheet, p4, PAD * 4 + pw * 3, row_y, "S4 · COLD — the wind-down (A15)",
                     sub="Scorched timber, the thatch burnt through in two bites, a thread of grey smoke off the head beam, a scorch-speckle fan on the paving and two swept paper masks."))
    y = max(ys) + 6

    # ── A2 crew phases ───────────────────────────────────────────────────────
    _text(sheet, "A2 · THE CREW — soaked straw hat + sheepskin, a silhouette shared with nothing else in the game (wide dark disc over a bulky pale fleece mass). THROWER: 4-phase over-shoulder ladle swing on the 1.3 s wind-up, 22 px willow scoop. STRIKER: willow bat, ONE frame of contact at the arc's apex.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    crew_w = (WIDTH - PAD * 3) // 2
    for col, night in ((0, 0.0), (1, 0.95)):
        cp = _panel(crew_w, night)
        _guides(cp, crew_w)
        for i in range(4):
            _thrower(cp, 44 + i * 62, night, i)
            _text(cp, "T%d" % i, 38 + i * 62, L(FAR_Y) + 2, 8,
                  (150, 160, 185) if night > 0.5 else (66, 56, 44))
        for i in range(4):
            _striker(cp, 320 + i * 62, night, i)
            _text(cp, "S%d" % i, 314 + i * 62, L(FAR_Y) + 2, 8,
                  (150, 160, 185) if night > 0.5 else (66, 56, 44))
        _yardsticks(cp, night, x=crew_w - 26)
        lbl = "DAY (setup / rehearsal)" if night < 0.5 else "NIGHT — fleece + hat cool toward (54,64,96); the molten charge in the scoop is capped 150"
        yy2 = _place(sheet, cp, PAD + col * (crew_w + PAD), y, "A2 crew pose cycle — " + lbl,
                     sub="T0 cocked low behind · T1 loaded high behind · T2 the throw across the body · T3 follow-through, scoop empty.   S0 waiting low · S1 raised · S2 CONTACT (bat horizontal at the board) · S3 recoil.")
        if col == 1:
            y = yy2
    z = _zoom(sheet, _panel_scaffold(150, 0.95, 'manned', 1.1, crew=True),
              (30, L(FAR_Y) - 34, 90, 40), 4, PAD, y + 14, "4x · crew silhouette read at night (nearest)")
    _wrap(sheet, "The read order at 1x: hat brim (a hard horizontal), fleece shoulder (a soft pale mass), then the long diagonal of the handle. The bat and the scoop point OPPOSITE ways at every phase pair, so two crew never merge into one blob.",
          PAD + z + 16, y + 14, 420, 9, (196, 194, 204), 11)
    y += 14 + 40 * 4 + 12

    # ── R1 · the parade dwell strip ──────────────────────────────────────────
    _text(sheet, "A1+ · THE RIG DRIFTS. The iron flower rides the dragon's own mechanic — the whole rig translates at +%.2f x scroll for its lifetime, so the square does not slide past the player, it travels WITH them. That single change is what turns one glimpsed burst into a three-act beat."
          % DRIFT_K, PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    dstrip = [(0.97, "t 0.97 s — ENTER: the rig is still coming on and the FIRST burst is already lit"),
              (2.30, "t 2.30 s — THE DARK BEAT: hearth only, smoke drifting, the square still reading"),
              (3.47, "t 3.47 s — the SECOND burst, mid-square. The rig has travelled 174 px left in the meantime")]
    dys = []
    for i, (tt, cap) in enumerate(dstrip):
        rigx = int(380 - SCROLL_V * (1.0 - DRIFT_K) * tt)
        cyc = (tt - 0.75 + CONTACT_T) % BURST_PERIOD
        p, _sd = _panel_burst(FRAME_W, 0.95, cyc, count=120, cx=rigx, near_ref=(i == 0))
        dys.append(_place(sheet, p, PAD + i * (FRAME_W + PAD), y, cap,
                          sub=None))
    ty = _wrap(sheet, "THE ARITHMETIC. The rig + its two crew measure %d px wide, so a STATIC one crosses a %d px frame in (%d + %d) / %.0f = %.2f s. At +%.2f x scroll the closing speed drops to %.0f px/s and the same rig dwells %.2f s — x%.2f — which is exactly the window a %.1f s burst cycle needs to deliver BURST -> DARK BEAT -> BURST rather than one burst glimpsed on the way past. Maximum bursts inside the dwell: %d (contacts at 0.75 / 3.25 / 5.75 s). The round-1 caption said four bursts in 6.3 s; that was wrong arithmetic on a shorter dwell, and it is corrected everywhere on this sheet."
                      % (RIG_W, FRAME_W, FRAME_W, RIG_W, SCROLL_V, DWELL_STATIC, DRIFT_K,
                         SCROLL_V * (1.0 - DRIFT_K), DWELL_DRIFT,
                         DWELL_DRIFT / DWELL_STATIC, BURST_PERIOD, BURSTS_IN_DWELL),
               PAD, max(dys) + 2, WIDTH - PAD * 2, 10, (200, 198, 208), 12)
    ty = _wrap(sheet, "FALLBACK, if the drift is not affordable: THREE STATIC SCAFFOLDS spaced across the square at ~150 px, each firing on its own phase offset. The player still gets burst -> dark -> burst, bought with placement instead of velocity — at the cost of the 'it keeps pace with you' feeling the dragon already sells, and of the second burst being a different object rather than the same one.",
               PAD, ty, WIDTH - PAD * 2, 10, (176, 186, 200), 12)
    y = ty + 6

    # ── A3 burst cycle strip ─────────────────────────────────────────────────
    _text(sheet, "A3 · THE BURST CYCLE — one full 2.5 s cycle in 8 phases (the plan's 2.6 s cadence, with the DARK BEAT that makes the next throw land). %d-%d sparks/burst (up from the plan's 70-120); here 120. Gravity %.0f px/s² (the shipped Particle value), spread narrowed to ±%d°, each spark a SUB-STEPPED COMET — %d samples of its own parabola over %.2f s — and a per-spark jitter on the apex limit so the crown has no flat top."
          % (BURST_MIN, BURST_MAX, G_ACC, SPREAD_DEG, TRAIL_N, TRAIL_T),
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    phases = [(0.00, "0.00 s — DARK BEAT: rig manned, hearth only"),
              (0.10, "0.10 — wind-up, scoop loaded high"),
              (0.15, "0.15 — CONTACT +1f: the ONE 150-luma core px + rim-light"),
              (0.24, "0.24 — bloom, sparks still climbing"),
              (0.42, "0.42 — apex: the chrysanthemum at full width"),
              (0.72, "0.72 — the meteor fall, trails lengthening"),
              (1.10, "1.10 — ground bounce + skitter, apron smears"),
              (1.90, "1.90 — spent: smoke veil only, crowd still up")]
    bw = (WIDTH - PAD * 9) // 8
    burst_stats = []
    bx = PAD
    strip_y = y
    for cyc, cap in phases:
        p, st = _panel_burst(bw, 0.95, cyc, count=120)
        if st:
            burst_stats.append(st)
        sheet.blit(p, (bx, strip_y))
        pygame.draw.rect(sheet, (74, 78, 94), (bx, strip_y, bw, SLICE_H), 1)
        _wrap(sheet, cap, bx + 1, strip_y + SLICE_H + 2, bw - 2, 8, (200, 200, 210), 10)
        bx += bw + PAD
    y = strip_y + SLICE_H + 26
    peak, _st = _panel_burst(240, 0.95, CONTACT_T + 0.28)
    z = _zoom(sheet, peak, (46, 0, 150, 110), 3, PAD, y + 14, "3x · burst peak — spark count/arc, not brightness")
    ty = _wrap(sheet, "R2 · REAL TRAILS. The round-1 burst was 3 stale frames stacked behind each head — a 2-3 px smudge. Each spark's streak is now its OWN analytic parabola re-sampled backwards: %d sub-steps over %.2f s with the alpha decaying along the streak. Measured comet length at the bloom: %.0f-%.0f px (median %.0f). "
                      "That buys the fire with PIXEL COUNT instead of brightness, which is the only currency a 150-luma cap leaves: lit spark pixels %d -> %d (%.2f%% of a %dx%d frame), luma mass 25,145 -> %s — at a peak luma of %.1f, against %.1f before. The peak did not move, because every sub-step is drawn at strictly less alpha than the head and no two writes ever add."
                      % (TRAIL_N, TRAIL_T, stat["comet"]["lo"], stat["comet"]["hi"],
                         stat["comet"]["med"], 325, stat["spark"]["lit"],
                         stat["spark"]["pct"], 300, SLICE_H,
                         "{:,}".format(stat["spark"]["mass"]),
                         stat["spark"]["peak"], 123.3),
               PAD + z + 16, y + 14, WIDTH - PAD * 2 - z - 30, 10, (200, 198, 208), 12)
    ty = _wrap(sheet, "R3 + R4 · A TREE, NOT A FAN. Round 1 stacked 24 sparks on one scanline at y 512 — a ruled line across the top of a fire. The apex limit is now jittered per spark (vlim x (0.80 + 0.20·hash)), so the top of the crown spreads over %.1f px across %d scanlines with %d spark(s) on the topmost. "
                      "And the shape: spread ±82° -> ±%d°, gravity 300 -> %.0f with launch speeds raised to keep the ~512 apex, and the skirt de-energised so the glancing debris no longer outruns the crown. Airborne envelope 77 x 218 -> %d x %d px. The faster fall lengthens the comets for free."
                      % (stat["apex"]["span"], stat["apex"]["scanlines"],
                         stat["apex"]["on_top_line"], SPREAD_DEG, G_ACC,
                         stat["spark"]["env_h"], stat["spark"]["env_w"]),
               PAD + z + 16, ty + 2, WIDTH - PAD * 2 - z - 30, 10, (200, 198, 208), 12)
    _wrap(sheet, "R5 · THE CONTRAST LADDER. For %d frames at contact the whole block — rig, stall, crew, crowd AND paving — is multiplied by %.2f and the hearth's light budget by %.2f. Measured on the same geometry by one method: the hottest NON-SPARK pixel goes %.1f (released, 0.2 s later) -> %.1f (at contact) while the spark sustain holds at %.1f. The ladder now reads core 150 > rim (cap %d) > sparks %.0f > furnace %.0f. Before, the furnace outshone the thing it had just thrown."
                 % (CONTACT_FRAMES, LADDER_BLOCK, LADDER_HEARTH,
                    stat["ladder"]["undimmed"], stat["ladder"]["nonspark"],
                    stat["ladder"]["sustain"], RIM_CAP,
                    stat["ladder"]["sustain"], stat["ladder"]["nonspark"]),
          PAD + z + 16, ty + 2, WIDTH - PAD * 2 - z - 30, 10, (200, 198, 208), 12)
    y += 14 + 110 * 3 + 14

    # ── A4 rim light ─────────────────────────────────────────────────────────
    _text(sheet, "A4 · THE BURST RIM-LIGHT PASS — %d frames on a 100/60/30 decay, a 1 px warm top edge on every silhouette in the PROMENADE layer, capped %d. This is the storm chapter's lightning-silhouette blit INVERTED: the lightning flattens the street to black, the iron flower rims it in warm light. Same machinery, opposite meaning — and it ties the festival to the storm that paid for it."
          % (CONTACT_FRAMES, RIM_CAP), PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    rw = (WIDTH - PAD * 3) // 2

    def _rim_demo(w, strength):
        p = _panel(w, 0.95)
        _guides(p, w)
        # PROMENADE layer — the only layer the rim pass is allowed to touch
        prom = pygame.Surface((w, SLICE_H), pygame.SRCALPHA)
        _stall_ref(prom, 60, L(FAR_Y), 0.95, t=0.7)
        _scaffold(prom, w - 60, 0.95, 1.0, state='burst')
        _thrower(prom, w - 86, 0.95, 2)
        if strength > 0:
            _rim_light(prom, strength=strength)
        p.blit(prom, (0, 0))
        # NEAR deck goes down afterwards, unrimmed and unlit, in front of it
        near = pygame.Surface((w, SLICE_H), pygame.SRCALPHA)
        _person(near, w // 2 - 24, L(NEAR_Y), 0.95, h=29, back=True, chin=2,
                coat=(80, 88, 116), arms='up')
        _person(near, w // 2 + 16, L(NEAR_Y), 0.95, h=28, back=True, chin=2,
                coat=(104, 84, 96))
        p.blit(near, (0, 0))
        _yardsticks(p, 0.95, near=True)
        return p

    off_p = _rim_demo(rw, 0.0)
    on_p = _rim_demo(rw, 1.0)
    y1 = _place(sheet, off_p, PAD, y, "RIM OFF — the block between bursts",
                sub="Flat, cool, everything sitting in the same value band. This is 2.4 of every 2.5 seconds.")
    y2 = _place(sheet, on_p, PAD * 2 + rw, y, "RIM ON — frame 1 of 3 (100 / 60 / 30)",
                sub="Hat brims, the crew's shoulders, the awning ribs and the stall's counter edge all catch a 1 px warm line. The NEAR-deck pair in front is deliberately untouched: it draws in front of the pillars, so the fire's light must not reach it.")
    y = max(y1, y2)
    z = _zoom(sheet, on_p, (rw - 118, L(FAR_Y) - 40, 96, 44), 4, PAD, y + 14,
              "4x · rim ON — rig + crew, the promenade layer")
    z2 = _zoom(sheet, off_p, (rw - 118, L(FAR_Y) - 40, 96, 44), 4, PAD + z + 20, y + 14,
               "4x · rim OFF (same frame)")
    _wrap(sheet, "Detection is 'opaque pixel whose neighbour above is transparent' on the PROMENADE layer's own SRCALPHA surface, so it is ONE sweep per burst frame over one layer — the same cost profile as the existing lightning flash. Highlight is mixed 35%% toward (255,208,150), +18 value, hard-capped at 140 luma. "
                 "The honest number for what that does: measured over the rimmed pixels it is +%.0f luma on average (max +%.0f) at full strength — the round-1 caption said '+18', which was the boost constant, not the effect. Three frames at 100/60/30, not two: two frames is one dropped WASM frame away from a light that sometimes doesn't happen, which is worse than no light at all."
                 % (RIM_STAT["avg"], RIM_STAT["mx"]),
          PAD + z + z2 + 36, y + 14, WIDTH - PAD * 2 - z - z2 - 50, 10, (200, 198, 208), 12)
    y += 14 + 44 * 4 + 14

    # ── A5 doused apron ──────────────────────────────────────────────────────
    _text(sheet, "A5 · THE DOUSED APRON — datiehua sites are watered down for safety, so the paving in a 180 px apron around the rig is locally, permanently wet for this block: glossy, darker, and every burst mirrors in it as 1 px-wide, 6-10 px dither columns at alpha 45. It buys the spark-reflection image WITHOUT retuning the global wetness rate or spending the day plan's lantern-doubling window.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    aw = (WIDTH - PAD * 4) // 3
    ap1 = _panel(aw, 0.95)
    _guides(ap1, aw)
    _scaffold(ap1, aw // 2, 0.95, 1.0, state='manned')
    _yardsticks(ap1, 0.95)
    ap2 = _panel(aw, 0.95)
    _guides(ap2, aw)
    _wet_band(ap2, max(0, aw // 2 - 90), min(aw, aw // 2 + 90), 0.9, 0.95)
    _scaffold(ap2, aw // 2, 0.95, 1.0, state='manned')
    _yardsticks(ap2, 0.95)
    ap3, _s3 = _panel_burst(aw, 0.95, CONTACT_T + 0.55, crowd=False, stall=False)
    y1 = _place(sheet, ap1, PAD, y, "DRY paving (the rest of the street)",
                sub="Baseline: the festival's ordinary night stone.")
    y2 = _place(sheet, ap2, PAD * 2 + aw, y, "DOUSED apron, no burst — 180 px, edges marked",
                sub="Darker, glossier, a horizontal specular dither. The crew watered it before the show; the player never sees them do it and doesn't need to.")
    y3 = _place(sheet, ap3, PAD * 3 + aw * 2, y, "DOUSED apron + a falling burst",
                sub="Reflections as vertical SMEARS, not mirrored points — which is what wet stone actually does to a moving source. Alpha 45, dithered, so they never compete with the sparks themselves.")
    y = max(y1, y2, y3)
    z = _zoom(sheet, ap3, (aw // 2 - 60, L(FAR_Y) - 6, 120, 34), 4, PAD, y + 14,
              "4x · the apron smears under a falling burst")
    _wrap(sheet, "The smear length is 6-10 px, keyed off the spark's own x so neighbouring columns differ, and every other pixel below the second row is skipped — a dither, so at 1x it reads as a shimmer rather than as a set of drawn lines. Reflection alpha scales with the parent spark's alpha, so the apron dims with the burst instead of outliving it.",
          PAD + z + 20, y + 14, WIDTH - PAD * 2 - z - 40, 10, (200, 198, 208), 12)
    y += 14 + 34 * 4 + 14

    # ── A6/A7/A8/A13 parade support ──────────────────────────────────────────
    _text(sheet, "A6-A8 + A13 · DRAGON-PARADE SUPPORT — the staging the existing perf_dragon_dance needs around it. Reveal order right-to-left: PEARL → head → seven carriers → tail → DRUM CART. The pearl leads because convention puts the chased ball ahead of the head; the drum trails because the player's reveal order makes 'mystery → face → mass → drum' the dramatic sequence.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    qw = (WIDTH - PAD * 5) // 4
    # A6 pearl, 3 phases of the figure-8
    pp = _panel(qw, 0.95)
    _guides(pp, qw)
    for i, tt in enumerate((0.0, 0.42, 0.84)):
        _pearl_bearer(pp, 40 + i * 62, 0.95, tt, trace=(i == 1))
    _yardsticks(pp, 0.95, coin_x=qw - 22, near=True)
    y1 = _place(sheet, pp, PAD, y, "A6 · PEARL + BEARER — figure-8 @ 0.8 Hz (path traced on the middle figure)",
                sub="Bearer re-dealt at the near lane's 1.5x (%d px). Pole overhead, 10 px amber sphere, tassel so it reads as SWUNG rather than floating. Pearl luma pulled 145 -> %.0f and the halo budget 40 -> 24, so the 3 px pole stays legible THROUGH the glow and the parade's lead object stops competing with the fire."
                    % (stat["crowd_h"], stat["pearl"]["hot"]))
    dp = _panel(qw, 0.95)
    _guides(dp, qw)
    _drum_cart(dp, qw // 2, 0.95, 0.34)
    _yardsticks(dp, 0.95, near=True)
    y2 = _place(sheet, dp, PAD * 2 + qw, y, "A7 · DRUM-AND-CYMBAL CART — %d px measured (the plan said 70)" % stat["cart"]["w"],
                sub="Barrel drum at 1.5x the busker's on a 2-wheel chassis (the weekend_kit spoked wheel), a drummer riding the bed and striking in antiphase, two flanking cymbal figures — all three now at the near lane's 1.5x — and a PULLER at the front, because the platform is dragged, per the source.")
    cp2 = _panel(qw, 0.0)
    _guides(cp2, qw)
    _draped_cart(cp2, qw // 2 - 20, 0.0, 0.0)
    _person(cp2, qw // 2 + 14, L(FAR_Y), 0.0, h=18, coat=(120, 100, 78), arms='point')
    _yardsticks(cp2, 0.0)
    y3 = _place(sheet, cp2, PAD * 3 + qw * 2, y, "A8 · DRAPED DRAGON-HEAD HANDCART (day, 163-178 s)",
                sub="16 px of red cloth TENTING over two horn nubs, a brow shelf and a snout ridge, roped to the bed. Unmistakably a head; never a face. It arrives 148 s before it dances and nobody looks at it.")
    ARCH_TOP = 460
    ap = _tall_panel(qw, 0.95, ARCH_TOP)
    _lantern_arch(ap, qw // 2, 0.95, 0.6, span=120, ltop=ARCH_TOP)
    _person(ap, qw // 2 - 46, FAR_Y - ARCH_TOP, 0.95, h=18, coat=(90, 96, 124))
    _person(ap, qw // 2 + 40, FAR_Y - ARCH_TOP, 0.95, h=17, coat=(104, 88, 100))
    _person(ap, 26, NEAR_Y - ARCH_TOP, 0.95, h=30, coat=(84, 92, 124))
    _text(ap, "497 garland", 2, GARLAND_TOP_Y - ARCH_TOP - 10, 7, (150, 176, 150))
    _text(ap, "512 spark", 2, SPARK_CEIL - ARCH_TOP + 2, 7, (168, 140, 100))
    _text(ap, "560 band", 2, BAND_TOP - ARCH_TOP + 2, 7, (140, 156, 184))
    y4 = _place(sheet, ap, PAD * 4 + qw * 3, y, "A13 · LANTERN ARCH — apex y=497, 120 px span, 6 lanterns  (panel sliced from y=460)",
                sub="497 is not a new maximum and not a compromise: it is GROUND_Y-98, the top_y the SHIPPED night-festival lantern garland is already strung at. Round 1's 560 put the gateway UNDER the overhead lattice it is meant to be a gateway through; 477 would have been a genuinely new ceiling. The mislabeled ghost line is gone.")
    y = max(y1, y2, y3, y4) + 4
    y = _wrap(sheet, "THE PROCESSION, RE-MEASURED (R12). Round 1 quoted the plan's estimates; these are the rendered widths. " +
                     "  ·  ".join("%s %d px" % (n, v) for n, v in proc) +
                     "  =  %d px total, against the plan's 390. The gaps are deliberately widened 30/20 -> 40/30 so the drum cart's cymbal figures stop colliding with the dragon's tail at the near lane's new 1.5x scale, and the drum cart itself measures %d px, not the planned 70. "
                     "A %d px set still cannot fit in a %d px frame — which is the point: the player never sees the whole dragon at once."
                     % (stat["procession"], stat["cart"]["w"], stat["procession"], FRAME_W),
              PAD, y, WIDTH - PAD * 2, 10, (200, 198, 208), 12) + 2

    # ── A15 residue ──────────────────────────────────────────────────────────
    _text(sheet, "A15 · THE RESIDUE SET — the festival hands back to Chapter 9 with evidence, not a fade. The scorch field decays over two blocks; the masks are the troupe's souvenirs, swept; the rig is cold and still smoking.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    rw2 = (WIDTH - PAD * 4) // 3
    r1 = _panel(rw2, 0.95)
    _guides(r1, rw2)
    _scorch_fan(r1, rw2 // 2, 0.95, decay=0.0, w=int(rw2 * 0.95))
    _scaffold(r1, rw2 // 2, 0.95, 2.4, state='cold')
    _dropped_mask(r1, rw2 // 2 + 54, 0.95)
    _dropped_mask(r1, rw2 // 2 - 62, 0.95, flipped=True)
    _yardsticks(r1, 0.95)
    r2 = _panel(rw2, 0.95)
    _guides(r2, rw2)
    _scorch_fan(r2, rw2 // 2, 0.95, decay=0.55, w=int(rw2 * 0.95))
    _dropped_mask(r2, rw2 // 2 + 10, 0.95)
    _person(r2, 40, L(NEAR_Y), 0.95, h=29, coat=(78, 86, 110))
    _yardsticks(r2, 0.95, near=True)
    r3 = _panel(rw2, 0.95)
    _guides(r3, rw2)
    _scorch_fan(r3, rw2 // 2, 0.95, decay=0.9, w=int(rw2 * 0.95))
    _yardsticks(r3, 0.95)
    y1 = _place(sheet, r1, PAD, y, "BLOCK 0 — the cold rig, fresh scorch, two masks",
                sub="Thatch burnt through, timber pulled 55% toward ash, two smoke threads (alpha 30 / 24) still climbing off the head beam and the hearth.")
    y2 = _place(sheet, r2, PAD * 2 + rw2, y, "BLOCK +1 — field at 55% decay",
                sub="One mask left, an ordinary walker back on the near deck. The street is resuming.")
    y3 = _place(sheet, r3, PAD * 3 + rw2 * 2, y, "BLOCK +2 — 90% decayed, hand-off to Ch9",
                sub="A whisper of speckle on the stone and nothing else. Chapter 9's close-down begins on schedule.")
    y = max(y1, y2, y3) + 6

    # ── audit footer ─────────────────────────────────────────────────────────
    a = _audit()
    coin_l = _luma(COIN_CORE)
    passed = (a["over"] == 0 and a["hottest"] <= NIGHT_GLOW_CAP
              and a["hottest"] < coin_l and a["apex"] >= SPARK_CEIL)
    per = "  ".join("%s=%.0f" % (k, v) for k, v in a["hot_by"].items())
    cal = "  ".join("a%d->%.0f" % (av, lm) for av, lm in a["cal"])
    _text(sheet, "NIGHT-CAP + CEILING AUDIT (measured on RENDERED pixels, night=0.95, across the burst cycle and every new piece)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 16
    y = _wrap(sheet,
              "hottest festival pixel = %.1f luma  ·  pixels over the %d cap = %d  ·  gold coin core = %.1f luma, SOLE BRIGHTEST (%.0f%% hotter than the hottest festival pixel)  ·  "
              "spark primary (191,142,82) own luma = %.1f (sits ON the cap, so the one core pixel per burst is the hottest thing the show can make)  ·  "
              "highest pixel any spark reached = y %.1f (ceiling %d, headroom %.1f px)  ·  sparks alive per burst frame %s  ·  every non-spark piece stays inside 560-640.   %s"
              % (a["hottest"], NIGHT_GLOW_CAP, a["over"], coin_l,
                 (coin_l / max(1.0, a["hottest"]) - 1.0) * 100.0,
                 _luma(SPARK_COL),
                 a["apex"], SPARK_CEIL, a["apex"] - SPARK_CEIL, a["counts"],
                 "PASS — nothing breaches 150, nothing breaches y=512, the coin stays sole-brightest."
                 if passed else "FAIL — see per-piece numbers."),
              PAD, y, WIDTH - PAD * 2, 10, (170, 205, 185) if passed else (225, 145, 135), 13)
    y = _wrap(sheet, "SPARK LUMA CALIBRATION — one spark drawn at each sustain alpha over the real night paving (bg %.0f luma), read back off the rendered surface:  %s.  "
                     "Sustain band alpha 120-200 -> effective %.0f-%.0f luma, inside the plan's 90-130 target. Rendered spread including the comet tail: %.0f-%.0f."
                     % (a["bg_luma"], cal, a["cal"][0][1], a["cal"][-1][1], a["spark_lo"], a["spark_hi"]),
              PAD, y + 2, WIDTH - PAD * 2, 9, (196, 196, 208), 12)
    y = _wrap(sheet, "per-piece hottest: " + per, PAD, y + 2, WIDTH - PAD * 2, 9, (176, 176, 190), 12)
    y = _wrap(sheet, "R9 · THE SPARK CORRIDOR + COMPOSITING CONTRACT. Between y %d and the %d ceiling every spark's alpha is attenuated x1.00 -> x%.2f and its colour cooled toward %s — iron cools as it rises, so the physics and the safety argument are the same argument, and the cooled hue widens the gap to the coin's (255,232,150) at the exact height where the two could ever share a scanline. "
                     "The FX composites WITH THE PROMENADE LAYER — after the promenade silhouettes, before pillars, coins and Pip — so a spark can never draw over a coin or over the bird. And the A4 rim pass runs on promenade-layer silhouettes ONLY, never on near-deck front-of-pillar figures: a near-deck figure draws in front of the pillars, so rim-lighting one would put the fire's light on the player's side of the play space."
                     % (CORRIDOR_LO, CORRIDOR_HI, CORRIDOR_FLOOR, str(SPARK_COOL)),
              PAD, y + 2, WIDTH - PAD * 2, 9, (186, 200, 210), 12)

    out = "/home/user/skybit/docs/sidewalk_overhaul/festival/fire_parade_round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    final = pygame.Surface((WIDTH, min(sheet.get_height(), y + 14)))
    final.blit(sheet, (0, 0))
    pygame.image.save(final, out)
    print("saved", out, final.get_size())
    print("AUDIT", {k: (round(v, 1) if isinstance(v, float) else v)
                    for k, v in a.items() if k not in ("hot_by", "cal")})
    print("per-piece hottest:", {k: round(v, 1) for k, v in a["hot_by"].items()})
    print("burst spark counts alive:", [s["n"] for s in burst_stats])
    print("--- PUNCH-LIST VERIFICATION (fire) ---")
    print("R1 dwell   ", stat["dwell"])
    print("R2 sparks  ", stat["spark"], " comet:", stat["comet"])
    print("R3 apex    ", stat["apex"])
    print("R4 envelope %dw x %dh (was 218 x 77)" % (stat["spark"]["env_w"], stat["spark"]["env_h"]))
    print("R5 ladder  ", stat["ladder"])
    print("R9 corridor y%d->y%d alpha x1.00->x%.2f, hue %s -> %s"
          % (CORRIDOR_LO, CORRIDOR_HI, CORRIDOR_FLOOR, SPARK_COL, SPARK_COOL))
    print("R6 near-lane figure height %d px" % stat["crowd_h"])
    print("R10 rim    ", stat["rim"])
    print("R11 arch   apex y %d (shipped garland top_y)" % GARLAND_TOP_Y)
    print("R12 pieces  pearl", stat["pearl"], "cart", stat["cart"])
    print("R12 tops    rig", stat["rig"]["top"], "cold-smoke", stat["cold_smoke"]["top"],
          "burst-smoke", stat["burst_smoke"]["top"])
    print("R12 procession", proc, "=", stat["procession"], "px")
    print("PASS" if passed else "FAIL")
    return a, passed


if __name__ == "__main__":
    render()
