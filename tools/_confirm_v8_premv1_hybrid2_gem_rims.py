"""Locked design + rim-shine bezels around the gems.

The locked perimeter (G8 rim-shine x1.4) leaves the gems with their stock
dim seat ring. This design gives every facet gem — the popup's flanking
pair, the bottom gems, and the card corner gems — a miniature of the same
bezel the perimeter wears: dark contact keyline, the rim gold, pale inner
glint, and a top-light arc. Columns: IN-GAME · LOCKED · LOCKED + gem rims.

Output: colorways/gem_rims_v1.png
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import math

import pygame
import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_frames as fr
import _confirm_v8_premv1_hybrid2_outline_compare as oc
from _confirm_v8_premv1_hybrid2_card_kinship import (SID, TIER, render_pop,
                                                     render_card)
from _confirm_v8_premv1_hybrid2_current_vs_locked import render_stock
from _confirm_v8_premv1_hybrid2_perimeter_blend import make_buttons_frame
from _confirm_v8_premv1_hybrid2_perimeter_colors import (
    POP_W, POP_H, BG_DEEP_A, BG_GLINT_A, CARD_S, COLORWAYS,
    LOCKED_THICKNESS, make_locked_frame, framed_card_draw)
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

G8_PAL = COLORWAYS[-1][2]

_orig_facet = sc.facet_gem


def facet_gem_rimmed(surf, cx, cy, r, base, deep, mystery=False):
    """Stock facet gem plus a miniature rim-shine bezel: the same contact
    keyline / rim gold / pale glint stack the locked perimeter wears, with
    a top-left light arc standing in for the polished grade."""
    _orig_facet(surf, cx, cy, r, base, deep, mystery)
    pygame.draw.circle(surf, (5, 5, 12), (int(cx), int(cy)), int(r + m(4.6)),
                       max(1, m(0.8)))
    pygame.draw.circle(surf, (232, 196, 108), (int(cx), int(cy)),
                       int(r + m(3.8)), max(1, m(1.4)))
    pygame.draw.circle(surf, (246, 220, 140), (int(cx), int(cy)),
                       int(r + m(2.9)), max(1, m(0.7)))
    rr = int(r + m(3.8))
    lay = pygame.Surface((rr * 2 + 2, rr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.arc(lay, (252, 234, 166, 180),
                    (1, 1, rr * 2, rr * 2),
                    math.radians(40), math.radians(220), max(1, m(1.2)))
    surf.blit(lay, (int(cx) - rr - 1, int(cy) - rr - 1))


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

    def set_locked_column():
        pal = G8_PAL
        fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = (pal["deep"], pal["mid"],
                                                  pal["bright"])
        fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
        store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A,
                                                BG_GLINT_A)
        store_mod._frame_hook = make_locked_frame(1.0)
        h2.overlay_buttons = make_buttons_frame(
            can_stops, buy_text, make_locked_frame(CARD_S), pal)
        sc._card_frame = make_locked_frame(CARD_S)
        h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])

    try:
        panels = [("IN-GAME", "the design currently live in the game",
                   render_stock(), render_card(sc.draw_card),
                   render_category())]

        set_locked_column()
        panels.append((f"LOCKED · rim-shine ×{LOCKED_THICKNESS}",
                       "gems keep their stock dim seat ring",
                       render_pop(), render_card(patched_card),
                       render_category(patched_card)))

        sc.facet_gem = facet_gem_rimmed
        set_locked_column()
        panels.append(("LOCKED + GEM RIMS",
                       "every gem gets a miniature of the perimeter's "
                       "bezel: keyline / rim gold / glint / top light",
                       render_pop(), render_card(patched_card),
                       render_category(patched_card)))
        sc.facet_gem = _orig_facet

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
                 "gem bezels in the locked rim-shine gold · "
                 "popup / card / category · 2x",
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
                           "colorways", "gem_rims_v1.png")
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        sc.facet_gem = _orig_facet
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        sc.draw_card = _orig_card_draw
        for attr in ("_bg_hook", "_frame_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
