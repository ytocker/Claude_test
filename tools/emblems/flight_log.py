"""
Bespoke engraved center glyphs for the FAME — Flight Log achievement family
(GOLD tone). Procedural art only; these drop into
``game.achievement_icons._GLYPHS`` via the sibling render harness and are stamped
by the same engrave pipeline (dark inset pass down-right + lit body + up-left
sheen), so each glyph is authored with the single passed ``col`` and only routes
a saturated accent through ``_accent`` (none are needed here — Flight Log is pure
single-colour gold).

Four silhouette families keep the category readable at the ~22px glyph floor:

  * per-run pillars  — ARCHITECTURE that grows by count + structure
                       (1 post → 2-post gate → 3-post colonnade → triumphal arch).
  * score            — a CHEVRON climb whose rung-COUNT is the read (2 → 3).
  * day-cycle        — sun-on-horizon that gains identical MOON DISCS (1 → 3);
                       count is the read, no phase/crescent shapes.
  * lifetime pillars — a GLOBE that closes into a full flight-ORBIT.

Tier escalation for every family lives in ONE shared helper taking a ``tier``
arg, so the count/material climb is defined once and a glance reads the rank off
real motif growth rather than sub-pixel rank-pips.
"""
from __future__ import annotations

import math
import pygame

from game.achievement_icons import _GLYPH_SH, _accent


# ── shared rank-dressing accents (faint cherry-on-top, never the read) ────────
#
# The spec demotes L-marks to optional accents. They are drawn in the engraved
# inset-shadow tone so they sit UNDER the lit motif and never compete with the
# count/structure read that actually carries each tier.

def _rank_pips(surf, cx, baseline_y, r, col, n):
    # L1 — up to three small notch-dots tucked under the motif's foot.
    pr = max(2, int(r * 0.07))
    span = r * 0.30
    x0 = cx - span * (n - 1) / 2
    for i in range(n):
        pygame.draw.circle(surf, col, (int(x0 + span * i), int(baseline_y)), pr)


def _rank_wreath(surf, cx, baseline_y, r, col):
    # L2 — a short laurel-echo tick flanking each side of the foot.
    for sgn in (-1, 1):
        bx = cx + sgn * r * 0.66
        pygame.draw.line(surf, col, (int(bx), int(baseline_y)),
                         (int(bx + sgn * r * 0.18), int(baseline_y - r * 0.18)),
                         max(2, int(r * 0.07)))
        pygame.draw.line(surf, col, (int(bx), int(baseline_y)),
                         (int(bx + sgn * r * 0.20), int(baseline_y + r * 0.02)),
                         max(2, int(r * 0.07)))


def _rank_crownlet(surf, cx, top_y, r, col):
    # L4 — a 3-point engraved crownlet seated on top of the motif's apex.
    w = r * 0.50
    h = r * 0.26
    base_y = top_y
    pts = [
        (cx - w, base_y),
        (cx - w, base_y - h * 0.5),
        (cx - w * 0.5, base_y - h * 0.1),
        (cx, base_y - h),
        (cx + w * 0.5, base_y - h * 0.1),
        (cx + w, base_y - h * 0.5),
        (cx + w, base_y),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])


# ═══════════════════════════════════════════════════════════════════════════
# Family 1 — per-run pillars: architecture grows by COUNT + STRUCTURE.
#   tier 0 first_flight  : ONE squat pillar + a parcel at its foot.       L0
#   tier 1 pillar_25     : TWO pillars (a gateway), parcel gone.          L1 pips
#   tier 2 pillar_50     : THREE pillars stepping up (a colonnade).       L2 wreath
#   tier 3 pillar_100    : a triumphal ARCH spanning two posts.           L4 crown
# ═══════════════════════════════════════════════════════════════════════════

def _draw_one_pillar(surf, cx, top, h, shaft_w, cap_w, cap_h, col):
    # A single sandstone post: flared capital + base block + plain tapered shaft
    # (flutes are sub-pixel at row size, so the shaft is left clean per the spec
    # Fallback).
    pygame.draw.rect(surf, col, (int(cx - shaft_w / 2), int(top + cap_h),
                                 int(shaft_w), int(h - cap_h * 2)))
    for yy in (top, top + h - cap_h):
        pygame.draw.rect(surf, col, (int(cx - cap_w / 2), int(yy),
                                     int(cap_w), int(cap_h)),
                         border_radius=max(1, int(cap_h * 0.35)))


def _glyph_pillar_tier(surf, cx, cy, r, col, tier):
    # Shared "pillar gateway" motif. The number of posts and the resolution into
    # a monument IS the escalation; rank marks ride underneath only.
    base_y = cy + r * 0.92          # common foot line for all tiers

    if tier == 0:
        # First Delivery — one squat post with a little parcel at its foot.
        h = r * 1.20
        top = base_y - h
        sw = max(3, int(r * 0.34))
        cw = int(sw * 1.7)
        ch = max(2, int(r * 0.16))
        _draw_one_pillar(surf, cx - r * 0.30, top, h, sw, cw, ch, col)
        # parcel/letter: a small enveloped square with a corner-fold, at the foot.
        bx, by = cx + r * 0.46, base_y - r * 0.30
        bs = r * 0.42
        pygame.draw.rect(surf, col, (int(bx - bs / 2), int(by - bs / 2),
                                     int(bs), int(bs)),
                         border_radius=max(1, int(bs * 0.12)))
        # the corner fold (cross-tie of the parcel) in the inset tone so it reads
        # as an indent on the parcel face.
        pygame.draw.line(surf, _GLYPH_SH, (int(bx - bs / 2), int(by - bs * 0.1)),
                         (int(bx + bs / 2), int(by - bs * 0.1)), max(2, int(r * 0.07)))
        pygame.draw.line(surf, _GLYPH_SH, (int(bx), int(by - bs / 2)),
                         (int(bx), int(by + bs / 2)), max(2, int(r * 0.07)))
        return

    if tier == 1:
        # Courier in Training — two equal posts framing a gateway.
        h = r * 1.34
        top = base_y - h
        sw = max(3, int(r * 0.30))
        cw = int(sw * 1.7)
        ch = max(2, int(r * 0.15))
        for sgn in (-1, 1):
            _draw_one_pillar(surf, cx + sgn * r * 0.50, top, h, sw, cw, ch, col)
        # a lintel bridging the two caps so the pair reads as a GATE, not a tally.
        pygame.draw.rect(surf, col, (int(cx - r * 0.74), int(top - r * 0.04),
                                     int(r * 1.48), max(2, int(r * 0.16))),
                         border_radius=max(1, int(r * 0.05)))
        _rank_pips(surf, cx, base_y + r * 0.14, r, _GLYPH_SH, 2)
        return

    if tier == 2:
        # Route Veteran — three posts stepping up in height (a colonnade
        # receding to the right reads as DEPTH / a row).
        sw = max(3, int(r * 0.24))
        cw = int(sw * 1.7)
        ch = max(2, int(r * 0.13))
        cols = (-0.60, 0.0, 0.60)
        heights = (1.04, 1.30, 1.54)
        for fx, fh in zip(cols, heights):
            h = r * fh
            _draw_one_pillar(surf, cx + fx * r, base_y - h, h, sw, cw, ch, col)
        _rank_wreath(surf, cx, base_y + r * 0.14, r, _GLYPH_SH)
        return

    # tier 3 — Centurion: a triumphal arch (a thick semicircle bridging two
    # posts), the colonnade resolved into a single monument, crowned.
    sw = max(4, int(r * 0.30))
    span = r * 0.56                 # half-distance between the two post centres
    leg_top = cy - r * 0.20
    leg_h = base_y - leg_top
    for sgn in (-1, 1):
        px = cx + sgn * span
        pygame.draw.rect(surf, col, (int(px - sw / 2), int(leg_top),
                                     int(sw), int(leg_h)))
        # base block
        pygame.draw.rect(surf, col, (int(px - sw * 0.85), int(base_y - r * 0.16),
                                     int(sw * 1.7), max(2, int(r * 0.16))),
                         border_radius=max(1, int(r * 0.05)))
    # the arch: a thick semicircular band springing from the two post tops.
    arc_r = span + sw / 2
    rect = pygame.Rect(int(cx - arc_r), int(leg_top - arc_r),
                       int(arc_r * 2), int(arc_r * 2))
    pygame.draw.arc(surf, col, rect, math.radians(0), math.radians(180),
                    max(4, int(sw * 0.95)))
    # keystone block at the apex.
    pygame.draw.rect(surf, col, (int(cx - r * 0.13), int(leg_top - arc_r - r * 0.04),
                                 int(r * 0.26), int(r * 0.24)),
                     border_radius=max(1, int(r * 0.04)))
    _rank_crownlet(surf, cx, leg_top - arc_r - r * 0.18, r, col)


def _glyph_first_flight(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 0)


def _glyph_pillar_25(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 1)


def _glyph_pillar_50(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 2)


def _glyph_pillar_100(surf, cx, cy, r, col):
    _glyph_pillar_tier(surf, cx, cy, r, col, 3)


# ═══════════════════════════════════════════════════════════════════════════
# Family 2 — score: a chevron climb. The rung-COUNT carries the tier (2 → 3);
# score_500 alone adds a wing-pip. NO ray-halo (it muds into the chevrons).
#   tier 0 score_100 : 2 chevrons + three tally ticks beneath.
#   tier 1 score_500 : 3 chevrons rising higher + a wing-pip on the top one.
# ═══════════════════════════════════════════════════════════════════════════

def _draw_chevron(surf, cx, apex_y, half_w, thick, col):
    # An up-pointing chevron (a thick fat-bottomed ">" rotated to point up).
    drop = half_w * 0.62
    outer = [
        (cx - half_w, apex_y + drop),
        (cx, apex_y),
        (cx + half_w, apex_y + drop),
        (cx + half_w - thick * 0.5, apex_y + drop + thick * 0.7),
        (cx, apex_y + thick),
        (cx - half_w + thick * 0.5, apex_y + drop + thick * 0.7),
    ]
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in outer])


def _glyph_score_tier(surf, cx, cy, r, col, tier):
    n = 2 if tier == 0 else 3
    half_w = r * 0.66
    thick = max(3, int(r * 0.22))
    step = r * 0.46                 # vertical spacing between stacked chevrons
    # Stack rises up-right: each higher chevron is nudged right so the climb
    # reads as a delivery-flight ascent, not a static stack.
    top_apex = cy - (n - 1) * step / 2 - r * 0.18
    for i in range(n):
        ax = cx + (i - (n - 1) / 2) * r * 0.16
        ay = top_apex + (n - 1 - i) * step
        _draw_chevron(surf, ax, ay, half_w, thick, col)

    if tier == 0:
        # three short tally ticks beneath — the "triple digits" nod.
        ty = cy + r * 0.82
        for dx in (-0.26, 0.0, 0.26):
            x = cx + dx * r
            pygame.draw.line(surf, col, (int(x), int(ty)),
                             (int(x), int(ty + r * 0.22)), max(2, int(r * 0.10)))
    else:
        # a small wing-pip lifting off ABOVE the top chevron — the only added
        # flourish (NO ray halo, which would mud into the chevrons). Set clear of
        # the chevron stack and given a 2-lobe trailing edge so it reads as a
        # wing, not a fourth chevron.
        wx = cx + r * 0.06
        wy = top_apex - r * 0.46
        wing = [
            (wx - r * 0.40, wy + r * 0.14),     # shoulder
            (wx + r * 0.06, wy - r * 0.30),     # leading edge to tip
            (wx + r * 0.40, wy - r * 0.36),     # tip
            (wx + r * 0.14, wy - r * 0.08),     # trailing lobe 1
            (wx + r * 0.02, wy + r * 0.06),     # trailing lobe 2
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in wing])


def _glyph_score_100(surf, cx, cy, r, col):
    _glyph_score_tier(surf, cx, cy, r, col, 0)


def _glyph_score_500(surf, cx, cy, r, col):
    _glyph_score_tier(surf, cx, cy, r, col, 1)


# ═══════════════════════════════════════════════════════════════════════════
# Family 3 — day-cycle: a half-sun over a horizon that acquires identical moon
# discs. The disc-COUNT is the night-count and the read (1 → 3); no phase
# shapes (sub-pixel at row size).
#   tier 0 day_complete : half-sun + 1 moon-disc, faint orbit arc.     L0
#   tier 1 day_three    : half-sun + 3 identical moon-discs in a row.  L2 wreath
# ═══════════════════════════════════════════════════════════════════════════

def _draw_half_sun(surf, sun_cx, horizon_y, sun_r, r, col):
    # A clean half-disc sitting ON the horizon (drawn as a filled polygon fan of
    # the upper semicircle so it's a solid dome with a flat base), ringed by a
    # gap then distinct radiating rays so it reads as a SUN, not a hill.
    fan = [(sun_cx + sun_r, horizon_y)]
    for k in range(13):
        a = math.pi * k / 12          # 0..pi sweeping the upper half
        fan.append((sun_cx + math.cos(a) * sun_r, horizon_y - math.sin(a) * sun_r))
    pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in fan])
    for k in range(5):
        a = math.pi * (k + 0.5) / 5    # five rays fanning over the upper half
        x1 = sun_cx + math.cos(a) * sun_r * 1.28
        y1 = horizon_y - math.sin(a) * sun_r * 1.28
        x2 = sun_cx + math.cos(a) * sun_r * 1.66
        y2 = horizon_y - math.sin(a) * sun_r * 1.66
        pygame.draw.line(surf, col, (int(x1), int(y1)), (int(x2), int(y2)),
                         max(2, int(r * 0.09)))


def _glyph_day_tier(surf, cx, cy, r, col, tier):
    horizon_y = cy + r * 0.52
    sun_r = r * 0.42
    sun_cx = cx - r * 0.30
    _draw_half_sun(surf, sun_cx, horizon_y, sun_r, r, col)
    # horizon line.
    pygame.draw.line(surf, col, (int(cx - r * 0.94), int(horizon_y)),
                     (int(cx + r * 0.94), int(horizon_y)), max(2, int(r * 0.11)))

    moon_r = r * 0.22
    if tier == 0:
        # one plain moon-disc up-right of the sun, framed by a faint orbit arc
        # (one day → night). The moon carries an inset bite of shadow on its
        # lower-right so it reads as a celestial disc, not just a dot.
        mx, my = cx + r * 0.52, cy - r * 0.42
        pygame.draw.circle(surf, col, (int(mx), int(my)), int(moon_r))
        pygame.draw.circle(surf, _GLYPH_SH,
                           (int(mx + moon_r * 0.42), int(my + moon_r * 0.30)),
                           int(moon_r * 0.62))
        orb = pygame.Rect(int(mx - r * 0.82), int(my - r * 0.82),
                          int(r * 1.64), int(r * 1.64))
        pygame.draw.arc(surf, col, orb, math.radians(-20), math.radians(150),
                        max(2, int(r * 0.07)))
    else:
        # three identical moon-discs arcing over the sun in a row — the COUNT is
        # the read; a faint orbit arc threads them.
        arc_cx, arc_cy = cx, cy + r * 0.34
        arc_r = r * 0.86
        orb = pygame.Rect(int(arc_cx - arc_r), int(arc_cy - arc_r),
                          int(arc_r * 2), int(arc_r * 2))
        pygame.draw.arc(surf, col, orb, math.radians(28), math.radians(152),
                        max(2, int(r * 0.07)))
        for ang in (148, 90, 32):
            a = math.radians(ang)
            mx = arc_cx + math.cos(a) * arc_r
            my = arc_cy - math.sin(a) * arc_r
            pygame.draw.circle(surf, col, (int(mx), int(my)), int(moon_r))
        _rank_wreath(surf, cx, horizon_y + r * 0.34, r, _GLYPH_SH)


def _glyph_day_complete(surf, cx, cy, r, col):
    _glyph_day_tier(surf, cx, cy, r, col, 0)


def _glyph_day_three(surf, cx, cy, r, col):
    _glyph_day_tier(surf, cx, cy, r, col, 1)


# ═══════════════════════════════════════════════════════════════════════════
# Family 4 — lifetime pillars: a globe that closes into a full flight-orbit.
# Distinct from the per-run architecture: this is all-time DISTANCE.
#   tier 0 frequent_flyer : winged globe (circle + 1 lat + 1 long arc).  L2 wreath
#   tier 1 globetrotter   : globe wrapped by a full dashed orbit ring +
#                           a parrot-pip on the orbit.                    L4 crown
# ═══════════════════════════════════════════════════════════════════════════

def _draw_globe(surf, cx, cy, gr, col):
    # Circle + ONE vertical meridian + ONE horizontal equator arc (the spec
    # Fallback — extra longitude lines crowd at row size).
    lw = max(2, int(gr * 0.12))
    pygame.draw.circle(surf, col, (int(cx), int(cy)), int(gr), lw)
    # equator: a shallow horizontal ellipse arc across the middle.
    eq = pygame.Rect(int(cx - gr), int(cy - gr * 0.34),
                     int(gr * 2), int(gr * 0.68))
    pygame.draw.ellipse(surf, col, eq, lw)
    # meridian: a tall narrow ellipse for the front-facing longitude.
    mer = pygame.Rect(int(cx - gr * 0.40), int(cy - gr),
                      int(gr * 0.80), int(gr * 2))
    pygame.draw.ellipse(surf, col, mer, lw)


def _glyph_lifetime_tier(surf, cx, cy, r, col, tier):
    gr = r * 0.52
    gcx, gcy = cx, cy + (0 if tier else -r * 0.04)

    if tier == 0:
        _draw_globe(surf, gcx, gcy, gr, col)
        # a tiny wing-tick riding the globe's upper-right shoulder — "flyer".
        wx, wy = gcx + gr * 0.78, gcy - gr * 0.72
        wing = [
            (wx - r * 0.06, wy + r * 0.16),
            (wx + r * 0.40, wy - r * 0.16),
            (wx + r * 0.16, wy + r * 0.04),
            (wx + r * 0.34, wy + r * 0.10),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in wing])
        _rank_wreath(surf, cx, cy + r * 0.96, r, _GLYPH_SH)
        return

    # tier 1 — the route closes into a full lap: a dashed flight-orbit ellipse
    # wraps the globe at a jaunty tilt, with a parrot-silhouette pip on it.
    _draw_globe(surf, gcx, gcy, gr, col)
    orb_rx, orb_ry = r * 0.96, r * 0.50
    tilt = math.radians(-22)
    n = 22
    dash_w = max(2, int(r * 0.10))
    pip_at = None
    for i in range(n):
        if i % 2:                    # every other segment skipped → dashed look
            continue
        a0 = i / n * math.tau
        a1 = (i + 1) / n * math.tau
        seg = []
        for a in (a0, a1):
            ex = math.cos(a) * orb_rx
            ey = math.sin(a) * orb_ry
            rx = ex * math.cos(tilt) - ey * math.sin(tilt)
            ry = ex * math.sin(tilt) + ey * math.cos(tilt)
            seg.append((int(gcx + rx), int(gcy + ry)))
        # behind the globe (top arc) → inset tone; in front (bottom) → lit, so
        # the ring reads as wrapping AROUND the globe.
        a_mid = (a0 + a1) / 2
        front = math.sin(a_mid) > 0
        pygame.draw.line(surf, col if front else _GLYPH_SH, seg[0], seg[1], dash_w)
        if abs(a_mid - math.radians(20)) < math.radians(18):
            pip_at = seg[1]
    # parrot-pip: a small body + beak chevron riding the front of the orbit.
    if pip_at is None:
        pip_at = (int(gcx + orb_rx * 0.92), int(gcy + orb_ry * 0.2))
    px, py = pip_at
    pygame.draw.circle(surf, col, (px, py), max(3, int(r * 0.13)))
    pygame.draw.polygon(surf, col, [
        (px + int(r * 0.10), py - int(r * 0.04)),
        (px + int(r * 0.28), py + int(r * 0.02)),
        (px + int(r * 0.10), py + int(r * 0.10)),
    ])
    _rank_crownlet(surf, cx, gcy - gr - r * 0.10, r, col)


def _glyph_frequent_flyer(surf, cx, cy, r, col):
    _glyph_lifetime_tier(surf, cx, cy, r, col, 0)


def _glyph_globetrotter(surf, cx, cy, r, col):
    _glyph_lifetime_tier(surf, cx, cy, r, col, 1)


GLYPHS = {
    "first_flight": _glyph_first_flight,
    "pillar_25": _glyph_pillar_25,
    "pillar_50": _glyph_pillar_50,
    "pillar_100": _glyph_pillar_100,
    "score_100": _glyph_score_100,
    "score_500": _glyph_score_500,
    "day_complete": _glyph_day_complete,
    "day_three": _glyph_day_three,
    "frequent_flyer": _glyph_frequent_flyer,
    "globetrotter": _glyph_globetrotter,
}
