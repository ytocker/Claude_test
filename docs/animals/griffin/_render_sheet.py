"""Round-2 review sheet for the SINGLE production GRIFFIN skin.

Renders the converged V4 at hero 130px AND at the in-game truth-test scale
(40px, level + dive), plus a NEAREST-NEIGHBOR x3 magnification of those 40px
reads so the true gameplay-pixel silhouette is honest (smoothscale flatters
tiny detail that vanishes in motion). Shown over BOTH a night and a bright-day
backdrop so the read survives both skies.

The distinctiveness proof is the right-hand strip: the SHIPPING bald-eagle skin
(game/animal_skins.get_eagle) is rendered at the SAME 40px NEAREST x3 read
directly beside the griffin, so the feather→fur / lion-rump separation is
provable side-by-side. Headless (SDL dummy) so it runs in CI / on the build box.
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
    "griffin_skins", os.path.join(_here, "griffin_skins.py"))
griffin_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(griffin_skins)

from game.animal_skins import get_eagle

get_griffin = griffin_skins.BUILDERS["skin_griffin"]

# ── colours ──────────────────────────────────────────────────────────────────
NIGHT_TOP = (24, 26, 52)
NIGHT_BOT = (40, 30, 60)
DAY_TOP = (140, 200, 246)
DAY_BOT = (206, 234, 250)
CARD_BG = (16, 17, 34)
GOLD = (190, 150, 70)               # griffin is top-tier
TEXT = (236, 238, 250)
SUB = (150, 156, 190)
PANEL = (12, 13, 28)

HERO_PX = 130
GAME_PX = 40
MAG = 3

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 18
HEADER_H = 64
SHEET_W = 860
SHEET_H = 600

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(NIGHT_TOP[i] + (NIGHT_BOT[i] - NIGHT_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(220):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(80, 200)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy), rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render("Skybit — GRIFFIN Skin · Round 2 (V4 converged)", True, TEXT), (PAD, 14))
sheet.blit(F_SUB.render(
    "Single ship build. Lion rump + dark tail-tuft outside the wing · feather→fur value step · dark beak/outline · neck-ruff.",
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
        crop, (max(1, int(crop.get_width() * f)), max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _grad_panel(rect, top, bot):
    p = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(p, c, (0, y), (rect.w, y))
    s2 = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s2, (255, 255, 255, 255), s2.get_rect(), border_radius=10)
    p2 = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    p2.blit(p, (0, 0))
    p2.blit(s2, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sheet.blit(p2, rect.topleft)


def _bg_tile(rect, day):
    _grad_panel(rect, DAY_TOP, DAY_BOT) if day else _grad_panel(rect, NIGHT_TOP, NIGHT_BOT)


# ── card 1: GRIFFIN — hero + 40px reads ──────────────────────────────────────
cx, cy = PAD, HEADER_H + PAD
CARD_W, CARD_H = 560, 480
card = pygame.Rect(cx, cy, CARD_W, CARD_H)
pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
pygame.draw.rect(sheet, GOLD, card, 3, border_radius=12)
sheet.blit(F_NAME.render("GRIFFIN  ·  skin_griffin", True, GOLD), (cx + 14, cy + 10))
sheet.blit(F_FEAT.render("eagle fore + lion rump · enormous swept wings · dark-tipped tail · two-creature seam",
                         True, SUB), (cx + 14, cy + 36))

# Hero panel — half night / half day.
hero_panel = pygame.Rect(cx + 14, cy + 62, 200, 280)
_grad_panel(pygame.Rect(hero_panel.x, hero_panel.y, hero_panel.w, hero_panel.h // 2),
            NIGHT_TOP, NIGHT_BOT)
_grad_panel(pygame.Rect(hero_panel.x, hero_panel.y + hero_panel.h // 2,
                        hero_panel.w, hero_panel.h - hero_panel.h // 2),
            DAY_TOP, DAY_BOT)
hero = smooth(get_griffin, 0, 0, HERO_PX)
sheet.blit(hero, hero.get_rect(center=hero_panel.center))
sheet.blit(F_TAG.render("130px hero (night / day)", True, (230, 230, 235)),
           (hero_panel.x + 6, hero_panel.bottom - 18))

# Game panel — smooth 40px (day + night) + NEAREST x3 across all 4 poses.
gp = pygame.Rect(cx + 226, cy + 62, 320, 280)
pygame.draw.rect(sheet, PANEL, gp, border_radius=10)

# Row 1: smooth 40px level over NIGHT, dive over DAY.
nrect = pygame.Rect(gp.x + 10, gp.y + 10, 140, 70)
drect = pygame.Rect(gp.x + 168, gp.y + 10, 140, 70)
_bg_tile(nrect, day=False)
_bg_tile(drect, day=True)
gl = smooth(get_griffin, 2, 0, GAME_PX)
sheet.blit(gl, gl.get_rect(center=nrect.center))
gd = smooth(get_griffin, 1, -32, GAME_PX)
sheet.blit(gd, gd.get_rect(center=drect.center))
sheet.blit(F_TAG.render("40px smooth  ·  night-level / day-dive", True, SUB),
           (gp.x + 10, gp.y + 84))

# Row 2: NEAREST x3 honest read — level over NIGHT, dive over DAY.
nlev = pygame.Rect(gp.x + 10, gp.y + 104, 140, 92)
ndiv = pygame.Rect(gp.x + 168, gp.y + 104, 140, 92)
_bg_tile(nlev, day=False)
_bg_tile(ndiv, day=True)
nl = nearest40(get_griffin, 2, 0, MAG)
sheet.blit(nl, nl.get_rect(center=nlev.center))
nd = nearest40(get_griffin, 1, -32, MAG)
sheet.blit(nd, nd.get_rect(center=ndiv.center))
sheet.blit(F_TAG.render("40px NEAREST x3  ·  night-level / day-dive", True, (210, 200, 150)),
           (gp.x + 10, gp.y + 200))

# Row 3: the two widest down-pose frames NEAREST x3 (rump must stay visible).
wlev = pygame.Rect(gp.x + 10, gp.y + 220, 140, 56)
wdiv = pygame.Rect(gp.x + 168, gp.y + 220, 140, 56)
_bg_tile(wlev, day=False)
_bg_tile(wdiv, day=True)
wl = nearest40(get_griffin, 0, 0, MAG)        # widest down-pose
sheet.blit(wl, wl.get_rect(center=wlev.center))
wd = nearest40(get_griffin, 0, -20, MAG)
sheet.blit(wd, wd.get_rect(center=wdiv.center))
sheet.blit(F_TAG.render("down-pose (widest wings) — rump + tail still outside the wing",
                        True, (210, 200, 150)), (gp.x + 10, gp.bottom - 16))

# ── card 2: DISTINCTIVENESS — griffin vs SHIPPING eagle, same 40px read ──────
ex0 = cx + CARD_W + PAD
ecard = pygame.Rect(ex0, cy, SHEET_W - ex0 - PAD, CARD_H)
pygame.draw.rect(sheet, CARD_BG, ecard, border_radius=12)
pygame.draw.rect(sheet, (120, 130, 160), ecard, 3, border_radius=12)
sheet.blit(F_NAME.render("vs SHIPPING EAGLE", True, (200, 210, 230)), (ex0 + 14, cy + 10))
sheet.blit(F_FEAT.render("same 40px NEAREST x3", True, SUB), (ex0 + 14, cy + 36))


def _vs_row(y, label, g_frame, g_tilt, e_frame, e_tilt, day):
    bg = pygame.Rect(ex0 + 14, y, ecard.w - 28, 92)
    _bg_tile(bg, day=day)
    gimg = nearest40(get_griffin, g_frame, g_tilt, MAG)
    eimg = nearest40(get_eagle, e_frame, e_tilt, MAG)
    sheet.blit(gimg, gimg.get_rect(center=(bg.x + bg.w // 4, bg.centery)))
    sheet.blit(eimg, eimg.get_rect(center=(bg.x + 3 * bg.w // 4, bg.centery)))
    tagcol = (40, 50, 70) if day else (210, 215, 235)
    sheet.blit(F_TAG.render("GRIFFIN", True, tagcol), (bg.x + 8, bg.y + 6))
    sheet.blit(F_TAG.render("EAGLE", True, tagcol), (bg.x + 3 * bg.w // 4 - 18, bg.y + 6))
    sheet.blit(F_FEAT.render(label, True, SUB), (ex0 + 14, bg.bottom + 2))


_vs_row(cy + 62, "level — night", 2, 0, 2, 0, day=False)
_vs_row(cy + 178, "level — bright day", 2, 0, 2, 0, day=True)
_vs_row(cy + 294, "dive — bright day", 1, -32, 1, -32, day=True)
for i, line in enumerate((
        "Tell: griffin keeps a gold lion rump +",
        "dark tail-tuft OUTSIDE the wing; eagle",
        "is one brown body, no tuft. Wing",
        "feathers darker/cooler = real value step.")):
    sheet.blit(F_FEAT.render(line, True, (210, 200, 150)),
               (ex0 + 14, cy + 404 + i * 17))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
