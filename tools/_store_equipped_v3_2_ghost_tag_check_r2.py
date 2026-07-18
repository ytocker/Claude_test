#!/usr/bin/env python3
"""
equipped-card v3.2 — ghost-tag-check concept, round 2 (final).

Narrative unchanged: "the price is gone, it's yours." But round 1's tag was a
hairline OUTLINE that fragmented into stray strokes at the 162x100 tile size,
composited to a cold B-leading lavender-grey, and stacked on the frame's busiest
corner. Round 2 fixes all of that:

  * The tag is now a FILLED tilted-rect wash (a closed silhouette survives the
    downscale where a thin outline breaks up), in warm cream so the composite
    lands near neutral instead of lavender.
  * The grommet / forked cord / knot are gone — sub-pixel corner noise. The
    filled ghost plane plus the bold check carry the whole idea.
  * The tag is repositioned inward and down onto quiet indigo gradient, clear of
    the gold left rail and the top-left corner filigree, so the ghost owns its
    own real estate.
  * The bold check is anchored inside the ghost face and shares the tag's -7°
    tilt, so tick + tag read as one "cancelled price" unit — the tick stays the
    fully-opaque hero, the wash stays pure atmosphere.

Drawn LAST over an equipped card whose green chip is suppressed and whose regalia
double-frame is already laid, so the frame carries "selected" and the struck tag
carries "paid for / owned".
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
# Warm cream chosen so a faint wash over the card's strongly blue indigo body
# still composites to a neutral R≈B≈G cream — a cold cream would only reinforce
# the body's blue and read as lavender-grey. Alpha sits at the low end (~30%): a
# filled plane this faint is atmosphere, never ink competing with the gold
# regalia, yet enough to overcome the deep-blue body's tint at the sample point.
WASH = (255, 233, 172)
WASH_A = 78
CHECK = (250, 246, 232)          # fully-opaque hero tick
BITE = (46, 38, 18)              # dark 1px offset so the tick edges bite

TAG_CENTER = (66, 78)            # inward + down onto quiet gradient, off the frame
TAG_TILT = sc._TAG_TILT          # share the real swing-tag's -7°


def _tilt(dx, dy):
    """Rotate an offset by the tag's -7° so struck marks share the tag's lean."""
    th = math.radians(TAG_TILT)
    c, s = math.cos(th), math.sin(th)
    return (dx * c + dy * s, -dx * s + dy * c)


def draw_ghost_tag_check(surf):
    """Lay a FILLED cream wash in the real swing-tag's silhouette + tilt (a closed
    plane survives the 162×100 downscale), then strike a bold opaque cream ✓ over
    its face at the same -7° lean. The wash is pure low-alpha atmosphere; the tick
    is the only element that must resolve at 1×, so it stays fully opaque with a
    1px dark bite offset for edge separation against the cream."""
    # Filled tilted-rect plane: authored upright on its own surface, rotated the
    # same -7° as the real tag, then centred — silhouette + tilt match exactly.
    trad = sc.m(3)
    face = pygame.Surface((sc._TAG_W, sc._TAG_H), pygame.SRCALPHA)
    pygame.draw.rect(face, (*WASH, WASH_A),
                     pygame.Rect(0, 0, sc._TAG_W, sc._TAG_H),
                     border_radius=trad)
    rot = pygame.transform.rotate(face, TAG_TILT)
    surf.blit(rot, rot.get_rect(center=TAG_CENTER))

    # Hero ✓: elbow seated in the ghost's upper-left numeral zone, a long dominant
    # up-right arm and a short up-left arm, every vertex tilted -7° so tick + tag
    # lock into one cancelled-price unit.
    ex, ey = 45, 61
    short = _tilt(-sc.m(6), -sc.m(5))
    lng = _tilt(sc.m(12), -sc.m(14))
    pts = [
        (ex + short[0], ey + short[1]),   # short arm start (upper-left)
        (ex, ey),                         # elbow
        (ex + lng[0], ey + lng[1]),       # long arm end (upper-right)
    ]
    cw = max(2, sc.m(3.5))
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
ZOOM_W, ZOOM_H = sc.CARD_W * 2, sc.CARD_H * 2
sheet_h = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL_H + ZOOM_H + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render("equipped v3.2 — ghost-tag-check · round 2 · skin_mummy",
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

card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
zoom = pygame.transform.scale(card1x, (ZOOM_W, ZOOM_H))
zx = PAD + 2 * (PANEL_W + GAP)
zt = zlbl_f.render("CONCEPT @1× (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(zx + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(zoom, (zx + (PANEL_W - ZOOM_W) // 2, zoom_y))


OUT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped_v3_2", "ghost_tag_check", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT), "render failed: output not written"
print("saved", OUT, sheet.get_size())
