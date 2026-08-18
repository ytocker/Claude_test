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
# One notch under GOLD_PALE so the sign's peak value can never climb above the
# lit hero's — the item has to stay the brightest thing in the stall.
BULB_GLASS = lerp_color(GOLD_PALE, GOLD, 0.18)
REVEAL = (40, 22, 14)
# Cream teeth are 1.09:1 against lit thatch, so their edge — not their fill —
# is the silhouette. Red is only 2.5:1, so it takes the same keyline.
TOOTH_KEY = (74, 22, 24)

# Shared awning grid, authored in logical px: stripe boundaries and the gap
# midpoints between them. Asymmetric by construction — never centre it.
GRID_0 = -33.0
PITCH = 12.5
BULB_U = (-26.75, -14.25, -1.75, 10.75, 23.25, 35.75)

HALF_HI, HALF_LO = 44.0, 40.0
STEP_H = 8.0
RAIL_TOP_H, BODY_TOP_H, BODY_BOT_H = 16.0, 13.5, 3.0
CAP_TOP_H, CAP_BOT_H = 12.25, 4.25
BEAD_IN = 2.0
TOOTH_HALF = 3.125
BULB_H = 14.75


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


def _teeth(X):
    """Candy teeth on the awning's own boundaries, walked one pitch PAST the
    board on each side and clipped to the edge — the two stubs that fall out
    are unequal because the grid is, and forcing them equal would break the
    phase-lock with the stripes below."""
    out = []
    for k in range(-1, 7):
        u = GRID_0 + PITCH * k
        lo = max(-HALF_HI, u - TOOTH_HALF)
        hi = min(HALF_HI, u + TOOTH_HALF)
        if hi - lo <= 0.5:
            continue
        x0, x1 = X(lo), X(hi)
        if x1 - x0 < 1:
            continue
        col = AWN_RED if k % 2 == 0 else AWN_CREAM_D
        out.append((x0, x1, col, lo <= -HALF_HI, hi >= HALF_HI))
    return out


def _sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    sv = lambda v: int(m(v) * scale)
    X = lambda u: cx + sv(u)
    Y = lambda h: body_top - sv(h)

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
    # at SS=2). A single device px would land as a half-covered pixel after the
    # downscale and lose ~half its contrast against the thatch.
    ew = max(2, int(round(m(1.0) * scale)))
    pygame.draw.polygon(surf, WOOD_EDGE, slab, ew)

    rail_top, rail_bot = Y(RAIL_TOP_H), Y(BODY_TOP_H)
    for tx0, tx1, col, at_l, at_r in _teeth(X):
        pygame.draw.rect(surf, col, (tx0, rail_top, tx1 - tx0,
                                     rail_bot - rail_top))
        pygame.draw.line(surf, TOOTH_KEY, (tx0, rail_top), (tx1 - 1, rail_top),
                         ew)
        if at_l:
            pygame.draw.line(surf, TOOTH_KEY, (tx0, rail_top),
                             (tx0, rail_bot - 1), ew)
        if at_r:
            pygame.draw.line(surf, TOOTH_KEY, (tx1 - 1, rail_top),
                             (tx1 - 1, rail_bot - 1), ew)

    # ONE continuous reveal under the whole course. Per-tooth shadows average
    # away at 1x; a single unbroken dark line survives and doubles as the rail's
    # silhouette against the board.
    pygame.draw.line(surf, REVEAL, (X(-HALF_HI), rail_bot),
                     (X(HALF_HI) - 1, rail_bot), ew)

    cap = _plinth_pts(X, Y, HALF_HI - BEAD_IN, HALF_LO - BEAD_IN,
                      CAP_TOP_H, CAP_BOT_H, STEP_H + BEAD_IN)
    pygame.draw.polygon(surf, GOLD_DEEP, cap, max(1, m(0.5)))

    f = font(11 * scale)
    gradient_text(surf, label, f, (cx, Y((CAP_TOP_H + CAP_BOT_H) * 0.5) + ew),
                  GOLD_A_TOP, GOLD_A_BOT, weight=m(1.0 * scale),
                  keyline=LABEL_KEY, kw=m(1.0), shadow=False, tracking=m(0.6))

    # Exactly six bulbs, one per tooth gap — the lights read as the rhythm's
    # negative space, so they never collide with a glyph and the count is fixed
    # whatever the label says.
    r = max(2, int(round(m(1.25) * scale)))
    by = Y(BULB_H)
    # bulbs live wholly INSIDE the course: a halo spilling onto the thatch would
    # wash out the very edge the silhouette gate depends on, and a seat poking
    # past the top line would hand that edge a low-contrast gold pixel.
    prev = surf.get_clip()
    surf.set_clip(pygame.Rect(x0, rail_top + ew, bw, rail_bot - rail_top - ew))
    pad = m(6)
    glow = pygame.Surface((bw + pad * 2, (rail_bot - rail_top) + pad * 2),
                          pygame.SRCALPHA)
    for u in BULB_U:
        capped_glow(glow, X(u) - x0 + pad, by - rail_top + pad,
                    max(2, int(m(4) * scale)), GOLD, 30)
    surf.blit(glow, (x0 - pad, rail_top - pad))

    for u in BULB_U:
        bx = X(u)
        pygame.draw.circle(surf, GOLD_DEEP, (bx, by), r + max(1, ew))
        pygame.draw.circle(surf, BULB_GLASS, (bx, by), r)
        pygame.draw.circle(surf, lerp_color(BULB_GLASS, WOOD_EDGE, 0.35),
                           (bx, by), r, 1)
    surf.set_clip(prev)


def install():
    mixed.install()
    sh.STALL_SIGN_HOOK = _sign
