#!/usr/bin/env python3
"""Figure: 4 card states (2×2 grid) + buy-confirmation popup, side by side."""
import os, sys, tempfile
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
import game.store_catalog as catalog
from game.draw import UI_CREAM, NEAR_BLACK, WHITE, lerp_color
from game.surprise_box_variants import _draw_qmark
from game.store import _confirm_tier_banner

sd.load()
SID    = "skin_mummy"
CW, CH = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324 × 200
RECT   = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                     CW - 2 * sc.m(sc._INSET), CH - 2 * sc.m(sc._INSET))
pal    = sc.RARITY[catalog.rarity(SID)]

tmp = tempfile.mkdtemp()

def surf_to_pil(surf, name):
    from PIL import Image
    path = os.path.join(tmp, f"{name}.png")
    pygame.image.save(surf, path)
    return Image.open(path).convert("RGB")


# ── Render 4 card states ──────────────────────────────────────────────────────

def card(label, equipped, owned, balance=None):
    sc._card_cache.clear()
    if balance is not None:
        _orig = sd.balance; sd.balance = lambda: balance
    s = pygame.Surface((CW, CH), pygame.SRCALPHA)
    sc.draw_card(s, SID, RECT, equipped, False, owned=owned)
    if balance is not None:
        sd.balance = _orig
    sc._card_cache.clear()
    return surf_to_pil(s, label)

cards = {
    "unaffordable": card("unaffordable", False, False, balance=0),
    "affordable":   card("affordable",   False, False, balance=999_999),
    "owned":        card("owned",        False, True),
    "equipped":     card("equipped",     True,  False),
}

GRID = [
    ("unaffordable", "UNAFFORDABLE", "(grey price tag)"),
    ("affordable",   "AFFORDABLE",   "(cream price tag)"),
    ("owned",        "OWNED",        "(gem badge)"),
    ("equipped",     "EQUIPPED",     "(check tag + frame)"),
]


# ── Render buy-confirmation popup (SS=2 surface, then smoothscale) ────────────

def render_popup(affordable):
    m  = sc.m
    SS = sc.SS
    POP_W, POP_H = 200, 340
    CX = POP_W // 2

    CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
    R_HERO, DISC_CY                             = 41, 104
    GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
    NAME_FS, Y_NAME                             = 30, 155
    Y_BANNER, BANNER_W, BANNER_H                = 175, 120, 22
    Y_CHIP, CHIP_H                              = 229, 28
    Y_BTN, BTN_H, BTN_W                        = 273, 30, 136
    Y_CANCEL, CANCEL_H, CANCEL_W               = 308, 22, 80

    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    rect = pygame.Rect(m(CARD_X), m(CARD_TOP), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(
        sc.vgrad_stops(rect.w, rect.h, rad,
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

    name  = sc._name(SID)
    price = catalog.cost(SID)
    sc.plain_text(big, name, sc.font(NAME_FS), (m(CX), m(Y_NAME)),
                  (250, 248, 240), shadow_a=160, weight=m(0.9),
                  keyline=(6, 6, 16), kw=m(1.0))

    _confirm_tier_banner(big, CX, Y_BANNER, BANNER_W, BANNER_H,
                         catalog.rarity(SID).upper(), pal)

    sc.price_chip(big, m(CX), m(Y_CHIP), f"{price:,}", m(CHIP_H),
                  affordable=affordable)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH COINS", sc.font(9), (m(CX), m(251)),
                      (150, 166, 190), shadow_a=0)

    h_btn = m(BTN_H); w_btn = m(BTN_W)
    btn_r = pygame.Rect(m(CX) - w_btn // 2, m(Y_BTN) - h_btn // 2, w_btn, h_btn)
    if affordable:
        top_c = lerp_color(pal["gem"], WHITE, 0.18)
        bot_c = lerp_color(pal["deep"], (4, 4, 12), 0.4)
        rim_c = lerp_color(pal["gem"], WHITE, 0.45)
        sc.chip_body(big, btn_r, h_btn // 2, top_c, bot_c, (4, 4, 12), rim_c, gloss=72)
        sc.plain_text(big, "CONFIRM", sc.font(13), btn_r.center, (255, 255, 255),
                      shadow_a=180, tracking=m(1.4), weight=m(1.0),
                      keyline=lerp_color(pal["deep"], (0, 0, 0), 0.5), kw=m(1.0))
    else:
        sc.chip_body(big, btn_r, h_btn // 2,
                     (60, 56, 76), (36, 34, 52), (20, 18, 32), (100, 96, 120), gloss=40)
        sc.plain_text(big, "CONFIRM", sc.font(13), btn_r.center, (120, 116, 134), shadow_a=0)

    h_can = m(CANCEL_H); w_can = m(CANCEL_W)
    can_r = pygame.Rect(m(CX) - w_can // 2, m(Y_CANCEL) - h_can // 2, w_can, h_can)
    sc.chip_body(big, can_r, h_can // 2,
                 (70, 62, 80), (44, 38, 56), (30, 26, 40), (120, 112, 132), gloss=30)
    sc.plain_text(big, "CANCEL", sc.font(11), can_r.center, UI_CREAM, shadow_a=0)

    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), pal["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), pal["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=pal["gem"], ring_a=50)
    sc.blit_thumb(big, SID, cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=pal["gem"])

    pop = pygame.transform.smoothscale(big, (POP_W, POP_H))
    return surf_to_pil(pop, f"popup_{'aff' if affordable else 'unaff'}")

popup_affordable   = render_popup(affordable=True)
popup_unaffordable = render_popup(affordable=False)


# ── Compose PIL canvas ────────────────────────────────────────────────────────
from PIL import Image, ImageDraw, ImageFont

try:
    font_hdr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    font_lbl = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    font_sec = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
except Exception:
    font_hdr = font_lbl = font_sub = font_sec = ImageFont.load_default()

BG    = (8,  8,  20)
GOLD  = (220, 190, 100)
CREAM = (200, 185, 140)
DIM   = (90,  85,  70)
GRN   = (140, 200, 140)
CYAN  = (130, 200, 200)

MARGIN  = 20
GAP     = 10
LABEL_H = 36
HDR_H   = 44
DIVIDER = 28      # gap between card grid and popup columns
SEC_H   = 22      # section sub-header height

POP_W_D, POP_H_D = 200, 340   # popup display size

# Card grid: 2 cols × 2 rows
CARD_GRID_COLS = 2
CARD_GRID_ROWS = 2
GRID_W = CARD_GRID_COLS * CW + (CARD_GRID_COLS - 1) * GAP
GRID_H = CARD_GRID_ROWS * (CH + LABEL_H) + (CARD_GRID_ROWS - 1) * GAP

# Two popups side by side (affordable + unaffordable)
POP_PAIR_W = 2 * POP_W_D + GAP
POP_PAIR_H = SEC_H + GAP + POP_H_D

CONTENT_H = max(GRID_H, POP_PAIR_H)

canvas_w = MARGIN + GRID_W + DIVIDER + POP_PAIR_W + MARGIN
canvas_h = MARGIN + HDR_H + GAP + SEC_H + GAP + CONTENT_H + MARGIN

canvas = Image.new("RGB", (canvas_w, canvas_h), BG)
draw   = ImageDraw.Draw(canvas)

# Header
draw.text((canvas_w // 2, MARGIN + HDR_H // 2),
          "STORE CARD — ALL STATES + BUY POPUP",
          fill=GOLD, font=font_hdr, anchor="mm")

content_y = MARGIN + HDR_H + GAP

# ── Section headers ──────────────────────────────────────────────────────────
cards_x0    = MARGIN
popups_x0   = MARGIN + GRID_W + DIVIDER

draw.text((cards_x0 + GRID_W // 2,  content_y + SEC_H // 2),
          "CARD STATES", fill=CREAM, font=font_sec, anchor="mm")
draw.text((popups_x0 + POP_PAIR_W // 2, content_y + SEC_H // 2),
          "BUY POPUP (AFFORDABLE / NOT ENOUGH COINS)",
          fill=CREAM, font=font_sec, anchor="mm")

grid_y = content_y + SEC_H + GAP

# ── 2×2 card grid ────────────────────────────────────────────────────────────
for idx, (key, title, sub) in enumerate(GRID):
    col = idx % 2
    row = idx // 2
    x0  = cards_x0 + col * (CW + GAP)
    y0  = grid_y   + row * (CH + LABEL_H + GAP)
    canvas.paste(cards[key], (x0, y0))
    label_cy = y0 + CH + LABEL_H // 2
    title_col = GRN if key == "owned" else CREAM
    draw.text((x0 + CW // 2, label_cy - 9), title, fill=title_col, font=font_lbl, anchor="mm")
    draw.text((x0 + CW // 2, label_cy + 9), sub,   fill=DIM,        font=font_sub, anchor="mm")

# ── Popup pair ────────────────────────────────────────────────────────────────
pop_y = grid_y
for i, (pop_img, label) in enumerate([
        (popup_affordable,   "AFFORDABLE"),
        (popup_unaffordable, "NOT ENOUGH COINS")]):
    px = popups_x0 + i * (POP_W_D + GAP)
    canvas.paste(pop_img, (px, pop_y))
    draw.text((px + POP_W_D // 2, pop_y + POP_H_D + 12),
              label, fill=CYAN, font=font_sub, anchor="mm")

out_dir = "docs/store_owned_v2"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "card_states_and_popup.png")
canvas.save(out)
print(f"saved {out} ({canvas.width}x{canvas.height})")
