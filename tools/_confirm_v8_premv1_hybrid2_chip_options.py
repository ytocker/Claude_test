"""hybrid-2 price-bar options: taller bar (28→34) × gold-tone backgrounds.

Four EPIC popups side by side. Option A keeps the current GOLD_A gradient as
the reference; B/C/D step the gradient toward purer gold by raising the green
channel relative to red — same rims, same coin, same numeral throughout, so
only the background tone and the extra height read as differences.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import (m, font, coin_glyph, plain_text, chip_body_stops,
                              _glyph_base, _stamp_bold,
                              GOLD_A_STOPS, GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT,
                              GOLD_A_NUM)
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BAR_H = 34

OPTIONS = [
    ("A · current gold", GOLD_A_STOPS),
    ("B · mint gold", [
        (0.00, (250, 214, 110)),
        (0.32, (238, 192, 76)),
        (0.66, (210, 158, 44)),
        (1.00, (160, 112, 26)),
    ]),
    ("C · classic bullion", [
        (0.00, (255, 232, 140)),
        (0.32, (244, 208, 92)),
        (0.66, (216, 172, 52)),
        (1.00, (166, 124, 30)),
    ]),
    ("D · champagne", [
        (0.00, (255, 242, 178)),
        (0.32, (248, 222, 120)),
        (0.66, (224, 190, 78)),
        (1.00, (174, 138, 46)),
    ]),
]


def make_chip_fn(stops):
    def chip(ov, price, cy=h2.CHIP_CY):
        txt = f"{price:,}"
        r = pygame.Rect(0, 0, m(168), m(BAR_H))
        r.center = (m(h2.CX), m(cy))
        chip_body_stops(ov, r, m(11), stops, GOLD_A_RIM_DARK,
                        GOLD_A_RIM_BRIGHT, gloss=120)
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


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    try:
        panels = []
        for label, stops in OPTIONS:
            h2.overlay_bullion_chip = make_chip_fn(stops)
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 f"hybrid-2 price-bar options · height 28 -> {BAR_H} · gold tones · EPIC",
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
                           "hybrid2_chip_options.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
