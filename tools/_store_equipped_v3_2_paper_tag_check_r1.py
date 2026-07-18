#!/usr/bin/env python3
"""
equipped-card v3.2 — paper-tag-check concept, round 1.

An equipped skin swaps its cream price swing-tag for the SAME swing-tag stamped
with a bold ✓ instead of a numeral: the only rectangular silhouette in the
equipped-state set, so it reads instantly against the round chips/medallions
while directly reusing the price-tag's hang-tag metaphor. The card wears the
regalia double-frame for its equipped signal; the check-tag is the second,
literal "this one's yours — paid/claimed" read hanging off the same cord.

Drawn LAST over an equipped card whose state chip is suppressed, so the frame +
check-tag are the sole state signals on the concept panel.
"""
import math
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


# ── regalia frame — copied verbatim from _store_equipped_v3_regalia_frame_r2 ──
def draw_regalia_frame(surf, body):
    """The nested second gold frame, decoupled from bevel_rim.

    Read outer→inner: a warm-gold OUTER bead hugging the card edge, a flat dark
    VALLEY that cleaves the two beads apart, a HOT constant INNER track (the hero
    line, hotter than the bevel on EVERY edge), a fine dark inner keyline, and
    four bright corner masses. Because each bead is a single flat-colour stroke —
    not a gradient — the sides and bottom stay exactly as bright as the top, so
    the double frame reads as an even jewelled ring at the 162×100 tile size."""
    OUTER = (236, 202, 116)     # warm-gold outer bead (the bevel-echo line)
    VALLEY = (9, 9, 22)         # flat near-body dark — clean, no indigo bleed
    INNER = (255, 240, 190)     # HOT constant inner track — hotter than the bevel
    KEY = (46, 38, 18)          # deep inner keyline: a defined inner boundary
    GLINT = (255, 248, 224)     # jewel highlight on the two top-lit corners

    def bead(inset, w, col, alpha=255):
        """A CONSTANT-colour rounded-rect stroke inset `inset` device-px from the
        card edge — no top-lit falloff, so the stroke is equally hot on all four
        sides."""
        r = body.inflate(-2 * inset, -2 * inset)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, alpha), r, width=w,
                         border_radius=max(1, rad - inset))
        surf.blit(s, (0, 0))

    bead(inset=2,  w=sc.m(3.0), col=OUTER)           # outer bead
    bead(inset=8,  w=sc.m(1.4), col=VALLEY)          # flat dark valley (widened)
    bead(inset=10, w=sc.m(2.0), col=INNER)           # HOT inner track (hero line)
    bead(inset=13, w=max(1, sc.m(0.6)), col=KEY)     # fine inner keyline

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


# ── paper-tag-check overlay ───────────────────────────────────────────────────
# Same swing-tag metaphor as price_chip, sized ~7% down (identical 81:94 ratio)
# so it feels like the same product family but reads as its own equipped token.
_PT_W, _PT_H, _PT_TILT = 75, 87, -7


def _pt_rot_point(px, py, center):
    """Rotate a face-local point about the tag centre — the check-tag's own copy
    of _tag_rot_point pinned to this concept's smaller face size."""
    th = math.radians(_PT_TILT)
    dx, dy = px - _PT_W / 2, py - _PT_H / 2
    rx = dx * math.cos(th) + dy * math.sin(th)
    ry = -dx * math.sin(th) + dy * math.cos(th)
    return (center[0] + rx, center[1] + ry)


def _pt_draw_check(face):
    """A bold cream ✓ struck into the tag face. Asymmetric tick: a short arm from
    upper-left DOWN to the vertex, a long arm sweeping UP-RIGHT past centre. A 1px
    dark ghost sits under it so the check reads as pressed into the paper, and a
    faint top-light echo keeps the cream stroke from going flat."""
    cx = _PT_W // 2
    # Face coords are device px; the check is authored directly at that scale so
    # its stroke lands near the "~3px·SS" brief weight without the m() helper.
    w = 6                                   # ≈ 3 logical px at SS=2
    vertex = (cx - 3, int(_PT_H * 0.62))    # bottom of the tick
    l_arm  = (cx - 14, int(_PT_H * 0.50))   # SHORT arm — upper-left
    r_arm  = (cx + 20, int(_PT_H * 0.28))   # LONG arm — up-right, owns the face

    def stroke(col, dx=0, dy=0, ww=w):
        a = (l_arm[0] + dx, l_arm[1] + dy)
        v = (vertex[0] + dx, vertex[1] + dy)
        b = (r_arm[0] + dx, r_arm[1] + dy)
        pygame.draw.line(face, col, a, v, ww)
        pygame.draw.line(face, col, v, b, ww)
        for pt in (a, v, b):                # round the joints/caps
            pygame.draw.circle(face, col, pt, ww // 2)

    stroke((80, 52, 12, 235), dx=1, dy=1)        # recessed dark ghost (pressed)
    stroke((250, 246, 232, 255))                 # bold cream check
    stroke((255, 250, 236, 200), dx=0, dy=-1, ww=max(1, w - 3))  # top-light echo


def paper_tag_check(surf):
    """Draw the cream swing-tag stamped with a ✓, hung on one clean gold cord —
    mirrors price_chip's fixed (44,60) anchor + (22,13) knot so it lands exactly
    where the price tag did, but slightly smaller and check-stamped."""
    rad3 = sc.m(3)
    grommet = (28, 12)                       # single punched hole near the top
    tag_center = (44, 60)                    # same anchor as price_chip
    knot = (22, 13)

    face = pygame.Surface((_PT_W, _PT_H), pygame.SRCALPHA)
    brect = pygame.Rect(0, 0, _PT_W, _PT_H)

    # exact price-tag cream face gradient + gamma so the two tags share one paper
    body = sc.vgrad_stops(_PT_W, _PT_H, rad3,
                          [(0.0, (248, 238, 210)), (1.0, (224, 204, 166))],
                          255, gamma=1.04)
    face.blit(body, (0, 0))
    sc.bevel_rim(face, brect, rad3, (80, 52, 12, 200),
                 (255, 240, 190, 200), w=max(1, sc.m(1.2)))

    _pt_draw_check(face)

    # punched hole + thin gold grommet ring
    pygame.draw.circle(face, (0, 0, 0, 0), grommet, sc.m(5))
    pygame.draw.circle(face, (110, 80, 30), grommet, sc.m(5) + 1, width=max(1, sc.m(1)))

    rot = pygame.transform.rotate(face, _PT_TILT)
    cord = (190, 165, 115)
    gx, gy = _pt_rot_point(*grommet, tag_center)
    lw = sc.m(1.5)
    # ONE clean cord grommet→knot (no V, no multi-loop)
    pygame.draw.line(surf, cord, (gx, gy), knot, lw)
    surf.blit(rot, rot.get_rect(center=tag_center))
    pygame.draw.circle(surf, cord, knot, sc.m(1.5))
    pygame.draw.circle(surf, (220, 195, 145), knot, max(1, sc.m(0.6)))


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


# ── Panel 2 — CONCEPT (regalia frame + paper-tag-check overlay) ──────────────
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p2, rect)
paper_tag_check(p2)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
STRIP_W, STRIP_H = sc.CARD_W * 2, sc.CARD_H * 2   # 324×200 nearest-neighbour 1×

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
panel_y = PAD + HDR_H + LBL_H              # = 102
slbl_y = panel_y + PANEL_H + SGAP
strip_y = slbl_y + SLBL_H
sheet_h = strip_y + STRIP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.2 — paper-tag-check · round 1 · skin_mummy",
                    True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("PAPER-TAG-CHECK", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× read: smoothscale Panel 2 to the true 162×100 tile, then 2× nearest so the
# sheet shows exactly how the check-tag resolves at real card size.
strip = pygame.transform.scale(
    pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H)),
    (STRIP_W, STRIP_H))
strip_x = PAD + 2 * (PANEL_W + GAP) + (PANEL_W - STRIP_W) // 2
zt = zlbl_f.render("PAPER-TAG-CHECK @1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(strip_x + STRIP_W // 2, strip_y - 4)))
sheet.blit(strip, (strip_x, strip_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_2", "paper_tag_check", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
