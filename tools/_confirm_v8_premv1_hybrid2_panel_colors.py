"""hybrid-2 shared panel-gold refinement — chip and BUY move together.

The G2 gradient is now the identity of both the price bar and the BUY
button, so each panel applies one candidate palette to BOTH: the bar gets
the S2-clean finish (gloss 0, linear sheen), BUY derives its Z1 stops from
the same ramp with a ~10% darker foot so the bar stays the brightest gold.
Text is the locked T3 treatment (CANCEL style, cream).

  P1 · G2 as picked (reference)
  P2 · honey — warmer, a touch more red
  P3 · lemon gold — cooler, yellower
  P4 · antique — deeper, aged
  P5 · airy — lighter, brighter
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
                              GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM)
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BAR_H = 34
BTN_W, BTN_H, BTN_CY = 99, 42, 360
BUY_CX, CAN_CX = 76, 184
BUY_TEXT = (255, 248, 220)

PALETTES = [
    ("P1 · G2 as picked", [
        (0.00, (255, 232, 140)), (0.32, (244, 208, 92)),
        (0.66, (216, 172, 52)), (1.00, (166, 124, 30))]),
    ("P2 · honey", [
        (0.00, (255, 226, 124)), (0.32, (244, 198, 78)),
        (0.66, (210, 162, 44)), (1.00, (160, 116, 26))]),
    ("P3 · lemon gold", [
        (0.00, (255, 238, 156)), (0.32, (242, 212, 104)),
        (0.66, (210, 176, 62)), (1.00, (158, 126, 36))]),
    ("P4 · antique", [
        (0.00, (244, 214, 116)), (0.32, (226, 186, 72)),
        (0.66, (192, 148, 40)), (1.00, (140, 102, 22))]),
    ("P5 · airy", [
        (0.00, (255, 240, 168)), (0.32, (250, 220, 116)),
        (0.66, (226, 188, 72)), (1.00, (178, 138, 42))]),
]


def _darken(c, f=0.9):
    return tuple(int(v * f) for v in c)


def buy_stops_from(chip_stops):
    return [(0.00, chip_stops[0][1]),
            (0.40, chip_stops[1][1]),
            (1.00, _darken(chip_stops[3][1], 0.9))]


def make_chip_fn(stops):
    def chip(ov, price, cy=h2.CHIP_CY):
        txt = f"{price:,}"
        r = pygame.Rect(0, 0, m(168), m(BAR_H))
        r.center = (m(h2.CX), m(cy))
        chip_body_stops(ov, r, m(11), stops, GOLD_A_RIM_DARK,
                        GOLD_A_RIM_BRIGHT, gloss=0)
        top_sheen(ov, r, m(11), m(12), peak=64)
        num_font = font(18)
        base = _stamp_bold(_glyph_base(txt, num_font, 0), m(0.7))
        bw = base.get_width()
        coin_d, gap = m(22), m(5)
        left = m(h2.CX) - (coin_d + gap + bw) // 2
        coin_glyph(ov, left + coin_d // 2, m(cy), m(11))
        plain_text(ov, txt, num_font,
                   (left + coin_d + gap + bw // 2, m(cy)), GOLD_A_NUM,
                   shadow_a=0, weight=m(0.7))
        for bx in (r.left + m(13), r.right - m(13)):
            h2._bolt_dot(ov, bx, m(cy))
    return chip


def make_buttons_fn(chip_stops):
    z_stops = buy_stops_from(chip_stops)

    def buttons(ov):
        rad = m(12)
        for cx, is_cancel in ((BUY_CX, False), (CAN_CX, True)):
            r = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
            r.center = (m(cx), m(BTN_CY))
            if is_cancel:
                s = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
                lab_c, pk, lbl = (150, 155, 200), 14, "CANCEL"
                rd, rb = CARD_RING_DEEP, CARD_RING_BRIGHT
            else:
                s, lab_c, pk, lbl = z_stops, BUY_TEXT, 28, "BUY"
                rd, rb = GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, s, 255), r.topleft)
            top_sheen(ov, r, rad, m(12), peak=pk)
            bevel_rim(ov, r, rad, rd, (*rb, 235), w=max(1, m(2.0)))
            plain_text(ov, lbl, font(14), r.center, lab_c,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2._DRAW_FN[0] = btn._patched_draw()
    try:
        panels = []
        for label, stops in PALETTES:
            h2.overlay_bullion_chip = make_chip_fn(stops)
            h2.overlay_buttons = make_buttons_fn(stops)
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "hybrid-2 shared panel gold · chip + BUY together · T3 text · EPIC",
                 fill=(236, 214, 160))
        for i, (label, pop) in enumerate(panels):
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(206, 190, 150), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1",
                           "hybrid2_panel_colors.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
