"""Round-2 convergence sheet for the AEROBATIC TEAM JET · BLUE ANGEL.

ONE production build now. Renders the refined design as a HERO 130px on a DAY
sky and a NIGHT sky, then the in-game truth-test scale (40px, level + dive) at
NEAREST-NEIGHBOR x3 magnification on BOTH a day and a night card — so the gold
spear's downscale survival and the cool self-rim's night-sky hold are honest
(smoothscale flatters tiny detail that vanishes in motion). Headless (SDL
dummy) so it runs in CI / on the build box.

The skin build draws a FLAT, NOSE-RIGHT, UPRIGHT planform (the game applies the
inverted nose-up secret-skin spin later). To preview the real in-game attitude,
this sheet applies the production 205° spin to each frame before scaling —
mirroring game/animal_jet_fighter.build_jet_fighter's final rotate.
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
    "aerobatic_skins", os.path.join(_here, "aerobatic_skins.py"))
aerobatic_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(aerobatic_skins)

getter = aerobatic_skins.BUILDERS["skin_aerobatic"]

# Secret-skin attitude: the flat planform is spun to the cocky inverted
# nose-high pose the game uses, so the preview matches gameplay.
JET_SPIN = 205

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 16
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

CARD_BG   = (16, 17, 34)
CARD_EDGE = (200, 158, 64)               # gold rim (priciest skin)
TEXT      = (236, 238, 250)
SUB       = (150, 156, 190)
HERO_DAY   = (150, 190, 232)             # bright day-sky panel
HERO_NIGHT = (20, 22, 46)                # night-sky panel
DAY_SKY    = (118, 162, 212)
NIGHT_SKY  = (12, 13, 28)

SHEET_W = PAD + 760 + PAD
SHEET_H = HEADER_H + PAD + 470 + PAD

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int((26, 28, 56)[i] + ((44, 34, 64)[i] - (26, 28, 56)[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(220):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB   = pygame.font.SysFont("Arial", 15)
F_NAME  = pygame.font.SysFont("Arial", 21, bold=True)
F_FEAT  = pygame.font.SysFont("Arial", 13)
F_TAG   = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — JET redesign · AEROBATIC TEAM JET · Round 2 (SHIP)", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "v1 · BLUE ANGEL converged: ONE dominant GOLD spear, near-pure navy body, baked cool self-rim, small cool burner.",
    True, SUB), (PAD, 42))


def _spun(frame_idx, tilt):
    s = getter(frame_idx, tilt)
    s = pygame.transform.rotate(s, JET_SPIN)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(frame_idx, tilt, target_px):
    crop = _spun(frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    f = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _hero_panel(rect, bg, label):
    pygame.draw.rect(sheet, bg, rect, border_radius=10)
    hero = smooth(0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=rect.center))
    sheet.blit(F_TAG.render(label, True, (40, 40, 40) if bg[0] > 100 else SUB),
               (rect.x + 8, rect.bottom - 18))


def _game_panel(rect, daynight):
    bg = DAY_SKY if daynight == "DAY" else NIGHT_SKY
    pygame.draw.rect(sheet, bg, rect, border_radius=10)
    g_level = smooth(2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(rect.x + 44, rect.y + 34)))
    g_dive = smooth(1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(rect.x + 110, rect.y + 34)))
    tag_col = (30, 30, 40) if daynight == "DAY" else SUB
    sheet.blit(F_TAG.render(daynight + " 40px (level / dive)", True, tag_col),
               (rect.x + 10, rect.y + 62))
    n_level = nearest40(2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(rect.x + 50, rect.y + 128)))
    n_dive = nearest40(1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(rect.x + 128, rect.y + 128)))
    sheet.blit(F_TAG.render("NEAREST x3 — read = 2 values + 1 accent", True, (214, 200, 150)),
               (rect.x + 10, rect.bottom - 18))


cx = PAD
cy = HEADER_H + PAD
card = pygame.Rect(cx, cy, 760, 470)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=14)
pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=14)

sheet.blit(F_NAME.render("v1 · BLUE ANGEL — navy gloss + GOLD nose→spine→tail spear", True, CARD_EDGE),
           (cx + 16, cy + 10))
sheet.blit(F_FEAT.render(
    "tell: ONE bold gold spear · body almost pure navy · cool self-rim holds the night silhouette · burner cool & small",
    True, SUB), (cx + 16, cy + 38))

top = cy + 66
# Hero day + hero night, side by side.
_hero_panel(pygame.Rect(cx + 16, top, 178, 178), HERO_DAY, "130px DAY")
_hero_panel(pygame.Rect(cx + 202, top, 178, 178), HERO_NIGHT, "130px NIGHT")
# Day game panel + night game panel.
_game_panel(pygame.Rect(cx + 388, top, 178, 178), "DAY")
_game_panel(pygame.Rect(cx + 574, top, 170, 178), "NIGHT")

# Bottom strip: 40px truth row repeated larger so the reviewer can eyeball the
# day/night spear hold without squinting.
strip_y = top + 194
sheet.blit(F_TAG.render(
    "40px NEAREST x3 truth-row — DAY then NIGHT, level + dive. Name the livery in under a second = spear is bold enough.",
    True, SUB), (cx + 16, strip_y - 4))
sx = cx + 16
for daynight, bg in (("DAY", DAY_SKY), ("NIGHT", NIGHT_SKY)):
    for fr, tilt, lab in ((2, 0, "level"), (1, -32, "dive")):
        cell = pygame.Rect(sx, strip_y + 16, 176, 150)
        pygame.draw.rect(sheet, bg, cell, border_radius=8)
        n = nearest40(fr, tilt, MAG)
        sheet.blit(n, n.get_rect(center=(cell.centerx, cell.y + 64)))
        tc = (30, 30, 40) if daynight == "DAY" else SUB
        sheet.blit(F_TAG.render(f"{daynight} · {lab}", True, tc), (cell.x + 8, cell.bottom - 18))
        sx += 184

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
