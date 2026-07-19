"""unlock-latch concept — Round 1 review sheet for the buy-confirm popup
action button. Renders the full StoreScene confirm popup twice (affordable /
unaffordable) with only the action button swapped for a padlock pill: an OPEN
shackle + warm fill signals affordability, a CLOSED shackle + pewter tarnish
signals locked/too-expensive."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import math

import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
from game import store_catalog
from game.config import W, H

POP_W, POP_H = 200, 340
POP_X = (W - POP_W) // 2
POP_Y = (H - POP_H) // 2


def _unlock_latch_button(big, affordable):
    """Draw the padlock pill into the action-button slot on the SS=2 surface.
    The pill's temperature is the primary read (warm=buy / pewter=locked); the
    shackle state is the secondary confirming cue (open vs closed)."""
    m = sc.m
    CX_D = m(100)
    Y_BTN_D = m(273)
    BTN_H_D = m(30)
    BTN_W_D = m(136)
    btn_x0 = CX_D - BTN_W_D // 2
    btn_y0 = Y_BTN_D - BTN_H_D // 2
    rad = BTN_H_D // 2

    r = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)
    cy = Y_BTN_D

    if affordable:
        sc._dark_chip_body(big, r, rad,
                           [(0.0, (55, 45, 25)), (1.0, (35, 28, 12))],
                           (25, 18, 6), (200, 165, 80), gloss=40, gamma=1.06)
        sc.bevel_rim(big, r, rad, (100, 80, 30, 220), (230, 200, 120, 200), w=2)
        label_col = (220, 200, 130)
    else:
        sc._dark_chip_body(big, r, rad,
                           [(0.0, (52, 48, 58)), (1.0, (38, 34, 46))],
                           (28, 26, 36), (80, 76, 90), gloss=10, gamma=1.04)
        sc.bevel_rim(big, r, rad, (50, 46, 60, 180), (100, 96, 112, 160), w=2)
        label_col = (90, 85, 100)

    # Padlock glyph at the left side of the pill.
    pk_cx = btn_x0 + m(18)
    pk_cy = cy
    pk_body_w = m(14)
    pk_body_h = m(10)
    pk_body_r = m(2)
    pk_body = pygame.Rect(pk_cx - pk_body_w // 2, pk_cy - pk_body_h // 2 + m(2),
                          pk_body_w, pk_body_h)

    if affordable:
        body_col = (200, 170, 80, 220)
        arc_col = (200, 170, 80, 220)
        shackle_w = max(1, m(2))
    else:
        body_col = (80, 75, 95, 200)
        arc_col = (80, 75, 95, 200)
        shackle_w = max(1, m(2))

    pygame.draw.rect(big, body_col, pk_body, border_radius=pk_body_r)
    pygame.draw.rect(big, (20, 16, 28, 200), pk_body,
                     width=max(1, m(1)), border_radius=pk_body_r)
    pygame.draw.circle(big, (20, 16, 28, 200), (pk_cx, pk_cy + m(2)), max(1, m(2)))

    shackle_r = pk_body_w // 2 - m(1)
    arc_center_x = pk_cx
    arc_center_y = pk_cy - pk_body_h // 2 + m(1)

    if affordable:
        # Open shackle: right leg seats into the body, left leg swings free.
        arc_rect = pygame.Rect(arc_center_x - shackle_r, arc_center_y - shackle_r,
                               shackle_r * 2, shackle_r * 2)
        pygame.draw.arc(big, arc_col, arc_rect, 0, math.pi, shackle_w)
        pygame.draw.line(big, arc_col,
                         (pk_cx + shackle_r, arc_center_y),
                         (pk_cx + shackle_r, pk_cy - pk_body_h // 2 + m(2)), shackle_w)
        pygame.draw.line(big, arc_col,
                         (pk_cx - shackle_r, arc_center_y),
                         (pk_cx - shackle_r - m(3), arc_center_y - m(6)), shackle_w)
    else:
        # Closed shackle: full U, both legs seated into the body.
        arc_rect = pygame.Rect(arc_center_x - shackle_r, arc_center_y - shackle_r,
                               shackle_r * 2, shackle_r * 2)
        pygame.draw.arc(big, arc_col, arc_rect, 0, math.pi, shackle_w)
        pygame.draw.line(big, arc_col,
                         (pk_cx - shackle_r, arc_center_y),
                         (pk_cx - shackle_r, pk_cy - pk_body_h // 2 + m(2)), shackle_w)
        pygame.draw.line(big, arc_col,
                         (pk_cx + shackle_r, arc_center_y),
                         (pk_cx + shackle_r, pk_cy - pk_body_h // 2 + m(2)), shackle_w)

    # Label "UNLOCK" — seated to the right of the padlock.
    label_x = btn_x0 + m(34)
    label_w = BTN_W_D - m(34)
    sc.plain_text(big, "UNLOCK", sc.font(9.5),
                  (label_x + label_w // 2, cy),
                  label_col, shadow_a=0, weight=m(0.9))


def patched_draw_confirm(self, surf):
    """Copy of StoreScene._draw_confirm with the EQUIP action chip replaced by
    the unlock-latch pill; every other popup element is drawn identically."""
    store_catalog_ = store_mod.store_catalog
    store_data_ = store_mod.store_data
    store_cards_ = store_mod.store_cards
    UI_CREAM = store_mod.UI_CREAM
    NEAR_BLACK = store_mod.NEAR_BLACK
    _draw_qmark = store_mod._draw_qmark

    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog_.is_secret(sid) and not store_data_.is_owned(sid)
    tier = store_catalog_.rarity(sid)
    pal = (store_cards_.MYSTERY if secret
           else store_cards_.RARITY.get(tier, store_cards_.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog_.cost(sid)
    affordable = store_data_.balance() >= price

    _POP_W, _POP_H = 200, 340
    CX = _POP_W // 2
    SS = store_cards_.SS
    m = store_cards_.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120
    Y_CHIP, CHIP_H = 229, 28
    Y_CANCEL, CANCEL_H, CANCEL_W = 308, 22, 80

    big = pygame.Surface((_POP_W * SS, _POP_H * SS), pygame.SRCALPHA)

    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
    store_cards_.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(store_cards_.vgrad_stops(
        rect.w, rect.h, rad,
        [(0.0, store_cards_.CARD_T), (1.0, store_cards_.CARD_B)], 255, gamma=1.15),
        rect.topleft)
    store_cards_.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    store_cards_.bevel_rim(big, rect, rad, store_cards_.CARD_RING_DEEP,
                           (*store_cards_.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*store_cards_.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    store_cards_.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                           pal["gem"], pal["deep"])
    store_cards_.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                           pal["gem"], pal["deep"])

    store_cards_.plain_text(big, name, store_cards_.font(NAME_FS),
                            (m(CX), m(Y_NAME)), (250, 248, 240),
                            shadow_a=160, weight=m(0.9),
                            keyline=(6, 6, 16), kw=m(1.0))

    store_cards_._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    store_cards_.price_chip(big, m(CX), m(Y_CHIP), f"{price:,}",
                            m(CHIP_H), affordable=affordable)

    if not affordable:
        store_cards_.plain_text(big, "NOT ENOUGH COINS",
                                store_cards_.font(9), (m(CX), m(251)),
                                (150, 166, 190), shadow_a=0)

    # ── unlock-latch action button (replaces the EQUIP chip) ──────────────────
    _unlock_latch_button(big, affordable)

    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2,
                        w_can, h_can)
    store_cards_._dark_chip_body(big, can_r, h_can // 2,
                                 [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                                 (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    store_cards_.plain_text(big, "CANCEL", store_cards_.font(11),
                            can_r.center, (130, 124, 148), shadow_a=0)

    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    store_cards_._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"],
                             peak=95, layers=24)
    store_cards_._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"],
                             peak=70, layers=12)
    store_cards_.cabochon(big, cx_ss, cy_ss, r_ss,
                          store_cards_.CABO_LO, store_cards_.CABO_HI,
                          ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK,
                    thick=5)
    else:
        store_cards_.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    store_cards_.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    pop = pygame.transform.smoothscale(big, (_POP_W, _POP_H))
    px = (W - _POP_W) // 2
    py = (H - _POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, _POP_W, _POP_H)
    surf.blit(pop, (px, py))


def _render_popup(sid, affordable, price):
    orig_balance = sd.balance
    sd.balance = (lambda: price + 5000) if affordable else (lambda: max(0, price - 100))
    try:
        scene = store_mod.StoreScene()
        scene.view = "category"
        scene.t = 0.0
        scene._confirm = sid
        surf = pygame.Surface((W, H), pygame.SRCALPHA)
        surf.fill((8, 8, 20, 255))
        scene._draw_confirm(surf)
    finally:
        sd.balance = orig_balance
    return surf.subsurface((POP_X, POP_Y, POP_W, POP_H)).copy()


def main():
    store_mod.StoreScene._draw_confirm = patched_draw_confirm

    # A concrete, ownable, non-secret skin gives a real thumbnail + price chip.
    sid = next(i for i in store_catalog.ids_of_kind("skin")
               if not store_catalog.is_secret(i))
    price = store_catalog.cost(sid)

    afford = _render_popup(sid, True, price)
    locked = _render_popup(sid, False, price)

    sheet = pygame.Surface((460, 400))
    sheet.fill((8, 8, 20))

    hfont = pygame.font.SysFont("Arial", 15, bold=True)
    lfont = pygame.font.SysFont("Arial", 12, bold=True)
    hdr = hfont.render("unlock-latch · PADLOCK PILL", True, (220, 190, 100))
    sheet.blit(hdr, (10, 10))

    sheet.blit(afford, (0, 30))
    sheet.blit(locked, (220, 30))

    la = lfont.render("AFFORDABLE (open)", True, (200, 185, 140))
    lb = lfont.render("LOCKED (closed)", True, (200, 185, 140))
    sheet.blit(la, (100 - la.get_width() // 2, 380))
    sheet.blit(lb, (320 - lb.get_width() // 2, 380))

    out_dir = os.path.join(os.path.dirname(__file__), "..",
                           "docs", "store_confirm_popup", "unlock-latch")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")
    pygame.image.save(sheet, out)
    print("saved", os.path.abspath(out), "size", sheet.get_size(), "sid", sid)


if __name__ == "__main__":
    main()
