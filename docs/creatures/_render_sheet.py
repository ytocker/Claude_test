"""Round-1 review sheet for the candidate animal Store skins.

Renders each creature at hero 130px AND at the in-game truth-test scale
(40px, level + a dive tilt) on dark night-sky cards, labelled. Headless
(SDL dummy) so it runs in CI / on the build box.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

# Import after the dummy driver is set so the parrot module can build surfaces.
import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "creature_skins", os.path.join(_here, "creature_skins.py"))
creature_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(creature_skins)

BUILDERS = creature_skins.BUILDERS

ORDER = [
    ("skin_owl", "OWL", "facial disc + huge eyes"),
    ("skin_toucan", "TOUCAN", "oversized orange beak"),
    ("skin_penguin", "PENGUIN", "black/white split + beak"),
    ("skin_bat", "BAT", "membrane span + ears"),
    ("skin_flamingo", "FLAMINGO", "pink S-neck + bent beak"),
    ("skin_eagle", "BALD EAGLE", "white head + hooked beak"),
    ("skin_bee", "BEE", "gold/black stripes"),
    ("skin_dragon", "DRAGON  (gacha)", "horns + spiked tail + wing"),
    ("skin_phoenix", "PHOENIX  (gacha)", "flame crest + fire gradient"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 3
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 300, 232
PAD = 16
HEADER_H = 60
HERO_PX = 130
GAME_PX = 40

NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
HERO_PANEL = (28, 30, 56)
GAME_PANEL = (12, 13, 28)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

# Scattered stars on the backdrop.
import random
rng = random.Random(7)
for _ in range(140):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — Animal Store Skins · Round 1", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Each creature: HERO 130px (left) + in-game 40px level & dive-tilt (right, the truth test). Dark night-sky card.",
    True, SUB), (PAD, 44))


def scaled(getter, frame_idx, tilt, target_px):
    """Render a frame, trim to its non-transparent bounds, scale longest
    edge to target_px with smoothscale."""
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    crop = s.subsurface(rect).copy()
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    out = pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))
    return out


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    # Name + feature.
    sheet.blit(F_NAME.render(name, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 34))

    # Hero panel (left).
    hero_panel = pygame.Rect(cx + 12, cy + 56, 150, 162)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = scaled(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Game panel (right) — two 40px reads: level + dive tilt.
    game_panel = pygame.Rect(cx + 170, cy + 56, 118, 162)
    pygame.draw.rect(sheet, GAME_PANEL, game_panel, border_radius=10)
    # level
    g_level = scaled(getter, 2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(game_panel.centerx, game_panel.y + 40)))
    sheet.blit(F_TAG.render("40px level", True, SUB),
               (game_panel.x + 8, game_panel.y + 64))
    # dive tilt (climbing/diving — use a downward dive of -35°)
    g_dive = scaled(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(game_panel.centerx, game_panel.y + 108)))
    sheet.blit(F_TAG.render("40px dive", True, SUB),
               (game_panel.x + 8, game_panel.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
