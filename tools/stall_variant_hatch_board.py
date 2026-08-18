"""HATCH BOARD — stall sign/item concept: the propped-open shutter.

The hut's front hatch is hinged under the awning and propped forward-and-down
on two timber struts. The category name rides the board's SHADED UNDERSIDE;
the merchandise STANDS on a full-width timber sill across the deck lip; a
single shaft of golden-hour sun falls between the two and separates them.

Why the name lives on a downward-facing plane: it makes the sign legitimately
the darkest object in the frame, so gold type on near-black wood wins the
hierarchy by physics rather than by out-glowing the item. The item is then the
only lit thing in the opening and reads first at a squint.

Exploration module — installs into the store_hub hook seam, never edits it.
"""
import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, vgrad, lerp_color, capped_glow, gradient_text,
    _punch_contrast, _rim_light, _group_thumb,
    WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE,
    AWN_RED, AWN_RED_D, AWN_CREAM, AWN_CREAM_D,
    GOLD, GOLD_PALE, GOLD_A_TOP, GOLD_A_BOT, LABEL_KEY,
)


# The board is a plane facing DOWN and away from a low upper-left sun, so both
# stops sit below the body's own value — dark at the hinge (buried under the
# awning), a shade open at the front edge (nearer, catching sky bounce).
BOARD_HINGE = (30, 19, 10)
BOARD_FRONT = (52, 34, 18)
KRAFT = (150, 118, 78)
CLOTH = (176, 76, 66)


def _geom(ctx):
    """Every measurement the two hooks share, so the sign and the item can be
    authored against ONE set of edges (hard walls = the m(8) posts + deck lip)."""
    s = ctx["scale"]
    cx, deck_y, body_top = ctx["cx"], ctx["deck_y"], ctx["body_top"]
    g = dict(
        s=s, cx=cx, deck_y=deck_y, body_top=body_top,
        # hard walls
        in_half=ctx["half_w"] - m(8),
        sill_top=deck_y - m(8),
        # hatch board
        y_hinge=body_top + int(m(9) * s),
        y_front=body_top + int(m(20) * s),
        top_half=int(m(84) * s) // 2,
        front_half=int(m(96) * s) // 2,
        y_text=body_top + int(m(15.5) * s),
        y_prop_foot=body_top + int(m(31) * s),
        x_prop_head=int(m(44) * s),
        # merchandise
        item_base=deck_y - m(7),
        box=int(m(38) * s),
        dress_dx=int(m(32) * s),
    )
    return g


# =============================================================================
# ITEM — sill counter, sun shaft, plinth, hero.
# =============================================================================
def _board_cast_shadow(surf, g):
    """The hatch throws its shadow DOWN-RIGHT onto the back wall — the one cue
    that seats the board in front of the interior instead of painted on it."""
    h = int(m(7) * g["s"])
    off = int(m(3) * g["s"])
    x0 = max(g["cx"] - g["in_half"], g["cx"] - g["front_half"] + off)
    x1 = min(g["cx"] + g["in_half"], g["cx"] + g["front_half"] + off)
    band = pygame.Surface((max(1, x1 - x0), h), pygame.SRCALPHA)
    for y in range(h):
        a = int(96 * (1 - y / h) ** 1.5)
        pygame.draw.line(band, (0, 0, 0, a), (0, y), (band.get_width(), y))
    surf.blit(band, (x0, g["y_front"]))


def _sill(surf, g):
    """A full-width market counter across the deck lip: the plane the goods
    stand ON, so the item has a floor instead of floating in the opening."""
    x0 = g["cx"] - g["in_half"]
    w = g["in_half"] * 2
    top = g["sill_top"]
    h = (g["deck_y"] + m(2)) - top
    x1 = x0 + w - 1
    surf.blit(vgrad(w, h, 0, WOOD_HI, WOOD_LO), (x0, top))
    for k in range(1, 4):
        sy = top + h * k // 4
        pygame.draw.line(surf, lerp_color(WOOD_LO, WOOD_EDGE, 0.35),
                         (x0, sy), (x1, sy), max(1, m(0.7)))
    pygame.draw.line(surf, WOOD_EDGE, (x0, top + h - m(1)),
                     (x1, top + h - m(1)), max(1, m(1.4)))
    pygame.draw.line(surf, lerp_color(WOOD_HI, GOLD_PALE, 0.35),
                     (x0, top), (x1, top), max(1, m(1)))


def _dressing(surf, g):
    """Market slack-filler for the 2.9:1 sill: folded goods left, a price
    pennant + crate lip right. Deliberately capped below the hero's shoulder and
    knocked ~28% down in value — these read as DEPTH, never as competition."""
    s, top = g["s"], g["sill_top"]
    pad = m(20)
    lay = pygame.Surface((g["in_half"] * 2 + pad * 2, m(40)), pygame.SRCALPHA)
    ox, oy = g["cx"] - g["in_half"] - pad, top - m(30)

    def L(x, y):
        return (x - ox, y - oy)

    lx = g["cx"] - g["dress_dx"]
    bw, bh = int(m(15) * s), int(m(4.5) * s)
    tw, th = int(m(12) * s), int(m(4) * s)
    # authored a lane ABOVE their final value, because the whole cluster then
    # takes a flat 28% knock-down — pitched any darker they silhouette into the
    # unlit back wall and stop reading as goods at all.
    fold_lo = lerp_color(KRAFT, WOOD_HI, 0.30)
    def block(r, base):
        """Lit top-left edge, dark bottom-right edge — the one sun, and cheaper
        in pixels than a full keyline on forms this small."""
        lay.blit(vgrad(r.w, r.h, 0, lerp_color(base, WOOD_HI, 0.30), base), r)
        k = max(1, m(0.6))
        pygame.draw.line(lay, lerp_color(base, WOOD_HI, 0.70),
                         (r.x, r.y), (r.right - 1, r.y), k)
        pygame.draw.line(lay, WOOD_EDGE, (r.x, r.bottom - 1),
                         (r.right - 1, r.bottom - 1), k)
        pygame.draw.line(lay, WOOD_EDGE, (r.right - 1, r.y),
                         (r.right - 1, r.bottom - 1), k)

    for rw, rh, ry, base in ((bw, bh, top - bh, fold_lo),
                             (tw, th, top - bh - th, KRAFT)):
        block(pygame.Rect(*L(lx - rw // 2, ry), rw, rh), base)

    rx = g["cx"] + g["dress_dx"]
    cw, chh = int(m(16) * s), int(m(6) * s)
    cr = pygame.Rect(*L(rx - cw // 2, top - chh), cw, chh)
    block(cr, lerp_color(WOOD_MID, WOOD_HI, 0.20))
    pygame.draw.line(lay, WOOD_LO, (cr.x + m(1), cr.bottom - m(2)),
                     (cr.right - m(2), cr.y + m(1)), max(1, m(0.6)))

    pole_h = int(m(10) * s)
    px = rx - cw // 2 + int(m(2) * s)
    pygame.draw.line(lay, WOOD_EDGE, L(px, top - chh),
                     L(px, top - chh - pole_h), max(1, m(1.2)))
    fw, fh = int(m(9) * s), int(m(5) * s)
    ftop = top - chh - pole_h + int(m(1) * s)
    pygame.draw.polygon(lay, CLOTH, [L(px, ftop), L(px + fw, ftop + fh // 2),
                                     L(px, ftop + fh)])
    pygame.draw.polygon(lay, lerp_color(CLOTH, WOOD_EDGE, 0.45),
                        [L(px, ftop), L(px + fw, ftop + fh // 2),
                         L(px, ftop + fh)], max(1, m(0.7)))

    lay.fill((183, 183, 183, 255), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lay, (ox, oy))


def _sun_shaft(surf, g):
    """ONE shaft, matching the one light: it enters at the board's left front
    corner and lands on the sill between the folded goods and the hero, so the
    gap that separates sign from item is a lit gap, not an empty one."""
    s = g["s"]
    y0, y1 = g["y_front"], g["sill_top"]
    if y1 - y0 < 4:
        return
    x0a = g["cx"] - g["front_half"]
    x0b = x0a + int(m(8) * s)
    x1a = g["cx"] - int(m(21) * s)
    x1b = g["cx"] - int(m(14) * s)
    fe = max(2, m(3))
    xmin = min(x0a, x1a) - fe
    xmax = max(x0b, x1b) + fe
    h = y1 - y0
    beam = pygame.Surface((xmax - xmin + 1, h), pygame.SRCALPHA)
    for iy in range(h):
        t = iy / max(1, h - 1)
        a0 = 34.0 * (1.0 - t)
        if a0 <= 0:
            continue
        xa = x0a + (x1a - x0a) * t - fe
        xb = x0b + (x1b - x0b) * t + fe
        for ix in range(int(xa), int(xb) + 1):
            d = min(ix - xa, xb - ix)
            k = min(1.0, d / (2 * fe))
            a = int(a0 * k)
            if a > 0:
                beam.set_at((ix - xmin, iy), (*GOLD_PALE, a))
    surf.blit(beam, (xmin, y0))

    pool_rx, pool_ry = int(m(5.5) * s), int(m(2) * s)
    pc = ((x1a + x1b) // 2, y1 + m(1))
    pool = pygame.Surface((pool_rx * 2 + 2, pool_ry * 2 + 2), pygame.SRCALPHA)
    for i in range(6, 0, -1):
        a = int(44 * (1 - (i - 1) / 6) ** 1.6)
        pygame.draw.ellipse(pool, (*GOLD_PALE, a),
                            (pool_rx - pool_rx * i // 6,
                             pool_ry - pool_ry * i // 6,
                             2 * pool_rx * i // 6, 2 * pool_ry * i // 6))
    surf.blit(pool, (pc[0] - pool_rx, pc[1] - pool_ry))


def _plinth(surf, g, iw):
    """A 3px riser so the hero stands PROUD of the counter clutter rather than
    sharing its baseline."""
    s = g["s"]
    ph = m(3)
    pw = iw + int(m(7) * s)
    r = pygame.Rect(g["cx"] - pw // 2, g["item_base"], pw, ph + m(1))
    surf.blit(vgrad(r.w, r.h, 0, lerp_color(WOOD_MID, WOOD_HI, 0.25), WOOD_LO),
              r.topleft)
    pygame.draw.rect(surf, WOOD_EDGE, r, width=max(1, m(0.8)))


def _item_hook(surf, ctx):
    g = _geom(ctx)
    _board_cast_shadow(surf, g)
    _sill(surf, g)
    _dressing(surf, g)
    _sun_shaft(surf, g)

    src, _lb = _group_thumb(ctx["group"])
    w, h = src.get_size()
    sc = g["box"] / max(w, h)
    # the board owns the top of the opening; the hero is contained into what is
    # LEFT, never pushed under it.
    room = (g["item_base"] - g["y_front"]) - m(2)
    if h * sc > room:
        sc = room / h
    img = pygame.transform.smoothscale(
        src, (max(1, int(w * sc)), max(1, int(h * sc))))
    img = _punch_contrast(img)
    r = img.get_rect(midbottom=(g["cx"], g["item_base"]))

    _plinth(surf, g, r.w)
    capped_glow(surf, r.centerx, r.centery, int(m(24) * g["s"]), GOLD, 30,
                layers=9)
    sh_off = m(3)
    cast = img.copy()
    cast.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    cast.set_alpha(130)
    surf.blit(cast, (r.x + sh_off, r.y + sh_off))
    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


# =============================================================================
# SIGN — the propped hatch board.
# =============================================================================
def _props(surf, g):
    """Two struts from the board's front corners back-down to the post inner
    faces: the reason the board hangs where it does, drawn thin so they stay
    corner furniture."""
    peg = max(1, m(1.4))
    for sgn in (-1, 1):
        a = (g["cx"] + sgn * g["x_prop_head"], g["y_front"])
        # the foot lands TANGENT to the post's inner face, never on it — the
        # posts are a hard wall this concept is not allowed to redraw.
        b = (g["cx"] + sgn * (g["in_half"] - peg), g["y_prop_foot"])
        pygame.draw.line(surf, WOOD_EDGE, a, b, max(1, m(1.5)))
        pygame.draw.line(surf, lerp_color(WOOD_MID, WOOD_HI, 0.25),
                         (a[0], a[1] - m(1)), (b[0], b[1] - m(1)),
                         max(1, m(0.8)))
        pygame.draw.circle(surf, WOOD_EDGE, b, peg)


def _board(surf, g):
    """The hatch: a FAKED wedge — wider at the front edge than at the hinge so
    it reads as tilted toward the viewer, while the face itself is never sheared
    so the type stays dead level and legible."""
    y0, y1 = g["y_hinge"], g["y_front"]
    th, fh = g["top_half"], g["front_half"]
    cx = g["cx"]
    pts = [(cx - th, y0), (cx + th, y0), (cx + fh, y1), (cx - fh, y1)]
    w, h = fh * 2, y1 - y0
    face = vgrad(w, h, 0, BOARD_HINGE, BOARD_FRONT)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - (cx - fh), y - y0) for x, y in pts])
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(face, (cx - fh, y0))
    pygame.draw.polygon(surf, WOOD_EDGE, pts, max(1, m(1.2)))
    # the lit chamfer rides ON the front lip, above the dark outline — sitting it
    # any higher walks it into the type's baseline on a face this shallow.
    ch = max(1, m(1))
    pygame.draw.line(surf, lerp_color(WOOD_HI, GOLD_PALE, 0.25),
                     (cx - fh + m(2), y1 - ch), (cx + fh - m(2), y1 - ch),
                     max(1, m(1)))


def _hem_overlay(surf, ctx, g):
    """Re-lay the awning's scalloped hem over the board's top strip so the hinge
    reads as TUCKED UNDER the canopy. Pixel-identical to the architecture's own
    awning pass, so nothing about the hut changes — only the stacking order of
    the new board against it."""
    cx, half_w = ctx["cx"], ctx["half_w"]
    awn_y = ctx["body_top"]
    awn_h = int(m(15) * g["s"])
    stripe_w = max(m(8), int((half_w * 2) / 9))
    awn = pygame.Surface((half_w * 2, awn_h), pygame.SRCALPHA)
    n_str = int((half_w * 2) // stripe_w) + 1
    for s in range(n_str):
        c_top = AWN_RED if s % 2 == 0 else AWN_CREAM
        c_bot = AWN_RED_D if s % 2 == 0 else AWN_CREAM_D
        awn.blit(vgrad(stripe_w, awn_h, 0, c_top, c_bot), (s * stripe_w, 0))
    mask = pygame.Surface((half_w * 2, awn_h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    for s in range(n_str + 1):
        pygame.draw.circle(mask, (0, 0, 0, 0), (s * stripe_w, awn_h),
                           stripe_w // 2)
    awn.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(awn, (cx - half_w, awn_y))
    pygame.draw.line(surf, (0, 0, 0, 120), (cx - half_w, awn_y),
                     (cx + half_w, awn_y), max(1, m(1)))


def _sign_hook(surf, ctx):
    g = _geom(ctx)
    _props(surf, g)
    _board(surf, g)
    _hem_overlay(surf, ctx, g)
    f = font(11 * g["s"])
    gradient_text(surf, ctx["label"], f, (g["cx"], g["y_text"]),
                  GOLD_A_TOP, GOLD_A_BOT, weight=m(1.0 * g["s"]),
                  keyline=LABEL_KEY, kw=m(1.0), shadow=False, tracking=m(0.6))


def install():
    sh.STALL_SIGN_HOOK = _sign_hook
    sh.STALL_ITEM_HOOK = _item_hook
