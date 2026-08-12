"""Button label size × border width grid on the checkpoint-2 design.

Rows: BUY/CANCEL label font size (14 current, 16, 18).
Cols: button perimeter (bevel rim) width (2.0 current, 3.0, 4.0 logical px).
Gold system, D1 frame, EPIC tier — everything else per checkpoint 2.

Output: colorways/button_text_border_grid_v1.png
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
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import (CHIP_CY, BG_DEEP_A,
                                                    BG_GLINT_A, _chip_cy_zone)
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
TEXT_SIZES = [14, 16, 18]
RIM_WIDTHS = [2.0, 3.0, 4.0]


def make_buttons(can_stops, buy_text, rim_d, rim_b, fpx, rim_w):
    from game.store_cards import (vgrad_stops, bevel_rim, top_sheen,
                                  drop_shadow, plain_text, font)

    def buttons(ov):
        rad = m(12)
        for cx, lbl in ((76, "BUY"), (184, "CANCEL")):
            r = pygame.Rect(0, 0, m(99), m(42))
            r.center = (m(cx), m(360))
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, can_stops, 255), r.topleft)
            top_sheen(ov, r, rad, m(12), peak=14)
            bevel_rim(ov, r, rad, rim_d, (*rim_b, 235), w=max(1, m(rim_w)))
            plain_text(ov, lbl, font(fpx), r.center, buy_text,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


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
        MARGIN, HEAD, GAP, ROW_FOOT = 20, 46, 12, 26
        strip_w = MARGIN * 2 + len(RIM_WIDTHS) * (POP_W + GAP) - GAP
        strip_h = HEAD + len(TEXT_SIZES) * (POP_H + ROW_FOOT + 24) + MARGIN
        grid = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((MARGIN, 14),
                 "button label size (rows) x border width (cols) · gold · D1 · EPIC",
                 fill=(236, 214, 160))

        y = HEAD
        for fpx in TEXT_SIZES:
            tag = "  (current)" if fpx == 14 else ""
            idr.text((MARGIN, y + 2), f"text size {fpx}{tag}",
                     fill=(206, 190, 150))
            y += 20
            for i, rim_w in enumerate(RIM_WIDTHS):
                h2.overlay_buttons = make_buttons(
                    can_stops, buy_text, pal["deep"], pal["bright"], fpx, rim_w)
                pop = h2.render_popup("EPIC")
                pil = Image.frombytes("RGB", (POP_W, POP_H),
                                      pygame.image.tostring(pop, "RGB"))
                x = MARGIN + i * (POP_W + GAP)
                grid.paste(pil, (x, y))
                wt = "  (current)" if rim_w == 2.0 else ""
                idr.text((x + POP_W // 2, y + POP_H + 5),
                         f"fs={fpx} · border={rim_w:g}{wt}",
                         fill=(170, 170, 195), anchor="mt")
            y += POP_H + ROW_FOOT + 4

        out_img = grid.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "button_text_border_grid_v1.png")
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
