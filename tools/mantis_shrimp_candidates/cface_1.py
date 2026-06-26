"""Cartoon-shrimp face on the ORIGINAL duotone bruiser — CFACE 1: CLASSIC.
Clean stalked BEAD eyes (a simple dark sphere + a big white highlight, not the
busy iridescent jewel), two long trailing ANTENNAE (the missing "this is a
shrimp" tell), and a small friendly mouth. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _STALK, _STALK_RIM, _CARA_H, CROWN_Y,
)


def _antenna(surf, pts, hi):
    pygame.draw.lines(surf, _STALK_RIM, False, pts, 2)
    pygame.draw.lines(surf, hi, False, pts[:-1], 1)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Two long antennae sweeping up-and-back over the carapace (the shrimp tell).
    _antenna(surf, [(hcx + 5, hcy - 2), (hcx + 1, CROWN_Y + 1 + rcy),
                    (hcx - 8, CROWN_Y - 2 + rcy), (hcx - 16, CROWN_Y - 5 + rcy)], _CARA_H)
    _antenna(surf, [(hcx + 6, hcy), (hcx + 3, CROWN_Y + 5 + rcy),
                    (hcx - 6, CROWN_Y + 3 + rcy), (hcx - 13, CROWN_Y + 2 + rcy)], _CARA_H)
    # Clean stalked bead eyes.
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        base = (hcx + sgn * 2, hcy - 3)
        tip = (tx, hcy - 8 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)
        pygame.draw.line(surf, _STALK, base, tip, 3)
        pygame.draw.circle(surf, _STALK_RIM, tip, 5)
        pygame.draw.circle(surf, (44, 32, 64), tip, 4)
        pygame.draw.circle(surf, (255, 255, 255), (tip[0] - 1, tip[1] - 2), 2)
    # Small friendly mouth.
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 2, hcy + 4, 8, 6), 3.6, 5.8, 2)


build = make(face)
