"""Round 2 (final) — shelf concept 'slate-and-gold' (store_confirm_shelf_v3).

Thesis: a charcoal shelf with an indigo whisper so the popup sits inside
Skybit's night, and the BUY button IS the gold — a fully gold-fill CTA that
becomes the single hero of warmth against the cool slate. CANCEL recedes
further into bronze; the price chip is a warm off-white ledger tile, never
pure cream.

R2 tightens the gold hierarchy on art-director notes: CANCEL's label is now
legibly espresso on bronze; CANCEL's rim is dimmed + thinned so BUY alone
owns the bright gilded edge; the chip face is pulled down ~8% so the BUY peak
is the brightest warm in the frame; CANCEL's fill deepens into bronze.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output -> docs/store_confirm_shelf_v3/slate-and-gold/round_2.png
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
CX           = 100

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                            = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
Y_NAME, Y_BANNER, BANNER_W                = 155, 175, 120

SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
CHIP_CY                            = 258
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 76, 30, 9, 302, 8
BUY_CX = CX - (BTN_W + BTN_GAP) // 2   # = 58
CAN_CX = CX + (BTN_W + BTN_GAP) // 2   # = 142
CHIP_W, CHIP_H, CHIP_RAD = 112, 34, 8

PAL   = sc.RARITY["epic"]
PRICE = 500

# Gold bevel for the hero — the warm gilded rim now belongs to BUY alone.
GOLD_DEEP   = (58, 48, 22)
GOLD_BRIGHT = (236, 202, 116)
# CANCEL's rim tarnishes into a dimmer, thinner gold so it reads as the same
# struck-metal family as BUY without stealing the bright gilded edge.
CAN_RIM_BRIGHT = (196, 168, 110)
# Inert family: when the wallet is short, the rim tarnishes to cool grey so the
# gold rim never promises an action the player can't take.
GREY_DEEP   = (54, 58, 74)
GREY_BRIGHT = (140, 138, 160)


def _btn(big, rect, rad, label, fill_stops, lab_col, lab_fs, affordable,
         rim_bright, rim_w):
    sc.drop_shadow(big, rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad, fill_stops, 255), rect.topleft)
    sc.top_sheen(big, rect, rad, m(11), peak=24)
    if affordable:
        sc.bevel_rim(big, rect, rad, GOLD_DEEP, rim_bright, w=rim_w)
    else:
        # Grey rim matches the greyed coin + price so the whole inert state is
        # one cool signal, not a gold rim contradicting a dead button.
        sc.bevel_rim(big, rect, rad, (*GREY_DEEP, 210), (*GREY_BRIGHT, 190),
                     w=max(1, m(2.0)))
    sc.plain_text(big, label, sc.font(lab_fs), rect.center, lab_col,
                  shadow_a=90, weight=m(0.8))


def _draw_chip(big, cx, cy, price, affordable):
    # Warm off-white ledger tile — a matte face (deliberately NO top_sheen) so it
    # never competes with the gold BUY button for "press me". Its face is pulled
    # down from R1 so the BUY peak stays the brightest warm in the frame. A gold
    # hairline under the numeral echoes the button rim without turning the chip
    # into a CTA.
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H)); chip.center = (cx, cy)
    crad = m(CHIP_RAD)
    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
        face_stops = [(0.0, (206, 196, 172)), (1.0, (182, 172, 146))]
    else:
        face_stops = [(0.0, (60, 60, 74)), (1.0, (44, 44, 58))]
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)
    if affordable:
        sc.bevel_rim(big, chip, crad, GOLD_DEEP, (*GOLD_BRIGHT, 180), w=max(1, m(1.3)))
    else:
        sc.bevel_rim(big, chip, crad, (*GREY_DEEP, 200), (*GREY_BRIGHT, 170),
                     w=max(1, m(1.3)))

    txt = f"{price:,}"
    num_font = sc.font(22)
    coin_r = m(15)
    coin_d = coin_r * 2
    gap = m(4)
    num_w = num_font.size(txt)[0]
    total = coin_d + gap + num_w
    left = cx - total // 2
    coin_cx = left + coin_r
    num_cx = left + coin_d + gap + num_w // 2
    num_cy = cy + m(2)

    if affordable:
        sc.coin_glyph(big, coin_cx, cy, coin_r)
        num_col = (46, 38, 20)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r, width=max(1, m(1)))
        pygame.draw.circle(big, (128, 132, 146), (coin_cx, cy), coin_r - m(3),
                           width=max(1, m(1)))
        num_col = (110, 115, 130)
    num_r = sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                          shadow_a=0, weight=m(0.8))

    if affordable:
        # 1px gold hairline spanning the numeral width, 3px below its baseline —
        # a quiet gilded underscore tying the price to the gold BUY.
        rule = pygame.Surface((num_r.w, max(1, m(1))), pygame.SRCALPHA)
        rule.fill((198, 166, 96, int(255 * 0.55)))
        big.blit(rule, (num_r.x, num_r.bottom + m(3)))


def _draw_shelf(big, affordable):
    # Recessed charcoal tray with an indigo whisper bled in — the popup's floor.
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)

    if affordable:
        shelf_stops = [(0.0, (34, 36, 52)), (1.0, (20, 21, 34))]
    else:
        shelf_stops = [(0.0, (30, 31, 42)), (0.5, (22, 22, 32)), (1.0, (14, 14, 22))]

    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=20)
    lip = (96, 100, 124) if affordable else (58, 60, 76)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    # Soft seat shadow above the lip so the tray reads as sunk into the card.
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Micro-walls: cool-steel lit-left / shadowed-right strips for inset depth.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(46 * (xx / max(1, wall_w - 1)))
            pygame.draw.line(lwall, (110, 114, 140, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(46 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable)

    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)
    # BUY IS the gold: full hero gold-fill + espresso ink + the bright gilded rim.
    _btn(big, buy, brad, "BUY",
         [(0.0, (242, 200, 96)), (1.0, (206, 158, 54))], (38, 28, 8), 14, affordable,
         rim_bright=(*GOLD_BRIGHT, 230), rim_w=max(1, m(2.0)))
    # CANCEL sinks deeper into bronze with a dim, thinned rim and an espresso
    # label that stays legible (>=3:1) without competing for the press.
    _btn(big, can, brad, "CANCEL",
         [(0.0, (156, 126, 66)), (1.0, (120, 90, 38))], (78, 60, 30), 13, affordable,
         rim_bright=(*CAN_RIM_BRIGHT, 150), rim_w=max(1, m(1.4)))

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(322)),
                      (150, 166, 190), shadow_a=0)


def render_popup(name, affordable):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # card body
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

    # corner gems + name + banner
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.plain_text(big, name, sc.font(30), (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(Y_BANNER), m(BANNER_W), PAL)

    # shelf
    _draw_shelf(big, affordable)

    # disc + aura + thumb LAST so the hero disc floats above the shelf
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── sheet layout ─────────────────────────────────────────────────────────────
CANVAS_W, CANVAS_H = 444, 412
canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, 30),
          "slate-and-gold r2  |  AFFORDABLE / UNAFFORDABLE",
          fill=(232, 210, 150), font=fnt_hdr, anchor="mm")

PANELS = [(18, True), (226, False)]
PANEL_Y = 54

panels_data = []
for px, affordable in PANELS:
    surf  = render_popup("TEMPEST", affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panels_data.append((px, affordable, panel))

for px, affordable, panel in panels_data:
    canvas.paste(panel, (px, PANEL_Y))
    bx, by = px + 5, PANEL_Y + 5
    bw     = fnt_badge.getlength("B") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "B", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v3", "slate-and-gold", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL verification ─────────────────────────────────────────────────────────
aff_panel = panels_data[0][2]
probe = aff_panel.getpixel((118, 224))
print(f"\n=== PIL Verification ===")
print(f"(118, 224) on affordable panel: {probe}  "
      f"-> {'non-background OK' if probe != (8, 8, 20) else 'WARN: background!'}")
buy_rim = aff_panel.getpixel((BUY_CX, BTN_CY - BTN_H // 2 + 1))
can_rim = aff_panel.getpixel((CAN_CX, BTN_CY - BTN_H // 2 + 1))
print(f"BUY rim top @ ({BUY_CX},{BTN_CY - BTN_H//2 + 1}): {buy_rim}")
print(f"CANCEL rim top @ ({CAN_CX},{BTN_CY - BTN_H//2 + 1}): {can_rim}")
print(f"-> BUY brighter gold than CANCEL: "
      f"{'OK' if sum(buy_rim) > sum(can_rim) else 'check'}")
