"""Render 4-column comparison: Design 4 NEON DINER with 4 cord variants."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame; pygame.init()
import importlib.util

spec = importlib.util.spec_from_file_location(
    "design_4_cords",
    os.path.join(os.path.dirname(__file__), "design_4_cords.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from _render_shared import gameplay_panel, carry_zoom_panel, hero_panel

FONT    = pygame.font.SysFont("DejaVu Sans", 15, bold=True)
FONT_SM = pygame.font.SysFont("DejaVu Sans", 12)

VARIANTS = mod.VARIANTS   # [(label, build_fn), ...]

N        = len(VARIANTS)
COL_W    = 180
PLAY_H   = 260
HERO_SZ  = 180
CARRY_SZ = 180
LABEL_H  = 32
PAD      = 12

TOTAL_W = N * COL_W + (N + 1) * PAD
TOTAL_H = PAD + LABEL_H + PAD + PLAY_H + PAD + HERO_SZ + PAD + CARRY_SZ + PAD

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill((18, 16, 28))

title = FONT.render("NEON NIGHT-DINER — 4 cord variants", True, (240, 235, 255))
canvas.blit(title, (PAD, 4))

y_play  = PAD + LABEL_H + PAD
y_hero  = y_play  + PLAY_H  + PAD
y_carry = y_hero  + HERO_SZ + PAD

for i, (label, build_fn) in enumerate(VARIANTS):
    x0 = PAD + i * (COL_W + PAD)
    cx = x0 + COL_W // 2

    lab = FONT_SM.render(label, True, (200, 200, 210))
    canvas.blit(lab, lab.get_rect(centerx=cx, y=PAD + 2))

    gp = gameplay_panel(build_fn, COL_W, PLAY_H, night=False)
    canvas.blit(gp, (x0, y_play))

    hp = hero_panel(build_fn, HERO_SZ)
    canvas.blit(hp, hp.get_rect(centerx=cx, y=y_hero))

    cz = carry_zoom_panel(build_fn, zoom=5)
    canvas.blit(cz, cz.get_rect(centerx=cx, y=y_carry))

    if i > 0:
        pygame.draw.line(canvas, (50, 45, 70),
                         (x0 - PAD // 2, PAD),
                         (x0 - PAD // 2, TOTAL_H - PAD), 1)

out = os.path.join(os.path.dirname(__file__), "..", "..",
                   "docs", "store_redesign", "parcels", "ufo", "design_4",
                   "cord_variants.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved → {out}")
