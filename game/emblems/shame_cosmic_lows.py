"""Bespoke engraved center glyphs for the SHAME — Cosmic Jokes + Lifetime Lows
(Hall of SHAME) medallions, rendered TARNISHED (cracked-pewter anti-trophy).

Seven anti-trophy glyphs in the single-colour engrave idiom of
``game.achievement_icons``: each ``_glyph_<id>(surf, cx, cy, r, col)`` lays BOLD
filled shapes in the passed ``col`` only — the builder strokes a down-right inset
shadow + up-left sheen for the struck-relief look, so a glyph hard-codes no fills
of its own. Recessed sockets/eyes use the engraved-shadow tone ``_SH``; the lone
two-tone prop (the magnet pole-tips) routes through ``ai._accent`` so it stays
bronze until the medal is earned. Authored to the ~44px legibility floor:
nothing thinner than ~2px, and each id resolves to ONE decisive silhouette that
puts the JOKE in the shape.

The tricky trio is drawn apart on purpose: ``groundhog_day`` wraps the repeat
loop around a rectangular PILLAR, ``same_time_tomorrow`` wraps it around a round
CLOCK, and ``three_am`` is a clock with a MOON and NO loop — three unmistakable
silhouettes. ``lightning_magnet`` shows a magnet catching MANY bolts (poles UP),
the mirror of the coin-pulling ``magnet_life`` (poles down).

WRITE-ONLY module: imports ``game`` read-only and never mutates it; the render
harness merges ``GLYPHS`` into a private copy of the badge glyph table.
"""
from __future__ import annotations

import math

import pygame

import game.achievement_icons as ai

# Reuse the live module's engraved-shadow tone so the dark sockets/recesses in
# these glyphs match the cast-shadow pass the builder stamps around them.
_SH = ai._GLYPH_SH


def _loop_arrow(surf, cx, cy, rad, col, w):
    # A single circular repeat/recycle arrow leaving a gap at the lower-right and
    # chasing its own tail — the shared "stuck in a loop" cue. Wrapped around a
    # pillar (groundhog) or a clock (same_time), the enclosed object is what tells
    # the two apart; the loop itself is deliberately identical.
    rect = pygame.Rect(cx - rad, cy - rad, rad * 2, rad * 2)
    a_start = math.radians(-32)
    a_stop = math.radians(250)
    pygame.draw.arc(surf, col, rect, a_start, a_stop, w)
    # Arrowhead at the visual stop end. pygame arcs run CCW in math angles while
    # the surface y is flipped, so place points with y negated and aim the head
    # along the direction of travel (toward a slightly larger angle).
    ex = cx + rad * math.cos(a_stop)
    ey = cy - rad * math.sin(a_stop)
    a_prev = a_stop - math.radians(20)
    px = cx + rad * math.cos(a_prev)
    py = cy - rad * math.sin(a_prev)
    dx, dy = ex - px, ey - py
    dl = math.hypot(dx, dy) or 1.0
    dx, dy = dx / dl, dy / dl
    hl = rad * 0.55
    # two barbs swept back from the tip
    for sgn in (-1, 1):
        bx = ex - dx * hl + sgn * (-dy) * hl * 0.7
        by = ey - dy * hl + sgn * dx * hl * 0.7
        pygame.draw.line(surf, col, (int(ex), int(ey)), (int(bx), int(by)), w)


def _pillar(surf, cx, cy, r, col, scale=1.0):
    # A single sandstone pillar (flared capital + shaft + base) — the temple-gate
    # read, scaled to sit inside the groundhog loop.
    shaft_w = max(4, int(r * 0.30 * scale))
    cap_w = int(shaft_w * 1.7)
    h = int(r * 1.12 * scale)
    top = cy - h // 2
    cap_h = max(3, int(r * 0.15 * scale))
    pygame.draw.rect(surf, col, (cx - shaft_w // 2, top + cap_h,
                                 shaft_w, h - cap_h * 2))
    for yy in (top, cy + h // 2 - cap_h):            # capital + base slabs
        pygame.draw.rect(surf, col, (cx - cap_w // 2, yy, cap_w, cap_h),
                         border_radius=max(1, int(r * 0.05)))


def _clock_face(surf, cx, cy, rr, col, w):
    # Bare clock dial: a bold ring, four cardinal ticks, and a hub. Hands are the
    # caller's job so three_am / same_time can pose them differently.
    pygame.draw.circle(surf, col, (cx, cy), rr, w)
    for i in range(4):
        a = i * math.pi / 2
        x1 = cx + int(math.cos(a) * rr * 0.74)
        y1 = cy + int(math.sin(a) * rr * 0.74)
        x2 = cx + int(math.cos(a) * rr * 0.94)
        y2 = cy + int(math.sin(a) * rr * 0.94)
        pygame.draw.line(surf, col, (x1, y1), (x2, y2), max(2, w - 1))
    pygame.draw.circle(surf, col, (cx, cy), max(3, int(rr * 0.14)))


def _glyph_ninety_nine(surf, cx, cy, r, col):
    # A circular fill-gauge run almost the whole way round, with ONE final segment
    # bitten out of the very top and a bold down-arrow plunging into that gap —
    # "one notch short, and it went the wrong way." No numerals; the missing top
    # wedge IS the 99.
    rad = int(r * 0.66)
    w = max(4, int(r * 0.26))
    rect = pygame.Rect(cx - rad, cy - rad, rad * 2, rad * 2)
    # Fill arc from just right of top, clockwise all the way to just left of top,
    # leaving a clean wedge missing at 12 o'clock. In math/CCW+flipped-y terms
    # that is a sweep from ~100° up and around to ~80°.
    pygame.draw.arc(surf, col, rect, math.radians(100), math.radians(80 + 360), w)
    # Bold down-arrow dropped into the top gap — the final notch that fell short.
    ax = cx
    a_top = cy - int(r * 0.46)
    a_tip = cy + int(r * 0.10)
    pygame.draw.line(surf, col, (ax, a_top), (ax, a_tip), max(4, int(r * 0.18)))
    head = int(r * 0.24)
    pygame.draw.polygon(surf, col, [
        (ax, a_tip + int(r * 0.14)),
        (ax - head, a_tip - head + int(r * 0.14)),
        (ax + head, a_tip - head + int(r * 0.14)),
    ])


def _glyph_groundhog_day(surf, cx, cy, r, col):
    # A repeat/loop arrow wound around a single sandstone PILLAR — stuck reliving
    # the same pillar. The enclosed rectangular pillar is what sets this apart
    # from same_time_tomorrow (whose loop rings a round clock).
    _pillar(surf, cx, cy, r, col, scale=0.94)
    _loop_arrow(surf, cx, cy, int(r * 0.80), col, max(4, int(r * 0.16)))


def _glyph_stat_impossible(surf, cx, cy, r, col):
    # A bell-curve silhouette on a baseline with a lone outlier spike stranded far
    # out on the right tail — the one-in-a-million all-prime run. The isolated
    # dot-topped spike, detached from the hump, is the whole read.
    base_y = cy + int(r * 0.62)
    left = cx - int(r * 0.92)
    right = cx + int(r * 0.30)
    # baseline axis
    pygame.draw.line(surf, col, (left, base_y),
                     (cx + int(r * 0.98), base_y), max(3, int(r * 0.11)))
    # Gaussian hump as a filled polygon rising off the baseline.
    peak = cx - int(r * 0.31)
    pts = [(left, base_y)]
    span = right - left
    for i in range(1, 15):
        t = i / 15
        x = left + int(t * span)
        # bell centred on `peak`, normalised width
        u = (x - peak) / (r * 0.42)
        y = base_y - int(math.exp(-u * u) * r * 0.92)
        pts.append((x, y))
    pts.append((right, base_y))
    pygame.draw.polygon(surf, col, pts)
    # Lone outlier: a thin spike far out on the tail, capped with a bold dot,
    # clearly separated from the hump — the improbable event.
    ox = cx + int(r * 0.74)
    pygame.draw.line(surf, col, (ox, base_y),
                     (ox, base_y - int(r * 0.56)), max(3, int(r * 0.12)))
    pygame.draw.circle(surf, col, (ox, base_y - int(r * 0.62)), max(4, int(r * 0.16)))


def _glyph_three_am(surf, cx, cy, r, col):
    # A clock reading 3 o'clock with a crescent moon tucked at its shoulder and NO
    # loop — the "it is 3 a.m., go to bed" gag. Short hour hand out to 3, long
    # minute hand up to 12; the moon is what separates it from same_time_tomorrow.
    ccx = cx - int(r * 0.14)
    ccy = cy + int(r * 0.10)
    rr = int(r * 0.60)
    w = max(3, int(r * 0.11))
    _clock_face(surf, ccx, ccy, rr, col, w)
    hw = max(3, int(r * 0.10))
    # hour hand -> 3 o'clock (right), short
    pygame.draw.line(surf, col, (ccx, ccy),
                     (ccx + int(rr * 0.62), ccy), hw)
    # minute hand -> 12 (up), long
    pygame.draw.line(surf, col, (ccx, ccy),
                     (ccx, ccy - int(rr * 0.88)), hw)
    # Crescent moon at the upper-right shoulder: a disc with a bite carved out by
    # a second disc in the shadow tone — a clean waning crescent.
    mx = cx + int(r * 0.62)
    my = cy - int(r * 0.56)
    mr = int(r * 0.34)
    pygame.draw.circle(surf, col, (mx, my), mr)
    pygame.draw.circle(surf, _SH, (mx + int(mr * 0.55), my - int(mr * 0.30)),
                       int(mr * 0.92))


def _glyph_same_time_tomorrow(surf, cx, cy, r, col):
    # A repeat/loop arrow wound around a round CLOCK — déjà-vu of the exact same
    # clock-minute on two days. Same loop as groundhog, but here it rings a clock
    # dial (not a pillar), and there is no moon (unlike three_am).
    rr = int(r * 0.46)
    w = max(3, int(r * 0.10))
    _clock_face(surf, cx, cy, rr, col, w)
    hw = max(3, int(r * 0.10))
    # generic pose (~10:10) so the hands don't mimic three_am's 3 o'clock.
    pygame.draw.line(surf, col, (cx, cy),
                     (cx - int(rr * 0.56), cy - int(rr * 0.44)), hw)
    pygame.draw.line(surf, col, (cx, cy),
                     (cx + int(rr * 0.30), cy - int(rr * 0.68)), hw)
    _loop_arrow(surf, cx, cy, int(r * 0.82), col, max(4, int(r * 0.15)))


def _glyph_snake_bit(surf, cx, cy, r, col):
    # A coiled snake reared up on an S-body with a flicking forked tongue — the
    # genie's viper that keeps sinking its fangs in. Built as a chain of discs
    # along an S-curve for a smooth round-capped tube, so it reads unmistakably as
    # a SNAKE (never a bottle or skull).
    tube = max(4, int(r * 0.11))
    n = 22
    top_y = cy - int(r * 0.58)
    bot_y = cy + int(r * 0.82)
    amp = r * 0.52
    path = []
    for i in range(n + 1):
        t = i / n
        y = top_y + int(t * (bot_y - top_y))
        x = cx + int(math.sin(t * 2 * math.pi) * amp)
        path.append((x, y))
    # taper: fat neck near the head, thin at the tail tip.
    for i, (x, y) in enumerate(path):
        t = i / n
        rad = int(tube * (1.9 - 1.2 * t))
        pygame.draw.circle(surf, col, (x, y), max(2, rad))
    # Head: a rounded wedge at the top of the S, canted so the snout faces up.
    hx, hy = path[0]
    head_r = int(r * 0.26)
    pygame.draw.circle(surf, col, (hx, hy), head_r)
    # snout jutting up-left toward the tongue
    pygame.draw.polygon(surf, col, [
        (hx - int(head_r * 0.2), hy - int(head_r * 0.4)),
        (hx - int(r * 0.20), hy - int(r * 0.34)),
        (hx + int(head_r * 0.5), hy - int(head_r * 0.1)),
    ])
    # slit eye (recessed) so the head reads as a face, not a knob.
    pygame.draw.circle(surf, _SH, (hx + int(head_r * 0.28), hy - int(head_r * 0.18)),
                       max(2, int(r * 0.06)))
    # Forked tongue flicking out of the snout — the bite.
    tx, ty = hx - int(r * 0.20), hy - int(r * 0.34)
    tw = max(2, int(r * 0.06))
    pygame.draw.line(surf, col, (hx - int(head_r * 0.1), hy - int(head_r * 0.2)),
                     (tx, ty), tw)
    for sgn in (-1, 1):
        pygame.draw.line(surf, col, (tx, ty),
                         (tx - int(r * 0.14), ty - int(r * 0.10) * sgn), tw)


def _glyph_lightning_magnet(surf, cx, cy, r, col):
    # A horseshoe magnet with its poles turned UP, catching a barrage of lightning
    # bolts raining down from a small storm cloud — "you attract strikes." The
    # poles-up magnet + MANY bolts is the mirror of magnet_life (poles down, one
    # coin) and beats a lone bolt by showing the magnet doing the pulling.
    mcx = cx
    mcy = cy + int(r * 0.30)
    rr = int(r * 0.46)
    leg_w = max(6, int(r * 0.28))
    bar = max(6, int(r * 0.30))
    # Curved yoke at the BOTTOM (opening upward): lower semicircle arc.
    arc_rect = pygame.Rect(mcx - rr, mcy - rr, rr * 2, rr * 2)
    pygame.draw.arc(surf, col, arc_rect, math.radians(186), math.radians(354), bar)
    # Two legs rising to the poles.
    leg_h = int(r * 0.52)
    leg_top = mcy - leg_h
    for sgn in (-1, 1):
        lx = mcx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, col, (lx, leg_top, leg_w, leg_h))
    # Pole-tip bands (accent on unlock) capping the mouths that face the storm.
    tip_h = max(4, int(r * 0.18))
    for sgn, tip in ((-1, ai._accent((212, 64, 56))), (1, ai._accent((224, 228, 240)))):
        lx = mcx + sgn * rr - leg_w // 2
        pygame.draw.rect(surf, tip, (lx, leg_top - tip_h, leg_w, tip_h))
    # Small storm cloud riding across the top.
    cloud_y = cy - int(r * 0.66)
    for lx, lr in ((-0.34, 0.30), (0.06, 0.38), (0.42, 0.28)):
        pygame.draw.circle(surf, col, (cx + int(lx * r), cloud_y), int(lr * r))
    pygame.draw.rect(surf, col, (cx - int(r * 0.44), cloud_y,
                                 int(r * 0.90), int(r * 0.24)),
                     border_radius=max(2, int(r * 0.10)))
    # THREE bolts stabbing down out of the cloud into the magnet's poles/mouth —
    # the "many strikes" that make this a magnet, not a single hit.
    def bolt(bx, by, h, s):
        pts = [
            (bx, by),
            (bx - int(s * r * 0.10), by + h * 0.42),
            (bx + int(s * r * 0.02), by + h * 0.42),
            (bx - int(s * r * 0.06), by + h),
            (bx + int(s * r * 0.14), by + h * 0.34),
            (bx + int(s * r * 0.02), by + h * 0.34),
        ]
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts])

    top = cloud_y + int(r * 0.16)
    bolt(cx - int(r * 0.30), top, int(r * 0.44), 1.0)
    bolt(cx + int(r * 0.02), top, int(r * 0.50), 1.1)
    bolt(cx + int(r * 0.34), top, int(r * 0.44), 1.0)


GLYPHS = {
    "ninety_nine": _glyph_ninety_nine,
    "groundhog_day": _glyph_groundhog_day,
    "stat_impossible": _glyph_stat_impossible,
    "three_am": _glyph_three_am,
    "same_time_tomorrow": _glyph_same_time_tomorrow,
    "snake_bit": _glyph_snake_bit,
    "lightning_magnet": _glyph_lightning_magnet,
}
