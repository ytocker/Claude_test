"""LOCKED final confirm-popup design — the canonical renderer.

Silver two-metals colourway only. Every decision from the design sessions:
B5 constellation-web background · platinum price bar 168×34 S2-clean at
cy=300 · B2 buttons 99×42 with panel-matched silver BUY and T3 cream text ·
rarity banner at cy=402 flanked by gems · zone-centred item name (1 line at
y=237, 2-line block spread symmetrically around it).

NOT yet ported to game/store.py — this script is the reference for that port.
Output: docs/confirm_purchase_v8/premium-v1/colorways/FINAL_locked.png
(RARE · EPIC · LEGENDARY strip, 1688×1040).
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
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import (_patched_draw_final,
                                                    _chip_cy_zone,
                                                    CHIP_CY, BG_DEEP_A,
                                                    BG_GLINT_A)
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
    h2._DRAW_FN[0] = _patched_draw_final()
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    silver_label, silver = DESIGNS[0]
    store_mod._bg_hook = hook_constellation(silver["glint"], BG_DEEP_A, BG_GLINT_A)
    h2.overlay_bullion_chip = cw.make_chip_fn(silver["bar"])
    h2.overlay_buttons = cw.make_buttons_fn(silver["buy"], silver["can"])
    try:
        MARGIN, HEAD, GAP = 20, 58, 12
        strip_w = MARGIN * 2 + len(TIERS) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + MARGIN
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 18),
                 "LOCKED FINAL · silver two-metals · B5 · bar 300 · zone-centred name",
                 fill=(236, 214, 160))
        for i, tier in enumerate(TIERS):
            pop = h2.render_popup(tier)
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), tier,
                     fill=(206, 190, 150), anchor="mt")

        out_img = strip.resize((strip_w * 2, strip_h * 2), Image.LANCZOS)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "FINAL_locked.png")
        assert out_img.size == (1688, 1040)
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
