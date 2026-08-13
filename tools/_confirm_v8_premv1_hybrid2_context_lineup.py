"""Store-context lineup: category screen · live confirm · chosen design.

Four full 360x640 gameplay frames at one uniform scale: the item-card grid
as the game shows it, the confirm popup currently live in gameplay, and the
locked checkpoint-5 design in both candidate colour systems — all around
the same real catalog item.

Output: colorways/store_context_lineup_v1.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_frames as fr
import _confirm_v8_premv1_hybrid2_outline_compare as oc
from _confirm_v8_premv1_hybrid2_buy_accents import make_buttons_accent
from _confirm_v8_premv1_hybrid2_buy_accents4 import make_inner_keyline
from _confirm_v8_premv1_hybrid2_current_vs_locked2 import (SID, store_frame,
                                                           render_locked_frame,
                                                           _chip_cy_zone_named)
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.config import W, H
from PIL import Image, ImageDraw

BG_DEEP_A, BG_GLINT_A = 155, 138


def main():
    _orig_bal = store_data.balance
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    try:
        scene = StoreScene()
        scene.view = "category"
        scene.tab = 0
        scene.page = 0
        tier = store_catalog.rarity(SID)

        panels = [("STORE CATEGORY (as in game)", store_frame(scene, None)),
                  ("CURRENT confirm (live gameplay)", store_frame(scene, SID))]

        h2.CHIP_CY = CHIP_CY
        h2._chip_cy = lambda _tier: _chip_cy_zone_named(scene._disp_name(SID))
        _, silver_pal = DESIGNS[0]
        can_stops, _t, _, _ = silver_pal["can"]
        systems = (("CHOSEN · gold", oc.GOLD, oc.PANEL_GOLD, (26, 17, 4)),
                   ("CHOSEN · silver", oc.SILVER, oc.PLATINUM, (14, 16, 30)))
        for label, pal, (bar, buy), shadow in systems:
            fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                      pal["bright"])
            fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
            h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
            store_mod._bg_hook = hook_constellation(pal["glint"],
                                                    BG_DEEP_A, BG_GLINT_A)
            store_mod._frame_hook = fr.frame_double_bevel
            h2.overlay_bullion_chip = cw.make_chip_fn(bar)
            _bs, buy_text, _rd, _rb = buy
            h2.overlay_buttons = make_buttons_accent(
                can_stops, buy_text, pal["deep"], pal["bright"],
                make_inner_keyline(pal["glint"], pal["bright"], shadow))
            panels.append((label, render_locked_frame(scene, tier)))

        MARGIN, HEAD, GAP = 24, 52, 20
        cell_w, cell_h = W * 2, H * 2
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + 34
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "store context lineup · category cards · live confirm · "
                 f"chosen design · {scene._disp_name(SID)} ({tier}) · 2x",
                 fill=(236, 214, 160))
        for i, (label, surf) in enumerate(panels):
            pil = Image.frombytes("RGB", (W, H), pygame.image.tostring(surf, "RGB"))
            x = MARGIN + i * (cell_w + GAP)
            strip.paste(pil.resize((cell_w, cell_h), Image.LANCZOS), (x, HEAD))
            idr.text((x + cell_w // 2, HEAD + cell_h + 10), label,
                     fill=(206, 190, 150), anchor="mt")
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "store_context_lineup_v1.png")
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        store_data.balance = _orig_bal
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
