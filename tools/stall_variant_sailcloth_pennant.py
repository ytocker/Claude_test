"""SAILCLOTH PENNANT — stall sign + item concept for the hub market huts.

Thesis: the stall is a WORKING RIG, not a display case. The name hangs from a
bamboo spar as a catenary swallowtail pennant lashed across the gable; the goods
hang below in a lashed rope cradle with a knotted cloth swag behind them. Every
element is load-bearing, so the flanks read as spare capacity (coiled hank, an
empty second sling) rather than as dead air.

Concept module for the design loop only — it installs itself into the
store_hub hook seam and never edits the stall architecture.
"""
import math

import pygame

import game.store_hub as sh
from game.store_hub import (m, font, lerp_color, gradient_text, capped_glow,
                            vgrad, _glyph_base, _group_thumb, _punch_contrast,
                            _rim_light, WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE,
                            AWN_RED, AWN_RED_D, AWN_CREAM, AWN_CREAM_D,
                            GOLD, GOLD_A_TOP, GOLD_A_BOT, LABEL_KEY)

# Hemp lane, derived from the stall's own timber so the rigging never reads as
# a foreign material — cord is bleached wood, not rope-coloured plastic.
ROPE_HI = lerp_color(WOOD_HI, AWN_CREAM, 0.42)
ROPE_MID = lerp_color(WOOD_MID, AWN_CREAM_D, 0.30)
ROPE_LO = lerp_color(WOOD_LO, WOOD_EDGE, 0.35)

# The pennant's own ramp lives one step DOWN from the awning's cream stripes so
# the sign can never out-value the goods it advertises; true AWN_CREAM is spent
# only on a hairline top-edge catch.
CLOTH_HI = AWN_CREAM_D
CLOTH_LO = (186, 166, 138)

SWAG_TOP = (138, 96, 72)
SWAG_BOT = (96, 64, 48)


def _sv(v, scale):
    """Logical px -> device px at a stall's own scale factor."""
    return int(m(v) * scale)


# =============================================================================
# Rigging primitives — one low golden-hour key from the upper left, so every
# cord carries its highlight up-left and its shade down-right.
# =============================================================================
def _rope_run(surf, pts, w, twist=True):
    """A twisted hemp run along a polyline: a shaded core plus alternating
    diagonal ticks so the cord reads as laid strands rather than a drawn line.
    Ticks are authored at SS and dissolve into fibre texture on the downscale."""
    w = max(2, int(w))
    lo = [(x + w * 0.30, y + w * 0.34) for x, y in pts]
    hi = [(x - w * 0.24, y - w * 0.28) for x, y in pts]
    pygame.draw.lines(surf, ROPE_LO, False, lo, w)
    pygame.draw.lines(surf, ROPE_MID, False, pts, w)
    if w >= 3:
        pygame.draw.lines(surf, ROPE_HI, False, hi, max(1, int(w * 0.42)))
    if not twist or w < 3:
        return
    step = max(m(2), int(w * 1.7))
    carry = 0.0
    tick = 0
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg <= 0:
            continue
        ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
        px, py = -uy, ux
        d = carry
        while d < seg:
            cxp, cyp = x0 + ux * d, y0 + uy * d
            col = ROPE_LO if tick % 2 else ROPE_HI
            ax = cxp - ux * w * 0.34 - px * w * 0.44
            ay = cyp - uy * w * 0.34 - py * w * 0.44
            bx = cxp + ux * w * 0.34 + px * w * 0.44
            by = cyp + uy * w * 0.34 + py * w * 0.44
            pygame.draw.line(surf, col, (ax, ay), (bx, by), max(1, int(w * 0.34)))
            tick += 1
            d += step
        carry = d - seg


def _lashing(surf, cx, cy, half_w, half_h, wraps, w):
    """A whipped lashing: N tight wraps banded across a spar or post, each wrap
    lit on its upper-left shoulder — the joint that tells the eye this thing was
    TIED on, not printed on."""
    w = max(2, int(w))
    span = half_w * 2
    for i in range(wraps):
        t = (i + 0.5) / wraps
        x = cx - half_w + span * t
        lean = half_h * 0.34
        pygame.draw.line(surf, ROPE_LO, (x + w * 0.3, cy - half_h + w * 0.3),
                         (x - lean + w * 0.3, cy + half_h + w * 0.3), w)
        pygame.draw.line(surf, ROPE_MID, (x, cy - half_h),
                         (x - lean, cy + half_h), w)
        pygame.draw.line(surf, ROPE_HI, (x - w * 0.22, cy - half_h),
                         (x - lean - w * 0.22, cy + half_h),
                         max(1, int(w * 0.40)))


def _knot(surf, x, y, r):
    """A tied-off knot boss: two overlapping lobes, lit up-left."""
    r = max(2, int(r))
    pygame.draw.circle(surf, ROPE_LO, (int(x + r * 0.28), int(y + r * 0.32)), r)
    pygame.draw.circle(surf, ROPE_MID, (int(x), int(y)), r)
    pygame.draw.circle(surf, WOOD_HI, (int(x - r * 0.30), int(y - r * 0.34)),
                       max(1, int(r * 0.58)))


def _fill_poly_vgrad(surf, pts, top, bot):
    """Fill an arbitrary polygon with a vertical ramp — the gradient is built on
    the polygon's own bbox so the ramp always spans the shape, never the frame."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)) - 1, int(min(ys)) - 1
    w = max(1, int(max(xs)) - x0 + 2)
    h = max(1, int(max(ys)) - y0 + 2)
    body = vgrad(w, h, 0, top, bot)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(p[0] - x0, p[1] - y0) for p in pts])
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (x0, y0))


def _soft_fold(surf, x, y_top, y_bot, w, alpha=30):
    """A slack fold read as a soft vertical shade band, feathered to nothing at
    its edges so it never becomes a drawn stripe."""
    w = max(2, int(w))
    band = pygame.Surface((w * 2 + 1, max(1, int(y_bot - y_top))), pygame.SRCALPHA)
    for i in range(-w, w + 1):
        a = int(alpha * (1.0 - abs(i) / (w + 0.5)) ** 1.4)
        if a <= 0:
            continue
        pygame.draw.line(band, (0, 0, 0, a), (i + w, 0), (i + w, band.get_height()))
    surf.blit(band, (int(x - w), int(y_top)))


# =============================================================================
# SIGN — a swallowtail pennant slung from a bamboo spar lashed across the gable.
# =============================================================================
def sign_hook(surf, ctx):
    cx = ctx["cx"]
    body_top = ctx["body_top"]
    scale = ctx["scale"]
    half_w, eave = ctx["half_w"], ctx["eave"]
    apex_y = ctx["roof_apex_y"]
    label = ctx["label"]

    limit = half_w + eave

    spar_y = body_top - _sv(26, scale)
    spar_half = min(_sv(46, scale), limit - m(1))
    spar_t = max(2, _sv(2.5, scale))

    cloth_half = min(_sv(42, scale), spar_half - max(2, _sv(3, scale)))
    cloth_top = body_top - _sv(24, scale)
    cloth_bot = body_top - _sv(7, scale)
    cloth_h = cloth_bot - cloth_top
    flick = max(2, _sv(1.6, scale))
    border = max(2, _sv(1.5, scale))

    # The free bottom edge is the only edge allowed to move: the type sits on the
    # spar's CHORD, dead level, because sheared type at 10 logical px stops being
    # readable long before it starts being charming.
    sag_top = min(m(2), max(1, int(cloth_h * 0.13)))
    sag_bot = sag_top + m(2)
    tail_d = max(2, int(cloth_h * 0.15))
    notch = max(2, int(cloth_h * 0.17))

    # The awning seam is a hard floor: shrink the sag/tail envelope (never the
    # type) until the deepest point of the hanging edge clears it.
    deepest = max(tail_d + (notch + tail_d) * 0.0, 0.0)
    for k in range(41):
        a = k / 40.0
        deepest = max(deepest, -notch + (tail_d + notch) * a
                      + sag_bot * math.sin(math.pi * a))
    room = (body_top - max(2, _sv(1.5, scale))) - cloth_bot - border * 0.5
    if deepest > room > 0:
        f = room / deepest
        sag_bot = max(1, int(sag_bot * f))
        tail_d = max(1, int(tail_d * f))
        notch = max(1, int(notch * f))

    def top_y(x):
        u = (x - (cx - cloth_half)) / max(1.0, 2.0 * cloth_half)
        return cloth_top + sag_top * math.sin(math.pi * max(0.0, min(1.0, u)))

    def bot_y(x):
        a = min(1.0, abs(x - cx) / max(1.0, float(cloth_half + flick)))
        return (cloth_bot - notch + (tail_d + notch) * a
                + sag_bot * math.sin(math.pi * a))

    steps = 26
    top_pts = [(cx - cloth_half + 2.0 * cloth_half * i / steps, 0.0)
               for i in range(steps + 1)]
    top_pts = [(x, top_y(x)) for x, _ in top_pts]
    bot_pts = [(cx - (cloth_half + flick)
                + 2.0 * (cloth_half + flick) * i / steps, 0.0)
               for i in range(steps + 1)]
    bot_pts = [(x, bot_y(x)) for x, _ in bot_pts]
    # The FILL runs flat up under the spar while only the TRIM curve carries the
    # sag — a sagging fill edge would open a gap of sky between spar and cloth
    # at mid-span, and the pennant would read as unhooked.
    hem_y = spar_y + spar_t * 0.4
    poly = ([(top_pts[0][0], hem_y), (top_pts[-1][0], hem_y)]
            + bot_pts[::-1])

    # Cast the pennant onto the thatch it hangs against, clipped to the roof
    # triangle so the shadow never leaks into open sky.
    seam_stop = body_top - max(2, _sv(1.5, scale))
    roof = [(cx - limit, seam_stop), (cx + limit, seam_stop), (cx, apex_y)]
    sx, sy = max(1, _sv(2.0, scale)), max(1, _sv(3.0, scale))
    shp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(shp, (18, 10, 6, 92), [(x + sx, y + sy) for x, y in poly])
    rmask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rmask, (255, 255, 255, 255), roof)
    shp.blit(rmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(shp, (0, 0))

    # Spar first: the cloth hangs FROM it, so it must be underneath the cloth's
    # top hem the way a real sleeve swallows its pole.
    pygame.draw.line(surf, WOOD_LO, (cx - spar_half, spar_y + spar_t * 0.5),
                     (cx + spar_half, spar_y + spar_t * 0.5), spar_t)
    pygame.draw.line(surf, WOOD_MID, (cx - spar_half, spar_y),
                     (cx + spar_half, spar_y), spar_t)
    pygame.draw.line(surf, WOOD_HI, (cx - spar_half, spar_y - spar_t * 0.34),
                     (cx + spar_half, spar_y - spar_t * 0.34),
                     max(1, int(spar_t * 0.42)))
    for s in (-1, 1):
        nx = cx + s * int(spar_half * 0.62)
        pygame.draw.line(surf, WOOD_LO, (nx, spar_y - spar_t),
                         (nx, spar_y + spar_t), max(1, _sv(1.0, scale)))
        pygame.draw.circle(surf, WOOD_EDGE,
                           (cx + s * spar_half, int(spar_y)),
                           max(1, int(spar_t * 0.7)))

    _fill_poly_vgrad(surf, poly, CLOTH_HI, CLOTH_LO)

    # Folds sit in the slack OUTSIDE the wordmark: the widest label owns the
    # centre of the cloth, so the fold lane is pushed out to whatever margin the
    # type leaves rather than parked at a fixed offset.
    ink_half = _glyph_base(label, font(11 * scale), m(0.6)).get_width() // 2
    fw = max(3, _sv(1.5, scale))
    lo_x = ink_half + m(1) + fw + 1
    hi_x = cloth_half - border - fw - 1
    fold_x = max(lo_x, min(_sv(20, scale), hi_x))
    if fold_x <= hi_x:
        for s in (-1, 1):
            fx = cx + s * fold_x
            _soft_fold(surf, fx, hem_y + border, bot_y(fx) - border, fw)

    # Macaw-red trim, split by the key: lit runs up-left, shaded runs down-right.
    lit = [(x, y + border * 0.5) for x, y in top_pts]
    shd = [(x, y - border * 0.5) for x, y in bot_pts]
    pygame.draw.lines(surf, AWN_RED, False, lit, border)
    pygame.draw.lines(surf, AWN_RED_D, False, shd, border)
    pygame.draw.line(surf, AWN_RED, (top_pts[0][0] + border * 0.5, hem_y),
                     (bot_pts[0][0] + border * 0.5, bot_pts[0][1]), border)
    pygame.draw.line(surf, AWN_RED_D,
                     (top_pts[-1][0] - border * 0.5, hem_y),
                     (bot_pts[-1][0] - border * 0.5, bot_pts[-1][1]), border)
    pygame.draw.lines(surf, AWN_CREAM, False,
                      [(x, y + border * 1.35) for x, y in top_pts], 1)

    # Lash the spar where it actually crosses the thatch rake — the only two
    # points on its run that have anything to tie to.
    rake = limit * (spar_y - apex_y) / max(1.0, float(body_top - apex_y))
    for s in (-1, 1):
        lx = cx + s * rake
        if abs(rake) < spar_half:
            _lashing(surf, lx, spar_y, max(2, _sv(2.6, scale)),
                     spar_t * 1.5, 3, max(2, _sv(1.5, scale)))

    for s in (-1, 1):
        ex = cx + s * spar_half
        _rope_run(surf, [(ex, spar_y + spar_t * 0.4),
                         (ex + s * _sv(1.2, scale), spar_y + _sv(4, scale)),
                         (ex + s * _sv(0.4, scale), spar_y + _sv(7, scale))],
                  max(2, _sv(1.2, scale)), twist=False)

    f = font(11 * scale)
    base = _glyph_base(label, f, m(0.6))
    bb = base.get_bounding_rect()
    ink_top = top_y(cx) + border + max(1, _sv(1.0, scale))
    ink_bot = (cloth_bot - notch) - border - max(1, _sv(1.0, scale))
    ink_cy = (ink_top + ink_bot) * 0.5
    # gradient_text centres the glyph BOX; caps sit high inside it, so re-centre
    # on the ink or the type floats off the chord it is supposed to sit on.
    cy = int(round(ink_cy + base.get_height() * 0.5 - bb.centery))
    gradient_text(surf, label, f, (cx, cy), GOLD_A_TOP, GOLD_A_BOT,
                  weight=m(1.0 * scale), keyline=LABEL_KEY,
                  kw=max(1, m(0.7)), shadow=False, tracking=m(0.6))


# =============================================================================
# ITEM — the goods slung in a lashed rope cradle over a knotted swag valance.
# =============================================================================
def item_hook(surf, ctx):
    cx = ctx["cx"]
    deck_y = ctx["deck_y"]
    body_top = ctx["body_top"]
    half_w = ctx["half_w"]
    scale = ctx["scale"]
    group = ctx["group"]

    # The m(8) posts are hard walls, so the span stops a hair short of the inner
    # face and lets the line cap land flush instead of biting into the timber.
    post_in = half_w - m(8) - max(3, _sv(2.0, scale))
    rope_y = body_top + _sv(20, scale)
    rope_w = max(m(1.6), _sv(1.8, scale))

    # ---- swag valance: mid-tone by contract. It is the backdrop the goods are
    # read against, so it must sit BELOW the kraft parcel and below the awning
    # cream in value or it starts competing for the eye.
    swag_x = min(_sv(34, scale), post_in - _sv(8, scale))
    swag_top = body_top + _sv(16, scale)
    swag_dip = body_top + _sv(30, scale)
    y_out = swag_top + max(2, _sv(3, scale))
    y_mid = swag_top + max(3, int((swag_dip - swag_top) * 0.35))
    dip = max(2, swag_dip - y_mid)

    steps = 20
    for s in (-1, 1):
        pts_b = []
        for i in range(steps + 1):
            u = i / steps
            x = cx + s * swag_x * (1.0 - u)
            y = y_out + (y_mid - y_out) * u + dip * math.sin(math.pi * u)
            pts_b.append((x, y))
        top_line = [(cx + s * swag_x, swag_top), (cx, swag_top + max(1, m(1)))]
        _fill_poly_vgrad(surf, top_line + pts_b[::-1], SWAG_TOP, SWAG_BOT)

    for fx in (cx - swag_x * 0.55, cx, cx + swag_x * 0.55):
        u = 1.0 - abs(fx - cx) / max(1.0, float(swag_x))
        fy = y_out + (y_mid - y_out) * u + dip * math.sin(math.pi * u)
        _soft_fold(surf, fx, swag_top + max(1, m(1)), fy - m(1),
                   max(2, _sv(2.0, scale)), alpha=46)

    # Swag knots tie off to the posts, and the leftover cloth keeps running past
    # them as short tails — the flank is rigging, not empty frame.
    for s in (-1, 1):
        kx = cx + s * swag_x
        tw = max(3, _sv(5, scale))
        tl = _sv(13, scale)
        tail = [(kx, swag_top + m(1)),
                (kx + s * tw, swag_top + m(1)),
                (kx + s * (tw + _sv(2.5, scale)), swag_top + tl),
                (kx + s * max(1, int(tw * 0.35)), swag_top + int(tl * 0.86))]
        _fill_poly_vgrad(surf, tail, SWAG_TOP, SWAG_BOT)
        _rope_run(surf, [(kx, swag_top + max(1, _sv(1.5, scale))),
                         (cx + s * post_in, swag_top - max(1, _sv(1.0, scale)))],
                  max(2, _sv(1.2, scale)), twist=False)
        _knot(surf, kx, swag_top + max(2, _sv(2.0, scale)),
              max(2, _sv(2.2, scale)))

    # ---- the main span: one rope, post to post, whipped at both ends.
    _rope_run(surf, [(cx - post_in, rope_y), (cx + post_in, rope_y)], rope_w)
    for s in (-1, 1):
        _lashing(surf, cx + s * (post_in - _sv(3, scale)), rope_y,
                 max(2, _sv(2.4, scale)), rope_w * 1.7, 3,
                 max(2, _sv(1.4, scale)))

    # ---- the cradle: two risers into a five-strand net sling.
    sling_x = _sv(22, scale)
    env = _sv(30, scale)
    item_bot = deck_y - m(13)
    end_y = item_bot - _sv(10, scale)
    sag_base = _sv(12, scale)

    def cord(k, sag_f, skew):
        pts = []
        for i in range(15):
            u = i / 14.0
            x = cx - sling_x + 2 * sling_x * u
            y = (end_y + skew * (1 - 2 * u) + sag_base * sag_f
                 * math.sin(math.pi * u))
            pts.append((x, y))
        return pts

    strands = [(0.30, _sv(2.4, scale)), (0.55, -_sv(1.6, scale)),
               (1.00, 0.0), (0.78, _sv(1.6, scale)), (0.42, -_sv(2.4, scale))]
    cw = max(2, _sv(1.5, scale))

    for s in (-1, 1):
        _rope_run(surf, [(cx + s * sling_x, rope_y),
                         (cx + s * sling_x, end_y)], max(2, _sv(1.4, scale)))

    for k in (2, 3, 4):
        _rope_run(surf, cord(k, *strands[k]), cw)
    for s in (-1, 1):
        _knot(surf, cx + s * sling_x, end_y, max(2, _sv(1.7, scale)))

    # ---- the goods. No dome, no glass: the item IS the hero, so it gets the
    # full envelope the rig leaves and the only real glow on the stall.
    src, _lb = _group_thumb(group)
    w, h = src.get_size()
    # Contain to the box the RIG leaves — width to the envelope, height to the
    # clear air between the span rope and the item's hang line — and solve it on
    # the POST-tilt footprint, or a near-square item grows through the rope it is
    # supposed to be hanging from.
    ca, sa = math.cos(math.radians(6)), math.sin(math.radians(6))
    # The risers are SHORT: a heavy load rides right up under its span, and the
    # extra device pixel of hang would cost the goods legibility at 1x.
    avail = max(m(8), item_bot - rope_y - 1)
    f = min(env / (w * ca + h * sa), avail / (w * sa + h * ca))
    img = pygame.transform.smoothscale(
        src, (max(1, int(w * f)), max(1, int(h * f))))
    img = _punch_contrast(img)
    # Rotate BEFORE the rim so the contour highlight stays locked to the one
    # up-left key; a rim baked in before the tilt would swing the sun with it.
    img = pygame.transform.rotate(img, 6)
    bb = img.get_bounding_rect()
    ix = int(cx - bb.centerx)
    iy = int(item_bot - bb.bottom)

    capped_glow(surf, cx, int(iy + bb.centery), int(env * 0.82), GOLD, 30,
                layers=9)

    sh_img = img.copy()
    sh_img.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    for i, a in enumerate((44, 60, 74)):
        sh_img.set_alpha(a)
        d = _sv(3.0, scale) - i
        surf.blit(sh_img, (ix + d, iy + d + _sv(1.5, scale)))
    sill = pygame.Surface((bb.width + m(8), max(3, _sv(5, scale))),
                          pygame.SRCALPHA)
    pygame.draw.ellipse(sill, (12, 8, 6, 105), sill.get_rect())
    surf.blit(sill, (int(cx - sill.get_width() * 0.5 + _sv(2, scale)),
                     int(deck_y - m(8) - sill.get_height() * 0.55)))

    surf.blit(_rim_light(img), (ix, iy), special_flags=pygame.BLEND_ADD)
    surf.blit(img, (ix, iy))

    # Two strands cross IN FRONT of the load, so the sling reads as carrying the
    # item rather than sitting politely behind it.
    for k in (0, 1):
        _rope_run(surf, cord(k, *strands[k]), cw)

    # ---- flank capacity: a coiled spare hank left, a slack empty sling right.
    peg_y = swag_top + _sv(26, scale)
    for s in (-1, 1):
        px = cx + s * (post_in - max(2, _sv(2, scale)))
        pygame.draw.line(surf, WOOD_LO, (px, peg_y),
                         (px - s * _sv(5, scale), peg_y), max(2, _sv(2, scale)))
        pygame.draw.line(surf, WOOD_HI, (px, peg_y - max(1, _sv(0.8, scale))),
                         (px - s * _sv(5, scale), peg_y - max(1, _sv(0.8, scale))),
                         max(1, _sv(0.9, scale)))

    hx = cx - (post_in - _sv(7, scale))
    hr = max(3, _sv(5, scale))
    _rope_run(surf, [(cx - post_in + _sv(2, scale), peg_y),
                     (hx, peg_y + hr)], max(2, _sv(1.2, scale)), twist=False)
    for i in range(3):
        rr = hr - i * max(1, _sv(1.4, scale))
        if rr < 2:
            break
        pygame.draw.ellipse(surf, ROPE_LO,
                            (hx - rr + m(1), peg_y + hr - rr * 1.1 + m(1),
                             rr * 2, rr * 2.2), max(2, _sv(1.1, scale)))
        pygame.draw.ellipse(surf, ROPE_MID,
                            (hx - rr, peg_y + hr - rr * 1.1, rr * 2, rr * 2.2),
                            max(1, _sv(0.9, scale)))

    ex = cx + (post_in - _sv(3, scale))
    ei = cx + (post_in - _sv(15, scale))
    slack = []
    for i in range(13):
        u = i / 12.0
        slack.append((ei + (ex - ei) * u,
                      peg_y + _sv(13, scale) * math.sin(math.pi * u)))
    _rope_run(surf, slack, max(2, _sv(1.2, scale)))
    _knot(surf, ei, peg_y + max(1, _sv(1.0, scale)), max(2, _sv(1.6, scale)))


def install():
    sh.STALL_SIGN_HOOK = sign_hook
    sh.STALL_ITEM_HOOK = item_hook
