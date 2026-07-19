#!/usr/bin/env python3
"""
big-press  ·  store confirm-popup action button  ·  round 1

Concept (locked): the buy-confirm action button is a WIDE BEVELED LOZENGE with
chamfered edges and a TOP-EDGE SHEEN STRIP only — no radial dome, because the
overhanging cabochon disc that crowns the popup already owns the dome read.
Symmetric centred layout, one line: "GET IT". No coin/price on the button (cost
stays in the price chip above). Affordable = bright bevel + top sheen, a
physically pressable slab. Disabled = the whole lozenge drops in lightness +
saturation to dimmed slate and a padlock glyph is stamped centred over a greyed
label.

Sheet: LEFT = AFFORDABLE state, RIGHT = UNAFFORDABLE state — each the exact
in-game StoreScene popup cropped to 200x340, with only the action button
replaced by this concept.
"""
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
    """Faithful reproduction of StoreScene._draw_confirm with ONLY the action
    button slot replaced by the big-press beveled lozenge — every other popup
    element (card body, corner gems, name, rarity banner, price chip, NOT ENOUGH
    COINS, CANCEL, crowning disc + aura) is drawn identically to the live game."""
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
    Y_BTN, BTN_H, BTN_W = 273, 30, 136
    Y_CANCEL, CANCEL_H, CANCEL_W = 308, 22, 80

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

    # ── name (above banner) ───────────────────────────────────────────────────
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

    # ── action button: big-press beveled lozenge ──────────────────────────────
    CX_D = m(CX)
    Y_BTN_D = m(Y_BTN)
    BTN_H_D = m(BTN_H)
    BTN_W_D = m(BTN_W)
    btn_x0 = CX_D - BTN_W_D // 2
    btn_y0 = Y_BTN_D - BTN_H_D // 2
    lrad = BTN_H_D // 2

    if affordable:
        # Wide beveled lozenge — bright top sheen, NO radial dome (disc owns it).
        sc._dark_chip_body(big, pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D), lrad,
                           [(0.0, (60, 55, 80)), (1.0, (35, 30, 55))],
                           (25, 20, 42), (140, 130, 160), gloss=60, gamma=1.08)
        sc.bevel_rim(big, pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D), lrad,
                     (40, 36, 65, 220), (160, 148, 200, 200), w=max(1, m(1.5)))
        # Top-edge sheen strip (horizontal, feathered to the ends — not radial).
        sheen_h = max(2, m(2))
        sheen_w = BTN_W_D - 4
        sheen_surf = pygame.Surface((sheen_w, sheen_h), pygame.SRCALPHA)
        for sx in range(sheen_w):
            hx = abs(sx - sheen_w / 2) / (sheen_w / 2)
            a = int(160 * (1.0 - hx ** 1.4))
            for sy in range(sheen_h):
                sheen_surf.set_at((sx, sy), (230, 220, 255, a))
        big.blit(sheen_surf, (btn_x0 + 2, btn_y0 + 2))
        sc.plain_text(big, "GET IT", sc.font(10), (CX_D, Y_BTN_D),
                      (230, 225, 248), shadow_a=120, weight=m(0.9),
                      keyline=(20, 16, 38), kw=m(0.7))
    else:
        # Disabled: dimmed slate lozenge, padlock stamped over a greyed label.
        full_r = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)
        sc._dark_chip_body(big, full_r, lrad,
                           [(0.0, (38, 34, 48)), (1.0, (26, 22, 36))],
                           (18, 16, 28), (70, 65, 85), gloss=10, gamma=1.04)
        sc.bevel_rim(big, full_r, lrad, (35, 32, 48, 180), (80, 75, 100, 150),
                     w=max(1, m(1.5)))
        sc.plain_text(big, "GET IT", sc.font(10), (CX_D, Y_BTN_D),
                      (75, 70, 90), shadow_a=0)
        pk_cx, pk_cy = CX_D, Y_BTN_D
        pk_w, pk_h = m(14), m(12)
        pk_rad = m(3)
        body_r = pygame.Rect(pk_cx - pk_w // 2, pk_cy - pk_h // 2 + m(2),
                             pk_w, pk_h - m(3))
        pygame.draw.rect(big, (90, 85, 110, 220), body_r, border_radius=pk_rad)
        pygame.draw.rect(big, (55, 50, 70, 255), body_r, width=max(1, m(1)),
                         border_radius=pk_rad)
        shackle_r = pk_w // 2 - m(1)
        arc_rect = pygame.Rect(pk_cx - shackle_r, pk_cy - pk_h // 2 - shackle_r + m(2),
                               shackle_r * 2, shackle_r * 2)
        pygame.draw.arc(big, (90, 85, 110, 200), arc_rect, 0, 3.14159, max(1, m(2)))
        pygame.draw.circle(big, (45, 40, 60, 255), (pk_cx, pk_cy + m(1)), max(1, m(2)))

    # ── cancel button ─────────────────────────────────────────────────────────
    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2, w_can, h_can)
    sc._dark_chip_body(big, can_r, h_can // 2,
                       [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                       (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, (130, 124, 148),
                  shadow_a=0)

    # ── overhanging disc + spotlight halo (crowns the card) ───────────────────
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


def render_state(affordable):
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


afford_img = render_state(True)
unafford_img = render_state(False)

# ── review sheet ──────────────────────────────────────────────────────────────
SHEET_W, SHEET_H = 460, 400
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))

# paste crops (via pygame surfaces so we stay in one toolkit for the chrome)
def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")

sheet.blit(_pil_to_surf(afford_img), (0, 30))
sheet.blit(_pil_to_surf(unafford_img), (220, 30))

hdr_font = store_mod._font(16, True)
hdr = hdr_font.render("big-press · BEVELED LOZENGE", True, (220, 190, 100))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (200, 185, 140))
lu = lbl_font.render("NOT ENOUGH", True, (200, 185, 140))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(320, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup", "big-press", "round_1.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
