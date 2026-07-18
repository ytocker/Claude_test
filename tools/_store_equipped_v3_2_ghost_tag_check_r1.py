#!/usr/bin/env python3
"""
equipped-card v3.2 — ghost-tag-check concept, round 1.

Narrative: "the price is gone, it's yours." The swing-tag from Panel 0's
unequipped price chip is redrawn as a faint cream hairline ghost — same tilted
rectangle, same grommet, same cord off the knot — and a bold, fully-opaque cream
✓ is struck over its face. The ghost is pure atmosphere; the tick is the hero.

Rendered LAST over an equipped card whose green chip is suppressed and whose
regalia double-frame is already laid, so the frame carries "selected" and the
struck-out tag carries "paid for / owned".
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game.hud import _font as hud_font

sd.load()

SID = "skin_mummy"
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
rad = sc.m(sc.CARD_RAD)


# ── regalia frame (copied verbatim from _store_equipped_v3_regalia_frame_r2) ──
def draw_regalia_frame(surf, body):
    """The nested second gold frame, decoupled from bevel_rim."""
    OUTER = (236, 202, 116)
    VALLEY = (9, 9, 22)
    INNER = (255, 240, 190)
    KEY = (46, 38, 18)
    GLINT = (255, 248, 224)

    def bead(inset, w, col, alpha=255):
        r = body.inflate(-2 * inset, -2 * inset)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), r, width=w,
                         border_radius=max(1, rad - inset))
        surf.blit(s, (0, 0))

    bead(inset=2,  w=sc.m(3.0), col=OUTER)
    bead(inset=8,  w=sc.m(1.4), col=VALLEY)
    bead(inset=10, w=sc.m(2.0), col=INNER)
    bead(inset=13, w=max(1, sc.m(0.6)), col=KEY)

    track = body.inflate(-2 * 10, -2 * 10)
    leg = sc.m(7)
    corners = [
        (track.left,  track.top,     1,  1),
        (track.right, track.top,    -1,  1),
        (track.left,  track.bottom,  1, -1),
        (track.right, track.bottom, -1, -1),
    ]
    for cxp, cyp, sx, sy in corners:
        pygame.draw.polygon(surf, INNER, [
            (cxp, cyp),
            (cxp + sx * leg, cyp),
            (cxp, cyp + sy * leg),
        ])
    for cxp, cyp, sx, sy in corners[:2]:
        pygame.draw.line(surf, GLINT, (cxp, cyp), (cxp + sx * leg, cyp),
                         max(1, sc.m(0.8)))


# ── ghost-tag-check overlay ──────────────────────────────────────────────────
def draw_ghost_tag_check(surf):
    """Trace Panel 0's swing-tag as a faint cream hairline (tag rect + grommet +
    cord off the knot) so the object still reads, then strike a bold opaque cream
    ✓ over its face. Ghost stays cool and light at partial alpha so it never
    competes with the gold regalia; the tick is the only element that must read
    at 1×. The 1px dark offset under the tick gives it bite against the cream."""
    GHOST = (250, 246, 232)          # cream, kept LIGHT — never indigo-on-indigo
    GHOST_A = 92                     # ~36% alpha: present as atmosphere, not ink
    CHECK = (250, 246, 232)          # fully-opaque hero tick
    BITE = (46, 38, 18)              # dark 1px offset so the tick edges bite

    tag_center = (44, 60)            # same anchor price_chip() lands the tag on
    grommet = (30, 13)               # tag-face-local grommet, per price_chip()
    knot = (22, 13)
    trad = sc.m(3)                   # tag corner radius, matched to price_chip()
    hair = max(1, sc.m(0.8))         # hairline stroke — the "ghost" weight

    # Tag face outline + grommet ring, authored upright on the face surface then
    # rotated the same -7° as the real tag so silhouette + tilt match exactly.
    face = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, sc._TAG_W, sc._TAG_H)
    pygame.draw.rect(face, (*GHOST, GHOST_A), brect, width=hair,
                     border_radius=trad)
    pygame.draw.circle(face, (*GHOST, GHOST_A), grommet, sc.m(5) + 1,
                       width=max(1, sc.m(1)))
    rot = pygame.transform.rotate(face, sc._TAG_TILT)

    # Cord from the rotated grommet back to the knot — mirrors the two-strand
    # forked cord the real chip draws, but as a single faint hairline pair.
    gx, gy = sc._tag_rot_point(*grommet, tag_center)
    cord = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    lw = max(1, sc.m(1))
    pygame.draw.line(cord, (*GHOST, GHOST_A), (gx, gy),
                     (knot[0] - 1, knot[1] - 1), lw)
    pygame.draw.line(cord, (*GHOST, GHOST_A), (gx, gy),
                     (knot[0] + 2, knot[1] + 2), lw)
    pygame.draw.circle(cord, (*GHOST, GHOST_A), knot, max(1, sc.m(1.2)))
    surf.blit(cord, (0, 0))
    surf.blit(rot, rot.get_rect(center=tag_center))

    # The hero tick: asymmetric ✓ crossing the tag face. The long up-right arm is
    # routed through the tag centre so it dominates the ghosted numeral area.
    cx, cy = tag_center
    pts = [
        (cx - sc.m(8), cy - sc.m(1)),    # short arm start (upper-left)
        (cx - sc.m(3), cy + sc.m(4)),    # elbow (lower)
        (cx + sc.m(8), cy - sc.m(10)),   # long arm end (upper-right)
    ]
    cw = max(2, sc.m(3))
    bite = [(x + 1, y + 1) for (x, y) in pts]
    pygame.draw.lines(surf, BITE, False, bite, cw)
    pygame.draw.lines(surf, CHECK, False, pts, cw)


# ── Panel 0 — UNEQUIPPED (price tag fully visible; study the geometry) ────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)


# ── Panel 1 — REGALIA FRAME ONLY (chip suppressed) ───────────────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p1, rect)


# ── Panel 2 — CONCEPT (regalia frame + ghost-tag-check) ──────────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p2, rect)
draw_ghost_tag_check(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
# 1× downscale strip of Panel 2 under the row: (162,100) → 2× nearest = 324×200
ZOOM_W, ZOOM_H = sc.CARD_W * 2, sc.CARD_H * 2
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.2 — ghost-tag-check · round 1 · skin_mummy",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("GHOST-TAG-CHECK", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
panel_y = PAD + HDR_H + LBL_H          # = 102
zlbl_y = panel_y + PANEL_H + SGAP
zoom_y = zlbl_y + SLBL_H

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× read of the concept only: true 162×100 tile blown back up nearest-neighbour
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
zx = PAD + 2 * (PANEL_W + GAP)          # centred under the concept panel
zt = zlbl_f.render("CONCEPT @1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(zx + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(zoom, (zx + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_2", "ghost_tag_check", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
