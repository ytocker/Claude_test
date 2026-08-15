"""Gold shade ladder on the locked P2 slim-double frame.

Same golden palette family throughout — the options differ only in shade,
value, and chroma of the gold. No structural changes: same P2 frame, stock
shelf, stock card footer. Each column swaps the perimeter gold
holistically: popup frame, button rims, card frame, category cards, hero
ring, corner/bottom gems, and background glints all follow.
Columns: IN-GAME · G1 antique (reference) · G2 rich · G3 luminous ·
G4 deep-old · G5 honey · G6 soft.

Output: colorways/perimeter_gold_shades_v1.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import inspect
import re
import textwrap

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
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene
from game.store_cards import m
from game.config import W, H
from PIL import Image, ImageDraw, ImageFont

POP_W, POP_H = 260, 442
BG_DEEP_A, BG_GLINT_A = 155, 138
CARD_S = 154 / 240

P2 = {"key_w": 1.2, "band_w": 2.5, "band_a": 110, "bevel_w": 2.6,
      "hairs": ((3.8, 1.0, "deep", 170), (4.8, 1.0, "bright", 120))}

COLORWAYS = [
    ("G1 · antique-gold", "current muted gold — as shipped (reference)",
     oc.GOLD),
    ("G2 · rich-gold", "saturated amber gold — highest chroma",
     dict(deep=(122, 74, 0), mid=(244, 164, 14), bright=(255, 190, 30),
          gem=(252, 176, 20), gem_deep=(140, 86, 2),
          glint=(252, 180, 30), ring=(255, 188, 40))),
    ("G3 · luminous-gold", "lighter, sunnier — bright leans yellow-white",
     dict(deep=(112, 86, 26), mid=(240, 194, 78), bright=(255, 232, 140),
          gem=(250, 210, 92), gem_deep=(132, 100, 30),
          glint=(250, 214, 104), ring=(255, 224, 120))),
    ("G4 · deep-old-gold", "darker, moodier — heavier antique read",
     dict(deep=(66, 44, 6), mid=(176, 126, 30), bright=(228, 174, 54),
          gem=(206, 148, 38), gem_deep=(88, 58, 8),
          glint=(210, 156, 46), ring=(222, 168, 56))),
    ("G5 · honey-gold", "warmer amber lean — still unmistakably gold",
     dict(deep=(112, 62, 6), mid=(230, 148, 30), bright=(255, 186, 62),
          gem=(244, 166, 44), gem_deep=(126, 72, 10),
          glint=(244, 170, 52), ring=(250, 178, 62))),
    ("G6 · soft-gold", "gently desaturated pale gold — calm luxury",
     dict(deep=(100, 82, 42), mid=(212, 184, 112), bright=(250, 226, 156),
          gem=(232, 202, 126), gem_deep=(116, 94, 48),
          glint=(230, 204, 134), ring=(238, 212, 144))),
]


def framed_card_draw():
    src = textwrap.dedent(inspect.getsource(sc.draw_card))
    src, n1 = re.subn(
        r"pygame\.draw\.rect\(surf, \(4, 5, 16\), rect.*?border_radius=trad\)",
        "_card_frame(surf, rect, rad)", src, flags=re.DOTALL)
    assert n1 == 1, f"card frame patch failed: {n1}"
    ns = {}
    exec(compile(src, "<perimeter_colors_card>", "exec"), sc.__dict__, ns)
    return ns["draw_card"]


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

    try:
        panels = [("IN-GAME", "the design currently live in the game",
                   render_stock(), render_card(sc.draw_card),
                   render_category())]

        for role, note, pal in COLORWAYS:
            params = dict(P2, pal=pal)
            fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                      pal["bright"])
            fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
            store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A,
                                                    BG_GLINT_A)
            store_mod._frame_hook = make_frame(params, 1.0)
            h2.overlay_buttons = make_buttons_frame(
                can_stops, buy_text, make_frame(params, CARD_S), pal)
            sc._card_frame = make_frame(params, CARD_S)
            h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
            panels.append((role, note, render_pop(),
                           render_card(patched_card),
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
                 "gold shade ladder on the P2 slim-double frame · same golden "
                 "palette, shade/chroma variations only · popup / card / "
                 "category · 2x", fill=(236, 214, 160), font=f_head)
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
                           "colorways", "perimeter_gold_shades_v1.png")
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
