#!/usr/bin/env python3
"""Round-1 review render for the `inset-cream-cartouche` equipped indicator: a
cream stadium cartouche carved INTO the card's lower body as a deboss — a dark
recess wall frames a top-bright/warm-bottom cream field, with a top-left shadow
lip and a bottom-right catch-light so it reads as pressed into the card
material. Rendered headless onto a labeled review sheet; ships nothing."""
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
    """A cream stadium plate DEBOSSED into the dark-blue card body. Drawn OVER
    the body and frame with no masking rectangle: a near-black recess wall seats
    the plate, a top-bright cream gradient gives it real luminance range so it
    doesn't dissolve against the body, and the recess is lit top-left dark /
    bottom-right bright to read as carved negative relief."""
    m = sc.m
    cx, cy = 162, 174
    w, h = 156, 28
    rad = h // 2                                    # fully rounded ends = stadium
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)  # x 84→240, straight-edge zone

    # (1) recess wall — a near-black stadium one px larger on every side, the
    # dark ring the cartouche is sunk into.
    wall = r.inflate(2 * m(1), 2 * m(1))
    pygame.draw.rect(surf, (6, 7, 18), wall, border_radius=rad + m(1))

    # (2) interior fill — top-bright cream easing to a warm bottom so the plate
    # carries luminance range against the card body, clipped to the stadium.
    fill = sc.vgrad_stops(w, h, rad,
                          [(0.0, (255, 246, 222)), (1.0, (226, 210, 176))], 255)
    surf.blit(fill, r.topleft)

    # (3) shadow lip — a 2px dark stroke hugging the TOP + LEFT inner arc; the
    # recessed near edge falls into shadow under a top-left light.
    lip = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(lip, (6, 7, 18), lip.get_rect(), width=2, border_radius=rad)
    tl = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(tl, (255, 255, 255, 255), [(0, 0), (w, 0), (0, h)])
    lip.blit(tl, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(lip, r.topleft)

    # (4) catch-light — a 1px pale stroke on the BOTTOM + RIGHT inner arc where
    # light pools at the base of the recess.
    glint = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(glint, (255, 244, 214), glint.get_rect(), width=1,
                     border_radius=rad)
    br = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(br, (255, 255, 255, 255), [(w, 0), (w, h), (0, h)])
    glint.blit(br, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(glint, r.topleft)

    # (5) label — dark warm ink struck on the cream field, no shadow needed.
    sc.plain_text(surf, "EQUIPPED", sc.font(10), (cx, cy), (56, 42, 30),
                  shadow_a=0, tracking=m(1.1), weight=m(0.8))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (hang-tag + regalia frame, no cartouche)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + inset cartouche)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_inset_cream_cartouche(p2)


# ── compose review sheet ──────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
HDR_H = 48
LBL_H = 34
SGAP = 20
SLBL_H = 24
xs = [20, 360, 700]
panel_y = 102

GOLD = (236, 202, 116)
GREY = (150, 150, 168)
CREAM = (246, 244, 232)

# zoom of panel 2 — render then nearest-neighbour blow-up of the true 1× card
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


# header
hf = hud_font(22, True)
hg = hf.render("equipped v4c — inset-cream-cartouche · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNEQUIPPED", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ INSET CREAM CARTOUCHE", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

# zoom strip beneath panel 2
zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v4c", "inset_cream_cartouche", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
