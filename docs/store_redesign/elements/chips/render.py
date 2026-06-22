"""
CONSTELLATION store — CHIP FAMILY element loop.

The pill-chip product line: the cost chip (price), plus its matching states —
EQUIP, EQUIPPED, and can't-afford/LOCKED. Every chip shares ONE silhouette
(fully-rounded pill, h/2 radius) and ONE edge finish (dark outer keyline under
a bright top-left bevel = a crisp DOUBLE rim per THEME), so the row reads as a
single product line no matter the body colour.

User directive on the PRICE chip: it is a SINGLE SMOOTH GOLD GRADIENT — a
gradual bright-crown -> deep-amber ramp. No two-tone, no spliced champagne
band. Depth comes from the ramp + gloss sweep + double rim alone. Numerals are
dark deep-brown for punch; the coin sits in its own left cell with a clear gap
before the digits.

Authored resolution-independently and rendered at SS=4 (the THEME crispness
lever), one smoothscale down. Pure pygame, both build targets safe.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font, _GOLD_BRIGHT, _GOLD_PALE, _GOLD_DEEP


# ── supersample (THEME: author logical, render at SS, one smoothscale down) ────
SS = 4
DW, DH = W * SS, H * SS


def m(v):
    return int(round(v * SS))


def font(size):
    return _font(max(1, int(round(size * SS))), True)


def _stamp_bold(base, weight):
    """Faux-bold ring-stamp (THEME type-weight recipe): grow strokes ~`weight`
    px evenly without filling counters. Weights are deliberately small — the
    visible thickening at the downscaled target wants only ~0.5px."""
    weight = max(0, min(m(0.5), int(round(weight * 0.42))))
    if weight <= 0:
        return base
    w, h = base.get_size()
    pad = weight + m(1)
    out = pygame.Surface((w + pad * 2, h + pad * 2), pygame.SRCALPHA)
    ring = [(-weight, 0), (weight, 0), (0, -weight), (0, weight)]
    d = max(1, int(round(weight * 0.71)))
    ring += [(-d, -d), (d, -d), (-d, d), (d, d)]
    for dx, dy in ring:
        out.blit(base, (pad + dx, pad + dy))
    out.blit(base, (pad, pad))
    return out


def _glyph_base(txt, font_obj, tracking):
    if tracking:
        widths = [font_obj.size(ch)[0] for ch in txt]
        total = sum(widths) + tracking * (len(txt) - 1)
        hh = font_obj.get_height()
        base = pygame.Surface((max(1, total), hh), pygame.SRCALPHA)
        x = 0
        for ch, wch in zip(txt, widths):
            base.blit(font_obj.render(ch, True, WHITE), (x, 0))
            x += wch + tracking
        return base
    return font_obj.render(txt, True, WHITE)


def plain_text(surf, txt, font_obj, center, color, shadow_a=150, tracking=0,
               weight=None, keyline=None, kw=None):
    """Solid type, faux-bolded, optional crisp dark keyline (THEME thick+crisp)."""
    base = _glyph_base(txt, font_obj, tracking)
    if weight is None:
        weight = m(0.8)
    base = _stamp_bold(base, weight)
    img = base.copy()
    img.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    r = img.get_rect(center=center)
    if shadow_a:
        sh = base.copy()
        sh.fill((*NEAR_BLACK, 255), special_flags=pygame.BLEND_RGBA_MULT)
        sh.set_alpha(shadow_a)
        surf.blit(sh, (r.x, r.y + m(1.5)))
    if keyline:
        p = kw if kw is not None else m(1)
        kl = base.copy()
        kl.fill((*keyline, 255), special_flags=pygame.BLEND_RGBA_MULT)
        for ang in range(0, 360, 45):
            dx = int(round(p * math.cos(math.radians(ang))))
            dy = int(round(p * math.sin(math.radians(ang))))
            surf.blit(kl, (r.x + dx, r.y + dy))
    surf.blit(img, r)
    return r


def lerp_stops(stops, t):
    """Sample a piecewise-linear colour ramp at t in [0,1]. The price gradient
    is authored as an N-stop ramp (still ONE continuous gold gradient, no
    two-tone split) so the bright-crown -> deep-amber falloff can be shaped."""
    t = max(0.0, min(1.0, t))
    n = len(stops)
    seg = 0
    while seg < n - 2 and t > stops[seg + 1][0]:
        seg += 1
    t0, c0 = stops[seg]
    t1, c1 = stops[seg + 1]
    local = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
    return lerp_color(c0, c1, max(0.0, min(1.0, local)))


def vgrad_stops(w, h, radius, stops, gamma=1.0):
    """Vertical rounded-rect filled by a continuous multi-stop gradient — one
    smooth ramp top to bottom (NOT a spliced crown band)."""
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = (y / max(1, h - 1)) ** gamma
        c = lerp_stops(stops, t)
        pygame.draw.line(body, (*c, 255), (0, y), (w - 1, y))
    if radius > 0:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h),
                         border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def vgrad(w, h, radius, top, bot, gamma=1.0):
    return vgrad_stops(w, h, radius, [(0.0, top), (1.0, bot)], gamma=gamma)


def drop_shadow(surf, rect, radius, blur, alpha, dy):
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.4)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy, rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, r.topleft)


def soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=8):
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def multistop_v(w, h, stops):
    surf = pygame.Surface((w, h))
    n = len(stops)
    for y in range(h):
        f = y / max(1, h - 1)
        seg = 0
        while seg < n - 2 and f > stops[seg + 1][0]:
            seg += 1
        t0, c0 = stops[seg]
        t1, c1 = stops[seg + 1]
        local = 0.0 if t1 == t0 else (f - t0) / (t1 - t0)
        pygame.draw.line(surf, lerp_color(c0, c1, max(0.0, min(1.0, local))),
                         (0, y), (w - 1, y))
    return surf


def bevel_rim(surf, rect, radius, deep, bright, w):
    """THEME emboss: dark outer keyline + bright top-left inner stroke."""
    pygame.draw.rect(surf, deep, rect, width=w, border_radius=radius)
    inner = rect.inflate(-w, -w)
    br = bright if len(bright) == 4 else (*bright, 220)
    hl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(hl, br, inner.move(-rect.x, -rect.y),
                     width=max(1, w // 2), border_radius=max(1, radius - w))
    grad = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        a = int(255 * (1 - y / rect.h) ** 1.4)
        pygame.draw.line(grad, (255, 255, 255, a), (0, y), (rect.w, y))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hl, rect.topleft)


def contact_shadow(surf, rect, radius, depth, alpha=90):
    ao = pygame.Surface(rect.size, pygame.SRCALPHA)
    for i in range(depth):
        a = int(alpha * (1 - i / depth))
        pygame.draw.rect(ao, (0, 0, 0, a),
                         (i, i, rect.w - 2 * i, rect.h - 2 * i),
                         width=max(1, m(0.8)), border_radius=max(1, radius - i))
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(rect.w, 0), (rect.w, rect.h), (0, rect.h)])
    ao.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(ao, rect.topleft)


def gloss_sweep(surf, rect, radius, peak=120):
    """THEME single gloss sweep across the upper portion — the wet-gloss tell."""
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, int(rect.h * 0.5))
    for y in range(h):
        a = int(peak * (1 - y / h) ** 1.6)
        pygame.draw.line(sweep, (255, 255, 255, a), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


def chip_body_stops(surf, r, radius, stops, rim_dark, rim_bright, gloss=120,
                    gamma=1.05):
    """The ONE chip-body finish shared across the whole family, fed by a
    continuous gradient ramp: drop shadow, single smooth gradient fill, one
    gloss sweep, bottom-right contact AO, then the DOUBLE rim — a dark outer
    keyline UNDER a bright top-left bevel (THEME defined edge)."""
    drop_shadow(surf, r, radius, blur=m(4), alpha=110, dy=m(2))
    surf.blit(vgrad_stops(r.w, r.h, radius, stops, gamma=gamma), r.topleft)
    gloss_sweep(surf, r, radius, peak=gloss)
    contact_shadow(surf, r, radius, m(3), alpha=80)
    pygame.draw.rect(surf, rim_dark, r, width=max(1, m(1.6)), border_radius=radius)
    bevel_rim(surf, r, radius, rim_dark, (*rim_bright, 235), w=max(1, m(1.5)))


def chip_body(surf, r, radius, top, bot, rim_dark, rim_bright, gloss=120,
              gamma=1.05):
    chip_body_stops(surf, r, radius, [(0.0, top), (1.0, bot)], rim_dark,
                    rim_bright, gloss=gloss, gamma=gamma)


def coin_glyph(surf, cx, cy, r, rim=_GOLD_DEEP):
    """Beveled gold coin (THEME coin recipe): radial face lit top-left, a
    directional sheen, a crisp double rim, and a $ relief. Lives in its own
    cell with a clear gap before the digits."""
    d = r * 2
    face = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    c = r + m(1)
    edge = max(1, int(r * 0.10))
    for i in range(r, 0, -1):
        t = 1 - i / r
        col = lerp_color((255, 233, 158), (196, 138, 36), t ** 0.85)
        pygame.draw.circle(face, (*col, 255), (c, c), i)
    sheen = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(sheen, (255, 248, 214, 150),
                       (c - r // 3, c - r // 3), int(r * 0.6))
    smask = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (c, c), r - edge)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    face.blit(sheen, (0, 0), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(face, (90, 56, 12, 255), (c, c), r, max(1, m(1.2)))
    pygame.draw.circle(face, (*rim, 240), (c, c), r - max(1, m(0.8)), max(1, m(1)))
    pygame.draw.circle(face, (255, 248, 206, 150), (c, c), r - edge, max(1, int(m(0.7))))
    if r >= m(5):
        sf = font(max(7, r * 0.95 / SS))
        sh = sf.render("$", True, (120, 80, 16))
        face.blit(sh, sh.get_rect(center=(c, c + m(1))))
        gl = sf.render("$", True, (255, 240, 188))
        face.blit(gl, gl.get_rect(center=(c, c - m(0.5))))
    surf.blit(face, face.get_rect(center=(cx, cy)))


def coin_glyph_mono(surf, cx, cy, r, lo, hi, rim, sheen_col=(232, 238, 250)):
    """A desaturated coin for the LOCKED state — same beveled-disc construction
    as coin_glyph but a cool slate ramp so the locked chip reads as a dimmed
    sibling of the gold coin, not a different object."""
    d = r * 2
    face = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    c = r + m(1)
    edge = max(1, int(r * 0.10))
    for i in range(r, 0, -1):
        t = 1 - i / r
        col = lerp_color(hi, lo, t ** 0.85)
        pygame.draw.circle(face, (*col, 255), (c, c), i)
    sheen = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(sheen, (*sheen_col, 130), (c - r // 3, c - r // 3), int(r * 0.6))
    smask = pygame.Surface((d + m(2), d + m(2)), pygame.SRCALPHA)
    pygame.draw.circle(smask, (255, 255, 255, 255), (c, c), r - edge)
    sheen.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    face.blit(sheen, (0, 0), special_flags=pygame.BLEND_ADD)
    pygame.draw.circle(face, (12, 14, 24, 255), (c, c), r, max(1, m(1.2)))
    pygame.draw.circle(face, (*rim, 240), (c, c), r - max(1, m(0.8)), max(1, m(1)))
    if r >= m(5):
        sf = font(max(7, r * 0.95 / SS))
        sh = sf.render("$", True, (44, 50, 68))
        face.blit(sh, sh.get_rect(center=(c, c + m(1))))
        gl = sf.render("$", True, (226, 232, 246))
        face.blit(gl, gl.get_rect(center=(c, c - m(0.5))))
    surf.blit(face, face.get_rect(center=(cx, cy)))


def lock_glyph(surf, cx, cy, h, body=(214, 222, 238), dark=(28, 32, 48)):
    """A small padlock for the LOCKED chip — a rounded shackle + a beveled body,
    drawn oversized so the downscale keeps it crisp. Kept compact; it sits in
    the coin cell so the chip silhouette is unchanged."""
    bw, bh = int(h * 0.78), int(h * 0.56)
    bx, by = cx - bw // 2, cy - bh // 2 + int(h * 0.12)
    sr = int(bw * 0.30)                          # shackle radius
    sy = by - int(sr * 0.2)
    # shackle: an arc rising from the body top
    pygame.draw.arc(surf, dark, (cx - sr, sy - sr, sr * 2, sr * 2),
                    math.radians(20), math.radians(160), max(1, m(2.6)))
    pygame.draw.arc(surf, (240, 244, 252), (cx - sr, sy - sr, sr * 2, sr * 2),
                    math.radians(70), math.radians(160), max(1, m(1.2)))
    # body: beveled rounded-rect
    rb = pygame.Rect(bx, by, bw, bh)
    surf.blit(vgrad(bw, bh, m(4), lerp_color(body, WHITE, 0.25),
                    lerp_color(body, dark, 0.5), gamma=1.1), rb.topleft)
    pygame.draw.rect(surf, dark, rb, width=max(1, m(1.2)), border_radius=m(4))
    # keyhole
    kr = max(1, int(bw * 0.13))
    pygame.draw.circle(surf, dark, (cx, by + bh // 2 - kr), kr)
    pygame.draw.line(surf, dark, (cx, by + bh // 2 - kr),
                     (cx, by + bh - max(1, int(bh * 0.28))), max(1, m(1.4)))


# =============================================================================
# Price-chip ramps — THREE single, continuous gold gradients to pick between.
# Each is ONE smooth ramp (bright crown at top -> deep amber at the bottom);
# NONE is two-tone. They differ only in where the ramp sits and how deep it
# bottoms out, so the AD can judge which gold reads most premium.
# =============================================================================
PRICE_RAMP = {
    # A — Royal gold: a luminous champagne-touched crown easing into a rich,
    # saturated amber. Balanced premium; the safe default candidate.
    "A": dict(
        stops=[(0.00, (255, 224, 150)),
               (0.34, (250, 198, 92)),
               (0.68, (224, 154, 44)),
               (1.00, (176, 110, 22))],
        rim_dark=(86, 50, 8), rim_bright=(255, 240, 190),
        num=(52, 28, 4), coin_rim=(120, 74, 14), gamma=1.06),
    # B — Honey gold: a slightly warmer, deeper bottom with a tighter bright
    # band up top, so the chip glows hotter in the crown and sinks darker at
    # the foot — the most 'molten metal' of the three.
    "B": dict(
        stops=[(0.00, (255, 230, 162)),
               (0.28, (252, 196, 84)),
               (0.62, (214, 140, 36)),
               (1.00, (152, 92, 16))],
        rim_dark=(80, 46, 8), rim_bright=(255, 244, 198),
        num=(48, 26, 4), coin_rim=(118, 70, 12), gamma=1.10),
    # C — Burnished gold: starts a touch cooler/paler and ramps to the deepest
    # bronze foot of the set; maximum top-to-bottom value travel for the most
    # sculpted, dimensional read.
    "C": dict(
        stops=[(0.00, (255, 236, 176)),
               (0.40, (244, 188, 76)),
               (0.74, (200, 128, 30)),
               (1.00, (138, 84, 14))],
        rim_dark=(74, 44, 8), rim_bright=(255, 238, 184),
        num=(44, 24, 4), coin_rim=(112, 68, 12), gamma=1.12),
}


def price_chip(surf, cx, cy, text, h, ramp="A", state="afford"):
    """The cost chip + its sibling states, ALL on one pill silhouette and the
    same double-rim finish (THEME one-family rule).

    state:
      afford  — the gold price (single smooth ramp, dark deep-brown numerals)
      locked  — can't-afford: cool slate body, LIGHT legible numerals, a small
                lock in the coin cell (still the same pill + double rim)
    """
    cfg = PRICE_RAMP[ramp]
    coin_d = int(h * 0.66)
    pad = m(13)
    gapc = m(8)                                  # clear gap: coin cell -> digits
    f = font(h * 0.50 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)
    w = pad + coin_d + gapc + nw + pad
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    if state == "afford":
        chip_body_stops(surf, r, h // 2, cfg["stops"], cfg["rim_dark"],
                        cfg["rim_bright"], gloss=130, gamma=cfg["gamma"])
        x = r.x + pad
        coin_glyph(surf, x + coin_d // 2, cy, coin_d // 2, rim=cfg["coin_rim"])
        x += coin_d + gapc
        plain_text(surf, text, f, (x + nw // 2, cy), cfg["num"], shadow_a=0,
                   weight=m(1.0))
    else:  # locked / can't-afford — cool slate, light numerals, small lock
        chip_body(surf, r, h // 2, (104, 110, 132), (54, 58, 80),
                  (12, 14, 24), (176, 184, 206), gloss=78)
        x = r.x + pad
        lock_glyph(surf, x + coin_d // 2, cy, coin_d)
        x += coin_d + gapc
        plain_text(surf, text, f, (x + nw // 2, cy), (236, 240, 250), shadow_a=0,
                   weight=m(1.0), keyline=(18, 22, 36), kw=m(0.7))
    return r


def status_chip(surf, cx, cy, text, h, kind="equip"):
    """EQUIP / EQUIPPED — same pill silhouette + double-rim finish as price.
    EQUIP is a neutral cream-gold (owned, not active); EQUIPPED is a clean,
    distinct green so the active state is unmistakable at a glance."""
    if kind == "equipped":
        top, bot = (96, 220, 138), (28, 138, 74)
        rim_dark, rim_bright = (8, 56, 28), (198, 255, 218)
        num = (6, 42, 18)
    else:  # equip
        top, bot = (242, 238, 226), (178, 170, 150)
        rim_dark, rim_bright = (62, 54, 34), (255, 252, 244)
        num = (50, 38, 16)
    f = font(h * 0.48 / SS)
    nw = _glyph_base(text, f, 0).get_width() + m(2)
    pad = m(17)
    w = pad * 2 + nw
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    chip_body(surf, r, h // 2, top, bot, rim_dark, rim_bright, gloss=118)
    if kind == "equipped":
        # a tiny check mark before the word so EQUIPPED reads as a confirmed
        # state, sharing the cell-then-label rhythm of the price chip
        cxk = r.x + pad - m(2)
        plain_text(surf, text, f, (r.centerx + m(5), cy), num, shadow_a=0,
                   weight=m(0.9))
        ck = cxk
        pygame.draw.lines(surf, num, False,
                          [(ck, cy + m(1)), (ck + m(4), cy + m(5)),
                           (ck + m(11), cy - m(6))], max(1, m(2.6)))
    else:
        plain_text(surf, text, f, r.center, num, shadow_a=0, weight=m(0.9))
    return r


# =============================================================================
# Review sheet
# =============================================================================
BG_STOPS = [
    (0.00, (6, 7, 24)),
    (0.30, (11, 11, 40)),
    (0.55, (18, 16, 58)),
    (0.78, (26, 20, 72)),
    (1.00, (14, 12, 46)),
]
NEBULA_GLOW = (70, 60, 150)


def _label(surf, txt, cx, y, size=11, col=(236, 214, 150)):
    plain_text(surf, txt, font(size), (cx, y), col, shadow_a=130, weight=m(0.7),
               keyline=(10, 10, 24), kw=m(0.7), tracking=m(1))


def render_sheet():
    # generous logical canvas; ON the shared night-sky bg
    LW, LH = 360, 560
    sw, sh = LW * SS, LH * SS
    surf = pygame.Surface((sw, sh))
    surf.blit(multistop_v(sw, sh, BG_STOPS), (0, 0))
    soft_glow(surf, sw // 2, int(sh * 0.40), m(220), NEBULA_GLOW, 60, layers=10)

    cx = sw // 2
    _label(surf, "CONSTELLATION — CHIP FAMILY", cx, m(20), size=13,
           col=(255, 244, 206))
    _label(surf, "PRICE = SINGLE SMOOTH GOLD GRADIENT", cx, m(38), size=9,
           col=(196, 182, 220))

    ch = m(30)                                   # showcase chip height (large)
    # ── three single-gradient PRICE ramps, each at 280 / 1,500 / 7,000 ────────
    col_x = [sw // 4, sw // 2, sw - sw // 4]
    ramp_top = {"A": "RAMP A", "B": "RAMP B", "C": "RAMP C"}
    ramp_sub = {"A": "ROYAL GOLD", "B": "HONEY GOLD", "C": "BURNISHED"}
    values = ["280", "1,500", "7,000"]
    y0 = m(64)
    for col, ramp in enumerate("ABC"):
        x = col_x[col]
        _label(surf, ramp_top[ramp], x, y0, size=11, col=(255, 232, 168))
        _label(surf, ramp_sub[ramp], x, y0 + m(15), size=9)
        for i, v in enumerate(values):
            price_chip(surf, x, y0 + m(40) + i * m(46), v, ch, ramp=ramp,
                       state="afford")

    # ── the matching states (share the exact pill + edge finish) ─────────────
    sy = y0 + m(40) + 3 * m(46) + m(34)
    gold_rule_y = sy - m(18)
    rule = pygame.Surface((sw - m(40), m(3)), pygame.SRCALPHA)
    for sx in range(rule.get_width()):
        hx = abs(sx - rule.get_width() / 2) / (rule.get_width() / 2)
        a = int(150 * (1.0 - hx ** 1.6))
        pygame.draw.line(rule, (*_GOLD_BRIGHT, a), (sx, 0), (sx, m(2)))
    surf.blit(rule, (m(20), gold_rule_y))
    _label(surf, "STATES — ONE PILL, ONE EDGE FINISH", cx, sy, size=12,
           col=(255, 244, 206))

    row_y = sy + m(40)
    sx3 = [sw // 4, sw // 2, sw - sw // 4]
    _label(surf, "EQUIP", sx3[0], row_y - m(24), size=10)
    _label(surf, "EQUIPPED", sx3[1], row_y - m(24), size=10)
    _label(surf, "LOCKED", sx3[2], row_y - m(24), size=10)
    status_chip(surf, sx3[0], row_y, "EQUIP", ch, kind="equip")
    status_chip(surf, sx3[1], row_y, "EQUIPPED", ch, kind="equipped")
    price_chip(surf, sx3[2], row_y, "7,000", ch, ramp="A", state="locked")

    # ── a 'family line-up' row: the default gold price beside its siblings so
    #    the shared silhouette + double rim reads at a glance ──────────────────
    line_y = row_y + m(58)
    _label(surf, "FAMILY LINE-UP (default ramp A)", cx, line_y - m(20), size=11,
           col=(236, 214, 150))
    lx = [m(70), m(150), m(232), m(312)]
    price_chip(surf, lx[0], line_y + m(14), "1,500", ch, ramp="A", state="afford")
    status_chip(surf, lx[1], line_y + m(14), "EQUIP", ch, kind="equip")
    status_chip(surf, lx[2], line_y + m(14), "EQUIPPED", ch, kind="equipped")
    price_chip(surf, lx[3], line_y + m(14), "7,000", ch, ramp="A", state="locked")

    return surf, (LW, LH)


def main():
    surf, (LW, LH) = render_sheet()
    # render extra-large for SS-crisp review: downscale to 1.6x logical
    out_w, out_h = int(LW * 1.6), int(LH * 1.6)
    out = pygame.transform.smoothscale(surf, (out_w, out_h))
    path = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, path)
    print("SS =", SS, "device =", surf.get_size(), "-> saved", path)


if __name__ == "__main__":
    main()
