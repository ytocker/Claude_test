#!/usr/bin/env python3
"""
scale-to-fit  ·  store buy-confirmation popup v4  ·  long-name overflow  ·  R2

The control/baseline concept for the long-name overflow problem: the item
name shrinks uniformly (font size stepped down −0.5 from 30) until it fits
inside a 168px safe width, then renders as a single centred line at Y_NAME=168.

R2 (final pass), per art-director notes:
  · Floor raised 9 → 20. Below sz=20 this concept loses authority, so we stop
    there and let the true stress case (TEMPEST CONDOR) sit AT the floor —
    the honest limit of the "just shrink it" approach, documented in-render.
  · Useful band is 30→20 only; nothing ships smaller.
  · When sz < 26 a small positive tracking (+2 device px) spreads the
    compressed word toward the 168px cap so it doesn't float mid-space.
  · Keyline is guaranteed: kept full at the floor (sz=20 >= 18), dropped only
    if a glyph were ever too small for a clean keyline.

Everything else in the draw function is unchanged from R1 / shelf-chip R2.
"""
import math
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
UI_CREAM    = store_mod.UI_CREAM
NEAR_BLACK  = store_mod.NEAR_BLACK

m = sc.m

# The three names driving the panels: short, near-limit, stress test.
NAMES = ["MUMMY", "SUGAR GLIDER", "TEMPEST CONDOR"]

# Floor for the shrink band — below this the concept fails (see docstring).
FLOOR_SZ = 20

# Font size + tracking actually used per panel — captured for the footer.
_used_sz = {}
_used_trk = {}


# ── Shelf-chip helpers (unchanged from R2) ────────────────────────────────────

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


# ── scale-to-fit draw function (shelf-chip R2 base, name render swapped) ───────

def _draw_confirm(self, surf):
    self._confirm_panel = self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret   = store_catalog.is_secret(sid) and not sd.is_owned(sid)
    tier     = store_catalog.rarity(sid)
    pal      = sc.MYSTERY if secret else sc.RARITY.get(tier, sc.RARITY["common"])
    tier_word = "MYSTERY" if secret else tier.upper()
    name     = "???" if secret else self._disp_name(sid)
    price    = store_catalog.cost(sid)
    affordable = sd.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    NAME_FS, Y_NAME = 30, 168
    Y_BANNER, BANNER_W = 188, 120

    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
    CHIP_CY  = 258
    BTN_W, BTN_H, BTN_RAD = 76, 30, 9
    BTN_CY   = 302
    BTN_GAP  = 8
    BUY_CX   = CX - (BTN_W + BTN_GAP) // 2
    CAN_CX   = CX + (BTN_W + BTN_GAP) // 2

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

    # Corner gems + banner
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])

    # scale-to-fit: shrink font toward the floor until the name fits safe_w.
    # Below FLOOR_SZ the concept loses authority, so we stop there rather than
    # ship illegibly small text — the honest limit of "just shrink it".
    safe_w = m(168)
    sz = NAME_FS  # start at 30
    tracking = 0
    while sz > FLOOR_SZ:
        f = sc.font(sz)
        if sc._glyph_base(name, f, tracking).get_width() <= safe_w:
            break
        sz -= 0.5

    # Small sizes float mid-space; a touch of positive tracking spreads the
    # compressed word back out toward the 168px cap.
    if sz < 26:
        tracking = 2  # device px

    name_font = sc.font(sz)
    _used_sz[name] = sz
    _used_trk[name] = tracking
    # Drop the keyline only if a glyph is too small for a clean stroke; at the
    # sz=20 floor it still survives, so it stays.
    kw_val = m(1.0) if sz >= 18 else 0
    sc.plain_text(big, name, name_font, (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, tracking=tracking, weight=m(0.9),
                  keyline=(6, 6, 16), kw=kw_val)

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
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK, thick=5)
    else:
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


def render_panel(forced_name):
    store_mod.StoreScene._draw_confirm = _draw_confirm
    store_mod.StoreScene._disp_name = lambda self, sid: forced_name
    sd.load()
    sd.balance = lambda: 999_999     # affordable state only
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
    return full.crop((px, py, px + POP_W, py + POP_H))


def _pil_to_surf(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode)


# ── Compose review sheet: 3 panels + zoom strip ───────────────────────────────
PANEL_W = 200
PANEL_H = 340
GAP     = 10
MARGIN  = 18
HDR_H   = 30
FOOT_H  = 44
N       = len(NAMES)
ZOOM_Y0, ZOOM_Y1 = 130, 210
ZOOM_H  = 2 * (ZOOM_Y1 - ZOOM_Y0)   # 160

BG   = (8, 8, 20)
GOLD = (220, 190, 100)
DIM  = (140, 130, 100)
CYAN = (120, 200, 200)
PILL_BG   = (24, 22, 38)
PILL_TEXT = (240, 236, 224)

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = (MARGIN + HDR_H + GAP + PANEL_H + GAP + ZOOM_H + GAP + FOOT_H + MARGIN)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

try:
    fhdr  = store_mod._font(14, True)
    fbadge = store_mod._font(10, True)
    flbl  = store_mod._font(11, True)
    fsub  = store_mod._font(9, False)
except Exception:
    fhdr = fbadge = flbl = fsub = None

# Header
hdr_txt = "SCALE-TO-FIT · Long-name overflow R2"
if fhdr:
    h = fhdr.render(hdr_txt, True, GOLD)
    canvas.blit(h, h.get_rect(midtop=(CANVAS_W // 2, MARGIN)))

panel_top = MARGIN + HDR_H + GAP

panel_imgs = []
for i, nm in enumerate(NAMES):
    x0  = MARGIN + i * (PANEL_W + GAP)
    img = render_panel(nm)
    panel_imgs.append(img)
    canvas.blit(_pil_to_surf(img), (x0, panel_top))

    # Panel border
    pygame.draw.rect(canvas, (38, 36, 58),
                     (x0 - 1, panel_top - 1, PANEL_W + 2, PANEL_H + 2), width=1)

    # ID badge — small dark pill top-left corner
    if fbadge:
        bt = fbadge.render(str(i), True, PILL_TEXT)
        pad = 4
        pw, ph = bt.get_width() + pad * 2, bt.get_height() + pad * 2
        bx, by = x0 + 6, panel_top + 6
        pygame.draw.rect(canvas, PILL_BG, (bx, by, pw, ph), border_radius=5)
        canvas.blit(bt, (bx + pad, by + pad))

# ── Zoom strip: 2× crop of Panel 2's name zone (y=130..210, full width) ────────
zoom_top = panel_top + PANEL_H + GAP
p2 = panel_imgs[2]
name_crop = p2.crop((0, ZOOM_Y0, PANEL_W, ZOOM_Y1))
zoom = name_crop.resize((PANEL_W * 2, ZOOM_H), Image.NEAREST)
zoom_w = PANEL_W * 2
zoom_x = (CANVAS_W - zoom_w) // 2
canvas.blit(_pil_to_surf(zoom), (zoom_x, zoom_top))
pygame.draw.rect(canvas, (38, 36, 58),
                 (zoom_x - 1, zoom_top - 1, zoom_w + 2, ZOOM_H + 2), width=1)
if fsub:
    zt = fsub.render("PANEL 2 NAME ZONE · 2× (y 130–210) · AT FLOOR sz20",
                     True, DIM)
    canvas.blit(zt, zt.get_rect(midtop=(CANVAS_W // 2, zoom_top + 4)))

# ── Footer per panel ──────────────────────────────────────────────────────────
foot_y = zoom_top + ZOOM_H + GAP
for i, nm in enumerate(NAMES):
    x0 = MARGIN + i * (PANEL_W + GAP)
    cx = x0 + PANEL_W // 2
    sz = _used_sz.get(nm, 30)
    trk = _used_trk.get(nm, 0)
    sz_str = f"{sz:g}"
    if flbl:
        l1 = flbl.render(f"{i} · {nm}", True, CYAN)
        canvas.blit(l1, l1.get_rect(midtop=(cx, foot_y)))
    if fsub:
        l2 = fsub.render(f"(sz {sz_str}, trk {trk:g})", True, DIM)
        canvas.blit(l2, l2.get_rect(midtop=(cx, foot_y + 18)))

OUT = os.path.join(os.path.dirname(__file__), "..", "docs",
                   "store_confirm_popup_v4", "long-name", "scale-to-fit",
                   "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
w, h = canvas.get_size()
print(f"saved {OUT} ({w}x{h})")
print("font sizes used:", {k: f"{v:g}" for k, v in _used_sz.items()})
print("tracking used:", {k: f"{v:g}" for k, v in _used_trk.items()})
