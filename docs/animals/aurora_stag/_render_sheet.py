"""Round-3 review sheet for the AURORA STAG production skin (final pass).

Round 3 applies the art-director's minimal must-fix list (palette/halo/gap/clip
frozen): re-aimed FORWARD brow-tines that flip horns→antlers, notch-detached
true-cross tip-stars, and a higher tine anchor so the dive rotation keeps the
lower tine legible. The sheet stress-tests the single ship build the way it
will actually render: hero 130px plus the in-game truth-test scale (40px level
+ dive, smooth AND NEAREST-NEIGHBOR x3) shown PROMINENTLY on a BRIGHT-DAY
gradient (the chroma-read insurance) and on night sky. Headless (SDL dummy) so
it runs in CI / on the build box.
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
    "aurora_stag_skins", os.path.join(_here, "aurora_stag_skins.py"))
aurora_stag_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aurora_stag_skins)

getter = aurora_stag_skins.BUILDERS["skin_aurora_stag"]


# ── backdrops: the game's real bright-day gradient + a night sky ─────────────
# Bright-day bottom ~(170,220,245) per the punch list — the worst case for a
# light-cored aurora; if the crown sings here it sings everywhere.
DAY_TOP = (96, 165, 230)
DAY_BOT = (170, 220, 245)
NIGHT_TOP = (14, 16, 36)
NIGHT_BOT = (28, 20, 50)

TEXT = (236, 238, 250)
SUB = (150, 156, 190)
TEXT_DAY = (24, 36, 56)
SUB_DAY = (60, 84, 110)
LEG_EDGE = (150, 110, 220)

HERO_PX = 130
GAME_PX = 40
MAG = 3


def _crop(frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(frame_idx, tilt, target_px):
    crop = _crop(frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    fac = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * fac)),
               max(1, int(crop.get_height() * fac))))


def nearest40(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def vgrad(surf, rect, top, bot):
    for y in range(rect.h):
        t = y / max(1, rect.h - 1)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(surf, col, (rect.x, rect.y + y),
                         (rect.right, rect.y + y))


pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 26, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_PANEL = pygame.font.SysFont("Arial", 17, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)


# ── layout: two big stress-test panels side by side (DAY left, NIGHT right) ──
# The DIVE NEAREST x3 row is widened to THREE dive instances (the must-fix #3
# re-check: forward tine + both tip-stars must stay legible post-rotation).
PAD = 18
HEADER_H = 70
PANEL_W = 500
PANEL_H = 380
SHEET_W = PAD * 3 + PANEL_W * 2
SHEET_H = HEADER_H + PANEL_H + PAD * 2

sheet = pygame.Surface((SHEET_W, SHEET_H))
sheet.fill((18, 20, 34))

# a faint star-field in the header band.
import random
rng = random.Random(7)
for _ in range(120):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, HEADER_H + 6)
    b = rng.randint(70, 180)
    pygame.draw.circle(sheet, (b, b, min(255, b + 40)), (sx, sy), 1)

sheet.blit(F_TITLE.render(
    "Skybit — AURORA STAG (legendary) · Round 3 · FORWARD TINES + NOTCHED STARS",
    True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "ONE production build on BRIGHT-DAY (sky bottom ~170,220,245) and NIGHT.  "
    "Hero 130px · 40px level & dive (smooth) · 40px NEAREST x3 level + x3 DIVE.",
    True, SUB), (PAD, 44))


def draw_panel(px, py, label, top, bot, txt, sub):
    panel = pygame.Rect(px, py, PANEL_W, PANEL_H)
    vgrad(sheet, panel, top, bot)
    pygame.draw.rect(sheet, LEG_EDGE, panel, 3, border_radius=12)
    sheet.blit(F_PANEL.render(label, True, txt), (px + 14, py + 10))

    # Hero (left half).
    hero = smooth(0, 0, HERO_PX)
    hero_cx, hero_cy = px + 110, py + 175
    sheet.blit(hero, hero.get_rect(center=(hero_cx, hero_cy)))
    sheet.blit(F_TAG.render("130px hero", True, sub),
               (px + 56, py + 320))

    # 40px smooth reference (level + dive), top right.
    g_level = smooth(2, 0, GAME_PX)
    g_dive = smooth(1, -32, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(px + 290, py + 56)))
    sheet.blit(g_dive, g_dive.get_rect(center=(px + 360, py + 56)))
    sheet.blit(F_TAG.render("40px smooth  (level / dive)", True, sub),
               (px + 250, py + 84))

    # 40px NEAREST x3 — the honest gameplay-pixel read.
    # One LEVEL plus THREE DIVE instances (must-fix #3 re-check: forward tine +
    # both tip-stars stay legible through the dive rotation).
    n_level = nearest40(2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(px + 250, py + 215)))
    sheet.blit(F_TAG.render("level", True, sub), (px + 232, py + 268))

    for k, dive_tilt in enumerate((-24, -32, -40)):
        n_dive = nearest40(1, dive_tilt, MAG)
        cx = px + 330 + k * 58
        sheet.blit(n_dive, n_dive.get_rect(center=(cx, py + 215)))
        sheet.blit(F_TAG.render(f"{dive_tilt}", True, sub),
                   (cx - 12, py + 268))
    sheet.blit(F_TAG.render("40px NEAREST x3  ·  level / DIVE x3", True, sub),
               (px + 250, py + 300))


draw_panel(PAD, HEADER_H + PAD, "BRIGHT DAY (worst case)",
           DAY_TOP, DAY_BOT, TEXT_DAY, SUB_DAY)
draw_panel(PAD * 2 + PANEL_W, HEADER_H + PAD, "NIGHT",
           NIGHT_TOP, NIGHT_BOT, TEXT, SUB)

out_path = os.path.join(_here, "round_3.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
