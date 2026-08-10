"""hybrid-2 price-bar S2 refinement: kill the elliptical gloss blob.

The gloss_sweep patch stacks ellipses whose rounded outline reads as a white
blob on the 168px bar at high peak. This version passes gloss=0 into
chip_body_stops and lays a clean rectangular top_sheen band instead — same
shine level as S2, no ellipse. Rendered next to S2 for comparison.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_chip_options as opts
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import (m, font, coin_glyph, plain_text, chip_body_stops,
                              top_sheen, _glyph_base, _stamp_bold,
                              GOLD_A_RIM_DARK, GOLD_A_RIM_BRIGHT, GOLD_A_NUM)
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BAR_H = opts.BAR_H

G2 = [
    (0.00, (255, 232, 140)),
    (0.32, (244, 208, 92)),
    (0.66, (216, 172, 52)),
    (1.00, (166, 124, 30)),
]


def make_chip_fn(gloss, sheen_peak):
    def chip(ov, price, cy=h2.CHIP_CY):
        txt = f"{price:,}"
        r = pygame.Rect(0, 0, m(168), m(BAR_H))
        r.center = (m(h2.CX), m(cy))
        chip_body_stops(ov, r, m(11), G2, GOLD_A_RIM_DARK,
                        GOLD_A_RIM_BRIGHT, gloss=gloss)
        if sheen_peak:
            top_sheen(ov, r, m(11), m(12), peak=sheen_peak)
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


VARIANTS = [
    ("S2 · ellipse gloss", 190, 0),
    ("S2-clean · linear sheen", 0, 64),
]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    try:
        panels = []
        for label, gloss, sheen in VARIANTS:
            h2.overlay_bullion_chip = make_chip_fn(gloss, sheen)
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "hybrid-2 price bar · S2 vs S2-clean (no gloss ellipse) · EPIC",
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
                           "hybrid2_chip_s2_clean.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
