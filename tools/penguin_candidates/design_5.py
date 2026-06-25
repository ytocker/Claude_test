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
_AK_ICE_D   = (46, 72, 96)          # #2E4860 deep-ice back (darkened for the split)
_AK_ICE     = (132, 176, 204)       # frost-pale mid body
_AK_BELLY   = (244, 251, 255)       # #F4FBFF near-white belly / crystal cores
_AK_BELLY_D = (200, 218, 232)
_AK_BEAK    = (191, 224, 242)       # #BFE0F2 frost-blue beak (not orange!)
_AK_BEAK_H  = (223, 251, 255)       # #DFFBFF cold rim-glint
_AK_BEAK_D  = (66, 100, 130)        # darker frost outline so the beak reads as a shape
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


def _lerp(a, b, t):
    return (round(a[0] + (b[0] - a[0]) * t),
            round(a[1] + (b[1] - a[1]) * t),
            round(a[2] + (b[2] - a[2]) * t))


def _aurora_ribbon(surf, cx, base_y, frame):
    """A wreath of vertical light streaks arcing over the crown — color-lerped
    continuously green→cyan→violet across its width, each streak drawn 3× at
    growing size / dropping alpha to fake a soft glow falloff. A travelling
    brightness wave keyed to the frame makes it visibly shimmer across the flap.
    Roots tuck just above the crown so the ribbon wreathes the spikes instead of
    floating as a detached cap."""
    n = 6
    span = 22
    stops = [_AK_AURORA_G, _AK_AURORA_C, _AK_AURORA_V]
    for i in range(n):
        t = i / (n - 1)
        # 2-segment lerp green→cyan→violet.
        col = _lerp(stops[0], stops[1], t * 2) if t < 0.5 \
            else _lerp(stops[1], stops[2], (t - 0.5) * 2)
        sx = cx - span // 2 + round(t * span)
        # Arch: taller in the middle, shorter at the ends.
        arch = 1.0 - abs(t - 0.5) * 1.4
        # Travelling brightness wave along the ribbon, per frame.
        wave = 0.55 + 0.45 * (((i + frame) % n) / (n - 1))
        h = max(3, int((6 + arch * 9) * wave))
        top = base_y - h
        for grow, alpha in ((2, int(60 * wave)), (1, int(110 * wave)),
                            (0, int(200 * wave))):
            streak = pygame.Surface((3 + grow * 2, h + grow * 2),
                                    pygame.SRCALPHA)
            pygame.draw.ellipse(streak, (*col, alpha), streak.get_rect())
            surf.blit(streak, (sx - 1 - grow, top - grow))


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
    # Cold lit-rim on the upper-left back — ice catching the aurora, and keeps
    # the dark back reading against a dark night sky.
    pygame.draw.arc(surf, _AK_GLOW, (BCX - 16, BCY - 16, 22, 26), 1.3, 3.0, 1)

    # Far ice flipper.
    _rot_blit(surf, _aurora_flipper(wing_angle_deg * 0.5 - 16), (BCX + 11, BCY))

    # ── Aurora ribbon wreathing the crown (drawn before head/crown) ──
    # Flowing color-lerped vertical streaks with a per-frame shimmer wave; roots
    # tuck just above the crown so it reads as light around the tiara, not a cap.
    _aurora_ribbon(surf, HCX - 1, CROWN_Y - 4, frame)

    # Head — frost-pale slate dome.
    _aaellipse(surf, _AK_ICE_D, (HCX,     HCY + 2), 12, 12)
    _aaellipse(surf, _AK_ICE,   (HCX - 1, HCY + 1), 11, 11)
    # Near-white face oval (keeps the dark/light split on the head too).
    _aaellipse(surf, _AK_BELLY, (HCX, HCY + 3), 7, 7)

    # ── Glowing icy-cyan eyes — real bloom kept INSIDE the opaque head so
    # _add_outline never halos it, plus a hot white core so they emit at night. ──
    bloom = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(bloom, (*_AK_AURORA_C, 140), (7, 7), 7)
    pygame.draw.circle(bloom, (*_AK_AURORA_C, 90), (7, 7), 4)
    surf.blit(bloom, (HCX + 2 - 7, HCY + 1 - 7))
    _eye(surf, HCX - 1, HCY, 3, iris=_AK_EYE)
    _eye(surf, HCX + 4, HCY, 3, iris=_AK_EYE)
    # Hot white core inside each iris — the "luminous" tell.
    surf.set_at((HCX - 1, HCY), _AK_GLOW)
    surf.set_at((HCX + 4, HCY), _AK_GLOW)

    # Frost-blue beak — the only non-orange beak. Darker outline so the shape
    # separates from the pale head; a cold rim-glint on the TOP edge.
    beak_pts = [(HCX + 2, HCY + 3), (HCX + 12, HCY + 6), (HCX + 2, HCY + 8)]
    pygame.draw.polygon(surf, _AK_BEAK, beak_pts)
    pygame.draw.polygon(surf, _AK_BEAK_D, beak_pts, 1)
    pygame.draw.line(surf, _AK_BEAK_H, (HCX + 3, HCY + 4), (HCX + 11, HCY + 6), 1)

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
