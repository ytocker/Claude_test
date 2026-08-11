"""Colourways #2 and #4 with BUY matched to the chip panel colour.

Four EPIC panels: each concept's round_2 (gold BUY) next to a variant whose
BUY derives its gradient from the price bar's own ramp (same top/mid, ~10%
darker foot so the bar stays brightest). Matched BUYs take dark text in the
bar's numeral colour — cream would wash out on the bright panel fills.
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
import _confirm_v8_premv1_hybrid2_colorway as cw
import game.store_data as store_data
import game.store_catalog as store_catalog
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442


def _darken(c, f=0.9):
    return tuple(int(v * f) for v in c)


def matched_buy(bar):
    stops, num_col, rim_d, rim_b = bar
    buy_stops = [(0.00, stops[0][1]), (0.40, stops[1][1]),
                 (1.00, _darken(stops[-1][1], 0.9))]
    return (buy_stops, num_col, rim_d, rim_b)


def variant(slug, pal, matched):
    pal = dict(pal)
    if matched:
        pal["buy"] = matched_buy(pal["bar"])
    return pal


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2._DRAW_FN[0] = btn._patched_draw()
    try:
        jobs = [
            ("#2 · gold BUY (r2)", cw.PALETTES_R2["two-metals"], False),
            ("#2 · silver BUY match", cw.PALETTES_R2["two-metals"], True),
            ("#4 · gold BUY (r2)", cw.PALETTES_R2["ivory-manuscript"], False),
            ("#4 · ivory BUY match", cw.PALETTES_R2["ivory-manuscript"], True),
        ]
        panels = []
        for label, pal, matched in jobs:
            p = variant(label, pal, matched)
            h2.overlay_bullion_chip = cw.make_chip_fn(p["bar"])
            h2.overlay_buttons = cw.make_buttons_fn(p["buy"], p["can"])
            h2.overlay_quatrefoil = cw.make_quatrefoil_fn(p["glint"])
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "colourways #2 / #4 · BUY matched to chip panel colour · EPIC",
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
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "matched_buy_2_4.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost


if __name__ == "__main__":
    main()
