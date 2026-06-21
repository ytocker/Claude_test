"""Round-1 review sheet for the RETRO CHROME jet-fighter redesign.

Renders each of the 5 chrome takes at hero 130px AND at the in-game
truth-test scale (40px, level + dive tilt), plus a NEAREST-NEIGHBOR x3
magnification of those 40px reads — the honest gameplay-pixel silhouette
(smoothscale flatters tiny detail that vanishes in motion). Both DAY and
NIGHT backdrops per card, because the north star is "reads at 40px day AND
night". Headless (SDL dummy) so it runs in CI / on the build box.

The builds draw nose-RIGHT, upright, level. The secret skin flies inverted
nose-up in game, so the sheet applies the production 205° spin to every
read — what the reviewer sees is the true in-game attitude.
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
    "chrome_skins", os.path.join(_here, "chrome_skins.py"))
chrome_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chrome_skins)

BUILDERS = chrome_skins.BUILDERS

# The secret skin flies inverted nose-up; bake that spin into every read so the
# sheet shows the true in-game attitude rather than the flat planform.
GAME_SPIN = 205

ORDER = [
    ("chrome_v1", "V1 · SABRE RED-NOSE",
     "red radome + checker tail · swept · top-band chrome"),
    ("chrome_v2", "V2 · MIG RED-STAR",
     "red intake + fuselage star · straight wing · facet chrome"),
    ("chrome_v3", "V3 · BLUE-ANGEL TRIM",
     "blue+yellow spine stripe · swept · big bubble canopy"),
    ("chrome_v4", "V4 · RACING No.7",
     "black 7 roundel + anti-glare · deep-swept · raw mirror"),
    ("chrome_v5", "V5 · GOLD-BAR SABRE",
     "yellow rec-band + rivet panels · swept · red tips"),
]

# ── layout ───────────────────────────────────────────────────────────────────
COLS = 2
ROWS = (len(ORDER) + COLS - 1) // COLS
CARD_W, CARD_H = 470, 250
PAD = 16
HEADER_H = 64
HERO_PX = 130
GAME_PX = 40
MAG = 3

BG_TOP = (20, 22, 40)
BG_BOT = (34, 28, 52)
CARD_BG = (16, 17, 34)
CARD_EDGE = (96, 102, 140)
TEXT = (236, 238, 250)
SUB = (152, 158, 192)

# Day + night sky swatches for the dual-read panels.
DAY_TOP = (150, 200, 240)
DAY_BOT = (206, 230, 248)
NIGHT_TOP = (18, 20, 46)
NIGHT_BOT = (34, 26, 56)

SHEET_W = PAD + COLS * (CARD_W + PAD)
SHEET_H = HEADER_H + PAD + ROWS * (CARD_H + PAD)

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 28, bold=True)
F_SUB = pygame.font.SysFont("Arial", 14)
F_NAME = pygame.font.SysFont("Arial", 18, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 12)
F_TAG = pygame.font.SysFont("Arial", 11, bold=True)

sheet.blit(F_TITLE.render("Skybit — Secret JET FIGHTER · RETRO CHROME · Round 1", True, TEXT), (PAD, 12))
sheet.blit(F_SUB.render(
    "5 takes on a polished bare-metal Cold-War jet. HERO 130px · 40px level+dive (smooth) · NEAREST x3 (honest read) · DAY and NIGHT.",
    True, SUB), (PAD, 42))


def _grad_rect(target, rect, top, bot, radius=10):
    g = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(g, col, (0, y), (rect.w, y))
    mask = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
    g = g.convert_alpha()
    g.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    target.blit(g, rect.topleft)


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


# The game spins the flat planform 205° into the inverted nose-up attitude.
# The getter takes a tilt_deg; feeding GAME_SPIN (plus a dive delta) shows the
# real in-game pose. Level = pure spin; dive = spin minus a pitch-down delta.
LEVEL = GAME_SPIN
DIVE = GAME_SPIN - 32

for idx, (key, name, feat) in enumerate(ORDER):
    getter = BUILDERS[key]
    r, c = divmod(idx, COLS)
    cx = PAD + c * (CARD_W + PAD)
    cy = HEADER_H + PAD + r * (CARD_H + PAD)

    card = pygame.Rect(cx, cy, CARD_W, CARD_H)
    pygame.draw.rect(sheet, CARD_BG, card, border_radius=12)
    pygame.draw.rect(sheet, CARD_EDGE, card, 2, border_radius=12)

    sheet.blit(F_NAME.render(name, True, TEXT), (cx + 14, cy + 10))
    sheet.blit(F_FEAT.render(feat, True, SUB), (cx + 14, cy + 33))

    # Hero panel (left) on a split day/night ground so the chrome value reads
    # on both skies at large scale.
    hero_panel = pygame.Rect(cx + 12, cy + 52, 150, 182)
    _grad_rect(sheet, pygame.Rect(hero_panel.x, hero_panel.y, hero_panel.w // 2, hero_panel.h),
               DAY_TOP, DAY_BOT)
    _grad_rect(sheet, pygame.Rect(hero_panel.x + hero_panel.w // 2, hero_panel.y,
                                  hero_panel.w - hero_panel.w // 2, hero_panel.h),
               NIGHT_TOP, NIGHT_BOT)
    hero = smooth(getter, 0, LEVEL, HERO_PX)
    sheet.blit(hero, hero.get_rect(center=hero_panel.center))
    sheet.blit(F_TAG.render("130px  day | night", True, (40, 44, 60)),
               (hero_panel.x + 6, hero_panel.bottom - 16))

    # Right block: a DAY row and a NIGHT row, each with smooth 40px + NEAREST x3
    # for level and dive.
    rx = cx + 174
    rw = CARD_W - (174 + 14)
    for ri, (label, top, bot, txt) in enumerate((
            ("DAY", DAY_TOP, DAY_BOT, (40, 44, 60)),
            ("NIGHT", NIGHT_TOP, NIGHT_BOT, (200, 206, 235)))):
        ry = cy + 52 + ri * 92
        panel = pygame.Rect(rx, ry, rw, 86)
        _grad_rect(sheet, panel, top, bot)
        sheet.blit(F_TAG.render(label, True, txt), (panel.x + 6, panel.y + 4))

        # smooth 40px level + dive
        g_level = smooth(getter, 2, LEVEL, GAME_PX)
        sheet.blit(g_level, g_level.get_rect(center=(panel.x + 36, panel.y + 46)))
        g_dive = smooth(getter, 1, DIVE, GAME_PX)
        sheet.blit(g_dive, g_dive.get_rect(center=(panel.x + 78, panel.y + 46)))
        # NEAREST x3 level + dive (the honest read)
        n_level = nearest40(getter, 2, LEVEL, MAG)
        sheet.blit(n_level, n_level.get_rect(center=(panel.x + 150, panel.y + 46)))
        n_dive = nearest40(getter, 1, DIVE, MAG)
        sheet.blit(n_dive, n_dive.get_rect(center=(panel.x + 232, panel.y + 46)))
        sheet.blit(F_TAG.render("40px smooth      NEAREST x3  (level / dive)", True, txt),
                   (panel.x + 70, panel.y + 4))

out_path = os.path.join(_here, "round_1.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
