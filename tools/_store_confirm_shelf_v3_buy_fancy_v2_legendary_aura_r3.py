"""buy-fancy-v2 concept E — legendary-aura (r3, final).

A warm legendary aura wells up under BUY (affordable only) — toned to a warm
accent, not an inferno: a low, wide ambient haze that laps out to the shelf
walls, plus a modest core halo. The BUY face itself stays the brightest anchor: the
glow is support light, not the star. Three facet gems float clearly OUTSIDE the
button like satellite stars, each with a controlled (non-white) glint. CANCEL
stays a plain deep-card button. On the unaffordable panel BUY reverts to a
locked slate + padlock with NO glow and NO satellites — the legendary treatment
is a reward for being able to afford it.

Everything else (card body, corner gems, name, banner, shelf, chip, disc/aura/
thumb drawn LAST, SS=2 pipeline) is preserved from the c-orig-bg base.

Sheet: left=AFFORDABLE (x=18), right=UNAFFORDABLE (x=226), 444×412, panels_y=54.
Output → docs/store_confirm_shelf_v3/buy-fancy-v2/legendary-aura/round_3.png
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
CX           = POP_W // 2

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                            = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
NAME_FS, Y_NAME                            = 30, 155
Y_BANNER, BANNER_W                         = 175, 120

SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87
CHIP_CY                            = 258
BTN_W, BTN_H, BTN_RAD              = 76, 30, 9
BTN_CY, BTN_GAP                    = 302, 8
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2
CHIP_W, CHIP_H, CHIP_RAD          = 112, 34, 8

PAL   = sc.RARITY["epic"]
PRICE = 500

HAIR_GOLD = sc.CARD_RING_BRIGHT
_hair_final = None


def _padlock(surf, cx, cy, h, color):
    bw, bh = int(h * 0.92), int(h * 0.60)
    body = pygame.Rect(0, 0, bw, bh)
    body.center = (cx, cy + int(h * 0.20))
    pygame.draw.rect(surf, color, body, border_radius=max(1, int(h * 0.14)))
    sr = int(h * 0.30)
    arc = pygame.Rect(cx - sr, body.top - sr, sr * 2, sr * 2)
    pygame.draw.arc(surf, color, arc, math.radians(15), math.radians(165),
                    max(1, int(h * 0.17)))
    kh = pygame.Rect(0, 0, max(1, int(h * 0.16)), max(1, int(h * 0.22)))
    kh.center = (cx, body.centery + int(h * 0.02))
    pygame.draw.rect(surf, (10, 14, 26), kh, border_radius=1)


def _btn(big, btn_rect, rad, label, font_px, locked=False, is_cancel=False):
    # Original indigo fills + gold bevel: the CANCEL button and the LOCKED BUY
    # both flow through here so only the affordable BUY carries the legendary
    # gold + aura treatment applied in _draw_shelf.
    if locked:
        stops   = [(0.0, (58, 60, 74)), (1.0, (40, 42, 54))]
        lab_col = (150, 152, 162)
        sheen   = 10
    elif is_cancel:
        stops   = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
        lab_col = (150, 155, 200)
        sheen   = 14
    else:
        stops   = [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))]
        lab_col = (200, 205, 240)
        sheen   = 22

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)

    if locked:
        sc.bevel_rim(big, btn_rect, rad, (20, 18, 36, 180), (130, 124, 160, 200),
                     w=max(1, m(1.2)))
    else:
        rim_w = m(2.2) if is_cancel else m(2.0)
        sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 230), w=max(1, rim_w))

    lab_font = sc.font(font_px)
    if locked:
        lw = lab_font.size(label)[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.92)
        inner  = m(4)
        grp    = lock_w + inner + lw
        gx     = btn_rect.centerx - grp // 2
        _padlock(big, gx + lock_w // 2, btn_rect.centery, lock_h, lab_col)
        sc.plain_text(big, label, lab_font,
                      (gx + lock_w + inner + lw // 2, btn_rect.centery),
                      lab_col, shadow_a=0, weight=m(0.6))
    else:
        sc.plain_text(big, label, lab_font, btn_rect.center, lab_col,
                      shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def _draw_chip(big, cx, cy, price, affordable):
    global _hair_final
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
        # Match the card body colour just above the shelf so the chip reads
        # as an inlay rather than a floating pill.
        face_stops = [(0.0, (18, 20, 50)), (1.0, (10, 11, 30))]
    else:
        face_stops = [(0.0, (28, 28, 50)), (1.0, (18, 18, 36))]
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)

    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 200), w=max(1, m(1.4)))
    else:
        sc.bevel_rim(big, chip, crad, (44, 58, 58, 200), (120, 140, 140, 180),
                     w=max(1, m(1.4)))

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
        num_col = (236, 240, 232)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        pygame.draw.circle(big, (128, 132, 146), (coin_cx, cy), coin_r - m(3),
                           width=max(1, m(1)))
        num_col = (150, 154, 162)
    sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                  shadow_a=0, weight=m(0.8))

    if affordable:
        num_h = num_font.size(txt)[1]
        baseline = (num_cy - num_h // 2) + num_font.get_ascent()
        hair_h = m(2)
        hair_y = baseline + m(3)
        hair = pygame.Surface((num_w, hair_h), pygame.SRCALPHA)
        hair.fill((*HAIR_GOLD, int(255 * 0.85)))
        big.blit(hair, (num_cx - num_w // 2, hair_y))
        _hair_final = (
            (num_cx - num_w // 2) / SS,
            (num_cx + num_w // 2) / SS,
            (hair_y + hair_h // 2) / SS,
        )


def _draw_shelf(big, affordable):
    # Original _draw_confirm shelf palette — indigo-blue instead of teal.
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)

    shelf_stops = ([(0.0, (28, 30, 62)), (1.0, (14, 16, 40))] if affordable
                   else [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))])
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    lip = (115, 106, 140) if affordable else (62, 62, 86)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Walls: original purple-lit left / dark right.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * xx / max(1, wall_w - 1))
            pygame.draw.line(lwall, (130, 120, 165, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    # Step 1 — legendary aura, laid down BEFORE the chip and buttons so it reads
    # as light welling up from under the button rather than a sticker on top.
    # Affordable only: the bloom is the "you can claim this" reward tell. A wide,
    # low ambient field fills the shelf with warmth (lapping up toward the chip
    # and out to the walls), then a tighter core halo hugs the BUY seat.
    #
    # NOTE the aura is built from _alpha_aura (normal alpha-carry blits), NOT
    # soft_glow: soft_glow composites with BLEND_ADD, which ignores its alpha arg
    # and bleaches its centre to pure white — that white core was what outshone
    # the BUY face in r1. Alpha-carry layers can never exceed their own colour,
    # so every glow pixel stays warm amber and below the button's top-sheen,
    # keeping the gold BUY face the brightest anchor in the field.
    lg  = sc.RARITY["legendary"]
    if affordable:
        # Toned to a warm accent, not an inferno: a low, wide ambient haze that
        # laps out to the walls plus a modest core halo. Both stay well under the
        # gold BUY top-sheen so the button body remains the brightest element.
        sc._alpha_aura(big, m(BUY_CX), m(BTN_CY) - m(10), m(55),
                       lg["glow"], peak=20, layers=22)   # wide ambient haze
        sc._alpha_aura(big, m(BUY_CX), m(BTN_CY), m(30),
                       lg["glow"], peak=60, layers=16)    # modest core halo

    # Step 2 — chip (unchanged).
    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable)

    # Step 3 — BUY button. Its gold face is the warmest/brightest point in the
    # field; the aura above is only support light.
    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    brad = m(BTN_RAD)
    if affordable:
        sc.drop_shadow(big, buy, brad, blur=m(3), alpha=150, dy=m(2))
        gold_surf = sc.gold_a_fill(buy.w, buy.h, brad, 255)
        big.blit(gold_surf, buy.topleft)
        sc.top_sheen(big, buy, brad, m(12), peak=40)
        sc.bevel_rim(big, buy, brad, sc.GOLD_A_RIM_DARK,
                     (*sc.GOLD_A_RIM_BRIGHT, 240), w=max(1, m(2.0)))
        sc.plain_text(big, "BUY", sc.font(14), buy.center, sc.GOLD_A_NUM,
                      shadow_a=0, weight=m(0.8), keyline=(200, 160, 60), kw=m(0.6))
    else:
        _btn(big, buy, brad, "BUY", 14, locked=True)

    # Step 4 — CANCEL button (plain deep-card; no glow, no gold).
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    _btn(big, can, brad, "CANCEL", 13, locked=False, is_cancel=True)

    # Step 5 — three satellite facet gems floating clearly OUTSIDE the button
    # like satellite stars. The BUY button nearly fills the shelf (a ~12px band
    # above it, ~5px below, ~7px at each side), so a full orbit would drop gems
    # onto the button face or off the shelf. The one genuinely clear zone is the
    # band directly above the button, so the three gems ride a shallow crown arc
    # there — every facet body sits above the button top edge, none on the face.
    # Each gets a controlled amber glint capped over its hot pip so no gem pixel
    # blows past the BUY top-sheen to near-white.
    if affordable:
        gem_r = m(5)
        # A slightly deeper base than the raw legendary gem so the brightest
        # crown facet lands BELOW the BUY top-sheen — the gold face stays the
        # brightest anchor.
        sat_base = sc.lerp_color(lg["gem"], lg["deep"], 0.22)
        # (dx, dy) from BUY centre — a shallow arc cupping the top rim. Chosen so
        # every gem body AND its dark seat clear the button top edge (287): the
        # lowest seat pixel stays above the face, none reads as debris on it.
        crown = [(0, -29), (-24, -26), (24, -26)]
        for dx, dy in crown:
            sx = m(BUY_CX) + m(dx)
            sy = m(BTN_CY) + m(dy)
            sc.facet_gem(big, sx, sy, gem_r, sat_base, lg["deep"])
            # Cap the highlight: overpaint the gem's hot white pip with a warm
            # glint (max (230,200,140)) so no gem pixel blows past the BUY
            # top-sheen to near-white.
            gr  = max(1, int(gem_r * 0.30) + m(1))
            gcx = sx - int(gem_r * 0.24)
            gcy = sy - int(gem_r * 0.24)
            pygame.draw.circle(big, (230, 200, 140), (gcx, gcy), gr)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(322)),
                      (150, 176, 176), shadow_a=0)


def render_popup(name, affordable):
    global _hair_final
    _hair_final = None
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

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

    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.plain_text(big, name, sc.font(NAME_FS), (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(Y_BANNER), m(BANNER_W), PAL)

    _draw_shelf(big, affordable)

    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    final = pygame.transform.smoothscale(big, (POP_W, POP_H))

    if affordable and _hair_final is not None:
        x0, x1, hy = _hair_final
        pygame.draw.line(final, HAIR_GOLD, (int(round(x0)), int(round(hy))),
                         (int(round(x1)), int(round(hy))), 1)

    return final


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
          "legendary-aura (E) r3  |  AFFORDABLE / UNAFFORDABLE",
          fill=(180, 200, 240), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR
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
    bw = fnt_badge.getlength("E") + 8
    draw.rounded_rectangle([bx - 1, by - 1, bx + bw + 1, by + 18], radius=5,
                            fill=(200, 190, 240))
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "E", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v3", "buy-fancy-v2",
                   "legendary-aura", "round_3.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL verification ─────────────────────────────────────────────────────────
def _lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]

BG = (8, 8, 20)
aff = panels_data[0][2]
un  = panels_data[1][2]

# 1) BUY face is the brightest anchor: warm amber R>G>B.
buy_px = aff.getpixel((BUY_CX, BTN_CY))
print(f"AFF BUY center ({BUY_CX},{BTN_CY}): {buy_px}  "
      f"→ {'OK warm amber R>G>B' if buy_px[0] > buy_px[1] > buy_px[2] else 'WARN'}")

# 2) Wide ambient field reaches out across the shelf to the wall. The AD's
# suggested (BUY_CX, SHELF_Y+10) point is occluded by the price chip (which is
# drawn opaque over the glow), so probe the OPEN shelf beside the button and the
# left wall to prove the warm field laps outward.
open_probe = aff.getpixel((30, 292))          # open shelf just left of BUY
wall_probe = aff.getpixel((18, 292))          # out at the left shelf wall
print(f"AFF open-shelf (30,292): {open_probe}  "
      f"→ {'OK warm non-bg' if open_probe[0] > open_probe[2] and open_probe != BG else 'WARN'}")
print(f"AFF wall reach (18,292): {wall_probe}  "
      f"→ {'OK warm at wall' if wall_probe[0] > wall_probe[2] else 'WARN'}")

# The BUY face's own brightest point is its gold top-sheen — measure it over the
# whole button rect so it can serve as the "brightest anchor" reference.
btn_top   = BTN_CY - BTN_H // 2
bx0, by0  = BUY_CX - BTN_W // 2, btn_top
buy_sheen_lum = max(_lum(aff.getpixel((xx, yy)))
                    for yy in range(by0 + 1, by0 + BTN_H - 1)
                    for xx in range(bx0 + 1, bx0 + BTN_W - 1))

# 3) One satellite gem, clearly OUTSIDE the button rect (top crown gem, ~y=273).
sat_y  = BTN_CY - 29
sat_px = aff.getpixel((BUY_CX, sat_y))
print(f"AFF top gem ({BUY_CX},{sat_y}): {sat_px}  outside={sat_y < btn_top}  "
      f"→ {'OK non-bg outside' if sat_px != BG and sat_y < btn_top else 'WARN'}")

# No bright gem pixel may intrude on the button face: the brightest button-rect
# pixel must itself be a warm GOLD sheen pixel (R>G>B), not a pale gem facet.
face_worst = (0, None)
for yy in range(by0 + 1, by0 + BTN_H - 1):
    for xx in range(bx0 + 1, bx0 + BTN_W - 1):
        p = aff.getpixel((xx, yy))
        if _lum(p) > face_worst[0]:
            face_worst = (_lum(p), p)
fw = face_worst[1]
print(f"AFF button-face brightest {fw} L{face_worst[0]:.0f}  "
      f"→ {'OK gold sheen, no gem intrusion' if fw[0] > fw[1] > fw[2] else 'WARN gem/pale pixel on face'}")

# 4) Gems capped below the BUY top-sheen. Scan each crown gem's disc.
gem_max = 0
for cx, cy in [(BUY_CX, 273), (BUY_CX - 24, 276), (BUY_CX + 24, 276)]:
    for yy in range(cy - 7, cy + 7):
        for xx in range(cx - 7, cx + 7):
            if 0 <= xx < POP_W and 0 <= yy < POP_H:
                gem_max = max(gem_max, _lum(aff.getpixel((xx, yy))))
print(f"AFF gem max lum {gem_max:.0f} vs BUY top-sheen lum {buy_sheen_lum:.0f}  "
      f"→ {'OK gem not brighter than sheen' if gem_max <= buy_sheen_lum + 1 else 'WARN'}")

# 5) Unaffordable BUY: slate/locked, no warm glow, no satellites.
un_buy = un.getpixel((BUY_CX, BTN_CY))
print(f"UN BUY center ({BUY_CX},{BTN_CY}): {un_buy}  "
      f"→ {'OK slate/locked' if abs(un_buy[0]-un_buy[2]) < 30 and un_buy[0] < 130 else 'WARN'}")
un_open = un.getpixel((30, 292))
print(f"UN open-shelf (30,292): {un_open}  "
      f"→ {'OK no warm glow' if un_open[0] <= un_open[2] + 6 else 'WARN'}")

can_px = aff.getpixel((CAN_CX, BTN_CY))
print(f"AFF CANCEL center ({CAN_CX},{BTN_CY}): {can_px}  "
      f"→ {'OK indigo' if can_px[2] > can_px[0] else 'WARN'}")
