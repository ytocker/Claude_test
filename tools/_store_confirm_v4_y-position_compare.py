"""Comparison figure: item name text position options.

Rows   → Y_NAME value (168 current, then +6/+12/+18).
Columns → 4 representative name cases.
Output  → docs/store_confirm_popup_v4/y-position/compare.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc

SS   = sc.SS    # 2
m    = sc.m     # round(x*2)

POP_W, POP_H = 200, 340
CX            = POP_W // 2

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                             = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
BANNER_W                                    = 120
SHELF_X, SHELF_Y, SHELF_W, SHELF_H         = 13, 235, 174, 87
CHIP_CY                                     = 258
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP    = 76, 30, 9, 302, 8
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2

PAL   = sc.RARITY["epic"]
PRICE = 500

# ── helpers that mirror production code ──────────────────────────────────────

def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()

def _draw_btn(big, btn_rect, label, locked=False):
    rad  = m(BTN_RAD)
    stops   = ([(0.0,(42,40,50)),(1.0,(28,26,36))] if locked
                else [(0.0,(84,78,126)),(1.0,(50,46,82))])
    lab_col = (90, 88,108) if locked else (220,210,240)
    sheen   = 12 if locked else 28
    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)
    sc.bevel_rim(big, btn_rect, rad, (20,18,36,180), (130,124,160,200), w=max(1,m(1.2)))
    sc.plain_text(big, label, sc.font(13), btn_rect.center, lab_col,
                  shadow_a=110, weight=m(0.8), keyline=(18,16,32), kw=m(0.9))

def _draw_chip(big):
    CHIP_W, CHIP_H, CHIP_RAD = 120, 36, 8
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (m(CX), m(CHIP_CY))
    crad = m(CHIP_RAD)
    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad,
             [(0.0,(235,220,175)),(1.0,(205,190,145))], 255), chip.topleft)
    pygame.draw.rect(big, (120,74,14), chip, width=max(1,m(1)), border_radius=crad)
    txt      = f"{PRICE:,}"
    num_font = sc.font(22)
    coin_r   = m(14)
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_r*2 + gap + num_w
    left     = m(CX) - total//2
    coin_cx  = left + coin_r
    num_cx   = left + coin_r*2 + gap + num_w//2
    sc.coin_glyph(big, coin_cx, m(CHIP_CY), coin_r)
    sc.plain_text(big, txt, num_font, (num_cx, m(CHIP_CY)+m(3)), (52,28,4),
                  shadow_a=0, weight=m(0.8))

# ── main popup renderer (parametric base_y) ───────────────────────────────────

def render_popup(name, base_y):
    big = pygame.Surface((POP_W*SS, POP_H*SS), pygame.SRCALPHA)

    # card body
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad,
             [(0.0,sc.CARD_T),(1.0,sc.CARD_B)], 255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4,5,16), rect, width=max(1,m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT,230), w=max(1,m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT,55), tray,
                     width=max(1,m(1)), border_radius=rad-m(3))

    # corner gems
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])

    # name + banner (parametric)
    safe_w = m(168)
    nf30   = sc.font(30)
    if _nw(name, nf30) <= safe_w:
        nf33 = sc.font(33)
        draw_f = nf33 if _nw(name, nf33) <= safe_w else nf30
        sc.plain_text(big, name, draw_f, (m(CX), m(base_y)), (250,248,240),
                      shadow_a=160, weight=m(0.9), keyline=(6,6,16), kw=m(1.0))
        banner_y = base_y + 20
    else:
        spaces = [i for i,c in enumerate(name) if c == ' ']
        if spaces:
            best = min(spaces, key=lambda i: max(_nw(name[:i],nf30), _nw(name[i+1:],nf30)))
            l1, l2 = name[:best], name[best+1:]
        else:
            bi, bm = 1, float('inf')
            for i in range(1, len(name)):
                if name[i-1]=='-' or name[i]=='-':
                    continue
                mw = max(_nw(name[:i]+'-',nf30), _nw(name[i:],nf30))
                if mw < bm:
                    bm, bi = mw, i
            l1, l2 = name[:bi]+'-', name[bi:]
        sc.plain_text(big, l1, sc.font(30), (m(CX), m(base_y-11)), (250,248,240),
                      shadow_a=160, weight=m(0.9), keyline=(6,6,16), kw=m(1.0))
        sc.plain_text(big, l2, sc.font(27), (m(CX), m(base_y+11)), (250,248,240),
                      shadow_a=120, weight=m(0.8), keyline=(6,6,16), kw=m(1.0))
        banner_y = base_y + 40

    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(banner_y), m(BANNER_W), PAL)

    # shelf
    shelf_rect  = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad   = m(CARD_RAD)
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                           [(0.0,(28,30,62)),(1.0,(14,16,40))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255,255,255,255), smask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(smask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115,106,140), (0,0), (shelf_rect.w-1,0), max(1,m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120*(1-yy/m(6)))
        pygame.draw.line(seat, (0,0,0,a), (0,yy), (shelf_rect.w-1,yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y-m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # coin chip
    _draw_chip(big)

    # buttons
    buy_r = pygame.Rect(0,0,m(BTN_W),m(BTN_H)); buy_r.center = (m(BUY_CX),m(BTN_CY))
    can_r = pygame.Rect(0,0,m(BTN_W),m(BTN_H)); can_r.center = (m(CAN_CX),m(BTN_CY))
    _draw_btn(big, buy_r, "BUY")
    _draw_btn(big, can_r, "CANCEL")

    # disc + aura + thumb (last)
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss+m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss+m(20), PAL["glow"], peak=70,  layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss*1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))

# ── layout ───────────────────────────────────────────────────────────────────

Y_OPTIONS = [
    (168, "Y=168  ★ current"),
    (174, "Y=174  (+6)"),
    (180, "Y=180  (+12)"),
    (186, "Y=186  (+18)"),
]

COLUMNS = [
    ("A", "MUMMY",          "SHORT · f33"),
    ("B", "MEGA DAD",       "MED · f30 guard"),
    ("C", "TEMPEST CONDOR", "LONG · space split"),
    ("D", "BASKETBALL",     "LONG · hyphen"),
]

MARGIN      = 18
ROW_LBL_W   = 120
GAP_C       = 8
GAP_R       = 12
COL_HDR_H   = 36
ROW_HDR_H   = 0   # labels are in the left strip

N_ROWS = len(Y_OPTIONS)
N_COLS = len(COLUMNS)

CANVAS_W = MARGIN + ROW_LBL_W + GAP_C + N_COLS*POP_W + (N_COLS-1)*GAP_C + MARGIN
CANVAS_H = MARGIN + COL_HDR_H + GAP_R + N_ROWS*POP_H + (N_ROWS-1)*GAP_R + MARGIN

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

# PIL fonts
try:
    fnt_hdr  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_lbl  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
    fnt_sub  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",      10)
    fnt_badge= ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
except Exception:
    fnt_hdr = fnt_lbl = fnt_sub = fnt_badge = ImageFont.load_default()

# Column headers
for col_i, (badge_id, case_name, case_label) in enumerate(COLUMNS):
    px = MARGIN + ROW_LBL_W + GAP_C + col_i*(POP_W+GAP_C) + POP_W//2
    py = MARGIN + COL_HDR_H//2
    draw.text((px, py-8), case_name,  fill=(210,205,240), font=fnt_lbl,  anchor="mm")
    draw.text((px, py+7), case_label, fill=(130,125,155), font=fnt_sub,  anchor="mm")

# Rows
for row_i, (base_y, row_label) in enumerate(Y_OPTIONS):
    ry = MARGIN + COL_HDR_H + GAP_R + row_i*(POP_H+GAP_R)

    # row label (left strip, vertically centred)
    lx = MARGIN + ROW_LBL_W//2
    ly = ry + POP_H//2
    is_current = (base_y == 168)
    lbl_col = (255, 220, 100) if is_current else (190, 185, 220)
    draw.text((lx, ly), row_label, fill=lbl_col, font=fnt_lbl, anchor="mm")

    for col_i, (badge_id, name, _) in enumerate(COLUMNS):
        px = MARGIN + ROW_LBL_W + GAP_C + col_i*(POP_W+GAP_C)

        # render popup panel
        popup_surf = render_popup(name, base_y)
        raw   = pygame.image.tostring(popup_surf, "RGB")
        panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
        canvas.paste(panel, (px, ry))

        # ID badge (top-left, dark pill)
        badge_txt = badge_id
        bx, by    = px+5, ry+5
        bw, bh    = fnt_badge.getlength(badge_txt)+8, 17
        draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=4,
                                fill=(24,22,38))
        draw.text((bx+4, by+bh//2), badge_txt, fill=(230,225,245),
                  font=fnt_badge, anchor="lm")

        # Y indicator line on the panel (thin horizontal rule at the name Y)
        # Draw a subtle tick on the right edge of the panel to show exact name Y
        tick_y = ry + base_y
        draw.line([(px+POP_W-6, tick_y), (px+POP_W-1, tick_y)],
                  fill=(255,200,60,180), width=1)

    print(f"  row Y={base_y:<3}  banner_gap_1line={base_y+20-base_y}  "
          f"banner_2line_top={base_y+40}  shelf_gap={235-(base_y+40)}px")

OUT = "docs/store_confirm_popup_v4/y-position/compare.png"
canvas.save(OUT)
print(f"\nSaved  {OUT}  ({CANVAS_W}×{CANVAS_H})")
