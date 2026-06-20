"""Round-1 review sheet for the candidate PAPER PLANE Store skins.

Renders each dart at hero 130px AND at the in-game truth-test scale (40px,
level + dive) magnified x3 with NEAREST-NEIGHBOR so the true gameplay-pixel
silhouette is honest — and does it twice, once on a DAY sky and once on a
NIGHT sky, because a folded-paper skin's value structure must hold against
both. Headless (SDL dummy) so it runs in CI / on the build box.
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

BUILDERS = pp.BUILDERS
LABELS = pp.LABELS
ORDER = ["v1_notebook", "v2_lined", "v3_newspaper", "v4_dollar", "v5_kraft"]

# ── layout ───────────────────────────────────────────────────────────────────
CARD_W, CARD_H = 720, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Day + night sky swatches (the two real backdrops a flyer must survive).
DAY_TOP = (150, 206, 240)
DAY_BOT = (236, 222, 188)
NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)

CARD_BG = (16, 17, 34)
CARD_EDGE = (190, 150, 70)               # gold rim — this is a premium secret
TEXT = (236, 238, 250)
SUB = (150, 156, 190)

SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + len(ORDER) * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — PAPER PLANE Store Skin · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "Secret premium NON-creature flyer. HERO 130px (day | night) · 40px NEAREST x3 level/dive on DAY and NIGHT. Flap = bank + nose-bob.",
    True, SUB), (PAD, 44))


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
    for _ in range(60):
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


for idx, key in enumerate(ORDER):
    getter = BUILDERS[key]
    name, feat = LABELS[key]
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(name, True, CARD_EDGE), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("40px tell: " + feat, True, SUB), (cx + 14, cy + 36))

    panel_y = cy + 58
    panel_h = 178
    # Four panels across: DAY hero | NIGHT hero | DAY 40px | NIGHT 40px.
    panels = [
        ("DAY hero", DAY_TOP, DAY_BOT, False, "hero"),
        ("NIGHT hero", NIGHT_TOP, NIGHT_BOT, True, "hero"),
        ("DAY 40px x3", DAY_TOP, DAY_BOT, False, "game"),
        ("NIGHT 40px x3", NIGHT_TOP, NIGHT_BOT, True, "game"),
    ]
    pw = 168
    for pi, (tag, top, bot, night, mode) in enumerate(panels):
        px = cx + 14 + pi * (pw + 8)
        prect = pygame.Rect(px, panel_y, pw, panel_h)
        bg = _grad(pw, panel_h, top, bot)
        if night:
            _stars(bg, 3 + pi)
        sheet.blit(bg, prect)
        pygame.draw.rect(sheet, (10, 10, 20), prect, 1, border_radius=8)

        if mode == "hero":
            hero = smooth(getter, 0, 0, HERO_PX)
            sheet.blit(hero, hero.get_rect(center=prect.center))
        else:
            n_level = nearest40(getter, 2, 0, MAG)
            sheet.blit(n_level, n_level.get_rect(center=(prect.x + 52, prect.centery)))
            n_dive = nearest40(getter, 1, -32, MAG)
            sheet.blit(n_dive, n_dive.get_rect(center=(prect.x + 118, prect.centery)))

        tagcol = (245, 245, 250) if night else (30, 34, 50)
        sheet.blit(F_TAG.render(tag, True, tagcol), (prect.x + 6, prect.bottom - 18))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
