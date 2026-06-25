"""EMPEROR penguin — design_2 of the penguin store-skin redesign.

The regal gradient royal: the premium grown-up penguin, carried by a vertical
slate→steel body gradient and an orange→yellow ear-to-throat melt that the flat
build can never show. No crest — elegance by colour, deliberate contrast to the
spiky ROCKHOPPER. The 40px hero read is the warm orange ear-patch bleeding into
a golden-yellow bib against a cool slate body.

Built on the same chassis as ``animal_skins.build_penguin``. Scratch-only —
NOT registered in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye, _pen_flipper,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── EMPEROR palette ───────────────────────────────────────────────────────────
_EM_SLATE   = (44, 53, 80)          # #2C3550 dark slate (body gradient top)
_EM_SLATE_D = (28, 34, 55)          # deeper shadow rim
_EM_STEEL   = (90, 106, 134)        # #5A6A86 lighter steel (gradient base)
_EM_BELLY   = (255, 253, 246)       # #FFFDF6 white belly
_EM_BELLY_D = (210, 212, 218)       # soft belly undershadow
_EM_ORANGE  = (240, 138, 40)        # #F08A28 burnt-amber ear-patch (cooled for regal)
_EM_AMBER   = (248, 184, 70)        # amber mid-tone in the ear-to-throat melt
_EM_YELLOW  = (255, 218, 106)       # #FFDA6A golden-yellow throat bib (lifted)
_EM_YELLOW_U = (228, 168, 60)       # amber underline so the collar separates from belly
_EM_CORAL   = (255, 156, 176)       # #FF9CB0 coral lower-mandible stripe
_EM_FLIPRIM = (170, 194, 222)       # pale-blue flipper leading-edge rim
_EM_FOOT    = (60, 72, 96)          # dark slate-grey webbed feet


def _em_flipper(angle_deg):
    """Slate flipper with a thin pale-blue leading-edge rim for the regal read."""
    w = pygame.Surface((34, 40), pygame.SRCALPHA)
    pts = [(18, 10), (26, 16), (22, 34), (14, 30)]
    pygame.draw.polygon(w, _EM_SLATE_D, pts)
    pygame.draw.polygon(w, _EM_SLATE, [(18, 11), (24, 17), (20, 30), (15, 27)])
    pygame.draw.line(w, _EM_FLIPRIM, (18, 13), (22, 18), 1)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def build_emperor(wing_angle_deg):
    surf = _new()

    # Stubby tail — slate-dark.
    pygame.draw.polygon(surf, _EM_SLATE_D,
                        [(13, BCY + 8), (6, BCY + 14), (18, BCY + 14)])

    # ── Taller egg body with a faked vertical slate→steel gradient ──
    # Three nested ellipses shrinking upward produce a cooler-dark top and a
    # lighter steel lower-body; the white belly oval completes the emperor split.
    _aaellipse(surf, _EM_SLATE_D, (BCX + 1, BCY + 1), 17, 19)   # shadow rim
    _aaellipse(surf, _EM_SLATE,   (BCX,     BCY),      16, 18)   # top slate
    _aaellipse(surf, _EM_STEEL,   (BCX + 1, BCY + 7),  15, 12)  # steel belly
    # White belly oval.
    _aaellipse(surf, _EM_BELLY,   (BCX + 1, BCY + 4),  11, 13)
    _aaellipse(surf, _EM_BELLY_D, (BCX + 1, BCY + 10),  9,  5)
    # Pale-steel lit edge on the upper-left back — a 1px rim so the slate form
    # keeps separation against dark night pillars (matches the flipper rim).
    pygame.draw.arc(surf, _EM_FLIPRIM,
                    (BCX - 16, BCY - 17, 22, 26), 1.4, 3.0, 2)

    # Far slate flipper.
    _rot_blit(surf, _em_flipper(wing_angle_deg * 0.5 - 16), (BCX + 11, BCY))

    # Head — smooth, crest-less slate dome merging into body.
    _aaellipse(surf, _EM_SLATE_D, (HCX,     HCY + 2), 12, 12)
    _aaellipse(surf, _EM_SLATE,   (HCX - 1, HCY + 1), 11, 11)

    # ── Ear-to-throat melt: a narrow vertical teardrop down each side of the
    # neck into the chest bib — the real king/emperor silhouette. Small,
    # outboard, diagonal so the warm reads as an elegant accent, not a mask. ──
    for sx in (-1, 1):
        ex = HCX + sx * 9
        _aaellipse(surf, _EM_YELLOW, (ex - sx, HCY + 9), 4, 6)   # bib tip (inner/low)
        _aaellipse(surf, _EM_AMBER,  (ex,      HCY + 4), 4, 5)   # mid fade
        _aaellipse(surf, _EM_ORANGE, (ex + sx, HCY - 1), 4, 4)   # ear-patch (outer/high)
    # Glowing yellow chest bib connecting both sides, with an amber underline so
    # the collar separates cleanly from the white belly at 40px.
    _aaellipse(surf, _EM_YELLOW,   (HCX, HCY + 11), 9, 5)
    _aaellipse(surf, _EM_YELLOW_U, (HCX, HCY + 14), 8, 2)

    # White face (no rosy cheek — stately). Drawn over the melt so the eyes sit
    # on white, never on the warm patches.
    _aaellipse(surf, _EM_BELLY, (HCX, HCY + 3), 8, 8)

    # Eyes — symmetric dark dots with a catch-light, regal-forward gaze.
    _eye(surf, HCX - 3, HCY, 3)
    _eye(surf, HCX + 3, HCY, 3)

    # Long slender beak: upper mandible in soft slate, lower in coral pink.
    pygame.draw.polygon(surf, _EM_STEEL,
                        [(HCX + 2, HCY + 3), (HCX + 13, HCY + 6),
                         (HCX + 2, HCY + 7)])
    pygame.draw.polygon(surf, _EM_CORAL,
                        [(HCX + 2, HCY + 7), (HCX + 13, HCY + 6),
                         (HCX + 2, HCY + 9)])

    # Near slate flipper.
    _rot_blit(surf, _em_flipper(wing_angle_deg), (BCX - 6, BCY + 1))

    # Dark slate-grey webbed feet.
    for fx in (27, 37):
        pygame.draw.polygon(surf, _EM_FOOT,
                            [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 4, BCY + 20), (fx - 4, BCY + 20)])
        pygame.draw.polygon(surf, _EM_SLATE_D,
                            [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 4, BCY + 20), (fx - 4, BCY + 20)], 1)
    return surf


build = _make_prebuilt_skin(build_emperor)
