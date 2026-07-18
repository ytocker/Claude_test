#!/usr/bin/env python3
import os, sys, math
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font
from game.draw import lerp_color

sd.load()
SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2*ri, PANEL_H - 2*ri)


def draw_lower_left_corner(surf):
    """Struck emerald coin-boss badge inset into the free lower-left corner: a
    circular medallion that reads as a physically pressed mark of the equipped
    state — categorically a COIN, not a ribbon. Emerald-mint so it stays legible
    against the cream/ink upper-left ✓ hang-tag at the opposite corner.

    Nudged right (+4 px) and up (-4 px) so no green crosses the frame bead line;
    a continuous dark outer ring locks the read as 'sitting on top' rather than
    dissolving into the gold beading."""
    # r2: nudged right +4, up -4 from r1 (was 34,168) to clear the frame bead.
    cx, cy = 38, 164
    R = sc.m(12)

    # equipped-green enamel ramp — same DNA as the EQUIPPED status chip so the
    # badge reads as active-state family.
    C_HI = (18, 32, 24)
    C_LO = (12, 22, 16)
    MINT = (100, 230, 148)

    pad = sc.m(4)
    D = R * 2 + pad * 2
    disc = pygame.Surface((D, D), pygame.SRCALPHA)
    c = R + pad

    # bottom-right contact shadow anchoring the coin into the card body.
    for k in range(sc.m(3), 0, -1):
        a = int(70 * (k / sc.m(3)))
        pygame.draw.circle(disc, (0, 0, 0, a),
                           (c + sc.m(1.5), c + sc.m(2)), R + k)

    # radial dome — lit centre deepening to the rim gives the pressed-metal read.
    for i in range(R, 0, -1):
        t = (i / R) ** 1.25
        col = lerp_color(C_HI, C_LO, t)
        pygame.draw.circle(disc, (*col, 255), (c, c), i)

    # r2 fix #1+#2: continuous dark outer ring one step outside R — the coin now
    # explicitly reads as sitting ON TOP of the frame beading regardless of what
    # colour the frame is under it, and the full circular silhouette is preserved.
    pygame.draw.circle(disc, (0, 0, 0, 210), (c, c), R + 1, 2)

    # dark inner keyline seating the coin inside its outer ring.
    pygame.draw.circle(disc, (5, 12, 8, 235), (c, c), R, max(1, sc.m(1.4)))

    # r2 fix #3: rim glint concentrated at 10-11 o'clock (120-150° in pygame's
    # convention) and rendered in three fading passes so the falloff reads as
    # surface curvature rather than a detached sparkle.  No BLEND_ADD — additive
    # compositing would smear green outside the coin boundary.
    glint_rect = (c - R + sc.m(1), c - R + sc.m(1),
                  R * 2 - sc.m(2), R * 2 - sc.m(2))
    glint_arc_start = math.radians(120)
    glint_arc_stop  = math.radians(155)
    for alpha, thickness in [(200, max(1, sc.m(1.5))),
                              (110, max(1, sc.m(3))),
                              (45,  max(1, sc.m(5)))]:
        # inner bright core → outer soft halo, each drawn as a slightly wider arc
        inner_rect = (
            glint_rect[0] + thickness // 2,
            glint_rect[1] + thickness // 2,
            glint_rect[2] - thickness,
            glint_rect[3] - thickness,
        )
        g = pygame.Surface((D, D), pygame.SRCALPHA)
        pygame.draw.arc(g, (*MINT, alpha),
                        inner_rect if alpha < 200 else glint_rect,
                        glint_arc_start, glint_arc_stop,
                        max(1, thickness))
        disc.blit(g, (0, 0))

    # r2 fix #4: embossed mint 5-point star — the dark under-shadow is widened by
    # 1 SS2 px (outer radius grown by sc.m(0.5)) and its offset is deepened to
    # push the lower-right facets down so the pip reads 'struck proud' rather than
    # 'green sticker'.  The mint face stays flat — value contrast alone lifts it.
    def star_pts(scx, scy, ro, ri_):
        pts = []
        for k in range(10):
            ang = -math.pi / 2 + k * math.pi / 5
            rr = ro if k % 2 == 0 else ri_
            pts.append((scx + rr * math.cos(ang), scy + rr * math.sin(ang)))
        return pts

    ro, rin = R * 0.60, R * 0.26
    # shadow: offset 1 ss-px deeper lower-right than r1, outer radius widened 1 px.
    pygame.draw.polygon(disc, (4, 12, 8, 200),
                        star_pts(c + sc.m(0.8), c + sc.m(1.0), ro + sc.m(0.5), rin))
    # mint face: unchanged position, keeping the flat face crisp.
    pygame.draw.polygon(disc, MINT,
                        star_pts(c - sc.m(0.4), c - sc.m(0.4), ro, rin))
    # hot core specular kiss — the single specular on the disc; no bloom.
    pygame.draw.polygon(disc, (200, 255, 220),
                        star_pts(c - sc.m(0.4), c - sc.m(0.4), ro * 0.5, rin * 0.5))

    surf.blit(disc, (cx - c, cy - c))


# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT (equipped base + medallion on top)
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
draw_lower_left_corner(p2)

# Compose review sheet
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD = (236, 202, 116); GREY = (150, 152, 168); CREAM_LBL = (250, 246, 232)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H
sheet_w = xs[-1] + PANEL_W + PAD
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)
title_f = hud_font(22, True)
tt = title_f.render("equipped v4 — lower-left-corner · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))
labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY), ("+ LOWER-LEFT CORNER", CREAM_LBL)]
panels = [p0, p1, p2]
lbl_f = hud_font(15, True); zlbl_f = hud_font(13, True)
for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip = pygame.transform.scale2x(card1x)
zx = xs[-1] + (PANEL_W - strip_w) // 2
zt = zlbl_f.render("@1x (162x100 tile, 2x nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(xs[-1] + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(strip, (zx, zoom_y))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4", "lower_left_corner", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())
