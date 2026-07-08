#!/usr/bin/env python3
"""
gem-cut-panel confirm_purchase_v5 round 2.

All five art-director mandatories addressed:
1. Disc rebuilt as bright tier-coloured gem well — CABO_LO/CABO_HI both
   well above lum 100, warm ambient fill, no dark hole.
2. Additive bloom radiates OUTWARD well past disc edge so glow bleeds
   continuously into card fill — no dark seam.
3. Disc core stays strongly tier-saturated to centre.
4. Tier word raised to ~35 px cap-height (minimum 26 px for long words) —
   dominates the top third.
5. Glow colour normalised to equal perceptual luminance (all tiers to
   lum ≈ 100) so the same bloom procedure produces matched brightness
   with a colour-swap only.
"""
import os
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import sys
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, price_chip, chip_body_stops, chip_body,
    _glyph_base, font, m, SS, thumb, _rim_light,
    GOLD_A_STOPS,
    GOLD_A_RIM_DARK as GOLD_RIM_DK,
    GOLD_A_RIM_BRIGHT as GOLD_RIM_BR,
)
from game.hud import _font
from game.draw import lerp_color, WHITE, NEAR_BLACK


# ── mandatory gloss_sweep patch: sheen via RGB magnitude, not source alpha ────
# BLEND_ADD ignores source alpha — using (v,v,v,255) keeps glow RGB-driven so
# the additive sheen stays small and tight rather than blowing out the crown.
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)


sc.gloss_sweep = _gloss_sweep_fixed


# ── tier palette (per brief; sky-bright gem/glow, not dark jewel tones) ───────
TIERS = [
    ("RARE",      "skin_ninja",
     {"gem": (108, 188, 252), "glow": (60, 140, 230),  "deep": (18, 44, 90)}),
    ("EPIC",      "skin_mummy",
     {"gem": (194, 122, 248), "glow": (150, 60, 220),  "deep": (44, 10, 80)}),
    ("LEGENDARY", "skin_astronaut",
     {"gem": (255, 202, 104), "glow": (220, 160, 40),  "deep": (90, 50, 0)}),
]
PRICE = {"RARE": "1,500", "EPIC": "6,000", "LEGENDARY": "15,000"}

POP_W, POP_H = 208, 300
CHAMFER = 21          # logical px — ~45-deg corner chamfer for the crystal silhouette
BEVEL_W = 7           # faceted frame band width, logical px
R_DISC   = 46         # disc radius, logical px
CY_DISC  = 152        # disc centre y from popup-body top, logical px

LX, LY = -0.7071, -0.7071   # top-left light for bevel facet value-stepping


# ── geometry ──────────────────────────────────────────────────────────────────
def octagon(x, y, w, h, c):
    """8-point chamfered rect: the gem-cut silhouette."""
    return [
        (x + c, y), (x + w - c, y),
        (x + w, y + c), (x + w, y + h - c),
        (x + w - c, y + h), (x + c, y + h),
        (x, y + h - c), (x, y + c),
    ]


def facet_value(a, b, cx, cy, dk, mid, hi):
    """Value-step one bevel quad from top-left light: outward normal dot LV
    maps shaded->mid->lit across the bright glass range."""
    mx, my = (a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy
    ml = math.hypot(mx, my) or 1
    d = (mx / ml) * LX + (my / ml) * LY
    f = (d + 1) / 2
    return lerp_color(lerp_color(dk, mid, min(1.0, f * 2)),
                      hi, max(0.0, (f - 0.5) * 2))


# ── glow normalisation ────────────────────────────────────────────────────────
def _lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def norm_glow_col(color, target=100.0):
    """Scale glow colour to target perceptual luminance so BLEND_ADD bloom
    yields equal visual brightness across all tiers with a colour-swap only.
    Target=100 is chosen so no channel clamps for any of the three tiers."""
    lum = _lum(color)
    if lum < 1:
        return color
    s = min(3.0, target / lum)
    return (min(255, int(color[0] * s)),
            min(255, int(color[1] * s)),
            min(255, int(color[2] * s)))


# ── disc primitives ───────────────────────────────────────────────────────────
def _bloom_outward(surf, cx, cy, r, glow, peak=55, layers=14):
    """BLEND_ADD rings that extend ~1.65× disc radius into the card fill.
    No dark seam can form because the glow bleeds continuously; the disc
    body (drawn after) simply sits within the already-glowing field."""
    ng = norm_glow_col(glow)
    bloom_r = int(r * 2.65)
    for i in range(layers, 0, -1):
        ri = int(bloom_r * i / layers)
        ai = int(peak * (1 - (i - 1) / layers) ** 1.8)
        if ai <= 0 or ri <= 0:
            continue
        g = pygame.Surface((ri * 2 + 2, ri * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*ng, ai), (ri + 1, ri + 1), ri)
        surf.blit(g, (cx - ri - 1, cy - ri - 1), special_flags=pygame.BLEND_ADD)


def _bright_gem_disc(surf, cx, cy, r, gem, glow, deep, skin_id):
    """Bright tier-coloured disc — the second-brightest zone on the card.

    Stack (bottom to top):
      bloom outward → bright radial body → skin → glass gloss → gem ring.

    cabo_lo (disc centre, lum > 200) and cabo_hi (disc rim, lum > 130) are
    both well above lum 100 for all three tiers, so the disc is never a dark
    hole regardless of tier."""

    # 1. Wide bloom first so the glow field is already in the card fill before
    #    the disc body lands — eliminates any possible dark gap at the rim.
    _bloom_outward(surf, cx, cy, r, glow)

    # 2. Bright radial disc body.
    #    cabo_lo = CENTRE (drawn last, topmost): gem lerped toward white
    #    cabo_hi = RIM (drawn first): gem-adjacent, stays strongly saturated
    cabo_lo = lerp_color(gem, (255, 255, 255), 0.48)   # centre lum ≈ 200–230
    cabo_hi = lerp_color(gem, glow, 0.22)              # rim  lum ≈ 133–196

    pad  = m(4)
    dsz  = r * 2 + pad * 2
    disc = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    cc   = r + pad
    for i in range(r, 0, -1):
        col = lerp_color(cabo_lo, cabo_hi, (i / r) ** 1.28)
        pygame.draw.circle(disc, (*col, 255), (cc, cc), i)

    # Thin inner-rim vignette so the skin silhouette reads against the bright
    # centre without flattening into it.
    vig = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    for i in range(r, int(r * 0.76), -1):
        a = int(55 * (1 - (i - r * 0.76) / (r * 0.24)))
        pygame.draw.circle(vig, (0, 0, 0, max(0, a)), (cc, cc), i, max(1, m(0.7)))
    disc.blit(vig, (0, 0))
    surf.blit(disc, (cx - cc, cy - cc))

    # 3. Skin thumbnail — rim-lit so it pops off the bright gem base.
    try:
        t  = thumb(skin_id, int(r * 1.5))
        rt = t.get_rect(center=(cx, cy))
        surf.blit(_rim_light(t, color=(255, 252, 240), alpha=160), rt.topleft,
                  special_flags=pygame.BLEND_ADD)
        surf.blit(t, rt)
    except Exception:
        # geometry stand-in if skin unavailable in this env
        pygame.draw.circle(surf, lerp_color(gem, (255, 255, 255), 0.35),
                           (cx, cy), r // 2)

    # 4. Soft additive glass gloss across the upper disc face (peak ≤ 28 so it
    #    adds sparkle without blowing out the bright base).
    gloss = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    for yy in range(r):
        hw = int(math.sqrt(max(0, r * r - yy * yy)))
        av = int(28 * (1 - yy / r) ** 1.6)
        if av <= 0 or hw <= 0:
            continue
        pygame.draw.line(gloss, (av, av, av, 255),
                         (cc - hw, cc - r + yy), (cc + hw, cc - r + yy))
    circ = pygame.Surface((dsz, dsz), pygame.SRCALPHA)
    pygame.draw.circle(circ, (255, 255, 255, 255), (cc, cc), r - m(1))
    gloss.blit(circ, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gloss, (cx - cc, cy - cc), special_flags=pygame.BLEND_ADD)

    # 5. Bright gem ring — well-lit edge, not a dark trench.
    ring_col = lerp_color(gem, (255, 255, 255), 0.52)
    pygame.draw.circle(surf, ring_col, (cx, cy), r, max(2, m(2.5)))
    # Thin accent line inset from the ring for a layered depth read.
    pygame.draw.circle(surf, lerp_color(deep, (0, 0, 0), 0.12),
                       (cx, cy), r - m(2), max(1, m(0.8)))


# ── popup card ────────────────────────────────────────────────────────────────
def render_popup(tier_word, skin, pal):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    x  = m(9)
    y  = m(9)
    w  = POP_W * SS - m(18)
    h  = POP_H * SS - m(18)
    c  = m(CHAMFER)
    bw = m(BEVEL_W)
    cx = x + w / 2
    cy = y + h / 2

    outer = octagon(x, y, w, h, c)
    inner = octagon(x + bw, y + bw, w - 2 * bw, h - 2 * bw, c)

    gem, glow, deep = pal["gem"], pal["glow"], pal["deep"]

    # ── card body: sky-bright gradient masked to octagon silhouette ───────────
    body_stops = [
        (0.00, lerp_color(gem, WHITE, 0.52)),
        (0.42, lerp_color(gem, WHITE, 0.12)),
        (1.00, lerp_color(gem, glow,  0.55)),
    ]
    body  = vgrad_stops(w, h, 0, body_stops, 255, gamma=1.05)
    omask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(omask, (255, 255, 255, 255),
                        [(px - x, py - y) for px, py in outer])
    body.blit(omask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # multi-layer octagon drop shadow (top-left light → shadow offset down)
    sh = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    for i in range(m(6), 0, -1):
        a = int(150 * (i / m(6)) ** 1.7 / m(6) * 2.6)
        if a <= 0:
            continue
        off_oct = octagon(x - i, y - i + m(3), w + 2 * i, h + 2 * i, c + i)
        pygame.draw.polygon(sh, (0, 0, 0, a), off_oct)
    big.blit(sh, (0, 0))
    big.blit(body, (x, y))

    # ── faceted bevel frame: 8 quads value-stepped by facing to the light ─────
    dk  = lerp_color(gem, glow, 0.72)
    mid = lerp_color(gem, WHITE, 0.10)
    hi  = lerp_color(gem, WHITE, 0.72)
    for i in range(8):
        a, b  = outer[i], outer[(i + 1) % 8]
        ib, ia = inner[(i + 1) % 8], inner[i]
        col = facet_value(a, b, cx, cy, dk, mid, hi)
        pygame.draw.polygon(big, col, [a, b, ib, ia])

    # glass crown sheen across upper half, masked to octagon
    sheen = pygame.Surface((w, h), pygame.SRCALPHA)
    for yy in range(int(h * 0.5)):
        av = int(70 * (1 - yy / (h * 0.5)) ** 1.5)
        pygame.draw.line(sheen, (255, 255, 255, av), (0, yy), (w, yy))
    sheen.blit(omask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(sheen, (x, y))

    # edge strokes: dark outer keyline + value-stepped inner rim
    lit = lerp_color(gem, WHITE, 0.85)
    shd = lerp_color(deep, NEAR_BLACK, 0.15)
    key = lerp_color(deep, NEAR_BLACK, 0.35)
    pygame.draw.polygon(big, key, outer, max(1, m(1.4)))
    pygame.draw.polygon(big, (*lerp_color(gem, WHITE, 0.55), 150), inner, max(1, m(0.8)))
    for i in range(8):
        a, b = inner[i], inner[(i + 1) % 8]
        col = facet_value(a, b, cx, cy, (*shd, 200), (*gem, 60), (*lit, 235))
        pygame.draw.line(big, col, a, b, max(1, m(1.4)))

    # ── 1. TIER WORD — top-third dominant focal ───────────────────────────────
    # Starts at 35 px cap-height; auto-shrinks only as far as 26 px so even
    # LEGENDARY stays clearly dominant. Tracking reduced from R1 so long words
    # fit at a bigger size. Saturated gem fill + dark keyline pops off the pale
    # glass crown.
    icx     = int(cx)
    tw_y    = y + m(40)
    sz      = 35
    tf      = font(sz)
    trk     = m(1.2)
    inner_w = w - 2 * bw - m(12)
    while _glyph_base(tier_word, tf, trk).get_width() > inner_w and sz > 26:
        sz -= 1
        tf  = font(sz)

    word_col = lerp_color(gem, WHITE, 0.06)
    word_kl  = lerp_color(deep, NEAR_BLACK, 0.08)
    plain_text(big, tier_word, tf, (icx, tw_y), word_col, shadow_a=0,
               tracking=trk, weight=m(1.5),
               keyline=word_kl, kw=m(1.2))

    # ── 2. DISC — bright gem well; second-brightest zone ──────────────────────
    dcx, dcy = icx, y + m(CY_DISC)
    _bright_gem_disc(big, dcx, dcy, m(R_DISC), gem, glow, deep, skin)

    # ── 3. PRICE + CONFIRM — foot row ─────────────────────────────────────────
    aff = (tier_word != "LEGENDARY")
    price_chip(big, icx, y + h - m(52), PRICE[tier_word], m(22), affordable=aff)
    _confirm_chip(big, icx, y + h - m(22), m(24), aff)

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


def _confirm_chip(surf, cx, cy, h, affordable):
    text = "CONFIRM"
    f    = font(h * 0.44 / SS)
    nw   = _glyph_base(text, f, m(1.4)).get_width()
    pad  = m(20)
    r    = pygame.Rect(cx - (nw + pad * 2) // 2, cy - h // 2, nw + pad * 2, h)
    if affordable:
        chip_body_stops(surf, r, h // 2, GOLD_A_STOPS, GOLD_RIM_DK, GOLD_RIM_BR,
                        gloss=64, gamma=1.04)
        col, kl = (54, 30, 4), None
    else:
        chip_body(surf, r, h // 2, (92, 98, 122), (50, 54, 76),
                  (14, 16, 28), (162, 170, 196), gloss=44)
        col, kl = (196, 202, 224), (20, 24, 40)
    plain_text(surf, text, f, r.center, col, shadow_a=0,
               tracking=m(1.4), weight=m(1.0), keyline=kl, kw=m(0.7))
    return r


# ── compose three-tier review canvas ─────────────────────────────────────────
GAP      = 22
CANVAS_W = GAP + 3 * (POP_W + GAP)
CANVAS_H = POP_H + 78
canvas   = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill((10, 12, 24))

title_f = _font(19, True)
tt = title_f.render(
    "confirm_purchase_v5  ·  gem-cut-panel  ·  round 2", True, (224, 228, 244))
canvas.blit(tt, tt.get_rect(midtop=(CANVAS_W // 2, 12)))

lab_f = _font(14, True)
for i, (word, skin, pal) in enumerate(TIERS):
    pop = render_popup(word, skin, pal)
    px  = GAP + i * (POP_W + GAP)
    py  = 50
    canvas.blit(pop, (px, py))
    lt = lab_f.render(word, True, lerp_color(pal["gem"], WHITE, 0.25))
    canvas.blit(lt, lt.get_rect(midtop=(px + POP_W // 2, py + POP_H + 6)))

OUT = "/home/user/skybit/docs/confirm_purchase_v5/gem-cut-panel/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
print("saved", OUT, canvas.get_size())
