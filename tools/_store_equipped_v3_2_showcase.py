"""Phase 5 showcase: equipped state v3.2 — BEFORE (regalia frame only) + 5 checkmark variants."""
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
PANEL_W, PANEL_H = sc.CARD_W * sc.SS, sc.CARD_H * sc.SS   # 324×200
ri = sc.m(sc._INSET)
rect = pygame.Rect(ri, ri, PANEL_W - 2 * ri, PANEL_H - 2 * ri)
rad = sc.m(sc.CARD_RAD)

BG = (8, 8, 20)


def draw_regalia_frame(surf, body):
    OUTER = (236, 202, 116)
    VALLEY = (9, 9, 22)
    INNER = (255, 240, 190)
    KEY = (46, 38, 18)
    GLINT = (255, 248, 224)

    def bead(inset, w, col):
        r = body.inflate(-2 * inset, -2 * inset)
        s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(s, (*col, 255), r, width=w,
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


# ── BEFORE panel: regalia frame only ─────────────────────────────────────────
orig_chip = sc.state_chip
sc.state_chip = lambda *a, **kw: None
sc._card_cache.clear()
before_card = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
sc.draw_card(before_card, SID, rect, equipped=True, secret=False)
sc.state_chip = orig_chip
sc._card_cache.clear()
draw_regalia_frame(before_card, rect)

before_panel = pygame.Surface((PANEL_W, PANEL_H))
before_panel.fill(BG)
before_panel.blit(before_card, (0, 0))


# ── Concept panels: crop (x=700, y=102) from each round_2.png ─────────────────
CONCEPTS = [
    ("cord_tag_check",   "CORD TAG"),
    ("stamp_check",      "STAMP"),
    ("paper_tag_check",  "PAPER TAG"),
    ("embroidered_check","EMBROIDERED"),
    ("ghost_tag_check",  "GHOST TAG"),
]

panels = [("FRAME ONLY", before_panel)]
for slug, label in CONCEPTS:
    path = os.path.join("docs/store_equipped_v3_2", slug, "round_2.png")
    img = pygame.image.load(path).convert()
    sub = img.subsurface(pygame.Rect(700, 102, PANEL_W, PANEL_H))
    panel = pygame.Surface((PANEL_W, PANEL_H))
    panel.fill(BG)
    panel.blit(sub, (0, 0))
    panels.append((label, panel))


# ── Layout ────────────────────────────────────────────────────────────────────
PAD   = 20
GAP   = 8
HDR_H = 40
FTR_H = 32
N     = len(panels)   # 6

sheet_w = PAD + N * PANEL_W + (N - 1) * GAP + PAD
sheet_h = PAD + HDR_H + PANEL_H + FTR_H + PAD

showcase = pygame.Surface((sheet_w, sheet_h))
showcase.fill(BG)

fh = hud_font(15, True)
fl = hud_font(11, True)

title = fh.render("store card — EQUIPPED v3.2 · regalia-frame + checkmark variants",
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

out = "docs/store_equipped_v3_2/showcase.png"
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(showcase, out)
print(f"saved {sheet_w}×{sheet_h} → {out}")
