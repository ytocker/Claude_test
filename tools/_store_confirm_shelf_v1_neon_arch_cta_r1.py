"""NEON-ARCH-CTA shelf concept — Round 1.

Two-panel sheet: an asymmetric CTA cluster inside the confirm-popup shelf.
A dominant arch-top BUY button (near-black enamel + neon rim/aura + faint
scanlines) sits above a ghost CANCEL pill, with a horizontal price meter
capping the shelf. Left = affordable (gold neon), right = unaffordable
(steel-blue neon + short grey meter + lock).

Output: docs/store_confirm_shelf_v1/neon-arch-cta/round_1.png
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc

SS = sc.SS       # 2
m  = sc.m        # round(x*2)

POP_W, POP_H = 200, 340
CX = 100
SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 235, 174, 87

# Card geometry carried over from the shared confirm-popup base.
CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X = 11, 117, 33, 167
BANNER_W = 120

BTN_W = 76
PAL   = sc.RARITY["epic"]
PRICE = 500
NAME  = "TEMPEST CONDOR"
BASE_Y = 178


def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()


def _round_mask(size, tl, tr, bl, br):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_top_left_radius=tl, border_top_right_radius=tr,
                     border_bottom_left_radius=bl, border_bottom_right_radius=br)
    return mask


def _draw_price_meter(big, affordable):
    # A slim status bar capping the shelf: how close the wallet is to the cost.
    mw, mh = m(140), m(16)
    rad    = m(8)
    meter  = pygame.Rect(0, 0, mw, mh)
    meter.center = (m(CX), m(246))

    big.blit(sc.vgrad_stops(mw, mh, rad,
             [(0.0, (20, 20, 36)), (1.0, (14, 14, 28))], 255), meter.topleft)

    inset = m(1)
    track_w_full = mw - inset * 2
    if affordable:
        frac  = 1.0
        stops = [(0.0, (210, 170, 60)), (1.0, (160, 120, 30))]
    else:
        frac  = 0.15
        stops = [(0.0, (150, 96, 96)), (1.0, (120, 80, 80))]
    fill_w = max(rad, int(track_w_full * frac))
    fill   = sc.vgrad_stops(fill_w, mh - inset * 2, rad, stops, 255)
    big.blit(fill, (meter.x + inset, meter.y + inset))

    # Left-cap coin + numeral read the price against the fill.
    coin_r = m(6)
    coin_cx = meter.x + m(9)
    sc.coin_glyph(big, coin_cx, meter.centery, coin_r)
    num_font = sc.font(13)
    txt = f"{PRICE:,}"
    num_r = sc.plain_text(big, txt, num_font,
                          (coin_cx + m(8) + num_font.size(txt)[0] // 2,
                           meter.centery + m(1)),
                          (240, 210, 140), shadow_a=120, weight=m(0.7))

    if not affordable:
        # A small padlock flags the shortfall to the right of the numeral.
        lx = num_r.right + m(6)
        ly = meter.centery
        body = pygame.Rect(0, 0, m(7), m(6))
        body.center = (lx + m(3), ly + m(2))
        pygame.draw.rect(big, (150, 146, 170), body, border_radius=m(1))
        pygame.draw.arc(big, (150, 146, 170),
                        pygame.Rect(body.x + m(1), body.y - m(4), m(5), m(7)),
                        0.15, 3.0, max(1, m(1)))


def _draw_buy_arch(big, affordable):
    # The dominant call to action: an arch-topped enamel slab lit by a neon rim.
    bw, bh = m(130), m(48)
    top_rad, bot_rad = m(24), m(8)
    buy = pygame.Rect(0, 0, bw, bh)
    buy.center = (m(CX), m(267))

    if affordable:
        rim_bright = (200, 168, 80, 220)
        aura_col   = (180, 140, 40)
        label_col  = (240, 215, 150)
    else:
        rim_bright = (80, 120, 180, 220)
        aura_col   = (60, 90, 160)
        label_col  = (140, 136, 160)

    # Halo bleeds past the slab before the body masks its own footprint.
    sc._alpha_aura(big, buy.centerx, buy.centery, buy.w // 2 + m(8),
                   aura_col, peak=50, layers=10)

    body = sc.vgrad_stops(bw, bh, 0,
             [(0.0, (36, 32, 58)), (1.0, (22, 18, 42))], 255).copy()
    body.blit(_round_mask((bw, bh), top_rad, top_rad, bot_rad, bot_rad),
              (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Faint CRT scanlines inside the arch sell the neon-panel feel.
    scan = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for yy in range(0, bh, m(2)):
        pygame.draw.line(scan, (190, 190, 215, 12), (0, yy), (bw - 1, yy))
    scan.blit(_round_mask((bw, bh), top_rad, top_rad, bot_rad, bot_rad),
              (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    body.blit(scan, (0, 0))

    big.blit(body, buy.topleft)
    sc.bevel_rim(big, buy, top_rad, (20, 18, 36, 180), rim_bright, w=max(1, m(1.5)))
    sc.plain_text(big, "BUY", sc.font(16), buy.center, label_col,
                  shadow_a=130, weight=m(1.0), keyline=(14, 12, 30), kw=m(0.9))


def _draw_cancel_pill(big):
    # A quiet ghost pill: outline + whisper of fill so it defers to BUY.
    cw, ch = m(BTN_W), m(20)
    rad    = m(10)
    can = pygame.Rect(0, 0, cw, ch)
    can.center = (m(CX), m(313))

    big.blit(sc.vgrad_stops(cw, ch, rad,
             [(0.0, (40, 38, 58, 40)), (1.0, (28, 26, 46, 40))], 38), can.topleft)
    pygame.draw.rect(big, (110, 106, 140, 180), can,
                     width=max(1, m(1)), border_radius=rad)
    sc.plain_text(big, "CANCEL", sc.font(12), can.center, (160, 156, 185),
                  shadow_a=90, weight=m(0.6))


def render_popup(affordable):
    big = pygame.Surface((POP_W * SS, POP_H * SS), pygame.SRCALPHA)

    # ── card body ──
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

    # ── corner gems ──
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])

    # ── name + tier banner ──
    safe_w = m(168)
    nf30 = sc.font(30)
    if _nw(NAME, nf30) <= safe_w:
        nf33 = sc.font(33)
        draw_f = nf33 if _nw(NAME, nf33) <= safe_w else nf30
        sc.plain_text(big, NAME, draw_f, (m(CX), m(BASE_Y)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        banner_y = BASE_Y + 20
    else:
        spaces = [i for i, c in enumerate(NAME) if c == ' ']
        best = min(spaces, key=lambda i: max(_nw(NAME[:i], nf30), _nw(NAME[i + 1:], nf30)))
        l1, l2 = NAME[:best], NAME[best + 1:]
        sc.plain_text(big, l1, sc.font(30), (m(CX), m(BASE_Y - 11)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        sc.plain_text(big, l2, sc.font(27), (m(CX), m(BASE_Y + 11)), (250, 248, 240),
                      shadow_a=120, weight=m(0.8), keyline=(6, 6, 16), kw=m(1.0))
        banner_y = BASE_Y + 40
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(banner_y), m(BANNER_W), PAL)

    # ── shelf panel (the recessed CTA tray) ──
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0,
                           [(0.0, (28, 30, 62)), (1.0, (14, 16, 40))], 255).copy()
    smask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(smask, (255, 255, 255, 255), smask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(smask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    pygame.draw.line(shelf, (115, 106, 140), (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # ── neon-arch CTA cluster ──
    _draw_price_meter(big, affordable)
    _draw_buy_arch(big, affordable)
    _draw_cancel_pill(big)

    # ── disc + aura + thumb (LAST, so the hero reads over the tray) ──
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── sheet layout ──────────────────────────────────────────────────────────────
MARGIN   = 18
GAP      = 8
HDR_H    = 24
CANVAS_W = 444
CANVAS_H = 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((MARGIN, MARGIN), "NEON-ARCH-CTA  |  AFFORDABLE / UNAFFORDABLE",
          fill=(210, 205, 240), font=fnt_hdr, anchor="lm")

panels_y = MARGIN + HDR_H
for i, affordable in enumerate((True, False)):
    px = MARGIN + i * (POP_W + GAP)
    surf = render_popup(affordable)
    raw  = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, panels_y))

    bx, by = px + 5, panels_y + 5
    bw = fnt_badge.getlength("B") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "B", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = "docs/store_confirm_shelf_v1/neon-arch-cta/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")
