"""Mantis shrimp face — DESIGN 1: TWIN PERISCOPES (refined). Keeps the iconic
stalked jewel eyes but fixes the read: SHORTER, less-spread stalks so the jewels
sit just above a clear head (not floating far up), bigger jewels, and a small
dark mandible mouth so there's an actual face. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK, _STALK_RIM, _CARA_D,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Short, gently-spread periscope stalks — tips sit just above the head.
    for sgn, bx, tx in ((-1, hcx - 2, hcx - 5), (1, hcx + 3, hcx + 6)):
        base = (bx, hcy - 4)
        tip = (tx, hcy - 10 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)
        pygame.draw.line(surf, _STALK, base, tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 5, glow=glow)
    # Small dark mandible mouth on the head front so it reads as a face.
    pygame.draw.line(surf, _STALK_RIM, (hcx - 1, hcy + 5), (hcx + 5, hcy + 5), 2)
    pygame.draw.line(surf, _CARA_D, (hcx + 1, hcy + 7), (hcx + 3, hcy + 7), 1)


build = make(face)
