"""stellar-crown — round_2 final render.

Round_2 fixes: Zone A luminance too low in r1 (dark chip). Swapped to
chip_body_stops with a bright brass-gold gradient so it reads 2× brighter than
Zone B. Crown gem sizes increased (r=11-16) for bolder WOW presence.
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
GOLD_WEDGE = (218, 148, 52)  # brighter wedge fill in r2

# Bright gold Zone A stops — readable over the dark body
ZONE_A_STOPS = [
    (0.0,  (255, 230, 140)),
    (0.4,  (236, 192, 80)),
    (0.75, (196, 140, 38)),
    (1.0,  (148, 90, 18)),
]

PALETTES = {
    "RARE": {"gem": (108, 188, 252), "deep": (28, 68, 128), "glow": (168, 218, 252)},
    "EPIC": {"gem": (194, 122, 248), "deep": (88, 38, 168), "glow": (224, 178, 252)},
    "LEGENDARY": {"gem": (255, 202, 104), "deep": (148, 88, 18), "glow": (255, 238, 168)},
}
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

    # ── card body
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

    # ── Zone A: BRIGHT gold chip (r2 fix — luminance ≥2× Zone B)
    chip_cx, chip_cy = m(CX), m(CHIP_CY)
    half_w, half_h = m(34), m(13)
    apex_l, apex_r = chip_cx - m(46), chip_cx + m(46)
    # wedge apex caps (drawn first so chip seats over inner edge)
    for apex_x in (apex_l, apex_r):
        sign = -1 if apex_x < chip_cx else 1
        pygame.draw.polygon(big, GOLD_WEDGE, [
            (chip_cx + sign * half_w, chip_cy - half_h),
            (chip_cx + sign * half_w, chip_cy + half_h),
            (apex_x, chip_cy),
        ])
    chip_r = pygame.Rect(0, 0, m(68), m(26))
    chip_r.center = (chip_cx, chip_cy)
    # BRIGHT chip via chip_body_stops so lum ≫ dark Zone B
    sc.chip_body_stops(big, chip_r, m(10), ZONE_A_STOPS,
                       GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, gloss=36)
    # coin + numeral
    num_f = sc.font(15)
    nw = num_f.size(PRICES[tier])[0]
    coin_d, gap = m(18), m(4)
    group_w = coin_d + gap + nw
    left = chip_cx - group_w // 2
    sc.coin_glyph(big, left + m(9), chip_cy, m(9))
    sc.plain_text(big, PRICES[tier], num_f, (left + coin_d + gap + nw // 2, chip_cy),
                  (48, 26, 4), shadow_a=0, weight=m(0.8))
    # apex pips
    for ax in (apex_l, apex_r):
        sc.facet_gem(big, ax, chip_cy, m(5), (240, 190, 80), (110, 70, 14))

    # ── BUY button (fill lum ≥ 2× CANCEL)
    buy_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy_r.center = (m(BUY_CX), m(BTN_CY))
    sc.chip_body_stops(big, buy_r, m(BTN_RAD),
                       [(0.0, (168, 108, 24)), (1.0, (108, 62, 8))],
                       GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, gloss=28)
    sc.plain_text(big, "BUY", sc.font(14), buy_r.center, (255, 248, 220),
                  shadow_a=120, weight=m(1.0))

    # ── CANCEL button
    can_r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can_r.center = (m(CAN_CX), m(BTN_CY))
    sc._dark_chip_body(big, can_r, m(BTN_RAD),
                       [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))],
                       CARD_RING_DEEP, CARD_RING_BRIGHT, gloss=14)
    sc.plain_text(big, "CANCEL", sc.font(13), can_r.center, (150, 155, 200),
                  shadow_a=120, weight=m(0.9))

    # ── Zone B: flank gems + lozenge (garnet cross-hue for LEGENDARY)
    zb_pal = ZONE_B_GARNET if tier == "LEGENDARY" else pal
    sc.facet_gem(big, m(GEM_L_X), m(Y_BANNER), m(ZONE_B_GEM_R), zb_pal["gem"], zb_pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(Y_BANNER), m(ZONE_B_GEM_R), zb_pal["gem"], zb_pal["deep"])
    sc._ribbon_lozenge(big, tier, m(CX), m(Y_BANNER), m(146), zb_pal)

    # ── dead zone: mini crown-shard motif
    scx, scy = m(130), m(297)
    w2 = m(18)
    top_y, mid_y, bot_y = scy - m(12), scy - m(2), scy + m(12)
    shard = [
        (scx - w2, top_y), (scx - w2 // 2, mid_y), (scx, top_y - m(2)),
        (scx + w2 // 2, mid_y), (scx + w2, top_y),
        (scx + w2, bot_y), (scx - w2, bot_y),
    ]
    pygame.draw.polygon(big, (10, 11, 30), shard)
    pygame.draw.polygon(big, CARD_RING_BRIGHT, shard, width=max(2, m(2)))
    sc.facet_gem(big, scx, scy, m(6), pal["gem"], pal["deep"])

    # ── crown (LARGER gems in r2: r=11-16 for bold WOW presence)
    acx, acy = m(CX), m(DISC_CY) - m(12)
    R = m(66)
    apex = (m(CX), m(DISC_CY) - m(36))
    angles = [-150, -120, -90, -60, -30]
    sizes = [m(11), m(13), m(16), m(13), m(11)]   # r1 was 9-12; r2 is 11-16
    centers = [(acx + R * math.cos(math.radians(a)),
                acy + R * math.sin(math.radians(a))) for a in angles]
    crown_pal = PALETTES["LEGENDARY"] if tier == "LEGENDARY" else pal
    for i in range(len(centers) - 1):
        poly = [centers[i], centers[i + 1], apex, apex]
        pygame.draw.polygon(big, GOLD_WEDGE, poly)
        pygame.draw.polygon(big, CARD_RING_DEEP, poly, width=max(2, m(2)))
    arc_box = (acx - R, acy - R, 2 * R, 2 * R)
    under_box = (acx - R, acy - R + m(1), 2 * R, 2 * R)
    pygame.draw.arc(big, (58, 48, 22), under_box,
                    math.radians(30), math.radians(150), max(2, m(2)))
    pygame.draw.arc(big, (*CARD_RING_BRIGHT, 255), arc_box,
                    math.radians(30), math.radians(150), max(3, m(3)))
    for (gx, gy), gr in zip(centers, sizes):
        sc.facet_gem(big, int(round(gx)), int(round(gy)), gr,
                     crown_pal["gem"], crown_pal["deep"])

    # ── hero (last)
    sc.cabochon(big, m(CX), m(DISC_CY), m(R_HERO), CABO_LO, CABO_HI,
                ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, m(CX), m(DISC_CY), int(m(R_HERO) * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (m(CX), m(DISC_CY)), int(m(R_HERO) * 0.7))
    if tier == "LEGENDARY":
        orig = getattr(sc, "CABO_SPEC_A", 180)
        sc.CABO_SPEC_A = int(orig * 0.8)
    sc.cabochon_glass(big, m(CX), m(DISC_CY), m(R_HERO), tint=pal["gem"])
    if tier == "LEGENDARY":
        sc.CABO_SPEC_A = orig

    # ── name
    nf = _fit_name_font(NAMES[tier], m(POP_W) - m(40))
    sc.plain_text(big, NAMES[tier], nf, (m(CX), m(Y_NAME)), (220, 225, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def main():
    MARGIN, HEAD, GAP = 20, 58, 12
    tiers = ["RARE", "EPIC", "LEGENDARY"]
    strip = pygame.Surface((1688, 1040), pygame.SRCALPHA)
    bg = sc.vgrad_stops(1688, 1040, 0, [(0.0, (20, 20, 34)), (1.0, (9, 9, 18))], 255)
    strip.blit(bg, (0, 0))

    title_f = sc.font(15)
    sc.plain_text(strip, "STELLAR-CROWN  -  confirm purchase  (premium-v2, round 2)",
                  title_f, (1688 // 2, m(20)), (236, 202, 116), shadow_a=140, weight=m(0.8))

    label_f = sc.font(16)
    for i, tier in enumerate(tiers):
        big = pygame.Surface((m(POP_W), m(POP_H)), pygame.SRCALPHA)
        draw_popup(big, tier)
        X = 2 * (MARGIN + i * (POP_W + GAP))
        Y = 2 * HEAD
        strip.blit(big, (X, Y))
        pal = PALETTES[tier]
        sc.plain_text(strip, tier, label_f,
                      (X + m(POP_W) // 2, 2 * (HEAD - 18)), pal["gem"],
                      shadow_a=140, weight=m(0.9))

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "confirm_purchase_v8", "premium-v2", "stellar-crown",
                       "round_2.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(strip, out)
    print("wrote", out, strip.get_size())


if __name__ == "__main__":
    main()
