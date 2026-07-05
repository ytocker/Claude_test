"""Render a BINKY diaper candidate to a round review sheet.

Lays out: a large hero product-shot, the in-gameplay panel, and 40px NEAREST
"truth reads" on both day and navy-night sky (the make-or-break view — the
costume lives or dies at icon size on both skies).
"""
from __future__ import annotations
import os, sys, importlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
pygame.init()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from game import biome
from tools.ninja_render import gameplay_panel, hero_panel

DESIGN = sys.argv[1] if len(sys.argv) > 1 else "design_2"
OUT = sys.argv[2]

mod = importlib.import_module(f"tools.binky_diaper_candidates.{DESIGN}")
build = mod.build

FONT = pygame.font.SysFont("monospace", 14, bold=True)
SMALL = pygame.font.SysFont("monospace", 11)


def _truth_read(palette, label):
    """40px NEAREST upscale of the frame on a flat sky-tint tile."""
    frame = build(2, 10.0)
    bb = frame.get_bounding_rect()
    frame = frame.subsurface(bb).copy() if bb.width else frame
    # fit into a 40px box preserving aspect, NEAREST so we judge real pixels
    sw, sh = frame.get_size()
    sc = 40 / max(sw, sh)
    small = pygame.transform.scale(frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
    big = pygame.transform.scale(small, (small.get_width() * 4, small.get_height() * 4))
    tile = pygame.Surface((200, 200))
    tile.fill(palette["sky_top"])
    tile.blit(big, big.get_rect(center=(100, 92)))
    tile.blit(SMALL.render(label, True, (255, 255, 255)), (8, 178))
    pygame.draw.rect(tile, (255, 255, 255), tile.get_rect(), 1)
    return tile


day = biome.palette_for_phase(0.0)
night = biome.palette_for_phase(0.64375)

hero = hero_panel(build, 300, tilt=0.0)
gp = gameplay_panel(build, 220, 320)
td = _truth_read(day, "40px DAY (nearest)")
tn = _truth_read(night, "40px NAVY NIGHT (nearest)")

W, H = 640, 560
sheet = pygame.Surface((W, H))
sheet.fill((28, 26, 38))
title = FONT.render("BINKY diaper redo — DESIGN 2 PUFFY DISPOSABLE — round 1", True, (255, 235, 200))
sheet.blit(title, (16, 12))

sheet.blit(hero, (16, 40))
sheet.blit(FONT.render("HERO", True, (200, 200, 210)), (16, 344))
sheet.blit(gp, (374, 40))
sheet.blit(FONT.render("IN GAMEPLAY (day)", True, (200, 200, 210)), (374, 344))

sheet.blit(td, (90, 370))
sheet.blit(tn, (350, 370))

pygame.image.save(sheet, OUT)
print("WROTE", OUT)
