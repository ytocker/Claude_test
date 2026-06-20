"""Round-2 review sheet for the JET FIGHTER store skin (STEEL RAPTOR).

Single converged production build. Renders the hero at 130px and the in-game
truth-test scale (40px, NEAREST x3, level + dive) on BOTH a day sky and a
night sky — judged on the 40px DIVE frame. Also lays out all 4 baked frames
so the afterburner PULSE (bright on the middle two, dim at the ends, ±1px
nose pitch) is verifiable. Headless (SDL dummy) so it runs in CI.
"""
import os
import sys
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

import importlib.util
_here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location(
    "jet_fighter_skins", os.path.join(_here, "jet_fighter_skins.py"))
jet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jet)

getter = jet.BUILDERS["skin_jet_fighter"]

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 76
HERO_PX = 130
GAME_PX = 40
MAG = 3

TEXT = (236, 238, 250)
SUB = (150, 156, 190)
CARD_BG = (16, 17, 34)
CARD_EDGE = (190, 150, 70)            # gold rim — the priciest secret skin
PANEL_LBL = (210, 200, 150)

DAY_TOP, DAY_BOT = (150, 200, 240), (240, 220, 180)
NIGHT_TOP, NIGHT_BOT = (18, 20, 44), (40, 28, 60)

SHEET_W = 820
SHEET_H = 760

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — JET FIGHTER (skin_jet_fighter) · Round 2 · STEEL RAPTOR", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "Converged production build. HERO 130px · 40px NEAREST x3 (level / DIVE) on DAY + NIGHT — judged on the DIVE frame.",
    True, SUB), (PAD, 44))
sheet.blit(F_SUB.render(
    "Flap = afterburner PULSE: bright middle 2 frames, dim at ends, ±1px nose pitch (no wing flap).",
    True, SUB), (PAD, 60))


def _grad_panel(w, h, top, bot):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (w, y))
    return s


def _stars(rect, seed, n=34):
    r = random.Random(seed)
    for _ in range(n):
        sx = r.randint(rect.x + 2, rect.right - 2)
        sy = r.randint(rect.y + 2, rect.bottom - 2)
        b = r.randint(120, 220)
        pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)


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


# ── Card 1: HERO 130px on day + night ────────────────────────────────────────
cy = HEADER_H
card = pygame.Rect(PAD, cy, SHEET_W - 2 * PAD, 196)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)
sheet.blit(F_NAME.render("HERO 130px", True, CARD_EDGE), (card.x + 14, cy + 10))
sheet.blit(F_FEAT.render("arrowhead nose + delta dominant · warm rim signature · cool canopy anchor", True, SUB), (card.x + 14, cy + 36))

hero = smooth(1, 0, HERO_PX)
hd = pygame.Rect(card.x + 20, cy + 56, 360, 120)
sheet.blit(_grad_panel(hd.w, hd.h, DAY_TOP, DAY_BOT), hd.topleft)
pygame.draw.rect(sheet, (90, 90, 120), hd, 1, border_radius=8)
sheet.blit(hero, hero.get_rect(center=hd.center))
sheet.blit(F_TAG.render("130px (day)", True, (40, 40, 60)), (hd.x + 6, hd.bottom - 18))

hn = pygame.Rect(card.x + 400, cy + 56, 360, 120)
sheet.blit(_grad_panel(hn.w, hn.h, NIGHT_TOP, NIGHT_BOT), hn.topleft)
_stars(hn, 5)
pygame.draw.rect(sheet, (90, 90, 120), hn, 1, border_radius=8)
sheet.blit(hero, hero.get_rect(center=hn.center))
sheet.blit(F_TAG.render("130px (night)", True, PANEL_LBL), (hn.x + 6, hn.bottom - 18))


# ── Card 2: PULSE — all 4 baked frames at 40px x3 (day) ───────────────────────
cy = HEADER_H + 210
card = pygame.Rect(PAD, cy, SHEET_W - 2 * PAD, 180)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)
sheet.blit(F_NAME.render("AFTERBURNER PULSE · 4 frames @ 40px x3 (day)", True, CARD_EDGE), (card.x + 14, cy + 10))
sheet.blit(F_FEAT.render("throttle read: dim → BRIGHT → BRIGHT → dim · twin white cores stay distinct", True, SUB), (card.x + 14, cy + 36))
pp = pygame.Rect(card.x + 14, cy + 56, card.w - 28, 108)
sheet.blit(_grad_panel(pp.w, pp.h, DAY_TOP, DAY_BOT), pp.topleft)
pygame.draw.rect(sheet, (90, 90, 120), pp, 1, border_radius=8)
for fi in range(4):
    fr = nearest40(fi, 0, MAG)
    cxp = pp.x + 100 + fi * 200
    sheet.blit(fr, fr.get_rect(center=(cxp, pp.y + 54)))
    sheet.blit(F_TAG.render("frame %d" % fi, True, (40, 40, 60)), (cxp - 26, pp.bottom - 18))


# ── Card 3: TRUTH TEST — 40px x3 level + DIVE, day then night ─────────────────
cy = HEADER_H + 400
card = pygame.Rect(PAD, cy, SHEET_W - 2 * PAD, 180)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)
sheet.blit(F_NAME.render("TRUTH TEST · 40px x3 — level / DIVE (judged on DIVE)", True, CARD_EDGE), (card.x + 14, cy + 10))
sheet.blit(F_FEAT.render("burner capped to rear third · nose + delta dominant · rim lifts night silhouette", True, SUB), (card.x + 14, cy + 36))


def truth_panel(px, top, bot, stars_seed, label):
    tp = pygame.Rect(px, cy + 56, 366, 108)
    sheet.blit(_grad_panel(tp.w, tp.h, top, bot), tp.topleft)
    if stars_seed is not None:
        _stars(tp, stars_seed, 26)
    pygame.draw.rect(sheet, (90, 90, 120), tp, 1, border_radius=8)
    lvl = nearest40(1, 0, MAG)
    sheet.blit(lvl, lvl.get_rect(center=(tp.x + 100, tp.y + 52)))
    dive = nearest40(0, -30, MAG)
    sheet.blit(dive, dive.get_rect(center=(tp.x + 262, tp.y + 52)))
    fg = (40, 40, 60) if stars_seed is None else PANEL_LBL
    sheet.blit(F_TAG.render(label, True, fg), (tp.x + 6, tp.bottom - 18))


truth_panel(card.x + 14, DAY_TOP, DAY_BOT, None, "40px x3 day  (level / DIVE)")
truth_panel(card.x + 402, NIGHT_TOP, NIGHT_BOT, 9, "40px x3 night  (level / DIVE)")

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
