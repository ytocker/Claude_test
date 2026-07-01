"""Render 6-column colour comparison for Design 3 GOLDEN GLYPH DISC."""
import os, sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame; pygame.init()
import importlib.util

spec = importlib.util.spec_from_file_location(
    "design_3_colors",
    os.path.join(os.path.dirname(__file__), "design_3_colors.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from _render_shared import gameplay_panel, hero_panel, carry_zoom_panel

FONT    = pygame.font.SysFont("DejaVu Sans", 14, bold=True)
FONT_SM = pygame.font.SysFont("DejaVu Sans", 11)

VARIANTS = mod.VARIANTS

N        = len(VARIANTS)
COL_W    = 170
PLAY_H   = 250
HERO_SZ  = 170
CARRY_SZ = 170
LABEL_H  = 36
PAD      = 10

TOTAL_W = N * COL_W + (N + 1) * PAD
TOTAL_H = PAD + LABEL_H + PAD + PLAY_H + PAD + HERO_SZ + PAD + CARRY_SZ + PAD

canvas = pygame.Surface((TOTAL_W, TOTAL_H))
canvas.fill((18, 16, 28))

title = FONT.render("GOLDEN GLYPH DISC — colour variants", True, (240, 235, 255))
canvas.blit(title, (PAD, 4))

y_play  = PAD + LABEL_H + PAD
y_hero  = y_play  + PLAY_H  + PAD
y_carry = y_hero  + HERO_SZ + PAD

for i, (label, build_fn) in enumerate(VARIANTS):
    x0 = PAD + i * (COL_W + PAD)
    cx = x0 + COL_W // 2

    for li, line in enumerate(label.split("\n")):
        col = (255, 215, 60) if i == 0 else (200, 200, 210)
        lab = FONT_SM.render(line, True, col)
        canvas.blit(lab, lab.get_rect(centerx=cx, y=PAD + li * 14))

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
                   "docs", "store_redesign", "parcels", "ufo", "design_3",
                   "color_variants.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(canvas, out)
print(f"saved → {out}")
