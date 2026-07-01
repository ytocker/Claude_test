"""Shared base for piñata burro tail-design candidates.

All palette constants, helper functions, and the full body draw split into
three phases so each design_N.py can insert its tail between the legs and
the body slab (where the body naturally overlaps the tail's root).

Usage in design_N.py:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from _shared import (
        draw_rope, draw_legs, draw_body, draw_head,
        _make_prebuilt_skin, _phase, _TROT,
        BCX, BCY,
        CREAM, CREAM_D, PINK, ORANGE, TURQ, ORANGE_D, TURQ_D, PINK_D,
    )
    import pygame

    def _draw_tail(surf, cx, cy, bob, sway): ...   # YOUR tail here

    def build_fn(wing_angle_deg):
        surf = pygame.Surface((64, 84), pygame.SRCALPHA)
        ph = _phase(wing_angle_deg)
        bob = _TROT[ph]["bob"]
        sway = _TROT[ph]["sway"]
        cx, cy = BCX, BCY + bob
        draw_rope(surf, cx, cy)
        draw_legs(surf, cx, cy, sway)
        _draw_tail(surf, cx, cy, bob, sway)   # tail BEFORE body so body overlaps root
        draw_body(surf, cx, cy)
        draw_head(surf, cx, cy)
        return surf

    build = _make_prebuilt_skin(build_fn)
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + anchors ────────────────────────────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY       # body centre → (32, 44)


# ── crepe-fringe colourway ──────────────────────────────────────────────────
PINK       = (242, 73, 126)
PINK_D     = (196, 48, 96)
ORANGE     = (245, 139, 31)
ORANGE_D   = (200, 104, 18)
TURQ       = (35, 194, 168)
TURQ_D     = (22, 150, 130)
CREAM      = (255, 241, 214)
CREAM_D    = (228, 206, 168)
SNOUT      = (250, 232, 202)
EAR_IN     = (255, 158, 120)
EYE        = (40, 26, 30)
EYE_GLINT  = (255, 255, 255)
HOOF       = (120, 86, 70)

TASSELS = (ORANGE, PINK, ORANGE, PINK)


# ── trot animation table ────────────────────────────────────────────────────
def _phase(angle_deg):
    return int(round((50 - angle_deg) / 30.0)) % 4


_TROT = (
    {"bob":  2, "sway":  1.0},
    {"bob":  0, "sway":  0.0},
    {"bob": -2, "sway": -1.0},
    {"bob":  0, "sway":  0.0},
)


# ── drawing helpers ─────────────────────────────────────────────────────────
def _fringe_band(surf, cx, cy, rx, ry, color, shadow, n_scallop):
    _aaellipse(surf, color, (cx, cy), rx, ry)
    step = (2 * rx) / n_scallop
    r_sc = max(2, int(step * 0.6))
    fy = cy + ry - 1
    for i in range(n_scallop):
        sx = int(cx - rx + step * (i + 0.5))
        t = (sx - (cx - rx)) / (2 * rx)
        curve = math.sin(math.pi * t)
        pygame.draw.circle(surf, color, (sx, int(fy + curve * 1.5)), r_sc)
        pygame.draw.circle(surf, shadow,
                           (int(sx + step * 0.5), int(fy + curve * 1.0)),
                           max(1, r_sc - 1))


def _leg(surf, hip_x, hip_y, reach, swing, tassel_color, *, back=False, outer=False):
    s = (-swing if back else swing) * (4.0 if outer else 1.5)
    foot_x = int(hip_x + reach + s)
    foot_y = int(hip_y + 11 - abs(swing) * 1.5)
    knee_x = int(hip_x + reach * 0.5 + s * 0.5)
    knee_y = int(hip_y + 6)
    pygame.draw.line(surf, CREAM_D, (hip_x, hip_y), (knee_x, knee_y), 5)
    pygame.draw.line(surf, CREAM, (hip_x, hip_y), (knee_x, knee_y), 3)
    pygame.draw.line(surf, CREAM_D, (knee_x, knee_y), (foot_x, foot_y), 5)
    pygame.draw.line(surf, CREAM, (knee_x, knee_y), (foot_x, foot_y), 3)
    pygame.draw.circle(surf, HOOF, (foot_x, foot_y), 2)
    _aaellipse(surf, tassel_color, (foot_x, foot_y + 2), 4, 4)
    pygame.draw.circle(surf, CREAM, (foot_x, foot_y + 2), 1)
    for dx in (-2, 0, 2):
        pygame.draw.line(surf, tassel_color, (foot_x, foot_y + 2),
                         (foot_x + dx, foot_y + 7), 1)


def _ear(surf, base_x, base_y, lean, color):
    tip = (base_x + lean, base_y - 10)
    pts = [(base_x - 3, base_y), (base_x + 3, base_y), tip]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, EAR_IN, [(base_x - 1, base_y - 1),
                                       (base_x + 1, base_y - 1),
                                       (base_x + lean // 2, base_y - 6)])
    pygame.draw.polygon(surf, CREAM_D, pts, 1)


# ── modular draw phases ─────────────────────────────────────────────────────
def draw_rope(surf, cx, cy):
    pygame.draw.line(surf, CREAM_D, (cx, cy - 22), (cx, cy - 16), 2)


def draw_legs(surf, cx, cy, sway):
    hip_y = cy + 7
    _leg(surf, cx - 6,  hip_y, -3, sway, TASSELS[2], back=True)
    _leg(surf, cx - 10, hip_y, -7, sway, TASSELS[3], back=True, outer=True)
    _leg(surf, cx + 6,  hip_y,  3, sway, TASSELS[1])
    _leg(surf, cx + 10, hip_y,  7, sway, TASSELS[0], outer=True)


def draw_body(surf, cx, cy):
    _fringe_band(surf, cx - 1, cy - 4, 17, 7, PINK,   PINK_D,   8)
    _fringe_band(surf, cx - 1, cy + 1, 17, 6, ORANGE, ORANGE_D, 8)
    _fringe_band(surf, cx - 1, cy + 6, 16, 6, TURQ,   TURQ_D,   8)
    top_rect = pygame.Rect(cx - 1 - 17, cy - 4 - 7, 34, 14)
    pygame.draw.arc(surf, CREAM, top_rect, math.radians(15), math.radians(165), 2)
    bot_rect = pygame.Rect(cx - 1 - 16, cy + 6 - 6, 32, 12)
    pygame.draw.arc(surf, CREAM, bot_rect, math.radians(200), math.radians(340), 2)


def draw_head(surf, cx, cy):
    neck_x = cx + 13
    pygame.draw.polygon(surf, ORANGE, [
        (neck_x - 4, cy - 2), (neck_x + 5, cy - 9),
        (neck_x + 9, cy - 8), (neck_x + 4, cy + 3),
    ])
    pygame.draw.polygon(surf, ORANGE_D, [
        (neck_x - 4, cy - 2), (neck_x + 4, cy + 3), (neck_x - 1, cy + 2),
    ])
    mane_pts = [(neck_x - 5, cy + 1), (neck_x - 1, cy - 10),
                (neck_x + 3, cy - 12), (neck_x + 1, cy - 4), (neck_x - 2, cy + 2)]
    pygame.draw.polygon(surf, CREAM, mane_pts)
    for k in range(4):
        my = cy - 9 + k * 3
        pygame.draw.line(surf, CREAM_D, (neck_x - 4 + k, my),
                         (neck_x - 6 + k, my + 2), 1)
    hx, hy = neck_x + 8, cy - 9
    _aaellipse(surf, PINK,  (hx, hy), 6, 5)
    _aaellipse(surf, PINK_D, (hx, hy + 2), 6, 3)
    _aaellipse(surf, SNOUT, (hx + 6, hy + 1), 6, 4)
    _aaellipse(surf, SNOUT, (hx + 10, hy + 1), 3, 3)
    pygame.draw.circle(surf, CREAM_D, (hx + 12, hy + 1), 3, 1)
    pygame.draw.circle(surf, EYE, (hx + 11, hy + 2), 1)
    hrect = pygame.Rect(hx - 7, hy - 6, 22, 12)
    pygame.draw.arc(surf, CREAM, hrect, math.radians(0), math.radians(170), 2)
    _ear(surf, hx - 3, hy - 4, -4, CREAM)
    _ear(surf, hx + 1, hy - 5, -3, CREAM)
    pygame.draw.circle(surf, EYE, (hx + 1, hy - 1), 2)
    pygame.draw.circle(surf, EYE_GLINT, (hx, hy - 2), 1)


# ── cached skin getter factory ──────────────────────────────────────────────
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
