"""PARTY HAT redesign — DESIGN 2: BIRTHDAY CROWN (SCRATCH ONLY).

A pointed paper birthday crown: a gold zig-zag band of five triangular points
wrapping the head, each tip capped with a coloured gem. The silhouette is the
opposite of the original cone — WIDE and spiky, hugging the crown of the skull
low rather than rising into a tall point. That short-and-wide read is what sells
"it's my birthday" instead of "party cone".
"""
import math

import pygame

from tools.partyhat_candidates._template import make_build, make_icon

# Gold paper band + warm shade for the zig-zag body; a pale rim-light traces the
# lit edge of each point so the flat gold gains a bevel without a gradient muddy
# at 40px. Three jewel tones cycle across the tips for that toy-crown read.
_GOLD = (245, 197, 66)
_GOLD_LO = (214, 154, 30)
_RIM = (255, 240, 184)
_RUBY = (232, 69, 74)
_EMERALD = (63, 180, 107)
_SAPPHIRE = (59, 123, 232)
_GEM_HI = (255, 255, 255)

_GEMS = (_RUBY, _EMERALD, _SAPPHIRE, _RUBY, _EMERALD)


def draw_hat(surf, cx, base_y, head_w, facing=1):
    """Draw a side-profile BIRTHDAY CROWN sized for a head of width head_w,
    centered at cx, with the band's lower rim resting at base_y."""
    r = head_w * 0.5
    f = 1 if facing >= 0 else -1

    # The crown wraps a round head, so its band is WIDER than the skull and its
    # lower rim dips at the edges to cup the curve. Points are short — the tallest
    # rises only ~0.7*head_w so the thing stays a low, spiky tiara, not a cone.
    band_hw = r * 1.12
    left_x = cx - band_hw
    right_x = cx + band_hw

    # Lower rim of the band: a shallow upward arc (cups the round crown).
    rim_dip = r * 0.30
    band_h = r * 0.34            # vertical thickness of the solid gold band
    band_top_y = base_y - band_h

    def rim_y(t):
        # t in [0,1] across the band; edges sit at base_y, centre lifts up.
        return base_y - rim_dip * (1.0 - 4.0 * (t - 0.5) ** 2)

    def rim_top_y(t):
        return rim_y(t) - band_h

    # Five triangular points fanning up off the band top. A subtle forward lean
    # (scaled by facing) makes the crown read as worn rather than balanced.
    n_pts = 5
    lean = r * 0.10 * f
    # Tip heights vary a touch so the zig-zag silhouette isn't mechanically even.
    tip_scale = (0.78, 0.92, 1.0, 0.92, 0.78)
    point_h = r * 0.92

    # Compute the saw-tooth top outline: alternating valley (band top) / peak.
    valleys = []  # x at each point base centre
    peaks = []    # (x, y) peak apex per point
    seg = (right_x - left_x) / n_pts
    for i in range(n_pts):
        t_c = (i + 0.5) / n_pts
        vx = left_x + (i + 0.5) * seg
        valleys.append((i, vx, t_c))
        px = vx + lean
        py = rim_top_y(t_c) - point_h * tip_scale[i]
        peaks.append((px, py))

    # Build the full crown polygon: bottom rim (left->right), then back down the
    # saw-tooth top (right->left) so points alternate up.
    poly = []
    steps = 16
    for s in range(steps + 1):
        t = s / steps
        x = left_x + (right_x - left_x) * t
        poly.append((x, rim_y(t)))
    # Top edge, right to left: weave valley(top) -> peak -> valley(top) ...
    top_pts = []
    # right edge top
    top_pts.append((right_x, rim_top_y(1.0)))
    for i in reversed(range(n_pts)):
        # valley to the right of this peak, then the peak
        t_right = (i + 1) / n_pts
        vx_r = left_x + (i + 1) * seg
        top_pts.append((vx_r, rim_top_y(t_right)))
        top_pts.append(peaks[i])
    t_left = 0.0
    top_pts.append((left_x, rim_top_y(0.0)))
    poly.extend(top_pts)

    pygame.draw.polygon(surf, _GOLD, poly)

    # Shade the trailing flank of each point a step darker for cheap bevel.
    for i in range(n_pts):
        px, py = peaks[i]
        t_left_v = i / n_pts
        t_right_v = (i + 1) / n_pts
        vx_l = left_x + i * seg
        vx_r = left_x + (i + 1) * seg
        # Darken the back-facing half of the triangle (away from the light/lean).
        if f >= 0:
            shade_base = (vx_l, rim_top_y(t_left_v))
        else:
            shade_base = (vx_r, rim_top_y(t_right_v))
        pygame.draw.polygon(surf, _GOLD_LO, [shade_base, (px, py), (px, (shade_base[1] + py) * 0.5)])

    # Darker seam along the band's bottom rim for thickness.
    band_pts = [(left_x, rim_y(0.0))]
    for s in range(steps + 1):
        t = s / steps
        x = left_x + (right_x - left_x) * t
        band_pts.append((x, rim_y(t)))
    seam_h = max(1, int(band_h * 0.32))
    seam = [(x, y) for (x, y) in band_pts]
    seam += [(x, y - seam_h) for (x, y) in reversed(band_pts)]
    pygame.draw.polygon(surf, _GOLD_LO, seam)

    # Rim-light: a bright thread up the lit edge of each point and along band top.
    rim_w = max(1, int(r * 0.07))
    for i in range(n_pts):
        px, py = peaks[i]
        if f >= 0:
            t_right_v = (i + 1) / n_pts
            vx_r = left_x + (i + 1) * seg
            lit_base = (vx_r, rim_top_y(t_right_v))
        else:
            t_left_v = i / n_pts
            vx_l = left_x + i * seg
            lit_base = (vx_l, rim_top_y(t_left_v))
        pygame.draw.line(surf, _RIM, lit_base, (px, py), rim_w)

    # Gems on each tip. Faceted look = solid diamond + dark lower shade + a white
    # spark; gated below ~20px to a plain dot so tips don't smear at tiny scale.
    gem_r = max(2, int(r * 0.18))
    for i in range(n_pts):
        px, py = peaks[i]
        col = _GEMS[i]
        _draw_gem(surf, px, py, gem_r, col, head_w)


def _shade(col, k):
    return (int(col[0] * k), int(col[1] * k), int(col[2] * k))


def _draw_gem(surf, cx, cy, r, col, head_w):
    cx, cy = int(round(cx)), int(round(cy))
    if head_w < 20:
        pygame.draw.circle(surf, col, (cx, cy), max(1, r - 1))
        return
    # Diamond facet: a kite (top point, sides, bottom point).
    diamond = [
        (cx, cy - r),
        (cx + r * 0.8, cy),
        (cx, cy + r),
        (cx - r * 0.8, cy),
    ]
    pygame.draw.polygon(surf, col, diamond)
    # Lower-right facet darker for depth.
    pygame.draw.polygon(surf, _shade(col, 0.62),
                        [(cx, cy + r), (cx + r * 0.8, cy), (cx, cy)])
    # Bright spark top-left.
    pygame.draw.circle(surf, _GEM_HI,
                       (int(cx - r * 0.3), int(cy - r * 0.35)),
                       max(1, int(r * 0.28)))


# Seat: a birthday crown is SHORT, so it hugs the skull low and wide. Crown
# anchor sits at CROWN_Y(31); a wide band (hw 32) with the lower rim dropped well
# down (dy 16) cups the round head, and the ~0.7*hw points clear the 64x100
# canvas top comfortably. No forward shove — a tiara sits centred on the dome.
build = make_build(draw_hat, seat={"hw": 32, "dx": -1, "dy": 10})
icon = make_icon(draw_hat)
