"""Shelf-redesign concept 4 — hanging-price-tab.

The price chip is evicted from the button row: it becomes a narrow tab that
hangs at the shelf's top lip (mostly above the shelf, a sliver seated inside).
Below it, BUY and CANCEL merge into one split-footer bar divided by a beveled
seam (left half = BUY, right half = CANCEL). The footer sits low, embracing
the bottom gems. Nothing stacks with a gap — price is a label, actions a footer.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE, 444×412
Output → docs/store_confirm_shelf_v3/shelf-redesign/hanging-price-tab/round_1.png
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

SHELF_X, SHELF_Y, SHELF_W, SHELF_H = 13, 258, 174, 58   # shelf_bottom=316
# Price tab (hangs at shelf top lip)
CHIP_W   = 88
CHIP_H   = 26
CHIP_RAD = 8
CHIP_CY  = 250     # tab_bottom=263, SHELF_Y=258 → tab hangs 8px above shelf, 5px inside
# Footer bar
BAR_H    = 36
BAR_CY   = 285     # bar_top=267, bar_bottom=303
BAR_RAD  = 10
BOT_GEM_R  = 11
BOT_GEM_CY = 309
BOT_GEM_LX = 33
BOT_GEM_RX = 167

PAL   = sc.RARITY["epic"]
PRICE = 500

HAIR_GOLD   = sc.CARD_RING_BRIGHT
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


def _draw_shelf(big, affordable):
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)

    # Shelf tray
    shelf_stops = ([(0.0, (28, 30, 62)), (1.0, (14, 16, 40))] if affordable
                   else [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))])
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=30)
    lip = (115, 106, 140) if affordable else (62, 62, 86)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Price tab — drawn first, mostly above shelf, hangs at top lip
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (m(CX), m(CHIP_CY))
    crad = m(CHIP_RAD)
    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=80, dy=m(2))
    tab_stops = ([(0.0, (40, 42, 74)), (1.0, (26, 28, 54))] if affordable
                 else [(0.0, (40, 42, 62)), (1.0, (28, 28, 46))])
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, tab_stops, 255), chip.topleft)
    sc.top_sheen(big, chip, crad, m(9), peak=30 if affordable else 14)
    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 200), w=max(1, m(1.4)))
    else:
        sc.bevel_rim(big, chip, crad, (44, 58, 58, 200), (110, 130, 130, 160),
                     w=max(1, m(1.2)))

    # Coin + price inside tab
    txt      = f"{PRICE:,}"
    num_font = sc.font(18)
    coin_r   = m(11)
    coin_d   = coin_r * 2
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_d + gap + num_w
    left     = m(CX) - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_d + gap + num_w // 2
    if affordable:
        sc.coin_glyph(big, coin_cx, m(CHIP_CY), coin_r)
        sc.plain_text(big, txt, num_font, (num_cx, m(CHIP_CY) + m(1)), (236, 240, 232),
                      shadow_a=0, weight=m(0.7))
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, m(CHIP_CY)), coin_r)
        sc.plain_text(big, txt, num_font, (num_cx, m(CHIP_CY) + m(1)), (140, 144, 152),
                      shadow_a=0, weight=m(0.7))

    # Split footer bar — BUY left half, CANCEL right half
    bar_top  = m(BAR_CY) - m(BAR_H) // 2
    bar_bot  = bar_top + m(BAR_H)
    bar_left = m(SHELF_X)
    bar_right= m(SHELF_X + SHELF_W)
    bar_mid  = m(CX)
    bar_rad  = m(BAR_RAD)

    # BUY left half (rounded bottom-left + top-left corners)
    buy_rect = pygame.Rect(bar_left, bar_top, bar_mid - bar_left, m(BAR_H))
    if affordable:
        buy_stops = [(0.0, (48, 52, 108)), (1.0, (28, 32, 72))]
        buy_lab   = (214, 220, 250)
    else:
        buy_stops = [(0.0, (58, 60, 74)), (1.0, (40, 42, 54))]
        buy_lab   = (150, 152, 162)
    sc.drop_shadow(big, buy_rect, bar_rad, blur=m(3), alpha=90, dy=m(2))
    # Draw left half with full radius but squared right edge
    buy_surf = sc.vgrad_stops(buy_rect.w + bar_rad, buy_rect.h, bar_rad, buy_stops, 255)
    buy_surf = buy_surf.subsurface((0, 0, buy_rect.w, buy_rect.h)).copy()
    big.blit(buy_surf, buy_rect.topleft)
    sc.top_sheen(big, buy_rect, 0, m(10), peak=28 if affordable else 10)
    # BUY label
    buy_font = sc.font(14)
    if affordable:
        sc.plain_text(big, "BUY", buy_font, buy_rect.center, buy_lab,
                      shadow_a=100, weight=m(0.8), keyline=(8, 6, 20), kw=m(0.9))
    else:
        lock_h = m(12)
        _padlock(big, buy_rect.centerx, buy_rect.centery, lock_h, buy_lab)

    # CANCEL right half (rounded bottom-right + top-right corners)
    can_rect  = pygame.Rect(bar_mid, bar_top, bar_right - bar_mid, m(BAR_H))
    can_stops = [(0.0, (26, 28, 64)), (1.0, (14, 16, 44))]
    can_lab   = (150, 155, 200)
    sc.drop_shadow(big, can_rect, bar_rad, blur=m(3), alpha=70, dy=m(2))
    # Draw right half: full-radius on right side, squared left edge
    can_surf = sc.vgrad_stops(can_rect.w + bar_rad, can_rect.h, bar_rad, can_stops, 255)
    can_surf = can_surf.subsurface((bar_rad, 0, can_rect.w, can_rect.h)).copy()
    big.blit(can_surf, can_rect.topleft)
    sc.top_sheen(big, can_rect, 0, m(10), peak=18)
    can_font = sc.font(12)
    sc.plain_text(big, "CANCEL", can_font, can_rect.center, can_lab,
                  shadow_a=80, weight=m(0.7), keyline=(6, 6, 18), kw=m(0.8))

    # Seam between BUY and CANCEL
    pygame.draw.line(big, (*sc.CARD_RING_DEEP[:3], 200),
                     (bar_mid, bar_top + m(2)), (bar_mid, bar_bot - m(2)), max(1, m(1)))
    pygame.draw.line(big, (160, 156, 200, 80),
                     (bar_mid + max(1, m(1)), bar_top + m(2)),
                     (bar_mid + max(1, m(1)), bar_bot - m(2)), max(1, m(1)))

    # Outer rim around the whole bar (draw as one rect)
    bar_full = pygame.Rect(bar_left, bar_top, bar_right - bar_left, m(BAR_H))
    pygame.draw.rect(big, (*sc.CARD_RING_BRIGHT, 120), bar_full,
                     width=max(1, m(1)), border_radius=bar_rad)


def _draw_bottom_gems(big, affordable):
    for gem_cx in [m(BOT_GEM_LX), m(BOT_GEM_RX)]:
        if affordable:
            sc._alpha_aura(big, gem_cx, m(BOT_GEM_CY), m(16), PAL["glow"], peak=60, layers=14)
            sc.facet_gem(big, gem_cx, m(BOT_GEM_CY), m(BOT_GEM_R), PAL["gem"], PAL["deep"])
        else:
            sc._alpha_aura(big, gem_cx, m(BOT_GEM_CY), m(16), (90, 92, 110), peak=35, layers=14)
            sc.facet_gem(big, gem_cx, m(BOT_GEM_CY), m(BOT_GEM_R), (80, 82, 100), (50, 52, 66))


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

    # Bottom frame gems drawn AFTER shelf so they sit on top of any shelf overlap
    _draw_bottom_gems(big, affordable)

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


MARGIN, HDR_H, GAP_HDR = 18, 28, 8
CANVAS_W, CANVAS_H     = 444, 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, MARGIN + HDR_H // 2),
          "hanging-price-tab  |  AFFORDABLE / UNAFFORDABLE",
          fill=(180, 200, 240), font=fnt_hdr, anchor="mm")

panels_y    = MARGIN + HDR_H + GAP_HDR
panels_data = []
for px, affordable in [(18, True), (226, False)]:
    surf  = render_popup("TEMPEST", affordable)
    bg    = pygame.Surface((POP_W, POP_H))
    bg.fill((8, 8, 20))
    bg.blit(surf, (0, 0))
    raw   = pygame.image.tostring(bg, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panels_data.append((px, affordable, panel))

for px, affordable, panel in panels_data:
    canvas.paste(panel, (px, panels_y))
    bx, by = px + 5, panels_y + 5
    badge  = "4"
    bw     = int(fnt_badge.getlength(badge)) + 8
    draw.rounded_rectangle([bx - 1, by - 1, bx + bw + 1, by + 18], radius=5,
                            fill=(170, 160, 220))
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), badge, fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
      "docs", "store_confirm_shelf_v3", "shelf-redesign", "hanging-price-tab", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# PIL verification
img    = Image.open(OUT)
tab    = img.getpixel((18 + 100, 54 + 250))   # price tab centre
bar    = img.getpixel((18 + 60,  54 + 285))   # BUY half centre
gem_l  = img.getpixel((18 + 33,  54 + 309))   # left bottom gem
print(f"size:{img.size}  tab:{tab}  bar:{bar}  gem_l:{gem_l}")
