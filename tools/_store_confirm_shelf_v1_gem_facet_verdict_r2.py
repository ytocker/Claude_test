"""Shelf concept C — GEM-FACET-VERDICT (round 2).

Revised on art-director critique: explicit facet crease lines (girdle seam +
culet seam) so the gem reads as a cut stone, not just a coloured lozenge; crown
polygon alpha raised to 128 so the top face visibly outvalues the pavilion;
grey-quartz fill lifted + given a cool blue cast so BUY passes luminance
separation from amethyst CANCEL on all displays; BUY/CANCEL size ratio pushed to
~1.4× for a clear call-to-action hierarchy; hot specular pip moved fully into the
upper-left crown facet above the girdle seam; quartz rim darkened to contrast the
now-lighter quartz fill.

Output → docs/store_confirm_shelf_v1/gem-facet-verdict/round_2.png
"""
import sys, os, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
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
SHELF_X, SHELF_Y, SHELF_W, SHELF_H        = 13, 235, 174, 87

PAL   = sc.RARITY["epic"]
PRICE = 500
NAME  = "TEMPEST CONDOR"
BASE_Y = 178

# ── gem-lozenge builder ──────────────────────────────────────────────────────

def _hex_points(cx, cy, w, h):
    """Stretched horizontal hexagon (elongated lozenge): pointed left/right tips
    with a flat top+bottom edge so the facet reads as a cut lozenge."""
    inset = int(h * 0.62)
    x0, y0 = cx - w // 2, cy - h // 2
    return [
        (x0,              cy),          # left tip
        (x0 + inset,      y0),          # top-left shoulder
        (x0 + w - inset,  y0),          # top-right shoulder
        (x0 + w,          cy),          # right tip
        (x0 + w - inset,  y0 + h),      # bottom-right shoulder
        (x0 + inset,      y0 + h),      # bottom-left shoulder
    ]


def _gem_lozenge(big, cx, cy, w, h, stops, crown_col, rim_col, pip_r,
                 aura_col=None, aura_peak=60, aura_layers=10):
    # Warm/cool halo seats the gem into the shelf before the facet is drawn.
    if aura_col is not None:
        sc._alpha_aura(big, cx, cy, w // 2 + m(12), aura_col,
                       peak=aura_peak, layers=aura_layers)

    pts_abs = _hex_points(cx, cy, w, h)
    x0, y0  = cx - w // 2, cy - h // 2
    pts_loc = [(px - x0, py - y0) for px, py in pts_abs]

    # Base ramp clipped to the lozenge outline.
    surf = sc.vgrad_stops(w, h, 0, stops, 255).copy()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts_loc)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Girdle + culet crease lines on a masked overlay so the upper and lower
    # cut planes read as distinct facets rather than a flat gradient blob.
    deep_col = stops[-1][1]
    seam_col = (*deep_col, int(255 * 0.45))
    crease   = pygame.Surface((w, h), pygame.SRCALPHA)
    # horizontal girdle seam at the gem's equator
    pygame.draw.line(crease, seam_col, (0, h // 2), (w - 1, h // 2), 1)
    # short culet seam from top-edge centre down ~40% of gem height
    pygame.draw.line(crease, seam_col, (w // 2, 0), (w // 2, int(h * 0.42)), 1)
    crease.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(crease, (0, 0))

    # Crown facets — alpha 128 so the top face visibly outvalues the pavilion.
    lt    = (pts_loc[0][0], cy - y0)    # left tip in local space
    tl    = pts_loc[1]                  # top-left shoulder
    tmid  = (w // 2, 0)                 # top-edge centre
    ctr   = (w // 2, h // 2)
    crown = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(crown, crown_col, [lt, tl, ctr])
    pygame.draw.polygon(crown, crown_col, [tl, tmid, ctr])
    crown.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(crown, (0, 0))

    # Hot specular pip inside the upper-left crown facet, above the girdle line.
    # Position 22%/28% from left/top keeps it clear of the culet and girdle seams.
    pip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 235),
                       (int(w * 0.22), int(h * 0.28)), pip_r)
    surf.blit(pip, (0, 0), special_flags=pygame.BLEND_ADD)

    big.blit(surf, (x0, y0))

    # Bright girdle outline.
    pygame.draw.polygon(big, rim_col, pts_abs, max(2, m(1)))


# ── plaque + label helpers ───────────────────────────────────────────────────

def _price_plaque(big, affordable):
    rect = pygame.Rect(0, 0, m(130), m(22))
    rect.center = (m(CX), m(249))
    rad = m(6)
    sc.drop_shadow(big, rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(rect.w, rect.h, rad,
             [(0.0, (32, 34, 60)), (1.0, (20, 22, 44))], 255), rect.topleft)
    sc.bevel_rim(big, rect, rad, (12, 12, 28, 190), (240, 210, 140, 210),
                 w=max(1, m(1.2)))

    txt      = f"{PRICE}"
    num_font = sc.font(15)
    coin_r   = m(10)
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_r * 2 + gap + num_w
    left     = m(CX) - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_r * 2 + gap + num_w // 2

    if affordable:
        sc.coin_glyph(big, coin_cx, m(249), coin_r)
        num_col = (240, 210, 140)
    else:
        # Grey coin disc + numeral so the price reads locked at a glance.
        pygame.draw.circle(big, (120, 122, 135), (coin_cx, m(249)), coin_r)
        pygame.draw.circle(big, (86, 88, 100), (coin_cx, m(249)), coin_r,
                           max(1, m(1)))
        num_col = (110, 115, 130)
    sc.plain_text(big, txt, num_font, (num_cx, m(249)), num_col,
                  shadow_a=90, weight=m(0.8), keyline=(10, 10, 24), kw=m(0.7))


# ── main popup renderer ───────────────────────────────────────────────────────

def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()


def render_popup(affordable):
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
    sc.plain_text(big, NAME.split()[0], sc.font(30), (m(CX), m(BASE_Y - 11)),
                  (250, 248, 240), shadow_a=160, weight=m(0.9),
                  keyline=(6, 6, 16), kw=m(1.0))
    sc.plain_text(big, NAME.split()[1], sc.font(27), (m(CX), m(BASE_Y + 11)),
                  (250, 248, 240), shadow_a=120, weight=m(0.8),
                  keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(BASE_Y + 40), m(BANNER_W), PAL)

    # ── shelf (base layer) ────────────────────────────────────────────────────
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
    pygame.draw.line(shelf, (115, 106, 140), (0, 0),
                     (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # price plaque
    _price_plaque(big, affordable)

    # BUY lozenge — 80×36, ~1.4× wider than CANCEL (52×26) for clear hierarchy.
    if affordable:
        _gem_lozenge(big, m(58), m(295), m(80), m(36),
                     [(0.0, (210, 165, 50)), (0.5, (245, 195, 80)),
                      (1.0, (165, 125, 30))],
                     crown_col=(255, 230, 130, 128), rim_col=(255, 220, 100),
                     pip_r=m(3), aura_col=(200, 160, 40),
                     aura_peak=60, aura_layers=10)
        buy_lbl = (240, 215, 160)
    else:
        # Grey-quartz with a +5 blue cast throughout — lighter than R1 so it
        # clears amethyst CANCEL in luminance, and the blue cast reads as a
        # different stone (not just dimmed gold).
        _gem_lozenge(big, m(58), m(295), m(80), m(36),
                     [(0.0, (150, 152, 169)), (0.5, (182, 184, 203)),
                      (1.0, (120, 122, 141))],
                     crown_col=(232, 236, 246, 128),
                     # rim darkened so it contrasts the lifted frostier fill
                     rim_col=(110, 112, 128),
                     pip_r=m(3), aura_col=None)
        buy_lbl = (160, 162, 178)
    sc.plain_text(big, "BUY", sc.font(11), (m(58), m(316)), buy_lbl,
                  shadow_a=110, weight=m(0.8), keyline=(12, 12, 26), kw=m(0.7))

    # CANCEL lozenge — cool amethyst, trimmed to 52×26 (~0.72× BUY) so the
    # call-to-action hierarchy is unmissable.
    _gem_lozenge(big, m(142), m(295), m(52), m(26),
                 [(0.0, (100, 70, 160)), (0.5, (130, 95, 195)),
                  (1.0, (75, 50, 130))],
                 crown_col=(228, 200, 255, 128), rim_col=(160, 130, 220),
                 pip_r=m(2), aura_col=(100, 70, 160),
                 aura_peak=40, aura_layers=8)
    sc.plain_text(big, "CANCEL", sc.font(10), (m(142), m(316)), (175, 168, 210),
                  shadow_a=110, weight=m(0.7), keyline=(14, 12, 26), kw=m(0.6))

    # disc + aura + thumb LAST so the hero sits above the shelf.
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
TITLE_H  = 28
GAP      = 8
CANVAS_W = MARGIN + POP_W + GAP + POP_W + MARGIN   # 444
CANVAS_H = MARGIN + TITLE_H + GAP + POP_H + MARGIN  # 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_title = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    fnt_sub   = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    fnt_badge = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
except Exception:
    fnt_title = fnt_sub = fnt_badge = ImageFont.load_default()

draw.text((MARGIN, MARGIN + TITLE_H // 2),
          "GEM-FACET-VERDICT  |  AFFORDABLE / UNAFFORDABLE",
          fill=(235, 228, 250), font=fnt_title, anchor="lm")

PANELS = [
    (True,  "AFFORDABLE"),
    (False, "UNAFFORDABLE"),
]

py = MARGIN + TITLE_H + GAP
for i, (affordable, sub) in enumerate(PANELS):
    px = MARGIN + i * (POP_W + GAP)

    surf  = render_popup(affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, py))

    # ID badge "C"
    bx, by = px + 5, py + 5
    bw, bh = fnt_badge.getlength("C") + 8, 17
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + bh // 2), "C", fill=(230, 225, 245),
              font=fnt_badge, anchor="lm")

    # per-panel sub-label
    draw.text((px + POP_W - 5, py + 6), sub, fill=(180, 175, 210),
              font=fnt_sub, anchor="ra")

OUT = "docs/store_confirm_shelf_v1/gem-facet-verdict/round_2.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved  {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL pixel verification ────────────────────────────────────────────────────
from PIL import Image as PILImage

img = PILImage.open(OUT).convert("RGB")

# (a) Affordable BUY gem centre: sample slightly below equator (pavilion zone)
# to avoid crown facet averaging and confirm warm gold fill is dominant.
# BUY lozenge centre = (58, 295) in popup; pavilion sample at y=300.
aff_buy_x = MARGIN + 58
aff_buy_y = py + 300
r, g, b = img.getpixel((aff_buy_x, aff_buy_y))
print(f"Affordable BUY pavilion pixel  ({aff_buy_x},{aff_buy_y}): R={r} G={g} B={b}")
assert r > 200 and g > 150 and b < 100, \
    f"FAIL warm-gold check: R={r} G={g} B={b}"
print("  PASS: warm gold")

# (b) Unaffordable BUY gem luminance must be >= 40 above CANCEL gem luminance,
# confirming the lifted grey-quartz fill clears amethyst on all displays.
unaff_px     = MARGIN + POP_W + GAP   # x start of second panel
unaff_buy_x  = unaff_px + 58
unaff_buy_y  = py + 295
r2, g2, b2   = img.getpixel((unaff_buy_x, unaff_buy_y))
lum_buy      = 0.299 * r2 + 0.587 * g2 + 0.114 * b2

unaff_can_x  = unaff_px + 142
unaff_can_y  = py + 295
r3, g3, b3   = img.getpixel((unaff_can_x, unaff_can_y))
lum_cancel   = 0.299 * r3 + 0.587 * g3 + 0.114 * b3

print(f"Unaffordable BUY   ({unaff_buy_x},{unaff_buy_y}): "
      f"R={r2} G={g2} B={b2}  lum={lum_buy:.1f}")
print(f"Unaffordable CANCEL({unaff_can_x},{unaff_can_y}): "
      f"R={r3} G={g3} B={b3}  lum={lum_cancel:.1f}")
print(f"Luminance gap: {lum_buy - lum_cancel:.1f}")
assert lum_buy - lum_cancel >= 40, (
    f"FAIL luminance-gap check: BUY={lum_buy:.1f}, "
    f"CANCEL={lum_cancel:.1f}, gap={lum_buy - lum_cancel:.1f}")
print("  PASS: luminance separation >= 40")
