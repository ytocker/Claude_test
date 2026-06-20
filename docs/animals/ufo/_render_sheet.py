"""Round-1 review sheet for the candidate UFO Store skin (5 variants).

Renders each saucer at hero 130px AND at the in-game truth-test scale (40px,
level + dive), magnified NEAREST-NEIGHBOR x3 so the honest gameplay-pixel read
is visible. Critically, the UFO's "flap" is a CHASING RIM-LIGHT CYCLE, so each
card also shows all 4 frames at 40px side by side to prove the chase + beam
pulse reads as motion. Everything is shown on BOTH a bright DAY sky and a NIGHT
sky, since the brief asks the glow to strike hardest at night. Headless (SDL
dummy) so it runs in CI / on the build box.
"""
import os
import sys
import importlib.util
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "ufo_skins", os.path.join(_here, "ufo_skins.py"))
ufo_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ufo_skins)

BUILDERS = ufo_skins.BUILDERS

ORDER = [
    ("V1 · Classic Chrome (cyan/green)",
     "chrome disc + green dome (alien) + cyan rim chase + green beam"),
    ("V2 · Brushed Steel (magenta)",
     "wide flat steel + smoky dome + dense magenta chase · no beam"),
    ("V3 · Matte Stealth (amber)",
     "matte dark + tall amber dome (alien) + amber chase + big beam"),
    ("V4 · Oil-Slick Iridescent",
     "anodised banded metal + crystal dome + prismatic chase"),
    ("V5 · Retro Tin-Toy (Saturn)",
     "cream/red litho + Saturn ring + carnival bulb chase"),
]

# ── layout ───────────────────────────────────────────────────────────────────
CARD_W, CARD_H = 520, 300
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

TEXT = (236, 238, 250)
SUB = (150, 156, 190)
CARD_BG = (16, 17, 34)
CARD_EDGE = (190, 150, 70)          # gold rim — ultra-premium slot

# Day + night sample skies (Skybit interpolates between these over the cycle).
DAY_TOP, DAY_BOT = (150, 205, 240), (208, 226, 234)
NIGHT_TOP, NIGHT_BOT = (20, 22, 48), (44, 30, 60)

COLS = 1
ROWS = len(ORDER)
SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))
rng = random.Random(7)
for _ in range(180):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 12)
F_TAG = pygame.font.SysFont("Arial", 11, bold=True)

sheet.blit(F_TITLE.render("Skybit — UFO Store Skin · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px NEAREST x3 (the honest gameplay read) on DAY + NIGHT · "
    "all 4 frames = the rim-light CHASE / beam pulse (the wingless 'flap').",
    True, SUB), (PAD, 42))


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


def _sky_patch(w, h, top, bot, seed):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        s.fill(tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)),
               pygame.Rect(0, y, w, 1))
    r = random.Random(seed)
    if top[0] < 60:                      # stars only on the night patch
        for _ in range(int(w * h / 280)):
            r2 = r.randint(0, w), r.randint(0, h)
            b = r.randint(120, 220)
            pygame.draw.circle(s, (b, b, min(255, b + 25)), r2, 1)
    return s


for idx, (key, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(key, True, CARD_EDGE), (cx + 14, cy + 8))
    sheet.blit(F_FEAT.render(feat, True, SUB), (cx + 14, cy + 32))

    # ── hero panels: 130px on a DAY sky and a NIGHT sky (side by side) ──
    hy = cy + 52
    for j, (top, bot, lbl) in enumerate(
            ((DAY_TOP, DAY_BOT, "DAY"), (NIGHT_TOP, NIGHT_BOT, "NIGHT"))):
        hp = pygame.Rect(cx + 14 + j * 116, hy, 108, 156)
        patch = _sky_patch(hp.w, hp.h, top, bot, 11 + j)
        sheet.blit(patch, hp)
        pygame.draw.rect(sheet, (60, 64, 110), hp, 1, border_radius=8)
        hero = smooth(getter, 0, 0, HERO_PX)
        sheet.blit(hero, hero.get_rect(center=hp.center))
        sheet.blit(F_TAG.render(lbl + " 130px", True, TEXT), (hp.x + 6, hp.bottom - 16))

    # ── chase strip: all 4 frames at 40px NEAREST x3 on DAY then NIGHT ──
    gx = cx + 14 + 2 * 116 + 8
    gp = pygame.Rect(gx, hy, CARD_W - (gx - cx) - 14, 156)
    half = gp.h // 2
    for j, (top, bot, lbl) in enumerate(
            ((DAY_TOP, DAY_BOT, "DAY"), (NIGHT_TOP, NIGHT_BOT, "NIGHT"))):
        strip = pygame.Rect(gp.x, gp.y + j * half, gp.w, half - 2)
        patch = _sky_patch(strip.w, strip.h, top, bot, 21 + j)
        sheet.blit(patch, strip)
        pygame.draw.rect(sheet, (60, 64, 110), strip, 1, border_radius=8)
        # 4 chase frames (level) + 1 dive read at the end.
        step = strip.w // 5
        for fi in range(4):
            n = nearest40(getter, fi, 0, MAG)
            sheet.blit(n, n.get_rect(center=(strip.x + step // 2 + fi * step,
                                             strip.y + half // 2 - 4)))
        nd = nearest40(getter, 1, -30, MAG)
        sheet.blit(nd, nd.get_rect(center=(strip.x + step // 2 + 4 * step,
                                           strip.y + half // 2 - 4)))
        sheet.blit(F_TAG.render(lbl + " 40px NEAREST x3 — frames 0·1·2·3  |  dive",
                                True, TEXT), (strip.x + 6, strip.bottom - 15))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
