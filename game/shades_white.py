"""WHITE RETRO — white plastic frames with dark lenses, retro-fashion.

Rounded-rect white frames (chunky 60s/70s plastic) holding near-black lenses
with a cool sheen. The white plastic is the read; the dark glass is the
contrast. Frames are slightly oversized so the white survives at 22px.
"""
import pygame

_FRAME   = (244, 244, 248)
_FRAME_D = (196, 198, 210)         # underside shade so plastic reads as 3D
_FRAME_H = (255, 255, 255)
_LENS    = (24, 28, 40)
_SHEEN   = (120, 150, 200)
_GLINT   = (255, 255, 255)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    lw = max(4, int(eye_w * 0.42))
    lh = max(4, int(eye_w * 0.40))
    sep = max(4, int(eye_w * 0.44))
    rad = max(1, int(eye_w * 0.10))
    thick = max(2, int(eye_w * 0.09))

    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    for (lx, ly) in (far, near):
        outer = pygame.Rect(0, 0, lw + thick * 2, lh + thick * 2)
        outer.center = (lx, ly)
        # underside first so the top rim can sit a touch brighter
        sh = outer.copy(); sh.move_ip(0, 1)
        pygame.draw.rect(surf, _FRAME_D, sh, border_radius=rad)
        pygame.draw.rect(surf, _FRAME, outer, border_radius=rad)
        pygame.draw.line(surf, _FRAME_H, (outer.left + rad, outer.top + 1),
                         (outer.right - rad, outer.top + 1), 1)
        inner = pygame.Rect(0, 0, lw, lh)
        inner.center = (lx, ly)
        pygame.draw.rect(surf, _LENS, inner, border_radius=max(1, rad - 1))
        # cool sheen sweeping the upper-outer corner of the dark glass
        pygame.draw.line(surf, _SHEEN, (lx - f * lw * 0.30, ly - lh * 0.28),
                         (lx + f * lw * 0.10, ly + lh * 0.05),
                         max(1, int(eye_w * 0.05)))
        pygame.draw.circle(surf, _GLINT,
                           (int(lx - f * lw * 0.28), int(ly - lh * 0.28)),
                           max(1, int(eye_w * 0.045)))

    # White bridge bar.
    pygame.draw.line(surf, _FRAME, (far[0] + f * (lw // 2), cy - lh // 4),
                     (near[0] - f * (lw // 2), cy - lh // 4), thick)
    pygame.draw.line(surf, _FRAME_H, (far[0] + f * (lw // 2), cy - lh // 4 - 1),
                     (near[0] - f * (lw // 2), cy - lh // 4 - 1), 1)

    # Temple arm toward the ear.
    pygame.draw.line(surf, _FRAME, (far[0] - f * (lw // 2 + thick), cy - lh // 5),
                     (far[0] - f * (lw // 2 + max(3, int(eye_w * 0.32))),
                      cy - max(1, int(eye_w * 0.10))), thick)
