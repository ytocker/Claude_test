"""Round-2 review sheet for the NAVAL INTERCEPTOR jet redesign — the single
converged production build (JOLLY ROGERS).

Renders the ONE build at hero 130px AND at the in-game truth-test scale
(40px, level + dive tilt), with a NEAREST-NEIGHBOR x3 magnification of those
40px reads so the true gameplay-pixel silhouette is honest (smoothscale
flatters tiny detail that vanishes in motion). Every read is shown on THREE
backgrounds — a DAY sky, a NIGHT sky, AND a DAY warm-sandstone-PILLAR case —
because the north star is "reads at 40px on day AND night, and never melts
into a pillar". Headless (SDL dummy) so it runs in CI / on the build box.

NOTE on attitude: the build draws the jet NOSE-RIGHT / UPRIGHT / LEVEL (no
baked rotation), matching the redesign brief — the game applies the inverted
nose-up presentation later. So this sheet shows the clean upright planform,
which is what the build must nail.
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

from game.draw import get_stone_pillar_body

GETTER = naval_skins.get_naval

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 16
HEADER_H = 70
HERO_PX = 130
GAME_PX = 40
MAG = 3

# Day sky (gameplay daytime gradient) vs night sky (deep blue).
DAY_TOP = (126, 196, 232)
DAY_BOT = (196, 228, 240)
NIGHT_TOP = (20, 24, 52)
NIGHT_BOT = (38, 30, 62)

# DAY sandstone pillar palette (game/biome.py DAY phase) — the warm
# background the dark airframe must NOT melt into.
STONE_LIGHT = (225, 195, 155)
STONE_MID   = (175, 140, 105)
STONE_DARK  = (95, 70, 55)
STONE_ACCENT = (255, 220, 170)

SHEET_BG_TOP = (16, 18, 36)
SHEET_BG_BOT = (30, 24, 50)
CARD_BG = (18, 20, 38)
LEAD_EDGE = (210, 168, 80)
TEXT = (236, 238, 250)
SUB = (152, 158, 192)
TAGD = (60, 70, 86)
TAGN = (200, 206, 240)

PW, PH = 320, 196
SHEET_W = PAD + 3 * (PW + PAD)
SHEET_H = HEADER_H + PAD + PH + PAD + 120

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_TOP[i] + (SHEET_BG_BOT[i] - SHEET_BG_TOP[i]) * t)
               for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 26, bold=True)
F_SUB = pygame.font.SysFont("Arial", 13)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 12)
F_TAG = pygame.font.SysFont("Arial", 11, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — JET FIGHTER redesign · NAVAL INTERCEPTOR · Round 2 (production)",
    True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "v3 JOLLY ROGERS converged: deep-navy single mass · CONTINUOUS gold leading-edge "
    "rail · cool canopy · warm twin burner. HERO 130px + 40px NEAREST x3 level/dive "
    "on DAY · NIGHT · DAY-PILLAR.", True, SUB), (PAD, 42))


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


def _pillar_bg(w, h):
    """Day sky with two warm sandstone pillar columns intruding from top and
    bottom — the worst-case 'dark airframe over warm stone' read. The jet is
    centred so its dark body overlaps a warm pillar where it would otherwise
    melt in."""
    s = _sky(w, h, DAY_TOP, DAY_BOT)
    body_seed = 3
    col_w = 78
    for cx in (96, w - 96):
        # Top pillar hanging down, bottom pillar rising up.
        top = get_stone_pillar_body(col_w, h // 2 + 10, STONE_LIGHT, STONE_MID,
                                    STONE_DARK, STONE_ACCENT, body_seed)
        s.blit(top, (cx - col_w // 2, 0))
        bot = get_stone_pillar_body(col_w, h // 2 + 10, STONE_LIGHT, STONE_MID,
                                    STONE_DARK, STONE_ACCENT, body_seed + 1)
        s.blit(bot, (cx - col_w // 2, h - (h // 2 + 10)))
        body_seed += 2
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


def _panel(sky, getter):
    """One background panel: hero 130px on the left, then 40px-smooth (top)
    and 40px-NEAREST-x3 (bottom) level/dive reads — the honest read."""
    p = sky.copy()
    pygame.draw.rect(p, (255, 255, 255, 30), p.get_rect(), 1)
    hero = smooth(getter, 0, 0, HERO_PX)
    p.blit(hero, hero.get_rect(center=(76, p.get_height() // 2)))
    g_level = smooth(getter, 2, 0, GAME_PX)
    p.blit(g_level, g_level.get_rect(center=(176, 44)))
    g_dive = smooth(getter, 1, -32, GAME_PX)
    p.blit(g_dive, g_dive.get_rect(center=(230, 44)))
    n_level = nearest40(getter, 2, 0, MAG)
    p.blit(n_level, n_level.get_rect(center=(180, 132)))
    n_dive = nearest40(getter, 1, -32, MAG)
    p.blit(n_dive, n_dive.get_rect(center=(250, 132)))
    return p


py = HEADER_H + 4
panels = [
    ("DAY", TAGD, _sky(PW, PH, DAY_TOP, DAY_BOT)),
    ("NIGHT", TAGN, _sky(PW, PH, NIGHT_TOP, NIGHT_BOT, stars=True)),
    ("DAY · WARM PILLAR", (120, 80, 40), _pillar_bg(PW, PH)),
]
for i, (label, tagcol, bg) in enumerate(panels):
    px = PAD + i * (PW + PAD)
    panel = _panel(bg, GETTER)
    sheet.blit(panel, (px, py))
    sheet.blit(F_TAG.render(label, True, tagcol), (px + 6, py + 4))
    sheet.blit(F_TAG.render("130px", True, (90, 90, 90)), (px + 6, py + PH - 16))
    sheet.blit(F_TAG.render("40px smooth", True, (200, 200, 200)),
               (px + 150, py + 4))
    sheet.blit(F_TAG.render("40px NEAREST x3  (level / dive)", True,
                            (210, 190, 130)), (px + 138, py + PH - 16))

# ── Frame strip: all 4 baked poses at 40px NEAREST x3 to prove the burner
#    footprint pulses ~2px between frames + the gold rail / canopy are
#    constant across the pulse. ───────────────────────────────────────────────
fy = py + PH + PAD
sheet.blit(F_NAME.render("All 4 afterburner-pulse frames  ·  40px NEAREST x3  ·  "
                         "burner footprint pulses, gold rail + canopy constant",
                         True, LEAD_EDGE), (PAD, fy))
strip = _sky((PW + PAD) * 3, 84, NIGHT_TOP, NIGHT_BOT, stars=True)
for f in range(4):
    img = nearest40(GETTER, f, 0, MAG)
    strip.blit(img, img.get_rect(center=(70 + f * 150, 44)))
sheet.blit(strip, (PAD, fy + 26))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
