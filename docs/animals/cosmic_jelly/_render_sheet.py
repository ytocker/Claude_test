"""Round-2 review sheet for the FINAL COSMIC JELLY skin.

The art-director wants day-sky survival proven FIRST, so this sheet LEADS with
the honest gameplay read: the 40px sprite smoothscaled DOWN to in-game pixels
then magnified back x3 with NEAREST-NEIGHBOR, on a BRIGHT-DAY noon-sky panel
(level + dive). The night hero is secondary. Smoothscale flatters tiny detail
that vanishes in motion, so the NEAREST x3 read is the truth test for the rim,
diadem and swirl.

Single production build now (V4 SOLID VOID-CORE, perfected), so the sheet shows
the one creature across its 4 pulse frames rather than 5 candidates. Headless
(SDL dummy) so it runs in CI / on the build box.
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
    "cosmic_jelly_skins", os.path.join(_here, "cosmic_jelly_skins.py"))
cosmic_jelly_skins = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cosmic_jelly_skins)

getter = cosmic_jelly_skins.BUILDERS["skin_cosmic_jelly"]
WING_ANGLES = cosmic_jelly_skins._WING_ANGLES   # 50,20,-10,-40 = down→up

GAME_PX = 40
MAG = 3
HERO_PX = 130

# ── palette ───────────────────────────────────────────────────────────────────
BG_TOP = (12, 8, 30)
BG_BOT = (30, 16, 48)
CARD_BG = (10, 8, 24)
LEG_EDGE = (200, 160, 90)              # gold rim — legendary spectacle
TEXT = (236, 238, 250)
SUB = (150, 150, 190)
# A genuine bright NOON-sky blue — the value the dark void must survive against.
DAY_SKY = (150, 200, 245)
NIGHT_SKY = (16, 12, 36)
PANEL_DARK = (8, 6, 20)

pygame.font.init()
F_TITLE = pygame.font.SysFont("Arial", 30, bold=True)
F_SUB = pygame.font.SysFont("Arial", 15)
F_NAME = pygame.font.SysFont("Arial", 20, bold=True)
F_TAG = pygame.font.SysFont("Arial", 13, bold=True)
F_SMALL = pygame.font.SysFont("Arial", 12)


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


def nearest_truth(frame_idx, tilt, mag):
    """The truth test: smoothscale DOWN to 40px gameplay pixels, then magnify
    back up with NEAREST so we inspect exactly those gameplay pixels."""
    small = smooth(frame_idx, tilt, GAME_PX)
    return pygame.transform.scale(
        small, (small.get_width() * mag, small.get_height() * mag))


# ── sheet layout ──────────────────────────────────────────────────────────────
SHEET_W, SHEET_H = 1180, 720
sheet = pygame.Surface((SHEET_W, SHEET_H))
for y in range(SHEET_H):
    t = y / SHEET_H
    col = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
    pygame.draw.line(sheet, col, (0, y), (SHEET_W, y))
rng = random.Random(7)
for _ in range(180):
    sx, sy = rng.randint(0, SHEET_W), rng.randint(0, SHEET_H)
    b = rng.randint(60, 170)
    pygame.draw.circle(sheet, (b, b, min(255, b + 40)), (sx, sy), rng.choice([1, 1, 2]))

sheet.blit(F_TITLE.render(
    "Skybit — COSMIC JELLY (legendary)  ·  Round 2  ·  FINAL: V4 SOLID VOID-CORE",
    True, TEXT), (24, 16))
sheet.blit(F_SUB.render(
    "LEAD: 40px NEAREST x3 on a NOON-DAY sky (the honest gameplay truth) — level & dive, all 4 pulse frames.  Night hero secondary.",
    True, SUB), (24, 50))

PAD = 24


def labelled_sprite(panel, sprite, label, sub=None):
    sheet.blit(sprite, sprite.get_rect(center=(panel.centerx, panel.centery - (8 if sub else 0))))
    sheet.blit(F_SMALL.render(label, True, TEXT), (panel.x + 6, panel.bottom - 18))
    if sub:
        sheet.blit(F_SMALL.render(sub, True, (90, 70, 30)), (panel.x + 6, panel.bottom - 34))


# ════════ LEAD PANEL: 40px NEAREST x3 on a BRIGHT-DAY sky, level + dive ════════
lead = pygame.Rect(PAD, 80, 740, 360)
pygame.draw.rect(sheet, CARD_BG, lead, border_radius=14)
pygame.draw.rect(sheet, LEG_EDGE, lead, 3, border_radius=14)
sheet.blit(F_NAME.render("DAY-SKY TRUTH TEST — 40px NEAREST x3", True, LEG_EDGE),
           (lead.x + 16, lead.y + 12))
sheet.blit(F_SMALL.render(
    "the dark void-core + violet rim + gold diadem must hold their edge on noon blue",
    True, SUB), (lead.x + 16, lead.y + 40))

# Four pulse frames (down→up) shown level, plus a dive-tilt strip below.
cell_w = (lead.w - 40) // 4
for i in range(4):
    px = lead.x + 16 + i * cell_w
    # LEVEL on day sky
    p_lvl = pygame.Rect(px, lead.y + 66, cell_w - 8, 120)
    pygame.draw.rect(sheet, DAY_SKY, p_lvl, border_radius=8)
    spr = nearest_truth(i, 0, MAG)
    labelled_sprite(p_lvl, spr, f"frame {i} {'contract' if i == 0 else 'billow' if i == 3 else 'level'}")
    # DIVE on day sky
    p_dv = pygame.Rect(px, lead.y + 196, cell_w - 8, 120)
    pygame.draw.rect(sheet, DAY_SKY, p_dv, border_radius=8)
    spr2 = nearest_truth(i, -32, MAG)
    labelled_sprite(p_dv, spr2, f"dive -32deg")

sheet.blit(F_TAG.render("LEVEL  (above)        DIVE -32deg  (below)", True, (60, 50, 30)),
           (lead.x + 16, lead.bottom - 20))

# ════════ SECONDARY: NIGHT HERO + night 40px truth ════════
night = pygame.Rect(PAD + 760, 80, SHEET_W - (PAD + 760) - PAD, 360)
pygame.draw.rect(sheet, CARD_BG, night, border_radius=14)
pygame.draw.rect(sheet, LEG_EDGE, night, 3, border_radius=14)
sheet.blit(F_NAME.render("NIGHT HERO", True, LEG_EDGE), (night.x + 16, night.y + 12))

hero_panel = pygame.Rect(night.x + 16, night.y + 48, night.w - 32, 180)
pygame.draw.rect(sheet, NIGHT_SKY, hero_panel, border_radius=10)
hero = smooth(3, 0, HERO_PX)                 # billow pose hero
sheet.blit(hero, hero.get_rect(center=hero_panel.center))
sheet.blit(F_SMALL.render("130px · billow pose", True, SUB),
           (hero_panel.x + 8, hero_panel.bottom - 18))

# Night 40px NEAREST x3 (level + dive) so day vs night reads can be compared.
nt = pygame.Rect(night.x + 16, night.y + 236, night.w - 32, 96)
pygame.draw.rect(sheet, PANEL_DARK, nt, border_radius=10)
nl = nearest_truth(2, 0, MAG)
sheet.blit(nl, nl.get_rect(center=(nt.x + nt.w // 4, nt.centery - 4)))
nd = nearest_truth(1, -32, MAG)
sheet.blit(nd, nd.get_rect(center=(nt.x + 3 * nt.w // 4, nt.centery - 4)))
sheet.blit(F_SMALL.render("40px NEAREST x3 on night  (level / dive)", True, SUB),
           (nt.x + 8, nt.bottom - 18))

# ════════ BOTTOM: hero on DAY + the 4-frame pulse film-strip ════════
bottom = pygame.Rect(PAD, 460, SHEET_W - 2 * PAD, 240)
pygame.draw.rect(sheet, CARD_BG, bottom, border_radius=14)
pygame.draw.rect(sheet, LEG_EDGE, bottom, 3, border_radius=14)
sheet.blit(F_NAME.render("130px HERO on DAY  +  pulse / core-breathe film-strip (down → up)",
                         True, LEG_EDGE), (bottom.x + 16, bottom.y + 12))

day_hero = pygame.Rect(bottom.x + 16, bottom.y + 46, 200, 178)
pygame.draw.rect(sheet, DAY_SKY, day_hero, border_radius=10)
dh = smooth(3, 0, 150)
sheet.blit(dh, dh.get_rect(center=day_hero.center))
sheet.blit(F_SMALL.render("130px · day · billow", True, (60, 50, 30)),
           (day_hero.x + 8, day_hero.bottom - 18))

# 4-frame film-strip at 90px on night so the core-breathe + diadem pulse reads.
strip_x = bottom.x + 236
fw = (bottom.w - 236 - 16) // 4
labels = ("contract (small dense core)", "level", "level", "billow (big bright core)")
for i in range(4):
    fp = pygame.Rect(strip_x + i * fw, bottom.y + 46, fw - 8, 178)
    pygame.draw.rect(sheet, NIGHT_SKY, fp, border_radius=10)
    fr = smooth(i, 0, 120)
    sheet.blit(fr, fr.get_rect(center=fp.center))
    sheet.blit(F_SMALL.render(f"f{i}", True, TEXT), (fp.x + 6, fp.y + 6))
    sheet.blit(F_SMALL.render(labels[i], True, SUB), (fp.x + 6, fp.bottom - 18))

out_path = os.path.join(_here, "round_2.png")
pygame.image.save(sheet, out_path)
print("wrote", out_path, sheet.get_size())
