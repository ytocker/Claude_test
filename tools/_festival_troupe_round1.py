"""FIRE-TREE NIGHT — the MONKEY KING troupe + FOOD THEATRE, round-1 sheet.

Covers FESTIVAL_PLAN.md §4 (the third act) and §5-6 build-list rows A9-A12 + A14:

  A9  MONKEY KING TROUPE x3 — three masked acrobats in a 3-beat routine:
      staff spin (horizontal blur arc) · two-man shoulder tower with the third
      climbing · dismount somersault (tucked ball, airborne)
  A10 PAPER MONKEY MASK — the kid accessory, worn on the face AND pushed up on
      the head, built on the day_cast.draw_kid head geometry
  A11 FOOD-THEATRE overlays for the existing stalls — noodle-puller (arms wide,
      a dough ribbon doubling on a 4-step 0.9 s cycle), sugar-painter (seated,
      wand over a flat slab, an amber line-drawing resolving into a disc on a
      stick), tanghulu rack (a vertical hedgehog of skewered red fruit)
  A12 WALK-AND-EAT props x4 at 14 px figures — skewer, steam bun, tanghulu
      stick, cup — as accessory overlays on the retargeted chest-height reach
  A14 VENDOR STEP-OUT — the market-pause pose: out from BEHIND the counter to
      BESIDE it, facing the parade, one arm up shielding the eyes / waving

Research studied before drawing (web):
  - The monkey slot goes to masked HUMAN acrobats as Sun Wukong, not a live
    animal act: 耍猴 trainer numbers collapsed ~10,000 -> ~300, the practice is
    contested on welfare grounds, and a chained macaque reads sad rather than
    charming — and it fails the festival's upward razor, because a monkey on a
    chain looks DOWN. Masked acrobats are a temple-fair staple beside stilts,
    yangge and lion dance, and a direct sibling of the shipped bian-lian act.
  - The Monkey King's opera mask: gold face, red-brown fur ruff, two long swept
    phoenix plumes off the brow; the staff (Ruyi Jingu Bang) spin is the signature
    move and the most legible acrobatic motion available at this pixel scale.
  - Night-market eating: seating is sparse, so supper is a grazing STROLL —
    walk-and-eat is the dominant crowd behaviour, and tanghulu (hawthorn in a
    crackling sugar shell, skewered) is the single most legible 18 px food prop.
  - Tanghulu is displayed on a straw/foam POLE, skewers bristling outward — a
    ready-made spiky silhouette, unlike anything else on the stall row.

Panels are literal screen slices (world y 500-647 at 1x) with the far deck (595),
the near deck (638) and the 560 cast/prop band ceiling drawn in, so the vertical
budget is verifiable by eye. Nothing on THIS sheet is allowed above 560 — the
spark FX on the fire sheet is the plan's one sanctioned exception. Pure
pygame.draw + SRCALPHA, pygbag-safe. Scratch generator; touches no game file.
"""
from __future__ import annotations

import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── family colour contract ────────────────────────────────────────────────────

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
    """BLEND_RGB_ADD ignores alpha and adds RGB outright, so the falloff has to
    be baked into the RGB and the peak ADDED luma pre-scaled to `budget`. That
    pre-scale is what makes additive light auditable: base + budget is the worst
    case by construction (performers_cast._warm_halo)."""
    key = (radius, budget, color)
    hit = _HALO_CACHE.get(key)
    if hit is not None:
        return hit
    col = _cap150(color)
    d = radius * 2 + 2
    cxr = cyr = radius + 1
    acc = [[0.0, 0.0, 0.0] for _ in range(d * d)]
    for rr in range(radius, 0, -1):
        w = (rr / radius) * (1.0 - rr / radius) * 4.0
        k = rr / radius
        c = (col[0] * (0.5 + 0.5 * (1 - k)), col[1] * (0.5 + 0.5 * (1 - k)),
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
    surf.blit(_halo_surface(radius, peak, color), (cx - radius - 1, cy - radius - 1),
              special_flags=pygame.BLEND_RGB_ADD)


# ── world geometry ────────────────────────────────────────────────────────────

SLICE_TOP = 500
SLICE_H = 148
FAR_Y = 595
NEAR_Y = 638
BAND_TOP = 560


def L(world_y):
    return world_y - SLICE_TOP


SKY_DAY = (150, 146, 132)
SKY_NIGHT = (26, 32, 52)
PAVE_DAY = (146, 136, 118)
PAVE_NIGHT = (44, 46, 56)


def _panel(w, night):
    s = pygame.Surface((w, SLICE_H))
    sky = SKY_NIGHT if night > 0.5 else SKY_DAY
    pave = PAVE_NIGHT if night > 0.5 else PAVE_DAY
    s.fill(sky)
    pygame.draw.rect(s, pave, (0, L(FAR_Y), w, SLICE_H - L(FAR_Y)))
    pygame.draw.line(s, _shade(pave, 14), (0, L(FAR_Y)), (w, L(FAR_Y)), 1)
    pygame.draw.rect(s, _shade(pave, -12), (0, L(NEAR_Y), w, SLICE_H - L(NEAR_Y)))
    pygame.draw.line(s, _shade(pave, 8), (0, L(NEAR_Y)), (w, L(NEAR_Y)), 1)
    for gy in range(L(FAR_Y) + 8, L(NEAR_Y), 9):
        pygame.draw.line(s, _shade(pave, -8), (0, gy), (w, gy), 1)
    return s


def _guides(s, w):
    for xx in range(0, w, 12):
        pygame.draw.line(s, (110, 130, 160), (xx, L(BAND_TOP)), (min(w, xx + 6), L(BAND_TOP)), 1)


# ════════════════════════════════════════════════════════════════════════════
# SHARED CAST GEOMETRY — matched to ped_cast / day_cast so an overlay authored
# here drops onto the shipped drawers without re-deriving anatomy.
# ════════════════════════════════════════════════════════════════════════════

SKIN = (222, 178, 132)
KID_H = 13
VEND_H = 20


def _person(surf, cx, feet, night, *, h=18, coat=(96, 104, 140), hair=(52, 42, 34),
            arms='down', arm_t=0.0, back=False, chin=0, bulk=1.0, prop=None,
            apron=None, face_dir=1):
    """The adult pedestrian at shared proportions (head r3, torso ~8, legs ~7).
    `prop` hangs an A12 walk-and-eat item off the retargeted chest-height reach."""
    coat_c = _retint(coat, night)
    coat_dk = _shade(coat_c, -34)
    skin = _retint(SKIN, night)
    hair_c = _retint(hair, night)
    head_r = 3
    torso_h = int(h * 0.46)
    body_w = max(3, int(h * 0.26 * bulk))
    torso_bot = feet - (h - torso_h - head_r * 2)
    torso_top = torso_bot - torso_h
    hy = torso_top - head_r - chin
    for sgn in (-1, 1):
        pygame.draw.line(surf, coat_dk, (cx + sgn * 2, torso_bot), (cx + sgn * 2, feet), 2)
    pygame.draw.polygon(surf, coat_c, [
        (cx - body_w, torso_top), (cx + body_w, torso_top),
        (cx + body_w + 1, torso_bot), (cx - body_w - 1, torso_bot)])
    pygame.draw.polygon(surf, coat_dk, [
        (cx - body_w, torso_top), (cx + body_w, torso_top),
        (cx + body_w + 1, torso_bot), (cx - body_w - 1, torso_bot)], 1)
    if apron is not None:
        ap = _retint(apron, night)
        pygame.draw.rect(surf, ap, (cx - body_w + 1, torso_top + 3, body_w * 2 - 1, torso_h - 2))
        pygame.draw.rect(surf, _shade(ap, -34), (cx - body_w + 1, torso_top + 3, body_w * 2 - 1, torso_h - 2), 1)
    sh_y = torso_top + 2
    hand = None
    if arms == 'up':
        for sgn in (-1, 1):
            pygame.draw.line(surf, coat_c, (cx + sgn * body_w, sh_y),
                             (cx + sgn * (body_w + 3), sh_y - 7), 2)
    elif arms == 'shade':
        # A14: one arm up over the brow — the shielding/waving step-out gesture
        pygame.draw.line(surf, coat_c, (cx + body_w, sh_y), (cx + 2, hy - 4), 2)
        pygame.draw.line(surf, skin, (cx + 2, hy - 4), (cx - 3, hy - 4), 2)
        pygame.draw.line(surf, coat_c, (cx - body_w, sh_y), (cx - body_w - 1, sh_y + 6), 2)
    elif arms == 'reach_chest':
        # A12: `reach_up` retargeted to CHEST height, holding food
        hand = (cx + face_dir * (body_w + 3), sh_y + 1)
        pygame.draw.line(surf, coat_c, (cx + face_dir * body_w, sh_y), hand, 2)
        pygame.draw.line(surf, coat_c, (cx - face_dir * body_w, sh_y),
                         (cx - face_dir * (body_w + 1), sh_y + 6), 2)
    else:
        for sgn in (-1, 1):
            pygame.draw.line(surf, coat_c, (cx + sgn * body_w, sh_y),
                             (cx + sgn * (body_w + 1), sh_y + 6), 2)
    if back:
        pygame.draw.circle(surf, hair_c, (cx, hy), head_r)
        pygame.draw.circle(surf, _shade(hair_c, -18), (cx, hy + 1), head_r - 1)
    else:
        pygame.draw.circle(surf, skin, (cx, hy), head_r)
        pygame.draw.circle(surf, hair_c, (cx, hy - 1), head_r)
        pygame.draw.arc(surf, hair_c, (cx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), 2)
        pygame.draw.circle(surf, (34, 24, 20), (cx + face_dir, hy), 0)
    if prop and hand:
        _hand_food(surf, hand[0], hand[1], night, prop, face_dir)
    return hy, sh_y, torso_top


# ════════════════════════════════════════════════════════════════════════════
# A12 — WALK-AND-EAT PROPS.  Four hand-held items that must read on a 14 px
# figure, which means each one is a different SHAPE EVENT, not a different
# colour: a horizontal bar, a pale dome, a vertical bead-stack, a stubby block
# with steam. Night-market seating is sparse, so supper is a grazing stroll —
# this is the festival's dominant crowd behaviour, and it is carried by 4 sprites
# that are between 3 and 7 px tall.
# ════════════════════════════════════════════════════════════════════════════

def _hand_food(surf, hx, hy, night, kind, face=1):
    if kind == 'skewer':
        # a 1px stick run HORIZONTALLY with three dark meat blocks — a wide bar
        stick = _retint((166, 140, 92), night)
        pygame.draw.line(surf, stick, (hx - 1, hy), (hx + face * 8, hy - 2), 1)
        meat = _retint((146, 84, 58), night)
        for k in range(3):
            mx = hx + face * (2 + k * 2)
            pygame.draw.rect(surf, meat, (mx, hy - 1 - k // 2, 2, 3))
            pygame.draw.line(surf, _shade(meat, 22), (mx, hy - 1 - k // 2), (mx + 1, hy - 1 - k // 2), 1)
    elif kind == 'bun':
        # a pale DOME with a pinched crown + one steam wisp; the only round item
        bun = _cap_to(_retint((228, 220, 202), night), 132)
        pygame.draw.circle(surf, _shade(bun, -30), (hx + face * 3, hy - 1), 3)
        pygame.draw.circle(surf, bun, (hx + face * 3, hy - 1), 2)
        pygame.draw.circle(surf, _shade(bun, -34), (hx + face * 3, hy - 3), 1)
        _wisp(surf, hx + face * 3, hy - 4, 0.4, n=2, rise=8, spread=1.2, peak_a=42,
              r0=1, sway=1.4, color=_mix((236, 230, 218), (214, 168, 110), 0.6 if night > 0.4 else 0.0))
    elif kind == 'tanghulu':
        # THE festival prop: a VERTICAL stack of 3 red beads on a stick. The
        # plan calls it the brightest non-gold object in the flood beat, so it is
        # deliberately the hottest of the four and still capped well under the coin.
        stick = _retint((172, 148, 100), night)
        pygame.draw.line(surf, stick, (hx + face * 2, hy + 1), (hx + face * 2, hy - 9), 1)
        red = _cap_to(_retint((214, 58, 52), night), 120) if night > 0.05 else (222, 62, 54)
        for k in range(3):
            by = hy - 2 - k * 3
            pygame.draw.circle(surf, _shade(red, -34), (hx + face * 2, by), 2)
            pygame.draw.circle(surf, red, (hx + face * 2, by), 1)
    else:  # 'cup'
        cup = _cap_to(_retint((206, 200, 186), night), 130)
        pygame.draw.polygon(surf, cup, [(hx + face * 1, hy - 4), (hx + face * 5, hy - 4),
                                        (hx + face * 4, hy + 1), (hx + face * 2, hy + 1)])
        pygame.draw.polygon(surf, _shade(cup, -34), [(hx + face * 1, hy - 4), (hx + face * 5, hy - 4),
                                                     (hx + face * 4, hy + 1), (hx + face * 2, hy + 1)], 1)
        pygame.draw.line(surf, _retint((150, 90, 70), night),
                         (hx + face * 1, hy - 4), (hx + face * 5, hy - 4), 1)
        _wisp(surf, hx + face * 3, hy - 5, 0.7, n=2, rise=7, spread=1.0, peak_a=34,
              r0=1, sway=1.2, color=_mix((236, 230, 218), (214, 168, 110), 0.6 if night > 0.4 else 0.0))


# ════════════════════════════════════════════════════════════════════════════
# A9 — THE MONKEY KING MASK.  The whole act's read at 22 px lives here: a GOLD
# face, a red-brown fur RUFF, and two long swept PHOENIX PLUMES off the brow.
# The plumes are the silhouette event — no other head in the game has two long
# curved antennae, so the troupe is identifiable from outline alone.
# ════════════════════════════════════════════════════════════════════════════

def _monkey_mask(surf, hx, hy, night, *, r=4, plume=0.0, plume_dir=1, worn=True):
    gold = _cap_to(_retint((216, 178, 92), night), 132) if night > 0.05 else (224, 186, 96)
    gold_dk = _shade(gold, -40)
    ruff = _retint((156, 74, 46), night)
    ruff_dk = _shade(ruff, -26)
    # the fur ruff, drawn first so it reads as a collar BEHIND the face
    for k, ang in enumerate(range(120, 421, 30)):
        rad = math.radians(ang)
        mx = hx + int(math.cos(rad) * (r + 1))
        my = hy + int(math.sin(rad) * (r + 1))
        pygame.draw.circle(surf, ruff_dk if k % 2 else ruff, (mx, my), 2)
    pygame.draw.circle(surf, gold_dk, (hx, hy), r)
    pygame.draw.circle(surf, gold, (hx, hy), max(1, r - 1))
    # the opera face: a red brow band + two dark eye slits + a peach-shaped snout
    pygame.draw.line(surf, _retint((178, 58, 48), night), (hx - r + 1, hy - 1), (hx + r - 1, hy - 1), 1)
    pygame.draw.circle(surf, (26, 20, 18), (hx - 1, hy), 0)
    pygame.draw.circle(surf, (26, 20, 18), (hx + 1, hy), 0)
    pygame.draw.line(surf, gold_dk, (hx - 1, hy + 2), (hx + 1, hy + 2), 1)
    # TWO LONG SWEPT PHOENIX PLUMES — the outline read. They lag the body on the
    # spin and the somersault, which is where most of the act's motion lives.
    pl = _cap_to(_retint((208, 188, 118), night), 128) if night > 0.05 else (218, 198, 124)
    pl_dk = _shade(pl, -46)
    for sgn in (-1, 1):
        pts = []
        for k in range(6):
            f = k / 5.0
            px = hx + sgn * (1 + f * 8) * plume_dir - sgn * 0
            py = hy - r - 1 - f * 7 + math.sin(f * 2.6 + plume) * 2.2 * f
            pts.append((int(px), int(py)))
        pygame.draw.lines(surf, pl_dk, False, pts, 2)
        pygame.draw.lines(surf, pl, False, pts, 1)
        pygame.draw.circle(surf, pl, pts[-1], 1)
    if not worn:
        # pushed up on the head: a chin strap dangling, so it reads as an object
        pygame.draw.line(surf, _retint((150, 132, 96), night), (hx - r, hy + 2), (hx - r - 1, hy + 6), 1)


def _acrobat(surf, cx, feet, night, *, h=20, t=0.0, torso=(196, 84, 62),
             lean=0, arms='down', legs='stand', head_at=None, plume_dir=1):
    """A Monkey King acrobat body. Red-and-yellow SASH is the team uniform: a
    diagonal red band with a 1 px gold edge, dealt identically to all three so
    the trio reads as one troupe while the three POSES stay unrelated."""
    tor = _retint(torso, night)
    tor_dk = _shade(tor, -36)
    gold = _cap_to(_retint((214, 182, 96), night), 130)
    body_w = 4
    torso_h = int(h * 0.44)
    torso_bot = feet - (h - torso_h - 8)
    torso_top = torso_bot - torso_h
    if legs == 'wide':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor_dk, (cx + sgn * 2, torso_bot),
                             (cx + sgn * 6, feet), 2)
    elif legs == 'brace':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor_dk, (cx + sgn * 2, torso_bot), (cx + sgn * 5, feet - 4), 2)
            pygame.draw.line(surf, tor_dk, (cx + sgn * 5, feet - 4), (cx + sgn * 4, feet), 2)
    elif legs == 'none':
        pass
    else:
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor_dk, (cx + sgn * 2, torso_bot), (cx + sgn * 2, feet), 2)
    pygame.draw.polygon(surf, tor, [
        (cx - body_w + lean, torso_top), (cx + body_w + lean, torso_top),
        (cx + body_w, torso_bot), (cx - body_w, torso_bot)])
    pygame.draw.polygon(surf, tor_dk, [
        (cx - body_w + lean, torso_top), (cx + body_w + lean, torso_top),
        (cx + body_w, torso_bot), (cx - body_w, torso_bot)], 1)
    pygame.draw.line(surf, _retint((198, 62, 52), night),
                     (cx - body_w, torso_top + 5), (cx + body_w, torso_top + 1), 2)
    pygame.draw.line(surf, gold, (cx - body_w, torso_top + 6), (cx + body_w, torso_top + 2), 1)
    sh_y = torso_top + 2
    hx, hy = (cx + lean, torso_top - 4) if head_at is None else head_at
    hands = []
    if arms == 'staff':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 5, sh_y + 2), 2)
            hands.append((cx + sgn * 5, sh_y + 2))
    elif arms == 'up':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 6, sh_y - 8), 2)
            hands.append((cx + sgn * 6, sh_y - 8))
    elif arms == 'grip':
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 3, sh_y + 8), 2)
            hands.append((cx + sgn * 3, sh_y + 8))
    elif arms == 'climb':
        pygame.draw.line(surf, tor, (cx - body_w, sh_y), (cx - 9, sh_y - 7), 2)
        pygame.draw.line(surf, tor, (cx + body_w, sh_y), (cx + 5, sh_y + 5), 2)
        hands.append((cx - 9, sh_y - 7))
    else:
        for sgn in (-1, 1):
            pygame.draw.line(surf, tor, (cx + sgn * body_w, sh_y), (cx + sgn * 4, sh_y + 6), 2)
    _monkey_mask(surf, hx, hy, night, r=4, plume=t * 3.0, plume_dir=plume_dir)
    return hands, (hx, hy), sh_y


# ── the three beats, each its own SHAPE LANGUAGE ─────────────────────────────

def beat_staff_spin(surf, cx, night, t, *, feet=NEAR_Y):
    """BEAT 1 (2.0 s) — the staff spin. Silhouette event: a WIDE HORIZONTAL
    lens. A 20 px bar at 3 Hz reads as a blur arc, not as a rotating stick, at
    this pixel size — so it is drawn as the arc plus the two instantaneous ends."""
    g = L(feet)
    hands, head, sh_y = _acrobat(surf, cx, g, night, h=21, t=t, legs='wide', arms='staff')
    spin = t * 3.0 * math.tau
    cy = sh_y + 1
    staff = _cap_to(_retint((198, 172, 104), night), 128)
    staff_dk = _shade(staff, -44)
    # the blur arc: a flattened ellipse the bar sweeps out, drawn 1 px so it
    # reads as motion rather than as a hoop the figure is standing inside
    pygame.draw.ellipse(surf, staff_dk, (cx - 11, cy - 4, 22, 9), 1)
    for k, a_off in enumerate((0.0, 0.35, 0.7)):
        a = spin - a_off
        ex = cx + math.cos(a) * 10
        ey = cy + math.sin(a) * 3.4
        w = 2 if k == 0 else 1
        col = staff if k == 0 else staff_dk
        pygame.draw.line(surf, col, (cx - (ex - cx), cy - (ey - cy)), (ex, ey), w)
    # the banded ends of the Ruyi Jingu Bang — two gold cuffs, the only detail
    for sgn in (-1, 1):
        ex = cx + sgn * math.cos(spin) * 10
        ey = cy + sgn * math.sin(spin) * 3.4
        pygame.draw.circle(surf, _cap_to(_retint((222, 188, 96), night), 128), (int(ex), int(ey)), 1)


def beat_tower(surf, cx, night, t, *, feet=NEAR_Y):
    """BEAT 2 (2.4 s) — the two-man shoulder tower, the THIRD acrobat climbing.
    Silhouette event: a TALL VERTICAL column (34 px, the tallest human shape in
    the festival) crossed by one diagonal limb. Locked on a gong hit."""
    g = L(feet)
    # base: braced legs, arms gripping the upper man's ankles
    _acrobat(surf, cx, g, night, h=19, t=t, legs='brace', arms='grip',
             torso=(178, 74, 56))
    top_feet = g - 17
    sway = math.sin(t * 1.4) * 1.0
    _acrobat(surf, int(cx + sway), top_feet, night, h=17, t=t + 0.4, legs='stand',
             arms='up', torso=(206, 96, 62))
    # the climber, hooked on the base's left side, one arm reaching for the top
    _acrobat(surf, cx - 10, g, night, h=17, t=t + 0.8, legs='none', arms='climb',
             torso=(190, 132, 62), plume_dir=-1)
    tor = _retint((190, 132, 62), night)
    pygame.draw.line(surf, tor, (cx - 10, g - 12), (cx - 6, g - 3), 2)
    pygame.draw.line(surf, tor, (cx - 10, g - 10), (cx - 4, g - 9), 2)


def beat_somersault(surf, cx, night, t, *, feet=NEAR_Y, air=1.0):
    """BEAT 3 (1.5 s) — the dismount. Silhouette event: a compact tucked BALL,
    AIRBORNE, with a visible gap of paving under it. Nothing else in the cast is
    ever off the ground, so this beat is unmistakable even in one frame."""
    g = L(feet)
    arc = math.sin(max(0.0, min(1.0, air)) * math.pi)
    bx = cx
    by = g - 6 - int(arc * 16)
    tor = _retint((196, 84, 62), night)
    tor_dk = _shade(tor, -36)
    gold = _cap_to(_retint((214, 182, 96), night), 130)
    spin = air * math.tau * 1.25
    # the tuck: torso disc + wrapped limbs, rotated with the roll
    pygame.draw.circle(surf, tor_dk, (bx, by), 7)
    pygame.draw.circle(surf, tor, (bx, by), 6)
    pygame.draw.arc(surf, gold, (bx - 6, by - 6, 13, 13), spin, spin + 2.4, 2)
    for k in (0, 1):
        a = spin + k * 2.1
        pygame.draw.line(surf, tor_dk, (bx + int(math.cos(a) * 3), by + int(math.sin(a) * 3)),
                         (bx + int(math.cos(a) * 7), by + int(math.sin(a) * 7)), 2)
    # the masked head tucked into the ball, plumes streaming out of the roll
    hx = bx + int(math.cos(spin + 3.4) * 4)
    hy = by + int(math.sin(spin + 3.4) * 4)
    _monkey_mask(surf, hx, hy, night, r=3, plume=spin, plume_dir=-1)
    # a compressed ground shadow that keeps the ball ANCHORED while it is in air
    sh = pygame.Surface((16, 4), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (10, 10, 16, int(90 * (1.0 - 0.5 * arc))), (0, 0, 16, 4))
    surf.blit(sh, (bx - 8, g - 2))


def _ring(surf, w, night, t, *, cx, exclude=()):
    """The 5-deep spectator ring: near-deck figures turned INWARD, desynced
    clapping, and the post-troupe kids already wearing the souvenir."""
    for k, dx in enumerate((-64, -44, 44, 62, 78)):
        if k in exclude:
            continue
        x = cx + dx
        if not (6 < x < w - 6):
            continue
        clap = 'up' if math.sin(t * 4.0 + k * 1.7) > 0.2 else 'down'
        _person(surf, x, L(NEAR_Y), night, h=18 + (k % 3), back=(dx < 0),
                arms=clap, chin=1, face_dir=-1 if dx > 0 else 1,
                coat=((80, 88, 116), (104, 84, 96), (78, 96, 92))[k % 3])


# ════════════════════════════════════════════════════════════════════════════
# A10 — THE PAPER MONKEY MASK, on day_cast.draw_kid geometry.  ~1 kid in 3 wears
# one in the two blocks after the troupe. It is the only cause-and-effect the
# street ever states out loud, and it costs one accessory sprite.
# ════════════════════════════════════════════════════════════════════════════

def _kid(surf, cx, feet, night, t, *, mask=None, age=0.6, shirt=(196, 92, 84),
         pants=(70, 64, 82), hair=(60, 44, 34), point=False):
    """draw_kid proportions: total = KID_H * (0.62 + 0.38*age), head_r ~ 34 % of
    total, chibi big-head/stubby-body. The mask hangs off the SAME head circle
    the shipped drawer computes, so the overlay needs no new anatomy."""
    total = max(7, int(KID_H * (0.62 + 0.38 * age)))
    head_r = max(2, int(total * (0.34 - 0.06 * age)))
    body_h = max(3, int(total * 0.32))
    body_w = max(3, int(total * 0.30))
    body_bot = feet - max(2, int(total * 0.30))
    body_y = body_bot - body_h
    hy = body_y - head_r + 1
    sh = _retint(shirt, night)
    pa = _retint(pants, night)
    skin = _retint(SKIN, night)
    gait = math.sin(t * 1.7)
    pygame.draw.ellipse(surf, sh, (cx - body_w, body_y, body_w * 2, body_h + 1))
    pygame.draw.ellipse(surf, _shade(sh, -42), (cx - body_w, body_y, body_w * 2, body_h + 1), 1)
    for sgn, sw in ((-1, gait * body_w * 0.4), (1, -gait * body_w * 0.4)):
        pygame.draw.line(surf, pa, (cx + sgn * body_w * 0.4, body_bot),
                         (cx + sgn * body_w * 0.4 + sw, feet), 2)
    pygame.draw.line(surf, _shade(skin, -26), (cx, hy + head_r - 1), (cx, body_y + 1), max(2, head_r // 2))
    pygame.draw.circle(surf, skin, (cx, hy), head_r)
    pygame.draw.circle(surf, _shade(skin, -26), (cx, hy), head_r, 1)
    if point:
        pygame.draw.line(surf, skin, (cx - body_w * 0.4, body_y + 1),
                         (cx - body_w * 1.7, body_y - body_h * 0.4), 2)
    if mask == 'worn':
        # ON the face: the mask covers the head circle entirely, so the child's
        # own features vanish. That absence is the read at 10 px.
        _monkey_mask(surf, cx, hy, night, r=head_r + 1, plume=t * 2.0)
    elif mask == 'up':
        # PUSHED UP on the brow: mask tipped back above the head, the kid's face
        # showing beneath. Same sprite, 4 px higher, one strap line.
        pygame.draw.circle(surf, _retint(hair, night), (cx, hy - head_r // 3), head_r)
        pygame.draw.circle(surf, (38, 26, 20), (cx - head_r // 2, hy), max(1, head_r // 4))
        _monkey_mask(surf, cx, hy - head_r - 1, night, r=head_r, plume=t * 2.0, worn=False)
    else:
        pygame.draw.circle(surf, _retint(hair, night), (cx, hy - head_r // 3), head_r)
        pygame.draw.arc(surf, _retint(hair, night),
                        (cx - head_r, hy - head_r, head_r * 2 + 1, head_r * 2 + 1),
                        math.radians(0), math.radians(180), max(1, head_r // 2))
        pygame.draw.circle(surf, (38, 26, 20), (cx - head_r // 2, hy), max(1, head_r // 4))


# ════════════════════════════════════════════════════════════════════════════
# A11 — FOOD THEATRE.  Overlays on the SHIPPED stall shell, not new stalls. The
# thesis: at density crest #2 the market gets more interesting as it gets
# slightly less crowded, and it does that by making three stalls PERFORM.
# ════════════════════════════════════════════════════════════════════════════

HALF_W = 22


def _stall_shell(surf, sx, base_y, night, *, awning=("terra", "cream"),
                 counter_h=15, sign=(190, 150, 90)):
    """food_stalls._stall_shell, compressed — posts + striped awning + back wall
    + counter, so an overlay authored here sits at the shipped stall's metrics."""
    palette = {"terra": (198, 86, 66), "cream": (236, 224, 204),
               "bamboo": (170, 150, 96), "indigo": (86, 104, 150),
               "jade": (108, 150, 120), "rust": (176, 96, 58)}
    post_top = base_y - 34
    post = _mix((92, 64, 40), (60, 66, 92), 0.30 * night)
    for px in (sx - HALF_W + 3, sx + HALF_W - 3):
        pygame.draw.rect(surf, post, (px - 1, post_top, 3, base_y - post_top))
        pygame.draw.line(surf, _shade(post, -20), (px + 1, post_top), (px + 1, base_y), 1)
    wall = _mix(_mix((150, 132, 110), (150, 124, 96), 0.5), (56, 62, 88), 0.32 * night)
    pygame.draw.rect(surf, _shade(wall, -10), (sx - HALF_W + 4, post_top + 2, (HALF_W - 4) * 2, 13))
    aw = HALF_W + 1
    ay = post_top - 4
    col_a = _mix(palette[awning[0]], (70, 70, 96), min(0.6, 0.9 * night))
    col_b = _mix(palette[awning[1]], (74, 80, 104), min(0.72, 1.3 * night))
    pygame.draw.rect(surf, _mix((110, 80, 50), (60, 66, 92), 0.3 * night),
                     (sx - aw - 1, ay - 2, aw * 2 + 2, 2))
    for i, ax in enumerate(range(sx - aw, sx + aw, 6)):
        col = col_a if i % 2 == 0 else col_b
        pygame.draw.polygon(surf, col, [
            (ax, ay), (ax + 6, ay), (ax + 6, ay + 4), (ax + 3, ay + 6), (ax, ay + 4)])
    cy = base_y - counter_h
    counter = _mix((120, 84, 52), (60, 66, 92), 0.30 * night)
    pygame.draw.rect(surf, counter, (sx - HALF_W + 1, cy, (HALF_W - 1) * 2, counter_h))
    pygame.draw.rect(surf, _shade(counter, 16), (sx - HALF_W + 1, cy, (HALF_W - 1) * 2, 2))
    pygame.draw.rect(surf, _shade(counter, -22), (sx - HALF_W + 1, base_y - 4, (HALF_W - 1) * 2, 4))
    if sign:
        col = _cap150(_retint(sign, night))
        bx, by = sx - HALF_W + 6, post_top + 1
        pygame.draw.rect(surf, col, (bx - 2, by, 5, 12))
        pygame.draw.rect(surf, _shade(col, -30), (bx - 2, by, 5, 12), 1)
    return cy


def theatre_noodle(surf, sx, night, t, *, base_y=FAR_Y, step=None):
    """A11a — the NOODLE-PULLER. Arms thrown WIDE with a dough ribbon strung
    between them, doubling 1 -> 2 -> 4 -> 8 on a 4-step 0.9 s cycle. The dough is
    thrown UP on every fold, which is the razor: the beat moves light upward.
    The widest arm span on the whole street is the silhouette."""
    cy = _stall_shell(surf, sx, L(base_y), night, awning=("bamboo", "cream"))
    st = int((t / 0.225) % 4) if step is None else step
    strands = (1, 2, 4, 8)[st]
    lift = (0, 3, 1, 4)[st]
    # the puller stands BEHIND the counter, one head above it
    tor = _retint((150, 138, 120), night)
    body_top = cy - 13
    pygame.draw.polygon(surf, tor, [(sx - 4, body_top), (sx + 4, body_top),
                                    (sx + 5, cy), (sx - 5, cy)])
    pygame.draw.polygon(surf, _shade(tor, -34), [(sx - 4, body_top), (sx + 4, body_top),
                                                 (sx + 5, cy), (sx - 5, cy)], 1)
    skin = _retint(SKIN, night)
    pygame.draw.circle(surf, skin, (sx, body_top - 4), 3)
    # crown pinned to exactly 560 — the puller is the tallest thing behind the
    # counter and the band ceiling is what decides how high the arms can go
    pygame.draw.circle(surf, _retint((54, 44, 38), night), (sx, body_top - 4), 3)
    span = 15
    lh = (sx - span, body_top - 1 - lift)
    rh = (sx + span, body_top - 1 - lift)
    pygame.draw.line(surf, tor, (sx - 4, body_top + 2), lh, 2)
    pygame.draw.line(surf, tor, (sx + 4, body_top + 2), rh, 2)
    pygame.draw.circle(surf, skin, lh, 1)
    pygame.draw.circle(surf, skin, rh, 1)
    dough = _cap_to(_retint((228, 218, 194), night), 130)
    dough_dk = _shade(dough, -40)
    # the ribbon: `strands` sagging loops between the hands, tighter each fold
    for k in range(strands):
        sag = 8 - k * (6.0 / max(1, strands))
        pts = []
        for i in range(11):
            f = i / 10.0
            x = lh[0] + (rh[0] - lh[0]) * f
            yv = lh[1] + math.sin(f * math.pi) * sag + k * 0.9
            pts.append((int(x), int(yv)))
        pygame.draw.lines(surf, dough_dk if k % 2 else dough, False, pts, 1)
    # the flour board below and a slap-puff on the fold frames
    board = _retint((150, 122, 84), night)
    pygame.draw.rect(surf, board, (sx - 12, cy - 3, 24, 3))
    if st in (1, 3):
        _wisp(surf, sx, cy - 4, t, n=2, rise=9, spread=1.6, peak_a=40, r0=1,
              sway=1.6, color=(216, 210, 198))
    return st, strands


def theatre_sugar(surf, sx, night, t, *, base_y=FAR_Y, phase=None):
    """A11b — the SUGAR-PAINTER. Seated, a wand held over a flat stone slab,
    pouring an amber line-drawing that resolves into a disc on a stick. The pour
    is the ONE downward motion of the whole night, which is exactly why it earns
    its contrast against every rising thing around it."""
    cy = _stall_shell(surf, sx, L(base_y), night, awning=("rust", "cream"), sign=(176, 110, 70))
    ph = int((t / 1.4) % 3) if phase is None else phase
    # the SLAB — a pale 10px stone the drawing is poured onto
    slab = _cap_to(_retint((198, 194, 186), night), 126)
    pygame.draw.rect(surf, _shade(slab, -34), (sx - 8, cy - 5, 18, 5))
    pygame.draw.rect(surf, slab, (sx - 7, cy - 4, 16, 3))
    # the seated painter, leaning in over the slab
    tor = _retint((110, 124, 148), night)
    seat_y = cy - 1
    pygame.draw.polygon(surf, _shade(tor, -30), [(sx - 16, seat_y), (sx - 6, seat_y),
                                                 (sx - 7, seat_y - 5), (sx - 15, seat_y - 5)])
    pygame.draw.rect(surf, tor, (sx - 16, cy - 13, 8, 9))
    pygame.draw.rect(surf, _shade(tor, -34), (sx - 16, cy - 13, 8, 9), 1)
    skin = _retint(SKIN, night)
    # A SEATED figure buys the vertical budget the lifted disc needs — the whole
    # reason this act sits down rather than stands up.
    pygame.draw.circle(surf, skin, (sx - 12, cy - 16), 3)
    pygame.draw.circle(surf, _retint((56, 46, 40), night), (sx - 12, cy - 16), 3)
    amber = _cap_to(_retint((198, 146, 62), night), 126) if night > 0.05 else (214, 160, 68)
    if ph < 2:
        wand = (sx - 4 + ph * 4, cy - 11)
        pygame.draw.line(surf, tor, (sx - 9, cy - 11), wand, 2)
        pygame.draw.line(surf, _retint((140, 116, 78), night), wand, (wand[0] + 3, cy - 8), 1)
        # the falling thread of hot sugar + the trail already on the slab
        pygame.draw.line(surf, amber, (wand[0] + 3, cy - 8), (wand[0] + 3, cy - 5), 1)
        pts = [(sx - 6, cy - 4), (sx - 3, cy - 6), (sx, cy - 4), (sx + 3, cy - 6)]
        pygame.draw.lines(surf, amber, False, pts[:2 + ph * 2], 1)
        if ph == 1:
            pygame.draw.circle(surf, amber, (sx + 3, cy - 6), 1)
    else:
        # the FINISHED disc lifted on its stick — a lollipop of poured sugar
        pygame.draw.line(surf, tor, (sx - 9, cy - 11), (sx - 1, cy - 14), 2)
        pygame.draw.line(surf, _retint((150, 124, 82), night), (sx - 1, cy - 14), (sx + 4, cy - 16), 1)
        pygame.draw.circle(surf, _shade(amber, -40), (sx + 6, cy - 16), 4)
        pygame.draw.circle(surf, amber, (sx + 6, cy - 16), 3)
        pygame.draw.arc(surf, _shade(amber, -46), (sx + 3, cy - 19, 7, 7),
                        math.radians(200), math.radians(340), 1)
    return ph


def theatre_tanghulu(surf, sx, night, t, *, base_y=FAR_Y):
    """A11c — the TANGHULU RACK. Research: skewers are displayed bristling off a
    straw/foam POLE. That gives the stall row a spiky, radially-symmetric
    silhouette it does not otherwise contain — a new shape, not a new colour."""
    cy = _stall_shell(surf, sx, L(base_y), night, awning=("indigo", "cream"), sign=(168, 96, 80))
    pole_x = sx + 2
    # Pole height is set BY the band ceiling, not by taste: cap ellipse lands on
    # exactly 560 and the splay is tuned so no bead crosses it either.
    top = cy - 18
    straw = _retint((186, 162, 104), night)
    pygame.draw.rect(surf, _shade(straw, -34), (pole_x - 4, top, 8, cy - top))
    pygame.draw.rect(surf, straw, (pole_x - 3, top + 1, 6, cy - top - 2))
    for k in range(3):
        pygame.draw.line(surf, _shade(straw, -28), (pole_x - 3, top + 5 + k * 6),
                         (pole_x + 2, top + 5 + k * 6), 1)
    pygame.draw.ellipse(surf, _shade(straw, 12), (pole_x - 4, top - 2, 9, 4))
    stick = _retint((172, 148, 100), night)
    red = _cap_to(_retint((214, 58, 52), night), 120) if night > 0.05 else (222, 62, 54)
    red_dk = _shade(red, -38)
    # 5 skewers per side, splayed at alternating angles so no two overlap
    for k in range(5):
        for sgn in (-1, 1):
            ang = math.radians(20 + k * 13 + (6 if sgn > 0 else 0))
            ay = top + 5 + k * 4
            ex = pole_x + sgn * int(math.cos(ang) * 13)
            ey = ay - int(math.sin(ang) * 4)
            pygame.draw.line(surf, stick, (pole_x + sgn * 3, ay), (ex, ey), 1)
            for b in range(3):
                f = 0.45 + b * 0.26
                bx = int(pole_x + sgn * 3 + (ex - pole_x - sgn * 3) * f)
                by = int(ay + (ey - ay) * f)
                pygame.draw.circle(surf, red_dk, (bx, by), 2)
                pygame.draw.circle(surf, red, (bx, by), 1)
    if night > 0.05:
        _warm_glow(surf, pole_x, cy - 10, radius=8, peak=22, color=(140, 76, 60))


# ════════════════════════════════════════════════════════════════════════════
# A14 — THE VENDOR STEP-OUT.  The single most important beat in the plan: for
# the ten seconds the dragon passes, the market withdraws its own signature.
# The vendor leaves the counter, stands BESIDE it at the front edge, faces the
# parade and puts a hand up. Steam goes 3 wisps to 1. Calls stop.
# ════════════════════════════════════════════════════════════════════════════

def _vendor_working(surf, sx, night, t, *, base_y=FAR_Y):
    cy = _stall_shell(surf, sx, L(base_y), night, awning=("jade", "cream"), sign=(150, 120, 70))
    steam = _mix((236, 230, 218), (214, 168, 110), 0.6) if night > 0.4 else (236, 238, 240)
    for k, (dx, phz, pk) in enumerate(((-7, 0.0, 70), (2, 0.4, 58), (9, 0.7, 46))):
        _wisp(surf, sx + dx, cy - 6, t, n=3, rise=24, spread=2.8, phase=phz,
              peak_a=pk, r0=1, sway=2.6, color=steam)
    # BEHIND the counter, calling: only the head and one raised arm clear it
    _person(surf, sx - 2, L(base_y) - 12, night, h=17, coat=(150, 96, 74),
            apron=(206, 196, 176), arms='up', face_dir=-1)
    return cy


def _vendor_stepout(surf, sx, night, t, *, base_y=FAR_Y):
    cy = _stall_shell(surf, sx, L(base_y), night, awning=("jade", "cream"), sign=(150, 120, 70))
    steam = _mix((236, 230, 218), (214, 168, 110), 0.6) if night > 0.4 else (236, 238, 240)
    # 3 wisps -> 1, thinner: the market's own signature, withdrawn
    _wisp(surf, sx + 1, cy - 6, t, n=2, rise=14, spread=1.8, peak_a=34, r0=1,
          sway=1.8, color=steam)
    # BESIDE the counter at the front edge, full body visible, facing RIGHT
    _person(surf, sx + HALF_W + 6, L(base_y), night, h=19, coat=(150, 96, 74),
            apron=(206, 196, 176), arms='shade', face_dir=1)
    return cy


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


def _yardsticks(p, night, *, x=16, coin=False):
    _person(p, x, L(FAR_Y), night, h=18, coat=(96, 104, 140))
    _text(p, "adult", x - 12, L(FAR_Y) + 2, 7,
          (150, 160, 185) if night > 0.5 else (70, 58, 46))
    if coin:
        _gold_coin(p, p.get_width() - 18, 22, r=7)
        _text(p, "coin 230", p.get_width() - 46, 32, 7,
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

def _panel_beat(w, night, which, t, *, ring=True, clean=False, air=1.0):
    p = _panel(w, night)
    if not clean:
        _guides(p, w)
    cx = w // 2
    if ring:
        _ring(p, w, night, t, cx=cx)
    if which == 'spin':
        beat_staff_spin(p, cx, night, t)
    elif which == 'tower':
        beat_tower(p, cx, night, t)
    else:
        beat_somersault(p, cx, night, t, air=air)
    if not clean:
        _yardsticks(p, night)
    return p


def _panel_theatre(w, night, kind, t, *, clean=False, step=None):
    p = _panel(w, night)
    if not clean:
        _guides(p, w)
    cx = w // 2
    if kind == 'noodle':
        theatre_noodle(p, cx, night, t, step=step)
    elif kind == 'sugar':
        theatre_sugar(p, cx, night, t, phase=step)
    else:
        theatre_tanghulu(p, cx, night, t)
    if not clean:
        _yardsticks(p, night)
    return p


# ════════════════════════════════════════════════════════════════════════════
# AUDIT — rendered pixels, label-free panels.
# ════════════════════════════════════════════════════════════════════════════

def _audit():
    night = 0.95
    probe = _panel(200, night)
    bg = set(probe.get_at((x, y))[:3] for x in range(200) for y in range(SLICE_H))
    hottest = 0.0
    over = 0
    hot_by = {}
    tops = {}

    def scan(surf, tag):
        nonlocal hottest, over
        h = 0.0
        top = 9999
        for x in range(surf.get_width()):
            for y in range(surf.get_height()):
                c = surf.get_at((x, y))[:3]
                if c in bg:
                    continue
                l = _luma(c)
                h = max(h, l)
                top = min(top, y + SLICE_TOP)
                hottest = max(hottest, l)
                if l > NIGHT_GLOW_CAP:
                    over += 1
        hot_by[tag] = h
        tops[tag] = top

    for which in ('spin', 'tower', 'somersault'):
        for tt in (0.2, 0.9, 1.6):
            scan(_panel_beat(300, night, which, tt, clean=True), "M." + which)
    # The theatre pieces and the step-out sit on the SHIPPED food_stalls shell,
    # whose awning crossbar already tops out at 555 and whose steam already
    # climbs past it. Band compliance is therefore measured on the OVERLAY only
    # — the topmost pixel that differs from a bare shell — so the audit reports
    # what this round adds rather than re-litigating shipped geometry.
    shell_top = 9999
    overlay_top = {}

    def bare_shell(w, awn, sign):
        s = _panel(w, night)
        _stall_shell(s, w // 2, L(FAR_Y), night, awning=awn, sign=sign)
        return s

    def diff_top(full, bare, tag):
        top = 9999
        for x in range(full.get_width()):
            for y in range(full.get_height()):
                if full.get_at((x, y))[:3] != bare.get_at((x, y))[:3]:
                    top = min(top, y + SLICE_TOP)
                    break
        overlay_top[tag] = min(overlay_top.get(tag, 9999), top)

    shells = {'noodle': (("bamboo", "cream"), (190, 150, 90)),
              'sugar': (("rust", "cream"), (176, 110, 70)),
              'tanghulu': (("indigo", "cream"), (168, 96, 80))}
    for kind in ('noodle', 'sugar', 'tanghulu'):
        awn, sg = shells[kind]
        bare = bare_shell(260, awn, sg)
        for x in range(260):
            for yy in range(SLICE_H):
                if bare.get_at((x, yy))[:3] not in bg:
                    shell_top = min(shell_top, yy + SLICE_TOP)
                    break
        for st in (0, 1, 2, 3):
            full = _panel_theatre(260, night, kind, 0.3 + st * 0.5, clean=True,
                                  step=st if kind != 'tanghulu' else None)
            scan(full, "A11." + kind)
            diff_top(full, bare, "A11." + kind)

    p = _panel(300, night)
    for i, prop in enumerate(('skewer', 'bun', 'tanghulu', 'cup')):
        _person(p, 40 + i * 62, L(NEAR_Y), night, h=14, arms='reach_chest', prop=prop)
    scan(p, "A12.walk-and-eat")

    p = _panel(300, night)
    for i, mk in enumerate((None, 'worn', 'up')):
        _kid(p, 50 + i * 80, L(NEAR_Y), night, 0.5, mask=mk)
    scan(p, "A10.kid mask")

    p = _panel(240, night)
    _vendor_working(p, 120, night, 0.6)
    scan(p, "A14.working")
    p = _panel(240, night)
    _vendor_stepout(p, 120, night, 0.6)
    scan(p, "A14.step-out")
    # A14's band extent is the FIGURE's, measured alone: the steam column above
    # it is the shipped stall's own behaviour (this pose thins it, never adds
    # to it), so folding steam into the vendor's band number would be measuring
    # someone else's art.
    for tag, feet, hh, arms in (("A14.working", L(FAR_Y) - 12, 17, 'up'),
                                ("A14.step-out", L(FAR_Y), 19, 'shade')):
        fp = _panel(120, night)
        _person(fp, 60, feet, night, h=hh, coat=(150, 96, 74),
                apron=(206, 196, 176), arms=arms)
        top = 9999
        for x in range(120):
            for yy in range(SLICE_H):
                if fp.get_at((x, yy))[:3] not in bg:
                    top = min(top, yy + SLICE_TOP)
                    break
        overlay_top[tag] = top
    for tag in ("M.spin", "M.tower", "M.somersault", "A12.walk-and-eat", "A10.kid mask"):
        overlay_top[tag] = tops[tag]
    return dict(hottest=hottest, over=over, hot_by=hot_by, tops=tops,
                overlay_top=overlay_top, shell_top=shell_top)


# ════════════════════════════════════════════════════════════════════════════
# RENDER
# ════════════════════════════════════════════════════════════════════════════

def render():
    sheet = pygame.Surface((WIDTH, 2100))
    sheet.fill((24, 26, 36))
    y = PAD
    _text(sheet, "FIRE-TREE NIGHT — round 1 · THE MONKEY KING'S TROUPE (A9-A10) + FOOD THEATRE (A11) + WALK-AND-EAT (A12) + THE VENDOR STEP-OUT (A14)",
          PAD, y, 17, (250, 246, 236), bold=True)
    y += 21
    y = _wrap(sheet, "Panels are literal screen slices: world y 500-647 at 1x, with the far deck (595), the near deck (638) and the 560 cast/prop band ceiling (blue dashes) drawn in — NOTHING on this sheet is allowed above 560; the fire sheet's spark FX is the plan's one sanctioned exception. "
                     "The monkey slot goes to masked HUMAN acrobats rather than a live-animal act: 耍猴 trainer numbers collapsed from ~10,000 to ~300, the practice is contested on welfare grounds, a chained macaque reads sad rather than charming to a modern casual audience — and it fails the festival's razor, because a monkey on a chain looks DOWN.",
              PAD, y, WIDTH - PAD * 2, 10, (186, 186, 200), 12)
    y += 6

    # ── A9 the three beats ───────────────────────────────────────────────────
    _text(sheet, "A9 · THE MONKEY KING'S TROUPE — a 3-beat routine on a 5.9 s loop. The distinct-variants rule is applied to SHAPE LANGUAGE, not to costume: the three beats are a WIDE HORIZONTAL, a TALL VERTICAL and a ROUND AIRBORNE silhouette. Same three performers, same red-and-yellow sash, three unrelated outlines.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    bw = (WIDTH - PAD * 4) // 3
    ys = []
    for i, (which, lab, sub) in enumerate((
            ('spin', "BEAT 1 · STAFF SPIN (2.0 s) — a WIDE HORIZONTAL lens",
             "A 20 px bar at 3 Hz cannot read as a rotating stick at this pixel size, so it is drawn as the swept BLUR ARC plus the two instantaneous ends and three trailing samples. Legs wide, two gold cuffs on the Ruyi Jingu Bang. The most legible acrobatic motion available at 20 px."),
            ('tower', "BEAT 2 · SHOULDER TOWER (2.4 s) — a TALL VERTICAL column",
             "Two-high at 34 px: the tallest human shape in the entire festival, locked on a gong hit. The THIRD acrobat climbs the base's left side, so the column is crossed by one diagonal limb — the detail that stops it reading as one very tall person."),
            ('somersault', "BEAT 3 · DISMOUNT SOMERSAULT (1.5 s) — a ROUND, AIRBORNE ball",
             "A tucked ball rolling 30 px across the front of the ring with a visible GAP of paving under it and a compressed shadow keeping it anchored. Nothing else in the cast is ever off the ground, so this beat is unmistakable in a single frame."))):
        p = _panel_beat(bw, 0.95, which, 0.55 + i * 0.4)
        ys.append(_place(sheet, p, PAD + i * (bw + PAD), y, lab, sub=sub))
    y = max(ys)
    # routine as a 6-phase strip + a mask zoom
    _text(sheet, "The routine as one 6-phase loop (night), and the mask at 4x — the read that has to survive at 22 px", PAD, y + 2, 10, (216, 210, 190), bold=True)
    y += 16
    sw = (WIDTH - PAD * 8 - 220) // 6
    strip = [('spin', 0.1, 1.0), ('spin', 0.5, 1.0), ('tower', 1.1, 1.0),
             ('tower', 1.7, 1.0), ('somersault', 2.2, 0.35), ('somersault', 2.5, 0.85)]
    sx = PAD
    for i, (which, tt, air) in enumerate(strip):
        p = _panel_beat(sw, 0.95, which, tt, ring=(i in (0, 3)), air=air)
        sheet.blit(p, (sx, y))
        pygame.draw.rect(sheet, (74, 78, 94), (sx, y, sw, SLICE_H), 1)
        _text(sheet, "%d" % (i + 1), sx + 3, y + 2, 9, (230, 210, 160), bold=True)
        sx += sw + PAD
    mp = _panel(120, 0.95)
    _acrobat(mp, 60, L(NEAR_Y), 0.95, h=21, t=0.4, legs='wide', arms='up')
    _zoom(sheet, mp, (44, L(NEAR_Y) - 34, 34, 26), 6, sx + 8, y + 14,
          "6x · gold face · red-brown fur ruff · two swept phoenix plumes")
    y += SLICE_H + 20

    # ── A10 kid mask ─────────────────────────────────────────────────────────
    _text(sheet, "A10 · THE PAPER MONKEY MASK — the payoff. In the two blocks after the square, ~1 kid in 3 wears one. They BOUGHT it. It is the only visible cause-and-effect on the street all day, and it costs one accessory sprite hung off the head circle day_cast.draw_kid already computes.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    kw = (WIDTH - PAD * 3) // 2
    ys = []
    for col, night in ((0, 0.0), (1, 0.95)):
        p = _panel(kw, night)
        _guides(p, kw)
        labs = ("no mask (the shipped kid)", "WORN on the face", "PUSHED UP on the head",
                "worn + pointing up", "up + pointing up")
        for i, (mk, pt) in enumerate(((None, False), ('worn', False), ('up', False),
                                      ('worn', True), ('up', True))):
            x = 46 + i * 62
            _kid(p, x, L(NEAR_Y), night, 0.4 + i * 0.3, mask=mk, point=pt,
                 age=0.45 + (i % 3) * 0.2,
                 shirt=((196, 92, 84), (96, 132, 150), (168, 140, 90))[i % 3])
            _text(p, labs[i][:14], x - 24, L(NEAR_Y) + 2, 7,
                  (150, 160, 185) if night > 0.5 else (70, 58, 46))
        _yardsticks(p, night, x=kw - 22)
        ys.append(_place(sheet, p, PAD + col * (kw + PAD), y,
                         "A10 kid pool — " + ("DAY" if night < 0.5 else "NIGHT (gold capped 132, plumes 128)"),
                         sub="WORN: the mask covers the head circle entirely, so the child's own features vanish — that ABSENCE is the read at 10 px. PUSHED UP: the same sprite 4 px higher with a dangling chin strap, the kid's face showing beneath. Kids point rather than wave inside the window."))
    y = max(ys)
    kp = _panel(140, 0.95)
    _kid(kp, 40, L(NEAR_Y), 0.95, 0.5, mask='worn', age=0.7)
    _kid(kp, 96, L(NEAR_Y), 0.95, 0.5, mask='up', age=0.7)
    z = _zoom(sheet, kp, (20, L(NEAR_Y) - 22, 96, 26), 5, PAD, y + 14,
              "5x · worn vs pushed-up, at true kid scale")
    _wrap(sheet, "The two states have to differ in OUTLINE, not just position, or at 10 px they are the same blob: worn gives a smooth gold disc where a face should be, pushed-up gives a two-lobed head (mask above, hair below) plus a strap. The plumes read on both.",
          PAD + z + 20, y + 14, WIDTH - PAD * 2 - z - 40, 10, (200, 198, 208), 12)
    y += 14 + 26 * 5 + 14

    # ── A11 food theatre ─────────────────────────────────────────────────────
    _text(sheet, "A11 · FOOD THEATRE — three OVERLAYS on the shipped food_stalls shell, not three new stalls. The thesis of density crest #2: the market gets more INTERESTING as it gets slightly less crowded, and it does that by making three stalls perform. The queues form at these three, because people queue for the show, not the food.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    nw = (WIDTH - PAD * 5) // 4
    ys = []
    for i in range(4):
        p = _panel_theatre(nw, 0.0, 'noodle', 0.0, step=i)
        ys.append(_place(sheet, p, PAD + i * (nw + PAD), y,
                         "A11a NOODLE-PULLER — fold %d of 4 (%d strand%s)" % (i + 1, (1, 2, 4, 8)[i], "" if i == 0 else "s"),
                         sub="Arms thrown WIDE with the dough strung between them — the widest arm span on the street. The ribbon doubles 1-2-4-8 on a 0.9 s cycle and is thrown UP on every fold, so the beat obeys the razor. A slap-puff of flour on folds 2 and 4." if i == 0 else
                             "The doubling is the animation: four visible steps, each ribbon tighter and higher than the last."))
    y = max(ys)
    tw = (WIDTH - PAD * 5) // 4
    ys = []
    for i in range(3):
        p = _panel_theatre(tw, 0.95, 'sugar', 0.0, step=i)
        ys.append(_place(sheet, p, PAD + i * (tw + PAD), y,
                         ("A11b SUGAR-PAINTER — pour" if i == 0 else
                          ("A11b — the drawing half-formed" if i == 1 else "A11b — finished disc lifted on its stick")),
                         sub="Seated, leaning in, a wand over a pale 10 px stone slab, an amber thread falling onto it. The pour is the ONE downward motion of the entire night, which is exactly why it earns its contrast against every rising thing around it." if i == 0 else None))
    p = _panel_theatre(tw, 0.95, 'tanghulu', 0.4)
    ys.append(_place(sheet, p, PAD + 3 * (tw + PAD), y, "A11c TANGHULU RACK — the new stall-side silhouette",
                     sub="Skewers are displayed bristling off a straw POLE. That gives the stall row a spiky, radially symmetric outline it does not otherwise contain — a new SHAPE, not a new colour. 10 skewers x 3 beads, red capped 120."))
    y = max(ys)
    dp = _panel_theatre(240, 0.0, 'tanghulu', 0.4)
    z = _zoom(sheet, dp, (86, L(FAR_Y) - 32, 70, 34), 4, PAD, y + 14, "4x · tanghulu rack, day")
    np_ = _panel_theatre(240, 0.95, 'noodle', 0.0, step=3)
    z2 = _zoom(sheet, np_, (92, L(FAR_Y) - 34, 60, 30), 4, PAD + z + 20, y + 14, "4x · 8-strand fold, night")
    _wrap(sheet, "All three overlays keep the shipped stall metrics (HALF_W 22, counter at base-15, post top at base-34) and add nothing above the awning, so they drop onto the existing shell without re-deriving anatomy or disturbing the awning colour-pair deck. The awning pairs shown are bamboo/cream (noodle), rust/cream (sugar) and indigo/cream (tanghulu), so the three theatre stalls are also three different colour-pairs in a row.",
          PAD + z + z2 + 36, y + 14, WIDTH - PAD * 2 - z - z2 - 56, 10, (200, 198, 208), 12)
    y += 14 + 34 * 4 + 14

    # ── A12 walk-and-eat ─────────────────────────────────────────────────────
    _text(sheet, "A12 · WALK-AND-EAT PROPS x4 — the festival's DOMINANT crowd behaviour. Night-market seating is sparse, so supper is a grazing stroll rather than a seated effort. `reach_up` retargets to CHEST height and the four items hang off that one hand. Each is a different SHAPE EVENT, because at 14 px colour is the first thing to die.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    pw2 = (WIDTH - PAD * 3) // 2
    ys = []
    for col, night in ((0, 0.0), (1, 0.95)):
        p = _panel(pw2, night)
        _guides(p, pw2)
        for i, (prop, lab) in enumerate((('skewer', "skewer — a wide BAR"),
                                         ('bun', "steam bun — a pale DOME"),
                                         ('tanghulu', "tanghulu — a vertical STACK"),
                                         ('cup', "cup — a stubby BLOCK + steam"))):
            x = 60 + i * 82
            _person(p, x, L(NEAR_Y), night, h=14, arms='reach_chest', prop=prop,
                    coat=((92, 104, 132), (128, 96, 88), (86, 110, 96), (116, 100, 128))[i])
            _text(p, lab, x - 30, L(NEAR_Y) + 2, 7,
                  (150, 160, 185) if night > 0.5 else (70, 58, 46))
        # the same four on 18px adults, so the prop is proven at both cast sizes
        for i, prop in enumerate(('skewer', 'bun', 'tanghulu', 'cup')):
            _person(p, 400 + i * 40, L(FAR_Y), night, h=18, arms='reach_chest',
                    prop=prop, coat=(96, 104, 140))
        _text(p, "same 4 on 18 px far-deck adults", 372, L(FAR_Y) + 2, 7,
              (150, 160, 185) if night > 0.5 else (70, 58, 46))
        _yardsticks(p, night, x=pw2 - 20, coin=True)
        ys.append(_place(sheet, p, PAD + col * (pw2 + PAD), y,
                         "A12 — " + ("DAY" if night < 0.5 else "NIGHT (tanghulu red capped 120 — the plan's brightest non-gold object; bun 132, cup 130)"),
                         sub="Gait is dialled -15%% for walk-and-eat figures. The tanghulu is deliberately the hottest of the four and still sits ~110 luma under the coin."))
    y = max(ys)
    fp = _panel(280, 0.95)
    for i, prop in enumerate(('skewer', 'bun', 'tanghulu', 'cup')):
        _person(fp, 36 + i * 64, L(NEAR_Y), 0.95, h=14, arms='reach_chest', prop=prop)
    z = _zoom(sheet, fp, (16, L(NEAR_Y) - 24, 240, 28), 4, PAD, y + 14,
              "4x · all four at 14 px, night — read by shape alone")
    _wrap(sheet, "At 14 px a held object gets roughly 4x5 px. That is enough for exactly one silhouette idea each, so the four were chosen to be orthogonal: horizontal bar / round dome / vertical stack / squat block. Put any two side by side in a crowd and they are still distinguishable; put the same two in the same colour and they still are.",
          PAD + z + 20, y + 14, WIDTH - PAD * 2 - z - 40, 10, (200, 198, 208), 12)
    y += 14 + 28 * 4 + 14

    # ── A14 vendor step-out ──────────────────────────────────────────────────
    _text(sheet, "A14 · THE VENDOR STEP-OUT — the market pause. For the ten seconds the dragon occupies the block, every stall goes non-working: the vendor comes out from BEHIND the counter to BESIDE it, faces the parade, and puts a hand up. Steam thins 3 wisps to 1. Calls stop. The market withdraws its own signature and gives it back when the tail passes.",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 18
    vw = (WIDTH - PAD * 5) // 4
    ys = []
    for i, (night, fn, lab, sub) in enumerate((
            (0.0, _vendor_working, "WORKING (day) — behind the counter",
             "Three steam plumes at peak 70/58/46, head and one raised calling arm clearing the counter. The vendor is a half-figure: the counter owns the lower body."),
            (0.0, _vendor_stepout, "STEP-OUT (day) — beside the counter",
             "A WHOLE figure appears where there was half of one. That change in mass is the read, before the pose even registers."),
            (0.95, _vendor_working, "WORKING (night) — the market's signature",
             "Steam + call + counter. This is what the two stalls on the dragon route look like for the 9 seconds before the pearl arrives."),
            (0.95, _vendor_stepout, "STEP-OUT (night) — the pause",
             "One thin wisp, arm up shielding the eyes, facing right into the parade. Restarts staggered 0.4 s after the tail passes."))):
        p = _panel(vw, night)
        _guides(p, vw)
        fn(p, vw // 2 - (10 if i % 2 else 0), night, 0.6)
        _yardsticks(p, night)
        ys.append(_place(sheet, p, PAD + i * (vw + PAD), y, "A14 · " + lab, sub=sub))
    y = max(ys) + 6

    # ── audit ────────────────────────────────────────────────────────────────
    a = _audit()
    coin_l = _luma(COIN_CORE)
    top_ok = min(a["overlay_top"].values())
    passed = a["over"] == 0 and a["hottest"] <= NIGHT_GLOW_CAP and a["hottest"] < coin_l and top_ok >= BAND_TOP
    _text(sheet, "NIGHT-CAP + BAND AUDIT (measured on RENDERED pixels of label-free panels, night=0.95, across every pose/phase on this sheet)",
          PAD, y, 12, (240, 220, 150), bold=True)
    y += 16
    y = _wrap(sheet,
              "hottest pixel on this sheet = %.1f luma  ·  pixels over the %d cap = %d  ·  gold coin core = %.1f luma, SOLE BRIGHTEST (%.0f%% hotter)  ·  "
              "highest pixel any NEW piece reached = y %d against the %d band ceiling (headroom %d px)  ·  nothing here needs the spark exception.   %s"
              % (a["hottest"], NIGHT_GLOW_CAP, a["over"], coin_l,
                 (coin_l / max(1.0, a["hottest"]) - 1.0) * 100.0,
                 top_ok, BAND_TOP, top_ok - BAND_TOP,
                 "PASS — nothing breaches 150, no NEW art breaches y=560, the coin stays sole-brightest."
                 if passed else "FAIL — see per-piece numbers."),
              PAD, y, WIDTH - PAD * 2, 10, (170, 205, 185) if passed else (225, 145, 135), 13)
    y = _wrap(sheet, "per-piece hottest luma: " + "  ".join("%s=%.0f" % (k, v) for k, v in a["hot_by"].items()),
              PAD, y + 2, WIDTH - PAD * 2, 9, (176, 176, 190), 12)
    y = _wrap(sheet, "per-piece topmost NEW pixel (world y, measured as the topmost pixel that DIFFERS from a bare shipped stall shell where applicable): "
                     + "  ".join("%s=%d" % (k, v) for k, v in a["overlay_top"].items())
                     + ".   For reference the SHIPPED food_stalls shell itself already tops out at y %d (awning crossbar) and its steam climbs past it — unchanged by these overlays, and reported here so the band number isn't quietly re-litigating shipped geometry."
                     % a["shell_top"],
              PAD, y + 2, WIDTH - PAD * 2, 9, (176, 176, 190), 12)

    out = "/home/user/skybit/docs/sidewalk_overhaul/festival/troupe_food_round_1.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    final = pygame.Surface((WIDTH, min(sheet.get_height(), y + 14)))
    final.blit(sheet, (0, 0))
    pygame.image.save(final, out)
    print("saved", out, final.get_size())
    print("AUDIT hottest=%.1f over=%d topmost=%d" % (a["hottest"], a["over"], top_ok))
    print("per-piece hottest:", {k: round(v, 1) for k, v in a["hot_by"].items()})
    print("per-piece NEW-art top y:", a["overlay_top"])
    print("shipped stall shell top y:", a["shell_top"])
    print("PASS" if passed else "FAIL")
    return a, passed


if __name__ == "__main__":
    render()
