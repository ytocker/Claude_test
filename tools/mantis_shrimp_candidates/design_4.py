"""Mantis shrimp face — DESIGN 4: WIDE STALKS + ROSTRUM. The anatomical take:
outward-angled stalk eyes in a clear V-splay, a pointed rostrum snout at the
front of the head, and short antennae — reads as a real mantis-shrimp face.
Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK, _STALK_RIM, _CARA, _CARA_D,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Pointed rostrum snout at the front-top of the head (the species tell).
    pygame.draw.polygon(surf, _CARA_D,
                        [(hcx + 6, hcy - 5), (hcx + 12, hcy - 9), (hcx + 8, hcy - 1)])
    pygame.draw.polygon(surf, _CARA,
                        [(hcx + 6, hcy - 4), (hcx + 11, hcy - 8), (hcx + 8, hcy - 2)])
    # Short antennae flicking up off the brow.
    pygame.draw.line(surf, _STALK_RIM, (hcx - 1, hcy - 5), (hcx - 5, hcy - 11), 1)
    pygame.draw.line(surf, _STALK_RIM, (hcx + 2, hcy - 5), (hcx + 5, hcy - 11), 1)
    # Outward-angled eye-stalks in a clear V — moderate length, jewels splayed.
    for sgn, bx in ((-1, hcx - 2), (1, hcx + 3)):
        tip = (hcx + sgn * 9, hcy - 8 + rcy)
        pygame.draw.line(surf, _STALK_RIM, (bx, hcy - 3), tip, 5)
        pygame.draw.line(surf, _STALK, (bx, hcy - 3), tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 5, glow=glow)


build = make(face)
