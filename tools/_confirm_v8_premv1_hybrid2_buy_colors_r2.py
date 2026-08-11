"""hybrid-2 BUY colour round_2 — three critique survivors, refined.

All panels: B2 geometry (99×42), S2-clean bullion price bar, indigo CANCEL.
Y1 tests the user's suggestion — BUY in the exact G2 panel colour of the
price chip. Y3 is deliberately tier-coloured to probe whether a per-tier
BUY survives the critique.
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
                              drop_shadow, plain_text,
                              CARD_RING_BRIGHT, CARD_RING_DEEP,
                              GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM)
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BTN_W, BTN_H, BTN_CY = 99, 42, 360
BUY_CX, CAN_CX = 76, 184

G2 = btn.G2

# (label, buy_stops, rim_d, rim_b, text_col)
OPTIONS = [
    ("Z1 · bullion match", [
        (0.00, (255, 232, 140)),
        (0.40, (238, 198, 80)),
        (1.00, (150, 110, 26)),
    ], GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM),
    ("Z2 · bright amber", [(0.0, (190, 128, 40)), (1.0, (120, 72, 14))],
     GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, (255, 248, 220)),
    ("Z3 · emerald jewel", [
        (0.00, (96, 196, 118)),
        (0.50, (52, 150, 84)),
        (1.00, (22, 96, 46)),
    ], GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, (232, 255, 238)),
]


def make_buttons_fn(stops, rim_d, rim_b, text_col):
    def buttons(ov):
        rad = m(12)
        for cx, w, h, is_cancel, fpx in (
            (BUY_CX, BTN_W, BTN_H, False, 16),
            (CAN_CX, BTN_W, BTN_H, True, 14),
        ):
            r = pygame.Rect(0, 0, m(w), m(h))
            r.center = (m(cx), m(BTN_CY))
            if is_cancel:
                s = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
                lab_c, pk = (150, 155, 200), 14
                rd, rb = CARD_RING_DEEP, CARD_RING_BRIGHT
                lbl = "CANCEL"
            else:
                s, lab_c, pk = stops, text_col, 28
                rd, rb = rim_d, rim_b
                lbl = "BUY"
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, s, 255), r.topleft)
            top_sheen(ov, r, rad, m(12), peak=pk)
            bevel_rim(ov, r, rad, rd, (*rb, 235), w=max(1, m(2.0)))
            plain_text(ov, lbl, font(fpx), r.center, lab_c,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2._DRAW_FN[0] = btn._patched_draw()
    h2.overlay_bullion_chip = btn.final_chip
    try:
        panels = []
        for label, stops, rd, rb, tc in OPTIONS:
            h2.overlay_buttons = make_buttons_fn(stops, rd, rb, tc)
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "hybrid-2 BUY colour round_2 · B2 buttons 99x42 · EPIC",
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
                           "hybrid2_buy_colors_r2.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
