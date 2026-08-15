"""Perimeter blend ladder — between the in-game frame and the new design.

Holistic verdict: the stock perimeter is too dull, the D1 double-bevel too
bold. Three in-between perimeter SYSTEMS, each applied everywhere at once
(popup frame, button rims, item card, category-grid cards) so a column
reads as one language: P1 refines the stock single bevel with a crisp
hairline (weight axis), P2 is the D1 construction at ~55% weight
(structure axis), P3 keeps moderate weight but shifts to the saturated
gold palette (colour axis — the "more gold" direction). Anchored by
IN-GAME and BOLD columns. Column stack: popup / card / category.

Output: colorways/perimeter_blend_v1.png
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
from _confirm_v8_premv1_hybrid2_card_kinship import (SID, TIER, render_pop,
                                                     render_card,
                                                     d1_card_draw,
                                                     card_frame_d1)
from _confirm_v8_premv1_hybrid2_current_vs_locked import render_stock
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

STOCK_PAL = {"deep": sc.CARD_RING_DEEP, "bright": sc.CARD_RING_BRIGHT,
             "mid": sc.lerp_color(sc.CARD_RING_DEEP, sc.CARD_RING_BRIGHT, 0.55)}
RICH_PAL = {"deep": oc.GOLD["deep"], "mid": oc.GOLD["mid"],
            "bright": oc.GOLD["bright"]}


def make_frame(p, s=1.0):
    """Parametric perimeter: keyline + optional satin band + bevel +
    inner hairlines, every stroke and inset scaled by s."""
    pal = p["pal"]

    def frame(surf, rect, rad):
        pygame.draw.rect(surf, (4, 5, 16), rect,
                         width=max(1, m(p["key_w"] * s)), border_radius=rad)
        if p.get("band_w"):
            band = rect.inflate(-m(2 * s), -m(2 * s))
            pygame.draw.rect(surf, (*pal["mid"], p["band_a"]), band,
                             width=max(2, m(p["band_w"] * s)),
                             border_radius=max(2, rad - m(1 * s)))
        sc.bevel_rim(surf, rect, rad, pal["deep"], (*pal["bright"], 235),
                     w=max(1, m(p["bevel_w"] * s)))
        for inset, w, key, a in p.get("hairs", ()):
            pygame.draw.rect(surf, (*pal[key], a),
                             rect.inflate(-m(2 * inset * s), -m(2 * inset * s)),
                             width=max(1, m(w * s)),
                             border_radius=max(1, rad - m(inset * s)))
    return frame


OPTIONS = [
    ("P1 · refined-bevel", "weight",
     {"pal": STOCK_PAL, "key_w": 1.6, "bevel_w": 3.2,
      "hairs": ((3.5, 1.2, "bright", 140),)}),
    ("P2 · slim-double", "structure",
     {"pal": STOCK_PAL, "key_w": 1.2, "band_w": 2.5, "band_a": 110,
      "bevel_w": 2.6,
      "hairs": ((3.8, 1.0, "deep", 170), (4.8, 1.0, "bright", 120))}),
    ("P3 · rich-gold", "colour",
     {"pal": RICH_PAL, "key_w": 1.4, "band_w": 3.0, "band_a": 90,
      "bevel_w": 3.0, "hairs": ((4.0, 1.1, "bright", 140),)}),
]


def make_buttons_frame(can_stops, buy_text, frame_fn, pal):
    """Locked button build with the rim swapped for the option's perimeter;
    BUY keeps an inner hairline mat in the option's palette (the I5 role)."""
    from game.store_cards import (vgrad_stops, top_sheen, drop_shadow,
                                  plain_text, font)

    def buttons(ov):
        rad = m(12)
        for cx, lbl in ((76, "BUY"), (184, "CANCEL")):
            r = pygame.Rect(0, 0, m(99), m(42))
            r.center = (m(cx), m(360))
            drop_shadow(ov, r, rad, blur=m(3), alpha=100, dy=m(2))
            ov.blit(vgrad_stops(r.w, r.h, rad, can_stops, 255), r.topleft)
            top_sheen(ov, r, rad, m(12), peak=14)
            frame_fn(ov, r, rad)
            if lbl == "BUY":
                kr = r.inflate(-m(13), -m(13))
                pygame.draw.rect(ov, (*pal["bright"], 90), kr,
                                 width=max(1, m(0.9)), border_radius=m(7))
            plain_text(ov, lbl, font(15), r.center, buy_text,
                       shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    return buttons


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
    pal = oc.GOLD
    bar, buy = oc.PANEL_GOLD
    _bs, buy_text, _rd, _rb = buy
    fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = pal["deep"], pal["mid"], pal["bright"]
    fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
    store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A, BG_GLINT_A)
    store_mod._frame_hook = fr.frame_double_bevel
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)
    locked_buttons = make_buttons_accent(
        can_stops, buy_text, pal["deep"], pal["bright"],
        make_inner_keyline(pal["glint"], pal["bright"], (26, 17, 4)))
    h2.overlay_buttons = locked_buttons
    h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])

    _orig_owned = store_data.is_owned
    _orig_equipped = store_data.equipped
    _orig_card_draw = sc.draw_card
    EQUIP_SID = "skin_cowboy"
    patched_card = d1_card_draw()

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
        stock_card = render_card(sc.draw_card)
        panels = [("IN-GAME (too dull)",
                   "the design currently live in the game",
                   "no change — card as in game",
                   render_stock(), stock_card, render_category())]

        for role, axis, p in OPTIONS:
            store_mod._frame_hook = make_frame(p, 1.0)
            h2.overlay_buttons = make_buttons_frame(
                can_stops, buy_text, make_frame(p, CARD_S), p["pal"])
            sc._card_frame = make_frame(p, CARD_S)
            panels.append((role,
                           f"{axis} axis — frame + button rims in this "
                           "perimeter system",
                           "same perimeter scaled to the card (also in "
                           "the category below)",
                           render_pop(),
                           render_card(patched_card),
                           render_category(patched_card)))
        store_mod._frame_hook = fr.frame_double_bevel
        h2.overlay_buttons = locked_buttons

        sc._card_frame = card_frame_d1
        panels.append(("BOLD (current new design)",
                       "checkpoint 7: D1 double-bevel + 4px button rims",
                       "D1 perimeter scaled to the card (also in category)",
                       render_pop(),
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
        FOOT = 220
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + FOOT + 40
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "perimeter blend ladder · in-game ↔ new design · each column: "
                 "popup / card / store category · MUMMY (epic) · 2x",
                 fill=(236, 214, 160), font=f_head)
        for i, (role, pop_change, card_change, pop, card, cat) in enumerate(panels):
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
            for prefix, change in (("POPUP: ", pop_change),
                                   ("CARD: ", card_change)):
                col = ((150, 150, 170) if change.startswith("no change")
                       else (222, 208, 170))
                for line in _tw.wrap(prefix + change, 44):
                    idr.text((x + cell_w // 2, ty), line,
                             fill=col, anchor="mt", font=f_detail)
                    ty += 27
                ty += 6
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "perimeter_blend_v1.png")
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
