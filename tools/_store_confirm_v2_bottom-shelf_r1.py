"""Round-1 render for the bottom-shelf buy-confirm concept (v2).

Headless. Monkey-patches StoreScene._draw_confirm with the bottom-shelf
layout, renders the popup in both affordability states, and tiles them into
a labeled AFFORDABLE|UNAFFORDABLE review sheet under docs/. Ships nothing —
this is an exploration image, kept out of game/assets/ and the WASM bundle.
"""
import os
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()
pygame.display.set_mode((8, 8))

from game.config import W, H
from game import store, store_cards, store_catalog, store_data
from game.surprise_box_variants import _draw_qmark
from game.store import _draw_qmark as _store_qmark  # same symbol, keep import parity

store_data.load()

SID = "skin_mummy"


# ── the bottom-shelf _draw_confirm ────────────────────────────────────────────
def _draw_confirm_bottom_shelf(self, surf) -> None:
    """Buy-confirm with a raised shelf panel across the card base: price row on
    the lit lip, a warm-gold BUY as the primary action, muted CANCEL below.
    Unaffordable cools the shelf, greys the price, and recesses BUY behind a
    padlock + NOT ENOUGH read so the inert state survives colour-blindness."""
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
    affordable = bool(getattr(self, "_force_affordable", True))

    POP_W, POP_H = 200, 340
    CX = POP_W // 2
    SS = store_cards.SS
    m = store_cards.m

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120

    # Shelf + interactive metrics (logical px).
    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 8, 235, 184, 87
    Y_PRICE = 244
    Y_BUY, BUY_W, BUY_H = 273, 136, 30
    Y_CANCEL, CANCEL_W, CANCEL_H = 308, 80, 22

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body (KEEP) ──────────────────────────────────────────────────────
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

    # ── corner gem pair (KEEP) ────────────────────────────────────────────────
    store_cards.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])
    store_cards.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R),
                          pal["gem"], pal["deep"])

    # ── name + rarity banner (KEEP) ───────────────────────────────────────────
    store_cards.plain_text(big, name, store_cards.font(NAME_FS),
                           (m(CX), m(Y_NAME)), (250, 248, 240),
                           shadow_a=160, weight=m(0.9),
                           keyline=(6, 6, 16), kw=m(1.0))
    store_cards._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ══ RAISED SHELF (replaces price chip / status / cancel block) ════════════
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)

    if affordable:
        shelf_stops = [(0.0, (38, 40, 82)), (1.0, (20, 22, 50))]
    else:
        # Cooler, bluer-grey shelf reads as "asleep" without touching the frame.
        shelf_stops = [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))]

    # Flat top (the lit front lip), rounded bottom that follows the card corners.
    shelf = store_cards.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255)
    shelf = shelf.copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    # Subtle top sheen so the shelf face catches a little room light.
    store_cards.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    # 1px lit top edge — the shelf casting light forward onto its own face.
    lip = (90, 88, 120) if affordable else (58, 60, 82)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    # Seat it: a soft inner shadow where the shelf meets the card, above the lip.
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # ── price row on the lip ──────────────────────────────────────────────────
    price_txt = f"{price:,}"
    f_price = store_cards.font(10)
    tw = f_price.size(price_txt)[0]
    coin_r = m(8)
    coin_d = coin_r * 2
    gap = m(4)
    total = coin_d + gap + tw
    start_x = m(CX) - total // 2
    coin_cx = start_x + coin_r
    num_cx = start_x + coin_d + gap + tw // 2
    py_price = m(Y_PRICE)

    # Dark backing plate so the numeral keeps maximum value-contrast on the
    # mid-value indigo shelf (and on the cooler unaffordable tint alike).
    plate = pygame.Rect(0, 0, tw + m(10), f_price.get_height() + m(2))
    plate.center = (num_cx, py_price)
    plate_surf = pygame.Surface(plate.size, pygame.SRCALPHA)
    plate_surf.fill((8, 8, 20, 150))
    pygame.draw.rect(plate_surf, (8, 8, 20, 150), plate_surf.get_rect(),
                     border_radius=m(5))
    plate_surf.blit(pygame.Surface(plate.size, pygame.SRCALPHA), (0, 0))
    big.blit(plate_surf, plate.topleft)

    if affordable:
        store_cards.coin_glyph(big, coin_cx, py_price, coin_r)
        num_col = (248, 238, 210)
    else:
        # Grey the coin: draw it, then knock it back to slate.
        cs = pygame.Surface((coin_d + m(2), coin_d + m(2)), pygame.SRCALPHA)
        store_cards.coin_glyph(cs, cs.get_width() // 2, cs.get_height() // 2, coin_r)
        grey = pygame.Surface(cs.get_size(), pygame.SRCALPHA)
        grey.fill((70, 74, 92, 210))
        cs.blit(grey, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        big.blit(cs, cs.get_rect(center=(coin_cx, py_price)))
        num_col = (110, 115, 130)

    store_cards.plain_text(big, price_txt, f_price, (num_cx, py_price),
                           num_col, shadow_a=0, weight=m(0.7),
                           keyline=(6, 6, 16), kw=m(0.9))

    # ── BUY button ────────────────────────────────────────────────────────────
    buy = pygame.Rect(0, 0, m(BUY_W), m(BUY_H))
    buy.center = (m(CX), m(Y_BUY))
    buy_rad = buy.h // 2

    if affordable:
        store_cards._dark_chip_body(
            big, buy, buy_rad,
            [(0.0, (65, 52, 20)), (1.0, (38, 30, 10))],
            store_cards.CARD_RING_DEEP, store_cards.CARD_RING_BRIGHT,
            gloss=16, gamma=1.05)
        store_cards.top_sheen(big, buy, buy_rad, m(12), peak=40)
        store_cards.plain_text(big, "BUY", store_cards.font(14), buy.center,
                               (250, 240, 214), shadow_a=150, weight=m(1.0),
                               keyline=(24, 16, 4), kw=m(1.0))
    else:
        # Recessed enamel: desaturated fill + INVERTED bevel (dark lip on top,
        # faint light on the bottom) so it reads pressed-in / dead.
        big.blit(store_cards.vgrad_stops(
            buy.w, buy.h, buy_rad,
            [(0.0, (22, 22, 28)), (1.0, (16, 16, 22))], 255), buy.topleft)
        inv = pygame.Surface(buy.size, pygame.SRCALPHA)
        for yy in range(buy.h):
            a = int(120 * (1 - yy / buy.h) ** 1.6)          # shadow strongest at top
            pygame.draw.line(inv, (0, 0, 0, a), (0, yy), (buy.w, yy))
        for yy in range(buy.h):
            a = int(60 * (yy / buy.h) ** 2.4)               # faint light at bottom
            pygame.draw.line(inv, (150, 152, 172, a), (0, yy), (buy.w, yy))
        inv_mask = pygame.Surface(buy.size, pygame.SRCALPHA)
        pygame.draw.rect(inv_mask, (255, 255, 255, 255), inv_mask.get_rect(),
                         border_radius=buy_rad)
        inv.blit(inv_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        big.blit(inv, buy.topleft)
        pygame.draw.rect(big, (10, 10, 14), buy, width=max(1, m(1.4)),
                         border_radius=buy_rad)

        # Padlock + BUY, both slate, carry the inert read without relying on the
        # bevel direction alone (colour-blind safe).
        slate = (150, 166, 190)
        lab = store_cards.font(13)
        lw = lab.size("BUY")[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.9)
        inner_gap = m(4)
        grp = lock_w + inner_gap + lw
        gx = m(CX) - grp // 2
        _padlock(big, gx + lock_w // 2, buy.centery, lock_h, slate)
        store_cards.plain_text(big, "BUY", lab,
                               (gx + lock_w + inner_gap + lw // 2, buy.centery),
                               slate, shadow_a=0, weight=m(0.6))
        store_cards.plain_text(big, "NOT ENOUGH COINS", store_cards.font(8),
                               (m(CX), m(Y_BUY) + m(BUY_H) // 2 + m(6)),
                               (150, 166, 190), shadow_a=0)

    # ── CANCEL (muted, tappable) ──────────────────────────────────────────────
    can = pygame.Rect(0, 0, m(CANCEL_W), m(CANCEL_H))
    can.center = (m(CX), m(Y_CANCEL))
    can_flat = pygame.Surface(can.size, pygame.SRCALPHA)
    can_flat.fill((0, 0, 0, 0))
    pygame.draw.rect(can_flat, (16, 16, 26, 120), can_flat.get_rect(),
                     border_radius=can.h // 2)
    big.blit(can_flat, can.topleft)
    store_cards.plain_text(big, "CANCEL", store_cards.font(10), can.center,
                           (130, 124, 148), shadow_a=0)

    # ── overhanging disc + halo (KEEP, crowns the card) ───────────────────────
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"],
                            peak=95, layers=24)
    store_cards._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"],
                            peak=70, layers=12)
    store_cards.cabochon(big, cx_ss, cy_ss, r_ss,
                         store_cards.CABO_LO, store_cards.CABO_HI,
                         ring=pal["gem"], ring_a=50)
    if secret:
        _store_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17),
                     store.UI_CREAM, store.NEAR_BLACK, thick=5)
    else:
        store_cards.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    store_cards.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    # ── composite ─────────────────────────────────────────────────────────────
    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px = (W - POP_W) // 2
    py = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))

    self.confirm_no_rect = pygame.Rect(px + CX - 40, py + 300, 80, 32)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + CX - BUY_W // 2, py + Y_BUY - BUY_H // 2, BUY_W, BUY_H)


def _padlock(surf, cx, cy, h, color):
    """Tiny procedural padlock — rounded body + shackle arc — for the inert BUY."""
    bw = int(h * 0.92)
    bh = int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc, math.radians(15), math.radians(165),
                    max(1, int(h * 0.17)))
    # keyhole punched dark so the lock reads at thumbnail size
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.20)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (20, 20, 30), kh, border_radius=1)


# ── render both states ────────────────────────────────────────────────────────
store.StoreScene._draw_confirm = _draw_confirm_bottom_shelf


def _render(affordable):
    scene = store.StoreScene()
    scene._confirm = SID
    scene._force_affordable = affordable
    surf = pygame.Surface((W, H), pygame.SRCALPHA)
    scene._draw_confirm(surf)
    r = scene._confirm_panel
    crop = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
    crop.blit(surf, (0, 0), pygame.Rect(r.x, r.y, r.w, r.h))
    return crop


aff = _render(True)
una = _render(False)

# ── review sheet ──────────────────────────────────────────────────────────────
SCALE = 2
pw, ph = aff.get_width() * SCALE, aff.get_height() * SCALE
aff = pygame.transform.smoothscale(aff, (pw, ph))
una = pygame.transform.smoothscale(una, (pw, ph))

PAD, GAP, TITLE_H, LABEL_H = 40, 44, 76, 44
sheet_w = PAD * 2 + pw * 2 + GAP
sheet_h = TITLE_H + ph + LABEL_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
for y in range(sheet_h):
    t = y / sheet_h
    c = (int(14 + 8 * t), int(15 + 8 * t), int(30 + 14 * t))
    pygame.draw.line(sheet, c, (0, y), (sheet_w, y))

tfont = store_cards._font(30, True)
lfont = store_cards._font(22, True)


def _center_text(fnt, txt, cx, cy, col):
    img = fnt.render(txt, True, col)
    sheet.blit(img, img.get_rect(center=(cx, cy)))


_center_text(tfont, "BUY-CONFIRM v2  —  BOTTOM-SHELF  —  round 1",
             sheet_w // 2, TITLE_H // 2, (236, 202, 116))

x0 = PAD
x1 = PAD + pw + GAP
ytop = TITLE_H
sheet.blit(aff, (x0, ytop))
sheet.blit(una, (x1, ytop))
_center_text(lfont, "AFFORDABLE", x0 + pw // 2, ytop + ph + LABEL_H // 2,
             (214, 220, 236))
_center_text(lfont, "UNAFFORDABLE", x1 + pw // 2, ytop + ph + LABEL_H // 2,
             (214, 220, 236))

out_dir = "docs/store_confirm_popup_v2/bottom-shelf"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "round_1.png")
pygame.image.save(sheet, out)

# ── sanity samples (printed, never viewed) ────────────────────────────────────
print("saved", out, sheet.get_size())
# Shelf face on the affordable crop (mid-height of shelf, off-center).
sx = x0 + int(pw * 0.30)
sy = ytop + int(ph * (270 / 340))
print("shelf face (affordable):", sheet.get_at((sx, sy)))
# BUY button centre (affordable) — expect warm gold.
bx = x0 + pw // 2
by = ytop + int(ph * (273 / 340))
print("BUY centre (affordable):", sheet.get_at((bx, by)))
# BUY button centre (unaffordable) — expect dark recessed.
print("BUY centre (unaffordable):", sheet.get_at((x1 + pw // 2, by)))
