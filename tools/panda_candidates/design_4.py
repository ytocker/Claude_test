"""Panda animal-skin candidate — DESIGN 4: KUNG-FU PANDA.

The action/hero panda. The shared giant-panda kit (white face disc, round
black ears, black eye patches, nose) armoured with martial-arts gear: a red
headband whose two tails stream back off the skull, black panda arms thrown
into an open fighting pose so the flap reads as throwing punches, cloth
wrist wraps, a wide black obi sash knotted across the white belly, and a gold
chest medallion breaking the belly.

Scratch builder only — mirrors game/animal_skins.py geometry + the
`_make_prebuilt_skin` factory so it lifts straight into production later. Not
registered in any BUILDERS map; rendered via tools/ninja_render.py.
"""
import math
import pygame

from game import parrot
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY   # body centre (32, 44)
HCX, HCY = 44, 22 + DY   # head centre (44, 34)
CROWN_Y = 12 + DY        # top of head (24)


# ── palette ──────────────────────────────────────────────────────────────────
BLACK     = (26, 26, 26)        # #1A1A1A panda black
BLACK_HI  = (54, 54, 60)        # soft black highlight on arm/ear mass
WHITE     = (245, 245, 245)     # #F5F5F5 panda white
WHITE_SH  = (216, 216, 220)     # white value step
RED       = (200, 16, 46)       # #C8102E kung-fu red
RED_SH    = (122, 12, 30)       # #7A0C1E red shadow
GOLD      = (227, 178, 60)      # #E3B23C gold emblem + wrap trim
GOLD_SH   = (176, 132, 36)
PINK      = (231, 169, 169)     # warm cheek/nose-tip accent


def _make_prebuilt_skin(build_fn):
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _rot_blit(surf, layer, anchor):
    surf.blit(layer, layer.get_rect(center=anchor).topleft)


def _flap(angle_deg):
    """0..1 'wing is up' factor; _WING_ANGLES runs 50→-40. Drives the
    punch reach + the trailing-tail flick so the pose feels alive."""
    return (angle_deg + 40) / 90.0


# ── black panda arm ending in a fist, with a red/gold wrist wrap ─────────────
def _panda_arm(angle_deg):
    """A stubby black panda forearm + rounded fist, banded by a cloth wrist
    wrap. Drawn level then rotated with the flap so the 4 poses read as
    punches thrown at different heights."""
    w = pygame.Surface((46, 46), pygame.SRCALPHA)
    # Forearm mass — wedge from shoulder root out to the fist.
    forearm = [(20, 18), (38, 16), (40, 28), (22, 30)]
    pygame.draw.polygon(w, BLACK, forearm)
    # Soft top highlight so the black limb keeps form against dark night sky.
    pygame.draw.line(w, BLACK_HI, (22, 19), (37, 18), 2)
    # Rounded fist / paw at the end (suggested knuckles).
    pygame.draw.circle(w, BLACK, (40, 23), 8)
    pygame.draw.circle(w, BLACK_HI, (38, 20), 3)
    for kx, ky in ((44, 20), (45, 24), (43, 27)):
        pygame.draw.circle(w, (16, 16, 16), (kx, ky), 1)
    # Cloth wrist wrap banding the forearm — two red turns + a gold trim line.
    pygame.draw.line(w, RED, (27, 17), (30, 30), 5)
    pygame.draw.line(w, RED_SH, (27, 17), (30, 30), 5)  # darker undertone
    pygame.draw.line(w, RED, (30, 16), (33, 29), 4)
    pygame.draw.line(w, GOLD, (31, 16), (34, 29), 1)
    return pygame.transform.rotate(w, angle_deg)


def _headband_tail(length, droop, flick):
    """One streaming headband ribbon — a tapering red cloth tail with a gold
    edge, that flicks with the flap so it reads dynamic. `flick` shifts the
    tip vertically; `droop` curves the midpoint."""
    w = pygame.Surface((length + 6, 28), pygame.SRCALPHA)
    base_y = 14
    tip_y = base_y + flick
    mid_y = base_y + droop
    pts = [
        (2, base_y - 4),
        (length // 2, mid_y - 5),
        (length + 3, tip_y - 1),
        (length + 3, tip_y + 3),
        (length // 2, mid_y + 4),
        (2, base_y + 4),
    ]
    pygame.draw.polygon(w, RED, pts)
    pygame.draw.polygon(w, RED_SH, pts, 1)
    # Gold trim along the lower edge.
    pygame.draw.line(w, GOLD, (3, base_y + 3), (length // 2, mid_y + 3), 1)
    pygame.draw.line(w, GOLD, (length // 2, mid_y + 3), (length + 2, tip_y + 2), 1)
    return w


def build(wing_angle_deg) -> pygame.Surface:
    """Draw one 64×84 SRCALPHA frame of the Kung-Fu Panda."""
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    f = _flap(wing_angle_deg)            # 0 (wing down) .. 1 (wing up)

    # ── trailing headband tails (drawn first so they stream BEHIND the head) ──
    # Two red ribbons flicking back-left off the skull, pushing past the
    # head silhouette for the dynamic flapping feel. Flick tracks the wing.
    flick = int(round((f - 0.5) * 10))   # -5..+5 px tail-tip swing
    tail_lo = _headband_tail(20, 3, 6 + flick)
    tail_hi = _headband_tail(17, -2, -2 + flick)
    # Anchor at the back-left of the head; ribbons run off-canvas-ward.
    _rot_blit(surf, pygame.transform.flip(tail_hi, True, False),
              (HCX - 16, HCY - 5))
    _rot_blit(surf, pygame.transform.flip(tail_lo, True, False),
              (HCX - 15, HCY + 2))

    # ── far arm (behind the body) thrown back, low-contrast ──
    far_ang = wing_angle_deg * 0.5 - 28
    _rot_blit(surf, _panda_arm(far_ang), (BCX + 9, BCY - 1))

    # ── body: chunky white torso framed by a black shoulder yoke ──
    # Black shoulder yoke under the sash (the real panda's dark shoulder band).
    _aaellipse(surf, BLACK, (BCX, BCY - 6), 19, 11)
    # White belly/torso disc over the collision centre.
    _aaellipse(surf, WHITE_SH, (BCX, BCY + 2), 18, 16)
    _aaellipse(surf, WHITE, (BCX - 1, BCY + 1), 17, 15)
    # Soft belly value step low-left for roundness.
    _aaellipse(surf, WHITE_SH, (BCX - 5, BCY + 7), 9, 7)

    # ── black leg stubs braced in a stance ──
    for sgn, lx in ((-1, BCX - 7), (1, BCX + 7)):
        ly = BCY + 13
        pygame.draw.line(surf, BLACK, (lx, ly), (lx + sgn * 2, ly + 7), 5)
        pygame.draw.circle(surf, BLACK, (lx + sgn * 2, ly + 7), 3)

    # ── wide black obi sash across the belly, knotted at the front ──
    sash_y = BCY + 5
    pygame.draw.polygon(surf, BLACK, [
        (BCX - 17, sash_y - 3), (BCX + 17, sash_y - 4),
        (BCX + 17, sash_y + 4), (BCX - 17, sash_y + 5),
    ])
    pygame.draw.line(surf, BLACK_HI, (BCX - 16, sash_y - 2),
                     (BCX + 16, sash_y - 3), 1)
    # Knot at the front-centre with a short hanging end.
    pygame.draw.circle(surf, BLACK, (BCX + 1, sash_y + 1), 4)
    pygame.draw.circle(surf, BLACK_HI, (BCX, sash_y - 1), 2)
    pygame.draw.polygon(surf, BLACK, [
        (BCX - 1, sash_y + 3), (BCX + 3, sash_y + 3),
        (BCX + 1, sash_y + 12),
    ])

    # ── gold chest medallion breaking the white belly above the sash ──
    mcx, mcy = BCX - 1, sash_y - 8
    pygame.draw.circle(surf, GOLD_SH, (mcx, mcy + 1), 5)
    pygame.draw.circle(surf, GOLD, (mcx, mcy), 5)
    pygame.draw.circle(surf, RED_SH, (mcx, mcy), 3)
    # Tiny yin-yang style dot.
    pygame.draw.circle(surf, WHITE, (mcx - 1, mcy - 1), 1)

    # ── ears: two round black ears up past the crown ──
    for dx in (-8, 9):
        _aaellipse(surf, BLACK, (HCX + dx, CROWN_Y + 1), 6, 6)
        _aaellipse(surf, BLACK_HI, (HCX + dx - 1, CROWN_Y - 1), 2, 2)

    # ── head: round white face disc ──
    _aaellipse(surf, WHITE_SH, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, WHITE, (HCX, HCY), 12, 11)

    # ── two black teardrop eye patches angled down-inward ──
    for sgn, ex in ((-1, HCX - 6), (1, HCX + 6)):
        patch = [
            (ex, HCY - 5), (ex + sgn * 5, HCY - 3),
            (ex + sgn * 4, HCY + 4), (ex - sgn * 1, HCY + 3),
        ]
        pygame.draw.polygon(surf, BLACK, patch)
        # White eye glint dot keeps the look fierce-but-friendly.
        pygame.draw.circle(surf, (250, 250, 245), (ex + sgn * 2, HCY), 2)
        pygame.draw.circle(surf, (18, 18, 22), (ex + sgn * 2, HCY), 1)

    # Cheek blush low on the face for charm.
    _aaellipse(surf, PINK, (HCX - 7, HCY + 5), 3, 2)
    _aaellipse(surf, PINK, (HCX + 7, HCY + 5), 3, 2)

    # Nose triangle + soft mouth line.
    pygame.draw.polygon(surf, BLACK, [
        (HCX - 2, HCY + 4), (HCX + 2, HCY + 4), (HCX, HCY + 7)])
    pygame.draw.line(surf, BLACK, (HCX, HCY + 7), (HCX, HCY + 9), 1)
    pygame.draw.line(surf, BLACK, (HCX - 3, HCY + 9), (HCX, HCY + 9), 1)
    pygame.draw.line(surf, BLACK, (HCX, HCY + 9), (HCX + 3, HCY + 9), 1)

    # ── red headband across the brow with a knot at the side ──
    band_y = HCY - 5
    pygame.draw.polygon(surf, RED, [
        (HCX - 12, band_y - 2), (HCX + 12, band_y - 3),
        (HCX + 12, band_y + 3), (HCX - 12, band_y + 2),
    ])
    pygame.draw.line(surf, RED_SH, (HCX - 12, band_y + 2),
                     (HCX + 12, band_y + 3), 1)
    pygame.draw.line(surf, GOLD, (HCX - 11, band_y - 1),
                     (HCX + 11, band_y - 2), 1)
    # Side knot where the trailing tails leave the head.
    pygame.draw.circle(surf, RED, (HCX - 12, band_y + 1), 3)
    pygame.draw.circle(surf, RED_SH, (HCX - 12, band_y + 1), 3, 1)

    # ── near arm (over the body) — the hero punch, reach tracks the flap ──
    near_ang = wing_angle_deg
    reach_x = int(round(-2 + f * 4))
    reach_y = int(round(2 - f * 6))
    _rot_blit(surf, _panda_arm(near_ang), (BCX - 6 + reach_x, BCY + reach_y))

    return surf


get_skin = _make_prebuilt_skin(build)
