"""Correct 3D-projection crib model shared by the seat-design concepts.

Layering (back to front): opening interior + back rim  ->  parrot (clipped to
above-the-crib + inside-the-opening)  ->  full front wall (sticks + weave
courses, clipped out of the opening)  ->  lit front lip along the bottom arc.

The parrot can never overlay the front wall; the wall can never intrude into
the opening. Knobs: bird seat height / sprite, lip depth (lip_scale), wall
height (stick_bottom / courses), opening size (rim override).
"""
import math
import pygame
import _nestbase as nb


def lip_y(px, ecx, ecy, ra, rb, lip_scale=1.0):
    """Screen y of the opening's front (bottom) edge at column px, or None."""
    nx = (px - ecx) / ra
    if abs(nx) > 1.0: return None
    return ecy + rb * lip_scale * math.sqrt(1.0 - nx * nx)


def _geo(cy, rim=None):
    if rim is None:
        return nb.geo(cy)
    rx, ry_off, rw, rh = rim
    ry = cy + ry_off
    return rx, ry, rw, rh, rx + rw / 2.0, ry + rh / 2.0, rw / 2.0, rh / 2.0


def make_clipped_bird(cy, bird_dy=0, lip_scale=1.0, bird_img=None, rim=None):
    """Bird visible only above the crib or through the opening (down to the lip)."""
    rx, ry, rw, rh, ecx, ecy, ra, rb = _geo(cy, rim)
    img = bird_img if bird_img is not None else nb.BIRD
    bw, bh = img.get_size()
    bx, by = nb.CX - bw // 2, cy - bh // 2 + 5 + bird_dy
    out = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for sy in range(bh):
        py = by + sy
        for sx in range(bw):
            c = img.get_at((sx, sy))
            if c[3] == 0: continue
            px = bx + sx
            if py >= ry:
                ly = lip_y(px, ecx, ecy, ra, rb, lip_scale)
                inside = nb.t_ell(px, py, ecx, ecy, ra, rb) <= 1.02
                below_lip_ok = ly is not None and py <= ly
                if not (inside or below_lip_ok):
                    continue
            out.set_at((sx, sy), c)
    return out, bx, by


def wall_layer(surf_size, cy, courses=None, stick_bottom=None, lip_scale=1.0,
               rim=None):
    """Sticks + weave courses + notches, with every pixel that falls inside
    the opening removed — the wall hugs beneath the lip, never crosses it."""
    rx, ry, rw, rh, ecx, ecy, ra, rb = _geo(cy, rim)
    courses = courses if courses is not None else nb.COURSES
    stick_bottom = stick_bottom if stick_bottom is not None else nb.STICK_BOTTOM
    n = len(courses)
    layer = pygame.Surface(surf_size, pygame.SRCALPHA)
    for vx in nb.VERTS:
        nb._nest_stick_span(layer, vx, ry + rh, cy + stick_bottom)
    wins = {k: v for k, v in nb.STICK_WINS.items() if k[0] < n}
    nb._nest_weave(layer, cy, range(n), courses, wins)
    for ci in range(2, n):
        offset, col, x1, x2, sag = courses[ci]
        base_y = cy + offset
        for (cii, vx), w in wins.items():
            if cii == ci and w:
                nb._nest_stick_at_course(layer, vx, x1, x2, base_y, sag)
    nb._nest_notches(layer, cy, courses, wins)
    for x in range(rx, rx + rw + 1):
        ly = lip_y(x, ecx, ecy, ra, rb, lip_scale)
        if ly is None: continue
        for y in range(ry - 1, int(ly) + 1):
            layer.set_at((x, y), (0, 0, 0, 0))
    return layer


def draw_front_lip(surf, cy, thickness=1, color=None, lip_scale=1.0, rim=None):
    rx, ry, rw, rh, ecx, ecy, ra, rb = _geo(cy, rim)
    color = color or nb._NEST_TWIG_BRIGHT
    for x in range(rx, rx + rw + 1):
        ly = lip_y(x, ecx, ecy, ra, rb, lip_scale)
        if ly is None: continue
        for k in range(thickness):
            surf.set_at((x, int(ly) - k), color)


def draw_back_rim(surf, cy, rim=None):
    rx, ry, rw, rh, ecx, ecy, ra, rb = _geo(cy, rim)
    pygame.draw.arc(surf, nb._NEST_TWIG_MID, (rx, ry, rw, rh), 0, math.pi, 2)


def draw_crib(surf, cy, alive, interior_fn, bird_dy=0, lip_px=1, courses=None,
              lip_color=None, lip_scale=1.0, stick_bottom=None, bird_img=None,
              rim=None):
    interior_fn(surf, cy)
    draw_back_rim(surf, cy, rim)
    if alive:
        bird, bx, by = make_clipped_bird(cy, bird_dy, lip_scale, bird_img, rim)
        surf.blit(bird, (bx, by))
    surf.blit(wall_layer(surf.get_size(), cy, courses, stick_bottom, lip_scale,
                         rim), (0, 0))
    draw_front_lip(surf, cy, lip_px, lip_color, lip_scale, rim)
