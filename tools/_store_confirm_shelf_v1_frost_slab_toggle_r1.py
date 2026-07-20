"""Round 1 — shelf concept 'frost-slab-toggle'.

The shelf becomes ONE frosted-glass slab: a full-width price lane on top, then
two asymmetric panes (BUY ~62% warm-gold, CANCEL ~38% cool slate) split by a
thin dark mullion, all wrapped in the card's single gold bevel rim.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v1/frost-slab-toggle/round_1.png
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

# BUY owns the left ~62% of the slab, CANCEL the right ~38%; together they span
# the full slab width so the mullion is the only seam between them.
BUY_W  = 108
CAN_W  = SHELF_W - BUY_W          # 66
LANE_H = 37                       # full-width price lane above the two panes

SLAB_RAD = m(14)


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


def _draw_shelf(big, affordable):
    slab_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    slab = pygame.Surface(slab_rect.size, pygame.SRCALPHA)
    W, H = slab.get_size()
    lane_h = m(LANE_H)

    # Base frosted-glass ground — only the price lane shows it; the panes cover
    # the lower half with their own fills.
    slab.blit(sc.vgrad_stops(W, H, 0,
              [(0.0, (46, 48, 72)), (1.0, (30, 32, 54))], 255), (0, 0))
    sc.top_sheen(slab, slab.get_rect(), SLAB_RAD, m(16), peak=32)

    # ── price lane (full slab top) ───────────────────────────────────────────
    txt      = f"{PRICE}"
    num_font = sc.font(18)
    coin_r   = m(12)
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_r * 2 + gap + num_w
    left     = W // 2 - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_r * 2 + gap + num_w // 2
    lane_cy  = m(22)                     # == m(SHELF_Y+22) in slab-local space
    if affordable:
        sc.coin_glyph(slab, coin_cx, lane_cy, coin_r)
        num_col = (240, 210, 140)
    else:
        pygame.draw.circle(slab, (78, 82, 98), (coin_cx, lane_cy), coin_r)
        pygame.draw.circle(slab, (110, 115, 130), (coin_cx, lane_cy), coin_r,
                           max(1, m(1)))
        num_col = (110, 115, 130)
    sc.plain_text(slab, txt, num_font, (num_cx, lane_cy + m(1)), num_col,
                  shadow_a=110, weight=m(0.8), keyline=(14, 12, 26), kw=m(0.8))

    # ── BUY pane (left ~62%) ────────────────────────────────────────────────
    buy = pygame.Rect(0, lane_h, m(BUY_W), H - lane_h)
    if affordable:
        buy_stops = [(0.0, (52, 46, 76)), (0.5, (64, 58, 90)), (1.0, (40, 36, 62))]
    else:
        buy_stops = [(0.0, (38, 38, 54)), (1.0, (26, 26, 42))]
    slab.blit(sc.vgrad_stops(buy.w, buy.h, 0, buy_stops, 255), buy.topleft)
    if affordable:
        # Low-alpha warm-cream wash tips the neutral frost into frosted-gold.
        wash = pygame.Surface(buy.size, pygame.SRCALPHA)
        wash.fill((255, 238, 196, 30))
        slab.blit(wash, buy.topleft)
    sc.top_sheen(slab, buy, 0, m(12), peak=(30 if affordable else 18))
    if affordable:
        # Soft inner glow, clipped to the pane so it stays an interior warmth.
        slab.set_clip(buy)
        sc._alpha_aura(slab, buy.centerx, buy.centery, m(40),
                       (200, 170, 80), peak=45, layers=8)
        slab.set_clip(None)

    if affordable:
        sc.plain_text(slab, "BUY", sc.font(14), buy.center, (240, 220, 160),
                      shadow_a=120, weight=m(0.9), keyline=(30, 24, 8), kw=m(0.9))
    else:
        _padlock(slab, buy.centerx, buy.centery - m(8), (120, 120, 142))
        sc.plain_text(slab, "BUY", sc.font(14),
                      (buy.centerx, buy.centery + m(8)), (100, 100, 120),
                      shadow_a=100, weight=m(0.9), keyline=(20, 20, 30), kw=m(0.9))

    # ── CANCEL pane (right ~38%) ────────────────────────────────────────────
    can = pygame.Rect(m(BUY_W), lane_h, m(CAN_W), H - lane_h)
    slab.blit(sc.vgrad_stops(can.w, can.h, 0,
              [(0.0, (32, 34, 52)), (1.0, (22, 24, 42))], 255), can.topleft)
    sc.top_sheen(slab, can, 0, m(10), peak=16)
    sc.plain_text(slab, "CANCEL", sc.font(13), can.center, (170, 166, 190),
                  shadow_a=110, weight=m(0.8), keyline=(16, 16, 28), kw=m(0.8))

    # ── mullion + shared gold rim ───────────────────────────────────────────
    pygame.draw.line(slab, (10, 10, 20), (m(BUY_W), lane_h), (m(BUY_W), H),
                     max(1, m(1)))
    sc.bevel_rim(slab, slab.get_rect(), SLAB_RAD, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, 230), w=max(1, m(1.6)))

    # Round the slab corners so the card's radius reads through.
    mask = pygame.Surface(slab.get_size(), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=SLAB_RAD)
    slab.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    sc.drop_shadow(big, slab_rect, SLAB_RAD, blur=m(4), alpha=115, dy=m(2))
    big.blit(slab, slab_rect.topleft)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(325)),
                      (150, 166, 190), shadow_a=90, weight=m(0.6))


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
          "FROST-SLAB-TOGGLE  |  AFFORDABLE / UNAFFORDABLE",
          fill=(220, 214, 245), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR
PANELS = [(18, "AFFORDABLE", True), (18 + POP_W + GAP_C, "UNAFFORDABLE", False)]

for px, _label, affordable in PANELS:
    surf  = render_popup("TEMPEST", 178, affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, panels_y))

    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength("A") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "A", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = "docs/store_confirm_shelf_v1/frost-slab-toggle/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")
