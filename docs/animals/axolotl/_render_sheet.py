"""Round-3 review sheet for the single production AXOLOTL skin.

Round 1 was a 5-up exploration; rounds 2–3 proof ONE converged design hard,
the way the art-director asked:

  * HERO 130px on a white field FIRST (the rim must survive near-white-on-pale),
    then on the real in-game bright-day and night skies.
  * 40px NEAREST x3 of BOTH the level pose AND the dive pose, on bright-day AND
    night backdrops — the honest gameplay-pixel read.
  * a down-pose vs up-pose strip so the crown's tight→bloom pulse is checkable.

Sky colours are lifted from game/biome.py keyframes (DAY phase 0.0, NIGHT phase
0.64) so "bright-day AND night" means the actual shipped skies, not a guess.
Headless (SDL dummy).
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import importlib.util
import random
import pygame

pygame.init()
pygame.display.set_mode((1, 1))
pygame.font.init()

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "axolotl_skins", os.path.join(_here, "axolotl_skins.py"))
axolotl_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(axolotl_skins)

getter = axolotl_skins.get_axolotl
build = axolotl_skins.build_axolotl

# ── honest in-game skies (game/biome.py keyframes) ───────────────────────────
DAY_TOP, DAY_BOT = (40, 110, 200), (170, 220, 245)      # bright cyan day
NIGHT_TOP, NIGHT_BOT = (5, 8, 30), (35, 55, 115)        # moonlit night
WHITE_TOP, WHITE_BOT = (252, 252, 255), (236, 240, 248)  # pale stress field

GAME_PX = 40
MAG = 5
HERO_PX = 130

INK = (236, 232, 244)
SUB = (176, 164, 198)
TAG = (210, 200, 150)
PANEL_EDGE = (96, 76, 116)

F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_H = pygame.font.SysFont("Arial", 16, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)


def _grad(target, rect, top, bot):
    for y in range(rect.height):
        t = y / max(1, rect.height)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(target, col, (rect.x, rect.y + y), (rect.right, rect.y + y))


def _stars(target, rect, seed):
    rng = random.Random(seed)
    for _ in range(int(rect.width * rect.height / 260)):
        sx = rng.randint(rect.x, rect.right - 1)
        sy = rng.randint(rect.y, rect.bottom - 1)
        b = rng.randint(150, 235)
        target.set_at((sx, sy), (b, b, min(255, b + 25)))


def _crop(frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(frame_idx, tilt, px):
    crop = _crop(frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest(frame_idx, tilt, px, mag):
    small = smooth(frame_idx, tilt, px)
    return pygame.transform.scale(small, (small.get_width() * mag, small.get_height() * mag))


# ── layout ───────────────────────────────────────────────────────────────────
W, H = 1180, 760
sheet = pygame.Surface((W, H))
_grad(sheet, sheet.get_rect(), (26, 22, 38), (42, 28, 50))

sheet.blit(F_TITLE.render("Skybit — AXOLOTL Store Skin · Round 3 (production build)",
                          True, INK), (24, 16))
sheet.blit(F_SUB.render(
    "skin_axolotl · leucistic antler-crown · 1px #A03A5E rim · 5-fork crown (3/2) · 3-dot face."
    "  Crown bloom capped ~98°; tines 2px full-length; dive face = 3 dots.", True, SUB), (24, 48))

# ── row 1: hero on WHITE | DAY | NIGHT ───────────────────────────────────────
hero_y = 78
hero_w = 360
for i, (label, top, bot, starseed) in enumerate((
        ("HERO 130px · WHITE stress field", WHITE_TOP, WHITE_BOT, None),
        ("HERO 130px · in-game DAY sky", DAY_TOP, DAY_BOT, None),
        ("HERO 130px · in-game NIGHT sky", NIGHT_TOP, NIGHT_BOT, 11))):
    px = 24 + i * (hero_w + 8)
    panel = pygame.Rect(px, hero_y, hero_w, 210)
    _grad(sheet, panel, top, bot)
    if starseed is not None:
        _stars(sheet, panel, starseed)
    pygame.draw.rect(sheet, PANEL_EDGE, panel, 1, border_radius=8)
    hero = smooth(0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=panel.center))
    lab_col = (40, 44, 64) if i == 0 else (235, 240, 250)
    sheet.blit(F_TAG.render(label, True, lab_col), (panel.x + 8, panel.y + 6))

# ── row 2: 40px NEAREST x3 — level + dive, on DAY and NIGHT ───────────────────
mag_y = hero_y + 230
sheet.blit(F_H.render("40px gameplay read — NEAREST x5 (level + dive)", True, INK),
           (24, mag_y))
strip_y = mag_y + 26
strip_w = 568
for i, (label, top, bot, starseed) in enumerate((
        ("in-game DAY sky", DAY_TOP, DAY_BOT, None),
        ("in-game NIGHT sky", NIGHT_TOP, NIGHT_BOT, 23))):
    px = 24 + i * (strip_w + 8)
    panel = pygame.Rect(px, strip_y, strip_w, 200)
    _grad(sheet, panel, top, bot)
    if starseed is not None:
        _stars(sheet, panel, starseed)
    pygame.draw.rect(sheet, PANEL_EDGE, panel, 1, border_radius=8)
    lab_col = (235, 240, 250) if i == 1 else (40, 44, 64)
    sheet.blit(F_TAG.render(label, True, lab_col), (panel.x + 8, panel.y + 6))
    n_level = nearest(2, 0, GAME_PX, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.x + 150, panel.centery + 6)))
    n_dive = nearest(1, -32, GAME_PX, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 410, panel.centery + 6)))
    sheet.blit(F_TAG.render("LEVEL", True, lab_col), (panel.x + 122, panel.bottom - 22))
    sheet.blit(F_TAG.render("DIVE", True, lab_col), (panel.x + 388, panel.bottom - 22))

# ── row 3: pulse strip — down-pose (tight) vs up-pose (bloom) at 40px x5 ──────
pulse_y = strip_y + 220
sheet.blit(F_H.render("Crown pulse — down-pose (tight ~30°) → up-pose (bloom ~98° capped)",
                      True, INK), (24, pulse_y))
ppanel = pygame.Rect(24, pulse_y + 26, W - 48, 96)
_grad(sheet, ppanel, (60, 52, 78), (40, 34, 56))
pygame.draw.rect(sheet, PANEL_EDGE, ppanel, 1, border_radius=8)
labels = ("down 50°", "20°", "-10°", "up -40°")
for fi in range(4):
    n = nearest(fi, 0, GAME_PX, MAG)
    cx = ppanel.x + 90 + fi * 150
    sheet.blit(n, n.get_rect(center=(cx, ppanel.centery)))
    sheet.blit(F_TAG.render(labels[fi], True, TAG), (cx - 24, ppanel.bottom - 18))
# hero down vs up side by side on the right for clarity
hd = smooth(0, 0, 86)
hu = smooth(3, 0, 86)
sheet.blit(hd, hd.get_rect(center=(ppanel.right - 150, ppanel.centery)))
sheet.blit(hu, hu.get_rect(center=(ppanel.right - 60, ppanel.centery)))

out_path = os.path.join(_here, "round_3.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
