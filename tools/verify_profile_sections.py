"""Headless smoke + screenshot of the four Profile sections with seeded stats.
Run with PYTHONPATH=/home/user/skybit. Writes docs/profile/integrated_sections.png.
"""
import os
import tempfile
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game import store_data

store_data.STORE_FILE = tempfile.mktemp(suffix=".json")
store_data._IS_BROWSER = False
store_data._reset_for_test()
store_data.load()

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
hist = [max(0, int(40 * pow(2.718, -((i - 6) ** 2) / 18)) + random.randint(0, 4))
        for i in range(20)]
s["death_pillar_histogram"] = hist

from game.profile import ProfileScene

sc = ProfileScene()
pad = 12
sheet = pygame.Surface((pad + 4 * (360 + pad), pad * 2 + 640))
sheet.fill((18, 16, 22))
labels = ["GEAR", "STATS", "SHAME", "ARCADE"]
lf = pygame.font.Font(None, 22)
for i in range(4):
    sc.section = i
    sc.t = 1.2
    frame = pygame.Surface((360, 640))
    sc.render(frame)
    sheet.blit(frame, (pad + i * (360 + pad), pad))

out = "/home/user/skybit/docs/profile/integrated_sections.png"
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
