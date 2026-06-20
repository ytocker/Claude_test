"""CYBER VISOR — one sleek horizontal neon bar spanning both eyes.

Single-piece exception (Geordi/Cyclops): a glossy dark visor bar with an
emissive neon line glowing through it and a soft halo, plus a metal end-cap
that wraps back toward the ear. The horizontal slit is the read.
"""
import pygame

_BODY    = (26, 28, 40)            # dark visor housing
_BODY_H  = (70, 78, 110)
_CAP     = (150, 158, 178)         # brushed-metal end cap
_NEON    = (60, 240, 220)          # emissive cyan-green slit
_NEON_H  = (200, 255, 250)


def draw_shades(surf, cx, cy, eye_w, facing=1):
    f = facing
    w = max(8, int(eye_w * 1.18))          # spans both eyes
    h = max(3, int(eye_w * 0.40))
    rad = max(1, int(eye_w * 0.16))

    rect = pygame.Rect(0, 0, w, h)
    rect.center = (cx, cy)

    # Soft neon halo behind the bar (additive glow feel via translucent layers).
    halo = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
    for i, a in ((4, 40), (2, 70)):
        pygame.draw.rect(halo, (*_NEON, a),
                         (4 - i, 4 - i, w + i * 2, h + i * 2), border_radius=rad + i)
    surf.blit(halo, (rect.left - 4, rect.top - 4), special_flags=pygame.BLEND_ADD)

    # Glossy dark housing.
    pygame.draw.rect(surf, _BODY, rect, border_radius=rad)
    pygame.draw.line(surf, _BODY_H, (rect.left + rad, rect.top + 1),
                     (rect.right - rad, rect.top + 1), 1)

    # Emissive neon slit running the length of the visor.
    slit_y = cy + max(1, int(h * 0.10))
    inset = max(2, int(w * 0.10))
    pygame.draw.line(surf, _NEON, (rect.left + inset, slit_y),
                     (rect.right - inset, slit_y), max(1, int(eye_w * 0.09)))
    pygame.draw.line(surf, _NEON_H, (rect.left + inset + w * 0.10, slit_y - 1),
                     (rect.left + inset + w * 0.55, slit_y - 1),
                     max(1, int(eye_w * 0.035)))

    # Metal end cap wrapping back toward the ear.
    ear_x = cx - f * (w // 2)
    cap = pygame.Rect(0, 0, max(2, int(eye_w * 0.14)), h + 2)
    cap.center = (ear_x, cy)
    pygame.draw.rect(surf, _CAP, cap, border_radius=max(1, rad // 2))
    pygame.draw.line(surf, (255, 255, 255), (cap.centerx, cap.top + 1),
                     (cap.centerx, cap.bottom - 1), 1)
    # Short stem from the cap toward the ear.
    pygame.draw.line(surf, _CAP, (ear_x, cy),
                     (ear_x - f * max(2, int(eye_w * 0.16)), cy - max(1, int(eye_w * 0.06))),
                     max(1, int(eye_w * 0.07)))
