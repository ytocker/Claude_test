"""Cartoon-shrimp face — CFACE 3: REALISTIC COMPOUND. The most true-to-life take:
the iridescent compound eyes (cleaned up) on stalks, a pointed ROSTRUM snout, a
long antenna pair PLUS a short antennule pair, and small mandible mouthparts —
clearly a (cartoon) mantis shrimp. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK, _STALK_RIM, _CARA, _CARA_D, _CARA_H,
    _BAND, CROWN_Y,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Pointed rostrum snout at the front of the head (the species tell).
    pygame.draw.polygon(surf, _CARA_D,
                        [(hcx + 8, hcy - 1), (hcx + 14, hcy - 5), (hcx + 9, hcy + 3)])
    pygame.draw.polygon(surf, _CARA,
                        [(hcx + 8, hcy), (hcx + 13, hcy - 4), (hcx + 9, hcy + 2)])
    # Long trailing antenna pair over the carapace.
    for dy in (0, 3):
        pygame.draw.lines(surf, _STALK_RIM, False,
                          [(hcx + 6, hcy - 2 + dy), (hcx - 2, CROWN_Y + dy + rcy),
                           (hcx - 11, CROWN_Y - 2 + dy + rcy),
                           (hcx - 17, CROWN_Y - 4 + dy + rcy)], 2)
        pygame.draw.lines(surf, _CARA_H, False,
                          [(hcx + 6, hcy - 2 + dy), (hcx - 2, CROWN_Y + dy + rcy)], 1)
    # Short antennule pair flicking forward off the snout.
    pygame.draw.line(surf, _BAND, (hcx + 9, hcy + 1), (hcx + 15, hcy + 2), 1)
    pygame.draw.line(surf, _BAND, (hcx + 9, hcy + 2), (hcx + 14, hcy + 5), 1)
    # Iridescent compound eyes on short stalks.
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        base = (hcx + sgn * 2, hcy - 3)
        tip = (tx, hcy - 8 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)
        pygame.draw.line(surf, _STALK, base, tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 5, glow=glow)
    # Small mandible mouthparts.
    pygame.draw.line(surf, _STALK_RIM, (hcx, hcy + 5), (hcx + 6, hcy + 5), 2)
    pygame.draw.line(surf, _CARA_H, (hcx + 1, hcy + 7), (hcx + 4, hcy + 7), 1)


build = make(face)
