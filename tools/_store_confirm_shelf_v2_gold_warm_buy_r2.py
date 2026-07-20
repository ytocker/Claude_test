"""Round 2 — shelf concept 'gold-warm-buy'.

Both action buttons wear the card's single golden bevel. BUY warms toward a
lifted amber fill so its luminance clearly leads CANCEL's cool indigo — the
warm block wins the eye. The price chip is dialled back so BUY remains the
brightest warm element. CANCEL keeps its full cool-indigo value; the
warm/cool temperature split depends on it staying saturated.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v2/gold-warm-buy/round_2.png
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc

SS = sc.SS      # 2
m  = sc.m       # round(x*2)

POP_W, POP_H = 200, 340
CX           = POP_W // 2

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                            = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
BANNER_W                                   = 120
SHELF_X, SHELF_Y, SHELF_W, SHELF_H         = 13, 235, 174, 87

PAL   = sc.RARITY["epic"]
PRICE = 500

# Chip floats above the button row; buttons split the shelf width with a small
# seam-gap so each reads as its own rimmed block, not two halves of a slab.
CHIP_CY   = 251
BTN_TOP   = 271
BTN_H     = 38
BTN_GAP   = 8
BUY_W     = 94
CAN_W     = SHELF_W - BUY_W - BTN_GAP     # 72
BTN_RAD   = 9


def _padlock(surf, cx, cy, col):
    # A 6x5 body + a semicircular shackle reads as a lock at any tiny size.
    body = pygame.Rect(0, 0, m(6), m(5))
    body.center = (cx, cy + m(1))
    sh_w = m(4)
    arc = pygame.Rect(cx - sh_w // 2, cy - m(4), sh_w, m(6))
    pygame.draw.arc(surf, col, arc, math.radians(20), math.radians(160),
                    max(1, m(0.9)))
    pygame.draw.rect(surf, col, body, border_radius=max(1, m(1)))


def _btn(big, rect, label, fill_stops, lab_col, sheen_peak, keyline,
         bevel_a, locked=False):
    rad = m(BTN_RAD)
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad, fill_stops, 255), rect.topleft)
    sc.top_sheen(big, rect, rad, m(11), peak=sheen_peak)
    if locked:
        _padlock(big, rect.centerx, rect.centery - m(7), (150, 150, 172))
        sc.plain_text(big, label, sc.font(14),
                      (rect.centerx, rect.centery + m(8)), lab_col,
                      shadow_a=100, weight=m(0.9), keyline=keyline, kw=m(0.9))
    else:
        sc.plain_text(big, label, sc.font(14), rect.center, lab_col,
                      shadow_a=120, weight=m(0.9), keyline=keyline, kw=m(0.9))
    # Same golden material on both buttons; dimmed alpha when locked.
    sc.bevel_rim(big, rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, bevel_a), w=max(1, m(1.6)))


def _draw_chip(big, affordable):
    CHIP_W, CHIP_H, CHIP_RAD = 108, 30, 7
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (m(CX), m(CHIP_CY))
    crad = m(CHIP_RAD)

    if affordable:
        # Pulled ~20 luma below the old value so the chip reads as passive info
        # rather than competing with the BUY button for warmth leadership.
        face_stops = [(0.0, (206, 192, 150)), (1.0, (176, 160, 116))]
    else:
        face_stops = [(0.0, (98, 102, 118)), (1.0, (74, 78, 94))]
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)
    sc.top_sheen(big, chip, crad, m(8), peak=40)

    txt      = f"{PRICE}"
    num_font = sc.font(18)
    coin_r   = m(11)
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_r * 2 + gap + num_w
    left     = chip.centerx - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_r * 2 + gap + num_w // 2
    cy       = chip.centery

    if affordable:
        sc.coin_glyph(big, coin_cx, cy, coin_r)
        num_col = (52, 28, 4)
    else:
        pygame.draw.circle(big, (120, 124, 140), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (150, 154, 168), (coin_cx, cy), coin_r,
                           max(1, m(1)))
        num_col = (58, 62, 78)
    sc.plain_text(big, txt, num_font, (num_cx, cy + m(1)), num_col,
                  shadow_a=70, weight=m(0.7))

    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 160), w=max(1, m(1.2)))
    else:
        sc.bevel_rim(big, chip, crad, (40, 42, 52),
                     (150, 154, 168, 110), w=max(1, m(1.2)))


def _draw_shelf(big, affordable):
    _draw_chip(big, affordable)

    buy_r = pygame.Rect(m(SHELF_X), m(BTN_TOP), m(BUY_W), m(BTN_H))
    can_r = pygame.Rect(m(SHELF_X + BUY_W + BTN_GAP), m(BTN_TOP),
                        m(CAN_W), m(BTN_H))

    # CANCEL: cool indigo kept fully saturated — the warm/cool split depends on
    # CANCEL holding its chromaticity, so nothing here changes from Round 1.
    can_stops = [(0.0, (84, 78, 126)), (1.0, (50, 46, 82))]
    _btn(big, can_r, "CANCEL", can_stops, (220, 210, 240), 24,
         (14, 12, 26), 200)

    # BUY: lifted amber (R−B chroma ~58) so luminance matches or beats CANCEL
    # (~85 avg), reversing the hierarchy inversion from Round 1 (~60 avg).
    if affordable:
        buy_stops = [(0.0, (104, 80, 44)), (1.0, (70, 52, 26))]
        _btn(big, buy_r, "BUY", buy_stops, (230, 215, 175), 32,
             (30, 24, 8), 200)
    else:
        buy_stops = [(0.0, (48, 48, 60)), (1.0, (34, 34, 46))]
        _btn(big, buy_r, "BUY", buy_stops, (110, 110, 128), 18,
             (18, 18, 28), 110, locked=True)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(315)),
                      (170, 150, 120), shadow_a=90, weight=m(0.6))


def render_popup(name, base_y, affordable):
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

    # corner gems
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])

    # name + banner
    def _nw(txt, font):
        return sc._glyph_base(txt, font, 0).get_width()

    safe_w = m(168)
    nf30   = sc.font(30)
    nf33   = sc.font(33)
    draw_f = nf33 if _nw(name, nf33) <= safe_w else nf30
    sc.plain_text(big, name, draw_f, (m(CX), m(base_y)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    banner_y = base_y + 20

    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(banner_y), m(BANNER_W), PAL)

    # shelf (the concept under test)
    _draw_shelf(big, affordable)

    # disc + aura + thumb (LAST)
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── sheet layout ─────────────────────────────────────────────────────────────
MARGIN   = 18
HDR_H    = 28
GAP_HDR  = 8
GAP_C    = 8
CANVAS_W = 444
CANVAS_H = 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, MARGIN + HDR_H // 2),
          "gold-warm-buy  |  AFFORDABLE / UNAFFORDABLE",
          fill=(220, 214, 245), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR
PANELS = [(18, "AFFORDABLE", True), (18 + POP_W + GAP_C, "UNAFFORDABLE", False)]

for px, _label, affordable in PANELS:
    surf  = render_popup("TEMPEST", 178, affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, panels_y))

    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength("B") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "B", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = "docs/store_confirm_shelf_v2/gold-warm-buy/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL pixel verification ────────────────────────────────────────────────────
# The AFFORDABLE panel sits at canvas x=18, y=panels_y (=54).
# BUY button center in popup coords: (SHELF_X + BUY_W/2, BTN_TOP + BTN_H/2)
#   = (13+47, 271+19) = (60, 290) → canvas (78, 344)
# CANCEL button center in popup coords: (SHELF_X+BUY_W+BTN_GAP + CAN_W/2, BTN_TOP+BTN_H/2)
#   = (115+36, 271+19) = (151, 290) → canvas (169, 344)
BG        = (8, 8, 20)
px_check  = canvas.getpixel((118, 224))
buy_px    = canvas.getpixel((78, 344))
cancel_px = canvas.getpixel((169, 344))

assert px_check[:3] != BG,  f"(118,224) is background — card body not rendering: {px_check}"
assert buy_px[0] > buy_px[2], \
    f"BUY fill not warm: R={buy_px[0]} B={buy_px[2]} at (78,344)"
assert cancel_px[2] >= cancel_px[0], \
    f"CANCEL fill not cool: R={cancel_px[0]} B={cancel_px[2]} at (169,344)"

print(f"PIL verify OK — (118,224)={px_check[:3]}, "
      f"BUY(78,344) R={buy_px[0]} B={buy_px[2]}, "
      f"CANCEL(169,344) R={cancel_px[0]} B={cancel_px[2]}")
