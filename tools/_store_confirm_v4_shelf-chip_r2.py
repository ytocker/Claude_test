#!/usr/bin/env python3
"""
shelf-chip  ·  store buy-confirmation popup v4  ·  round 2

Concept: the v2 bottom-shelf tray (an inset shelf zone with its own bg colour
+ seat/lip/micro-wall architecture) carrying a single cream coin CHIP as the
price display, over TWO completely identical action buttons — BUY and CANCEL
share every property (size, radius, fill, bevel, label style) and differ only
by their text string, so neither is visually privileged in the affordable
state. Unaffordable cools the chip to slate, locks BUY behind a padlock, and
leaves CANCEL at full indigo since it is always actionable.

R2 changes vs R1:
- CHIP_CY lowered to 258 so the full chip clears the shelf lip and sits inside the tray.
- BTN_CY moved to 302 to re-centre the chip→button group inside the shelf vertically.
- Button top-stop raised to (84,78,126) so buttons lift clearly off the (28,30,62) tray bed.
- Shelf gradient deepened to (28,30,62)→(14,16,40) for a crisply recessed material identity.
- Shelf lip brightened to (115,106,140) to stay legible against the deeper tray.
- Button width trimmed 80→76 to give ~7px breathing room from the micro-walls.
"""
import os
import sys
import math

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

m = sc.m


def _padlock(surf, cx, cy, h, color):
    """Tiny procedural padlock — rounded body + shackle arc + punched keyhole —
    so the locked BUY reads as inert without relying on hue alone."""
    bw = int(h * 0.92)
    bh = int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc, math.radians(15), math.radians(165),
                    max(1, int(h * 0.17)))
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.22)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (24, 22, 34), kh, border_radius=1)


def _draw_button(big, rect, rad, label, locked=False):
    """One identical button body for BOTH BUY and CANCEL — the ONLY parameter
    that changes between the two in the affordable state is `label`. `locked`
    is used solely for the unaffordable BUY, which dims to slate + a padlock."""
    if locked:
        stops = [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))]
        lab_col = (90, 88, 108)
        sheen = 12
    else:
        # Top stop lifted so the button face clearly separates from the
        # (28,30,62) shelf tray bed — identical for BUY and CANCEL.
        stops = [(0.0, (84, 78, 126)), (1.0, (50, 46, 82))]
        lab_col = (220, 210, 240)
        sheen = 28

    sc.drop_shadow(big, rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad, stops, 255), rect.topleft)
    sc.top_sheen(big, rect, rad, m(12), peak=sheen)
    sc.bevel_rim(big, rect, rad, (20, 18, 36, 180), (130, 124, 160, 200),
                 w=max(1, m(1.2)))

    lab_font = sc.font(13)
    if locked:
        # Padlock sits just left of the label as a colour-blind-safe inert cue.
        lw = lab_font.size(label)[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.92)
        inner = m(4)
        grp = lock_w + inner + lw
        gx = rect.centerx - grp // 2
        _padlock(big, gx + lock_w // 2, rect.centery, lock_h, lab_col)
        sc.plain_text(big, label, lab_font,
                      (gx + lock_w + inner + lw // 2, rect.centery),
                      lab_col, shadow_a=0, weight=m(0.6))
    else:
        sc.plain_text(big, label, lab_font, rect.center, lab_col,
                      shadow_a=110, weight=m(0.8), keyline=(18, 16, 32), kw=m(0.9))


def _coin_chip(big, cx, cy, price, affordable):
    """Cream coin plaque centred in the shelf: a matte ivory pill with coin +
    numeral. It reads as a DISPLAY element (no gloss, dark espresso numeral on
    ivory ~10:1) so it never competes with the two buttons for a tap."""
    CHIP_W, CHIP_H, CHIP_RAD = 120, 36, 8
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
        face_stops = [(0.0, (235, 220, 175)), (1.0, (205, 190, 145))]
        border = (120, 74, 14)
    else:
        face_stops = [(0.0, (60, 60, 74)), (1.0, (44, 44, 58))]
        border = (78, 80, 96)
    # Matte fill — deliberately NO top_sheen so it never reads as a button.
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)
    pygame.draw.rect(big, border, chip, width=max(1, m(1)), border_radius=crad)

    txt = f"{price:,}"
    num_font = sc.font(22)
    coin_r = m(14)
    coin_d = coin_r * 2
    gap = m(4)
    num_w = num_font.size(txt)[0]
    total = coin_d + gap + num_w
    left = cx - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2
    # Baseline: nudge the numeral down so its cap-height rests on the coin's
    # lower edge rather than floating off its optical centre.
    num_cy = cy + m(3)

    if affordable:
        sc.coin_glyph(big, coin_cx, cy, coin_r)
        num_col = (52, 28, 4)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        pygame.draw.circle(big, (128, 132, 146), (coin_cx, cy), coin_r - m(3),
                           width=max(1, m(1)))
        num_col = (110, 115, 130)
    sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                  shadow_a=0, weight=m(0.8))


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

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER, BANNER_W = 175, 120

    # ── shelf + chip + button metrics (logical) ───────────────────────────────
    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
    # Chip lowered 10px so entire chip body sits visibly below the shelf lip.
    CHIP_CY = 258
    # Button width trimmed to give ~7px breathing room from micro-walls.
    BTN_W, BTN_H, BTN_RAD = 76, 30, 9
    # Button row nudged down to re-centre the chip→button group inside the shelf.
    BTN_CY = 302
    BTN_GAP = 8
    BUY_CX = CX - (BTN_W + BTN_GAP) // 2
    CAN_CX = CX + (BTN_W + BTN_GAP) // 2

    big = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)

    # ── card body (KEEP) ──────────────────────────────────────────────────────
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

    # ── corner gem pair + name + banner (KEEP) ────────────────────────────────
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.plain_text(big, name, sc.font(NAME_FS),
                  (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ══ INSET SHELF (from v2 bottom-shelf R2) ═════════════════════════════════
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)

    if affordable:
        # Deeper/cooler than R1 so the tray reads as a clearly recessed zone,
        # darker than the card body above it.
        shelf_stops = [(0.0, (28, 30, 62)), (1.0, (14, 16, 40))]
    else:
        shelf_stops = [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))]

    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    # Lip brightened to stay legible against the deeper (28,30,62) tray top.
    lip = (115, 106, 140) if affordable else (62, 62, 86)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    # Seat shadow where the shelf meets the card body above.
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Micro-walls: lit-left / shadowed-right strips in the inset gap for depth.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (xx / max(1, wall_w - 1)))
            pygame.draw.line(lwall, (130, 120, 165, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    # ── cream coin chip (centrepiece) ─────────────────────────────────────────
    _coin_chip(big, m(CX), m(CHIP_CY), price, affordable)

    # ── identical BUY + CANCEL pair ───────────────────────────────────────────
    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)

    _draw_button(big, buy, brad, "BUY", locked=not affordable)
    _draw_button(big, can, brad, "CANCEL", locked=False)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(317)),
                      (150, 166, 190), shadow_a=0)

    # ── overhanging disc + halo (KEEP, drawn LAST) ────────────────────────────
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
        px + CAN_CX - BTN_W // 2, py + BTN_CY - BTN_H // 2, BTN_W, BTN_H)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + BUY_CX - BTN_W // 2, py + BTN_CY - BTN_H // 2, BTN_W, BTN_H)


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
    # non-SRCALPHA surface: read as RGB to avoid a garbage alpha channel
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
    "shelf-chip v4 R2 · SEATED CHIP + DEEPER TRAY + LIFTED BUTTONS", True, (226, 208, 150))
sheet.blit(hdr, hdr.get_rect(midtop=(SHEET_W // 2, 8)))

lbl_font = store_mod._font(12, True)
la = lbl_font.render("AFFORDABLE", True, (204, 190, 150))
lu = lbl_font.render("UNAFFORDABLE", True, (204, 190, 150))
sheet.blit(la, la.get_rect(midtop=(100, 378)))
sheet.blit(lu, lu.get_rect(midtop=(330, 378)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v4", "shelf-chip", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
print("saved", OUT, sheet.get_size())
