"""Hero-ring dominance ladder on the checkpoint-5 design.

The in-game bezel is the layered triple ring hardcoded in cabochon_glass
(dark keyline, CARD_RING gold rim, pale glint). The locked design stamps an
opaque 1.6px outline-gold circle on top, which reads too dominant. Five
rungs grade that stamped circle from absent (pure in-game bezel) up to the
current locked value; each panel shows the full popup with a 2x zoom of the
hero zone below.

Output: colorways/hero_ring_ladder_v2.png
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
from PIL import Image, ImageDraw, ImageFont

POP_W, POP_H = 260, 442
BG_DEEP_A, BG_GLINT_A = 155, 138

# (role line, detail line, hero_circle)
RUNGS = [
    ("R0 · CURRENT — as in game today", "stock bezel, no added circle", None),
    ("R1 · IN-BETWEEN 1", "+1.0px gold circle, alpha 70", (1.0, 70)),
    ("R2 · IN-BETWEEN 2", "+1.2px gold circle, alpha 120", (1.2, 120)),
    ("R3 · IN-BETWEEN 3", "+1.4px gold circle, alpha 180", (1.4, 180)),
    ("R4 · CHOSEN DESIGN — current lock", "1.6px opaque gold circle", (1.6, 255)),
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
    store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A, BG_GLINT_A)
    store_mod._frame_hook = fr.frame_double_bevel
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)
    h2.overlay_buttons = make_buttons_accent(
        can_stops, buy_text, pal["deep"], pal["bright"],
        make_inner_keyline(pal["glint"], pal["bright"], (26, 17, 4)))
    try:
        f_head = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        f_role = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        f_detail = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        MARGIN, HEAD, GAP = 24, 64, 16
        cell_w, cell_h = POP_W * 2, POP_H * 2
        strip_w = MARGIN * 2 + len(RUNGS) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + 96
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "hero ring dominance ladder · checkpoint 5 · gold · EPIC · 2x",
                 fill=(236, 214, 160), font=f_head)
        for i, (role, detail, circle) in enumerate(RUNGS):
            h2._DRAW_FN[0] = oc._patched_draw(pal["ring"], hero_circle=circle)
            pop = h2.render_popup("EPIC")
            pil = Image.frombytes("RGB", (POP_W, POP_H),
                                  pygame.image.tostring(pop, "RGB"))
            x = MARGIN + i * (cell_w + GAP)
            strip.paste(pil.resize((cell_w, cell_h), Image.LANCZOS), (x, HEAD))
            idr.text((x + cell_w // 2, HEAD + cell_h + 14), role,
                     fill=(236, 214, 160), anchor="mt", font=f_role)
            idr.text((x + cell_w // 2, HEAD + cell_h + 50), detail,
                     fill=(180, 180, 205), anchor="mt", font=f_detail)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "hero_ring_ladder_v4.png")
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
