"""Round-1 review sheet for the FLYING-WING STEALTH jet redesign.

Each candidate is shown at hero 130px AND at the in-game truth-test scale
(40px, level + dive tilt), the 40px reads NEAREST-NEIGHBOR x3 magnified so the
honest gameplay-pixel silhouette is visible — on BOTH a day stone sky and a
night sky, because a dark low-vis wing must survive both. The CURRENT
production Steel Raptor leads the sheet as the silhouette-contrast baseline.
Headless (SDL dummy) so it runs in CI / on the build box.
"""
import os
import sys
import importlib.util

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "flyingwing_skins", os.path.join(_here, "flyingwing_skins.py"))
flyingwing_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flyingwing_skins)

from game.animal_jet_fighter import get_jet_fighter   # current production baseline

BUILDERS = flyingwing_skins.BUILDERS

# Current jet leads as the silhouette-contrast baseline, then the 5 candidates.
ORDER = [
    ("__current__", "CURRENT · STEEL RAPTOR", "pointy dart + delta + twin tail (the silhouette to differ from)"),
    ("v1 B-2 CRESCENT", "v1 · B-2 CRESCENT", "smooth crescent + double-W sawtooth, matte charcoal"),
    ("v2 YF-23 DIAMOND", "v2 · YF-23 DIAMOND", "angular diamond kite + cool-blue edge-glow"),
    ("v3 ARROWHEAD WING", "v3 · ARROWHEAD WING", "sharp arrowhead + two-tone panels + amber slit"),
    ("v4 SWEPT MANTA", "v4 · SWEPT MANTA", "widest boomerang + deep sawtooth + blue glow"),
    ("v5 OBSIDIAN SPLIT", "v5 · OBSIDIAN SPLIT", "matte-black value-split stress test + amber slit"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 560, 268
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

SHEET_BG_T = (22, 24, 40)
SHEET_BG_B = (34, 28, 48)
CARD_BG = (16, 17, 30)
CARD_EDGE = (60, 64, 104)
CUR_EDGE = (150, 156, 176)        # neutral rim for the baseline card
TEXT = (236, 238, 250)
SUB = (150, 156, 190)

# Day = warm sandstone sunset; Night = deep blue. Both are real in-game skies.
DAY_T = (224, 176, 120)
DAY_B = (196, 132, 96)
NIGHT_T = (20, 24, 50)
NIGHT_B = (36, 30, 58)
HERO_PANEL = (28, 30, 52)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_T[i] + (SHEET_BG_B[i] - SHEET_BG_T[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(23)
for _ in range(200):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(70, 180)
    pygame.draw.circle(sheet, (b, b, min(255, b + 26)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — JET redesign · FLYING-WING STEALTH · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px NEAREST x3 (level / dive) on DAY stone + NIGHT sky — the honest wide-wing read. Current Steel Raptor leads as the silhouette baseline.",
    True, SUB), (PAD, 42))


def _vpanel(surf, rect, top, bot):
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(surf, col, (rect.x, rect.y + y), (rect.right, rect.y + y))


def _crop(getter, frame_idx, tilt):
    s = getter(frame_idx, tilt)
    r = s.get_bounding_rect()
    if r.w == 0 or r.h == 0:
        r = s.get_rect()
    return s.subsurface(r).copy()


def smooth(getter, frame_idx, tilt, target_px):
    crop = _crop(getter, frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _read_block(panel_x, panel_y, getter, top, bot, label):
    """One sky panel: hero is shared above; here we draw the 40px NEAREST x3
    level + dive reads over a real sky gradient."""
    panel = pygame.Rect(panel_x, panel_y, 196, 168)
    _vpanel(sheet, panel, top, bot)
    pygame.draw.rect(sheet, (0, 0, 0), panel, 1)
    sheet.blit(F_TAG.render(label, True, (250, 250, 250)),
               (panel.x + 8, panel.y + 6))
    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.x + 56, panel.y + 92)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 140, panel.y + 92)))
    sheet.blit(F_TAG.render("level", True, (245, 245, 245)),
               (panel.x + 40, panel.bottom - 18))
    sheet.blit(F_TAG.render("dive", True, (245, 245, 245)),
               (panel.x + 128, panel.bottom - 18))


for idx, (key, name, feat) in enumerate(ORDER):
    getter = get_jet_fighter if key == "__current__" else BUILDERS[key]
    is_cur = key == "__current__"
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CUR_EDGE if is_cur else CARD_EDGE,
                     card, 3 if is_cur else 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, CUR_EDGE if is_cur else TEXT),
               (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 36))

    # Hero panel (left) on neutral dark so the finish reads true.
    hero_panel = pygame.Rect(cx + 12, cy + 60, 140, 196)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Day + Night truth panels (right).
    _read_block(cx + 162, cy + 60, getter, DAY_T, DAY_B, "DAY 40px x3")
    _read_block(cx + 362, cy + 60, getter, NIGHT_T, NIGHT_B, "NIGHT 40px x3")

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
