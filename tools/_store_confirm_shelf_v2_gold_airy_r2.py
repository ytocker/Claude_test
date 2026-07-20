"""Round 2 — shelf concept 'gold-airy' (store_confirm_shelf_v2).

Revision from art-director notes: buttons whisper harder (bevel alpha 165→115,
rim width m(1.3)→m(1.0)); chip bevel (alpha 215, w=m(1.6)) now measurably
out-golds the buttons so the hierarchy reads chip-dominates / buttons-whisper.
Buttons narrowed 80→74 to open breathing room alongside the shelf walls (~8–9 px
each side). Chip lowered CHIP_CY 248→252 so its top sits clearly inside the
shelf tray. Airy fill and chip face/size left exactly as-is — both confirmed
working by the director.

Sheet: left=AFFORDABLE, right=UNAFFORDABLE. Verify with PIL, never by viewing.
Output → docs/store_confirm_shelf_v2/gold-airy/round_2.png
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

# Chip is the centrepiece; the two accent buttons sit lower on the shelf.
# CHIP_CY lowered 248→252 so chip top sits clearly inside the shelf tray
# (shelf top at y=235, seat shadow at y=229–235).
CHIP_CY                     = 252
# BTN_W narrowed 80→74 to give ~8–9 px clear space from each shelf wall,
# reinforcing the airy feeling. Centers pinned so spacing is symmetric.
BTN_W, BTN_H, BTN_RAD       = 74, 30, 9
BTN_CY, BTN_GAP             = 295, 8
BUY_CX = 58
CAN_CX = 142


def _nw(txt, font):
    return sc._glyph_base(txt, font, 0).get_width()


def _padlock(surf, cx, cy, h, color):
    # Rounded body + shackle arc + punched keyhole: reads as a lock at any size.
    bw = int(h * 0.92)
    bh = int(h * 0.60)
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


def _btn(big, btn_rect, label, locked=False):
    """Whisper-thin accent button. The airiness comes from a slightly brighter
    indigo fill plus a barely-there gold bevel (alpha 115, w=m(1.0)) that
    whispers at the edge — so the chip's prominent bevel (alpha 215, w=m(1.6))
    reads as the clear dominant element on the shelf."""
    rad = m(BTN_RAD)
    if locked:
        stops   = [(0.0, (44, 42, 52)), (1.0, (28, 26, 38))]
        lab_col = (88, 86, 104)
        sheen   = 12
        bevel_a = 100
    else:
        # Brighter than the card body (84,78,126)/(50,46,82) for extra air;
        # confirmed working by the director — keep unchanged.
        stops   = [(0.0, (96, 88, 136)), (1.0, (60, 54, 96))]
        lab_col = (220, 210, 240)
        sheen   = 30
        # alpha 165→115, width m(1.3)→m(1.0) so the bevel barely kisses the
        # edge and yields clearly to the chip's gold (alpha 215, w=m(1.6)).
        bevel_a = 115

    sc.drop_shadow(big, btn_rect, rad, blur=m(3), alpha=90, dy=m(2))
    big.blit(sc.vgrad_stops(btn_rect.w, btn_rect.h, rad, stops, 255),
             btn_rect.topleft)
    sc.top_sheen(big, btn_rect, rad, m(12), peak=sheen)
    # Barely-there bevel — the gold whispers, not shouts.
    sc.bevel_rim(big, btn_rect, rad, sc.CARD_RING_DEEP,
                 (*sc.CARD_RING_BRIGHT, bevel_a), w=max(1, m(1.0)))

    lab_font = sc.font(13)
    if locked:
        # Padlock left of the label is a colour-blind-safe inert cue.
        lw     = lab_font.size(label)[0]
        lock_h = m(11)
        lock_w = int(lock_h * 0.92)
        inner  = m(4)
        grp    = lock_w + inner + lw
        gx     = btn_rect.centerx - grp // 2
        _padlock(big, gx + lock_w // 2, btn_rect.centery, lock_h, lab_col)
        sc.plain_text(big, label, lab_font,
                      (gx + lock_w + inner + lw // 2, btn_rect.centery),
                      lab_col, shadow_a=0, weight=m(0.6))
    else:
        sc.plain_text(big, label, lab_font, btn_rect.center, lab_col,
                      shadow_a=110, weight=m(0.8), keyline=(18, 16, 32), kw=m(0.9))


def _draw_chip(big, affordable):
    """Wider warm-amber coin plaque with the largest coin in the series and a
    prominent gold bevel — the dominant visual element against the airy buttons.
    Face, size, and coin radius all unchanged from director-confirmed round 1."""
    CHIP_W, CHIP_H, CHIP_RAD = 136, 36, 8
    chip = pygame.Rect(0, 0, m(CHIP_W), m(CHIP_H))
    chip.center = (m(CX), m(CHIP_CY))
    crad = m(CHIP_RAD)

    sc.drop_shadow(big, chip, crad, blur=m(3), alpha=90, dy=m(2))

    if affordable:
        face_stops = [(0.0, (238, 224, 180)), (1.0, (208, 192, 148))]
    else:
        face_stops = [(0.0, (60, 60, 74)), (1.0, (44, 44, 58))]
    # Matte fill — deliberately NO top_sheen so it reads as a display, not a tap.
    big.blit(sc.vgrad_stops(chip.w, chip.h, crad, face_stops, 255), chip.topleft)

    if affordable:
        # Prominent gold bevel (alpha 215, w=m(1.6)) — the loudest gold on the
        # shelf, clearly above the buttons' whisper (alpha 115, w=m(1.0)).
        sc.bevel_rim(big, chip, crad, sc.CARD_RING_DEEP,
                     (*sc.CARD_RING_BRIGHT, 215), w=max(1, m(1.6)))
    else:
        sc.bevel_rim(big, chip, crad, (54, 58, 74, 200), (140, 138, 160, 130),
                     w=max(1, m(1.6)))

    txt      = f"{PRICE:,}"
    num_font = sc.font(22)
    coin_r   = m(16)
    coin_d   = coin_r * 2
    gap      = m(4)
    num_w    = num_font.size(txt)[0]
    total    = coin_d + gap + num_w
    left     = m(CX) - total // 2
    coin_cx  = left + coin_r
    num_cx   = left + coin_d + gap + num_w // 2
    cy       = m(CHIP_CY)
    num_cy   = cy + m(3)

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


def _draw_shelf(big, affordable):
    # ── inset shelf tray (the stage the chip + accents sit on) ────────────────
    shelf_rect = pygame.Rect(m(SHELF_X), m(SHELF_Y), m(SHELF_W), m(SHELF_H))
    shelf_rad  = m(CARD_RAD)

    if affordable:
        shelf_stops = [(0.0, (38, 40, 82)), (1.0, (20, 22, 50))]
    else:
        shelf_stops = [(0.0, (30, 32, 52)), (0.5, (22, 22, 42)), (1.0, (14, 14, 30))]

    shelf = sc.vgrad_stops(shelf_rect.w, shelf_rect.h, 0, shelf_stops, 255).copy()
    shelf_mask = pygame.Surface(shelf_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shelf_mask, (255, 255, 255, 255), shelf_mask.get_rect(),
                     border_bottom_left_radius=shelf_rad,
                     border_bottom_right_radius=shelf_rad)
    shelf.blit(shelf_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    sc.top_sheen(shelf, shelf.get_rect(), 0, m(20), peak=35)
    lip = (100, 92, 120) if affordable else (62, 62, 86)
    pygame.draw.line(shelf, lip, (0, 0), (shelf_rect.w - 1, 0), max(1, m(1)))
    # Seat shadow where the shelf meets the card body above.
    seat = pygame.Surface((shelf_rect.w, m(6)), pygame.SRCALPHA)
    for yy in range(m(6)):
        a = int(120 * (1 - yy / m(6)))
        pygame.draw.line(seat, (0, 0, 0, a), (0, yy), (shelf_rect.w - 1, yy))
    big.blit(seat, (shelf_rect.x, shelf_rect.y - m(6)))
    big.blit(shelf, shelf_rect.topleft)

    # Micro-walls: lit-left / shadowed-right strips in the inset gap for depth.
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

    # ── centrepiece chip + whisper-thin accent buttons ────────────────────────
    _draw_chip(big, affordable)

    buy = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    buy.center = (m(BUY_CX), m(BTN_CY))
    can = pygame.Rect(0, 0, m(BTN_W), m(BTN_H))
    can.center = (m(CAN_CX), m(BTN_CY))

    _btn(big, buy, "BUY", locked=not affordable)
    _btn(big, can, "CANCEL", locked=False)

    if not affordable:
        sc.plain_text(big, "NOT ENOUGH", sc.font(8), (m(CX), m(317)),
                      (150, 166, 190), shadow_a=0)


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

draw.text((CANVAS_W // 2, MARGIN + HDR_H // 2), "gold-airy r2",
          fill=(238, 214, 150), font=fnt_hdr, anchor="mm")

panels_y = MARGIN + HDR_H + GAP_HDR
PANELS = [(18, "AFFORDABLE", True), (18 + POP_W + GAP_C, "UNAFFORDABLE", False)]

for px, _label, affordable in PANELS:
    surf  = render_popup("TEMPEST", 178, affordable)
    raw   = pygame.image.tostring(surf, "RGB")
    panel = Image.frombytes("RGB", (POP_W, POP_H), raw)
    canvas.paste(panel, (px, panels_y))

    bx, by = px + 5, panels_y + 5
    bw     = fnt_badge.getlength("E") + 8
    draw.rounded_rectangle([bx, by, bx + bw, by + 17], radius=4, fill=(24, 22, 38))
    draw.text((bx + 4, by + 8), "E", fill=(238, 214, 150), font=fnt_badge, anchor="lm")

OUT = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_confirm_shelf_v2", "gold-airy", "round_2.png")
OUT = os.path.abspath(OUT)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
canvas.save(OUT)
print(f"Saved {OUT}  ({CANVAS_W}x{CANVAS_H})")
