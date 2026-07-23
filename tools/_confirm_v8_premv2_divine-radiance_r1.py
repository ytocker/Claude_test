"""divine-radiance — confirm-purchase popup, round_1 exploration render.

A reliquary read: the item floats inside a living halo. The >=60px statement
is a 16-petal SOLID-GOLD sunburst (the petals carry the structure, not the soft
glow). A capped corona dies above the name; Zone A is a pale moonstone price
band over a dark keyline. Offline review tool only — never shipped.
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


# MANDATORY gloss_sweep patch — the shipped gloss_sweep caches by rect size and
# would leak across the many distinct button rects in a review strip; this
# stateless variant draws a soft crown sheen without the cache.
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
CARD_RING_DEEP = sc.CARD_RING_DEEP        # (58, 48, 22)
CARD_RING_BRIGHT = sc.CARD_RING_BRIGHT    # (236, 202, 116)
GOLD_A_RIM_DARK = (86, 50, 8)
GOLD_A_RIM_BRIGHT = (255, 240, 190)
WHITE = (255, 255, 255)

# Popup-spec tier palettes (corona / hero aura / gem / dead-zone jewel).
TIERS = {
    "RARE":      {"gem": (108, 188, 252), "deep": (28, 68, 128),  "glow": (168, 218, 252)},
    "EPIC":      {"gem": (194, 122, 248), "deep": (88, 38, 168),  "glow": (224, 178, 252)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (148, 88, 18),  "glow": (255, 238, 168)},
}
# LEGENDARY Zone-B rose override so the flank gems + banner separate from the
# amber sunburst instead of melting into it.
ZONE_B_ROSE = {"gem": (240, 150, 150), "deep": (150, 52, 60), "glow": (255, 196, 196)}

SIDS = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}


def _fit_font(text, start, max_w):
    """Pick the largest project-bold size whose glyph run fits max_w."""
    sz = start
    f = sc.font(sz)
    while sc._glyph_base(text, f, 0).get_width() > max_w and sz > 6:
        sz -= 1
        f = sc.font(sz)
    return f


def render_popup(tier):
    pal = TIERS[tier]
    sid = SIDS[tier]
    W, H = m(POP_W), m(POP_H)
    big = pygame.Surface((W, H), pygame.SRCALPHA)

    rad = m(22)
    rect = pygame.Rect(m(9), m(9), W - m(18), H - m(18))

    # 1 ── card body: shadow, navy gradient, sheen, dark keyline, gold bevel rim
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=160, dy=m(4))
    body_surf = sc.vgrad_stops(rect.w, rect.h, rad,
                               [(0.0, CARD_T), (1.0, CARD_B)], 252, gamma=1.15)
    big.blit(body_surf, rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=62)
    pygame.draw.rect(big, (4, 5, 16), rect, width=m(2), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230),
                 w=max(1, m(2)))

    # 2 ── capped outer corona: a soft halo behind the hero, then a kill-slab of
    # the clean body gradient re-laid below the disc so NO glow survives down
    # into the name (cy=213). Keeps the radiance a crown, not a wash.
    sc._alpha_aura(big, m(CX), m(DISC_CY), m(60), pal["glow"], peak=70, layers=14)
    kx0, ky0 = m(CX) - m(80), m(193)
    kw, kh = m(160), m(240) - m(193)
    big.blit(body_surf.subsurface((kx0 - rect.x, ky0 - rect.y, kw, kh)),
             (kx0, ky0))

    # 3 ── name plate (bright, dark-keylined for legibility on the navy body)
    name_f = _fit_font(NAMES[tier], 20, m(POP_W) - m(44))
    sc.plain_text(big, NAMES[tier], name_f, (m(CX), m(Y_NAME)),
                  sc.lerp_color(pal["glow"], WHITE, 0.35), shadow_a=150,
                  weight=m(1.0), keyline=(6, 6, 16), kw=m(1.0))

    # 4 ── Zone A: dark keyline mat FIRST, moonstone price band on top
    mat = pygame.Surface((m(100), m(32)), pygame.SRCALPHA)
    pygame.draw.rect(mat, (6, 7, 18, 200), mat.get_rect(), border_radius=m(9))
    big.blit(mat, (m(CX) - m(50), m(CHIP_CY) - m(16)))
    band = pygame.Rect(m(CX) - m(48), m(CHIP_CY) - m(13), m(96), m(26))
    sc.chip_body_stops(big, band, m(8),
                       [(0.0, (232, 236, 248)), (0.5, (198, 208, 232)),
                        (1.0, (150, 166, 204))],
                       rim_dark=(64, 72, 104), rim_bright=(255, 255, 255),
                       gloss=40)
    price = PRICES[tier]
    price_f = sc.font(15)
    num_w = sc._glyph_base(price, price_f, 0).get_width()
    coin_r = m(9)
    gap = m(4)
    total = coin_r * 2 + gap + num_w
    gx = m(CX) - total // 2
    try:
        sc.coin_glyph(big, gx + coin_r, m(CHIP_CY), coin_r)
    except Exception:
        pygame.draw.circle(big, (232, 176, 72), (gx + coin_r, m(CHIP_CY)), coin_r)
    sc.plain_text(big, price, price_f,
                  (gx + coin_r * 2 + gap + num_w // 2, m(CHIP_CY)),
                  (40, 44, 72), shadow_a=0, weight=m(0.6))

    # 5 ── dead-zone rayed medallion (a small radiant seal between band + shelf)
    mcx, mcy = m(CX), m(297)
    pygame.draw.circle(big, (12, 13, 32), (mcx, mcy), m(15))
    pygame.draw.circle(big, CARD_RING_BRIGHT, (mcx, mcy), m(15), max(1, m(1)))
    for k in range(8):
        a = math.pi * 2 * k / 8
        x1, y1 = mcx + m(16) * math.cos(a), mcy + m(16) * math.sin(a)
        x2, y2 = mcx + m(26) * math.cos(a), mcy + m(26) * math.sin(a)
        pygame.draw.line(big, CARD_RING_BRIGHT, (x1, y1), (x2, y2), max(2, m(2)))
    sc.facet_gem(big, mcx, mcy, m(6), pal["gem"], pal["deep"])

    # 6 ── shelf + BUY / CANCEL
    shelf = pygame.Rect(m(17), m(335), m(226), m(91))
    big.blit(sc.vgrad_stops(shelf.w, shelf.h, m(14),
                            [(0.0, (22, 24, 54)), (1.0, (12, 13, 36))],
                            255, gamma=1.1), shelf.topleft)
    pygame.draw.rect(big, (6, 7, 18), shelf, width=max(1, m(1.4)),
                     border_radius=m(14))

    buy = pygame.Rect(m(BUY_CX) - m(BTN_W) // 2, m(BTN_CY) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    sc.chip_body_stops(big, buy, m(BTN_RAD),
                       [(0.0, (224, 180, 96)), (1.0, (176, 120, 40))],
                       rim_dark=GOLD_A_RIM_DARK, rim_bright=GOLD_A_RIM_BRIGHT,
                       gloss=32)
    sc.plain_text(big, "BUY", sc.font(13), buy.center, (60, 36, 8),
                  shadow_a=0, weight=m(0.9), keyline=(255, 240, 200), kw=m(0.8))

    can = pygame.Rect(m(CAN_CX) - m(BTN_W) // 2, m(BTN_CY) - m(BTN_H) // 2,
                      m(BTN_W), m(BTN_H))
    sc._dark_chip_body(big, can, m(BTN_RAD),
                       [(0.0, (40, 44, 72)), (1.0, (22, 24, 48))],
                       rim_dark=CARD_RING_DEEP, rim_bright=CARD_RING_BRIGHT,
                       gloss=14)
    sc.plain_text(big, "CANCEL", sc.font(11), can.center, (170, 180, 214),
                  shadow_a=0, weight=m(0.7))

    # 7 ── Zone B: flank gems + tier lozenge (LEGENDARY swaps to rose)
    zb = ZONE_B_ROSE if tier == "LEGENDARY" else pal
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(9), zb["gem"], zb["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(9), zb["gem"], zb["deep"])
    sc._ribbon_lozenge(big, tier, m(CX), m(Y_BANNER), m(146), zb)

    # 8 ── the STATEMENT: 16 solid-gold sunburst petals around the hero. Roots
    # start just inside the dome so the cabochon (step 10) caps them. Cardinal
    # rays are short so the down-ray clears the name; diagonals run long.
    hx, hy = m(CX), m(DISC_CY)
    inner_r = m(55)
    a_base = math.radians(8)
    a_tip = math.radians(2)
    for k in range(16):
        ang = -math.pi / 2 + math.pi * 2 * k / 16
        tip_r = m(80) if k % 2 else m(66)
        p1 = (hx + inner_r * math.cos(ang - a_base),
              hy + inner_r * math.sin(ang - a_base))
        p2 = (hx + inner_r * math.cos(ang + a_base),
              hy + inner_r * math.sin(ang + a_base))
        p3 = (hx + tip_r * math.cos(ang + a_tip),
              hy + tip_r * math.sin(ang + a_tip))
        p4 = (hx + tip_r * math.cos(ang - a_tip),
              hy + tip_r * math.sin(ang - a_tip))
        poly = [p1, p2, p3, p4]
        pygame.draw.polygon(big, (196, 124, 34), poly)
        pygame.draw.polygon(big, (86, 50, 8), poly, width=max(1, m(1)))

    # 9 ── dimmed inner corona: a tight bright halo hugging the hero rim
    sc._alpha_aura(big, hx, hy, m(58), pal["glow"], peak=140, layers=10)

    # 10 ── hero (drawn LAST so it caps the petal roots + sits under glass)
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
        sc.plain_text(strip, "divine-radiance", sub_f, (cxh, m(44)),
                      (150, 150, 172), shadow_a=0, weight=m(0.4))
        strip.blit(render_popup(tier), (col_x, m(HEAD)))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v2",
                       "divine-radiance", "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
