"""Thunderstorm DRAMA concept preview (no game code touched).

Renders the real gameplay scene at four moments of the dusk thunderstorm, for a
"current" reference row plus three escalating dramatic concepts, into one
comparison grid:

    python tools/sketch_thunderstorm.py
    -> docs/screenshots/thunderstorm/concepts.png

Columns = moments (captioned with the second INTO the event; event opens at
biome_time 140). Rows = current / concept A / B / C. Throwaway design sketch:
the dramatic effects (heavier raindrops, extra white flashes, storm
tint+vignette, bolder/forked bolt, splashes, foreground rain) are drawn here as
preview overlays so the look can be judged before porting into the game.
"""
import os
import sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import math
import random
import pygame

pygame.init()
pygame.display.set_mode((360, 640))

from game.config import W, H, GROUND_Y
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground
from game.world import World
from game.entities import Coin
from game.scenes import _draw_lightning_bolt
import game.weather as weather

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                   "docs", "screenshots", "thunderstorm")
os.makedirs(OUT, exist_ok=True)
EVENT_START = 140.0               # biome_time the run opens on (storm begins)


# ── base scene (same composition as tools/render_storm_jolt) ─────────────────
def render_base(world, surf):
    phase = world.biome_phase
    pal = _biome.palette_for_phase(phase)
    bucket = int((phase % 1.0) * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    for bx, by, sc, v in ((20, 90, 0.9, 0), (220, 130, 1.0, 2), (90, 200, 0.8, 3)):
        draw_cloud(surf, bx, by, sc, variant=v)
    draw_mountains(surf, world.bg_scroll, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, world.bg_scroll,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    for p in world.pipes:
        p.draw(surf)
    for c in world.coins:
        c.draw(surf)
    for p in world.particles:
        p.draw(surf)
    world.bird.draw(surf, flipped=False)
    for t in world.float_texts:
        t.draw(surf)
    world.weather.draw(surf)
    _draw_lightning_bolt(surf, world.lightning_strike)


def build_world(biome_time, strike=False):
    random.seed(int(biome_time) * 7 + 1)
    w = World()
    w.ready_t = 0
    w.biome_time = biome_time
    for _ in range(40):                       # populate rain streaks
        w.weather.update(1 / 60, w.biome_phase)
    w.score = 250
    w.coin_count = 60
    for k in range(4):
        w.coins.append(Coin(210 + k * 38, 250 + (k % 2) * 26))
    w._spawn_pipe(W + 50)
    w.bird.y = H * 0.42
    if strike:
        w._fire_storm_jolt()
        for _ in range(5):                    # let the bolt reach mid-life
            for p in w.particles:
                p.update(1 / 60)
            for t in w.float_texts:
                t.update(1 / 60)
            if w.lightning_strike:
                w.lightning_strike["life"] -= 1 / 60
        w.weather.flash_remaining = 0.0       # preview controls the flash itself
    return w


# ── dramatic preview overlays ────────────────────────────────────────────────
def heavy_rain(surf, intensity, seed):
    rng = random.Random(seed)
    n = int(150 + intensity * 230)
    col = (150, 178, 224)
    for _ in range(n):
        x = rng.uniform(-10, W + 10)
        y = rng.uniform(-10, H)
        ln = rng.uniform(13, 22) * (0.7 + intensity * 0.5)
        dx = -ln * 0.42                       # wind slant
        x2, y2 = x + dx, y - ln
        pygame.draw.line(surf, col, (int(x), int(y)), (int(x2), int(y2)), 2)
        pygame.draw.circle(surf, (200, 218, 250), (int(x), int(y)), 1)  # teardrop head


def foreground_rain(surf, intensity, seed):
    rng = random.Random(seed + 99)
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    for _ in range(int(22 + intensity * 26)):
        x = rng.uniform(-20, W + 20); y = rng.uniform(-40, H)
        ln = rng.uniform(40, 90); dx = -ln * 0.45
        pygame.draw.line(layer, (200, 215, 245, 70),
                         (int(x), int(y)), (int(x + dx), int(y - ln)), 3)
    surf.blit(layer, (0, 0))


def splashes(surf, seed):
    rng = random.Random(seed + 5)
    for _ in range(26):
        x = rng.uniform(0, W); y = GROUND_Y + rng.uniform(-4, 10)
        pygame.draw.arc(surf, (210, 225, 250),
                        (int(x - 4), int(y - 3), 8, 6), 3.5, 6.0, 1)


def flash(surf, strength):
    f = pygame.Surface((W, H), pygame.SRCALPHA)
    f.fill((222, 230, 255, int(strength)))
    surf.blit(f, (0, 0))


_VIG = None
def vignette(surf, edge=150):
    global _VIG
    if _VIG is None:
        small = pygame.Surface((90, 160), pygame.SRCALPHA)
        cx, cy = 45, 80
        maxd = math.hypot(cx, cy)
        for yy in range(160):
            for xx in range(90):
                d = math.hypot(xx - cx, yy - cy) / maxd
                a = int(edge * (d ** 2.2))
                small.set_at((xx, yy), (8, 12, 26, a))
        _VIG = pygame.transform.smoothscale(small, (W, H))
    surf.blit(_VIG, (0, 0))


def storm_tint(surf, amt=70):
    t = pygame.Surface((W, H), pygame.SRCALPHA)
    t.fill((26, 34, 58, int(amt)))
    surf.blit(t, (0, 0))


def bolder_bolt(surf, forked=False):
    rng = random.Random(33)
    bx = int(W * 0.5)
    pts = [(bx + rng.randint(-50, 50), 0)]
    segs = 16
    for i in range(1, segs):
        t = i / segs
        pts.append((int(pts[0][0] * (1 - t) + bx * t + rng.uniform(-26, 26) * (1 - t)),
                    int((GROUND_Y - 120) * t)))
    pts.append((bx, GROUND_Y - 120))
    for col, a, wdt in (((150, 110, 240), 80, 16), ((180, 120, 255), 170, 10),
                        ((150, 225, 255), 235, 6), ((255, 255, 255), 255, 3)):
        lay = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.lines(lay, (*col, a), False, pts, wdt)
        if forked:                            # a couple of branches
            for bi in (5, 9):
                bp = pts[bi]
                ep = (bp[0] + rng.randint(-60, 60), bp[1] + rng.randint(30, 70))
                pygame.draw.line(lay, (*col, a), bp, ep, max(1, wdt - 3))
        surf.blit(lay, (0, 0))


# ── grid ─────────────────────────────────────────────────────────────────────
# (biome_time, strike?, base_flash, label)
MOMENTS = [
    (140.0, False, 0.0,  "t~0s  storm builds"),
    (160.0, False, 0.0,  "t~20s  peak rain"),
    (160.0, True,  0.0,  "t~20s  LIGHTNING -100"),
    (180.0, False, 0.18, "t~40s  thunder-flash"),
]
ROWS = ["Current", "A: heavier rain + flashes",
        "B: + darken/vignette + bolder bolt", "C: full drama"]


def compose(row, mi):
    bt, strike, base_flash, _ = MOMENTS[mi]
    w = build_world(bt, strike=strike)
    if base_flash > 0:
        w.weather.flash_remaining = base_flash
    surf = pygame.Surface((W, H))
    inten = weather.rain_intensity(w.biome_phase)
    seed = row * 100 + mi
    render_base(w, surf)
    if row == 0:                               # current reference
        if strike or base_flash > 0:
            flash(surf, 150)                   # the current full-screen flash
        return surf
    heavy_rain(surf, inten, seed)              # A+: much heavier raindrops
    if row >= 2:                               # B+: moody storm grade
        storm_tint(surf, 58)
        vignette(surf, 128)
    if row >= 3:                               # C: foreground rain + splashes
        foreground_rain(surf, inten, seed)
        splashes(surf, seed)
    # Flash kept partial so the dramatic scene reads (in game it's a full pulse);
    # bolt drawn ON TOP so it stays the brightest element.
    if strike:
        flash(surf, 120 + row * 12)
        if row >= 2:
            bolder_bolt(surf, forked=(row >= 3))
    elif base_flash > 0:
        flash(surf, 115 + row * 12)
    return surf


def main():
    cw, ch = int(W * 0.62), int(H * 0.62)
    gap, lblw, hdr = 6, 150, 26
    cols, rows = len(MOMENTS), len(ROWS)
    sheet = pygame.Surface((lblw + cols * cw + gap * (cols + 1),
                            hdr + rows * ch + gap * (rows + 1)))
    sheet.fill((16, 18, 26))
    fhdr = pygame.font.SysFont("Arial", 14, bold=True)
    flbl = pygame.font.SysFont("Arial", 13, bold=True)
    for mi, (_, _, _, label) in enumerate(MOMENTS):
        t = fhdr.render(label, True, (235, 238, 248))
        sheet.blit(t, (lblw + gap + mi * (cw + gap), 6))
    for r in range(rows):
        ry = hdr + gap + r * (ch + gap)
        lt = flbl.render(ROWS[r], True, (235, 238, 248))
        sheet.blit(lt, (6, ry + ch // 2 - 8))
        for mi in range(cols):
            cell = pygame.transform.smoothscale(compose(r, mi), (cw, ch))
            sheet.blit(cell, (lblw + gap + mi * (cw + gap), ry))
    path = os.path.join(OUT, "concepts.png")
    pygame.image.save(sheet, path)
    print("wrote", path, sheet.get_size())


if __name__ == "__main__":
    main()
