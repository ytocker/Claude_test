"""Cartoon-shrimp face — CFACE 4: DETERMINED. A clear cartoon-shrimp face that
keeps the bruiser attitude: clean bead eyes under a bold angry brow, antennae
swept back aggressively, and a set mandible. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _STALK, _STALK_RIM, _CARA_H, CROWN_Y,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Antennae swept back hard (low + fast) for an aggressive read.
    for dy in (0, 3):
        pygame.draw.lines(surf, _STALK_RIM, False,
                          [(hcx + 6, hcy - 1 + dy), (hcx - 4, CROWN_Y + 4 + dy + rcy),
                           (hcx - 13, CROWN_Y + 6 + dy + rcy),
                           (hcx - 18, CROWN_Y + 5 + dy + rcy)], 2)
        pygame.draw.lines(surf, _CARA_H, False,
                          [(hcx + 6, hcy - 1 + dy), (hcx - 4, CROWN_Y + 4 + dy + rcy)], 1)
    # Clean bead eyes on short stalks, set close.
    for sgn, tx in ((-1, hcx - 3), (1, hcx + 4)):
        base = (hcx + sgn * 2, hcy - 3)
        tip = (tx, hcy - 7 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)
        pygame.draw.line(surf, _STALK, base, tip, 3)
        pygame.draw.circle(surf, _STALK_RIM, tip, 5)
        pygame.draw.circle(surf, (44, 32, 64), tip, 4)
        pygame.draw.circle(surf, (255, 255, 255), (tip[0] - 1, tip[1] - 2), 2)
    # Bold angry brow — inner end LOW (anger), one clean 3px ridge per side.
    pygame.draw.line(surf, _STALK_RIM, (hcx - 9, hcy - 9), (hcx - 1, hcy - 5), 3)
    pygame.draw.line(surf, _STALK_RIM, (hcx + 10, hcy - 9), (hcx + 2, hcy - 5), 3)
    # Set mandible (a short down-frown).
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 3, hcy + 5, 9, 6), 0.4, 2.7, 2)


build = make(face)
