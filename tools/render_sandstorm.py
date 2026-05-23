"""SANDSTORM stage mockup (design tuning, tooling-only — not wired
into the game yet). Renders the event's key stages along its
timeline so we can judge the look: a daytime haboob with a long
tease (horizon dust WALL + DUST-DEVILS behind the mountains), an
ochre VISIBILITY veil over the course (pipes shown, Pip stays
crisp), mountains buried, and the bird coated in spread sand.

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
from game.entities import Bird, _snow_disc           # reuse soft disc
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground

pygame.init()
pygame.display.set_mode((W, H))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "sandstorm")
os.makedirs(OUT_DIR, exist_ok=True)

# Ochre/sepia sand palette
WALL = (196, 156, 96)
VEIL = (200, 150, 84)
MOTE = (212, 176, 120)
SAND = (200, 165, 108)
HORIZON = GROUND_Y - 70           # approx mountain-top line


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def sand_intensity(phase):
    """Long slow rise 0.05->0.18, short plateau, quicker fade to
    ~0.31 (before the sunset rain at 0.32)."""
    if phase < 0.05 or phase > 0.31:
        return 0.0
    if phase <= 0.18:
        return _smooth((phase - 0.05) / (0.18 - 0.05))
    if phase <= 0.20:
        return 1.0
    return _smooth(1.0 - (phase - 0.20) / (0.31 - 0.20))


# ── pieces ───────────────────────────────────────────────────────────────────

def draw_far(surf, s, rng):
    """Horizon dust wall + dust-devils (behind the mountains).
    Present even in the tease (low s)."""
    if s <= 0.02:
        return
    # dust wall: ochre gradient band sitting on the horizon, taller
    # + more opaque as s grows
    band_h = int(40 + s * 130)
    top = HORIZON - band_h
    wall = pygame.Surface((W, band_h), pygame.SRCALPHA)
    for yy in range(band_h):
        t = yy / band_h                       # 0 top -> 1 bottom
        a = int((30 + s * 150) * (0.3 + 0.7 * t))
        pygame.draw.line(wall, (*WALL, a), (0, yy), (W, yy))
    surf.blit(wall, (0, top))
    # 2 dust-devils: tapered spinning columns rising off the horizon
    for k, dx in enumerate((0.30, 0.66)):
        cx = W * dx
        h = int(70 + s * 120)
        col = pygame.Surface((60, h), pygame.SRCALPHA)
        for yy in range(h):
            t = yy / h
            wob = math.sin(t * 6.0 + k) * 8 * (1 - t)   # wavy taper
            wid = int((4 + (1 - t) * 16) * (0.5 + s))
            a = int((40 + s * 120) * (0.4 + 0.6 * (1 - t)))
            pygame.draw.line(col, (*WALL, a),
                             (30 + wob - wid, yy), (30 + wob + wid, yy))
        surf.blit(col, (int(cx - 30), HORIZON - h))


def mountain_bury(surf, s):
    """Ochre wash over the mountain band so the peaks get buried as
    the storm advances (mid+ intensity)."""
    if s < 0.25:
        return
    t = (s - 0.25) / 0.75
    a = int(150 * t)
    wash = pygame.Surface((W, GROUND_Y - (HORIZON - 30)), pygame.SRCALPHA)
    wash.fill((*WALL, a))
    surf.blit(wash, (0, HORIZON - 30))


def draw_pillars(surf):
    """A representative sandstone pillar pair (the 'course'), so the
    veil's effect on visibility is judgeable."""
    col = (196, 170, 120)
    edge = (150, 124, 80)
    gap_y, gap_h, pw, px = 250, 150, 56, int(W * 0.62)
    for rect in [(px, 0, pw, gap_y),
                 (px, gap_y + gap_h, pw, GROUND_Y - gap_y - gap_h)]:
        pygame.draw.rect(surf, col, rect, border_radius=6)
        pygame.draw.rect(surf, edge, rect, width=2, border_radius=6)


def playfield_veil(surf, s):
    """Full-screen ochre VISIBILITY veil — the gameplay effect.
    Capped so the course stays discernible (fair)."""
    if s < 0.30:
        return
    t = (s - 0.30) / 0.70
    a = int(105 * t)                          # fair cap ~105 at peak
    veil = pygame.Surface((W, H), pygame.SRCALPHA)
    veil.fill((*VEIL, a))
    surf.blit(veil, (0, 0))


def draw_particles(surf, s, rng):
    """Foreground driven sand: fast streaks + drifting motes."""
    if s < 0.20:
        return
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    n_streak = int(s * 90)
    for _ in range(n_streak):
        x = rng.uniform(0, W)
        y = rng.uniform(0, GROUND_Y)
        ln = rng.uniform(14, 40)
        a = rng.randint(70, 150)
        pygame.draw.line(layer, (*MOTE, a), (x, y), (x + ln, y + rng.uniform(-3, 4)),
                         rng.choice((1, 1, 2)))
    surf.blit(layer, (0, 0))
    n_mote = int(s * 70)
    for _ in range(n_mote):
        x = rng.uniform(0, W)
        y = rng.uniform(0, GROUND_Y)
        r = rng.randint(2, 5)
        surf.blit(_snow_disc(r, MOTE, rng.randint(90, 170)), (x - r, y - r))


def draw_bird_sand(surf, s, rng):
    """Spread tan sand coat over Pip's whole body (vs snow's top
    drift). Bird centre (BIRD_X, H*0.42)."""
    if s < 0.35:
        return
    t = (s - 0.35) / 0.65
    cx, cy = BIRD_X, int(H * 0.42)
    n = int(8 + t * 60)
    a = int(70 + t * 120)
    for i in range(n):
        # spread across the body bbox (rel ~ x[-22,30] y[-20,18]),
        # lighter over the face (right-upper)
        rx = rng.uniform(-22, 30)
        ry = rng.uniform(-20, 18)
        if rx > 12 and -16 < ry < 2 and rng.random() < 0.7:
            continue                          # keep eyes mostly clear
        r = rng.randint(1, 3)
        surf.blit(_snow_disc(r, SAND, a),
                  (cx + rx - r, cy + ry - r))


def scene(phase, rng):
    s = sand_intensity(phase)
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    bucket = int((phase % 1.0) * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    draw_far(surf, s, rng)                    # behind mountains
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    mountain_bury(surf, s)
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    draw_pillars(surf)
    playfield_veil(surf, s)                   # visibility veil over the course
    draw_particles(surf, s, rng)
    b = Bird()
    b.x = BIRD_X
    b.y = int(H * 0.42)
    b.vy = 0
    b.draw(surf)
    draw_bird_sand(surf, s, rng)
    return surf, s


def main():
    frames = [
        (0.08, "tease"),
        (0.13, "encroaching"),
        (0.17, "worsening"),
        (0.19, "PEAK haboob"),
        (0.27, "fading"),
    ]
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
