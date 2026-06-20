"""Round-1 review sheet for the candidate JET FIGHTER store skin.

Renders each of the 5 variants at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt) magnified x3 with NEAREST-NEIGHBOR, on BOTH a
day sky and a night sky — the burner glow must read against bright stone and
dark night alike. Headless (SDL dummy) so it runs in CI / on the build box.
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

BUILDERS = jet.BUILDERS

ORDER = [
    ("v1 · STEEL RAPTOR",    "delta planform + twin hot burner"),
    ("v2 · TOP GUN NAVY",    "3/4 navy body + canopy + cyan burner"),
    ("v3 · DESERT STRIKE",   "forward-swept tan wings + twin burner"),
    ("v4 · STEALTH PHANTOM", "matte-black facets + COLD cyan burner"),
    ("v5 · CHROME ACE",      "chrome 3/4 + red livery + smoke trail"),
]

# ── layout: one tall card per variant, full row ──────────────────────────────
CARD_W, CARD_H = 760, 220
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

TEXT = (236, 238, 250)
SUB = (150, 156, 190)
CARD_BG = (16, 17, 34)
CARD_EDGE = (190, 150, 70)            # gold rim — this is the priciest secret skin
PANEL_LBL = (210, 200, 150)

# Day + night sky swatches for the read-test panels.
DAY_TOP, DAY_BOT = (150, 200, 240), (240, 220, 180)
NIGHT_TOP, NIGHT_BOT = (24, 26, 52), (44, 32, 64)

SHEET_W = PAD + CARD_W + PAD
SHEET_H = HEADER_H + len(ORDER) * (CARD_H + PAD) + PAD

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

sheet.blit(F_TITLE.render("Skybit — JET FIGHTER (skin_jet_fighter) · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "Most expensive secret skin. HERO 130px · 40px NEAREST x3 (level / dive) on DAY + NIGHT. "
    "Flap = afterburner pulse + subtle pitch (no wing flap).",
    True, SUB), (PAD, 42))


def _grad_panel(w, h, top, bot):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (w, y))
    return s


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


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


for idx, (key, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    cx = PAD
    cy = HEADER_H + idx * (CARD_H + PAD)
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 3, border_radius=12)

    sheet.blit(F_NAME.render(key, True, CARD_EDGE), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render("read: " + feat, True, SUB), (cx + 14, cy + 36))

    panel_y = cy + 58
    panel_h = 148

    # ── Hero 130px on a day sky (left) ──
    hero_p = pygame.Rect(cx + 14, panel_y, 160, panel_h)
    sheet.blit(_grad_panel(hero_p.w, hero_p.h, DAY_TOP, DAY_BOT), hero_p.topleft)
    pygame.draw.rect(sheet, (90, 90, 120), hero_p, 1, border_radius=8)
    hero = smooth(getter, 1, 0, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_p.center))
    sheet.blit(F_TAG.render("130px (day)", True, (40, 40, 60)),
               (hero_p.x + 6, hero_p.bottom - 18))

    # ── Hero 130px on a night sky (next) ──
    hero_n = pygame.Rect(cx + 184, panel_y, 160, panel_h)
    sheet.blit(_grad_panel(hero_n.w, hero_n.h, NIGHT_TOP, NIGHT_BOT), hero_n.topleft)
    rng = random.Random(idx * 13 + 1)
    for _ in range(36):
        sx = rng.randint(hero_n.x + 2, hero_n.right - 2)
        sy = rng.randint(hero_n.y + 2, hero_n.bottom - 2)
        b = rng.randint(120, 220)
        pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)
    pygame.draw.rect(sheet, (90, 90, 120), hero_n, 1, border_radius=8)
    sheet.blit(hero, hero.get_rect(center=hero_n.center))
    sheet.blit(F_TAG.render("130px (night)", True, PANEL_LBL),
               (hero_n.x + 6, hero_n.bottom - 18))

    # ── 40px NEAREST x3 truth: day (level+dive) then night (level+dive) ──
    def truth_panel(px, top, bot, stars, label):
        tp = pygame.Rect(px, panel_y, 190, panel_h)
        sheet.blit(_grad_panel(tp.w, tp.h, top, bot), tp.topleft)
        if stars:
            r2 = random.Random(idx * 31 + 7)
            for _ in range(28):
                sx = r2.randint(tp.x + 2, tp.right - 2)
                sy = r2.randint(tp.y + 2, tp.bottom - 2)
                b = r2.randint(120, 210)
                pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), 1)
        pygame.draw.rect(sheet, (90, 90, 120), tp, 1, border_radius=8)
        lvl = nearest40(getter, 1, 0, MAG)
        sheet.blit(lvl, lvl.get_rect(center=(tp.x + 56, tp.y + 56)))
        dive = nearest40(getter, 0, -30, MAG)
        sheet.blit(dive, dive.get_rect(center=(tp.x + 134, tp.y + 56)))
        fg = (40, 40, 60) if not stars else PANEL_LBL
        sheet.blit(F_TAG.render(label, True, fg), (tp.x + 6, tp.bottom - 18))
        return tp

    truth_panel(cx + 354, DAY_TOP, DAY_BOT, False, "40px x3 day  (level / dive)")
    truth_panel(cx + 552, NIGHT_TOP, NIGHT_BOT, True, "40px x3 night  (level / dive)")

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
