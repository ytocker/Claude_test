"""SANDSTORM stage mockup (design tuning, tooling-only). Reuses the
haboob's smooth supersampled soft-disc rendering. Two walls:

* DISTANT wall — a beautiful towering haboob on the horizon BEHIND
  the mountains, with a sunlit billowing top rim. This is the long
  TEASE hero (present from low intensity, high quality).
* FOREGROUND wall — the engulfing leading edge that rises from the
  ground and rolls OVER Pip at the peak (Pip is drawn BEHIND the
  sand, so the haze/wall/motes blow in front of him).

Plus dust-devils, an ochre visibility veil, mountain burying, a
sample pillar pair, and the bird's spread sand coat.

Output: docs/screenshots/wind_themes/sandstorm/stages_sheet.png

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_sandstorm
"""
import os
import math
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import W, H, GROUND_Y, BIRD_X
from game.entities import Bird
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground
from tools.render_wind_themes import soft_disc, new_ss, blit_ss, SS

pygame.init()
pygame.display.set_mode((W, H))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "sandstorm")
os.makedirs(OUT_DIR, exist_ok=True)

HI   = ((250, 210, 150), (255, 225, 170))          # sunlit rim
BODY = ((150, 100, 58), (130, 86, 48), (168, 116, 70))
DEEP = ((96, 62, 36), (80, 52, 30))
HAZE = (198, 148, 82)
SAND = (200, 165, 108)
HORIZON = GROUND_Y - 70


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def sand_intensity(phase):
    if phase < 0.05 or phase > 0.31:
        return 0.0
    if phase <= 0.18:
        return _smooth((phase - 0.05) / (0.18 - 0.05))
    if phase <= 0.20:
        return 1.0
    return _smooth(1.0 - (phase - 0.20) / (0.31 - 0.20))


# ── DISTANT wall (the long-tease hero, behind the mountains) ─────────────────

def distant_wall(surf, s, rng):
    """A towering dust wall on the horizon, sunlit top rim catching
    the warm light — the beautiful distant haboob the player sees
    through the whole tease. Grows taller/closer with s."""
    if s <= 0.02:
        return
    ss = new_ss()
    base_y = (HORIZON + 12) * SS
    height = (0.20 + s * 0.28) * H * SS        # 0.20H (tease) -> 0.48H

    def top_y(xf):
        lump = (math.sin(xf * 7 + 0.5) * 0.11
                + math.sin(xf * 17 + 2.0) * 0.05) * height
        return base_y - height + lump

    cols = int(80 + s * 40)
    for ci in range(cols):
        xf = ci / (cols - 1)
        gx = xf * W * SS
        top = top_y(xf)
        for _ in range(int(5 + s * 5)):
            yy = rng.uniform(top, base_y + 10 * SS)
            d = (yy - top) / max(1.0, base_y - top)      # 0 top -> 1 base
            r = int(rng.uniform(13, 24) * SS)
            if d < 0.30:
                col = rng.choice(HI)
            elif d < 0.72:
                col = rng.choice(BODY)
            else:
                col = rng.choice(DEEP)
            ss.blit(soft_disc(r, col, rng.randint(85, 145)),
                    (gx - r + rng.uniform(-12, 12) * SS, yy - r))
        if rng.random() < 0.6:                 # bright sunlit rim on the crest
            rr = int(rng.uniform(8, 16) * SS)
            ss.blit(soft_disc(rr, rng.choice(HI), rng.randint(90, 150)),
                    (gx - rr, top - rr * 0.4))
    blit_ss(surf, ss)


def dust_devils(surf, s, rng):
    if s <= 0.03:
        return
    ss = new_ss()
    gy0 = (HORIZON + 4) * SS
    for k, dx in enumerate((0.30, 0.72)):
        cx = W * SS * dx
        h = (110 + s * 120) * SS
        steps = int(h / (5 * SS))
        for i in range(steps):
            t = i / steps
            wob = math.sin(t * 7.0 + k * 2.0) * 11 * SS * (1 - t)
            r = int((3 + (1 - t) * 9) * SS * (0.6 + s * 0.5))
            a = int((55 + s * 110) * (0.4 + 0.6 * (1 - t)))
            col = rng.choice(HI if t > 0.8 else BODY)
            ss.blit(soft_disc(r, col, a), (cx + wob - r, gy0 - t * h - r))
    blit_ss(surf, ss)


def mountain_bury(surf, s):
    if s < 0.30:
        return
    t = (s - 0.30) / 0.70
    band = pygame.Surface((W, GROUND_Y - (HORIZON - 24)), pygame.SRCALPHA)
    band.fill((*HAZE, int(150 * t)))
    surf.blit(band, (0, HORIZON - 24))


# ── FOREGROUND engulfing wall (rolls over Pip at the peak) ───────────────────

def foreground_wall(surf, s, rng):
    if s < 0.40:
        return
    fs = (s - 0.40) / 0.60                      # 0 at s=0.4 -> 1 at peak
    ss = new_ss()
    gy0 = GROUND_Y * SS
    top_frac = 0.92 - 0.50 * fs                 # rises from the ground

    def wall_top(xf):
        base = gy0 * (top_frac - xf * 0.10 * fs)
        lump = (math.sin(xf * 9) * 0.045
                + math.sin(xf * 23 + 1.7) * 0.028) * gy0 * (0.4 + fs)
        return base + lump

    cols = int(55 + fs * 50)
    for ci in range(cols):
        xf = ci / (cols - 1)
        gx = xf * W * SS
        top = wall_top(xf)
        for _ in range(int(5 + fs * 8)):
            yy = rng.uniform(top - 8 * SS, gy0)
            d = (yy - top) / max(1.0, gy0 - top)
            r = int(rng.uniform(18, 34) * SS)
            col = rng.choice(DEEP) if rng.random() < d * 0.85 else rng.choice(BODY)
            ss.blit(soft_disc(r, col, rng.randint(95, 150)),
                    (gx - r + rng.uniform(-14, 14) * SS, yy - r))
        if rng.random() < 0.5:
            rr = int(rng.uniform(10, 20) * SS)
            ss.blit(soft_disc(rr, rng.choice(HI), rng.randint(60, 110)),
                    (gx - rr, top - rr * 0.5))
    for _ in range(int(fs * 170)):
        xf = rng.random() ** 0.5
        gx = xf * W * SS
        gy = rng.uniform(wall_top(xf) - 130 * SS, wall_top(xf))
        if gy < 0:
            continue
        r = rng.randint(3, 8) * SS
        ss.blit(soft_disc(r, rng.choice(BODY), rng.randint(50, 110)), (gx - r, gy - r))
    blit_ss(surf, ss)


def warm_haze(surf, s):
    if s < 0.30:
        return
    t = (s - 0.30) / 0.70
    haze = pygame.Surface((W, H), pygame.SRCALPHA)
    for xx in range(0, W, 2):
        fx = xx / W
        a = int(t * (70 + fx * 80))
        pygame.draw.rect(haze, (*HAZE, a), (xx, 0, 2, H))
    surf.blit(haze, (0, 0))


def sand_particles(surf, s, rng):
    if s < 0.22:
        return
    ss = new_ss()
    for _ in range(int(s * 120)):
        x = rng.uniform(0, W) * SS
        y = rng.uniform(0, GROUND_Y) * SS
        r = rng.randint(2, 5) * SS
        ss.blit(soft_disc(r, SAND, rng.randint(70, 150)), (x - r, y - r))
    blit_ss(surf, ss)


def draw_pillars(surf):
    col = (196, 170, 120)
    edge = (150, 124, 80)
    gap_y, gap_h, pw, px = 250, 150, 56, int(W * 0.62)
    for rect in [(px, 0, pw, gap_y),
                 (px, gap_y + gap_h, pw, GROUND_Y - gap_y - gap_h)]:
        pygame.draw.rect(surf, col, rect, border_radius=6)
        pygame.draw.rect(surf, edge, rect, width=2, border_radius=6)


def draw_bird_sand(surf, s, rng):
    if s < 0.35:
        return
    t = (s - 0.35) / 0.65
    cx, cy = BIRD_X * SS, int(H * 0.42) * SS
    ss = new_ss()
    for _ in range(int(10 + t * 55)):
        rx = rng.uniform(-22, 30) * SS
        ry = rng.uniform(-20, 18) * SS
        r = rng.randint(1, 3) * SS
        ss.blit(soft_disc(r, SAND, int(80 + t * 120)), (cx + rx - r, cy + ry - r))
    blit_ss(surf, ss)


def scene(phase, rng):
    s = sand_intensity(phase)
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    bucket = int((phase % 1.0) * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    # distant haboob + devils sit on the horizon, BEHIND the mountains
    distant_wall(surf, s, rng)
    dust_devils(surf, s, rng)
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    mountain_bury(surf, s)
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    draw_pillars(surf)
    # Pip + his sand coat, BEHIND the foreground sand
    b = Bird()
    b.x = BIRD_X
    b.y = int(H * 0.42)
    b.vy = 0
    b.draw(surf)
    draw_bird_sand(surf, s, rng)
    # foreground sand engulfs everything in front of Pip
    warm_haze(surf, s)
    foreground_wall(surf, s, rng)
    sand_particles(surf, s, rng)
    return surf, s


def main():
    frames = [(0.08, "tease"), (0.13, "encroaching"), (0.17, "worsening"),
              (0.19, "PEAK haboob"), (0.27, "fading")]
    panels = []
    for ph, lbl in frames:
        rng = random.Random(int(ph * 1000))
        surf, s = scene(ph, rng)
        panels.append((f"{lbl}  phase {ph:.2f}  s={s:.2f}", surf))

    cols = len(panels)
    margin, label_h = 10, 24
    sheet_w = cols * (W + margin) + margin
    sheet_h = H + label_h + 2 * margin
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((24, 26, 32))
    font = pygame.font.SysFont("Arial", 13, bold=True)
    for i, (lbl, surf) in enumerate(panels):
        x = margin + i * (W + margin)
        pygame.draw.rect(sheet, (70, 64, 50), (x - 2, margin - 2, W + 4, H + 4), 2)
        sheet.blit(surf, (x, margin))
        sheet.blit(font.render(lbl, True, (235, 220, 190)), (x + 4, margin + H + 4))
    out = os.path.join(OUT_DIR, "stages_sheet.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  ({sheet_w}x{sheet_h})")


if __name__ == "__main__":
    main()
