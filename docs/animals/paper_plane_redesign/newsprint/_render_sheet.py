"""Round-2 convergence sheet — NEWSPRINT / COMIC paper-plane skin (PRODUCTION).

The art-director picked V3 · SUNDAY COMIC and asked for ONE ship-ready build.
This sheet inspects that single production build:

  * a HERO read at 130px (smoothscaled, flattering), and
  * the in-game truth test at 40px — level + dive tilt — on BOTH a DAY sky and a
    NIGHT sky, magnified back up with NEAREST-NEIGHBOR so the honest gameplay
    pixels are inspected with no extra smoothing.

The day/night split is the load-bearing test: the warm Ben-Day field + ONE red
POW + clean inked nose must read on a bright day sky AND a dark night sky.
Headless (SDL dummy) so it runs in CI / on the build box.
"""
import importlib.util
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "newsprint_skins", os.path.join(_here, "newsprint_skins.py"))
newsprint_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(newsprint_skins)

getter = newsprint_skins.get_newsprint

# ── layout ───────────────────────────────────────────────────────────────────
HERO_PX = 130
GAME_PX = 40
MAG = 3

CARD_W, CARD_H = 560, 232
PAD = 16
HEADER_H = 70

# Day sky (Skybit warm daylight) + night sky (deep blue) gradients for the
# in-game truth panels.
DAY_TOP, DAY_BOT = (150, 200, 240), (224, 232, 214)
NIGHT_TOP, NIGHT_BOT = (24, 26, 52), (44, 34, 64)

SHEET_BG_TOP, SHEET_BG_BOT = (30, 32, 46), (18, 19, 30)
CARD_BG = (24, 25, 38)
CARD_EDGE = (70, 74, 110)
TEXT = (238, 240, 250)
SUB = (150, 156, 190)
HERO_PANEL = (40, 42, 60)

# One production card; a second card holds an annotated notes strip.
SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + PAD + (CARD_H + PAD) + 150

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_TOP[i] + (SHEET_BG_BOT[i] - SHEET_BG_TOP[i]) * t)
                for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 26, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)
F_NOTE = pygame.font.SysFont("Arial", 13)

sheet.blit(F_TITLE.render(
    "Skybit — PAPER PLANE redesign · NEWSPRINT / COMIC · Round 2 (production)",
    True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "V3 · SUNDAY COMIC converged to ONE ship-ready build. HERO 130px · 40px "
    "NEAREST x3 (level / dive) on DAY and NIGHT.", True, SUB), (PAD, 44))


def _grad_panel(rect, top, bot):
    surf = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / rect.h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(surf, col, (0, y), (rect.w, y))
    return surf


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
    """Truth test: smoothscale DOWN to true 40px gameplay pixels, then magnify
    back up with NEAREST-NEIGHBOR — exactly those pixels, no extra smoothing."""
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


cx = PAD
cy = HEADER_H + PAD
card = pygame.Rect(cx, cy, CARD_W, CARD_H)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

sheet.blit(F_NAME.render(
    "skin_newsprint  ·  SUNDAY COMIC (halftone + red POW)", True, TEXT),
    (cx + 14, cy + 10))

# Hero panel (left).
hero_panel = pygame.Rect(cx + 12, cy + 44, 150, 172)
pygame.draw.rect(sheet, HERO_PANEL, hero_panel, border_radius=10)
hero = smooth(0, 0, HERO_PX)
sheet.blit(hero, hero.get_rect(center=hero_panel.center))
sheet.blit(F_TAG.render("130px hero", True, SUB),
           (hero_panel.x + 6, hero_panel.bottom - 18))

# Two truth panels: DAY (mid) + NIGHT (right), each level + dive at NEAREST x3.
for j, (label, top, bot) in enumerate(
        (("DAY", DAY_TOP, DAY_BOT), ("NIGHT", NIGHT_TOP, NIGHT_BOT))):
    px = cx + 174 + j * 196
    panel = pygame.Rect(px, cy + 44, 184, 172)
    pygame.draw.rect(sheet, (10, 10, 18), panel.inflate(4, 4), border_radius=10)
    sheet.blit(_grad_panel(panel, top, bot), panel.topleft)
    sub_text = (40, 40, 50) if label == "DAY" else (200, 206, 230)
    sheet.blit(F_TAG.render(label + " · 40px NEAREST x3", True, sub_text),
               (panel.x + 8, panel.y + 6))

    n_level = nearest40(2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(panel.x + 52, panel.y + 96)))
    n_dive = nearest40(1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 132, panel.y + 96)))
    sheet.blit(F_TAG.render("level / dive", True, sub_text),
               (panel.x + 8, panel.bottom - 18))

# ── notes strip ───────────────────────────────────────────────────────────────
ny = cy + CARD_H + PAD
note_card = pygame.Rect(cx, ny, CARD_W, 134)
pygame.draw.rect(sheet, CARD_BG, note_card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, note_card, 2, border_radius=12)
sheet.blit(F_NAME.render("Punch-list converged", True, TEXT), (cx + 14, ny + 10))
notes = [
    "POW pulled to TRAILING third; forward nose is clean inked light paper "
    "(nose-RIGHT reads in one frame).",
    "Halftone field shrunk ~18% and pulled OFF the nose tip — it frames the "
    "POW, never floods the lit facet.",
    "Hard fold: 2px dark crease + 1px lit lip = a crisp value STEP; dart "
    "silhouette survives in pure value.",
    "ONE saturated red mass + ONE white-hot core (the colourblind / value "
    "anchor). No second competing red.",
    "Magenta dropped for a capped warm-ORANGE minority so the field reads "
    "'warm bright print', not pink mush.",
    "Night tail rim verified — baked 1px self-rim separates the dark "
    "under-fold from the night sky.",
]
for i, line in enumerate(notes):
    sheet.blit(F_NOTE.render("•  " + line, True, SUB), (cx + 16, ny + 40 + i * 16))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
