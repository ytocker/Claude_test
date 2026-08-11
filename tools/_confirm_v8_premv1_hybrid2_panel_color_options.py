"""Panel-colour options for the bar + BUY pair against the gold craft layer.

Context: gold frame + gold constellation web + indigo body + charcoal
CANCEL are fixed; the gold panels (bar/BUY) read poorly. Five pair options
rendered on the D1 frame (held constant so only the panel colour varies),
EPIC tier, all with the locked S2-clean bar finish and T3 BUY text.

  E1 · gold (current, reference)
  E2 · platinum — the earlier two-metals pick, now inside the gold frame
  E3 · moonstone — pale blue, kin to the indigo body, cool vs gold
  E4 · ivory — warm neutral bridging the gold without repeating it
  E5 · sapphire — jewel-tone panels tying to the tier-gem language
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_frames as fr
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import (CHIP_CY, BG_DEEP_A,
                                                    BG_GLINT_A, _chip_cy_zone)
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442


def _pair(stops, num_col, rim_d, rim_b, buy_text):
    bar = (stops, num_col, rim_d, rim_b)
    buy = ([(0.00, stops[0][1]), (0.40, stops[1][1]),
            (1.00, tuple(int(v * 0.9) for v in stops[-1][1]))],
           buy_text, rim_d, rim_b)
    return bar, buy


GOLD = _pair([(0.00, (244, 214, 128)), (0.35, (224, 186, 98)),
              (0.70, (196, 160, 78)), (1.00, (146, 114, 50))],
             (52, 28, 4), (78, 50, 14), (250, 226, 160), (255, 248, 220))
PLATINUM = _pair([(0.00, (240, 244, 252)), (0.35, (214, 220, 232)),
                  (0.70, (178, 186, 202)), (1.00, (140, 148, 168))],
                 (30, 36, 60), (70, 78, 98), (255, 255, 255), (255, 248, 220))
MOONSTONE = _pair([(0.00, (226, 238, 255)), (0.35, (196, 214, 244)),
                   (0.70, (160, 180, 220)), (1.00, (120, 140, 185))],
                  (24, 34, 68), (54, 68, 110), (235, 245, 255), (255, 248, 220))
IVORY = _pair([(0.00, (252, 248, 238)), (0.35, (238, 230, 212)),
               (0.70, (218, 208, 186)), (1.00, (188, 176, 150))],
              (56, 40, 20), (110, 96, 70), (255, 255, 248), (255, 248, 220))
SAPPHIRE = _pair([(0.00, (118, 168, 248)), (0.35, (84, 132, 224)),
                  (0.70, (56, 100, 192)), (1.00, (34, 66, 144))],
                 (235, 244, 255), (16, 32, 80), (170, 205, 255), (240, 248, 255))

OPTIONS = [
    ("E1 · gold (current)", GOLD),
    ("E2 · platinum", PLATINUM),
    ("E3 · moonstone", MOONSTONE),
    ("E4 · ivory", IVORY),
    ("E5 · sapphire", SAPPHIRE),
]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2._DRAW_FN[0] = fr._patched_draw_frames()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    _, silver = DESIGNS[0]
    store_mod._bg_hook = hook_constellation(fr.GEM_SIL, BG_DEEP_A, BG_GLINT_A)
    store_mod._frame_hook = fr.frame_double_bevel   # held constant for judging
    try:
        panels = []
        for label, (bar, buy) in OPTIONS:
            h2.overlay_bullion_chip = cw.make_chip_fn(bar)
            h2.overlay_buttons = cw.make_buttons_fn(buy, silver["can"])
            panels.append((label, h2.render_popup("EPIC")))

        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(panels) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "FIGURE E · bar+BUY panel colours vs gold craft layer · D1 frame · EPIC",
                 fill=(236, 214, 160))
        for i, (label, pop) in enumerate(panels):
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(170, 170, 195), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "panel_color_options_v1.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
