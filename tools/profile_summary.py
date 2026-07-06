"""Compose a one-figure STATUS SUMMARY of the Profile work: a title/status band,
the four live section screenshots, a 'what's in it' bullet panel under each, and
a footer of under-the-hood facts + remaining polish. Writes
docs/profile/profile_summary.png. Run with PYTHONPATH=/home/user/skybit.
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

GOLD = (238, 198, 112)
CREAM = (232, 222, 210)
PALE = (196, 186, 210)
BG = (13, 11, 19)
PANEL = (26, 22, 36)

pad, gap = 18, 14
title_h, status_h, head_h = 50, 30, 26
shot_h = H
panel_h = 214
foot_h = 76

sheet_w = pad * 2 + 4 * W + 3 * gap
y_head = title_h + status_h
y_shot = y_head + head_h
y_panel = y_shot + shot_h + 10
y_foot = y_panel + panel_h + 14
sheet_h = y_foot + foot_h + pad

sheet = pygame.Surface((sheet_w, sheet_h))
sheet.fill(BG)

f_title = pygame.font.Font(None, 42)
f_status = pygame.font.Font(None, 25)
f_head = pygame.font.Font(None, 27)
f_bul = pygame.font.Font(None, 22)
f_foot = pygame.font.Font(None, 22)


def wrap(font, text, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if font.size(t)[0] <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


ti = f_title.render("Skybit  —  Profile Section:  Status & Contents", True, GOLD)
sheet.blit(ti, ti.get_rect(center=(sheet_w // 2, title_h // 2 + 4)))
st = f_status.render(
    "Built · integrated · 80 unit tests green · pushed to "
    "v5_store_profile   —   a 4-section switcher on the Profile screen",
    True, CREAM)
sheet.blit(st, st.get_rect(center=(sheet_w // 2, title_h + status_h // 2)))

heads = ["GEAR", "STATS", "SHAME", "ARCADE"]
bullets = [
    ["Live loadout hero (equipped", "parrot + parcel)",
     "Owned-cosmetics grid — tap to equip",
     "The original screen, now tab 1"],
    ["Personal bests: score / pillars /", "flight / near-miss",
     "Lifetime: runs, time aloft, pillars, coins",
     "“Days since last dignified flight” board",
     "Nemesis death-histogram (Gerald)"],
    ["Tarnished anti-achievement badges",
     "Witty glyph + tier per badge",
     "(bronze / silver / gold by value)",
     "Locked badges show progress",
     "Auto-saddled demeaning title"],
    ["Crystal Ball — “predicts” next run (free)",
     "Vending Machine — 5 coins -> junk",
     "Master Beakon — 20 coins for",
     "“tips for life”",
     "Coins wired through store_data"],
]

for i, fr in enumerate(frames):
    x = pad + i * (W + gap)
    hi = f_head.render(heads[i], True, GOLD)
    sheet.blit(hi, hi.get_rect(center=(x + W // 2, y_head + head_h // 2)))
    sheet.blit(fr, (x, y_shot))
    pygame.draw.rect(sheet, (64, 54, 42), (x - 1, y_shot - 1, W + 2, shot_h + 2), 1)

    pr = pygame.Rect(x, y_panel, W, panel_h)
    pygame.draw.rect(sheet, PANEL, pr, border_radius=10)
    pygame.draw.rect(sheet, (70, 58, 46), pr, 1, border_radius=10)
    ty = pr.y + 14
    for b in bullets[i]:
        lead = b.startswith(("(", "“")) or b.endswith(("+", "→")) is False and \
            b[0].islower()
        prefix = "" if b[0].islower() or b.startswith(("(", "“")) else "• "
        for k, line in enumerate(wrap(f_bul, prefix + b, W - 28)):
            li = f_bul.render(line, True, CREAM if k == 0 and prefix else PALE)
            sheet.blit(li, (pr.x + 14 + (0 if k == 0 else 14), ty))
            ty += 22
        ty += 4

fr_rect = pygame.Rect(pad, y_foot, sheet_w - 2 * pad, foot_h)
pygame.draw.rect(sheet, (22, 18, 30), fr_rect, border_radius=10)
pygame.draw.rect(sheet, (60, 50, 40), fr_rect, 1, border_radius=10)
foot_lines = [
    "Under the hood:  persistent lifetime / best / death-context stats in "
    "store_data (record_run at each death) · Gerald nemesis + derivations · "
    "all-procedural art (no PNGs) · both build targets · 80 unit tests.",
    "Remaining polish:  tap-to-open curio overlays (currently toast feedback) · "
    "Junk Drawer / Scroll of Wisdom viewers · crystal-ball accuracy self-grading.",
]
fy = fr_rect.y + 16
for ln in foot_lines:
    li = f_foot.render(ln, True, CREAM)
    sheet.blit(li, (fr_rect.x + 16, fy))
    fy += 26

out = "/home/user/skybit/docs/profile/profile_summary.png"
pygame.image.save(sheet, out)
print("wrote", out, sheet.get_size())
