#!/usr/bin/env python3
"""Round-1 review render for the `bottom-glyph-seal` equipped indicator: a
chamfered octagonal gold certification seal seated on the card's lower body,
glyph-only (a deep-relief 4-point star, no text). Rendered headless onto a
labeled review sheet; ships nothing."""
import os, sys, math
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


def draw_bottom_glyph_seal(surf):
    """A chamfered octagonal gold certification seal biased up into the lower
    body so it sits tangent to the straight bottom edge. A pressed-in dark seat
    gives it depth; the gold face is lit from top-left (cream bevel on the upper
    facets), keylined dark all round, and carries a single deep-relief 4-point
    star struck into the metal with a lower-right intaglio catch-light."""
    m = sc.m
    cx, cy, r = 162, 175, 17

    # Flat-facet-up octagon: vertices at k*45-22.5° give flat top + bottom faces
    # so the seal reads as a chamfered square and sits square on the card edge.
    verts = [(cx + r * math.cos(math.radians(k * 45 - 22.5)),
              cy + r * math.sin(math.radians(k * 45 - 22.5))) for k in range(8)]

    # Pressed-in dark seat: a soft black disc a touch wider than the seal so a
    # dark contact ring peeks out and the medallion reads as inset into the card.
    seat_r = r + m(2)
    seat = pygame.Surface((seat_r * 2 + 2, seat_r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (seat_r + 1, seat_r + 1), seat_r)
    surf.blit(seat, (cx - seat_r - 1, cy - seat_r - 1))

    # Gold face: one smooth warm-gold ramp on the bounding box, hard-clipped to
    # the octagon so the whole medallion is ONE continuous gradient (domed metal),
    # never a two-tone splice.
    bx0, by0 = cx - r, cy - r
    gold = sc.vgrad_stops(2 * r, 2 * r, 0,
                          [(0.0, (255, 240, 190)), (0.45, (236, 202, 116)),
                           (1.0, (176, 120, 44))], 255, gamma=1.05).copy()
    mask = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(vx - bx0, vy - by0) for vx, vy in verts])
    gold.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gold, (bx0, by0))

    # Dark keyline round all 8 edges — the defined contact edge under the bevel.
    pygame.draw.polygon(surf, (86, 50, 8), verts, width=max(2, m(1)))

    # Cream catch-light on the upper-left facets only (left face → up-left chamfer
    # → top face): the raised-medallion rim under a top-left light.
    pygame.draw.lines(surf, (255, 240, 190), False,
                      [verts[4], verts[5], verts[6], verts[7]], max(1, m(1)))

    # Deep-relief intaglio glyph: a 4-point star struck in dark-key metal, sized
    # to ~60% of the seal so it stamps the face without crowding the rim.
    sr = r * 0.6
    ir = sr * 0.38
    star = []
    for i in range(8):
        ang = math.radians(-90 + i * 45)
        rr = sr if i % 2 == 0 else ir
        star.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    pygame.draw.polygon(surf, (46, 38, 18), star)
    # Light pools in the lower-right wall of the pressed groove — the intaglio
    # tell that the glyph is cut IN, not raised.
    pygame.draw.lines(surf, (255, 244, 214), False,
                      [star[2], star[3], star[4]], max(1, m(0.7)))

    # Tiny hot specular up-left of centre for jewelled polish.
    pr = m(1.2)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 200), (pr + 1, pr + 1), pr)
    surf.blit(pip, (159 - pr - 1, 172 - pr - 1))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (hang-tag + regalia frame, no seal)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + bottom glyph seal)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_bottom_glyph_seal(p2)


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

# true-size zoom of panel 2 (→162×100 live card→scale2x for a crisp detail view)
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
hg = hf.render("equipped v4c — bottom-glyph-seal · round 1 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNEQUIPPED", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ BOTTOM GLYPH SEAL", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v4c", "bottom_glyph_seal", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
