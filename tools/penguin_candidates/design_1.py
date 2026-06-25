"""ROCKHOPPER penguin — design_1 of the penguin store-skin redesign.

The flat ``skin_penguin`` reads as default penguin clip-art. ROCKHOPPER fixes
that with the one thing it lacks: a crown-breaking crest. The hero read is a
fan of spiky upswept golden-yellow brow plumes exploding up-and-out past the
crown off a black head, paired with bold red eyes — the truest "penguin with
attitude" silhouette and a bulletproof 40px tell.

Built on the same chassis as ``animal_skins.build_penguin`` (navy-back /
white-belly egg, little-neck head, stubby flipper flap), with the crest, red
eyes, fatter beak and set-apart hopping feet layered on top. Scratch-only —
NOT registered in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye, _pen_flipper,
    BCX, BCY, HCX, HCY, CROWN_Y,
)


# ── ROCKHOPPER palette ───────────────────────────────────────────────────────
_RH_BACK    = (30, 34, 51)          # #1E2233 near-black head/back
_RH_BACK_D  = (18, 20, 34)          # deepened back shadow for the egg rim
_RH_BACK_H  = (78, 86, 112)         # cool flipper leading-edge highlight
_RH_BELLY   = (247, 244, 236)       # #F7F4EC white belly / face
_RH_BELLY_D = (212, 210, 202)       # soft belly undershadow
_RH_CREST   = (255, 210, 30)        # #FFD21E yellow crest plume
_RH_CREST_D = (214, 162, 14)        # plume root / shading for depth
_RH_CREST_H = (255, 236, 130)       # bright plume highlight lick
_RH_BEAK    = (255, 138, 30)        # #FF8A1E orange beak / feet
_RH_BEAK_D  = (198, 96, 16)         # beak / foot shadow + outline
_RH_EYE     = (226, 59, 46)         # #E23B2E fiery red iris (species tell)


def _crest_plume(surf, root_x, root_y, tip_x, tip_y, base_w):
    """One spiky upswept brow plume: a fat-rooted triangle tapering to a point.

    Drawn root→tip with a deep flank and a bright inner lick so the spike still
    reads as a glowing yellow shard after the 40px downscale; the 2px-min base
    keeps the point from vanishing."""
    pygame.draw.polygon(surf, _RH_CREST_D, [
        (root_x - base_w, root_y),
        (tip_x, tip_y),
        (root_x + base_w, root_y + 1),
    ])
    pygame.draw.polygon(surf, _RH_CREST, [
        (root_x - base_w + 1, root_y),
        (tip_x, tip_y + 1),
        (root_x + base_w - 1, root_y),
    ])
    pygame.draw.line(surf, _RH_CREST_H, (root_x, root_y - 1), (tip_x, tip_y + 1), 1)


def build_rockhopper(wing_angle_deg):
    surf = _new()
    # Stubby tail.
    pygame.draw.polygon(surf, _RH_BACK_D,
                        [(13, BCY + 8), (6, BCY + 14), (18, BCY + 14)])
    # Egg-shaped body (near-black back).
    _aaellipse(surf, _RH_BACK_D, (BCX + 1, BCY + 1), 17, 18)
    _aaellipse(surf, _RH_BACK, (BCX, BCY), 16, 17)
    # White belly oval — the high-contrast two-tone split (never broken).
    _aaellipse(surf, _RH_BELLY, (BCX + 1, BCY + 3), 11, 14)
    _aaellipse(surf, _RH_BELLY_D, (BCX + 1, BCY + 9), 9, 6)

    # Far flipper tucked behind, dark with a pale leading edge.
    _rot_blit(surf, _pen_flipper(wing_angle_deg * 0.5 - 16), (BCX + 11, BCY))

    # Head merges into body (penguin little-neck look).
    _aaellipse(surf, _RH_BACK_D, (HCX, HCY + 2), 12, 12)
    _aaellipse(surf, _RH_BACK, (HCX - 1, HCY + 1), 11, 11)
    # White face mask, narrowed a touch so the dark brow above reads under the
    # crest instead of a full white dome eating the spikes' contrast.
    _aaellipse(surf, _RH_BELLY, (HCX, HCY + 4), 7, 7)

    # ── HERO: spiky golden brow-plume fan exploding up past the crown ──
    # Roots ride the brow just above each eye; tips fan up-and-back past
    # CROWN_Y (24) to y~9-14, with two stray flicks breaking the silhouette so
    # it never settles into a smooth cap. Back plumes first so front overlap.
    # Outer-left back flick (the strayest break).
    _crest_plume(surf, HCX - 7, CROWN_Y + 5, HCX - 13, CROWN_Y - 12, 3)
    _crest_plume(surf, HCX - 4, CROWN_Y + 4, HCX - 8, CROWN_Y - 15, 4)
    # Centre brace — tallest, near-vertical with a slight back rake.
    _crest_plume(surf, HCX, CROWN_Y + 3, HCX - 1, CROWN_Y - 16, 4)
    _crest_plume(surf, HCX + 4, CROWN_Y + 4, HCX + 6, CROWN_Y - 14, 4)
    # Outer-right forward flicks (sweep up-and-out over the brow).
    _crest_plume(surf, HCX + 7, CROWN_Y + 5, HCX + 13, CROWN_Y - 11, 3)
    _crest_plume(surf, HCX + 9, CROWN_Y + 6, HCX + 16, CROWN_Y - 5, 2)

    # ── Red eyes — the rockhopper species tell, two close fiery dots ──
    _eye(surf, HCX - 2, HCY + 1, 3, iris=_RH_EYE)
    _eye(surf, HCX + 5, HCY + 1, 3, iris=_RH_EYE)

    # Fatter stubby orange beak (chunky rockhopper bill, not a thin sliver).
    beak = [(HCX + 2, HCY + 3), (HCX + 12, HCY + 7), (HCX + 2, HCY + 10)]
    pygame.draw.polygon(surf, _RH_BEAK, beak)
    pygame.draw.polygon(surf, _RH_BEAK_D, beak, 1)
    # Mandible line so the chunky bill reads as two plates, not a wedge.
    pygame.draw.line(surf, _RH_BEAK_D, (HCX + 3, HCY + 7), (HCX + 11, HCY + 7), 1)

    # Near flipper over the body.
    _rot_blit(surf, _pen_flipper(wing_angle_deg), (BCX - 6, BCY + 1))

    # Pink-orange webbed feet set WIDE apart — the hopping stance.
    for fx in (25, 39):
        foot = [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                (fx + 4, BCY + 20), (fx - 4, BCY + 20)]
        pygame.draw.polygon(surf, _RH_BEAK, foot)
        pygame.draw.polygon(surf, _RH_BEAK_D, foot, 1)
    return surf


build = _make_prebuilt_skin(build_rockhopper)
