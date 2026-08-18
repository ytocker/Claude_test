"""Stall SIGN theme: BOLT-ROLL LACQUER BOARD (awning family).

The board is read as the stall's awning caught mid-roll: an oxblood lacquer
plank whose cloth is bolted to the TOP edge only and rolled up onto a real
timber bar, with a two-device-row band of unrolled selvedge still showing
below the plank. The bar is the signature — a shaded cylinder with red
whipping bands and radius-matched cream end caps, silhouette carried by a
dark reveal along its outer arc rather than by the cream, which is far too
close in value to lit thatch to hold an edge.

Value hierarchy is authored downward from the item, not upward from the sign:
the roll crown is the sign's one bright, the caps sit a step under it, and the
cream is pulled off pure so the whole board stays subordinate to the goods in
the opening.

Bulbs come OFF the ornament and onto the field as one lamp per end, so
lighting never depends on the label's width and the type band stays clear.

Exploration-only: install() layers this sign over the chosen mix-C item hooks;
game/ is never edited.
"""
import math

import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, lerp_color, lerp_stops, vgrad, gradient_text, capped_glow,
    _glyph_base, _stamp_bold,
    GOLD, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT, LABEL_KEY,
    AWN_RED, AWN_CREAM, AWN_CREAM_D,
)

# Lacquer field: dark enough that gold ink and lit thatch both separate from it.
OX_TOP = (88, 26, 28)
OX_BOT = (52, 16, 18)
OX_KEY = (46, 14, 16)
# The roll's outer arc, NOT the cream, is the silhouette pixel against thatch.
ROLL_REVEAL = (74, 22, 24)
ROLL_LO = (168, 150, 124)
# The glass is deliberately kept under the roll crown's value: a paler bulb
# stole the sign's brightest pixel from the ornament and the board read as two
# gold dots. The halo, not the disc, is what sells the lamp.
BULB_GLASS = GOLD

# Board metrics in logical px: x as ±offset from cx, h as height above the
# awning seam. The seam is a hard floor just under h=1 and the roof rake caps
# the board's width, so every number here is authored against those two limits.
PLANK_HALF = 42.0
PLANK_TOP, PLANK_BOT = 14.4, 3.2
SELVEDGE_FLOOR = 1.05
ROLL_AXIS_H = 16.4
ROLL_R = 2.5
# The cap matches the bar's radius, so the pair reads as one capsule rather
# than a rod pushed through two beads; the one-radius overhang past the tube
# end is what makes the bar look like a real turned dowel with proud ends.
KNOB_X, KNOB_R = 42.5, 2.5
WHIP_X, WHIP_HALF = 36.0, 1.0
BULB_X = 37.6
BULB_HS = (8.8,)
BULB_R = 2.6
# Type is authored at TYPE_PT and steps DOWN per stall until the longest label
# still leaves the lamps their clear air — the lamp is the fixed part.
TYPE_PT, TYPE_PT_MIN, TYPE_CLEAR = 10.4, 8.6, 3.5

# The sign's cream is pulled well OFF pure awning cream. Measured against the
# goods in the opening, a full-value crown put the sign's brightest pixel at
# 0.93 of the item's on COSTUMES — the board was winning the stall. Held here,
# every stall's sign peak sits at 0.76-0.84 of its item's.
ROLL_CREAM = lerp_color(AWN_CREAM, AWN_CREAM_D, 0.70)
# The caps take a further step down, past the awning's shadow cream toward the
# tube's underside: an end face is turned off the upper-left key, and a cap that
# holds plateau value beats the crown on the downscale (its dome carries a whole
# 2x2 block of peak) so the sign reads as two dots with a bar between them.
KNOB_CREAM = lerp_color(ROLL_CREAM, ROLL_LO, 0.62)

# Cylinder ramp sampled across the bar's diameter; the upper-left keeps the
# cream and everything below it rolls off to the shadowed underside. The cream
# plateau runs deep (0.44) because a shorter one put the ramp's knee inside the
# lit face and left a dull patch part-way along the bar.
ROLL_STOPS = [(0.0, ROLL_CREAM), (0.44, ROLL_CREAM), (0.62, AWN_CREAM_D),
              (1.0, ROLL_LO)]
# The cap's ramp keeps the tube's SHAPE (same knee, same quarter-of-the-drop at
# it) but rides lower throughout; reusing the tube's literal mid stop would put
# a tone brighter than the cap's own plateau into its shadow side and hang a
# bright ring round the bottom of the dome.
KNOB_STOPS = [(0.0, KNOB_CREAM), (0.44, KNOB_CREAM),
              (0.62, lerp_color(KNOB_CREAM, ROLL_LO, 0.25)), (1.0, ROLL_LO)]
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
        kx = 0.10 * max(0.0, min(1.0, (xx - x0) / span))
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


def _knob(surf, kx, ky, r, u, outward):
    """A turned end cap on the bar: a cream hemisphere keyed upper-left, its
    dark keyline run as an ARC over the outer/upper face only. A full ring drew
    a hard seam exactly where the cap meets the tube and cut the bar into three
    parked objects; leaving the inboard ~160 degrees un-keyed lets the cap's
    cream run straight into the cylinder's, so the whole thing reads as one
    turned dowel while the outer face still owns a hard edge over the rake."""
    ir = int(math.ceil(r)) + 1
    w = ir * 2 + 1
    ball = pygame.Surface((w, w), pygame.SRCALPHA)
    lx, ly, lz = -0.58, -0.58, 0.57
    edge = 1.0 - max(1.0, 1.0 * u) / r
    # The kept arc is centred slightly ABOVE the outward horizontal so it hands
    # off to the tube's own top reveal instead of ending in mid-air.
    a_c = math.radians(20.0 if outward > 0 else 160.0)
    half = math.radians(100.0)
    for iy in range(w):
        for ix in range(w):
            dx = (ix + 0.5 - ir) / r
            dy = (iy + 0.5 - ir) / r
            rr = math.hypot(dx, dy)
            if rr >= 1.06:
                continue
            nz = math.sqrt(max(0.0, 1.0 - min(1.0, rr * rr)))
            lam = max(0.0, dx * lx + dy * ly + nz * lz)
            col = lerp_stops(KNOB_STOPS, max(0.0, min(1.0, 1.0 - lam * 1.15)))
            if rr >= edge:
                da = math.atan2(-dy, dx) - a_c
                da = abs((da + math.pi) % (2 * math.pi) - math.pi)
                if da <= half:
                    col = OX_KEY
            cov = max(0.0, min(1.0, (1.0 - rr) * r + 0.5))
            ball.set_at((ix, iy), (*col, int(255 * cov)))
    surf.blit(ball, (int(round(kx)) - ir, int(round(ky)) - ir))


def _sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    u = m(1.0) * scale                      # device px per authored logical px
    X = lambda v: cx + v * u
    Y = lambda hh: body_top - hh * u
    kl = max(1, int(round(1.0 * u)))

    # ── lacquer plank ────────────────────────────────────────────────────────
    # The selvedge is snapped to whole 2-device-row blocks from the plank's
    # bottom DOWN: the downscale samples in 2x2 blocks, so a band authored in
    # fractional rows lands as cream-tinted mud instead of one clean cream
    # screen row over one clean dark one, which is the whole point of it.
    sel_top = int(round(Y(PLANK_BOT)))
    sel_top += sel_top & 1
    key_top = sel_top + 2
    sel_end = key_top + 2
    x0, x1 = int(round(X(-PLANK_HALF))), int(round(X(PLANK_HALF)))
    p_top = int(round(Y(PLANK_TOP)))
    p_rect = pygame.Rect(x0, p_top, x1 - x0, sel_top - p_top)
    surf.blit(vgrad(p_rect.w, p_rect.h, 0, OX_TOP, OX_BOT), p_rect.topleft)
    pygame.draw.rect(surf, OX_KEY, p_rect, width=kl)

    # ── type ─────────────────────────────────────────────────────────────────
    # Centred on the CAP band, not on the font's padded box: the glyph surface
    # carries descender air the all-caps label never uses, and a plank this
    # shallow shows the error immediately. The bolded cap measures ~8.2 logical
    # px at this size against an 11.2 plank, so the band is hung on the plank's
    # own middle and the 1px rims absorb the last fifth of a pixel each. The cap
    # is deliberately held near 72% of the field: at 83% the counters closed and
    # the ink touched both rims, which is what made the board look shouty.
    #
    # Width is fitted, not assumed: the LAMP is the fixed part of this sign (its
    # whole reason for living on the field is that lighting must not vary with
    # the label), so the longest word steps down a half point at a time until it
    # leaves the bulb its clear air — which is what a sign painter does anyway.
    r = max(1, int(round(BULB_R * u)))
    seat = max(1, int(round(1.0 * u)))
    free = (X(BULB_X) - (r + seat)) - cx - m(TYPE_CLEAR)
    pt = TYPE_PT
    while True:
        f = font(pt * scale)
        base = _stamp_bold(_glyph_base(label, f, m(0.6)), m(1.0 * scale))
        ink = base.get_bounding_rect()
        if ink.w * 0.5 + m(1.0) <= free or pt <= TYPE_PT_MIN:
            break
        pt -= 0.2
    band_c = Y((PLANK_TOP + PLANK_BOT) * 0.5)
    cy = band_c + (base.get_height() * 0.5 - ink.centery)
    # The ramp's bottom stop is lifted off pure GOLD_A_BOT: the descending edge
    # of a 6px cap on near-black lacquer is where contrast actually fails, and
    # unlifted it fell under 4.5:1 exactly on the letters' lower halves.
    ink_bot = lerp_color(GOLD_A_BOT, GOLD_A_TOP, 0.30)
    gradient_text(surf, label, f, (cx, int(round(cy))), GOLD_A_TOP, ink_bot,
                  weight=m(1.0 * scale), keyline=LABEL_KEY, kw=m(1.0),
                  shadow=False, tracking=m(0.6))

    # ── end lamps ────────────────────────────────────────────────────────────
    # Lamps live on the FIELD, outboard of the widest label, so the lighting is
    # identical on a seven-letter stall and an eight-letter one. ONE lamp a side,
    # not a column of three: at this size three discs merged into a smear with
    # no dark between them, so the sign paid for six lights and read as two
    # blurs. One bigger bulb with a real halo buys the fairground note honestly.
    pad = m(8)
    gw, gh = (x1 - x0) + pad * 2, (sel_top - p_top) + pad * 2
    glow = pygame.Surface((gw, gh), pygame.SRCALPHA)
    bulbs = [(int(round(X(sgn * BULB_X))), int(round(Y(bh))))
             for bh in BULB_HS for sgn in (-1, 1)]
    for bx, by in bulbs:
        capped_glow(glow, bx - x0 + pad, by - p_top + pad, m(8), GOLD, 70)
    surf.blit(glow, (x0 - pad, p_top - pad))
    for bx, by in bulbs:
        pygame.draw.circle(surf, GOLD_DEEP, (bx, by), r + seat)
        pygame.draw.circle(surf, BULB_GLASS, (bx, by), r)

    # ── cream selvedge, then its closure hairline ────────────────────────────
    # Cloth, so it is laid over the board's lower rim and AFTER the type AND the
    # lamp halo: the keyline stamp reaches a fifth of a px past the plank and
    # the halo washes gold over the rim, either of which would contaminate the
    # one clean cream screen row this band exists to produce.
    pygame.draw.rect(surf, AWN_CREAM_D, (x0, sel_top, x1 - x0, key_top - sel_top))
    pygame.draw.rect(surf, OX_KEY, (x0, key_top, x1 - x0, sel_end - key_top))

    # ── the roll, over the plank's top edge ──────────────────────────────────
    # It overlaps the plank by half a px because cloth rolls OVER a top-bolted
    # edge; leaving a seam there would read as a separate object parked on top.
    # The axis is nudged (<=0.5 device px) so the bar's crown starts on an even
    # device row: that is what lets the reveal land as whole 1x pixels on every
    # stall instead of only on the ones whose scale happens to line up.
    rr = ROLL_R * u
    crown = int(round(Y(ROLL_AXIS_H) - rr))
    y_ax = (crown - (crown & 1)) + rr
    _cylinder(surf, X(-KNOB_X), X(KNOB_X), y_ax, rr, cx, u)
    for sgn in (-1, 1):
        _knob(surf, X(sgn * KNOB_X), y_ax, KNOB_R * u, u, sgn)


def install():
    import tools.stall_variant_mixed as mixed

    mixed.install()
    sh.STALL_SIGN_HOOK = _sign
