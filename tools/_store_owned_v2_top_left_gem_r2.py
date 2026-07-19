#!/usr/bin/env python3
"""store_owned_v2 — top-left-gem concept.
Owned state: no hang-tag; instead a second facet-gem badge appears at the
top-LEFT corner, mirroring the top-right rarity crest gem.
Two gems = owned. One gem = unowned/equipped-only.
"""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import pygame; pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
import game.store_data as sd
from game import store_catalog

sd.load()
SID = "skin_mummy"

CW, CH = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324 × 200
CARD_RECT = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                        CW - 2 * sc.m(sc._INSET), CH - 2 * sc.m(sc._INSET))

BG    = (8, 8, 20)
xs    = [20, 360, 700]
PY    = 102
SHEET_W = xs[-1] + CW + 20
SHEET_H = PY + CH + 8 + CH + 36    # panel + gap + zoom strip + label row

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill(BG)


def make_card(equipped, owned):
    s = pygame.Surface((CW, CH), pygame.SRCALPHA)
    sc.draw_card(s, SID, CARD_RECT, equipped, False, owned=owned)
    return s


# ── Panel 0: UNOWNED (price tag) ─────────────────────────────────────────────
p0 = make_card(False, False)
sheet.blit(p0, (xs[0], PY))

# ── Panel 1: EQUIPPED BASE (regalia frame + check tag) ───────────────────────
p1 = make_card(True, False)
sheet.blit(p1, (xs[1], PY))

# ── Panel 2: CONCEPT — top-left gem (no hang-tag) ────────────────────────────
p2 = pygame.Surface((CW, CH), pygame.SRCALPHA)

# Draw full card body but suppress the state_chip so no hang-tag is drawn
_orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc.draw_card(p2, SID, CARD_RECT, False, False, owned=False)
sc.state_chip = _orig_chip

# Mirror the top-right gem to the top-left corner (identical call, mirrored cx)
pal = sc.RARITY[store_catalog.rarity(SID)]
gem_cx_right = CARD_RECT.right  - sc.m(19)
gem_cx_left  = CARD_RECT.x      + sc.m(19)
gem_cy       = CARD_RECT.y      + sc.m(19)
gem_r        = sc.m(sc.GEM_R + 3)
sc.facet_gem(p2, gem_cx_left, gem_cy, gem_r, pal["gem"], pal["deep"])

sheet.blit(p2, (xs[2], PY))

# ── Zoom strip: true 1× read scaled 2× ───────────────────────────────────────
zoom = pygame.transform.scale2x(
    pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H)))
sheet.blit(zoom, (xs[2], PY + CH + 8))

# ── Save ──────────────────────────────────────────────────────────────────────
out_dir = "docs/store_owned_v2/top_left_gem"
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "round_2.png")
pygame.image.save(sheet, out)
print(f"saved {out} ({SHEET_W}x{SHEET_H})")

# ── 1× legibility check ───────────────────────────────────────────────────────
from PIL import Image
im = Image.open(out).convert("RGB")
# Sample the top-left gem area on the zoom strip (xs[2], PY+CH+8 is zoom origin)
zx, zy = xs[2], PY + CH + 8
# The gem at top-left in the zoom strip (scale2x of 162×100 → 324×200)
# gem_cx_left at SS=2 → 1× coord = gem_cx_left//2; then ×2 in zoom = gem_cx_left
# Gem center in zoom coords:
zoom_gem_cx = zx + gem_cx_left         # already device px, scale2x ×2 = same
zoom_gem_cy = zy + gem_cy
# Zoom is smoothscale(SS→1x) → scale2x, so zoom pixel = p2 pixel at half res then ×2
# Simpler: sample at device coords on p2 region (xs[2], PY)
p2_gem_px = im.getpixel((xs[2] + gem_cx_left, PY + gem_cy))
p2_right_px = im.getpixel((xs[2] + gem_cx_right, PY + gem_cy))
print(f"top-left gem pixel  @({gem_cx_left},{gem_cy}): {p2_gem_px}")
print(f"top-right gem pixel @({gem_cx_right},{gem_cy}): {p2_right_px}")
bg_px = im.getpixel((xs[2] + 5, PY + 5))
print(f"card body corner pixel: {bg_px}  (should be indigo/dark, not BG)")
