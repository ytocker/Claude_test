#!/usr/bin/env python3
"""
segmented-bar  ·  store buy-confirmation popup v3  ·  round 1

Concept: price display and buttons are ONE machined bar. A single tall
rounded-rect (w=168, r=10) is divided by chamfered bevel-channel grooves
into a top PRICE row and a bottom BUY|CANCEL button row. Every segment
shares the same outer rounded corners, so it reads as one milled control
face rather than stacked shapes — the grooves are the only thing that
separate the cells.
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


def _hchannel(big, x0, x1, y_top, h):
    """Horizontal chamfered groove: dark valley with a bright top lip catching
    the light and a dark bottom shadow — sells a recessed machined seam so the
    price row reads milled into the same slab as the buttons, not stacked on."""
    lw = max(1, sc.m(1))
    pygame.draw.rect(big, (8, 8, 18), (x0, y_top, x1 - x0, h))
    pygame.draw.line(big, (50, 48, 68), (x0, y_top), (x1, y_top), lw)
    pygame.draw.line(big, (4, 4, 12), (x0, y_top + h - lw), (x1, y_top + h - lw), lw)


def _vchannel(big, x_center, y0, y1, valley_w):
    """Vertical chamfered groove splitting BUY|CANCEL: bright left lip, dark
    right shadow — matches the horizontal seam so the two grooves meet as one
    milled cross, keeping the bar a single object."""
    lw = max(1, sc.m(1))
    vx = x_center - valley_w // 2
    pygame.draw.rect(big, (8, 8, 18), (vx, y0, valley_w, y1 - y0))
    pygame.draw.line(big, (50, 48, 68), (vx, y0), (vx, y1), lw)
    pygame.draw.line(big, (4, 4, 12), (vx + valley_w - lw, y0),
                     (vx + valley_w - lw, y1), lw)


def _button_row(big, bar, bar_rad, btn_top_local, btn_h_local, split_x_local,
                left_stops, right_stops, left_sheen, right_sheen):
    """Paint the two button cells over the bottom of the bar while inheriting
    the bar's rounded bottom corners. Both cells are the SAME shape — only fill
    + sheen differ — so BUY and CANCEL read as siblings milled from one face."""
    layer = pygame.Surface(bar.size, pygame.SRCALPHA)
    lw = split_x_local
    rw = bar.w - split_x_local
    lgrad = sc.vgrad_stops(lw, btn_h_local, 0, left_stops, 255, gamma=1.05)
    rgrad = sc.vgrad_stops(rw, btn_h_local, 0, right_stops, 255, gamma=1.05)
    layer.blit(lgrad, (0, btn_top_local))
    layer.blit(rgrad, (split_x_local, btn_top_local))
    # press sheen at each cell's top edge (BUY glossy, CANCEL muted)
    if left_sheen:
        sc.top_sheen(layer, pygame.Rect(0, btn_top_local, lw, btn_h_local),
                     0, sc.m(12), peak=left_sheen)
    if right_sheen:
        sc.top_sheen(layer, pygame.Rect(split_x_local, btn_top_local, rw, btn_h_local),
                     0, sc.m(12), peak=right_sheen)
    # carve the shared rounded silhouette so bottom corners match the bar
    mask = pygame.Surface(bar.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bar.w, bar.h),
                     border_radius=bar_rad)
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(layer, bar.topleft)


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


def _price_in_segment(big, cx_d, cy_d, price, affordable):
    """Coin glyph + numeral centred in the top price segment."""
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
        sc.coin_glyph(big, coin_cx, cy_d, coin_r, rim=sc.GOLD_A_COIN_RIM)
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (248, 238, 210),
                      shadow_a=150, weight=sc.m(1.0),
                      keyline=(12, 10, 22), kw=sc.m(1.1))
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy_d), coin_r)
        pygame.draw.circle(big, (100, 102, 116), (coin_cx, cy_d), coin_r,
                           width=max(1, sc.m(1)))
        pygame.draw.circle(big, (122, 126, 140), (coin_cx, cy_d),
                           coin_r - sc.m(3), width=max(1, sc.m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, cy_d), (110, 115, 130),
                      shadow_a=0, weight=sc.m(0.7),
                      keyline=(12, 10, 22), kw=sc.m(1.0))


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

    # ── segmented-bar concept metrics (logical) ───────────────────────────────
    BAR_W, BAR_RAD = 168, 10
    BAR_X = CX - BAR_W // 2                       # 16
    BAR_TOP = 200
    PRICE_H = 40
    DIV_Y = BAR_TOP + PRICE_H                     # 240 · horizontal groove top
    BTN_TOP = 244                                 # button cells begin below groove
    BTN_H = 40
    BAR_BOT = BTN_TOP + BTN_H                     # 284
    BAR_H = BAR_BOT - BAR_TOP                     # 84
    PRICE_CY = BAR_TOP + PRICE_H // 2             # 220
    VCH_X = CX                                    # 100 · vertical groove centre
    BTN_CY = BTN_TOP + BTN_H // 2                 # 264
    HIT_H = BTN_H

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

    # ── the one machined bar ──────────────────────────────────────────────────
    bar = pygame.Rect(m(BAR_X), m(BAR_TOP), m(BAR_W), m(BAR_H))
    bar_rad = m(BAR_RAD)
    sc.drop_shadow(big, bar, bar_rad, blur=m(5), alpha=140, dy=m(3))

    # 1. price face over the WHOLE bar — its rounded corners become the shared
    #    silhouette for every segment below.
    if affordable:
        price_stops = [(0.0, (20, 18, 34)), (1.0, (30, 26, 44))]   # cool indigo
    else:
        price_stops = [(0.0, (32, 30, 44)), (1.0, (20, 18, 32))]   # cool grey
    big.blit(sc.vgrad_stops(bar.w, bar.h, bar_rad, price_stops, 255, gamma=1.03),
             bar.topleft)

    # 2. button cells over the bottom half, inheriting the bottom corners
    btn_top_local = m(BTN_TOP) - bar.y
    btn_h_local = m(BTN_H)
    split_local = m(VCH_X) - bar.x
    if affordable:
        buy_stops = sc.GOLD_A_STOPS
        buy_sheen = 58
    else:
        buy_stops = [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))]     # inert slate
        buy_sheen = 12
    can_stops = [(0.0, (30, 28, 44)), (1.0, (20, 18, 32))]
    _button_row(big, bar, bar_rad, btn_top_local, btn_h_local, split_local,
                buy_stops, can_stops, buy_sheen, 24)

    # 3. horizontal groove between price + buttons
    _hchannel(big, bar.x, bar.right, m(DIV_Y), m(BTN_TOP) - m(DIV_Y))
    # 4. vertical groove splitting BUY|CANCEL, meeting the horizontal seam
    _vchannel(big, m(VCH_X), m(DIV_Y), bar.bottom, max(2, m(3)))

    # 5. outer bevel rim — one dark keyline + one bright inner catch for the
    #    whole object, so all segments sit inside a single milled edge.
    pygame.draw.rect(big, (6, 6, 14), bar, width=max(1, m(1)), border_radius=bar_rad)
    sc.bevel_rim(big, bar, bar_rad, (10, 9, 20),
                 (58, 56, 80, 210), w=max(1, m(1.5)))

    # ── segment content ───────────────────────────────────────────────────────
    _price_in_segment(big, m(CX), m(PRICE_CY), price, affordable)

    if affordable:
        sc.plain_text(big, "BUY", sc.font(13),
                      (m(BAR_X) + split_local // 2, m(BTN_CY)), (52, 28, 4),
                      shadow_a=0, weight=m(1.0),
                      keyline=(255, 236, 176), kw=m(0.9))
    else:
        sc.plain_text(big, "BUY", sc.font(13),
                      (m(BAR_X) + split_local // 2 - m(9), m(BTN_CY)),
                      (100, 104, 120), shadow_a=0, weight=m(0.6))
        _padlock(big, m(BAR_X) + split_local // 2 + m(15), m(BTN_CY))

    can_cx = m(VCH_X) + (bar.right - m(VCH_X)) // 2
    sc.plain_text(big, "CANCEL", sc.font(11), (can_cx, m(BTN_CY)),
                  (130, 124, 148), shadow_a=0, weight=m(0.6))

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(295)),
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
        px + BAR_X, py + BTN_TOP, VCH_X - BAR_X, HIT_H)
    self.confirm_no_rect = pygame.Rect(
        px + VCH_X, py + BTN_TOP, (BAR_X + BAR_W) - VCH_X, HIT_H)
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
    "segmented-bar R1 · ONE MILLED BAR · GROOVE-SPLIT PRICE|BUY|CANCEL",
    True, (200, 196, 224))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (196, 192, 220))
lu = lbl_font.render("UNAFFORDABLE", True, (196, 192, 220))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(330, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v3", "segmented-bar", "round_1.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
