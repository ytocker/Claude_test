#!/usr/bin/env python3
"""
unified-banner  ·  store buy-confirmation popup v4  ·  long-name overflow  ·  R2

R2 folds in the art-director's ITERATE notes on R1's two-row banner:

  1. The 25px dark gutter between the name and tier rows is gone. Both rows now
     live inside ONE continuous notched-lozenge body with ONE outline and ONE
     width; the boundary is a 2px hairline divider, not a dead band.
  2. The gem gradient behind the NAME row is darkened toward black (gem * 0.55)
     so cream-on-gem clears 4.5:1 on the darkest tier by fill alone — the dark
     keyline is margin, not the sole safety net. The tier row keeps the normal
     glow->deep gem ramp so its dark ink still reads.
  3. Name-band vertical padding is tightened so font 22 fills the row and reads
     proud rather than timid.
  4. Names that still overflow at the sz=17 floor (~15px cap at SS=2) wrap to
     TWO lines at a space before shrinking further; each line then shrinks to
     fit the banner instead of collapsing to unreadable single-line type.
  5. The notched lozenge tips (pointed bevels) keep the banner reading as its
     own object, not a taller copy of the old single-row tier ribbon.

This sheet still stress-tests the WORST case: three long names on the DARKEST
RARITY tier (epic — lowest-luminance gem in RARITY) so the dark_gem fill math
is proven where it matters. A 2x zoom of panel 0's name zone isolates the
cream-on-darkened-gem read.
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
from game.draw import lerp_color, NEAR_BLACK, WHITE

_draw_qmark = store_mod._draw_qmark
UI_CREAM = store_mod.UI_CREAM
NEAR_BLACK_UI = store_mod.NEAR_BLACK

m = sc.m

# Darkest tier in the RARITY dict by gem luminance (epic gem 194,122,248 ->
# ~158, below rare/legendary/common). Forcing this proves the cream name band.
DARK_TIER = "epic"
DARK_TIER_WORD = "EPIC"

# Three long item names to overflow-test the auto-widening banner. The third
# overflows the sz=17 floor and must wrap to two lines.
PANELS = ["MUMMY", "SUGAR GLIDER", "TEMPEST CONDOR"]


def _unified_banner(big, name, tier_word, cx, cy, max_w, pal):
    """ONE continuous notched-lozenge banner carrying NAME (top) + TIER (bottom).

    The single body clips to one lozenge polygon and wears one outline; a 2px
    hairline splits the two zones. The name zone's gem gradient is darkened
    toward black so cream type clears contrast on the darkest tier by fill;
    the tier zone keeps the normal glow->deep ramp for its dark ink. Long
    names shrink to a sz=17 floor, then wrap to two lines rather than clipping.
    """
    NAME_FS_BANNER = 22           # smaller than the hero 30 but readable in-band
    TIER_FS = 8                   # matches the existing _ribbon_lozenge treatment
    PAD_X = m(8)
    name_h = m(20)                # tight: font 22 fills the row, reads proud
    div_h = max(1, m(2))          # hairline divider, not a dark gutter
    tier_h = m(14)
    tip_w = m(8)                  # notched lozenge tip inset

    target = m(max_w) - PAD_X * 2

    def bw(txt, fnt):
        return sc._glyph_base(txt, fnt, 0).get_width()

    # Shrink the name toward a sz=17 floor (~15px cap at SS=2). Below that the
    # glyphs get too small to read, so we prefer a two-line wrap instead.
    sz = NAME_FS_BANNER
    name_font = sc.font(sz)
    while sz > 17:
        name_font = sc.font(sz)
        if bw(name, name_font) <= target:
            break
        sz -= 0.5

    # Still too wide at the floor? Split at the space that best balances the two
    # halves, then keep shrinking so the WIDER line fits the banner width.
    two_line = False
    line1 = line2 = None
    if bw(name, name_font) > target:
        spaces = [i for i, c in enumerate(name) if c == " "]
        if spaces:
            best = min(spaces, key=lambda i: max(
                bw(name[:i], name_font), bw(name[i + 1:], name_font)))
            line1, line2 = name[:best], name[best + 1:]
            two_line = True
            while sz > 9:
                name_font = sc.font(sz)
                if max(bw(line1, name_font), bw(line2, name_font)) <= target:
                    break
                sz -= 0.5
            name_h = m(32)        # taller name zone hosts both lines

    tier_font = sc.font(TIER_FS)
    tier_w = sc._glyph_base(tier_word, tier_font, m(1.4)).get_width()

    if two_line:
        name_w = max(bw(line1, name_font), bw(line2, name_font))
    else:
        name_w = bw(name, name_font)

    inner_w = max(name_w, tier_w) + PAD_X * 2
    banner_w = min(m(max_w), max(m(60), inner_w))
    banner_h = name_h + div_h + tier_h

    w, h = banner_w, banner_h
    x0, y0 = cx - w // 2, cy - h // 2
    # Notched lozenge: pointed bevel tips at vertical mid — the banner's own
    # silhouette, distinct from a plain rounded ribbon.
    pt = min(tip_w, h // 2)
    poly = [(0, h // 2), (pt, 0), (w - pt, 0),
            (w, h // 2), (w - pt, h), (pt, h)]

    # ONE gradient body for both zones. The name zone (top) is darkened toward
    # black so cream fill clears 4.5:1 even on epic; the tier zone (bottom)
    # keeps the normal glow->deep gem ramp for its dark ink.
    gem = pal["gem"]
    dark_gem = tuple(max(0, int(c * 0.55)) for c in gem)
    ratio = name_h / banner_h
    stops = [
        (0.0, dark_gem),
        (max(0.0, ratio - 0.02), dark_gem),
        (min(1.0, ratio + 0.02), pal.get("glow", gem)),
        (1.0, pal.get("deep", (4, 5, 16))),
    ]
    body = sc.vgrad_stops(w, h, 0, stops, 255, gamma=1.05)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255, 255, 255, 255), poly)
    body.blit(pmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0, 0, 0, 120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))

    # ONE outline for the whole shape.
    abspoly = [(x0 + px, y0 + py) for px, py in poly]
    pygame.draw.polygon(big, (4, 5, 16), abspoly, width=max(1, m(1.4)))

    # Hairline divider centred in the 2px band at the zone boundary.
    div_cy = y0 + name_h + div_h // 2
    pygame.draw.line(big, (60, 58, 80), (x0 + pt, div_cy), (x0 + w - pt, div_cy),
                     div_h)

    # NAME — top zone — cream + dark keyline (fill already clears contrast).
    name_cy = y0 + name_h // 2
    if two_line:
        sc.plain_text(big, line1, name_font, (cx, name_cy - m(8)), (250, 248, 240),
                      shadow_a=0, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.9))
        sc.plain_text(big, line2, name_font, (cx, name_cy + m(8)), (250, 248, 240),
                      shadow_a=0, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.9))
    else:
        sc.plain_text(big, name, name_font, (cx, name_cy), (250, 248, 240),
                      shadow_a=0, weight=m(0.8), keyline=(6, 6, 16), kw=m(0.9))

    # TIER — bottom zone — existing dark-ink-on-gradient lozenge treatment.
    tier_cy = y0 + name_h + div_h + tier_h // 2
    tier_col = pal.get("ink", (14, 12, 26))
    sc.plain_text(big, tier_word, tier_font, (cx, tier_cy), tier_col,
                  shadow_a=0, tracking=m(1.4), weight=m(0.7))


# ── Shelf-chip helpers (unchanged from shelf-chip R2) ─────────────────────────

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


def _draw_confirm(self, surf):
    self._confirm_panel = self.confirm_yes_rect = self.confirm_no_rect = None
    sid = self._confirm
    if sid is None:
        return

    scrim = pygame.Surface((W, H), pygame.SRCALPHA)
    scrim.fill((4, 4, 10, 180))
    surf.blit(scrim, (0, 0))

    secret = store_catalog.is_secret(sid) and not sd.is_owned(sid)
    # Force the darkest tier so this sheet proves the cream name band.
    tier = DARK_TIER
    pal = sc.MYSTERY if secret else sc.RARITY.get(tier, sc.RARITY["common"])
    tier_word = "MYSTERY" if secret else DARK_TIER_WORD
    name = "???" if secret else self._disp_name(sid)
    price = store_catalog.cost(sid)
    affordable = sd.balance() >= price

    POP_W, POP_H = 200, 340
    CX = POP_W // 2

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
    # Y_NAME lane is now free — the unified banner carries the name. Kept only
    # so nothing downstream trips on a missing symbol.
    NAME_FS, Y_NAME = 30, 155
    Y_BANNER = 188

    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
    CHIP_CY = 258
    BTN_W, BTN_H, BTN_RAD = 76, 30, 9
    BTN_CY = 302
    BTN_GAP = 8
    BUY_CX = CX - (BTN_W + BTN_GAP) // 2
    CAN_CX = CX + (BTN_W + BTN_GAP) // 2

    big = pygame.Surface((POP_W * sc.SS, POP_H * sc.SS), pygame.SRCALPHA)

    # Card body
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad = m(CARD_RAD)
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

    # Corner gems + unified banner (name + tier in ONE banner).
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    _unified_banner(big, name, tier_word, m(CX), m(Y_BANNER), 168, pal)

    # Shelf
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)
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

    # Disc + aura + thumb LAST so the hero overhangs everything below it.
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    if secret:
        _draw_qmark(big, cx_ss, cy_ss, int(r_ss * 1.17), UI_CREAM, NEAR_BLACK_UI, thick=5)
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


store_mod.StoreScene._draw_confirm = _draw_confirm


def render_panel(name):
    # Per-panel name override; the draw fn forces the darkest tier itself.
    store_mod.StoreScene._disp_name = staticmethod(lambda sid, nm=name: nm)
    sd.load()
    sd.balance = lambda: 999_999          # affordable state
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


# ── Compose review sheet: 3 panels + zoom strip ───────────────────────────────
PANEL_W, PANEL_H = 200, 340
GAP = 14
MARGIN = 18
HDR_H = 26
FOOT_H = 20
N = len(PANELS)

BG = (8, 8, 20)
GOLD = (220, 190, 100)
DIM = (140, 130, 100)
CYAN = (120, 200, 200)

fhdr = store_mod._font(14, True)
flbl = store_mod._font(10, True)
fsub = store_mod._font(9, False)
fbadge = store_mod._font(11, True)

# Render panels first so we can build the zoom strip from panel 0.
panel_imgs = [render_panel(nm) for nm in PANELS]

# Zoom strip: 2x of panel 0's name zone (popup y=155..220).
ZY0, ZY1 = 155, 220
zoom_src = panel_imgs[0].crop((0, ZY0, PANEL_W, ZY1))
ZW, ZH = PANEL_W * 2, (ZY1 - ZY0) * 2
zoom_img = zoom_src.resize((ZW, ZH), Image.NEAREST)

zoom_lbl_h = 18
ZONE_H = ZH + zoom_lbl_h + 6

panel_top = MARGIN + HDR_H + GAP
row_bottom = panel_top + PANEL_H + FOOT_H

CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = row_bottom + GAP + ZONE_H + MARGIN

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

# Header
hdr_txt = "UNIFIED-BANNER · Long-name overflow R2 (darkest tier)"
h = fhdr.render(hdr_txt, True, GOLD)
canvas.blit(h, h.get_rect(midtop=(CANVAS_W // 2, MARGIN)))

for i, (nm, img) in enumerate(zip(PANELS, panel_imgs)):
    x0 = MARGIN + i * (PANEL_W + GAP)
    canvas.blit(_pil_to_surf(img), (x0, panel_top))
    pygame.draw.rect(canvas, (38, 36, 58),
                     (x0 - 1, panel_top - 1, PANEL_W + 2, PANEL_H + 2), width=1)

    # ID badge — dark pill top-left of each panel.
    bx, by, bw, bh = x0 + 6, panel_top + 6, 20, 18
    pygame.draw.rect(canvas, (10, 10, 22), (bx, by, bw, bh), border_radius=6)
    pygame.draw.rect(canvas, (70, 68, 96), (bx, by, bw, bh), width=1, border_radius=6)
    bnum = fbadge.render(str(i), True, (222, 214, 176))
    canvas.blit(bnum, bnum.get_rect(center=(bx + bw // 2, by + bh // 2)))

    # Footer: id + name + (darkest tier)
    foot = flbl.render(f"{i} · {nm} · (darkest tier)", True, CYAN)
    canvas.blit(foot, foot.get_rect(midtop=(x0 + PANEL_W // 2, panel_top + PANEL_H + 4)))

# Zoom strip
zoom_top = row_bottom + GAP + zoom_lbl_h
zx = (CANVAS_W - ZW) // 2
zlbl = fsub.render(
    "2× ZOOM · panel 0 name zone (popup y=155..220) · cream-on-darkened-gem, darkest tier",
    True, DIM)
canvas.blit(zlbl, zlbl.get_rect(midtop=(CANVAS_W // 2, row_bottom + GAP)))
canvas.blit(_pil_to_surf(zoom_img), (zx, zoom_top))
pygame.draw.rect(canvas, (70, 68, 96), (zx - 1, zoom_top - 1, ZW + 2, ZH + 2), width=1)

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_popup_v4", "long-name",
                   "unified-banner", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(canvas, OUT)
w, h = canvas.get_size()
print(f"saved {OUT} ({w}x{h})")
