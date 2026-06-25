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
_AD_BEAK    = (44, 34, 48)          # #2A2230 dark stubby beak
_AD_BEAK_W  = (210, 120, 50)        # warm orange base wash
_AD_BEAK_H  = (150, 120, 150)       # beak highlight line
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

    # Stubby tail — layered so it reads as plumage, not a flat triangle.
    pygame.draw.polygon(surf, _AD_BACK_D,
                        [(13, BCY + 7), (5, BCY + 14), (18, BCY + 13)])
    pygame.draw.polygon(surf, _AD_BACK,
                        [(14, BCY + 8), (8, BCY + 12), (18, BCY + 12)])

    # ── Body: 3-layer glossy blue-black egg + chest highlight ──
    _aaellipse(surf, _AD_BACK_D, (BCX + 1, BCY + 1), 18, 18)   # shadow rim
    _aaellipse(surf, _AD_BACK,   (BCX,     BCY),     17, 17)   # main
    _aaellipse(surf, _AD_BACK_H, (BCX - 5, BCY - 6),  7,  6)   # cool chest light

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

    # ── HERO: clean white eye-rings on the blue-black head ──
    # A pale ring behind each eye is the Adélie tell; bigger r4 eyes read at 40px.
    pygame.draw.circle(surf, _AD_RING, (HCX - 2, HCY), 5)
    pygame.draw.circle(surf, _AD_RING, (HCX + 6, HCY), 5)
    _eye(surf, HCX - 2, HCY, 4, iris=(18, 16, 22))
    _eye(surf, HCX + 6, HCY, 4, iris=(18, 16, 22))

    # ── Neat short beak: dark with a warm base wash + highlight line ──
    beak = [(HCX + 3, HCY + 3), (HCX + 12, HCY + 6), (HCX + 3, HCY + 9)]
    pygame.draw.polygon(surf, _AD_BEAK_W, beak)              # warm base
    pygame.draw.polygon(surf, _AD_BEAK,
                        [(HCX + 6, HCY + 4), (HCX + 12, HCY + 6),
                         (HCX + 6, HCY + 8)])                # dark tip
    pygame.draw.polygon(surf, _AD_BACK_D, beak, 1)           # outline
    pygame.draw.line(surf, _AD_BEAK_H, (HCX + 4, HCY + 5), (HCX + 10, HCY + 6), 1)

    # Near flipper over the body.
    _rot_blit(surf, _ad_flipper(wing_angle_deg), (BCX - 7, BCY + 1))

    # ── Tidy orange feet: toe split + outline ──
    for fx in (27, 38):
        foot = [(fx - 3, BCY + 16), (fx + 4, BCY + 16),
                (fx + 5, BCY + 20), (fx - 4, BCY + 20)]
        pygame.draw.polygon(surf, _AD_FOOT, foot)
        pygame.draw.polygon(surf, _AD_FOOT_D, foot, 1)
        pygame.draw.line(surf, _AD_FOOT_D, (fx + 1, BCY + 20), (fx + 1, BCY + 18), 1)
    return surf


build = _make_prebuilt_skin(build_adelie)
