"""aurora-chromatic — round_2 final render.

Round_2 fix: Zone A (dark chip) was barely distinguishable from the dark body
(lum diff only 3.3). Replaced with a BRIGHT tier-coloured chip using
chip_body_stops — the tier's glow stops create a luminous focal point. Aurora
lobes are more vivid (peak=220) and the diagonal sweep covers the full card body.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
pygame.init()
pygame.display.set_mode((1, 1))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game.store_cards as sc


def _safe_gloss(surf, rect, radius, peak=46):
    w, h = rect[2], rect[3]
    gsurf = pygame.Surface((w, h), pygame.SRCALPHA)
    gsurf.fill((0, 0, 0, 0))
    steps = 10
    for i in range(steps):
        t = i / (steps - 1)
        alpha = int(peak * (1 - t))
        bar_h = max(1, int(h * 0.45 * (1 - t)))
        pygame.draw.ellipse(gsurf, (255, 255, 255, alpha),
            (int(w * 0.1), int(h * 0.04 + i * 1.5), int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))
sc.gloss_sweep = _safe_gloss


m = sc.m

POP_W, POP_H = 260, 442
CX, DISC_CY, R_HERO = 130, 135, 53
Y_NAME, CHIP_CY = 213, 247
BTN_CY, BTN_W, BTN_H, BTN_RAD = 360, 99, 31, 12
BUY_CX, CAN_CX = 76, 184
Y_BANNER, GEM_L_X, GEM_R_X = 402, 43, 217

CARD_T = (28, 30, 70)
CARD_B = (12, 13, 38)
CARD_RING_DEEP = sc.CARD_RING_DEEP
CARD_RING_BRIGHT = sc.CARD_RING_BRIGHT

TIERS = {
    "RARE":      {
        "gem": (108, 188, 252), "deep": (28, 68, 128), "glow": (168, 218, 252),
        "sweep": (20, 60, 140),
    },
    "EPIC":      {
        "gem": (194, 122, 248), "deep": (88, 38, 168), "glow": (224, 178, 252),
        "sweep": (80, 30, 160),
    },
    "LEGENDARY": {
        "gem": (255, 202, 104), "deep": (148, 88, 18), "glow": (255, 238, 168),
        "sweep": (160, 90, 20),
    },
}
ZONE_B_PAL = {
    "RARE":      {"gem": (236, 202, 116), "glow": (255, 240, 180), "deep": (100, 68, 18)},
    "EPIC":      {"gem": (236, 202, 116), "glow": (255, 240, 180), "deep": (100, 68, 18)},
    "LEGENDARY": {"gem": (148, 196, 248), "glow": (200, 224, 255), "deep": (48, 88, 160)},
}

SIDS = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}


def _diagonal_sweep(surf, rect, col, angle_deg=35, alpha=155, n_bands=28):
    rx, ry, rw, rh = rect
    tan_a = math.tan(math.radians(angle_deg))
    sweep = pygame.Surface((rw, rh), pygame.SRCALPHA)
    band_h = max(1, rh // n_bands)
    for i in range(n_bands):
        t = i / max(1, n_bands - 1)
        x_off = int(rw * t * tan_a / 2.0)
        bright = 0.35 + 0.65 * (1 - abs(t - 0.5) * 2)
        a = int(alpha * bright)
        r2 = min(255, int(col[0] * bright))
        g2 = min(255, int(col[1] * bright))
        b2 = min(255, int(col[2] * bright))
        x_left = max(0, x_off)
        x_right = min(rw, rw - x_off)
        if x_right > x_left:
            pygame.draw.rect(sweep, (r2, g2, b2, a),
                             (x_left, i * band_h, x_right - x_left, band_h + 1))
    surf.blit(sweep, (rx, ry))


def render_popup(tier):
    pal = TIERS[tier]
    zb_pal = ZONE_B_PAL[tier]
    sid = SIDS[tier]
    W, H = m(POP_W), m(POP_H)
    big = pygame.Surface((W, H), pygame.SRCALPHA)

    card_rad = m(22)
    rect = pygame.Rect(m(9), m(9), W - m(18), H - m(18))

    # 1 · card body + shadow
    sc.drop_shadow(big, rect, card_rad, blur=m(8), alpha=160, dy=m(4))
    body_w = sc.vgrad_stops(rect.w, rect.h, card_rad,
                            [(0.0, CARD_T), (1.0, CARD_B)], 252, gamma=1.15)
    big.blit(body_w, rect.topleft)
    sc.bevel_rim(big, rect, card_rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(2)))

    # 2 · STATEMENT: three larger aurora lobes (peak=220, r=80 in r2)
    for (lx, ly, lr, lp) in [
        (m(70),  m(140), m(80), 200),
        (m(130), m(90),  m(88), 220),
        (m(190), m(150), m(80), 190),
    ]:
        sc._alpha_aura(big, lx, ly, lr, pal["glow"], peak=lp, layers=18)

    # 3 · Diagonal elemental sweep — now covers FULL card height
    _diagonal_sweep(big, (rect.x, rect.y, rect.w, rect.h),
                    pal["sweep"], angle_deg=35, alpha=155)

    # 4 · top sheen + dark keyline
    sc.top_sheen(big, rect, card_rad, m(20), peak=45)
    pygame.draw.rect(big, (4, 5, 16), rect, width=m(2), border_radius=card_rad)

    # 5 · Name (above the protective vignette)
    name_sz = 20
    while name_sz > 6:
        nf = sc.font(name_sz)
        if sc._glyph_base(NAMES[tier], nf, 0).get_width() <= m(POP_W) - m(44):
            break
        name_sz -= 1
    sc.plain_text(big, NAMES[tier], sc.font(name_sz),
                  (m(CX), m(Y_NAME)), (255, 255, 255),
                  shadow_a=180, weight=m(1.0), keyline=(4, 5, 16), kw=m(1.4))

    # 6 · Protective vignette before Zone A (darker in r2)
    vig = pygame.Surface((m(240), m(150)), pygame.SRCALPHA)
    pygame.draw.rect(vig, (6, 7, 18, 200), vig.get_rect(), border_radius=m(8))
    big.blit(vig, (m(10), m(232)))

    # 7 · Zone A — BRIGHT tier-coloured chip (r2 fix: replaces dark chip)
    zone_a = pygame.Rect(m(CX) - m(89), m(CHIP_CY) - m(21), m(178), m(42))
    # glow→gem gradient so the chip reads as the tier's brightest element
    sc.chip_body_stops(big, zone_a, m(12),
                       [(0.0, pal["glow"]), (0.5, pal["gem"]),
                        (1.0, tuple(max(0, c - 40) for c in pal["gem"]))],
                       tuple(max(0, c - 80) for c in pal["gem"]),
                       tuple(min(255, c + 60) for c in pal["glow"]),
                       gloss=40)
    # Coin + numeral (dark text on bright chip)
    price = PRICES[tier]
    price_f = sc.font(20)
    num_w = sc._glyph_base(price, price_f, 0).get_width()
    coin_r = m(11)
    gap = m(5)
    total = coin_r * 2 + gap + num_w
    gx = m(CX) - total // 2
    try:
        sc.coin_glyph(big, gx + coin_r, m(CHIP_CY), coin_r)
    except Exception:
        pygame.draw.circle(big, (232, 176, 72), (gx + coin_r, m(CHIP_CY)), coin_r)
    # Dark text on bright chip
    txt_col = (20, 12, 8) if tier != "LEGENDARY" else (30, 20, 6)
    sc.plain_text(big, price, price_f,
                  (gx + coin_r * 2 + gap + num_w // 2, m(CHIP_CY)),
                  txt_col, shadow_a=0, weight=m(0.9))

    # 8 · dead zone: gem cluster (unchanged, works)
    spark_cy = m(297)
    for k in range(5):
        ang = math.pi * 2 * k / 5 - math.pi / 2
        sx = m(CX) + int(m(22) * math.cos(ang))
        sy = spark_cy + int(m(10) * math.sin(ang))
        sc.facet_gem(big, sx, sy, m(5), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(CX), spark_cy, m(8), pal["gem"], pal["deep"])

    # 9 · shelf + BUY / CANCEL
    shelf = pygame.Rect(m(17), m(335), m(226), m(91))
    big.blit(sc.vgrad_stops(shelf.w, shelf.h, m(14),
                            [(0.0, (20, 22, 50)), (1.0, (10, 11, 32))],
                            255, gamma=1.1), shelf.topleft)
    pygame.draw.rect(big, (5, 6, 16), shelf, width=max(1, m(1)), border_radius=m(14))

    buy = pygame.Rect(m(BUY_CX) - m(BTN_W) // 2, m(BTN_CY) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    buy_fill_lo = tuple(min(255, int(c * 0.75)) for c in pal["gem"])
    buy_fill_hi = tuple(min(255, int(c)) for c in pal["glow"])
    sc.chip_body_stops(big, buy, m(BTN_RAD),
                       [(0.0, buy_fill_hi), (1.0, buy_fill_lo)],
                       tuple(max(0, c - 80) for c in pal["gem"]),
                       tuple(min(255, c + 60) for c in pal["glow"]),
                       gloss=32)
    buy_txt = (20, 12, 8) if tier != "LEGENDARY" else (30, 20, 6)
    sc.plain_text(big, "BUY", sc.font(13), buy.center, buy_txt,
                  shadow_a=0, weight=m(0.9))

    can = pygame.Rect(m(CAN_CX) - m(BTN_W) // 2, m(BTN_CY) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    sc._dark_chip_body(big, can, m(BTN_RAD),
                       [(0.0, (38, 40, 72)), (1.0, (20, 22, 50))],
                       CARD_RING_DEEP, CARD_RING_BRIGHT, gloss=12)
    sc.plain_text(big, "CANCEL", sc.font(11), can.center, (160, 170, 210),
                  shadow_a=0, weight=m(0.7))

    # 10 · Zone B — contrasting hue (gold for RARE/EPIC, silver-blue for LEGENDARY)
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(9), zb_pal["gem"], zb_pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(9), zb_pal["gem"], zb_pal["deep"])
    sc._ribbon_lozenge(big, tier, m(CX), m(Y_BANNER), m(146), zb_pal)

    # 11 · hero (last)
    hx, hy = m(CX), m(DISC_CY)
    CABO_LO, CABO_HI = (22, 24, 50), (6, 7, 20)
    sc.cabochon(big, hx, hy, m(R_HERO), CABO_LO, CABO_HI,
                ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, hx, hy, int(m(R_HERO) * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (hx, hy), int(m(R_HERO) * 0.7))
    if tier == "LEGENDARY":
        orig = getattr(sc, "CABO_SPEC_A", 180)
        sc.CABO_SPEC_A = int(orig * 0.8)
    sc.cabochon_glass(big, hx, hy, m(R_HERO), tint=pal["gem"])
    if tier == "LEGENDARY":
        sc.CABO_SPEC_A = orig

    return big


def main():
    MARGIN, HEAD, GAP = 20, 58, 12
    order = ["RARE", "EPIC", "LEGENDARY"]
    pw, ph = m(POP_W), m(POP_H)

    strip_w = m(MARGIN) * 2 + len(order) * pw + (len(order) - 1) * m(GAP)
    strip_h = m(HEAD) + ph + m(MARGIN)
    strip = pygame.Surface((strip_w, strip_h))
    strip.fill((24, 24, 34))

    head_f = sc.font(15)
    sub_f = sc.font(9)
    for i, tier in enumerate(order):
        col_x = m(MARGIN) + i * (pw + m(GAP))
        cxh = col_x + pw // 2
        sc.plain_text(strip, tier, head_f, (cxh, m(24)),
                      (236, 224, 196), shadow_a=0, weight=m(0.9))
        sc.plain_text(strip, "aurora-chromatic", sub_f, (cxh, m(44)),
                      (150, 150, 172), shadow_a=0, weight=m(0.4))
        strip.blit(render_popup(tier), (col_x, m(HEAD)))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v2",
                       "aurora-chromatic", "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
