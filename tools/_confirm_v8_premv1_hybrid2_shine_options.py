"""hybrid-2 price-bar shine options: G2 classic bullion, four shine levels.

Shine is layered from three levers — the gloss-sweep peak, a hotter top
gradient stop, and a diagonal mirror glint streaking across the bar — so the
options escalate from the plain G2 finish to full mirror polish. The glint is
drawn under the coin/numeral so the price stays crisp.
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
                              _glyph_base, _stamp_bold,
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
G2_HOT_TOP = [
    (0.00, (255, 248, 190)),
    (0.22, (250, 224, 116)),
    (0.60, (222, 178, 58)),
    (1.00, (166, 124, 30)),
]
RIM_MIRROR = (255, 250, 220)

SHINE_OPTIONS = [
    ("S1 · G2 as picked", G2, 120, GOLD_A_RIM_BRIGHT, False),
    ("S2 · high gloss", G2, 190, GOLD_A_RIM_BRIGHT, False),
    ("S3 · hot top + glint", G2_HOT_TOP, 150, GOLD_A_RIM_BRIGHT, True),
    ("S4 · mirror polish", G2_HOT_TOP, 200, RIM_MIRROR, True),
]


def _glint(ov, r):
    g = pygame.Surface(r.size, pygame.SRCALPHA)
    w, h = r.size
    slant = int(h * 0.55)
    x0 = int(w * 0.16)
    band_w = int(w * 0.09)
    for bx, bw, a in [(x0, band_w, 95), (x0 + int(band_w * 2.1), band_w // 2, 55)]:
        poly = [(bx + slant, 0), (bx + bw + slant, 0), (bx + bw, h), (bx, h)]
        pygame.draw.polygon(g, (255, 255, 255, a), poly)
    mask = pygame.Surface(r.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=m(11))
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    ov.blit(g, r.topleft)


def make_chip_fn(stops, gloss, rim_bright, glint):
    def chip(ov, price, cy=h2.CHIP_CY):
        txt = f"{price:,}"
        r = pygame.Rect(0, 0, m(168), m(BAR_H))
        r.center = (m(h2.CX), m(cy))
        chip_body_stops(ov, r, m(11), stops, GOLD_A_RIM_DARK,
                        rim_bright, gloss=gloss)
        if glint:
            _glint(ov, r)
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
        for label, stops, gloss, rim, glint in SHINE_OPTIONS:
            h2.overlay_bullion_chip = make_chip_fn(stops, gloss, rim, glint)
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 f"hybrid-2 price-bar SHINE options · G2 bullion · height {BAR_H} · EPIC",
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
                           "hybrid2_chip_shine_options.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
