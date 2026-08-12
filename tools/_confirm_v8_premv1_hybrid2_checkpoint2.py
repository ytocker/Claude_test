"""CHECKPOINT 2 — locked design state after the outline/button sessions.

Locked: D1 platinum-double-bevel frame construction · B5 constellation web ·
bar 168×34 S2-clean at cy=300 with push-down · zone-centred name · cross-
graft buttons (CANCEL's charcoal background on both, BUY's cream text design
on both) · hero bezel + CANCEL border follow the outline system.

Still open: the colour system — GOLD (gold outlines/web/panels) vs SILVER
(silver outlines/web, platinum panels). Both rows render here across all
three tiers. NOT yet ported to game/store.py.

Output: colorways/CHECKPOINT3.png (2 rows × RARE/EPIC/LEGENDARY)
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
TIERS = ["RARE", "EPIC", "LEGENDARY"]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    _, silver_pal = DESIGNS[0]
    can_stops, _can_text, _, _ = silver_pal["can"]
    try:
        MARGIN, HEAD, GAP, ROW_FOOT = 20, 46, 12, 26
        strip_w = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
        strip_h = HEAD + 2 * (POP_H + ROW_FOOT + 24) + MARGIN
        grid = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((MARGIN, 14),
                 "CHECKPOINT 3 · D1 · fs15/border4 buttons · colour system open",
                 fill=(236, 214, 160))

        rows = (("GOLD system", oc.GOLD, oc.PANEL_GOLD),
                ("SILVER system", oc.SILVER, oc.PLATINUM))
        y = HEAD
        for row_label, pal, (bar, buy) in rows:
            fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                      pal["bright"])
            fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
            h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
            store_mod._bg_hook = hook_constellation(pal["glint"],
                                                    BG_DEEP_A, BG_GLINT_A)
            store_mod._frame_hook = fr.frame_double_bevel
            h2.overlay_bullion_chip = cw.make_chip_fn(bar)
            _bs, buy_text, _rd, _rb = buy
            h2.overlay_buttons = make_buttons(
                can_stops, buy_text, pal["deep"], pal["bright"], 15, 4.0)
            idr.text((MARGIN, y + 2), row_label, fill=(206, 190, 150))
            y += 20
            for i, tier in enumerate(TIERS):
                pop = h2.render_popup(tier)
                pil = Image.frombytes("RGB", (POP_W, POP_H),
                                      pygame.image.tostring(pop, "RGB"))
                x = MARGIN + i * (POP_W + GAP)
                grid.paste(pil, (x, y))
                idr.text((x + POP_W // 2, y + POP_H + 5), tier,
                         fill=(170, 170, 195), anchor="mt")
            y += POP_H + ROW_FOOT + 4

        out_img = grid.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "CHECKPOINT3.png")
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
