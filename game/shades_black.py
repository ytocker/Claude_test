"""BLACK SHADES (wayfarer) — bold angular trapezoid black lenses, thick frame.

The cool factor lives in the chunky frame and the hard trapezoid lens shape
with one diagonal sheen streak. Built from polygons so the angular wayfarer
canting survives downscale where a rounded rect would mush.
"""
import pygame

_FRAME   = (16, 16, 22)
_FRAME_H = (70, 72, 86)            # top-rim catch-light so black lifts off navy
_LENS    = (32, 32, 42)
_LENS_D  = (12, 12, 18)
_SHEEN   = (150, 165, 200)


def _trapezoid(cx, cy, w, h, drop):
    """Wayfarer lens quad: wider/taller at the outer-top, canted down to the
    inner-bottom by ``drop``. Returned as a polygon point list."""
    hw, hh = w / 2, h / 2
    return [
        (cx - hw, cy - hh),
        (cx + hw, cy - hh + drop * 0.2),
        (cx + hw - w * 0.12, cy + hh),
        (cx - hw + w * 0.04, cy + hh - drop),
    ]


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw = max(4, int(eye_w * 0.42))         # lens width
    lh = max(4, int(eye_w * 0.40))         # lens height
    sep = max(4, int(eye_w * 0.42))
    drop = max(1, int(eye_w * 0.10))

    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    for (lx, ly) in (far, near):
        outer = _trapezoid(lx, ly, lw + max(2, int(eye_w * 0.10)),
                           lh + max(2, int(eye_w * 0.10)), drop)
        # mirror the quad's inner cant toward the beak (facing flips x)
        outer = [(lx + (px - lx) * f, py) for (px, py) in outer]
        pygame.draw.polygon(surf, _FRAME, outer)

    for (lx, ly) in (far, near):
        lens = _trapezoid(lx, ly, lw, lh, drop)
        lens = [(lx + (px - lx) * f, py) for (px, py) in lens]
        pygame.draw.polygon(surf, _LENS, lens)
        # diagonal sheen streak across the dark glass
        sx0 = lx - f * (lw * 0.30)
        pygame.draw.line(surf, _SHEEN, (sx0, ly - lh * 0.30),
                         (sx0 + f * (lw * 0.30), ly + lh * 0.10),
                         max(1, int(eye_w * 0.05)))
        pygame.draw.polygon(surf, _LENS_D, [
            (lx + f * lw * 0.10, ly + lh * 0.20),
            (lx + f * lw * 0.40, ly + lh * 0.10),
            (lx + f * lw * 0.30, ly + lh * 0.45),
        ])

    # Thick brow bar connecting the lenses across the top.
    bar_w = max(2, int(eye_w * 0.12))
    pygame.draw.line(surf, _FRAME, (far[0] - f * (lw // 2), cy - lh // 2),
                     (near[0] + f * (lw // 2), cy - lh // 2), bar_w)
    pygame.draw.line(surf, _FRAME_H, (far[0] - f * (lw // 3), cy - lh // 2 - 1),
                     (near[0] + f * (lw // 3), cy - lh // 2 - 1), 1)

    # Chunky temple hinge + arm toward the ear.
    pygame.draw.line(surf, _FRAME, (far[0] - f * (lw // 2), cy - lh // 4),
                     (far[0] - f * (lw // 2 + max(2, int(eye_w * 0.30))),
                      cy - max(1, int(eye_w * 0.10))), bar_w)
