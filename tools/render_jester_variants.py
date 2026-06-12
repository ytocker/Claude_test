"""Look-dev mockup: 10 NEW Court Jester power-up dice presenters.

The user loved the Court Jester from the dice-clown sheet for its sly,
"up-to-something / NAUGHTY" read. This sheet explores TEN higher-quality
takes on that ONE archetype — each a large hero jester standing in the day
clearing (sky + grass + the real parrot for scale), presenting a glowing
power-up die. Everything is drawn from pygame primitives; we import the REAL
game helpers (biome palette, glow cache, live parrot) and the chunky body
kit from the dice-clown mockup, and mutate no game state.

THE FIXED POSE (identical on all ten — a hard requirement): the die floats in
the upper-LEFT focal slot, the viewer's-LEFT arm (`cx - …`) is raised
diagonally up presenting an open offering glove toward the die, and the
viewer's-RIGHT arm (`cx + …`) hangs straight down. This MIRRORS the original
jester (which raised its right arm to a die at upper-right). The die's
power-up treatment is kept EXACTLY consistent across all ten: classic d6 pips,
gold glow halo (BLEND_ADD), top-left rim light, gentle bob, orbiting sparkles.

Each cell is supersampled 2x then smoothscaled for crisp anti-aliasing.

    PYTHONPATH=. python tools/render_jester_variants.py
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

# Reuse the chunky mascot body kit + the consistent floating-die prop from the
# dice-clown mockup so these jesters read as the SAME family of casual mascots
# and the power-up die is pixel-identical to the approved treatment.
from tools.render_clown_dice import (
    _shade, _poly, _facet_body, _round_head, _nose, _arm, _leg, _shoes,
    _shadow, draw_floating_die, RIM, WHITE, INK, ROSY,
    DAY_PHASE, SS, VIEW_W, VIEW_H, VIEW_FEET_Y,
)


# ── the NAUGHTY face kit ──────────────────────────────────────────────────────
# The signature of this archetype is a MISCHIEVOUS, scheming read — never the
# plain happy smile-arcs of the original. Each jester gets one of these sly
# expression treatments, all built from the same friendly-but-cheeky vocabulary
# (round highlighted eyes that never read as empty sockets, a tilted knowing
# brow, an asymmetric curl of mouth, a round nose specular, a cheek blush).

def _brow(surf, x, y, w, tilt, color=INK, weight=3):
    """One angled eyebrow — the single biggest lever on a scheming read. `tilt`
    in pixels raises the inner end (negative) or outer end (positive)."""
    pygame.draw.line(surf, color, (x - w, y + tilt), (x + w, y - tilt), weight)


def _cheek(surf, cx, cy, r, *, strong=False):
    """Warm cheek blush discs so the mischief always reads charming, not cold."""
    for s in (-1, 1):
        a = 210 if strong else 150
        blush = pygame.Surface((16, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(blush, (*ROSY, a), blush.get_rect())
        surf.blit(blush, (cx + s * (r - 7) - 8, cy + 1))


def _pupil(surf, x, y, *, look=0, big=4):
    """A round highlighted eye whose pupil can glance sideways (`look` shifts
    the dark pupil within the white) for a sly sidelong read."""
    pygame.draw.circle(surf, WHITE, (x, y), big)
    pygame.draw.circle(surf, _shade(WHITE, -30), (x, y), big, 1)
    pygame.draw.circle(surf, (44, 40, 58), (x + look, y + 1), max(2, big - 2))
    pygame.draw.circle(surf, WHITE, (x + look - 1, y - 1), 1)


def naughty_face(surf, cx, hy, hr, *, style, nose_col=(232, 72, 72)):
    """Paint one of several MISCHIEVOUS expressions. Every style keeps the
    round nose + a cheek blush so the jester stays appealing; the eyes, brows
    and mouth carry the specific scheming flavour."""
    ex = max(6, hr // 2)

    if style == "smirk":
        # Half-lidded sly smirk: heavy upper lids, sidelong pupils, one corner
        # of the mouth pulled up.
        _cheek(surf, cx, hy + 3, hr)
        for s in (-1, 1):
            _pupil(surf, cx + s * ex, hy, look=2, big=4)
            # Heavy lid skims the top of the eye for a half-lidded look.
            pygame.draw.line(surf, INK, (cx + s * ex - 5, hy - 3),
                             (cx + s * ex + 5, hy - 4), 2)
            _brow(surf, cx + s * ex, hy - 9, 6, -2)
        _nose(surf, cx, hy + 6, 6, nose_col)
        # Asymmetric grin: flat-ish left, curling up hard on the right.
        pygame.draw.arc(surf, (195, 60, 70), (cx - 9, hy + 8, 22, 12),
                        math.pi * 1.15, math.tau * 0.99, 3)

    elif style == "raised_brow":
        # ONE eyebrow cocked high — the classic "oh really?" scheming look.
        _cheek(surf, cx, hy + 3, hr)
        _pupil(surf, cx - ex, hy, look=1, big=4)
        _pupil(surf, cx + ex, hy, look=1, big=4)
        _brow(surf, cx - ex, hy - 11, 6, 1)        # level brow
        _brow(surf, cx + ex, hy - 13, 6, -3, weight=3)  # cocked high + angled
        _nose(surf, cx, hy + 6, 6, nose_col)
        pygame.draw.arc(surf, (195, 60, 70), (cx - 9, hy + 8, 20, 11),
                        math.pi * 1.08, math.tau * 0.96, 3)

    elif style == "sidelong":
        # Both pupils slide hard to the side (toward the die) — caught plotting.
        _cheek(surf, cx, hy + 3, hr)
        for s in (-1, 1):
            _pupil(surf, cx + s * ex, hy, look=-3, big=4)
            _brow(surf, cx + s * ex, hy - 9, 6, -2 if s < 0 else -1)
        _nose(surf, cx, hy + 6, 6, nose_col)
        # Knowing closed-mouth curl.
        pygame.draw.arc(surf, (195, 60, 70), (cx - 8, hy + 9, 20, 10),
                        math.pi * 1.2, math.tau * 0.98, 3)

    elif style == "tongue":
        # Cheeky tongue poking out the corner — playful taunt.
        _cheek(surf, cx, hy + 3, hr, strong=True)
        for s in (-1, 1):
            _pupil(surf, cx + s * ex, hy, look=s, big=4)
            _brow(surf, cx + s * ex, hy - 9, 6, -2)
        _nose(surf, cx, hy + 6, 6, nose_col)
        pygame.draw.arc(surf, (195, 60, 70), (cx - 9, hy + 8, 20, 11),
                        math.pi * 1.05, math.tau * 0.97, 3)
        # Tongue tip out the right corner.
        pygame.draw.ellipse(surf, (236, 120, 130), (cx + 6, hy + 14, 8, 7))
        pygame.draw.ellipse(surf, _shade((236, 120, 130), -45),
                            (cx + 6, hy + 14, 8, 7), 1)

    elif style == "wink":
        # A big cheeky wink — one eye a happy crescent, the other wide.
        _cheek(surf, cx, hy + 3, hr, strong=True)
        # Open eye (left).
        _pupil(surf, cx - ex, hy, look=2, big=5)
        _brow(surf, cx - ex, hy - 10, 6, 1)
        # Winking eye (right): downward crescent arc.
        pygame.draw.arc(surf, INK, (cx + ex - 6, hy - 4, 12, 10),
                        math.pi * 0.1, math.pi * 0.9, 3)
        _brow(surf, cx + ex, hy - 11, 6, -3)
        _nose(surf, cx, hy + 6, 6, nose_col)
        pygame.draw.arc(surf, (195, 60, 70), (cx - 9, hy + 8, 22, 12),
                        math.pi * 1.1, math.tau * 0.99, 3)

    else:  # "grin" — scheming open grin with a glint
        _cheek(surf, cx, hy + 3, hr, strong=True)
        for s in (-1, 1):
            _pupil(surf, cx + s * ex, hy, look=1, big=5)
            # Twinkle glint top-right of each eye.
            pygame.draw.circle(surf, WHITE, (cx + s * ex + 2, hy - 3), 1)
            _brow(surf, cx + s * ex, hy - 10, 6, -2)
        _nose(surf, cx, hy + 6, 6, nose_col)
        # Wide scheming grin with a little tooth line.
        rect = (cx - 11, hy + 7, 22, 13)
        pygame.draw.arc(surf, (195, 60, 70), rect,
                        math.pi * 1.02, math.tau * 0.98, 3)
        pygame.draw.line(surf, WHITE, (cx - 7, hy + 13), (cx + 7, hy + 13), 2)


# ── belled-cap kit ────────────────────────────────────────────────────────────
# The fool's cap is the jester's loudest silhouette cue. Each variation owns a
# distinct cap shape, every one finished with belled tips (a lit specular on
# each bell so they read as gold spheres, not flat discs).

def _bell(surf, x, y, r=4, col=(245, 240, 200)):
    pygame.draw.circle(surf, _shade(col, -55), (x, y), r + 1)
    pygame.draw.circle(surf, col, (x, y), r)
    pygame.draw.circle(surf, _shade(col, 80), (x - 1, y - 1), max(1, r // 2))


def _cap_point(surf, cx, base_y, hr, dx, dy, col, *, span=16):
    """One drooping cap point as a triangle from the head crown to a belled
    tip, with a lit top-left facet + dark keyline."""
    bx, by = cx + dx, base_y + dy
    pts = [(cx - span, base_y + 2), (cx + span, base_y + 2), (bx, by)]
    pygame.draw.polygon(surf, col, pts)
    pygame.draw.polygon(surf, _shade(col, 50),
                        [(cx - span, base_y + 2), (cx + span // 2, base_y + 2),
                         (bx, by)])
    pygame.draw.polygon(surf, _shade(col, -60), pts, 2)
    _bell(surf, bx, by)


def cap_three_point(surf, cx, base_y, hr, cols):
    """Classic drooping three-point belled cap."""
    a, b, c = cols[0], cols[1], cols[2]
    _cap_point(surf, cx, base_y, hr, -28, -28, a)
    _cap_point(surf, cx, base_y, hr, 0, -40, b)
    _cap_point(surf, cx, base_y, hr, 28, -28, c)


def cap_four_point(surf, cx, base_y, hr, cols):
    """Four shorter belled points fanned across the crown."""
    a, b, c, _d = cols
    _cap_point(surf, cx, base_y, hr, -30, -22, a, span=18)
    _cap_point(surf, cx, base_y, hr, -11, -36, b, span=18)
    _cap_point(surf, cx, base_y, hr, 11, -36, c, span=18)
    _cap_point(surf, cx, base_y, hr, 30, -22, a, span=18)


def cap_donkey(surf, cx, base_y, hr, cols):
    """Two tall donkey-ear points sweeping up and out, belled tips."""
    a, b = cols[0], cols[1]
    _cap_point(surf, cx, base_y, hr, -26, -46, a, span=13)
    _cap_point(surf, cx, base_y, hr, 26, -46, b, span=13)
    # Low band cap joining the ears.
    pygame.draw.arc(surf, _shade(a, -20), (cx - 18, base_y - 14, 36, 22),
                    math.pi, math.tau, 4)


def cap_coxcomb(surf, cx, base_y, hr, cols):
    """Rooster-crest coxcomb: a row of stiff scalloped lobes along the crown."""
    a, b = cols[0], cols[1]
    lobes = [(-22, -16), (-9, -30), (5, -34), (18, -22)]
    for i, (dx, dy) in enumerate(lobes):
        col = a if i % 2 == 0 else b
        bx, by = cx + dx, base_y + dy
        pygame.draw.circle(surf, _shade(col, -55), (bx, by), 9)
        pygame.draw.circle(surf, col, (bx, by), 8)
        pygame.draw.circle(surf, _shade(col, 55), (bx - 2, by - 2), 3)
    # A bell dangling off the crest tip.
    _bell(surf, cx + 22, base_y - 14)


def cap_hood(surf, cx, base_y, hr, cols):
    """Curled close hood with a single long forward-curling belled point."""
    a = cols[0]
    pygame.draw.ellipse(surf, _shade(a, -30), (cx - hr - 1, base_y - 18,
                                               hr * 2 + 2, 26))
    pygame.draw.ellipse(surf, a, (cx - hr, base_y - 18, hr * 2, 24))
    pygame.draw.arc(surf, _shade(a, 45), (cx - hr + 3, base_y - 16, hr, 14),
                    math.pi, math.tau, 2)
    # Long forward-curling point sweeping right then dropping a bell.
    pts = [(cx - 6, base_y - 14), (cx + 8, base_y - 16),
           (cx + 30, base_y - 30), (cx + 24, base_y - 14),
           (cx + 10, base_y - 6)]
    pygame.draw.polygon(surf, _shade(a, 20), pts)
    pygame.draw.polygon(surf, _shade(a, -55), pts, 2)
    _bell(surf, cx + 30, base_y - 30)


def cap_horned(surf, cx, base_y, hr, cols):
    """Low two-horn hood — short devilish horns curling out, belled tips. Reads
    a touch more impish for the darker palettes."""
    a, b = cols[0], cols[1]
    pygame.draw.ellipse(surf, _shade(a, -30), (cx - hr - 1, base_y - 12,
                                               hr * 2 + 2, 20))
    pygame.draw.ellipse(surf, a, (cx - hr, base_y - 12, hr * 2, 18))
    for s, col in ((-1, a), (1, b)):
        bx, by = cx + s * 22, base_y - 28
        pts = [(cx + s * 12, base_y - 6), (cx + s * 20, base_y - 6),
               (bx, by)]
        pygame.draw.polygon(surf, col, pts)
        pygame.draw.polygon(surf, _shade(col, 45),
                            [(cx + s * 12, base_y - 6),
                             (cx + s * 16, base_y - 6), (bx, by)])
        pygame.draw.polygon(surf, _shade(col, -60), pts, 2)
        _bell(surf, bx, by, r=3)


# ── collar kit ────────────────────────────────────────────────────────────────

def _collar_belled(surf, cx, neck_y, gold, n=3):
    """The original drooping belled-collar points hanging off the neck."""
    span = (n - 1) // 2
    for s in range(-span, span + 1):
        tx = cx + s * 15
        _poly(surf, gold, [(cx, neck_y), (tx - 6, neck_y + 16),
                           (tx + 6, neck_y + 16)], oc=_shade(gold, -60))
        _bell(surf, tx, neck_y + 17, r=3, col=(240, 235, 200))


def _collar_scalloped(surf, cx, neck_y, col, r=22, lobes=9):
    """A scalloped ruff-style collar: a row of overlapping lobes ringing the
    neck with lit tops + a small dangling bell at each outer edge."""
    for i in range(lobes):
        t = i / (lobes - 1)
        lx = int(cx - r + 2 * r * t)
        ly = int(neck_y + 5 + math.sin(t * math.pi) * -3)
        rad = 8
        pygame.draw.circle(surf, _shade(col, -50), (lx, ly), rad)
        pygame.draw.circle(surf, col, (lx, ly), rad - 1)
        pygame.draw.circle(surf, _shade(col, 55), (lx - 2, ly - 2), 3)
    for s in (-1, 1):
        _bell(surf, cx + s * (r + 2), neck_y + 8, r=3, col=(240, 235, 200))


# ── the unified jester builder ────────────────────────────────────────────────
# Every variation funnels through ONE builder so the MIRRORED POSE is literally
# identical across all ten: die upper-LEFT, LEFT arm raised to it, RIGHT arm
# hanging straight down. Only the palette / cap / costume-motif / collar / face
# differ. This is the hard pose requirement, enforced in code.

def build_jester(surf, cx, feet_y, hand_up, *, dark, light, gold,
                 cap_fn, motif, collar, face_style, skin=(255, 209, 169),
                 nose_col=(232, 72, 72)):
    """Draw ONE chunky court jester in the fixed mirrored presenting pose.

    `hand_up` is the upper-LEFT die-side target the LEFT arm reaches toward;
    the RIGHT arm always hangs straight down (mirror of the original jester's
    down-arm). `motif` selects the costume split style; the rest are kit fns."""
    hip_y = feet_y - 92

    _shoes(surf, cx, feet_y, 14, 26, _shade(dark, -10),
           toe=_shade(gold, 10))
    # Two-tone tights — left leg light, right leg dark (mirrors the body split).
    _leg(surf, (cx - 7, hip_y), (cx - 13, feet_y - 9), 12, light)
    _leg(surf, (cx + 7, hip_y), (cx + 13, feet_y - 9), 12, dark)

    neck_y = hip_y - 52
    _draw_costume(surf, cx, hip_y, dark, light, gold, motif)

    # POSE — the hard requirement. LEFT arm (cx - …) raised up to the die;
    # RIGHT arm (cx + …) hangs straight DOWN. Arms swap the two tones for a
    # motley flourish (raised arm = dark to read against the bright sky/die).
    _arm(surf, (cx - 25, hip_y - 46), hand_up, 8, dark, up=True)
    _arm(surf, (cx + 25, hip_y - 48), (cx + 33, hip_y - 6), 8, light)

    # Collar.
    if collar == "scalloped":
        _collar_scalloped(surf, cx, neck_y, _shade(light, 10))
    else:
        _collar_belled(surf, cx, neck_y, gold)

    hr = 22
    hy = neck_y - hr
    _round_head(surf, cx, hy, hr, skin, blush=False)
    # Cap drawn BEFORE the face so droops never cover the eyes; crown band on
    # top of the head ties it down.
    cap_fn(surf, cx, hy - hr, hr, (dark, light, gold, dark))
    naughty_face(surf, cx, hy, hr, style=face_style, nose_col=nose_col)


def _draw_costume(surf, cx, hip_y, dark, light, gold, motif):
    """The torso, varied by motif. All share a faceted, dimensional read."""
    seam = (250, 248, 235)
    top = hip_y - 52
    if motif == "split":
        # Vertical split halves: left light, right dark.
        _facet_body(surf, [(cx - 28, hip_y + 10), (cx, hip_y + 10),
                           (cx, top), (cx - 18, top)], light)
        _facet_body(surf, [(cx, hip_y + 10), (cx + 28, hip_y + 10),
                           (cx + 18, top), (cx, top)], dark)
        pygame.draw.line(surf, seam, (cx, top + 2), (cx, hip_y + 8), 2)
    elif motif == "quartered":
        # Four quarters alternating tones around the chest centre.
        midy = (top + hip_y + 10) // 2
        quads = [((cx - 28, hip_y + 10), (cx, hip_y + 10), (cx, midy),
                  (cx - 23, midy), dark),
                 ((cx, hip_y + 10), (cx + 28, hip_y + 10), (cx + 23, midy),
                  (cx, midy), light),
                 ((cx - 23, midy), (cx, midy), (cx, top), (cx - 18, top),
                  light),
                 ((cx, midy), (cx + 23, midy), (cx + 18, top), (cx, top),
                  dark)]
        for *pts, col in quads:
            _facet_body(surf, list(pts), col)
        pygame.draw.line(surf, seam, (cx, top + 2), (cx, hip_y + 8), 2)
        pygame.draw.line(surf, seam, (cx - 25, midy), (cx + 25, midy), 2)
    elif motif == "panels":
        # Vertical two-tone panel stripes.
        _facet_body(surf, [(cx - 28, hip_y + 10), (cx + 28, hip_y + 10),
                           (cx + 18, top), (cx - 18, top)], dark)
        for i in range(-2, 3, 2):
            px = cx + i * 11
            pygame.draw.polygon(surf, light,
                                [(px - 4, hip_y + 9), (px + 4, hip_y + 9),
                                 (px + 3, top + 1), (px - 3, top + 1)])
    else:  # "scalloped" hem split body
        _facet_body(surf, [(cx - 28, hip_y + 6), (cx, hip_y + 6),
                           (cx, top), (cx - 18, top)], dark)
        _facet_body(surf, [(cx, hip_y + 6), (cx + 28, hip_y + 6),
                           (cx + 18, top), (cx, top)], light)
        pygame.draw.line(surf, seam, (cx, top + 2), (cx, hip_y + 6), 2)
        # Scalloped hem lobes along the bottom edge.
        for i in range(-3, 4):
            hx = cx + i * 8
            col = light if (i + hip_y) % 2 else dark
            pygame.draw.circle(surf, _shade(col, -30), (hx, hip_y + 7), 5)
            pygame.draw.circle(surf, col, (hx, hip_y + 7), 4)
    # Gold belt buttons along the waist on every motif.
    for i in range(7):
        bx = cx - 21 + i * 7
        pygame.draw.circle(surf, _shade(gold, -55), (bx, hip_y + 6), 3)
        pygame.draw.circle(surf, gold, (bx, hip_y + 6), 3)
        pygame.draw.circle(surf, _shade(gold, 70), (bx - 1, hip_y + 5), 1)


# ── the ten jester variations ────────────────────────────────────────────────
# Deep two-tone split + gold accents; NO diamonds (those belong to the
# Harlequin). Each varies palette / cap / costume motif / collar / expression
# so all ten read distinctly while sharing the one mirrored presenting pose.

JESTERS = [
    ("Plum & Lime", dict(
        dark=(86, 38, 138), light=(126, 214, 110), gold=(250, 205, 72),
        cap_fn=cap_three_point, motif="split", collar="belled",
        face_style="smirk")),
    ("Crimson & Cream", dict(
        dark=(186, 36, 52), light=(244, 234, 210), gold=(244, 198, 78),
        cap_fn=cap_four_point, motif="quartered", collar="scalloped",
        face_style="raised_brow")),
    ("Royal Blue & Gold", dict(
        dark=(40, 70, 162), light=(248, 206, 88), gold=(252, 226, 130),
        cap_fn=cap_donkey, motif="panels", collar="belled",
        face_style="sidelong")),
    ("Teal & Magenta", dict(
        dark=(28, 130, 138), light=(220, 70, 150), gold=(250, 210, 90),
        cap_fn=cap_coxcomb, motif="split", collar="scalloped",
        face_style="wink")),
    ("Black & Scarlet", dict(
        dark=(34, 30, 42), light=(214, 44, 52), gold=(248, 206, 96),
        cap_fn=cap_horned, motif="quartered", collar="belled",
        face_style="grin")),
    ("Violet & Orange", dict(
        dark=(110, 52, 168), light=(244, 144, 56), gold=(250, 214, 96),
        cap_fn=cap_coxcomb, motif="panels", collar="scalloped",
        face_style="tongue")),
    ("Forest & Gold", dict(
        dark=(34, 104, 64), light=(246, 200, 78), gold=(252, 224, 124),
        cap_fn=cap_three_point, motif="scalloped", collar="belled",
        face_style="smirk")),
    ("Wine & Teal", dict(
        dark=(122, 30, 64), light=(58, 178, 178), gold=(250, 208, 86),
        cap_fn=cap_hood, motif="split", collar="scalloped",
        face_style="raised_brow")),
    ("Indigo & Lime", dict(
        dark=(54, 48, 140), light=(150, 220, 90), gold=(250, 210, 84),
        cap_fn=cap_four_point, motif="panels", collar="belled",
        face_style="sidelong")),
    ("Charcoal & Red", dict(
        dark=(48, 46, 58), light=(212, 56, 60), gold=(246, 202, 92),
        cap_fn=cap_horned, motif="quartered", collar="scalloped",
        face_style="wink")),
]


# ── per-cell gameplay scene (mirrored: die upper-LEFT) ───────────────────────

def render_cell(spec, idx, show_inset):
    """One tight day-clearing scene at SS supersample: sky + a sliver of grass
    + cast shadow, the chunky jester filling ~70-80% of the cell, the head-sized
    power-up die in the upper-LEFT focal slot, and the real parrot for scale.
    Returns VIEW_W x VIEW_H."""
    palette = shaped_palette(DAY_PHASE)
    bw, bh = VIEW_W * SS, VIEW_H * SS
    big = pygame.Surface((bw, bh))

    g_y = int(VIEW_FEET_Y * SS) + 6 * SS
    for y in range(g_y):
        t = 0.45 + 0.55 * (y / g_y)
        c = lerp_color(palette['sky_mid'], palette['sky_bot'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
    for y in range(g_y, bh):
        t = (y - g_y) / max(1, bh - g_y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(big, c, (0, y), (bw, y))
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
        tx = rng.randint(8, VIEW_W - 8) * SS
        ty = g_y + rng.randint(3, max(4, bh // SS - VIEW_FEET_Y - 4)) * SS
        for k in (-3, 0, 3):
            pygame.draw.line(big, tuft, (tx + k * SS, ty),
                             (tx + k * SS, ty - rng.randint(4, 7) * SS),
                             max(1, SS))

    layer = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
    # Figure nudged RIGHT of centre so the die has clear sky in the upper-LEFT
    # to float in, fully off the head silhouette (mirror of the original).
    jester_cx = VIEW_W // 2 + 12
    feet_y = VIEW_FEET_Y
    _shadow(layer, jester_cx, feet_y, 96)

    # The die floats in the clear UPPER-LEFT corner; the raised LEFT hand reaches
    # up toward it from below-right (the jester-side base of the die).
    die_x = jester_cx - 66
    die_base_y = 46
    hand_up = (die_x + 26, die_base_y + 32)

    build_jester(layer, jester_cx, feet_y, hand_up, **spec)

    pulse = idx * 1.7 + 2.0
    draw_floating_die(layer, die_x, die_base_y, pulse, show_inset=show_inset)

    # Real parrot flying in low from the RIGHT for scale, clear of the figure
    # and the upper-left die.
    bird = get_parrot(1, -10)
    bird = pygame.transform.smoothscale(
        bird, (int(bird.get_width() * 0.92), int(bird.get_height() * 0.92)))
    layer.blit(bird, (VIEW_W - 22 - bird.get_width() // 2,
                      (feet_y - 64) - bird.get_height() // 2))

    big.blit(pygame.transform.smoothscale(layer, (bw, bh)), (0, 0))
    return pygame.transform.smoothscale(big, (VIEW_W, VIEW_H))


CAPTIONS = [
    "plum/lime · 3-point cap · sly smirk",
    "crimson/cream · 4-point cap · raised brow",
    "royal-blue/gold · donkey-ear cap · sidelong glance",
    "teal/magenta · coxcomb crest · cheeky wink",
    "black/scarlet · horned hood · scheming grin",
    "violet/orange · coxcomb crest · tongue-out",
    "forest/gold · 3-point cap · sly smirk",
    "wine/teal · curled hood · raised brow",
    "indigo/lime · 4-point cap · sidelong glance",
    "charcoal/red · horned hood · cheeky wink",
]


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))

    cols, rows = 5, 2
    sw, sh = int(VIEW_W * 1.88), int(VIEW_H * 1.88)

    PAD = 44
    GAP = 22
    TITLE_H = 92
    CAP_H = 64
    FOOT_H = VIEW_H + 28

    canvas_w = PAD * 2 + cols * sw + (cols - 1) * GAP
    canvas_h = (PAD * 2 + TITLE_H + rows * (sh + CAP_H) + (rows - 1) * GAP
                + FOOT_H)
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((24, 22, 30))

    f_title = pygame.font.SysFont(None, 70, bold=True)
    f_sub = pygame.font.SysFont(None, 32, bold=True)
    f_cap = pygame.font.SysFont(None, 38, bold=True)
    f_caps = pygame.font.SysFont(None, 28, bold=True)

    title = f_title.render("COURT JESTER — naughty dice presenter (10 takes)",
                           True, (250, 240, 210))
    canvas.blit(title, (PAD, PAD - 2))
    sub = f_sub.render(
        "MIRRORED pose on all 10: die floats UPPER-LEFT · LEFT arm raised to "
        "it · RIGHT arm hangs down · each jester plotting something",
        True, (190, 195, 205))
    canvas.blit(sub, (PAD, PAD + 50))

    # Show the rolled-result inset in a couple of cells to hint the mechanic.
    inset_cells = {0, 9}

    y0 = PAD + TITLE_H
    template_cell = None
    for i, (name, spec) in enumerate(JESTERS):
        r, c = divmod(i, cols)
        cx = PAD + c * (sw + GAP)
        cy = y0 + r * (sh + CAP_H + GAP)
        cell = render_cell(spec, i, show_inset=(i in inset_cells))
        if i == 0:
            template_cell = cell
        scaled = pygame.transform.smoothscale(cell, (sw, sh))
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(cx - 1, cy - 1, sw + 2, sh + 2), 1)
        canvas.blit(scaled, (cx, cy))
        cap = f_cap.render(f"{i + 1}. {name}", True, (235, 225, 165))
        canvas.blit(cap, (cx + (sw - cap.get_width()) // 2, cy + sh + 6))
        sub2 = f_caps.render(CAPTIONS[i], True, (190, 196, 206))
        canvas.blit(sub2, (cx + (sw - sub2.get_width()) // 2, cy + sh + 38))

    # ONE 1x legibility inset proving the design reads at in-game scale.
    if template_cell is not None:
        foot_y = y0 + rows * (sh + CAP_H) + (rows - 1) * GAP + 14
        ix = PAD
        pygame.draw.rect(canvas, (70, 76, 96),
                         pygame.Rect(ix - 2, foot_y - 2, VIEW_W + 4,
                                     VIEW_H + 4), 1)
        canvas.blit(template_cell, (ix, foot_y))
        tag = f_cap.render(
            "1x in-game scale (Plum & Lime) — die stays a clear takeable "
            "pickup in the upper-left, fully off the face",
            True, (200, 206, 216))
        canvas.blit(tag, (ix + VIEW_W + 24, foot_y + VIEW_H // 2 - 14))

    out_dir = os.path.join("docs", "jester")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")


if __name__ == "__main__":
    main()
