#!/usr/bin/env python3
"""
equipped-card v3.1 — corner-studs symbol, round 2 (final).

Builds on the APPROVED regalia double-frame (v3 round 2): two concentric gold
beads plus corner masses. On top of it this pins FOUR gold rivet-studs, one on
each corner of the HOT inner gold track. Round 1's studs were gold-on-gold and
vanished; round 2 seats every rivet in a DARK socket so the warm cap pops.

Each stud is three clean zones, nothing sub-pixel:
  1. a dark indigo SOCKET disc (the washer/recess) — the cap sits in a dark seat
     so gold-on-dark clears the ~40% luminance contrast bar,
  2. a warm-gold DOME cap raised inside the socket,
  3. one cream specular PIP at upper-left + one bronze shadow at lower-right —
     the asymmetric pair reads as struck, domed metal instead of a flat dot.

Four rivets (not two) read as a riveted hardware SYSTEM, not stray decoration.
The top-right rivet is lifted a hair so a clear dark gap stays between it and the
faceted tier gem in that corner.

Drawn LAST over an equipped card whose green chip is suppressed, so the frame +
studs are the sole state signal on the concept panel.
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


def draw_regalia_frame(surf, body):
    """The approved nested second gold frame, decoupled from bevel_rim.

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
    bead(inset=8,  w=sc.m(1.4), col=VALLEY)          # flat dark valley
    bead(inset=10, w=sc.m(2.0), col=INNER)           # HOT inner track (hero line)
    bead(inset=13, w=max(1, sc.m(0.6)), col=KEY)     # fine inner keyline

    track = body.inflate(-2 * 10, -2 * 10)
    leg = sc.m(7)
    corners = [
        (track.left,  track.top,     1,  1),   # TL (top-lit)
        (track.right, track.top,    -1,  1),   # TR (top-lit)
        (track.left,  track.bottom,  1, -1),   # BL
        (track.right, track.bottom, -1, -1),   # BR
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


def draw_corner_studs(surf):
    """FOUR struck-metal rivet-studs, one per corner of the HOT inner rail.

    Each rivet is rendered on a 4× sub-canvas so its fractional radii and the
    off-centre specular pip stay clean AA discs when scaled to card SS. Three
    zones only — a dark indigo SOCKET disc that seats the rivet in a recess, a
    warm-gold DOME cap raised inside it, and an asymmetric CREAM pip (upper-left)
    / BRONZE shadow (lower-right) pair that models a struck dome under top-left
    light. Gold-on-dark, not gold-on-gold: the cap now clears ~40% luminance
    contrast against its immediate surround.

    The inner rail corners sit at device (18,18) / (306,18) / (18,182) /
    (306,182); centres are inset a couple px so the socket rides ON the gold rail
    and never clips the card edge. The top-right rivet is lifted 2px so a ≥6px
    dark gap stays clear between it and the faceted tier gem at (278,46) r22."""
    SOCK_LO = (28, 24, 66)      # darker outer washer ring — socket depth
    SOCKET = (44, 40, 96)       # deep-indigo washer/recess — the dark seat
    CAP = (236, 202, 116)       # warm-gold rivet dome — the raised head
    CAP_HI = (250, 224, 152)    # lit upper-left of the dome (roundness, not flat)
    PIP = (255, 248, 224)       # cream specular pip — top-left struck sheen
    BRONZE = (140, 110, 55)     # bronze shadow — the shaded lower-right of dome

    # Drawn directly at device SS (like the frame beads) — a per-stud smoothscale
    # muddied the tiny cap to olive; crisp fills keep gold-on-dark contrast.
    def stud(cx, cy):
        pygame.draw.circle(surf, SOCK_LO, (cx, cy), 7)             # outer dark ring
        pygame.draw.circle(surf, SOCKET, (cx, cy), 6)             # indigo seat
        pygame.draw.circle(surf, CAP, (cx, cy), 4)               # warm dome cap
        pygame.draw.circle(surf, CAP_HI, (cx - 1, cy - 1), 2)    # lit upper-left
        pygame.draw.circle(surf, BRONZE, (cx + 2, cy + 2), 1)    # shaded lower-right
        pygame.draw.circle(surf, PIP, (cx - 1, cy - 1), 1)       # cream specular pip

    stud(22, 22)     # TL — on the inner-rail top-left corner
    stud(302, 20)    # TR — lifted 2px to hold a ≥6px gap off the tier gem
    stud(22, 178)    # BL
    stud(302, 178)   # BR


def build_concept(with_studs):
    """An equipped card with the green state chip suppressed, the regalia frame
    laid over it, and (optionally) the four corner studs — so the frame ± studs
    are the ONLY equipped signal on the tile."""
    orig_chip = sc.state_chip
    sc.state_chip = lambda *a, **kw: None
    sc._card_cache.clear()
    surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.draw_card(surf, SID, rect, equipped=True, secret=False)
    sc.state_chip = orig_chip
    sc._card_cache.clear()
    draw_regalia_frame(surf, rect)
    if with_studs:
        draw_corner_studs(surf)
    return surf


# ── Panel 0 — UNEQUIPPED (price tag visible, no symbol) ──────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)

# ── Panel 1 — REGALIA FRAME ONLY / Panel 2 — FRAME + 4 CORNER STUDS ──────────
p1 = build_concept(with_studs=False)
p2 = build_concept(with_studs=True)


# ── Compose the review sheet ─────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24

GOLD = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)

N = 3
panel_y = PAD + HDR_H + LBL_H                 # = 102
# a true 1× row under the panels shows frame-only vs +studs side by side
STRIP_W, STRIP_H = sc.CARD_W * 2, sc.CARD_H * 2   # scale2x of the true 162×100 tile
slbl_y = panel_y + PANEL_H + SGAP
strip_y = slbl_y + SLBL_H

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD          # 1044
sheet_h = strip_y + STRIP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.1 — corner-studs · round 2 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME ONLY", GREY),
          ("FRAME + 4 CORNER STUDS", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
slbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× read: two genuine 162×100 tiles (smoothscale DOWN, then nearest 2×) so the
# frame-only → +studs delta is legible at true store size, not pixel-doubled.
def tile1x(panel):
    card1x = pygame.transform.smoothscale(panel, (sc.CARD_W, sc.CARD_H))
    return pygame.transform.scale(card1x, (STRIP_W, STRIP_H))

strip_frame = tile1x(p1)
strip_studs = tile1x(p2)
sx_frame = PAD + (PANEL_W - STRIP_W) // 2 + (PANEL_W + GAP)        # under panel 1
sx_studs = PAD + (PANEL_W - STRIP_W) // 2 + 2 * (PANEL_W + GAP)    # under panel 2

for sx, cap, panel_x_off, col in [
        (sx_frame, "@1× frame only", PANEL_W + GAP, GREY),
        (sx_studs, "@1× + 4 studs (delta)", 2 * (PANEL_W + GAP), CREAM_LBL)]:
    center_x = PAD + panel_x_off + PANEL_W // 2
    st = slbl_f.render(cap, True, col)
    sheet.blit(st, st.get_rect(midbottom=(center_x, slbl_y + SLBL_H - 4)))

sheet.blit(strip_frame, (sx_frame, strip_y))
sheet.blit(strip_studs, (sx_studs, strip_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "corner_studs", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
