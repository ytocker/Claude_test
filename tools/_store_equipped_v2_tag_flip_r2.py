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
# owned face. An OPEN padlock (keyhole cut as cream negative space + a lifted
# shackle leg) reads as "unlocked / yours" where the price used to be.
TAG_W, TAG_H = sc._TAG_W, sc._TAG_H  # 81, 94 at SS=2
TAG_TILT = sc._TAG_TILT              # -7

face = pygame.Surface((TAG_W, TAG_H), pygame.SRCALPHA)
FACE_RAD = sc.m(3)                    # 6 — matches the price-chip swing-tag

# Warm cream owned face: brighter + warmer than the for-sale tag so the flip
# reads at a glance.
cream = sc.vgrad_stops(TAG_W, TAG_H, FACE_RAD,
                       [(0.0, (252, 247, 232)), (1.0, (236, 224, 197))],
                       255, gamma=1.03)
face.blit(cream, (0, 0))

INK = (26, 28, 66)                    # deep indigo shackle ink
GOLD_RIM = (236, 202, 116)

# ── Padlock geometry — centred on the tag's optical centre, ~57% of the face
# width so the glyph carries at true 1× (~8px). ─────────────────────────────
bw, bh, brad = 46, 32, 7
bx, by = (TAG_W - bw) // 2, 48        # body spans x17..63, y48..80
kx = bw // 2                          # keyhole on the body centreline

# Shackle stamped as an OPEN U: a rigid U rotated about its right (seated) leg
# base so the LEFT leg lifts clear of the body — the "unlocked" tell. Drawn
# BEFORE the body so the right leg seats into it and only the open arch shows.
hinge = (bx + bw // 2 + 13, by + 2)   # right leg base, 2px into the body top
Lh, R, TH = 15, 13, 8
ang = math.radians(24)
ca, sa = math.cos(ang), math.sin(ang)


def _place(x, y):
    return (hinge[0] + (x * ca - y * sa), hinge[1] + (x * sa + y * ca))


_pts = []
for i in range(9):                    # right leg up
    _pts.append((0.0, -Lh * i / 8))
for i in range(19):                   # arch over the top
    phi = math.pi * i / 18
    _pts.append((-R + R * math.cos(phi), -Lh - R * math.sin(phi)))
for i in range(9):                    # left (lifted) leg down
    _pts.append((-2 * R, -Lh + Lh * i / 8))

for (x, y) in _pts:
    px, py = _place(x, y)
    pygame.draw.circle(face, INK, (int(round(px)), int(round(py))), TH // 2)

# Contact shadow so the padlock body sits ON the cream rather than floating.
_sh = pygame.Surface((bw, bh), pygame.SRCALPHA)
pygame.draw.rect(_sh, (0, 0, 0, 60), (0, 0, bw, bh), border_radius=brad)
face.blit(_sh, (bx + 1, by + 2))

# Padlock BODY: the store-card indigo gradient (28,30,70)→(12,13,38) so the
# owned face speaks the store's art language. The keyhole is a CREAM circle +
# tapered slot punched as transparent negative space — the warm face reads
# straight through it, which is the most legible small-scale "lock".
bsurf = pygame.Surface((bw, bh), pygame.SRCALPHA)
bsurf.blit(sc.vgrad_stops(bw, bh, brad,
                          [(0.0, (28, 30, 70)), (1.0, (12, 13, 38))],
                          255, gamma=1.06), (0, 0))
pygame.draw.line(bsurf, (58, 60, 110), (brad, 2), (bw - brad, 2), 1)  # bevel kiss
pygame.draw.rect(bsurf, (8, 9, 24), (0, 0, bw, bh), 1, border_radius=brad)
pygame.draw.circle(bsurf, (0, 0, 0, 0), (kx, 12), 5)
pygame.draw.polygon(bsurf, (0, 0, 0, 0),
                    [(kx - 3, 12), (kx + 3, 12), (kx + 2, 25), (kx - 2, 25)])
face.blit(bsurf, (bx, by))

# Gold rim around the whole silhouette.
pygame.draw.rect(face, GOLD_RIM, (0, 0, TAG_W, TAG_H), 1, border_radius=FACE_RAD)

# Grommet eyelet (verbatim placement from price_chip).
GROMMET = (30, 13)
pygame.draw.circle(face, (0, 0, 0, 0), GROMMET, sc.m(5))
pygame.draw.circle(face, GOLD_RIM, GROMMET, sc.m(5) + 1, width=max(1, sc.m(1)))

# Die-cut corner notch on the lower-outer corner — punched AFTER the rim so the
# straight corner rim is removed, then the diagonal gets its own dark inner
# shadow + carried gold rim so it reads as an intentional cut, crisp against the
# dark card body.
NOTCH = 16
a_pt = (TAG_W - NOTCH, TAG_H)          # (65, 94)
b_pt = (TAG_W, TAG_H - NOTCH)          # (81, 78)
pygame.draw.polygon(face, (0, 0, 0, 0), [a_pt, b_pt, (TAG_W, TAG_H)])
pygame.draw.line(face, (150, 112, 44),
                 (a_pt[0] - 1, a_pt[1] - 1), (b_pt[0] - 1, b_pt[1] - 1), 1)
pygame.draw.line(face, GOLD_RIM, a_pt, b_pt, 1)

# ── Hang the tag: cord + knot lifted VERBATIM from price_chip, with a 1px dark
# drop-shadow under the cord so it holds contrast where it crosses the warm
# face. ─────────────────────────────────────────────────────────────────────
rot = pygame.transform.rotate(face, TAG_TILT)
TAG_CENTER = (44, 60)
KNOT = (22, 13)
cord = (190, 165, 115)
gx, gy = sc._tag_rot_point(*GROMMET, TAG_CENTER)
lw = sc.m(1.5)
cshadow = (78, 58, 30)
pygame.draw.line(p2, cshadow, (gx + 1, gy + 1),
                 (KNOT[0] - 1 + 1, KNOT[1] - 1 + 1), lw)
pygame.draw.line(p2, cshadow, (gx + 1, gy + 1),
                 (KNOT[0] + 2 + 1, KNOT[1] + 2 + 1), lw)
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


_text(sheet, "equipped v2 — tag-flip · skin_mummy · r2", title_f,
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
                   "docs", "store_equipped_v2", "tag_flip", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {out}  ({sheet_w}x{sheet_h})")
