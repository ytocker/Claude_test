"""Shared geometry + helpers for MONARCH wing-variant builders (design_4b..4f).

All variants share the classic playing-card wing silhouette, body, head, and
animation rig from design_4 MONARCH.  Each variant imports this module and only
overrides `_draw_wing` with its own palette/pattern.
"""
import pygame
from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y   = 24

_INK   = (26, 19, 14)
_FLAKE = (245, 241, 230)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    return (a + 40) / 90.0


# Shared playing-card wing silhouette (identical to design_4).
_WING_R = [
    (34, 26),   # inner top
    (45, 13),   # forewing leading rise
    (56, 10),   # forewing apex
    (63, 20),   # forewing outer shoulder
    (62, 32),   # forewing trailing outer
    (60, 40),   # shallow notch fore/hind
    (57, 48),   # hindwing outer
    (50, 54),   # hindwing rounded lobe
    (42, 56),   # hindwing bottom
    (34, 49),   # inner bottom
]


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def _inset(pts, frac):
    cx, cy = _centroid(pts)
    return [(x + (cx - x) * frac, y + (cy - y) * frac) for x, y in pts]


def _transform(pts, side, spread, nx):
    out = []
    for x, y in pts:
        dx = (x - BCX) * side
        out.append((BCX + dx * nx, y - spread))
    return out


def _wing_mask(pts):
    m = _new()
    pygame.draw.polygon(m, (255, 255, 255, 255), pts)
    return m


def draw_body(surf, lift=0, ink=_INK, flake=_FLAKE):
    L = lift
    pygame.draw.polygon(surf, ink, [
        (BCX - 3, BCY - L), (BCX + 3, BCY - L),
        (BCX + 1, BCY + 5 - L),
        (BCX - 3, BCY + 9 - L),
        (BCX - 5, BCY + 4 - L),
    ])
    for (fx, fy) in ((BCX - 1, BCY + 2), (BCX - 2, BCY + 6)):
        pygame.draw.circle(surf, flake, (fx, fy - L), 1)
    _aaellipse(surf, ink, (BCX, BCY - L), 5, 7)
    pygame.draw.circle(surf, flake, (BCX - 1, BCY - 2 - L), 1)


def draw_head(surf, lift=0, ink=_INK, flake=_FLAKE,
              ring_col=(250, 132, 30), club_col=(255, 179, 71)):
    L = lift
    for (tx, ty) in ((HCX - 6, CROWN_Y - L), (HCX + 4, CROWN_Y - L)):
        sx = HCX + (1 if tx > HCX else -1)
        sy = HCY - 4 - L
        mx = (sx + tx) / 2 + (2 if tx > HCX else -2)
        my = (sy + ty) / 2
        pygame.draw.lines(surf, ink, False, [(sx, sy), (mx, my), (tx, ty)], 1)
        pygame.draw.circle(surf, ink, (tx, ty), 2)
        pygame.draw.circle(surf, club_col, (tx, ty - 1), 1)
    _aaellipse(surf, ring_col, (HCX, HCY - L), 6, 6)
    _aaellipse(surf, ink, (HCX, HCY - L), 5, 5)
    pygame.draw.circle(surf, flake, (HCX - 2, HCY - 1 - L), 1)
    pygame.draw.circle(surf, flake, (HCX + 2, HCY - L), 1)


def make_build(draw_wing_fn, ink=_INK, flake=_FLAKE,
               ring_col=(250, 132, 30), club_col=(255, 179, 71)):
    """Return a `build(frame_idx, tilt_deg)` function using the given wing draw fn."""
    state = {"frames": None, "rot": {}}

    def _build_frame(wing_angle_deg):
        surf = _new()
        f = _flap(wing_angle_deg)
        spread = int(f * 9)
        nx = 1.0 - 0.42 * f
        draw_wing_fn(surf, -1, spread, nx)
        draw_body(surf, spread, ink, flake)
        draw_wing_fn(surf, +1, spread, nx)
        draw_head(surf, spread, ink, flake, ring_col, club_col)
        return surf

    def _fn(frame_idx: int, tilt_deg: float) -> pygame.Surface:
        if state["frames"] is None:
            state["frames"] = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
        frame_idx %= 4
        key = (frame_idx, int(round(tilt_deg / 3)) * 3)
        if key not in state["rot"]:
            state["rot"][key] = pygame.transform.rotozoom(
                state["frames"][frame_idx], key[1], 1.0)
        return state["rot"][key]

    return _fn
