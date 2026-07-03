"""Round-3 review sheet for the converged SUGAR GLIDER Store skin.

One production design (V4 twilight, refined per the punch list). Shown at hero
130px and at the in-game truth-test scale (40px, level + dive) on THREE skies:
a bright-day blue, a PALE near-white cloud gradient (the day-pop stress test),
and a night sky. The 40px reads are also NEAREST-NEIGHBOR x3 magnified so the
true gameplay-pixel silhouette is honest. Headless (SDL dummy) for CI.
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
    "sugar_glider_skins", os.path.join(_here, "sugar_glider_skins.py"))
sg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sg)

getter = sg.BUILDERS["skin_sugar_glider"]

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 16
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Three test skies.
DAY_TOP, DAY_BOT = (150, 206, 240), (208, 234, 246)
PALE_TOP, PALE_BOT = (236, 242, 248), (250, 251, 252)   # near-white cloud
NIGHT_TOP, NIGHT_BOT = (24, 26, 52), (40, 30, 60)

SHEET_BG_T = (18, 19, 32)
SHEET_BG_B = (32, 26, 44)
CARD_BG = (16, 17, 30)
CARD_EDGE = (70, 74, 120)
TEXT = (236, 238, 250)
SUB = (158, 164, 196)

SHEET_W = 820
SHEET_H = 860

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_T[i] + (SHEET_BG_B[i] - SHEET_BG_T[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — Sugar Glider Skin · Round 3 (final pass)", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Single production build (skin_sugar_glider). HERO 130px + 40px NEAREST x3 (level+dive) on "
    "DAY / PALE-CLOUD / NIGHT. North star: lives or dies at 40px in motion.",
    True, SUB), (PAD, 44))


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


def sky_panel(rect, top, bot, *, stars=False, radius=10):
    panel = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(panel, col, (0, y), (rect.w, y))
    if stars:
        import random
        rng = random.Random(rect.x * 7 + rect.y)
        for _ in range(28):
            sx, sy = rng.randint(0, rect.w), rng.randint(0, rect.h)
            b = rng.randint(120, 220)
            pygame.draw.circle(panel, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))
    rounded = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(rounded, (255, 255, 255), rounded.get_rect(), border_radius=radius)
    panel = panel.convert_alpha()
    panel.blit(rounded, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sheet.blit(panel, rect.topleft)


SKIES = [
    ("DAY", DAY_TOP, DAY_BOT, False, (40, 60, 80)),
    ("PALE CLOUD", PALE_TOP, PALE_BOT, False, (60, 70, 90)),
    ("NIGHT", NIGHT_TOP, NIGHT_BOT, True, (200, 200, 230)),
]

# ── Section A · HERO 130px on all three skies ────────────────────────────────
y0 = HEADER_H + PAD
hero_card = pygame.Rect(PAD, y0, SHEET_W - 2 * PAD, 230)
pygame.draw.rect(sheet, CARD_BG, hero_card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, hero_card, 2, border_radius=12)
sheet.blit(F_NAME.render("HERO 130px — the up-close read", True, TEXT), (hero_card.x + 14, hero_card.y + 10))

hero_w = (hero_card.w - 4 * 14) // 3
for i, (label, top, bot, stars, tagcol) in enumerate(SKIES):
    r = pygame.Rect(hero_card.x + 14 + i * (hero_w + 14), hero_card.y + 44, hero_w, 160)
    sky_panel(r, top, bot, stars=stars)
    h = smooth(0, 0, HERO_PX)
    sheet.blit(h, h.get_rect(center=r.center))
    sheet.blit(F_TAG.render(label, True, tagcol), (r.x + 8, r.bottom - 20))

# ── Section B · the GLIDE CYCLE silhouette delta (all 4 poses, NEAREST x3) ───
y1 = hero_card.bottom + PAD
cyc_card = pygame.Rect(PAD, y1, SHEET_W - 2 * PAD, 170)
pygame.draw.rect(sheet, CARD_BG, cyc_card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, cyc_card, 2, border_radius=12)
sheet.blit(F_NAME.render("GLIDE CYCLE — taut wide kite ↔ tucked dart (40px NEAREST x3, night)", True, TEXT),
           (cyc_card.x + 14, cyc_card.y + 10))
strip = pygame.Rect(cyc_card.x + 14, cyc_card.y + 42, cyc_card.w - 28, 100)
sky_panel(strip, NIGHT_TOP, NIGHT_BOT, stars=True)
for fi in range(4):
    cx = strip.x + 90 + fi * 180
    img = nearest40(fi, 0, MAG)
    sheet.blit(img, img.get_rect(center=(cx, strip.centery)))
    sheet.blit(F_TAG.render(["tucked (dart)", "mid-tuck", "mid-spread", "spread (glide)"][fi], True, (200, 200, 230)),
               (cx - 40, strip.bottom - 18))

# ── Section C · the honest 40px read, NEAREST x3, level + dive, all skies ─────
y2 = cyc_card.bottom + PAD
read_card = pygame.Rect(PAD, y2, SHEET_W - 2 * PAD, SHEET_H - y2 - PAD)
pygame.draw.rect(sheet, CARD_BG, read_card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, read_card, 2, border_radius=12)
sheet.blit(F_NAME.render("THE HONEST READ — 40px NEAREST x3 (level / dive)", True, TEXT),
           (read_card.x + 14, read_card.y + 10))

col_w = (read_card.w - 4 * 14) // 3
for i, (label, top, bot, stars, tagcol) in enumerate(SKIES):
    r = pygame.Rect(read_card.x + 14 + i * (col_w + 14), read_card.y + 44, col_w, read_card.h - 60)
    sky_panel(r, top, bot, stars=stars)
    lvl = nearest40(2, 0, MAG)
    sheet.blit(lvl, lvl.get_rect(center=(r.centerx, r.y + r.h * 0.32)))
    dive = nearest40(1, -32, MAG)
    sheet.blit(dive, dive.get_rect(center=(r.centerx, r.y + r.h * 0.72)))
    sheet.blit(F_TAG.render(label + " · level / dive", True, tagcol), (r.x + 8, r.bottom - 20))

out_path = os.path.join(_here, "round_3.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
