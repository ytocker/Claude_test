"""HEART SHADES (festival / Lolita) — playful heart-shaped lenses.

Two filled heart lenses in thin gold rims with pink/magenta tinted glass,
joined by a bridge and a temple wire toward the ear. The heart silhouette
IS the read, so each lens is built as a FILLED gold heart (two top lobes +
a downward point) and then inset by the rim width with a tinted-pink heart
of glass — never a stroked outline, which stipples and breaks the point at
tiny radii. Everything scales off `eye_w` so the same code is a clean
product shot at eye_w=96 and still reads as a bold heart at eye_w=22.
"""
import math

import pygame

_RIM    = (244, 206, 110)           # warm gold metal
_RIM_H  = (255, 244, 196)           # bright top-lobe highlight
_RIM_D  = (182, 138, 58)            # underside / shadow side of the wire
_PINK_T = (255, 176, 214)           # bright pink top of the glass
_PINK_B = (206, 70, 150)            # deeper magenta floor (vertical fade)
_GLINT  = (255, 255, 255)


def _heart_points(cx, cy, r):
    """Polygon outline of a heart whose bounding span is ~2r wide, centred
    so (cx,cy) sits at the lens centre. Two lobe arcs sampled as points plus
    the bottom point — a polygon fills solidly at any size, where a curve
    stroke would thin out and drop pixels at the tip."""
    # Lobe geometry: two circles side by side, point reaching below them.
    lobe_r = r * 0.50
    lobe_y = cy - r * 0.28
    lx = cx - r * 0.46
    rx = cx + r * 0.46
    tip = (cx, cy + r * 0.94)

    pts = []
    # Left lobe: sweep over the top-left arc from the valley up and around.
    for deg in range(210, 410, 12):
        a = math.radians(deg)
        pts.append((lx + lobe_r * math.cos(a), lobe_y + lobe_r * math.sin(a)))
    # Down the right shoulder of the right lobe into the tip.
    for deg in range(130, 330, 12):
        a = math.radians(deg)
        pts.append((rx + lobe_r * math.cos(a), lobe_y + lobe_r * math.sin(a)))
    pts.append(tip)
    return pts


def _tinted_heart(r, top, bot, alpha, rim):
    """Glass heart inset by `rim`, with a vertical top→bot pink fade so the
    flat fill reads as curved candy glass."""
    size = int(r * 2.4)
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    grad = pygame.Surface((size, size), pygame.SRCALPHA)
    span = max(1, size - 1)
    for yy in range(size):
        t = yy / span
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t), alpha)
        pygame.draw.line(grad, c, (0, yy), (size, yy))
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    inner = max(2, r - rim)
    # Anchor the glass heart a touch low: the tip reaches further from centre
    # than the lobes, so a uniform inset would leave a fat gold band at the
    # point. Dropping the centroid keeps an even gold rim all the way around.
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        _heart_points(size / 2, size / 2 + rim * 0.5, inner))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    g.blit(grad, (0, 0))
    return g, size


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r    = max(3, int(eye_w * 0.26))
    sep  = max(4, int(eye_w * 0.46))
    rim  = max(1, int(eye_w * 0.075))
    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    # Bridge BEHIND the lenses so the heart lobes overlap it cleanly; the
    # lower pass is the gold catch-light underside.
    bx0 = far[0] + f * int(r * 0.30)
    bx1 = near[0] - f * int(r * 0.30)
    by = cy - max(1, int(r * 0.30))
    pygame.draw.line(surf, _RIM_D, (bx0, by + 1), (bx1, by + 1), max(1, rim))
    pygame.draw.line(surf, _RIM, (bx0, by), (bx1, by), max(1, rim))

    # Temple wire toward the ear (-facing).
    ex = far[0] - f * (r + max(2, int(eye_w * 0.30)))
    ey = cy - max(1, int(eye_w * 0.10))
    pygame.draw.line(surf, _RIM_D, (far[0] - f * int(r * 0.6), cy), (ex, ey),
                     max(1, rim))
    pygame.draw.line(surf, _RIM, (far[0] - f * int(r * 0.6), cy), (ex, ey),
                     max(1, rim - 1) or 1)

    for (lx, ly) in (far, near):
        # Solid gold heart = filled gold polygon (with a 1px-down shadow
        # copy for the wire underside), then the tinted glass heart inset.
        pygame.draw.polygon(surf, _RIM_D, _heart_points(lx, ly + 1, r))
        pygame.draw.polygon(surf, _RIM, _heart_points(lx, ly, r))
        glass, gs = _tinted_heart(r, _PINK_T, _PINK_B, 210, rim)
        surf.blit(glass, (lx - gs // 2, ly - gs // 2))
        # Bright crescent over the two top lobes so the gold pops off the head.
        hi = max(1, rim - 1) or 1
        pygame.draw.arc(surf, _RIM_H,
                        (lx - r * 0.96, ly - r * 0.78, r * 0.92, r * 0.92),
                        0.3, 2.9, hi)
        pygame.draw.arc(surf, _RIM_H,
                        (lx + r * 0.04, ly - r * 0.78, r * 0.92, r * 0.92),
                        0.3, 2.9, hi)

    # One pinprick glint on the near lens's left lobe — sells glossy candy glass.
    pygame.draw.circle(surf, _GLINT,
                       (int(near[0] - r * 0.34), int(cy - r * 0.30)),
                       max(1, int(eye_w * 0.055)))
