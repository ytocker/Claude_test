"""Render the design_2 AMBER RELIC review sheet: hero | day | night."""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

import pygame

pygame.init()

import tools.ninja_render as nr
from tools.mosquito_candidates.design_2 import build

hero = nr.hero_panel(build, 220)
panel_day = nr.gameplay_panel(build, 220, 392)
panel_night = nr.gameplay_panel(build, 220, 392, frame_idx=0, tilt=-8.0)

PAD = 16
TITLE_H = 40
panels = [hero, panel_day, panel_night]
labels = ["HERO", "DAY", "NIGHT (climb)"]
ph = max(p.get_height() for p in panels)
pw = sum(p.get_width() for p in panels) + PAD * (len(panels) + 1)
sheet = pygame.Surface((pw, ph + TITLE_H + PAD * 2), pygame.SRCALPHA)
sheet.fill((18, 16, 24))

font = pygame.font.SysFont("dejavusans", 22, bold=True)
small = pygame.font.SysFont("dejavusans", 15)
title = font.render("DESIGN 2 — AMBER RELIC", True, (255, 216, 115))
sheet.blit(title, (PAD, PAD // 2))

x = PAD
for p, lbl in zip(panels, labels):
    y = TITLE_H + PAD
    sheet.blit(p, (x, y))
    tag = small.render(lbl, True, (232, 220, 200))
    sheet.blit(tag, (x + (p.get_width() - tag.get_width()) // 2, y + p.get_height() + 2))
    x += p.get_width() + PAD

out = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "docs", "store_redesign", "animal", "mosquito", "design_2", "round_1.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out, sheet.get_size())
