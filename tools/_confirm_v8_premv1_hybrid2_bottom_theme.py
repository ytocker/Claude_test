"""Common-theme bottom redesign on the P2-gold perimeter.

P2 (slim-double) won the perimeter ladder but goes fully golden here
(saturated gold palette on frame, buttons, cards). The bottom zones — the
popup's dark shelf tray and the card's footer rows — get a shared theme
per option: B1 stands the content on a warm gilded plinth, B2 keeps the
dark stage but frames it with a double gold lip (the P2 hairline-pair
language), B3 removes the box entirely and keeps one gold divider.
Columns: IN-GAME · P2-GOLD reference · B1 · B2 · B3, each popup / card /
category.

Output: colorways/bottom_theme_v1.png
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
                                                        make_buttons_frame,
                                                        RICH_PAL)
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

P2GOLD = {"pal": RICH_PAL, "key_w": 1.2, "band_w": 2.5, "band_a": 110,
          "bevel_w": 2.6,
          "hairs": ((3.8, 1.0, "deep", 170), (4.8, 1.0, "bright", 120))}

GOLD_BRIGHT = RICH_PAL["bright"]
GOLD_DEEP = RICH_PAL["deep"]

SHELF = (17, 335, 226, 91)
SHELF_RAD = 23
CARD_FOOT_Y = 56  # footer rows start (logical, card space)


def _shelf_base(big, stops, rounded=True):
    r = pygame.Rect(m(SHELF[0]), m(SHELF[1]), m(SHELF[2]), m(SHELF[3]))
    shelf = sc.vgrad_stops(r.w, r.h, 0, stops, 255).copy()
    if rounded:
        smask = pygame.Surface(r.size, pygame.SRCALPHA)
        pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                         border_bottom_left_radius=m(SHELF_RAD),
                         border_bottom_right_radius=m(SHELF_RAD))
        shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=30)
    return r, shelf


# ── B1 · gilded plinth ────────────────────────────────────────────────────────
def shelf_gilded(big, affordable):
    r, shelf = _shelf_base(big, [(0.0, (66, 50, 22)), (0.5, (44, 33, 13)),
                                 (1.0, (26, 19, 8))])
    pygame.draw.line(shelf, (*GOLD_BRIGHT, 230), (0, 0), (r.w - 1, 0),
                     max(1, m(1.2)))
    pygame.draw.line(shelf, (*GOLD_DEEP, 200), (0, m(1.4)), (r.w - 1, m(1.4)),
                     max(1, m(0.8)))
    big.blit(shelf, r.topleft)


def footer_gilded(surf, rect, pal):
    y0 = rect.y + m(CARD_FOOT_Y)
    band = pygame.Surface((rect.w, rect.bottom - y0), pygame.SRCALPHA)
    grad = sc.vgrad_stops(rect.w, rect.bottom - y0, 0,
                          [(0.0, (66, 50, 22)), (1.0, (26, 19, 8))], 150)
    band.blit(grad, (0, 0))
    smask = pygame.Surface(band.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=m(sc.CARD_RAD) - m(2),
                     border_bottom_right_radius=m(sc.CARD_RAD) - m(2))
    band.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(band, (rect.x, y0))
    pygame.draw.line(surf, (*GOLD_BRIGHT, 210), (rect.x + m(4), y0),
                     (rect.right - m(4), y0), max(1, m(0.9)))


# ── B2 · double-lip stage ─────────────────────────────────────────────────────
def shelf_double_lip(big, affordable):
    r, shelf = _shelf_base(big, [(0.0, (40, 36, 28)), (0.5, (26, 23, 17)),
                                 (1.0, (14, 12, 9))])
    pygame.draw.line(shelf, (*GOLD_BRIGHT, 220), (0, 0), (r.w - 1, 0),
                     max(1, m(1)))
    pygame.draw.line(shelf, (*GOLD_DEEP, 190), (0, m(2.6)), (r.w - 1, m(2.6)),
                     max(1, m(1)))
    seat = pygame.Surface((r.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(110 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (r.w - 1, yy))
    big.blit(seat, (r.x, r.y - m(6)))
    big.blit(shelf, r.topleft)


def footer_double_lip(surf, rect, pal):
    y0 = rect.y + m(CARD_FOOT_Y)
    pygame.draw.line(surf, (*GOLD_BRIGHT, 190), (rect.x + m(5), y0),
                     (rect.right - m(5), y0), max(1, m(0.8)))
    pygame.draw.line(surf, (*GOLD_DEEP, 160), (rect.x + m(5), y0 + m(1.6)),
                     (rect.right - m(5), y0 + m(1.6)), max(1, m(0.8)))


# ── B3 · open floor ───────────────────────────────────────────────────────────
def shelf_open(big, affordable):
    pygame.draw.line(big, (*GOLD_BRIGHT, 180), (m(14), m(SHELF[1])),
                     (m(246), m(SHELF[1])), max(1, m(1)))


def footer_open(surf, rect, pal):
    y0 = rect.y + m(CARD_FOOT_Y)
    pygame.draw.line(surf, (*GOLD_BRIGHT, 170), (rect.x + m(5), y0),
                     (rect.right - m(5), y0), max(1, m(0.9)))


def themed_card_draw():
    src = textwrap.dedent(inspect.getsource(sc.draw_card))
    src, n1 = re.subn(
        r"pygame\.draw\.rect\(surf, \(4, 5, 16\), rect.*?border_radius=trad\)",
        "_card_frame(surf, rect, rad)", src, flags=re.DOTALL)
    assert n1 == 1, f"card frame patch failed: {n1}"
    src, n2 = re.subn(r"(\n\s*# rarity RIBBON)",
                      r"\n    _card_bottom_hook(surf, rect, pal)\1", src)
    assert n2 == 1, f"card bottom patch failed: {n2}"
    ns = {}
    exec(compile(src, "<bottom_theme_card>", "exec"), sc.__dict__, ns)
    return ns["draw_card"]


OPTIONS = [
    ("B1 · gilded-plinth",
     "shelf re-graded to a warm bronze plinth with a bright gold lip",
     "matching warm footer band + gold top hairline",
     shelf_gilded, footer_gilded),
    ("B2 · double-lip-stage",
     "warm charcoal stage framed by a double gold lip (the P2 pair)",
     "same double gold hairline above the footer rows",
     shelf_double_lip, footer_double_lip),
    ("B3 · open-floor",
     "shelf box removed — continuous body + one gold divider",
     "same single gold divider above the footer rows",
     shelf_open, footer_open),
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
    pal = oc.GOLD
    bar, buy = oc.PANEL_GOLD
    _bs, buy_text, _rd, _rb = buy
    fr.SIL_DEEP, fr.SIL_MID, fr.SIL_BRIGHT = pal["deep"], pal["mid"], pal["bright"]
    fr.GEM_SIL, fr.GEM_SIL_DEEP = pal["gem"], pal["gem_deep"]
    store_mod._bg_hook = hook_constellation(pal["glint"], BG_DEEP_A, BG_GLINT_A)
    store_mod._frame_hook = make_frame(P2GOLD, 1.0)
    h2.overlay_bullion_chip = cw.make_chip_fn(bar)
    h2.overlay_buttons = make_buttons_frame(
        can_stops, buy_text, make_frame(P2GOLD, CARD_S), RICH_PAL)

    _orig_owned = store_data.is_owned
    _orig_equipped = store_data.equipped
    _orig_card_draw = sc.draw_card
    EQUIP_SID = "skin_cowboy"
    patched_card = themed_card_draw()
    sc._card_frame = make_frame(P2GOLD, CARD_S)

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
        panels = [("IN-GAME",
                   "the design currently live in the game",
                   "no change — card as in game",
                   render_stock(), render_card(sc.draw_card),
                   render_category())]

        sc._card_bottom_hook = lambda surf, rect, pal_: None
        h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
        panels.append(("P2·GOLD (reference)",
                       "P2 slim-double perimeter in saturated gold; "
                       "bottom shelf unchanged",
                       "P2-gold frame; footer rows unchanged",
                       render_pop(), render_card(patched_card),
                       render_category(patched_card)))

        for role, pop_note, card_note, shelf_fn, foot_fn in OPTIONS:
            store_mod._shelf_hook = shelf_fn
            sc._card_bottom_hook = foot_fn
            h2._DRAW_FN[0] = oc._patched_draw(pal["ring"], shelf_hook=True)
            panels.append((role,
                           f"P2-gold + {pop_note}",
                           f"P2-gold + {card_note}",
                           render_pop(), render_card(patched_card),
                           render_category(patched_card)))
        h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])

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
        FOOT = 250
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + FOOT + 40
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "bottom-zone themes on P2-gold · popup shelf ⇄ card footer · "
                 "each column: popup / card / store category · 2x",
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
                           "bottom_theme_v1.png")
        strip.save(out)
        print("saved", out, strip.size)
    finally:
        store_data.balance = _orig_bal
        store_catalog.cost = _orig_cost
        h2.CHIP_CY = _orig_chip_cy
        sc.draw_card = _orig_card_draw
        for attr in ("_bg_hook", "_frame_hook", "_shelf_hook"):
            if hasattr(store_mod, attr):
                delattr(store_mod, attr)


if __name__ == "__main__":
    main()
