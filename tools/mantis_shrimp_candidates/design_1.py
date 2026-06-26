"""Mantis shrimp face — DESIGN 1: TWIN PERISCOPES (refined). Keeps the iconic
stalked jewel eyes but fixes the read: SHORTER, less-spread stalks so the jewels
sit just above a clear head (not floating far up), bigger jewels, and a small
dark mandible mouth so there's an actual face. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK, _STALK_RIM, _CARA_H,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Short periscope stalks from a SHARED root (hcx±2) so they read as one head,
    # not two antennae; tips low enough that the jewels' lower edge meets the
    # head crown (no floating gap).
    for sgn, tx in ((-1, hcx - 5), (1, hcx + 6)):
        base = (hcx + sgn * 2, hcy - 3)
        tip = (tx, hcy - 9 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)
        pygame.draw.line(surf, _STALK, base, tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 5, glow=glow)
    # Mandible mouth — wider, with a pale lip below so it survives 40px.
    pygame.draw.line(surf, _STALK_RIM, (hcx - 2, hcy + 5), (hcx + 5, hcy + 5), 3)
    pygame.draw.line(surf, _CARA_H, (hcx - 1, hcy + 7), (hcx + 4, hcy + 7), 1)


build = make(face)
