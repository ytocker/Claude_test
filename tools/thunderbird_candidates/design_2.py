"""TOTEM THUNDERBIRD — Pacific Northwest coastal formline thunderbird skin.

Flat-graphic, carved-totem read: thick black formline outlines, red flat
chest, turquoise U-form accents, a bone-cream horn crown. No gradients, no
glow — value comes from flat colour contrast so it stays legible carved
down to 40px, the way real totem art works at a distance.

The horns are the cultural hero: two thick bone-tipped arcs sweeping up and
out well clear of the head, reading as a crown/V notch even at 40px. The head
carries the single red focal eye; the chest motif is demoted to turquoise so
it never competes for the eye's role.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 46
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
    """A coastal U-form feather-block: a black outer U, a flat inner fill,
    a crescent riding its tip — the alphabet of NW formline."""
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
    # Crescent tip bridges the two arms up top.
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


def _horn(surf, side):
    """One thick horn: a wide-based black arc sweeping up-and-out from the
    crown, capped by a bone-cream tip. Bone reads higher-contrast than
    turquoise against sky, so the crown notch survives the 40px squeeze."""
    # Root anchors close to the crown centre; the sweep carries the tip
    # ~9px above the head silhouette and well outboard for a clear V.
    root_x = HCX + side * 3
    root_y = HCY - 7
    tip_x = HCX + side * 15
    tip_y = CROWN_Y - 12
    # Thick tapered blade: wide base near the skull, narrowing to the tip.
    horn = [
        (root_x - side * 4, root_y + 1),         # inner base
        (root_x + side * 5, root_y - 2),         # outer base — wide foot
        (HCX + side * 12, CROWN_Y - 4),          # mid outer edge of the sweep
        (tip_x + side * 1, tip_y),               # tip apex
        (tip_x - side * 4, tip_y + 2),           # tip inner
        (HCX + side * 6, CROWN_Y - 3),           # mid inner edge
    ]
    pygame.draw.polygon(surf, BLACK, horn)
    # Bone-cream tip cap at full alpha — the crown's high-contrast punch.
    cap = [
        (tip_x + side * 1, tip_y),
        (tip_x - side * 4, tip_y + 2),
        (HCX + side * 8, CROWN_Y - 2),
        (HCX + side * 11, CROWN_Y - 5),
    ]
    pygame.draw.polygon(surf, BONE, cap)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)  # 0 wings-up … 1 wings-down power stroke

    # --- Wings/back: stacked U-form feather-blocks, one wing per side. The
    # stroke reads at the TOP of the stack (small vertical drop) rather than
    # as bottom-edge fringe, so the power stroke never muddies the silhouette.
    for side in (-1, 1):
        base_x = BCX + side * 15
        drop = int(strike * 3)
        for i in range(3):
            fy = CROWN_Y + 6 + i * 11 + (i * drop if i else 0)
            fw = 22 - i * 3
            fh = 11 - i * 1.2
            fx = base_x + side * (i * 2)
            _uform(surf, fx, fy, fw, fh, outer=BLACK, inner=RED, tip=TURQ)
        # A dry lightning-snake under each wing. On the power stroke it
        # shortens to 60% so the outer feathers never dissolve into fringe.
        snake_len = 20 * (0.6 + 0.4 * (1.0 - strike))
        _lightning(surf, base_x + side * 2, BCY + 4, side * 9, snake_len)

    # --- Body: heavy black formline shell over a flat red chest. The chest
    # is pulled down a touch so a black neck-strip can separate it cleanly
    # from the head above.
    _aaellipse(surf, BLACK, (BCX, BCY), 18, 20)
    _aaellipse(surf, RED, (BCX, BCY + 1), 13, 15)
    # Chest motif — turquoise-only U-form. Demoted so the head eye is the
    # single red focal point; no red seed, no bone eye competing up here.
    _uform(surf, BCX, BCY + 3, 15, 13, outer=BLACK, inner=TURQ, tip=TURQ)

    # --- Single talon per side: a short black formline claw that closes the
    # bottom silhouette without the old three-crescent noise.
    for side in (-1, 1):
        tx = BCX + side * 7
        ty = BCY + 18
        talon = [
            (tx - side * 3, ty - 3),
            (tx + side * 3, ty - 2),
            (tx + side * 2, ty + 4),
            (tx - side * 1, ty + 6),
            (tx - side * 4, ty + 2),
        ]
        pygame.draw.polygon(surf, BLACK, talon)

    # --- Neck: a black formline strip bridging head and body so at 40px the
    # two shapes read as distinct carved blocks rather than one red mass.
    neck = pygame.Rect(HCX - 9, HCY + 7, 18, 6)
    pygame.draw.rect(surf, BLACK, neck)

    # --- Head: black formline mass, red-filled face.
    _aaellipse(surf, BLACK, (HCX, HCY), 13, 12)
    _aaellipse(surf, RED, (HCX, HCY), 9, 9)

    # Two upward-and-outward sweeping horns — the thunderbird tell, drawn
    # before the eye so the eye can never be occluded by a stray horn edge.
    for side in (-1, 1):
        _horn(surf, side)

    # Beak — a black formline hook that juts a good 5px past the head
    # outline so the profile reads as a bird facing right.
    beak = [
        (HCX + 9, HCY - 2),
        (HCX + 22, HCY + 2),
        (HCX + 20, HCY + 5),
        (HCX + 11, HCY + 7),
        (HCX + 8, HCY + 3),
    ]
    pygame.draw.polygon(surf, BLACK, beak)
    pygame.draw.line(surf, RED, (HCX + 11, HCY + 2), (HCX + 18, HCY + 3), 1)

    # The single red focal eye — the one red dot the whole piece points to.
    _aaellipse(surf, BONE, (HCX + 2, HCY - 1), 6, 4)
    _aaellipse(surf, RED, (HCX + 2, HCY - 1), 5, 3)
    pygame.draw.circle(surf, BLACK, (HCX + 3, HCY - 1), 3)
    pygame.draw.circle(surf, BONE, (HCX + 4, HCY - 2), 1)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _cache[key]
