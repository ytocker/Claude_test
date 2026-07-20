"""Round 2 (final) — shelf concept 'twilight-vault' (store_confirm_shelf_v3).

A deep-teal vault: the bright turquoise BUY is the dominant warm-neutral CTA,
and a moody near-black-teal chip hosts the gold price + a signature gold
hairline rule under the numeral. The chip face sits 20+ luma below the button
teal so the display never competes with the actionable button.

R2 director notes folded in: the signature hairline is resurrected at full
gold (thicker + brighter + higher alpha, and drawn 1px directly on the shrunk
surface so the SS-then-shrink average can't collapse it to olive); the CANCEL
body is pushed darker to open a real luma gap under BUY; the chip face top lip
is lifted a few luma so the very-dark face reads as lit, not a hole.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v3/twilight-vault/round_2.png
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
BUY_CX = CX - (BTN_W + BTN_GAP) // 2   # = 58
CAN_CX = CX + (BTN_W + BTN_GAP) // 2   # = 142
CHIP_W, CHIP_H, CHIP_RAD          = 112, 34, 8

PAL   = sc.RARITY["epic"]
PRICE = 500

# Signature hairline colour: the card's bright gold ring tone, drawn opaque so
# it survives the /SS shrink instead of averaging into olive with the dark face.
HAIR_GOLD = sc.CARD_RING_BRIGHT   # (236, 202, 116)

# render_popup stashes the final-surface hairline geometry here so it can be
# stamped as a crisp 1px line AFTER smoothscale — the SS-then-shrink collapse
# that muddied R1's hairline is sidestepped entirely.
_hair_final = None


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
    pygame.draw.rect(surf, (10, 24, 26), kh, border_radius=1)


def _btn(big, btn_rect, rad, label, font_px, locked=False, is_cancel=False):
    # Unlocked BUY: bright turquoise fill is the dominant warm-neutral CTA.
    # CANCEL recedes: a markedly darker teal body opens a real luma gap under
    # BUY so hierarchy lives in the button bodies, not just the labels.
    # Locked BUY: teal-grey fill + grey bevel + padlock — an inert family that
    # matches the greyed chip, never a false gold.
    if locked:
        stops   = [(0.0, (34, 52, 52)), (1.0, (22, 36, 36))]
        lab_col = (110, 128, 128)
        sheen   = 12
    elif is_cancel:
        stops   = [(0.0, (18, 80, 78)), (1.0, (9, 52, 52))]
        lab_col = (157, 174, 172)
        sheen   = 14
    else:
        stops   = [(0.0, (26, 120, 116)), (1.0, (14, 80, 78))]
        lab_col = (224, 248, 246)
        sheen   = 26

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=100, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255), btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)

    if locked:
        sc.bevel_rim(big, btn_rect, rad, (44, 58, 58, 200), (120, 140, 140, 180),
                     w=max(1, m(1.8)))
    else:
        # Gold bevel is the shared jewel accent tying both live buttons together.
        # CANCEL's rim is drawn a hair heavier so the warm gold still reads over
        # its darker body.
        rim_w = m(2.2) if is_cancel else m(2.0)
        sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 230), w=max(1, rim_w))

    lab_font = sc.font(font_px)
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
                      shadow_a=110, weight=m(0.8), keyline=(6, 20, 20), kw=m(0.9))


def _draw_chip(big, cx, cy, price, affordable):
    # Very dark teal display pill — deliberately below the button teal in luma
    # so it reads as a readout, never a second button. NO top_sheen for the
    # same reason. Gold price + gold hairline are the concept's signature.
    global _hair_final
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (cx, cy)
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
        # Top lip lifted a few luma vs R1 so the face reads as a lit surface
        # (subtle catchlight) rather than a punched hole — still ~40 L, well
        # below BUY's ~96 L peak.
        face_stops = [(0.0, (12, 36, 40)), (1.0, (5, 22, 26))]
    else:
        face_stops = [(0.0, (34, 36, 44)), (1.0, (24, 26, 32))]
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

    # Signature gold hairline: a thin rule under the numeral, spanning only the
    # digit width. R1 drew it at 1px@55% in the SS surface, where the /SS shrink
    # averaged it into olive mud. R2 draws a thick opaque gold band in the SS
    # surface AND stashes the geometry so a crisp 1px gold line is stamped on
    # the final 200x340 surface — the shrink can no longer collapse it.
    if affordable:
        num_h = num_font.size(txt)[1]
        baseline = (num_cy - num_h // 2) + num_font.get_ascent()
        hair_h = m(2)
        hair_y = baseline + m(3)
        hair = pygame.Surface((num_w, hair_h), pygame.SRCALPHA)
        hair.fill((*HAIR_GOLD, int(255 * 0.85)))
        big.blit(hair, (num_cx - num_w // 2, hair_y))
        # Final-surface (1x) geometry — SS coords divided back down by SS.
        _hair_final = (
            (num_cx - num_w // 2) / SS,
            (num_cx + num_w // 2) / SS,
            (hair_y + hair_h // 2) / SS,
        )


def _draw_shelf(big, affordable):
    # Recessed teal tray: chip + buttons seat inside it below the disc.
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad = m(CARD_RAD)

    shelf_stops = [(0.0, (14, 42, 46)), (1.0, (8, 26, 30))]
    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=18)
    lip = (46, 74, 74)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Micro-walls: teal lit-left / shadowed-right strips for inset depth.
    wall_draw_h = m(CARD_TOP + CARD_H - CARD_RAD - SHELF_Y)
    if wall_draw_h > 0:
        wall_w = m(SHELF_X - CARD_X)
        lwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (xx / max(1, wall_w - 1)))
            pygame.draw.line(lwall, (58, 108, 108, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(lwall, (m(CARD_X), m(SHELF_Y)))
        rwall = pygame.Surface((wall_w, wall_draw_h), pygame.SRCALPHA)
        for xx in range(wall_w):
            a = int(50 * (1 - xx / max(1, wall_w - 1)))
            pygame.draw.line(rwall, (0, 0, 0, a), (xx, 0), (xx, wall_draw_h - 1))
        big.blit(rwall, (m(SHELF_X + SHELF_W), m(SHELF_Y)))

    _draw_chip(big, m(CX), m(CHIP_CY), PRICE, affordable)

    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H)); can.center = (m(CAN_CX), m(BTN_CY))
    brad = m(BTN_RAD)
    _btn(big, buy, brad, "BUY", 14, locked=not affordable)
    _btn(big, can, brad, "CANCEL", 13, locked=False, is_cancel=True)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(7), (m(CX), m(322)),
                      (150, 176, 176), shadow_a=0)


def render_popup(name, affordable):
    global _hair_final
    _hair_final = None
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
    _draw_shelf(big, affordable)

    # disc + aura + thumb (LAST so disc floats above shelf)
    cx_ss, cy_ss, r_ss = m(CX), m(DISC_CY), m(R_HERO)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(55), PAL["glow"], peak=95, layers=24)
    sc._alpha_aura(big, cx_ss, cy_ss, r_ss + m(20), PAL["glow"], peak=70, layers=12)
    sc.cabochon(big, cx_ss, cy_ss, r_ss, sc.CABO_LO, sc.CABO_HI,
                ring=PAL["gem"], ring_a=50)
    sc.blit_thumb(big, "skin_tempest", cx_ss, cy_ss, int(r_ss * 1.5))
    sc.cabochon_glass(big, cx_ss, cy_ss, r_ss, tint=PAL["gem"])

    final = pygame.transform.smoothscale(big, (POP_W, POP_H))

    # Stamp the signature hairline as a crisp 1px opaque gold line on the SHRUNK
    # surface, so the /SS average can never dilute it to olive.
    if affordable and _hair_final is not None:
        x0, x1, hy = _hair_final
        pygame.draw.line(final, HAIR_GOLD, (int(round(x0)), int(round(hy))),
                         (int(round(x1)), int(round(hy))), 1)

    return final


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
          "twilight-vault r2  |  AFFORDABLE / UNAFFORDABLE",
          fill=(232, 210, 150), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR   # = 54
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
    bw     = fnt_badge.getlength("C") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "C", fill=(230, 225, 245), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v3", "twilight-vault", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")

# ── PIL verification (never by viewing) ──────────────────────────────────────
aff_final = panels_data[0][2]
def _lum(p): return p[0]*0.299 + p[1]*0.587 + p[2]*0.114

probe = aff_final.getpixel((118, 224))
print(f"\n=== PIL Verification (aff_final is the 200x340 popup panel) ===")
print(f"(118, 224): {probe}  "
      f"→ {'non-background OK' if probe != (8, 8, 20) else 'WARN: background!'}")

# Signature hairline: the crisp 1px line lives just under the numeral (~popup
# y 272). Scan a y-band at chip-centre x to catch it, verify pure gold not olive.
hair_x = CX + 18   # under the numeral, right of the coin
best = None
for yy in range(266, 282):
    p = aff_final.getpixel((hair_x, yy))
    if best is None or (p[0] - p[2]) > (best[1][0] - best[1][2]):
        best = (yy, p)
hy, hp = best
gold_ok = hp[0] > 170 and (hp[0] - hp[2]) > 70
olive_bad = hp == (58, 48, 22)
print(f"hairline brightest @ ({hair_x},{hy}): {hp}  "
      f"→ gold R>170 & R-B>70: {'OK' if gold_ok else 'FAIL'}"
      f" | olive(58,48,22): {'BAD' if olive_bad else 'no'}")

# BUY / CANCEL top rim must both read warm gold. Scan a few rows from the button
# top edge; pick the pixel with the strongest R>B (the gold bevel).
def _rim_scan(cx):
    top = BTN_CY - BTN_H // 2
    b = None
    for yy in range(top, top + 5):
        p = aff_final.getpixel((cx, yy))
        if b is None or (p[0] - p[2]) > (b[1][0] - b[1][2]):
            b = (yy, p)
    return b
by_, bp = _rim_scan(BUY_CX)
print(f"BUY rim @ ({BUY_CX},{by_}): {bp}  → warm gold R>B: "
      f"{'OK' if bp[0] > bp[2] else 'FAIL'}")
cyr, cp = _rim_scan(CAN_CX)
print(f"CANCEL rim @ ({CAN_CX},{cyr}): {cp}  → warm gold R>B: "
      f"{'OK' if cp[0] > cp[2] else 'FAIL'}")

# BUY↔CANCEL body luma gap (must exceed ~30). Sample above the label to dodge
# both the centred text and the top rim.
buy_face = aff_final.getpixel((BUY_CX, BTN_CY - 9))
can_face = aff_final.getpixel((CAN_CX, BTN_CY - 9))
print(f"BUY body {buy_face} lum={_lum(buy_face):.1f} | CANCEL body {can_face} "
      f"lum={_lum(can_face):.1f} | gap={_lum(buy_face)-_lum(can_face):.1f} "
      f"→ {'OK (>30)' if _lum(buy_face)-_lum(can_face) > 30 else 'CHECK'}")

# Button teal vs chip face luma delta (concept requires 20+).
chip_face = aff_final.getpixel((CX + 40, CHIP_CY))
print(f"BUY face lum={_lum(buy_face):.1f} | chip face {chip_face} "
      f"lum={_lum(chip_face):.1f} | delta={_lum(buy_face)-_lum(chip_face):.1f} "
      f"→ {'OK (>=20)' if _lum(buy_face)-_lum(chip_face) >= 20 else 'CHECK'}")
