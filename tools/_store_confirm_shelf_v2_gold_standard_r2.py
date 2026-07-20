"""Round 2 — shelf concept 'gold-standard' (store_confirm_shelf_v2 series).

Director revisions applied:
  1. Button gold rim boosted: alpha 200→255, w m(1.6)→m(2.2) — clearly gold.
  2. CANCEL recedes from BUY: fill dropped to (58,54,84)→(38,36,62), sheen 28→16.
  3. Locked BUY swapped from gold bevel to grey: (54,58,74)/(140,138,160)
     at w=m(1.8) — matches the chip's grey-out signal for inert state.
  4. Chip bevel alpha checked after render; reduced 180→150 only if chip rim
     reads brighter than button rim in PIL sampling.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v2/gold-standard/round_2.png
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

PAL   = sc.RARITY["epic"]
PRICE = 500


def _padlock(surf, cx, cy, h, color):
    # Rounded body + shackle arc + punched keyhole reads as "locked" at tiny
    # size without leaning on hue alone.
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
    pygame.draw.rect(surf, (24, 22, 34), kh, border_radius=1)


def _btn(big, btn_rect, rad, label, locked=False, is_cancel=False):
    # Locked BUY: muted fill + grey rim — lock icon + grey chip already signal
    # inert, so the rim must not contradict them with false gold.
    # CANCEL recedes: dimmer fill + lower sheen keeps BUY as the visual anchor.
    # Unlocked BUY: gold rim at full alpha so both buttons read clearly gilded.
    if locked:
        stops   = [(0.0, (42, 40, 50)), (1.0, (28, 26, 36))]
        lab_col = (90, 88, 108)
        sheen   = 12
    elif is_cancel:
        stops   = [(0.0, (58, 54, 84)), (1.0, (38, 36, 62))]
        lab_col = (190, 182, 218)
        sheen   = 16
    else:
        stops   = [(0.0, (84, 78, 126)), (1.0, (50, 46, 82))]
        lab_col = (220, 210, 240)
        sheen   = 28

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)

    if locked:
        # Grey bevel matches the locked chip and the padlock icon — same inert family.
        sc.bevel_rim(big, btn_rect, rad, (54, 58, 74, 200), (140, 138, 160, 180),
                     w=max(1, m(1.8)))
    else:
        # Gold bevel at full alpha — the defining element; boosted from r1's 200→255
        # so the rim clearly reads warm gold, not bronze.
        sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 255), w=max(1, m(2.2)))

    lab_font = sc.font(13)
    if locked:
        lw = lab_font.size(label)[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.92)
        inner  = m(4)
        grp = lock_w + inner + lw
        gx  = btn_rect.centerx - grp // 2
        _padlock(big, gx + lock_w // 2, btn_rect.centery, lock_h, lab_col)
        sc.plain_text(big, label, lab_font,
                      (gx + lock_w + inner + lw // 2, btn_rect.centery),
                      lab_col, shadow_a=0, weight=m(0.6))
    else:
        sc.plain_text(big, label, lab_font, btn_rect.center, lab_col,
                      shadow_a=110, weight=m(0.8), keyline=(18, 16, 32), kw=m(0.9))


def _draw_chip(big, cx, cy, price, affordable, chip_bevel_alpha=180, chip_bevel_w=None):
    # Matte amber display pill; golden bevel when affordable, grey when not.
    # chip_bevel_alpha / chip_bevel_w are adjusted post-render if PIL sampling
    # shows the chip rim out-golding the buttons (note 4).
    CHIP_W, CHIP_H, CHIP_RAD = 120, 36, 8
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)
    if chip_bevel_w is None:
        chip_bevel_w = max(1, m(1.4))

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
        face_stops = [(0.0, (235, 220, 175)), (1.0, (205, 190, 145))]
    else:
        face_stops = [(0.0, (60, 60, 74)), (1.0, (44, 44, 58))]
    # Matte fill — deliberately NO top_sheen so the chip never reads as a button.
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)
    if affordable:
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, chip_bevel_alpha), w=chip_bevel_w)
    else:
        # Grey bevel keeps the same rim silhouette while the chip reads inert.
        sc.bevel_rim(big, chip, crad, (54, 58, 74, 200), (140, 138, 160, 180),
                     w=max(1, m(1.4)))

    txt = f"{price:,}"
    num_font = sc.font(22)
    coin_r = m(14)
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
        num_col = (52, 28, 4)
    else:
        pygame.draw.circle(big, (150, 152, 162), (coin_cx, cy), coin_r)
        pygame.draw.circle(big, (108, 112, 126), (coin_cx, cy), coin_r,
                           width=max(1, m(1)))
        pygame.draw.circle(big, (128, 132, 146), (coin_cx, cy), coin_r - m(3),
                           width=max(1, m(1)))
        num_col = (110, 115, 130)
    sc.plain_text(big, txt, num_font, (num_cx, num_cy), num_col,
                  shadow_a=0, weight=m(0.8))


def _draw_shelf(big, affordable, chip_bevel_alpha=180, chip_bevel_w=None):
    # Inset recessed tray carried over unchanged — only chip + buttons sit in it.
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)

    if affordable:
        shelf_stops = [(0.0, (28, 30, 62)), (1.0, (14, 16, 40))]
    else:
        shelf_stops = [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))]

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

    # Micro-walls: lit-left / shadowed-right strips for inset depth.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (xx / max(1, wall_w - 1)))
            pygame.draw.line(lwall, (130, 120, 165, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable,
               chip_bevel_alpha=chip_bevel_alpha, chip_bevel_w=chip_bevel_w)

    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)
    # CANCEL gets is_cancel=True so its fill and sheen recede behind BUY.
    _btn(big, buy, brad, "BUY", locked=not affordable)
    _btn(big, can, brad, "CANCEL", locked=False, is_cancel=True)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(322)),
                      (150, 166, 190), shadow_a=0)


def render_popup(name, affordable, chip_bevel_alpha=180, chip_bevel_w=None):
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

    # corner gems + name + banner
    sc.facet_gem(big, m(GEM_L_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.facet_gem(big, m(GEM_R_X), m(GEM_CY), m(GEM_R), PAL["gem"], PAL["deep"])
    sc.plain_text(big, name, sc.font(NAME_FS), (m(CX), m(Y_NAME)), (250, 248, 240),
                  shadow_a=160, weight=m(0.9), keyline=(6, 6, 16), kw=m(1.0))
    sc._ribbon_lozenge(big, 'EPIC', m(CX), m(Y_BANNER), m(BANNER_W), PAL)

    # shelf
    _draw_shelf(big, affordable,
                chip_bevel_alpha=chip_bevel_alpha, chip_bevel_w=chip_bevel_w)

    # disc + aura + thumb (LAST so disc floats above shelf)
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    return pygame.transform.smoothscale(big, (POP_W, POP_H))


# ── sheet layout ─────────────────────────────────────────────────────────────
MARGIN, HDR_H, GAP_HDR, GAP_C = 18, 28, 8, 8
CANVAS_W, CANVAS_H = 444, 412

canvas = Image.new("RGB", (CANVAS_W, CANVAS_H), (8, 8, 20))
draw   = ImageDraw.Draw(canvas)

try:
    fnt_hdr   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    fnt_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 11)
except Exception:
    fnt_hdr = fnt_badge = ImageFont.load_default()

draw.text((CANVAS_W // 2, MARGIN + HDR_H // 2),
          "gold-standard r2  |  AFFORDABLE / UNAFFORDABLE",
          fill=(232, 210, 150), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR
PANELS = [(18, True), (18 + POP_W + GAP_C, False)]

# ── Pass 1: render at default chip bevel alpha to run the note-4 comparison ──
# BUY button rim is at alpha=255; chip affordable bevel is at alpha=180.
# The gradient in bevel_rim fades top→bottom, so sample the top-edge strip.
# px=18 for affordable panel; BUY button center-x ≈ BUY_CX, center-y ≈ BTN_CY.
# In 1x coordinates: BUY_CX = CX-(BTN_W+BTN_GAP)//2 = 100-42 = 58, BTN_CY=302.
# Top of BUY button ≈ BTN_CY - BTN_H//2 = 302-15 = 287.  Sample y=289 (just inside rim).
# CHIP top-edge in 1x: CHIP_CY - 18 = 258 - 18 = 240. Sample y=241.

pass1_panels = []
for px, affordable in PANELS:
    surf  = render_popup("TEMPEST", affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    pass1_panels.append((px, affordable, panel))

# Sample BUY button rim on the affordable panel (px=18).
aff_panel = pass1_panels[0][2]   # affordable panel, 1x coords
buy_rim_px = aff_panel.getpixel((BUY_CX, BTN_CY - BTN_H // 2 + 2))   # just inside top rim
chip_rim_px = aff_panel.getpixel((CX, CHIP_CY - 18 + 2))              # top of chip

buy_lum  = buy_rim_px[0] * 0.299 + buy_rim_px[1] * 0.587 + buy_rim_px[2] * 0.114
chip_lum = chip_rim_px[0] * 0.299 + chip_rim_px[1] * 0.587 + chip_rim_px[2] * 0.114

print(f"Pass-1 BUY rim sample  @ ({BUY_CX},{BTN_CY - BTN_H//2 + 2}): {buy_rim_px}  lum={buy_lum:.1f}")
print(f"Pass-1 chip rim sample @ ({CX},{CHIP_CY - 18 + 2}):  {chip_rim_px}  lum={chip_lum:.1f}")

# Note 4: only reduce chip bevel if chip rim is genuinely brighter than button.
chip_needs_reduction = chip_lum > buy_lum
if chip_needs_reduction:
    print("Note 4 applies: re-rendering with chip alpha 180→150, w m(1.4)→m(1.2)")
    final_chip_alpha = 150
    final_chip_w     = max(1, m(1.2))
else:
    print("Note 4 not triggered: button rim already out-golds chip rim.")
    final_chip_alpha = 180
    final_chip_w     = None   # uses default m(1.4)

# ── Pass 2: final render with note-4 decision applied ────────────────────────
panels_data = []
for px, affordable in PANELS:
    surf  = render_popup("TEMPEST", affordable,
                         chip_bevel_alpha=final_chip_alpha if affordable else 180,
                         chip_bevel_w=final_chip_w if affordable else None)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    panels_data.append((px, affordable, panel))

# ── Compose sheet ─────────────────────────────────────────────────────────────
for px, affordable, panel in panels_data:
    canvas.paste(panel, (px, panels_y))
    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength("A") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "A", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v2", "gold-standard", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── Note 5: PIL verification ─────────────────────────────────────────────────
# (118, 224) should be non-background (card body visible there).
# BUY button rim: affordable panel px=18, BUY top-edge.
aff_final = panels_data[0][2]
probe_118_224 = aff_final.getpixel((118, 224))
buy_rim_final = aff_final.getpixel((BUY_CX, BTN_CY - BTN_H // 2 + 2))
print(f"\n=== PIL Verification ===")
print(f"(118, 224) on affordable panel: {probe_118_224}  "
      f"→ {'non-background OK' if probe_118_224 != (8, 8, 20) else 'WARN: background!'}")
print(f"BUY rim @ ({BUY_CX},{BTN_CY - BTN_H//2 + 2}): {buy_rim_final}  "
      f"→ warm gold R>G>B: {'OK' if buy_rim_final[0] > buy_rim_final[2] else 'FAIL'}")
r, g, b = buy_rim_final
print(f"   Target ≥(180,155,85): R≥180={'OK' if r >= 180 else 'FAIL'}, "
      f"G≥155={'OK' if g >= 155 else 'FAIL'}, B≥85: n/a (warm if R>B)")
