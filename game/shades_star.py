"""STAR SHADES — gold/yellow star-shaped lenses, novelty eyewear.

Each lens is a filled 5-point star with a darker gold inset and a bright rim
so the silhouette reads even at 22px. Tuned smaller-armed than a decorative
star so it still scans as a lens covering the eye.
"""
import math
import pygame

_RIM    = (255, 250, 220)
_LENS   = (255, 206, 60)           # gold star glass
_LENS_D = (210, 150, 30)
_LENS_H = (255, 238, 150)
_GLINT  = (255, 255, 255)


def _star(surf, cx, cy, r, color, rot=-math.pi / 2, inner=0.46):
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * inner
        a = rot + i * math.pi / 5
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pygame.draw.polygon(surf, color, pts)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r = max(3, int(eye_w * 0.34))          # star outer radius
    sep = max(4, int(eye_w * 0.50))
    rim = max(1, int(eye_w * 0.06))

    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    for (lx, ly) in (far, near):
        _star(surf, lx, ly, r + rim, _RIM)
        _star(surf, lx, ly, r, _LENS)
        _star(surf, lx, ly, max(2, int(r * 0.62)), _LENS_D)
        # Upper-point sheen.
        pygame.draw.circle(surf, _LENS_H, (lx, ly - max(1, int(r * 0.45))),
                           max(1, int(r * 0.20)))

    # Bridge between the two stars.
    pygame.draw.line(surf, _RIM, (far[0] + f * (r // 2), cy),
                     (near[0] - f * (r // 2), cy), rim + 1)

    # Temple arm toward the ear.
    pygame.draw.line(surf, _RIM, (far[0] - f * (r // 2), cy),
                     (far[0] - f * (r // 2 + max(2, int(eye_w * 0.30))),
                      cy - max(1, int(eye_w * 0.07))), rim + 1)

    pygame.draw.circle(surf, _GLINT, (near[0] - f * (r // 3), cy - r // 3),
                       max(1, int(eye_w * 0.05)))
