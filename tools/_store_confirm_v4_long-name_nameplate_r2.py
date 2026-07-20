#!/usr/bin/env python3
"""
nameplate  ·  store buy-confirmation popup v4  ·  long-name overflow  ·  round 2

Concept: the hero name sits on an inset ENGRAVED PLATE — a neutral indigo
deboss with a faint rim — so it always reads as a framed product label in a
display case. The plate auto-widens from a short-name minimum up to a 168px
hard cap; the name is scale-to-fit inside the plate's inner width, so a long
name is NEVER clipped, only shrunk to stay fully framed. The plate is a fixed
indigo (NOT tinted by the tier gem); the tier lozenge stays separate below.

Everything else is unchanged from shelf-chip R2 — this only swaps the flat
`plain_text` name for the nameplate.
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

# Filled by _patched_draw_confirm so the sheet footer can report the plate
# width the auto-widener chose for each panel's name.
_captured = {"plate_w": 0}


# ── shelf-chip helpers (unchanged from R2) ────────────────────────────────────

def _padlock(surf, cx, cy, h, color):
    bw, bh = int(h * 0.92), int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc,
                    math.radians(15), math.radians(165), max(1, int(h * 0.17)))
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.22)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (24, 22, 34), kh, border_radius=1)


def _draw_button(big, rect, rad, label, locked=False):
    if locked:
        stops = [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))]
        lab_col = (90, 88, 108)
        sheen = 12
    else:
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
                      shadow_a=110, weight=m(0.8),
                      keyline=(18, 16, 32), kw=m(0.9))


def _coin_chip(big, cx, cy, price, affordable):
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
    num_cy = cy + m(3)
    if affordable:
        sc.coin_glyph(big, coin_cx, cy, coin_r)
        num_col = (52, 28, 4)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        num_col = (110, 115, 130)
    sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                  shadow_a=0, weight=m(0.8))


# ── patched draw: shelf-chip R2 body with the nameplate swapped in ────────────

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
    Y_BANNER, BANNER_W = 188, 120

    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
    CHIP_CY = 258
    BTN_W, BTN_H, BTN_RAD = 76, 30, 9
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

    # ── corner gem pair (KEEP) ────────────────────────────────────────────────
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

    # ── nameplate ─────────────────────────────────────────────────────────────
    PLATE_H = 26        # logical px, tall enough to frame the name
    PLATE_RAD = 5       # corner radius
    PLATE_PAD_X = 10    # inner horizontal padding
    PLATE_MIN_W = 60    # minimum plate width (for very short names)
    MAX_NAME_W = 168    # hard cap

    # scale-to-fit inside plate so a long name is framed, never clipped
    safe_inner_w = m(MAX_NAME_W - PLATE_PAD_X * 2)
    name_font = sc.font(NAME_FS)
    sz = NAME_FS
    while sz > 9:
        name_font = sc.font(sz)
        glyph_w = sc._glyph_base(name, name_font, 0).get_width()
        if glyph_w <= safe_inner_w:
            break
        sz -= 0.5
    glyph_w = sc._glyph_base(name, name_font, 0).get_width()

    # plate auto-width: glyph + padding, clamped to [MIN, MAX]
    plate_logical_w = min(MAX_NAME_W, max(PLATE_MIN_W,
                          int(glyph_w / sc.SS) + PLATE_PAD_X * 2))
    _captured["plate_w"] = plate_logical_w
    plate_rect = pygame.Rect(0, 0, m(plate_logical_w), m(PLATE_H))
    plate_rect.center = (m(CX), m(Y_NAME))
    plate_rad = m(PLATE_RAD)

    # plate fill: neutral indigo, lifted ~+15 above the card body so the plate
    # registers on its surface (not just its bevel) even under the hero glow.
    # Card body is CARD_T≈(28,30,70); this sits clearly above it, still darker
    # than the tier gems, and stays fixed (NOT tier-tinted).
    plate_stops = [(0.0, (44, 42, 72)), (1.0, (30, 28, 56))]
    plate_surf = sc.vgrad_stops(plate_rect.w, plate_rect.h, plate_rad,
                                plate_stops, 255)

    # deboss: symmetric engrave — a dark top groove-shadow as assertive as the
    # bright bottom lip. Lines are 2px in the SS=2 plate surface so each reads
    # as a crisp ~1px edge at ship scale (R1's 1px lines fell sub-pixel).
    # Principle: top ~50% darker than plate fill, bottom ~50% brighter.
    pygame.draw.line(plate_surf, (12, 10, 24),
                     (plate_rad, 0), (plate_rect.w - plate_rad, 0), 2)
    pygame.draw.line(plate_surf, (12, 10, 24),
                     (plate_rad, 1), (plate_rect.w - plate_rad, 1), 1)
    pygame.draw.line(plate_surf, (72, 68, 108),
                     (plate_rad, plate_rect.h - 2),
                     (plate_rect.w - plate_rad, plate_rect.h - 2), 2)

    # faint outer rim
    sc.bevel_rim(plate_surf, plate_surf.get_rect(), plate_rad,
                 (10, 8, 28, 160), (80, 74, 110, 120), w=1)

    big.blit(plate_surf, plate_rect.topleft)

    # name text on top of plate
    sc.plain_text(big, name, name_font, plate_rect.center, (250, 248, 240),
                  shadow_a=100, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))

    # ── tier lozenge (KEEP, separate, below the plate) ────────────────────────
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # ══ INSET SHELF (from v2 bottom-shelf R2) ═════════════════════════════════
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)
    if affordable:
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
    lip = (115, 106, 140) if affordable else (62, 62, 86)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)
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

    _coin_chip(big, m(CX), m(CHIP_CY), price, affordable)

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


# ── render one panel with a forced hero name ──────────────────────────────────

def render_panel(name):
    sd.load()
    sd.balance = lambda: 999_999      # affordable state
    # Force the hero name so we can probe short / wide / max-width behaviour.
    store_mod.StoreScene._disp_name = staticmethod(lambda sid: name)
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
    crop = full.crop((px, py, px + POP_W, py + POP_H))
    return crop, _captured["plate_w"]


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


PANELS = [
    ("MUMMY", "short — narrow plate"),
    ("SUGAR GLIDER", "wide plate, near max"),
    ("TEMPEST CONDOR", "max 168px, scaled to fit"),
]

# ── compose sheet ─────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = 200, 340
GAP = 12
MARGIN = 18
HDR_H = 26
FOOT_H = 30
N = len(PANELS)

# zoom strip: 2x of panel-2 name zone (popup y 140..200 → 60px tall → 120px)
ZOOM = 2
ZONE_Y0, ZONE_Y1 = 140, 200
ZOOM_W = PANEL_W * ZOOM
ZOOM_H = (ZONE_Y1 - ZONE_Y0) * ZOOM
ZOOM_LBL_H = 22

# 1× inset crop of panel-2 name zone, to prove the plate reads at true ship
# size (100% of the popup, not 2×) against the indigo card.
ONE_LBL_H = 22
ONE_W = PANEL_W
ONE_H = ZONE_Y1 - ZONE_Y0

ROW_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_W = max(ROW_W, MARGIN + ZOOM_W + MARGIN)
CANVAS_H = (MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + GAP
            + ZOOM_LBL_H + ZOOM_H + GAP
            + ONE_LBL_H + ONE_H + MARGIN)

BG = (8, 8, 20)
GOLD = (220, 190, 100)
DIM = (140, 130, 100)
CYAN = (120, 200, 200)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

fhdr = store_mod._font(15, True)
flbl = store_mod._font(11, True)
fsub = store_mod._font(9, False)
fbadge = store_mod._font(11, True)

hdr = fhdr.render("NAMEPLATE · Long-name overflow R2", True, GOLD)
canvas.blit(hdr, hdr.get_rect(midtop=(CANVAS_W // 2, MARGIN)))

panel_top = MARGIN + HDR_H + GAP
row_x0 = (CANVAS_W - ROW_W) // 2 + MARGIN

panel2_img = None
for i, (name, note) in enumerate(PANELS):
    x0 = row_x0 + i * (PANEL_W + GAP)
    img, plate_w = render_panel(name)
    if i == 2:
        panel2_img = img
    canvas.blit(_pil_to_surf(img), (x0, panel_top))
    pygame.draw.rect(canvas, (38, 36, 58),
                     (x0 - 1, panel_top - 1, PANEL_W + 2, PANEL_H + 2), width=1)

    # ID badge: dark pill top-left of the panel
    bx, by, bw, bh = x0 + 6, panel_top + 6, 20, 18
    pygame.draw.rect(canvas, (16, 16, 30), (bx, by, bw, bh), border_radius=6)
    pygame.draw.rect(canvas, (60, 58, 84), (bx, by, bw, bh), width=1, border_radius=6)
    idt = fbadge.render(str(i), True, (210, 210, 230))
    canvas.blit(idt, idt.get_rect(center=(bx + bw // 2, by + bh // 2)))

    # footer: id + name + plate width
    cx = x0 + PANEL_W // 2
    fy = panel_top + PANEL_H + 5
    l1 = flbl.render(f"{i} · {name}", True, CYAN)
    l2 = fsub.render(f"{note}  (plate {plate_w}px)", True, DIM)
    canvas.blit(l1, l1.get_rect(midtop=(cx, fy)))
    canvas.blit(l2, l2.get_rect(midtop=(cx, fy + 14)))

# ── zoom strip: 2x panel-2 name zone ──────────────────────────────────────────
zone = panel2_img.crop((0, ZONE_Y0, PANEL_W, ZONE_Y1))
zone2x = zone.resize((ZOOM_W, ZOOM_H), Image.NEAREST)
zy_lbl = panel_top + PANEL_H + FOOT_H + GAP
zx = (CANVAS_W - ZOOM_W) // 2
zl = flbl.render("2× ZOOM · panel 2 name zone — plate edge · deboss · scale-fit",
                 True, GOLD)
canvas.blit(zl, zl.get_rect(midleft=(zx, zy_lbl + ZOOM_LBL_H // 2)))
zy = zy_lbl + ZOOM_LBL_H
canvas.blit(_pil_to_surf(zone2x), (zx, zy))
pygame.draw.rect(canvas, (38, 36, 58),
                 (zx - 1, zy - 1, ZOOM_W + 2, ZOOM_H + 2), width=1)

# ── 1× inset: panel-2 name zone at true ship size ─────────────────────────────
oy_lbl = zy + ZOOM_H + GAP
ox = (CANVAS_W - ONE_W) // 2
ol = flbl.render("1× · panel 2 at ship size — plate reads engraved on card",
                 True, GOLD)
canvas.blit(ol, ol.get_rect(midtop=(CANVAS_W // 2, oy_lbl + 3)))
oy = oy_lbl + ONE_LBL_H
canvas.blit(_pil_to_surf(zone), (ox, oy))
pygame.draw.rect(canvas, (38, 36, 58),
                 (ox - 1, oy - 1, ONE_W + 2, ONE_H + 2), width=1)

OUT = os.path.join(os.path.dirname(__file__), "..", "docs",
                   "store_confirm_popup_v4", "long-name", "nameplate", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
w, h = canvas.get_size()
print(f"saved {OUT} ({w}x{h})")
