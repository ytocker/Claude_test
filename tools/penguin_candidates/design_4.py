"""ROCKHOPPER penguin — design_4, WAVE 2 from-scratch redraw.

The punk crested penguin, rebuilt from scratch on a properly crafted body (wave 1
just bolted the crest onto the flat chassis). Bold integrated spiky golden brow
crest + fiery red eyes over a 3-layer navy body with a chest highlight, gloss
sheen and feather-textured flippers, plus a chunky outlined beak. Scratch-only —
NOT registered in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── ROCKHOPPER palette ────────────────────────────────────────────────────────
_RH_BACK    = (38, 43, 64)          # #262B40 navy
_RH_BACK_D  = (21, 25, 42)          # #15192A shadow
_RH_BACK_H  = (90, 100, 134)        # #5A6486 cool highlight
_RH_SHEEN   = (150, 166, 205)       # gloss overlay
_RH_BELLY   = (247, 244, 236)       # #F7F4EC belly
_RH_BELLY_D = (212, 210, 202)       # belly undershadow
_RH_BELLY_H = (255, 255, 255)       # belly sheen
_RH_CREST   = (255, 210, 30)        # #FFD21E crest plume
_RH_CREST_D = (214, 162, 14)        # #D6A20E plume root / flank
_RH_CREST_H = (255, 236, 130)       # #FFEC82 bright plume lick
_RH_BEAK    = (255, 138, 30)        # #FF8A1E orange beak / feet
_RH_BEAK_D  = (198, 96, 16)         # beak shadow / outline
_RH_EYE     = (242, 64, 46)         # #F2402E fiery red iris


def _rh_flipper(angle_deg):
    """Navy flipper with a strong cool leading-edge highlight so it reads as a
    wing (interior feather ticks dropped — sub-pixel noise at gameplay scale)."""
    w = pygame.Surface((34, 42), pygame.SRCALPHA)
    pts = [(18, 9), (27, 16), (22, 35), (13, 30)]
    pygame.draw.polygon(w, _RH_BACK_D, pts)
    pygame.draw.polygon(w, _RH_BACK, [(18, 11), (25, 17), (20, 31), (15, 27)])
    pygame.draw.line(w, _RH_BACK_H, (18, 11), (25, 18), 2)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def _crest_plume(surf, root_x, root_y, tip_x, tip_y, base_w):
    """One FAT upswept brow plume: dark keyline + deep flank + bright inner lick
    so the spike survives the 40px downscale AND separates from the sky and from
    the neighbouring plumes (gold-on-blue has weak value contrast on its own)."""
    outer = [(root_x - base_w, root_y), (tip_x, tip_y), (root_x + base_w, root_y + 1)]
    pygame.draw.polygon(surf, _RH_BACK_D, outer)             # dark keyline base
    pygame.draw.polygon(surf, _RH_CREST_D, [
        (root_x - base_w + 1, root_y), (tip_x, tip_y + 1),
        (root_x + base_w - 1, root_y)])
    pygame.draw.polygon(surf, _RH_CREST, [
        (root_x - base_w + 2, root_y), (tip_x, tip_y + 2),
        (root_x + base_w - 2, root_y)])
    pygame.draw.line(surf, _RH_CREST_H, (root_x, root_y - 1), (tip_x, tip_y + 2), 1)
    pygame.draw.polygon(surf, _RH_BACK_D, outer, 1)          # outer keyline stroke


def build_rockhopper(wing_angle_deg):
    surf = _new()

    # Stubby layered tail.
    pygame.draw.polygon(surf, _RH_BACK_D,
                        [(13, BCY + 7), (5, BCY + 14), (18, BCY + 13)])
    pygame.draw.polygon(surf, _RH_BACK,
                        [(14, BCY + 8), (8, BCY + 12), (18, BCY + 12)])

    # ── Body: 3-layer navy egg + chest highlight ──
    _aaellipse(surf, _RH_BACK_D, (BCX + 1, BCY + 1), 18, 18)
    _aaellipse(surf, _RH_BACK,   (BCX,     BCY),     17, 17)
    _aaellipse(surf, _RH_BACK_H, (BCX - 5, BCY - 6),  7,  6)

    # Gloss-sheen overlay.
    sheen = pygame.Surface((22, 9), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*_RH_SHEEN, 100), sheen.get_rect())
    surf.blit(sheen, (BCX - 15, BCY - 14))

    # Far flipper.
    _rot_blit(surf, _rh_flipper(wing_angle_deg * 0.5 - 16), (BCX + 12, BCY))

    # ── White belly with sheen + undershadow ──
    _aaellipse(surf, _RH_BELLY,   (BCX + 1, BCY + 3), 12, 14)
    _aaellipse(surf, _RH_BELLY_H, (BCX,     BCY - 2),  8,  6)
    _aaellipse(surf, _RH_BELLY_D, (BCX + 1, BCY + 10), 9,  5)

    # Head dome (3-layer) + a cool rim-light on the crown/upper-back so the
    # navy dome pops off dark night skies.
    _aaellipse(surf, _RH_BACK_D, (HCX,     HCY + 2), 12, 12)
    _aaellipse(surf, _RH_BACK,   (HCX - 1, HCY + 1), 11, 11)
    _aaellipse(surf, _RH_BACK_H, (HCX - 4, HCY - 3),  4,  4)
    pygame.draw.arc(surf, _RH_BACK_H, (HCX - 11, HCY - 10, 22, 20), 0.5, 2.4, 1)
    pygame.draw.arc(surf, _RH_BACK_H, (BCX - 16, BCY - 16, 22, 26), 1.3, 2.6, 1)

    # ── HERO: bold spiky golden brow-fan — 4 FAT wide-splayed plumes with dark
    # keylines so the crest carries the silhouette in flight, not just in close-up.
    _crest_plume(surf, HCX - 6, CROWN_Y + 5, HCX - 18, CROWN_Y - 9, 6)
    _crest_plume(surf, HCX - 1, CROWN_Y + 3, HCX - 3, CROWN_Y - 17, 8)
    _crest_plume(surf, HCX + 5, CROWN_Y + 4, HCX + 9, CROWN_Y - 14, 7)
    _crest_plume(surf, HCX + 9, CROWN_Y + 5, HCX + 20, CROWN_Y - 7, 6)

    # Red eyes on a pale face bed so they read against the dark head.
    _aaellipse(surf, _RH_BELLY, (HCX + 1, HCY), 7, 6)
    _eye(surf, HCX - 1, HCY, 4, iris=_RH_EYE)
    _eye(surf, HCX + 5, HCY, 4, iris=_RH_EYE)

    # ── Chunky outlined orange beak + lower-mandible wedge + highlight ──
    beak = [(HCX + 2, HCY + 3), (HCX + 12, HCY + 7), (HCX + 2, HCY + 10)]
    pygame.draw.polygon(surf, _RH_BEAK, beak)
    pygame.draw.polygon(surf, _RH_BEAK_D,
                        [(HCX + 2, HCY + 7), (HCX + 12, HCY + 7),
                         (HCX + 2, HCY + 10)])
    pygame.draw.polygon(surf, _RH_BACK_D, beak, 1)
    pygame.draw.line(surf, (255, 200, 120), (HCX + 3, HCY + 5), (HCX + 10, HCY + 6), 1)

    # Near flipper.
    _rot_blit(surf, _rh_flipper(wing_angle_deg), (BCX - 7, BCY + 1))

    # ── Wide-set hopping feet with toe splits ──
    for fx in (25, 39):
        foot = [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                (fx + 4, BCY + 20), (fx - 4, BCY + 20)]
        pygame.draw.polygon(surf, _RH_BEAK, foot)
        pygame.draw.polygon(surf, _RH_BEAK_D, foot, 1)
        for tx in (fx - 1, fx + 2):
            pygame.draw.line(surf, _RH_BEAK_D, (tx, BCY + 20), (tx, BCY + 18), 1)
    return surf


build = _make_prebuilt_skin(build_rockhopper)
