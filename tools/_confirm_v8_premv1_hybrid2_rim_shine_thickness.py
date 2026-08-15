"""Perimeter thickness ladder for the G8 rim-shine design.

G8 (the perimeter wearing the hero rim's layered gold gradient) with the
stroke stack swept between x1.0 and x1.5 in 0.1 steps — the fine ladder
inside the earlier coarse one. Colors and the polished grade are identical
across the ladder — only the stroke widths and insets scale. Anchors: the
in-game design and the current P2 antique-gold frame. Columns: IN-GAME ·
CURRENT (G1) · x1.0 .. x1.5, each popup / card / category.

Output: colorways/rim_shine_thickness_v2.png
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
from _confirm_v8_premv1_hybrid2_card_kinship import (SID, TIER, render_pop,
                                                     render_card)
from _confirm_v8_premv1_hybrid2_current_vs_locked import render_stock
from _confirm_v8_premv1_hybrid2_perimeter_blend import (make_frame,
                                                        make_buttons_frame)
from _confirm_v8_premv1_hybrid2_perimeter_colors import (
    P2, POP_W, POP_H, BG_DEEP_A, BG_GLINT_A, CARD_S, COLORWAYS,
    make_rim_shine_frame, framed_card_draw)
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.config import W, H
from PIL import Image, ImageDraw, ImageFont

G8_PAL = COLORWAYS[-1][2]
assert COLORWAYS[-1][0].startswith("G8")

# rungs picked where the stroke stack actually crosses a pixel boundary —
# in-between values render identically to a neighbor and would mislead
THICKNESS = [
    ("×1.0", "G8 exactly as added (lower anchor)", 1.0),
    ("×1.15", "one pixel step up on the popup frame", 1.15),
    ("×1.25", "popup and card both one step up", 1.25),
    ("×1.3", "next pixel step", 1.3),
    ("×1.4", "next pixel step", 1.4),
    ("×1.5", "the T3 bold weight (upper anchor)", 1.5),
]


def main():
    _orig_bal = store_data.balance
    _orig_cost = store_catalog.cost
    _orig_chip_cy = h2.CHIP_CY
    store_data.balance = lambda: 99999
    store_catalog.cost = lambda sid: 1100
    h2.SIDS[TIER] = SID
    h2.NAMES[TIER] = "MUMMY"
    h2.PRICES[TIER] = 1100
    h2.overlay_quatrefoil = lambda ov: None
    h2.CHIP_CY = CHIP_CY
    h2._chip_cy = _chip_cy_zone
    _, silver_pal = DESIGNS[0]
    can_stops, _t, _, _ = silver_pal["can"]
    bar, buy = oc.PANEL_GOLD
    _bs, buy_text, _rd, _rb = buy
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)

    _orig_owned = store_data.is_owned
    _orig_equipped = store_data.equipped
    _orig_card_draw = sc.draw_card
    EQUIP_SID = "skin_cowboy"
    patched_card = framed_card_draw()

    def render_category(card_draw=None):
        store_data.is_owned = lambda s: s == EQUIP_SID or _orig_owned(s)
        store_data.equipped = lambda slot: EQUIP_SID
        if card_draw is not None:
            sc.draw_card = card_draw
        sc.clear_cache()
        scene = StoreScene()
        scene.view = "category"
        scene.tab = 0
        scene.page = 0
        surf_c = pygame.Surface((W, H))
        scene.render(surf_c)
        sc.draw_card = _orig_card_draw
        store_data.is_owned = _orig_owned
        store_data.equipped = _orig_equipped
        sc.clear_cache()
        return surf_c

    def set_column(pal, frame_at):
        fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                  pal["bright"])
        fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
        store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A,
                                                BG_GLINT_A)
        store_mod._frame_hook = frame_at(1.0)
        h2.overlay_buttons = make_buttons_frame(
            can_stops, buy_text, frame_at(CARD_S), pal)
        sc._card_frame = frame_at(CARD_S)
        h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])

    try:
        panels = [("IN-GAME", "the design currently live in the game",
                   render_stock(), render_card(sc.draw_card),
                   render_category())]

        g1 = oc.GOLD
        set_column(g1, lambda scale: make_frame(dict(P2, pal=g1), scale))
        panels.append(("CURRENT (G1)",
                       "P2 antique-gold frame — current working design",
                       render_pop(), render_card(patched_card),
                       render_category(patched_card)))

        for role, note, t in THICKNESS:
            set_column(G8_PAL,
                       lambda scale, t=t: make_rim_shine_frame(scale, t))
            panels.append((role, f"G8 rim-shine · {note}",
                           render_pop(), render_card(patched_card),
                           render_category(patched_card)))

        f_head = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        f_role = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        f_detail = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        import textwrap as _tw
        MARGIN, HEAD, GAP = 24, 64, 20
        pop_w, pop_h = POP_W * 2, POP_H * 2
        card_w, card_h = sc.CARD_W * 2, sc.CARD_H * 2
        cell_w = max(pop_w, card_w) + 40
        cat_w, cat_h = cell_w, cell_w * H // W
        cell_h = pop_h + 12 + card_h + 12 + cat_h
        FOOT = 150
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + FOOT + 40
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "perimeter thickness ladder for G8 rim-shine · stroke stack "
                 "scaled, colors identical · popup / card / category · 2x",
                 fill=(236, 214, 160), font=f_head)
        for i, (role, note, pop, card, cat) in enumerate(panels):
            x = MARGIN + i * (cell_w + GAP)
            pp = Image.frombytes("RGB", (POP_W, POP_H),
                                 pygame.image.tostring(pop, "RGB"))
            strip.paste(pp.resize((pop_w, pop_h), Image.LANCZOS),
                        (x + (cell_w - pop_w) // 2, HEAD))
            cc = Image.frombytes("RGBA", (sc.CARD_W, sc.CARD_H),
                                 pygame.image.tostring(card, "RGBA"))
            cbg = Image.new("RGBA", (card_w, card_h), (10, 9, 20, 255))
            cbg.alpha_composite(cc.resize((card_w, card_h), Image.LANCZOS))
            strip.paste(cbg.convert("RGB"),
                        (x + (cell_w - card_w) // 2, HEAD + pop_h + 12))
            cat_img = Image.frombytes("RGB", (W, H),
                                      pygame.image.tostring(cat, "RGB"))
            strip.paste(cat_img.resize((cat_w, cat_h), Image.LANCZOS),
                        (x, HEAD + pop_h + 12 + card_h + 12))
            ty = HEAD + cell_h + 14
            idr.text((x + cell_w // 2, ty), role,
                     fill=(236, 214, 160), anchor="mt", font=f_role)
            ty += 40
            col = (150, 150, 170) if i == 0 else (222, 208, 170)
            for line in _tw.wrap(note, 44):
                idr.text((x + cell_w // 2, ty), line,
                         fill=col, anchor="mt", font=f_detail)
                ty += 27
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1",
                           "colorways", "rim_shine_thickness_v2.png")
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        sc.draw_card = _orig_card_draw
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
