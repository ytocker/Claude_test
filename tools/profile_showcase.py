"""Compose a single showcase figure of the new Profile sections for review.

Renders the four live Profile tabs (GEAR / STATS / SHAME / ARCADE) with seeded
stats + a few owned cosmetics, lays them in a captioned row, and adds a second
row of zoomed detail crops of the witty bits. Writes docs/profile/showcase.png.
Run with PYTHONPATH=/home/user/skybit.
"""
import os
import tempfile
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import store_data, store_catalog
from game.config import W, H

store_data.STORE_FILE = tempfile.mktemp(suffix=".json")
store_data._IS_BROWSER = False
store_data._reset_for_test()
store_data.load()

# A wallet + a few owned cosmetics so GEAR isn't bare.
store_data.add_coins(1840)
for grp in ("parrot", "shades", "parcels"):
    try:
        for sid in list(store_catalog.ids_of_group(grp))[:3]:
            store_data.grant(sid)
    except Exception:
        pass

s = store_data.all_stats()
s.update({
    "runs_played": 2941, "total_time_s": 63 * 3600, "total_pillars": 48200,
    "total_coins_earned": 271000, "best_score": 1284, "best_pillars": 312,
    "best_time_s": 247, "best_near_misses": 19, "scoreless_deaths": 5,
    "pillar1_deaths": 12, "sub3s_deaths": 14, "max_flaps_per_sec": 11,
    "coins_ignored": 8420, "same_pillar_streak": 4, "last_death_pillar": 6,
    "deaths_with_powerup": {"ghost": 2, "kfc": 1},
    "powerups_by_kind": {"magnet": 40, "kfc": 6},
    "last_dignified_date": "2026-06-15",
})
random.seed(1)
s["death_pillar_histogram"] = [
    max(0, int(40 * pow(2.718, -((i - 6) ** 2) / 18)) + random.randint(0, 4))
    for i in range(20)]

from game.profile import ProfileScene

scene = ProfileScene()
frames = []
for sec in range(4):
    scene.section = sec
    scene.t = 1.2
    fr = pygame.Surface((W, H))
    scene.render(fr)
    frames.append(fr)

GOLD = (236, 196, 110)
PALE = (208, 196, 220)
BG = (14, 12, 20)
pad, gap = 18, 14
title_h, cap_h = 58, 28

cols = 4
row1_w = pad * 2 + cols * W + (cols - 1) * gap
sheet_w = row1_w

# detail crops: (frame index, src rect, header)
details = [
    (1, pygame.Rect(8, 320, W - 16, 250),
     "Nemesis histogram + days-since-dignified board"),
    (2, pygame.Rect(8, 150, W - 16, 250),
     "Wall of Shame — tiered tarnished badges"),
    (3, pygame.Rect(8, 150, W - 16, 250),
     "Arcade curios — coin-wired"),
]
d_cols = len(details)
d_w = (sheet_w - pad * 2 - (d_cols - 1) * gap) // d_cols
d_scale = d_w / details[0][1].width
d_h = int(details[0][1].height * d_scale)
dhead_h = 26

row1_top = title_h
row2_top = row1_top + cap_h + H + gap + 6
sheet_h = row2_top + dhead_h + d_h + pad

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

big = pygame.font.Font(None, 40)
cap = pygame.font.Font(None, 24)
hf = pygame.font.Font(None, 24)

t1 = big.render("Skybit Profile  —  Stats · Hall of Shame · Arcade", True, GOLD)
sheet.blit(t1, t1.get_rect(center=(sheet_w // 2, title_h // 2 + 2)))

labels = ["GEAR — loadout + owned cosmetics",
          "STATS — bests · lifetime · histogram",
          "SHAME — anti-achievements + title",
          "ARCADE — crystal · vending · Beakon"]
for i, fr in enumerate(frames):
    x = pad + i * (W + gap)
    y = row1_top + cap_h
    ci = cap.render(labels[i], True, PALE)
    sheet.blit(ci, ci.get_rect(center=(x + W // 2, row1_top + cap_h // 2)))
    sheet.blit(fr, (x, y))
    pygame.draw.rect(sheet, (60, 52, 40), (x - 1, y - 1, W + 2, H + 2), 1)

for j, (fi, rect, head) in enumerate(details):
    x = pad + j * (d_w + gap)
    hi = hf.render(head, True, PALE)
    sheet.blit(hi, hi.get_rect(midleft=(x, row2_top + dhead_h // 2)))
    crop = frames[fi].subsurface(rect).copy()
    crop = pygame.transform.smoothscale(crop, (d_w, d_h))
    sheet.blit(crop, (x, row2_top + dhead_h))
    pygame.draw.rect(sheet, (60, 52, 40),
                     (x - 1, row2_top + dhead_h - 1, d_w + 2, d_h + 2), 1)

out = "/home/user/skybit/docs/profile/showcase.png"
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
