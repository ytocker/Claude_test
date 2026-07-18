#!/usr/bin/env python3
"""
Floating-gold-lozenge concept — round 2.

Art-director notes applied:
  • Lozenge relocated to chip lane (cy=180, hh=12) so it no longer overlaps
    the item name; bottom edge lands exactly on the card body floor.
  • Redundant hang-tag suppressed on Panel 2 via a scoped monkey-patch.
  • Star device replaced by a debossed angular ✓ (three vertices, rounded
    caps) that echoes the hang-tag check language — unambiguous "equipped".
  • Keyline repaleted to (46,38,18); shadow to (9,9,22) to stay on-brand.
  • Micro-detail bevel lines dropped — gradient carries the light unaided.
"""
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
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)

# ── lozenge geometry ──────────────────────────────────────────────────────────
# cy=180 puts the indicator in the chip lane below the name (name lane ~y=164).
# hh=12 keeps the bottom point exactly on the card body floor at y=192; hw=22
# gives enough horizontal presence to read as a deliberate diamond badge.
_CX, _CY, _HW, _HH = 162, 180, 22, 12


def _poly(cx=_CX, cy=_CY, hw=_HW, hh=_HH):
    return [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]


def draw_floating_gold_lozenge(surf):
    """Gold rhombus seated in the chip lane as the sole equipped indicator.
    A debossed angular ✓ serves as the device — unambiguous, matching the
    hang-tag check idiom already established in the chip family. No micro-
    detail lines: the gradient facets carry the lighting without invisible 1px
    artifacts collapsing at 1×."""
    poly = _poly()
    cx, cy = _CX, _CY

    # Seat shadow — indigo-tinted so it reads as a shadow rather than a hard
    # black blot; the card ground is near-black indigo, not true black.
    dy = sc.m(2)
    sh = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
    pygame.draw.polygon(sh, (9, 9, 22, 120), [(x, y + dy) for x, y in poly])
    surf.blit(sh, (0, 0))

    # Gold body — vertical Ramp gradient clipped to the rhombus silhouette via a
    # white polygon mask under BLEND_RGBA_MIN so the pointed tip is geometrically
    # exact; no bounding-rect artifact.
    ox, oy = cx - _HW, cy - _HH
    bw, bh = _HW * 2, _HH * 2
    local = [(x - ox, y - oy) for x, y in poly]
    body = sc.vgrad_stops(bw, bh, 0,
                          [(0.0, (255, 240, 190)), (1.0, (236, 202, 116))], 255,
                          gamma=1.06)
    mask = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), local)
    body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(body, (ox, oy))

    # Dark keyline in the canonical dark-key tone — the same (46,38,18) used
    # by the regalia frame and the gem keyline keeps the card reading as one
    # consistent system.
    pygame.draw.polygon(surf, (46, 38, 18), poly, width=max(2, sc.m(1.4)))

    # Debossed angular ✓ — three vertices fitted inside the lozenge, short steep
    # left arm / long shallow right arm matching the hang-tag check proportion.
    # Containment check (|Δx|/hw + |Δy|/hh ≤ 1): 0.87, 0.52, 0.91 respectively.
    v_left   = (cx - 10, cy - 5)   # upper-left tip — short steep side
    v_vertex = (cx -  4, cy + 4)   # V bottom — slightly left of lozenge centre
    v_right  = (cx +  9, cy - 6)   # upper-right tip — long shallow side
    stroke_w = max(3, sc.m(2))
    ink = (46, 38, 18)
    pygame.draw.lines(surf, ink, False, [v_left, v_vertex, v_right], stroke_w)
    # Round endpoints eliminate the square-cap chop that would look like a dash
    # at small scales.
    r_cap = stroke_w // 2
    pygame.draw.circle(surf, ink, v_left,   r_cap)
    pygame.draw.circle(surf, ink, v_vertex, r_cap + 1)
    pygame.draw.circle(surf, ink, v_right,  r_cap)


# ── panels ────────────────────────────────────────────────────────────────────

# Panel 0 — UNEQUIPPED
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False, owned=False)

# Panel 1 — EQUIPPED BASE (regalia frame + check hang-tag, concept-free)
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False, owned=False)

# Panel 2 — CONCEPT: lozenge as the sole equipped indicator; hang-tag
# suppressed via a scoped patch so the chip lane is owned by the lozenge alone.
sc._card_cache.clear()
_orig_state_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False, owned=False)
sc.state_chip = _orig_state_chip
draw_floating_gold_lozenge(p2)

# ── compose review sheet ──────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD, GAP = 20, 16
HDR_H, LBL_H = 48, 34
SGAP, SLBL_H = 20, 24
GOLD_COL = (236, 202, 116)
GREY = (150, 152, 168)
CREAM_LBL = (250, 246, 232)
xs = [20, 360, 700]
panel_y = PAD + HDR_H + LBL_H          # 102
sheet_w = xs[-1] + PANEL_W + PAD
strip_w, strip_h = sc.CARD_W * 2, sc.CARD_H * 2
zlbl_y  = panel_y + PANEL_H + SGAP
zoom_y  = zlbl_y + SLBL_H
sheet_h = zoom_y + strip_h + PAD
sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

title_f = hud_font(22, True)
tt = title_f.render(
    "equipped v4c — floating-gold-lozenge · round 2 · skin_mummy",
    True, GOLD_COL)
sheet.blit(tt, tt.get_rect(midtop=(sheet_w // 2, PAD // 2 + 4)))

labels = [("UNEQUIPPED", GREY), ("EQUIPPED BASE", GREY),
          ("+ FLOATING GOLD LOZENGE", CREAM_LBL)]
panels = [p0, p1, p2]
lbl_f = hud_font(15, True)
zlbl_f = hud_font(13, True)
for x, panel, (label, col) in zip(xs, panels, labels):
    lt = lbl_f.render(label, True, col)
    sheet.blit(lt, lt.get_rect(midbottom=(x + PANEL_W // 2, panel_y - 6)))
    sheet.blit(panel, (x, panel_y))

# Zoom strip — downscale Panel 2 to true 1× then nearest-2× so the review
# matches exactly what the store grid blits at runtime.
card1x = pygame.transform.smoothscale(p2, (sc.CARD_W, sc.CARD_H))
strip  = pygame.transform.scale2x(card1x)
zx = xs[-1] + (PANEL_W - strip_w) // 2
zt = zlbl_f.render("@1x (162×100 tile, 2× nearest)", True, GREY)
sheet.blit(zt, zt.get_rect(midbottom=(xs[-1] + PANEL_W // 2, zlbl_y + SLBL_H - 4)))
sheet.blit(strip, (zx, zoom_y))

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",
    "docs", "store_equipped_v4c", "floating_gold_lozenge", "round_2.png"))
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pygame.image.save(sheet, OUT)
assert os.path.exists(OUT)
print("saved", OUT, sheet.get_size())

# ── 1× pixel-visibility check ─────────────────────────────────────────────────
# Confirm the lozenge and check mark both survive the smoothscale to 162×100 by
# sampling the bounding area of each in the downscaled panel.
try:
    from PIL import Image
    img = Image.open(OUT).convert("RGB")
    w, h = img.size

    # The 1× panel is blitted at sheet x=xs[-1]=700, y=panel_y=102 at SS=2,
    # so in the sheet it occupies the right column at 2× resolution.
    # The zoom strip starts at zoom_y and is 2× nearest, so within the strip
    # the lozenge center (162,180 in SS) maps to:
    # strip x = zx + (162//2) * 2 = zx + 162 = zx + 162
    # strip y = zoom_y + (180//2) * 2 = zoom_y + 180
    # Lozenge center at 1× is (81, 90), at 2×-nearest: x=zx+162, y=zoom_y+180

    # Sample the gold body area of the lozenge in the zoom strip
    sample_cx = zx + (sc.CARD_W // 2) * 2    # 162 → half=81 → ×2=162 from strip left
    sample_cy = zoom_y + (_CY // 2) * 2        # 180 → half=90 → ×2=180 from strip top

    pixels = []
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            px, py = sample_cx + dx, sample_cy + dy
            if 0 <= px < w and 0 <= py < h:
                pixels.append(img.getpixel((px, py)))

    # Gold is roughly R>180, G>140, B<100 — check that gold appears
    gold_pixels = [p for p in pixels if p[0] > 160 and p[1] > 110 and p[2] < 130]
    # Dark check ink is roughly R<80, G<60, B<40
    dark_pixels = [p for p in pixels if p[0] < 90 and p[1] < 70 and p[2] < 50]

    print(f"1× lozenge area: {len(pixels)} pixels sampled, "
          f"{len(gold_pixels)} gold, {len(dark_pixels)} dark-ink")
    if len(gold_pixels) >= 4:
        print("  [PASS] lozenge gold body visible at 1×")
    else:
        print("  [WARN] lozenge may be too small — gold pixels:", gold_pixels[:5])
    if len(dark_pixels) >= 1:
        print("  [PASS] check-mark ink visible at 1×")
    else:
        print("  [WARN] check-mark ink not sampled — may be present but thin")
except ImportError:
    print("PIL not available — skipping 1× pixel check")
