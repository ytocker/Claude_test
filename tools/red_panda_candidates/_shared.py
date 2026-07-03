"""Red panda back-redesign shared chassis.

Everything EXCEPT the tail/back geometry — body, head, ears, mask, eyes, paws.
Each candidate supplies `back(surf, f)` which draws the tail BEFORE the body
so the body ellipses naturally root and overlap the tail base.
"""
import math
import pygame
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W = SPRITE_W   # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY   # body centre (32, 44)
HCX, HCY = 44, 22 + DY   # head centre (44, 34)
CROWN_Y  = 12 + DY        # 24

FUR     = (193, 68, 14)
FUR_D   = (150, 48, 8)
FUR_H   = (224, 110, 44)
RING    = (122, 42, 12)
SEAM    = (74, 36, 16)
CREAM   = (255, 244, 230)
CREAM_W = (255, 252, 248)
CREAM_D = (224, 200, 176)
EYEDK   = (58, 26, 12)


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


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _eye(surf, cx, cy, r, *, iris=EYEDK, white=(255, 250, 244)):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3), max(1, r // 3))


def _flap(angle_deg):
    """0 = down-pose (tail counter-sweeps up), 1 = up-pose (paws tuck)."""
    return (angle_deg + 40) / 90.0


def _paw_pair(surf, by, f, col=SEAM):
    drop = int(6 - f * 5)
    for fx in (28, 38):
        pygame.draw.line(surf, col, (fx, by), (fx, by + drop), 3)
        pygame.draw.circle(surf, col, (fx, by + drop), 2)


def _ear(surf, cx, cy, r, sgn):
    pygame.draw.circle(surf, FUR_D, (cx, cy), r)
    pygame.draw.circle(surf, CREAM_D, (cx + sgn, cy + 1), max(1, r - 2))


def _mask(surf, hx, hy, w, h):
    _aaellipse(surf, CREAM_D, (hx - 5, hy + 4), w, h)
    _aaellipse(surf, CREAM_D, (hx + 6, hy + 4), w, h)
    _aaellipse(surf, CREAM,   (hx - 5, hy + 2), w, h)
    _aaellipse(surf, CREAM,   (hx + 6, hy + 2), w, h)
    _aaellipse(surf, CREAM,   (hx, hy + 3), 5, h)
    for dx in (-6, 7):
        pygame.draw.line(surf, FUR_D, (hx + dx, hy - 4),
                         (hx + dx + (1 if dx > 0 else -1), hy + 4), 2)


def _build(wing_angle_deg, *, back_fn):
    surf = _new()
    f = _flap(wing_angle_deg)

    # Tail / back — drawn first so the body overlaps the root naturally.
    back_fn(surf, f)

    # Body
    bcy = BCY + 2
    _aaellipse(surf, FUR_D, (BCX + 5, bcy + 1), 14, 13)
    _aaellipse(surf, FUR,   (BCX + 4, bcy), 13, 12)
    _aaellipse(surf, RING,  (BCX + 6, bcy + 5), 9, 8)
    _aaellipse(surf, CREAM, (BCX + 6, bcy + 5), 8, 7)
    _aaellipse(surf, FUR_H, (BCX + 1, bcy - 4), 5, 3)
    _paw_pair(surf, bcy + 11, f)

    # Head
    hcx, hcy = HCX, HCY - 1
    _aaellipse(surf, FUR_D, (hcx + 1, hcy + 1), 14, 13)
    _aaellipse(surf, FUR,   (hcx, hcy), 13, 12)
    _ear(surf, hcx - 8, CROWN_Y + 3, 6, -1)
    _ear(surf, hcx + 9, CROWN_Y + 3, 6, +1)
    _mask(surf, hcx, hcy, 7, 8)
    _eye(surf, hcx - 4, hcy, 3)
    _eye(surf, hcx + 6, hcy, 3)
    pygame.draw.circle(surf, EYEDK, (hcx + 1, hcy + 6), 2)
    pygame.draw.line(surf, EYEDK, (hcx + 1, hcy + 7), (hcx + 1, hcy + 9), 1)
    return surf


def make(back_fn):
    """Wrap a back_fn into a cached (frame_idx, tilt_deg) -> Surface getter."""
    return _make_prebuilt_skin(lambda a: _build(a, back_fn=back_fn))
