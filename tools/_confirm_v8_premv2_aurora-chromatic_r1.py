"""aurora-chromatic — confirm-purchase popup, round_1 exploration render.

Full-card elemental sweep: three large aurora lobes in the tier's colour flood
the upper card. A dark protective vignette beneath makes Zone A readable.
Zone A: wide _dark_chip_body price plate. Zone B: contrasting-hue lozenge.
Offline review tool only — never shipped.
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


# Mandatory gloss_sweep BLEND_ADD patch
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

# ── popup geometry (logical px; flow through m()) ─────────────────────────────
POP_W, POP_H = 260, 442
CX, DISC_CY, R_HERO = 130, 135, 53
Y_NAME, NAME_FS, CHIP_CY = 213, 45, 247
BTN_CY, BTN_W, BTN_H, BTN_RAD, BTN_GAP = 360, 99, 31, 12, 10
BUY_CX, CAN_CX = 76, 184
Y_BANNER, GEM_L_X, GEM_R_X = 402, 43, 217

CARD_T = (28, 30, 70)
CARD_B = (12, 13, 38)
CARD_RING_DEEP = sc.CARD_RING_DEEP
CARD_RING_BRIGHT = sc.CARD_RING_BRIGHT
GOLD_A_RIM_DARK = (86, 50, 8)
GOLD_A_RIM_BRIGHT = (255, 240, 190)

# Tier palettes — sweep colour + aura colour + gem
TIERS = {
    "RARE":      {
        "gem": (108, 188, 252), "deep": (28, 68, 128), "glow": (168, 218, 252),
        "sweep": (20, 60, 140),   # deep navy blue
    },
    "EPIC":      {
        "gem": (194, 122, 248), "deep": (88, 38, 168), "glow": (224, 178, 252),
        "sweep": (80, 30, 160),   # deep violet
    },
    "LEGENDARY": {
        "gem": (255, 202, 104), "deep": (148, 88, 18), "glow": (255, 238, 168),
        "sweep": (160, 90, 20),   # deep amber
    },
}

# Zone-B contrasting palette: cross-hue from the tier aurora
ZONE_B_PAL = {
    "RARE":      {"gem": (236, 202, 116), "glow": (255, 240, 180), "deep": (100, 68, 18)},
    "EPIC":      {"gem": (236, 202, 116), "glow": (255, 240, 180), "deep": (100, 68, 18)},
    "LEGENDARY": {"gem": (148, 196, 248), "glow": (200, 224, 255), "deep": (48, 88, 160)},
}

SIDS = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}

_SOVEREIGN_NUM_STOPS = sc._SOVEREIGN_NUM_STOPS


def _diagonal_sweep(surf, rect, col, angle_deg=35, alpha=150, n_bands=30):
    """Horizontal-slice implementation of a 35° diagonal colour wash."""
    rx, ry, rw, rh = rect
    tan_a = math.tan(math.radians(angle_deg))
    sweep = pygame.Surface((rw, rh), pygame.SRCALPHA)
    band_h = max(1, rh // n_bands)
    for i in range(n_bands):
        t = i / max(1, n_bands - 1)
        x_off = int(rw * t * tan_a / 2.0)
        y0 = i * band_h
        # brightness peaks at the sweep centre and falls off
        bright = 0.3 + 0.7 * (1 - abs(t - 0.5) * 2)
        a = int(alpha * bright)
        r2 = min(255, int(col[0] * bright))
        g2 = min(255, int(col[1] * bright))
        b2 = min(255, int(col[2] * bright))
        x_left = max(0, x_off)
        x_right = min(rw, rw - x_off)
        if x_right > x_left:
            pygame.draw.rect(sweep, (r2, g2, b2, a),
                             (x_left, y0, x_right - x_left, band_h + 1))
    surf.blit(sweep, (rx, ry))


def render_popup(tier):
    pal = TIERS[tier]
    zb_pal = ZONE_B_PAL[tier]
    sid = SIDS[tier]
    W, H = m(POP_W), m(POP_H)
    big = pygame.Surface((W, H), pygame.SRCALPHA)

    card_rad = m(22)
    rect = pygame.Rect(m(9), m(9), W - m(18), H - m(18))

    # 1 ── card body: dark navy gradient + shadow
    sc.drop_shadow(big, rect, card_rad, blur=m(8), alpha=160, dy=m(4))
    body_w = sc.vgrad_stops(rect.w, rect.h, card_rad,
                            [(0.0, CARD_T), (1.0, CARD_B)], 252, gamma=1.15)
    big.blit(body_w, rect.topleft)
    sc.bevel_rim(big, rect, card_rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(2)))

    # 2 ── STATEMENT: three overlapping aurora lobes, each r=m(72) ≥ 72 logical px
    # Left lobe / centre lobe / right lobe — create borealis curtain over upper card
    for (lx, ly, lr, lp) in [
        (m(70),  m(140), m(74), 160),
        (m(130), m(90),  m(80), 200),
        (m(190), m(150), m(74), 150),
    ]:
        sc._alpha_aura(big, lx, ly, lr, pal["glow"], peak=lp, layers=16)

    # 3 ── Diagonal elemental sweep over the lobes (alpha=140, tier colour)
    _diagonal_sweep(big, (rect.x, rect.y, rect.w, rect.h // 2),
                    pal["sweep"], angle_deg=35, alpha=140)

    # 4 ── top sheen across the aurora zone
    sc.top_sheen(big, rect, card_rad, m(20), peak=45)

    # 5 ── Dark keyline rim over body
    pygame.draw.rect(big, (4, 5, 16), rect, width=m(2), border_radius=card_rad)

    # 6 ── Protective dark vignette behind Zone A + CTAs so they read on the aurora
    vig = pygame.Surface((m(240), m(150)), pygame.SRCALPHA)
    pygame.draw.rect(vig, (6, 7, 18, 170), vig.get_rect(), border_radius=m(8))
    big.blit(vig, (m(10), m(232)))

    # 7 ── Name: shrink from 20 until it fits
    name_sz = 20
    while name_sz > 6:
        nf = sc.font(name_sz)
        if sc._glyph_base(NAMES[tier], nf, 0).get_width() <= m(POP_W) - m(44):
            break
        name_sz -= 1
    sc.plain_text(big, NAMES[tier], sc.font(name_sz),
                  (m(CX), m(Y_NAME)), (255, 255, 255),
                  shadow_a=160, weight=m(1.0), keyline=(4, 5, 16), kw=m(1.2))

    # 8 ── Zone A: wide dark chip price plate (178×40) for structural weight
    zone_a = pygame.Rect(m(CX) - m(89), m(CHIP_CY) - m(20), m(178), m(40))
    sc._dark_chip_body(big, zone_a, m(11),
                       [(0.0, (24, 28, 58)), (0.5, (18, 20, 48)), (1.0, (12, 14, 36))],
                       rim_dark=CARD_RING_DEEP, rim_bright=CARD_RING_BRIGHT, gloss=12)

    # price: coin_glyph + numeral in gold sovereign stops
    price = PRICES[tier]
    price_f = sc.font(20)
    num_surf = sc._glyph_base(price, price_f, 0)
    num_w = num_surf.get_width()
    coin_r = m(11)
    gap = m(5)
    total = coin_r * 2 + gap + num_w
    gx = m(CX) - total // 2
    try:
        sc.coin_glyph(big, gx + coin_r, m(CHIP_CY), coin_r)
    except Exception:
        pygame.draw.circle(big, (232, 176, 72), (gx + coin_r, m(CHIP_CY)), coin_r)

    # Render numeral using sovereign gold gradient stops
    for (t_pos, col) in _SOVEREIGN_NUM_STOPS:
        sc.plain_text(big, price, price_f,
                      (gx + coin_r * 2 + gap + num_w // 2, m(CHIP_CY) + int(t_pos * m(20) - m(10))),
                      col, shadow_a=0, weight=m(0.8))
    # Draw numeral once at centre (overwrites the multi-stop; gives the visual gradient impression)
    sc.plain_text(big, price, price_f,
                  (gx + coin_r * 2 + gap + num_w // 2, m(CHIP_CY)),
                  _SOVEREIGN_NUM_STOPS[1][1], shadow_a=120, weight=m(0.9),
                  keyline=(20, 22, 44), kw=m(0.8))

    # 9 ── dead zone: aurora spark cluster (five small facet gems in tier colour)
    spark_cy = m(297)
    for k in range(5):
        ang = math.pi * 2 * k / 5 - math.pi / 2
        sx = m(CX) + int(m(22) * math.cos(ang))
        sy = spark_cy + int(m(10) * math.sin(ang))
        sc.facet_gem(big, sx, sy, m(5), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(CX), spark_cy, m(8), pal["gem"], pal["deep"])

    # 10 ── shelf + BUY / CANCEL
    shelf = pygame.Rect(m(17), m(335), m(226), m(91))
    big.blit(sc.vgrad_stops(shelf.w, shelf.h, m(14),
                            [(0.0, (20, 22, 50)), (1.0, (10, 11, 32))],
                            255, gamma=1.1), shelf.topleft)
    pygame.draw.rect(big, (5, 6, 16), shelf, width=max(1, m(1)),
                     border_radius=m(14))

    buy = pygame.Rect(m(BUY_CX) - m(BTN_W) // 2, m(BTN_CY) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    # BUY fill uses tier gem colour so it reads 2× brighter than the dark CANCEL
    buy_fill_lo = tuple(min(255, int(c * 0.7)) for c in pal["gem"])
    buy_fill_hi = tuple(min(255, int(c * 1.0)) for c in pal["glow"])
    sc.chip_body_stops(big, buy, m(BTN_RAD),
                       [(0.0, buy_fill_hi), (1.0, buy_fill_lo)],
                       rim_dark=GOLD_A_RIM_DARK, rim_bright=GOLD_A_RIM_BRIGHT,
                       gloss=30)
    buy_txt_col = (20, 12, 8) if tier != "LEGENDARY" else (60, 40, 10)
    sc.plain_text(big, "BUY", sc.font(13), buy.center, buy_txt_col,
                  shadow_a=0, weight=m(0.9))

    can = pygame.Rect(m(CAN_CX) - m(BTN_W) // 2, m(BTN_CY) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    sc._dark_chip_body(big, can, m(BTN_RAD),
                       [(0.0, (38, 40, 72)), (1.0, (20, 22, 50))],
                       rim_dark=CARD_RING_DEEP, rim_bright=CARD_RING_BRIGHT,
                       gloss=12)
    sc.plain_text(big, "CANCEL", sc.font(11), can.center, (160, 170, 210),
                  shadow_a=0, weight=m(0.7))

    # 11 ── Zone B: flank gems + lozenge in contrasting hue
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(9), zb_pal["gem"], zb_pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(9), zb_pal["gem"], zb_pal["deep"])
    sc._ribbon_lozenge(big, tier, m(CX), m(Y_BANNER), m(146), zb_pal)

    # 12 ── hero drawn last: cabochon + thumb + glass
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
                       "aurora-chromatic", "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
