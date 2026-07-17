"""Phase 5 showcase: equipped state — BEFORE + 5 concept panels."""
import os, sys
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
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS  # 324×200

# ── render BEFORE panel (stock equipped: green chip only) ─────────────────────
sc._card_cache.clear()
before = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
ri = sc.m(sc._INSET)
rect_card = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
sc.draw_card(before, SID, rect_card, equipped=True, secret=False)
sc._card_cache.clear()

# Blit onto dark background so the showcase panel matches the concept crops.
before_panel = pygame.Surface((PANEL_W, PANEL_H))
before_panel.fill((8, 8, 20))
before_panel.blit(before, (0, 0))

# ── per-concept crop coordinates (from each script's layout constants) ─────────
# All r2 scripts: PAD=20, GAP=16, PANEL_W=324
# HDR_H and label position determine panel_y for each sheet.
#
# charged_frame:   GAP=16, HDR_H=48, LBL_H=34 → panel_y=102
# corner_seal:     GAP=16, HDR_H=48, LBL_H=34 → panel_y=102
# inner_gasket:    GAP=16, HDR_H=48, LBL_H=34 → panel_y=102
# emerald_weave:   GAP=16, HDR_H=54, LBL_H=34 → panel_y=108
# activation_burst:GAP=16, HDR_H=48, LBL_H=34 → panel_y=102
#
# Concept panel column (0-indexed):
# charged_frame, corner_seal, inner_gasket, activation_burst → index 2
# emerald_weave → index 1 (mummy teal-equipped; index 2 is ninja comparison)

def _x(pidx, gap=16):
    return 20 + pidx * (PANEL_W + gap)

CONCEPTS = [
    ("charged_frame",    "CHARGED FRAME",   _x(2), 102),
    ("corner_seal",      "CORNER SEAL",     _x(2), 102),
    ("inner_gasket",     "INNER GASKET",    _x(2), 102),
    ("emerald_weave",    "EMERALD WEAVE",   _x(1), 108),
    ("activation_burst", "ACTIV. BURST",    _x(2), 102),
]

panels = [("BEFORE", before_panel)]
for slug, label, x0, y0 in CONCEPTS:
    path = os.path.join("docs/store_equipped", slug, "round_2.png")
    img = pygame.image.load(path).convert()
    sub = img.subsurface(pygame.Rect(x0, y0, PANEL_W, PANEL_H))
    panels.append((label, sub.copy()))

# ── layout ────────────────────────────────────────────────────────────────────
BG    = (8, 8, 20)
PAD   = 20
GAP   = 8
HDR_H = 40
FTR_H = 32
N     = len(panels)  # 6

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + PANEL_H + FTR_H + PAD

showcase = pygame.Surface((sheet_w, sheet_h))
showcase.fill(BG)

fh = hud_font(15, True)
fl = hud_font(11, True)

title = fh.render("store card — EQUIPPED state · 5 design concepts",
                  True, (240, 224, 180))
showcase.blit(title, ((sheet_w - title.get_width()) // 2,
                       PAD + (HDR_H - title.get_height()) // 2))

y_panels = PAD + HDR_H
for i, (label, surf) in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    showcase.blit(surf, (x, y_panels))
    col = (170, 166, 190) if i == 0 else (255, 226, 120)
    t = fl.render(label, True, col)
    y_lbl = y_panels + PANEL_H + (FTR_H - t.get_height()) // 2
    showcase.blit(t, (x + (PANEL_W - t.get_width()) // 2, y_lbl))

out = "docs/store_equipped/showcase.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(showcase, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
