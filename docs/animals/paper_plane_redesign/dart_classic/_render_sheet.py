"""Round-2 review sheet for the CLASSIC DART paper-plane skin — final build.

The art-director picked v3 (DEEP-KEEL RAZOR); this is the converged single
production build. It is shown at hero 130px AND at the in-game truth-test scale
(40px, level + dive tilt) with a NEAREST-NEIGHBOR x3 magnification so the true
gameplay-pixel silhouette is honest (smoothscale flatters tiny detail that
vanishes in motion).

Three sky cases, because a white paper dart has three failure modes:
  * DAY open sky — risks washing out on bright blue.
  * DAY over a PALE PILLAR — the hardest day case; if the rim alone separates
    the dart from pale sandstone, the keel isn't dark enough.
  * NIGHT — risks dimming on dark sky; the keel must still read as a FOLD (the
    lighter inner lip), not a detached wedge.

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
    "dart_classic_skins", os.path.join(_here, "dart_classic_skins.py"))
dart_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dart_skins)

getter = dart_skins.BUILDERS["skin_dart_classic"]

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 16
HEADER_H = 78
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Day sky (Skybit-ish noon blue), pale sandstone pillar, and night sky.
DAY_TOP, DAY_BOT = (150, 200, 240), (205, 232, 248)
PILLAR_TOP, PILLAR_BOT = (232, 214, 178), (210, 188, 150)   # pale sandstone
NIGHT_TOP, NIGHT_BOT = (24, 26, 52), (40, 30, 60)
SHEET_BG_T, SHEET_BG_B = (18, 20, 38), (30, 24, 46)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)

SHEET_W = PAD + 760 + PAD
SHEET_H = HEADER_H + PAD + 2 * (210 + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_T[i] + (SHEET_BG_B[i] - SHEET_BG_T[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 26, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — PAPER PLANE · CLASSIC DART · Round 2 (production build)", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "Converged v3 DEEP-KEEL RAZOR: fuller trailing chord, dark keel, hard 1px crease + lighter inner lip. Nose RIGHT.",
    True, SUB), (PAD, 40))
sheet.blit(F_SUB.render(
    "HERO 130px | 40px level+dive, smooth + NEAREST x3 (the honest gameplay read) over DAY / pale PILLAR / NIGHT.",
    True, SUB), (PAD, 58))


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
        crop, (max(1, int(crop.get_width() * fac)), max(1, int(crop.get_height() * fac))))


def nearest40(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def grad_panel(rect, top, bot):
    p = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, y), (rect.w, y))
    sheet.blit(p, rect.topleft)


def sky_block(panel, top, bot, label, stars=False):
    """Smooth 40px (level/dive) on top, NEAREST x3 (level/dive) below, each
    read judged over the real sky."""
    grad_panel(panel, top, bot)
    if stars:
        import random
        rng = random.Random(3)
        for _ in range(40):
            sx = panel.x + rng.randint(4, panel.w - 4)
            sy = panel.y + rng.randint(4, panel.h - 4)
            b = rng.randint(120, 210)
            pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)
    pygame.draw.rect(sheet, CARD_EDGE, panel, 1, border_radius=8)
    tag_col = TEXT if stars else (40, 40, 30)

    g_level = smooth(2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(panel.x + 40, panel.y + 34)))
    g_dive = smooth(1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(panel.x + 96, panel.y + 34)))

    n_level = nearest40(2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.x + 48, panel.y + 112)))
    n_dive = nearest40(1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 124, panel.y + 112)))

    sheet.blit(F_TAG.render(label, True, tag_col), (panel.x + 8, panel.y + 6))
    sheet.blit(F_TAG.render("smooth", True, tag_col), (panel.x + 8, panel.y + 56))
    sheet.blit(F_TAG.render("NEAREST x3  (level / dive)", True, tag_col),
               (panel.x + 8, panel.bottom - 18))


# ── Row 1: hero + DAY open sky + pale PILLAR day case ────────────────────────
cx = PAD
cy = HEADER_H + PAD
card = pygame.Rect(cx, cy, 760, 210)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)
sheet.blit(F_NAME.render("DAY READ", True, TEXT), (cx + 14, cy + 8))
sheet.blit(F_FEAT.render("hero | open day sky | pale sandstone pillar (hardest day case)", True, SUB),
           (cx + 14, cy + 32))

hero_panel = pygame.Rect(cx + 14, cy + 56, 150, 142)
grad_panel(hero_panel, NIGHT_TOP, NIGHT_BOT)
pygame.draw.rect(sheet, CARD_EDGE, hero_panel, 1, border_radius=8)
hero = smooth(0, 0, HERO_PX)
sheet.blit(hero, hero.get_rect(center=hero_panel.center))
sheet.blit(F_TAG.render("HERO 130px", True, TEXT),
           (hero_panel.x + 6, hero_panel.bottom - 18))

day_panel = pygame.Rect(cx + 178, cy + 56, 280, 142)
pillar_panel = pygame.Rect(cx + 470, cy + 56, 280, 142)
sky_block(day_panel, DAY_TOP, DAY_BOT, "DAY  (open sky)", stars=False)
sky_block(pillar_panel, PILLAR_TOP, PILLAR_BOT, "DAY  (pale PILLAR)", stars=False)

# ── Row 2: NIGHT read ────────────────────────────────────────────────────────
cy2 = HEADER_H + PAD + (210 + PAD)
card2 = pygame.Rect(cx, cy2, 760, 210)
pygame.draw.rect(sheet, CARD_BG, card2, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card2, 2, border_radius=12)
sheet.blit(F_NAME.render("NIGHT READ", True, TEXT), (cx + 14, cy2 + 8))
sheet.blit(F_FEAT.render("keel must read as a connected FOLD (lighter inner lip), not a detached wedge", True, SUB),
           (cx + 14, cy2 + 32))

hero2 = pygame.Rect(cx + 14, cy2 + 56, 150, 142)
grad_panel(hero2, DAY_TOP, DAY_BOT)
pygame.draw.rect(sheet, CARD_EDGE, hero2, 1, border_radius=8)
h2 = smooth(0, 0, HERO_PX)
sheet.blit(h2, h2.get_rect(center=hero2.center))
sheet.blit(F_TAG.render("HERO 130px (day sky)", True, (40, 40, 30)),
           (hero2.x + 6, hero2.bottom - 18))

night_a = pygame.Rect(cx + 178, cy2 + 56, 280, 142)
night_b = pygame.Rect(cx + 470, cy2 + 56, 280, 142)
sky_block(night_a, NIGHT_TOP, NIGHT_BOT, "NIGHT", stars=True)
sky_block(night_b, (16, 18, 40), (28, 20, 44), "NIGHT  (deep)", stars=True)


out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
