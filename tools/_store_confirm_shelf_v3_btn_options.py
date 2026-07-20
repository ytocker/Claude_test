"""Button colour exploration for C** hybrid.

6 panels: CURRENT (round_3) + 5 darker options.
All share: original indigo shelf, card-body chip, gold bevel on both buttons.
Only BUY and CANCEL fill colours differ.

Output: docs/store_confirm_shelf_v3/c-orig-bg/btn_options.png
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

SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
CHIP_CY                            = 258
BTN_W, BTN_H, BTN_RAD              = 76, 30, 9
BTN_CY, BTN_GAP                    = 302, 8
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2
CHIP_W, CHIP_H, CHIP_RAD          = 112, 34, 8

PAL   = sc.RARITY["epic"]
PRICE = 500
HAIR_GOLD = sc.CARD_RING_BRIGHT
_hair_final = None

# ── Button colour palettes ─────────────────────────────────────────────────────
# Each entry: (id, name, buy_stops, cancel_stops, buy_label, cancel_label)
OPTIONS = [
    ("0",  "CURRENT",
     [(0.0,(84,78,126)),(1.0,(50,46,82))],
     [(0.0,(68,62,104)),(1.0,(40,36,70))],
     (220,210,240), (168,162,200)),

    ("1",  "DEEP-CARD",
     [(0.0,(38,40,84)),(1.0,(22,24,56))],
     [(0.0,(26,28,64)),(1.0,(14,16,44))],
     (200,205,240), (150,155,200)),

    ("2",  "DARK VIOLET",
     [(0.0,(52,44,80)),(1.0,(32,26,54))],
     [(0.0,(38,32,60)),(1.0,(22,18,40))],
     (215,205,240), (162,154,198)),

    ("3",  "MIDNIGHT BLUE",
     [(0.0,(28,36,90)),(1.0,(16,22,62))],
     [(0.0,(18,26,68)),(1.0,(10,14,46))],
     (196,206,245), (146,155,210)),

    ("4",  "DARK SLATE",
     [(0.0,(44,42,64)),(1.0,(26,24,42))],
     [(0.0,(32,30,48)),(1.0,(18,16,32))],
     (210,208,232), (158,156,190)),

    ("5",  "OBSIDIAN",
     [(0.0,(30,26,52)),(1.0,(16,14,34))],
     [(0.0,(22,18,40)),(1.0,(12,10,26))],
     (205,200,232), (154,148,186)),
]


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
    pygame.draw.rect(surf, (8, 6, 20), kh, border_radius=1)


def _btn(big, btn_rect, rad, label, font_px,
         stops, lab_col, sheen, locked=False):
    if locked:
        l_stops   = [(0.0,(58,60,74)),(1.0,(40,42,54))]
        l_lab_col = (150,152,162)
        l_sheen   = 10
    else:
        l_stops, l_lab_col, l_sheen = stops, lab_col, sheen

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, l_stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=l_sheen)

    if locked:
        sc.bevel_rim(big, btn_rect, rad, (20,18,36,180), (130,124,160,200),
                     w=max(1, m(1.2)))
    else:
        sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 230), w=max(1, m(2.0)))

    lab_font = sc.font(font_px)
    if locked:
        lw = lab_font.size(label)[0]
        lock_h = m(11); lock_w = int(lock_h * 0.92); inner = m(4)
        grp = lock_w + inner + lw
        gx  = btn_rect.centerx - grp // 2
        _padlock(big, gx + lock_w // 2, btn_rect.centery, lock_h, l_lab_col)
        sc.plain_text(big, label, lab_font,
                      (gx + lock_w + inner + lw // 2, btn_rect.centery),
                      l_lab_col, shadow_a=0, weight=m(0.6))
    else:
        sc.plain_text(big, label, lab_font, btn_rect.center, l_lab_col,
                      shadow_a=110, weight=m(0.8), keyline=(8,6,20), kw=m(0.9))


def _draw_chip(big, cx, cy, affordable):
    global _hair_final
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)
    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    face_stops = ([(0.0,(18,20,50)),(1.0,(10,11,30))] if affordable
                  else [(0.0,(28,28,50)),(1.0,(18,18,36))])
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)

    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 200), w=max(1, m(1.4)))
    else:
        sc.bevel_rim(big, chip, crad, (44,58,58,200), (120,140,140,180),
                     w=max(1, m(1.4)))

    txt = f"{PRICE:,}"
    num_font = sc.font(22)
    coin_r = m(15); coin_d = coin_r * 2; gap = m(4)
    num_w = num_font.size(txt)[0]
    total = coin_d + gap + num_w
    left = cx - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2
    num_cy = cy + m(3)

    if affordable:
        sc.coin_glyph(big, coin_cx, cy, coin_r)
        num_col = (236, 240, 232)
    else:
        pygame.draw.circle(big, (150,152,162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108,112,126), (coin_cx, cy), coin_r, width=max(1,m(1)))
        pygame.draw.circle(big, (128,132,146), (coin_cx, cy), coin_r-m(3), width=max(1,m(1)))
        num_col = (150, 154, 162)
    sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                  shadow_a=0, weight=m(0.8))

    if affordable:
        num_h = num_font.size(txt)[1]
        baseline = (num_cy - num_h // 2) + num_font.get_ascent()
        hair_h = m(2); hair_y = baseline + m(3)
        hair = pygame.Surface((num_w, hair_h), pygame.SRCALPHA)
        hair.fill((*HAIR_GOLD, int(255 * 0.85)))
        big.blit(hair, (num_cx - num_w // 2, hair_y))
        _hair_final = ((num_cx - num_w // 2) / SS,
                       (num_cx + num_w // 2) / SS,
                       (hair_y + hair_h // 2) / SS)


def _draw_shelf(big, affordable, buy_stops, can_stops, buy_lab, can_lab):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)
    shelf_stops = ([(0.0,(28,30,62)),(1.0,(14,16,40))] if affordable
                   else [(0.0,(30,32,52)),(0.5,(22,22,42)),(1.0,(14,14,30))])
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255,255,255,255), smask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(smask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    lip = (115,106,140) if affordable else (62,62,86)
    pygame.draw.line(shelf, lip, (0,0), (shelf_rect.w-1, 0), max(1,m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0,0,0,a), (0,yy), (shelf_rect.w-1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        for col_fn, bx_ in [
            (lambda xx: (130,120,165,int(50*xx/max(1,wall_w-1))), m(CARD_X)),
            (lambda xx: (0,0,0,int(50*(1-xx/max(1,wall_w-1)))), m(SHELF_X+SHELF_W)),
        ]:
            _w = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
            for xx in range(wall_w):
                pygame.draw.line(_w, col_fn(xx), (xx,0), (xx, wall_draw_h-1))
            big.blit(_w, (bx_, m(SHELF_Y)))

    _draw_chip(big, m(CX), m(CHIP_CY), affordable)

    buy = pygame.Rect(0,0,m(BTN_W),m(BTN_H)); buy.center = (m(BUY_CX),m(BTN_CY))
    can = pygame.Rect(0,0,m(BTN_W),m(BTN_H)); can.center = (m(CAN_CX),m(BTN_CY))
    brad = m(BTN_RAD)
    _btn(big, buy, brad, "BUY",    14, buy_stops, buy_lab, 22, locked=not affordable)
    _btn(big, can, brad, "CANCEL", 13, can_stops, can_lab, 14)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX),m(322)),
                      (150,152,162), shadow_a=0)


def render_popup(affordable, buy_stops, can_stops, buy_lab, can_lab):
    global _hair_final
    _hair_final = None
    big = pygame.Surface((POP_W*SS, POP_H*SS), pygame.SRCALPHA)

    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad,
             [(0.0,sc.CARD_T),(1.0,sc.CARD_B)], 255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4,5,16), rect, width=max(1,m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT,230), w=max(1,m(1.9)))
    tray = rect.inflate(-m(8),-m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT,55), tray,
                     width=max(1,m(1)), border_radius=rad-m(3))

    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.plain_text(big, "TEMPEST", sc.font(NAME_FS), (m(CX),m(Y_NAME)), (250,248,240),
                  shadow_a=160, weight=m(0.9), keyline=(6,6,16), kw=m(1.0))
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(Y_BANNER), m(BANNER_W), PAL)

    _draw_shelf(big, affordable, buy_stops, can_stops, buy_lab, can_lab)

    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss+m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss+m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss*1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    final = pygame.transform.smoothscale(big, (POP_W, POP_H))
    if affordable and _hair_final is not None:
        x0, x1, hy = _hair_final
        pygame.draw.line(final, HAIR_GOLD,
                         (int(round(x0)), int(round(hy))),
                         (int(round(x1)), int(round(hy))), 1)
    return final


# ── Showcase canvas ───────────────────────────────────────────────────────────
PANEL_W, PANEL_H = 200, 355
MARGIN = 20; GAP = 8; HDR_H = 40; FOOT_H = 36
N = len(OPTIONS)

CANVAS_W = MARGIN + N * PANEL_W + (N-1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_lbl   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    fnt_foot  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 9)
except Exception:
    fnt_hdr = fnt_lbl = fnt_badge = fnt_foot = ImageFont.load_default()

hx = CANVAS_W // 2; hy = MARGIN + HDR_H // 2
draw.text((hx, hy-8), "BUTTON COLOUR OPTIONS — DARKER VARIANTS",
          fill=(210,205,240), font=fnt_hdr, anchor="mm")
draw.text((hx, hy+8), "0=CURRENT  ·  1–5=darker options  ·  AFFORDABLE STATE",
          fill=(130,125,155), font=fnt_lbl, anchor="mm")

BTN_CY_355 = round(302 * 355 / 340)
panels_ok  = True

for i, (badge, name, buy_s, can_s, buy_l, can_l) in enumerate(OPTIONS):
    surf  = render_popup(True, buy_s, can_s, buy_l, can_l)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panel = panel.resize((PANEL_W, PANEL_H), Image.LANCZOS)

    px = MARGIN + i * (PANEL_W + GAP)
    py = MARGIN + HDR_H + GAP
    canvas.paste(panel, (px, py))

    # ID badge
    bw = int(fnt_badge.getlength(badge)) + 10; bh = 19
    bx_, by_ = px+5, py+5
    draw.rounded_rectangle([bx_-1, by_-1, bx_+bw+1, by_+bh+1], radius=5,
                            fill=(200,190,240))
    draw.rounded_rectangle([bx_, by_, bx_+bw, by_+bh], radius=4, fill=(24,22,38))
    draw.text((bx_+5, by_+bh//2), badge, fill=(236,228,255),
              font=fnt_badge, anchor="lm")

    # Footer
    fy1 = py + PANEL_H + 6; fy2 = fy1 + 16
    cx_ = px + PANEL_W // 2
    col1 = (255,220,100) if badge == "0" else (200,195,235)
    draw.text((cx_, fy1), name,    fill=col1,          font=fnt_lbl,  anchor="mm")
    draw.text((cx_, fy2), "darker" if badge != "0" else "original",
              fill=(130,125,155), font=fnt_foot, anchor="mm")

    # Verify
    sample_x = px + 58; sample_y = py + BTN_CY_355
    px_val = canvas.getpixel((sample_x, sample_y))
    ok = px_val != (8,8,20)
    panels_ok = panels_ok and ok
    print(f"  {badge} ({sample_x},{sample_y}) = {px_val}  {'OK' if ok else 'WARN'}")

OUT = "docs/store_confirm_shelf_v3/c-orig-bg/btn_options.png"
canvas.save(OUT)
print(f"\nSaved {OUT}  ({CANVAS_W}×{CANVAS_H})")
print(f"All panels non-background: {'YES' if panels_ok else 'SOME FAILED'}")
