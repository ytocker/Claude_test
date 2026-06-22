"""
CONSTELLATION store — CONTROLS + BUY MODAL element loop.

Covers the action/nav chrome that frames the store: the BACK pill, the
`< PAGE 1/3 >` page controls, and the buy-confirmation MODAL (the money
screen). Everything is authored resolution-independently and rendered at
SS = 4, then one smoothscale down — the shared crispness lever locked in
THEME.md. The pipeline + every material primitive (vgrad, bevel_rim,
gloss_sweep, drop_shadow, coin_glyph, cabochon, facet_gem, faux-bold type)
is reused verbatim from the reference render_hi.py so this element reads as
the same screen as its 7 siblings.

This sheet shows the BACK pill + page controls once, then THREE modal panel /
CTA treatments side by side over the shared night-sky bg, all using the real
epic item skin_phoenix. Files only — no commit, no integration.

Both build targets safe: pure pygame, no numpy, no desktop/browser-only API.
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

# Reuse the locked reference pipeline + primitives so this element is, by
# construction, the same material language as the rest of the store.
_HI = os.path.abspath(os.path.join(_HERE, "..", "..", "constellation_hi"))
if _HI not in sys.path:
    sys.path.insert(0, _HI)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import render_hi as R
from render_hi import (
    m, font, vgrad, gloss_sweep, top_sheen, contact_shadow, bevel_rim,
    drop_shadow, soft_glow, coin_glyph, cabochon, cabochon_glass, facet_gem,
    blit_thumb, gold_rule, plain_text, gradient_text, multistop_v,
    price_chip, _glyph_base, _draw_qmark,
)
from render_hi import (
    GOLD, GOLD_PALE, GOLD_DEEP, CABO_LO, CABO_HI, CREAM, RARITY, MYSTERY,
    BG_STOPS, NEBULA_GLOW,
)
from game.draw import lerp_color, NEAR_BLACK
from game import store_catalog

ITEM = "skin_phoenix"          # real epic item, per the brief
TIER = store_catalog.rarity(ITEM)
PAL = RARITY[TIER]
NAME = store_catalog.name(ITEM)
PRICE = store_catalog.cost(ITEM)


# =============================================================================
# BACK pill — premium gradient gold/dark pill with a chevron + defined edge.
# Authored as a standalone so the element can be reviewed in isolation; the
# generous bottom margin is expressed by the caller positioning it.
# =============================================================================
def back_pill(surf, cx, cy, w=172, h=40, gold=False):
    """The BACK control. Two finishes: the default dark-indigo gradient (sits
    quietly at the bottom of the store) and an optional warm-gold finish for
    contexts that want it louder. Both carry the locked defined edge: a dark
    outer keyline UNDER a bright top-left bevel."""
    r = pygame.Rect(0, 0, m(w), m(h))
    r.center = (cx, cy)
    rad = r.h // 2
    drop_shadow(surf, r, rad, blur=m(6), alpha=140, dy=m(3))
    if gold:
        surf.blit(vgrad(r.w, r.h, rad, (255, 214, 104), (196, 130, 32),
                        255, gamma=1.06), r.topleft)
        chev_col = (74, 44, 8)
        txt_col = (60, 34, 6)
        key = None
        bev_dark = (92, 54, 10)
    else:
        surf.blit(vgrad(r.w, r.h, rad, (36, 34, 74), (16, 16, 40), 250),
                  r.topleft)
        chev_col = GOLD_PALE
        txt_col = GOLD_PALE
        key = (40, 26, 6)
        bev_dark = lerp_color(GOLD, NEAR_BLACK, 0.42)
    top_sheen(surf, r, rad, m(16), peak=52)
    contact_shadow(surf, r, rad, m(4), alpha=85)
    pygame.draw.rect(surf, (4, 5, 16), r, width=max(1, m(1.8)), border_radius=rad)
    bevel_rim(surf, r, rad, bev_dark, (*GOLD, 222), w=max(1, m(1.6)))
    # left chevron in a small recessed cap so it reads as an affordance
    cxx = r.x + m(26)
    if gold:
        pygame.draw.lines(surf, (255, 244, 206), False,
                          [(cxx + m(6), r.centery - m(8)),
                           (cxx - m(4), r.centery),
                           (cxx + m(6), r.centery + m(8))], max(1, m(3)))
    pygame.draw.lines(surf, chev_col, False,
                      [(cxx + m(5), r.centery - m(7)),
                       (cxx - m(3), r.centery),
                       (cxx + m(5), r.centery + m(7))], max(1, m(2.6)))
    plain_text(surf, "BACK", font(18), (r.centerx + m(9), r.centery),
               txt_col, shadow_a=160, weight=m(1.0),
               keyline=key, kw=m(1.0) if key else None, tracking=m(1))
    return r


# =============================================================================
# Page controls — `< PAGE 1/3 >` with beveled arrow buttons as comfy tap
# targets. Arrows are ~40x30 logical (≈ a 44px physical target), separated
# from the label, double-rimmed, lit top-left.
# =============================================================================
def arrow_button(surf, cx, cy, glyph, w=40, h=30):
    r = pygame.Rect(0, 0, m(w), m(h))
    r.center = (cx, cy)
    rad = m(13)
    drop_shadow(surf, r, rad, blur=m(4), alpha=100, dy=m(2))
    surf.blit(vgrad(r.w, r.h, rad, (60, 46, 26), (26, 19, 11), 255), r.topleft)
    top_sheen(surf, r, rad, m(10), peak=58)
    contact_shadow(surf, r, rad, m(3), alpha=70)
    pygame.draw.rect(surf, (12, 10, 4), r, width=max(1, m(1.5)), border_radius=rad)
    bevel_rim(surf, r, rad, (60, 40, 12), (*GOLD_PALE, 222), w=max(1, m(1.2)))
    plain_text(surf, glyph, font(16), (cx, cy - m(1)), GOLD_PALE, shadow_a=0,
               weight=m(1.0))
    return r


def page_controls(surf, cx, cy, page=1, total=3, spread=150):
    """Centered `< PAGE n/total >`: the two arrow buttons flank a loud
    gradient-gold page label. spread = logical px between the arrow centres."""
    plain_text(surf, f"PAGE  {page} / {total}", font(13), (cx, cy), GOLD_PALE,
               shadow_a=150, weight=m(0.9), keyline=(10, 10, 22), kw=m(0.8),
               tracking=m(1))
    arrow_button(surf, cx - m(spread // 2), cy, "<")
    arrow_button(surf, cx + m(spread // 2), cy, ">")


# =============================================================================
# Modal building blocks shared by all variants
# =============================================================================
def _scrim(surf):
    """~70% flat dark scrim so the panel reads as the only lit object."""
    s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    s.fill((3, 4, 10, 180))                       # ~70% perceived dim
    surf.blit(s, (0, 0))


def _panel_chassis(surf, panel, rad, double_edge=True):
    """The modal panel body: indigo gradient, top gloss, bottom-right AO, and
    the locked DEFINED EDGE. double_edge draws a second concentric gold rule
    inset from the bevel — the 'double-gold edge' the brief calls for."""
    drop_shadow(surf, panel, rad, blur=m(13), alpha=205, dy=m(7))
    surf.blit(vgrad(panel.w, panel.h, rad, (30, 30, 70), (12, 12, 36),
                    255, gamma=1.15), panel.topleft)
    top_sheen(surf, panel, rad, m(36), peak=58)
    contact_shadow(surf, panel, rad, m(9), alpha=98)
    pygame.draw.rect(surf, (3, 4, 14), panel, width=max(1, m(2)),
                     border_radius=rad)
    bevel_rim(surf, panel, rad, lerp_color(GOLD, NEAR_BLACK, 0.4),
              (*GOLD, 240), w=max(1, m(2.0)))
    if double_edge:
        inner = panel.inflate(-m(11), -m(11))
        pygame.draw.rect(surf, (*GOLD_DEEP, 150), inner, width=max(1, m(1)),
                         border_radius=rad - m(5))
        pygame.draw.rect(surf, (*GOLD_PALE, 80), inner.inflate(m(2), m(2)),
                         width=max(1, m(0.8)), border_radius=rad - m(4))


def _stage(surf, cx, cy, R_disc, gem_r=10, seat_deg=45):
    """The glass-cabochon stage: tier aura, domed well, rim-lit phoenix under
    glass, and the rarity gem SEATED on the dome rim (not floating)."""
    soft_glow(surf, cx, cy, R_disc + m(5), PAL["glow"], 46, layers=8)
    cabochon(surf, cx, cy, R_disc, CABO_LO, CABO_HI, ring=PAL["gem"], ring_a=55)
    blit_thumb(surf, ITEM, cx, cy, R_disc * 1.5)
    cabochon_glass(surf, cx, cy, R_disc, tint=PAL["gem"])
    # gem seated ON the rim at seat_deg up-right: place its centre right on the
    # bezel circle so it reads as set into the gold, never adrift.
    ang = math.radians(seat_deg)
    gx = int(cx + R_disc * math.cos(ang))
    gy = int(cy - R_disc * math.sin(ang))
    facet_gem(surf, gx, gy, gem_r, PAL["gem"], PAL["deep"])


def _buy_button(surf, rect, label="BUY", glow=True, inner=True, coin=False):
    """The primary CTA: bright gradient gold, gloss sweep, optional outer halo
    + subtle inner top glow, dark numerals/label. Defined gold edge."""
    rad = rect.h // 2
    if glow:
        g = pygame.Surface((rect.w + m(16), rect.h + m(16)), pygame.SRCALPHA)
        for k in range(6, 0, -1):
            pygame.draw.rect(g, (*GOLD, int(30 * k / 6)),
                             (m(8) - k * m(1.4), m(8) - k * m(1.4),
                              rect.w + 2 * k * m(1.4), rect.h + 2 * k * m(1.4)),
                             border_radius=rad + int(k * m(1.4)))
        surf.blit(g, (rect.x - m(8), rect.y - m(8)), special_flags=pygame.BLEND_ADD)
    drop_shadow(surf, rect, rad, blur=m(3), alpha=105, dy=m(2))
    surf.blit(vgrad(rect.w, rect.h, rad, (255, 220, 110), (200, 132, 32),
                    gamma=1.06), rect.topleft)
    gloss_sweep(surf, rect, rad, peak=152)
    if inner:
        ig = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        soft_glow(ig, rect.w // 2, int(rect.h * 0.32), int(rect.w * 0.42),
                  (255, 250, 220), 92, layers=6)
        im = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(im, (255, 255, 255, 255), im.get_rect(), border_radius=rad)
        ig.blit(im, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(ig, rect.topleft, special_flags=pygame.BLEND_ADD)
    pygame.draw.rect(surf, (90, 54, 10), rect, width=max(1, m(1.6)),
                     border_radius=rad)
    bevel_rim(surf, rect, rad, (90, 54, 10), (*GOLD_PALE, 235), w=max(1, m(1.4)))
    if coin:
        cd = int(rect.h * 0.5)
        f = font(15)
        lw = _glyph_base(label, f, 0).get_width()
        gapc = m(6)
        tot = cd + gapc + lw
        x0 = rect.centerx - tot // 2
        coin_glyph(surf, x0 + cd // 2, rect.centery, cd // 2, rim=(118, 72, 14))
        plain_text(surf, label, f, (x0 + cd + gapc + lw // 2, rect.centery),
                   (52, 30, 6), shadow_a=0, weight=m(1.0))
    else:
        plain_text(surf, label, font(17), rect.center, (52, 30, 6), shadow_a=0,
                   weight=m(1.0), tracking=m(1))


def _cancel_button(surf, rect, label="CANCEL"):
    """Secondary control: one value step lighter than the panel so it is
    clearly separate, but never competes with BUY. Same edge finish family."""
    rad = rect.h // 2
    drop_shadow(surf, rect, rad, blur=m(3), alpha=95, dy=m(2))
    surf.blit(vgrad(rect.w, rect.h, rad, (86, 82, 106), (52, 48, 70)), rect.topleft)
    top_sheen(surf, rect, rad, m(14), peak=46)
    contact_shadow(surf, rect, rad, m(3), alpha=70)
    pygame.draw.rect(surf, (16, 16, 28), rect, width=max(1, m(1.6)),
                     border_radius=rad)
    bevel_rim(surf, rect, rad, (16, 16, 28), (190, 186, 206, 220), w=max(1, m(1.2)))
    plain_text(surf, label, font(15), rect.center, CREAM, shadow_a=130,
               weight=m(0.9), keyline=(14, 14, 26), kw=m(0.9), tracking=m(1))


# =============================================================================
# Three modal treatments. Each owns a panel rect; the caller blits over bg.
# =============================================================================
def modal_v1_royal(surf, panel):
    """V1 ROYAL — the canonical centered panel. Symmetric BUY / CANCEL pair
    (BUY on the right, primary). Clean vertical hierarchy with a soft gold rule
    under the heading and a single-gradient price chip."""
    rad = m(20)
    _panel_chassis(surf, panel, rad, double_edge=True)
    cx = panel.centerx
    plain_text(surf, "CONFIRM PURCHASE", font(14), (cx, panel.y + m(30)),
               GOLD_PALE, shadow_a=150, tracking=m(1.4), weight=m(0.95),
               keyline=(10, 10, 24), kw=m(0.9))
    gold_rule(surf, panel.x + m(30), panel.right - m(30), panel.y + m(50),
              GOLD, peak=180)
    _stage(surf, cx, panel.y + m(112), m(44))
    plain_text(surf, NAME, font(21), (cx, panel.y + m(186)), GOLD, shadow_a=160,
               weight=m(1.0), keyline=(60, 36, 8), kw=m(1.1), tracking=m(1))
    plain_text(surf, TIER.upper(), font(11), (cx, panel.y + m(207)), PAL["gem"],
               shadow_a=130, tracking=m(1.4), weight=m(0.7))
    price_chip(surf, cx, panel.y + m(236), f"{PRICE:,}", m(32), variant=1,
               affordable=True)
    bw, bh, gut = m(108), m(44), m(16)
    by = panel.bottom - m(36)
    nx = cx - (bw * 2 + gut) // 2
    _cancel_button(surf, pygame.Rect(nx, by - bh // 2, bw, bh))
    _buy_button(surf, pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh))


def modal_v2_weighted(surf, panel):
    """V2 WEIGHTED CTA — the CTA-best-practice layout: BUY gets ~60% of the
    button row width (the dominant primary), CANCEL ~40% as a quiet pill. The
    price is fused into a heavier 'tag' chip and the heading sits on a recessed
    gold ribbon plate so the money line is unmistakable."""
    rad = m(20)
    _panel_chassis(surf, panel, rad, double_edge=True)
    cx = panel.centerx
    # recessed heading ribbon plate
    plate = pygame.Rect(panel.x + m(22), panel.y + m(18), panel.w - m(44), m(34))
    surf.blit(vgrad(plate.w, plate.h, plate.h // 2, (20, 20, 50), (10, 10, 30)),
              plate.topleft)
    pygame.draw.rect(surf, (3, 4, 14), plate, width=max(1, m(1.4)),
                     border_radius=plate.h // 2)
    pygame.draw.rect(surf, (*GOLD_DEEP, 170), plate.inflate(-m(2), -m(2)),
                     width=max(1, m(0.9)), border_radius=plate.h // 2)
    plain_text(surf, "CONFIRM PURCHASE", font(13), plate.center, GOLD_PALE,
               shadow_a=140, tracking=m(1.4), weight=m(0.95),
               keyline=(10, 10, 24), kw=m(0.8))
    _stage(surf, cx, panel.y + m(112), m(44))
    plain_text(surf, NAME, font(21), (cx, panel.y + m(186)), GOLD, shadow_a=160,
               weight=m(1.0), keyline=(60, 36, 8), kw=m(1.1), tracking=m(1))
    plain_text(surf, TIER.upper(), font(11), (cx, panel.y + m(207)), PAL["gem"],
               shadow_a=130, tracking=m(1.4), weight=m(0.7))
    price_chip(surf, cx, panel.y + m(236), f"{PRICE:,}", m(34), variant=1,
               affordable=True)
    # weighted button row: CANCEL ~40%, BUY ~60%, 8px+ gap
    row_w = panel.w - m(44)
    gut = m(14)
    bh = m(46)
    cw = int((row_w - gut) * 0.40)
    bw = row_w - gut - cw
    rx = panel.x + m(22)
    by = panel.bottom - m(38)
    _cancel_button(surf, pygame.Rect(rx, by - bh // 2, cw, bh))
    _buy_button(surf, pygame.Rect(rx + cw + gut, by - bh // 2, bw, bh),
                label="BUY", coin=True)


def modal_v3_cabochon(surf, panel):
    """V3 CABOCHON-FORWARD — a taller hero stage. The cabochon is enlarged and
    raised, the gem seated higher on the rim, the name/rarity tucked beneath in
    a single tight lane, and the CTA pair sits on a faint inner footer rule so
    the action zone reads as a distinct shelf. Heading is a clean gold bevel
    wordmark instead of a plate."""
    rad = m(20)
    _panel_chassis(surf, panel, rad, double_edge=True)
    cx = panel.centerx
    gradient_text(surf, "CONFIRM PURCHASE", font(14), (cx, panel.y + m(30)),
                  (255, 246, 206), (240, 182, 74), tracking=m(1.4),
                  weight=m(1.0), keyline=(60, 36, 8), kw=m(1.0), shadow=True)
    gold_rule(surf, panel.x + m(34), panel.right - m(34), panel.y + m(50),
              GOLD, peak=170)
    _stage(surf, cx, panel.y + m(118), m(50), gem_r=11, seat_deg=52)
    plain_text(surf, NAME, font(22), (cx, panel.y + m(198)), GOLD, shadow_a=160,
               weight=m(1.05), keyline=(60, 36, 8), kw=m(1.2), tracking=m(1))
    plain_text(surf, TIER.upper(), font(11), (cx, panel.y + m(219)), PAL["gem"],
               shadow_a=130, tracking=m(1.4), weight=m(0.7))
    price_chip(surf, cx, panel.y + m(248), f"{PRICE:,}", m(32), variant=1,
               affordable=True)
    # footer shelf rule above the action zone
    by = panel.bottom - m(38)
    gold_rule(surf, panel.x + m(30), panel.right - m(30), by - m(34), GOLD,
              peak=90, thick=m(1))
    bw, bh, gut = m(108), m(44), m(16)
    nx = cx - (bw * 2 + gut) // 2
    _cancel_button(surf, pygame.Rect(nx, by - bh // 2, bw, bh))
    _buy_button(surf, pygame.Rect(nx + bw + gut, by - bh // 2, bw, bh))


# =============================================================================
# Review sheet — chrome row on top, three modal variants below, all on the
# shared night-sky bg. Authored at SS then one smoothscale per panel.
# =============================================================================
def _bg_tile(w, h, seed=0):
    """A slice of the shared CONSTELLATION background for any sub-surface."""
    surf = pygame.Surface((w, h))
    surf.blit(multistop_v(w, h, BG_STOPS), (0, 0))
    # gentler, wider bloom on this landscape sheet so it doesn't read as hard
    # concentric rings behind the chrome row (the live store is portrait).
    soft_glow(surf, w // 2, int(h * 0.5), int(w * 0.55), NEBULA_GLOW,
              34, layers=12)
    rnd = __import__("random").Random(70 + seed)
    for n, rmin, rmax, amin, amax in ((90, 0.4, 0.9, 30, 90),
                                       (36, 0.9, 1.6, 70, 150),
                                       (12, 1.4, 2.6, 130, 220)):
        for _ in range(n):
            x = rnd.randint(0, w)
            y = rnd.randint(0, h)
            rr = m(rnd.uniform(rmin, rmax))
            a = rnd.randint(amin, amax)
            tint = rnd.choice([(255, 252, 240), (220, 226, 255), (255, 240, 210)])
            pygame.draw.circle(surf, (*tint, a), (x, y), max(1, int(rr)))
    return surf


def _label(surf, txt, cx, y):
    plain_text(surf, txt, font(12), (cx, y), GOLD_PALE, shadow_a=140,
               weight=m(0.85), keyline=(10, 10, 24), kw=m(0.8), tracking=m(1))


def render_sheet():
    pad = m(26)
    gap = m(22)
    # modal panel footprint (device px). Three side by side.
    pw, ph = m(264), m(330)
    chrome_h = m(150)                              # BACK + page-controls band
    sw = pad * 2 + pw * 3 + gap * 2
    sh = pad + chrome_h + gap + m(28) + ph + pad
    sheet = _bg_tile(sw, sh)

    # ── chrome band: BACK pill (default + gold) + page controls ──────────────
    _label(sheet, "BACK PILL", sw // 6, pad + m(8))
    back_pill(sheet, sw // 6, pad + m(46))
    back_pill(sheet, sw // 6, pad + m(96), gold=True)

    _label(sheet, "PAGE CONTROLS", sw // 2, pad + m(8))
    page_controls(sheet, sw // 2, pad + m(70))
    # a second, wider spread to show the comfortable tap-target geometry
    page_controls(sheet, sw // 2, pad + m(118), page=2, total=3, spread=190)

    _label(sheet, "TAP TARGETS  (≈44px)", sw * 5 // 6, pad + m(8))
    R.arrow_button = arrow_button
    arrow_button(sheet, sw * 5 // 6 - m(34), pad + m(60), "<")
    arrow_button(sheet, sw * 5 // 6 + m(34), pad + m(60), ">")
    back_pill(sheet, sw * 5 // 6, pad + m(110), w=140, h=40)

    # ── modal row ────────────────────────────────────────────────────────────
    row_y = pad + chrome_h + gap
    titles = ("V1  ROYAL  —  symmetric pair", "V2  WEIGHTED  —  60/40 CTA",
              "V3  CABOCHON-FORWARD")
    builders = (modal_v1_royal, modal_v2_weighted, modal_v3_cabochon)
    for i, (title, build) in enumerate(zip(titles, builders)):
        col_cx = pad + pw * i + gap * i + pw // 2
        _label(sheet, title, col_cx, row_y + m(14))
        panel = pygame.Rect(pad + (pw + gap) * i, row_y + m(28), pw, ph)
        # local scrim only over this column's modal cell so each variant shows
        # its own dim-against-bg read without bleeding into siblings.
        cell = pygame.Rect(panel.x - m(10), panel.y - m(10),
                           pw + m(20), ph + m(20))
        sc = pygame.Surface(cell.size, pygame.SRCALPHA)
        sc.fill((3, 4, 10, 150))
        sheet.blit(sc, cell.topleft)
        build(sheet, panel)

    return sheet


def main():
    R._build_static_bg()                           # primes shared bg caches
    sheet = render_sheet()
    sw, sh = sheet.get_size()
    # one smoothscale down from SS author space. Keep 1.6x logical detail so the
    # SS-crisp edges + faceted gems survive on the review sheet.
    zoom = 1.6
    out = pygame.transform.smoothscale(
        sheet, (int(sw / SS_ * zoom), int(sh / SS_ * zoom)))
    path = os.path.join(_HERE, "round_1.png")
    pygame.image.save(out, path)
    print("saved", path, out.get_size())


SS_ = R.SS

if __name__ == "__main__":
    main()
