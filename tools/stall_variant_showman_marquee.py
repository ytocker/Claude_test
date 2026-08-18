"""Stall-front variant: SHOWMAN MARQUEE (sign + item, a bound pair).

Sign  = a bulb-studded stepped cartouche in deep warm brown, riding the lower
        roof with its own drop shadow — a fairground marquee, not a plaque.
Item  = one hero on a turned-timber baluster pedestal standing in a hard pool
        of light on the stall sill.

The spotlight is sold by the FLOOR, never by a cone: a bright elliptical pool
with a hard contact shadow, two shadowed riser blocks reading as the lower
tiers of a display, and a fast fall-off to STALL_DARK at the opening's edges.
A visible light cone would double the light sources and flatten the hero, so
separation comes from value + rim only.

Exploration-only: install() swaps the two hooks; game/ is never edited.
"""
import math

import pygame

import game.store_hub as sh
from game.store_hub import (
    m, font, lerp_color, vgrad, gradient_text, capped_glow, _glyph_base,
    _group_thumb, _punch_contrast, _rim_light,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT,
    WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE, STALL_DARK, LABEL_KEY,
)

CARTOUCHE_TOP = (66, 40, 22)
CARTOUCHE_BOT = (40, 24, 13)
BULB_SEAT = GOLD_DEEP
# bulbs sit a notch under GOLD_PALE so the sign's peak value can never climb
# above the hero's — the item has to be the brightest thing in the stall.
BULB_GLASS = lerp_color(GOLD_PALE, GOLD, 0.18)
POOL_CORE = lerp_color(WOOD_HI, GOLD_PALE, 0.35)
# colorway seams: the harness swaps these wholesale, the construction never moves
INK_TOP = GOLD_A_TOP
INK_BOT = GOLD_A_BOT
INK_KEY = LABEL_KEY
INK_W = 1.0
PANEL_INSET = None  # (color) draws a recessed name panel inside the frame


# ── sign ─────────────────────────────────────────────────────────────────────
def _cartouche_points(cx, bottom_y, half_c, half_1, half_2, t0, t1, t2):
    """Stepped marquee silhouette: one tall central block whose top steps DOWN
    and OUT twice per side onto a shared flat bottom edge."""
    return [
        (cx - half_2, bottom_y), (cx - half_2, t2), (cx - half_1, t2),
        (cx - half_1, t1), (cx - half_c, t1), (cx - half_c, t0),
        (cx + half_c, t0), (cx + half_c, t1), (cx + half_1, t1),
        (cx + half_1, t2), (cx + half_2, t2), (cx + half_2, bottom_y),
    ]


def _sign(surf, ctx):
    cx, scale, label = ctx["cx"], ctx["scale"], ctx["label"]
    body_top = ctx["body_top"]

    # the awning seam is a hard ceiling for the opening below, so the board is
    # seated a hair above it and never dips onto the stripes.
    bottom_y = body_top - int(m(3) * scale)
    h = int(m(17) * scale)
    step = int(m(4) * scale)
    half_c, half_1, half_2 = (int(m(38) * scale), int(m(41) * scale),
                              int(m(44) * scale))
    t0 = bottom_y - h
    t1, t2 = t0 + step, t0 + step * 2

    pts = _cartouche_points(cx, bottom_y, half_c, half_1, half_2, t0, t1, t2)
    off = max(1, int(m(1.5) * scale))

    # one light (low sun, upper-left) => the board's own shadow falls down-right
    # onto the thatch, which is what lifts it off the roof.
    shadow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shadow, (0, 0, 0, 90),
                        [(x + off, y + off) for x, y in pts])
    surf.blit(shadow, (0, 0))

    x0, y0 = cx - half_2, t0
    bw, bh = half_2 * 2, bottom_y - t0
    body = vgrad(bw, bh, 0, CARTOUCHE_TOP, CARTOUCHE_BOT)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(x - x0, y - y0) for x, y in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))

    pygame.draw.polygon(surf, WOOD_EDGE, pts, max(1, int(m(1.2) * scale)))

    d = max(1, int(m(2) * scale))
    bead = _cartouche_points(cx, bottom_y - d, half_c - d, half_1 - d,
                             half_2 - d, t0 + d, t1 + d, t2 + d)
    pygame.draw.polygon(surf, GOLD_DEEP, bead, max(1, m(0.5)))

    if PANEL_INSET is not None:
        pr = pygame.Rect(cx - half_c + d * 2, t0 + d * 2,
                         (half_c - d * 2) * 2, (bottom_y - d) - (t0 + d * 2))
        pygame.draw.rect(surf, PANEL_INSET, pr,
                         border_radius=max(2, int(m(2) * scale)))
        pygame.draw.rect(surf, GOLD_DEEP, pr, max(1, m(0.5)),
                         border_radius=max(2, int(m(2) * scale)))

    f = font(11 * scale)
    gradient_text(surf, label, f, (cx, t0 + int(h * 0.56)),
                  INK_TOP, INK_BOT, weight=m(INK_W * scale),
                  keyline=INK_KEY, kw=m(1.0), shadow=False, tracking=m(0.6))

    # exactly six bulbs, each a discrete disc on its own seat — a fairy-light
    # dusting of 1px points would only read as noise after the downscale.
    r = max(2, int(round(m(1.5) * scale)))
    seat = max(1, m(0.8))
    pad = m(8)
    glow = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    bulbs = []
    for k in (12, 28, 42):
        for sgn in (-1, 1):
            bx = cx + sgn * int(m(k) * scale)
            ax = abs(bx - cx)
            by = t0 if ax <= half_c else (t1 if ax <= half_1 else t2)
            bulbs.append((bx, by))
    for bx, by in bulbs:
        capped_glow(glow, bx - x0 + pad, by - y0 + pad, m(5), GOLD, 30)
    surf.blit(glow, (x0 - pad, y0 - pad))
    for bx, by in bulbs:
        pygame.draw.circle(surf, BULB_SEAT, (bx, by), r + seat)
        pygame.draw.circle(surf, BULB_GLASS, (bx, by), r)
        pygame.draw.circle(surf, lerp_color(BULB_GLASS, WOOD_EDGE, 0.35),
                           (bx, by), r, 1)


# ── item ─────────────────────────────────────────────────────────────────────
def _light_pool(surf, cx, bottom_y, w, h):
    """The spotlight itself, read as a POOL on the floor: a warm elliptical
    ramp alpha-feathered to nothing at its rim. No cone, no beam."""
    pool = pygame.Surface((w, h), pygame.SRCALPHA)
    hw, hh = w / 2.0, h / 2.0
    for py in range(h):
        dy = (py + 0.5 - hh) / hh
        for px in range(w):
            dx = (px + 0.5 - hw) / hw
            rr = math.sqrt(dx * dx + dy * dy)
            if rr >= 1.0:
                continue
            k = (1.0 - rr)
            col = lerp_color(WOOD_MID, POOL_CORE, min(1.0, k ** 0.75))
            pool.set_at((px, py), (*col, int(255 * k ** 0.85)))
    surf.blit(pool, (cx - w // 2, bottom_y - h))


def _riser(surf, cx, bottom_y, w, h, inner_sign):
    """A lower display tier: a block sunk in shadow whose upper-left edges catch
    only the pool's spill, brightest at the end nearest the hero."""
    rect = pygame.Rect(cx - w // 2, bottom_y - h, w, h)
    surf.blit(vgrad(rect.w, rect.h, 0,
                    lerp_color(WOOD_LO, STALL_DARK, 0.45), STALL_DARK),
              rect.topleft)
    lip = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for px in range(rect.w):
        t = px / max(1, rect.w - 1)
        near = t if inner_sign < 0 else 1.0 - t
        a = int(150 * near ** 1.8)
        if a > 0:
            lip.set_at((px, 0), (*lerp_color(WOOD_MID, GOLD_PALE, 0.2), a))
    # the lit vertical is the LEFT one on BOTH risers — the sun sits upper-left,
    # and lighting each block's pool-facing edge would invent a second source.
    for py in range(rect.h):
        a = int(110 * (1 - py / max(1, rect.h)))
        if a > 0:
            lip.set_at((0, py), (*lerp_color(WOOD_MID, GOLD_PALE, 0.2), a))
    surf.blit(lip, rect.topleft)
    pygame.draw.line(surf, WOOD_EDGE, (rect.left, rect.bottom - 1),
                     (rect.right - 1, rect.bottom - 1), 1)


def _pedestal(surf, cx, base_y, scale):
    """A turned baluster cut to the three elements that survive the 1x
    downscale: foot disc, short tapered shaft carrying the single gold bead,
    top plate. Every upper-left curve takes WOOD_HI and every lower-right one
    WOOD_EDGE so the turning still reads."""
    total = int(m(4.7) * scale)
    ys = [base_y - int(round(total * f / 10.0))
          for f in (0.0, 2.5, 7.5, 10.0)]
    hi, lo = WOOD_HI, WOOD_EDGE

    def band(y_bot, y_top, w_bot, w_top, ellipse=False):
        y_top = min(y_top, y_bot - 1)
        rect = pygame.Rect(cx - max(w_bot, w_top) // 2, y_top,
                           max(2, max(w_bot, w_top)), y_bot - y_top)
        if ellipse:
            pygame.draw.ellipse(surf, WOOD_LO, rect)
            pygame.draw.arc(surf, hi, rect, math.radians(95), math.radians(185),
                            max(1, m(0.6)))
            pygame.draw.arc(surf, lo, rect, math.radians(275), math.radians(360),
                            max(1, m(0.6)))
        else:
            pts = [(cx - w_bot // 2, y_bot), (cx - w_top // 2, y_top),
                   (cx + w_top // 2, y_top), (cx + w_bot // 2, y_bot)]
            pygame.draw.polygon(surf, WOOD_LO, pts)
            pygame.draw.line(surf, hi, pts[0], pts[1], max(1, m(0.6)))
            pygame.draw.line(surf, lo, pts[2], pts[3], max(1, m(0.6)))
        return rect

    w = lambda v: max(2, int(m(v) * scale))
    band(ys[0], ys[1], w(18), w(18), ellipse=True)
    shaft = band(ys[1], ys[2], w(9), w(7))
    plate = band(ys[2], ys[3], w(20), w(20))
    pygame.draw.line(surf, hi, plate.topleft, (plate.right - 1, plate.top),
                     max(1, m(0.6)))
    pygame.draw.line(surf, lo, (plate.left, plate.bottom - 1),
                     (plate.right - 1, plate.bottom - 1), max(1, m(0.6)))
    bead = max(1, int(round(m(0.7) * scale)))
    bcx = cx - max(1, int(m(2) * scale))
    pygame.draw.circle(surf, GOLD_DEEP, (bcx, shaft.centery), bead + 1)
    pygame.draw.circle(surf, GOLD_PALE, (bcx, shaft.centery), bead)
    return ys[3]


def _item(surf, ctx):
    cx, deck_y, scale, group = ctx["cx"], ctx["deck_y"], ctx["scale"], ctx["group"]
    body_top, half_w = ctx["body_top"], ctx["half_w"]

    sill_y = deck_y - m(8)                      # deck lip: hard floor
    hem_y = body_top + int(m(15) * scale)       # awning hem: hard ceiling
    open_l, open_r = cx - half_w + m(8), cx + half_w - m(8)
    prev_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(open_l, hem_y, open_r - open_l, sill_y - hem_y))

    # hard vignette: past the light pool the interior drops to STALL_DARK so
    # the eye is squeezed back onto the lit hero instead of wandering the sill.
    half_open = (open_r - open_l) // 2
    knee = int(m(39) * scale)
    vig = pygame.Surface((open_r - open_l, sill_y - hem_y), pygame.SRCALPHA)
    for px in range(vig.get_width()):
        t = (abs(open_l + px - cx) - knee) / max(1, half_open - knee)
        a = int(210 * max(0.0, min(1.0, t)) ** 1.1)
        if a > 0:
            pygame.draw.line(vig, (*STALL_DARK, a), (px, 0),
                             (px, vig.get_height()))
    surf.blit(vig, (open_l, hem_y))

    pool_w, pool_h = int(m(46) * scale), max(3, int(m(7) * scale))
    _light_pool(surf, cx, sill_y, pool_w, pool_h)
    capped_glow(surf, cx, sill_y - pool_h // 2, int(m(16) * scale), GOLD, 22)

    # the pedestal stands one pixel BEHIND the deck lip, which is what buys the
    # contact shadow room to read instead of being cut off by the sill.
    base_y = sill_y - max(1, m(1))
    sh_w, sh_h = int(m(18) * scale), max(2, int(m(3) * scale))
    csh = pygame.Surface((sh_w, sh_h), pygame.SRCALPHA)
    pygame.draw.ellipse(csh, (12, 8, 6, 120), csh.get_rect())
    surf.blit(csh, (cx - sh_w // 2 + m(1.5), base_y - sh_h + m(1)))

    plate_y = _pedestal(surf, cx, base_y, scale)

    src, _lb = _group_thumb(group)
    iw, ih = src.get_size()
    # contain to the envelope, then give height priority to the awning hem so a
    # tall skin loses a pixel rather than tucking under the stripes.
    box = int(m(40) * scale)
    s = box / max(iw, ih)
    head_room = plate_y - (hem_y + m(1))
    if ih * s > head_room:
        s = head_room / ih
    img = pygame.transform.smoothscale(
        src, (max(1, int(iw * s)), max(1, int(ih * s))))
    img = _punch_contrast(img)
    r = img.get_rect(midbottom=(cx, plate_y))
    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(_rim_light(img, color=(255, 224, 150), alpha=165),
              r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)

    surf.set_clip(prev_clip)


def install():
    sh.STALL_SIGN_HOOK = _sign
    sh.STALL_ITEM_HOOK = _item
