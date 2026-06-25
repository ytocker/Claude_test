"""ADÉLIE penguin — design_1, WAVE 2 from-scratch redraw.

The definitive penguin drawn really well: a crisp glossy blue-black tuxedo with
the signature white eye-ring. NOT the flat chassis with props — the body, head,
beak, flippers and feet are all rebuilt with the premium shading the project's
best animals use (3-layer body + chest-highlight ellipse + gloss-sheen overlay,
outlined beak with a highlight line, eye surround). Scratch-only — NOT registered
in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── ADÉLIE palette ───────────────────────────────────────────────────────────
_AD_BACK    = (27, 36, 54)          # #1B2436 glossy blue-black
_AD_BACK_D  = (15, 22, 38)          # #0F1626 deep shadow rim
_AD_BACK_H  = (70, 85, 122)         # #46557A cool blue chest highlight
_AD_SHEEN   = (150, 168, 210)       # soft blue gloss overlay
_AD_BELLY   = (246, 247, 251)       # #F6F7FB off-white belly
_AD_BELLY_D = (208, 214, 226)       # belly undershadow
_AD_BELLY_H = (255, 255, 255)       # belly top sheen
_AD_RING    = (238, 240, 248)       # white eye-ring
_AD_BEAK    = (210, 120, 50)        # #D27832 warm orange beak (the colour anchor)
_AD_BEAK_D  = (168, 88, 28)         # #A8581C lower-mandible shadow / outline
_AD_BEAK_H  = (240, 168, 88)        # #F0A858 warm top highlight
_AD_FOOT    = (255, 154, 60)        # #FF9A3C foot orange
_AD_FOOT_D  = (200, 110, 32)        # foot shadow / outline


def _ad_flipper(angle_deg):
    """Blue-black flipper with a cool 1px leading-edge highlight."""
    w = pygame.Surface((34, 42), pygame.SRCALPHA)
    pts = [(18, 9), (27, 16), (22, 35), (13, 30)]
    pygame.draw.polygon(w, _AD_BACK_D, pts)
    pygame.draw.polygon(w, _AD_BACK, [(18, 11), (25, 17), (20, 31), (15, 27)])
    pygame.draw.line(w, _AD_BACK_H, (18, 12), (24, 18), 1)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def build_adelie(wing_angle_deg):
    surf = _new()

    # Stubby tail — layered, outer point pulled in so it stays attached to the
    # body mass at flap angles (no detached spike).
    pygame.draw.polygon(surf, _AD_BACK_D,
                        [(14, BCY + 7), (7, BCY + 13), (18, BCY + 13)])
    pygame.draw.polygon(surf, _AD_BACK,
                        [(15, BCY + 8), (10, BCY + 12), (18, BCY + 12)])

    # ── Body: 3-layer glossy blue-black egg + chest highlight ──
    _aaellipse(surf, _AD_BACK_D, (BCX + 1, BCY + 1), 18, 18)   # shadow rim
    _aaellipse(surf, _AD_BACK,   (BCX,     BCY),     17, 17)   # main
    _aaellipse(surf, _AD_BACK_H, (BCX - 7, BCY - 8),  5,  4)   # cool backlight (up onto back)

    # Gloss-sheen overlay top-left — the premium wet read (toucan technique).
    sheen = pygame.Surface((22, 9), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*_AD_SHEEN, 110), sheen.get_rect())
    surf.blit(sheen, (BCX - 15, BCY - 14))

    # Far flipper behind.
    _rot_blit(surf, _ad_flipper(wing_angle_deg * 0.5 - 16), (BCX + 12, BCY))

    # ── White belly: oval + top sheen + lower undershadow ──
    _aaellipse(surf, _AD_BELLY,   (BCX + 1, BCY + 3), 12, 14)
    _aaellipse(surf, _AD_BELLY_H, (BCX,     BCY - 2),  8,  6)   # upper sheen
    _aaellipse(surf, _AD_BELLY_D, (BCX + 1, BCY + 10), 9,  5)   # lower shadow

    # Head dome (3-layer), merging into the body with a little neck.
    _aaellipse(surf, _AD_BACK_D, (HCX,     HCY + 2), 12, 12)
    _aaellipse(surf, _AD_BACK,   (HCX - 1, HCY + 1), 11, 11)
    _aaellipse(surf, _AD_BACK_H, (HCX - 4, HCY - 3),  4,  4)   # head sheen

    # AO shadow under the chin where head meets the white belly.
    sh = pygame.Surface((20, 7), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (12, 16, 28, 90), sh.get_rect())
    surf.blit(sh, (HCX - 12, HCY + 8))

    # ── HERO: two SEPARATE white eye-rings on the blue-black head ──
    # Spaced wide with a dark gap of _AD_BACK between, and only a thin rim of
    # white around a big r4 iris (the real Adélie look — a rim, not a white mask).
    for ex in (HCX - 3, HCX + 8):
        pygame.draw.circle(surf, _AD_RING, (ex, HCY), 5)
    _eye(surf, HCX - 3, HCY, 4, iris=(18, 16, 22))
    _eye(surf, HCX + 8, HCY, 4, iris=(18, 16, 22))

    # ── Neat short ORANGE beak (the one warm colour anchor): banded + highlight,
    # sat below the eye-line so it never collides with the rings. ──
    beak = [(HCX + 3, HCY + 5), (HCX + 12, HCY + 7), (HCX + 3, HCY + 10)]
    pygame.draw.polygon(surf, _AD_BEAK, beak)
    pygame.draw.polygon(surf, _AD_BEAK_D,
                        [(HCX + 3, HCY + 8), (HCX + 12, HCY + 7),
                         (HCX + 3, HCY + 10)])               # lower-mandible shadow
    pygame.draw.polygon(surf, _AD_BEAK_D, beak, 1)           # outline
    pygame.draw.line(surf, _AD_BEAK_H, (HCX + 4, HCY + 6), (HCX + 10, HCY + 7), 1)

    # Near flipper over the body — lifted so its dark edge doesn't gash the
    # white belly sheen.
    _rot_blit(surf, _ad_flipper(wing_angle_deg), (BCX - 7, BCY - 2))

    # ── Tidy orange feet: toe split + outline ──
    for fx in (27, 38):
        foot = [(fx - 3, BCY + 16), (fx + 4, BCY + 16),
                (fx + 5, BCY + 20), (fx - 4, BCY + 20)]
        pygame.draw.polygon(surf, _AD_FOOT, foot)
        pygame.draw.polygon(surf, _AD_FOOT_D, foot, 1)
        pygame.draw.line(surf, _AD_FOOT_D, (fx + 1, BCY + 20), (fx + 1, BCY + 18), 1)
    return surf


build = _make_prebuilt_skin(build_adelie)
