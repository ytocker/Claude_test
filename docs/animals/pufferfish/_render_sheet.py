"""Round-2 review sheet for the PUFFERFISH Store skin.

Leads with the single production build (`skin_pufferfish`) blown up at hero
130px on BOTH a bright-day and a night backdrop, with the in-game truth test
(40px level + dive, NEAREST-NEIGHBOR x3) on each sky so the silhouette is
checked honestly against both. A DESATURATED 40px thumbnail proves the read
holds in grayscale — it must not depend on yellow alone. Two small alt
variants follow for comparison. Headless (SDL dummy) so it runs in CI.
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
    "pufferfish_skins", os.path.join(_here, "pufferfish_skins.py"))
pufferfish_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pufferfish_skins)

BUILDERS = pufferfish_skins.BUILDERS
TELLS = pufferfish_skins.TELLS

# ── palette / layout ─────────────────────────────────────────────────────────
PAD = 16
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

DAY_TOP, DAY_BOT = (118, 196, 240), (190, 228, 246)
NIGHT_TOP, NIGHT_BOT = (22, 24, 50), (40, 30, 60)
SHEET_TOP, SHEET_BOT = (18, 20, 40), (34, 26, 52)
CARD_BG = (16, 17, 34)
CARD_EDGE = (70, 80, 130)
LEAD_EDGE = (210, 168, 70)
TEXT = (236, 238, 250)
SUB = (158, 164, 198)
GAME_PANEL = (12, 13, 28)

HERO_CARD_W, HERO_CARD_H = 760, 300
ALT_CARD_W, ALT_CARD_H = 372, 196

SHEET_W = PAD + HERO_CARD_W + PAD
SHEET_H = (HEADER_H + PAD + HERO_CARD_H + PAD + ALT_CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_TOP[i] + (SHEET_BOT[i] - SHEET_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(180):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 190)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — PUFFERFISH Store Skin · Round 2 (converged)", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "Lead = skin_pufferfish: V4 star body + V1 friendly face. HERO 130px day & night · 40px NEAREST x3 (level/dive) per sky · grayscale 40px proof.",
    True, SUB), (PAD, 44))


def _grad_rect(surf, rect, top, bot):
    for i in range(rect.h):
        t = i / max(1, rect.h)
        col = tuple(int(top[j] + (bot[j] - top[j]) * t) for j in range(3))
        pygame.draw.line(surf, col, (rect.x, rect.y + i), (rect.right, rect.y + i))


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


def small40(getter, frame_idx, tilt):
    return smooth(getter, frame_idx, tilt, GAME_PX)


def nearest40(getter, frame_idx, tilt, mag):
    small = small40(getter, frame_idx, tilt)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def desaturate(src):
    """Grayscale a surface preserving alpha — luminance test proves the
    silhouette holds without leaning on the yellow hue."""
    out = src.copy()
    out.lock()
    for yy in range(out.get_height()):
        for xx in range(out.get_width()):
            r, g, b, a = out.get_at((xx, yy))
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)
            out.set_at((xx, yy), (lum, lum, lum, a))
    out.unlock()
    return out


# ── LEAD CARD: skin_pufferfish, blown up on both skies + grayscale proof ──────
lead = BUILDERS["skin_pufferfish"]
cx, cy = PAD, HEADER_H
pygame.draw.rect(sheet, CARD_BG, (cx, cy, HERO_CARD_W, HERO_CARD_H), border_radius=12)
pygame.draw.rect(sheet, LEAD_EDGE, (cx, cy, HERO_CARD_W, HERO_CARD_H), 3, border_radius=12)
sheet.blit(F_NAME.render("skin_pufferfish  (production lead)", True, LEAD_EDGE), (cx + 14, cy + 8))
sheet.blit(F_FEAT.render("read: " + TELLS["skin_pufferfish"], True, SUB), (cx + 14, cy + 34))

# Day hero (left).
day_panel = pygame.Rect(cx + 14, cy + 58, 200, 226)
_grad_rect(sheet, day_panel, DAY_TOP, DAY_BOT)
pygame.draw.rect(sheet, CARD_EDGE, day_panel, 1, border_radius=10)
hero = smooth(lead, 0, 0, HERO_PX)
sheet.blit(hero, hero.get_rect(center=day_panel.center))
sheet.blit(F_TAG.render("130px · DAY", True, (40, 50, 70)), (day_panel.x + 6, day_panel.bottom - 18))

# Night hero (right of day).
night_panel = pygame.Rect(day_panel.right + 12, cy + 58, 200, 226)
_grad_rect(sheet, night_panel, NIGHT_TOP, NIGHT_BOT)
pygame.draw.rect(sheet, CARD_EDGE, night_panel, 1, border_radius=10)
hero_n = smooth(lead, 0, 0, HERO_PX)
sheet.blit(hero_n, hero_n.get_rect(center=night_panel.center))
sheet.blit(F_TAG.render("130px · NIGHT", True, (200, 206, 240)), (night_panel.x + 6, night_panel.bottom - 18))

# Truth column: 40px NEAREST x3 level/dive on day (top) and night (bottom).
truth = pygame.Rect(night_panel.right + 12, cy + 58, 196, 226)
day_t = pygame.Rect(truth.x, truth.y, truth.w, truth.h // 2 - 2)
night_t = pygame.Rect(truth.x, day_t.bottom + 4, truth.w, truth.h // 2 - 2)
_grad_rect(sheet, day_t, DAY_TOP, DAY_BOT)
_grad_rect(sheet, night_t, NIGHT_TOP, NIGHT_BOT)
for panel, label, tc in ((day_t, "40px x3 · DAY", (40, 50, 70)),
                         (night_t, "40px x3 · NIGHT", (200, 206, 240))):
    nl = nearest40(lead, 2, 0, MAG)
    sheet.blit(nl, nl.get_rect(center=(panel.x + 56, panel.y + 50)))
    nd = nearest40(lead, 1, -32, MAG)
    sheet.blit(nd, nd.get_rect(center=(panel.x + 132, panel.y + 50)))
    sheet.blit(F_TAG.render(label + "  (level/dive)", True, tc), (panel.x + 6, panel.bottom - 18))
    pygame.draw.rect(sheet, CARD_EDGE, panel, 1, border_radius=8)

# Grayscale proof column.
gray = pygame.Rect(truth.right + 12, cy + 58, HERO_CARD_W - (truth.right + 12 - cx) - 14, 226)
pygame.draw.rect(sheet, (70, 70, 70), gray, border_radius=10)
_grad_rect(sheet, gray.inflate(-4, -4), (96, 96, 96), (40, 40, 40))
gl = desaturate(nearest40(lead, 2, 0, MAG))
sheet.blit(gl, gl.get_rect(center=(gray.centerx, gray.y + 60)))
gd = desaturate(nearest40(lead, 1, -32, MAG))
sheet.blit(gd, gd.get_rect(center=(gray.centerx, gray.y + 150)))
sheet.blit(F_TAG.render("40px GRAYSCALE proof", True, (235, 235, 235)), (gray.x + 6, gray.bottom - 18))
sheet.blit(F_TAG.render("(level / dive)", True, (210, 210, 210)), (gray.x + 6, gray.bottom - 34))

# ── ALT comparison row (two small cards) ──────────────────────────────────────
alt_y = cy + HERO_CARD_H + PAD
for i, key in enumerate(("alt_dense_star", "alt_coral_star")):
    ax = PAD + i * (ALT_CARD_W + PAD)
    pygame.draw.rect(sheet, CARD_BG, (ax, alt_y, ALT_CARD_W, ALT_CARD_H), border_radius=10)
    pygame.draw.rect(sheet, CARD_EDGE, (ax, alt_y, ALT_CARD_W, ALT_CARD_H), 2, border_radius=10)
    sheet.blit(F_NAME.render(key, True, TEXT), (ax + 12, alt_y + 8))
    sheet.blit(F_FEAT.render(TELLS[key], True, SUB), (ax + 12, alt_y + 34))

    g = BUILDERS[key]
    dp = pygame.Rect(ax + 12, alt_y + 56, 120, 128)
    _grad_rect(sheet, dp, DAY_TOP, DAY_BOT)
    pygame.draw.rect(sheet, CARD_EDGE, dp, 1, border_radius=8)
    h = smooth(g, 0, 0, 100)
    sheet.blit(h, h.get_rect(center=dp.center))
    sheet.blit(F_TAG.render("100px", True, (40, 50, 70)), (dp.x + 4, dp.bottom - 16))

    tp = pygame.Rect(dp.right + 10, alt_y + 56, ALT_CARD_W - (dp.right + 10 - ax) - 12, 128)
    pygame.draw.rect(sheet, GAME_PANEL, tp, border_radius=8)
    nl = nearest40(g, 2, 0, MAG)
    sheet.blit(nl, nl.get_rect(center=(tp.x + 56, tp.centery - 6)))
    nd = nearest40(g, 1, -32, MAG)
    sheet.blit(nd, nd.get_rect(center=(tp.x + 132, tp.centery - 6)))
    sheet.blit(F_TAG.render("40px x3 (level/dive)", True, (210, 200, 150)), (tp.x + 6, tp.bottom - 16))


out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
