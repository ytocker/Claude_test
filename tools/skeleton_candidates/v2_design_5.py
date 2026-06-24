"""v2_design_5 — AUREX-MACAW: cursed gold-lich parrot skeleton.

The ``_v2_anatomy`` parrot skeleton (hooked bone beak + long tail) gilded in
gold so the gold skull is the brightest mass, with two hot violet rune-fire
socket points and a dark tattered mantle behind the shoulders (a dark silhouette,
not a violet glow). One gold coin at the feet. Scratch only.
"""
import pygame

from game.store_skins import _make_prebuilt_skin, _poly
from tools.skeleton_candidates import _v2_anatomy as A


# Gilded bone over a near-black flesh; gold is the brightest element.
P = A.Pal(
    bone=(255, 226, 122), bone_sh=(224, 162, 30), bone_deep=(150, 100, 12),
    body=(20, 18, 14), body_deep=(12, 10, 8), keyline=(60, 40, 8),
    socket=(40, 16, 60), glint=(255, 244, 200),
)

_MANTLE, _MANTLE_RIM = (22, 18, 31), (90, 70, 18)
_VIOLET = (184, 120, 255)
_GOLD_H = (255, 248, 210)


def _mantle(surf, angle_deg, P):
    # Dark tattered mantle behind the shoulders — a DARK silhouette collar+drape,
    # well below the gold value so the gold skull wins the read.
    drape = [(20, 22), (38, 20), (40, 36), (30, 44), (18, 40), (16, 28)]
    _poly(surf, _MANTLE, drape)
    pygame.draw.line(surf, _MANTLE_RIM, (22, 22), (37, 21), 1)   # thin collar rim


def _runes(surf, angle_deg, P):
    # Two contained violet socket pips (the only hot violet on the bird) + a
    # single gold coin disc at the feet.
    glow = pygame.Surface((A.SPRITE_W, A.SPRITE_H), pygame.SRCALPHA)
    pygame.draw.circle(glow, (*_VIOLET, 200), (45, 16), 2)
    pygame.draw.circle(glow, (*_VIOLET, 110), (45, 16), 3, 1)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    # Gold crown band across the brow (equal value to the dome, dark under-rim).
    pygame.draw.line(surf, P.keyline, (39, 11), (53, 11), 3)
    pygame.draw.line(surf, P.bone, (39, 10), (53, 10), 2)
    pygame.draw.circle(surf, _GOLD_H, (46, 10), 1)
    # One gold coin disc at the feet.
    pygame.draw.circle(surf, P.keyline, (30, 53), 3)
    pygame.draw.circle(surf, P.bone, (30, 53), 2)
    pygame.draw.circle(surf, _GOLD_H, (29, 52), 1)


def _build(wing_angle_deg):
    return A.build_skeleton(wing_angle_deg, P, pre=_mantle, post=_runes,
                            socket_fill=(60, 24, 90))


build = _make_prebuilt_skin(_build)
