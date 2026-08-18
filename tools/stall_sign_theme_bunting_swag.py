"""Stall SIGN theme: BUNTING SWAG RIBBON — awning-family sign, one per stall.

Thesis: the stall dressed itself for market day. A fishtail oxblood ribbon board
is tacked flat to the gable, and a single flag garland is strung across the rake
above it. The board is the ONLY thing carrying type; the garland is pure
festival, so the sign reads as decoration-plus-name rather than as a plaque.

Deliberately ONE halyard, not two. A second tier would double the ornament and
start competing with the awning stripes directly below the board — the whole
concept rests on a big quiet oxblood field with one thin ribbon of colour above
it and roughly nine parts air to one part ornament.

Exploration-only: install() takes the chosen mix-C item/sign binding and then
overrides ONLY the sign hook, so every open stall wears this theme over its own
item presentation. game/ is never edited.
"""
import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, gradient_text, vgrad,
    GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT, WOOD_EDGE, LABEL_KEY,
    AWN_RED_D, AWN_CREAM, AWN_CREAM_D,
)

# Oxblood field: sits a full step under the awning's AWN_RED_D so the board can
# never be mistaken for a piece of the awning it hangs above.
OX_TOP = (88, 26, 28)
OX_BOT = (52, 16, 18)
OX_KEY = (46, 14, 16)

# Flag keyline is a warmer, lighter red than the board's — the garland has to
# separate from the THATCH, the board from the SKY, and one ink can't do both.
FLAG_KEY = (74, 22, 24)
FLAG_RED_TOP, FLAG_RED_BOT = AWN_RED_D, (110, 26, 30)
FLAG_CREAM_TOP, FLAG_CREAM_BOT = AWN_CREAM, AWN_CREAM_D

INK_TOP, INK_BOT, INK_KEY = GOLD_A_TOP, GOLD_A_BOT, LABEL_KEY

# ── shared awning-theme frame (logical px; h counts UP from body_top) ─────────
BOARD_HALF = 42.0
BOARD_LO, BOARD_HI = 1.5, 11.5
NOTCH_RUN = 4.0                     # horizontal depth of the fishtail V per end
CAP_MID = (BOARD_LO + BOARD_HI) * 0.5

# The awning stripe grid, asymmetric about cx exactly as the stall draws it —
# centre-symmetrising the garland would divorce it from the awning below.
GRID = (-33.0, -20.5, -8.0, 4.5, 17.0, 29.5)
ANCHOR_L, ANCHOR_R = GRID[0], GRID[5]
CORD_END_H = 20.0
CORD_DIP = 4.0
FLAG_W, FLAG_D = 8.0, 1.5
PEG_R = 1.5


def _d(v, scale):
    """Logical px -> device px, UNROUNDED. The catenary and the flag tips are
    sub-logical-px moves; rounding them per-point stair-steps the whole swag."""
    return v * sh.SS * scale


def _sv(v, scale):
    """Logical px -> device px for structural widths, which must land on whole
    device pixels or the downscale eats a 1px keyline entirely."""
    return int(m(v) * scale)


def _cord_h(u):
    """Halyard height at horizontal offset u: a parabola pinned to both pegs and
    sagging CORD_DIP at mid-span."""
    mid = (ANCHOR_L + ANCHOR_R) * 0.5
    half = (ANCHOR_R - ANCHOR_L) * 0.5
    t = (u - mid) / half
    return (CORD_END_H - CORD_DIP) + CORD_DIP * t * t


def _roof_mask(ctx):
    """The thatch triangle, as the stall itself lays it out. The garland is
    PEGGED into the rake, so no part of it may float off the roof into the sky —
    the outer peg sits within half a pixel of the rake line by construction."""
    cx, body_top = ctx["cx"], ctx["body_top"]
    half_w, eave = ctx["half_w"], ctx["eave"]
    return [(cx - half_w - eave, body_top), (cx + half_w + eave, body_top),
            (cx, ctx["roof_apex_y"])]


def _garland(layer, cx, body_top, scale):
    """One halyard, five hanging flags. Flags are laid first and the cord runs
    over their heads, so the cord reads as a single unbroken run that the cloth
    is stitched to rather than as five separate strings."""
    def P(u, h):
        return (cx + _d(u, scale), body_top - _d(h, scale))

    key1 = max(1, _sv(1.0, scale))
    key2 = max(key1 + 1, _sv(1.5, scale))

    for i, b in enumerate(GRID[:5]):
        left, right = P(b, _cord_h(b)), P(b + FLAG_W, _cord_h(b + FLAG_W))
        tip = P(b + FLAG_W * 0.5, _cord_h(b + FLAG_W * 0.5) - FLAG_D)
        top, bot = ((FLAG_RED_TOP, FLAG_RED_BOT) if i % 2 == 0
                    else (FLAG_CREAM_TOP, FLAG_CREAM_BOT))

        xs = [p[0] for p in (left, right, tip)]
        ys = [p[1] for p in (left, right, tip)]
        x0, y0 = int(min(xs)), int(min(ys))
        w = max(1, int(max(xs)) - x0 + 1)
        h = max(1, int(max(ys)) - y0 + 1)
        cloth = vgrad(w, h, 0, top, bot)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255),
                            [(x - x0, y - y0) for x, y in (left, right, tip)])
        cloth.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        layer.blit(cloth, (x0, y0))

        pygame.draw.polygon(layer, FLAG_KEY, [left, right, tip], key1)
        # the down-right run takes the heavier line: one low key from the upper
        # left, and at this depth the doubled edge IS the flag's shape cue.
        pygame.draw.line(layer, FLAG_KEY, right, tip, key2)

    pts = []
    steps = 48
    for i in range(steps + 1):
        u = ANCHOR_L + (ANCHOR_R - ANCHOR_L) * i / steps
        pts.append(P(u, _cord_h(u)))
    pygame.draw.lines(layer, WOOD_EDGE, False, pts, key1)

    r = max(1, int(round(_d(PEG_R, scale))))
    for u in (ANCHOR_L, ANCHOR_R):
        px, py = P(u, CORD_END_H)
        pygame.draw.circle(layer, GOLD_DEEP, (int(px), int(py)), r)
        pygame.draw.circle(layer, WOOD_EDGE, (int(px), int(py)), r, 1)


def _board_points(cx, body_top, scale):
    """Fishtail ribbon silhouette: a flat bar whose ends are notched by a V that
    runs NOTCH_RUN inward to a point at mid-height, leaving two tails per end."""
    def P(u, h):
        return (cx + _d(u, scale), body_top - _d(h, scale))

    return [P(-BOARD_HALF, BOARD_HI), P(BOARD_HALF, BOARD_HI),
            P(BOARD_HALF - NOTCH_RUN, CAP_MID), P(BOARD_HALF, BOARD_LO),
            P(-BOARD_HALF, BOARD_LO), P(-BOARD_HALF + NOTCH_RUN, CAP_MID)]


def _sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    _garland(layer, cx, body_top, scale)
    keep = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(keep, (255, 255, 255, 255), _roof_mask(ctx))
    layer.blit(keep, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))

    pts = _board_points(cx, body_top, scale)
    off = max(1, _sv(1.5, scale))
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 90),
                        [(x + off, y + off) for x, y in pts])
    surf.blit(shadow, (0, 0))

    x0 = int(cx - _d(BOARD_HALF, scale))
    y0 = int(body_top - _d(BOARD_HI, scale))
    bw = max(2, int(cx + _d(BOARD_HALF, scale)) - x0 + 1)
    bh = max(2, int(body_top - _d(BOARD_LO, scale)) - y0 + 1)
    body = vgrad(bw, bh, 0, OX_TOP, OX_BOT)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - x0, y - y0) for x, y in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))

    pygame.draw.polygon(surf, OX_KEY, pts, max(1, _sv(1.0, scale)))

    gradient_text(surf, label, font(11 * scale),
                  (int(cx), int(body_top - _d(CAP_MID, scale))),
                  INK_TOP, INK_BOT, weight=m(1.0 * scale),
                  keyline=INK_KEY, kw=m(1.0), shadow=False, tracking=m(0.6))


def install():
    import tools.stall_variant_mixed as mixed

    mixed.install()
    sh.STALL_SIGN_HOOK = _sign
