"""Reusable mantis-shrimp chassis primitives for the FULL redesign wave.

These give every candidate the same skeleton — the strike gag (clubs cock back on
the down-pose, PUNCH forward on the up-pose), arm + fist drawing, parameterized
jewel/orb eyes, glow caches, the cached 4-frame getter — while each design_N.py
composes its own body/palette/proportions on top. Anchors match production:
body ≈(32,44), head ≈(44,34), crown ≈y=24, bird faces RIGHT.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # body centre → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre → (44, 34)
CROWN_Y  = 12 + DY              # crown → 24


def make_skin(build_fn):
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


def new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def aaellipse(surf, col, center, rx, ry):
    _aaellipse(surf, col, center, rx, ry)


def strike(angle_deg):
    """0 = clubs cocked back (down-pose) → 1 = punched forward (up-pose)."""
    return 1.0 - (angle_deg + 40) / 90.0


def lerp_pt(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def shade(col, f):
    return tuple(max(0, min(255, int(c * f))) for c in col)


def glow_dot(surf, cx, cy, r, col):
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for rr, a in ((r * 2, 40), (int(r * 1.4), 70), (r, 120)):
        pygame.draw.circle(g, (*col, a), (r * 2, r * 2), rr)
    surf.blit(g, (int(cx - r * 2), int(cy - r * 2)),
              special_flags=pygame.BLEND_RGBA_ADD)


def recoil(s):
    """Body recoils on the punch — returns (rcx, rcy) offsets."""
    return -int(s * 2), int(s * 1)


def club_targets(bcx, bcy, hcx, hcy, s):
    """Strike-interpolated world points for both raptorial arms. Mirrors the
    production geometry: the rear fist stays a separate low mass; the lead fist
    drives UP+FORWARD over the snout on the punch."""
    sh = (bcx + 7, bcy + 3)
    rear_shoulder = lerp_pt((bcx + 2, bcy + 11), (bcx + 4, bcy + 6), s)
    rear_elbow = lerp_pt((bcx + 3, bcy + 16), (bcx + 13, bcy + 8), s)
    rear_fist = lerp_pt((bcx + 4, bcy + 20), (bcx + 21, bcy + 10), s)
    near_elbow = lerp_pt((bcx + 13, bcy + 6), (hcx + 5, hcy + 0), s)
    near_fist = lerp_pt((bcx + 19, bcy + 11), (hcx + 15, hcy - 10), s)
    return sh, rear_shoulder, rear_elbow, rear_fist, near_elbow, near_fist


def arm(surf, a, b, rim, arm_col, w=3):
    pygame.draw.line(surf, rim, a, b, w + 2)
    pygame.draw.line(surf, arm_col, a, b, w)


def round_club(surf, fist, r, *, rim, col, hi, spark=None):
    """A rounded boxing-glove fist with a dark heel rim + a top-left highlight."""
    pygame.draw.circle(surf, rim, fist, r + 1)
    pygame.draw.circle(surf, col, fist, r)
    pygame.draw.circle(surf, hi, (fist[0] - 1, fist[1] - 1), max(1, r - 2))
    if spark:
        pygame.draw.circle(surf, spark, (fist[0] + 1, fist[1] - 1), max(1, r // 3))


def hammer_club(surf, fist, shoulder, r, *, rim, col, hi, face):
    """A squared anvil/hammer head whose bright striking FACE points along the
    throw direction (shoulder→fist)."""
    dx, dy = fist[0] - shoulder[0], fist[1] - shoulder[1]
    mag = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / mag, dy / mag
    px, py = -uy, ux
    pts = [
        (fist[0] - ux * r + px * r, fist[1] - uy * r + py * r),
        (fist[0] + ux * r + px * r, fist[1] + uy * r + py * r),
        (fist[0] + ux * r - px * r, fist[1] + uy * r - py * r),
        (fist[0] - ux * r - px * r, fist[1] - uy * r - py * r),
    ]
    pygame.draw.polygon(surf, rim, pts)
    inner = [(p[0] - ux, p[1] - uy) for p in pts]
    pygame.draw.polygon(surf, col, inner)
    pygame.draw.circle(surf, hi, (int(fist[0] - ux * 2), int(fist[1] - uy * 2)),
                       max(1, r // 2))
    # white-hot striking face on the leading edge
    fx, fy = int(fist[0] + ux * (r - 1)), int(fist[1] + uy * (r - 1))
    pygame.draw.line(surf, face,
                     (int(fx + px * r), int(fy + py * r)),
                     (int(fx - px * r), int(fy - py * r)), 2)


def orb_eye(surf, cx, cy, r, *, core, rim, mid=None, band=False, hi=True,
            glow=None):
    """A compound-eye orb on a stalk tip. `mid` paints the lower hemisphere a
    second hue (the split peacock eye); `band` draws the white ommatidia line;
    `glow` (a colour) adds a night bloom."""
    if glow:
        glow_dot(surf, cx, cy, max(2, r - 1), glow)
    pygame.draw.circle(surf, rim, (cx, cy), r + 1, 1)
    pygame.draw.circle(surf, core, (cx, cy), r)
    if mid is not None:
        pygame.draw.circle(surf, mid, (cx, cy), r,
                           draw_top_right=False, draw_bottom_right=True,
                           draw_top_left=False, draw_bottom_left=True)
    if band:
        pygame.draw.line(surf, (250, 252, 250), (cx - r, cy), (cx + r, cy), 1)
    if hi:
        pygame.draw.circle(surf, (255, 255, 255),
                           (cx - max(1, r // 3), cy - max(1, r // 3)),
                           max(1, r // 3))


def stalk(surf, base, tip, *, rim, col, w=3):
    pygame.draw.line(surf, rim, base, tip, w + 2)
    pygame.draw.line(surf, col, base, tip, w)


def tail_fan(surf, cx, cy, *, body, body_d, edge, rib=None, count=3, span=18):
    """Segmented abdomen sweeping back to a 3-blade tail-fan with coloured edges."""
    step = span / count
    for i in range(count):
        x = cx - int(i * step)
        rx, ry = 8 - i, 11 - i
        pygame.draw.ellipse(surf, body_d, (x - rx, cy - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, body, (x - rx, cy - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, edge, (x - rx, cy - ry, rx * 2, ry * 2), 1)
    tx = cx - int(span)
    for dy, dx in ((-7, -6), (0, -9), (7, -6)):
        pygame.draw.polygon(surf, edge, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)])
        if rib:
            pygame.draw.line(surf, rib, (tx, cy), (tx + dx, cy + dy), 1)
