"""Mantis shrimp face — DESIGN 2: BIG FRONT GOGGLE EYES. Drops the tall stalks
entirely: two big forward-facing iridescent compound eyes sit directly on the
head side by side, with a tiny smile — a clear, cute, casual read. Body/tail/
clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK, _STALK_RIM,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Two big compound eyes on SHORT vertical stalk-nubs (keeps the stalk-eyed
    # mantis identity without floating). Right eye pulled in to clear the club.
    for ex, ey in ((hcx - 4, hcy - 3), (hcx + 4, hcy - 3)):
        pygame.draw.line(surf, _STALK_RIM, (ex, ey + 5), (ex, ey + 2), 3)
        pygame.draw.line(surf, _STALK, (ex, ey + 5), (ex, ey + 2), 1)
        _jewel_eye(surf, ex, ey, 6, glow=glow)
    # Clear upward smile under the eyes (thicker, wider box).
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 4, hcy + 3, 10, 7), 3.5, 6.0, 2)


build = make(face)
