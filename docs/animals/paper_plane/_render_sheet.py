"""Round-2 review sheet for the production PAPER PLANE Store skin (DOLLAR-BILL).

Renders the dart at hero 130px (day | night) AND at the in-game truth-test
scale (40px, level + dive) magnified x3 with NEAREST-NEIGHBOR so the true
gameplay-pixel silhouette is honest — twice, once on a DAY sky and once on a
NIGHT sky, because a folded-paper skin's value structure must hold against
both. Headless (SDL dummy) so it runs in CI / on the build box.

Each 40px cell shows exactly ONE silhouette in its pose: the level cell and the
dive cell live in separate sub-panels so they can never overlap into a broken
double-image.
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
    "paper_plane_skins", os.path.join(_here, "paper_plane_skins.py"))
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)

# Hero panels use the size-only gold flourish; 40px panels use the production
# getter so the truth-test matches exactly what ships.
HERO_GETTER = pp.get_paper_plane_hero
GAME_GETTER = pp.get_paper_plane

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

DAY_TOP = (150, 206, 240)
DAY_BOT = (236, 222, 188)
NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)

CARD_BG = (16, 17, 34)
CARD_EDGE = (190, 150, 70)               # gold rim — this is a premium secret
TEXT = (236, 238, 250)
SUB = (150, 156, 190)

# Geometry. One wide card. Six panels in a row:
#   DAY hero | NIGHT hero | DAY level | DAY dive | NIGHT level | NIGHT dive
HERO_PW = 168
GAME_PW = 132
PANEL_H = 178
GAP = 8

CARD_W = 14 + HERO_PW + GAP + HERO_PW + GAP + GAME_PW * 4 + GAP * 3 + 14
CARD_H = 58 + PANEL_H + 16

SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + CARD_H + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — PAPER PLANE Store Skin · Round 2 (DOLLAR-BILL)", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Production build. HERO 130px (day | night) · 40px NEAREST x3 — ONE silhouette per cell: level + dive, on DAY and NIGHT. Flap = banked nose-bob.",
    True, SUB), (PAD, 48))


def _grad(w, h, top, bot):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        s.set_at((0, y), tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    return pygame.transform.scale(s.subsurface((0, 0, 1, h)), (w, h))


def _stars(surf, seed):
    import random
    rng = random.Random(seed)
    w, h = surf.get_size()
    for _ in range(50):
        sx, sy = rng.randint(0, w), rng.randint(0, h)
        b = rng.randint(120, 220)
        pygame.draw.circle(surf, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))


def _crop(getter, frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(getter, frame_idx, tilt, target_px):
    crop = _crop(getter, frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    fac = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * fac)), max(1, int(crop.get_height() * fac))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(small, (small.get_width() * mag, small.get_height() * mag))


cx = PAD
cy = HEADER_H + PAD

card = pygame.Rect(cx, cy, CARD_W, CARD_H)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)

sheet.blit(F_NAME.render("DOLLAR-BILL DART", True, CARD_EDGE), (cx + 14, cy + 10))
sheet.blit(F_FEAT.render(
    "40px tell: green dart + HARD-fold value break (bright top facet / dark under-fold) + ringed portrait medallion + baked self-rim",
    True, SUB), (cx + 14, cy + 36))

panel_y = cy + 58

# Each entry: (tag, top, bot, night, mode). One pose per panel for the 40px
# cells so there is never an overlapping double-image.
panels = [
    ("DAY hero",     DAY_TOP,   DAY_BOT,   False, "hero", HERO_PW),
    ("NIGHT hero",   NIGHT_TOP, NIGHT_BOT, True,  "hero", HERO_PW),
    ("DAY 40px lvl", DAY_TOP,   DAY_BOT,   False, "level", GAME_PW),
    ("DAY 40px dive", DAY_TOP,  DAY_BOT,   False, "dive",  GAME_PW),
    ("NIGHT 40px lvl", NIGHT_TOP, NIGHT_BOT, True, "level", GAME_PW),
    ("NIGHT 40px dive", NIGHT_TOP, NIGHT_BOT, True, "dive", GAME_PW),
]

px = cx + 14
for tag, top, bot, night, mode, pw in panels:
    prect = pygame.Rect(px, panel_y, pw, PANEL_H)
    bg = _grad(pw, PANEL_H, top, bot)
    if night:
        _stars(bg, hash(tag) & 0xff)
    sheet.blit(bg, prect)
    pygame.draw.rect(sheet, (10, 10, 20), prect, 1, border_radius=8)

    if mode == "hero":
        hero = smooth(HERO_GETTER, 0, 0, HERO_PX)
        sheet.blit(hero, hero.get_rect(center=prect.center))
    elif mode == "level":
        spr = nearest40(GAME_GETTER, 2, 0, MAG)        # level pose, no tilt
        sheet.blit(spr, spr.get_rect(center=prect.center))
    else:  # dive
        spr = nearest40(GAME_GETTER, 1, -32, MAG)      # dive pose, nose-down tilt
        sheet.blit(spr, spr.get_rect(center=prect.center))

    tagcol = (245, 245, 250) if night else (30, 34, 50)
    sheet.blit(F_TAG.render(tag, True, tagcol), (prect.x + 6, prect.bottom - 18))
    px += pw + GAP

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
