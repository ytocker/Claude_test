#!/usr/bin/env python3
"""Round-2 render for the `inset-cream-cartouche` equipped indicator.

Addresses all art-director round-1 notes: correct draw order (cartouche drawn
BEFORE the regalia frame so the gold track lands on top and the plate reads as
carved into the card material rather than stickered on), lifted name ~11 SS to
open a clean band for the cartouche, 2 px catch-light keyed to the approved
rim-bright anchor, palette snapped to approved anchors throughout, and label
font/tracking refinements. Headless render; ships nothing."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)


def draw_inset_cream_cartouche(surf):
    """Cream stadium plate DEBOSSED into the dark-blue card body.

    Called BEFORE _draw_regalia_frame so the gold track lands on top and the
    plate sits visually behind it — a recess UNDER the frame reads as carved-in,
    whereas over the frame reads as a sticker.

    Palette anchors: (255,240,190)→(248,238,210) field, (9,9,22) recess wall
    and lip, (46,38,18) label ink. Catch-light thickened to 2 px so it
    survives the smoothscale down to the 162×100 game card."""
    m = sc.m
    cx, cy = 162, 174
    w, h = 156, 28
    rad = h // 2                                      # fully rounded ends = stadium
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)  # x 84→240

    # recess wall — near-black stadium one SS px larger on every side; the dark
    # ring the cartouche is sunk into.
    wall = r.inflate(2 * m(1), 2 * m(1))
    pygame.draw.rect(surf, (9, 9, 22), wall, border_radius=rad + m(1))

    # interior fill — warm bright top cream easing to a slightly cooler base so
    # the plate carries luminance range against the indigo card body.
    fill = sc.vgrad_stops(w, h, rad,
                          [(0.0, (255, 240, 190)), (1.0, (248, 238, 210))], 255)
    surf.blit(fill, r.topleft)

    # shadow lip — dark stroke hugging the TOP + LEFT inner arc; the recessed
    # near edge falls into shadow under a top-left light source.
    lip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(lip, (9, 9, 22), lip.get_rect(), width=2, border_radius=rad)
    tl = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(tl, (255, 255, 255, 255), [(0, 0), (w, 0), (0, h)])
    lip.blit(tl, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, r.topleft)

    # catch-light — 2 px bright stroke on the BOTTOM + RIGHT inner arc; 2 px
    # instead of R1's 1 px so it resolves after downscale to game resolution.
    glint = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(glint, (255, 240, 190), glint.get_rect(), width=2,
                     border_radius=rad)
    br = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(br, (255, 255, 255, 255), [(w, 0), (w, h), (0, h)])
    glint.blit(br, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(glint, r.topleft)

    # label — approved warm-dark ink, cap height +1 (font 11), tighter tracking.
    sc.plain_text(surf, "EQUIPPED", sc.font(11), (cx, cy), (46, 38, 18),
                  shadow_a=0, tracking=m(0.8), weight=m(0.8))


# ── Panel 0 — UNEQUIPPED ──────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# ── Panel 1 — EQUIPPED BASE (hang-tag + regalia frame, no cartouche) ──────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# ── Panel 2 — CONCEPT: correct depth order ────────────────────────────────────
# Stacking: card body → lifted name → cartouche → regalia frame → check-tag.
# Both name and state_chip are suppressed during the base draw so they can be
# placed in the right position in the stack — name must be above the body but
# BELOW the cartouche band, and the check-tag must come after the regalia frame.
_orig_name_on    = sc._name_on
_orig_state_chip = sc.state_chip
sc._name_on      = lambda *a, **kw: None
sc.state_chip    = lambda *a, **kw: None

sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=False, secret=False, owned=False)

sc._name_on    = _orig_name_on
sc.state_chip  = _orig_state_chip

# Re-draw name lifted ~11 SS above the original y so it clears the cartouche
# band; the open zone below the name title receives the cream plate.
sc._name_on(p2, sc._name(SID),
            rect.centerx, rect.y + sc.m(78) - sc.m(11), rect.w - sc.m(26))

# Cartouche BEFORE the regalia frame so the gold track overlaps its edges.
draw_inset_cream_cartouche(p2)

# Regalia frame ON TOP of the cartouche — the gold bead track visually locks
# the cartouche into the card and closes its left/right edges.
sc._draw_regalia_frame(p2, rect, sc.m(sc.CARD_RAD))

# Equipped check-tag as the final element (hardcoded to (44,60) inside the
# draw path, so the cx/cy args here are conventional placeholders).
cx_card = rect.centerx
cy_chip = rect.y + sc.m(88) - sc._CHIP_DY
sc.state_chip(p2, SID, cx_card, cy_chip, True, False, sc.m(20), owned=False)


# ── compose review sheet ──────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
LBL_H = 34
SGAP = 20
SLBL_H = 24
xs = [20, 360, 700]
panel_y = 102

GOLD = (236, 202, 116)
GREY = (150, 150, 168)
CREAM = (246, 244, 232)

# Zoom panel 2 — smoothscale simulates the final in-game card; nearest-neighbour
# 2× blows it back up so the cartouche detail is legible in the review sheet.
zoom = pygame.transform.smoothscale(p2, (162, 100))
zoom = pygame.transform.scale2x(zoom)   # 324×200

sheet_w = xs[-1] + PANEL_W + PAD
sheet_h = panel_y + PANEL_H + LBL_H + SGAP + SLBL_H + zoom.get_height() + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)


def label(txt, x, y, w, col, size=18):
    f = hud_font(size, True)
    g = f.render(txt, True, col)
    sheet.blit(g, (x + (w - g.get_width()) // 2, y))


hf = hud_font(22, True)
hg = hf.render("equipped v4c — inset-cream-cartouche · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNEQUIPPED", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ INSET CREAM CARTOUCHE R2", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v4c", "inset_cream_cartouche", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
