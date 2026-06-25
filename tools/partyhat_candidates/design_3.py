"""PARTY HAT redesign — DESIGN 3: JESTER CAP (SCRATCH ONLY).

A floppy two-point harlequin hood draped over the crown: alternating
violet/gold diamond blocks, one droopy point flopping forward over the beak,
one flopping back, each tipped with a dangling jingle bell. Asymmetric and
unmistakably not-a-cone even at 40px — the silhouette is two drooping horns,
not a single peak.
"""
import math

import pygame

from ._template import make_build, make_icon

_VIOLET = (123, 47, 247)
_VIOLET_LO = (88, 32, 178)
_GOLD = (255, 210, 63)
_GOLD_LO = (210, 168, 40)
_TEAL = (25, 195, 201)
_SHADOW = (42, 36, 64)
_BELL_HI = (255, 243, 196)
_BELL = (201, 162, 39)
_BELL_LO = (150, 118, 24)


def _bezier(p0, p1, p2, n=14):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def _droop_point(surf, root, ctrl, tip, half_w, col, col_lo, head_w):
    """A tapering floppy horn from a fat root to a thin drooping tip, drawn as
    two bezier edges so the lobe curves like soft fabric rather than a rigid
    spike. Returns the tip point for hanging the bell."""
    # Spine controls the curl; the two edges run parallel to it, pinching to a
    # point at the tip so the lobe reads as cloth, not a triangle.
    spine = _bezier(root, ctrl, tip, 16)
    left, right = [], []
    n = len(spine)
    for i, (x, y) in enumerate(spine):
        t = i / (n - 1)
        # Width fattest near the root, tapering smoothly to zero at the tip.
        w = half_w * (1.0 - t) ** 0.85
        if i < n - 1:
            nx, ny = spine[i + 1]
        else:
            nx, ny = x, y
        dx, dy = nx - x, ny - y
        d = math.hypot(dx, dy) or 1.0
        # Perpendicular offset gives the lobe its thickness.
        px, py = -dy / d, dx / d
        left.append((x + px * w, y + py * w))
        right.append((x - px * w, y - py * w))
    poly = left + right[::-1]
    pygame.draw.polygon(surf, col, poly)
    # A darker underside seam along the lower edge fakes the fold of fabric.
    pygame.draw.polygon(surf, col_lo, [spine[0]] + right + [spine[-1]])
    return tip


def _bell(surf, x, y, r, head_w):
    """A round jingle bell: gold body, bright top catch-light, dark slit, and a
    tiny clapper hole. Gated detail so it stays a clean dot when shrunk."""
    x, y = int(x), int(y)
    r = max(2, int(r))
    # Tiny stem linking the lobe tip to the bell.
    pygame.draw.line(surf, _BELL_LO, (x, y - r - 1), (x, y - r + 1),
                     max(1, r // 3))
    pygame.draw.circle(surf, _BELL_LO, (x, y), r)
    pygame.draw.circle(surf, _BELL, (x, y), max(1, r - 1))
    if head_w >= 20:
        # Equator slit + bottom mouth read as a real jingle bell.
        pygame.draw.line(surf, _BELL_LO, (x - r + 1, y + r // 3),
                         (x + r - 1, y + r // 3), max(1, r // 3))
        pygame.draw.circle(surf, _BELL_LO, (x, y + r - 1), max(1, r // 3))
    pygame.draw.circle(surf, _BELL_HI, (x - r // 3, y - r // 3),
                       max(1, r // 3))


def _draw_diamonds(surf, hood_poly, cx, crown_y, r, head_w):
    """Harlequin diamond checker clipped to the hood cap. A rotated lattice of
    violet/gold rhombi sells the jester pattern; gated off when too small so the
    cap stays clean two-tone instead of muddy speckle."""
    bb = pygame.Rect(0, 0, 0, 0)
    xs = [p[0] for p in hood_poly]
    ys = [p[1] for p in hood_poly]
    bb = pygame.Rect(int(min(xs)) - 2, int(min(ys)) - 2,
                     int(max(xs) - min(xs)) + 4, int(max(ys) - min(ys)) + 4)
    if bb.width <= 0 or bb.height <= 0:
        return
    layer = pygame.Surface(bb.size, pygame.SRCALPHA)
    ox, oy = bb.left, bb.top

    # Harlequin checker: rhombi packed corner-to-corner on a diagonal lattice,
    # coloured by (row+col) parity so every diamond is ringed by its opposite —
    # a true argyle, not bands. Cells are squat (wider than tall) and small
    # relative to the cap so several rows survive the dome's curvature and the
    # pattern reads as diamonds rather than stripes.
    dx_ = max(5, r * 0.42)   # rhombus half-width
    dy_ = max(4, r * 0.30)   # rhombus half-height
    j0 = int(bb.width / dx_) + 4
    k0 = int(bb.height / dy_) + 4
    for k in range(-2, k0):
        for j in range(-2, j0):
            # Brick offset: each row shifts a half-cell so corners kiss.
            ccx = bb.left + (j + (0.5 if k % 2 else 0)) * dx_
            ccy = bb.top + k * dy_
            rhomb = [
                (ccx - ox, ccy - dy_ - oy),
                (ccx + dx_ - ox, ccy - oy),
                (ccx - ox, ccy + dy_ - oy),
                (ccx - dx_ - ox, ccy - oy),
            ]
            col = _VIOLET if (j + k) % 2 == 0 else _GOLD
            pygame.draw.polygon(layer, col + (255,), rhomb)

    mask = pygame.Surface(bb.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - ox, p[1] - oy) for p in hood_poly])
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(layer, (ox, oy))


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile JESTER CAP sized for a head of width head_w, centred
    at cx, base line (crown top) at base_y."""
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1

    # The hood caps the crown: a low dome hugging the skull, with its band line
    # a touch below base_y so the cloth wraps onto the round head.
    crown_y = base_y - r * 0.24
    dome_top = crown_y - r * 0.62
    left_x = cx - r * 0.92
    right_x = cx + r * 0.92

    # Soft dome of the cap, drawn as an arc-topped polygon so the cloth bulges.
    dome = []
    steps = 16
    for i in range(steps + 1):
        t = i / steps
        ang = math.pi * t  # left → right over the top
        x = cx - math.cos(ang) * (r * 0.92)
        y = crown_y + r * 0.34 - math.sin(ang) * (r * 0.96)
        dome.append((x, y))
    cap_poly = dome + [(right_x, crown_y + r * 0.34), (left_x, crown_y + r * 0.34)]
    pygame.draw.polygon(surf, _VIOLET, cap_poly)

    # Two drooping horns sprout from the dome's shoulders and flop OUT to the
    # sides (not over the beak): each rises off the shoulder then curls back down
    # so the tip droops level with the band. Roots overlap the dome so they read
    # as one continuous hood. Forward horn is shorter so it clears the beak.
    horn_w = r * 0.34
    # Forward horn (toward the beak): up-and-out, tip drooping down beside the head.
    fwd_root = (cx + f * r * 0.52, dome_top + r * 0.26)
    fwd_ctrl = (cx + f * r * 1.18, dome_top - r * 0.28)
    fwd_tip = (cx + f * r * 1.14, crown_y + r * 0.10)
    # Back horn: longer, up-and-out the other way, tip drooping lower.
    bck_root = (cx - f * r * 0.52, dome_top + r * 0.26)
    bck_ctrl = (cx - f * r * 1.30, dome_top - r * 0.34)
    bck_tip = (cx - f * r * 1.34, crown_y + r * 0.22)

    # Draw the back horn first so the forward one overlaps it.
    bck_tip = _droop_point(surf, bck_root, bck_ctrl, bck_tip, horn_w,
                           _GOLD, _GOLD_LO, head_w)
    fwd_tip = _droop_point(surf, fwd_root, fwd_ctrl, fwd_tip, horn_w,
                           _VIOLET, _VIOLET_LO, head_w)

    # Harlequin checker over the whole hood region (dome + horn roots).
    if head_w >= 18:
        hood_region = cap_poly
        _draw_diamonds(surf, hood_region, cx, crown_y, r, head_w)

    # A teal scalloped brim band rings the base of the cap — the jester collar.
    band_y = crown_y + r * 0.26
    band_h = max(2, int(r * 0.20))
    pygame.draw.rect(surf, _SHADOW,
                     (int(left_x), int(band_y), int(right_x - left_x), band_h))
    pygame.draw.rect(surf, _TEAL,
                     (int(left_x), int(band_y), int(right_x - left_x),
                      max(1, band_h - 1)))
    if head_w >= 20:
        bump_r = max(2, int(r * 0.13))
        step = bump_r * 1.8
        x = left_x + bump_r
        by = band_y + band_h
        while x <= right_x - bump_r * 0.5:
            pygame.draw.circle(surf, _SHADOW, (int(x), int(by)), bump_r)
            pygame.draw.circle(surf, _TEAL, (int(x), int(by - 1)),
                               max(1, bump_r - 1))
            x += step

    # Bells dangle off each drooping tip — the jester's jingle.
    bell_r = max(2, r * 0.26)
    _bell(surf, fwd_tip[0], fwd_tip[1] + bell_r + 1, bell_r, head_w)
    _bell(surf, bck_tip[0], bck_tip[1] + bell_r + 1, bell_r, head_w)


# Seat tuned so the dome caps the crown and the two horns flop off the sides
# without clipping the 64x100 candidate canvas (crown anchor y≈31).
build = make_build(draw_hat, seat={"hw": 27, "dx": 0, "dy": 12})
icon = make_icon(draw_hat)
