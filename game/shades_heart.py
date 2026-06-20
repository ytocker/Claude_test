"""HEART SHADES — pink heart-shaped lenses, playful novelty eyewear.

The heart silhouette must survive downscale, so each lens is built as two
filled circles (the lobes) plus a triangle point, drawn at a hand-tuned size
relative to ``eye_w`` with a bright white frame outline carrying the shape.
"""
import pygame

_FRAME   = (255, 250, 252)         # white plastic rim
_LENS    = (255, 110, 170)         # bubblegum pink
_LENS_H  = (255, 175, 210)         # upper-lobe sheen
_LENS_D  = (220, 70, 130)
_GLINT   = (255, 255, 255)


def _heart(surf, cx, cy, w, color):
    """Filled heart centred so its widest span is ~``w``. Two lobes + a point."""
    lobe_r = max(1, int(w * 0.30))
    lobe_y = cy - max(1, int(w * 0.10))
    lx = cx - lobe_r + 1
    rx = cx + lobe_r - 1
    pygame.draw.circle(surf, color, (int(lx), int(lobe_y)), lobe_r)
    pygame.draw.circle(surf, color, (int(rx), int(lobe_y)), lobe_r)
    tip_y = cy + max(2, int(w * 0.46))
    pygame.draw.polygon(surf, color, [
        (cx - lobe_r - lobe_r // 2 + 1, lobe_y),
        (cx + lobe_r + lobe_r // 2 - 1, lobe_y),
        (cx, tip_y),
    ])


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(4, int(eye_w * 0.56))          # heart span per lens
    sep = max(4, int(eye_w * 0.50))
    rim = max(1, int(eye_w * 0.07))

    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    for (lx, ly) in (far, near):
        # White frame underlay (slightly larger heart) gives the rim.
        _heart(surf, lx, ly, w + rim * 2, _FRAME)
        _heart(surf, lx, ly, w, _LENS)
        # Lobe sheen + deeper point shadow for a glossy candy look.
        pygame.draw.circle(surf, _LENS_H,
                           (lx - max(1, int(w * 0.18)), ly - max(1, int(w * 0.10))),
                           max(1, int(w * 0.16)))
        pygame.draw.polygon(surf, _LENS_D, [
            (lx, ly + max(1, int(w * 0.12))),
            (lx + max(1, int(w * 0.18)), ly + max(1, int(w * 0.22))),
            (lx, ly + max(2, int(w * 0.46))),
        ])

    # Pink bridge dipping between the two hearts.
    pygame.draw.line(surf, _FRAME, (far[0] + f * (w // 3), cy - w // 4),
                     (near[0] - f * (w // 3), cy - w // 4), rim + 1)

    # Temple arm.
    pygame.draw.line(surf, _FRAME, (far[0] - f * (w // 2), cy),
                     (far[0] - f * (w // 2 + max(2, int(eye_w * 0.32))),
                      cy - max(1, int(eye_w * 0.08))), rim + 1)

    pygame.draw.circle(surf, _GLINT,
                       (near[0] - max(1, int(w * 0.20)), cy - max(1, int(w * 0.14))),
                       max(1, int(eye_w * 0.05)))
