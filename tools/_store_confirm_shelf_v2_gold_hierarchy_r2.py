"""Round 2 — shelf concept 'gold-hierarchy' (store_confirm_shelf_v2).

Hierarchy is carried by golden-bevel intensity + label weight, NOT by fill.
A single prominent amber price CHIP is the information anchor; below it sit two
minimal indigo action triggers — BUY (full-intensity gold rim, larger label)
and CANCEL (same rim at reduced alpha, smaller + quieter label). No fill change
separates them, so the eye is steered by rim brightness and type size alone.

R2 revisions:
- Locked BUY rim alpha dropped to 55 so it reads clearly below CANCEL's 80.
- CANCEL rim alpha reduced to 80 — widens the affordable BUY(215)↔CANCEL(80) gap.
- CANCEL label quieter: (165,158,190) instead of (190,180,210).
- BUY width 88px, CANCEL width 74px, each centred at their own CX (58, 142).
- Locked chip grey coin gets an explicit (120,122,138) keyline ring.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v2/gold-hierarchy/round_2.png
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

PAL   = sc.RARITY["epic"]
PRICE = 500

# The chip is the anchor: oversized amber plaque, centred above the triggers.
CHIP_W, CHIP_H, CHIP_RAD = 130, 38, 9
CHIP_TOP                 = 237

# Each button is centred at its own X so widths are independent.
# BUY is wider (88px) to reinforce primary status; CANCEL is narrower (74px).
BTN_TOP, BTN_H, BTN_RAD = 281, 34, 9
BUY_CX, BUY_W           = 58, 88
CAN_CX, CAN_W           = 142, 74


def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()


def _padlock(surf, cx, cy, col):
    # A 6x5 body + a semicircular shackle reads as a lock at any tiny size.
    body = pygame.Rect(0, 0, m(6), m(5))
    body.center = (cx, cy + m(1))
    sh_w = m(4)
    arc = pygame.Rect(cx - sh_w // 2, cy - m(4), sh_w, m(6))
    pygame.draw.arc(surf, col, arc, math.radians(20), math.radians(160),
                    max(1, m(0.9)))
    pygame.draw.rect(surf, col, body, border_radius=max(1, m(1)))


def _draw_chip(big, affordable):
    chip = pygame.Rect(m(CX) - m(CHIP_W) // 2, m(CHIP_TOP), m(CHIP_W), m(CHIP_H))
    crad = m(CHIP_RAD)

    if affordable:
        face_stops = [(0.0, (240, 224, 180)), (1.0, (210, 194, 150))]
        rim_bright = (*sc.CARD_RING_BRIGHT, 190)
    else:
        face_stops = [(0.0, (108, 108, 122)), (1.0, (84, 84, 98))]
        rim_bright = (140, 142, 156, 150)

    sc.drop_shadow(big, chip, crad, blur=m(4), alpha=120, dy=m(2))
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)
    sc.top_sheen(big, chip, crad, m(14), peak=(54 if affordable else 30))
    sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP, rim_bright, w=max(1, m(1.5)))

    # coin + numeral, centred as a unit inside the plaque
    txt      = str(PRICE)
    num_font = sc.font(24)
    coin_r   = m(15)
    gap      = m(5)
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
        pygame.draw.circle(big, (70, 72, 86), (coin_cx, cy), coin_r)
        # Explicit keyline so the grey coin reads crisply at 1x scale.
        pygame.draw.circle(big, (120, 122, 138), (coin_cx, cy), coin_r,
                           max(1, m(1)))
        num_col = (60, 62, 74)
    sc.plain_text(big, txt, num_font, (num_cx, cy + m(1)), num_col,
                  shadow_a=90, weight=m(0.8), keyline=None)


def _draw_buy(big, affordable):
    # Centre the button at BUY_CX so its width is independent of CANCEL's.
    buy_r = pygame.Rect(m(BUY_CX) - m(BUY_W) // 2, m(BTN_TOP), m(BUY_W), m(BTN_H))
    rad   = m(BTN_RAD)

    if affordable:
        fill_stops = [(0.0, (84, 78, 126)), (1.0, (50, 46, 82))]
        rim_bright = (*sc.CARD_RING_BRIGHT, 215)
        lbl_col    = (220, 210, 240)
    else:
        # Locked: gold rim dialled back well below CANCEL's 80 so it reads
        # clearly subordinate even in the unaffordable state.
        fill_stops = [(0.0, (58, 58, 72)), (1.0, (40, 40, 52))]
        rim_bright = (*sc.CARD_RING_BRIGHT, 55)
        lbl_col    = (128, 128, 148)

    sc.drop_shadow(big, buy_r, rad, blur=m(3), alpha=110, dy=m(2))
    big.blit(sc.vgrad_stops(buy_r.w, buy_r.h, rad, fill_stops, 255), buy_r.topleft)
    sc.top_sheen(big, buy_r, rad, m(12), peak=30)
    sc.bevel_rim(big, buy_r, rad, sc.CARD_RING_DEEP, rim_bright, w=max(1, m(1.7)))

    if affordable:
        sc.plain_text(big, "BUY", sc.font(14), buy_r.center, lbl_col,
                      shadow_a=110, weight=m(0.8), keyline=(18, 16, 32), kw=m(0.9))
    else:
        _padlock(big, buy_r.centerx, buy_r.centery - m(7), (120, 120, 142))
        sc.plain_text(big, "BUY", sc.font(14),
                      (buy_r.centerx, buy_r.centery + m(8)), lbl_col,
                      shadow_a=90, weight=m(0.8), keyline=(20, 20, 30), kw=m(0.9))


def _draw_cancel(big):
    # Centre the button at CAN_CX so its width is independent of BUY's.
    can_r = pygame.Rect(m(CAN_CX) - m(CAN_W) // 2, m(BTN_TOP), m(CAN_W), m(BTN_H))
    rad   = m(BTN_RAD)

    # Same indigo fill as BUY — hierarchy comes from the lower-alpha rim
    # and the smaller, quieter label.
    fill_stops = [(0.0, (84, 78, 126)), (1.0, (50, 46, 82))]

    sc.drop_shadow(big, can_r, rad, blur=m(3), alpha=110, dy=m(2))
    big.blit(sc.vgrad_stops(can_r.w, can_r.h, rad, fill_stops, 255), can_r.topleft)
    sc.top_sheen(big, can_r, rad, m(12), peak=20)
    sc.bevel_rim(big, can_r, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 80), w=max(1, m(1.6)))
    sc.plain_text(big, "CANCEL", sc.font(12), can_r.center, (165, 158, 190),
                  shadow_a=90, weight=m(0.7), keyline=(18, 16, 32), kw=m(0.8))


def _draw_shelf(big, affordable):
    _draw_chip(big, affordable)
    _draw_buy(big, affordable)
    _draw_cancel(big)
    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(326)),
                      (168, 150, 160), shadow_a=90, weight=m(0.6))


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
    safe_w = m(168)
    nf30   = sc.font(30)
    if _nw(name, nf30) <= safe_w:
        nf33 = sc.font(33)
        draw_f = nf33 if _nw(name, nf33) <= safe_w else nf30
        sc.plain_text(big, name, draw_f, (m(CX), m(base_y)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        banner_y = base_y + 20
    else:
        spaces = [i for i, c in enumerate(name) if c == ' ']
        best = min(spaces, key=lambda i: max(_nw(name[:i], nf30), _nw(name[i+1:], nf30)))
        l1, l2 = name[:best], name[best+1:]
        sc.plain_text(big, l1, sc.font(30), (m(CX), m(base_y-11)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        sc.plain_text(big, l2, sc.font(27), (m(CX), m(base_y+11)), (250, 248, 240),
                      shadow_a=120, weight=m(0.8), keyline=(6, 6, 16), kw=m(1.0))
        banner_y = base_y + 40

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
          "gold-hierarchy  |  AFFORDABLE / UNAFFORDABLE  (R2)",
          fill=(220, 214, 245), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR
PANELS = [(18, "AFFORDABLE", True), (18 + POP_W + GAP_C, "UNAFFORDABLE", False)]

for px, _label, affordable in PANELS:
    surf  = render_popup("TEMPEST", 178, affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, panels_y))

    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength("C") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "C", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = "docs/store_confirm_shelf_v2/gold-hierarchy/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL verification ──────────────────────────────────────────────────────────
from PIL import Image as _I
img = _I.open(OUT)

# (a) left panel center: must be non-background
left_cx, left_cy = 18 + POP_W // 2, panels_y + POP_H // 2
px_center = img.getpixel((left_cx, left_cy))
assert px_center != (8, 8, 20), f"Left panel center looks like background: {px_center}"
print(f"(a) left panel center ({left_cx},{left_cy}) = {px_center}  OK")

# (b) BUY rim gold check — sample top-edge of BUY button in affordable panel
# BUY_CX=58 in popup space; panels start at x=18; BUY top = panels_y + BTN_TOP - 2
buy_sample_x = 18 + BUY_CX
buy_sample_y = panels_y + 281 - 2
px_buy = img.getpixel((buy_sample_x, buy_sample_y))
buy_gold = (px_buy[0] + px_buy[1]) // 2 - px_buy[2]
print(f"(b) BUY rim pixel ({buy_sample_x},{buy_sample_y}) = {px_buy}  gold-score={buy_gold}")
assert buy_gold > 40, f"BUY rim not visibly gold: {px_buy}, score={buy_gold}"
print("    BUY rim gold  OK")

# (c) CANCEL rim must be measurably less gold than BUY
can_sample_x = 18 + CAN_CX
can_sample_y = buy_sample_y
px_can = img.getpixel((can_sample_x, can_sample_y))
can_gold = (px_can[0] + px_can[1]) // 2 - px_can[2]
print(f"(c) CANCEL rim pixel ({can_sample_x},{can_sample_y}) = {px_can}  gold-score={can_gold}")
assert can_gold < buy_gold, (
    f"CANCEL rim not below BUY: CANCEL={can_gold} >= BUY={buy_gold}"
)
print("    CANCEL rim < BUY rim  OK")
print("All PIL checks passed.")
