"""Compact 5×5 button grid: label size × border width, FULL popups at 1×.

Each cell is the complete popup at native game scale, so the buttons are
judged in full context while 25 combinations still fit one figure. Rows: font sizes 14–18. Cols: border widths 2.0–4.0.
Gold system, D1 frame, EPIC, per checkpoint 2.

Output: colorways/button_text_border_grid_v3.png
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
import _confirm_v8_premv1_hybrid2_outline_compare as oc
from _confirm_v8_premv1_hybrid2_button_text_border import make_buttons
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import (CHIP_CY, BG_DEEP_A,
                                                    BG_GLINT_A, _chip_cy_zone)
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
TEXT_SIZES = [14, 15, 16, 17, 18]
RIM_WIDTHS = [2.0, 2.5, 3.0, 3.5, 4.0]
# full popup at native 1x scale per cell
CELL_W, CELL_H = POP_W, POP_H


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    _, silver_pal = DESIGNS[0]
    can_stops, _t, _, _ = silver_pal["can"]
    pal = oc.GOLD
    bar, buy = oc.PANEL_GOLD
    _bs, buy_text, _rd, _rb = buy
    fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = pal["deep"], pal["mid"], pal["bright"]
    fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
    h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
    store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A, BG_GLINT_A)
    store_mod._frame_hook = fr.frame_double_bevel
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)
    try:
        L_MARGIN, T_MARGIN, GAP, HDR = 96, 64, 8, 26
        grid_w = L_MARGIN + len(RIM_WIDTHS) * (CELL_W + GAP) - GAP + 16
        grid_h = T_MARGIN + HDR + len(TEXT_SIZES) * (CELL_H + GAP) - GAP + 16
        grid = Image.new("RGB", (grid_w, grid_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((12, 12),
                 "BUY/CANCEL · label size (rows) x border width (cols) · gold · EPIC",
                 fill=(236, 214, 160))
        for i, w in enumerate(RIM_WIDTHS):
            x = L_MARGIN + i * (CELL_W + GAP)
            tag = " (cur)" if w == 2.0 else ""
            idr.text((x + CELL_W // 2, T_MARGIN + 8),
                     f"border {w:g}{tag}", fill=(206, 190, 150), anchor="mm")
        for r, fpx in enumerate(TEXT_SIZES):
            y = T_MARGIN + HDR + r * (CELL_H + GAP)
            tag = " (cur)" if fpx == 14 else ""
            idr.text((L_MARGIN - 10, y + CELL_H // 2),
                     f"fs {fpx}{tag}", fill=(206, 190, 150), anchor="rm")
            for i, rim_w in enumerate(RIM_WIDTHS):
                h2.overlay_buttons = make_buttons(
                    can_stops, buy_text, pal["deep"], pal["bright"], fpx, rim_w)
                pop = h2.render_popup("EPIC")
                pil = Image.frombytes("RGB", (POP_W, POP_H),
                                      pygame.image.tostring(pop, "RGB"))
                grid.paste(pil, (L_MARGIN + i * (CELL_W + GAP), y))
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "button_text_border_grid_v3.png")
        grid.save(out)
        print("saved", out, grid.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
