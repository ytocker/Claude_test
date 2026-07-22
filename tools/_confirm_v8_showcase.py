#!/usr/bin/env python3
"""
confirm_purchase_v8  ·  showcase assembly

6 panels: BEFORE (v5_integration current design) + 5 round_2 concepts.
Each panel: EPIC tier popup cropped from each 3-tier strip → scaled to 200×355.
Canvas: (8,8,20) BG · 200×355 panels · 12px gaps · 20px margins · 50px header · 28px footer.
"""
import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc
from game.store_cards import (
    vgrad_stops, plain_text, m, SS, font,
    CABO_LO, CABO_HI, CARD_T, CARD_B, CARD_RING_BRIGHT, CARD_RING_DEEP,
)
from game.hud import _font
from game.draw import lerp_color, NEAR_BLACK, WHITE
from PIL import Image

# ── mandatory gloss_sweep patch ───────────────────────────────────────────────
def _gloss_sweep_fixed(surf, rect, radius, peak=120):
    sweep = pygame.Surface(rect.size, pygame.SRCALPHA)
    h = max(1, rect.h)
    for y in range(h):
        v = int(peak * (1 - y / h) ** 2.4)
        if v <= 0:
            continue
        pygame.draw.line(sweep, (v, v, v, 255), (0, y), (rect.w, y))
    sm = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(sm, (255, 255, 255, 255), sm.get_rect(), border_radius=radius)
    sweep.blit(sm, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sweep, rect.topleft, special_flags=pygame.BLEND_ADD)

sc.gloss_sweep = _gloss_sweep_fixed

# ── palette used for BEFORE render (EPIC tier) ────────────────────────────────
EPIC_PAL = {"gem": (194, 122, 248), "glow": (150, 60, 220), "deep": (44, 10, 80)}
EPIC_PRICE = "1,400"
EPIC_SID   = "skin_prism"
EPIC_NAME  = "PRISM"
EPIC_WORD  = "EPIC"

# ── shared popup geometry ─────────────────────────────────────────────────────
POP_W, POP_H = 260, 442
CX = 130
CARD_X, CARD_TOP_Y, CARD_W, CARD_H, CARD_RAD = 10, 127, 240, 299, 23
DISC_CY, DISC_R = 135, 53
GEM_L_X, GEM_R_X, GEM_CY, GEM_R = 43, 217, 152, 14


# ── shared chrome (same as all r2 scripts) ────────────────────────────────────
def card_body(big):
    rect = pygame.Rect(m(CARD_X), m(CARD_TOP_Y), m(CARD_W), m(CARD_H))
    rad  = m(CARD_RAD)
    sc.drop_shadow(big, rect, rad, blur=m(8), alpha=165, dy=m(4))
    big.blit(vgrad_stops(rect.w, rect.h, rad,
                         [(0.0, CARD_T), (1.0, CARD_B)], 255, gamma=1.15), rect.topleft)
    sc.top_sheen(big, rect, rad, m(30), peak=56)
    pygame.draw.rect(big, (4, 5, 16), rect, width=max(1, m(2)), border_radius=rad)
    sc.bevel_rim(big, rect, rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 230), w=max(1, m(1.9)))
    tray = rect.inflate(-m(8), -m(8))
    pygame.draw.rect(big, (*CARD_RING_BRIGHT, 55), tray, width=max(1, m(1)),
                     border_radius=rad - m(3))


def corner_gems(big, pal):
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def name_text(big, name):
    nfs  = 45
    nfnt = font(nfs)
    mw   = m(CARD_W - 20)
    while sc._glyph_base(name, nfnt, 0).get_width() > mw and nfs > 24:
        nfs -= 1
        nfnt = font(nfs)
    plain_text(big, name, nfnt, (m(CX), m(213)), (250, 248, 240),
               shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))


def rarity_banner(big, tier_word, pal):
    cx, cy_log, w_log, h_log = CX, 247, 156, 23
    f   = font(h_log * 0.58)
    tw  = sc._glyph_base(tier_word, f, m(1.4)).get_width()
    w   = min(m(w_log), tw + m(16) * 2)
    h   = m(h_log)
    pt  = h // 2
    x0, y0 = m(cx) - w // 2, m(cy_log) - h // 2
    poly = [(0,h//2),(pt,0),(w-pt,0),(w,h//2),(w-pt,h),(pt,h)]
    top  = lerp_color(pal["gem"], WHITE, 0.1)
    bot  = lerp_color(pal["deep"], NEAR_BLACK, 0.05)
    body = vgrad_stops(w, h, 0, [(0.0,top),(0.5,pal["glow"]),(1.0,bot)], 255, gamma=1.08)
    pmask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(pmask, (255,255,255,255), poly)
    body.blit(pmask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sh = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (0,0,0,120), poly)
    big.blit(sh, (x0, y0 + m(2)))
    big.blit(body, (x0, y0))
    abspoly = [(x0+px, y0+py) for px, py in poly]
    pygame.draw.polygon(big, (4,5,16), abspoly, width=max(1, m(1.4)))
    plain_text(big, tier_word, f, (m(cx), m(cy_log)), (14,12,26),
               shadow_a=0, tracking=m(1.4), weight=m(0.7))


def hero_disc(big, sid, pal):
    cx, cy, r = m(CX), m(DISC_CY), m(DISC_R)
    sc._alpha_aura(big, cx, cy, r + m(18), pal["glow"], peak=52, layers=15)
    sc.cabochon(big, cx, cy, r, CABO_LO, CABO_HI, ring=pal["gem"], ring_a=50)
    try:
        sc.blit_thumb(big, sid, cx, cy, int(r * 1.5))
    except Exception:
        pygame.draw.circle(big, pal["gem"], (cx, cy), int(r * 0.7))
    sc.cabochon_glass(big, cx, cy, r, tint=pal["gem"])
    rw = max(3, m(3.0))
    pygame.draw.circle(big, pal["gem"], (cx, cy), r + rw // 2 + m(1), rw)


# ── BEFORE: original v5_integration shelf layout ──────────────────────────────
def before_shelf(big, price_str, pal):
    """Reproduces the current v5_integration shelf: small buttons + isolated price chip."""
    SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 17, 335, 226, 91
    SHELF_RAD = m(CARD_RAD)
    BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 99, 31, 12, 360, 10
    BUY_CX = CX - (BTN_W + BTN_GAP) // 2   # = 75
    CAN_CX = CX + (BTN_W + BTN_GAP) // 2   # = 185
    CHIP_CY, CHIP_W, CHIP_H = 402, 88, 26
    BOT_GEM_CY = 402

    # shelf body (bottom rounded corners only)
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf = vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                        [(0.0, (34,36,72)), (0.5, (22,24,54)), (1.0, (12,14,36))],
                        255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255,255,255,255), smask.get_rect(),
                     border_bottom_left_radius=SHELF_RAD,
                     border_bottom_right_radius=SHELF_RAD)
    shelf.blit(smask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115,106,140), (0,0), (shelf_rect.w-1, 0), max(1, m(1)))
    big.blit(shelf, shelf_rect.topleft)

    # price chip (88×26) at cy=402
    cx_ = m(CX)
    cy_ = m(CHIP_CY)
    cw_ = m(CHIP_W)
    ch_ = m(CHIP_H)
    chip_rad = m(8)
    chip_r = pygame.Rect(cx_ - cw_//2, cy_ - ch_//2, cw_, ch_)
    sc.drop_shadow(big, chip_r, chip_rad, blur=m(3), alpha=80, dy=m(2))
    big.blit(vgrad_stops(cw_, ch_, chip_rad,
                         [(0.0,(22,18,34)),(1.0,(12,10,22))], 255, gamma=1.0),
             chip_r.topleft)
    sc.bevel_rim(big, chip_r, chip_rad, CARD_RING_DEEP, (*CARD_RING_BRIGHT, 200),
                 w=max(1, m(1.4)))

    # coin + price on chip (small — price is subordinate to the isolated chip)
    f_chip = font(10)
    tw_chip = sc._glyph_base(price_str, f_chip, 0).get_width()
    coin_r_c = m(8)
    grp = coin_r_c*2 + m(4) + tw_chip
    coin_cx_c = cx_ - grp//2 + coin_r_c
    text_cx_c = coin_cx_c + coin_r_c + m(4) + tw_chip//2
    sc.coin_glyph(big, coin_cx_c, cy_, coin_r_c)
    plain_text(big, price_str, f_chip, (text_cx_c, cy_), (230, 210, 160),
               shadow_a=80, weight=m(0.7), keyline=(20,14,4), kw=m(0.6))

    # BUY button (99×31)
    for cx_btn, lbl, is_b in [(m(BUY_CX), "BUY", True), (m(CAN_CX), "CANCEL", False)]:
        bw, bh, br = m(BTN_W), m(BTN_H), m(BTN_RAD)
        br_rect = pygame.Rect(cx_btn - bw//2, m(BTN_CY) - bh//2, bw, bh)
        if is_b:
            stops = [(0.0,(148,106,28)),(1.0,(72,48,10))]
            lab_c = (255,246,208)
            rim_b = (*CARD_RING_BRIGHT, 220)
        else:
            stops = [(0.0,(28,24,42)),(1.0,(16,14,28))]
            lab_c = (176,172,208)
            rim_b = (*CARD_RING_BRIGHT, 140)
        sc.drop_shadow(big, br_rect, br, blur=m(3), alpha=100, dy=m(2))
        big.blit(vgrad_stops(bw, bh, br, stops, 255, gamma=1.1), br_rect.topleft)
        sc.top_sheen(big, br_rect, br, m(10), peak=36 if is_b else 10)
        sc.bevel_rim(big, br_rect, br, CARD_RING_DEEP, rim_b, w=max(1, m(1.4)))
        plain_text(big, lbl, font(9), br_rect.center, lab_c,
                   shadow_a=120, tracking=m(1.1), weight=m(0.8 if is_b else 0.6),
                   keyline=(6,6,16), kw=m(0.6))

    # bottom gems flanking chip
    for gx in [m(GEM_L_X), m(GEM_R_X)]:
        sc._alpha_aura(big, gx, m(BOT_GEM_CY), m(16), pal["glow"], peak=60, layers=14)
        sc.facet_gem(big, gx, m(BOT_GEM_CY), m(GEM_R), pal["gem"], pal["deep"])


def render_before():
    """Render the current v5_integration confirm popup using EPIC palette."""
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)
    card_body(big)
    corner_gems(big, EPIC_PAL)
    name_text(big, EPIC_NAME)
    rarity_banner(big, EPIC_WORD, EPIC_PAL)
    before_shelf(big, EPIC_PRICE, EPIC_PAL)
    hero_disc(big, EPIC_SID, EPIC_PAL)
    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── showcase assembly ─────────────────────────────────────────────────────────
PANEL_W, PANEL_H = 200, 355
GAP       = 12
MARGIN    = 20
HEADER_H  = 50
FOOTER_H  = 28

SLUGS = [
    "slot-marquee",
    "coin-rail-twin",
    "enamel-split-bar",
    "luggage-tag",
    "treasure-drawer",
]

# crop coords for EPIC tier popup from 2× 3-tier strip (EPIC is i=1)
# strip: MARGIN=20, HEAD=58, GAP=12, POP_W=260 in logical coords
# 2× strip: EPIC popup x=2*(20+1*(260+12))=584, y=2*58=116, w=520, h=884
_M, _H, _G, _PW, _PH = 20, 58, 12, 260, 442
EPIC_X2 = 2 * (_M + 1 * (_PW + _G))   # = 584
EPIC_Y2 = 2 * _H                       # = 116
EPIC_W2 = 2 * _PW                      # = 520
EPIC_H2 = 2 * _PH                      # = 884

CANVAS_W = MARGIN * 2 + PANEL_W * 6 + GAP * 5
CANVAS_H = HEADER_H + PANEL_H + FOOTER_H

# build BEFORE panel from pygame render
before_pg = render_before()
before_raw = pygame.image.tostring(before_pg, "RGB")
before_pil = Image.frombytes("RGB", (POP_W, POP_H), before_raw)
before_panel = before_pil.resize((PANEL_W, PANEL_H), Image.LANCZOS)

panels = [before_panel]
labels = ["BEFORE"]

for slug in SLUGS:
    strip_path = f"/home/user/skybit/docs/confirm_purchase_v8/{slug}/round_2.png"
    strip = Image.open(strip_path)
    epic_crop = strip.crop((EPIC_X2, EPIC_Y2, EPIC_X2 + EPIC_W2, EPIC_Y2 + EPIC_H2))
    panel = epic_crop.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    panels.append(panel)
    labels.append(slug)

# assemble canvas
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))

# draw panels and labels (using PIL for text)
from PIL import ImageDraw, ImageFont as PILFont

draw = ImageDraw.Draw(canvas)

# header text
draw.text((MARGIN, 14), "confirm_purchase_v8  ·  showcase  ·  BEFORE vs. 5 round-2 concepts",
          fill=(232, 226, 208))
draw.text((MARGIN, 32), "EPIC tier  ·  branch: v5_integration",
          fill=(140, 148, 168))

for i, (panel, slug) in enumerate(zip(panels, labels)):
    px = MARGIN + i * (PANEL_W + GAP)
    py = HEADER_H
    canvas.paste(panel, (px, py))

    # divider line between BEFORE and first concept
    if i == 1:
        div_x = px - GAP // 2
        draw.line([(div_x, py), (div_x, py + PANEL_H)], fill=(80, 76, 100), width=1)

    # slug label below panel
    label_y = HEADER_H + PANEL_H + 6
    draw.text((px + PANEL_W // 2, label_y), slug,
              fill=(180, 176, 210), anchor="mt")

OUT = "/home/user/skybit/docs/confirm_purchase_v8/showcase.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"saved {canvas.size[0]}×{canvas.size[1]}  →  {OUT}")
