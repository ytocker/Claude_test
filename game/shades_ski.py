"""SKI GOGGLES — one big wraparound mirrored lens + foam rim + strap.

A single wide lens (covering both eyes) with a subtle mirror gradient and a
diagonal sheen sweep, ringed by a chunky foam rim and trailing a strap back
toward the ear. The wide single-lens silhouette distinguishes it instantly.
"""
import pygame

_FOAM    = (54, 58, 78)            # dark frame/foam ring
_FOAM_H  = (96, 102, 128)
_STRAP   = (230, 120, 60)          # bright nylon strap accent
_STRAP_H = (255, 175, 110)
_MIRROR_T = (180, 235, 245)        # mirrored sky-blue top
_MIRROR_B = (120, 110, 200)        # purple-ish mirror bottom
_SHEEN   = (255, 255, 255)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(6, int(eye_w * 1.05))          # wraparound lens width
    h = max(4, int(eye_w * 0.62))
    rim = max(2, int(eye_w * 0.12))

    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)
    rad = max(2, int(eye_w * 0.22))

    # Foam rim (slightly larger rounded rect behind the lens).
    frame = rect.inflate(rim * 2, rim * 2)
    pygame.draw.rect(surf, _FOAM, frame, border_radius=rad + rim)
    pygame.draw.line(surf, _FOAM_H, (frame.left + rad, frame.top + 1),
                     (frame.right - rad, frame.top + 1), max(1, rim // 2))

    # Mirrored lens — vertical gradient clipped to the rounded rect.
    lens = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = (int(_MIRROR_T[0] + (_MIRROR_B[0] - _MIRROR_T[0]) * t),
             int(_MIRROR_T[1] + (_MIRROR_B[1] - _MIRROR_T[1]) * t),
             int(_MIRROR_T[2] + (_MIRROR_B[2] - _MIRROR_T[2]) * t), 255)
        pygame.draw.line(lens, c, (0, yy), (w, yy))
    clip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(clip, (255, 255, 255, 255), clip.get_rect(), border_radius=rad)
    lens.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(lens, rect.topleft)

    # Diagonal sheen band sweeping across the mirror.
    pygame.draw.line(surf, _SHEEN, (rect.left + w * 0.12, rect.bottom - 2),
                     (rect.left + w * 0.42, rect.top + 2),
                     max(1, int(eye_w * 0.06)))
    pygame.draw.line(surf, (255, 255, 255, 160),
                     (rect.left + w * 0.30, rect.bottom - 2),
                     (rect.left + w * 0.52, rect.top + 4),
                     max(1, int(eye_w * 0.04)))

    # Strap running back toward the ear, with a buckle highlight.
    sy = cy - max(1, int(h * 0.05))
    sx0 = frame.left - f * 0   # frame edge on the ear side depends on facing
    ear_x = cx - f * (w // 2 + rim)
    pygame.draw.line(surf, _STRAP, (ear_x, sy),
                     (ear_x - f * max(3, int(eye_w * 0.34)), sy - max(1, int(eye_w * 0.10))),
                     max(2, int(eye_w * 0.13)))
    pygame.draw.line(surf, _STRAP_H, (ear_x, sy - max(1, int(eye_w * 0.04))),
                     (ear_x - f * max(3, int(eye_w * 0.30)), sy - max(1, int(eye_w * 0.13))),
                     1)
