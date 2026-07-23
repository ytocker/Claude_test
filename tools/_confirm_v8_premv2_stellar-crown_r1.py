"""stellar-crown — confirm-purchase popup, premium-v2, round 1.

A jewelled sovereign crown arcs over the hero cabochon: tier-coloured crown
jewels linked by flat solid-gold wedge gussets, riding a gold circlet. The crown
IS the >=60px statement; Zone A is the crown's golden base band, Zone B the tier
ribbon below. Rendered headless to a 3-tier review strip.
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
from game.hud import _font


# MANDATORY gloss_sweep patch — a Rect-indexed, self-contained sweep so the
# review render never depends on the runtime gloss cache/curve.
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
                            (int(w * 0.1), int(h * 0.04 + i * 1.5),
                             int(w * 0.8), bar_h))
    surf.blit(gsurf, (rect[0], rect[1]))


sc.gloss_sweep = _safe_gloss

m = sc.m

# ── constants ─────────────────────────────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130
DISC_CY = 135
R_HERO = 53
Y_NAME = 213
NAME_FS = 45
CHIP_CY = 247
BTN_CY = 360
BTN_W, BTN_H, BTN_RAD, BTN_GAP = 99, 31, 12, 10
BUY_CX, CAN_CX = 76, 184
Y_BANNER = 402
GEM_L_X, GEM_R_X = 43, 217
ZONE_B_GEM_R = 9

CARD_T = (28, 30, 70)
CARD_B = (12, 13, 38)
CARD_RING_DEEP = (58, 48, 22)
CARD_RING_BRIGHT = (236, 202, 116)
GOLD_A_RIM_DARK = (86, 50, 8)
GOLD_A_RIM_BRIGHT = (255, 240, 190)
CABO_LO = (22, 24, 50)
CABO_HI = (6, 7, 20)
GOLD_WEDGE = (204, 132, 42)

PRICE_STOPS = [(0.0, (236, 176, 72)), (0.45, (204, 132, 42)), (1.0, (150, 90, 18))]

PALETTES = {
    "RARE": {"gem": (108, 188, 252), "deep": (28, 68, 128), "glow": (168, 218, 252)},
    "EPIC": {"gem": (194, 122, 248), "deep": (88, 38, 168), "glow": (224, 178, 252)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (148, 88, 18), "glow": (255, 238, 168)},
}
# LEGENDARY Zone B crosses to garnet so the ribbon reads apart from the amber crown.
ZONE_B_GARNET = {"gem": (212, 92, 72), "deep": (92, 28, 20), "glow": (238, 146, 110)}

SIDS = {"RARE": "skin_wizard", "EPIC": "skin_prism", "LEGENDARY": "skin_astronaut"}
NAMES = {"RARE": "FROST WING", "EPIC": "PRISM WING", "LEGENDARY": "INFERNO WING"}
PRICES = {"RARE": "720", "EPIC": "1,400", "LEGENDARY": "2,600"}


def _fit_name_font(text, max_w):
    fs = m(NAME_FS)
    nf = _font(fs, True)
    while nf.size(text)[0] > max_w and fs > m(12):
        fs -= m(2)
        nf = _font(fs, True)
    return nf


def draw_popup(big, tier):
    pal = PALETTES[tier]
    sid = SIDS[tier]

    # ── card body ─────────────────────────────────────────────────────────────
    card_rect = pygame.Rect(m(6), m(6), m(248), m(430))
    rad = m(24)
    sc.drop_shadow(big, card_rect, rad, blur=m(8), alpha=170, dy=m(4))
    body = sc.vgrad_stops(card_rect.w, card_rect.h, rad,
                          [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15)
    big.blit(body, card_rect.topleft)
    sc.top_sheen(big, card_rect, rad, m(30), peak=62)
    pygame.draw.rect(big, (4, 5, 16), card_rect, width=m(2), border_radius=rad)
    sc.bevel_rim(big, card_rect, rad, CARD_RING_DEEP,
                 (*CARD_RING_BRIGHT, 230), w=max(1, m(2)))

    # ── Zone A: pointed gold price lozenge ─────────────────────────────────────
    chip_cx, chip_cy = m(CX), m(CHIP_CY)
    half_w, half_h = m(32), m(12)
    apex_l, apex_r = chip_cx - m(42), chip_cx + m(42)
    # apex caps first so the body seats over their inner edge
    pygame.draw.polygon(big, GOLD_WEDGE, [
        (chip_cx - half_w, chip_cy - half_h),
        (chip_cx - half_w, chip_cy + half_h), (apex_l, chip_cy)])
    pygame.draw.polygon(big, GOLD_WEDGE, [
        (chip_cx + half_w, chip_cy - half_h),
        (chip_cx + half_w, chip_cy + half_h), (apex_r, chip_cy)])
    chip_r = pygame.Rect(0, 0, m(64), m(24))
    chip_r.center = (chip_cx, chip_cy)
    sc._dark_chip_body(big, chip_r, m(9), PRICE_STOPS,
                       (78, 44, 8), (255, 226, 150), gloss=14, gamma=1.04)
    # coin + numeral group, centred in an inner lane of width m(52)
    num_f = sc.font(15)
    nw = num_f.size(PRICES[tier])[0]
    coin_d, gap = m(18), m(4)
    group_w = coin_d + gap + nw
    left = chip_cx - group_w // 2
    coin_cx = left + m(9)
    num_cx = left + coin_d + gap + nw // 2
    sc.coin_glyph(big, coin_cx, chip_cy, m(9))
    sc.plain_text(big, PRICES[tier], num_f, (num_cx, chip_cy), (52, 28, 4),
                  shadow_a=0, weight=m(0.8))
    # apex pips at each pointed tip
    sc.facet_gem(big, apex_l, chip_cy, m(4), (220, 170, 60), (100, 62, 12))
    sc.facet_gem(big, apex_r, chip_cy, m(4), (220, 170, 60), (100, 62, 12))

    # ── BUY button ─────────────────────────────────────────────────────────────
    buy_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy_r.center = (m(BUY_CX), m(BTN_CY))
    sc.chip_body_stops(big, buy_r, m(BTN_RAD),
                       [(0.0, (120, 75, 18)), (1.0, (80, 45, 8))],
                       GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, gloss=28, gamma=1.05)
    sc.plain_text(big, "BUY", sc.font(14), buy_r.center, (255, 248, 220),
                  shadow_a=120, weight=m(1.0))

    # ── CANCEL button ────────────────────────────────────────────────────────
    can_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can_r.center = (m(CAN_CX), m(BTN_CY))
    sc._dark_chip_body(big, can_r, m(BTN_RAD),
                       [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))],
                       CARD_RING_DEEP, CARD_RING_BRIGHT, gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(13), can_r.center, (150, 155, 200),
                  shadow_a=120, weight=m(0.9))

    # ── Zone B: rarity ribbon (garnet cross-hue on LEGENDARY) ─────────────────
    zb_pal = ZONE_B_GARNET if tier == "LEGENDARY" else pal
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(ZONE_B_GEM_R),
                 zb_pal["gem"], zb_pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(ZONE_B_GEM_R),
                 zb_pal["gem"], zb_pal["deep"])
    sc._ribbon_lozenge(big, tier, m(CX), m(Y_BANNER), m(146), zb_pal)

    # ── dead zone: mini crown-shard motif ─────────────────────────────────────
    scx, scy = m(130), m(297)
    w = m(18)
    top_y, mid_y, bot_y = scy - m(12), scy - m(2), scy + m(12)
    shard = [
        (scx - w, top_y), (scx - w // 2, mid_y), (scx, top_y - m(2)),
        (scx + w // 2, mid_y), (scx + w, top_y),
        (scx + w, bot_y), (scx - w, bot_y),
    ]
    pygame.draw.polygon(big, (10, 11, 30), shard)
    pygame.draw.polygon(big, CARD_RING_BRIGHT, shard, width=max(1, m(1)))
    sc.facet_gem(big, scx, scy, m(6), pal["gem"], pal["deep"])

    # ── crown assembly (over card body, under the hero) ───────────────────────
    acx, acy = m(CX), m(DISC_CY) - m(12)
    R = m(66)
    apex = (m(CX), m(DISC_CY) - m(36))
    angles = [-150, -120, -90, -60, -30]
    sizes = [m(9), m(11), m(12), m(11), m(9)]
    centers = [(acx + R * math.cos(math.radians(a)),
                acy + R * math.sin(math.radians(a))) for a in angles]
    # LEGENDARY crown stays amber to match the gold gussets; RARE/EPIC take tier hue
    crown_pal = PALETTES["LEGENDARY"] if tier == "LEGENDARY" else pal
    # flat solid-gold wedge gussets between adjacent jewels
    for i in range(len(centers) - 1):
        poly = [centers[i], centers[i + 1], apex, apex]
        pygame.draw.polygon(big, GOLD_WEDGE, poly)
        pygame.draw.polygon(big, CARD_RING_DEEP, poly, width=max(1, m(1)))
    # gold circlet arc + a dark under-arc a pixel below
    arc_box = (acx - R, acy - R, 2 * R, 2 * R)
    under_box = (acx - R, acy - R + m(1), 2 * R, 2 * R)
    pygame.draw.arc(big, (58, 48, 22), under_box,
                    math.radians(30), math.radians(150), max(2, m(2)))
    pygame.draw.arc(big, (*CARD_RING_BRIGHT, 255), arc_box,
                    math.radians(30), math.radians(150), max(2, m(2)))
    # crown jewels on top
    for (gx, gy), gr in zip(centers, sizes):
        sc.facet_gem(big, int(round(gx)), int(round(gy)), gr,
                     crown_pal["gem"], crown_pal["deep"])

    # ── hero cabochon (LAST so it overhangs the crown) ────────────────────────
    sc.cabochon(big, m(CX), m(DISC_CY), m(R_HERO), CABO_LO, CABO_HI,
                ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, m(CX), m(DISC_CY), int(m(R_HERO) * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (m(CX), m(DISC_CY)),
                           int(m(R_HERO) * 0.7))
    if tier == "LEGENDARY":
        orig = getattr(sc, "CABO_SPEC_A", 180)
        sc.CABO_SPEC_A = int(orig * 0.8)
    sc.cabochon_glass(big, m(CX), m(DISC_CY), m(R_HERO), tint=pal["gem"])
    if tier == "LEGENDARY":
        sc.CABO_SPEC_A = orig

    # ── name ─────────────────────────────────────────────────────────────────
    nf = _fit_name_font(NAMES[tier], m(POP_W) - m(40))
    sc.plain_text(big, NAMES[tier], nf, (m(CX), m(Y_NAME)), (220, 225, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def main():
    MARGIN, HEAD, GAP = 20, 58, 12
    tiers = ["RARE", "EPIC", "LEGENDARY"]
    # Build the sheet directly at 2x so the popups keep their authored crispness.
    strip = pygame.Surface((1688, 1040), pygame.SRCALPHA)
    bg = sc.vgrad_stops(1688, 1040, 0, [(0.0, (20, 20, 34)), (1.0, (9, 9, 18))], 255)
    strip.blit(bg, (0, 0))

    title_f = sc.font(15)
    sc.plain_text(strip, "STELLAR-CROWN  -  confirm purchase  (premium-v2, round 1)",
                  title_f, (int(1688 * 0.5), m(20)), (236, 202, 116),
                  shadow_a=140, weight=m(0.8))

    label_f = sc.font(16)
    for i, tier in enumerate(tiers):
        big = pygame.Surface((m(POP_W), m(POP_H)), pygame.SRCALPHA)
        draw_popup(big, tier)
        x1 = MARGIN + i * (POP_W + GAP)          # 1x left
        X = 2 * x1
        Y = 2 * HEAD
        strip.blit(big, (X, Y))
        pal = PALETTES[tier]
        sc.plain_text(strip, tier, label_f,
                      (X + m(POP_W) // 2, 2 * (HEAD - 18)), pal["gem"],
                      shadow_a=140, weight=m(0.9))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v2", "stellar-crown",
                       "round_1.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
