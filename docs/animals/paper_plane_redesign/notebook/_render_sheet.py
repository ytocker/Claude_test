"""Round-1 review sheet for the NOTEBOOK PAPER paper-plane redesign.

Renders each of the 5 sub-takes at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt) on BOTH a DAY and a NIGHT sky, plus a
NEAREST-NEIGHBOR x3 magnification of those 40px reads so the true gameplay-pixel
silhouette is honest (smoothscale flatters tiny detail that vanishes in motion).
Headless (SDL dummy) so it runs in CI / on the build box.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "notebook_skins", os.path.join(_here, "notebook_skins.py"))
notebook_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notebook_skins)

BUILDERS = notebook_skins.BUILDERS
HERO_BUILDERS = notebook_skins.HERO_BUILDERS

ORDER = [
    ("skin_notebook_v1", "V1  CLASSIC RULED",
     "straight blue rules + red KEEL margin · spiral holes"),
    ("skin_notebook_v2", "V2  FOLD-FOLLOWING",
     "rules bend along facets (3D) · red TOP-edge margin"),
    ("skin_notebook_v3", "V3  CREAM + BIRO STAR",
     "warm cream · bold rules · biro star doodle"),
    ("skin_notebook_v4", "V4  GRADED A+",
     "dense rules · red 'A+' scrawl · torn fringe"),
    ("skin_notebook_v5", "V5  BOLD LOOSE-LEAF",
     "2 heavy rules + bold margin (40px-first) · ring holes"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 1
CARD_W, CARD_H = 760, 210
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Day sky (warm sunset stone) + night sky (deep indigo) — the two truth tests.
DAY_TOP = (250, 214, 150)
DAY_BOT = (236, 170, 120)
NIGHT_TOP = (26, 28, 56)
NIGHT_BOT = (42, 32, 64)

SHEET_BG_T = (18, 19, 38)
SHEET_BG_B = (34, 26, 50)
CARD_BG = (22, 23, 42)
CARD_EDGE = (74, 78, 128)
TEXT = (238, 240, 250)
SUB = (158, 164, 196)
PANEL_DAY = (244, 200, 150)
PANEL_NIGHT = (20, 22, 44)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + len(ORDER) * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_T[i] + (SHEET_BG_B[i] - SHEET_BG_T[i]) * t)
                for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — Paper Plane redesign · NOTEBOOK PAPER · Round 1", True, TEXT),
    (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px level & dive · NEAREST-NEIGHBOR x3 (the honest gameplay "
    "read) on DAY and NIGHT sky. Nose points RIGHT.",
    True, SUB), (PAD, 44))


def _crop(getter, frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(getter, frame_idx, tilt, target_px):
    crop = _crop(getter, frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)),
               max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _grad_panel(rect, top, bot, radius=10):
    p = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, y), (rect.w, y))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     mask.get_rect(), border_radius=radius)
    p.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sheet.blit(p, rect.topleft)


def _night_stars(rect, n, seed):
    import random
    rng = random.Random(seed)
    for _ in range(n):
        sx = rng.randint(rect.x + 4, rect.right - 4)
        sy = rng.randint(rect.y + 4, rect.bottom - 4)
        b = rng.randint(120, 220)
        pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)


for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    hero_getter = HERO_BUILDERS[key]
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("tell: " + feat, True, SUB), (cx + 14, cy + 34))

    # ── Hero panel (left) — split day/night halves to vet both grounds. ──
    hero_panel = pygame.Rect(cx + 14, cy + 56, 168, 140)
    _grad_panel(pygame.Rect(hero_panel.x, hero_panel.y,
                            hero_panel.w // 2, hero_panel.h), DAY_TOP, DAY_BOT)
    night_half = pygame.Rect(hero_panel.x + hero_panel.w // 2, hero_panel.y,
                             hero_panel.w - hero_panel.w // 2, hero_panel.h)
    _grad_panel(night_half, NIGHT_TOP, NIGHT_BOT)
    _night_stars(night_half, 26, idx + 1)
    hero = smooth(hero_getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px  day | night", True, TEXT),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # ── 40px truth panels: a DAY block and a NIGHT block, each with smooth +
    #    NEAREST x3 level/dive. ──
    def _truth_block(px, top, bot, dark_bg, label):
        panel = pygame.Rect(px, cy + 56, 270, 140)
        _grad_panel(panel, top, bot)
        if dark_bg:
            _night_stars(panel, 40, idx * 7 + (0 if top is DAY_TOP else 13))
        txt_col = (60, 40, 30) if not dark_bg else (220, 224, 240)
        # Row 1: smooth 40px level + dive.
        g_level = smooth(getter, 2, 0, GAME_PX)
        sheet.blit(g_level, g_level.get_rect(
            center=(panel.x + 40, panel.y + 28)))
        g_dive = smooth(getter, 1, -32, GAME_PX)
        sheet.blit(g_dive, g_dive.get_rect(
            center=(panel.x + 92, panel.y + 28)))
        # Row 2: NEAREST x3 level + dive (honest read).
        n_level = nearest40(getter, 2, 0, MAG)
        sheet.blit(n_level, n_level.get_rect(
            center=(panel.x + 150, panel.y + 34)))
        n_dive = nearest40(getter, 1, -32, MAG)
        sheet.blit(n_dive, n_dive.get_rect(
            center=(panel.x + 224, panel.y + 34)))
        sheet.blit(F_TAG.render(label, True, txt_col),
                   (panel.x + 8, panel.y + 60))
        sheet.blit(F_TAG.render("smooth 40 · NEAREST x3 (level/dive)",
                                True, txt_col),
                   (panel.x + 8, panel.bottom - 18))

    _truth_block(cx + 192, DAY_TOP, DAY_BOT, False, "DAY")
    _truth_block(cx + 472, NIGHT_TOP, NIGHT_BOT, True, "NIGHT")

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
