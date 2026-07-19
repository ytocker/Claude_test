#!/usr/bin/env python3
"""ledger-row buy-confirm middle-block — round 2 render.

Round 2 addresses five art-director notes on the R1 sheet:
  • BUY pill fill raised to warm gold mids so it reads as a lit coin-gold CTA.
  • Price numeral bumped to font(13) and coin shrunk to r6, making the numeral
    the clearly dominant text in the ledger row.
  • Dotted leader alpha raised 70→110 so it reads as a real ledger device.
  • Price strip pushed toward warm-amber (fill alpha 30→72, colour shifted away
    from the cool card-body bleed).
  • Locked coin in the unaffordable state desaturated further (higher wash alpha,
    more neutral grey) so it reads clearly spent/inert.

Everything above y≈195 — card body, bevels, corner gems, name, rarity lozenge,
overhanging cabochon + halo, scrim — is copied unchanged from R1.
"""
import math
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

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body (kept) ─────────────────────────────────────────────────────
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

    # ── corner gem pair (kept) ───────────────────────────────────────────────
    store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])
    store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])

    # ── name (kept) ──────────────────────────────────────────────────────────
    store_cards.plain_text(big, name, store_cards.font(NAME_FS),
                           (m(CX), m(Y_NAME)), (250, 248, 240),
                           shadow_a=160, weight=m(0.9),
                           keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner (kept) ─────────────────────────────────────────────────
    store_cards._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── ledger-row block (replaces price_chip / equip / cancel) ──────────────
    def _engrave(y_dev):
        # A 2-device-px incised rule: bright catch-light riding a dark groove, so
        # the tray reads as two shallow shelves rather than a printed line.
        pygame.draw.line(big, (65, 62, 55), (m(16), y_dev - 1), (m(184), y_dev - 1))
        pygame.draw.line(big, (12, 10, 20), (m(16), y_dev), (m(184), y_dev))

    def _left_text(txt, fnt, left_x, cy, color):
        w = fnt.size(txt)[0]
        return store_cards.plain_text(big, txt, fnt, (left_x + w // 2, cy),
                                      color, shadow_a=0)

    def _right_text(txt, fnt, right_x, cy, color, keyline=None, kw=None):
        w = fnt.size(txt)[0]
        return store_cards.plain_text(big, txt, fnt, (right_x - w // 2, cy),
                                      color, shadow_a=120, weight=m(0.7),
                                      keyline=keyline, kw=kw)

    def _grey_coin(cx, cy, r):
        # Reuse the exact in-game coin, then wash with a stronger neutral-grey
        # so the unaffordable coin reads clearly spent rather than merely tinted.
        store_cards.coin_glyph(big, cx, cy, r)
        d = r * 2
        wash = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(wash, (96, 96, 100, 225), (r, r), r)
        pygame.draw.circle(wash, (118, 118, 122, 245), (r, r), r, max(1, m(1)))
        big.blit(wash, (cx - r, cy - r))

    def _padlock(cx, cy, s, col):
        bw, bh = int(s * 1.15), int(s * 0.9)
        body = pygame.Rect(cx - bw // 2, cy - bh // 6, bw, bh)
        pygame.draw.rect(big, col, body, border_radius=max(1, s // 5))
        sr = int(s * 0.42)
        pygame.draw.arc(big, col, (cx - sr, cy - bh // 6 - int(sr * 1.4),
                                   2 * sr, 2 * sr),
                        0.0, math.pi, max(2, s // 5))

    # Warm amber strip — alpha and hue raised so card-body bleed no longer
    # dominates; the row reads clearly as a warmer register than the card field.
    strip = pygame.Surface((m(168), m(34)), pygame.SRCALPHA)
    strip.fill((200, 160, 60, 72))
    big.blit(strip, (m(16), m(198)))

    _engrave(m(198))                                  # top hairline
    row_cy = m(215)

    _left_text("PRICE", store_cards.font(7), m(22), row_cy, (180, 170, 140))
    # Coin shrunk to r6 so the font(13) numeral is unambiguously the largest
    # text element in the ledger row.
    if affordable:
        store_cards.coin_glyph(big, m(44), row_cy, m(6))
    else:
        _grey_coin(m(44), row_cy, m(6))

    # Dotted leader — alpha raised 70→110 to read as a visible ledger device;
    # right endpoint trimmed to keep clear of the wider font(13) numeral.
    dot_col = (180, 170, 140)
    x = m(58)
    while x <= m(140):
        dot = pygame.Surface((m(2), m(2)), pygame.SRCALPHA)
        pygame.draw.circle(dot, (*dot_col, 110), (m(1), m(1)), max(1, m(1)))
        big.blit(dot, (x - m(1), row_cy - m(1)))
        x += m(12)

    price_txt = f"{price:,}"
    if affordable:
        _right_text(price_txt, store_cards.font(13), m(162), row_cy,
                    (248, 238, 210), keyline=(8, 7, 4), kw=m(1.0))
    else:
        _right_text(price_txt, store_cards.font(13), m(162), row_cy,
                    (110, 115, 130), keyline=(10, 11, 16), kw=m(1.0))

    _engrave(m(235))                                  # bottom hairline

    # ── BUY pill ──────────────────────────────────────────────────────────────
    buy_r = pygame.Rect(0, 0, m(136), m(30))
    buy_r.center = (m(100), m(260))
    buy_rad = buy_r.h // 2
    if affordable:
        # Fill pushed to warm gold mids so the pill glows like a coin — the
        # primary CTA must read as the warmest, brightest surface in the panel.
        store_cards._dark_chip_body(
            big, buy_r, buy_rad,
            [(0.0, (160, 120, 50)), (1.0, (120, 90, 34))],
            (60, 46, 16), (236, 202, 116), gloss=16, gamma=1.05)
        store_cards.bevel_rim(big, buy_r, buy_rad, (58, 44, 16),
                              (*store_cards.CARD_RING_BRIGHT, 235), w=max(1, m(1.5)))
        store_cards.plain_text(big, "BUY", store_cards.font(13),
                               buy_r.center, (248, 238, 210),
                               shadow_a=140, weight=m(0.9), tracking=m(1.5),
                               keyline=(20, 14, 4), kw=m(0.8))
    else:
        store_cards._dark_chip_body(
            big, buy_r, buy_rad,
            [(0.0, (22, 20, 18)), (1.0, (14, 13, 12))],
            (30, 28, 26), (60, 56, 52), gloss=8, gamma=1.04)
        _padlock(buy_r.centerx, buy_r.centery, m(12), (120, 128, 142))
        store_cards.plain_text(big, "NOT ENOUGH", store_cards.font(8),
                               (m(100), m(285)), (150, 166, 190), shadow_a=0,
                               tracking=m(0.8))

    # ── CANCEL text button (no chip; padded hit zone) ────────────────────────
    store_cards.plain_text(big, "CANCEL", store_cards.font(10),
                           (m(100), m(308)), (130, 124, 148), shadow_a=0)

    # ── overhanging disc + spotlight halo (kept) ─────────────────────────────
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

    # ── downscale + composite ────────────────────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))

    # Hit rects — BUY pill and the padded CANCEL text zone.
    if affordable:
        self.confirm_yes_rect = pygame.Rect(px + 100 - 68, py + 260 - 15, 136, 30)
    self.confirm_no_rect = pygame.Rect(px + 100 - 40, py + 300, 80, 32)


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


# ── pixel-verify BUY face luminance ──────────────────────────────────────────
# Sample a 20×10 px rect centred on the BUY pill face (popup-relative coords).
BUY_PILL_CY = 260 - (POP_H // 2 - (340 // 2))  # row 260 in popup coords
buy_crop = afford.crop((100 - 30, 260 - 10, 100 + 30, 260 + 10))
pix = list(buy_crop.getdata())
avg_lum = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pix) / len(pix)
print(f"BUY face avg luminance: {avg_lum:.1f}  (target ≥ 100)")
assert avg_lum >= 100, f"BUY pill too dark: {avg_lum:.1f}"


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


_ctext(CANVAS_W // 2, 10, "ledger-row · v2 buy-confirm · round 2", f_hdr,
       (220, 190, 100))
_ctext(110, 380, "AFFORDABLE", f_lab, (200, 185, 140))
_ctext(330, 380, "NOT ENOUGH", f_lab, (200, 185, 140))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v2", "ledger-row", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print("saved", OUT, canvas.size)
