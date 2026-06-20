"""Round-2 review sheet for the production UFO Store skin (`skin_ufo`).

Renders the single converged saucer at hero 130px AND at the in-game truth-test
scale (40px), magnified NEAREST-NEIGHBOR x3 so the honest gameplay-pixel read
is visible. The UFO's "flap" is a CHASING RIM-LIGHT CYCLE, so the strip shows
all 4 chase frames at 40px side by side plus a dive tilt, to prove the chase +
beam pulse reads as rotation. Everything is shown on the BRIGHTEST DAY-biome
sky (sky_bot ≈ (170,220,245), the band that swallows a near-black disc) AND a
night sky, to confirm the baked keyline holds the silhouette on both. Headless
(SDL dummy) so it runs in CI / on the build box.
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

getter = ufo_skins.BUILDERS["skin_ufo"]

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 78
HERO_PX = 130
GAME_PX = 40
MAG = 3

TEXT = (236, 238, 250)
SUB = (150, 156, 190)
BG = (12, 13, 26)
PANEL_EDGE = (190, 150, 70)          # gold rim — ultra-premium slot

# BRIGHTEST day-biome band vs a night band (biome.py DAY sky_bot / NIGHT).
DAY_TOP, DAY_BOT = (90, 170, 230), (170, 220, 245)    # bright cyan → pale lip
NIGHT_TOP, NIGHT_BOT = (5, 8, 30), (35, 55, 115)

CARD_W = 980
CARD_H = 470
SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + CARD_H + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(BG[i] + (8) * (1 - t)) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — UFO Store Skin (skin_ufo) · Round 2", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "Converged: V3 Matte Stealth AMBER on V1 disc geometry. Wide disc dominates "
    "the dome; baked pale-amber keyline holds the silhouette on the BRIGHTEST",
    True, SUB), (PAD, 44))
sheet.blit(F_SUB.render(
    "day sky; 8-dot rim chase (lit pair = bigger/brighter, dark contour) reads "
    "as rotation; capped pulsing beam; dome = glint over a dark occupant pupil.",
    True, SUB), (PAD, 62))


def _crop(frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(frame_idx, tilt, target_px):
    crop = _crop(frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _sky_patch(w, h, top, bot, seed):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        s.fill(tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)),
               pygame.Rect(0, y, w, 1))
    r = random.Random(seed)
    if top[0] < 40:                      # stars only on the night patch
        for _ in range(int(w * h / 300)):
            r2 = r.randint(0, w), r.randint(0, h)
            b = r.randint(120, 220)
            pygame.draw.circle(s, (b, b, min(255, b + 25)), r2, 1)
    return s


cx = PAD
cy = HEADER_H + PAD
card = pygame.Rect(cx, cy, CARD_W, CARD_H)
pygame.draw.rect(sheet, (18, 19, 38), card, border_radius=14)
pygame.draw.rect(sheet, PANEL_EDGE, card, 3, border_radius=14)

sheet.blit(F_NAME.render("MATTE STEALTH · AMBER  —  production skin_ufo", True, PANEL_EDGE),
           (cx + 16, cy + 10))
sheet.blit(F_FEAT.render(
    "wide disc + low amber dome (glint/pupil) + 8-dot contoured rim chase + "
    "capped pulsing beam + baked keyline", True, SUB), (cx + 16, cy + 36))

# Two rows: DAY (top) then NIGHT (bottom). Each row = hero 130px + chase strip.
row_h = (CARD_H - 64) // 2
for ri, (top, bot, lbl) in enumerate(
        ((DAY_TOP, DAY_BOT, "BRIGHTEST DAY"), (NIGHT_TOP, NIGHT_BOT, "NIGHT"))):
    ry0 = cy + 60 + ri * row_h
    # hero panel
    hp = pygame.Rect(cx + 16, ry0, 196, row_h - 14)
    sheet.blit(_sky_patch(hp.w, hp.h, top, bot, 11 + ri), hp)
    pygame.draw.rect(sheet, (60, 64, 110), hp, 1, border_radius=8)
    hero = smooth(0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hp.center))
    sheet.blit(F_TAG.render(lbl + " · 130px", True, TEXT), (hp.x + 8, hp.bottom - 18))

    # chase strip: frames 0·1·2·3 + dive, 40px NEAREST x3
    gp = pygame.Rect(hp.right + 12, ry0, card.right - 16 - (hp.right + 12), row_h - 14)
    sheet.blit(_sky_patch(gp.w, gp.h, top, bot, 31 + ri), gp)
    pygame.draw.rect(sheet, (60, 64, 110), gp, 1, border_radius=8)
    step = gp.w // 5
    midy = gp.y + (gp.h - 18) // 2
    for fi in range(4):
        n = nearest40(fi, 0, MAG)
        sheet.blit(n, n.get_rect(center=(gp.x + step // 2 + fi * step, midy)))
    nd = nearest40(1, -28, MAG)
    sheet.blit(nd, nd.get_rect(center=(gp.x + step // 2 + 4 * step, midy)))
    sheet.blit(F_TAG.render(
        lbl + " · 40px NEAREST x3 — chase frames 0 · 1 · 2 · 3   |   dive",
        True, TEXT), (gp.x + 8, gp.bottom - 18))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
