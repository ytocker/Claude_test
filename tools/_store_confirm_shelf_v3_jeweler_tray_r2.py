"""Round 2 (final) — shelf concept 'jeweler-tray' (store_confirm_shelf_v3).

Thesis holds: a warm amber-black tray where the gold coin + price on the
obsidian chip is the ONLY pure-warm value cue, and BUY is the sole colored
fill drawing the tap.

R2 changes over R1 (director notes):
  - CANCEL is now a ghost obsidian control (near-shelf fill) with its gold
    bevel kept — no longer a twin-sapphire button, so BUY is the only colored
    fill and the blue/blue colorblind ambiguity is gone.
  - Unaffordable BUY deadens to inert slate (no colored fill, near-flat sheen)
    so it plainly reads as un-tappable.
  - Size asymmetry: BUY (84w) dominates, CANCEL (66w) recedes.
  - Chip hairline rule bumped to survive the smoothscale to 1x.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v3/jeweler-tray/round_2.png
"""
import os, sys

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

# ── layout constants (1x popup coords) ────────────────────────────────────────
POP_W, POP_H = 200, 340
CX = 100

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
Y_NAME, Y_BANNER, BANNER_W = 155, 175, 120
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
CHIP_CY = 258
# Size asymmetry: BUY dominates, CANCEL recedes.
BUY_W, CAN_W = 84, 66
BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 30, 9, 302, 8
BUY_CX = CX - (BUY_W + BTN_GAP) // 2   # = 54
CAN_CX = CX + (BUY_W + BTN_GAP) // 2   # = 146
CHIP_W, CHIP_H, CHIP_RAD = 112, 34, 8

PAL   = sc.RARITY["epic"]
PRICE = 500

# jeweler-tray gold bevel — same warm ring the card frame uses, so both the
# BUY CTA and the ghost CANCEL still read as part of the gilded set.
BEVEL_DEEP   = (58, 48, 22)
BEVEL_BRIGHT = (236, 202, 116)
BEVEL_ALPHA  = 230
BEVEL_W      = max(1, m(2.0))
# grey inert bevel for the deadened unaffordable BUY.
GREY_DEEP    = (54, 58, 74, 200)
GREY_BRIGHT  = (140, 138, 160, 180)


def _btn(big, btn_rect, rad, label, font_px, fill_stops, lab_col, bevel,
         sheen_peak):
    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, fill_stops, 255),
             btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen_peak)

    if bevel == "gold":
        sc.bevel_rim(big, btn_rect, rad, BEVEL_DEEP, (*BEVEL_BRIGHT, BEVEL_ALPHA),
                     w=BEVEL_W)
    else:
        sc.bevel_rim(big, btn_rect, rad, GREY_DEEP, GREY_BRIGHT, w=BEVEL_W)

    sc.plain_text(big, label, sc.font(font_px), btn_rect.center, lab_col,
                  shadow_a=110, weight=m(0.8), keyline=(14, 16, 30), kw=m(0.9))


def _draw_chip(big, cx, cy, price, affordable):
    # Matte obsidian set-stone tray — deliberately NO top_sheen so it never
    # reads as a glossy button. The warm-gold numeral is the shelf's only pure
    # warm note; a hairline gold rule seats the digits like an engraved value.
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))
    face_stops = [(0.0, (26, 24, 30)), (1.0, (16, 15, 20))]
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)

    if affordable:
        sc.bevel_rim(big, chip, crad, BEVEL_DEEP, (*BEVEL_BRIGHT, BEVEL_ALPHA),
                     w=max(1, m(1.4)))
    else:
        sc.bevel_rim(big, chip, crad, GREY_DEEP, GREY_BRIGHT, w=max(1, m(1.4)))

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
    num_cy = cy + m(3)

    if affordable:
        sc.coin_glyph(big, coin_cx, cy, coin_r)
        num_col = (238, 206, 128)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        pygame.draw.circle(big, (128, 132, 146), (coin_cx, cy), coin_r - m(3),
                           width=max(1, m(1)))
        num_col = (110, 115, 130)

    num_rect = sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                             shadow_a=0, weight=m(0.8))

    # Hairline gold rule seated 3px below the numeral baseline, spanning the
    # digit width — alpha bumped so it survives the smoothscale to 1x.
    if affordable:
        baseline = num_rect.top + num_font.get_ascent()
        rule_y = baseline + m(3)
        rule = pygame.Surface((num_rect.w, max(1, m(1))), pygame.SRCALPHA)
        rule.fill((236, 202, 116, 170))
        big.blit(rule, (num_rect.centerx - num_rect.w // 2, rule_y))


def _draw_shelf(big, affordable):
    # Warm amber-black recessed tray with a brass lip. Only the chip + buttons
    # sit in it; the hero disc floats above (drawn later).
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)

    shelf_stops = [(0.0, (36, 26, 14)), (1.0, (18, 13, 7))]
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=22)

    lip = (128, 96, 44)   # warm brass front edge
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Micro-walls: warm-lit left / shadowed right strips for inset depth.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (xx / max(1, wall_w - 1)))
            pygame.draw.line(lwall, (150, 118, 60, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable)

    buy = pygame.Rect(0, 0, m(BUY_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(CAN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)

    # BUY is the sole colored fill; when unaffordable it deadens to inert slate.
    if affordable:
        _btn(big, buy, brad, "BUY", 14,
             [(0.0, (72, 96, 196)), (1.0, (44, 62, 150))], (232, 238, 252),
             "gold", 26)
    else:
        _btn(big, buy, brad, "BUY", 14,
             [(0.0, (58, 60, 74)), (1.0, (40, 42, 54))], (150, 152, 162),
             "grey", 10)

    # CANCEL is a ghost obsidian control (near-shelf fill), gold bevel kept so
    # it still binds to the gilded set without competing with BUY for color.
    _btn(big, can, brad, "CANCEL", 13,
         [(0.0, (32, 30, 38)), (1.0, (20, 19, 26))], (190, 194, 204),
         "gold", 14)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(322)),
                      (160, 148, 128), shadow_a=0)


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

    # disc + aura + thumb (LAST so disc floats above shelf)
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── sheet layout ─────────────────────────────────────────────────────────────
MARGIN, HDR_H, GAP_HDR = 18, 28, 8
CANVAS_W, CANVAS_H = 444, 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, MARGIN + HDR_H // 2),
          "jeweler-tray r2  |  AFFORDABLE / UNAFFORDABLE",
          fill=(232, 210, 150), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR   # = 54
PANELS = [(18, True), (226, False)]

panels_data = []
for px, affordable in PANELS:
    surf  = render_popup("TEMPEST", affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panels_data.append((px, affordable, panel))

for px, affordable, panel in panels_data:
    canvas.paste(panel, (px, panels_y))
    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength("A") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "A", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v3", "jeweler-tray", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL verification ─────────────────────────────────────────────────────────
# (118, 224) on the affordable panel must be non-background (card body visible).
aff_final = panels_data[0][2]
probe = aff_final.getpixel((118, 224))
print(f"\n=== PIL Verification ===")
print(f"(118, 224) on affordable panel: {probe}  "
      f"→ {'non-background OK' if probe != (8, 8, 20) else 'WARN: background!'}")
