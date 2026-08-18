"""Stall SIGN theme: BOLT-ROLL LACQUER BOARD (awning family).

The board is read as the stall's awning caught mid-roll: an oxblood lacquer
plank whose cloth is bolted to the TOP edge only and rolled up onto a real
timber bar, with the last 1.5px of unrolled selvedge still showing below the
plank. The bar is the signature — a shaded cylinder with red whipping bands
and proud cream end knobs, silhouette carried by a dark reveal along its
outer arc rather than by the cream, which is far too close in value to lit
thatch to hold an edge.

Bulbs come OFF the ornament and onto the field as two three-lamp end columns,
so lighting never depends on the label's width and the type band stays clear.

Exploration-only: install() layers this sign over the chosen mix-C item hooks;
game/ is never edited.
"""
import math

import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, lerp_color, lerp_stops, vgrad, gradient_text, capped_glow,
    _glyph_base, _stamp_bold,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT, LABEL_KEY,
    AWN_RED, AWN_CREAM, AWN_CREAM_D,
)

# Lacquer field: dark enough that gold ink and lit thatch both separate from it.
OX_TOP = (88, 26, 28)
OX_BOT = (52, 16, 18)
OX_KEY = (46, 14, 16)
# The roll's outer arc, NOT the cream, is the silhouette pixel against thatch.
ROLL_REVEAL = (74, 22, 24)
ROLL_LO = (168, 150, 124)
BULB_GLASS = lerp_color(GOLD_PALE, GOLD, 0.18)

# Board metrics in logical px: x as ±offset from cx, h as height above the
# awning seam. The seam is a hard floor at h=1.5 and the roof rake caps the
# board's width, so every number here is authored against those two limits.
PLANK_HALF = 42.0
PLANK_TOP, PLANK_BOT = 13.5, 3.0
CAP_TOP, CAP_BOT = 11.75, 3.75
SELVEDGE_FLOOR = 1.5
ROLL_AXIS_H = 15.5
ROLL_R = 2.5
KNOB_X, KNOB_R = 42.5, 3.0
WHIP_X, WHIP_HALF = 38.0, 1.0
BULB_X = 37.5
BULB_HS = (5.0, 8.0, 11.0)
BULB_R = 1.4

# Cylinder ramp sampled across the bar's diameter; the upper-left third keeps
# the cream and everything below it rolls off to the shadowed underside.
ROLL_STOPS = [(0.0, AWN_CREAM), (0.30, AWN_CREAM), (0.62, AWN_CREAM_D),
              (1.0, ROLL_LO)]
WHIP_STOPS = [(0.0, AWN_RED), (0.30, AWN_RED), (0.62, (150, 30, 32)),
              (1.0, (96, 20, 22))]


def _cylinder(surf, x0, x1, y_ax, r, cx, u):
    """The bar as a true horizontal cylinder: value is a function of the
    vertical position across the diameter (its only real curvature), with a
    slight lengthwise fall-off so the single upper-left key still reads along
    the bar. Edge coverage is analytic so the tube keeps a round profile
    through the downscale."""
    x_lo, x_hi = int(math.floor(x0)), int(math.ceil(x1))
    y_lo, y_hi = int(math.floor(y_ax - r)) - 1, int(math.ceil(y_ax + r)) + 1
    w, h = x_hi - x_lo, y_hi - y_lo
    tube = pygame.Surface((w, h), pygame.SRCALPHA)
    # The outer-arc reveal is the bar's only silhouette against lit thatch, so
    # it is counted in whole device rows and padded to the next even one: a
    # 1px line straddling the downscale's 2-row block averages into the cream
    # and the bar loses its edge on exactly the stalls whose parity is odd.
    rev_r0 = int(round(y_ax - r))
    rev_r1 = rev_r0 + 2 + (rev_r0 & 1)
    span = max(1.0, x1 - x0)
    for ix in range(w):
        xx = x_lo + ix + 0.5
        if xx < x0 or xx > x1:
            continue
        whip = min(abs(xx - (cx - WHIP_X * u)),
                   abs(xx - (cx + WHIP_X * u))) <= WHIP_HALF * u
        stops = WHIP_STOPS if whip else ROLL_STOPS
        kx = 0.16 * max(0.0, min(1.0, (xx - x0) / span))
        for iy in range(h):
            yy = y_lo + iy + 0.5
            d = yy - y_ax
            cov = max(0.0, min(1.0, r - abs(d) + 0.5))
            if cov <= 0.0:
                continue
            t = max(0.0, min(1.0, (d / r + 1.0) * 0.5))
            if y_lo + iy < rev_r1:
                col = ROLL_REVEAL
            else:
                col = lerp_stops(stops, min(1.0, t + kx))
            tube.set_at((ix, iy), (*col, int(255 * cov)))
    surf.blit(tube, (x_lo, y_lo))


def _knob(surf, kx, ky, r, u):
    """A turned end cap on the bar: a cream sphere keyed upper-left, ringed by
    the plank's own dark keyline so the proudest part of the sign still owns a
    hard edge wherever it crosses the roof rake."""
    ir = int(math.ceil(r)) + 1
    w = ir * 2 + 1
    ball = pygame.Surface((w, w), pygame.SRCALPHA)
    lx, ly, lz = -0.58, -0.58, 0.57
    for iy in range(w):
        for ix in range(w):
            dx = (ix + 0.5 - ir) / r
            dy = (iy + 0.5 - ir) / r
            rr = math.hypot(dx, dy)
            if rr >= 1.06:
                continue
            nz = math.sqrt(max(0.0, 1.0 - min(1.0, rr * rr)))
            lam = max(0.0, dx * lx + dy * ly + nz * lz)
            col = lerp_stops(ROLL_STOPS, max(0.0, min(1.0, 1.0 - lam * 1.15)))
            cov = max(0.0, min(1.0, (1.0 - rr) * r + 0.5))
            ball.set_at((ix, iy), (*col, int(255 * cov)))
    surf.blit(ball, (int(round(kx)) - ir, int(round(ky)) - ir))
    pygame.draw.circle(surf, OX_KEY, (int(round(kx)), int(round(ky))),
                       int(round(r)), max(1, int(round(1.0 * u))))


def _sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    u = m(1.0) * scale                      # device px per authored logical px
    X = lambda v: cx + v * u
    Y = lambda hh: body_top - hh * u
    kl = max(1, int(round(1.0 * u)))

    # ── cream selvedge, then its closure hairline ────────────────────────────
    # The last of the unrolled cloth shows below the plank inside the seam
    # clearance. The whole reveal is only ~1.4px once the scene is downscaled,
    # so the closure is SNAPPED to the 2-device-px block the downscale samples:
    # unaligned it averages half-and-half with the cream and the sign's bottom
    # edge dissolves into lit thatch, which is the one edge cream can't hold.
    sel_top = int(round(Y(PLANK_BOT)))
    sel_end = int(math.floor(Y(SELVEDGE_FLOOR)))
    key_top = max(sel_top, (sel_end - 2) & ~1)
    x0, x1 = int(round(X(-PLANK_HALF))), int(round(X(PLANK_HALF)))
    pygame.draw.rect(surf, AWN_CREAM_D, (x0, sel_top, x1 - x0,
                                         max(0, key_top - sel_top)))
    pygame.draw.rect(surf, OX_KEY, (x0, key_top, x1 - x0, sel_end - key_top))

    # ── lacquer plank ────────────────────────────────────────────────────────
    p_top = int(round(Y(PLANK_TOP)))
    p_rect = pygame.Rect(x0, p_top, x1 - x0, sel_top - p_top)
    surf.blit(vgrad(p_rect.w, p_rect.h, 0, OX_TOP, OX_BOT), p_rect.topleft)
    pygame.draw.rect(surf, OX_KEY, p_rect, width=kl)

    # ── type ─────────────────────────────────────────────────────────────────
    # Centred on the CAP band, not on the font's padded box: the glyph surface
    # carries descender air the all-caps label never uses, and a plank this
    # shallow shows the error immediately.
    f = font(11 * scale)
    base = _stamp_bold(_glyph_base(label, f, m(0.6)), m(1.0 * scale))
    ink = base.get_bounding_rect()
    band_c = Y((CAP_TOP + CAP_BOT) * 0.5 + 0.25)
    cy = band_c + (base.get_height() * 0.5 - ink.centery)
    gradient_text(surf, label, f, (cx, int(round(cy))), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0 * scale), keyline=LABEL_KEY, kw=m(1.0),
                  shadow=False, tracking=m(0.6))

    # ── end-lamp columns ─────────────────────────────────────────────────────
    # Lamps live on the FIELD, outboard of the widest label, so the lighting is
    # identical on a seven-letter stall and an eight-letter one.
    r = max(1, int(round(BULB_R * u)))
    seat = max(1, int(round(0.7 * u)))
    pad = m(8)
    gw, gh = (x1 - x0) + pad * 2, (sel_top - p_top) + pad * 2
    glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
    bulbs = [(int(round(X(sgn * BULB_X))), int(round(Y(bh))))
             for bh in BULB_HS for sgn in (-1, 1)]
    for bx, by in bulbs:
        capped_glow(glow, bx - x0 + pad, by - p_top + pad, m(5), GOLD, 30)
    surf.blit(glow, (x0 - pad, p_top - pad))
    for bx, by in bulbs:
        pygame.draw.circle(surf, GOLD_DEEP, (bx, by), r + seat)
        pygame.draw.circle(surf, BULB_GLASS, (bx, by), r)

    # ── the roll, over the plank's top edge ──────────────────────────────────
    # It overlaps the plank by half a px because cloth rolls OVER a top-bolted
    # edge; leaving a seam there would read as a separate object parked on top.
    y_ax = Y(ROLL_AXIS_H)
    _cylinder(surf, X(-KNOB_X), X(KNOB_X), y_ax, ROLL_R * u, cx, u)
    for sgn in (-1, 1):
        _knob(surf, X(sgn * KNOB_X), y_ax, KNOB_R * u, u)


def install():
    import tools.stall_variant_mixed as mixed

    mixed.install()
    sh.STALL_SIGN_HOOK = _sign
