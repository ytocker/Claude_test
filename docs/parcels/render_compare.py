"""Combined 14-up PARCEL comparison — every designed parcel carried by Pip in the
same real gameplay frame (day + night), grouped by price tier with labels.

Surfaces the whole tab at a glance so the tiers read as a ladder. Run with:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python docs/parcels/render_compare.py
"""
import os, sys, pathlib

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "showcase"))

import pygame
import render_showcase as RS
from game.config import W, H, BIRD_X, PARCEL_Y_OFFSET
from game import store_catalog

# (parcel_id, tier label) in tab order; the two secrets show their real look here.
TIERS = [
    ("parcel_envelope",  "LOW"),
    ("parcel_sack",      "LOW"),
    ("parcel_takeout",   "LOW"),
    ("parcel_jar",       "LOW"),
    ("parcel_picnic",    "LOW"),
    ("parcel_steamer",   "MID"),
    ("parcel_bottle",    "MID"),
    ("parcel_balloon",   "MID"),
    ("parcel_chest",     "HIGH"),
    ("parcel_lantern",   "HIGH"),
    ("parcel_flask",     "HIGH"),
    ("parcel_ufo",       "PREMIUM"),
    ("parcel_comet",     "PREMIUM"),
    ("parcel_snowglobe", "PREMIUM"),
]

TIER_COLOR = {
    "LOW":     (150, 200, 150),
    "MID":     (150, 190, 240),
    "HIGH":    (235, 195, 120),
    "PREMIUM": (220, 150, 235),
}

# A tight crop around Pip + the carried parcel, scaled up so the 22px gift reads.
CROP = 150
SCALE = 1.6
CW, CH = int(CROP * SCALE), int(CROP * SCALE)


def _crop(full):
    cx, cy = int(BIRD_X), int(H * 0.42 + PARCEL_Y_OFFSET // 2)
    x0 = max(0, min(W - CROP, cx - CROP // 2))
    y0 = max(0, min(H - CROP, cy - CROP // 2))
    sub = full.subsurface(pygame.Rect(x0, y0, CROP, CROP)).copy()
    return pygame.transform.smoothscale(sub, (CW, CH))


def _frame(world, base, pid):
    world.bird.equipped_skin = store_catalog.BASE_SKIN
    world.bird.equipped_parcel = pid
    full = base.copy()
    world.bird.draw(full, 0, 0)
    return _crop(full)


def main():
    pygame.init()
    RS.SCENE_PHASE = 0.0
    day_w, day_b = RS.build_scene()
    RS.SCENE_PHASE = 0.52
    night_w, night_b = RS.build_scene()

    cols, rows = 7, 2          # 14 parcels across two rows of seven
    pad, lab = 10, 26
    title_h = 46
    cell_w = CW
    cell_h = CH * 2 + lab * 2 + 6   # day frame, night frame, two label strips
    sheet_w = pad + cols * (cell_w + pad)
    sheet_h = title_h + pad + rows * (cell_h + pad)
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((20, 22, 28))

    big = pygame.font.SysFont("Arial", 26, bold=True)
    small = pygame.font.SysFont("Arial", 15, bold=True)
    tiny = pygame.font.SysFont("Arial", 12, bold=True)
    sheet.blit(big.render("SKYBIT — PARCELS (14 looks, carried in-frame: DAY / NIGHT)",
                          True, (245, 245, 250)), (pad, 10))

    for i, (pid, tier) in enumerate(TIERS):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = title_h + pad + r * (cell_h + pad)
        name = store_catalog.name(pid)
        cost = store_catalog.cost(pid)
        tc = TIER_COLOR[tier]
        # name + tier/cost label
        sheet.blit(small.render(name, True, (235, 238, 245)), (x + 2, y))
        sheet.blit(tiny.render(f"{tier} · {cost}", True, tc), (x + 2, y + lab - 8))
        ytop = y + lab + 4
        sheet.blit(_frame(day_w, day_b, pid), (x, ytop))
        sheet.blit(_frame(night_w, night_b, pid), (x, ytop + CH + 2))
        # tier accent bar
        pygame.draw.rect(sheet, tc, pygame.Rect(x, ytop - 3, cell_w, 2))

    out = HERE / "gameplay_compare.png"
    pygame.image.save(sheet, str(out))
    print("wrote", out)


if __name__ == "__main__":
    main()
