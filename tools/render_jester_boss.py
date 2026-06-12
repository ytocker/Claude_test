"""Look-dev mockup: the dice-clown presenter's EVOLVED "BOSS" form (ROUND 1).

The approved FRIENDLY presenter — tile #13 of `render_jester_variants.py`
("Plum & Lime — FINAL (no shadow)") — fronts an EASY route. This sheet explores
his EVOLVED BOSS form: the bigger, MEANER jester the player meets later, who
offers a MUCH HARDER route. The brief is a PLAYFUL-MENACING mini-boss (casual-
arcade, NOT horror-gore) who still reads as the SAME clown, evolved.

Panel 0 is the UNCHANGED original #13 (the friendly easy-route presenter) for
side-by-side comparison. Panels 1-5 are five distinct evolved bosses. Every
boss is:
  - PHYSICALLY LARGER — the whole jester FIGURE layer is rendered then scaled up
    ~1.3-1.45x inside a taller panel, while the real parrot stays the SAME size
    in every panel, so the boss visibly dwarfs both the parrot and #13.
  - MEANER — a `menace` face path: steeper low-angled brows, GLOWING eyes (a hot
    pupil + a coloured `blit_glow`), a wider jagged grin with bigger FANGS.
  - WRAPPED IN AN OMINOUS BODY AURA — a new `body_aura` helper layers radial
    glows (per-version dark-crimson / violet / black hue) BEHIND the figure, with
    a few floating ember/spark particles. This is the danger telegraph.
  - CORRUPTED in palette — #13's plum/lime/gold deepened + desaturated + pushed
    toward each version's aura hue, still recognisably the same clown.
  - STILL PRESENTING the route DIE (the 3D cube + its yellow aura, upper-LEFT,
    LEFT arm raised to it) — the offer is unchanged, only the offerer is.

Nothing under `game/` is touched; we import the real kit and mutate no state.
Headless + deterministic. Output: docs/jester/boss_round_1.png.

    PYTHONPATH=. python tools/render_jester_boss.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H
from game.draw import lerp_color, blit_glow
from game.parrot import get_parrot
from tools.render_warren_mockup import shaped_palette

from tools.render_clown_dice import (
    _shade, DAY_PHASE, SS, VIEW_W, VIEW_H, VIEW_FEET_Y,
    _round_head, _nose,
)

# The whole approved jester kit — body, pose, caps, collar, costume, the die +
# its yellow aura — is reused verbatim so the boss stays in the SAME family.
from tools.render_jester_variants import (
    build_jester, cap_four_point, _bell, _cap_point,
    draw_cupped_die, _cheek,
)


# ── palette corruption ────────────────────────────────────────────────────────
# #13's plum/lime/gold pushed toward each version's danger hue: deepen (drag
# toward black), desaturate (drag toward the channel mean), then tint toward the
# aura colour. Still the same three-role costume — just corrupted — so the boss
# reads as the SAME clown gone bad, never a brand-new character.

BASE = dict(dark=(96, 44, 150), light=(132, 218, 116), gold=(250, 205, 72))


def _desat(c, amt):
    g = sum(c) / 3.0
    return tuple(int(ch + (g - ch) * amt) for ch in c)


def _deepen(c, amt):
    return tuple(int(ch * (1.0 - amt)) for ch in c)


def corrupt(c, hue, *, deep=0.32, desat=0.34, tint=0.30):
    """Deepen + desaturate + tint a base costume colour toward the danger `hue`."""
    c = _deepen(c, deep)
    c = _desat(c, desat)
    return lerp_color(c, hue, tint)


def corrupt_palette(hue, **kw):
    return {k: corrupt(v, hue, **kw) for k, v in BASE.items()}


# ── ominous body aura (the danger telegraph) ─────────────────────────────────
# A layered radial glow BEHIND the whole figure plus a few floating embers. The
# core reads on VALUE (a dark vignette ring that darkens the sky behind the boss)
# so the menace survives any sky, with an additive coloured bloom on top for the
# "corruption" colour pop. `breathe` pulses it so the aura looks alive.

def body_aura(surf, cx, cy, radius, hue, breathe, *, dark=(8, 4, 12),
              embers=True, seed=0):
    """Paint a breathing corruption halo centred on the boss torso. Two passes:
    an ALPHA dark→hue vignette (reads on value, telegraphs "danger" on any sky),
    then an additive coloured bloom for the glow, then drifting ember sparks."""
    size = radius * 2 + 4
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = radius + 2
    # Dark→hue alpha vignette. Outer edge is the deep danger dark fading to
    # nothing; the body of the halo carries the version hue. Drawn large→small so
    # inner rings overpaint, feathering each band into the next.
    stops = [
        (1.00, dark, 0),
        (0.86, dark, 150),
        (0.62, hue, 165),
        (0.40, hue, 120),
        (0.20, _shade(hue, 60), 70),
    ]
    for t_out, col, a_in in stops:
        r = max(1, int(radius * t_out))
        steps = max(4, r // 5)
        for k in range(steps):
            rr = int(r * (1 - k / steps))
            if rr < 1:
                break
            a = int(a_in * (k / steps) ** 0.5)
            a = min(255, int(a * (0.80 + 0.20 * breathe)))
            pygame.draw.circle(s, (*col, a), (c, c), rr)
    surf.blit(s, (cx - c, cy - c))
    # Additive coloured bloom layered on top so the corruption hue GLOWS (pops
    # off the value vignette without washing it flat).
    blit_glow(surf, cx, cy, int(radius * 0.62 * (1.0 + 0.06 * breathe)),
              _shade(hue, 70), alpha=46 + int(26 * breathe))

    if not embers:
        return
    # A few floating ember/spark particles rising out of the aura — the boss is
    # smouldering. Deterministic angles/radii per `seed` so the sheet is stable.
    rng = __import__('random').Random(seed * 977 + 3)
    ember_col = _shade(hue, 120)
    for i in range(7):
        a0 = rng.uniform(0, math.tau)
        rad = radius * rng.uniform(0.45, 0.92)
        drift = breathe * 8 + i * 3
        ex = int(cx + math.cos(a0) * rad)
        ey = int(cy + math.sin(a0) * rad * 0.82) - int(drift % 14)
        tw = 0.5 + 0.5 * math.sin(breathe * 6.0 + i * 1.7)
        sz = 2 + int(2 * tw)
        spark = pygame.Surface((sz * 4, sz * 4), pygame.SRCALPHA)
        al = int(120 + 120 * tw)
        pygame.draw.circle(spark, (*ember_col, al), (sz * 2, sz * 2), sz)
        pygame.draw.circle(spark, (255, 240, 220, al), (sz * 2, sz * 2),
                           max(1, sz // 2))
        surf.blit(spark, (ex - sz * 2, ey - sz * 2),
                  special_flags=pygame.BLEND_ADD)


# ── the MEAN boss face (overrides the friendly #13 face) ─────────────────────
# A `menace` path: keep the SAME face anatomy as #13 (so it's the same clown) but
# swing every cue to MEAN — steep low brows knitting toward the nose, GLOWING
# eyes (a coloured glow under a hot slit pupil), and a WIDE JAGGED grin with two
# big fangs. The friendly #13 face stays untouched (panel 0 uses `naughty_face`).

def _glow_eye(surf, x, y, glow_col, *, look, narrow=False):
    """A menacing GLOWING eye: a coloured glow halo, a dark socket, then a hot
    bright slit pupil shoved toward the die (sidelong). `narrow` gives the hollow,
    quieter wraith read (a thin glowing slit, no full sclera)."""
    blit_glow(surf, x, y, 7, glow_col, alpha=150)
    if narrow:
        # Hollow glowing slit — no white sclera. Reads cold + empty.
        pygame.draw.ellipse(surf, (10, 8, 14), (x - 5, y - 3, 10, 7))
        pygame.draw.ellipse(surf, glow_col, (x - 4 + look, y - 2, 6, 4))
        pygame.draw.circle(surf, (255, 255, 255),
                           (x + look, y), 1)
        return
    # Dark recessed socket so the glow reads as light coming FROM the eye.
    pygame.draw.ellipse(surf, (16, 10, 18), (x - 6, y - 5, 12, 11))
    # Hot bright pupil (the glow's source) jammed to the die-side corner.
    px = x + look
    pygame.draw.circle(surf, glow_col, (px, y + 1), 4)
    pygame.draw.circle(surf, _shade(glow_col, 130), (px, y + 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (px - 1, y - 1), 1)


def menace_face(surf, cx, hy, hr, *, nose_col, glow_col, fang_xtra=0,
                narrow_eyes=False):
    """Paint the MEAN boss expression. SAME geometry as #13's naughty_face — the
    nose, the cheeks, the lopsided sly mouth seat — so it's clearly the same
    clown, but every cue swung MEAN: steep low brows knitting toward the nose,
    glowing eyes, a wider JAGGED grin with two big fangs. `fang_xtra` lengthens
    the fangs (demon read); `narrow_eyes` gives the hollow wraith slit."""
    ex = max(6, hr // 2)
    look = -3
    _cheek(surf, cx, hy + 5, hr, strong=False)

    for s in (-1, 1):
        exx = cx + s * ex
        _glow_eye(surf, exx, hy, glow_col, look=look, narrow=narrow_eyes)
        # MEAN brow — the universal anger shape #13 was carefully kept OUT of:
        # the INNER (nose-side) end drops LOW and the outer rides high, knitting
        # into a hard down-and-in "V" over the nose. Heavy dark ink for weight.
        inner = (exx - s * 1, hy - 8)        # inner end LOW (anger)
        outer = (exx + s * 11, hy - 17)      # outer end HIGH
        pygame.draw.line(surf, (24, 14, 22), inner, outer, 3)
        # A second short stroke thickening the inner knit so the scowl reads bold.
        pygame.draw.line(surf, (24, 14, 22), inner,
                         (exx - s * 4, hy - 10), 3)

    _nose(surf, cx, hy + 3, 4, nose_col)

    # A WIDER, more JAGGED open grin than #13 — a snarl. The die-side corner still
    # rides highest (lopsided sly), but the lip is a sawtooth and TWO big fangs
    # drop from the tooth row for the mean edge.
    mw = 13
    my = hy + 12
    l_corner = (cx - mw - 1, my - 3)
    r_corner = (cx + mw, my - 1)
    bottom = (cx, my + 10)
    mouth_poly = [l_corner, (cx - 6, my + 1), (cx + 6, my + 1), r_corner,
                  (cx + 7, my + 5), bottom, (cx - 7, my + 5)]
    pygame.draw.polygon(surf, (84, 16, 28), mouth_poly)
    # Jagged tooth band along the top of the grin (a row of points, not a smooth
    # band) so the grin reads as a snarl.
    top_teeth = [l_corner]
    for k in range(7):
        t = k / 6.0
        tx = l_corner[0] + (r_corner[0] - l_corner[0]) * t
        ty = my + (0 if k % 2 == 0 else 3)
        top_teeth.append((tx, ty))
    top_teeth.append((r_corner[0], r_corner[1] + 3))
    top_teeth.append((l_corner[0], l_corner[1] + 3))
    pygame.draw.polygon(surf, (250, 246, 236), top_teeth)
    pygame.draw.polygon(surf, _shade((250, 246, 236), -80), top_teeth, 1)
    # TWO big fangs hanging into the dark mouth (one each side), longer than #13's
    # single fang. `fang_xtra` drops them further for the demon read.
    for fs in (-1, 1):
        fx = cx + fs * 6
        fang = [(fx - 2, my + 3), (fx + 2, my + 3),
                (fx, my + 9 + fang_xtra)]
        pygame.draw.polygon(surf, (252, 250, 244), fang)
        pygame.draw.polygon(surf, _shade((252, 250, 244), -80), fang, 1)
    # The lip as a tight MEAN crescent — corners flicked up, centre dipped, but
    # drawn in a darker bloodier line than #13's friendly MOUTH.
    lip = []
    for k in range(13):
        t = k / 12.0
        lx = l_corner[0] - 2 + (r_corner[0] + 2 - (l_corner[0] - 2)) * t
        ly = (l_corner[1] - 2) + ((r_corner[1] - 1) - (l_corner[1] - 2)) * t \
            + (1.0 - (2.0 * t - 1.0) ** 2) * 10.0
        lip.append((lx, ly))
    pygame.draw.lines(surf, (150, 30, 44), False, lip, 3)


# ── boss cap add-ons (horns / taller crown) ──────────────────────────────────
# Drawn as wrappers that first lay the approved four-point cap, then add the
# version-specific menace silhouette (small horns through the cap, or a taller
# crown-spike) so each boss owns a distinct head shape while staying a jester.

def _horn(surf, base, tip, col):
    """A small curved menace horn — a tapered dark cone with a lit front edge."""
    bx, by = base
    tx, ty = tip
    midx = (bx + tx) // 2 + (4 if tx > bx else -4)
    midy = (by + ty) // 2
    pts = [(bx - 4, by), (bx + 4, by), (midx + 2, midy), (tx, ty)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, _shade(col, 40),
                        [(bx - 4, by), (bx, by), (midx, midy), (tx, ty)])
    pygame.draw.polygon(surf, _shade(col, -70), pts, 2)


def cap_demon(surf, cx, base_y, hr, cols):
    """The approved four-point fool's cap with two small horns pushed THROUGH it —
    the demon-jester read."""
    cap_four_point(surf, cx, base_y, hr, cols)
    horn = (28, 18, 30)
    _horn(surf, (cx - 13, base_y - 4), (cx - 24, base_y - 26), horn)
    _horn(surf, (cx + 13, base_y - 4), (cx + 24, base_y - 26), horn)


def cap_crown(surf, cx, base_y, hr, cols):
    """A taller, more COMMANDING cap for the Genie-King boss: the four-point cap
    plus a central upright crown-spike rising between the points (regal menace),
    each tipped with a dark-gold bell. Reads as a king's fool, not a floppy one."""
    a, b, c, d = cols
    # Central tall spike FIRST so the splayed points overlap its base.
    spike = [(cx - 9, base_y - 2), (cx + 9, base_y - 2),
             (cx + 4, base_y - 40), (cx - 4, base_y - 40)]
    pygame.draw.polygon(surf, a, spike)
    pygame.draw.polygon(surf, _shade(a, 45),
                        [(cx - 9, base_y - 2), (cx - 1, base_y - 2),
                         (cx - 2, base_y - 40)])
    pygame.draw.polygon(surf, _shade(a, -65), spike, 2)
    _bell(surf, cx, base_y - 42, r=4, col=_shade(c, -10))
    # Two tall side prongs flanking the spike — a three-pronged crown silhouette.
    for s in (-1, 1):
        _cap_point(surf, cx, base_y, hr, s * 26, -22, b, span=12)


# ── the boss head (menace face + version cap) ────────────────────────────────
# Mirrors render_jester_variants._draw_tilted_head but routes through menace_face
# instead of the friendly naughty_face, and lets each version override the cap.

def _draw_boss_head(surf, cx, cy, hr, skin, cap_fn, cap_cols, tilt_deg,
                    *, nose_col, glow_col, fang_xtra=0, narrow_eyes=False):
    pad = 80
    scratch = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    sx, sy = pad, pad
    _round_head(scratch, sx, sy, hr, skin, blush=False)
    cap_fn(scratch, sx, sy - hr + 7, hr, cap_cols)
    menace_face(scratch, sx, sy, hr, nose_col=nose_col, glow_col=glow_col,
                fang_xtra=fang_xtra, narrow_eyes=narrow_eyes)
    rot = pygame.transform.rotate(scratch, tilt_deg)
    surf.blit(rot, (cx - rot.get_width() // 2, cy - rot.get_height() // 2))


def build_boss(surf, cx, feet_y, hand_up, *, dark, light, gold, cap_fn,
               glow_col, nose_col=(150, 30, 30), fang_xtra=0,
               narrow_eyes=False, skin=(214, 168, 150)):
    """Draw the EVOLVED boss jester: the approved chunky body/pose from
    build_jester, but with the costume's HEAD swapped for the menace head. We
    reuse build_jester for everything from the neck down (so the body, pose,
    collar, costume, harlequin legs and presenting arms are pixel-family with
    #13), then OVER-draw the boss head on top with the mean glowing face + the
    version cap. `skin` is dulled toward a corpse-grey so the face reads corrupted.
    """
    # Body, pose, collar, costume, legs, arms — straight from the approved kit so
    # the boss is unmistakably the same jester. Its friendly head is then painted
    # OVER by the menace head below (same head seat math as build_jester).
    build_jester(surf, cx, feet_y, hand_up, dark=dark, light=light, gold=gold,
                 cap_fn=cap_four_point, motif="quartered", collar="scalloped",
                 variant="browcock", collar_in_gold=True, skin=skin,
                 nose_col=nose_col)
    # Re-derive the head seat exactly as build_jester does, then over-draw the
    # mean glowing boss head + the version cap on top of the friendly one.
    hip_dx = -6
    hip_y = feet_y - 84
    hip_cx = cx + hip_dx
    neck_y = hip_y - 50
    hr = 22
    head_cx = hip_cx - 4
    hy_center = neck_y - hr
    cap_cols = (dark, light, gold, dark)
    _draw_boss_head(surf, head_cx, hy_center, hr, skin, cap_fn, cap_cols, -8,
                    nose_col=nose_col, glow_col=glow_col, fang_xtra=fang_xtra,
                    narrow_eyes=narrow_eyes)


# ── the five evolved bosses ──────────────────────────────────────────────────
# Each entry: a corrupted palette tinted toward its danger hue, an aura hue +
# dark, a version cap, the eye-glow colour and face flavour, and a FIGURE SCALE
# (how much bigger than #13 the boss looms). Panel 0 is the untouched #13.

CRIMSON = (150, 24, 24)
VIOLET = (118, 30, 158)
FIRE = (224, 96, 20)
SMOKE = (40, 36, 52)
PURPLE = (96, 36, 168)

BOSSES = [
    # 1 — THE BRUTE: bulked + hunched, deep-red corrupted palette, red glowing
    # eyes, dark-red body aura. The widest, most looming silhouette.
    dict(name="The Brute", vibe="bigger · hunched · dark-red aura · red eyes",
         pal=corrupt_palette(CRIMSON, deep=0.40, desat=0.30, tint=0.34),
         aura_hue=(150, 20, 20), aura_dark=(20, 4, 6), glow=(255, 70, 50),
         cap=cap_four_point, scale=1.46, fang_xtra=2),
    # 2 — THE CORRUPTED: violet-black corruption, eerie magenta eye-glow, sharper
    # teeth (extra-jagged grin reads via the bigger fangs). Cracked-seam palette.
    dict(name="The Corrupted",
         vibe="violet-black corruption · magenta glow · seams",
         pal=corrupt_palette(VIOLET, deep=0.34, desat=0.46, tint=0.40),
         aura_hue=(120, 24, 150), aura_dark=(14, 4, 18), glow=(236, 70, 230),
         cap=cap_four_point, scale=1.34, fang_xtra=1, seams=True),
    # 3 — THE DEMON JESTER: small horns through the cap, fiery red/orange aura,
    # glowing YELLOW eyes, prominent long fangs.
    dict(name="The Demon Jester",
         vibe="horns · fiery aura · yellow eyes · long fangs",
         pal=corrupt_palette(FIRE, deep=0.30, desat=0.24, tint=0.30),
         aura_hue=(214, 70, 16), aura_dark=(22, 6, 2), glow=(255, 206, 40),
         cap=cap_demon, scale=1.38, fang_xtra=4),
    # 4 — THE SHADOW WRAITH: darkened near-silhouette, cold smoky-black aura,
    # hollow glowing eyes. Ominous + quiet (no embers — it's still).
    dict(name="The Shadow Wraith",
         vibe="near-silhouette · cold smoke · hollow eyes",
         pal=corrupt_palette(SMOKE, deep=0.62, desat=0.62, tint=0.45),
         aura_hue=(44, 40, 64), aura_dark=(4, 4, 8), glow=(120, 200, 220),
         cap=cap_four_point, scale=1.40, narrow_eyes=True, embers=False,
         skin=(150, 140, 150)),
    # 5 — THE GENIE KING (boss): regal dark-gold menace, taller crown cap,
    # commanding purple aura, a sly evil grin. The climactic hard-route boss.
    dict(name="The Genie King",
         vibe="crown · commanding purple aura · regal menace",
         pal={**corrupt_palette(PURPLE, deep=0.30, desat=0.26, tint=0.30),
              "gold": (212, 158, 40)},
         aura_hue=(108, 36, 188), aura_dark=(12, 4, 24), glow=(210, 120, 255),
         cap=cap_crown, scale=1.42, fang_xtra=1),
]


# ── per-cell scene ────────────────────────────────────────────────────────────
# A taller-than-source panel (so the bigger bosses fit), the same day clearing,
# the boss figure rendered onto its own layer then SCALED UP and composited over
# its body aura, the route die floating upper-left, and the real parrot un-scaled
# for the size comparison.

PANEL_W = VIEW_W
PANEL_H = VIEW_H + 56          # taller so the looming bosses are not clipped
FEET_Y = PANEL_H - 26


def _scene_bg(big, bw, bh, idx):
    palette = shaped_palette(DAY_PHASE)
    g_y = int(FEET_Y * SS) + 6 * SS
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        pygame.draw.line(big, lerp_color(palette['sky_mid'],
                                         palette['sky_bot'], t), (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        pygame.draw.line(big, lerp_color(palette['ground_top'],
                                         palette['ground_mid'], t), (0, y),
                         (bw, y))
    pygame.draw.line(big, _shade(palette['ground_top'], 15), (0, g_y), (bw, g_y))
    hill = pygame.Surface((bw, 30 * SS), pygame.SRCALPHA)
    hc = _shade(palette['ground_mid'], 22)
    for hx, hw, hh in ((40, 90, 18), (130, 110, 22), (185, 80, 16)):
        pygame.draw.ellipse(hill, (*hc, 160),
                            ((hx - hw) * SS, 0, hw * 2 * SS, hh * 2 * SS))
    big.blit(hill, (0, g_y - 14 * SS))
    tuft = _shade(palette['ground_top'], 22)
    rng = __import__('random').Random(idx * 131 + 7)
    for _ in range(10):
        tx = rng.randint(8, PANEL_W - 8) * SS
        ty = g_y + rng.randint(3, max(4, bh // SS - FEET_Y - 4)) * SS
        for k in (-3, 0, 3):
            pygame.draw.line(big, tuft, (tx + k * SS, ty),
                             (tx + k * SS, ty - rng.randint(4, 7) * SS),
                             max(1, SS))


def render_original(idx):
    """Panel 0: the UNCHANGED #13 friendly presenter, drawn in this taller panel
    at the SAME figure size as the source sheet (no scale-up), for comparison."""
    bw, bh = PANEL_W * SS, PANEL_H * SS
    big = pygame.Surface((bw, bh))
    _scene_bg(big, bw, bh, idx)

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    jester_cx = PANEL_W // 2 + 12
    die_x = jester_cx - 66
    die_base_y = 36
    hand_up = (die_x + 6, 76 + (PANEL_H - VIEW_H))
    # The #13 spec verbatim (friendly face), seated so its FEET land on FEET_Y.
    build_jester(layer, jester_cx, FEET_Y, hand_up,
                 dark=BASE['dark'], light=BASE['light'], gold=BASE['gold'],
                 cap_fn=cap_four_point, motif="quartered", collar="scalloped",
                 variant="browcock", collar_in_gold=True)
    draw_cupped_die(layer, die_x, die_base_y, idx * 1.7 + 2.0)
    _blit_parrot(layer)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


def _blit_parrot(layer):
    """The real parrot, ALWAYS the same size, low on the RIGHT — the scale ruler
    that proves the bosses dwarf both it and #13."""
    bird = get_parrot(1, -10)
    bird = pygame.transform.smoothscale(
        bird, (int(bird.get_width() * 0.92), int(bird.get_height() * 0.92)))
    layer.blit(bird, (PANEL_W - 22 - bird.get_width() // 2,
                      (FEET_Y - 64) - bird.get_height() // 2))


def render_boss(spec, idx):
    bw, bh = PANEL_W * SS, PANEL_H * SS
    big = pygame.Surface((bw, bh))
    _scene_bg(big, bw, bh, idx)

    layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    jester_cx = PANEL_W // 2 + 12
    die_x = jester_cx - 66
    die_base_y = 36

    breathe = 0.5 + 0.5 * math.sin((idx * 1.7 + 2.0) * 1.3)

    # OMINOUS BODY AURA first, behind the figure — centred on the torso, scaled
    # with the boss so the bigger bosses carry a bigger halo. Drawn straight onto
    # the supersampled `big` so the soft radial falloff stays smooth.
    scale = spec["scale"]
    torso_x = int(jester_cx * SS)
    torso_y = int((FEET_Y - 64) * SS)
    aura_r = int(96 * scale * SS)
    body_aura(big, torso_x, torso_y, aura_r, spec["aura_hue"], breathe,
              dark=spec["aura_dark"], embers=spec.get("embers", True), seed=idx)

    # The boss FIGURE on its own transparent layer so we can scale it UP (bigger
    # = more menacing) while the parrot + die stay at base size. Feet are seated
    # at a virtual baseline that, after scaling about the feet, lands on FEET_Y.
    fig = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    base_feet = FEET_Y
    hand_up = (die_x + 6, 76 + (PANEL_H - VIEW_H))
    pal = spec["pal"]
    build_boss(fig, jester_cx, base_feet, hand_up,
               dark=pal["dark"], light=pal["light"], gold=pal["gold"],
               cap_fn=spec["cap"], glow_col=spec["glow"],
               fang_xtra=spec.get("fang_xtra", 0),
               narrow_eyes=spec.get("narrow_eyes", False),
               skin=spec.get("skin", (214, 168, 150)))
    if spec.get("seams"):
        _add_seams(fig, jester_cx, base_feet, spec["glow"])

    # Scale the figure layer up ABOUT THE FEET so the boss looms taller/broader
    # but stays planted on the ground line. Anchor the scaled surface so the feet
    # pixel-column stays put and the extra height grows UPWARD.
    sw, sh = int(PANEL_W * scale), int(PANEL_H * scale)
    fig_big = pygame.transform.smoothscale(fig, (sw, sh))
    off_x = int(jester_cx - jester_cx * scale)
    off_y = int(base_feet - base_feet * scale)
    layer.blit(fig_big, (off_x, off_y))

    # The route DIE + its yellow aura, unchanged, floating upper-left at BASE
    # scale (the offer the boss presents is identical to #13's).
    draw_cupped_die(layer, die_x, die_base_y, idx * 1.7 + 2.0)
    _blit_parrot(layer)

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (PANEL_W, PANEL_H))


def _add_seams(surf, cx, feet_y, glow):
    """Glowing corruption CRACKS across the Corrupted boss's torso — a few
    branching bright seams so the body reads as fracturing with corruption."""
    hip_y = feet_y - 84
    top = hip_y - 50
    rng = __import__('random').Random(424)
    for _ in range(4):
        x0 = cx + rng.randint(-22, 22)
        y0 = top + rng.randint(2, 8)
        pts = [(x0, y0)]
        for _ in range(3):
            x0 += rng.randint(-6, 6)
            y0 += rng.randint(8, 16)
            pts.append((x0, y0))
        pygame.draw.lines(surf, _shade(glow, 60), False, pts, 2)
        pygame.draw.lines(surf, (255, 240, 255), False, pts, 1)


# ── sheet layout ──────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cells = []
    captions = []
    cells.append(render_original(0))
    captions.append(("current — EASY route", "#13 plum/lime · friendly grin "
                     "· the un-evolved presenter"))
    for i, spec in enumerate(BOSSES, start=1):
        cells.append(render_boss(spec, i))
        captions.append((spec["name"], spec["vibe"]))

    cols, rows = 3, 2
    sw, sh = int(PANEL_W * 3.1), int(PANEL_H * 3.1)

    PAD = 48
    GAP = 26
    TITLE_H = 100
    CAP_H = 70
    FOOT_H = PANEL_H + 40

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((20, 16, 24))

    f_title = pygame.font.SysFont(None, 74, bold=True)
    f_sub = pygame.font.SysFont(None, 32, bold=True)
    f_cap = pygame.font.SysFont(None, 40, bold=True)
    f_caps = pygame.font.SysFont(None, 28, bold=True)

    title = f_title.render(
        "DICE JESTER — EVOLVED BOSS form (round 1)", True, (252, 226, 226))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "Panel 0 = the approved FRIENDLY #13 (easy route). Panels 1-5 = the "
        "MEANER, LARGER boss who offers a MUCH HARDER route — each bulked + "
        "looming (parrot kept at the SAME size for scale), with a glowing-eye "
        "fanged menace face, an ominous breathing BODY AURA + embers, and a "
        "corrupted plum/lime/gold palette. Still presents the route die.",
        True, (196, 190, 200))
    canvas.blit(sub, (PAD, PAD + 54))

    y0 = PAD + TITLE_H
    strongest = None
    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        border = (210, 60, 60) if i == 4 else (70, 60, 80)  # ring the strongest
        pygame.draw.rect(canvas, border,
                         pygame.Rect(cx - 2, cy - 2, sw + 4, sh + 4), 2)
        canvas.blit(scaled, (cx, cy))
        name, vibe = captions[i]
        tag = "0. " + name if i == 0 else f"{i}. {name}"
        cap = f_cap.render(tag, True, (245, 220, 200))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 8))
        sub2 = f_caps.render(vibe, True, (190, 184, 196))
        canvas.blit(sub2, (cx + (sw - sub2.get_width()) // 2, cy + sh + 42))
        if i == 5:
            strongest = cell      # the Genie King — the climactic boss

    # 1x inset proving the strongest evolved boss reads at in-game scale.
    if strongest is not None:
        foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 16
        ix = PAD
        pygame.draw.rect(canvas, (210, 60, 60),
                         pygame.Rect(ix - 2, foot_y - 2, PANEL_W + 4,
                                     PANEL_H + 4), 2)
        canvas.blit(strongest, (ix, foot_y))
        tag = f_cap.render(
            "1x in-game scale (The Genie King, the climactic hard-route boss) — "
            "proving the looming silhouette, the breathing dark-purple body aura, "
            "the crown cap and the glowing-eye fanged menace face still read at "
            "the size the player meets him.",
            True, (206, 200, 210))
        # Wrap the tag across two lines beside the inset.
        canvas.blit(tag, (ix + PANEL_W + 24, foot_y + PANEL_H // 2 - 14))

    out_dir = os.path.join("docs", "jester")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "boss_round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
