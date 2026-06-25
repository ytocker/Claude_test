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
_RH_BACK    = (38, 43, 64)          # navy head/back, lifted for night self-contrast
_RH_BACK_D  = (22, 25, 42)          # deepened back shadow for the egg rim
_RH_BACK_H  = (78, 86, 112)         # cool flipper leading-edge highlight
_RH_BELLY   = (247, 244, 236)       # #F7F4EC white belly / face
_RH_BELLY_D = (212, 210, 202)       # soft belly undershadow
_RH_CREST   = (255, 210, 30)        # #FFD21E yellow crest plume
_RH_CREST_D = (214, 162, 14)        # plume root / shading for depth
_RH_CREST_H = (255, 236, 130)       # bright plume highlight lick
_RH_BEAK    = (255, 138, 30)        # #FF8A1E orange beak / feet
_RH_BEAK_D  = (198, 96, 16)         # beak / foot shadow + outline
_RH_EYE     = (242, 64, 46)         # #F2402E fiery red iris (species tell)


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

    # ── HERO: spiky golden brow-plume fan exploding up-and-OUT past the crown ──
    # Four fat plumes with real dark gaps between them so the jagged silhouette
    # survives the 40px downscale instead of melting into a smooth yellow cap.
    # Outer tips splay laterally and cross the head outline from both top corners.
    # Outer-left raked flick — strayest, splayed wide past the head edge.
    _crest_plume(surf, HCX - 6, CROWN_Y + 5, HCX - 16, CROWN_Y - 9, 4)
    # Centre brace — tallest, near-vertical with a slight back rake.
    _crest_plume(surf, HCX - 1, CROWN_Y + 3, HCX - 2, CROWN_Y - 16, 5)
    # Mid-right.
    _crest_plume(surf, HCX + 4, CROWN_Y + 4, HCX + 8, CROWN_Y - 13, 4)
    # Outer-right forward flick — splayed wide over the brow.
    _crest_plume(surf, HCX + 8, CROWN_Y + 5, HCX + 18, CROWN_Y - 7, 4)

    # ── Red eyes — the rockhopper species tell. Bigger + brighter so they read
    # against the dark head at 40px, ringed by the pale face so they never sink
    # into the navy. Tightened spacing for a focused-forward glare. ──
    _aaellipse(surf, _RH_BELLY, (HCX, HCY), 7, 6)        # pale face bed under eyes
    _eye(surf, HCX - 1, HCY, 4, iris=_RH_EYE)
    _eye(surf, HCX + 4, HCY, 4, iris=_RH_EYE)

    # Fatter stubby orange beak (chunky rockhopper bill, not a thin sliver).
    beak = [(HCX + 2, HCY + 3), (HCX + 12, HCY + 7), (HCX + 2, HCY + 10)]
    pygame.draw.polygon(surf, _RH_BEAK, beak)
    # Filled lower-mandible wedge (value, not a 1px line) so the two-plate read
    # survives the 40px downscale.
    pygame.draw.polygon(surf, _RH_BEAK_D,
                        [(HCX + 2, HCY + 7), (HCX + 12, HCY + 7),
                         (HCX + 2, HCY + 10)])

    # Near flipper over the body.
    _rot_blit(surf, _pen_flipper(wing_angle_deg), (BCX - 6, BCY + 1))

    # Pink-orange webbed feet set WIDE apart — the hopping stance. Two toe-split
    # notches per foot so each reads as webbed toes, not an orange brick.
    for fx in (25, 39):
        foot = [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                (fx + 4, BCY + 20), (fx - 4, BCY + 20)]
        pygame.draw.polygon(surf, _RH_BEAK, foot)
        pygame.draw.polygon(surf, _RH_BEAK_D, foot, 1)
        for tx in (fx - 1, fx + 2):
            pygame.draw.line(surf, _RH_BEAK_D, (tx, BCY + 20), (tx, BCY + 18), 1)
    return surf


build = _make_prebuilt_skin(build_rockhopper)
