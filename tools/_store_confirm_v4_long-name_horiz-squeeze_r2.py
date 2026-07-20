#!/usr/bin/env python3
"""
horiz-squeeze  ·  store buy-confirmation popup v4  ·  long-name overflow  ·  R2

Concept: names that would blow past the 168px name-zone are CONDENSED
HORIZONTALLY at full font-size 30 rather than shrunk. The type block keeps a
constant cap-height silhouette no matter how long the name is, so every card
reads at the same visual weight.

R2 tightens the condense ladder on the art-director notes:

  1. Negative tracking, FLOORED AT -12 device px (was -20). Past -12 adjacent
     glyphs fuse into continuous ink bars and the word-space collapses, so -12
     is the hard stop for spacing-only condense. The keyline is stamped from the
     SAME tracked master, so it condenses in lockstep — one stroke, not
     per-glyph fragments.
  2. Below -12: HAND OFF to a horizontal width-scale. The name is rendered once
     at the -12 tracked master, then pygame.transform.smoothscale narrows the
     glyph SHAPES (real condense) to meet the safe width. Because the scale
     shrinks the letters themselves — not just the gaps — it never lets letters
     touch: the 2px ink gap survives, and the word-space (an intrinsic space
     advance, always wider than a letter gap) scales by the same ratio so it
     stays ~1.5x the letter gap. Cap-height (the silhouette weight) is untouched;
     the keyline scales with the glyphs and holds >=1px through the range.

Everything else in the popup is UNCHANGED from shelf-chip R2 (name zone parked
at Y_NAME=168 / Y_BANNER=188). This sheet stress-tests three name lengths and
zooms the tracking-condensed case so the keyline can be inspected up close.
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
UI_CREAM    = store_mod.UI_CREAM
NEAR_BLACK  = store_mod.NEAR_BLACK

m = sc.m

NAME_FS   = 30
Y_NAME    = 168
Y_BANNER  = 188
SAFE_LOG  = 168          # logical name-zone width the type must fit inside
TRACK_FLOOR = -12        # device-px floor: below this glyphs fuse into ink bars

# Panels: name string + ID badge label.
PANELS = ["MUMMY", "SUGAR GLIDER", "TEMPEST CONDOR"]


# ── name condensing ───────────────────────────────────────────────────────────

def _draw_name(big, name, cx_ss, y_ss):
    """Draw the item name in the name zone, condensing horizontally if it would
    overflow. Returns the regime label for the footer."""
    name_font = sc.font(NAME_FS)
    safe_w = m(SAFE_LOG)

    # Step 1: close inter-glyph spacing one device-px at a time, floored at -12
    # so adjacent glyphs never fuse.
    tracking = 0
    while tracking > TRACK_FLOOR:
        if sc._glyph_base(name, name_font, tracking).get_width() <= safe_w:
            break
        tracking -= 1

    gw_at_track = sc._glyph_base(name, name_font, tracking).get_width()

    if gw_at_track <= safe_w:
        # Pure tracking condense: crisp, keyline stamped from the tracked master.
        sc.plain_text(big, name, name_font, (cx_ss, y_ss), (250, 248, 240),
                      shadow_a=160, tracking=tracking, weight=m(0.9),
                      keyline=(6, 6, 16), kw=m(1.0))
        return "(native)" if tracking == 0 else f"(tracking {tracking})"

    # Step 2: -12 still too wide -> render the -12 master once and narrow the
    # glyph SHAPES horizontally (real condense) to reach the safe width.
    name_h = m(40)
    temp_w = gw_at_track + m(20)
    temp = pygame.Surface((temp_w, name_h), pygame.SRCALPHA)
    sc.plain_text(temp, name, name_font, (temp_w // 2, name_h // 2),
                  (250, 248, 240), shadow_a=0, tracking=tracking,
                  weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    scale_ratio = safe_w / gw_at_track
    dst_w = max(1, int(temp_w * scale_ratio))
    squeezed = pygame.transform.smoothscale(temp, (dst_w, name_h))
    big.blit(squeezed, squeezed.get_rect(center=(cx_ss, y_ss)))
    return f"(scale x{scale_ratio:.2f})"


# ── shelf-chip helpers (unchanged from R2) ────────────────────────────────────

def _padlock(surf, cx, cy, h, color):
    bw, bh = int(h * 0.92), int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr  = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc,
                    math.radians(15), math.radians(165), max(1, int(h * 0.17)))
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.22)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (24, 22, 34), kh, border_radius=1)


def _draw_button(big, rect, rad, label, locked=False):
    if locked:
        stops   = [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))]
        lab_col = (90, 88, 108)
        sheen   = 12
    else:
        stops   = [(0.0, (84, 78, 126)), (1.0, (50, 46, 82))]
        lab_col = (220, 210, 240)
        sheen   = 28
    sc.drop_shadow(big, rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad, stops, 255), rect.topleft)
    sc.top_sheen(big, rect, rad, m(12), peak=sheen)
    sc.bevel_rim(big, rect, rad, (20, 18, 36, 180), (130, 124, 160, 200),
                 w=max(1, m(1.2)))
    lab_font = sc.font(13)
    if locked:
        lw     = lab_font.size(label)[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.92)
        inner  = m(4)
        grp    = lock_w + inner + lw
        gx     = rect.centerx - grp // 2
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
        border     = (120, 74, 14)
    else:
        face_stops = [(0.0, (60, 60, 74)), (1.0, (44, 44, 58))]
        border     = (78, 80, 96)
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)
    pygame.draw.rect(big, border, chip, width=max(1, m(1)), border_radius=crad)

    txt      = f"{price:,}"
    num_font = sc.font(22)
    coin_r   = m(14)
    coin_d   = coin_r * 2
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_d + gap + num_w
    left     = cx - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_d + gap + num_w // 2
    num_cy   = cy + m(3)

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


# ── patched confirm draw (shelf-chip R2 body, name zone at 168/188) ───────────

def _draw_confirm(self, surf):
    self._confirm_panel = self.confirm_yes_rect = self.confirm_no_rect = None
    self._regime = "(native)"
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    tier      = store_catalog.rarity(sid)
    pal       = sc.RARITY.get(tier, sc.RARITY["common"])
    tier_word = tier.upper()
    name      = self._disp_name(sid)          # forced test name per panel
    price     = store_catalog.cost(sid)
    affordable = sd.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    BANNER_W = 120

    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
    CHIP_CY = 258
    BTN_W, BTN_H, BTN_RAD = 76, 30, 9
    BTN_CY  = 302
    BTN_GAP = 8
    BUY_CX  = CX - (BTN_W + BTN_GAP) // 2
    CAN_CX  = CX + (BTN_W + BTN_GAP) // 2

    big = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)

    # Card body
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad,
                            [(0.0, sc.CARD_T), (1.0, sc.CARD_B)], 255, gamma=1.15),
             rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    # Corner gems + condensed name + banner
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    self._regime = _draw_name(big, name, m(CX), m(Y_NAME))
    sc._ribbon_lozenge(big, tier_word, m(CX), m(Y_BANNER), m(BANNER_W), pal)

    # Shelf
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)
    shelf_stops = ([(0.0, (28, 30, 62)), (1.0, (14, 16, 40))] if affordable
                   else [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))])
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
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
        lwall  = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
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
    _draw_button(big, buy, brad, "BUY",    locked=not affordable)
    _draw_button(big, can, brad, "CANCEL", locked=False)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(317)),
                      (150, 166, 190), shadow_a=0)

    # Disc + aura + thumb LAST
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    sc.blit_thumb(big, sid, cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    px  = (W - POP_W) // 2
    py  = (H - POP_H) // 2
    self._confirm_panel = pygame.Rect(px, py, POP_W, POP_H)
    surf.blit(pop, (px, py))
    self.confirm_no_rect = pygame.Rect(
        px + CAN_CX - BTN_W // 2, py + BTN_CY - BTN_H // 2, BTN_W, BTN_H)
    if affordable:
        self.confirm_yes_rect = pygame.Rect(
            px + BUY_CX - BTN_W // 2, py + BTN_CY - BTN_H // 2, BTN_W, BTN_H)


store_mod.StoreScene._draw_confirm = _draw_confirm


# ── panel render ──────────────────────────────────────────────────────────────

def render_panel(name):
    """Force `name` through _disp_name, render the affordable popup, return the
    200x340 crop + the regime label the draw path resolved."""
    store_mod.StoreScene._disp_name = lambda self, sid, _n=name: _n
    sd.load()
    sd.balance = lambda: 999_999          # affordable state
    sc.clear_cache()
    scene = store_mod.StoreScene()
    scene.view     = "category"
    scene._confirm = "skin_mummy"
    screen = pygame.Surface((W, H))
    screen.fill((6, 7, 18))
    scene.render(screen)
    POP_W, POP_H = 200, 340
    px, py = (W - POP_W) // 2, (H - POP_H) // 2
    raw  = pygame.image.tostring(screen, "RGB")
    full = Image.frombytes("RGB", (W, H), raw)
    return full.crop((px, py, px + POP_W, py + POP_H)), scene._regime


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


# ── compose sheet ─────────────────────────────────────────────────────────────

PANEL_W, PANEL_H = 200, 340
GAP     = 12
MARGIN  = 16
HDR_H   = 26
FOOT_H  = 34
ZOOM    = 2                                  # 2x magnification of the name zone
ZW, ZH  = PANEL_W * ZOOM, 55 * ZOOM          # zoom of logical y=140..195
N       = len(PANELS)

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = (MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + GAP
            + 18 + ZH + MARGIN)

BG   = (8, 8, 20)
GOLD = (220, 190, 100)
CYAN = (120, 200, 200)
DIM  = (140, 130, 100)
PILL = (18, 20, 40)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

fhdr = store_mod._font(15, True)
flbl = store_mod._font(11, True)
fsub = store_mod._font(9, False)
fbadge = store_mod._font(12, True)

# Header
h = fhdr.render("HORIZ-SQUEEZE · Long-name overflow R2", True, GOLD)
canvas.blit(h, h.get_rect(midtop=(CANVAS_W // 2, MARGIN)))

panel_top = MARGIN + HDR_H + GAP
crops = []

for i, name in enumerate(PANELS):
    x0 = MARGIN + i * (PANEL_W + GAP)
    img, regime = render_panel(name)
    crops.append(img)
    canvas.blit(_pil_to_surf(img), (x0, panel_top))
    pygame.draw.rect(canvas, (38, 36, 58),
                     (x0 - 1, panel_top - 1, PANEL_W + 2, PANEL_H + 2), width=1)

    # ID badge: dark pill top-left of the panel.
    badge = pygame.Rect(x0 + 6, panel_top + 6, 22, 18)
    pygame.draw.rect(canvas, PILL, badge, border_radius=6)
    pygame.draw.rect(canvas, (60, 64, 96), badge, width=1, border_radius=6)
    bt = fbadge.render(str(i), True, CYAN)
    canvas.blit(bt, bt.get_rect(center=badge.center))

    # Footer: id + name, then regime label.
    cx = x0 + PANEL_W // 2
    fy = panel_top + PANEL_H + 5
    l1 = flbl.render(f"{i} · {name}", True, CYAN)
    l2 = fsub.render(regime, True, DIM)
    canvas.blit(l1, l1.get_rect(midtop=(cx, fy)))
    canvas.blit(l2, l2.get_rect(midtop=(cx, fy + 15)))

# Zoom strip: 2x of Panel 1's name zone (SUGAR GLIDER, tracking regime).
zoom_label_y = panel_top + PANEL_H + FOOT_H + GAP
zl = flbl.render("ZOOM 2x · Panel 1 name zone (tracking-condensed keyline check)",
                 True, GOLD)
canvas.blit(zl, zl.get_rect(midtop=(CANVAS_W // 2, zoom_label_y)))

name_crop = crops[1].crop((0, 140, PANEL_W, 195))         # 200x55
zoom_img = name_crop.resize((ZW, ZH), Image.NEAREST)
zx = (CANVAS_W - ZW) // 2
zy = zoom_label_y + 18
canvas.blit(_pil_to_surf(zoom_img), (zx, zy))
pygame.draw.rect(canvas, (70, 74, 110), (zx - 1, zy - 1, ZW + 2, ZH + 2), width=1)

OUT = os.path.join(os.path.dirname(__file__), "..", "docs",
                   "store_confirm_popup_v4", "long-name", "horiz-squeeze",
                   "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
w, hh = canvas.get_size()
print(f"saved {OUT} ({w}x{hh})")
