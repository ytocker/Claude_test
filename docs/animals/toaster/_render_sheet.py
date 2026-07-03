"""Round-2 review sheet for the production FLYING TOASTER store skin.

Renders the single converged NOIR CHROME build at hero 130px AND at the
in-game truth-test scale (40px, level + dive tilt) with a NEAREST-NEIGHBOR x3
magnification of the 40px reads — the honest gameplay-pixel silhouette
(smoothscale flatters tiny detail that vanishes in motion). The 40px reads run
on BOTH a DAY sky and a NIGHT sky so the chrome/gold/ember contrast is verified
across the full biome cycle. A flap strip shows all 4 frames so the toast-pop
and ember mid-pop are visible. A deuteranope simulation of the 40px reads
confirms the gold toast stays distinct from the orange ember slot.

Headless (SDL dummy) so it runs in CI / on the build box.
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
    "toaster_skins", os.path.join(_here, "toaster_skins.py"))
toaster_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toaster_skins)

GET = toaster_skins.BUILDERS["skin_toaster"]

# ── layout ───────────────────────────────────────────────────────────────────
PAD = 22
HEADER_H = 74
HERO_PX = 130
GAME_PX = 40
MAG = 3

DAY_TOP = (118, 196, 236)
DAY_BOT = (224, 232, 200)
DAY_BRIGHT = (180, 222, 248)         # the brightest pale-blue day band — the
DAY_BRIGHT2 = (210, 236, 250)        # crispness stress test for the body
NIGHT_TOP = (22, 26, 54)
NIGHT_BOT = (44, 32, 62)

SHEET_BG_TOP = (18, 20, 40)
SHEET_BG_BOT = (34, 26, 52)
PANEL_BG = (16, 17, 34)
EDGE = (188, 150, 72)
TEXT = (238, 240, 250)
SUB = (154, 160, 192)

SHEET_W = 1120
SHEET_H = 790

sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(SHEET_BG_TOP[i] + (SHEET_BG_BOT[i] - SHEET_BG_TOP[i]) * t)
                for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))

import random
rng = random.Random(11)
for _ in range(220):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(70, 190)
    pygame.draw.circle(sheet, (b, b, min(255, b + 30)), (sx, sy),
                       rng.choice([1, 1, 2]))

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 26, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_FEAT = pygame.font.SysFont("Arial", 13)
F_TAG = pygame.font.SysFont("Arial", 12, bold=True)

sheet.blit(F_TITLE.render(
    "Skybit — FLYING TOASTER (skin_toaster) · Round 2 · NOIR CHROME (converged)",
    True, EDGE), (PAD, 16))
sheet.blit(F_SUB.render(
    "Soft feathered After-Dark wings · thick warm ember bar · toast clamped inside top edge · darker day belly · "
    "deuteranope-checked.",
    True, SUB), (PAD, 50))


def _crop(frame_idx, tilt):
    s = GET(frame_idx, tilt)
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
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


def _sky(rect, top, bot):
    s = pygame.Surface((rect.w, rect.h))
    for y in range(rect.h):
        t = y / max(1, rect.h)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        pygame.draw.line(s, col, (0, y), (rect.w, y))
    return s


def deuter(surf):
    """A simple deuteranope (green-blind) simulation so the review proves the
    gold toast and orange ember stay distinguishable for red-green deficiency.
    Brettel-style approximation collapsing onto the protan/deutan confusion
    line — good enough to catch warm-band merges."""
    out = surf.copy()
    out.lock()
    w, h = out.get_size()
    for y in range(h):
        for x in range(w):
            r, g, b, a = out.get_at((x, y))
            if a == 0:
                continue
            # Deuteranope LMS→RGB collapse (linearised-ish, integer-cheap).
            nr = int(0.625 * r + 0.375 * g)
            ng = int(0.700 * r + 0.300 * g)
            nb = int(0.300 * g + 0.700 * b)
            out.set_at((x, y), (min(255, nr), min(255, ng), min(255, nb), a))
    out.unlock()
    return out


# ── HERO panel (night) ────────────────────────────────────────────────────────
hero_panel = pygame.Rect(PAD, HEADER_H + PAD, 230, 300)
sheet.blit(_sky(hero_panel, NIGHT_TOP, NIGHT_BOT), hero_panel)
pygame.draw.rect(sheet, EDGE, hero_panel, 2, border_radius=12)
hero = smooth(0, 0, HERO_PX)
sheet.blit(hero, hero.get_rect(center=(hero_panel.centerx, hero_panel.centery - 14)))
sheet.blit(F_TAG.render("HERO 130px · night", True, (220, 224, 240)),
           (hero_panel.x + 10, hero_panel.bottom - 22))

# Hero on the BRIGHTEST day band — the silhouette-crispness stress test.
hero_day = pygame.Rect(PAD, hero_panel.bottom + PAD, 230, 240)
sheet.blit(_sky(hero_day, DAY_BRIGHT, DAY_BRIGHT2), hero_day)
pygame.draw.rect(sheet, EDGE, hero_day, 2, border_radius=12)
hero2 = smooth(2, 0, HERO_PX)
sheet.blit(hero2, hero2.get_rect(center=(hero_day.centerx, hero_day.centery - 10)))
sheet.blit(F_TAG.render("HERO 130px · brightest day", True, (40, 50, 60)),
           (hero_day.x + 10, hero_day.bottom - 22))

# ── 40px reads (right column): DAY + NIGHT, level + dive, NEAREST x3 ──────────
gx = hero_panel.right + PAD
cell_w = 410
cell_h = 130
rows = (("DAY · level / dive", DAY_TOP, DAY_BOT, (40, 50, 60)),
        ("NIGHT · level / dive", NIGHT_TOP, NIGHT_BOT, (220, 224, 240)))
for ri, (label, top, bot, txtc) in enumerate(rows):
    cell = pygame.Rect(gx, HEADER_H + PAD + ri * (cell_h + 12), cell_w, cell_h)
    sheet.blit(_sky(cell, top, bot), cell)
    pygame.draw.rect(sheet, (96, 100, 128), cell, 1, border_radius=10)
    n_level = nearest40(2, 0, MAG)
    sheet.blit(n_level, n_level.get_rect(center=(cell.x + 130, cell.centery + 6)))
    n_dive = nearest40(1, -32, MAG)
    sheet.blit(n_dive, n_dive.get_rect(center=(cell.x + 300, cell.centery + 6)))
    sheet.blit(F_TAG.render(label + "  · 40px NEAREST x3", True, txtc),
               (cell.x + 8, cell.y + 6))

# ── flap strip: all 4 frames at 40px NEAREST x3 on night (toast-pop + ember) ──
strip = pygame.Rect(gx, HEADER_H + PAD + 2 * (cell_h + 12), cell_w, 140)
sheet.blit(_sky(strip, NIGHT_TOP, NIGHT_BOT), strip)
pygame.draw.rect(sheet, (96, 100, 128), strip, 1, border_radius=10)
sheet.blit(F_TAG.render("FLAP CYCLE · 4 frames · watch the toast mid-pop + ember",
                        True, (220, 224, 240)), (strip.x + 8, strip.y + 6))
for fi in range(4):
    fr = nearest40(fi, 0, MAG)
    sheet.blit(fr, fr.get_rect(center=(strip.x + 56 + fi * 100, strip.centery + 8)))

# ── deuteranope check strip (bottom-left, under the heroes) ───────────────────
dpanel = pygame.Rect(PAD, hero_day.bottom + PAD, 230, 110)
sheet.blit(_sky(dpanel, NIGHT_TOP, NIGHT_BOT), dpanel)
pygame.draw.rect(sheet, EDGE, dpanel, 1, border_radius=10)
sheet.blit(F_TAG.render("DEUTERANOPE · level", True, (220, 224, 240)),
           (dpanel.x + 8, dpanel.y + 6))
d_norm = nearest40(2, 0, 2)
d_sim = deuter(d_norm)
sheet.blit(d_norm, d_norm.get_rect(center=(dpanel.x + 64, dpanel.centery + 8)))
sheet.blit(d_sim, d_sim.get_rect(center=(dpanel.x + 158, dpanel.centery + 8)))
sheet.blit(F_FEAT.render("normal / deuter", True, SUB),
           (dpanel.x + 8, dpanel.bottom - 18))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
