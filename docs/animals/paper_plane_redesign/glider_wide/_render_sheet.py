"""Round-2 convergence sheet for the WIDE GLIDER paper-plane redesign.

ONE production build (KEEL GLIDER, converged from Round-1 winner V5) shown at:
  * hero 130px on a soft day sky AND a night sky (folds read in colour),
  * the in-game truth-test scale: 40px NEAREST x3 magnified, level + dive, on
    BOTH a day sky and a night sky.
The 40px NEAREST read is the honest gameplay silhouette (smoothscale flatters
tiny detail that vanishes in motion); day+night proves the baked self-rim holds
value on either backdrop, and a pale PILLAR strip checks the day value guard.
The CURRENT dollar dart leads for an apples-to-apples "different silhouette"
check. Headless (SDL dummy) so it runs in CI / on the build box.
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
    "glider_wide_skins", os.path.join(_here, "glider_wide_skins.py"))
glider_wide_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(glider_wide_skins)

# Current production dart, for an apples-to-apples "different silhouette" check.
from game import animal_paper_plane as prod

PROD_GLIDER = glider_wide_skins.BUILDERS["skin_glider_wide"]


# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 70

# Day + night skies sampled to mirror the game's biome interpolation poles.
DAY_TOP, DAY_BOT = (150, 198, 238), (206, 226, 240)
NIGHT_TOP, NIGHT_BOT = (24, 26, 52), (44, 34, 64)
# A pale sandstone pillar value, to verify the day value guard (the brightest
# manila must not flare out against it).
PILLAR = (224, 210, 178)
SHEET_TOP, SHEET_BOT = (20, 22, 44), (36, 28, 56)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
CURRENT_EDGE = (120, 124, 150)
HERO_EDGE = (220, 200, 150)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)

HERO_PX = 130
GAME_PX = 40
MAG = 3

SHEET_W = 1180
SHEET_H = 760

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_TOP[i] + (SHEET_BOT[i] - SHEET_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — PAPER PLANE redesign · WIDE GLIDER · Round 2 (KEEL GLIDER · production)",
    True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "ONE ship-ready build. HERO 130px (day+night) · 40px NEAREST x3 level / dive on DAY, NIGHT and a pale PILLAR — the honest gameplay read.",
    True, SUB), (PAD, 48))


def _vgrad(w, h, top, bot):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / max(1, h - 1)
        s.fill(tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)),
               (0, y, w, 1))
    return s


def _night_panel(w, h, idx):
    s = _vgrad(w, h, NIGHT_TOP, NIGHT_BOT)
    import random
    rng = random.Random(idx * 7 + 3)
    for _ in range(int(w * h / 360)):
        sx = rng.randint(2, w - 2)
        sy = rng.randint(2, h - 2)
        b = rng.randint(120, 220)
        pygame.draw.circle(s, (b, b, min(255, b + 24)), (sx, sy), 1)
    return s


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


# ── Top row: HERO 130px on day and night, plus the CURRENT dart for contrast ─
top_y = HEADER_H + PAD
hero_card = pygame.Rect(PAD, top_y, 760, 250)
pygame.draw.rect(sheet, CARD_BG, hero_card, border_radius=12)
pygame.draw.rect(sheet, HERO_EDGE, hero_card, 2, border_radius=12)
sheet.blit(F_NAME.render("KEEL GLIDER — production", True, HERO_EDGE),
           (hero_card.x + 16, hero_card.y + 10))
sheet.blit(F_FEAT.render(
    "nose-RIGHT · bold lit keel ridge vs hard-shadow shelf · two crisp rear points · warm manila held below white",
    True, SUB), (hero_card.x + 16, hero_card.y + 36))

for j, (label, mkpanel, txt) in enumerate((
        ("HERO · DAY", lambda w, h: _vgrad(w, h, DAY_TOP, DAY_BOT), (40, 50, 70)),
        ("HERO · NIGHT", lambda w, h: _night_panel(w, h, 99), (210, 214, 240)))):
    panel = pygame.Rect(hero_card.x + 20 + j * 366, hero_card.y + 60, 350, 176)
    sheet.blit(mkpanel(panel.w, panel.h), panel.topleft)
    pygame.draw.rect(sheet, CARD_EDGE, panel, 1, border_radius=10)
    sheet.blit(F_TAG.render(label, True, txt), (panel.x + 8, panel.y + 6))
    hero = smooth(PROD_GLIDER, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=panel.center))

# CURRENT dart reference card (different-silhouette check).
cur_card = pygame.Rect(PAD + 778, top_y, SHEET_W - (PAD + 778) - PAD, 250)
pygame.draw.rect(sheet, CARD_BG, cur_card, border_radius=12)
pygame.draw.rect(sheet, CURRENT_EDGE, cur_card, 2, border_radius=12)
sheet.blit(F_NAME.render("CURRENT", True, CURRENT_EDGE), (cur_card.x + 16, cur_card.y + 10))
sheet.blit(F_FEAT.render("dollar dart — narrow forward triangle", True, SUB),
           (cur_card.x + 16, cur_card.y + 36))
cpanel = pygame.Rect(cur_card.x + 20, cur_card.y + 60, cur_card.w - 40, 176)
sheet.blit(_vgrad(cpanel.w, cpanel.h, DAY_TOP, DAY_BOT), cpanel.topleft)
pygame.draw.rect(sheet, CARD_EDGE, cpanel, 1, border_radius=10)
chero = smooth(prod.get_paper_plane, 0, 0, HERO_PX)
sheet.blit(chero, chero.get_rect(center=cpanel.center))

# ── Bottom row: 40px NEAREST x3, level + dive, on DAY / NIGHT / PILLAR ────────
bot_y = top_y + 250 + PAD
truth_card = pygame.Rect(PAD, bot_y, SHEET_W - 2 * PAD, SHEET_H - bot_y - PAD)
pygame.draw.rect(sheet, CARD_BG, truth_card, border_radius=12)
pygame.draw.rect(sheet, HERO_EDGE, truth_card, 2, border_radius=12)
sheet.blit(F_NAME.render("40px NEAREST x3 — the honest gameplay read", True, TEXT),
           (truth_card.x + 16, truth_card.y + 10))
sheet.blit(F_FEAT.render(
    "level (frame 2, 0deg) + dive (frame 1, -32deg). Day, night, and a pale sandstone pillar — keel + wide span must hold; brightest manila must not flare.",
    True, SUB), (truth_card.x + 16, truth_card.y + 34))

cols = (
    ("DAY", lambda w, h: _vgrad(w, h, DAY_TOP, DAY_BOT), (40, 50, 70)),
    ("NIGHT", lambda w, h: _night_panel(w, h, 5), (210, 214, 240)),
    ("PILLAR (day)", lambda w, h: _vgrad(w, h, PILLAR, tuple(max(0, c - 22) for c in PILLAR)), (60, 44, 24)),
)
col_w = (truth_card.w - 40 - 2 * 16) // 3
for j, (label, mkpanel, txt) in enumerate(cols):
    panel = pygame.Rect(truth_card.x + 20 + j * (col_w + 16),
                        truth_card.y + 62, col_w, truth_card.h - 80)
    sheet.blit(mkpanel(panel.w, panel.h), panel.topleft)
    pygame.draw.rect(sheet, CARD_EDGE, panel, 1, border_radius=10)
    sheet.blit(F_TAG.render(label, True, txt), (panel.x + 8, panel.y + 6))

    n_level = nearest40(PROD_GLIDER, 2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.centerx, panel.y + 78)))
    sheet.blit(F_TAG.render("level", True, txt),
               (n_level.get_rect(center=(panel.centerx, panel.y + 78)).centerx - 14,
                panel.y + 78 + 60))

    n_dive = nearest40(PROD_GLIDER, 1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.centerx, panel.bottom - 70)))
    sheet.blit(F_TAG.render("dive", True, txt),
               (n_dive.get_rect(center=(panel.centerx, panel.bottom - 70)).centerx - 12,
                panel.bottom - 18))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
