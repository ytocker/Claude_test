"""hybrid-2 FINAL — every locked decision assembled.

Recipe: exec-patched base (chip/buttons suppressed, bg hook injected) ·
B5 constellation-web background ornament · price bar 168×34 S2-clean at
cy=300 with two-line push-down · B2 buttons 99×42, BUY matched to the panel
colour with T3 cream text · rarity banner at cy=402 over the shelf, flanked
by the bottom gems.

Output: colorways/final_showcase.png — rows = the two matched colourways
(#2 two-metals silver, #4 ivory-manuscript ivory), columns = RARE/EPIC/
LEGENDARY, so the final pick is down to one colour decision.
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
import _confirm_v8_premv1_hybrid2_bg_scribble as bgmod
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
CHIP_CY = 300
BG_DEEP_A, BG_GLINT_A = 110, 100   # B5 round_2 alphas

TIERS = ["RARE", "EPIC", "LEGENDARY"]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: {v: h2.PRICES[k] for k, v in h2.SIDS.items()}.get(sid, 0)
    h2._DRAW_FN[0] = bgmod._patched_draw_with_hook()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    try:
        MARGIN, HEAD, GAP, ROW_FOOT = 20, 46, 12, 26
        strip_w = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
        strip_h = HEAD + len(DESIGNS) * (POP_H + ROW_FOOT + 24) + MARGIN
        grid = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(grid)
        idr.text((MARGIN, 14),
                 "FINAL · hybrid-2 · B5 constellation-web · bar cy=300 · B2 buttons",
                 fill=(236, 214, 160))

        y = HEAD
        for row_label, pal in DESIGNS:
            store_mod._bg_hook = hook_constellation(pal["glint"],
                                                    BG_DEEP_A, BG_GLINT_A)
            h2.overlay_bullion_chip = cw.make_chip_fn(pal["bar"])
            h2.overlay_buttons = cw.make_buttons_fn(pal["buy"], pal["can"])
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
                           "final_showcase.png")
        out_img.save(out)
        print("saved", out, out_img.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        if hasattr(store_mod, "_bg_hook"):
            del store_mod._bg_hook


if __name__ == "__main__":
    main()
