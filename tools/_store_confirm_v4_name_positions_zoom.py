"""
store_confirm_popup_v4 — name + banner Y-position intermediates.

Renders 5 panels showing positions between CURRENT (155/175) and OPTION A
(182/200) so the user can pick a precise stopping point.

Each panel has an ID badge (top-left corner chip) for easy reference.
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

# ── Positions to compare (CURRENT + 3 intermediates + OPTION A) ───────────────
# IDs: 0 = CURRENT anchor, 1–3 = intermediates, A = OPTION A anchor
OPTIONS = [
    ("0", "CURRENT",  155, 175),
    ("1", "INT-1",    162, 182),
    ("2", "INT-2",    168, 188),
    ("3", "INT-3",    175, 195),
    ("A", "OPTION A", 182, 200),
]


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


# ── Parameterised draw function ───────────────────────────────────────────────

def _build_draw_fn(y_name, y_banner):
    def _draw(self, surf):
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
        NAME_FS  = 30
        BANNER_W = 120

        SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
        CHIP_CY  = 258
        BTN_W, BTN_H, BTN_RAD = 76, 30, 9
        BTN_CY   = 302
        BTN_GAP  = 8
        BUY_CX   = CX - (BTN_W + BTN_GAP) // 2
        CAN_CX   = CX + (BTN_W + BTN_GAP) // 2

        big = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)

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

        sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
        sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
        sc.plain_text(big, name, sc.font(NAME_FS),
                      (m(CX), m(y_name)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        sc._ribbon_lozenge(big, tier_word, m(CX), m(y_banner), m(BANNER_W), pal)

        shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
        shelf_rad  = m(CARD_RAD)
        shelf_stops = [(0.0, (28, 30, 62)), (1.0, (14, 16, 40))]
        shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
        smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                         border_bottom_left_radius=shelf_rad,
                         border_bottom_right_radius=shelf_rad)
        shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
        lip = (115, 106, 140)
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
        _draw_button(big, buy, brad, "BUY",    locked=False)
        _draw_button(big, can, brad, "CANCEL", locked=False)

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
        self.confirm_yes_rect = pygame.Rect(
            px + BUY_CX - BTN_W // 2, py + BTN_CY - BTN_H // 2, BTN_W, BTN_H)

    return _draw


def render_panel(y_name, y_banner):
    store_mod.StoreScene._draw_confirm = _build_draw_fn(y_name, y_banner)
    sd.load()
    sd.balance = lambda: 999_999
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


def _draw_id_badge(canvas, badge_id, x0, panel_top):
    """Draw a small pill ID badge in the top-left corner of a panel."""
    try:
        fbadge = store_mod._font(10, True)
    except Exception:
        return
    pad_x, pad_y = 5, 3
    txt_surf = fbadge.render(badge_id, True, (240, 235, 220))
    tw, th = txt_surf.get_size()
    pill_w  = tw + pad_x * 2
    pill_h  = th + pad_y * 2
    pill    = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    pygame.draw.rect(pill, (24, 22, 38, 210), pill.get_rect(), border_radius=3)
    pill.blit(txt_surf, (pad_x, pad_y))
    canvas.blit(pill, (x0 + 4, panel_top + 4))


# ── Compose comparison sheet ──────────────────────────────────────────────────
PANEL_W = 200
PANEL_H = 340
GAP     = 10
MARGIN  = 18
HDR_H   = 28
FOOT_H  = 40
N       = len(OPTIONS)

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + GAP + FOOT_H + MARGIN

BG   = (8, 8, 20)
GOLD = (220, 190, 100)
DIM  = (140, 130, 100)
CYAN = (120, 200, 200)
ANCH = (200, 160, 80)   # amber tint for anchor panels (0 and A)

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

try:
    fhdr  = store_mod._font(14, True)
    flbl  = store_mod._font(11, True)
    fsub  = store_mod._font(9, False)
except Exception:
    fhdr = flbl = fsub = None

hdr_txt = "SHELF-CHIP V4 · NAME + BANNER INTERMEDIATES (CURRENT → OPTION A)"
if fhdr:
    h = fhdr.render(hdr_txt, True, GOLD)
    canvas.blit(h, h.get_rect(midtop=(CANVAS_W // 2, MARGIN)))

panel_top = MARGIN + HDR_H + GAP

for i, (badge_id, label, y_name, y_banner) in enumerate(OPTIONS):
    x0  = MARGIN + i * (PANEL_W + GAP)
    img = render_panel(y_name, y_banner)
    canvas.blit(_pil_to_surf(img), (x0, panel_top))

    is_anchor = (badge_id in ("0", "A"))
    border_col = (80, 70, 40) if is_anchor else (38, 36, 58)
    pygame.draw.rect(canvas, border_col,
                     (x0 - 1, panel_top - 1, PANEL_W + 2, PANEL_H + 2), width=1)

    # ID badge on the panel
    _draw_id_badge(canvas, badge_id, x0, panel_top)

    # Footer
    cx    = x0 + PANEL_W // 2
    foot_y = panel_top + PANEL_H + 6
    lbl_col = ANCH if is_anchor else CYAN
    if flbl:
        l1 = flbl.render(label, True, lbl_col)
        canvas.blit(l1, l1.get_rect(midtop=(cx, foot_y)))
    if fsub:
        sub = fsub.render(f"name {y_name} / banner {y_banner}", True, DIM)
        canvas.blit(sub, sub.get_rect(midtop=(cx, foot_y + 16)))

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v4", "name-position-intermediates.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
w, h = canvas.get_size()
print(f"saved {OUT} ({w}×{h})")
