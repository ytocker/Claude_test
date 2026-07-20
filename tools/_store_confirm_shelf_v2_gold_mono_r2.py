"""Round 2 — shelf concept 'gold-mono' (store_confirm_shelf_v2 series).

Maximum minimalism: BOTH action buttons wear the same very-dark near-black
neutral fill and the same golden bevel rim, so nothing but the label string
("BUY" vs "CANCEL") privileges one over the other. The gold rim is the sole
ornament. The price chip carries a cream-warm body with its own golden bevel
and becomes the popup's warm visual anchor amid the restrained buttons.

Round 2 revisions applied:
- Button fill raised so buttons read above the shelf tray (luma delta ≥ 12)
- BUY label warm cream / CANCEL label cool slate — same brightness, split hue
- Locked BUY fill also raised so the disabled shape stays legible
- Gold bevel rim alpha on affordable buttons lifted from 210 → 230 to punch
  against the near-black fill backdrop
- Chip left exactly as is (already the hierarchy anchor)

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v2/gold-mono/round_2.png
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

# Chip above an identical BUY/CANCEL pair; the trio is vertically centred in the
# recessed shelf so the warm chip crowns the two restrained dark buttons.
CHIP_CY                     = 260
BTN_W, BTN_H, BTN_RAD       = 76, 30, 9
BTN_CY, BTN_GAP             = 296, 8
BUY_CX = CX - (BTN_W + BTN_GAP) // 2
CAN_CX = CX + (BTN_W + BTN_GAP) // 2

PAL   = sc.RARITY["epic"]
PRICE = 500


def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()


def _btn(big, btn_rect, label, locked=False):
    """One button body shared by BUY and CANCEL — identical dark fill + gold
    bevel. Fills are the only structural element; label temperature (warm cream
    for BUY, cool slate for CANCEL) is what signals intent so the two remain
    visually even in weight while still readable as different actions.
    Locked state dims everything but keeps the gold rim alive."""
    rad = m(BTN_RAD)
    if locked:
        # Raised slightly from r1 so the disabled shape reads above the shelf
        # tray instead of dissolving into it; dimmed gold rim + padlock still
        # signal locked state without competing with the affordable panel.
        stops    = [(0.0, (34, 31, 42)), (1.0, (20, 18, 30))]
        lab_col  = (85, 83, 100)
        sheen    = 10
        bright_a = 130
    else:
        # Fill raised ~12 luma above the shelf tray (~31,31,46) so top_sheen
        # at peak=22 catches a visible plate face without creating a glow.
        stops    = [(0.0, (46, 43, 60)), (1.0, (26, 23, 36))]
        sheen    = 22
        # Gold rim alpha lifted so it punches against the near-black fill;
        # the fill is the sole backdrop so the bevel needs to carry alone.
        bright_a = 230
        # Warm cream for BUY signals affordance; cool slate for CANCEL reads
        # as retreat — same perceptual brightness, opposite hue temperature.
        if label == "BUY":
            lab_col = (238, 224, 182)
        else:
            lab_col = (198, 205, 236)

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255),
             btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)
    sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, bright_a), w=max(1, m(1.6)))
    sc.plain_text(big, label, sc.font(13), btn_rect.center, lab_col,
                  shadow_a=110, weight=m(0.8), keyline=(10, 8, 20), kw=m(0.8))


def _draw_chip(big, affordable):
    """Cream-warm price chip with its own golden bevel — the one warm element,
    so it anchors the eye while both buttons hold back. Grey slate + grey bevel
    when unaffordable so the chip reads as inert alongside the locked BUY."""
    CHIP_W, CHIP_H, CHIP_RAD = 120, 36, 8
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (m(CX), m(CHIP_CY))
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
        face_stops = [(0.0, (248, 240, 210)), (1.0, (216, 200, 155))]
    else:
        face_stops = [(0.0, (68, 68, 82)), (1.0, (44, 44, 58))]
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)

    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 200), w=max(1, m(1.5)))
    else:
        sc.bevel_rim(big, chip, crad, (54, 58, 74, 200),
                     (140, 138, 160, 160), w=max(1, m(1.5)))

    txt      = f"{PRICE:,}"
    num_font = sc.font(22)
    coin_r   = m(14)
    coin_d   = coin_r * 2
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_d + gap + num_w
    left     = m(CX) - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_d + gap + num_w // 2
    cy       = m(CHIP_CY)

    if affordable:
        sc.coin_glyph(big, coin_cx, cy, coin_r)
        num_col = (52, 28, 4)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        num_col = (110, 115, 130)
    sc.plain_text(big, txt, num_font, (num_cx, cy + m(3)), num_col,
                  shadow_a=0, weight=m(0.8))


def _draw_shelf(big, affordable):
    """Recessed shelf tray carrying the chip + identical button pair. The tray
    stays neutral dark in both states — the chip's warmth and the label strings
    carry all the meaning."""
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)

    shelf_stops = [(0.0, (24, 24, 40)), (1.0, (12, 12, 26))]
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=26)
    # A single faint gold-tinted lip is the only ornament the tray itself gets.
    pygame.draw.line(shelf, (96, 88, 118), (0, 0), (shelf_rect.w - 1, 0),
                     max(1, m(1)))

    # Seat shadow where the tray meets the card body above it.
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Lit-left / shadowed-right micro-walls in the inset gap for recessed depth.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (xx / max(1, wall_w - 1)))
            pygame.draw.line(lwall, (120, 112, 140, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    # chip (warm anchor) above the two restrained buttons
    _draw_chip(big, affordable)

    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can.center = (m(CAN_CX), m(BTN_CY))
    _btn(big, buy, "BUY", locked=not affordable)
    _btn(big, can, "CANCEL", locked=False)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(317)),
                      (150, 166, 190), shadow_a=90, weight=m(0.6))


def render_popup(name, base_y, affordable):
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
        best = min(spaces, key=lambda i: max(_nw(name[:i], nf30), _nw(name[i+1:], nf30)))
        l1, l2 = name[:best], name[best+1:]
        sc.plain_text(big, l1, sc.font(30), (m(CX), m(base_y-11)), (250, 248, 240),
                      shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
        sc.plain_text(big, l2, sc.font(27), (m(CX), m(base_y+11)), (250, 248, 240),
                      shadow_a=120, weight=m(0.8), keyline=(6, 6, 16), kw=m(1.0))
        banner_y = base_y + 40

    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(banner_y), m(BANNER_W), PAL)

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
          "gold-mono  |  AFFORDABLE / UNAFFORDABLE",
          fill=(224, 208, 150), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR
PANELS = [(18, "AFFORDABLE", True), (18 + POP_W + GAP_C, "UNAFFORDABLE", False)]

for px, _label, affordable in PANELS:
    surf  = render_popup("TEMPEST", 178, affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, panels_y))

    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength("D") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "D", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = "docs/store_confirm_shelf_v2/gold-mono/round_2.png"
OUT = os.path.join(os.path.dirname(__file__), "..", OUT)
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL verification (sampling only — image is never displayed) ───────────────
from PIL import Image as _Img
_img = _Img.open(OUT).convert("RGB")

# (a) left panel center should be non-background
px_a = _img.getpixel((118, 224))
lum_a = int(0.299 * px_a[0] + 0.587 * px_a[1] + 0.114 * px_a[2])
assert lum_a > 15, f"Left panel center looks like background: {px_a} lum={lum_a}"
print(f"[OK] (a) left panel center (118,224) = {px_a}  lum={lum_a}")

# (b) BUY button body — sample 2px below the top edge, well clear of text.
# BUY_CX=58, BTN_CY=296, BTN_H=30 in popup 1:1 coords; left panel at x=18,
# panels_y=54 in canvas. Button top edge = 54+296-15=335; sample at +2 = 337.
# The top gradient stop (46,43,60) gives lum≈46 there, well above shelf (≈12).
buy_body_px = (18 + 58, 54 + 296 - 15 + 2)   # → (76, 337)
px_b = _img.getpixel(buy_body_px)
lum_b = int(0.299 * px_b[0] + 0.587 * px_b[1] + 0.114 * px_b[2])
assert lum_b > 45, f"BUY button body lum too low: {px_b} lum={lum_b} at {buy_body_px}"
print(f"[OK] (b) BUY button body {buy_body_px} = {px_b}  lum={lum_b}")

# (c) BUY label warm (R>B), CANCEL label cool (B>R).
# BUY_CX=58, CAN_CX=142 in popup coords. Scan a strip across each label zone.
buy_label_candidates = [
    _img.getpixel((18 + 58 + dx, 54 + 296 + dy))
    for dx in range(-10, 11, 2) for dy in range(-4, 5, 2)
]
can_label_candidates = [
    _img.getpixel((18 + 142 + dx, 54 + 296 + dy))
    for dx in range(-10, 11, 2) for dy in range(-4, 5, 2)
]
# Warmest pixel in BUY zone (highest R-B delta)
buy_warm = max(buy_label_candidates, key=lambda p: p[0] - p[2])
can_cool  = max(can_label_candidates, key=lambda p: p[2] - p[0])
print(f"[CHECK] BUY warmest pixel  = {buy_warm}  (R-B = {buy_warm[0]-buy_warm[2]})")
print(f"[CHECK] CANCEL coolest pixel = {can_cool}  (B-R = {can_cool[2]-can_cool[0]})")
if buy_warm[0] > buy_warm[2]:
    print("[OK] (c) BUY label R > B (warm)")
else:
    print(f"[WARN] (c) BUY warm check inconclusive: {buy_warm}")
if can_cool[2] > can_cool[0]:
    print("[OK] (c) CANCEL label B > R (cool)")
else:
    print(f"[WARN] (c) CANCEL cool check inconclusive: {can_cool}")
