"""Round 1 — 'wax-seal-verdict' store-confirm shelf concept.

Twin medallion pair (BUY = big warm-gold legendary disc, CANCEL = smaller
steel-blue disc) with a domed gold wax-seal price disc floating above them.
Two panels: affordable (full colour) vs unaffordable (BUY greys + locks, the
wax-seal desaturates, CANCEL stays saturated blue so the escape hatch reads).

Output: docs/store_confirm_shelf_v1/wax-seal-verdict/round_1.png
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
from PIL import Image, ImageDraw, ImageFont

pygame.init()
pygame.display.set_mode((1, 1))

import game.store_cards as sc

SS = sc.SS
m  = sc.m

POP_W, POP_H = 200, 340
CX           = POP_W // 2

CARD_X, CARD_W, CARD_TOP, CARD_H, CARD_RAD = 8, 184, 98, 230, 18
R_HERO, DISC_CY                            = 41, 104
GEM_R, GEM_CY, GEM_L_X, GEM_R_X            = 11, 117, 33, 167
BANNER_W                                   = 120
SHELF_X, SHELF_Y, SHELF_W, SHELF_H         = 13, 235, 174, 87

PAL   = sc.RARITY["epic"]
PRICE = 500

# ── wax-seal shelf: the medallion verdict pair + gold price disc ──────────────

def _blend_circle(big, cx, cy, r, color, alpha):
    """Alpha-blended fill so domed highlights read as light, not paint."""
    g = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(g, (*color, alpha), (r + 1, r + 1), r)
    big.blit(g, (cx - r - 1, cy - r - 1))


def _sheen_ellipse(big, cx, cy, w, h, color, alpha):
    """Top-of-dome specular smear on the indigo medallion body."""
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.ellipse(g, (*color, alpha), g.get_rect())
    big.blit(g, (cx - w // 2, cy - h // 2))


def _padlock(big, cx, cy):
    """Locked indicator over the greyed BUY gem — dark shackle + body."""
    col = (58, 60, 72)
    body = pygame.Rect(0, 0, m(8), m(7))
    body.center = (cx, cy + m(2))
    pygame.draw.rect(big, col, body, border_radius=m(1.5))
    shackle = pygame.Rect(body.centerx - m(3), body.top - m(4), m(6), m(8))
    pygame.draw.arc(big, col, shackle, 0, math.pi, max(2, m(1.6)))


def _draw_shelf(big, affordable):
    # base shelf ground (unchanged from the v4 confirm popup)
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

    wax_c   = (m(CX), m(249))
    wax_r   = m(18)
    buy_c   = (m(58), m(295))
    buy_r   = m(28)
    can_c   = (m(142), m(295))
    can_r   = m(22)

    # ── phase A: glows (behind everything) ───────────────────────────────────
    if affordable:
        sc._alpha_aura(big, wax_c[0], wax_c[1], wax_r + m(14), (190, 145, 30),
                       peak=55, layers=10)
        sc._alpha_aura(big, buy_c[0], buy_c[1], buy_r + m(14), (180, 130, 30),
                       peak=50, layers=10)
    # CANCEL keeps its cool glow in both states — the exit stays alive
    sc._alpha_aura(big, can_c[0], can_c[1], can_r + m(10), (60, 100, 170),
                   peak=35, layers=8)

    # ── phase B: disc bodies + rings ─────────────────────────────────────────
    # wax-seal price disc
    disc_base = (170, 125, 20) if affordable else (90, 90, 100)
    hi_col    = (220, 180, 70) if affordable else (140, 140, 150)
    ring_col  = (210, 170, 60) if affordable else (130, 130, 145)
    pygame.draw.circle(big, disc_base, wax_c, wax_r)
    _blend_circle(big, wax_c[0] - m(4), wax_c[1] - m(4), m(10), hi_col, 130)
    pygame.draw.circle(big, ring_col, wax_c, wax_r, max(1, m(1.5)))

    # BUY medallion body
    pygame.draw.circle(big, (26, 28, 58), buy_c, buy_r)
    _sheen_ellipse(big, buy_c[0], buy_c[1] - m(10), m(40), m(18), (48, 50, 82), 150)
    buy_ring = (200, 158, 50) if affordable else (110, 112, 130)
    pygame.draw.circle(big, buy_ring, buy_c, buy_r, max(2, m(2)))

    # CANCEL medallion body (always saturated)
    pygame.draw.circle(big, (26, 28, 58), can_c, can_r)
    _sheen_ellipse(big, can_c[0], can_c[1] - m(8), m(30), m(14), (48, 50, 82), 150)
    pygame.draw.circle(big, (80, 120, 180), can_c, can_r, max(2, m(2)))

    # ── phase C: gems, glyphs + labels on top ────────────────────────────────
    # wax-seal: coin glyph (left) + '500' ink (right)
    coin_r   = m(11)
    num_font = sc.font(14)
    num_txt  = f"{PRICE}"
    num_w    = num_font.size(num_txt)[0]
    gap      = m(2)
    total    = coin_r * 2 + gap + num_w
    left     = wax_c[0] - total // 2
    left_cx  = left + coin_r
    right_cx = left + coin_r * 2 + gap + num_w // 2
    sc.coin_glyph(big, left_cx, wax_c[1], coin_r)
    num_col = (60, 28, 4) if affordable else (44, 44, 54)
    sc.plain_text(big, num_txt, num_font, (right_cx, wax_c[1] + m(2)), num_col,
                  shadow_a=0, weight=m(0.8))

    # BUY gem + label
    if affordable:
        sc.facet_gem(big, buy_c[0], buy_c[1], m(14), (230, 185, 60), (100, 65, 10))
        buy_lab_col = (235, 210, 155)
    else:
        sc.facet_gem(big, buy_c[0], buy_c[1], m(14), (130, 130, 140), (50, 50, 60))
        _padlock(big, buy_c[0], buy_c[1])
        buy_lab_col = (120, 122, 138)
    sc.plain_text(big, "BUY", sc.font(11), (buy_c[0], m(327)), buy_lab_col,
                  shadow_a=120, weight=m(0.8), keyline=(10, 10, 22), kw=m(0.8))

    # CANCEL gem + label (always saturated blue)
    sc.facet_gem(big, can_c[0], can_c[1], m(11), (100, 150, 220), (30, 60, 130))
    sc.plain_text(big, "CANCEL", sc.font(10), (can_c[0], m(327)), (165, 175, 210),
                  shadow_a=120, weight=m(0.7), keyline=(10, 12, 26), kw=m(0.7))


# ── popup renderer (base copied from the v4 confirm popup) ────────────────────

def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()


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
        nf33   = sc.font(33)
        draw_f = nf33 if _nw(name, nf33) <= safe_w else nf30
        sc.plain_text(big, name, draw_f, (m(CX), m(base_y)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        banner_y = base_y + 20
    else:
        spaces = [i for i, c in enumerate(name) if c == ' ']
        if spaces:
            best = min(spaces, key=lambda i: max(_nw(name[:i], nf30), _nw(name[i + 1:], nf30)))
            l1, l2 = name[:best], name[best + 1:]
        else:
            bi, bm = 1, float('inf')
            for i in range(1, len(name)):
                if name[i - 1] == '-' or name[i] == '-':
                    continue
                mw = max(_nw(name[:i] + '-', nf30), _nw(name[i:], nf30))
                if mw < bm:
                    bm, bi = mw, i
            l1, l2 = name[:bi] + '-', name[bi:]
        sc.plain_text(big, l1, sc.font(30), (m(CX), m(base_y - 11)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        sc.plain_text(big, l2, sc.font(27), (m(CX), m(base_y + 11)), (250, 248, 240),
                      shadow_a=120, weight=m(0.8), keyline=(6, 6, 16), kw=m(1.0))
        banner_y = base_y + 40

    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(banner_y), m(BANNER_W), PAL)

    # shelf — the wax-seal verdict pair
    _draw_shelf(big, affordable)

    # disc + aura + thumb (last)
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── 2-panel sheet ─────────────────────────────────────────────────────────────

MARGIN   = 18
GAP      = 8
TITLE_H  = 28
NAME     = "TEMPEST"
BASE_Y   = 178

PANELS = [
    ("E", True,  "AFFORDABLE"),
    ("E", False, "UNAFFORDABLE"),
]

CANVAS_W = MARGIN + POP_W + GAP + POP_W + MARGIN            # 444
CANVAS_H = MARGIN + TITLE_H + GAP + POP_H + MARGIN          # 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
except Exception:
    fnt_title = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, MARGIN + TITLE_H // 2),
          "WAX-SEAL-VERDICT  |  AFFORDABLE / UNAFFORDABLE",
          fill=(235, 220, 160), font=fnt_title, anchor="mm")

py = MARGIN + TITLE_H + GAP
for i, (badge_id, affordable, _) in enumerate(PANELS):
    px = MARGIN + i * (POP_W + GAP)

    popup_surf = render_popup(NAME, BASE_Y, affordable)
    raw   = pygame.image.tostring(popup_surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, py))

    bx, by = px + 5, py + 5
    bw, bh = fnt_badge.getlength(badge_id) + 8, 17
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + bh // 2), badge_id, fill=(230, 225, 245),
              font=fnt_badge, anchor="lm")

OUT = "docs/store_confirm_shelf_v1/wax-seal-verdict/round_1.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved  {OUT}  ({CANVAS_W}x{CANVAS_H})")
