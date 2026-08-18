"""Stall SIGN theme: CANDY DENTIL MARQUEE (sign only — items stay mix-C).

The showman marquee re-cut as a cornice: a two-tier plinth board carrying a
DENTIL RAIL of candy-striped teeth along its top course. Dentils are the
tooth-blocks of a classical bedmould, and here their pitch is stolen wholesale
from the awning's stripe grid below, so the sign reads as the SAME building's
trim rather than a plaque hung on it. The awning grid is asymmetric about the
hut's centre and is deliberately left that way — phase-locking to the stripes
matters more than a mirrored board, so the end teeth come out unequal.

Two reads carry the rail at 1x: one continuous reveal line under the whole
course (per-tooth drop shadows dissolve at the downscale) and one bulb per
tooth GAP, so the lights are the negative space of the candy rhythm and never
depend on where the label's glyphs land.

Exploration-only: install() binds the chosen mix-C item hooks, then swaps in
THIS sign; game/ is never edited.
"""
import pygame

import game.store_hub as sh
import tools.stall_variant_mixed as mixed
from game.store_hub import (
    m, font, lerp_color, vgrad, gradient_text, capped_glow,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT,
    WOOD_EDGE, LABEL_KEY, AWN_RED, AWN_CREAM_D,
)

# The earlier (96,30,28) field is retired: it put GOLD_A_BOT at 2.26:1, under
# the 2.3 ink floor. This pair keeps the darkest ink stop legal at the board's
# lightest row and still sits well under the thatch it lies on.
CD_TOP = (86, 32, 26)
CD_BOT = (50, 24, 16)
# Pulled most of the way to GOLD: at 0.18 the glass sat at 0.83 luma, so the
# rail's lights out-shone the lit hero once the halo piled on top. The item has
# to stay the brightest thing in the stall by a visible margin, not a hair.
BULB_GLASS = lerp_color(GOLD_PALE, GOLD, 0.45)
REVEAL = (40, 22, 14)
# Cream teeth are 1.09:1 against lit thatch, so their edge — not their fill —
# is the silhouette. Red is only 2.5:1, so it takes the same keyline.
TOOTH_KEY = (74, 22, 24)

# Shared awning grid, authored in logical px. Phased a HALF pitch off the stripe
# boundaries: a tooth now caps the MIDDLE of a stripe (so it can take that
# stripe's own colour and the candy reads as one continuous run of cloth up into
# the trim) and every bulb sits on a boundary. Asymmetric by construction —
# never centre it; the end reveals come out unequal and that is the phase-lock.
GRID_0 = -26.75
PITCH = 12.5
BULB_U = (-33.0, -20.5, -8.0, 4.5, 17.0, 29.5)

HALF_HI, HALF_LO = 44.0, 40.0
STEP_H = 8.0
RAIL_TOP_H, BODY_TOP_H, BODY_BOT_H = 16.0, 13.5, 3.0
CAP_TOP_H, CAP_BOT_H = 12.25, 4.5
BEAD_IN = 2.0
TOOTH_HALF = 3.125


def _plinth_pts(X, Y, half_hi, half_lo, top_h, bot_h, step_h):
    """Two-tier silhouette: a wide upper slab overhanging a narrower base, so
    the extra mass lands as shoulders on the SIDES. A comb of notches along the
    bottom would compete with the dentils and shred at the downscale."""
    return [
        (X(-half_lo), Y(bot_h)), (X(-half_lo), Y(step_h)),
        (X(-half_hi), Y(step_h)), (X(-half_hi), Y(top_h)),
        (X(half_hi), Y(top_h)), (X(half_hi), Y(step_h)),
        (X(half_lo), Y(step_h)), (X(half_lo), Y(bot_h)),
    ]


def _edges(surf, X, Y, ew, col):
    """The silhouette drawn as INWARD rects on the two-tier outline — the one
    dark ring the board's read against lit thatch depends on."""
    yt, yb, ys = Y(RAIL_TOP_H), Y(BODY_BOT_H), Y(STEP_H)
    xl2, xr2, xl1, xr1 = X(-HALF_HI), X(HALF_HI), X(-HALF_LO), X(HALF_LO)
    r = lambda *a: pygame.draw.rect(surf, col, a)
    r(xl2, yt, xr2 - xl2, ew)
    r(xl1, yb - ew, xr1 - xl1, ew)
    r(xl2, yt, ew, ys - yt)
    r(xr2 - ew, yt, ew, ys - yt)
    r(xl1, ys, ew, yb - ys)
    r(xr1 - ew, ys, ew, yb - ys)
    r(xl2, ys - ew, xl1 - xl2, ew)
    r(xr1, ys - ew, xr2 - xr1, ew)


def _stripe_col(cx, scale, x):
    """The colour of the awning stripe the given device column actually lands
    on, recomputed from the hut's own stripe maths. Tooth colour is READ from
    the cloth rather than alternated on the loop index: the stripe count is
    floor-divided per hut, so index parity flips between the 0.92 and 0.96
    stalls and a hardcoded alternation would put a red tooth over cream cloth
    on some of them."""
    half_w = int(m(58) * scale)
    stripe_w = max(m(8), int((half_w * 2) / 9))
    s = (x - (cx - half_w)) // stripe_w
    return AWN_RED if s % 2 == 0 else AWN_CREAM_D


def _teeth(X, cx, scale):
    """Candy teeth centred on the stripe midpoints, every one the SAME width.
    Built outward from the snapped centre instead of from two independently
    snapped edges: the edge-first form lost a device px to rounding wherever a
    tooth straddled cx, which showed up as one narrow tooth per stall. Nothing
    is walked past the board any more, so no stub and no clipped corner tooth —
    the unequal end reveals that fall out are the grid's asymmetry, showing."""
    tw = max(2, int(round(TOOTH_HALF * m(1) * scale)) * 2)
    out = []
    for k in range(-1, 6):
        u = GRID_0 + PITCH * k
        x0 = X(u) - tw // 2
        x1 = x0 + tw
        if x0 < X(-HALF_HI) or x1 > X(HALF_HI):
            continue
        out.append((x0, x1, _stripe_col(cx, scale, (x0 + x1) // 2)))
    return out


def _sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    sv = lambda v: int(m(v) * scale)
    # Every feature lands on the 2-device-px cell that becomes ONE final pixel.
    # Unsnapped, a tooth or an edge straddles two target pixels and the
    # downscale averages half its contrast away — fatal for a rail this small.
    cell = lambda p: p - (p & 1)
    X = lambda u: cell(cx + sv(u))
    Y = lambda h: cell(body_top - sv(h))

    slab = _plinth_pts(X, Y, HALF_HI, HALF_LO, RAIL_TOP_H, BODY_BOT_H, STEP_H)
    off = max(1, int(m(1.5) * scale))

    # one light (low sun, upper-left) => the board's own shadow falls down-right
    # onto the thatch, which is what lifts it off the roof.
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 90),
                        [(x + off, y + off) for x, y in slab])
    surf.blit(shadow, (0, 0))

    x0, y0 = X(-HALF_HI), Y(RAIL_TOP_H)
    bw, bh = X(HALF_HI) - x0, Y(BODY_BOT_H) - y0
    body = vgrad(bw, bh, 0, CD_TOP, CD_BOT)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - x0, y - y0) for x, y in slab])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))

    # every structural line is authored ONE FINAL-TARGET pixel wide (2 device px
    # at SS=2) and drawn INWARD. pygame's polygon width straddles the path, so
    # it would both halve the edge's contrast and push the board's shadow below
    # the seam floor.
    ew = max(2, int(round(m(1.0) * scale)))
    _edges(surf, X, Y, ew, WOOD_EDGE)

    rail_top, rail_bot = Y(RAIL_TOP_H), Y(BODY_TOP_H)
    for tx0, tx1, col in _teeth(X, cx, scale):
        pygame.draw.rect(surf, col, (tx0, rail_top, tx1 - tx0,
                                     rail_bot - rail_top))
        pygame.draw.rect(surf, TOOTH_KEY, (tx0, rail_top, tx1 - tx0, ew))

    # ONE continuous reveal under the whole course. Per-tooth shadows average
    # away at 1x; a single unbroken dark line survives and doubles as the rail's
    # silhouette against the board.
    pygame.draw.rect(surf, REVEAL,
                     (X(-HALF_HI), rail_bot, X(HALF_HI) - X(-HALF_HI), ew))

    # centred between the bead's own runs, not on the board — the cap-height ink
    # is a hair taller than the cap, so it is the FRAME that has to look centred.
    f = font(11 * scale)
    tr = gradient_text(surf, label, f, (cx, (Y(CAP_TOP_H) + Y(CAP_BOT_H)) // 2),
                       GOLD_A_TOP, GOLD_A_BOT, weight=m(1.0 * scale),
                       keyline=LABEL_KEY, kw=m(1.0), shadow=False,
                       tracking=m(0.6))

    cap = _plinth_pts(X, Y, HALF_HI - BEAD_IN, HALF_LO - BEAD_IN,
                      CAP_TOP_H, CAP_BOT_H, STEP_H + BEAD_IN)
    # the bead is decoration; it may never eat into the structural edge, so it
    # is fenced inside the outline rather than trusted to clear it at every scale
    fence = pygame.Rect(X(-HALF_HI) + ew, Y(RAIL_TOP_H) + ew,
                        X(HALF_HI) - X(-HALF_HI) - ew * 2,
                        Y(BODY_BOT_H) - Y(RAIL_TOP_H) - ew * 2)
    prev = surf.get_clip()
    # CORNER BRACKETS, not a closed frame: the cap-height ink overshoots the
    # cap, so the continuous top and bottom runs were crossing the glyphs and
    # both lines lost. Clipping the same outline to the two END MARGINS keeps
    # the corners (which is all the eye needs to read an enclosure) and hands
    # the ink rows back to the type — the type itself is not moved or resized.
    pad = ew + m(1)
    for mx0, mx1 in ((fence.left, tr.left - pad), (tr.right + pad, fence.right)):
        band = pygame.Rect(mx0, fence.top, mx1 - mx0, fence.height).clip(fence)
        if band.w <= 0:
            continue
        surf.set_clip(band)
        pygame.draw.polygon(surf, GOLD_DEEP, cap, max(1, m(0.5)))
    surf.set_clip(prev)

    # Exactly six bulbs, one per tooth gap — the lights read as the rhythm's
    # negative space, so they never collide with a glyph and the count is fixed
    # whatever the label says.
    r = max(2, int(round(m(1.25) * scale)))
    # authored on the course's own mid-line (h=14.75), then re-centred on the
    # mid-line of its OPEN interior: the keyline claims the top row, so an
    # un-recentred bulb clips lop-sided against it.
    top_in = rail_top + ew
    by = top_in + (rail_bot - top_in) // 2
    # bulbs live wholly INSIDE the course: a halo spilling onto the thatch would
    # wash out the very edge the silhouette gate depends on, and a seat poking
    # past the top line would hand that edge a low-contrast gold pixel.
    prev = surf.get_clip()
    surf.set_clip(pygame.Rect(x0, top_in, bw, rail_bot - top_in))
    pad = m(6)
    glow = pygame.Surface((bw + pad * 2, (rail_bot - rail_top) + pad * 2),
                          pygame.SRCALPHA)
    for u in BULB_U:
        capped_glow(glow, X(u) - x0 + pad, by - rail_top + pad,
                    max(2, int(m(4) * scale)), GOLD, 16)
    surf.blit(glow, (x0 - pad, rail_top - pad))

    # the GOLD_DEEP seat IS the rim at this size: the base's inner rim ring is a
    # whole pixel of a 2px-radius disc, so drawing it leaves no lit core at all
    # and the bulb reads as a dull washer instead of a light. Dimmed glass makes
    # the seat load-bearing — bulb-against-cream-tooth is only ~1.15:1, so the
    # dark collar is the entire separation, and the small stalls get a device px
    # more of it or the downscale eats one flank and the bulb runs into a tooth.
    seat = r + max(1, ew // 2) + (0 if scale >= 0.95 else 1)
    for u in BULB_U:
        bx = X(u)
        pygame.draw.circle(surf, GOLD_DEEP, (bx, by), seat)
        pygame.draw.circle(surf, BULB_GLASS, (bx, by), r)
    surf.set_clip(prev)


def install():
    mixed.install()
    sh.STALL_SIGN_HOOK = _sign
