#!/usr/bin/env python3
"""
coin-platform  ·  store buy-confirmation popup v3  ·  round 1

Concept: the price sits on a raised cream PLINTH — a matte warm-ivory
pedestal slab that reads as a stone surface the gold coin physically rests
on (contact shadows sell the "resting on" weight). The two action pills
below are the ONLY glossy bevelled objects, so control vs content is
unambiguous by finish: matte plinth = information, glossy pills = buttons.
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


def _plinth_top_edge(big, pl, plr):
    """A crisp 1px bright line hugging the top inner arc so the ivory slab
    reads as a lifted pedestal catching the top-left light, not a flat inlay."""
    y = pl.y + max(1, sc.m(1))
    pygame.draw.line(big, (252, 244, 222),
                     (pl.x + plr, y), (pl.right - plr, y), max(1, sc.m(1)))


def _contact_shadow_ellipse(big, cx, cy, rx, ry, alpha):
    """A soft blurred dark ellipse footprint — sells an object sitting ON the
    plinth face rather than floating above it. Layered for a feathered edge."""
    layers = 5
    for i in range(layers, 0, -1):
        a = int(alpha * (i / layers) ** 1.8 / layers * 2.2)
        if a <= 0:
            continue
        ex = int(rx * i / layers) + rx
        ey = int(ry * i / layers) + ry
        s = pygame.Surface((ex * 2 + 2, ey * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0, 0, 0, a), (0, 0, ex * 2, ey * 2))
        big.blit(s, (cx - ex, cy - ey))


def _padlock(big, cx, cy):
    """Inert-state lock glyph beside a dimmed BUY label with a dark keyline so
    the silhouette reads unambiguously as 'locked' at 1x screen size."""
    pk_w, pk_h = sc.m(15), sc.m(13)
    body_r = pygame.Rect(cx - pk_w // 2, cy - pk_h // 2 + sc.m(2),
                         pk_w, pk_h - sc.m(3))
    pygame.draw.rect(big, (24, 24, 34), body_r.inflate(sc.m(2), sc.m(2)),
                     border_radius=sc.m(4))
    pygame.draw.rect(big, (108, 112, 130, 230), body_r, border_radius=sc.m(3))
    pygame.draw.rect(big, (56, 58, 74, 255), body_r, width=max(1, sc.m(1)),
                     border_radius=sc.m(3))
    sh_r = pk_w // 2 - sc.m(1)
    arc = pygame.Rect(cx - sh_r, cy - pk_h // 2 - sh_r + sc.m(2), sh_r * 2, sh_r * 2)
    pygame.draw.arc(big, (24, 24, 34), arc.inflate(sc.m(2), sc.m(2)),
                    0, 3.14159, max(2, sc.m(3)))
    pygame.draw.arc(big, (108, 112, 130, 220), arc, 0, 3.14159, max(2, sc.m(2.5)))
    pygame.draw.circle(big, (50, 52, 66, 255), (cx, cy + sc.m(1)), max(2, sc.m(2.0)))


def _price_on_plinth(big, cx_d, cy_d, price, affordable):
    """Coin glyph + numeral centred together on the plinth face, the coin
    grounded by its own small contact shadow."""
    txt = f"{price:,}"
    coin_r = sc.m(14)
    coin_d = coin_r * 2
    gap = sc.m(6)
    num_font = sc.font(22)
    num_w = num_font.render(txt, True, (255, 255, 255)).get_width()
    total = coin_d + gap + num_w
    left = cx_d - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2

    if affordable:
        # small footprint shadow so the coin reads as resting on the cream face
        _contact_shadow_ellipse(big, coin_cx, cy_d + sc.m(1),
                                int(coin_r * 0.9), int(coin_r * 0.42), 60)
        sc.coin_glyph(big, coin_cx, cy_d, coin_r, rim=sc.GOLD_A_COIN_RIM)
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (248, 238, 210),
                      shadow_a=140, weight=sc.m(1.0),
                      keyline=(38, 28, 8), kw=sc.m(1.1))
    else:
        _contact_shadow_ellipse(big, coin_cx, cy_d + sc.m(1),
                                int(coin_r * 0.9), int(coin_r * 0.42), 45)
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy_d), coin_r)
        pygame.draw.circle(big, (100, 102, 116), (coin_cx, cy_d), coin_r,
                           width=max(1, sc.m(1)))
        pygame.draw.circle(big, (122, 126, 140), (coin_cx, cy_d),
                           coin_r - sc.m(3), width=max(1, sc.m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (110, 115, 130),
                      shadow_a=0, weight=sc.m(0.7),
                      keyline=(22, 22, 30), kw=sc.m(1.0))


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
    m = sc.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120

    # ── coin-platform concept metrics (logical) ───────────────────────────────
    PL_W, PL_H, PL_TOP, PL_RAD = 134, 44, 198, 8
    PL_CY = PL_TOP + PL_H // 2
    BTN_W, BTN_H, BTN_RAD = 80, 36, 9
    PAIR_GAP = 8
    Y_ACT = 280                       # btn_top 262 / btn_bot 298
    HIT_H = 36
    PAIR_W = BTN_W + PAIR_GAP + BTN_W
    PAIR_L = CX - PAIR_W // 2
    BUY_CX = PAIR_L + BTN_W // 2
    CAN_CX = PAIR_L + BTN_W + PAIR_GAP + BTN_W // 2

    big = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)

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

    # ── name ──────────────────────────────────────────────────────────────────
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # ── rarity banner ─────────────────────────────────────────────────────────
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ── raised cream plinth (matte, no press sheen) ───────────────────────────
    pl = pygame.Rect(m(CX - PL_W // 2), m(PL_TOP), m(PL_W), m(PL_H))
    plr = m(PL_RAD)
    sc.drop_shadow(big, pl, plr, blur=m(3), alpha=100, dy=m(2))
    if affordable:
        face = sc.vgrad_stops(pl.w, pl.h, plr,
                              [(0.0, (235, 220, 175)), (1.0, (205, 190, 145))],
                              255, gamma=1.02)
        big.blit(face, pl.topleft)
        _plinth_top_edge(big, pl, plr)
        pygame.draw.rect(big, (150, 132, 92), pl, width=max(1, m(1)),
                         border_radius=plr)
    else:
        face = sc.vgrad_stops(pl.w, pl.h, plr,
                              [(0.0, (52, 52, 64)), (1.0, (34, 34, 46))],
                              255, gamma=1.02)
        big.blit(face, pl.topleft)
        y = pl.y + max(1, m(1))
        pygame.draw.line(big, (86, 88, 104),
                         (pl.x + plr, y), (pl.right - plr, y), max(1, m(1)))
        pygame.draw.rect(big, (20, 20, 30), pl, width=max(1, m(1)),
                         border_radius=plr)
    _price_on_plinth(big, m(CX), m(PL_CY), price, affordable)

    # ── BUY + CANCEL action pair (glossy bevelled controls) ───────────────────
    buy_r = pygame.Rect(m(BUY_CX - BTN_W // 2), m(Y_ACT - BTN_H // 2),
                        m(BTN_W), m(BTN_H))
    can_r = pygame.Rect(m(CAN_CX - BTN_W // 2), m(Y_ACT - BTN_H // 2),
                        m(BTN_W), m(BTN_H))
    brad = m(BTN_RAD)

    if affordable:
        sc.drop_shadow(big, buy_r, brad, blur=m(4), alpha=115, dy=m(2))
        big.blit(sc.vgrad_stops(buy_r.w, buy_r.h, brad, sc.GOLD_A_STOPS,
                                255, gamma=sc.GOLD_A_GAMMA), buy_r.topleft)
        sc.top_sheen(big, buy_r, brad, m(16), peak=60)
        sc.bevel_rim(big, buy_r, brad, (86, 50, 8),
                     (255, 240, 190, 235), w=max(1, m(1.6)))
        sc.plain_text(big, "BUY", sc.font(13), buy_r.center, (52, 28, 4),
                      shadow_a=0, weight=m(1.0),
                      keyline=(255, 236, 176), kw=m(0.9))
    else:
        sc.drop_shadow(big, buy_r, brad, blur=m(4), alpha=100, dy=m(2))
        big.blit(sc.vgrad_stops(buy_r.w, buy_r.h, brad,
                                [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))],
                                255, gamma=1.04), buy_r.topleft)
        sc.top_sheen(big, buy_r, brad, m(14), peak=18)
        sc.bevel_rim(big, buy_r, brad, (34, 32, 44),
                     (86, 84, 102, 170), w=max(1, m(1.4)))
        sc.plain_text(big, "BUY", sc.font(13),
                      (buy_r.centerx - m(11), buy_r.centery), (100, 104, 120),
                      shadow_a=0, weight=m(0.6))
        _padlock(big, buy_r.centerx + m(16), buy_r.centery)

    # CANCEL — matched slate pill, always available
    sc.drop_shadow(big, can_r, brad, blur=m(4), alpha=110, dy=m(2))
    big.blit(sc.vgrad_stops(can_r.w, can_r.h, brad,
                            [(0.0, (30, 28, 44)), (1.0, (20, 18, 32))],
                            255, gamma=1.04), can_r.topleft)
    sc.top_sheen(big, can_r, brad, m(14), peak=28)
    sc.bevel_rim(big, can_r, brad, (44, 42, 58),
                 (110, 106, 128, 200), w=max(1, m(1.4)))
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, (130, 124, 148),
                  shadow_a=0, weight=m(0.6))

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(308)),
                      (150, 166, 190), shadow_a=0)

    # ── overhanging disc + spotlight halo (drawn last, over everything) ───────
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

    self.confirm_yes_rect = pygame.Rect(
        px + BUY_CX - BTN_W // 2, py + Y_ACT - HIT_H // 2, BTN_W, HIT_H)
    self.confirm_no_rect = pygame.Rect(
        px + CAN_CX - BTN_W // 2, py + Y_ACT - HIT_H // 2, BTN_W, HIT_H)
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
    raw = pygame.image.tostring(screen, "RGB")
    full = Image.frombytes("RGB", (W, H), raw)
    return full.crop((px, py, px + POP_W, py + POP_H))


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


afford_img = render_state(True)
unafford_img = render_state(False)

SHEET_W, SHEET_H = 460, 400
sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((8, 8, 20))
sheet.blit(_pil_to_surf(afford_img), (0, 30))
sheet.blit(_pil_to_surf(unafford_img), (230, 30))

hdr = store_mod._font(16, True).render(
    "coin-platform R1 · MATTE CREAM PLINTH + GLOSSY PILLS",
    True, (232, 214, 160))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (200, 185, 140))
lu = lbl_font.render("UNAFFORDABLE", True, (200, 185, 140))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(330, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v3", "coin-platform", "round_1.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
