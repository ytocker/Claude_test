"""Round-2 review sheet for the `inner-gasket` equipped-card concept.

Round-1 established perfect containment with BLEND_ADD. This pass replaces the
3 discrete inset rings (which created barcode-aliasing at 1×) with a single
smooth monotonic alpha ramp, pulls the hot-filament peak back from white-clip,
widens the primary pipe stroke so it holds at 1×, and fades the gasket out over
the lower quarter of the card so the ribbon/name/chip text stays clean.
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

PANEL_W = sc.CARD_W * sc.SS   # 324
PANEL_H = sc.CARD_H * sc.SS   # 200
ri    = sc.m(sc._INSET)
rect  = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
rad   = sc.m(sc.CARD_RAD)

# Emerald gasket palette — HOT pulled back from r1's (150,245,190) to keep peak
# below (130,255,190) when BLEND_ADD lands on an already-lit body.
EQ_PIPE     = (60,  210, 130)
EQ_PIPE_HOT = (120, 240, 180)


def _card(equipped):
    surf = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    sc.draw_card(surf, "skin_mummy", rect, equipped=equipped, secret=False)
    sc._card_cache.clear()
    return surf


orig_bal    = sd.balance
sd.balance  = lambda: 99999          # make the skin affordable so art shows
p1 = _card(equipped=False)
sd.balance  = orig_bal
sc._card_cache.clear()

p2 = _card(equipped=True)            # current in-game equipped reference
p3 = _card(equipped=True)            # inner-gasket concept built here

# ── gasket layer ──────────────────────────────────────────────────────────────
layer = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)

# Gasket rect lives inset from the body rim — glow stays fully contained.
g    = pygame.Rect(rect.x + sc.m(6), rect.y + sc.m(6),
                   rect.w - 2 * sc.m(6), rect.h - 2 * sc.m(6))
grad = rad - sc.m(3)

# 1. Primary pipe: width=m(2) so the stroke survives the 2→1× downscale.
pygame.draw.rect(layer, (*EQ_PIPE, 160), g,
                 width=max(1, sc.m(2)), border_radius=grad)

# 2. Hot filament threaded inside the pipe.
g2 = g.inflate(-sc.m(1.2), -sc.m(1.2))
pygame.draw.rect(layer, (*EQ_PIPE_HOT, 120), g2,
                 width=max(1, sc.m(1.2)), border_radius=max(1, grad - 1))

# 3. Smooth monotonic inward ramp — 7 rings, each lighter and slightly thinner,
#    no dark valleys between them (the alpha monotonically decreases inward).
for i in range(1, 8):
    inset = i * sc.m(0.8)
    gi    = g.inflate(-2 * int(inset), -2 * int(inset))
    if gi.width <= 0 or gi.height <= 0:
        continue
    # Power-law ensures the falloff front loads at the outer edge; by i=7 alpha
    # is effectively 0 so there is no hard termination ring at the center.
    a   = int(140 * (1 - (i - 1) / 7) ** 1.6)
    col = (EQ_PIPE[0], EQ_PIPE[1], EQ_PIPE[2], a)
    pygame.draw.rect(layer, col, gi,
                     width=max(1, sc.m(1)),
                     border_radius=max(1, grad - int(inset)))

# 4. Bottom-fade mask — the lower ~25% of the card carries the rarity ribbon,
#    item name, and price/chip; the gasket must not muddy that text zone.
#    We multiply the layer's alpha row-by-row: full opacity for the top 72%,
#    then a squared ramp to zero over the remaining 28%.
mask       = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
fade_start = int(PANEL_H * 0.72)
for y in range(0, fade_start):
    pygame.draw.line(mask, (255, 255, 255, 255), (0, y), (PANEL_W - 1, y))
for y in range(fade_start, PANEL_H):
    t     = (y - fade_start) / max(1, PANEL_H - fade_start)
    a_row = int(255 * (1 - t) ** 2)
    pygame.draw.line(mask, (255, 255, 255, a_row), (0, y), (PANEL_W - 1, y))
# BLEND_RGBA_MIN lets the mask attenuate layer's alpha without touching RGB.
layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

p3.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

# ── PIL pixel-ceiling check ───────────────────────────────────────────────────
# We check the gasket *layer* itself (before BLEND_ADD onto the card body) so
# the ceiling covers the gasket's own chrominance, not pre-existing card text or
# highlights that would trivially exceed it regardless of the gasket design.
try:
    import io
    from PIL import Image as _PIL

    buf = io.BytesIO()
    pygame.image.save(layer, buf, ".png")
    buf.seek(0)
    img  = _PIL.open(buf)
    flat = list(img.getdata())
    # Only sample pixels where the gasket painted something (alpha > 0).
    visible = [(r, g, b) for (r, g, b, a) in flat if a > 0]
    if visible:
        peak_r = max(px[0] for px in visible)
        peak_g = max(px[1] for px in visible)
        peak_b = max(px[2] for px in visible)
        peak   = (peak_r, peak_g, peak_b)
        print(f"gasket layer peak RGB (alpha>0 pixels): {peak}")
        # Art-director ceiling: R≤130, B≤190 (G is unrestricted — mint green lives at ~240).
        assert peak[0] <= 130 and peak[2] <= 190, f"peak exceeds ceiling: {peak}"
        print("  → within ceiling (R≤130, B≤190) ✓")
    else:
        print("gasket layer: no visible pixels found")
except Exception as e:
    print(f"PIL check: {e}")

# ── 1× inset strip (gasket judged at live 162×100) ───────────────────────────
ONE_W, ONE_H = sc.CARD_W, sc.CARD_H   # 162, 100

# ── Compose labeled review sheet ──────────────────────────────────────────────
BG    = (8, 8, 20)
PAD   = 20
GAP   = 16
HDR_H = 48
LBL_H = 34
SGAP  = 24     # gap between main panels and 1× strip
SLBL  = 28     # height of the strip's own label row

GREY = (170, 176, 190)
GOLD = (240, 205, 120)

sheet_w = PAD + 3 * PANEL_W + 2 * GAP + PAD
strip_y = PAD + HDR_H + LBL_H + PANEL_H + SGAP + SLBL
sheet_h = strip_y + ONE_H + PAD

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(30)
label_f = hud_font(20)
strip_f = hud_font(18)

title = title_f.render("equipped card — inner-gasket · skin_mummy · round 2", True, GOLD)
sheet.blit(title, (PAD, PAD + (HDR_H - title.get_height()) // 2))

panels = [
    (p1, "UNEQUIPPED",    GREY),
    (p2, "BASE EQUIPPED", GREY),
    (p3, "INNER-GASKET",  EQ_PIPE),
]
for i, (panel, label, col) in enumerate(panels):
    px  = PAD + i * (PANEL_W + GAP)
    ly  = PAD + HDR_H
    lbl = label_f.render(label, True, col)
    sheet.blit(lbl, (px + (PANEL_W - lbl.get_width()) // 2,
                     ly + (LBL_H - lbl.get_height()) // 2))
    sheet.blit(panel, (px, ly + LBL_H))

# 1× strip label
slbl = strip_f.render("1× final pixels  (162 × 100)", True, GREY)
sheet.blit(slbl, (PAD, strip_y - SLBL + (SLBL - slbl.get_height()) // 2))

for i, (panel, _, col) in enumerate(panels):
    small = pygame.transform.smoothscale(panel, (ONE_W, ONE_H))
    sx    = PAD + i * (PANEL_W + GAP) + (PANEL_W - ONE_W) // 2
    sheet.blit(small, (sx, strip_y))

out = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..",
    "docs", "store_equipped", "inner_gasket", "round_2.png"))
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
