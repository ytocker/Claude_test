"""ROUND SHADES (Lennon) — small perfectly-round metal frames, tinted lenses.

The teal-rose tint and the bright gold rim are the read. Smaller lenses than
the nerd specs and a fully filled (not clear) glass so it scans as shades, not
spectacles, even at 22px.
"""
import pygame

_RIM    = (236, 196, 96)           # warm gold metal
_RIM_H  = (255, 240, 180)
_LENS   = (54, 120, 120)           # teal tint
_LENS_D = (30, 80, 84)
_ROSE   = (150, 90, 110, 90)       # faint rose flush low in the glass
_GLINT  = (255, 255, 255)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r = max(2, int(eye_w * 0.27))
    sep = max(3, int(eye_w * 0.44))
    rim = max(1, int(eye_w * 0.07))

    near = (cx + f * (sep // 2), cy)
    far  = (cx - f * (sep // 2), cy)

    for (lx, ly) in (near, far):
        # Tinted glass with a vertical teal->darker fade for roundness.
        glass = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for yy in range(r * 2):
            t = yy / max(1, r * 2 - 1)
            c = (int(_LENS[0] + (_LENS_D[0] - _LENS[0]) * t),
                 int(_LENS[1] + (_LENS_D[1] - _LENS[1]) * t),
                 int(_LENS[2] + (_LENS_D[2] - _LENS[2]) * t), 215)
            pygame.draw.line(glass, c, (0, yy), (r * 2, yy))
        clip = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(clip, (255, 255, 255, 255), (r, r), r)
        glass.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # Rose flush across the lower lens.
        pygame.draw.ellipse(glass, _ROSE, (1, r, r * 2 - 2, r))
        surf.blit(glass, (lx - r, ly - r))

    # Gold rims.
    for (lx, ly) in (near, far):
        pygame.draw.circle(surf, _RIM, (lx, ly), r, rim)
    pygame.draw.arc(surf, _RIM_H, (near[0] - r, near[1] - r, r * 2, r * 2),
                    0.6, 2.3, max(1, rim - 1))

    # Flat metal bridge across the top.
    pygame.draw.line(surf, _RIM, (far[0] + f * r, cy - r // 2),
                     (near[0] - f * r, cy - r // 2), rim)

    # Temple arm toward the ear.
    pygame.draw.line(surf, _RIM, (far[0] - f * r, cy - 1),
                     (far[0] - f * (r + max(2, int(eye_w * 0.32))), cy - max(1, int(eye_w * 0.08))),
                     rim)

    pygame.draw.circle(surf, _GLINT, (near[0] - f * (r // 2), cy - r // 2),
                       max(1, int(eye_w * 0.055)))
