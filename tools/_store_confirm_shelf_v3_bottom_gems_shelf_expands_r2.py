"""Bottom-frame gems — option E: shelf-expands (R2).

Shelf top moves up while bottom stays fixed, making shelf taller and more dominant.
R2 changes vs R1:
  - Pull shelf back 6px: SHELF_Y=221, SHELF_H=101 (bottom stays at 322).
  - Re-seat gems to straddle shelf bottom rim: BOT_GEM_CY=316 (was 309) —
    gem spans y=305→327, 17px inside shelf, 5px below → frame-corner look.
  - Fix chip↔button gap: CHIP_CY=240 (was 246) → 4px gap above buttons.
  - Add dark circular seat halo in shelf face at gem positions so gems read as
    "set into" the shelf, not decals on top.
SHELF_Y=221, SHELF_H=101, CHIP_CY=240, BTN_CY=276.
Shelf bottom stays at 221+101=322 (same as original 235+87=322).

Sheet: left=AFFORDABLE, right=UNAFFORDABLE, 444×412
Output → docs/store_confirm_shelf_v3/bottom-gems/shelf-expands/round_2.png
"""
import os, sys, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image, ImageDraw, ImageFont
import game.store_cards as sc

SS = sc.SS
m  = sc.m

POP_W, POP_H = 200, 340
CX           = POP_W // 2

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                            = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
NAME_FS, Y_NAME                            = 30, 155
Y_BANNER, BANNER_W                         = 175, 120

# Option E: shelf top rises, bottom stays at 322 — shelf becomes more dominant
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 221, 174, 101
CHIP_CY                            = 240
BTN_W, BTN_H, BTN_RAD              = 76, 30, 9
BTN_CY, BTN_GAP                    = 276, 8
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2
CHIP_W, CHIP_H, CHIP_RAD          = 112, 34, 8

BOT_GEM_R  = 11
BOT_GEM_CY = 316
BOT_GEM_LX = 33
BOT_GEM_RX = 167

PAL   = sc.RARITY["epic"]
PRICE = 500

HAIR_GOLD   = sc.CARD_RING_BRIGHT
_hair_final = None


def _padlock(surf, cx, cy, h, color):
    bw, bh = int(h * 0.92), int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc, math.radians(15), math.radians(165),
                    max(1, int(h * 0.17)))
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.22)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (10, 14, 26), kh, border_radius=1)


def _btn(big, btn_rect, rad, label, font_px, locked=False, is_cancel=False):
    if locked:
        stops   = [(0.0, (58, 60, 74)), (1.0, (40, 42, 54))]
        lab_col = (150, 152, 162)
        sheen   = 10
    elif is_cancel:
        stops   = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
        lab_col = (150, 155, 200)
        sheen   = 14
    else:
        stops   = [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))]
        lab_col = (200, 205, 240)
        sheen   = 22

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)

    if locked:
        sc.bevel_rim(big, btn_rect, rad, (20, 18, 36, 180), (130, 124, 160, 200),
                     w=max(1, m(1.2)))
    else:
        rim_w = m(2.2) if is_cancel else m(2.0)
        sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 230), w=max(1, rim_w))

    lab_font = sc.font(font_px)
    if locked:
        lw = lab_font.size(label)[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.92)
        inner  = m(4)
        grp    = lock_w + inner + lw
        gx     = btn_rect.centerx - grp // 2
        _padlock(big, gx + lock_w // 2, btn_rect.centery, lock_h, lab_col)
        sc.plain_text(big, label, lab_font,
                      (gx + lock_w + inner + lw // 2, btn_rect.centery),
                      lab_col, shadow_a=0, weight=m(0.6))
    else:
        sc.plain_text(big, label, lab_font, btn_rect.center, lab_col,
                      shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def _draw_chip(big, cx, cy, price, affordable):
    global _hair_final
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))
    face_stops = ([(0.0, (18, 20, 50)), (1.0, (10, 11, 30))] if affordable
                  else [(0.0, (28, 28, 50)), (1.0, (18, 18, 36))])
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)

    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 200), w=max(1, m(1.4)))
    else:
        sc.bevel_rim(big, chip, crad, (44, 58, 58, 200), (120, 140, 140, 180),
                     w=max(1, m(1.4)))

    txt      = f"{price:,}"
    num_font = sc.font(22)
    coin_r   = m(15)
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
        num_col = (236, 240, 232)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        pygame.draw.circle(big, (128, 132, 146), (coin_cx, cy), coin_r - m(3),
                           width=max(1, m(1)))
        num_col = (150, 154, 162)
    sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                  shadow_a=0, weight=m(0.8))

    if affordable:
        num_h    = num_font.size(txt)[1]
        baseline = (num_cy - num_h // 2) + num_font.get_ascent()
        hair_h   = m(2)
        hair_y   = baseline + m(3)
        hair     = pygame.Surface((num_w, hair_h), pygame.SRCALPHA)
        hair.fill((*HAIR_GOLD, int(255 * 0.85)))
        big.blit(hair, (num_cx - num_w // 2, hair_y))
        _hair_final = (
            (num_cx - num_w // 2) / SS,
            (num_cx + num_w // 2) / SS,
            (hair_y + hair_h // 2) / SS,
        )


def _draw_shelf(big, affordable):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)

    shelf_stops = ([(0.0, (28, 30, 62)), (1.0, (14, 16, 40))] if affordable
                   else [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))])
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Dark circular seat behind each gem — acts as gem setting in the shelf face
    for gem_cx_abs, gem_cy_abs in [(BOT_GEM_LX, BOT_GEM_CY), (BOT_GEM_RX, BOT_GEM_CY)]:
        local_x = m(gem_cx_abs) - m(SHELF_X)
        local_y = m(gem_cy_abs) - m(SHELF_Y)
        seat_r  = m(14)
        seat_surf = pygame.Surface((seat_r*2+2, seat_r*2+2), pygame.SRCALPHA)
        for ri in range(seat_r, 0, -2):
            alpha = int(90 * (1 - ri / seat_r))
            pygame.draw.circle(seat_surf, (4, 5, 14, alpha),
                               (seat_r+1, seat_r+1), ri)
        shelf.blit(seat_surf, (local_x - seat_r - 1, local_y - seat_r - 1))

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
            a = int(50 * xx / max(1, wall_w - 1))
            pygame.draw.line(lwall, (130, 120, 165, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable)

    buy  = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy.center = (m(BUY_CX), m(BTN_CY))
    can  = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)
    _btn(big, buy, brad, "BUY",    14, locked=not affordable)
    _btn(big, can, brad, "CANCEL", 13, is_cancel=True)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7),
                      (m(CX), m(295)),
                      (150, 176, 176), shadow_a=0)


def _draw_bottom_gems(big, affordable):
    for gem_cx in [m(BOT_GEM_LX), m(BOT_GEM_RX)]:
        if affordable:
            sc._alpha_aura(big, gem_cx, m(BOT_GEM_CY), m(16), PAL["glow"], peak=70, layers=14)
            sc.facet_gem(big, gem_cx, m(BOT_GEM_CY), m(BOT_GEM_R), PAL["gem"], PAL["deep"])
        else:
            sc._alpha_aura(big, gem_cx, m(BOT_GEM_CY), m(16), (90, 92, 110), peak=35, layers=14)
            sc.facet_gem(big, gem_cx, m(BOT_GEM_CY), m(BOT_GEM_R), (80, 82, 100), (50, 52, 66))


def render_popup(name, affordable):
    global _hair_final
    _hair_final = None
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad,
             [(0.0, sc.CARD_T), (1.0, sc.CARD_B)], 255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 55), tray,
                     width=max(1, m(1)), border_radius=rad - m(3))

    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.plain_text(big, name, sc.font(NAME_FS), (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(Y_BANNER), m(BANNER_W), PAL)

    _draw_shelf(big, affordable)
    _draw_bottom_gems(big, affordable)

    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    final = pygame.transform.smoothscale(big, (POP_W, POP_H))
    if affordable and _hair_final is not None:
        x0, x1, hy = _hair_final
        pygame.draw.line(final, HAIR_GOLD, (int(round(x0)), int(round(hy))),
                         (int(round(x1)), int(round(hy))), 1)
    return final


MARGIN, HDR_H, GAP_HDR = 18, 28, 8
CANVAS_W, CANVAS_H     = 444, 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, MARGIN + HDR_H // 2),
          "Bottom gems E: shelf-expands  |  AFFORDABLE / UNAFFORDABLE",
          fill=(180, 200, 240), font=fnt_hdr, anchor="mm")

panels_y    = MARGIN + HDR_H + GAP_HDR
panels_data = []
for px, affordable in [(18, True), (226, False)]:
    surf  = render_popup("TEMPEST", affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panels_data.append((px, affordable, panel))

for px, affordable, panel in panels_data:
    canvas.paste(panel, (px, panels_y))
    bx, by = px + 5, panels_y + 5
    badge  = "E"
    bw     = int(fnt_badge.getlength(badge)) + 8
    draw.rounded_rectangle([bx - 1, by - 1, bx + bw + 1, by + 18], radius=5,
                            fill=(170, 160, 220))
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), badge, fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
      "docs", "store_confirm_shelf_v3", "bottom-gems", "shelf-expands", "round_2.png"))
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

BG  = (8, 8, 20)
aff = panels_data[0][2]
for lbl, gx, gy in [("left", BOT_GEM_LX, BOT_GEM_CY), ("right", BOT_GEM_RX, BOT_GEM_CY)]:
    p = aff.getpixel((gx, gy))
    print(f"  gem {lbl} ({gx},{gy}): {p}  {'ok' if p != BG else 'WARN bg'}")
p = aff.getpixel((BUY_CX, BTN_CY))
print(f"  BUY ({BUY_CX},{BTN_CY}): {p}  {'ok' if p != BG else 'WARN bg'}")
