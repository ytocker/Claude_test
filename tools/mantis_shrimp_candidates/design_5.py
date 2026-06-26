"""Mantis shrimp face — DESIGN 5: VISOR MIDBAND. The mantis shrimp's famous
hyperspectral compound-eye midband rendered as ONE bold horizontal iridescent
visor band across the head — a strong sci-fi graphic read — plus short antennae.
Body/tail/clubs unchanged."""
import pygame

from tools.mantis_shrimp_candidates._shared import (
    make, head_base, _STALK_RIM, _EYE_HUE, _EYE_HUE2, _glow_dot, _GLOW,
)


def face(surf, hcx, hcy, rcy, s, glow):
    head_base(surf, hcx, hcy)
    x0, x1, cy = hcx - 8, hcx + 9, hcy - 2
    if glow:
        _glow_dot(surf, hcx, cy, 4, _GLOW)
    # Dark seat capsule so the visor pops off any sky.
    pygame.draw.line(surf, _STALK_RIM, (x0, cy), (x1, cy), 7)
    # Iridescent visor: blue-shifted body + teal core.
    pygame.draw.line(surf, _EYE_HUE2, (x0, cy), (x1, cy), 5)
    pygame.draw.line(surf, _EYE_HUE, (x0 + 1, cy), (x1 - 1, cy), 3)
    # Equatorial midband of ommatidia (the signature white scan-line).
    pygame.draw.line(surf, (250, 252, 250), (x0 + 1, cy), (x1 - 1, cy), 1)
    # Dark center NOTCH so the band reads as TWO compound eyes joined by the
    # midband (a face), not one cyclops strip.
    pygame.draw.line(surf, _STALK_RIM, (hcx, cy - 2), (hcx, cy + 2), 2)
    # Two hot speculars so the visor snaps to attention at 40px.
    pygame.draw.circle(surf, (255, 255, 255), (hcx - 4, cy - 1), 1)
    pygame.draw.circle(surf, (255, 255, 255), (hcx + 4, cy - 1), 1)
    # A small dark mouth below so it unambiguously reads as a face.
    pygame.draw.line(surf, _STALK_RIM, (hcx - 2, hcy + 5), (hcx + 4, hcy + 5), 2)
    # Short 2px antennae flicking up off the brow.
    pygame.draw.line(surf, _STALK_RIM, (hcx - 4, cy - 3), (hcx - 7, hcy - 10), 2)
    pygame.draw.line(surf, _STALK_RIM, (hcx + 4, cy - 3), (hcx + 7, hcy - 10), 2)


build = make(face)
