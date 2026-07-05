"""BABY CHICK penguin — design_5, WAVE 2 from-scratch redraw.

A totally different adorable proportion: a fuzzy silver-grey down-covered baby
penguin with an oversized round head and huge sparkly eyes. The fuzzy silhouette
(short radial down ticks), the big-head proportion and the soft monochrome grey
palette set it apart from every adult. Scratch-only — NOT registered in
``animal_skins.BUILDERS``.
"""
import math
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── BABY CHICK palette ────────────────────────────────────────────────────────
_BC_DOWN    = (154, 163, 178)       # #9AA3B2 silver-grey down
_BC_DOWN_D  = (110, 118, 134)       # #6E7686 down shadow
_BC_DOWN_H  = (188, 196, 210)       # down highlight
_BC_BELLY   = (195, 202, 214)       # #C3CAD6 pale belly
_BC_BELLY_H = (237, 239, 244)       # #EDEFF4 belly sheen
_BC_CAP     = (96, 104, 120)        # darker grey crown cap
_BC_FACE    = (210, 216, 226)       # pale face mask
_BC_BEAK    = (58, 63, 76)          # #3A3F4C tiny dark beak
_BC_FOOT    = (124, 132, 148)       # #7C8494 pale-grey feet
_BC_SURR    = (228, 232, 240)       # eye surround


def _fuzz_ring(surf, cx, cy, rx, ry, col, n, length, jitter):
    """Short radial down ticks around an ellipse so the silhouette reads fuzzy,
    not a clean hard egg — the baby-down tell. Deterministic (no RNG) so the
    four cached frames stay stable; ``jitter`` varies tick length by index."""
    for i in range(n):
        a = (i / n) * math.tau
        ox, oy = math.cos(a), math.sin(a) * 0.92
        bx, by = cx + ox * rx, cy + oy * ry
        ln = length + (i % 3) * jitter
        pygame.draw.line(surf, col, (bx, by), (bx + ox * ln, by + oy * ln), 1)


def _bc_flipper(angle_deg):
    """Tiny stubby down flipper."""
    w = pygame.Surface((30, 36), pygame.SRCALPHA)
    pts = [(16, 9), (22, 15), (18, 28), (12, 24)]
    pygame.draw.polygon(w, _BC_DOWN_D, pts)
    pygame.draw.polygon(w, _BC_DOWN, [(16, 10), (20, 16), (16, 25), (13, 22)])
    return pygame.transform.rotate(w, angle_deg * 0.6)


def build_chick(wing_angle_deg):
    surf = _new()

    # ── Body: small fuzzy down egg (the head will dominate) ──
    # Fuzz ring first (behind), then the solid body over its roots. Fewer body
    # ticks so the lower silhouette stays soft-round (not spiky) against the sky.
    _fuzz_ring(surf, BCX, BCY + 2, 14, 14, _BC_DOWN_D, 24, 2, 1)
    _aaellipse(surf, _BC_DOWN_D, (BCX + 1, BCY + 3), 14, 14)
    _aaellipse(surf, _BC_DOWN,   (BCX,     BCY + 2), 13, 13)
    _aaellipse(surf, _BC_DOWN_H, (BCX - 4, BCY - 3),  5,  4)   # chest light
    # Pale belly with a brighter sheen so the body isn't a dead grey blob by day.
    _aaellipse(surf, _BC_BELLY,   (BCX + 1, BCY + 5), 9, 10)
    _aaellipse(surf, _BC_BELLY_H, (BCX,     BCY + 1), 7,  6)
    _aaellipse(surf, (250, 251, 254), (BCX - 1, BCY),  4, 3)   # hot sheen core

    # Far flipper.
    _rot_blit(surf, _bc_flipper(wing_angle_deg * 0.5 - 16), (BCX + 11, BCY + 2))

    # ── Head: OVERSIZED round head, the hero of the chibi proportion ──
    _fuzz_ring(surf, HCX - 1, HCY + 1, 14, 14, _BC_DOWN_D, 34, 2, 1)
    _aaellipse(surf, _BC_DOWN_D, (HCX,     HCY + 2), 14, 14)
    _aaellipse(surf, _BC_DOWN,   (HCX - 1, HCY + 1), 13, 13)
    # Darker grey crown cap.
    _aaellipse(surf, _BC_CAP, (HCX - 1, HCY - 5), 11, 7)
    # Pale round face mask.
    _aaellipse(surf, _BC_FACE, (HCX, HCY + 3), 10, 9)
    _aaellipse(surf, _BC_DOWN_H, (HCX - 4, HCY - 2), 4, 3)    # head sheen

    # ── HERO: huge SPARKLY eyes — two SEPARATE eyes (clear dark gap between),
    # a thin white ring around a smaller iris (pupil-in-white, not black sockets),
    # and an oversized catch-light that survives the 40px downscale. ──
    for ex in (HCX - 4, HCX + 8):
        pygame.draw.circle(surf, _BC_SURR, (ex, HCY + 1), 6)   # white sclera
        pygame.draw.circle(surf, (28, 30, 42), (ex, HCY + 1), 4)  # iris (ring of white left)
        pygame.draw.circle(surf, (255, 255, 255), (ex - 1, HCY - 1), 2)  # big catch-light
        pygame.draw.circle(surf, (235, 240, 250), (ex + 1, HCY + 3), 1)  # secondary sparkle

    # ── Tiny stubby dark beak, dropped BELOW the eye-line so it stops carving a
    # "nose socket" between the eyes. ──
    pygame.draw.polygon(surf, _BC_BEAK,
                        [(HCX, HCY + 8), (HCX + 5, HCY + 9), (HCX, HCY + 11)])

    # Near flipper.
    _rot_blit(surf, _bc_flipper(wing_angle_deg), (BCX - 6, BCY + 3))

    # ── Tiny stubby pale feet ──
    for fx in (28, 37):
        foot = [(fx - 2, BCY + 14), (fx + 3, BCY + 14),
                (fx + 3, BCY + 17), (fx - 3, BCY + 17)]
        pygame.draw.polygon(surf, _BC_FOOT, foot)
        pygame.draw.polygon(surf, _BC_DOWN_D, foot, 1)
    return surf


build = _make_prebuilt_skin(build_chick)
