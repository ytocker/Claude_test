"""PARTY HAT redesign — DESIGN 3: JESTER CAP (SCRATCH ONLY).

A perched two-point jester cap: a low dome caps the crown with a teal band at
the hairline, and TWO horns project up-and-out with open sky beneath them —
one short and forward, one longer and back — each tipped with a gold jingle
bell against that sky. The two horns + two bells are the whole silhouette: a
cap that is unmistakably not-a-cone even at a 40px worn read.

Detail is hard-gated on size. At small worn sizes the harlequin lattice and
scallops drop out and the cap goes clean two-tone (gold forward, violet back)
so the bells, the air under the horns, and the band line survive. The full
diamond pattern + scalloped collar return only at icon/hero size.
"""
import math

import pygame

from ._template import make_build, make_icon

_VIOLET = (123, 47, 247)
_VIOLET_LO = (88, 32, 178)
_VIOLET_RIM = (58, 22, 120)   # near-black-violet edge so the violet horn keeps
                              # a silhouette against night sky
_GOLD = (255, 210, 63)
_GOLD_LO = (210, 168, 40)
_TEAL = (25, 195, 201)
_TEAL_LO = (16, 132, 138)
_SHADOW = (32, 28, 50)
_BELL_HI = (255, 243, 196)
_BELL = (255, 210, 63)
_BELL_LO = (180, 138, 28)


def _bezier(p0, p1, p2, n=16):
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def _horn(surf, root, ctrl, tip, half_w, col, col_lo, rim_col, head_w):
    """A tapering horn from a fat root to a thin tip, drawn as two bezier edges
    so it curves like soft fabric. A dark rim is stroked down the outer edge so
    the lobe keeps a silhouette even against a same-hue night sky. Returns the
    tip point for hanging the bell."""
    spine = _bezier(root, ctrl, tip, 18)
    left, right = [], []
    n = len(spine)
    for i, (x, y) in enumerate(spine):
        t = i / (n - 1)
        w = half_w * (1.0 - t) ** 0.8
        if i < n - 1:
            nx, ny = spine[i + 1]
        else:
            nx, ny = x, y
        dx, dy = nx - x, ny - y
        d = math.hypot(dx, dy) or 1.0
        px, py = -dy / d, dx / d
        left.append((x + px * w, y + py * w))
        right.append((x - px * w, y - py * w))
    poly = left + right[::-1]
    pygame.draw.polygon(surf, col, poly)
    # Darker underside seam fakes the fold; a rim line on both edges keeps the
    # horn legible when its hue matches the sky behind it.
    pygame.draw.polygon(surf, col_lo, [spine[0]] + right + [spine[-1]])
    rim_w = max(1, int(head_w * 0.045))
    pygame.draw.lines(surf, rim_col, False, left, rim_w)
    pygame.draw.lines(surf, rim_col, False, right, rim_w)
    return tip


def _bell(surf, x, y, r, head_w):
    """A round jingle bell: gold body, bright catch-light, dark rim, slit. Gated
    detail so it survives as a clean rimmed gold dot when shrunk."""
    x, y = int(x), int(y)
    r = max(3, int(r))
    # Dark outer ring so a gold dot reads against gold/bright day sky too.
    pygame.draw.circle(surf, _BELL_LO, (x, y), r + 1)
    pygame.draw.circle(surf, _BELL, (x, y), r)
    if head_w >= 24:
        pygame.draw.line(surf, _BELL_LO, (x - r + 1, y + r // 3),
                         (x + r - 1, y + r // 3), max(1, r // 3))
        pygame.draw.circle(surf, _BELL_LO, (x, y + r - 1), max(1, r // 3))
    pygame.draw.circle(surf, _BELL_HI, (x - r // 3, y - r // 3),
                       max(2, r // 3))


def _draw_diamonds(surf, hood_poly, r):
    """Harlequin diamond checker clipped to the dome — icon/hero only. A rotated
    violet/gold lattice sells the full jester pattern at large sizes."""
    xs = [p[0] for p in hood_poly]
    ys = [p[1] for p in hood_poly]
    bb = pygame.Rect(int(min(xs)) - 2, int(min(ys)) - 2,
                     int(max(xs) - min(xs)) + 4, int(max(ys) - min(ys)) + 4)
    if bb.width <= 0 or bb.height <= 0:
        return
    layer = pygame.Surface(bb.size, pygame.SRCALPHA)
    ox, oy = bb.left, bb.top
    dx_ = max(5, r * 0.40)
    dy_ = max(4, r * 0.30)
    j0 = int(bb.width / dx_) + 4
    k0 = int(bb.height / dy_) + 4
    for k in range(-2, k0):
        for j in range(-2, j0):
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
    at cx, with the band line near base_y (the crown/hairline)."""
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1
    big = head_w >= 24   # diamonds + scallops + full bell detail only when big

    # Perched dome: a shallow cap hugging the crown, spanning ~1.5x head width
    # so cap+horns together land at ~1.7x — perched, not draped.
    crown_y = base_y - r * 0.06
    dome_top = crown_y - r * 0.50
    dome_hw = r * 0.72
    left_x = cx - dome_hw
    right_x = cx + dome_hw

    dome = []
    steps = 16
    for i in range(steps + 1):
        t = i / steps
        ang = math.pi * t
        x = cx - math.cos(ang) * dome_hw
        y = crown_y - math.sin(ang) * (r * 0.62)
        dome.append((x, y))
    cap_poly = dome + [(right_x, crown_y), (left_x, crown_y)]

    # Two-tone split when small: front half gold, back half violet, so each horn
    # base matches its horn and the cap reads as two colours not one blob. The
    # full harlequin lattice returns only at icon/hero size.
    if big:
        pygame.draw.polygon(surf, _VIOLET, cap_poly)
        _draw_diamonds(surf, cap_poly, r)
    else:
        front = [(p[0], p[1]) for p in cap_poly if (p[0] - cx) * f >= -0.5]
        pygame.draw.polygon(surf, _VIOLET, cap_poly)        # base fill
        if len(front) >= 3:
            pygame.draw.polygon(surf, _GOLD, front)         # forward half gold

    # Horns project UP-and-OUT with open sky beneath them. Roots are pinched and
    # sit near the crown of the dome (not its wide shoulders) so they do NOT
    # swallow the dome; tips rise ABOVE the dome top and reach out past the cap
    # edge so there is visible sky between each horn and the head. Forward horn
    # shorter, back horn longer — the asymmetric two-point silhouette.
    horn_w = r * 0.22
    # Forward horn (toward the beak): up-and-out, tip high and clearly rising.
    fwd_root = (cx + f * r * 0.30, dome_top + r * 0.08)
    fwd_ctrl = (cx + f * r * 0.80, dome_top - r * 0.60)
    fwd_tip = (cx + f * r * 0.84, dome_top - r * 0.34)
    # Back horn: longer, up-and-back, tip highest of the two.
    bck_root = (cx - f * r * 0.30, dome_top + r * 0.08)
    bck_ctrl = (cx - f * r * 0.92, dome_top - r * 0.86)
    bck_tip = (cx - f * r * 0.96, dome_top - r * 0.64)

    bck_tip = _horn(surf, bck_root, bck_ctrl, bck_tip, horn_w,
                    _VIOLET, _VIOLET_LO, _VIOLET_RIM, head_w)
    fwd_tip = _horn(surf, fwd_root, fwd_ctrl, fwd_tip, horn_w,
                    _GOLD, _GOLD_LO, _GOLD_LO, head_w)

    # Thin teal band at the hairline. On-bird it is a single line with a shadow
    # underline; scalloped bumps return only at icon/hero size.
    band_y = crown_y - r * 0.02
    band_h = max(2, int(r * 0.16)) if big else max(2, int(r * 0.12))
    pygame.draw.rect(surf, _SHADOW,
                     (int(left_x), int(band_y + band_h - 1),
                      int(right_x - left_x), max(1, int(band_h * 0.5))))
    pygame.draw.rect(surf, _TEAL,
                     (int(left_x), int(band_y), int(right_x - left_x), band_h))
    pygame.draw.line(surf, _TEAL_LO, (int(left_x), int(band_y)),
                     (int(right_x), int(band_y)), 1)
    if big:
        bump_r = max(2, int(r * 0.12))
        step = bump_r * 1.8
        x = left_x + bump_r
        by = band_y + band_h
        while x <= right_x - bump_r * 0.5:
            pygame.draw.circle(surf, _SHADOW, (int(x), int(by)), bump_r)
            pygame.draw.circle(surf, _TEAL, (int(x), int(by - 1)),
                               max(1, bump_r - 1))
            x += step

    # Bells at the RAISED tips, against open sky — the strongest jester signal.
    bell_r = max(3, r * 0.20)
    _bell(surf, fwd_tip[0] + f * bell_r * 0.4, fwd_tip[1], bell_r, head_w)
    _bell(surf, bck_tip[0] - f * bell_r * 0.4, bck_tip[1], bell_r, head_w)


# Seat: dome caps the crown with the band at the hairline; horns + bells rise
# into the headroom above the crown. hw shrunk + dy lifted so the cap is perched
# (~1.7x head width) instead of draped over the back.
build = make_build(draw_hat, seat={"hw": 22, "dx": 0, "dy": 7})
icon = make_icon(draw_hat)
