"""
Hurt-parrot concept: DEFIANT SNARL.

Thesis — "hurt, and coming for you anyway." Zero applied hardware: no
bandages, no soot, no cracked lenses, no comic dazing. The damage is read
purely off body language, because posture survives the 68x64 sprite scale
where any prop would turn to mush. Four levers do the work:

  * head + chest dropped and the head pushed forward, so Pip hunches INTO
    the screen instead of sagging away from it;
  * the lower mandible swung open off its hinge into a hard angular gape
    with a black interior — a shout, not a droop;
  * heavy brow wedges painted OVER the gold aviator rims, since the lenses
    own the face and anything drawn behind them is invisible;
  * the tail fan tightened and swept rearward, the silhouette cue for
    "bracing", plus a lower wing carry on every frame.

Built as a standalone exploration off `game.parrot._build_frame` so the
live sprite is untouched while the look is under review.
"""
import math
import os
import sys

# Run standalone from anywhere: this sheet lives outside the package, so the
# repo root has to be on the path before `game.*` resolves.
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "offscreen")

import pygame

pygame.init()

from game.draw import (
    BIRD_RED, BIRD_RED_D, BIRD_BELLY, BIRD_BEAK, BIRD_BEAK_D,
)
from game.parrot import SPRITE_W, SPRITE_H, _aaellipse, _build_wing, _add_outline

# Base wing angles carry a -5 deg offset so the wing sits lower through the
# whole cycle — a hunched, wound-up carry rather than the jaunty default.
_HURT_ANGLES = (5, -10, -25, -40)

# Head/beak ride 1 px forward and 2 px down; the body drops 2 px with them.
# Forward travel is capped at 1 px because the right aviator lens already
# reaches the sprite's right edge at the default anchor.
_HEAD_DX, _HEAD_DY = 1, 2
_BODY_DY = 2

BROW_DARK = (40, 8, 8)
BROW_EDGE = (120, 22, 22)          # thin lit top so the wedge beds into feathers
MOUTH_DARK = (15, 10, 10)

_JAW_HINGE = (52 + _HEAD_DX, 26 + _HEAD_DY)
_JAW_OPEN_DEG = 34.0

_TAIL_PIVOT = (22, 33)
_TAIL_SWEEP_DEG = 10.0
_TAIL_FLATTEN = 0.86


def _rot(p, pivot, deg, flatten=1.0):
    """Rotate about `pivot` in screen space (y down), optionally squashing
    vertically first. Positive `deg` lifts points that lie left of the pivot,
    which is the direction that sweeps the tail rearward."""
    x = p[0] - pivot[0]
    y = (p[1] - pivot[1]) * flatten
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return (pivot[0] + x * c - y * s, pivot[1] + x * s + y * c)


def _sweep_tail(p):
    return _rot((p[0], p[1] + _BODY_DY), _TAIL_PIVOT, _TAIL_SWEEP_DEG,
                _TAIL_FLATTEN)


def _draw_snarl_shades(surf, cx, cy):
    """Aviators re-anchored for this skin: the right lens sits +5 instead of
    +6 so the forward head shift doesn't push the gold rim off the canvas."""
    from game.parrot import SHADE_FRAME, SHADE_BLACK, SHADE_TINT, SHADE_GLINT

    r_outer = 6
    left = (cx - 4, cy)
    right = (cx + 5, cy - 1)

    pygame.draw.circle(surf, SHADE_FRAME, left, r_outer + 1)
    pygame.draw.circle(surf, SHADE_FRAME, right, r_outer + 1)
    pygame.draw.circle(surf, SHADE_BLACK, left, r_outer)
    pygame.draw.circle(surf, SHADE_BLACK, right, r_outer)
    tint = pygame.Surface((r_outer * 2, r_outer), pygame.SRCALPHA)
    pygame.draw.ellipse(tint, (*SHADE_TINT, 130), tint.get_rect())
    surf.blit(tint, (left[0] - r_outer, left[1] - r_outer + 1))
    surf.blit(tint, (right[0] - r_outer, right[1] - r_outer + 1))
    # Glints ride low on the lens: the brow wedge claims the upper third.
    pygame.draw.circle(surf, SHADE_GLINT, (left[0] - 2, left[1] + 1), 2)
    pygame.draw.circle(surf, SHADE_GLINT, (right[0] - 2, right[1] + 1), 2)
    pygame.draw.circle(surf, (255, 255, 255, 200), (left[0] + 2, left[1] + 3), 1)
    pygame.draw.circle(surf, (255, 255, 255, 200), (right[0] + 2, right[1] + 3), 1)
    pygame.draw.line(surf, SHADE_FRAME,
                     (left[0] + r_outer, left[1]),
                     (right[0] - r_outer, right[1]), 2)
    return left, right


def _brow_wedge(a, b, thick):
    """A downward-thickened quad from `a` to `b`. Filled rather than stroked so
    the wedge holds a solid 3 px mass at 1x — a stroked line anti-aliases away
    against the gold rim."""
    return [a, b, (b[0], b[1] + thick), (a[0], a[1] + thick)]


def _draw_brows(surf, head_c, head_rx, head_ry):
    """Both brow wedges, angled down toward the beak so they converge into a
    fierce V. Painted through a head-shaped mask: unclipped they would spill
    past the skull contour and leave stray pixels the outline pass would
    happily halo."""
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)

    rear = ((38.0, 15.0), (49.0, 19.5))
    front = ((50.0, 13.0), (61.0, 17.5))
    for a, b in (rear, front):
        pygame.draw.polygon(layer, BROW_DARK, _brow_wedge(a, b, 3.6))
        pygame.draw.line(layer, BROW_EDGE, a, b, 1)

    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _aaellipse(mask, (255, 255, 255, 255), head_c, head_rx, head_ry)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


def _draw_snarl_beak(surf):
    """Upper mandible fixed, lower mandible swung open off the hinge. The
    black wedge between them is built from the two jaw edges themselves, so
    the gape can never leak dark pixels outside the beak silhouette."""
    dx, dy = _HEAD_DX, _HEAD_DY
    hinge = _JAW_HINGE

    # Upper mandible: the macaw hook is kept intact, but its cutting edge
    # rises toward the tip so the gape widens forward instead of pinching —
    # a wedge-shaped opening reads as a shout, a parallel slit reads as a
    # seam.
    up_back = (53 + dx, 28 + dy)
    up_front = (59 + dx, 26.5 + dy)
    upper = [(52 + dx, 22 + dy), (57 + dx, 21 + dy), (62 + dx, 25 + dy),
             (61 + dx, 30 + dy), up_front, up_back]
    lower_flat = [(53 + dx, 28 + dy), (59 + dx, 29 + dy),
                  (58 + dx, 32 + dy), (52 + dx, 31 + dy)]
    lower = [_rot(p, hinge, _JAW_OPEN_DEG) for p in lower_flat]

    pygame.draw.polygon(surf, BIRD_BEAK, lower)
    pygame.draw.polygon(surf, BIRD_BEAK_D, lower, 1)
    pygame.draw.polygon(surf, BIRD_BEAK, upper)
    pygame.draw.polygon(surf, BIRD_BEAK_D, upper, 1)

    # Mouth cavity painted last: stroking the two jaws first and cutting the
    # cavity out of them afterwards keeps the 1 px jaw outlines from eating
    # the gap, which at this scale is the difference between an open snarl
    # and a closed beak with a seam.
    inset = 0.7
    cavity = [(up_back[0] + 0.6, up_back[1] + inset),
              (up_front[0] + 0.9, up_front[1] + inset),
              (up_front[0] - 0.4, up_front[1] + inset + 3.2),
              (lower[1][0] - 0.2, lower[1][1] - inset),
              (lower[0][0] + 0.6, lower[0][1] - inset * 0.4)]
    pygame.draw.polygon(surf, MOUTH_DARK, cavity)
    # Ridge gloss on the upper mandible only — the lower one is in shadow.
    pygame.draw.line(surf, (255, 230, 150),
                     (54 + dx, 23 + dy), (59 + dx, 25 + dy), 1)


def build_defiant_snarl_frame(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    tail_colors = [
        (200, 30, 40),
        (240, 95, 40),
        (255, 160, 55),
        (255, 220, 80),
    ]
    for i, c in enumerate(tail_colors):
        pts = [
            (2 + i * 3, 26 + i * 2),
            (14 + i, 24 + i),
            (20 + i, 30 + i * 2),
            (6 + i * 3, 36 + i * 2),
        ]
        pygame.draw.polygon(surf, c, [_sweep_tail(p) for p in pts])
    pygame.draw.line(surf, BIRD_RED_D,
                     _sweep_tail((4, 27)), _sweep_tail((18, 31)), 1)
    pygame.draw.line(surf, BIRD_RED_D,
                     _sweep_tail((6, 33)), _sweep_tail((20, 35)), 1)

    b = _BODY_DY
    _aaellipse(surf, (120, 20, 25), (34, 35 + b), 19, 14)
    _aaellipse(surf, BIRD_RED, (32, 32 + b), 19, 14)
    _aaellipse(surf, (255, 100, 100), (30, 29 + b), 13, 8)
    _aaellipse(surf, BIRD_BELLY, (28, 38 + b), 12, 6)
    sheen = pygame.Surface((28, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (255, 230, 230, 160), sheen.get_rect())
    surf.blit(sheen, (22, 21 + b))

    wing = _build_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(34, 28 + b)).topleft)

    hx, hy = 47 + _HEAD_DX, 21 + _HEAD_DY
    _aaellipse(surf, (150, 15, 20), (hx + 1, hy + 2), 12, 11)
    _aaellipse(surf, BIRD_RED, (hx, hy), 12, 11)
    _aaellipse(surf, (255, 130, 130), (hx - 3, hy + 3), 4, 3)
    _aaellipse(surf, (255, 170, 170), (hx - 1, hy - 5), 7, 3)

    _draw_snarl_shades(surf, 50 + _HEAD_DX, 20 + _HEAD_DY)
    _draw_brows(surf, (hx, hy), 12, 11)
    _draw_snarl_beak(surf)

    pygame.draw.line(surf, BIRD_BEAK_D, (28, 45 + b), (26, 49 + b), 2)
    pygame.draw.line(surf, BIRD_BEAK_D, (34, 45 + b), (36, 49 + b), 2)

    return surf


def build_frames():
    return [_add_outline(build_defiant_snarl_frame(a)) for a in _HURT_ANGLES]


# ── Review strip ─────────────────────────────────────────────────────────────

CELL_W, CELL_H = 68, 64
BG = (8, 8, 20)


def _verify(frame_idx, sprite):
    """Print-only legibility probes: the brow and gape are the two reads that
    must survive 1x, so they get counted rather than eyeballed."""
    w, h = sprite.get_size()
    brow_exact = brow_loose = gape = 0
    for y in range(h):
        for x in range(w):
            r, g, bl, a = sprite.get_at((x, y))
            if a < 16:
                continue
            if abs(r - BROW_DARK[0]) <= 12 and abs(g - BROW_DARK[1]) <= 12 \
                    and abs(bl - BROW_DARK[2]) <= 12:
                brow_exact += 1
            if y < 24 and r < 60 and g < 20:
                brow_loose += 1
            if abs(r - MOUTH_DARK[0]) <= 10 and abs(g - MOUTH_DARK[1]) <= 10 \
                    and abs(bl - MOUTH_DARK[2]) <= 10 and x > 46:
                gape += 1
    print(f"frame {frame_idx}: brow(exact)={brow_exact:4d}  "
          f"brow(dark-above-lens)={brow_loose:4d}  gape={gape:3d}")


def main():
    frames = build_frames()
    strip = pygame.Surface((CELL_W * len(frames), CELL_H))
    strip.fill(BG)
    for i, f in enumerate(frames):
        strip.blit(f, (i * CELL_W + (CELL_W - f.get_width()) // 2,
                       (CELL_H - f.get_height()) // 2))
        _verify(i, f)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "round_1.png")
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
