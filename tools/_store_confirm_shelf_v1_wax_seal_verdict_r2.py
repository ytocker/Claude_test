"""Round 2 — 'wax-seal-verdict' store-confirm shelf concept.

All art-director notes from round 1 applied, in priority order:
1. Wax-seal enlarged (r=18→26) — disc comfortably houses glyph + numeral.
2. Unaffordable disc lightened to (148,150,162) so dark ink reads;
   coin replaced with a flat grey disc+ring to match the muted palette.
3. BUY medallion enlarged (r=28→31), CANCEL shrunk (r=22→20); thinner
   CANCEL ring stroke vs bolder BUY ring to push the dominance hierarchy.
4. Checkmark (✓) on BUY gem, ✕ on CANCEL gem — both panels — so each
   circle reads as an icon-button, not a colour blob.
5. Wax centre raised (y=249→243) to seat the seal above the BUY medallion
   top with a visible spatial gap before the disc bodies merge.

Output: docs/store_confirm_shelf_v1/wax-seal-verdict/round_2.png
"""
import sys, os, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

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

    # Wax centre raised to y=243 so the seal floats with a seat gap over BUY.
    # BUY enlarged (r→31) for dominance; CANCEL shrunk (r→20) to stay secondary.
    wax_c   = (m(CX), m(243))
    wax_r   = m(26)
    buy_c   = (m(58), m(295))
    buy_r   = m(31)
    can_c   = (m(142), m(295))
    can_r   = m(20)

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
    # Wax-seal price disc.  Unaffordable disc_base lifted to (148,150,162) so
    # the dark ink numeral (44,44,54) achieves readable contrast on the ground.
    disc_base = (170, 125, 20) if affordable else (148, 150, 162)
    hi_col    = (220, 180, 70) if affordable else (190, 192, 204)
    ring_col  = (210, 170, 60) if affordable else (118, 120, 132)
    pygame.draw.circle(big, disc_base, wax_c, wax_r)
    # Dome highlight offset proportionally to the larger disc
    _blend_circle(big, wax_c[0] - m(5), wax_c[1] - m(5), m(12), hi_col, 130)
    pygame.draw.circle(big, ring_col, wax_c, wax_r, max(1, m(1.5)))

    # BUY medallion body — bolder ring stroke reinforces dominance
    pygame.draw.circle(big, (26, 28, 58), buy_c, buy_r)
    _sheen_ellipse(big, buy_c[0], buy_c[1] - m(10), m(40), m(18), (48, 50, 82), 150)
    buy_ring = (200, 158, 50) if affordable else (110, 112, 130)
    pygame.draw.circle(big, buy_ring, buy_c, buy_r, max(2, m(2.5)))

    # CANCEL medallion body — thinner ring stroke reads as secondary
    pygame.draw.circle(big, (26, 28, 58), can_c, can_r)
    _sheen_ellipse(big, can_c[0], can_c[1] - m(8), m(30), m(14), (48, 50, 82), 150)
    pygame.draw.circle(big, (80, 120, 180), can_c, can_r, max(1, m(1.5)))

    # ── phase C: gems, action glyphs + labels on top ─────────────────────────
    # Wax-seal: coin glyph (left) + price numeral (right), centred in the disc
    coin_r   = m(11)
    num_font = sc.font(14)
    num_txt  = f"{PRICE}"
    num_w    = num_font.size(num_txt)[0]
    gap      = m(2)
    total    = coin_r * 2 + gap + num_w
    left     = wax_c[0] - total // 2
    coin_cx  = left + coin_r
    right_cx = left + coin_r * 2 + gap + num_w // 2

    if affordable:
        sc.coin_glyph(big, coin_cx, wax_c[1], coin_r)
    else:
        # Grey disc+ring replaces the full-colour coin so both coin and disc
        # read "off" together — a unified desaturated muted state.
        grey_r = wax_r // 2 - m(2)
        pygame.draw.circle(big, (130, 132, 144), (coin_cx, wax_c[1]), grey_r)
        pygame.draw.circle(big, (100, 102, 114), (coin_cx, wax_c[1]), grey_r,
                           max(1, m(1.5)))

    num_col = (60, 28, 4) if affordable else (44, 44, 54)
    sc.plain_text(big, num_txt, num_font, (right_cx, wax_c[1] + m(2)), num_col,
                  shadow_a=0, weight=m(0.8))

    # BUY gem (larger r=16 to fill the enlarged medallion) + checkmark glyph.
    # Padlock dropped — the check/lock semantic is now carried by the icon.
    buy_gem_r = m(16)
    if affordable:
        sc.facet_gem(big, buy_c[0], buy_c[1], buy_gem_r, (230, 185, 60), (100, 65, 10))
        buy_lab_col = (235, 210, 155)
        ck_col      = (240, 220, 160)    # warm cream on gold gem
    else:
        sc.facet_gem(big, buy_c[0], buy_c[1], buy_gem_r, (130, 130, 140), (50, 50, 60))
        buy_lab_col = (120, 122, 138)
        ck_col      = (150, 148, 140)    # muted neutral on grey gem

    # Checkmark: short left arm + long right arm, classic √ proportion
    vx, vy = buy_c[0] - m(1), buy_c[1] + m(5)
    l_arm  = (buy_c[0] - m(8), buy_c[1] - m(1))
    r_arm  = (buy_c[0] + m(12), buy_c[1] - m(11))
    pygame.draw.line(big, ck_col, l_arm, (vx, vy),   max(2, m(2)))
    pygame.draw.line(big, ck_col, (vx, vy), r_arm,   max(2, m(2)))

    sc.plain_text(big, "BUY", sc.font(11), (buy_c[0], m(327)), buy_lab_col,
                  shadow_a=120, weight=m(0.8), keyline=(10, 10, 22), kw=m(0.8))

    # CANCEL gem + ✕ glyph — always saturated blue so the exit stays alive
    can_gem_r = m(10)
    sc.facet_gem(big, can_c[0], can_c[1], can_gem_r, (100, 150, 220), (30, 60, 130))

    # ✕: two crossed diagonals, cool cream colour, sized to the smaller gem
    x_col = (175, 185, 215)
    x_r   = m(6)
    pygame.draw.line(big, x_col,
                     (can_c[0] - x_r, can_c[1] - x_r),
                     (can_c[0] + x_r, can_c[1] + x_r), max(2, m(2)))
    pygame.draw.line(big, x_col,
                     (can_c[0] + x_r, can_c[1] - x_r),
                     (can_c[0] - x_r, can_c[1] + x_r), max(2, m(2)))

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

OUT = "docs/store_confirm_shelf_v1/wax-seal-verdict/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved  {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL pixel verification ────────────────────────────────────────────────────
img = Image.open(OUT)
rgb = img.load()

# Panel origin in canvas coords
AX0 = MARGIN                    # affordable panel left edge x
UX0 = MARGIN + POP_W + GAP     # unaffordable panel left edge x
PY0 = MARGIN + TITLE_H + GAP   # panel top edge y

# (a) Affordable wax disc body has gold pixels: R>120, G>60, B<60.
# Sample 13 px ABOVE the disc centre (y=230) where the bare disc body is
# exposed above the coin+numeral row (coin and text sit at y≈243).
ax_wax = AX0 + CX
ay_wax = PY0 + 230
r0, g0, b0 = rgb[ax_wax, ay_wax]
assert r0 > 120 and g0 > 60 and b0 < 60, \
    f"(a) Expected gold at affordable wax disc (above content), got ({r0},{g0},{b0})"
print(f"(a) PASS — affordable wax disc ({r0},{g0},{b0}) is gold")

# (b) Unaffordable wax disc is clearly lighter than the card body.
# Same y=230 above-content sample for consistency; compare to card body
# 55 px to the right (past the disc edge at x=CX+26=126).
ux_wax = UX0 + CX
uy_wax = PY0 + 230
ru, gu, bu = rgb[ux_wax, uy_wax]
card_x = min(ux_wax + 55, CANVAS_W - 1)
rc, gc, bc = rgb[card_x, uy_wax]
disc_lum = (ru + gu + bu) / 3
card_lum = (rc + gc + bc) / 3
assert disc_lum > card_lum + 40, \
    f"(b) Unaffordable disc ({ru},{gu},{bu}) not clearly lighter than card ({rc},{gc},{bc})"
print(f"(b) PASS — unaffordable disc lum {disc_lum:.0f} vs card lum {card_lum:.0f}")

# (c) CANCEL gem stays blue (B > R) in both panels.
can_lx_a = AX0 + 142   # cancel centre x, affordable panel
can_lx_u = UX0 + 142   # cancel centre x, unaffordable panel
can_ly    = PY0 + 295   # cancel centre y (same in both panels)
for cx_s, label in [(can_lx_a, "affordable"), (can_lx_u, "unaffordable")]:
    rs, gs, bs = rgb[cx_s, can_ly]
    assert bs > rs, \
        f"(c) CANCEL gem not blue in {label} panel: ({rs},{gs},{bs})"
    print(f"(c) PASS — CANCEL gem {label} ({rs},{gs},{bs}) is blue")

print("All pixel verifications passed.")
