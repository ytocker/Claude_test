"""Stall SIGN theme: BUNTING SWAG RIBBON — awning-family sign, one per stall.

Thesis: the stall dressed itself for market day. A fishtail oxblood ribbon board
is tacked flat to the gable, and a single flag garland is strung across the rake
above it. The board is the ONLY thing carrying type; the garland is pure
festival, so the sign reads as decoration-plus-name rather than as a plaque.

Deliberately ONE halyard, not two. A second tier would double the ornament and
start competing with the awning stripes directly below the board — the whole
concept rests on a big quiet oxblood field with one thin ribbon of colour above
it and roughly nine parts air to one part ornament.

Four DEEP flags, not five shallow ones: at stall scale a 1.5u pennant is a
dashed line, not cloth. Pulling the halyard's binding end one grid step inboard
buys rake headroom, a flatter dip frees depth at mid-span, and the depth goes
into fewer, bigger triangles that still clear the board top.

Exploration-only: install() takes the chosen mix-C item/sign binding and then
overrides ONLY the sign hook, so every open stall wears this theme over its own
item presentation. game/ is never edited.
"""
import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, gradient_text, vgrad,
    GOLD_A_TOP, GOLD_A_BOT, WOOD_EDGE, LABEL_KEY,
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
OUTER_HALF = 43.5                   # flared tail corners, still inside the rake
BOARD_LO, BOARD_HI = 1.5, 11.5
NOTCH_RUN = 8.0                     # horizontal depth of the fishtail V per end
CAP_MID = (BOARD_LO + BOARD_HI) * 0.5

# The awning stripe grid, asymmetric about cx exactly as the stall draws it —
# centre-symmetrising the garland would divorce it from the awning below.
GRID = (-33.0, -20.5, -8.0, 4.5, 17.0, 29.5)
ANCHOR_L, ANCHOR_R = GRID[1], GRID[5]
FLAG_B = GRID[1:5]
CORD_END_H = 20.5
CORD_DIP = 2.0
FLAG_W, FLAG_D = 9.5, 4.5
PEG_R = 1.0


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


def _outset(pts, d):
    """Grow a convex polygon by d device px along each EDGE normal, mitring the
    corners. Pushing the vertices out from the centroid instead would thin the
    long top edge to a third of d — at this size the dark key IS the flag's
    shape, so every edge has to carry the same weight. Miters are capped so a
    base corner can't spike across the gap where the cord has to show."""
    n = len(pts)
    cxp = sum(p[0] for p in pts) / n
    cyp = sum(p[1] for p in pts) / n
    lines = []
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        ex, ey = x2 - x1, y2 - y1
        ln = (ex * ex + ey * ey) ** 0.5 or 1.0
        nx, ny = ey / ln, -ex / ln
        if nx * ((x1 + x2) * 0.5 - cxp) + ny * ((y1 + y2) * 0.5 - cyp) < 0:
            nx, ny = -nx, -ny
        lines.append((nx, ny, nx * x1 + ny * y1 + d))

    out = []
    for i in range(n):
        ax, ay, ac = lines[i - 1]
        bx, by, bc = lines[i]
        px, py = pts[i]
        det = ax * by - ay * bx
        if abs(det) < 1e-9:
            out.append((px + bx * d, py + by * d))
            continue
        ix = (ac * by - bc * ay) / det
        iy = (ax * bc - bx * ac) / det
        vx, vy = ix - px, iy - py
        vl = (vx * vx + vy * vy) ** 0.5 or 1.0
        # 1.45d clears the tip's own natural miter (1.38d at this flag's
        # proportions) so the point stays sharp, while the much shallower base
        # corners get trimmed before they can spike across the cord gap.
        cap = d * 1.45
        if vl > cap:
            ix, iy = px + vx / vl * cap, py + vy / vl * cap
        out.append((ix, iy))
    return out


def _garland(layer, cx, body_top, scale):
    """One halyard, four hanging flags. The cord is laid FIRST and the cloth
    folds over it, so the halyard shows only in the gaps — the way bunting is
    actually strung, and the only way the flags keep their full depth."""
    def P(u, h):
        return (cx + _d(u, scale), body_top - _d(h, scale))

    # Two device px is the floor for anything that has to survive the downscale
    # to 360x640: at one px the cord dissolved into the thatch entirely.
    kw = max(2, _sv(1.0, scale))

    pts = []
    steps = 48
    for i in range(steps + 1):
        u = ANCHOR_L + (ANCHOR_R - ANCHOR_L) * i / steps
        pts.append(P(u, _cord_h(u)))
    pygame.draw.lines(layer, WOOD_EDGE, False, pts, kw)

    for i, b in enumerate(FLAG_B):
        left, right = P(b, _cord_h(b)), P(b + FLAG_W, _cord_h(b + FLAG_W))
        tip = P(b + FLAG_W * 0.5, _cord_h(b + FLAG_W * 0.5) - FLAG_D)
        cloth_pts = [left, right, tip]
        top, bot = ((FLAG_RED_TOP, FLAG_RED_BOT) if i % 2 == 0
                    else (FLAG_CREAM_TOP, FLAG_CREAM_BOT))

        pygame.draw.polygon(layer, FLAG_KEY, _outset(cloth_pts, kw))

        xs = [p[0] for p in cloth_pts]
        ys = [p[1] for p in cloth_pts]
        x0, y0 = int(min(xs)), int(min(ys))
        w = max(1, int(max(xs)) - x0 + 2)
        h = max(1, int(max(ys)) - y0 + 2)
        cloth = vgrad(w, h, 0, top, bot)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255),
                            [(x - x0, y - y0) for x, y in cloth_pts])
        cloth.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        layer.blit(cloth, (x0, y0))

    # Pegs are timber tacks, not jewellery: gold is reserved for the label, and
    # a smaller head also keeps the peg clear of the roof mask's rake edge.
    r = max(1, int(round(_d(PEG_R, scale))))
    for u in (ANCHOR_L, ANCHOR_R):
        px, py = P(u, CORD_END_H)
        pygame.draw.circle(layer, WOOD_EDGE, (int(px), int(py)), r)


def _board_points(cx, body_top, scale):
    """Fishtail ribbon silhouette: a flat bar whose ends are notched by a deep V
    to a point at mid-height, with the four tail corners FLARED past the bar's
    own half-width. Splayed tails read as a ribbon under tension; parallel ones
    read as a rectangle with a bite taken out."""
    def P(u, h):
        return (cx + _d(u, scale), body_top - _d(h, scale))

    notch = BOARD_HALF - NOTCH_RUN
    return [P(-OUTER_HALF, BOARD_HI), P(OUTER_HALF, BOARD_HI),
            P(notch, CAP_MID), P(OUTER_HALF, BOARD_LO),
            P(-OUTER_HALF, BOARD_LO), P(-notch, CAP_MID)]


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

    x0 = int(cx - _d(OUTER_HALF, scale))
    y0 = int(body_top - _d(BOARD_HI, scale))
    bw = max(2, int(cx + _d(OUTER_HALF, scale)) - x0 + 1)
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
