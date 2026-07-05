"""Shared flamingo chassis for the TAIL-only redesign.

Only the flamingo's tail is being revised — the production tail (two thin sharp
triangles drawn behind the body) reads as a detached shard rather than plumage
growing off the rump. This module reproduces the ENTIRE production flamingo
(`game/animal_skins.build_flamingo`) EXCEPT the tail, which each candidate
supplies as `tail_fn(surf)`. The tail is drawn FIRST (behind the body) at the
same z-order as production, so each design only varies that one element.

Palette, helpers and body/neck/head/beak/wing/leg geometry are copied verbatim
from production so the comparison isolates the tail change.
"""
import pygame

from game.parrot import _aaellipse
from game.animal_skins import (
    _make_prebuilt_skin, _new, _rot_blit, _eye, _flap,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── production flamingo palette (verbatim) ───────────────────────────────────
_FLA_BODY   = (255, 120, 158)
_FLA_BODY_D = (224, 84, 128)
_FLA_BODY_H = (255, 178, 200)
_FLA_NECK   = (255, 134, 170)
_FLA_LEG    = (236, 96, 130)
_FLA_BEAK   = (250, 214, 120)
_FLA_BEAK_T = (32, 30, 40)


def _fla_wing(angle_deg):
    w = pygame.Surface((42, 40), pygame.SRCALPHA)
    pts = [(20, 20), (38, 14), (38, 28), (22, 34), (12, 28)]
    pygame.draw.polygon(w, _FLA_BODY_D, pts)
    pygame.draw.polygon(w, _FLA_BODY, [(20, 20), (36, 16), (35, 26), (20, 30)])
    pygame.draw.polygon(w, _FLA_BODY_H, [(30, 16), (38, 18), (36, 24)])
    pygame.draw.line(w, _FLA_BODY_H, (21, 21), (35, 17), 1)
    return pygame.transform.rotate(w, angle_deg)


def build_flamingo(wing_angle_deg, tail_fn):
    surf = _new()

    # ── TAIL (behind the body) — the only varying element ──
    tail_fn(surf)

    # Rounded body, sitting a touch lower so the neck has room.
    _aaellipse(surf, _FLA_BODY_D, (BCX + 1, BCY + 3), 16, 13)
    _aaellipse(surf, _FLA_BODY, (BCX, BCY + 2), 15, 12)
    _aaellipse(surf, _FLA_BODY_H, (BCX - 3, BCY - 1), 8, 5)

    _rot_blit(surf, _fla_wing(wing_angle_deg * 0.5 - 14), (BCX + 7, BCY - 1))

    # ── HERO: the S-curve neck sweeping up then forward ──
    spine = [(BCX + 9, BCY - 1), (BCX + 13, BCY - 10),
             (BCX + 12, CROWN_Y + 4), (HCX - 4, CROWN_Y),
             (HCX, CROWN_Y - 3)]
    pygame.draw.lines(surf, _FLA_NECK, False, spine, 6)
    pygame.draw.lines(surf, _FLA_BODY_H, False, spine[:3], 1)

    # Small head at the top of the S.
    hx, hy = HCX, CROWN_Y - 3
    _aaellipse(surf, _FLA_BODY, (hx, hy), 7, 6)
    _aaellipse(surf, _FLA_BODY_H, (hx - 2, hy - 1), 3, 2)
    _eye(surf, hx + 1, hy - 1, 3)
    # Down-hooked beak: yellow base, black tip.
    pygame.draw.polygon(surf, _FLA_BEAK,
                        [(hx + 4, hy - 1), (hx + 12, hy + 2),
                         (hx + 11, hy + 5), (hx + 4, hy + 3)])
    pygame.draw.polygon(surf, _FLA_BEAK_T,
                        [(hx + 10, hy + 2), (hx + 13, hy + 4),
                         (hx + 10, hy + 6)])
    pygame.draw.polygon(surf, _FLA_BODY_D,
                        [(hx + 4, hy - 1), (hx + 12, hy + 2),
                         (hx + 11, hy + 5), (hx + 4, hy + 3)], 1)

    # Near wing over body.
    _rot_blit(surf, _fla_wing(wing_angle_deg), (BCX - 3, BCY))
    # Long thin legs (one folded forward, flamingo style).
    f = _flap(wing_angle_deg)
    kx = BCX + int(2 + f * 3)
    pygame.draw.lines(surf, _FLA_LEG, False,
                      [(BCX + 2, BCY + 12), (kx, BCY + 19),
                       (kx + 5, BCY + 16)], 2)
    pygame.draw.line(surf, _FLA_LEG, (BCX + 6, BCY + 12),
                     (BCX + 7, BCY + 20), 2)
    return surf


def make(tail_fn):
    """Wrap a tail_fn into a cached (frame_idx, tilt_deg) -> Surface getter."""
    return _make_prebuilt_skin(lambda a: build_flamingo(a, tail_fn))


# The PRODUCTION tail (for the comparison's ORIGINAL column / reference).
def tail_original(surf):
    pygame.draw.polygon(surf, _FLA_BODY_D,
                        [(11, BCY - 2), (2, BCY + 6), (15, BCY + 8)])
    pygame.draw.polygon(surf, _FLA_BODY_H,
                        [(12, BCY), (5, BCY + 5), (15, BCY + 6)])
