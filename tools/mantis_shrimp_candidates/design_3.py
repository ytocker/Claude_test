"""Mantis shrimp face — DESIGN 3: FIERCE BRUISER. A determined fighter face that
matches the boxer/strike theme: jewel eyes on short stalks NARROWED under a bold
angled dark brow ridge, plus a gritted mandible. Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK, _STALK_RIM,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Short stalks, eyes set close so the brow can scowl over them.
    for sgn, tx in ((-1, hcx - 5), (1, hcx + 6)):
        tip = (tx, hcy - 7 + rcy)
        pygame.draw.line(surf, _STALK_RIM, (hcx + sgn * 2, hcy - 3), tip, 5)
        pygame.draw.line(surf, _STALK, (hcx + sgn * 2, hcy - 3), tip, 3)
        _jewel_eye(surf, tip[0], tip[1], 5, glow=glow)
    # ONE bold continuous angled brow per side, inner end LOW (anger, not sad) —
    # a single clean 3px ridge each, no inner clutter.
    pygame.draw.line(surf, _STALK_RIM, (hcx - 9, hcy - 9), (hcx - 1, hcy - 5), 3)
    pygame.draw.line(surf, _STALK_RIM, (hcx + 10, hcy - 9), (hcx + 2, hcy - 5), 3)
    # Single 2px down-frown.
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 3, hcy + 5, 9, 6), 0.4, 2.7, 2)


build = make(face)
