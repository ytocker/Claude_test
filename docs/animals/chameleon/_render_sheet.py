"""Round-2 review sheet for the production CHAMELEON Store skin.

ONE converged design (v3 SPOTTED PANTHER, refined). Shows the hero at 130px on
BOTH bright-day and night, then ALL 4 flap frames at 40px NEAREST x4 on BOTH
backdrops so the per-frame mood-shift (teal→violet→coral→amber) is honest in
motion, plus a level + dive 40px NEAREST read. Headless (SDL dummy) for CI.
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
    "chameleon_skins", os.path.join(_here, "chameleon_skins.py"))
chameleon_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chameleon_skins)

get = chameleon_skins.BUILDERS["skin_chameleon"]

# ── palette / layout ─────────────────────────────────────────────────────────
HERO_PX = 130
GAME_PX = 40
MAG = 4

DAY_TOP, DAY_BOT = (150, 206, 235), (205, 232, 246)
NIGHT_TOP, NIGHT_BOT = (22, 24, 50), (40, 30, 60)
BG_TOP, BG_BOT = (16, 17, 34), (26, 22, 46)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
PANEL = (12, 13, 28)

SHEET_W, SHEET_H = 760, 660
sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    sheet.fill(tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)),
               (0, y, SHEET_W, 1))

import random
rng = random.Random(11)
for _ in range(140):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)
F_FRAME = pygame.font.SysFont("Arial", 11, bold=True)

sheet.blit(F_TITLE.render("Skybit — CHAMELEON Store Skin · Round 2 (converged)", True, TEXT), (16, 12))
sheet.blit(F_SUB.render(
    "v3 SPOTTED PANTHER refined · mood band teal→violet→coral→amber, one stop per frame · "
    "constant teal anchor · 40px NEAREST x4 honest read.",
    True, SUB), (16, 42))


def _swatch(top, bot, w, h):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        s.fill(tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)), (0, y, w, 1))
    return s


def _crop(frame_idx, tilt):
    s = get(frame_idx, tilt)
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


def nearest(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(small, (small.get_width() * mag, small.get_height() * mag))


# ── HERO row: 130px on DAY + NIGHT ───────────────────────────────────────────
hy = 70
day_p = pygame.Rect(16, hy, 168, 168)
night_p = pygame.Rect(192, hy, 168, 168)
sheet.blit(_swatch(DAY_TOP, DAY_BOT, day_p.w, day_p.h), day_p.topleft)
sheet.blit(_swatch(NIGHT_TOP, NIGHT_BOT, night_p.w, night_p.h), night_p.topleft)
for p, lab, col in ((day_p, "HERO 130px · DAY", (40, 60, 90)),
                    (night_p, "HERO 130px · NIGHT", SUB)):
    pygame.draw.rect(sheet, CARD_EDGE, p, 1, border_radius=8)
    sheet.blit(F_TAG.render(lab, True, col), (p.x + 6, p.bottom - 18))
hero = smooth(3, 0, HERO_PX)            # up-pose hero so the tongue flick shows
sheet.blit(hero, hero.get_rect(center=day_p.center))
sheet.blit(hero, hero.get_rect(center=night_p.center))

# Notes panel beside the hero.
np = pygame.Rect(372, hy, SHEET_W - 372 - 16, 168)
pygame.draw.rect(sheet, CARD_BG, np, border_radius=10)
pygame.draw.rect(sheet, CARD_EDGE, np, 1, border_radius=10)
notes = [
    "Mood band = 3 white/mood bars + spot cluster flush TOGETHER",
    "Constant teal anchor: body, rim, head, snout never shift",
    "Casque = wide-base scalloped HEAD-crest (gold)",
    "Turret catchlight (1px white) guaranteed every pose + dive",
    "Tongue: coral dart, up-pose ONLY (the one warm accent)",
    "Tail coil keeps one pixel of open centre",
    "Key light top-left (sheen + crest edge + glint)",
]
sheet.blit(F_NAME.render("skin_chameleon", True, TEXT), (np.x + 12, np.y + 10))
for i, line in enumerate(notes):
    sheet.blit(F_SUB.render("• " + line, True, SUB), (np.x + 12, np.y + 38 + i * 18))

# ── MOTION rows: all 4 frames at 40px NEAREST x4 on DAY then NIGHT ───────────
labels = ["f0 · teal", "f1 · violet", "f2 · coral", "f3 · amber"]


def motion_row(top, bot, y, lab):
    row = pygame.Rect(16, y, SHEET_W - 32, 150)
    sheet.blit(_swatch(top, bot, row.w, row.h), row.topleft)
    pygame.draw.rect(sheet, CARD_EDGE, row, 1, border_radius=8)
    sheet.blit(F_TAG.render(lab, True, SUB if top is NIGHT_TOP else (40, 60, 90)),
               (row.x + 8, row.y + 6))
    for fi in range(4):
        n = nearest(fi, 0, MAG)
        cx = row.x + 80 + fi * 130
        sheet.blit(n, n.get_rect(center=(cx, row.y + 78)))
        sheet.blit(F_FRAME.render(labels[fi], True, TEXT),
                   F_FRAME.render(labels[fi], True, TEXT).get_rect(center=(cx, row.bottom - 16)))
    # Dive read on the far right.
    nd = nearest(1, -32, MAG)
    cx = row.x + 80 + 4 * 130 - 30
    sheet.blit(nd, nd.get_rect(center=(cx, row.y + 78)))
    sheet.blit(F_FRAME.render("dive", True, (255, 210, 150)),
               F_FRAME.render("dive", True, (255, 210, 150)).get_rect(center=(cx, row.bottom - 16)))


motion_row(DAY_TOP, DAY_BOT, 252, "40px NEAREST x4 · 4 mood frames + dive · DAY")
motion_row(NIGHT_TOP, NIGHT_BOT, 418, "40px NEAREST x4 · 4 mood frames + dive · NIGHT")

# ── Level/dive smooth strip at the bottom for a clean silhouette read. ───────
strip = pygame.Rect(16, 584, SHEET_W - 32, 60)
pygame.draw.rect(sheet, PANEL, strip, border_radius=8)
sheet.blit(F_TAG.render("40px smooth · level f0 / up f3 / dive", True, SUB),
           (strip.x + 8, strip.y + 4))
for i, (fi, tilt) in enumerate(((0, 0), (3, 0), (1, -32))):
    g = smooth(fi, tilt, GAME_PX)
    sheet.blit(g, g.get_rect(center=(strip.x + 360 + i * 60, strip.centery + 4)))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
