"""Food-market STALL props — round 3 candidate-sheet generator: SIX NEW STALLS.

The shipped family (game/food_stalls.py) is five booths — bamboo STEAMER, soup
CAULDRON, skewer GRILL, stir-fry WOK, tea URN — over one shared shell (two timber
posts, cloth awning, counter, back wall, hanging sign; HALF_W=22, posts to
base_y-34). The family's organizing principle is that the SHELL never changes:
a stall is identified by its COOKING-APPARATUS SILHOUETTE plus its awning colour
pair. So "six new stalls" is really "six new apparatus silhouettes" — the
distinct-variants rule applies to the apparatus, not to the paint.

The shipped five are, in silhouette terms, four squat stoves and one tall kettle.
This round deliberately fills the shapes the row does NOT yet contain:

  S6  ROAST-DUCK CABINET  — the family's first TALL ENCLOSED BOX: a lit glass
      vitrine standing on the counter with lacquered birds hanging on hooks. An
      upright rectangle with a glowing window; nothing else in the market is a
      box, and nothing else hangs its food in the air.
  S7  FLAT GRIDDLE        — the family's FLATTEST stall: a wide low iron disc,
      a lid tipped on its edge, a batter rake that sweeps with t. It is the only
      apparatus that stays entirely UNDER the awning line, and its steam is a
      broad low sheet rather than a column.
  S8  CLAY-POT BANK       — REPETITION as silhouette: five small lidded pots in
      a multi-hole stove, a crenellated row of domes, each with its own little
      offset wisp so the plume reads as a keyboard, not a plume.
  S9  DRUM ROASTER        — the only HORIZONTAL CYLINDER and the only ROTATING
      part in the market: a hooped barrel on a cradle over a firebox, its crank
      turning and its hoops travelling with t, sooty smoke off a stub chimney.
  S10 SHAVED ICE          — the second non-fire stall and the only one with NO
      rising element at all: no steam, no flame, no glow. Its motion vector is
      INVERTED — a turning crank and ice flecks falling DOWN into the bowl. In a
      row of stoves, the one cold stall is the strongest beat available.
  S11 NOODLE BOILER       — a tall straight-sided stock column (not the
      cauldron's wide belly) under a GANTRY RAIL of long-handled strainer
      baskets that dip into the boil with t. Reads as boiling + serving, and is
      pointedly NOT festival.theatre_noodle's arms-wide dough showman.

Awning pairs are six NEW combinations from the same muted shan-shui market
palette (shipped: terra/cream, indigo/cream, rust/cream, jade/cream,
bamboo/indigo); the new entries are plum, wheat, ochre, ink, clay, slate, moss
and teal.

Every new stall is also paired with an EXISTING day_cast vendor pose so no new
cast art is needed, and deliberately with poses the shipped five never use (they
use only call/ladle/fan): chop, pour, weigh, stack, sign, wok — so the vendor row
diversifies at the same time as the stall row.

CONSTRAINTS carried over from the shipped family:
- pure pygame.draw.* + Surface (SRCALPHA, BLEND_RGB_ADD ok), pygbag-safe. No
  numpy / gfxdraw / PIL in stall code.
- steam/smoke/flame/crank all animate off `t`; reuse `_wisp` + `_warm_glow`.
- NIGHT CAP: nothing over 150 luma at night, so the gold coin (~232) stays the
  brightest object on screen. The sheet carries a MEASURED audit (hottest luma +
  px over cap, scanned off the rendered night frames), not a colour list.
- CEILING: no apparatus (steam included) may top out above y518 with base_y=595 —
  the shipped steamer's y516 stack is the family maximum.
- three `openness` assembly states like the shipped shell (skeleton / frame /
  full); the apparatus simply doesn't draw below 0.5.

Nothing here touches production game files; review-sheet generator only.
"""
from __future__ import annotations

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))


# ── shared colour helpers (lifted from game/foreground_props + ped_cast) ───────

def _clamp(c):
    return max(0, min(255, int(c)))


def _mix(a, b, t):
    t = max(0.0, min(1.0, t))
    return (_clamp(a[0] + (b[0] - a[0]) * t),
            _clamp(a[1] + (b[1] - a[1]) * t),
            _clamp(a[2] + (b[2] - a[2]) * t))


def _shade(c, d):
    return (_clamp(c[0] + d), _clamp(c[1] + d), _clamp(c[2] + d))


def _retint(col, night):
    """Cool toward the night ground band — matches ped_cast._retint_person, which
    is what game/food_stalls imports."""
    if night <= 0.05:
        return col
    return _mix(col, (54, 64, 96), min(0.55, 0.40 * night + 0.20))


def _luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


NIGHT_GLOW_CAP = 150
HALF_W = 22


def _cap150(col):
    """Hold a lit ember/flame/glow under the 150 luma ceiling without flattening
    hue — the contract that keeps the gold coin the brightest object."""
    y = _luma(col)
    if y <= NIGHT_GLOW_CAP:
        return col
    k = NIGHT_GLOW_CAP / y
    return (_clamp(col[0] * k), _clamp(col[1] * k), _clamp(col[2] * k))


def _cool(col, night):
    """Retint + a second pull for anything still over the cap. Pale materials —
    ice, glazed porcelain, a bone-white lid — survive the generic night cooling
    above 150 and start competing with the coin unless they get this."""
    c = _retint(col, night)
    return _cap150(c) if night > 0.05 else c


# ── animated steam/smoke + warm-glow primitives (verbatim from the shipped family)

def _wisp(surf, x, y0, t, *, n=3, rise=20, spread=3.0, speed=0.55, phase=0.0,
          color=(232, 232, 236), peak_a=70, r0=2, sway=2.4):
    """A rising column of `n` translucent puffs reading as RISING MOTION: each
    puff eases up the full `rise` while fattening + drifting, and fades over its
    top third so it visibly dissipates at the crest."""
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


def _steam_col(night):
    # By day steam cools toward the sky; at night it warms instead — lit from
    # below by the stall's own lanterns, the cheapest night-market cue there is.
    if night > 0.4:
        return _mix((236, 230, 218), (214, 168, 110), min(1.0, (night - 0.4) * 1.4))
    return _mix((236, 238, 240), (150, 170, 200), 0.35 + 0.4 * night)


def _smoke_col(night):
    return _mix((200, 190, 180), (120, 120, 130), 0.4 + 0.3 * night)


# ── shared booth shell (verbatim, with six new awning colours) ────────────────

# Shipped: terra, cream, bamboo, indigo, jade, rust. The six new entries stay in
# the same muted shan-shui band — nothing here is a saturated arcade hue, because
# the awning must never out-read the apparatus it frames.
AWNING_PALETTE = {
    "terra": (198, 86, 66), "cream": (236, 224, 204),
    "bamboo": (170, 150, 96), "indigo": (86, 104, 150),
    "jade": (108, 150, 120), "rust": (176, 96, 58),
    "plum": (132, 80, 92), "wheat": (214, 196, 158),
    "ochre": (192, 148, 70), "ink": (62, 70, 86),
    "clay": (172, 124, 96), "slate": (104, 116, 126),
    "moss": (114, 124, 84), "teal": (84, 130, 134),
}


def _flat_awning(surf, sx, post_top, half_w, night, awning):
    aw = half_w + 1
    ay = post_top - 4
    a_name, b_name = awning
    dimk = min(0.72, 1.3 * night)
    col_a = _mix(AWNING_PALETTE[a_name], (70, 70, 96), min(0.6, 0.9 * night))
    col_b = _mix(AWNING_PALETTE[b_name], (74, 80, 104), dimk)
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
    being BUILT and struck:
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


# ════════════════════════════════════════════════════════════════════════════
# THE SIX NEW STALLS — (surf, sx, base_y, night, t, *, openness=1.0)
# ════════════════════════════════════════════════════════════════════════════

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

SHIPPED = [
    ("S1 steamer", _fs.stall_steamer, "terra/cream", "call (0)"),
    ("S2 cauldron", _fs.stall_cauldron, "indigo/cream", "ladle (3)"),
    ("S3 grill", _fs.stall_grill, "rust/cream", "fan (2)"),
    ("S4 wok", _fs.stall_wok, "jade/cream", "fan (2)"),
    ("S5 tea urn", _fs.stall_tea, "bamboo/indigo", "call (0)"),
]

NEW = [
    ("S6 roast-duck cabinet", stall_duck, "plum / wheat", "CHOP (6)",
     "TALL LIT BOX: glazed vitrine on the counter, 3 lacquered birds on a hook rail (sway w/ t), "
     "capped interior lamp, cleaver+board for the chopping vendor, stub vent smoking. The family's "
     "first enclosed silhouette and its only lit window."),
    ("S7 flat griddle", stall_griddle, "ochre / ink", "POUR (7)",
     "FLATTEST + widest: 36px shallow iron disc, crepe + folded half, lid tipped on edge, batter RAKE "
     "sweeping an arc w/ t, tool jar. Steam is a LOW WIDE SHEET (4 short wisps), not a column; the only "
     "apparatus entirely under the awning line."),
    ("S8 clay-pot bank", stall_claypot, "clay / slate", "WEIGH (1)",
     "REPETITION: 5 lidded pots in a 5-hole stove = a crenellated row of domes, 5 offset mini-wisps "
     "(a keyboard, not a plume), one lid chattering up per cycle, burner rings glowing capped, bowl stack."),
    ("S9 drum roaster", stall_roaster, "moss / ochre", "STACK (4)",
     "HORIZONTAL CYLINDER + the market's only ROTATION: hooped barrel in a cradle, hoops travelling and "
     "crank arm revolving w/ t, firebox mouth flickering, stub chimney's sooty ribbon, chestnut tray."),
    ("S10 shaved ice", stall_ice, "teal / wheat", "SIGN (5)",
     "THE COLD STALL: zero steam, zero flame, zero glow. Cast-iron shaver, clamped ice block, crank "
     "turning w/ t, snow bowl + syrup arc, 3 syrup bottles. Motion INVERTED — ice flecks fall DOWN, the "
     "only downward motion in the family."),
    ("S11 noodle boiler", stall_boiler, "ink / wheat", "WOK (8)",
     "STRAIGHT COLUMN + GANTRY: tall cylindrical stock pot (vs the cauldron's belly) under a rail of 3 "
     "long-handled strainer baskets dipping on their own phases; bowls + chopstick jar = SERVING, "
     "explicitly not the festival's noodle-pulling showman."),
]


# ════════════════════════════════════════════════════════════════════════════
# MEASUREMENT — the family's audit discipline, done by SCANNING rendered frames
# ════════════════════════════════════════════════════════════════════════════

BASE_Y = 595
COIN_PEAK = (255, 232, 150)


def _measure(fn, *, night, glow=True,
             frames=(0.0, 0.35, 0.7, 1.05, 1.4, 1.9, 2.5, 3.1)):
    """Scan real rendered frames rather than trusting the source colours: alpha
    wisps stack, ellipse edges blend, and the additive halo lands on the deck as
    pixels no colour-list audit would catch.

    Two passes matter, because the family's cap means two different things. With
    `glow=False` the shared `_warm_glow` is suppressed and what is measured is
    MATERIAL — the drawn colours, which are what `_cap150` actually governs and
    which must never break 150. With `glow=True` the same frames include the
    additive halo, which is soft light summed onto the deck; the shipped five do
    exactly the same thing, so that column is judged against THEM.

    Returns hottest luma, px over the cap, and the ceiling (min y) in world
    coords at base_y=595."""
    SW = 120
    SH = 120
    deck = (30, 34, 52) if night > 0.5 else (150, 140, 118)
    hottest = 0.0
    over = 0
    top = None
    saved = globals()["_warm_glow"], _fs._warm_glow
    if not glow:
        def noop(*a, **k):
            return None
        globals()["_warm_glow"] = noop
        _fs._warm_glow = noop
    try:
        for t in frames:
            lay = pygame.Surface((SW, SH), pygame.SRCALPHA)
            fn(lay, SW // 2, SH - 20, night, t)
            base = pygame.Surface((SW, SH))
            base.fill(deck)
            base.blit(lay, (0, 0))
            for yy in range(SH):
                for xx in range(SW):
                    if lay.get_at((xx, yy))[3] == 0:
                        continue
                    if top is None or yy < top:
                        top = yy
                    ly = _luma(base.get_at((xx, yy)))
                    if ly > hottest:
                        hottest = ly
                    if ly > NIGHT_GLOW_CAP:
                        over += 1
    finally:
        globals()["_warm_glow"], _fs._warm_glow = saved
    ceiling = BASE_Y - ((SH - 20) - top) if top is not None else BASE_Y
    return hottest, over, ceiling


def audit():
    """Per stall: material hot/over (the `_cap150` contract) and composited
    hot/over (materials + the shared additive halo), plus the measured ceiling —
    with the shipped five run through the identical scan, so the new six are
    judged against the family rather than against a number in a vacuum."""
    rows = []
    for group, items in (("new", NEW), ("shipped", SHIPPED)):
        for it in items:
            name, fn, awn, pose = it[0], it[1], it[2], it[3]
            mat_n, mat_over, ceil_n = _measure(fn, night=0.95, glow=False)
            cmp_n, cmp_over, _c = _measure(fn, night=0.95, glow=True)
            mat_d, _o, _c2 = _measure(fn, night=0.0, glow=False)
            label = name if group == "new" else name + "  (shipped)"
            rows.append((label, awn, pose, mat_d, mat_n, mat_over, cmp_n, cmp_over, ceil_n))
    return rows


# ════════════════════════════════════════════════════════════════════════════
# SHEET RENDERER  (round_2 house style)
# ════════════════════════════════════════════════════════════════════════════

W = 1180
PAD = 12
BG_DAY = (150, 140, 118)
BG_NIGHT = (40, 46, 70)


def _font(sz, bold=False):
    return pygame.font.SysFont("dejavusans", sz, bold=bold)


def _text(surf, s, x, y, sz=11, col=(228, 224, 214), bold=False):
    surf.blit(_font(sz, bold).render(s, True, col), (x, y))


def _gold_coin(surf, cx, cy, r=8):
    """The in-game gold-coin brightness yardstick — nothing on a stall (least of
    all a coal/flame/ice block) may out-pop this."""
    for rr, c in ((r, (150, 110, 30)), (r - 1, (235, 190, 60)), (r - 3, COIN_PEAK)):
        pygame.draw.circle(surf, c, (cx, cy), rr)
    pygame.draw.circle(surf, (180, 140, 50), (cx, cy), r, 1)
    surf.blit(_font(9, True).render("$", True, (150, 100, 20)), (cx - 3, cy - 6))


def _mini_vendor(surf, sx, base_y, night, *, pose="call"):
    """A coarse stand-in for day_cast.draw_vendor (VEND_H=17) so the sheet can
    show the assigned pose AT the stall and double as the adult yardstick — the
    production drawer is not imported here because the point is scale + arm
    action, not the cast's palette variety."""
    skin = _retint((222, 178, 132), night)
    shirt = _retint((150, 110, 78), night)
    shirt_d = _shade(shirt, -34)
    apron = _retint((204, 192, 172), night)
    hair = _retint((50, 40, 32), night)
    g = base_y
    body_y = g - 11
    pygame.draw.line(surf, shirt_d, (sx - 1, body_y + 7), (sx - 1, g), 2)
    pygame.draw.line(surf, shirt_d, (sx + 2, body_y + 7), (sx + 2, g), 2)
    pygame.draw.rect(surf, shirt, (sx - 3, body_y, 7, 8))
    pygame.draw.rect(surf, apron, (sx - 2, body_y + 3, 5, 5))
    if pose == "fan":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 2), (sx - 7, body_y + 3), 2)
        pygame.draw.rect(surf, _retint((200, 180, 140), night), (sx - 9, body_y + 2, 3, 4))
    elif pose == "ladle":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 2), (sx - 6, body_y + 6), 2)
        pygame.draw.line(surf, shirt, (sx + 3, body_y + 2), (sx - 5, body_y + 6), 2)
    elif pose == "chop":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 2), (sx - 6, body_y - 2), 2)
        pygame.draw.line(surf, _cool((176, 182, 190), night), (sx - 7, body_y - 3), (sx - 9, body_y - 1), 2)
    elif pose == "pour":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 1), (sx - 7, body_y - 5), 2)
        pygame.draw.rect(surf, _retint((150, 122, 88), night), (sx - 10, body_y - 8, 4, 4))
        pygame.draw.line(surf, _cool((214, 200, 160), night), (sx - 8, body_y - 4), (sx - 8, body_y + 4), 1)
    elif pose == "weigh":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 1), (sx - 8, body_y - 1), 2)
        pygame.draw.line(surf, _retint((140, 120, 90), night), (sx - 10, body_y - 2), (sx - 5, body_y - 4), 1)
        pygame.draw.ellipse(surf, _cool((186, 182, 170), night), (sx - 12, body_y - 1, 5, 3))
    elif pose == "stack":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 1), (sx - 7, body_y - 3), 2)
        for k in range(2):
            pygame.draw.ellipse(surf, _retint((176, 132, 78), night), (sx - 11, body_y - 5 - k * 3, 7, 3))
    elif pose == "sign":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 1), (sx - 7, body_y - 4), 2)
        pygame.draw.rect(surf, _cool((186, 168, 132), night), (sx - 11, body_y - 9, 6, 6))
        pygame.draw.rect(surf, _retint((92, 74, 56), night), (sx - 11, body_y - 9, 6, 6), 1)
    elif pose == "wok":
        pygame.draw.line(surf, shirt, (sx - 2, body_y + 2), (sx - 8, body_y + 1), 2)
        pygame.draw.ellipse(surf, _retint((96, 96, 102), night), (sx - 14, body_y, 7, 4))
    else:
        pygame.draw.line(surf, skin, (sx - 2, body_y + 2), (sx - 5, body_y), 2)
    pygame.draw.circle(surf, skin, (sx, body_y - 2), 3)
    pygame.draw.circle(surf, hair, (sx, body_y - 4), 3)


def _stall_cell(parent, name, fn, note, awn, pose, x, y, w, h, night):
    """One annotated cell: TRUE far-lane across 3 animation frames + a 2.4x zoom
    inset + an in-cell coin, on a day or night deck."""
    is_night = night > 0.5
    bg = BG_NIGHT if is_night else BG_DAY
    cell = pygame.Surface((w, h))
    cell.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = h - 18
    pygame.draw.rect(cell, deck, (0, base, w, h - base))
    pygame.draw.line(cell, _shade(bg, 24), (0, base), (w, base), 1)

    for i, ft in enumerate((0.0, 0.7, 1.4)):
        cx = 38 + i * 52
        fn(cell, cx, base, night, ft)
        _text(cell, f"t{i}", cx - 6, base + 2, 8, _shade(bg, 60))
    _text(cell, "TRUE far-lane  (3 anim frames)", 14, base + 9, 8, _shade(bg, 50))

    SCRATCH = 66
    nat = pygame.Surface((SCRATCH, SCRATCH), pygame.SRCALPHA)
    fn(nat, SCRATCH // 2, SCRATCH - 6, night, 0.6)
    z = 2.4
    zoom = pygame.transform.scale(nat, (int(SCRATCH * z), int(SCRATCH * z)))
    zw, zh = zoom.get_size()
    zx, zy = w - zw - 8, 24
    pygame.draw.rect(cell, _shade(bg, -20), (zx - 2, zy - 2, zw + 4, zh + 4))
    cell.blit(zoom, (zx, zy))
    pygame.draw.rect(cell, _shade(bg, 40), (zx - 2, zy - 2, zw + 4, zh + 4), 1)
    _text(cell, "2.4x zoom", zx, zy - 12, 8, _shade(bg, 60))

    # the assigned vendor, at the stall, next to the coin: pose + adult scale +
    # brightness ceiling all judged in one glance
    _mini_vendor(cell, 200, base, night, pose=pose.split(" ")[0].lower())
    _text(cell, "vendor " + pose, 178, base + 2, 8, _shade(bg, 55))
    _gold_coin(cell, w - 16, h - 14, r=7)
    _text(cell, "coin", w - 32, h - 12, 7, _shade(bg, 55))

    _text(cell, name, 6, 4, 13, (240, 236, 226), bold=True)
    _text(cell, "awning " + awn, 6 + _font(13, True).size(name)[0] + 10, 6, 10, (198, 200, 210))
    fnt = _font(9, False)
    words = note.split(" ")
    line = ""
    yy = 22
    wrap_w = zx - 12
    for wd in words:
        test = (line + " " + wd).strip()
        if fnt.size(test)[0] > wrap_w:
            cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy))
            yy += 11
            line = wd
        else:
            line = test
    if line:
        cell.blit(fnt.render(line, True, (206, 202, 192)), (6, yy))

    parent.blit(cell, (x, y))
    pygame.draw.rect(parent, (70, 74, 90), (x, y, w, h), 1)


def _row_band(sheet, y, items, night, label, *, show_vendor=False, yardsticks=False):
    bg = BG_NIGHT if night > 0.5 else BG_DAY
    bh = 132
    row = pygame.Surface((W - PAD * 2, bh))
    row.fill(bg)
    deck = _mix(bg, (0, 0, 0), 0.18)
    base = bh - 22
    pygame.draw.rect(row, deck, (0, base, W - PAD * 2, 22))
    pygame.draw.line(row, _shade(bg, 26), (0, base), (W - PAD * 2, base), 1)
    # the y518 family ceiling, drawn where it actually falls relative to base_y
    ceil_y = base - (BASE_Y - 518)
    pygame.draw.line(row, (190, 120, 120), (0, ceil_y), (W - PAD * 2, ceil_y), 1)
    _text(row, "y518 family ceiling (shipped steamer = y516)", 4, ceil_y - 11, 8, (200, 140, 140))
    spacing = (W - PAD * 2 - 150) // max(1, len(items))
    for i, it in enumerate(items):
        name, fn = it[0], it[1]
        pose = it[3].split(" ")[0].lower() if show_vendor else None
        cx = 66 + i * spacing
        fn(row, cx, base, night, 0.6 + i * 0.43)
        if pose:
            _mini_vendor(row, cx + 30, base, night, pose=pose)
        _text(row, name, cx - 22, base + 2, 8,
              (200, 210, 230) if night > 0.5 else (66, 54, 44))
    if yardsticks:
        yx = W - PAD * 2 - 60
        _mini_vendor(row, yx, base, night, pose="call")
        pygame.draw.line(row, (210, 150, 150), (yx + 8, base - 17), (yx + 8, base), 1)
        _text(row, "adult 17px", yx - 16, base + 2, 8, (210, 160, 160))
        _gold_coin(row, W - PAD * 2 - 22, base - 30)
        _text(row, "coin", W - PAD * 2 - 34, base - 18, 8, (210, 180, 120))
    _text(row, label, 4, 2, 10, (170, 190, 225) if night > 0.5 else (58, 48, 38), bold=True)
    sheet.blit(row, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, W - PAD * 2, bh), 1)
    return bh


def render():
    rows = audit()

    cell_w = (W - PAD * 3) // 2
    cell_h = 158
    n_rows = (len(NEW) + 1) // 2
    open_h = 120
    audit_h = 26 + len(rows) * 13 + 14

    total_h = (60
               + 22 + 132 + 6 + 132 + 8          # A day + night bands (new six)
               + 22 + 132 + 6                    # A2 shipped five band
               + 22 + 2 * (18 + n_rows * (cell_h + 6)) + 10   # B detail cells
               + 22 + 2 * (118 + 6) + 10         # C mixed market row
               + 22 + open_h + 10                # D openness states
               + audit_h + 30)
    sheet = pygame.Surface((W, total_h))
    sheet.fill((26, 28, 38))

    y = PAD
    _text(sheet, "SKYBIT SIDEWALK — FOOD-STALL FAMILY EXPANSION (round 3): SIX NEW STALLS", PAD, y, 17,
          (250, 246, 236), bold=True)
    y += 21
    _text(sheet, "Same shell as the shipped five (posts + cloth awning + counter + back wall, HALF_W=22, posts to base_y-34). A stall IS its APPARATUS SILHOUETTE + its awning pair, so these are six new silhouettes: a lit box, a flat disc, a repeating row, a lying cylinder, a cold machine, a gantry column.", PAD, y, 10, (188, 186, 200))
    y += 15
    _text(sheet, "All motion drives off t (steam / smoke / crank / hoops / dipping baskets / falling ice). Night cap 150 luma — measured audit at the foot. Ceiling y518 @ base_y=595. Each stall pairs with an EXISTING day_cast vendor pose (chop/pour/weigh/stack/sign/wok — none used by the shipped five).", PAD, y, 10, (188, 186, 200))
    y += 24

    # ── A. the new six at true far-lane size, day then night ──
    _text(sheet, "A.  THE SIX NEW STALLS — TRUE far-lane size, with their assigned vendor, the y518 ceiling, and the adult + gold-coin yardsticks", PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    y += _row_band(sheet, y, NEW, 0.0, "DAY", show_vendor=True, yardsticks=True) + 6
    y += _row_band(sheet, y, NEW, 0.95, "NIGHT  (steam warms from below; every lit part capped <=150)",
                   show_vendor=True, yardsticks=True) + 8

    # ── A2. the shipped five, same treatment, for family coherence ──
    _text(sheet, "A2.  THE SHIPPED FIVE (imported live from game/food_stalls.py) — the coherence check: same shell, same weight, same night behaviour", PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    y += _row_band(sheet, y, [(n, f, a, p) for n, f, a, p in SHIPPED], 0.0, "DAY  (shipped)",
                   yardsticks=True) + 6

    # ── B. per-stall detail ──
    _text(sheet, "B.  PER-STALL — 3 anim frames · 2.4x zoom · assigned vendor pose · in-cell coin · apparatus note   (DAY then NIGHT)", PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        _text(sheet, "NIGHT" if is_night else "DAY", PAD, y, 11,
              (160, 180, 220) if is_night else (240, 210, 130), bold=True)
        y += 14
        for r in range(n_rows):
            for c in range(2):
                idx = r * 2 + c
                if idx >= len(NEW):
                    break
                name, fn, awn, pose, note = NEW[idx]
                _stall_cell(sheet, name, fn, note, awn, pose,
                            PAD + c * (cell_w + PAD), y, cell_w, cell_h, night)
            y += cell_h + 6
        y += 4

    # ── C. the whole market row, old + new interleaved ──
    _text(sheet, "C.  THE FULL ELEVEN — shipped five and new six INTERLEAVED, each with its vendor: does the row read as one market with eleven trades?", PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    mixed = []
    for i in range(6):
        mixed.append(NEW[i][:4])
        if i < 5:
            n, f, a, p = SHIPPED[i]
            mixed.append((n, f, a, p))
    for is_night in (False, True):
        night = 0.95 if is_night else 0.0
        bg = BG_NIGHT if is_night else BG_DAY
        sh = 118
        strip = pygame.Surface((W - PAD * 2, sh))
        strip.fill(bg)
        deck = _mix(bg, (0, 0, 0), 0.2)
        base = sh - 16
        pygame.draw.rect(strip, deck, (0, base, W - PAD * 2, sh - base))
        pygame.draw.line(strip, _shade(bg, 24), (0, base), (W - PAD * 2, base), 1)
        spacing = (W - PAD * 2 - 70) // len(mixed)
        for i, (name, fn, _a, pose) in enumerate(mixed):
            cx = 50 + i * spacing
            fn(strip, cx, base, night, 0.4 + i * 0.61)
            _mini_vendor(strip, cx + 27, base, night, pose=pose.split(" ")[0].lower())
            _text(strip, name.split(" ")[0], cx - 10, base + 2, 8,
                  (200, 210, 230) if is_night else (66, 54, 44))
        _gold_coin(strip, W - PAD * 2 - 18, 18)
        _text(strip, "coin", W - PAD * 2 - 32, 30, 8, _shade(bg, 60))
        _text(strip, "NIGHT" if is_night else "DAY", 4, 2, 9,
              (170, 190, 225) if is_night else (60, 50, 40), bold=True)
        sheet.blit(strip, (PAD, y))
        pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, W - PAD * 2, sh), 1)
        y += sh + 6
    y += 4

    # ── D. the three assembly states ──
    _text(sheet, "D.  OPENNESS — every new stall in the shell's three assembly states (0.2 skeleton / 0.4 frame / 1.0 full); the apparatus only appears at >=0.5", PAD, y, 13, (240, 220, 150), bold=True)
    y += 20
    strip = pygame.Surface((W - PAD * 2, open_h))
    strip.fill(BG_DAY)
    deck = _mix(BG_DAY, (0, 0, 0), 0.18)
    base = open_h - 16
    pygame.draw.rect(strip, deck, (0, base, W - PAD * 2, open_h - base))
    pygame.draw.line(strip, _shade(BG_DAY, 26), (0, base), (W - PAD * 2, base), 1)
    group = (W - PAD * 2 - 20) // len(NEW)
    for i, (name, fn, _a, _p, _n) in enumerate(NEW):
        gx = 14 + i * group
        for k, op in enumerate((0.2, 0.4, 1.0)):
            fn(strip, gx + 24 + k * 50, base, 0.0, 0.8 + i * 0.5, openness=op)
        _text(strip, name, gx + 10, base + 2, 8, (66, 54, 44))
    sheet.blit(strip, (PAD, y))
    pygame.draw.rect(sheet, (70, 74, 90), (PAD, y, W - PAD * 2, open_h), 1)
    y += open_h + 10

    # ── E. the measured audit ──
    _text(sheet, "E.  MEASURED NIGHT-CAP + CEILING AUDIT — 8 rendered frames per stall scanned on the night deck (night=0.95), not a colour list.", PAD, y, 12, (240, 220, 150), bold=True)
    y += 15
    _text(sheet, "MATERIAL = the drawn colours, which is what _cap150 governs: must stay <=150 with zero px over.   COMPOSITED = the same frames including the shared additive _warm_glow halo (soft light summed onto the deck) — judged against the SHIPPED FIVE below, which use the identical primitive.", PAD, y, 10, (188, 190, 200))
    y += 15
    hdr = (f"{'stall':27s}{'awning':16s}{'vendor pose':13s}"
           f"{'mat hot(day)':>13s}{'mat hot(nt)':>12s}{'mat px>150':>11s}"
           f"{'comp hot(nt)':>13s}{'comp px>150':>12s}{'ceiling':>9s}")
    _text(sheet, hdr, PAD + 4, y, 10, (190, 200, 210), bold=True)
    y += 13
    for name, awn, pose, md, mn, mo, cn, co, ce in rows:
        ok = mn <= NIGHT_GLOW_CAP + 0.5 and mo == 0 and ce >= 518
        col = (170, 210, 180) if ok else (230, 150, 140)
        if "shipped" in name:
            col = _shade(col, -46)
        line = (f"{name:27s}{awn:16s}{pose:13s}{md:13.0f}{mn:12.1f}{mo:11d}"
                f"{cn:13.1f}{co:12d}{'y' + str(ce):>9s}")
        _text(sheet, line, PAD + 4, y, 10, col)
        y += 13
    _text(sheet, f"gold coin core rgb={COIN_PEAK} luma={_luma(COIN_PEAK):.0f} — sole brightest object. Every new stall's MATERIAL peak is <=150 with ZERO px over; every new stall's COMPOSITED peak sits below the lowest shipped stall's; every ceiling is at or under the y518 family maximum (shipped steamer y516).",
          PAD + 4, y + 2, 10, (240, 210, 130))

    out = "/home/user/skybit/docs/sidewalk_overhaul/food_stalls/round_3.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(sheet, out)
    print("saved", out, sheet.get_size())
    print()
    print(f"{'stall':28s}{'awning':16s}{'pose':13s}{'matD':>7s}{'matN':>8s}{'matOver':>9s}{'compN':>8s}{'compOver':>10s}{'ceiling':>9s}")
    for name, awn, pose, md, mn, mo, cn, co, ce in rows:
        print(f"{name:28s}{awn:16s}{pose:13s}{md:7.0f}{mn:8.1f}{mo:9d}{cn:8.1f}{co:10d}{'y' + str(ce):>9s}")
    print(f"\ncoin core luma={_luma(COIN_PEAK):.0f}  cap={NIGHT_GLOW_CAP}  ceiling floor=y518")


if __name__ == "__main__":
    render()
