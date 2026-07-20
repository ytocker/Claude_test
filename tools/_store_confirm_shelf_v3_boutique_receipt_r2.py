"""Round 2 (final) — shelf concept 'boutique-receipt' (store_confirm_shelf_v3).

Revision of r1 on art-director notes. The shelf stays a cream/parchment field
under the dark indigo card, but the CTA hierarchy is sharpened: BUY is the only
dark solid wearing the bright gold crown, while CANCEL is demoted to a warm
parchment ghost that blends into the shelf (still framed by a dimmer gold rim so
it reads as a control, not decoration). The card->shelf seam is warmed toward
the card's own bottom hue so it reads card -> dark-warm lip -> cream with no grey
mud step.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output -> docs/store_confirm_shelf_v3/boutique-receipt/round_2.png
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
CX           = 100

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                            = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
Y_NAME, Y_BANNER, BANNER_W                 = 155, 175, 120

SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
CHIP_CY                            = 258
BTN_W, BTN_H, BTN_RAD, BTN_CY, BTN_GAP = 76, 30, 9, 302, 8
BUY_CX = CX - (BTN_W + BTN_GAP) // 2   # = 58
CAN_CX = CX + (BTN_W + BTN_GAP) // 2   # = 142
CHIP_W, CHIP_H, CHIP_RAD = 100, 30, 8

PAL   = sc.RARITY["epic"]
PRICE = 500

# On-theme browns — the shelf's own hue family, so bridges/rules never read as
# stray gold. The brown lip specifically keeps every gold bevel off the cream.
LIP_BROWN   = (150, 120, 80)
# Bleed warmed to the card's own bottom hue so the seam reads card -> dark-warm
# lip -> cream, never as a grey-mauve step where pure indigo bled over cream.
SEAM_BLEED  = (12, 12, 36)


def _btn(big, rect, rad, label, fill_stops, label_col, font_size,
         gold_bevel=True, keyline=None, sheen=20,
         bevel_alpha=230, bevel_w=None):
    sc.drop_shadow(big, rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad, fill_stops, 255), rect.topleft)
    sc.top_sheen(big, rect, rad, m(10), peak=sheen)
    if gold_bevel:
        # Gold bevel sits on chocolate/mocha only — the brown lip guarantees it
        # never contacts the cream field beneath. Alpha/width vary per button so
        # BUY alone owns the bright gold crown; CANCEL wears a dimmer frame.
        w = bevel_w if bevel_w is not None else max(1, m(2.0))
        sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, bevel_alpha), w=w)
    else:
        # Locked BUY: grey rim matches the greyed chip so inert reads by shape,
        # not hue alone.
        sc.bevel_rim(big, rect, rad, (54, 58, 74, 200), (140, 138, 160, 180),
                     w=max(1, m(2.0)))
    if keyline is not None:
        sc.plain_text(big, label, sc.font(font_size), rect.center, label_col,
                      shadow_a=90, weight=m(0.7), keyline=keyline, kw=m(0.8))
    else:
        sc.plain_text(big, label, sc.font(font_size), rect.center, label_col,
                      shadow_a=70, weight=m(0.7))


def _draw_chip(big, cx, cy, price, affordable):
    # Warm receipt-paper display pill — deliberately MATTE (no sheen) so it reads
    # as printed paper, not a button. Chocolate ink price + a brown hairline rule
    # (on-theme, never gold) underline the numeral like a receipt total.
    cw, ch, crad = m(CHIP_W), m(CHIP_H), m(CHIP_RAD)
    chip = pygame.Rect(0, 0, cw, ch)
    chip.center = (cx, cy)
    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=80, dy=m(2))

    if affordable:
        face_stops = [(0.0, (222, 210, 184)), (1.0, (202, 190, 162))]
    else:
        face_stops = [(0.0, (122, 120, 128)), (1.0, (100, 98, 108))]
    big.blit(sc.vgrad_stops(cw, ch, crad, face_stops, 255), chip.topleft)

    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 200), w=max(1, m(1.4)))
    else:
        sc.bevel_rim(big, chip, crad, (54, 58, 74, 200), (140, 138, 160, 180),
                     w=max(1, m(1.4)))

    txt = f"{price:,}"
    num_font = sc.font(19)
    coin_r = m(13)
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
        num_col = (58, 40, 22)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        pygame.draw.circle(big, (128, 132, 146), (coin_cx, cy), coin_r - m(3),
                           width=max(1, m(1)))
        num_col = (110, 108, 116)

    num_rect = sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                             shadow_a=0, weight=m(0.7))

    # Brown hairline rule spanning the numeral width, 3px below its baseline.
    # Drawn at m(2) height and 70% alpha so it survives the downscale to 1x
    # against the parchment face instead of ghosting out.
    hair_col = LIP_BROWN if affordable else (120, 122, 132)
    hair = pygame.Surface((num_rect.w, max(1, m(2))), pygame.SRCALPHA)
    hair.fill((*hair_col, 178))   # ~70% alpha
    big.blit(hair, (num_rect.x, num_rect.bottom + m(3)))


def _draw_shelf(big, affordable):
    # Cream shelf, rounded to sit inside the card's lower well.
    sx, sy, sw, sh = m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H)
    srad = m(13)

    shelf = pygame.Surface((sw, sh), pygame.SRCALPHA)
    for y in range(sh):
        t = y / max(1, sh - 1)
        c = sc.lerp_color((238, 228, 206), (216, 204, 178), t)
        pygame.draw.line(shelf, (*c, 255), (0, y), (sw - 1, y))
    mask = pygame.Surface((sw, sh), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_bottom_left_radius=srad, border_bottom_right_radius=srad)
    shelf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(shelf, (sx, sy))

    # Seam bleed: a shallow 3px strip fading the card's OWN bottom hue ->
    # transparent, so the cream connects up into the dark card with a warm dark
    # lip instead of the grey-mauve mud a wider pure-indigo bleed produced.
    bleed_h = m(3)
    bleed = pygame.Surface((sw, bleed_h), pygame.SRCALPHA)
    for y in range(bleed_h):
        a = int(255 * (1 - y / max(1, bleed_h)))
        pygame.draw.line(bleed, (*SEAM_BLEED, a), (0, y), (sw - 1, y))
    big.blit(bleed, (sx, sy))

    # Brown lip: the single line that fully separates every button/chip bevel
    # from the cream field — the gold never touches cream directly.
    pygame.draw.line(big, LIP_BROWN, (sx, sy), (sx + sw - 1, sy), max(1, m(1)))

    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable)

    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)

    if affordable:
        _btn(big, buy, brad, "BUY",
             [(0.0, (86, 54, 30)), (1.0, (58, 34, 16))],
             (246, 232, 206), 14, gold_bevel=True, keyline=(40, 22, 8), sheen=24)
    else:
        _btn(big, buy, brad, "BUY",
             [(0.0, (72, 66, 60)), (1.0, (50, 46, 42))],
             (140, 132, 120), 14, gold_bevel=False, keyline=(28, 26, 24), sheen=12)

    # CANCEL is a warm-parchment ghost — its fill blends into the cream shelf so
    # BUY is the only dark solid in the well. The gold bevel stays but at reduced
    # alpha/width so BUY alone owns the bright gold crown.
    _btn(big, can, brad, "CANCEL",
         [(0.0, (200, 186, 164)), (1.0, (180, 166, 142))],
         (148, 136, 112), 13, gold_bevel=True, keyline=None, sheen=12,
         bevel_alpha=130, bevel_w=max(1, m(1.4)))

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(322)),
                      (150, 120, 84), shadow_a=0)


def render_popup(name, affordable):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # Dark indigo card body — the shelf's light field is the pattern-break UNDER it.
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

    # cream shelf + chip + CTAs
    _draw_shelf(big, affordable)

    # disc + aura + thumb LAST so the hero disc floats above everything
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
PANEL_Y = 54

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, 30),
          "boutique-receipt r2  |  AFFORDABLE / UNAFFORDABLE",
          fill=(232, 210, 150), font=fnt_hdr, anchor="mm")

PANELS = [(18, True), (226, False)]

panels_data = []
for px, affordable in PANELS:
    surf  = render_popup("TEMPEST", affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panels_data.append((px, affordable, panel))

for px, affordable, panel in panels_data:
    canvas.paste(panel, (px, PANEL_Y))
    bx, by = px + 5, PANEL_Y + 5
    bw     = fnt_badge.getlength("D") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "D", fill=(246, 232, 206), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v3", "boutique-receipt", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL verification (never view the image) ──────────────────────────────────
aff_panel = panels_data[0][2]
probe = aff_panel.getpixel((118, 224))
print(f"(118, 224) affordable: {probe}  "
      f"-> {'non-background OK' if probe != (8, 8, 20) else 'WARN: background!'}")
shelf_px = aff_panel.getpixel((118, 330))
print(f"(118, 330) shelf: {shelf_px}")
cancel_px = aff_panel.getpixel((160, 356))
print(f"(160, 356) CANCEL body: {cancel_px}")
