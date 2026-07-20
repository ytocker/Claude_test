"""BUY-button v2 exploration — concept 'starburst-radiance' (B).

Twenty tapering triangle rays fan out from behind the affordable BUY button
like a glowing sunburst, alternating gold and violet, with an additive bloom
at the centre. The BUY button then sits on top so the radiance reads as light
escaping from around a live control — not decoration painted over it.

Everything else is inherited from the c-orig-bg shelf (indigo shelf, corner
gems, banner, chip, disc/aura/thumb drawn LAST). Only the affordable BUY
treatment changes; the locked/unaffordable BUY keeps its base slate + padlock.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE, 444×412
Output → docs/store_confirm_shelf_v3/buy-fancy-v2/starburst-radiance/round_2.png
"""
import os, sys, math
import math as _math

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


def _btn_locked(big, btn_rect, rad, label, font_px):
    # Unaffordable BUY keeps its base slate + padlock — the radiance treatment
    # is reserved for a control the player can actually press.
    stops   = [(0.0, (58, 60, 74)), (1.0, (40, 42, 54))]
    lab_col = (150, 152, 162)
    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=10)
    sc.bevel_rim(big, btn_rect, rad, (20, 18, 36, 180), (130, 124, 160, 200),
                 w=max(1, m(1.2)))
    lab_font = sc.font(font_px)
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


def _btn_buy_fancy(big, btn_rect, rad):
    # Deep-indigo BUY so the surrounding gold/violet rays and the central bloom
    # supply all the brightness — the button reads as the calm eye of the burst.
    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=140, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad,
             [(0.0, (38, 40, 84)), (1.0, (22, 24, 56))], 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=26)
    sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 240), w=max(1, m(2.4)))
    sc.plain_text(big, "BUY", sc.font(14), btn_rect.center, (220, 215, 245),
                  shadow_a=120, weight=m(0.9), keyline=(8, 6, 20), kw=m(0.9))


def _btn_cancel(big, btn_rect, rad):
    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad,
             [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))], 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=12)
    sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 130), w=max(1, m(1.2)))
    sc.plain_text(big, "CANCEL", sc.font(13), btn_rect.center, (168, 162, 200),
                  shadow_a=110, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))


def _draw_chip(big, cx, cy, price, affordable):
    global _hair_final
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
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


def _draw_rays(big):
    # Rays + bloom live on their own SRCALPHA layer so overlapping violet/gold
    # edges composite once, cleanly, and the whole burst can be clipped to the
    # shelf as a single unit — no light escapes below the card or past the rim.
    ray_layer = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    N_RAYS = 16
    cx_r, cy_r = m(BUY_CX), m(BTN_CY)
    for i in range(N_RAYS):
        angle = 2 * _math.pi * i / N_RAYS
        if i % 2 == 0:
            ray_col = (*sc.CARD_RING_BRIGHT, 160)          # gold
        else:
            ray_col = (160, 110, 220, 185)                 # brighter lilac

        ray_len = m(40)
        spread  = m(3.5)
        # The east-facing rays collide with the CANCEL button, muddying which
        # control the burst belongs to — clip them back so BUY owns the light.
        if _math.cos(angle) > 0.707:
            ray_len = int(ray_len * 0.6)

        tip = (cx_r, cy_r)
        perp_angle = angle + _math.pi / 2
        base_cx = cx_r + ray_len * _math.cos(angle)
        base_cy = cy_r + ray_len * _math.sin(angle)
        b1 = (base_cx + spread * _math.cos(perp_angle),
              base_cy + spread * _math.sin(perp_angle))
        b2 = (base_cx - spread * _math.cos(perp_angle),
              base_cy - spread * _math.sin(perp_angle))
        pygame.draw.polygon(ray_layer, ray_col, [tip, b1, b2])

    # Warm gold halo hugging the button edge — not a blown-white centre disc.
    sc.soft_glow(ray_layer, cx_r, cy_r, m(22), sc.CARD_RING_BRIGHT,
                 peak_alpha=95)

    mask = pygame.Surface(big.get_size(), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    pygame.draw.rect(mask, (255, 255, 255, 255), shelf_rect, border_radius=m(6))
    ray_layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    big.blit(ray_layer, (0, 0))


def _draw_shelf(big, affordable):
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

    # Radiance is reserved for the pressable BUY — the locked state stays quiet.
    if affordable:
        _draw_rays(big)

    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable)

    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)
    if affordable:
        _btn_buy_fancy(big, buy, brad)
    else:
        _btn_locked(big, buy, brad, "BUY", 14)
    _btn_cancel(big, can, brad)

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
          "starburst-radiance (B) r2  |  AFFORDABLE / UNAFFORDABLE",
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
    bw = fnt_badge.getlength("B") + 8
    draw.rounded_rectangle([bx - 1, by - 1, bx + bw + 1, by + 18], radius=5,
                            fill=(200, 190, 240))
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "B", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v3", "buy-fancy-v2",
                   "starburst-radiance", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# PIL verification
aff = panels_data[0][2]
buy_px = aff.getpixel((BUY_CX, BTN_CY))
print(f"BUY center ({BUY_CX},{BTN_CY}): {buy_px}  "
      f"→ {'OK indigo' if buy_px[2] >= buy_px[0] and buy_px[2] >= buy_px[1] else 'WARN'}")

# A ray fired up-left from BUY (~45deg above centre) must clear the dark shelf.
ray_px = aff.getpixel((BUY_CX - 22, BTN_CY - 22))
print(f"ray ~45deg ({BUY_CX-22},{BTN_CY-22}): {ray_px}  "
      f"→ {'OK ray' if max(ray_px) > 60 else 'WARN dim'}")

can_px = aff.getpixel((CAN_CX, BTN_CY))
print(f"CANCEL center ({CAN_CX},{BTN_CY}): {can_px}  "
      f"→ {'OK indigo' if can_px[2] >= can_px[0] and can_px[2] >= can_px[1] else 'WARN'}")

# No blown-white bloom: the BUY burst region must stay warm gold, never a
# white centre disc (coin/glass specular elsewhere are legitimately bright).
peak_white = 0
_btn_l, _btn_r = BUY_CX - BTN_W // 2, BUY_CX + BTN_W // 2
_btn_t, _btn_b = BTN_CY - BTN_H // 2, BTN_CY + BTN_H // 2
for yy in range(BTN_CY - 24, min(POP_H, SHELF_Y + SHELF_H)):
    for xx in range(max(0, BUY_CX - 34), BUY_CX + 34):
        if _btn_l <= xx <= _btn_r and _btn_t <= yy <= _btn_b:
            continue                      # skip the button face + its BUY label
        peak_white = max(peak_white, min(aff.getpixel((xx, yy))))
print(f"BUY-halo peak min-channel (blown-white gauge): {peak_white}  "
      f"→ {'OK warm' if peak_white < 210 else 'WARN blown'}")

# Ray/glow containment: nothing may leak below the card body (y > 328).
leak = 0
for yy in range(SHELF_Y + SHELF_H + 8, POP_H):   # below card bottom edge
    for xx in range(POP_W):
        if max(aff.getpixel((xx, yy))) > 24:
            leak += 1
print(f"non-bg pixels below card (y>{SHELF_Y + SHELF_H + 8}): {leak}  "
      f"→ {'OK contained' if leak == 0 else 'WARN spill'}")
