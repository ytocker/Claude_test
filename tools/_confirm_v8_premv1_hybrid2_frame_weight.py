"""Frame-weight ladder: thinner D1 perimeters on the checkpoint-7 design.

The locked D1 frame is a 5px gold mid-band + 4px bevel rim + two inner
hairlines. Each option scales every stroke width AND its inset by one
factor so the frame stays a coherent assembly, just lighter. Bookend
panels show the current in-game popup and the store category screen for
context. All panels are full 360x640 gameplay frames at 2x.

Output: colorways/frame_weight_options_v1.png
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
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m, bevel_rim
from game.config import W, H
from PIL import Image, ImageDraw, ImageFont

BG_DEEP_A, BG_GLINT_A = 155, 138


def make_frame(s):
    """D1 double-bevel with every stroke width and inset scaled by s."""
    def frame(big, rect, rad):
        band = rect.inflate(-m(3 * s), -m(3 * s))
        pygame.draw.rect(big, (*fr.SIL_MID, 150), band, width=max(2, m(5 * s)),
                         border_radius=rad - m(1))
        bevel_rim(big, rect, rad, fr.SIL_DEEP, (*fr.SIL_BRIGHT, 245),
                  w=max(1, m(4 * s)))
        inner = rect.inflate(-m(11 * s), -m(11 * s))
        pygame.draw.rect(big, (*fr.SIL_BRIGHT, 170), inner,
                         width=max(1, m(1.2 * s)), border_radius=rad - m(5 * s))
        pygame.draw.rect(big, (*fr.SIL_DEEP, 210),
                         rect.inflate(-m(8 * s), -m(8 * s)),
                         width=max(1, m(1 * s)), border_radius=rad - m(4 * s))
    return frame


# (role, detail, scale) — None scale = reference panels
OPTIONS = [
    ("T1 · lightest", "all strokes x0.5", 0.5),
    ("T2", "all strokes x0.65", 0.65),
    ("T3", "all strokes x0.8", 0.8),
    ("T4 · LOCKED (current)", "full weight x1.0", 1.0),
]


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

        panels = [("ORIGINAL confirm (in game)", "current live design",
                   store_frame(scene, SID))]

        h2.CHIP_CY = CHIP_CY
        h2._chip_cy = lambda _tier: _chip_cy_zone_named(scene._disp_name(SID))
        _, silver_pal = DESIGNS[0]
        can_stops, _t, _, _ = silver_pal["can"]
        pal = oc.GOLD
        bar, buy = oc.PANEL_GOLD
        _bs, buy_text, _rd, _rb = buy
        fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                  pal["bright"])
        fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
        h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
        store_mod._bg_hook = hook_constellation(pal["glint"],
                                                BG_DEEP_A, BG_GLINT_A)
        h2.overlay_bullion_chip = cw.make_chip_fn(bar)
        h2.overlay_buttons = make_buttons_accent(
            can_stops, buy_text, pal["deep"], pal["bright"],
            make_inner_keyline(pal["glint"], pal["bright"], (26, 17, 4)))
        for role, detail, s in OPTIONS:
            store_mod._frame_hook = make_frame(s)
            panels.append((role, detail, render_locked_frame(scene, tier)))

        panels.append(("STORE CATEGORY", "item cards as in game",
                       store_frame(scene, None)))

        f_head = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        f_role = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        f_detail = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        MARGIN, HEAD, GAP = 24, 64, 20
        cell_w, cell_h = W * 2, H * 2
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + 96
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "frame weight options · checkpoint 7 · gold · "
                 f"{scene._disp_name(SID)} ({tier}) · 2x",
                 fill=(236, 214, 160), font=f_head)
        for i, (role, detail, surf) in enumerate(panels):
            pil = Image.frombytes("RGB", (W, H),
                                  pygame.image.tostring(surf, "RGB"))
            x = MARGIN + i * (cell_w + GAP)
            strip.paste(pil.resize((cell_w, cell_h), Image.LANCZOS), (x, HEAD))
            idr.text((x + cell_w // 2, HEAD + cell_h + 14), role,
                     fill=(236, 214, 160), anchor="mt", font=f_role)
            idr.text((x + cell_w // 2, HEAD + cell_h + 50), detail,
                     fill=(180, 180, 205), anchor="mt", font=f_detail)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "frame_weight_options_v1.png")
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
