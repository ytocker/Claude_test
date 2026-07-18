#!/usr/bin/env python3
"""Round-1 review render for the `bead-clasp-nameplate` equipped indicator: a
warm gold nameplate seated in the card's lower body, clasped at each end by a
gold bead. Rendered headless onto a labeled review sheet; ships nothing."""
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


def draw_bead_clasp_nameplate(surf):
    """A gold nameplate in the lower body, seated over the card ground with a
    soft drop shadow and gloss, its ends pinched by two gold bead clasps that
    read as the fasteners holding the plate to the card."""
    m = sc.m
    cx, cy = 162, 176
    w, h, rad = 176, 28, 8
    r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)   # x 74→250, inside straight-edge zone

    # soft seat shadow so the plate lifts off the card body
    sc.drop_shadow(surf, r, rad, blur=m(4), alpha=110, dy=m(2))
    # canonical Ramp-A gold body — the ONE gold for every gold fill
    surf.blit(sc.gold_a_fill(r.w, r.h, rad), r.topleft)
    # light specular sweep across the crown
    sc.gloss_sweep(surf, r, rad, peak=90)
    # bottom-right ambient occlusion so the plate settles into its shadow
    sc.contact_shadow(surf, r, rad, m(3), alpha=70)
    # emboss: dark-amber contact keyline under a cream top-left bevel
    pygame.draw.rect(surf, (86, 50, 8), r, width=max(1, m(1.4)), border_radius=rad)
    sc.bevel_rim(surf, r, rad, (86, 50, 8), (255, 240, 190, 235), w=max(1, m(1.3)))

    # bead clasps pinning each end of the plate
    for bx in (78, 246):
        br = m(3)
        pygame.draw.circle(surf, (244, 192, 88), (bx, cy), br)          # top-ramp gold bead
        pygame.draw.circle(surf, (86, 50, 8), (bx, cy), br, max(1, m(0.7)))  # dark-amber keyline ring
        # tiny specular pip up-left
        pip = max(1, m(1))
        pygame.draw.circle(surf, (255, 248, 224),
                           (bx - m(1), cy - m(1)), pip)

    # single crisp dark stamp — the plate needs no masking rect, it reads on gold
    sc.plain_text(surf, "EQUIPPED", sc.font(11), (cx, cy), (46, 38, 18),
                  shadow_a=0, tracking=m(1.2), weight=m(0.9))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (hang-tag + regalia frame, no nameplate)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + nameplate)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_bead_clasp_nameplate(p2)


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

# zoom of panel 2
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
hg = hf.render("equipped v4c — bead-clasp-nameplate · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNEQUIPPED", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ BEAD CLASP NAMEPLATE", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

# zoom strip beneath panel 2
zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v4c", "bead_clasp_nameplate", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
