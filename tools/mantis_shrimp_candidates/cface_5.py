"""Cartoon-shrimp face — CFACE 5: CUTE COMPACT. A tight, clear, friendly face:
medium close-set round eyes, short perky antennae, rosy cheeks and a little
smile — the cuddly cartoon-shrimp read. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _STALK, _STALK_RIM, _CARA_H, CROWN_Y,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Short, perky antennae curling up off the brow.
    for sgn in (-1, 1):
        pygame.draw.lines(surf, _STALK_RIM, False,
                          [(hcx + sgn * 2, hcy - 4), (hcx + sgn * 5, CROWN_Y + 3 + rcy),
                           (hcx + sgn * 3, CROWN_Y - 2 + rcy)], 2)
        pygame.draw.circle(surf, _CARA_H, (hcx + sgn * 3, CROWN_Y - 2 + rcy), 1)
    # Medium close-set bead eyes on short stubs.
    for sgn, tx in ((-1, hcx - 3), (1, hcx + 4)):
        base = (hcx + sgn * 2, hcy - 2)
        tip = (tx, hcy - 6 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 4)
        pygame.draw.line(surf, _STALK, base, tip, 2)
        pygame.draw.circle(surf, _STALK_RIM, tip, 5)
        pygame.draw.circle(surf, (44, 32, 64), tip, 4)
        pygame.draw.circle(surf, (255, 255, 255), (tip[0] - 1, tip[1] - 2), 2)
    # Rosy cheeks + a little smile.
    pygame.draw.circle(surf, (255, 138, 120), (hcx - 5, hcy + 4), 2)
    pygame.draw.circle(surf, (255, 138, 120), (hcx + 6, hcy + 4), 2)
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 2, hcy + 4, 8, 6), 3.7, 5.7, 2)


build = make(face)
