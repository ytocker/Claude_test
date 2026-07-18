#!/usr/bin/env python3
"""Round-2 review render for the `bottom-glyph-seal` equipped indicator.

Changes from round 1 (per art-director notes):
- Relocated to bottom-RIGHT corner (cx=276, cy=176) — clears the name lane
  centred at x=162, diagonal counterweight to the top-left hang-tag.
- Seal radius reduced to 14 (from 17) and seat_r reduced to r+m(1)=16 so
  the seat disc bottom lands exactly at the card body bottom (y=192).
- 4-point star replaced with an angular bold ✓ echoing the hang-tag mark.
- Sub-pixel micro-details (intaglio catch-light, hot specular pip) removed;
  only the octagon body, keyline, cream bevel and ✓ survive at 162×100.
- Keyline consolidated to (46,38,18) — same near-black as the ✓ ink.
"""
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
# card body: x=8..316, y=8..192; bottom-right corner arc centre at (282,158),
# rad=34.  The seal+seat geometry below is verified to stay inside that arc.


def draw_bottom_glyph_seal(surf):
    """Chamfered octagonal gold certification seal in the bottom-right corner —
    diagonal counterweight to the top-left hang-tag. Positioned at cx=276,
    cy=176 so it sits clear of the item name centred at x=162. Seat disc uses
    r+m(1) so the bottom (176+16=192) aligns with the card body floor. The ✓
    glyph echoes the hang-tag stroke language: same near-black ink, same
    angular proportions, so equipped reads as one visual system."""
    m = sc.m
    cx, cy, r = 276, 176, 14

    # Flat-facet-up octagon: vertices at k*45-22.5° give flat top + bottom faces
    # so the seal reads as a chamfered square rather than a tilted diamond.
    verts = [(cx + r * math.cos(math.radians(k * 45 - 22.5)),
              cy + r * math.sin(math.radians(k * 45 - 22.5))) for k in range(8)]

    # Pressed-in dark seat: seat_r = r+m(1) = 16 → seat bottom = 176+16 = 192,
    # which lands exactly on the card body floor.  A circle wider than the seal
    # so a dark contact ring peeks around the medal and it reads as inset.
    seat_r = r + m(1)
    seat = pygame.Surface((seat_r * 2 + 2, seat_r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(seat, (0, 0, 0, 150), (seat_r + 1, seat_r + 1), seat_r)
    surf.blit(seat, (cx - seat_r - 1, cy - seat_r - 1))

    # Gold face: one continuous warm-gold ramp on the bounding box, clipped to
    # the octagon — a single gradient gives the whole face a domed-metal look
    # without a two-tone splice.
    bx0, by0 = cx - r, cy - r
    gold = sc.vgrad_stops(2 * r, 2 * r, 0,
                          [(0.0, (255, 240, 190)), (0.45, (236, 202, 116)),
                           (1.0, (176, 120, 44))], 255, gamma=1.05).copy()
    mask = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255),
                        [(vx - bx0, vy - by0) for vx, vy in verts])
    gold.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(gold, (bx0, by0))

    # Dark keyline round all 8 edges — the hard contact boundary under the bevel.
    # Unified near-black matches the ✓ ink so the two elements read as one system.
    pygame.draw.polygon(surf, (46, 38, 18), verts, width=max(2, m(1)))

    # Cream bevel on the upper-left 3 facets (left face → UL chamfer → top face):
    # the rim catch under a top-left virtual light.  ≥2px at SS so it resolves
    # at 162×100 live scale.
    pygame.draw.lines(surf, (255, 240, 190), False,
                      [verts[4], verts[5], verts[6], verts[7]], max(2, m(1)))

    # Angular bold ✓ struck into the face — short steep left arm, long gentle
    # right arm, same V-proportion as the hang-tag check.  Three points sized to
    # fit inside r=14.  Round caps prevent hairline tips at small render size.
    left_tip  = (cx - 8, cy + 2)
    vertex    = (cx - 3, cy + 7)
    right_tip = (cx + 8, cy - 5)
    stroke_w = max(3, m(2))   # 4px at SS=2 → 2px at 1× card
    cap_r    = max(2, m(1))   # 2px at SS=2 → 1px cap at 1×
    ink = (46, 38, 18)

    pygame.draw.lines(surf, ink, False, [left_tip, vertex, right_tip], stroke_w)
    for pt in [left_tip, vertex, right_tip]:
        pygame.draw.circle(surf, ink, (int(pt[0]), int(pt[1])), cap_r)


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (hang-tag + regalia frame, no seal)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + bottom-right glyph seal)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_bottom_glyph_seal(p2)


# ── pixel-sampling sanity check at live-card scale ────────────────────────────
# Verify the seal body is golden and the card slot it vacates is clean.
_live = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
# seal centre in 1× coords: (276//2, 176//2) = (138, 88)
_seal_px = _live.get_at((138, 88))
# name-lane centre at 1×: (162//2, 164//2) = (81, 82) — should be name-coloured, not seal gold
_name_px = _live.get_at((81, 82))
print(f"seal centre px (expect warm gold): {tuple(_seal_px)}")
print(f"name-lane centre px (expect dark/cream, not displaced): {tuple(_name_px)}")


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

# True-size zoom: downscale to 162×100 (live card), then scale2x for crisp
# detail view so the reviewer sees exactly what the player sees.
zoom = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
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
hg = hf.render("equipped v4c — bottom-glyph-seal · round 2 · skin_mummy", True, GOLD)
sheet.blit(hg, (PAD, PAD))

panels = [(p0, "UNEQUIPPED", GREY),
          (p1, "EQUIPPED BASE", GREY),
          (p2, "+ BOTTOM GLYPH SEAL (R2)", CREAM)]
for (panel, lbl, col), x in zip(panels, xs):
    sheet.blit(panel, (x, panel_y))
    label(lbl, x, panel_y + PANEL_H + 8, PANEL_W, col)

zx = xs[2]
zy = panel_y + PANEL_H + LBL_H + SGAP
label("ZOOM · PANEL 2 · live 162×100", zx, zy, PANEL_W, GREY, size=15)
sheet.blit(zoom, (zx, zy + SLBL_H))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v4c", "bottom_glyph_seal", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("wrote", out)
