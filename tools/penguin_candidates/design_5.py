"""AURORA KING penguin — design_5 of the penguin store-skin redesign.

The legendary showpiece: the only luminous penguin. A frost-blue recolored
body (deep-ice-blue back vs near-white belly — the split is preserved), a
crown of faceted ice-crystal spikes rising past CROWN_Y, and a soft aurora
ribbon (green→cyan→violet) arcing above the head with a per-frame shimmer.
Glowing icy-cyan eyes, a frost-blue beak (the only non-orange beak in the
set), frost-tipped flippers, pale-blue feet.

Glow is baked as defined translucent shapes — not free-floating blobs — so
``parrot._add_outline`` traces clean silhouette edges rather than dark halos.
Eye bloom is kept inside the opaque head ellipse for the same reason.

Built on the same chassis as ``animal_skins.build_penguin``. Scratch-only —
NOT registered in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye, _flap,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── AURORA KING palette ───────────────────────────────────────────────────────
_AK_ICE_D   = (62, 91, 114)         # #3E5B72 deep-ice back / shadow
_AK_ICE     = (144, 186, 210)       # frost-pale mid body
_AK_BELLY   = (242, 250, 255)       # #F2FAFF near-white belly / crystal cores
_AK_BELLY_D = (200, 218, 232)
_AK_BEAK    = (191, 224, 242)       # #BFE0F2 frost-blue beak (not orange!)
_AK_BEAK_H  = (223, 251, 255)       # #DFFBFF cold rim-glint
_AK_BEAK_D  = (100, 140, 170)
_AK_EYE     = (57, 182, 255)        # #39B6FF icy-cyan glowing iris
_AK_AURORA_G = (79, 227, 160)       # #4FE3A0 aurora green
_AK_AURORA_C = (57, 182, 255)       # #39B6FF aurora cyan
_AK_AURORA_V = (160, 107, 255)      # #A06BFF aurora violet
_AK_GLOW    = (223, 251, 255)       # #DFFBFF glow core / crystal highlight
_AK_FOOT    = (120, 173, 204)       # pale-blue webbed feet


def _aurora_flipper(angle_deg):
    """Ice-pale flipper with frost-crystal tip highlights."""
    w = pygame.Surface((34, 44), pygame.SRCALPHA)
    pts = [(18, 10), (26, 16), (22, 34), (14, 30)]
    pygame.draw.polygon(w, _AK_ICE_D, pts)
    pygame.draw.polygon(w, _AK_ICE, [(18, 11), (24, 17), (20, 30), (15, 27)])
    pygame.draw.line(w, _AK_BELLY, (18, 13), (22, 18), 1)
    # Frost-crystal tip glints.
    pygame.draw.line(w, _AK_GLOW, (16, 31), (20, 34), 2)
    pygame.draw.line(w, _AK_GLOW, (21, 31), (23, 33), 1)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def _ice_spike(surf, base_x, base_y, tip_x, tip_y, w_half):
    """One faceted ice-crystal spike: dark ice outer edge, bright frost core."""
    pygame.draw.polygon(surf, _AK_ICE_D, [
        (base_x - w_half, base_y),
        (tip_x, tip_y),
        (base_x + w_half, base_y),
    ])
    pygame.draw.polygon(surf, _AK_ICE, [
        (base_x - w_half + 1, base_y),
        (tip_x, tip_y + 1),
        (base_x + w_half - 1, base_y),
    ])
    # Bright inner glint line — the "faceted" tell.
    pygame.draw.line(surf, _AK_GLOW, (base_x, base_y - 1), (tip_x, tip_y + 2), 1)


def build_aurora(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    frame = int(round(wing_angle_deg / 20)) % 4  # 0-3 shimmer cycle

    # Stubby tail — ice-dark.
    pygame.draw.polygon(surf, _AK_ICE_D,
                        [(13, BCY + 8), (6, BCY + 14), (18, BCY + 14)])

    # Frost-blue egg body — deep-ice back / near-white belly split preserved.
    _aaellipse(surf, _AK_ICE_D, (BCX + 1, BCY + 1), 17, 18)
    _aaellipse(surf, _AK_ICE,   (BCX,     BCY),      16, 17)
    # Near-white belly oval.
    _aaellipse(surf, _AK_BELLY,   (BCX + 1, BCY + 3), 11, 14)
    _aaellipse(surf, _AK_BELLY_D, (BCX + 1, BCY + 9),  9,  6)
    # Crystalline belly sheen — a few thin highlight arcs.
    pygame.draw.line(surf, _AK_GLOW, (BCX - 5, BCY + 2), (BCX + 4, BCY - 1), 1)
    pygame.draw.line(surf, _AK_GLOW, (BCX - 4, BCY + 5), (BCX + 3, BCY + 2), 1)

    # Far ice flipper.
    _rot_blit(surf, _aurora_flipper(wing_angle_deg * 0.5 - 16), (BCX + 11, BCY))

    # ── Aurora ribbon above the head (drawn early, behind head/crown) ──
    # Three overlapping translucent ellipses in green/cyan/violet arcing over the
    # head. Kept as defined, relatively tight shapes so _add_outline traces clean
    # edges (not a diffuse blob that would get a dark ring halo).
    # Per-frame shimmer: the arc shifts very slightly left/right with frame.
    shimmer = (frame % 2) * 2 - 1   # alternates -1 / +1
    arc_y = CROWN_Y - 14
    arc_cx = HCX - 2 + shimmer

    aurora_colors_alpha = [
        (_AK_AURORA_G, 110),
        (_AK_AURORA_C, 120),
        (_AK_AURORA_V, 100),
    ]
    for i, (col, alpha) in enumerate(aurora_colors_alpha):
        ax = arc_cx + (i - 1) * 5
        ay = arc_y + (i % 2) * 2
        glow_surf = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (*col, alpha), glow_surf.get_rect())
        surf.blit(glow_surf, (ax - 10, ay - 5))

    # Head — frost-pale slate dome.
    _aaellipse(surf, _AK_ICE_D, (HCX,     HCY + 2), 12, 12)
    _aaellipse(surf, _AK_ICE,   (HCX - 1, HCY + 1), 11, 11)
    # Near-white face oval (keeps the dark/light split on the head too).
    _aaellipse(surf, _AK_BELLY, (HCX, HCY + 3), 7, 7)

    # ── Glowing icy-cyan eyes with bloom INSIDE the opaque head ──
    # Soft bloom circle drawn first (inside head boundary), then the iris/pupil
    # on top — bloom stays within the opaque head so _add_outline never halos it.
    pygame.draw.circle(surf, (*_AK_AURORA_C, 80),
                       (HCX + 2, HCY + 1), 5)          # inner bloom
    _eye(surf, HCX - 2, HCY, 3, iris=_AK_EYE)
    _eye(surf, HCX + 5, HCY, 3, iris=_AK_EYE)

    # Frost-blue beak — the only non-orange beak, sells "frozen royalty".
    beak_pts = [(HCX + 2, HCY + 3), (HCX + 12, HCY + 6), (HCX + 2, HCY + 8)]
    pygame.draw.polygon(surf, _AK_BEAK, beak_pts)
    pygame.draw.polygon(surf, _AK_BEAK_D, beak_pts, 1)
    # Cold rim-glint on the upper mandible.
    pygame.draw.line(surf, _AK_BEAK_H,
                     (HCX + 3, HCY + 4), (HCX + 10, HCY + 6), 1)

    # Near ice flipper.
    _rot_blit(surf, _aurora_flipper(wing_angle_deg), (BCX - 6, BCY + 1))

    # ── HERO: Faceted ice-crystal crown above the head ──
    # 5 spikes in a fan rising past CROWN_Y — tallest centre, shorter flanks.
    # Drawn after the head/eyes so they sit clearly on top as a tiara.
    spikes = [
        (HCX - 8, CROWN_Y + 2, HCX - 11, CROWN_Y - 7,  2),
        (HCX - 4, CROWN_Y + 1, HCX - 6,  CROWN_Y - 11, 3),
        (HCX,     CROWN_Y,     HCX - 1,  CROWN_Y - 14, 3),   # tallest
        (HCX + 4, CROWN_Y + 1, HCX + 7,  CROWN_Y - 11, 3),
        (HCX + 8, CROWN_Y + 2, HCX + 12, CROWN_Y - 7,  2),
    ]
    for bx, by, tx, ty, hw in spikes:
        _ice_spike(surf, bx, by, tx, ty, hw)

    # Pale-blue webbed feet with frost-white toe glints.
    for fx in (27, 37):
        pygame.draw.polygon(surf, _AK_FOOT,
                            [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 4, BCY + 20), (fx - 4, BCY + 20)])
        pygame.draw.polygon(surf, _AK_ICE_D,
                            [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 4, BCY + 20), (fx - 4, BCY + 20)], 1)
        # Frost-white toe glints.
        pygame.draw.line(surf, _AK_GLOW, (fx - 2, BCY + 17), (fx - 1, BCY + 19), 1)

    return surf


build = _make_prebuilt_skin(build_aurora)
