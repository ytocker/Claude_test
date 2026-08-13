"""Current in-game confirm popup vs the locked CHECKPOINT 5 design.

Left panel is the true shipping draw — the ORIGINAL StoreScene._draw_confirm
with no patches, hooks, or overlays. The two right panels are the locked
design in both candidate colour systems (that decision is still open).
EPIC / PRISM WING / 1,400 across all panels, rendered at 2x.

Output: colorways/current_vs_checkpoint5_v1.png
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
from _confirm_v8_premv1_hybrid2_buy_accents import make_buttons_accent
from _confirm_v8_premv1_hybrid2_buy_accents4 import make_inner_keyline
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442
BG_DEEP_A, BG_GLINT_A = 155, 138
TIER = "EPIC"


def render_stock():
    sid = h2.SIDS[TIER]

    class _Stub:
        _confirm = sid
        _confirm_panel = None
        confirm_yes_rect = None
        confirm_no_rect = None

        @staticmethod
        def _disp_name(_sid):
            return h2.NAMES[TIER]

    surf = pygame.Surface((360, 640))
    surf.fill((8, 8, 20))
    store_mod.StoreScene._draw_confirm(_Stub(), surf)
    return surf.subsurface(pygame.Rect(50, 40, POP_W, POP_H)).copy()


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1400
    try:
        panels = [("CURRENT (in game)", render_stock())]

        h2.overlay_quatrefoil = lambda ov: None
        h2.CHIP_CY = CHIP_CY
        h2._chip_cy = _chip_cy_zone
        _, silver_pal = DESIGNS[0]
        can_stops, _t, _, _ = silver_pal["can"]
        systems = (("LOCKED · gold", oc.GOLD, oc.PANEL_GOLD, (26, 17, 4)),
                   ("LOCKED · silver", oc.SILVER, oc.PLATINUM, (14, 16, 30)))
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
            panels.append((label, h2.render_popup(TIER)))

        MARGIN, HEAD, GAP = 24, 52, 20
        cell_w, cell_h = POP_W * 2, POP_H * 2
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + 34
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "confirm popup · current in-game vs CHECKPOINT 5 · EPIC · 2x",
                 fill=(236, 214, 160))
        for i, (label, pop) in enumerate(panels):
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (cell_w + GAP)
            strip.paste(pil.resize((cell_w, cell_h), Image.LANCZOS), (x, HEAD))
            idr.text((x + cell_w // 2, HEAD + cell_h + 10), label,
                     fill=(206, 190, 150), anchor="mt")
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "current_vs_checkpoint5_v1.png")
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
