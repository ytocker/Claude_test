"""TOTEM THUNDERBIRD — Pacific Northwest coastal formline thunderbird skin.

Flat-graphic, carved-totem read: thick black formline outlines, red flat
chest, turquoise U-form accents, upward-curving horns. No gradients, no
glow — value comes from flat colour contrast so it stays legible carved
down to 40px, the way real totem art works at a distance.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y = 24

# Formline palette — carved-wood totem values, no gradient/glow.
BLACK = (14, 14, 18)
RED = (196, 48, 43)
TURQ = (31, 166, 160)
BONE = (242, 232, 213)


def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _uform(surf, cx, cy, w, h, *, outer, inner, tip):
    """A coastal U-form feather-block: a black outer U, a red inner fill,
    a turquoise crescent riding its tip — the alphabet of NW formline."""
    half = w / 2.0
    # Outer U — thick black shell (drawn as a filled trapezoid arm-pair).
    outer_pts = [
        (cx - half, cy - h * 0.5),
        (cx - half * 0.55, cy + h * 0.5),
        (cx + half * 0.55, cy + h * 0.5),
        (cx + half, cy - h * 0.5),
    ]
    pygame.draw.polygon(surf, outer, outer_pts)
    # Inner fill sits inside the U walls, leaving a black rim.
    r = 0.62
    inner_pts = [
        (cx - half * r, cy - h * 0.42),
        (cx - half * 0.42 * r, cy + h * 0.34),
        (cx + half * 0.42 * r, cy + h * 0.34),
        (cx + half * r, cy - h * 0.42),
    ]
    pygame.draw.polygon(surf, inner, inner_pts)
    # Turquoise tip crescent bridges the two arms up top.
    pygame.draw.line(surf, tip,
                     (cx - half * 0.78, cy - h * 0.5),
                     (cx + half * 0.78, cy - h * 0.5), max(2, int(h * 0.16)))


def _lightning(surf, x0, y0, dx, dy):
    """A dry zig-zag lightning-snake — a thin red carved line, no glow."""
    pts = [
        (x0, y0),
        (x0 + dx * 0.30, y0 + dy * 0.22),
        (x0 + dx * 0.12, y0 + dy * 0.5),
        (x0 + dx * 0.42, y0 + dy * 0.72),
        (x0 + dx * 0.25, y0 + dy * 1.0),
    ]
    pygame.draw.lines(surf, RED, False, pts, 2)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)  # 0 wings-up … 1 wings-down power stroke

    # --- Wings/back: stacked U-form feather-blocks, one wing per side. The
    # strike phase drops the outer feathers so the stroke reads as motion.
    for side in (-1, 1):
        base_x = BCX + side * 15
        drop = int(strike * 8)
        for i in range(3):
            fy = CROWN_Y + 6 + i * 11 + (i * drop if i else 0)
            fw = 22 - i * 3
            fh = 11 - i * 1.2
            fx = base_x + side * (i * 2)
            _uform(surf, fx, fy, fw, fh, outer=BLACK, inner=RED, tip=TURQ)
        # A dry lightning-snake under each wing.
        _lightning(surf, base_x + side * 2, BCY + 6, side * 9, 20)

    # --- Body: heavy black formline shell over a flat red chest.
    _aaellipse(surf, BLACK, (BCX, BCY), 18, 21)
    _aaellipse(surf, RED, (BCX, BCY), 13, 16)
    # Single turquoise U-form "heart" motif dead-centre of the chest.
    _uform(surf, BCX, BCY + 2, 15, 14, outer=BLACK, inner=TURQ, tip=BONE)
    # Inner ovoid eye of the heart-form — the formline "seed".
    _aaellipse(surf, BLACK, (BCX, BCY - 2), 4, 5)
    _aaellipse(surf, BONE, (BCX, BCY - 3), 2, 3)

    # --- Talons: black ovoid feet with red claw crescents.
    for side in (-1, 1):
        tx = BCX + side * 8
        ty = BCY + 20
        _aaellipse(surf, BLACK, (tx, ty), 5, 4)
        for k in (-1, 0, 1):
            cx = tx + k * 3
            pygame.draw.arc(surf, RED,
                            pygame.Rect(cx - 3, ty, 6, 8),
                            3.6, 5.8, 2)

    # --- Head: black formline mass, red-filled face.
    _aaellipse(surf, BLACK, (HCX, HCY), 13, 12)
    _aaellipse(surf, RED, (HCX, HCY), 9, 9)

    # Two upward-curving horns — the thunderbird tell. Thick black polygon
    # arcs sweeping up-and-out from the crown, tipped turquoise.
    for side in (-1, 1):
        hx = HCX + side * 4
        horn = [
            (hx, HCY - 6),
            (hx + side * 3, CROWN_Y - 2),
            (hx + side * 9, CROWN_Y - 9),
            (hx + side * 12, CROWN_Y - 8),
            (hx + side * 8, CROWN_Y - 1),
            (hx + side * 5, HCY - 8),
        ]
        pygame.draw.polygon(surf, BLACK, horn)
        pygame.draw.circle(surf, TURQ, (hx + side * 11, CROWN_Y - 8), 2)

    # Large red ovoid eye with black pupil (formline eye).
    _aaellipse(surf, BONE, (HCX + 3, HCY - 1), 6, 4)
    _aaellipse(surf, RED, (HCX + 3, HCY - 1), 5, 3)
    pygame.draw.circle(surf, BLACK, (HCX + 4, HCY - 1), 3)
    pygame.draw.circle(surf, BONE, (HCX + 5, HCY - 2), 1)

    # Beak — a short black formline hook, red inner mouth-line.
    beak = [
        (HCX + 10, HCY - 1),
        (HCX + 17, HCY + 2),
        (HCX + 12, HCY + 6),
        (HCX + 8, HCY + 4),
    ]
    pygame.draw.polygon(surf, BLACK, beak)
    pygame.draw.line(surf, RED, (HCX + 10, HCY + 2), (HCX + 15, HCY + 2), 1)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _cache[key]
