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

# ── Panel 2 — CONCEPT EQUIPPED (suppress the stock chip; set the portrait) ───
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
p2 = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(p2, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()


# ── Claw-setting overlay (SS=2, coords already in device px) ─────────────────
# The equip signal is a bright-gold COLLAR RING clasped around the dome so the
# character portrait reads as a gemstone "set" in a jeweller's mounting. The
# ring alone must carry the read at thumbnail size; the prongs are texture.
CX, CY = 162, 86          # dome centre on the SS panel
DR = 62                   # dome radius
RING_IN, RING_OUT = 68, 75

# 1) Warm aura — a soft feathered glow behind the mount so the setting sits in a
#    pool of warm light. Feathered (not a hard disc) so no ring edge survives
#    the downscale.
aura = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
AURA_R = 80
for i in range(AURA_R, 0, -2):
    a = int(22 * (1 - (i - 1) / AURA_R) ** 1.5)
    if a <= 0:
        continue
    pygame.draw.circle(aura, (246, 206, 120, a), (CX, CY), i)
p2.blit(aura, (0, 0))

# 2) Collar ring — THE load-bearing signal. An annulus swept as fine wedge quads
#    so a single continuous angular gradient runs the lit top-left arc
#    (255,238,180) round to the shaded bottom-right (150,80,20) off ONE up-left
#    key — a real turned-metal band, never a flat stroke.
LIT = (-0.7071, -0.7071)                      # up-left key (screen space)
BRIGHT = (255, 238, 180)
SHADE = (150, 80, 20)
step = math.radians(3)
phi = 0.0
while phi < 2 * math.pi - 1e-6:
    a0, a1 = phi, phi + step
    mid = phi + step / 2
    d = math.cos(mid) * LIT[0] + math.sin(mid) * LIT[1]
    f = (d + 1) / 2
    col = sc.lerp_color(SHADE, BRIGHT, f)
    quad = [
        (CX + RING_IN * math.cos(a0), CY + RING_IN * math.sin(a0)),
        (CX + RING_OUT * math.cos(a0), CY + RING_OUT * math.sin(a0)),
        (CX + RING_OUT * math.cos(a1), CY + RING_OUT * math.sin(a1)),
        (CX + RING_IN * math.cos(a1), CY + RING_IN * math.sin(a1)),
    ]
    pygame.draw.polygon(p2, col, quad)
    phi += step

# dark contact keyline on the outer edge so the band separates from the body
pygame.draw.circle(p2, (70, 42, 10), (CX, CY), RING_OUT, max(1, sc.m(0.6)))
# pale glint on the inner top-left edge — the polished lip catching the key
glint = pygame.Rect(CX - RING_IN, CY - RING_IN, RING_IN * 2, RING_IN * 2)
pygame.draw.arc(p2, (255, 246, 214), glint,
                math.radians(95), math.radians(185), max(1, sc.m(0.6)))

# 3) Prongs — 5 claws gripping the setting. Texture only: they add jeweller
#    detail but never carry the read. Lit claws on the up-left arc, shaded on the
#    rest, each tipped with a hot specular pip.
PRONG_BRIGHT = (252, 224, 150)
PRONG_DARK = (150, 96, 30)
# (math-convention angle, is-lit) — up is 90°, matching the up-left key
PRONGS = [(90, True), (135, True), (180, True), (45, False), (270, False)]
HALFW = 5
for deg, lit in PRONGS:
    A = math.radians(deg)
    ux, uy = math.cos(A), -math.sin(A)          # outward (math space, y flipped)
    tx, ty = -uy, ux                            # tangent
    br, tr = RING_OUT + 2, RING_IN - 2          # base outside, tip biting inward
    base0 = (CX + br * ux + HALFW * tx, CY + br * uy + HALFW * ty)
    base1 = (CX + br * ux - HALFW * tx, CY + br * uy - HALFW * ty)
    tip = (CX + tr * ux, CY + tr * uy)
    pygame.draw.polygon(p2, PRONG_BRIGHT if lit else PRONG_DARK,
                        [base0, base1, tip])
    # 1px dark seat so the claw reads as a discrete piece, not a smear
    pygame.draw.polygon(p2, (60, 34, 8), [base0, base1, tip], max(1, sc.m(0.5)))
    # hot specular pip at the gripping tip
    pygame.draw.circle(p2, (255, 250, 228), (int(round(tip[0])), int(round(tip[1]))),
                       max(1, sc.m(0.9)))


# ── Sheet layout ────────────────────────────────────────────────────────────
BG = (14, 15, 28)
PAD = 20
GAP = 16
panel_y = 102
LBL_H = 34
SGAP = 20
SLBL_H = 24
N = 3

panels = [p0, p1, p2]
labels = ["UNEQUIPPED", "STOCK EQUIPPED", "CLAW SETTING"]

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
strip_h = PANEL_H                       # 1× card shown pixel-doubled (324×200)
sheet_h = panel_y + PANEL_H + LBL_H + SGAP + SLBL_H + strip_h + PAD

sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill(BG)

title_f = hud_font(26)
lbl_f = hud_font(18)
slbl_f = hud_font(14)


def _text(surf, text, f, center, col):
    g = f.render(text, True, col)
    surf.blit(g, g.get_rect(center=center))


_text(sheet, "equipped v3 — claw-setting · skin_mummy", title_f,
      (sheet_w // 2, 34), (245, 240, 250))
_text(sheet, "bright-gold collar ring sets the portrait in a gemstone mounting",
      slbl_f, (sheet_w // 2, 68), (170, 168, 190))

for i, (p, lab) in enumerate(zip(panels, labels)):
    x = PAD + i * (PANEL_W + GAP)
    sheet.blit(p, (x, panel_y))
    _text(sheet, lab, lbl_f, (x + PANEL_W // 2, panel_y + PANEL_H + LBL_H // 2),
          (210, 210, 225))

# 1× strip — smoothscale each SS panel to the true 162×100 card, then show at ×2
# so reviewers judge whether the collar ring survives at live thumbnail scale.
y_strip = panel_y + PANEL_H + LBL_H + SGAP + SLBL_H
_text(sheet, "at live 1× resolution (162×100, shown ×2)", slbl_f,
      (sheet_w // 2, y_strip - SLBL_H // 2), (150, 150, 170))
for i, p in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    small = pygame.transform.smoothscale(p, (sc.CARD_W, sc.CARD_H))
    shown = pygame.transform.scale(small, (PANEL_W, strip_h))
    sheet.blit(shown, (x, y_strip))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v3", "claw_setting", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {out}  ({sheet_w}x{sheet_h})")
