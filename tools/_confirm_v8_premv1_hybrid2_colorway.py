"""hybrid-2 holistic colourway renderer — /design run, rounds 1 and 2.

Geometry is locked (bar 168×34 S2-clean at 247 with push-down, quatrefoil 297,
B2 buttons 99×42, banner 402); each colourway re-assigns the colour SYSTEM:
price bar, BUY, CANCEL, and the quatrefoil catch-light move together. Gold is
allowed at most once per concept so the card never reads gold-on-gold.

Usage: python _confirm_v8_premv1_hybrid2_colorway.py <round>   (1 or 2)
Writes docs/confirm_purchase_v8/premium-v1/colorways/<slug>/round_<n>.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_button_options as btn
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import (m, font, vgrad_stops, bevel_rim, top_sheen,
                              drop_shadow, coin_glyph, plain_text,
                              chip_body_stops, _glyph_base, _stamp_bold,
                              CARD_RING_BRIGHT, CARD_RING_DEEP,
                              GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT)
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BAR_H = 34
BTN_W, BTN_H, BTN_CY = 99, 42, 360
BUY_CX, CAN_CX = 76, 184
Q_DEEP = (22, 24, 56)

G2 = [(0.00, (255, 232, 140)), (0.32, (244, 208, 92)),
      (0.66, (216, 172, 52)), (1.00, (166, 124, 30))]
Z1 = [(0.00, (255, 232, 140)), (0.40, (238, 198, 80)), (1.00, (150, 110, 26))]
INDIGO_CAN = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
CREAM = (255, 248, 220)

# Each palette: bar(stops, num, rim_d, rim_b), buy(stops, text, rim_d, rim_b),
#               can(stops, text, rim_d, rim_b), glint
PALETTES_R1 = {
    "gold-reserve": dict(
        bar=(G2, (52, 28, 4), GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        buy=([(0.0, (96, 150, 240)), (0.5, (56, 104, 200)), (1.0, (28, 60, 140))],
             (235, 244, 255), (16, 32, 80), (170, 205, 255)),
        can=(INDIGO_CAN, (150, 155, 200), CARD_RING_DEEP, CARD_RING_BRIGHT),
        glint=(200, 165, 90)),
    "two-metals": dict(
        bar=([(0.0, (240, 244, 252)), (0.35, (214, 220, 232)),
              (0.7, (178, 186, 202)), (1.0, (140, 148, 168))],
             (30, 36, 60), (70, 78, 98), (255, 255, 255)),
        buy=(Z1, CREAM, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        can=([(0.0, (24, 28, 44)), (1.0, (12, 14, 26))],
             (140, 148, 170), CARD_RING_DEEP, CARD_RING_BRIGHT),
        glint=(190, 200, 215)),
    "emerald-commerce": dict(
        bar=(G2, (52, 28, 4), GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        buy=([(0.0, (96, 196, 118)), (0.5, (52, 150, 84)), (1.0, (22, 96, 46))],
             (232, 255, 238), GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        can=(INDIGO_CAN, (150, 155, 200), CARD_RING_DEEP, CARD_RING_BRIGHT),
        glint=(200, 165, 90)),
    "ivory-manuscript": dict(
        bar=([(0.0, (252, 248, 238)), (0.35, (238, 230, 212)),
              (0.7, (218, 208, 186)), (1.0, (188, 176, 150))],
             (56, 40, 20), (110, 96, 70), (255, 255, 248)),
        buy=(Z1, CREAM, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        can=([(0.0, (40, 36, 52)), (1.0, (22, 20, 32))],
             (170, 160, 150), (30, 26, 20), (200, 186, 158)),
        glint=(215, 200, 170)),
    "midnight-royal": dict(
        bar=([(0.0, (226, 238, 255)), (0.35, (196, 214, 244)),
              (0.7, (160, 180, 220)), (1.0, (120, 140, 185))],
             (24, 34, 68), (54, 68, 110), (235, 245, 255)),
        buy=([(0.0, (248, 190, 84)), (0.5, (224, 156, 48)), (1.0, (160, 104, 20))],
             CREAM, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT),
        can=([(0.0, (18, 24, 54)), (1.0, (10, 13, 34))],
             (140, 152, 196), CARD_RING_DEEP, CARD_RING_BRIGHT),
        glint=(170, 195, 235)),
}

# Round 2 = round 1 + critique fixes. Gold-bar concepts collide with the
# gold-family LEGENDARY banner (hue distance 42 < 60), so those cross-hue the
# LEGENDARY banner to oxblood; gold-reserve's sapphire BUY sat at the 2.10
# hierarchy floor and gets brighter stops.
OXBLOOD = {"gem": (150, 60, 44), "deep": (70, 22, 16), "glow": (196, 96, 64)}
PALETTES_R2 = {k: dict(v) for k, v in PALETTES_R1.items()}
PALETTES_R2["gold-reserve"]["leg_banner"] = OXBLOOD
PALETTES_R2["emerald-commerce"]["leg_banner"] = OXBLOOD
PALETTES_R2["gold-reserve"]["buy"] = (
    [(0.0, (112, 166, 248)), (0.5, (64, 116, 212)), (1.0, (32, 68, 152))],
    (235, 244, 255), (16, 32, 80), (170, 205, 255))


def make_chip_fn(bar):
    stops, num_col, rim_d, rim_b = bar

    def chip(ov, price, cy=h2.CHIP_CY):
        txt = f"{price:,}"
        r = pygame.Rect(0, 0, m(168), m(BAR_H))
        r.center = (m(h2.CX), m(cy))
        chip_body_stops(ov, r, m(11), stops, rim_d, rim_b, gloss=0)
        top_sheen(ov, r, m(11), m(12), peak=64)
        num_font = font(18)
        base = _stamp_bold(_glyph_base(txt, num_font, 0), m(0.7))
        bw = base.get_width()
        coin_d, gap = m(22), m(5)
        left = m(h2.CX) - (coin_d + gap + bw) // 2
        coin_glyph(ov, left + coin_d // 2, m(cy), m(11))
        plain_text(ov, txt, num_font,
                   (left + coin_d + gap + bw // 2, m(cy)), num_col,
                   shadow_a=0, weight=m(0.7))
        for bx in (r.left + m(13), r.right - m(13)):
            h2._bolt_dot(ov, bx, m(cy))
    return chip


def make_buttons_fn(buy, can):
    def buttons(ov):
        rad = m(12)
        for cx, cfg, lbl in ((BUY_CX, buy, "BUY"), (CAN_CX, can, "CANCEL")):
            stops, text_col, rim_d, rim_b = cfg
            r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
            r.center = (m(cx), m(BTN_CY))
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, stops, 255), r.topleft)
            top_sheen(ov, r, rad, m(12), peak=28 if lbl == "BUY" else 14)
            bevel_rim(ov, r, rad, rim_d, (*rim_b, 235), w=max(1, m(2.0)))
            plain_text(ov, lbl, font(14), r.center, text_col,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


def make_quatrefoil_fn(glint):
    def quatrefoil(ov):
        cx, cy = m(h2.CX), m(297)
        d, rl = m(13), m(13)
        layer = pygame.Surface(ov.get_size(), pygame.SRCALPHA)
        centers = [(cx, cy - d), (cx, cy + d), (cx - d, cy), (cx + d, cy)]
        for lx, ly in centers:
            pygame.draw.circle(layer, (*Q_DEEP, 120), (lx, ly), rl, max(2, m(6)))
        for lx, ly in centers:
            pygame.draw.circle(layer, (*glint, 180), (lx, ly), rl - m(1),
                               max(1, m(0.5)))
        ov.blit(layer, (0, 0))
    return quatrefoil


_ORIG_BANNER = h2._confirm_tier_banner


def render_colorway(slug, pal, round_no):
    h2.overlay_bullion_chip = make_chip_fn(pal["bar"])
    h2.overlay_buttons = make_buttons_fn(pal["buy"], pal["can"])
    h2.overlay_quatrefoil = make_quatrefoil_fn(pal["glint"])
    leg_pal = pal.get("leg_banner")
    if leg_pal:
        h2._confirm_tier_banner = (
            lambda ov, cx, cy, w, hh, tw, p:
            _ORIG_BANNER(ov, cx, cy, w, hh, tw,
                         leg_pal if tw == "LEGENDARY" else p))
    else:
        h2._confirm_tier_banner = _ORIG_BANNER

    MARGIN, HEAD, GAP = 20, 58, 12
    tiers = ["RARE", "EPIC", "LEGENDARY"]
    strip_w = MARGIN * 2 + len(tiers) * (POP_W + GAP) - GAP
    strip_h = HEAD + POP_H + MARGIN
    strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
    idr = ImageDraw.Draw(strip)
    idr.text((MARGIN, 18), f"{slug} · colourway round_{round_no}",
             fill=(236, 214, 160))
    for i, tier in enumerate(tiers):
        pop = h2.render_popup(tier)
        pil = Image.frombytes("RGB", (POP_W, POP_H),
                              pygame.image.tostring(pop, "RGB"))
        x = MARGIN + i * (POP_W + GAP)
        strip.paste(pil, (x, HEAD))
        idr.text((x + POP_W // 2, HEAD + POP_H + 6), tier,
                 fill=(206, 190, 150), anchor="mt")

    out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1",
                           "colorways", slug)
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"round_{round_no}.png")
    assert out_img.size == (1688, 1040), f"size mismatch: {out_img.size}"
    out_img.save(out)
    print("saved", out)


def main():
    round_no = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    palettes = PALETTES_R1 if round_no == 1 else PALETTES_R2
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2._DRAW_FN[0] = btn._patched_draw()
    try:
        for slug, pal in palettes.items():
            render_colorway(slug, pal, round_no)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
