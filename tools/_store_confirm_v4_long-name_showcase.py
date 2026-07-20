#!/usr/bin/env python3
"""
Phase 5 showcase — long-name overflow, 5 design concepts
Crops Panel 2 (TEMPEST CONDOR stress test) from each concept's round_2.png,
scales to PANEL_W × PANEL_H, and composes a 5-panel comparison figure.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

from PIL import Image

# ── Source panel geometry (from each R2 script's layout constants) ────────────
# Each R2 sheet has 3 panels (MUMMY / SUGAR GLIDER / TEMPEST CONDOR).
# Panel 2 (index 2, TEMPEST CONDOR) is the stress-test crop we want.
#   x0 = row_x0 + 2 * (PANEL_W + GAP)
#   y0 = MARGIN + HDR_H + GAP

CONCEPTS = [
    {
        "slug":    "scale-to-fit",
        "id":      "A",
        "p2_x":    18 + 2 * (200 + 10),   # 438
        "p2_y":    18 + 30 + 10,           # 58
    },
    {
        "slug":    "line-break",
        "id":      "B",
        "p2_x":    18 + 2 * (200 + 10),   # 438
        "p2_y":    18 + 28 + 10,           # 56
    },
    {
        "slug":    "horiz-squeeze",
        "id":      "C",
        "p2_x":    16 + 2 * (200 + 12),   # 440
        "p2_y":    16 + 26 + 12,           # 54
    },
    {
        "slug":    "nameplate",
        "id":      "D",
        "p2_x":    18 + 2 * (200 + 12),   # 442
        "p2_y":    18 + 26 + 12,           # 56
    },
    {
        "slug":    "unified-banner",
        "id":      "E",
        "p2_x":    18 + 2 * (200 + 14),   # 446
        "p2_y":    18 + 26 + 14,           # 58
    },
]

# ── Showcase canvas constants ─────────────────────────────────────────────────

PANEL_W  = 200
PANEL_H  = 340
BG       = (8, 8, 20)
MARGIN   = 20
GAP      = 8
HDR_H    = 40
FOOT_H   = 34

N        = len(CONCEPTS)
CANVAS_W = MARGIN + N * PANEL_W + (N - 1) * GAP + MARGIN
CANVAS_H = MARGIN + HDR_H + GAP + PANEL_H + FOOT_H + MARGIN

CREAM    = (252, 246, 228)
DIM      = (150, 146, 170)
BORDER   = (40, 38, 60)
BADGE_BG = (24, 22, 38)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..",
                        "docs", "store_confirm_popup_v4", "long-name")
OUT      = os.path.join(BASE_DIR, "showcase.png")

# ── Helpers ───────────────────────────────────────────────────────────────────

def _pil_to_surf(img):
    rgb = img.convert("RGB")
    return pygame.image.fromstring(rgb.tobytes(), rgb.size, "RGB")


def _badge(font, label):
    txt   = font.render(label, True, CREAM)
    pad_h = 5
    pad_v = 3
    w     = txt.get_width()  + pad_h * 2
    h     = txt.get_height() + pad_v * 2
    surf  = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    pygame.draw.rect(surf, (*BADGE_BG, 220), (0, 0, w, h), border_radius=4)
    surf.blit(txt, (pad_h, pad_v))
    return surf

# ── Load + crop Panel 2 from each round_2.png ────────────────────────────────

panels = []
for c in CONCEPTS:
    path = os.path.join(BASE_DIR, c["slug"], "round_2.png")
    img  = Image.open(path)
    x0, y0 = c["p2_x"], c["p2_y"]
    crop = img.crop((x0, y0, x0 + PANEL_W, y0 + PANEL_H))
    if crop.size != (PANEL_W, PANEL_H):
        crop = crop.resize((PANEL_W, PANEL_H), Image.LANCZOS)
    panels.append(crop)
    print(f"  {c['slug']:20s}  src {img.size}  crop @({x0},{y0})  → {crop.size}")

# ── Compose canvas ────────────────────────────────────────────────────────────

canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(BG)

# Header
f_hdr  = pygame.font.Font(None, 24)
hdr    = f_hdr.render(
    "LONG-NAME OVERFLOW  ·  5 concepts  ·  TEMPEST CONDOR (14-char stress test)  ·  R2",
    True, (190, 186, 220))
canvas.blit(hdr, hdr.get_rect(midtop=(CANVAS_W // 2, MARGIN + 8)))

panel_top = MARGIN + HDR_H + GAP

f_badge = pygame.font.Font(None, 22)
f_slug  = pygame.font.Font(None, 16)
f_ver   = pygame.font.Font(None, 14)

for i, (c, img) in enumerate(zip(CONCEPTS, panels)):
    x0   = MARGIN + i * (PANEL_W + GAP)
    surf = _pil_to_surf(img)
    canvas.blit(surf, (x0, panel_top))

    # 1-px border
    pygame.draw.rect(canvas, BORDER,
                     (x0 - 1, panel_top - 1, PANEL_W + 2, PANEL_H + 2), width=1)

    # ID badge — top-left corner of panel
    badge = _badge(f_badge, c["id"])
    canvas.blit(badge, (x0 + 6, panel_top + 6))

    # Footer — slug name + FINAL
    slug_s = f_slug.render(c["slug"], True, CREAM)
    ver_s  = f_ver.render("FINAL", True, DIM)
    cx     = x0 + PANEL_W // 2
    fy     = panel_top + PANEL_H + 5
    canvas.blit(slug_s, slug_s.get_rect(midtop=(cx, fy)))
    canvas.blit(ver_s,  ver_s.get_rect(midtop=(cx, fy + 17)))

# ── Save ──────────────────────────────────────────────────────────────────────

pygame.image.save(canvas, OUT)
w, h = canvas.get_size()
print(f"\nSaved  {OUT}  ({w}×{h})")
