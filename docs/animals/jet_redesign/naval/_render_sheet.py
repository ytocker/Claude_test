"""Round-1 review sheet for the NAVAL INTERCEPTOR jet redesign candidates.

Renders each of the 5 sub-takes at hero 130px AND at the in-game truth-test
scale (40px, level + dive tilt), with a NEAREST-NEIGHBOR x3 magnification of
those 40px reads so the true gameplay-pixel silhouette is honest (smoothscale
flatters tiny detail that vanishes in motion). Crucially, every read is shown
on BOTH a DAY sky and a NIGHT sky panel — the north star is "reads at 40px on
day AND night". Headless (SDL dummy) so it runs in CI / on the build box.

NOTE on attitude: the candidates draw the jet NOSE-RIGHT / UPRIGHT / LEVEL
(no baked rotation), matching the redesign brief — the game applies the
inverted nose-up presentation later. So this sheet shows the clean upright
planform, which is what the builds must nail.
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
    "naval_skins", os.path.join(_here, "naval_skins.py"))
naval_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(naval_skins)

VARIANTS = naval_skins.VARIANTS
ORDER = ["naval_v1", "naval_v2", "naval_v3", "naval_v4", "naval_v5"]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 1
CARD_W, CARD_H = 720, 196
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Day sky (gameplay daytime gradient) vs night sky (deep blue).
DAY_TOP = (126, 196, 232)
DAY_BOT = (196, 228, 240)
NIGHT_TOP = (20, 24, 52)
NIGHT_BOT = (38, 30, 62)

SHEET_BG_TOP = (16, 18, 36)
SHEET_BG_BOT = (30, 24, 50)
CARD_BG = (18, 20, 38)
CARD_EDGE = (70, 76, 124)
LEAD_EDGE = (210, 168, 80)             # gold rim on the lead candidate (v1)
TEXT = (236, 238, 250)
SUB = (152, 158, 192)
TAGD = (60, 70, 86)
TAGN = (200, 206, 240)

ROWS = len(ORDER)
SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_TOP[i] + (SHEET_BG_BOT[i] - SHEET_BG_TOP[i]) * t)
               for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 19, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 11, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — JET FIGHTER redesign · NAVAL INTERCEPTOR · Round 1", True, TEXT),
    (PAD, 14))
sheet.blit(F_SUB.render(
    "F-14 Tomcat vibe: variable-sweep wings + twin canted tails + tandem fuselage. "
    "HERO 130px · 40px level/dive NEAREST x3 (the honest read) on DAY and NIGHT skies. "
    "Drawn nose-right/upright (game inverts later).",
    True, SUB), (PAD, 42))


def _sky(w, h, top, bot, stars=False):
    s = pygame.Surface((w, h))
    for y in range(h):
        t = y / h
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (w, y))
    if stars:
        import random
        rng = random.Random(11)
        for _ in range(int(w * h / 600)):
            sx, sy = rng.randint(0, w - 1), rng.randint(0, h - 1)
            b = rng.randint(120, 220)
            pygame.draw.circle(s, (b, b, min(255, b + 30)), (sx, sy), 1)
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
        crop, (max(1, int(crop.get_width() * f)),
               max(1, int(crop.get_height() * f))))


def nearest40(getter, frame_idx, tilt, mag):
    small = smooth(getter, frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _panel(label, sky, getter):
    """One sky panel: hero 130px on the left, then 40px-smooth (top) and
    40px-NEAREST-x3 (bottom) level/dive reads — the honest read."""
    p = sky.copy()
    pygame.draw.rect(p, (255, 255, 255, 30), p.get_rect(), 1)
    # Hero.
    hero = smooth(getter, 0, 0, HERO_PX)
    p.blit(hero, hero.get_rect(center=(78, p.get_height() // 2)))
    # 40px smooth level + dive.
    g_level = smooth(getter, 2, 0, GAME_PX)
    p.blit(g_level, g_level.get_rect(center=(178, 36)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    p.blit(g_dive, g_dive.get_rect(center=(232, 36)))
    # 40px NEAREST x3 level + dive.
    n_level = nearest40(getter, 2, 0, MAG)
    p.blit(n_level, n_level.get_rect(center=(182, 118)))
    n_dive = nearest40(getter, 1, -32, MAG)
    p.blit(n_dive, n_dive.get_rect(center=(252, 118)))
    return p


for idx, key in enumerate(ORDER):
    name, feat, getter = VARIANTS[key]
    cy = HEADER_H + PAD + idx * (CARD_H + PAD)
    cx = PAD
    is_lead = key == "naval_v1"
    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, LEAD_EDGE if is_lead else CARD_EDGE,
                     card, 3 if is_lead else 2, border_radius=12)

    sheet.blit(F_NAME.render(("v%d · " % (idx + 1)) + name, True,
                             LEAD_EDGE if is_lead else TEXT), (cx + 14, cy + 8))
    sheet.blit(F_FEAT.render(feat, True, SUB), (cx + 14, cy + 32))
    if is_lead:
        sheet.blit(F_TAG.render("LEAD (skin_naval)", True, LEAD_EDGE),
                   (CARD_W - 110, cy + 12))

    PW, PH = 320, 144
    py = cy + 46
    day = _sky(PW, PH, DAY_TOP, DAY_BOT)
    night = _sky(PW, PH, NIGHT_TOP, NIGHT_BOT, stars=True)
    dpanel = _panel(name, day, getter)
    npanel = _panel(name, night, getter)
    sheet.blit(dpanel, (cx + 14, py))
    sheet.blit(npanel, (cx + 14 + PW + 16, py))

    # Panel captions.
    sheet.blit(F_TAG.render("DAY", True, TAGD), (cx + 18, py + 2))
    sheet.blit(F_TAG.render("NIGHT", True, TAGN), (cx + 14 + PW + 20, py + 2))
    for bx in (cx + 14, cx + 14 + PW + 16):
        sheet.blit(F_TAG.render("130px", True, (90, 90, 90)), (bx + 4, py + PH - 16))
        sheet.blit(F_TAG.render("40px smooth", True, (90, 90, 90)),
                   (bx + 150, py + 2))
        sheet.blit(F_TAG.render("40px NEAREST x3  (level / dive)", True,
                               (200, 180, 120)), (bx + 138, py + PH - 16))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
