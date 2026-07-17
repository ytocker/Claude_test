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

# ── Panel 2 — CONCEPT EQUIPPED (suppress chip, draw our owned tag) ───────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()

# The receipt is still here — now it's mine: the same swing-tag, flipped to its
# owned face (warmer cream, corner notch, bold padlock) hanging on the same cord.
TAG_W, TAG_H = sc._TAG_W, sc._TAG_H  # 81, 94 at SS=2
TAG_TILT = sc._TAG_TILT              # -7

face = pygame.Surface((TAG_W, TAG_H), pygame.SRCALPHA)
FACE_COL = (250, 248, 240)   # owned face: noticeably warmer/brighter
face.fill(FACE_COL)

# Corner notch clips the lower-outer corner so the owned silhouette differs
# from the for-sale price tag at a glance.
NOTCH = 14
notch_pts = [(TAG_W - NOTCH, TAG_H), (TAG_W, TAG_H - NOTCH), (TAG_W, TAG_H)]
pygame.draw.polygon(face, (0, 0, 0, 0), notch_pts)

GOLD_RIM = (236, 202, 116)
pygame.draw.rect(face, GOLD_RIM, (0, 0, TAG_W, TAG_H), 1, border_radius=3)

# Bold padlock glyph in deep indigo ink.
INK = (28, 30, 70)
cx_tag = TAG_W // 2
cy_tag = int(TAG_H * 0.52)

body_w, body_h = 24, 18
body_r = pygame.Rect(cx_tag - body_w // 2, cy_tag - body_h // 2, body_w, body_h)
pygame.draw.rect(face, INK, body_r, border_radius=3)

# Open shackle above the body — an unlatched U reads as "yours / accessible".
sh_r = 10
sh_cx = cx_tag
sh_ty = cy_tag - body_h // 2 - sh_r * 2 + 2
shackle_rect = pygame.Rect(sh_cx - sh_r, sh_ty, sh_r * 2, sh_r * 2)
pygame.draw.arc(face, INK, shackle_rect, math.radians(0), math.radians(180), 5)
pygame.draw.line(face, INK, (sh_cx - sh_r, sh_ty + sh_r),
                 (sh_cx - sh_r, cy_tag - body_h // 2), 5)
pygame.draw.line(face, INK, (sh_cx + sh_r, sh_ty + sh_r),
                 (sh_cx + sh_r, cy_tag - body_h // 2 + 4), 5)

GROMMET = (30, 13)
pygame.draw.circle(face, (0, 0, 0, 0), GROMMET, sc.m(5))
pygame.draw.circle(face, GOLD_RIM, GROMMET, sc.m(5) + 1, width=max(1, sc.m(1)))

rot = pygame.transform.rotate(face, TAG_TILT)
TAG_CENTER = (44, 60)
KNOT = (22, 13)

# Cord+knot lifted verbatim from price_chip so the tag hangs identically.
cord = (190, 165, 115)
gx, gy = sc._tag_rot_point(*GROMMET, TAG_CENTER)
lw = sc.m(1.5)
pygame.draw.line(p2, cord, (gx, gy), (KNOT[0] - 1, KNOT[1] - 1), lw)
pygame.draw.line(p2, cord, (gx, gy), (KNOT[0] + 2, KNOT[1] + 2), lw)
p2.blit(rot, rot.get_rect(center=TAG_CENTER))
pygame.draw.circle(p2, cord, KNOT, sc.m(1.5))
pygame.draw.circle(p2, (min(cord[0] + 30, 255), min(cord[1] + 30, 255),
                        min(cord[2] + 30, 255)), KNOT, max(1, sc.m(0.6)))


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
labels = ["UNEQUIPPED", "STOCK EQUIPPED", "TAG FLIP"]

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


_text(sheet, "equipped v2 — tag-flip · skin_mummy", title_f,
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
                   "docs", "store_equipped_v2", "tag_flip", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {out}  ({sheet_w}x{sheet_h})")
