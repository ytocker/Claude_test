"""Round-2 review sheet for the STUNT / FIGHTER FOLD paper-plane production build.

Round 2 converges to ONE ship-ready design — V1 · RED RACING STRIPE — so this
sheet stages the PRODUCTION build beside the CURRENT dollar-bill dart (the
baseline to beat). Each is shown at hero 130px plus the in-game truth-test
scale: 40px NEAREST-NEIGHBOR x3 (the honest gameplay-pixel silhouette) for
LEVEL and DIVE poses, on BOTH a DAY and a NIGHT sky — the north star is "reads
at 40px on day AND night". The DIVE frame is the value stress-test (the fold
flattens most there). Headless (SDL dummy) so it runs in CI / on the build box.
"""
import os
import sys
import importlib.util

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_here = os.path.dirname(os.path.abspath(__file__))
_root = os.path.abspath(os.path.join(_here, "..", "..", "..", ".."))
sys.path.insert(0, _root)

import pygame
pygame.init()
pygame.display.set_mode((1, 1))
spec = importlib.util.spec_from_file_location(
    "stunt_fold_skins", os.path.join(_here, "stunt_fold_skins.py"))
stunt_fold_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stunt_fold_skins)

# Pull the current PRODUCTION dollar-bill dart so the sheet shows the baseline
# we must beat — obviously more dynamic, while staying equally legible.
prod_spec = importlib.util.spec_from_file_location(
    "animal_paper_plane",
    os.path.join(_root, "game", "animal_paper_plane.py"))
animal_paper_plane = importlib.util.module_from_spec(prod_spec)
prod_spec.loader.exec_module(animal_paper_plane)

ORDER = [
    ("STUNT FOLD · RED RACING STRIPE", stunt_fold_skins.get_stunt_fold,
     "production build — white top / red keel band / dark under-fold"),
    ("CURRENT · dollar-bill dart", animal_paper_plane.get_paper_plane,
     "production glider — the baseline to beat"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 1
ROWS = len(ORDER)
CARD_W, CARD_H = 760, 256
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Two sky moods for the truth test.
DAY_TOP = (150, 200, 240)
DAY_BOT = (224, 232, 210)
NIGHT_TOP = (22, 24, 50)
NIGHT_BOT = (40, 30, 62)

SHEET_TOP = (24, 26, 52)
SHEET_BOT = (40, 30, 60)
CARD_BG = (16, 17, 34)
CARD_EDGE = (90, 96, 160)
CUR_EDGE = (110, 120, 90)            # muted rim for the baseline card
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
HERO_PANEL = (28, 30, 56)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_TOP[i] + (SHEET_BOT[i] - SHEET_TOP[i]) * t)
                for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(180):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy),
                       rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — Paper Plane redesign · STUNT / FIGHTER FOLD · Round 2 (production)",
    True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "HERO 130px · 40px NEAREST x3 (the honest gameplay read) LEVEL / DIVE on DAY and NIGHT sky. "
    "Nose points RIGHT (forward). Current dart shown below as the baseline to beat.",
    True, SUB), (PAD, 46))


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
        crop, (max(1, int(crop.get_width() * f)),
               max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    """Truth test: smoothscale DOWN to true 40px gameplay pixels, then magnify
    back up with NEAREST so we inspect exactly those gameplay pixels."""
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _grad_panel(rect, top, bot):
    p = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, c, (0, y), (rect.w, y))
    return p


for idx, (name, getter, feat) in enumerate(ORDER):
    cx = PAD
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)

    is_cur = name.startswith("CURRENT")
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CUR_EDGE if is_cur else CARD_EDGE,
                     card, 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, CUR_EDGE if is_cur else TEXT),
               (cx + 14, cy + 8))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 32))

    # Hero panel (left) — on a neutral dark backdrop.
    hero_panel = pygame.Rect(cx + 12, cy + 54, 150, 190)
    pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
    hero = smooth(getter, 0, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px", True, SUB),
               (hero_panel.x + 6, hero_panel.bottom - 18))

    # Truth panels (right): a DAY column and a NIGHT column, each split into
    # level + dive — the honest 40px gameplay read on both skies side by side.
    tx = cx + 176
    tw = (CARD_W - 176 - PAD - 14) // 2

    day_panel = pygame.Rect(tx, cy + 54, tw, 190)
    sheet.blit(_grad_panel(day_panel, DAY_TOP, DAY_BOT), day_panel.topleft)
    pygame.draw.rect(sheet, (90, 120, 150), day_panel, 1, border_radius=8)

    night_panel = pygame.Rect(tx + tw + 14, cy + 54, tw, 190)
    sheet.blit(_grad_panel(night_panel, NIGHT_TOP, NIGHT_BOT),
               night_panel.topleft)
    pygame.draw.rect(sheet, (70, 76, 120), night_panel, 1, border_radius=8)
    # A few night stars for honesty against a dark sky.
    for _ in range(24):
        sx = rng.randint(night_panel.x + 2, night_panel.right - 2)
        sy = rng.randint(night_panel.y + 2, night_panel.bottom - 2)
        b = rng.randint(120, 210)
        pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)

    for panel, tag, tagcol in ((day_panel, "40px x3  DAY  level / dive",
                                (40, 50, 60)),
                               (night_panel, "40px x3  NIGHT  level / dive",
                                (200, 206, 230))):
        n_level = nearest40(getter, 2, 0, MAG)
        sheet.blit(n_level, n_level.get_rect(
            center=(panel.x + panel.w // 2, panel.y + 56)))
        # DIVE: the value stress-test pose (the fold flattens most here).
        n_dive = nearest40(getter, 1, -32, MAG)
        sheet.blit(n_dive, n_dive.get_rect(
            center=(panel.x + panel.w // 2, panel.y + 132)))
        sheet.blit(F_TAG.render(tag, True, tagcol),
                   (panel.x + 8, panel.bottom - 16))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
