#!/usr/bin/env python3
"""buy-then-wear buy-confirm action button — round 1 render.

A single clean "BUY & EQUIP" pill on one line: no coin embedded, no
micro-caption. The label carries the auto-equip promise; the price stays in the
price chip above. Affordable reads as a confident saturated warm-gold fill;
disabled drops to a muted desaturated pewter (a value/saturation drop, NOT a hue
swap) with greyed type — deliberately distinct from the coin-tab (embedded
price/coin) and big-press (padlock glyph) concepts.

Renders the FULL StoreScene confirm popup in both wallet states and swaps ONLY
the action-button block, so the pill is judged in its true surround.
"""
import os
import sys
import types

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image, ImageDraw, ImageFont

import game.store as store_mod
import game.store_cards as sc
import game.store_data as sd
from game.config import W, H


# ── replacement _draw_confirm ─────────────────────────────────────────────────
# A verbatim copy of StoreScene._draw_confirm whose ONLY change is the action
# button: the equip status_chip is swapped for the buy-then-wear pill. Its
# __globals__ are rebound to the store module so every module-level name
# (W/H/store_catalog/store_cards/store_data/_draw_qmark/UI_CREAM/NEAR_BLACK)
# resolves exactly as in the real render.
def _patched_draw_confirm(self, surf) -> None:
    self._confirm_panel = None
    self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog.is_secret(sid) and not store_data.is_owned(sid)
    tier = store_catalog.rarity(sid)
    pal = (store_cards.MYSTERY if secret
           else store_cards.RARITY.get(tier, store_cards.RARITY["common"]))
    tier_word = "MYSTERY" if secret else tier.upper()
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog.cost(sid)
    affordable = store_data.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    SS = store_cards.SS
    m = store_cards.m

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
    store_cards.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(store_cards.vgrad_stops(
        rect.w, rect.h, rad,
        [(0.0, store_cards.CARD_T), (1.0, store_cards.CARD_B)], 255, gamma=1.15),
        rect.topleft)
    store_cards.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    store_cards.bevel_rim(big, rect, rad, store_cards.CARD_RING_DEEP,
                          (*store_cards.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*store_cards.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    # ── corner gem pair ─────────────────────────────────────────────────────
    store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])
    store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])

    # ── name (above banner) ──────────────────────────────────────────────────
    store_cards.plain_text(big, name, store_cards.font(NAME_FS),
                           (m(CX), m(Y_NAME)), (250, 248, 240),
                           shadow_a=160, weight=m(0.9),
                           keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ────────────────────────────────────────────────────────
    store_cards._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── price chip ───────────────────────────────────────────────────────────
    store_cards.price_chip(big, m(CX), m(Y_CHIP), f"{price:,}",
                           m(CHIP_H), affordable=affordable)

    if not affordable:
        store_cards.plain_text(big, "NOT ENOUGH COINS",
                               store_cards.font(9), (m(CX), m(251)),
                               (150, 166, 190), shadow_a=0)

    # ── action button: buy-then-wear pill ─────────────────────────────────────
    CX_D = m(100)
    Y_BTN_D = m(Y_BTN)
    BTN_H_D = m(BTN_H)
    BTN_W_D = m(BTN_W)
    btn_x0 = CX_D - BTN_W_D // 2
    btn_y0 = Y_BTN_D - BTN_H_D // 2
    btn_rad = BTN_H_D // 2
    r = pygame.Rect(btn_x0, btn_y0, BTN_W_D, BTN_H_D)
    if affordable:
        # Confident saturated warm-gold fill — the auto-equip promise reads bold.
        store_cards.chip_body(big, r, btn_rad,
                              (210, 185, 100), (155, 120, 45),
                              (80, 58, 10), (255, 235, 160), gloss=65)
        store_cards.bevel_rim(big, r, btn_rad,
                              (120, 90, 30, 220), (255, 240, 160, 200), w=2)
        store_cards.plain_text(big, "BUY & EQUIP", store_cards.font(8.5),
                               (CX_D, Y_BTN_D),
                               (30, 22, 8), shadow_a=0, weight=m(0.9),
                               tracking=m(1.2))
    else:
        # Disabled drops to a muted desaturated pewter — a value/saturation fall,
        # not a hue swap — with the label greyed to match.
        store_cards._dark_chip_body(big, r, btn_rad,
                                    [(0.0, (52, 48, 58)), (1.0, (38, 34, 46))],
                                    (28, 26, 36), (80, 76, 90), gloss=10, gamma=1.04)
        store_cards.bevel_rim(big, r, btn_rad,
                              (50, 46, 60, 180), (100, 96, 112, 160), w=2)
        store_cards.plain_text(big, "BUY & EQUIP", store_cards.font(8.5),
                               (CX_D, Y_BTN_D),
                               (90, 85, 100), shadow_a=0, tracking=m(1.2))

    # ── cancel button ────────────────────────────────────────────────────────
    h_can = m(CANCEL_H)
    w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2,
                        w_can, h_can)
    store_cards._dark_chip_body(big, can_r, h_can // 2,
                                [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                                (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    store_cards.plain_text(big, "CANCEL", store_cards.font(11),
                           can_r.center, (130, 124, 148), shadow_a=0)

    # ── overhanging disc + spotlight halo (crowns the card) ──────────────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"],
                            peak=95, layers=24)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"],
                            peak=70, layers=12)
    store_cards.cabochon(big, cx_ss, cy_ss, r_ss,
                         store_cards.CABO_LO, store_cards.CABO_HI,
                         ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK,
                    thick=5)
    else:
        store_cards.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    store_cards.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── downscale and composite onto screen ──────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))


store_mod.StoreScene._draw_confirm = types.FunctionType(
    _patched_draw_confirm.__code__, store_mod.__dict__, "_draw_confirm")


# ── per-state render → PIL crop ───────────────────────────────────────────────
POP_W, POP_H = 200, 340
CROP_X, CROP_Y = (W - POP_W) // 2, (H - POP_H) // 2


def render_state(balance_val):
    sd.load()
    sd.balance = lambda: balance_val
    sc._card_cache.clear()
    scene = store_mod.StoreScene()
    scene.view = "category"
    scene._confirm = "skin_mummy"
    screen = pygame.Surface((W, H))
    scene.render(screen)
    raw = pygame.image.tostring(screen, "RGB")
    img = Image.frombytes("RGB", (W, H), raw)
    return img.crop((CROP_X, CROP_Y, CROP_X + POP_W, CROP_Y + POP_H))


afford = render_state(999_999)
locked = render_state(0)


# ── compose review sheet ──────────────────────────────────────────────────────
CANVAS_W, CANVAS_H = 460, 400
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
canvas.paste(afford, (0, 30))
canvas.paste(locked, (220, 30))

draw = ImageDraw.Draw(canvas)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
try:
    f_hdr = ImageFont.truetype(FONT_PATH, 11)
    f_lab = ImageFont.truetype(FONT_PATH, 13)
except Exception:
    f_hdr = f_lab = ImageFont.load_default()


def _ctext(x, y, txt, fnt, col):
    w = draw.textlength(txt, font=fnt)
    draw.text((x - w / 2, y), txt, font=fnt, fill=col)


_ctext(CANVAS_W // 2, 10, "buy-then-wear · BUY & EQUIP PILL", f_hdr, (220, 190, 100))
_ctext(110, 380, "AFFORDABLE", f_lab, (200, 185, 140))
_ctext(330, 380, "NOT ENOUGH", f_lab, (200, 185, 140))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup", "buy-then-wear", "round_1.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print("saved", OUT, canvas.size)
