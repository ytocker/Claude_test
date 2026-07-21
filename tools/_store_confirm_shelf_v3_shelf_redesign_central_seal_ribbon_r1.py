"""Shelf-redesign concept 3: central-seal-ribbon (R1).

The shelf collapses to a thin horizontal ribbon. The price chip becomes a
circular/oval medallion that protrudes above the ribbon's top edge as the
focal point; BUY and CANCEL are slim flanking buttons embedded in the ribbon
on either side of the medallion.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE, 444x412
Output -> docs/store_confirm_shelf_v3/shelf-redesign/central-seal-ribbon/round_1.png
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

SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 246, 174, 44   # thin ribbon; shelf_bottom=290
# Flanking buttons — slim, inside ribbon
BTN_W, BTN_H, BTN_RAD = 44, 28, 8
BTN_CY    = 264           # vertically centred in ribbon (mid of 246+44=290 → 268; nudge down)
BUY_CX    = 31            # left button centre
CAN_CX    = 169           # right button centre

# Medallion (price chip) — protrudes above ribbon
CHIP_W    = 80
CHIP_H    = 42
CHIP_RAD  = 12
CHIP_CY   = 246           # centre at ribbon TOP edge → top=225, bottom=267; 21px above ribbon

BOT_GEM_R  = 11
BOT_GEM_CY = 309
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
        # Subdued secondary: dimmer fill + softer sheen than BUY.
        stops   = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
        lab_col = (150, 155, 200)
        sheen   = 14
    else:
        # Primary CTA: brighter fill stops + stronger sheen so BUY leads.
        stops   = [(0.0, (48, 52, 104)), (1.0, (28, 30, 68))]
        lab_col = (214, 220, 250)
        sheen   = 30

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)

    if locked:
        sc.bevel_rim(big, btn_rect, rad, (20, 18, 36, 180), (130, 124, 160, 200),
                     w=max(1, m(1.2)))
    else:
        # Primary gets a marginally brighter rim than the secondary.
        rim_w = m(2.2) if is_cancel else m(2.4)
        rim_bright = (*sc.CARD_RING_BRIGHT, 200) if is_cancel else (*sc.CARD_RING_BRIGHT, 255)
        sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP, rim_bright, w=max(1, rim_w))

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


def _draw_shelf(big, affordable):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)

    # Thin ribbon shelf
    shelf_stops = ([(0.0, (28, 30, 62)), (1.0, (14, 16, 40))] if affordable
                   else [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))])
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(12), peak=28)
    lip = (115, 106, 140) if affordable else (62, 62, 86)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Flanking buttons (slim, text-focused) — drawn BEFORE medallion
    buy  = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy.center = (m(BUY_CX), m(BTN_CY))
    can  = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)
    _btn(big, buy, brad, "BUY",    13, locked=not affordable)
    _btn(big, can, brad, "CANCEL", 11, is_cancel=True)

    # Medallion (price chip) — drawn LAST in _draw_shelf so it renders on top of ribbon
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (m(CX), m(CHIP_CY))
    crad = m(CHIP_RAD)

    # Medallion drop shadow falls on ribbon
    sc.drop_shadow(big, chip, crad, blur=m(5), alpha=120, dy=m(3))

    face_stops = ([(0.0, (50, 52, 98)), (1.0, (32, 34, 72))] if affordable
                  else [(0.0, (44, 46, 70)), (1.0, (28, 28, 50))])
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)
    sc.top_sheen(big, chip, crad, m(14), peak=40 if affordable else 20)

    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 240), w=max(1, m(1.8)))
    else:
        sc.bevel_rim(big, chip, crad, (44, 58, 58, 200), (120, 140, 140, 180),
                     w=max(1, m(1.4)))

    # Coin + price inside medallion (same as base _draw_chip layout)
    txt      = f"{PRICE:,}"
    num_font = sc.font(20)
    coin_r   = m(13)
    coin_d   = coin_r * 2
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_d + gap + num_w
    left     = m(CX) - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_d + gap + num_w // 2
    num_cy   = m(CHIP_CY) + m(2)

    if affordable:
        sc.coin_glyph(big, coin_cx, m(CHIP_CY), coin_r)
        num_col = (236, 240, 232)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, m(CHIP_CY)), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, m(CHIP_CY)), coin_r, width=max(1, m(1)))
        num_col = (150, 154, 162)
    sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                  shadow_a=0, weight=m(0.7))


def _draw_bottom_gems(big, affordable):
    for gem_cx in [m(BOT_GEM_LX), m(BOT_GEM_RX)]:
        if affordable:
            sc._alpha_aura(big, gem_cx, m(BOT_GEM_CY), m(16), PAL["glow"], peak=60, layers=14)
            sc.facet_gem(big, gem_cx, m(BOT_GEM_CY), m(BOT_GEM_R), PAL["gem"], PAL["deep"])
        else:
            sc._alpha_aura(big, gem_cx, m(BOT_GEM_CY), m(16), (90, 92, 110), peak=35, layers=14)
            sc.facet_gem(big, gem_cx, m(BOT_GEM_CY), m(BOT_GEM_R), (80, 82, 100), (50, 52, 66))


def render_popup(name, affordable):
    global _hair_final
    _hair_final = None
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # 1. Card body + ring + tray border
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

    # 2. Top gems (facet_gem only)
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])

    # 3. Name text + ribbon lozenge
    sc.plain_text(big, name, sc.font(NAME_FS), (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(Y_BANNER), m(BANNER_W), PAL)

    # 4. Shelf (ribbon + flanking buttons + medallion)
    _draw_shelf(big, affordable)

    # 5. Bottom frame gems
    _draw_bottom_gems(big, affordable)

    # 6. Disc aura + cabochon + thumb + glass — LAST
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
          "central-seal-ribbon  |  AFFORDABLE / UNAFFORDABLE",
          fill=(180, 200, 240), font=fnt_hdr, anchor="mm")

panels_y    = MARGIN + HDR_H + GAP_HDR
panels_data = []
for px, affordable in [(18, True), (226, False)]:
    surf  = render_popup("TEMPEST", affordable)
    bg    = pygame.Surface((POP_W, POP_H))
    bg.fill((8, 8, 20))
    bg.blit(surf, (0, 0))
    raw   = pygame.image.tostring(bg, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panels_data.append((px, affordable, panel))

for px, affordable, panel in panels_data:
    canvas.paste(panel, (px, panels_y))
    bx, by = px + 5, panels_y + 5
    badge  = "3"
    bw     = int(fnt_badge.getlength(badge)) + 8
    draw.rounded_rectangle([bx - 1, by - 1, bx + bw + 1, by + 18], radius=5,
                            fill=(170, 160, 220))
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), badge, fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
      "docs", "store_confirm_shelf_v3", "shelf-redesign", "central-seal-ribbon", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# PIL verification
img    = Image.open(OUT)
seal   = img.getpixel((18 + 100, 54 + 246))   # medallion centre (at ribbon top)
btn    = img.getpixel((18 + 31,  54 + 264))   # BUY button centre
gem_l  = img.getpixel((18 + 33,  54 + 309))   # left bottom gem
print(f"size:{img.size}  seal:{seal}  btn:{btn}  gem_l:{gem_l}")
