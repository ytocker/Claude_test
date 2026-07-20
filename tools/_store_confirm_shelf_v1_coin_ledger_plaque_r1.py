"""Round 1 — shelf concept D: COIN-LEDGER-PLAQUE.

Three registers carved from one indigo card material: an engraved (debossed)
price plaque up top, a raised gold-rimmed BUY pill below-left, a recessed
CANCEL slot below-right. Two panels contrast the affordable vs unaffordable
read — the gold rim + gold inlay is the only affordance colour, so its absence
is what "can't afford" looks like.

Output → docs/store_confirm_shelf_v1/coin-ledger-plaque/round_1.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc

SS = sc.SS
m  = sc.m

POP_W, POP_H = 200, 340
CX           = POP_W // 2

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                            = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
BANNER_W                                    = 120
SHELF_X, SHELF_Y, SHELF_W, SHELF_H         = 13, 235, 174, 87

PAL   = sc.RARITY["epic"]
PRICE = 500

BASE_Y = 178
NAME   = "TEMPEST CONDOR"


def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()


def _deboss(big, rect, dark, light):
    """Reversed emboss: dark on the top+left interior, light on the
    bottom+right — the eye reads that inverted shadow as a sunken face."""
    pygame.draw.line(big, dark,  rect.topleft,     rect.topright)
    pygame.draw.line(big, dark,  rect.topleft,     rect.bottomleft)
    pygame.draw.line(big, light, rect.bottomleft,  rect.bottomright)
    pygame.draw.line(big, light, rect.topright,    rect.bottomright)


def _draw_price_plaque(big, affordable):
    plaque = pygame.Rect(0, 0, m(150), m(24))
    plaque.center = (m(CX), m(249))
    prad = m(6)
    # Darker-than-shelf body so the register sits below the card face.
    big.blit(sc.vgrad_stops(plaque.w, plaque.h, prad,
             [(0.0, (22, 24, 48)), (1.0, (14, 16, 36))], 255), plaque.topleft)
    _deboss(big, plaque, (8, 8, 18), (50, 52, 75))

    # Coin + numeral group, centred inside the plaque.
    coin_r   = m(11)
    gap      = m(4)
    num_font = sc.font(16)
    txt      = "500"
    num_w    = num_font.size(txt)[0]
    total    = coin_r * 2 + gap + num_w
    left     = m(CX) - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_r * 2 + gap + num_w // 2

    if affordable:
        sc.coin_glyph(big, coin_cx, m(249), coin_r)
        sc.plain_text(big, txt, num_font, (num_cx, m(249) + m(3)),
                      (240, 210, 140), shadow_a=100,
                      keyline=(8, 6, 18), kw=m(0.9))
    else:
        # Grey inlay: the gold is spent-only, so its lack signals "locked".
        pygame.draw.circle(big, (120, 118, 130), (coin_cx, m(249)), coin_r)
        pygame.draw.circle(big, (86, 84, 96), (coin_cx, m(249)), coin_r,
                           width=max(1, m(1)))
        sc.plain_text(big, txt, num_font, (num_cx, m(249) + m(3)),
                      (120, 118, 130), shadow_a=90,
                      keyline=(8, 6, 18), kw=m(0.9))


def _draw_buy_pill(big, affordable):
    buy_r = pygame.Rect(0, 0, m(74), m(28))
    buy_r.center = (m(58), m(298))
    brad = m(12)
    big.blit(sc.vgrad_stops(buy_r.w, buy_r.h, brad,
             [(0.0, (34, 36, 66)), (0.5, (28, 30, 56)), (1.0, (18, 20, 44))],
             255), buy_r.topleft)
    sc.top_sheen(big, buy_r, brad, m(10), peak=45)
    bright = (210, 170, 80, 220) if affordable else (130, 132, 150, 180)
    sc.bevel_rim(big, buy_r, brad, (20, 18, 36, 180), bright,
                 w=max(1, m(1.8)))
    lab_col = (235, 210, 150) if affordable else (130, 128, 148)
    sc.plain_text(big, "BUY", sc.font(14), buy_r.center, lab_col,
                  shadow_a=120, weight=m(0.8), keyline=(18, 16, 32), kw=m(0.9))


def _draw_cancel_slot(big):
    can_r = pygame.Rect(0, 0, m(70), m(28))
    can_r.center = (m(142), m(298))
    crad = m(10)
    # Reversed gradient (lighter at the bottom) reads as an inset floor.
    big.blit(sc.vgrad_stops(can_r.w, can_r.h, crad,
             [(0.0, (18, 18, 36)), (1.0, (24, 26, 50))], 255), can_r.topleft)
    _deboss(big, can_r, (10, 10, 24), (44, 46, 68))
    # bright/dark reversed vs the raised BUY pill — sunken, never gold.
    sc.bevel_rim(big, can_r, crad, (45, 47, 68, 180), (12, 12, 28, 180),
                 w=max(1, m(1)))
    sc.plain_text(big, "CANCEL", sc.font(12), can_r.center, (158, 155, 185),
                  shadow_a=110, weight=m(0.8), keyline=(10, 10, 24), kw=m(0.9))


def render_popup(affordable):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # card body
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

    # corner gems
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])

    # name + banner (space-split path for the 14-char name)
    nf30   = sc.font(30)
    spaces = [i for i, c in enumerate(NAME) if c == ' ']
    best   = min(spaces, key=lambda i: max(_nw(NAME[:i], nf30),
                                           _nw(NAME[i + 1:], nf30)))
    l1, l2 = NAME[:best], NAME[best + 1:]
    sc.plain_text(big, l1, sc.font(30), (m(CX), m(BASE_Y - 11)),
                  (250, 248, 240), shadow_a=160, weight=m(0.9),
                  keyline=(6, 6, 16), kw=m(1.0))
    sc.plain_text(big, l2, sc.font(27), (m(CX), m(BASE_Y + 11)),
                  (250, 248, 240), shadow_a=120, weight=m(0.8),
                  keyline=(6, 6, 16), kw=m(1.0))
    banner_y = BASE_Y + 40
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(banner_y), m(BANNER_W), PAL)

    # shelf ground (base structure preserved)
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                           [(0.0, (28, 30, 62)), (1.0, (14, 16, 40))],
                           255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0),
                     (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # three registers carved into the shelf
    _draw_price_plaque(big, affordable)
    _draw_buy_pill(big, affordable)
    _draw_cancel_slot(big)

    # disc + aura + thumb (last)
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70,  layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── sheet layout ──────────────────────────────────────────────────────────────

MARGIN   = 18
TITLE_H  = 28
GAP      = 8
CANVAS_W = 444
CANVAS_H = 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    fnt_sub   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
except Exception:
    fnt_title = fnt_badge = fnt_sub = ImageFont.load_default()

draw.text((CANVAS_W // 2, MARGIN + TITLE_H // 2 - 4),
          "COIN-LEDGER-PLAQUE  |  AFFORDABLE / UNAFFORDABLE",
          fill=(232, 224, 250), font=fnt_title, anchor="mm")

panels_y = MARGIN + TITLE_H + 8
PANELS = [
    ("D", "AFFORDABLE",   True),
    ("D", "UNAFFORDABLE", False),
]

for i, (badge_id, sub, affordable) in enumerate(PANELS):
    px = MARGIN + i * (POP_W + GAP)

    popup = render_popup(affordable)
    raw   = pygame.image.tostring(popup, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, panels_y))

    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength(badge_id) + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), badge_id, fill=(230, 225, 245),
              font=fnt_badge, anchor="lm")
    draw.text((px + POP_W - 6, panels_y + 13), sub, fill=(150, 146, 178),
              font=fnt_sub, anchor="rm")

OUT = "docs/store_confirm_shelf_v1/coin-ledger-plaque/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved  {OUT}  ({CANVAS_W}×{CANVAS_H})")
