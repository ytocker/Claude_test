"""5 surgical variations on the round-23 baseline Ruyi cloud.

Each variant paints the round-23 silhouette (3 lobes + base ribbon +
drop-shadow halo + arc keylines + dominant-lobe lit crescent) via a
shared internal _baseline_skeleton() helper, then applies ONE
surgical edit on top. Same family as the baseline by construction,
in contrast to ruyi_variants.py which deliberately diverged."""

from __future__ import annotations

import math
import random

import pygame

from cloud_variants import (
    _cloud_body_color, _ink_shadow_color, _lit_edge_color,
)
from ruyi_variants import (
    _ruyi_lobe, _ruyi_heart, _is_night, _lerp, _lerp_color,
    _seeded_jit, _alpha_surf,
)


# ── Local helpers ──────────────────────────────────────────────────────

def _pearl_dot(surf, cx, cy, r, color, alpha):
    """Porcelain pearl bead: small lit dot with a softer outer glow ring."""
    glow = _alpha_surf(r * 4, r * 4)
    pygame.draw.circle(glow, (*color, alpha // 3), (r * 2, r * 2), int(r * 1.6))
    pygame.draw.circle(glow, (*color, alpha), (r * 2, r * 2), r)
    surf.blit(glow, (cx - r * 2, cy - r * 2))


def _tassel_fringe(surf, x_top, y_top, length, body_col, accent_col, alpha):
    """Hanging silk tassel: 2-px knot + 3 thin drop strands fanning down."""
    pygame.draw.circle(surf, (*body_col, alpha), (x_top, y_top), 2)
    for dx in (-2, 0, 2):
        pygame.draw.line(surf, (*body_col, max(60, alpha - 60)),
                         (x_top + dx, y_top + 2),
                         (x_top + dx, y_top + length), 1)
    pygame.draw.line(surf, (*accent_col, alpha),
                     (x_top, y_top + length), (x_top, y_top + length + 2), 2)


def _ribbon_stem(surf, x, y_top, y_bot, color, alpha):
    """1-px vertical stem connecting a floating lobe to the ribbon below."""
    pygame.draw.line(surf, (*color, alpha), (x, y_top), (x, y_bot), 1)


def _baseline_skeleton(surf, x, y, palette, scale,
                       lobe_xs=(0.30, 0.50, 0.70),
                       lobe_lift=0,
                       lift_stems=False,
                       w=72, h=58):
    """Paints the round-23 baseline silhouette and returns lobe coords so
    decorating variants can place pearls / tassels / inner echoes on
    consistent anchor points. Drop-shadow halo gated at night per the
    round-2 AD cross-cutting fix."""
    w = int(w * scale)
    h = int(h * scale)
    night = _is_night(palette)
    body = _cloud_body_color(palette)
    edge = _ink_shadow_color(palette)
    lit = _lit_edge_color(palette)

    cx_left = x - w // 2
    cy_top = y - h // 2

    if not night:
        halo = _alpha_surf(w + 24, h + 24)
        pygame.draw.ellipse(halo, (*edge, 38),
                            pygame.Rect(0, 4, w + 20, h + 14))
        surf.blit(halo, (cx_left - 12, cy_top - 8))

    ribbon_h = max(4, int(h * 0.18))
    ribbon_y = cy_top + h - ribbon_h
    pygame.draw.ellipse(surf, (*body, 230),
                        pygame.Rect(cx_left + 4, ribbon_y, w - 8, ribbon_h))
    pygame.draw.arc(surf, edge,
                    pygame.Rect(cx_left + 4, ribbon_y, w - 8, ribbon_h),
                    math.radians(200), math.radians(340), 1)

    lobe_centers = []
    lobe_r = max(8, int(min(w, h) * 0.32))
    for i, xfrac in enumerate(lobe_xs):
        lcx = cx_left + int(w * xfrac)
        lcy = ribbon_y - lobe_lift - lobe_r // 2
        r = int(lobe_r * (1.1 if i == 1 else 1.0))
        _ruyi_lobe(surf, lcx, lcy, r, body, edge, lit,
                   body_a=248, key_a=180, lit_arc=(i == 1))
        if lift_stems and lobe_lift > 0:
            _ribbon_stem(surf, lcx, lcy + r // 2 + 1,
                         ribbon_y - 1, edge, 160)
        lobe_centers.append((lcx, lcy, r))
    return lobe_centers, (body, edge, lit, night)


# ══════════════════════════════════════════════════════════════════════
# 5 base-faithful variants — one surgical edit each
# ══════════════════════════════════════════════════════════════════════

# https://en.wikipedia.org/wiki/Ruyi_(scepter)
def draw_ruyi_compressed(surf, x, y, palette, scale=1.0):
    """Compressed Triplet: same DNA at lower aspect ratio — lobes pulled
    toward centre, frame denser. Same silhouette, different spacing."""
    _baseline_skeleton(surf, x, y, palette, scale,
                       lobe_xs=(0.35, 0.50, 0.65),
                       w=60, h=50)


# https://www.metmuseum.org/art/collection/search/61945
def draw_ruyi_pearled(surf, x, y, palette, scale=1.0):
    """Pearled Crown: baseline + 5 porcelain pearl beads along the top
    edges of the 3 lobes (Tang/Ming pearl-rim motif)."""
    centers, (body, edge, lit, night) = _baseline_skeleton(
        surf, x, y, palette, scale)
    pearl_r = max(1, int(2 * scale))
    pearl_col = lit if not night else _lerp_color(lit, body, 0.4)
    pearl_a = 220 if not night else 180
    pattern = ((2, -0.6), (1, -0.9), (2, -0.6))
    for (lcx, lcy, r), (n, yoff) in zip(centers, pattern):
        py = lcy + int(r * yoff)
        if n == 1:
            _pearl_dot(surf, lcx, py, pearl_r, pearl_col, pearl_a)
        else:
            spread = int(r * 0.55)
            for k in range(n):
                px = lcx - spread // 2 + k * spread
                _pearl_dot(surf, px, py, pearl_r, pearl_col, pearl_a)


# https://en.wikipedia.org/wiki/Chinese_paper_cutting
def draw_ruyi_lifted(surf, x, y, palette, scale=1.0):
    """Lifted Petals: 3 lobes float ~6 px above the ribbon, joined by
    1-px vertical stems. Paper-cut petal-on-stem-frame feel."""
    lift = max(3, int(6 * scale))
    _baseline_skeleton(surf, x, y, palette, scale,
                       lobe_lift=lift, lift_stems=True)


# https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/
def draw_ruyi_inner_echo(surf, x, y, palette, scale=1.0):
    """Inner Echo: baseline + 40%-scale mini-Ruyi echo drawn inside the
    dominant middle lobe (Tang caisson inner-motif). Outer silhouette
    unchanged; adds depth through a contained inner reference."""
    centers, (body, edge, lit, night) = _baseline_skeleton(
        surf, x, y, palette, scale)
    mlcx, mlcy, mr = centers[1]
    echo_r = max(3, int(mr * 0.40))
    echo_a = 110 if not night else 80
    for dx, dy in ((-echo_r, 0), (0, -echo_r // 2), (echo_r, 0)):
        pygame.draw.circle(surf, (*edge, echo_a),
                           (mlcx + dx // 2, mlcy + dy // 2),
                           max(1, echo_r // 3))
    pygame.draw.arc(surf, (*lit, echo_a),
                    pygame.Rect(mlcx - echo_r, mlcy - echo_r,
                                echo_r * 2, echo_r * 2),
                    math.radians(200), math.radians(340), 1)


# https://en.wikipedia.org/wiki/Dancheong
def draw_ruyi_tassel(surf, x, y, palette, scale=1.0):
    """Tassel Court Banner: baseline + 2 cinnabar silk tassels hanging
    off the underside of the base ribbon. Korean dancheong / temple-
    offering feel."""
    centers, (body, edge, lit, night) = _baseline_skeleton(
        surf, x, y, palette, scale)
    lcx0 = centers[0][0]
    lcx2 = centers[2][0]
    ribbon_y = centers[1][1] + centers[1][2] // 2 + 1
    tassel_len = max(5, int(7 * scale))
    accent = palette['horizon']
    tassel_body = _lerp_color(accent, _ink_shadow_color(palette), 0.4)
    alpha = 200 if not night else 150
    for tx in (lcx0 + (lcx2 - lcx0) // 3,
               lcx0 + (lcx2 - lcx0) * 2 // 3):
        _tassel_fringe(surf, tx, ribbon_y, tassel_len,
                       tassel_body, accent, alpha)


# ── Registry ──────────────────────────────────────────────────────────

VARIANTS = {
    1: draw_ruyi_compressed,
    2: draw_ruyi_pearled,
    3: draw_ruyi_lifted,
    4: draw_ruyi_inner_echo,
    5: draw_ruyi_tassel,
}

VARIANT_NAMES = {
    1: "Compressed Triplet",
    2: "Pearled Crown",
    3: "Lifted Petals",
    4: "Inner Echo",
    5: "Tassel Court Banner",
}

VARIANT_SOURCES = {
    1: "https://en.wikipedia.org/wiki/Ruyi_(scepter)",
    2: "https://www.metmuseum.org/art/collection/search/61945",
    3: "https://en.wikipedia.org/wiki/Chinese_paper_cutting",
    4: "https://www.dunhuang.ds.lib.uw.edu/mogao-cave-321-early-tang-dynasty/",
    5: "https://en.wikipedia.org/wiki/Dancheong",
}
