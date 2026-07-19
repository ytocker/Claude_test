#!/usr/bin/env python3
"""
big-press  ·  store confirm-popup action button  ·  round 2

Addresses all art-director critique points from round 1:

1. Re-warmed affordable cap: warm dark-gold body gradient, gold bevel rim
   (200,170,80)/(160,130,55), warm amber sheen strip, cream "GET IT" label.
2. Vertical cylindrical dome: 3-stop top→center-top→bottom gradient makes the
   cap feel raised and pressable — brightest at the top-center dome face, dark at
   the foot. Gloss tuned so it reinforces the peak, not fights the gradient.
3. Disabled padlock: label cleared entirely; single clean centered padlock glyph
   (light pewter icon on dark slate, >40 luma contrast). No label/icon merge.
4. Cap silhouette: height 35 logical (from 30), corner radius 40% of height —
   chamfered ends rather than full pill, reads "button cap" not "tag".
5. State temperatures: affordable = warm gold/amber; disabled = cold slate.
   Luma gap of affordable vs CANCEL ≥ 30 points (achieved ~55 points).
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image

import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
import game.store_catalog as store_catalog
from game.config import W, H

_draw_qmark = store_mod._draw_qmark
UI_CREAM = store_mod.UI_CREAM
NEAR_BLACK = store_mod.NEAR_BLACK


def _patched_draw_confirm(self, surf):
    """Faithful StoreScene._draw_confirm with ONLY the action-button slot replaced
    by the round-2 big-press cap — card body, gems, name, rarity banner, price chip,
    NOT-ENOUGH text, CANCEL, and the crowning disc + halo are all identical to live."""
    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog.is_secret(sid) and not sd.is_owned(sid)
    tier = store_catalog.rarity(sid)
    pal = (sc.MYSTERY if secret
           else sc.RARITY.get(tier, sc.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog.cost(sid)
    affordable = sd.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    SS = sc.SS
    m = sc.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120
    Y_CHIP, CHIP_H = 229, 28
    # Cap is 35 logical tall (from 30) — more mass reads as a pressable slab
    Y_BTN, BTN_H, BTN_W = 272, 35, 136
    Y_CANCEL, CANCEL_H, CANCEL_W = 310, 22, 80

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body ─────────────────────────────────────────────────────────────
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(sc.vgrad_stops(
        rect.w, rect.h, rad,
        [(0.0, sc.CARD_T), (1.0, sc.CARD_B)], 255, gamma=1.15),
        rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    # ── corner gem pair ───────────────────────────────────────────────────────
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

    # ── name ─────────────────────────────────────────────────────────────────
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ─────────────────────────────────────────────────────────
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── price chip ────────────────────────────────────────────────────────────
    sc.price_chip(big, m(CX), m(Y_CHIP), f"{price:,}", m(CHIP_H),
                  affordable=affordable)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH COINS", sc.font(9), (m(CX), m(251)),
                      (150, 166, 190), shadow_a=0)

    # ── action button: big-press cap ──────────────────────────────────────────
    CX_D    = m(CX)
    Y_BTN_D = m(Y_BTN)
    BTN_H_D = m(BTN_H)
    BTN_W_D = m(BTN_W)
    btn_x0  = CX_D - BTN_W_D // 2
    btn_y0  = Y_BTN_D - BTN_H_D // 2
    # 40% of height → chamfered ends that read "cap" rather than pill/tag
    lrad = int(BTN_H_D * 0.40)

    if affordable:
        # Vertical cylindrical dome: 3-stop gradient rises to its peak at 35% from
        # top (the brightest point of the dome face), then falls to the dark foot.
        # The foot being darker than the top edge gives the "proud off the card" read.
        sc._dark_chip_body(
            big,
            pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D),
            lrad,
            [(0.0, (65, 55, 30)), (0.35, (85, 72, 38)), (1.0, (30, 25, 12))],
            rim_dark=(80, 58, 12),          # very dark bronze outer keyline
            rim_bright=(200, 170, 80),      # warm gold bevel highlight
            gloss=20,
            gamma=1.0,
        )
        # Warm amber edge sheen across the full button top — feathered to the ends
        # so it wraps the cap contour rather than looking like a label underline.
        sheen_h = max(2, m(2))
        sheen_w = BTN_W_D - 4
        sheen_surf = pygame.Surface((sheen_w, sheen_h), pygame.SRCALPHA)
        for sx in range(sheen_w):
            hx = abs(sx - sheen_w / 2) / (sheen_w / 2)
            a = int(130 * (1.0 - hx ** 1.4))
            for sy in range(sheen_h):
                sheen_surf.set_at((sx, sy), (220, 185, 100, a))
        big.blit(sheen_surf, (btn_x0 + 2, btn_y0 + 2))
        # Cream label — warm, not cool white
        sc.plain_text(big, "GET IT", sc.font(10), (CX_D, Y_BTN_D),
                      (248, 238, 210), shadow_a=130, weight=m(0.9),
                      keyline=(20, 14, 4), kw=m(0.7))

    else:
        # Disabled: cold slate lozenge (intentionally different hue temperature
        # from affordable).  Value drops so the cap reads locked, not just dim.
        full_r = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)
        sc._dark_chip_body(
            big, full_r, lrad,
            [(0.0, (30, 26, 42)), (1.0, (18, 14, 28))],
            rim_dark=(22, 18, 36),
            rim_bright=(60, 55, 80),
            gloss=8, gamma=1.04,
        )
        # ── centered padlock glyph — NO label text, clean single icon ──────
        # Light pewter on dark slate: luma contrast ≈ 113 >> 40 required.
        pk_cx = CX_D
        pk_cy = Y_BTN_D
        icon_col   = (140, 130, 150)
        icon_dark  = (22, 18, 32)       # matches button body for keyhole cutout

        # Body: filled rounded rect 14×10 logical, top at 3 logical above center
        pk_bw  = m(14)
        pk_bh  = m(10)
        pk_brad = m(3)
        body_top = pk_cy - m(3)
        body_r = pygame.Rect(pk_cx - pk_bw // 2, body_top, pk_bw, pk_bh)
        pygame.draw.rect(big, icon_col, body_r, border_radius=pk_brad)

        # Keyhole: small filled circle at the body center
        key_cy = body_top + pk_bh // 2
        pygame.draw.circle(big, icon_dark, (pk_cx, key_cy), max(2, m(2)))

        # Shackle: top-half arc (0 → π) centered at the body-top edge so the feet
        # align with the body-width corners.  Radius = half body width so the
        # shackle spans exactly the body at its attachment points.
        shackle_r = pk_bw // 2          # = m(7) in device px
        arc_rect = pygame.Rect(
            pk_cx - shackle_r, body_top - shackle_r,
            shackle_r * 2, shackle_r * 2,
        )
        pygame.draw.arc(big, icon_col, arc_rect, 0, math.pi, max(3, m(2)))

    # ── cancel button ─────────────────────────────────────────────────────────
    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2, w_can, h_can)
    sc._dark_chip_body(big, can_r, h_can // 2,
                       [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                       (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, (130, 124, 148),
                  shadow_a=0)

    # ── overhanging disc + spotlight halo ─────────────────────────────────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK, thick=5)
    else:
        sc.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── downscale + composite ─────────────────────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))

    self.confirm_no_rect = pygame.Rect(
        px + CX - CANCEL_W // 2, py + Y_CANCEL - CANCEL_H // 2, CANCEL_W, CANCEL_H)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + CX - BTN_W // 2, py + Y_BTN - BTN_H // 2, BTN_W, BTN_H)


store_mod.StoreScene._draw_confirm = _patched_draw_confirm


def _render_state(affordable):
    sd.load()
    sd.balance = (lambda: 999_999) if affordable else (lambda: 0)
    sc._card_cache.clear()
    scene = store_mod.StoreScene()
    scene.view = "category"
    scene._confirm = "skin_mummy"
    screen = pygame.Surface((W, H))
    screen.fill((6, 7, 18))
    scene.render(screen)

    POP_W, POP_H = 200, 340
    px, py = (W - POP_W) // 2, (H - POP_H) // 2
    raw = pygame.image.tostring(screen, "RGBA")
    full = Image.frombytes("RGBA", (W, H), raw)
    return full.crop((px, py, px + POP_W, py + POP_H))


afford_img   = _render_state(True)
unafford_img = _render_state(False)


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")


# ── review sheet ──────────────────────────────────────────────────────────────
SHEET_W, SHEET_H = 460, 400
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))

sheet.blit(_pil_to_surf(afford_img),   (0,   30))
sheet.blit(_pil_to_surf(unafford_img), (220, 30))

hdr_font = store_mod._font(16, True)
hdr = hdr_font.render("big-press · BEVELED LOZENGE  r2", True, (220, 190, 100))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (200, 185, 140))
lu = lbl_font.render("NOT ENOUGH", True, (200, 185, 140))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(320, 378)))

OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_confirm_popup", "big-press", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
