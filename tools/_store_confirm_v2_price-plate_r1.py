#!/usr/bin/env python3
"""
price-plate  ·  store buy-confirmation popup v2  ·  round 1

Concept: the lower half of the confirm popup is reorganised around a HORIZONTAL
ENAMEL PLAQUE. A wide, low-radius rounded plate (machined-looking, NEVER a
capsule) carries the price — coin + numeral struck into a warm enamel field with
knurled short edges. Beneath it, action is split into a side-by-side BUY + CANCEL
pair so the primary tap and the escape hatch read as two distinct controls.

Everything above y~195 (card body, corner gems, name, rarity lozenge, crowning
cabochon + aura, scrim) is drawn identically to the live StoreScene._draw_confirm.

Sheet: LEFT = AFFORDABLE, RIGHT = UNAFFORDABLE — each the in-game popup cropped
to 200x340 with only the y~195-325 band replaced by this concept.
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


def _knurl(surf, rect, light, dark):
    """Machined-ridge read on the two SHORT (left/right) end caps: a short stack
    of 1px horizontal bands alternating a lighter/darker enamel tone. Kept to the
    mid-height band so it never fights the rounded corners; long edges stay flat."""
    strip_w = sc.m(5)
    n = 7
    step = sc.m(1.4)
    y0 = rect.centery - (n * step) // 2
    lw = max(1, sc.m(0.6))
    for left_cap in (True, False):
        x0 = rect.x + sc.m(3) if left_cap else rect.right - sc.m(3) - strip_w
        for i in range(n):
            yy = y0 + i * step
            col = light if i % 2 == 0 else dark
            pygame.draw.line(surf, col, (x0, yy), (x0 + strip_w, yy), lw)


def _price_in_plate(big, cx_d, cy_d, price, affordable):
    """Coin glyph + numeral, centred together on the plate baseline. The numeral
    is the highest-contrast element (cream on affordable, slate when tarnished)."""
    txt = f"{price:,}"
    coin_r = sc.m(8)
    coin_d = coin_r * 2
    gap = sc.m(4)
    num_font = sc.font(16)
    num_w = num_font.render(txt, True, (255, 255, 255)).get_width()
    total = coin_d + gap + num_w
    left = cx_d - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2

    if affordable:
        sc.coin_glyph(big, coin_cx, cy_d, coin_r)
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (248, 238, 210),
                      shadow_a=150, weight=sc.m(0.9),
                      keyline=(38, 28, 8), kw=sc.m(1.0))
    else:
        # tarnished: flat grey disc instead of the gold coin
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy_d), coin_r)
        pygame.draw.circle(big, (96, 100, 114), (coin_cx, cy_d), coin_r,
                           width=max(1, sc.m(1)))
        pygame.draw.circle(big, (122, 126, 140), (coin_cx, cy_d),
                           coin_r - sc.m(2), width=max(1, sc.m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (110, 115, 130),
                      shadow_a=0, weight=sc.m(0.6),
                      keyline=(22, 22, 30), kw=sc.m(0.9))


def _padlock(big, cx, cy):
    """Small slate padlock stamped over a tarnished BUY button."""
    pk_w, pk_h = sc.m(13), sc.m(11)
    body_r = pygame.Rect(cx - pk_w // 2, cy - pk_h // 2 + sc.m(2),
                         pk_w, pk_h - sc.m(3))
    pygame.draw.rect(big, (108, 114, 132, 230), body_r, border_radius=sc.m(3))
    pygame.draw.rect(big, (58, 62, 78, 255), body_r, width=max(1, sc.m(1)),
                     border_radius=sc.m(3))
    sh_r = pk_w // 2 - sc.m(1)
    arc = pygame.Rect(cx - sh_r, cy - pk_h // 2 - sh_r + sc.m(2), sh_r * 2, sh_r * 2)
    pygame.draw.arc(big, (108, 114, 132, 220), arc, 0, 3.14159, max(1, sc.m(2)))
    pygame.draw.circle(big, (52, 56, 70, 255), (cx, cy + sc.m(1)), max(1, sc.m(1.6)))


def _patched_draw_confirm(self, surf):
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

    # ── price-plate concept metrics (logical) ─────────────────────────────────
    PL_TOP, PL_W, PL_H, PL_RAD = 215, 120, 34, 7
    PL_CY = PL_TOP + PL_H // 2           # 232 — coin baseline
    Y_ACT = 278                          # BUY/CANCEL row centre
    BUY_W, BUY_H = 88, 30
    CAN_W, CAN_H = 64, 30
    PAIR_GAP = 8
    HIT_H = 32
    PAIR_W = BUY_W + PAIR_GAP + CAN_W
    PAIR_L = CX - PAIR_W // 2            # 20
    BUY_CX = PAIR_L + BUY_W // 2         # 64
    CAN_CX = PAIR_L + BUY_W + PAIR_GAP + CAN_W // 2   # 148

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

    # ── enamel price plaque ───────────────────────────────────────────────────
    pl = pygame.Rect(m(CX - PL_W // 2), m(PL_TOP), m(PL_W), m(PL_H))
    plr = m(PL_RAD)
    sc.drop_shadow(big, pl, plr, blur=m(4), alpha=120, dy=m(2))
    if affordable:
        face = sc.vgrad_stops(pl.w, pl.h, plr,
                              [(0.0, (55, 48, 28)), (0.5, (42, 36, 18)),
                               (1.0, (28, 22, 8))], 255, gamma=1.05)
        big.blit(face, pl.topleft)
        sc.top_sheen(big, pl, plr, m(14), peak=40)
        _knurl(big, pl, (86, 74, 44), (20, 16, 6))
        pygame.draw.rect(big, (14, 11, 4), pl, width=max(1, m(1)), border_radius=plr)
        sc.bevel_rim(big, pl, plr, (78, 52, 12, 210),
                     (255, 236, 178, 210), w=max(1, m(1.4)))
    else:
        face = sc.vgrad_stops(pl.w, pl.h, plr,
                              [(0.0, (42, 42, 52)), (1.0, (28, 28, 38))],
                              255, gamma=1.02)
        big.blit(face, pl.topleft)
        _knurl(big, pl, (66, 66, 78), (18, 18, 26))
        pygame.draw.rect(big, (14, 14, 20), pl, width=max(1, m(1)), border_radius=plr)
        sc.bevel_rim(big, pl, plr, (52, 54, 68, 200),
                     (150, 154, 172, 190), w=max(1, m(1.4)))
    _price_in_plate(big, m(CX), m(PL_CY), price, affordable)

    # ── BUY + CANCEL action pair ──────────────────────────────────────────────
    buy_r = pygame.Rect(m(BUY_CX - BUY_W // 2), m(Y_ACT - BUY_H // 2),
                        m(BUY_W), m(BUY_H))
    can_r = pygame.Rect(m(CAN_CX - CAN_W // 2), m(Y_ACT - CAN_H // 2),
                        m(CAN_W), m(CAN_H))
    brad = m(8)

    if affordable:
        sc._dark_chip_body(big, buy_r, brad,
                           [(0.0, (96, 72, 28)), (1.0, (60, 44, 14))],
                           (36, 26, 8), (255, 226, 150), gloss=48, gamma=1.06)
        sc.top_sheen(big, buy_r, brad, m(13), peak=54)
        sc.bevel_rim(big, buy_r, brad, (40, 28, 8, 220),
                     (255, 232, 162, 220), w=max(1, m(1.5)))
        sc.plain_text(big, "BUY", sc.font(13), buy_r.center, (252, 244, 224),
                      shadow_a=130, weight=m(0.9), keyline=(40, 26, 6), kw=m(0.9))
    else:
        sc._dark_chip_body(big, buy_r, brad,
                           [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))],
                           (20, 18, 26), (78, 76, 92), gloss=10, gamma=1.04)
        sc.bevel_rim(big, buy_r, brad, (34, 32, 44, 180),
                     (86, 84, 102, 150), w=max(1, m(1.4)))
        sc.plain_text(big, "BUY", sc.font(13),
                      (buy_r.centerx - m(9), buy_r.centery), (96, 100, 116),
                      shadow_a=0, weight=m(0.5))
        _padlock(big, buy_r.centerx + m(15), buy_r.centery)

    # CANCEL is always available — flat dark chip, unchanged across states.
    sc._dark_chip_body(big, can_r, brad,
                       [(0.0, (18, 16, 26)), (1.0, (12, 10, 20))],
                       (30, 28, 42), (70, 66, 82), gloss=14, gamma=1.04)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, (150, 144, 166),
                  shadow_a=0, weight=m(0.6))

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(302)),
                      (150, 166, 190), shadow_a=0)

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

    # Two hit rects in logical/screen space, both a full 32px tall.
    self.confirm_yes_rect = pygame.Rect(
        px + BUY_CX - BUY_W // 2, py + Y_ACT - HIT_H // 2, BUY_W, HIT_H)
    self.confirm_no_rect = pygame.Rect(
        px + CAN_CX - CAN_W // 2, py + Y_ACT - HIT_H // 2, CAN_W, HIT_H)
    if not affordable:
        self.confirm_yes_rect = None


store_mod.StoreScene._draw_confirm = _patched_draw_confirm


def render_state(affordable):
    sd.load()
    sd.balance = (lambda: 999_999) if affordable else (lambda: 0)
    sc.clear_cache()
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


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, "RGBA")


afford_img = render_state(True)
unafford_img = render_state(False)

SHEET_W, SHEET_H = 460, 400
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))
sheet.blit(_pil_to_surf(afford_img), (0, 30))
sheet.blit(_pil_to_surf(unafford_img), (220, 30))

hdr = store_mod._font(16, True).render("price-plate · ENAMEL PLAQUE + BUY/CANCEL",
                                       True, (220, 190, 100))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (200, 185, 140))
lu = lbl_font.render("UNAFFORDABLE", True, (200, 185, 140))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(320, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v2", "price-plate", "round_1.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
