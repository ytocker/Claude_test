#!/usr/bin/env python3
"""
equipped-card v3.1 — corner-studs symbol, round 1.

Builds on the APPROVED regalia double-frame (v3 round 2): the two concentric
gold beads plus corner masses. On top of that frame this adds the new symbol —
a symmetric PAIR of gold rivet-studs pinned at the two UPPER corners of the
inner gold rail. Read together, the closed double frame + the two fastened
studs say "frame fitted shut": the card isn't just outlined in gold, it's
RIVETED into its regalia, a stronger equipped signal than the frame alone.

Each stud is a struck-metal rivet: a deep-gold rim disc, a raised warm-gold
cap, a cream specular pip catching the top-left light, and a deep-indigo recess
at its centre. The right stud is nudged a hair up-right of its mirror position
so its rim clears the faceted tier gem in the top-right corner.

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
    """A mirrored pair of struck-metal rivet-studs on the two UPPER inner-rail
    corners — the "fitted shut" fasteners. Each stud is rendered on a 4×
    sub-canvas so its fractional radii (r≈5 rim, r≈3 cap, r≈1.2 recess) and the
    specular pip stay clean AA discs when scaled down to the card SS. The right
    stud rides a touch up-right of its mirror twin so its rim clears the faceted
    tier gem that lives in the top-right corner."""
    RIM = (196, 158, 74)        # deep-gold rim disc — the seated flange
    CAP = (236, 202, 116)       # warm-gold rivet head — the raised cap
    PIP = (255, 248, 224)       # cream specular pip — struck-metal sheen
    RECESS = (44, 40, 96)       # deep-indigo inlay dot — the driven recess

    K = 4                       # per-stud oversample for crisp fractional discs
    BOX = 26                    # device-px region around a stud centre
    half = BOX / 2

    def stud(cx, cy):
        sub = pygame.Surface((BOX * K, BOX * K), pygame.SRCALPHA)
        c = (half * K, half * K)
        pygame.draw.circle(sub, RIM, c, 5 * K)                 # rim flange
        pygame.draw.circle(sub, CAP, c, 3 * K)                 # raised cap
        # specular pip: a 1px sheen pulled to the top-left where the light sits
        pygame.draw.circle(sub, PIP,
                           (c[0] - 1.4 * K, c[1] - 1.4 * K), 1.1 * K)
        pygame.draw.circle(sub, RECESS, c, 1.2 * K)            # centre recess
        small = pygame.transform.smoothscale(sub, (BOX, BOX))
        surf.blit(small, (int(round(cx - half)), int(round(cy - half))))

    stud(28, 28)     # TL — mirror anchor
    stud(298, 26)    # TR — nudged up-right to clear the tier gem at (278,46) r22


# ── Panel 0 — UNEQUIPPED (price tag visible, no symbol) ──────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)

# ── Panel 1 — REGALIA FRAME ONLY (chip suppressed, no stud) ──────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p1, rect)

# ── Panel 2 — CONCEPT (chip suppressed, frame + corner studs) ────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(p2, rect)
draw_corner_studs(p2)


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
# 1× strip lives under panel 2 only
STRIP_W, STRIP_H = sc.CARD_W * 2, sc.CARD_H * 2   # scale2x of the true 162×100 tile
slbl_y = panel_y + PANEL_H + SGAP
strip_y = slbl_y + SLBL_H

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD          # 1044
sheet_h = strip_y + STRIP_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.1 — corner-studs · round 1 · skin_mummy", True, GOLD)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("REGALIA FRAME", GREY),
          ("+ CORNER STUDS", CREAM_LBL)]
panels = [p0, p1, p2]

lbl_f = hud_font(15, True)
slbl_f = hud_font(13, True)

for i, (panel, (label, col)) in enumerate(zip(panels, labels)):
    px = PAD + i * (PANEL_W + GAP)
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(px + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (px, panel_y))

# 1× read for the concept: true 162×100 tile (smoothscale down), then nearest 2×
px2 = PAD + 2 * (PANEL_W + GAP)
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip = pygame.transform.scale(card1x, (STRIP_W, STRIP_H))
st = slbl_f.render("@1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(st, st.get_rect(midbottom=(px2 + PANEL_W // 2, slbl_y + SLBL_H - 4)))
sheet.blit(strip, (px2 + (PANEL_W - STRIP_W) // 2, strip_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_1", "corner_studs", "round_1.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
