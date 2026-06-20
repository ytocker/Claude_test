"""MONOCLE — a single round gold-rimmed lens over the FRONT eye + a chain.

Single-piece exception: only the near (beak-side) eye is covered. The dapper
read is the thick gold ring, the glassy tint, and a fine chain dangling down
and trailing back toward the ear. No far lens, no temple arm.
"""
import pygame

_RIM    = (240, 200, 90)           # gold
_RIM_D  = (190, 150, 40)
_RIM_H  = (255, 244, 180)
_GLASS  = (190, 210, 220, 70)      # faint cool tint
_CHAIN  = (210, 178, 80)
_GLINT  = (255, 255, 255)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    r = max(3, int(eye_w * 0.34))
    rim = max(2, int(eye_w * 0.10))

    # Centre the single lens over the NEAR (beak-side) eye.
    lx = cx + f * max(2, int(eye_w * 0.18))
    ly = cy

    # Faint glass tint.
    glass = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(glass, _GLASS, (r, r), r)
    surf.blit(glass, (lx - r, ly - r))

    # Thick gold ring with a shaded underside + bright top-arc.
    pygame.draw.circle(surf, _RIM_D, (lx, ly), r, rim)
    pygame.draw.circle(surf, _RIM, (lx, ly), r, max(1, rim - 1))
    pygame.draw.arc(surf, _RIM_H, (lx - r, ly - r, r * 2, r * 2), 0.5, 2.3,
                    max(1, rim - 1))

    # Glassy glints.
    pygame.draw.circle(surf, _GLINT, (lx - f * (r // 2), ly - r // 2),
                       max(1, int(eye_w * 0.06)))
    pygame.draw.circle(surf, (255, 255, 255, 200), (lx + f * (r // 3), ly + r // 3),
                       max(1, int(eye_w * 0.035)))

    # Fine chain dangling from the lower-ear side of the ring, looping back.
    anchor = (lx - f * r, ly + r // 3)
    pygame.draw.circle(surf, _RIM, anchor, max(1, int(eye_w * 0.05)))
    drop = max(3, int(eye_w * 0.5))
    seg = max(1, int(eye_w * 0.07))
    # Two-segment dangling chain: down then a slight back-sway.
    p_mid = (anchor[0] - f * seg, anchor[1] + drop // 2)
    p_end = (anchor[0] - f * seg * 2, anchor[1] + drop)
    pygame.draw.line(surf, _CHAIN, anchor, p_mid, max(1, int(eye_w * 0.04)))
    pygame.draw.line(surf, _CHAIN, p_mid, p_end, max(1, int(eye_w * 0.04)))
    pygame.draw.circle(surf, _CHAIN, p_end, max(1, int(eye_w * 0.05)))
