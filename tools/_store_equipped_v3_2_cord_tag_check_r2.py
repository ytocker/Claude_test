#!/usr/bin/env python3
"""
equipped-card v3.2 — cord-tag-check concept, round 2 (final).

Same load-bearing idea as round 1: a gold HANG-DISC that keeps the price-tag's
cord-and-knot rigging but swaps the rectangular swing-tag for a round medallion
struck with a ✓, so the equipped state reads as "the same tag, re-minted as a
seal." Round 1's failures were all inside the disc: the cream ✓ sat cream-on-gold
at ~1.25:1 (nearly invisible), the disc gold was byte-identical to the frame's
outer bead (so it read as a fourth frame line, not a distinct coin), and the ✓
arms crowded the rim.

Round 2 fixes them together by giving the disc its OWN gold family — a deep
ANTIQUE-BRONZE face, clearly darker/redder than the frame's warm gold — so the
disc reads as a struck coin, and a CREAM ✓ then becomes the highest-contrast
element inside it (cream-on-antique-bronze clears WCAG by a wide margin). The
mark is pulled ~17% tighter so a clean bronze margin ring sits between its arm
tips and the rim keyline, and a single soft top-left specular arc adds the one
"premium coin" gloss cue without a full reeded edge. The cord stays fully
legible — two tan strands from the shared knot — as the concept's differentiator.
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
ri = sc.m(sc._INSET)                                      # 8
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)   # card body
rad = sc.m(sc.CARD_RAD)                                   # body corner radius


# ── Regalia frame (copied verbatim from _store_equipped_v3_regalia_frame_r2) ──
def draw_regalia_frame(surf, body):
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


# ── Cord-tag-check overlay ────────────────────────────────────────────────────
def draw_cord_tag_check(surf):
    """The gold hang-disc seal. Anchored on the SAME (44,60) tag body centre and
    (22,13) knot the price tag uses, so the cord rigging is inherited 1:1."""
    # Antique-bronze disc face — a distinct, DEEPER gold than the frame's warm
    # (236,202,116) bead, so the disc reads as its own struck coin rather than a
    # fourth frame line. The dark bottom of this ramp is also what makes the cream
    # ✓ the highest-contrast element inside the disc.
    BRONZE_TOP = (176, 130, 66)
    BRONZE_BOT = (104, 72, 32)
    CREAM = (250, 246, 232)
    CORD = (190, 165, 115)
    KEY = (74, 44, 14)
    SPEC = (255, 246, 214)

    cx, cy = 44, 60                 # tag body anchor (shared with price_chip)
    knot = (22, 13)
    r = 14                          # ~28px disc, device-px (SS already baked in)
    top = (cx, cy - r)             # cord lands on the disc crown

    # AA supersample factor for the disc + keyline + ✓, resolved once then
    # smoothscaled so the circular rim and stroke caps stay clean.
    F = 4
    D = 2 * r

    # Cord: two cream-tan strands from the knot down to the disc crown — the one
    # detail that separates this from a bare disc, so it stays fully legible.
    lw = sc.m(1.5)
    pygame.draw.line(surf, CORD, knot, (cx - 2, top[1] + 2), lw)
    pygame.draw.line(surf, CORD, knot, (cx + 2, top[1] + 2), lw)
    pygame.draw.circle(surf, CORD, knot, sc.m(1.5))
    pygame.draw.circle(surf, (min(CORD[0] + 30, 255), min(CORD[1] + 30, 255),
                              min(CORD[2] + 30, 255)), knot, max(1, sc.m(0.6)))

    # Soft drop shadow — positive relief lift, offset +1.2px at ~40% alpha.
    sh = pygame.Surface((D + 4, D + 4), pygame.SRCALPHA)
    pygame.draw.circle(sh, (10, 8, 4, 102), (sh.get_width() // 2,
                                             sh.get_height() // 2), r)
    off = sc.mf(1.2)
    surf.blit(sh, (cx - sh.get_width() // 2 + off, cy - sh.get_height() // 2 + off))

    # Disc: top-lit antique-bronze gradient masked to a circle + one fine dark
    # contact keyline at the rim (no reeded/beaded edge — the frame carries that).
    big = pygame.Surface((D * F, D * F), pygame.SRCALPHA)
    grad = sc.vgrad_stops(D * F, D * F, 0,
                          [(0.0, BRONZE_TOP), (1.0, BRONZE_BOT)], 255, gamma=1.06)
    cmask = pygame.Surface((D * F, D * F), pygame.SRCALPHA)
    pygame.draw.circle(cmask, (255, 255, 255, 255),
                       (D * F // 2, D * F // 2), D * F // 2)
    grad.blit(cmask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    big.blit(grad, (0, 0))
    pygame.draw.circle(big, KEY, (D * F // 2, D * F // 2),
                       D * F // 2, width=max(2, int(round(1.0 * sc.SS * F))))
    disc = pygame.transform.smoothscale(big, (D, D))
    surf.blit(disc, (cx - r, cy - r))

    # One restrained specular hit — a single soft top-left highlight arc a couple
    # px inside the rim, the cheapest "premium coin" gloss cue. Drawn supersampled
    # then downscaled so it reads as a soft sheen, not a hard drawn line.
    spec = pygame.Surface((D * F, D * F), pygame.SRCALPHA)
    import math
    pygame.draw.arc(spec, (*SPEC, 150),
                    pygame.Rect(int(2.5 * F), int(2.5 * F),
                                int((D - 5) * F), int((D - 5) * F)),
                    math.radians(105), math.radians(190), max(2, int(2.0 * F)))
    surf.blit(pygame.transform.smoothscale(spec, (D, D)), (cx - r, cy - r))

    # Raised ✓ — CREAM mark on the antique-bronze face (the highest-contrast
    # element inside the disc), with a faint dark relief shadow so it reads
    # embossed OUT of the face, never intaglio. Pulled ~17% tighter than r1 so a
    # clean bronze margin ring sits between the arm tips and the rim keyline.
    def check_layer(col, w):
        s = pygame.Surface((D * F, D * F), pygame.SRCALPHA)
        pts = [(cx - 9, cy - 2), (cx - 5, cy + 4), (cx + 8, cy - 8)]
        loc = [((px - (cx - r)) * F, (py - (cy - r)) * F) for px, py in pts]
        pygame.draw.lines(s, col, False, loc, w)
        for p in loc:                       # rounded caps / join
            pygame.draw.circle(s, col, (int(p[0]), int(p[1])), w // 2)
        return pygame.transform.smoothscale(s, (D, D))

    stroke = max(2, int(round(2.5 * sc.SS * F)))
    relief = check_layer((52, 32, 10, 165), stroke)
    surf.blit(relief, (cx - r + 1, cy - r + 1))
    surf.blit(check_layer(CREAM, stroke), (cx - r, cy - r))


# ── Panel 0 — UNEQUIPPED (price tag visible) ─────────────────────────────────
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


# ── Panel 2 — CONCEPT (regalia frame + cord-tag-check hang-disc) ─────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p2, rect)
draw_cord_tag_check(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H          # 162×100 — true 1× card size
ZOOM_W, ZOOM_H = PANEL_W, PANEL_H            # 2× nearest blow-up of the 1× tile

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.2 — cord-tag-check · round 2 · skin_mummy",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("CORD-TAG-CHECK", CREAM_LBL)]
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

# 1× read of the CONCEPT: TRUE 162×100 tile (smoothscale down), then blow it
# back up 2× nearest so the sheet shows how the hang-disc resolves at real size.
px2 = PAD + 2 * (PANEL_W + GAP)
card1x = pygame.transform.smoothscale(p2, (ONE_W, ONE_H))
zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
zt = zlbl_f.render("@1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(px2 + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(zoom, (px2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_2", "cord_tag_check", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
