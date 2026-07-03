"""Render the Design 9 (Trench-Dead War Parrot) round sheet."""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib.util
import pygame
pygame.init()

from tools.ninja_render import gameplay_panel, hero_panel, FRAME_IDX, TILT

spec = importlib.util.spec_from_file_location(
    "zombie_d9", os.path.join(os.path.dirname(__file__), "design_9.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
build = mod.build

PAD = 24
GP_W, GP_H = 200, 350
HERO = 280
TRUTH = 200

sheet_w = PAD * 4 + GP_W + HERO + TRUTH
sheet_h = PAD * 2 + 60 + max(GP_H, HERO, TRUTH)
sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
sheet.fill((16, 15, 22))

font = pygame.font.SysFont("dejavusans", 26, bold=True)
small = pygame.font.SysFont("dejavusans", 15)

title = font.render("DESIGN 9 — TRENCH-DEAD WAR PARROT", True, (236, 232, 224))
sheet.blit(title, (PAD, 16))

top = PAD + 60
x = PAD

gp = gameplay_panel(build, GP_W, GP_H)
sheet.blit(gp, (x, top))
sheet.blit(small.render("gameplay", True, (170, 168, 180)), (x, top + GP_H + 6))
x += GP_W + PAD

hp = hero_panel(build, HERO, frame_idx=FRAME_IDX, tilt=0.0)
sheet.blit(hp, (x, top))
sheet.blit(small.render("hero", True, (170, 168, 180)), (x, top + HERO + 6))
x += HERO + PAD

# 40px truth-read: shrink hero frame to 40x40 NEAREST, scale back 5x.
frame = build(FRAME_IDX, 0.0)
bb = frame.get_bounding_rect()
if bb.width and bb.height:
    frame = frame.subsurface(bb).copy()
sq = pygame.Surface((40, 40), pygame.SRCALPHA)
sw, sh = frame.get_size()
sc = 36.0 / max(sw, sh)
small_frame = pygame.transform.scale(frame, (max(1, int(sw * sc)), max(1, int(sh * sc))))
sq.blit(small_frame, small_frame.get_rect(center=(20, 20)))
truth = pygame.transform.scale(sq, (TRUTH, TRUTH))
tbg = pygame.Surface((TRUTH, TRUTH), pygame.SRCALPHA)
pygame.draw.rect(tbg, (22, 20, 32), tbg.get_rect(), border_radius=14)
tbg.blit(truth, (0, 0))
sheet.blit(tbg, (x, top))
sheet.blit(small.render("40px truth-read", True, (170, 168, 180)), (x, top + TRUTH + 6))

out = os.path.join(os.path.dirname(__file__), "..", "..",
                   "docs", "store_redesign", "costume", "zombie", "design_9", "round_1.png")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
pygame.image.save(sheet, out)
print("saved", out)
