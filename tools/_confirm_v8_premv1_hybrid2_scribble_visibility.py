"""Constellation-web visibility options on the checkpoint-3 design.

Five levels from the current alphas upward, including a "bold" variant that
double-draws the web with a 1px offset to thicken every line and star.
Gold system, D1 frame, fs15/border4 buttons, EPIC, full popups at 1×.

Output: colorways/scribble_visibility_v1.png
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
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store_cards import m
from PIL import Image, ImageDraw

POP_W, POP_H = 260, 442


def bold_hook(glint, deep_a, glint_a):
    """Double-draw with a 1px offset — thickens every web line and star."""
    base = hook_constellation(glint, deep_a, glint_a)

    def hook(big):
        base(big)
        shifted = pygame.Surface(big.get_size(), pygame.SRCALPHA)
        base(shifted)
        big.blit(shifted, (m(0.5), m(0.5)))
    return hook


# (label, hook factory, deep alpha, glint alpha)
OPTIONS = [
    ("V1 · current (110/100)", hook_constellation, 110, 100),
    ("V2 · lifted (140/125)", hook_constellation, 140, 125),
    ("V3 · strong (170/150)", hook_constellation, 170, 150),
    ("V4 · bold lines (140/125)", bold_hook, 140, 125),
    ("V5 · max (205/180)", hook_constellation, 205, 180),
]


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
    store_mod._frame_hook = fr.frame_double_bevel
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)
    h2.overlay_buttons = make_buttons(
        can_stops, buy_text, pal["deep"], pal["bright"], 15, 4.0)
    try:
        MARGIN, HEAD, GAP = 20, 50, 12
        strip_w = MARGIN * 2 + len(OPTIONS) * (POP_W + GAP) - GAP
        strip_h = HEAD + POP_H + 28
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 14),
                 "constellation web visibility · gold · D1 · fs15/border4 · EPIC",
                 fill=(236, 214, 160))
        for i, (label, factory, da, ga) in enumerate(OPTIONS):
            store_mod._bg_hook = factory(pal["glint"], da, ga)
            pop = h2.render_popup("EPIC")
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (POP_W + GAP)
            strip.paste(pil, (x, HEAD))
            idr.text((x + POP_W // 2, HEAD + POP_H + 6), label,
                     fill=(170, 170, 195), anchor="mt")
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "scribble_visibility_v1.png")
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
