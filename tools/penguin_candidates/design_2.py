"""GENTOO penguin — design_2, WAVE 2 from-scratch redraw.

The chubby cutie: a plump round casual-mascot penguin with the gentoo white
bonnet stripe across the eyes and oversized friendly eyes. Full from-scratch
build with 3-layer body shading, a generous belly gloss sheen, an AO chin
shadow, an eye-surround patch and a banded orange beak. Scratch-only — NOT
registered in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── GENTOO palette ───────────────────────────────────────────────────────────
_GE_BACK    = (35, 40, 58)          # #23283A slate-black
_GE_BACK_D  = (18, 21, 31)          # #12151F shadow
_GE_BACK_H  = (78, 90, 120)         # cool highlight
_GE_SHEEN   = (150, 168, 205)       # gloss overlay
_GE_BELLY   = (250, 250, 244)       # #FAFAF4 belly / bonnet
_GE_BELLY_D = (214, 216, 224)       # belly undershadow
_GE_BELLY_H = (255, 255, 255)       # belly top sheen
_GE_SURR    = (212, 222, 236)       # pale eye-surround patch
_GE_BEAK1   = (255, 122, 30)        # #FF7A1E deep-orange root
_GE_BEAK2   = (255, 179, 71)        # #FFB347 bright-orange tip
_GE_BEAK_D  = (190, 92, 16)         # beak outline
_GE_FOOT    = (255, 138, 42)        # #FF8A2A feet


def _ge_flipper(angle_deg):
    """Stubby slate flipper with a cool leading highlight."""
    w = pygame.Surface((34, 40), pygame.SRCALPHA)
    pts = [(18, 10), (26, 16), (21, 33), (14, 29)]
    pygame.draw.polygon(w, _GE_BACK_D, pts)
    pygame.draw.polygon(w, _GE_BACK, [(18, 11), (24, 17), (19, 29), (15, 26)])
    pygame.draw.line(w, _GE_BACK_H, (18, 13), (23, 18), 1)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def build_gentoo(wing_angle_deg):
    surf = _new()

    # Tiny tail.
    pygame.draw.polygon(surf, _GE_BACK_D,
                        [(14, BCY + 9), (8, BCY + 14), (19, BCY + 13)])

    # ── Body: plump, WIDER-than-tall chibi egg, 3-layer ──
    _aaellipse(surf, _GE_BACK_D, (BCX + 1, BCY + 2), 19, 17)   # shadow rim
    _aaellipse(surf, _GE_BACK,   (BCX,     BCY + 1), 18, 16)   # main
    _aaellipse(surf, _GE_BACK_H, (BCX - 6, BCY - 4),  7,  5)   # cool chest light

    # Gloss-sheen overlay top-left.
    sheen = pygame.Surface((24, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sheen, (*_GE_SHEEN, 110), sheen.get_rect())
    surf.blit(sheen, (BCX - 16, BCY - 13))

    # Far flipper behind.
    _rot_blit(surf, _ge_flipper(wing_angle_deg * 0.5 - 16), (BCX + 13, BCY + 1))

    # ── Big round white belly with sheen + undershadow ──
    _aaellipse(surf, _GE_BELLY,   (BCX + 1, BCY + 4), 14, 14)
    _aaellipse(surf, _GE_BELLY_H, (BCX,     BCY - 1),  9,  6)   # upper sheen
    _aaellipse(surf, _GE_BELLY_D, (BCX + 1, BCY + 11), 11, 5)   # lower shadow

    # Head — large round chibi head, nudged up + narrowed 1px and given a dark
    # rim at the body junction so it pops off the body instead of fusing at 40px.
    _aaellipse(surf, _GE_BACK_D, (HCX,     HCY),     13, 13)
    _aaellipse(surf, _GE_BACK,   (HCX - 1, HCY - 1), 11, 12)
    _aaellipse(surf, _GE_BACK_H, (HCX - 4, HCY - 4),  4,  4)
    pygame.draw.arc(surf, _GE_BACK_D, (HCX - 12, HCY + 4, 24, 14), 3.4, 6.0, 2)

    # AO chin shadow.
    sh = pygame.Surface((22, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (14, 16, 26, 95), sh.get_rect())
    surf.blit(sh, (HCX - 13, HCY + 8))

    # ── HERO: the gentoo white BONNET — a band ear-to-ear OVER the crown that
    # dips to a point behind each eye, leaving the lower face BLACK (the real
    # species tell: white headband on a black head, not a white face). ──
    pygame.draw.polygon(surf, _GE_BELLY, [
        (HCX - 11, HCY - 3), (HCX - 10, CROWN_Y), (HCX, CROWN_Y - 2),
        (HCX + 10, CROWN_Y), (HCX + 11, HCY - 3),
        (HCX + 8, HCY - 5), (HCX - 8, HCY - 5),
    ])
    # Thin tapered tails sweeping down-back behind each eye (not filled discs).
    pygame.draw.polygon(surf, _GE_BELLY,
                        [(HCX - 9, HCY - 3), (HCX - 6, HCY - 2), (HCX - 9, HCY + 4)])
    pygame.draw.polygon(surf, _GE_BELLY,
                        [(HCX + 11, HCY - 3), (HCX + 9, HCY - 2), (HCX + 12, HCY + 4)])

    # ── HERO: oversized friendly eyes (raised 1px) on small pale surrounds ──
    pygame.draw.circle(surf, _GE_SURR, (HCX - 2, HCY), 5)
    pygame.draw.circle(surf, _GE_SURR, (HCX + 7, HCY), 5)
    _eye(surf, HCX - 2, HCY, 5, iris=(22, 20, 28))
    _eye(surf, HCX + 7, HCY, 5, iris=(22, 20, 28))

    # ── Bright banded orange beak, root moved OUT so it clears the right eye ──
    root = [(HCX + 5, HCY + 5), (HCX + 14, HCY + 8), (HCX + 5, HCY + 11)]
    pygame.draw.polygon(surf, _GE_BEAK1, root)
    pygame.draw.polygon(surf, _GE_BEAK2,
                        [(HCX + 10, HCY + 6), (HCX + 14, HCY + 8),
                         (HCX + 10, HCY + 10)])              # bright tip
    pygame.draw.polygon(surf, _GE_BEAK_D, root, 1)
    pygame.draw.line(surf, (255, 220, 150), (HCX + 6, HCY + 7), (HCX + 12, HCY + 8), 1)

    # Near flipper.
    _rot_blit(surf, _ge_flipper(wing_angle_deg), (BCX - 8, BCY + 2))

    # ── Chunky orange feet, toe split ──
    for fx in (27, 39):
        foot = [(fx - 4, BCY + 16), (fx + 4, BCY + 16),
                (fx + 5, BCY + 21), (fx - 5, BCY + 21)]
        pygame.draw.polygon(surf, _GE_FOOT, foot)
        pygame.draw.polygon(surf, _GE_BEAK_D, foot, 1)
        pygame.draw.line(surf, _GE_BEAK_D, (fx, BCY + 21), (fx, BCY + 18), 1)
    return surf


build = _make_prebuilt_skin(build_gentoo)
