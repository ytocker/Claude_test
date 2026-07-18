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
# ring alone must carry the read at thumbnail size; the prongs sell "set" by
# gripping over the dome edge. Everything below is tuned so a distinct gold
# halo survives the 162×100 downscale.
CX, CY = 162, 86          # dome centre on the SS panel
DR = 62                   # dome radius
# Thicker band than r1 (68/75) so it can't collapse to 1px at 1×.
RING_IN, RING_OUT = 66, 78

# 1) Warm outer aura — a warm-gold halo bleeding OUTWARD from the ring so the
#    setting separates from both the dark body and any busy sky behind it. Warm
#    (not white, not indigo), feathered over ~8–12px so no hard edge survives.
aura = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
AURA_OUT = RING_OUT + 12
for i in range(AURA_OUT, RING_OUT - 1, -1):
    t = (i - RING_OUT) / (AURA_OUT - RING_OUT)   # 0 at ring, 1 at far edge
    a = int(60 * (1 - t) ** 2)                    # warm falloff, softest outside
    if a <= 0:
        continue
    pygame.draw.circle(aura, (250, 200, 108, a), (CX, CY), i)
p2.blit(aura, (0, 0))

# 2) Collar ring — THE load-bearing signal. An annulus swept as fine wedge quads
#    so a single continuous angular gradient runs the lit top-left arc round to
#    the shaded bottom-right off ONE up-left key — a real turned-metal band.
#    The lit quarter is pushed to near-white gold so the ring is always brighter
#    than the dome cream interior; the equip read never depends on item colour.
LIT = (-0.7071, -0.7071)                      # up-left key (screen space)
BRIGHT = (255, 252, 235)                       # hotter than dome cream (248,238,210)
MID = (232, 176, 96)
SHADE = (150, 80, 20)
step = math.radians(3)
phi = 0.0
while phi < 2 * math.pi - 1e-6:
    a0, a1 = phi, phi + step
    mid = phi + step / 2
    d = math.cos(mid) * LIT[0] + math.sin(mid) * LIT[1]
    f = (d + 1) / 2
    # Two-stop ramp so the lit quarter reaches near-white while the body of the
    # band still shows warm gold rather than washing out everywhere.
    if f > 0.5:
        col = sc.lerp_color(MID, BRIGHT, (f - 0.5) * 2)
    else:
        col = sc.lerp_color(SHADE, MID, f * 2)
    quad = [
        (CX + RING_IN * math.cos(a0), CY + RING_IN * math.sin(a0)),
        (CX + RING_OUT * math.cos(a0), CY + RING_OUT * math.sin(a0)),
        (CX + RING_OUT * math.cos(a1), CY + RING_OUT * math.sin(a1)),
        (CX + RING_IN * math.cos(a1), CY + RING_IN * math.sin(a1)),
    ]
    pygame.draw.polygon(p2, col, quad)
    phi += step

# 1) Hard inner-edge contour — a continuous deep-gold channel at the ring's
#    inner edge all the way around, so the band never fuses with the warm dome
#    glass inside it. ~4px at SS=2, drawn as a filled annulus band.
CONTOUR = (58, 48, 22)
cw = 4                                          # ~4px at SS=2
phi = 0.0
while phi < 2 * math.pi - 1e-6:
    a0, a1 = phi, phi + step
    quad = [
        (CX + RING_IN * math.cos(a0), CY + RING_IN * math.sin(a0)),
        (CX + (RING_IN + cw) * math.cos(a0), CY + (RING_IN + cw) * math.sin(a0)),
        (CX + (RING_IN + cw) * math.cos(a1), CY + (RING_IN + cw) * math.sin(a1)),
        (CX + RING_IN * math.cos(a1), CY + RING_IN * math.sin(a1)),
    ]
    pygame.draw.polygon(p2, CONTOUR, quad)
    phi += step

# dark contact keyline on the outer edge so the band separates from the body
pygame.draw.circle(p2, (70, 42, 10), (CX, CY), RING_OUT, max(1, sc.m(0.8)))
# pale glint on the lit top-left edge — the polished lip catching the key
glint = pygame.Rect(CX - (RING_IN + cw), CY - (RING_IN + cw),
                    (RING_IN + cw) * 2, (RING_IN + cw) * 2)
pygame.draw.arc(p2, (255, 250, 230), glint,
                math.radians(95), math.radians(185), max(1, sc.m(0.8)))

# 3) Prongs — 4 claws gripping the setting. Each reads as a tab that OVERLAPS
#    onto the dome edge (tip bites well inside DR), which is what sells
#    "set/equipped" over an ornamental frame. Lit claws on the up-left arc.
PRONG_BRIGHT = (255, 244, 200)
PRONG_DARK = (150, 96, 30)
# (math-convention angle, is-lit) — up is 90°, matching the up-left key. Four
# clearly-spaced claws so at true 1× they resolve as discrete grips.
PRONGS = [(120, True), (200, True), (30, False), (300, False)]
HALFW = 6
GRIP = DR - 6                                   # tip overlaps onto the dome face
for deg, lit in PRONGS:
    A = math.radians(deg)
    ux, uy = math.cos(A), -math.sin(A)          # outward (math space, y flipped)
    tx, ty = -uy, ux                            # tangent
    br = RING_OUT + 2                            # base just outside the band
    base0 = (CX + br * ux + HALFW * tx, CY + br * uy + HALFW * ty)
    base1 = (CX + br * ux - HALFW * tx, CY + br * uy - HALFW * ty)
    # narrow the tab as it reaches in so it reads as a tapered claw over the dome
    tip0 = (CX + GRIP * ux + (HALFW * 0.5) * tx, CY + GRIP * uy + (HALFW * 0.5) * ty)
    tip1 = (CX + GRIP * ux - (HALFW * 0.5) * tx, CY + GRIP * uy - (HALFW * 0.5) * ty)
    pygame.draw.polygon(p2, PRONG_BRIGHT if lit else PRONG_DARK,
                        [base0, base1, tip1, tip0])
    # dark seat around the claw so it reads as a discrete gripping piece
    pygame.draw.polygon(p2, (54, 34, 12), [base0, base1, tip1, tip0], max(1, sc.m(0.6)))
    # hot specular pip at the gripping tip
    tipc = (CX + GRIP * ux, CY + GRIP * uy)
    pygame.draw.circle(p2, (255, 252, 232),
                       (int(round(tipc[0])), int(round(tipc[1]))), max(1, sc.m(1.0)))


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


_text(sheet, "equipped v3 — claw-setting · skin_mummy · round 2", title_f,
      (sheet_w // 2, 34), (245, 240, 250))
_text(sheet, "thicker gold collar, hard inner contour, warm outer aura, dome-gripping claws",
      slbl_f, (sheet_w // 2, 68), (170, 168, 190))

for i, (p, lab) in enumerate(zip(panels, labels)):
    x = PAD + i * (PANEL_W + GAP)
    sheet.blit(p, (x, panel_y))
    _text(sheet, lab, lbl_f, (x + PANEL_W // 2, panel_y + PANEL_H + LBL_H // 2),
          (210, 210, 225))

# 1× strip — smoothscale each SS panel to the true 162×100 card, then show at ×2
# so reviewers judge whether the collar ring survives at live thumbnail scale.
y_strip = panel_y + PANEL_H + LBL_H + SGAP + SLBL_H
_text(sheet, "at live 1× resolution (162×100, shown ×2) — primary judging surface", slbl_f,
      (sheet_w // 2, y_strip - SLBL_H // 2), (150, 150, 170))
for i, p in enumerate(panels):
    x = PAD + i * (PANEL_W + GAP)
    small = pygame.transform.smoothscale(p, (sc.CARD_W, sc.CARD_H))
    shown = pygame.transform.scale(small, (PANEL_W, strip_h))
    sheet.blit(shown, (x, y_strip))

out = os.path.join(os.path.dirname(__file__), "..",
                   "docs", "store_equipped_v3", "claw_setting", "round_2.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print(f"saved {out}  ({sheet_w}x{sheet_h})")
