import os, sys, math

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


# ── Panel 0 — UNEQUIPPED ────────────────────────────────────────────────────
sc._card_cache.clear()
p0 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p0, SID, rect, equipped=False, secret=False)

# ── Panel 1 — STOCK EQUIPPED ────────────────────────────────────────────────
sc._card_cache.clear()
p1 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p1, SID, rect, equipped=True, secret=False)

# ── Panel 2 — CONCEPT EQUIPPED (suppress the stock chip; strike our seal) ────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()


# ── Collector seal — a RAISED gold-wax medallion planted upper-left ──────────
# Positive relief is the whole read: the disc catches an upper-left key so the
# scalloped rim and struck star sit PROUD of the card, the raised-vs-pressed
# counterpart to emboss-brand.
SX, SY = 44, 50          # SS=2 coords — upper-left quadrant
R = 44                   # outer radius (SS=2 => 22px at 1×)


def _star_pts(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    """5-point star polygon: alternating outer/inner radii, first point up."""
    pts = []
    for i in range(n * 2):
        rr = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


# 1) Drop shadow on its own SRCALPHA layer so the soft dark ground beneath the
#    disc sells the lift without darkening the whole card.
shadow = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.circle(shadow, (4, 4, 16, 140), (SX + 3, SY + 3), R + 2)
p2.blit(shadow, (0, 0))

# 2) Base amber disc
pygame.draw.circle(p2, (208, 164, 92), (SX, SY), R)

# 3) Scalloped rim — 16 rounded teeth ringing the perimeter so the silhouette
#    reads as a wax seal, not a plain coin.
N_TEETH = 16
for i in range(N_TEETH):
    ang = i * 2 * math.pi / N_TEETH
    ox = SX + R * math.cos(ang)
    oy = SY + R * math.sin(ang)
    pygame.draw.circle(p2, (180, 138, 70), (int(round(ox)), int(round(oy))), 3)
# redraw the base fill one notch in so teeth read as OUTWARD bumps on the disc
pygame.draw.circle(p2, (208, 164, 92), (SX, SY), R - 3)

# 4) Bevel lighting (key from upper-left) — a lit arc up-left, a shadowed arc
#    down-right, and a hot specular catch make the disc dome toward the viewer.
bevel = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
lit_rect = pygame.Rect(SX - (R - 3), SY - (R - 3), (R - 3) * 2, (R - 3) * 2)
pygame.draw.arc(bevel, (236, 202, 116, 230), lit_rect,
                math.radians(135), math.radians(315), 4)
pygame.draw.arc(bevel, (58, 48, 22, 200), lit_rect,
                math.radians(315), math.radians(360 + 135), 4)
p2.blit(bevel, (0, 0))
spec = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.circle(spec, (250, 245, 220, 200),
                   (SX - int(R * 0.6), SY - int(R * 0.6)), 5)
p2.blit(spec, (0, 0))

# 5) Inner disc face — a hair darker than the rim so the raised rim casts an
#    inward step and the center reads recessed enough to hold the struck glyph.
pygame.draw.circle(p2, (188, 146, 78), (SX, SY), R - 8)

# 6) Struck center star — cast amber (struck-IN, not painted-on) with a micro
#    bevel: a pale up-left ghost + a dark down-right ghost make it look impressed.
star_out, star_in = 18, 9
micro_up = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.polygon(micro_up, (220, 190, 130, 120),
                    _star_pts(SX - 1, SY - 1, star_out, star_in))
p2.blit(micro_up, (0, 0))
micro_dn = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
pygame.draw.polygon(micro_dn, (40, 28, 10, 120),
                    _star_pts(SX + 1, SY + 1, star_out, star_in))
p2.blit(micro_dn, (0, 0))
pygame.draw.polygon(p2, (128, 96, 46), _star_pts(SX, SY, star_out, star_in))


# ── Sheet layout ────────────────────────────────────────────────────────────
BG = (8, 8, 20)
PAD = 20
GAP = 16
HDR_H = 48
LBL_H = 34
SGAP = 20
SLBL_H = 24
N = 3

panels = [p0, p1, p2]
labels = ["UNEQUIPPED", "STOCK EQUIPPED", "COLLECTOR SEAL"]

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
strip_h = PANEL_H // 2  # 1x strip renders at half panel height
sheet_h = (HDR_H + PANEL_H + LBL_H + SGAP + SLBL_H + strip_h + PAD)

sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill(BG)

title_f = hud_font(26)
lbl_f = hud_font(18)
slbl_f = hud_font(14)


def _text(surf, text, f, center, col):
    g = f.render(text, True, col)
    surf.blit(g, g.get_rect(center=center))


_text(sheet, "equipped v2 — collector-seal · skin_mummy", title_f,
      (sheet_w // 2, HDR_H // 2), (245, 240, 250))

y_panel = HDR_H
for i, (p, lab) in enumerate(zip(panels, labels)):
    x = PAD + i * (PANEL_W + GAP)
    sheet.blit(p, (x, y_panel))
    _text(sheet, lab, lbl_f, (x + PANEL_W // 2, y_panel + PANEL_H + LBL_H // 2),
          (210, 210, 225))

# 1x strip — downscale to true grid size (162×100), then upscale so reviewers see
# how the concept reads at live resolution beside the 2x author panels.
y_strip = y_panel + PANEL_H + LBL_H + SGAP + SLBL_H
_text(sheet, "at live 1x resolution (downscaled then shown 2x)", slbl_f,
      (sheet_w // 2, y_strip - SLBL_H // 2), (150, 150, 170))
for i, p in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    small = pygame.transform.smoothscale(p, (sc.CARD_W, sc.CARD_H))
    shown = pygame.transform.scale(small, (PANEL_W, strip_h))
    sheet.blit(shown, (x, y_strip))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v2", "collector_seal", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {out}  ({sheet_w}x{sheet_h})")
