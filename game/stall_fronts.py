"""Chosen stall-front designs for the lagoon hub's open categories.

Each open stall keeps its own item presentation — PARROTS: the goods slung in
a lashed rope cradle over a knotted swag valance; PARCELS: a grounded paper
floor lantern the hero stands in front of; COSTUMES: a turned-timber pedestal
in a hard pool of light — but every stall shares one sign: a bulb-studded
stepped cartouche in the awning's own lacquer red, with cream piping tracing
its outline, so the sign reads as kin to the red/cream flags below it.

draw_hut() in store_hub calls draw_sign()/draw_item() for any group present
in ITEM; groups outside that set keep the stock cabochon + name-board front
untouched, so the four not-yet-open categories are unaffected when they ship.
"""
import math

import pygame

from game.store_hub import (
    m, font, lerp_color, vgrad, gradient_text, capped_glow, _glyph_base,
    _group_thumb, _punch_contrast, _rim_light,
    GOLD, GOLD_PALE, GOLD_DEEP, GOLD_A_TOP, GOLD_A_BOT,
    WOOD_HI, WOOD_MID, WOOD_LO, WOOD_EDGE, STALL_DARK, LABEL_KEY,
    AWN_RED, AWN_CREAM_D,
)

# Hemp lane, derived from the stall's own timber so the rigging never reads as
# a foreign material — cord is bleached wood, not rope-coloured plastic.
ROPE_HI = lerp_color(WOOD_HI, (244, 232, 206), 0.42)
ROPE_MID = lerp_color(WOOD_MID, AWN_CREAM_D, 0.30)
ROPE_LO = lerp_color(WOOD_LO, WOOD_EDGE, 0.35)
SWAG_TOP = (138, 96, 72)
SWAG_BOT = (96, 64, 48)

# Washi ladder for the lantern: the shell sits one value step below the sign
# so the hero — front-lit from the same low upper-left sun — stays the
# brightest thing in the stall.
LANT_HI = (186, 150, 100)
LANT_LO = (150, 116, 74)
LANT_CORD = (196, 168, 124)
FLANK_SHADE = lerp_color(WOOD_LO, STALL_DARK, 0.35)

# Sign: awning-matched lacquer red, cream piping, gold bulbs a notch under
# GOLD_PALE so the sign's peak can never climb above the hero's.
CARTOUCHE_TOP = (122, 26, 30)
CARTOUCHE_BOT = (74, 12, 18)
PIPING_COLOR = AWN_CREAM_D
BULB_SEAT = GOLD_DEEP
BULB_GLASS = lerp_color(GOLD_PALE, GOLD, 0.18)
POOL_CORE = lerp_color(WOOD_HI, GOLD_PALE, 0.35)
INK_PT = 11.5  # the largest size that still fits COSTUMES (widest label)
               # inside the cartouche


def _sv(v, scale):
    """Logical px -> device px at a stall's own scale factor."""
    return int(m(v) * scale)


def _px(v, scale, lo=1):
    return max(lo, int(m(v) * scale))


# =============================================================================
# Rigging primitives (PARROTS item) — one low golden-hour key from the upper
# left, so every cord carries its highlight up-left and its shade down-right.
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
# PARROTS item — the goods slung in a lashed rope cradle over a knotted swag.
# =============================================================================
def _item_sling(surf, ctx):
    cx = ctx["cx"]
    deck_y = ctx["deck_y"]
    body_top = ctx["body_top"]
    half_w = ctx["half_w"]
    scale = ctx["scale"]
    group = ctx["group"]

    # The m(8) posts are hard walls, so the span stops a hair short of the inner
    # face and lets the line cap land flush instead of biting into the timber.
    post_in = half_w - m(8) - max(3, _sv(2.0, scale))
    rope_y = body_top + _sv(15, scale)
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
    sling_x = _sv(30, scale)
    env = _sv(45, scale)
    item_bot = deck_y - m(9)
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
    # The risers are SHORT: a heavy load rides right up under its span, and the
    # extra device pixel of hang would cost the goods legibility at 1x.
    avail = max(m(8), item_bot - rope_y - 1)
    # Rotate the SOURCE first so the hero is resampled once — tilting after the
    # downscale costs a second resample and half the edge acuity at 1x. The rim
    # still bakes after the tilt, locked to the one up-left key.
    rot = pygame.transform.rotate(src, 3)
    rw, rh = rot.get_size()
    f = min(env / rw, avail / rh)
    img = pygame.transform.smoothscale(
        rot, (max(1, int(rw * f)), max(1, int(rh * f))))
    img = _punch_contrast(img)
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


# =============================================================================
# PARCELS item — a grounded paper floor lantern (andon) the hero stands in.
# =============================================================================
def _lantern_geom(ctx):
    """Every lantern part hangs off ONE metric set so the shell, the shadow it
    receives and the hero that casts it can never drift apart."""
    cx, deck_y, scale = ctx["cx"], ctx["deck_y"], ctx["scale"]
    sill = deck_y - m(8)
    pw, ph = _px(58, scale), _px(33, scale)
    foot_h = _px(3, scale, 2)
    return dict(
        cx=cx, scale=scale, sill=sill, foot_h=foot_h,
        awn_b=ctx["body_top"] + int(m(15) * scale),
        panel=pygame.Rect(cx - pw // 2, sill - foot_h - ph, pw, ph),
        fw=_px(5, scale, 3), hair=max(1, m(0.8)),
        box=int(m(44) * scale), base=deck_y - m(10),
    )


def _top_round(w, h, rad, top, bot):
    """Vertical gradient panel with only its TOP corners rounded — a paper shell
    stretched over a frame reads as square where it meets the floor."""
    body = vgrad(w, h, 0, top, bot)
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                     border_top_left_radius=rad, border_top_right_radius=rad)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def _lantern_front_light(img, warm=(255, 216, 162), peak=52, ambient=18):
    """The ONE key, applied to the hero as a DIRECTIONAL additive ramp that is
    hottest at the upper-left and falls to ambient at the lower-right.

    A flat _punch_contrast alone lifts the whole silhouette evenly, which reads
    as a washed sticker AND still loses to warm paper at the shadow side; a
    directional ramp buys the same average lift while keeping modelling, so the
    hero sits IN the lantern's light instead of being pasted over it."""
    w, h = img.get_size()
    out = img.copy()
    for y in range(h):
        ty = y / max(1, h - 1)
        for x in range(w):
            r, g, b, a = out.get_at((x, y))
            if a == 0:
                continue
            t = max(0.0, 1.0 - (x / max(1, w - 1) * 0.55 + ty * 0.45))
            k = (ambient + peak * t ** 1.15) / 255.0
            out.set_at((x, y), (min(255, int(r + warm[0] * k)),
                                min(255, int(g + warm[1] * k)),
                                min(255, int(b + warm[2] * k)), a))
    return out


def _item_lantern(surf, ctx):
    cx, scale = ctx["cx"], ctx["scale"]
    g = _lantern_geom(ctx)
    sill, awn_b, panel = g["sill"], g["awn_b"], g["panel"]
    pw, ph = panel.w, panel.h
    fw, hair = g["fw"], g["hair"]

    # The ~22px of opening either side of the shell is answered with STRUCTURE:
    # two bamboo uprights the lantern paper is strung between. They are the dark
    # rests that let lit paper + hero read as one bright centre.
    ux = _px(38, scale)
    uw = _px(3.2, scale, 3)
    for sgn in (-1, 1):
        x0 = cx + sgn * ux - uw // 2
        col = pygame.Rect(x0, awn_b, uw, sill - awn_b)
        if sgn < 0:
            surf.blit(vgrad(uw, col.h, 0, WOOD_MID, WOOD_LO), col.topleft)
            pygame.draw.line(surf, WOOD_HI, (x0, col.top), (x0, col.bottom - 1), 1)
            # the one key grazes the near upright's upper third and dies out
            wedge = pygame.Surface((uw, col.h), pygame.SRCALPHA)
            for y in range(int(col.h * 0.55)):
                a = int(80 * (1 - y / (col.h * 0.55)) ** 1.5)
                pygame.draw.line(wedge, (255, 206, 150, a), (0, y), (uw, y))
            surf.blit(wedge, col.topleft)
        else:
            surf.blit(vgrad(uw, col.h, 0, lerp_color(WOOD_LO, STALL_DARK, 0.55),
                            STALL_DARK), col.topleft)
        pygame.draw.line(surf, WOOD_EDGE, (x0 + uw - 1, col.top),
                         (x0 + uw - 1, col.bottom - 1), 1)

    for f in (0.20, 0.50, 0.80):
        cy = int(panel.top + panel.h * f)
        for sgn in (-1, 1):
            x0 = cx + sgn * ux
            inner = x0 - sgn * uw // 2
            edge = cx + sgn * (pw // 2 + fw)
            pygame.draw.line(surf, (*LANT_CORD, 150), (inner, cy), (edge, cy), hair)
            for k in (-1, 1):
                pygame.draw.line(surf, (*LANT_CORD, 200),
                                 (x0 - uw // 2 - 1, cy + k * hair),
                                 (x0 + uw // 2 + 1, cy + k * hair), 1)

    # Warmth seat only — a capped bleed behind the shell so the lantern separates
    # from STALL_DARK. It sits BEHIND the paper, so it never lifts the hero, and
    # it is clipped to the opening so it cannot wash over the deck lip or the
    # side posts, which are hard walls of the stall architecture.
    in_half = ctx["half_w"] - m(8)
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(cx - in_half, awn_b, in_half * 2, sill - awn_b))
    capped_glow(surf, cx, panel.centery, int(pw * 0.62), GOLD, 22, layers=8)
    surf.set_clip(old_clip)

    for sgn in (-1, 1):
        ex = cx + sgn * pw // 2
        lean = _px(1.5, scale, 1)
        pygame.draw.polygon(surf, FLANK_SHADE, [
            (ex, panel.top + _px(2, scale)),
            (ex + sgn * fw, panel.top + _px(2, scale) + lean),
            (ex + sgn * fw, panel.bottom + lean),
            (ex, panel.bottom)])
        pygame.draw.line(surf, lerp_color(FLANK_SHADE, WOOD_HI, 0.35 if sgn < 0 else 0.10),
                         (ex + sgn * fw, panel.top + _px(2, scale) + lean),
                         (ex + sgn * fw, panel.bottom + lean), 1)

    surf.blit(_top_round(pw, ph, _px(6, scale, 3), LANT_HI, LANT_LO), panel.topleft)
    for k in range(1, 5):
        ry = panel.top + int(panel.h * k / 5)
        rib = pygame.Surface((pw, hair), pygame.SRCALPHA)
        rib.fill((*lerp_color(LANT_LO, WOOD_EDGE, 0.45), 140))
        surf.blit(rib, (panel.left, ry))
    pygame.draw.line(surf, lerp_color(LANT_HI, WOOD_EDGE, 0.30),
                     (panel.right - 1, panel.top + _px(6, scale, 3)),
                     (panel.right - 1, panel.bottom - 1), hair)

    foot = pygame.Rect(panel.left - _px(2, scale), sill - g["foot_h"],
                       pw + _px(4, scale), g["foot_h"])
    surf.blit(vgrad(foot.w, foot.h, 0, WOOD_HI, WOOD_LO), foot.topleft)
    pygame.draw.line(surf, WOOD_EDGE, (foot.left, foot.bottom - 1),
                     (foot.right - 1, foot.bottom - 1), 1)
    for sgn in (-1, 1):
        rx = cx + sgn * (pw // 2 - _px(4, scale))
        pygame.draw.line(surf, lerp_color(WOOD_LO, WOOD_EDGE, 0.5),
                         (rx, foot.top), (rx, foot.bottom - 1), 1)

    # ---- the hero, standing in front of the lit shell.
    src, _lb = _group_thumb(ctx["group"])
    w, h = src.get_size()
    s = g["box"] / max(w, h)
    img = pygame.transform.smoothscale(src, (max(1, int(w * s)), max(1, int(h * s))))
    img = _punch_contrast(img, boost=40)
    img = _lantern_front_light(img)
    r = img.get_rect(midbottom=(g["cx"], g["base"]))

    # The hero stands IN FRONT of lit paper, so the key must throw its shadow
    # ONTO that paper — down-right, clipped to the shell. Without it the item
    # reads as a silhouette cut out of a lantern; with it the paper is a lit
    # ground the item is planted on. This is the whole concept's load-bearing
    # beat, so it is measured, not eyeballed.
    sil = img.copy()
    sil.fill((8, 5, 3, 255), special_flags=pygame.BLEND_RGBA_MULT)
    step = _px(1.1, scale, 1)
    old_clip = surf.get_clip()
    surf.set_clip(pygame.Rect(panel.left, panel.top,
                              panel.w + g["fw"], panel.h + g["foot_h"]))
    for k, a in ((1, 76), (2, 58), (3, 42), (4, 26), (5, 14)):
        sil.set_alpha(a)
        surf.blit(sil, (r.x + k * step, r.y + k * step))
    surf.set_clip(old_clip)

    # Contact shadow: cast down-RIGHT across the lantern floor and onto the
    # sill, so the item is planted by the same sun that lights it.
    ao = pygame.Surface((int(r.width * 1.45), _px(7, scale, 4)), pygame.SRCALPHA)
    for i in range(4):
        a = int(120 * (1 - i / 4))
        pygame.draw.ellipse(ao, (12, 8, 4, a),
                            (i * 2, i, ao.get_width() - i * 4, ao.get_height() - i * 2))
    surf.blit(ao, (r.centerx - ao.get_width() // 2 + _px(3, scale),
                   r.bottom - ao.get_height() // 2))

    surf.blit(_rim_light(img), r.topleft, special_flags=pygame.BLEND_ADD)
    surf.blit(img, r.topleft)


# =============================================================================
# SIGN — a bulb-studded stepped cartouche in the awning's own lacquer red,
# shared by every open stall.
# =============================================================================
def _cartouche_points(cx, bottom_y, half_c, half_1, half_2, t0, t1, t2):
    """Stepped marquee silhouette: one tall central block whose top steps DOWN
    and OUT twice per side onto a shared flat bottom edge."""
    return [
        (cx - half_2, bottom_y), (cx - half_2, t2), (cx - half_1, t2),
        (cx - half_1, t1), (cx - half_c, t1), (cx - half_c, t0),
        (cx + half_c, t0), (cx + half_c, t1), (cx + half_1, t1),
        (cx + half_1, t2), (cx + half_2, t2), (cx + half_2, bottom_y),
    ]


def draw_sign(surf, ctx):
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
    pygame.draw.polygon(surf, PIPING_COLOR, bead, max(1, m(0.5)))

    f = font(INK_PT * scale)
    gradient_text(surf, label, f, (cx, t0 + int(h * 0.56)),
                  GOLD_A_TOP, GOLD_A_BOT, weight=m(1.0 * scale),
                  keyline=LABEL_KEY, kw=m(1.0), shadow=False, tracking=m(0.6))

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


# =============================================================================
# COSTUMES item — a turned-timber pedestal in a hard pool of light.
# =============================================================================
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


def _item_pedestal(surf, ctx):
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


# Every group here gets the chosen sign + its own chosen item; anything not
# listed keeps the stock cabochon + name-board front drawn in store_hub.
ITEM = {
    "parrot": _item_sling,
    "parcels": _item_lantern,
    "costume": _item_pedestal,
}


def draw_item(surf, ctx):
    ITEM[ctx["group"]](surf, ctx)
