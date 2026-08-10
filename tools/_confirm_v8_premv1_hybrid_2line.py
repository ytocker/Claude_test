"""hybrid-1 / hybrid-2 · two-line item-name stress test.

Renders each hybrid twice on the EPIC tier — once with the standard short
fixture name, once with a name long enough to trigger _draw_confirm's
two-line wrap — so the collision behaviour of the fixed-position grafts
(bullion bar, banner, quatrefoil) under a wrapped name is visible in one
strip.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid as h1
import _confirm_v8_premv1_hybrid2 as h2

import game.store_data as store_data
import game.store_catalog as store_catalog
from PIL import Image, ImageDraw

LONG_NAME = "CELESTIAL PRISM GUARDIAN"
POP_W, POP_H = 260, 442


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    try:
        draw_fn = h1._patched_draw_confirm()
        panels = []
        for mod, label, render in (
            (h1, "hybrid-1", lambda t: h1.render_popup(draw_fn, t)),
            (h2, "hybrid-2", h2.render_popup),
        ):
            mod.NAMES["EPIC"] = "PRISM WING"
            panels.append((f"{label} · short", render("EPIC")))
            mod.NAMES["EPIC"] = LONG_NAME
            panels.append((f"{label} · 2-line", render("EPIC")))
            mod.NAMES["EPIC"] = "PRISM WING"

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18), f'two-line name stress test · "{LONG_NAME}" · EPIC',
                 fill=(236, 214, 160))
        for i, (label, pop) in enumerate(panels):
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(206, 190, 150), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                               "docs", "confirm_purchase_v8", "premium-v1")
        out = os.path.join(out_dir, "hybrid_2line_test.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
