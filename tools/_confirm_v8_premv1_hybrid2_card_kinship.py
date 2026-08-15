"""Figure K — popup ⇄ item-card design-language kinship concepts.

The popup is the item card's zoomed-in extension, so the two should share
vocabulary. Five isolated concepts, each changing ONE element on the popup
or the card while everything else stays at checkpoint 7: K1 rebuilds the
popup frame from the card's exact frame recipe scaled up; K2 adopts the
card's single top-right crest-gem grammar; K3 swaps the bullion bar for the
card's sumi hang-tag price language; K4 draws the rarity banner with the
card's lozenge ribbon construction; K5 echoes the popup's constellation web
onto the card body. Each panel pairs the popup with the same item's card.

Output: colorways/card_kinship_k_v1.png
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import inspect
import re
import textwrap

import _confirm_v8_premv1_hybrid2 as h2
import _confirm_v8_premv1_hybrid2_colorway as cw
import _confirm_v8_premv1_hybrid2_frames as fr
import _confirm_v8_premv1_hybrid2_outline_compare as oc
from _confirm_v8_premv1_hybrid2_buy_accents import make_buttons_accent
from _confirm_v8_premv1_hybrid2_buy_accents4 import make_inner_keyline
from _confirm_v8_premv1_hybrid2_current_vs_locked import render_stock
from _confirm_v8_premv1_hybrid2_scribbles import DESIGNS
from _confirm_v8_premv1_hybrid2_scribbles2 import hook_constellation
from _confirm_v8_premv1_hybrid2_name_layout import CHIP_CY, _chip_cy_zone
import game.store as store_mod
import game.store_cards as sc
import game.store_data as store_data
import game.store_catalog as store_catalog
from game.store import StoreScene, _confirm_tier_banner
from game.store_cards import m
from game.config import W, H
from PIL import Image, ImageDraw, ImageFont

POP_W, POP_H = 260, 442
BG_DEEP_A, BG_GLINT_A = 155, 138
SID, TIER = "skin_mummy", "EPIC"


# ── K1 · popup frame from the card's recipe, scaled ───────────────────────────
def frame_card_kinship(big, rect, rad):
    k = 1.6
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2 * k)),
                     border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 235), w=max(1, m(2.45 * k)))
    tray = rect.inflate(-m(7 * k), -m(7 * k))
    trad = rad - m(4 * k)
    pygame.draw.rect(big, (10, 10, 24, 200), tray.inflate(m(2 * k), m(2 * k)),
                     width=max(1, m(1 * k)), border_radius=trad + m(1 * k))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 90), tray,
                     width=max(1, m(1 * k)), border_radius=trad)


# ── K2 · single crest gem at the card's corner grammar ────────────────────────
def crest_gem_overlay(ov, pal_tier):
    # card: gem centre inset 19/162 of width from the corner; popup card body
    # spans x 10..250, y 127..426 → same fraction gives inset ~28
    sc.facet_gem(ov, m(10 + 240 - 28), m(127 + 28), m(16),
                 pal_tier["gem"], pal_tier["deep"])


# ── K3 · price as the card's sumi hang-tag, scaled ────────────────────────────
def tag_chip(ov, price, cy):
    k = 1.5
    tw, th = int(81 * k), int(94 * k)
    rad = m(3 * k)
    face = pygame.Surface((tw, th), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, tw, th)
    body = sc.vgrad_stops(tw, th, rad,
                          [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                          255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, rad, (80, 52, 12, 200),
                 (255, 240, 190, 200), w=max(1, m(1.2 * k)))
    sc.coin_glyph(face, tw // 2, int(th * 0.30), m(8 * k))
    sc.plain_text(face, f"{price:,}", sc.font(int(15 * k)),
                  (tw // 2, int(th * 0.66)), (52, 38, 14),
                  shadow_a=0, weight=m(0.9 * k))
    grommet = (int(30 * k), int(13 * k))
    pygame.draw.circle(face, (0, 0, 0, 0), grommet, m(5 * k))
    pygame.draw.circle(face, (110, 80, 30), grommet, m(5 * k) + 1,
                       width=max(1, m(1 * k)))
    rot = pygame.transform.rotate(face, -7)
    center = (m(130), m(cy + 8))
    knot = (m(130 - 14), m(cy - 34))
    gx = center[0] - tw // 2 + grommet[0]
    gy = center[1] - th // 2 + grommet[1]
    cord = (190, 165, 115)
    lw = m(1.5)
    pygame.draw.line(ov, cord, (gx, gy), (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(ov, cord, (gx, gy), (knot[0] + 2, knot[1] + 2), lw)
    ov.blit(rot, rot.get_rect(center=center))
    pygame.draw.circle(ov, cord, knot, m(1.5))


# ── K4 · rarity banner via the card's lozenge ribbon, scaled ──────────────────
def ribbon_banner(ov, tier_word, cx, cy, max_w, pal):
    k = 1.9
    f = sc.font(int(8.5 * k))
    tw = sc._glyph_base(tier_word, f, m(1.4 * k)).get_width()
    pad = m(14 * k)
    w = min(m(max_w), tw + pad * 2)
    h = m(12 * k)
    pt = h // 2
    x0, y0 = m(cx) - w // 2, m(cy) - h // 2
    poly = [(0, h // 2), (pt, 0), (w - pt, 0),
            (w, h // 2), (w - pt, h), (pt, h)]
    top = sc.lerp_color(pal["gem"], sc.WHITE, 0.1)
    bot = sc.lerp_color(pal["deep"], sc.NEAR_BLACK, 0.05)
    body = sc.vgrad_stops(w, h, 0, [(0.0, top), (0.5, pal["glow"]), (1.0, bot)],
                          255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    ov.blit(sh, (x0, y0 + m(2)))
    ov.blit(body, (x0, y0))
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(ov, (4, 5, 16), abspoly, width=max(1, m(1.4 * k / 1.9)))
    sc.plain_text(ov, tier_word, f, (m(cx), m(cy)), (14, 12, 26),
                  shadow_a=0, tracking=m(1.4 * k), weight=m(0.7 * k))


# ── K5 · constellation-web echo on the card body ──────────────────────────────
def _card_web(surf, rect):
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    cx, cy = rect.centerx, rect.centery
    s = 0.42
    nodes = [(0, -84), (74, -34), (52, 58), (-52, 58), (-74, -34),
             (30, -6), (-30, -6), (0, 30), (88, 26), (-88, 26)]
    nodes = [(cx + m(nx * s), cy + m(ny * s)) for nx, ny in nodes]
    web = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
           (0, 5), (0, 6), (1, 5), (4, 6), (5, 7), (6, 7), (2, 7), (3, 7),
           (5, 6), (1, 8), (2, 8), (4, 9), (3, 9)]
    glint = (240, 182, 62)
    deep = (22, 24, 56)
    for i, j in web:
        pygame.draw.line(layer, (*deep, 90), nodes[i], nodes[j], max(1, m(1)))
        pygame.draw.line(layer, (*glint, 52), nodes[i], nodes[j], 1)
    for x, y in nodes:
        pygame.draw.circle(layer, (*glint, 70), (int(x), int(y)), m(1.2))
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(mask, (255, 255, 255, 255), tray,
                     border_radius=m(sc.CARD_RAD) - m(4))
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(layer, (0, 0))


def patched_card_draw():
    src = textwrap.dedent(inspect.getsource(sc.draw_card))
    src, n = re.subn(r"(\n\s*# BAND A)", r"\n    _card_web(surf, rect)\1", src)
    assert n == 1, f"card web patch failed: {n}"
    ns = {}
    exec(compile(src, "<kinship_card_draw>", "exec"), sc.__dict__, ns)
    return ns["draw_card"]


def render_card(draw_fn):
    big = pygame.Surface((sc.CARD_W * sc.SS, sc.CARD_H * sc.SS), pygame.SRCALPHA)
    rect = pygame.Rect(m(sc._INSET), m(sc._INSET),
                       sc.CARD_W * sc.SS - 2 * m(sc._INSET),
                       sc.CARD_H * sc.SS - 2 * m(sc._INSET))
    draw_fn(big, SID, rect, False, False, owned=False)
    return pygame.transform.smoothscale(big, (sc.CARD_W, sc.CARD_H))


def render_pop(banner="stock", extra=None):
    pop = h2.render_base(TIER)
    ov = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)
    h2.overlay_buttons(ov)
    h2.overlay_bullion_chip(ov, h2.PRICES[TIER], h2._chip_cy(TIER))
    pal_tier = sc.RARITY[TIER.lower()]
    if banner == "stock":
        _confirm_tier_banner(ov, 130, 402, 140, 23, TIER, pal_tier)
    else:
        banner(ov, TIER, 130, 402, 140, pal_tier)
    if extra is not None:
        extra(ov, pal_tier)
    pop.blit(pygame.transform.smoothscale(ov, (POP_W, POP_H)), (0, 0))
    return pop


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
    h2.overlay_buttons = make_buttons_accent(
        can_stops, buy_text, pal["deep"], pal["bright"],
        make_inner_keyline(pal["glint"], pal["bright"], (26, 17, 4)))
    h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])
    try:
        stock_card = render_card(sc.draw_card)
        panels = []

        panels.append(("IN-GAME",
                       "the design currently live in the game",
                       "no change — card as in game",
                       render_stock(), stock_card))

        h2._DRAW_FN[0] = oc._patched_draw(pal["ring"], gem_x=None)
        panels.append(("BEFORE",
                       "no change — checkpoint 7, gems at stock position",
                       "no change — card as in game",
                       render_pop(), stock_card))
        h2._DRAW_FN[0] = oc._patched_draw(pal["ring"])

        panels.append(("K2 · crest-gem-grammar",
                       "gems moved to the sides, tucked to the frame at "
                       "the card's measured placement (in all K designs)",
                       "no change",
                       render_pop(), stock_card))

        store_mod._frame_hook = frame_card_kinship
        panels.append(("K1 · card-frame-kinship",
                       "K2 gems + frame rebuilt from the card's recipe: "
                       "keyline + single gold bevel + tray hairlines",
                       "no change",
                       render_pop(), stock_card))
        store_mod._frame_hook = fr.frame_double_bevel

        panels.append(("K4 · unified-ribbon",
                       "K2 gems + rarity banner redrawn as the card's "
                       "lozenge ribbon construction, scaled up",
                       "no change",
                       render_pop(banner=ribbon_banner), stock_card))

        _orig_owned = store_data.is_owned
        _orig_equipped = store_data.equipped
        EQUIP_SID = "skin_cowboy"
        store_data.is_owned = lambda s: s == EQUIP_SID or _orig_owned(s)
        store_data.equipped = lambda slot: EQUIP_SID
        sc.clear_cache()
        scene = StoreScene()
        scene.view = "category"
        scene.tab = 0
        scene.page = 0
        cat_surf = pygame.Surface((W, H))
        scene.render(cat_surf)
        store_data.is_owned = _orig_owned
        store_data.equipped = _orig_equipped
        sc.clear_cache()

        f_head = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        f_role = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        f_detail = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        MARGIN, HEAD, GAP = 24, 64, 20
        pop_w, pop_h = POP_W * 2, POP_H * 2
        card_w, card_h = sc.CARD_W * 2, sc.CARD_H * 2
        cell_w = max(pop_w, card_w) + 40
        cat_w, cat_h = cell_w, cell_w * H // W
        cell_h = pop_h + 12 + card_h + 12 + cat_h
        import textwrap as _tw
        FOOT = 220
        strip_w = MARGIN * 2 + len(panels) * (cell_w + GAP) - GAP
        strip_h = HEAD + cell_h + FOOT + 40
        strip = Image.new("RGB", (strip_w, strip_h), (10, 9, 20))
        idr = ImageDraw.Draw(strip)
        idr.text((MARGIN, 16),
                 "FIGURE K · popup-card kinship concepts · gold · MUMMY (epic) · "
                 "each column: popup / card / store category · 2x",
                 fill=(236, 214, 160), font=f_head)
        cat_img = Image.frombytes("RGB", (W, H),
                                  pygame.image.tostring(cat_surf, "RGB"))
        cat_img = cat_img.resize((cat_w, cat_h), Image.LANCZOS)
        for i, (role, pop_change, card_change, pop, card) in enumerate(panels):
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
            strip.paste(cat_img, (x, HEAD + pop_h + 12 + card_h + 12))
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
        idr.text((MARGIN, strip_h - 34),
                 "bottom row: store category as in game (COWBOY in its proper "
                 "EQUIPPED state) — identical context for every column",
                 fill=(150, 150, 170), font=f_detail)
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "confirm_purchase_v8", "premium-v1", "colorways",
                           "card_kinship_k_v9.png")
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
