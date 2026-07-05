"""Cartoon-shrimp face — CFACE 2: BIG EXPRESSIVE. Large round googly cartoon
eyes (white sclera + big dark pupil + shine) on short stalks, two trailing
antennae, and an open friendly smile. Maximum clarity + appeal. Body/tail/clubs
unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _STALK, _STALK_RIM, _CARA_H, _BAND, CROWN_Y,
)


def _antenna(surf, pts):
    pygame.draw.lines(surf, _STALK_RIM, False, pts, 2)
    pygame.draw.lines(surf, _BAND, False, pts[:-1], 1)   # warm-tipped feelers


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    _antenna(surf, [(hcx + 5, hcy - 2), (hcx, CROWN_Y + rcy),
                    (hcx - 9, CROWN_Y - 3 + rcy), (hcx - 16, CROWN_Y - 7 + rcy)])
    _antenna(surf, [(hcx + 6, hcy), (hcx + 2, CROWN_Y + 5 + rcy),
                    (hcx - 7, CROWN_Y + 3 + rcy), (hcx - 14, CROWN_Y + 1 + rcy)])
    # Big googly cartoon eyes on short stalks.
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        base = (hcx + sgn * 2, hcy - 2)
        tip = (tx, hcy - 7 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 4)
        pygame.draw.line(surf, _STALK, base, tip, 2)
        pygame.draw.circle(surf, _STALK_RIM, tip, 7)
        pygame.draw.circle(surf, (255, 255, 255), tip, 6)
        pygame.draw.circle(surf, (32, 26, 44), (tip[0] + 1, tip[1] + 1), 4)
        pygame.draw.circle(surf, (255, 255, 255), (tip[0] - 1, tip[1] - 1), 2)
    # Open friendly smile.
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 3, hcy + 3, 10, 8), 3.5, 6.0, 2)
    pygame.draw.line(surf, _STALK_RIM, (hcx - 2, hcy + 5), (hcx + 5, hcy + 5), 1)


build = make(face)
