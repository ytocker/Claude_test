"""Mantis shrimp face — DESIGN 2: BIG FRONT GOGGLE EYES. Drops the tall stalks
entirely: two big forward-facing iridescent compound eyes sit directly on the
head side by side, with a tiny smile — a clear, cute, casual read. Body/tail/
clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _jewel_eye, _STALK_RIM,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    # Two big compound eyes on tiny nubs, set forward on the head (no periscopes).
    for ex, ey in ((hcx - 4, hcy - 3), (hcx + 5, hcy - 3)):
        pygame.draw.circle(surf, _STALK_RIM, (ex, ey + 3), 2)   # short nub seat
        _jewel_eye(surf, ex, ey, 6, glow=glow)
    # Tiny upward smile under the eyes.
    pygame.draw.arc(surf, _STALK_RIM, (hcx - 3, hcy + 3, 9, 7), 3.5, 6.0, 2)


build = make(face)
