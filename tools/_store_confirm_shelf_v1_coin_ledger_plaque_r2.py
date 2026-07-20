"""Round 2 — shelf concept D: COIN-LEDGER-PLAQUE.

Same three-register card as Round 1. Four targeted revisions from art-director:
- BUY pill gold rim raised to m(3.0) and bright stop lifted to (225,185,95) so
  the rim is the hottest element on the shelf, not a hairline afterthought.
- Dark drop-line immediately inside the gold top rim reads as a beveled lip
  casting depth over the pill recess — the raised illusion becomes tactile.
- Plaque deboss catch-light edge lifted to (68,70,96) at m(1.5) width so the
  ~40-value delta survives the final smoothscale.
- Unaffordable BUY sheen deflated from peak=45 to peak=18 so the pill visibly
  loses gloss, not just colour — a second affordance cue for colourblind viewers.

Output → docs/store_confirm_shelf_v1/coin-ledger-plaque/round_2.png
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


def _deboss(big, rect, dark, light, lw=1):
    """Reversed emboss: dark on top+left interior, light on bottom+right —
    the inverted shadow reads as a sunken face. lw lets the light catch-edge
    be drawn at m(1.5) so it survives smoothscale with a clear value delta."""
    pygame.draw.line(big, dark,  rect.topleft,     rect.topright)
    pygame.draw.line(big, dark,  rect.topleft,     rect.bottomleft)
    pygame.draw.line(big, light, rect.bottomleft,  rect.bottomright, lw)
    pygame.draw.line(big, light, rect.topright,    rect.bottomright, lw)


def _draw_price_plaque(big, affordable):
    plaque = pygame.Rect(0, 0, m(150), m(24))
    plaque.center = (m(CX), m(249))
    prad = m(6)
    # Darker-than-shelf body so the register sits below the card face.
    big.blit(sc.vgrad_stops(plaque.w, plaque.h, prad,
             [(0.0, (22, 24, 48)), (1.0, (14, 16, 36))], 255), plaque.topleft)
    # Catch-light edge at m(1.5) keeps a ~38-value delta after smoothscale so
    # the sunken read is clear without competing with the gold pill rim.
    _deboss(big, plaque, (8, 8, 18), (68, 70, 96), lw=max(1, m(1.5)))

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
        # Grey inlay: the gold is spent-only, so its absence signals "locked".
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
    # Deflating the sheen on the locked state is a second affordance signal —
    # the pill loses gloss AND colour, not just colour, so colorblind players
    # still see a visibly flat vs raised button.
    sc.top_sheen(big, buy_r, brad, m(10), peak=45 if affordable else 18)

    if affordable:
        # bevel_rim's gradient mask reaches ~38% alpha at mid-pill height →
        # R≈112 on side edges — below the R>200 gold threshold. A constant-lit
        # gold ring (full alpha, all sides) is the only reliable way to satisfy
        # R>200,G>160,B<110 on top AND sides without BLEND_ADD (which adds to B
        # and kills the B<110 criterion). The ring's intrinsic warm gold is the
        # affordance signal; top_sheen already lit the pill interior above it.
        rim_w  = max(2, m(3.0))
        key_w  = max(1, m(0.8))
        # Thin dark outer contact keyline
        pygame.draw.rect(big, (14, 14, 30), buy_r, width=key_w, border_radius=brad)
        # Solid gold inner ring — full opacity ensures top+left+right all qualify
        gold_r = buy_r.inflate(-key_w * 2, -key_w * 2)
        gold_band_w = rim_w - key_w
        pygame.draw.rect(big, (240, 200, 100), gold_r,
                         width=gold_band_w, border_radius=max(1, brad - key_w))
        # Dark drop-line one step inside the gold top rail — the beveled lip
        # shadow over the pill recess makes the raised illusion tactile.
        shadow_y = buy_r.top + key_w + gold_band_w + max(1, m(1.5))
        pygame.draw.line(big, (14, 14, 30),
                         (buy_r.left  + rim_w + m(1), shadow_y),
                         (buy_r.right - rim_w - m(1), shadow_y))
    else:
        sc.bevel_rim(big, buy_r, brad, (20, 18, 36, 180), (130, 132, 150, 180),
                     w=max(1, m(1.8)))

    lab_col = (235, 210, 150) if affordable else (130, 128, 148)
    sc.plain_text(big, "BUY", sc.font(14), buy_r.center, lab_col,
                  shadow_a=120, weight=m(0.8), keyline=(18, 16, 32), kw=m(0.9))


def _draw_cancel_slot(big):
    can_r = pygame.Rect(0, 0, m(70), m(28))
    can_r.center = (m(142), m(298))
    crad = m(10)
    # Reversed gradient (lighter at bottom) reads as an inset floor.
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

    # name + banner (space-split for the 14-char name)
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

    # shelf ground
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

    # disc + aura + thumb LAST
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

OUT = "docs/store_confirm_shelf_v1/coin-ledger-plaque/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved  {OUT}  ({CANVAS_W}×{CANVAS_H})")

# ── PIL pixel verification ────────────────────────────────────────────────────
# BUY pill in the affordable panel (left side, i=0):
#   logical pill rect: left=21, top=284, right=95, bottom=312 (in popup coords)
#   canvas offset: px=18, panels_y=54
#   → pill in canvas: x 39..113, y 338..366
# Sample the top rim band (y=338..342) for warm gold presence.

BUY_X0, BUY_X1 = 18 + 21, 18 + 95   # 39..113
BUY_Y0, BUY_Y1 = panels_y + 284, panels_y + 312   # top-rim area

# Row-by-row scan of the top 8 rows — the smoothscale shifts the rim band by
# 1-2px relative to the SS geometry, so a narrow window misses it.
gold_pixels = 0
sample_hits = []
for sy in range(BUY_Y0, min(BUY_Y0 + 8, BUY_Y1)):
    for sx in range(BUY_X0, BUY_X1):
        if 0 <= sx < CANVAS_W and 0 <= sy < CANVAS_H:
            r, g, b = canvas.getpixel((sx, sy))
            if r > 200 and g > 160 and b < 110:
                gold_pixels += 1
                sample_hits.append((sx, sy, r, g, b))

print(f"\nPIL verify — gold pixels in BUY top-rim (R>200,G>160,B<110): {gold_pixels}")
if sample_hits:
    sx, sy, r, g, b = sample_hits[len(sample_hits) // 2]
    print(f"  Mid-sample pixel ({sx},{sy}): R={r} G={g} B={b}")
else:
    print("  WARNING: no warm-gold pixels found in rim band")

# Also count gold in the full BUY region (wider affordance check).
full_gold = 0
for sy in range(BUY_Y0, BUY_Y1):
    for sx in range(BUY_X0, BUY_X1):
        if 0 <= sx < CANVAS_W and 0 <= sy < CANVAS_H:
            r, g, b = canvas.getpixel((sx, sy))
            if r > 200 and g > 160 and b < 110:
                full_gold += 1
print(f"  Gold pixels in full BUY region: {full_gold}  (target ≥180)")
