"""hybrid-2 price-bar golden options: five tones on the gold end of the axis.

All five sit at green/red ≥ 0.80 — unambiguously gold rather than orange —
and fan out along lightness/saturation: from a deep saturated 22k through
bullion and bright 24k to pale gold leaf.
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
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442

GOLD_OPTIONS = [
    ("G1 · deep 22k", [
        (0.00, (250, 210, 92)),
        (0.32, (238, 188, 62)),
        (0.66, (208, 156, 36)),
        (1.00, (156, 112, 22)),
    ]),
    ("G2 · classic bullion", [
        (0.00, (255, 232, 140)),
        (0.32, (244, 208, 92)),
        (0.66, (216, 172, 52)),
        (1.00, (166, 124, 30)),
    ]),
    ("G3 · bright 24k", [
        (0.00, (255, 240, 150)),
        (0.32, (252, 216, 88)),
        (0.66, (230, 184, 52)),
        (1.00, (178, 134, 32)),
    ]),
    ("G4 · champagne", [
        (0.00, (255, 242, 178)),
        (0.32, (248, 222, 120)),
        (0.66, (224, 190, 78)),
        (1.00, (174, 138, 46)),
    ]),
    ("G5 · gold leaf", [
        (0.00, (255, 248, 200)),
        (0.32, (250, 232, 150)),
        (0.66, (232, 204, 104)),
        (1.00, (184, 152, 64)),
    ]),
]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    try:
        panels = []
        for label, stops in GOLD_OPTIONS:
            h2.overlay_bullion_chip = opts.make_chip_fn(stops)
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 f"hybrid-2 price-bar GOLD options · height {opts.BAR_H} · EPIC",
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
                           "hybrid2_chip_gold_options.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
