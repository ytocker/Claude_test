"""
CONSTELLATION store — CARD CHASSIS element loop (round 1).

Scope: the rounded panel that HOLDS an item. NOT the cabochon/gem/chip contents
(separate loops) — those are drawn here only as labelled placeholder boxes so the
three-band internal layout reads. The chassis must look like a lit, tactile object
floating above the nebula bg: a panel body gradient, a clearly DEFINED edge (a dark
outer keyline UNDER a bright top-left bevel, authored wide enough to survive the SS
downscale), a top gloss sheen, a bottom-right contact/AO shadow, and a soft outer
drop shadow. The EQUIPPED state adds a clean gold frame + edge halo around the whole
card. Strict three-band layout: cabochon lane -> name lane -> chip lane, each in its
own clear lane with generous padding.

Pipeline reused verbatim from docs/store_redesign/constellation_hi/render_hi.py: author
resolution-independently, render at SS=4, ONE smoothscale down. Both build targets safe
(pure pygame, no numpy / no desktop- or browser-only API).
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


# ── supersample (THE crispness lever — identical to the reference pipeline) ───
SS = 4
DW, DH = W * SS, H * SS


def m(v):
    return int(round(v * SS))


def font(size):
    return _font(max(1, int(round(size * SS))), True)


def _stamp_bold(base, weight):
    """Faux-bold: ring-stamp the glyph so strokes grow evenly without filling
    counters. The project ships only the Bold ttf; authored 'thicker' is this."""
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


# ── palette (CONSTELLATION DNA, locked by THEME.md) ───────────────────────────
BG_STOPS = [
    (0.00, (6, 7, 24)),
    (0.30, (11, 11, 40)),
    (0.55, (18, 16, 58)),
    (0.78, (26, 20, 72)),
    (1.00, (14, 12, 46)),
]
NEBULA_GLOW = (70, 60, 150)
GOLD = _GOLD_BRIGHT
GOLD_PALE = _GOLD_PALE
GOLD_DEEP = _GOLD_DEEP

CARD_T = (28, 30, 70)            # card body top (lit)
CARD_B = (12, 13, 38)            # card body bottom (shaded)
CARD_RING_DEEP = (58, 48, 22)    # bright bevel deep edge
CARD_RING_BRIGHT = (236, 202, 116)
NAME_COL = (246, 240, 216)


# =============================================================================
# Primitives (SS-aware, device-px) — same recipes as the reference pipeline so
# the chassis sits in the same lit world as every sibling element.
# =============================================================================

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


def vgrad(w, h, radius, top, bot, alpha=255, gamma=1.0):
    body = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        t = (y / max(1, h - 1)) ** gamma
        c = lerp_color(top, bot, t)
        pygame.draw.line(body, (*c, alpha), (0, y), (w - 1, y))
    if radius > 0:
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return body


def soft_glow(surf, cx, cy, radius, color, peak_alpha, layers=8):
    for i in range(layers, 0, -1):
        r = int(radius * i / layers)
        a = int(peak_alpha * (1 - (i - 1) / layers) ** 1.8)
        if r <= 0 or a <= 0:
            continue
        g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*color, a), (r + 1, r + 1), r)
        surf.blit(g, (cx - r - 1, cy - r - 1), special_flags=pygame.BLEND_ADD)


def drop_shadow(surf, rect, radius, blur, alpha, dy):
    """Multi-layer blurred outer shadow, offset DOWN (top-left light source) so
    the card reads as floating above the nebula, not painted on it."""
    for i in range(blur, 0, -1):
        a = int(alpha * (i / blur) ** 1.7 / blur * 2.4)
        if a <= 0:
            continue
        r = pygame.Rect(rect.x - i, rect.y - i + dy, rect.w + 2 * i, rect.h + 2 * i)
        s = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, a), s.get_rect(), border_radius=radius + i)
        surf.blit(s, r.topleft)


def top_sheen(surf, rect, radius, h, peak=46):
    """Glossy top highlight across the upper portion of a panel (the lit gloss)."""
    sheen = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    for y in range(h):
        pygame.draw.line(sheen, (255, 255, 255, int(peak * (1 - y / h) ** 1.3)),
                         (0, y), (rect.w, y))
    sm = pygame.Surface((rect.w, h), pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(),
                     border_top_left_radius=radius, border_top_right_radius=radius)
    sheen.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sheen, rect.topleft)


def contact_shadow(surf, rect, radius, depth, alpha=90):
    """Inner ambient-occlusion shadow hugging the bottom + right inner edges."""
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


def bevel_rim(surf, rect, radius, deep, bright, w):
    """Fine emboss: a dark outer keyline + a bright top-left inner stroke."""
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


def plain_text(surf, txt, font_obj, center, color, shadow_a=150, tracking=0,
               weight=None, keyline=None, kw=None):
    base = font_obj.render(txt, True, WHITE)
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


# ── background (shared night-sky canvas) ──────────────────────────────────────
_star_field = None


def _build_static_bg():
    global _star_field
    rnd = __import__("random").Random(70)
    stars = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for n, rmin, rmax, amin, amax in ((180, 0.4, 0.9, 30, 90),
                                       (70, 0.9, 1.6, 70, 150),
                                       (24, 1.4, 2.6, 130, 220)):
        for _ in range(n):
            x = rnd.randint(0, DW)
            y = rnd.randint(0, DH)
            r = m(rnd.uniform(rmin, rmax))
            a = rnd.randint(amin, amax)
            tint = rnd.choice([(255, 252, 240), (220, 226, 255), (255, 240, 210)])
            pygame.draw.circle(stars, (*tint, a), (x, y), max(1, int(r)))
    _star_field = stars


def draw_bg(surf):
    surf.blit(multistop_v(DW, DH, BG_STOPS), (0, 0))
    soft_glow(surf, DW // 2, int(DH * 0.42), m(200), NEBULA_GLOW, 60, layers=10)
    vig = pygame.Surface((DW, DH), pygame.SRCALPHA)
    for y in range(DH):
        d = abs(y - DH * 0.5) / (DH * 0.5)
        a = int(70 * d ** 1.5)
        pygame.draw.line(vig, (0, 0, 6, a), (0, y), (DW, y))
    surf.blit(vig, (0, 0))
    surf.blit(_star_field, (0, 0), special_flags=pygame.BLEND_ADD)


# =============================================================================
# Card chassis — the deliverable. The contents (cabochon/gem/chip) are drawn as
# labelled placeholder boxes only; their FINISH is the job of other loops.
# =============================================================================
CARD_W, CARD_H = 165, 99
CARD_RAD = 17

# Three-band internal layout. Generous, lane-disjoint padding so the chassis
# never crowds whatever content the other loops drop in. Bands are anchored from
# the panel top + a uniform inner inset so siblings can lay out against the same
# grid.
PAD = 11                 # uniform inner inset from the panel edge
BAND_A_H = 44            # cabochon lane (tallest — the hero sits here)
BAND_B_H = 16            # name lane
BAND_C_H = 24            # chip lane
LANE_GAP = 2             # whisper gap between lanes (the gold rule lives in B)


def _lanes(rect):
    """Return the three lane rects, top to bottom, inset by PAD. Strict: every
    lane is disjoint, so content loops can't accidentally overlap."""
    inner_x = rect.x + m(PAD)
    inner_w = rect.w - 2 * m(PAD)
    y = rect.y + m(PAD)
    a = pygame.Rect(inner_x, y, inner_w, m(BAND_A_H))
    y = a.bottom + m(LANE_GAP)
    b = pygame.Rect(inner_x, y, inner_w, m(BAND_B_H))
    y = b.bottom + m(LANE_GAP)
    c = pygame.Rect(inner_x, y, inner_w, m(BAND_C_H))
    return a, b, c


def _placeholder(surf, r, label, tint):
    """A clearly-labelled dashed placeholder for content owned by another loop.
    Deliberately flat + neutral so it reads as 'reserved lane', not finished art."""
    box = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(box, (*tint, 40), box.get_rect(), border_radius=m(6))
    surf.blit(box, r.topleft)
    # dashed contour so it never looks like a finished filled chip
    dash = m(6)
    col = (*tint, 150)
    x = r.x
    while x < r.right:
        pygame.draw.line(surf, col, (x, r.y), (min(x + dash, r.right), r.y), max(1, m(0.8)))
        pygame.draw.line(surf, col, (x, r.bottom), (min(x + dash, r.right), r.bottom), max(1, m(0.8)))
        x += dash * 2
    y = r.y
    while y < r.bottom:
        pygame.draw.line(surf, col, (r.x, y), (r.x, min(y + dash, r.bottom)), max(1, m(0.8)))
        pygame.draw.line(surf, col, (r.right, y), (r.right, min(y + dash, r.bottom)), max(1, m(0.8)))
        y += dash * 2
    plain_text(surf, label, font(8), r.center, (*tint, 255)[:3], shadow_a=120,
               weight=m(0.6))


# ── finish recipes: 5 distinct chassis treatments ────────────────────────────
# Each is a genuinely different take on the SAME chassis brief (body finish +
# edge treatment), all obeying the one-light-source + defined-edge rules.

def _finish_classic(surf, rect, rad):
    """A — the THEME baseline: indigo body, dark keyline under a warm-gold bevel,
    top gloss, bottom-right AO. The 'house' look the other loops assume."""
    surf.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(surf, rect, rad, m(30), peak=62)
    contact_shadow(surf, rect, rad, m(7), alpha=95)
    pygame.draw.rect(surf, (4, 5, 16), rect, width=max(1, m(2.0)), border_radius=rad)
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 235), w=max(1, m(2.0)))


def _finish_doubleframe(surf, rect, rad):
    """B — recessed inner-tray: same body, but a second inset gold hairline frame
    inside the bevel reads as a routed tray that the content sits down INTO.
    Stronger floating-object read; the edge is unmistakable."""
    surf.blit(vgrad(rect.w, rect.h, rad, CARD_T, CARD_B, 252, gamma=1.15), rect.topleft)
    top_sheen(surf, rect, rad, m(32), peak=66)
    contact_shadow(surf, rect, rad, m(7), alpha=98)
    pygame.draw.rect(surf, (3, 4, 14), rect, width=max(1, m(2.2)), border_radius=rad)
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 240), w=max(1, m(2.0)))
    # inset hairline tray frame: dark groove then a fine pale-gold lip
    inner = rect.inflate(-m(7), -m(7))
    irad = max(1, rad - m(5))
    pygame.draw.rect(surf, (6, 7, 20), inner, width=max(1, m(1.0)), border_radius=irad)
    lip = inner.inflate(-m(1.4), -m(1.4))
    hl = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(hl, (*GOLD_PALE, 150), lip.move(-rect.x, -rect.y),
                     width=max(1, m(0.9)), border_radius=max(1, irad - m(1)))
    grad = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        grad.fill((255, 255, 255, int(255 * (1 - y / rect.h) ** 1.5)), (0, y, rect.w, 1))
    hl.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(hl, rect.topleft)


def _finish_warmpanel(surf, rect, rad):
    """C — warmer 'aged-parchment-indigo' body (a touch of violet warmth lifted
    top-left) with a THICKER two-step keyline (near-black + a faint cool rim) so
    the silhouette pops hardest against the nebula. Richest body luminosity."""
    top = (40, 38, 86)
    bot = (14, 14, 42)
    surf.blit(vgrad(rect.w, rect.h, rad, top, bot, 252, gamma=1.22), rect.topleft)
    # a restrained top-left body bloom so the lit corner glows softly (not a hot
    # blob): low peak, kept up in the corner away from the content lane.
    bloom = pygame.Surface(rect.size, pygame.SRCALPHA)
    soft_glow(bloom, int(rect.w * 0.22), int(rect.h * 0.18), m(26),
              (108, 104, 188), 30, layers=7)
    bm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(bm, (255, 255, 255, 255), bm.get_rect(), border_radius=rad)
    bloom.blit(bm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(bloom, rect.topleft, special_flags=pygame.BLEND_ADD)
    top_sheen(surf, rect, rad, m(34), peak=70)
    contact_shadow(surf, rect, rad, m(8), alpha=104)
    # two-step keyline: a wide near-black contact ring, then a faint cool rim, so
    # the dark edge reads as genuine depth, not a single hard line.
    pygame.draw.rect(surf, (2, 3, 12), rect, width=max(1, m(2.6)), border_radius=rad)
    pygame.draw.rect(surf, (30, 32, 64), rect.inflate(-m(2.6), -m(2.6)),
                     width=max(1, m(1.0)), border_radius=max(1, rad - m(2)))
    bevel_rim(surf, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 240), w=max(1, m(2.2)))


CHASSIS = {
    "A · CLASSIC": _finish_classic,
    "B · INNER TRAY": _finish_doubleframe,
    "C · WARM GLOW": _finish_warmpanel,
}


def _equipped_frame(surf, rect, rad):
    """EQUIPPED state: a clean gold frame + an additive edge halo around the WHOLE
    card so the active item glows as the hero. Halo bleeds outward (lit), the
    frame stroke stays crisp on the keyline."""
    halo = pygame.Surface((rect.w + m(20), rect.h + m(20)), pygame.SRCALPHA)
    for k in range(7, 0, -1):
        pygame.draw.rect(halo, (*GOLD, int(26 * k / 7)),
                         (m(10) - k * m(1.4), m(10) - k * m(1.4),
                          rect.w + 2 * k * m(1.4), rect.h + 2 * k * m(1.4)),
                         width=max(1, m(1.5)), border_radius=rad + int(k * m(1.4)))
    surf.blit(halo, (rect.x - m(10), rect.y - m(10)), special_flags=pygame.BLEND_ADD)
    # the gold frame: a deep contact under-stroke + a bright gold lip on top so
    # the frame itself reads beveled, matching the one-light rule.
    pygame.draw.rect(surf, (96, 62, 14), rect.inflate(m(1), m(1)),
                     width=max(1, m(3.0)), border_radius=rad + m(1))
    pygame.draw.rect(surf, GOLD, rect, width=max(1, m(2.2)), border_radius=rad)
    bevel_rim(surf, rect, rad, (96, 62, 14), (*GOLD_PALE, 250), w=max(1, m(1.4)))


def draw_card(surf, rect, finish, equipped, label_bands=True):
    rad = m(CARD_RAD)
    # DEPTH: a soft multi-layer drop shadow so the card floats above the nebula
    drop_shadow(surf, rect, rad, blur=m(9), alpha=165, dy=m(4))
    CHASSIS[finish](surf, rect, rad)

    a, b, c = _lanes(rect)
    if label_bands:
        # BAND A — cabochon lane (the glass dome + skin go here; another loop)
        ar = pygame.Rect(0, 0, m(BAND_A_H - 4), m(BAND_A_H - 4))
        ar.center = a.center
        _placeholder(surf, ar, "CABOCHON", (150, 170, 220))
        # corner-gem reservation (top-right of band A), drawn as a tiny marker so
        # the chassis shows it leaves room without owning the gem art.
        gem = pygame.Rect(0, 0, m(15), m(15))
        gem.center = (rect.right - m(15), rect.y + m(15))
        _placeholder(surf, gem, "GEM", (210, 190, 120))
        # BAND B — name lane
        _placeholder(surf, b.inflate(-m(2), -m(1)), "NAME", (230, 224, 200))
        # BAND C — chip lane
        chip = pygame.Rect(0, 0, c.w - m(20), c.h)
        chip.center = c.center
        _placeholder(surf, chip, "PRICE / EQUIP CHIP", (230, 200, 120))

    if equipped:
        _equipped_frame(surf, rect, rad)


# =============================================================================
# Compose the round-1 review sheet
# =============================================================================
def render_sheet():
    # A column per finish: a NORMAL card (top) + the EQUIPPED treatment (bottom),
    # all on the shared night-sky bg, at a large SS-crisp scale.
    cols = list(CHASSIS.keys())
    pad = m(26)
    gut_x = m(30)
    gut_y = m(58)
    cw, ch = m(CARD_W), m(CARD_H)
    head_h = m(48)
    sub_h = m(26)

    sheet_w = pad * 2 + cw * len(cols) + gut_x * (len(cols) - 1)
    sheet_h = head_h + pad + (ch * 2 + gut_y) + pad + sub_h
    surf = pygame.Surface((sheet_w, sheet_h))
    draw_bg_into(surf)

    plain_text(surf, "STORE — ITEM CARD CHASSIS", font(15),
               (sheet_w // 2, head_h // 2 + m(2)), (252, 232, 168),
               shadow_a=150, tracking=m(2), weight=m(1.0),
               keyline=(40, 26, 6), kw=m(1.0))

    y0 = head_h + pad
    for i, name in enumerate(cols):
        x = pad + i * (cw + gut_x)
        # NORMAL
        r1 = pygame.Rect(x, y0, cw, ch)
        draw_card(surf, r1, name, equipped=False)
        plain_text(surf, name, font(10), (r1.centerx, r1.y - m(13)),
                   (210, 216, 240), shadow_a=130, weight=m(0.7))
        # EQUIPPED (same finish, gold frame + halo)
        r2 = pygame.Rect(x, y0 + ch + gut_y, cw, ch)
        draw_card(surf, r2, name, equipped=True)
        plain_text(surf, "EQUIPPED", font(9), (r2.centerx, r2.y - m(12)),
                   (255, 222, 130), shadow_a=130, weight=m(0.8), tracking=m(1))

    plain_text(surf, "three-band layout: CABOCHON / NAME / CHIP  ·  contents are placeholders (other loops)",
               font(8.5), (sheet_w // 2, sheet_h - sub_h // 2),
               (180, 188, 214), shadow_a=120, weight=m(0.6))
    return surf


def draw_bg_into(surf):
    """Nebula bg scaled to whatever sheet size we composed (the static starfield
    is built at full DW×DH, so blit a cropped/scaled copy that covers the sheet)."""
    w, h = surf.get_size()
    surf.blit(multistop_v(w, h, BG_STOPS), (0, 0))
    soft_glow(surf, w // 2, int(h * 0.46), int(w * 0.6), NEBULA_GLOW, 60, layers=10)
    stars = pygame.transform.smoothscale(_star_field, (w, h))
    surf.blit(stars, (0, 0), special_flags=pygame.BLEND_ADD)
    vig = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        d = abs(y - h * 0.5) / (h * 0.5)
        pygame.draw.line(vig, (0, 0, 6, int(70 * d ** 1.5)), (0, y), (w, y))
    surf.blit(vig, (0, 0))


def main():
    _build_static_bg()
    dev = render_sheet()
    dw, dh = dev.get_size()
    # downscale (the crispness lever) but keep ~1.7x logical so the cards read
    # large + crisp for close inspection on the review sheet.
    out = pygame.transform.smoothscale(dev, (int(dw / SS * 1.7), int(dh / SS * 1.7)))
    path = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, path)
    print("SS =", SS)
    print("saved", path, out.get_size())


if __name__ == "__main__":
    main()
