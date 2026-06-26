"""Mantis shrimp face — DESIGN 3: FIERCE BRUISER. A determined fighter face that
matches the boxer/strike theme: jewel eyes on short stalks NARROWED under a bold
angled dark brow ridge, plus a gritted mandible. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK, _STALK_RIM, _BAND_D,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Short stalks, eyes set lower + close so the brow can scowl over them.
    for sgn, bx, tx in ((-1, hcx - 2, hcx - 5), (1, hcx + 3, hcx + 6)):
        tip = (tx, hcy - 7 + rcy)
        pygame.draw.line(surf, _STALK_RIM, (bx, hcy - 3), tip, 5)
        pygame.draw.line(surf, _STALK, (bx, hcy - 3), tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 5, glow=glow)
    # Bold angled brow ridge across the head — the scowl (drawn over the stalk
    # roots so it reads as a furrowed brow above the eyes).
    pygame.draw.line(surf, _STALK_RIM, (hcx - 8, hcy - 5), (hcx - 1, hcy - 9), 3)
    pygame.draw.line(surf, _STALK_RIM, (hcx + 9, hcy - 5), (hcx + 2, hcy - 9), 3)
    pygame.draw.line(surf, _BAND_D, (hcx - 7, hcy - 5), (hcx - 2, hcy - 8), 1)
    pygame.draw.line(surf, _BAND_D, (hcx + 8, hcy - 5), (hcx + 3, hcy - 8), 1)
    # Gritted mandible — a short dark bar with a vertical tick (clenched).
    pygame.draw.line(surf, _STALK_RIM, (hcx - 2, hcy + 6), (hcx + 5, hcy + 6), 2)
    pygame.draw.line(surf, _STALK_RIM, (hcx + 1, hcy + 5), (hcx + 1, hcy + 7), 1)


build = make(face)
