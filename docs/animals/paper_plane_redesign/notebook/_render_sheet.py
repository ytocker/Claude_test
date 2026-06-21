"""Round-2 review sheet for the NOTEBOOK PAPER paper-plane redesign.

Single converged production build (`build_notebook`). Renders the hero at 130px
plus the in-game truth-test scale (40px, level + dive tilt) on DAY sky, NIGHT
sky, AND a DAY-GROUND / SANDSTONE-PILLAR case (the contrast trap from round 1),
each with a NEAREST-NEIGHBOR x3 magnification so the true gameplay-pixel
silhouette is honest (smoothscale flatters tiny detail that vanishes in motion).
Backdrop colours are the real `game/biome.py` DAY phase. Headless (SDL dummy).
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
    "notebook_skins", os.path.join(_here, "notebook_skins.py"))
notebook_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(notebook_skins)

getter = notebook_skins.get_notebook

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 16
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Real game/biome.py DAY phase colours.
DAY_SKY_TOP = (90, 170, 230)         # sky_mid → bright cyan
DAY_SKY_BOT = (170, 220, 245)        # sky_bot → pale near-white blue (the trap)
NIGHT_TOP = (26, 28, 56)
NIGHT_BOT = (42, 32, 64)
STONE_LIGHT = (225, 195, 155)        # sunlit sandstone (warm — the off-white trap)
STONE_MID = (175, 140, 105)
STONE_DARK = (95, 70, 55)
GROUND_TOP = (80, 200, 80)
GROUND_MID = (40, 150, 40)

SHEET_BG_T = (18, 19, 38)
SHEET_BG_B = (34, 26, 50)
CARD_BG = (22, 23, 42)
CARD_EDGE = (74, 78, 128)
TEXT = (238, 240, 250)
SUB = (158, 164, 196)

CARD_W = 760
HERO_CARD_H = 200
TRUTH_CARD_H = 196

SHEET_W = PAD + CARD_W + PAD
SHEET_H = (HEADER_H + PAD + HERO_CARD_H + PAD
           + 3 * (TRUTH_CARD_H + PAD))

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_T[i] + (SHEET_BG_B[i] - SHEET_BG_T[i]) * t)
                for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 26, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — Paper Plane · NOTEBOOK PAPER · Round 2 (ship build)", True, TEXT),
    (PAD, 12))
sheet.blit(F_SUB.render(
    "V5 · BOLD LOOSE-LEAF converged. HERO 130px + 40px level/dive · "
    "NEAREST x3 on DAY sky, NIGHT sky, and the real DAY-GROUND/SANDSTONE case.",
    True, SUB), (PAD, 42))


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
        crop, (max(1, int(crop.get_width() * f)),
               max(1, int(crop.get_height() * f))))


def nearest40(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _grad_panel(rect, top, bot, radius=10):
    p = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, col, (0, y), (rect.w, y))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     mask.get_rect(), border_radius=radius)
    p.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sheet.blit(p, rect.topleft)


def _night_stars(rect, n, seed):
    import random
    rng = random.Random(seed)
    for _ in range(n):
        sx = rng.randint(rect.x + 4, rect.right - 4)
        sy = rng.randint(rect.y + 4, rect.bottom - 4)
        b = rng.randint(120, 220)
        pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)


def _day_ground_panel(rect, radius=10):
    """A real DAY-phase backdrop: pale-blue sky, a sandstone pillar column, and
    a green ground band — the three surfaces the dart must hold contrast on."""
    p = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    horizon = int(rect.h * 0.72)
    for y in range(rect.h):
        if y < horizon:
            t = y / max(1, horizon)
            col = tuple(int(DAY_SKY_TOP[i] + (DAY_SKY_BOT[i] - DAY_SKY_TOP[i]) * t)
                        for i in range(3))
        else:
            t = (y - horizon) / max(1, rect.h - horizon)
            col = tuple(int(GROUND_TOP[i] + (GROUND_MID[i] - GROUND_TOP[i]) * t)
                        for i in range(3))
        pygame.draw.line(p, col, (0, y), (rect.w, y))
    # A sandstone pillar column rising through the sky band (the off-white trap).
    col_x, col_w = int(rect.w * 0.40), 70
    for x in range(col_w):
        t = x / col_w
        # Lit edge on the left, falling to shadow on the right.
        shade = abs(t - 0.32)
        col = tuple(int(STONE_LIGHT[i] + (STONE_DARK[i] - STONE_LIGHT[i])
                        * min(1.0, shade * 1.6)) for i in range(3))
        pygame.draw.line(p, col, (col_x + x, 0), (col_x + x, horizon + 6))
    pygame.draw.line(p, STONE_MID, (col_x, 0), (col_x, horizon + 6), 2)
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255),
                     mask.get_rect(), border_radius=radius)
    p.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sheet.blit(p, rect.topleft)
    return col_x + col_w // 2     # x where a dart should sit ON the pillar


def _truth_block(panel, label, txt_col, dart_x_hint=None):
    """Smooth-40 level + dive, then NEAREST x3 level + dive. If dart_x_hint is
    given the smooth reads straddle that x so one dart sits over the pillar."""
    lx = (dart_x_hint - panel.x) if dart_x_hint is not None else 40
    lx = max(40, min(panel.w - 120, lx))
    g_level = smooth(2, 0, GAME_PX)
    sheet.blit(g_level, g_level.get_rect(center=(panel.x + lx, panel.y + 56)))
    g_dive = smooth(1, -32, GAME_PX)
    sheet.blit(g_dive, g_dive.get_rect(center=(panel.x + lx + 52, panel.y + 56)))
    n_level = nearest40(2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.x + 162, panel.y + 60)))
    n_dive = nearest40(1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 236, panel.y + 60)))
    sheet.blit(F_TAG.render(label, True, txt_col), (panel.x + 8, panel.y + 10))
    sheet.blit(F_TAG.render("smooth 40 · NEAREST x3 (level / dive)", True,
                            txt_col), (panel.x + 8, panel.bottom - 18))


# ── Hero card: 130px on a split DAY-sky | DAY-ground | NIGHT triptych. ───────
cy = HEADER_H + PAD
card = pygame.Rect(PAD, cy, CARD_W, HERO_CARD_H)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)
sheet.blit(F_NAME.render("HERO 130px — silhouette on every day surface", True,
                         TEXT), (PAD + 14, cy + 10))

third = (CARD_W - 28) // 3
hp_day = pygame.Rect(PAD + 14, cy + 38, third - 6, 150)
hp_grd = pygame.Rect(hp_day.right + 6, cy + 38, third - 6, 150)
hp_ngt = pygame.Rect(hp_grd.right + 6, cy + 38, CARD_W - 28 - 2 * (third), 150)
_grad_panel(hp_day, DAY_SKY_TOP, DAY_SKY_BOT)
_day_ground_panel(hp_grd)
_grad_panel(hp_ngt, NIGHT_TOP, NIGHT_BOT)
_night_stars(hp_ngt, 30, 7)
hero = smooth(0, 0, HERO_PX)
for hp, tag in ((hp_day, "DAY SKY"), (hp_grd, "DAY GROUND"), (hp_ngt, "NIGHT")):
    sheet.blit(hero, hero.get_rect(center=hp.center))
    tcol = (60, 40, 30) if hp is not hp_ngt else (220, 224, 240)
    sheet.blit(F_TAG.render(tag, True, tcol), (hp.x + 6, hp.bottom - 18))


# ── Three truth cards: DAY sky, DAY ground/pillar, NIGHT. ────────────────────
def _truth_card(idx, title, kind):
    ty = HEADER_H + PAD + HERO_CARD_H + PAD + idx * (TRUTH_CARD_H + PAD)
    c = pygame.Rect(PAD, ty, CARD_W, TRUTH_CARD_H)
    pygame.draw.rect(sheet, CARD_BG, c, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, c, 2, border_radius=12)
    sheet.blit(F_NAME.render(title, True, TEXT), (PAD + 14, ty + 8))
    panel = pygame.Rect(PAD + 14, ty + 34, CARD_W - 28, 150)
    dart_hint = None
    if kind == "day":
        _grad_panel(panel, DAY_SKY_TOP, DAY_SKY_BOT)
        txt_col = (60, 40, 30)
    elif kind == "ground":
        dart_hint = _day_ground_panel(panel)
        txt_col = (60, 40, 30)
    else:
        _grad_panel(panel, NIGHT_TOP, NIGHT_BOT)
        _night_stars(panel, 46, idx * 11 + 3)
        txt_col = (220, 224, 240)
    _truth_block(panel, title, txt_col, dart_hint)


_truth_card(0, "DAY SKY — bright pale-blue cloud band", "day")
_truth_card(1, "DAY GROUND — sandstone pillar + green ground", "ground")
_truth_card(2, "NIGHT — deep indigo", "night")

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
