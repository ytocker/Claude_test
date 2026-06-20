"""Round-1 review sheet for the candidate PUFFERFISH Store skin.

Renders each of the 5 variants at hero 130px (smooth) AND at the in-game
truth-test scale: 40px level + dive tilt, plus a NEAREST-NEIGHBOR x3
magnification of those 40px reads so the honest gameplay-pixel silhouette is
visible (smoothscale flatters tiny detail that vanishes in motion). Headless
(SDL dummy) so it runs in CI / on the build box.

Also includes a small 4-frame flap strip per version so the inflate/deflate
PULSE gag is legible on the sheet.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "pufferfish_skins", os.path.join(_here, "pufferfish_skins.py"))
pufferfish_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pufferfish_skins)

BUILDERS = pufferfish_skins.BUILDERS
TELLS = pufferfish_skins.TELLS

ORDER = list(BUILDERS.keys())

# ── layout ───────────────────────────────────────────────────────────────────
CARD_W, CARD_H = 540, 232
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Two backdrops per card: a bright-day half (left) and a night half (right) so
# we honestly check the silhouette against BOTH skies, per the brief.
DAY_TOP = (120, 196, 240)
DAY_BOT = (188, 228, 246)
NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
SHEET_TOP = (18, 20, 40)
SHEET_BOT = (34, 26, 52)
CARD_EDGE = (70, 80, 130)
TEXT = (236, 238, 250)
SUB = (158, 164, 198)

COLS = 1
ROWS = len(ORDER)
SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_TOP[i] + (SHEET_BOT[i] - SHEET_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(140):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 190)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — PUFFERFISH Store Skin · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "5 distinct takes. HERO 130px (day|night) · 40px level+dive smooth · NEAREST x3 truth · 4-frame inflate PULSE.",
    True, SUB), (PAD, 42))


def _grad_rect(surf, rect, top, bot):
    for i in range(rect.h):
        t = i / max(1, rect.h)
        col = tuple(int(top[j] + (bot[j] - top[j]) * t) for j in range(3))
        pygame.draw.line(surf, col, (rect.x, rect.y + i), (rect.right, rect.y + i))


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
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


for idx, key in enumerate(ORDER):
    getter = BUILDERS[key]
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)
    cx = PAD
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)

    sheet.blit(F_NAME.render(key, True, TEXT), (cx + 4, cy - 2))
    sheet.blit(F_FEAT.render("40px tell: " + TELLS[key], True, SUB), (cx + 4, cy + 22))

    panel_top = cy + 42
    pygame.draw.rect(sheet, CARD_EDGE, (cx, panel_top, CARD_W, CARD_H - 42), 2,
                     border_radius=10)

    # ── HERO 130px on a split day|night backdrop ──
    hero_panel = pygame.Rect(cx + 8, panel_top + 8, 200, CARD_H - 60)
    half = hero_panel.copy(); half.w //= 2
    _grad_rect(sheet, half, DAY_TOP, DAY_BOT)
    night = hero_panel.copy(); night.x += half.w; night.w = hero_panel.w - half.w
    _grad_rect(sheet, night, NIGHT_TOP, NIGHT_BOT)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px  day | night", True, (240, 240, 240)),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # ── 40px reads ──
    gp = pygame.Rect(cx + 218, panel_top + 8, 168, CARD_H - 60)
    pygame.draw.rect(sheet, (12, 13, 28), gp, border_radius=8)
    g_level = smooth(getter, 2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(gp.x + 44, gp.y + 30)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(gp.x + 116, gp.y + 30)))
    sheet.blit(F_TAG.render("40px smooth", True, SUB), (gp.x + 8, gp.y + 52))
    n_level = nearest40(getter, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(gp.x + 48, gp.y + 116)))
    n_dive = nearest40(getter, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(gp.x + 122, gp.y + 116)))
    sheet.blit(F_TAG.render("40px NEAREST x3 (level / dive)", True, (210, 200, 150)),
               (gp.x + 8, gp.bottom - 18))

    # ── 4-frame inflate PULSE strip (down→up) at 56px ──
    fp = pygame.Rect(cx + 396, panel_top + 8, CARD_W - 404, CARD_H - 60)
    _grad_rect(sheet, fp, NIGHT_TOP, NIGHT_BOT)
    pygame.draw.rect(sheet, CARD_EDGE, fp, 1, border_radius=8)
    for fi in range(4):
        fr = smooth(getter, fi, 0, 48)
        fx = fp.x + 18 + fi * 30
        sheet.blit(fr, fr.get_rect(center=(fx, fp.y + fp.h // 2 - 6)))
    sheet.blit(F_TAG.render("PULSE: puff→deflate", True, (235, 220, 180)),
               (fp.x + 6, fp.bottom - 18))


out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
