"""Round-2 review sheet for the RED PANDA Store skin (single production build).

Round 1 was a five-way chooser; the art-director picked v3 BIG-TAIL HERO to
iterate. This sheet shows the ONE refined design under the honest truth test:

  * HERO 130px (night) — the showpiece read.
  * 40px level + dive over BOTH a bright-day AND a night swatch, each with a
    smooth-40 reference and a NEAREST-NEIGHBOR x3 magnification (the true
    gameplay-pixel silhouette; smoothscale flatters detail that vanishes in
    motion).
  * a DESATURATED 40px thumbnail — the colourblind / value test, where the
    cream ring-spots must still separate from the russet fur.

Headless (SDL dummy) so it runs in CI.
"""
import importlib.util
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "red_panda_skins", os.path.join(_here, "red_panda_skins.py"))
red_panda_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(red_panda_skins)

getter = red_panda_skins.BUILDERS["skin_red_panda"]

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
DAY_TOP = (150, 206, 248)
DAY_BOT = (212, 236, 252)
CARD_BG = (16, 17, 34)
CARD_EDGE = (60, 64, 110)
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
HERO_PANEL = (28, 30, 56)

SHEET_W = 940
SHEET_H = 470

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t)
               for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

rng = random.Random(7)
for _ in range(150):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy),
                       rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 26, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — RED PANDA Store Skin · Round 2  (v3 BIG-TAIL HERO, perfected)",
    True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Single production build. HERO 130px · 40px level & dive over NIGHT + DAY "
    "with NEAREST x3 (the honest read) · desaturated 40px (value/colourblind test).",
    True, SUB), (PAD, 46))


def _crop(frame_idx, tilt):
    s = getter(frame_idx, tilt)
    rect = s.get_bounding_rect()
    if rect.w == 0 or rect.h == 0:
        rect = s.get_rect()
    return s.subsurface(rect).copy()


def smooth(frame_idx, tilt, target_px):
    crop = _crop(frame_idx, tilt)
    longest = max(crop.get_width(), crop.get_height())
    fac = target_px / longest
    return pygame.transform.smoothscale(
        crop, (max(1, int(crop.get_width() * fac)),
               max(1, int(crop.get_height() * fac))))


def nearest40(frame_idx, tilt, mag):
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def desat(surf):
    """Grayscale copy preserving alpha — the colourblind / value check. Done
    per-pixel (no numpy on this box); the read surfaces are tiny so it's cheap."""
    out = surf.copy()
    w, h = out.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b, a = out.get_at((x, y))
            lum = int(r * 0.299 + g * 0.587 + b * 0.114)
            out.set_at((x, y), (lum, lum, lum, a))
    return out


def _grad_swatch(rect, top, bot):
    sw = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(sw, c, (0, y), (rect.w, y))
    sheet.blit(sw, rect.topleft)


# ── Hero panel (left) ─────────────────────────────────────────────────────────
hero_panel = pygame.Rect(PAD, HEADER_H + 6, 220, SHEET_H - HEADER_H - PAD - 6)
pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, hero_panel, 2, border_radius=12)
hero = smooth(0, 0, HERO_PX)
sheet.blit(hero, hero.get_rect(center=(hero_panel.centerx, hero_panel.y + 130)))
sheet.blit(F_NAME.render("skin_red_panda", True, TEXT),
           (hero_panel.x + 14, hero_panel.y + 12))
sheet.blit(F_TAG.render("HERO 130px (down-pose, tail high)", True, SUB),
           (hero_panel.x + 14, hero_panel.bottom - 24))

# ── Game-truth panel (right) ──────────────────────────────────────────────────
gx = hero_panel.right + PAD
gw = SHEET_W - gx - PAD


def _read_row(label, top, bot, row_y, row_h, tag_col):
    band = pygame.Rect(gx, row_y, gw, row_h)
    _grad_swatch(band, top, bot)
    pygame.draw.rect(sheet, CARD_EDGE, band, 1, border_radius=8)
    cy = band.y + row_h // 2 + 4
    g_lvl = smooth(2, 0, GAME_PX)
    sheet.blit(g_lvl, g_lvl.get_rect(center=(band.x + 36, cy)))
    g_div = smooth(1, -32, GAME_PX)
    sheet.blit(g_div, g_div.get_rect(center=(band.x + 80, cy)))
    n_lvl = nearest40(2, 0, MAG)
    sheet.blit(n_lvl, n_lvl.get_rect(center=(band.x + 170, cy)))
    n_div = nearest40(1, -32, MAG)
    sheet.blit(n_div, n_div.get_rect(center=(band.x + 270, cy)))
    # The four flap frames at NEAREST x3 (level) so pose-invariance is visible.
    fx = band.x + 350
    for fi in range(4):
        fr = nearest40(fi, 0, 2)
        sheet.blit(fr, fr.get_rect(center=(fx + fi * 38, cy)))
    sheet.blit(F_TAG.render(label, True, tag_col), (band.x + 6, band.y + 4))
    sheet.blit(F_TAG.render("40 / 40 / x3 lvl / x3 dive / 4 poses x2",
                            True, tag_col), (band.x + 6, band.bottom - 18))


row_h = 118
_read_row("NIGHT", NIGHT_TOP, (60, 44, 80),
          HEADER_H + 6, row_h, (215, 215, 235))
_read_row("BRIGHT DAY", DAY_TOP, DAY_BOT,
          HEADER_H + 6 + row_h + 10, row_h, (40, 50, 70))

# Desaturated 40px value test (bottom strip).
ds_y = HEADER_H + 6 + 2 * (row_h + 10)
ds = pygame.Rect(gx, ds_y, gw, SHEET_H - ds_y - PAD)
pygame.draw.rect(sheet, (60, 60, 64), ds, border_radius=8)
pygame.draw.rect(sheet, CARD_EDGE, ds, 1, border_radius=8)
cy = ds.centery + 2
for i, (fi, tilt) in enumerate([(2, 0), (1, -32)]):
    g = desat(nearest40(fi, tilt, MAG))
    sheet.blit(g, g.get_rect(center=(ds.x + 60 + i * 110, cy)))
sheet.blit(F_TAG.render(
    "DESATURATED 40px x3 (level / dive) — rings must separate from fur",
    True, (235, 235, 235)), (ds.x + 240, cy - 8))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
