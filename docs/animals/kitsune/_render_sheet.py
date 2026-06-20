"""Round-2 review sheet for the production KITSUNE skin.

ONE converged design, shown the honest way it must survive: hero 130px (with
the store-card gold aura ring) + 40px level/dive (smooth) + 40px NEAREST x3
(the true gameplay-pixel read; smoothscale flatters tiny detail that vanishes
in motion). Rendered on BOTH a night AND a bright-day backdrop so the violet
crown, white moon-disc blaze, and baked rims are checked against both extremes
of the day/night cycle. Headless (SDL dummy) so it runs in CI / on the build box.
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
    "kitsune_skins", os.path.join(_here, "kitsune_skins.py"))
kitsune_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kitsune_skins)

build_kitsune = kitsune_skins.build_kitsune
build_kitsune_aura = kitsune_skins.build_kitsune_aura
get_kitsune = kitsune_skins.get_kitsune
_add_outline = kitsune_skins._add_outline
_WING_ANGLES = kitsune_skins._WING_ANGLES

HERO_PX = 130
GAME_PX = 40
MAG = 3


def _hero_frame(angle):
    """Store card: outline the fox, then composite the gold aura ring BEHIND it
    (so the outline pass doesn't trace the soft halo into a dark ring)."""
    fox = _add_outline(build_kitsune(angle))
    aura = build_kitsune_aura()
    out = pygame.Surface(fox.get_size(), pygame.SRCALPHA)
    out.blit(aura, ((fox.get_width() - aura.get_width()) // 2,
                    (fox.get_height() - aura.get_height()) // 2))
    out.blit(fox, (0, 0))
    return out


# Cached outlined hero frames (with the gold aura ring); gameplay frames omit it.
_HERO = [_hero_frame(a) for a in _WING_ANGLES]


def _crop(surf):
    rect = surf.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = surf.get_rect()
    return surf.subsurface(rect).copy()


def _smooth(surf, target_px):
    crop = _crop(surf)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def hero_img():
    return _smooth(_HERO[0], HERO_PX)


def smooth_game(frame_idx, tilt, target_px=GAME_PX):
    return _smooth(get_kitsune(frame_idx, tilt), target_px)


def nearest40(frame_idx, tilt, mag=MAG):
    small = smooth_game(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


# ── sheet layout: two columns (NIGHT | BRIGHT DAY), shared rows ──────────────
PAD = 18
HEADER_H = 70
PANEL_W = 384
PANEL_H = 470
COL_GAP = 18

SHEET_W = PAD + PANEL_W + COL_GAP + PANEL_W + PAD
SHEET_H = HEADER_H + PAD + PANEL_H + PAD

TEXT = (236, 238, 250)
SUB = (158, 150, 190)
GOLD = (210, 168, 78)

NIGHT_TOP = (16, 18, 42)
NIGHT_BOT = (40, 26, 56)
DAY_TOP = (150, 206, 244)
DAY_BOT = (224, 240, 252)

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((10, 11, 24))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_PANEL = pygame.font.SysFont("Arial", 18, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — KITSUNE (legendary crown jewel) · Round 2", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "ONE production build. HERO 130px (gold aura ring, store card) · 40px level & dive (smooth) · NEAREST x3 (honest gameplay read).",
    True, SUB), (PAD, 44))


import random


def _gradient(panel, top, bot):
    for y in range(panel.get_height()):
        t = y / panel.get_height()
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(panel, col, (0, y), (panel.get_width(), y))


def build_panel(label, top, bot, starfield, sub_col):
    panel = pygame.Surface((PANEL_W, PANEL_H))
    _gradient(panel, top, bot)
    if starfield:
        rng = random.Random(7)
        for _ in range(120):
            sx, sy = rng.randint(0, PANEL_W), rng.randint(0, PANEL_H)
            b = rng.randint(90, 220)
            pygame.draw.circle(panel, (b, b, min(255, b + 28)), (sx, sy),
                               rng.choice([1, 1, 2]))
    pygame.draw.rect(panel, GOLD, panel.get_rect(), 3)
    panel.blit(F_PANEL.render(label, True, GOLD), (14, 10))

    # Hero (store card) — top, centred.
    hero = hero_img()
    hp = pygame.Rect(PANEL_W // 2 - 88, 40, 176, 196)
    panel.blit(hero, hero.get_rect(center=hp.center))
    panel.blit(F_TAG.render("HERO 130px · gold aura ring · down-pose full fan",
                            True, sub_col), (hp.x - 6, hp.bottom - 6))

    gy = 268
    # 40px smooth — level frame 2, dive frame 1 @ -32 (mass test).
    gl = smooth_game(2, 0)
    panel.blit(gl, gl.get_rect(center=(74, gy)))
    gd = smooth_game(1, -32)
    panel.blit(gd, gd.get_rect(center=(150, gy)))
    panel.blit(F_TAG.render("40px smooth  (level / dive)", True, sub_col),
               (28, gy + 30))

    # Flap delta: frame 0 (down, wide) vs frame 3 (up, gathered).
    f0 = smooth_game(0, 0)
    panel.blit(f0, f0.get_rect(center=(250, gy)))
    f3 = smooth_game(3, 0)
    panel.blit(f3, f3.get_rect(center=(326, gy)))
    panel.blit(F_TAG.render("flap: down / up", True, sub_col), (236, gy + 30))

    ny = 392
    nl = nearest40(2, 0)
    panel.blit(nl, nl.get_rect(center=(86, ny)))
    nd = nearest40(1, -32)
    panel.blit(nd, nd.get_rect(center=(228, ny)))
    panel.blit(F_TAG.render("40px NEAREST x3  (level / dive — the honest read)",
                            True, sub_col), (28, PANEL_H - 22))
    return panel


night = build_panel("NIGHT SKY", NIGHT_TOP, NIGHT_BOT, True, SUB)
day = build_panel("BRIGHT DAY SKY", DAY_TOP, DAY_BOT, False, (70, 92, 120))

sheet.blit(night, (PAD, HEADER_H + PAD))
sheet.blit(day, (PAD + PANEL_W + COL_GAP, HEADER_H + PAD))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
