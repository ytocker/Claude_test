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
    # Pointed rostrum snout on the front-LOW of the head (clear of the lead club,
    # which sits up-right) — the species tell.
    pygame.draw.polygon(surf, _CARA_D,
                        [(hcx - 8, hcy + 1), (hcx - 13, hcy + 4), (hcx - 6, hcy + 5)])
    pygame.draw.polygon(surf, _CARA,
                        [(hcx - 8, hcy + 2), (hcx - 12, hcy + 4), (hcx - 6, hcy + 4)])
    # Eye-stalks in a GENTLE V, tips pulled inboard so the jewels don't float wide.
    for sgn in (-1, 1):
        tip = (hcx + sgn * 6, hcy - 8 + rcy)
        pygame.draw.line(surf, _STALK_RIM, (hcx + sgn * 2, hcy - 3), tip, 5)
        pygame.draw.line(surf, _STALK, (hcx + sgn * 2, hcy - 3), tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 5, glow=glow)


build = make(face)
