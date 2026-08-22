"""Correct 3D-projection crib model shared by the seat-design concepts.

Layering (back to front): opening interior + back rim  ->  parrot (clipped to
above-the-crib + inside-the-opening)  ->  full front wall (sticks + ALL weave
courses, clipped out of the opening)  ->  lit front lip along the bottom arc.

The parrot can never overlay the front wall; the wall can never intrude into
the opening.
"""
import math
import pygame
import _nestbase as nb


def lip_y(px, ecx, ecy, ra, rb):
    """Screen y of the opening's front (bottom) edge at column px, or None."""
    nx = (px - ecx) / ra
    if abs(nx) > 1.0: return None
    return ecy + rb * math.sqrt(1.0 - nx * nx)


def make_clipped_bird(cy, bird_dy=0):
    """Bird visible only above the crib or through the opening."""
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    bx, by = nb.CX - nb.BW // 2, cy - nb.BH // 2 + 5 + bird_dy
    out = pygame.Surface((nb.BW, nb.BH), pygame.SRCALPHA)
    for sy in range(nb.BH):
        py = by + sy
        for sx in range(nb.BW):
            c = nb.BIRD.get_at((sx, sy))
            if c[3] == 0: continue
            px = bx + sx
            if py >= ry and nb.t_ell(px, py, ecx, ecy, ra, rb) > 1.02:
                continue
            out.set_at((sx, sy), c)
    return out, bx, by


def wall_layer(surf_size, cy, courses=None):
    """Sticks + all five weave courses + notches, with every pixel that falls
    inside the opening removed — the wall hugs beneath the lip, never crosses it."""
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    courses = courses if courses is not None else nb.COURSES
    layer = pygame.Surface(surf_size, pygame.SRCALPHA)
    for vx in nb.VERTS:
        nb._nest_stick_span(layer, vx, ry + rh, cy + nb.STICK_BOTTOM)
    nb._nest_weave(layer, cy, (0, 1, 2, 3, 4), courses, nb.STICK_WINS)
    for ci in (2, 3, 4):
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        for (cii, vx), wins in nb.STICK_WINS.items():
            if cii == ci and wins:
                nb._nest_stick_at_course(layer, vx, x1, x2, base_y, sag)
    nb._nest_notches(layer, cy, courses, nb.STICK_WINS)
    for x in range(rx, rx + rw + 1):
        ly = lip_y(x, ecx, ecy, ra, rb)
        if ly is None: continue
        for y in range(ry - 1, int(ly) + 1):
            layer.set_at((x, y), (0, 0, 0, 0))
    return layer


def draw_front_lip(surf, cy, thickness=1, color=None):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    color = color or nb._NEST_TWIG_BRIGHT
    for x in range(rx, rx + rw + 1):
        ly = lip_y(x, ecx, ecy, ra, rb)
        if ly is None: continue
        for k in range(thickness):
            surf.set_at((x, int(ly) - k), color)


def draw_back_rim(surf, cy):
    rx, ry, rw, rh, ecx, ecy, ra, rb = nb.geo(cy)
    pygame.draw.arc(surf, nb._NEST_TWIG_MID, (rx, ry, rw, rh), 0, math.pi, 2)


def draw_crib(surf, cy, alive, interior_fn, bird_dy=0, lip_px=1,
              courses=None, lip_color=None):
    interior_fn(surf, cy)
    draw_back_rim(surf, cy)
    if alive:
        bird, bx, by = make_clipped_bird(cy, bird_dy)
        surf.blit(bird, (bx, by))
    surf.blit(wall_layer(surf.get_size(), cy, courses), (0, 0))
    draw_front_lip(surf, cy, lip_px, lip_color)
