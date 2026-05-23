"""SANDSTORM stage mockup (design tuning, tooling-only). REBUILT to
reuse the high-quality haboob rendering from render_wind_themes
(warm haze cast + a dust WALL of smooth supersampled soft-disc
puffs with value contrast + a sunlit rim), scaled by intensity to
show the stages: distant horizon storm (tease) -> encroaching ->
peak haboob -> fade. Plus dust-devils, a sample pillar pair (to
judge the visibility veil), and the bird's spread sand coat.

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
# Reuse the haboob's smooth supersample helpers
from tools.render_wind_themes import soft_disc, new_ss, blit_ss, SS

pygame.init()
pygame.display.set_mode((W, H))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "sandstorm")
os.makedirs(OUT_DIR, exist_ok=True)

# Haboob palette (same families as theme_haboob)
HI   = ((250, 210, 150), (255, 225, 170))          # sunlit rim
BODY = ((150, 100, 58), (130, 86, 48), (168, 116, 70))
DEEP = ((96, 62, 36), (80, 52, 30))
HAZE = (198, 148, 82)
SAND = (200, 165, 108)


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


# ── pieces (smooth, supersampled) ────────────────────────────────────────────

def dust_wall(surf, s, rng):
    """The haboob dust wall — smooth soft-disc puffs rising from the
    ground. Height + density scale with s: a low distant band on
    the horizon at the tease, a tall looming wall at the peak."""
    if s <= 0.02:
        return
    ss = new_ss()
    gy0 = GROUND_Y * SS
    top_frac = 0.95 - 0.55 * s            # 0.95 (low) -> 0.40 (tall)

    def wall_top(xf):
        base = gy0 * (top_frac - xf * 0.10 * s)         # taller right at peak
        lump = (math.sin(xf * 9) * 0.045
                + math.sin(xf * 23 + 1.7) * 0.028) * gy0 * (0.4 + s)
        return base + lump

    cols = int(55 + s * 55)
    for ci in range(cols):
        xf = ci / (cols - 1)
        gx = xf * W * SS
        top = wall_top(xf)
        for _ in range(int(4 + s * 9)):
            yy = rng.uniform(top - 8 * SS, gy0)
            depth = (yy - top) / max(1.0, gy0 - top)
            r = int(rng.uniform(18, 34) * SS)
            col = rng.choice(DEEP) if rng.random() < depth * 0.85 else rng.choice(BODY)
            ss.blit(soft_disc(r, col, rng.randint(95, 150)),
                    (gx - r + rng.uniform(-14, 14) * SS, yy - r))
        if rng.random() < 0.5:
            rr = int(rng.uniform(10, 20) * SS)
            ss.blit(soft_disc(rr, rng.choice(HI), rng.randint(60, 110)),
                    (gx - rr, top - rr * 0.5))

    # lofted grit above the wall (scales with s)
    for _ in range(int(s * 170)):
        xf = rng.random() ** 0.5
        gx = xf * W * SS
        gy = rng.uniform(wall_top(xf) - 130 * SS, wall_top(xf))
        if gy < 0:
            continue
        r = rng.randint(3, 8) * SS
        ss.blit(soft_disc(r, rng.choice(BODY), rng.randint(50, 110)),
                (gx - r, gy - r))
    blit_ss(surf, ss)


def dust_devils(surf, s, rng):
    """A couple of slim spinning sand columns on the horizon
    (tease accents), built from smooth soft discs."""
    if s <= 0.03:
        return
    ss = new_ss()
    gy0 = (GROUND_Y - 18) * SS
    for k, dx in enumerate((0.32, 0.70)):
        cx = W * SS * dx
        h = (90 + s * 130) * SS
        steps = int(h / (5 * SS))
        for i in range(steps):
            t = i / steps                     # 0 base -> 1 top
            wob = math.sin(t * 7.0 + k * 2.0) * 10 * SS * (1 - t)
            r = int((3 + (1 - t) * 9) * SS * (0.6 + s * 0.6))
            a = int((45 + s * 110) * (0.35 + 0.65 * (1 - t)))
            col = rng.choice(BODY)
            ss.blit(soft_disc(r, col, a),
                    (cx + wob - r, gy0 - t * h - r))
    blit_ss(surf, ss)


def warm_haze(surf, s):
    """Orange/sepia cast + the VISIBILITY veil. Gated to the
    encroaching stage (s>0.3) so the tease keeps a clear playfield.
    Right side heavier (leading edge)."""
    if s < 0.30:
        return
    t = (s - 0.30) / 0.70
    haze = pygame.Surface((W, H), pygame.SRCALPHA)
    for xx in range(0, W, 2):
        fx = xx / W
        a = int(t * (70 + fx * 80))           # up to ~150 right edge at peak
        pygame.draw.rect(haze, (*HAZE, a), (xx, 0, 2, H))
    surf.blit(haze, (0, 0))


def sand_particles(surf, s, rng):
    """Foreground drifting sand motes (smooth)."""
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
    """Spread tan sand coat over Pip's whole body (smooth discs)."""
    if s < 0.35:
        return
    t = (s - 0.35) / 0.65
    cx, cy = BIRD_X * SS, int(H * 0.42) * SS
    ss = new_ss()
    for _ in range(int(10 + t * 55)):
        rx = rng.uniform(-22, 30) * SS
        ry = rng.uniform(-20, 18) * SS
        if rx > 12 * SS and -16 * SS < ry < 2 * SS and rng.random() < 0.7:
            continue                          # keep the eyes mostly clear
        r = rng.randint(1, 3) * SS
        ss.blit(soft_disc(r, SAND, int(80 + t * 120)), (cx + rx - r, cy + ry - r))
    blit_ss(surf, ss)


def scene(phase, rng):
    s = sand_intensity(phase)
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    bucket = int((phase % 1.0) * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    dust_devils(surf, s, rng)                 # on the horizon
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    draw_pillars(surf)                        # the course
    warm_haze(surf, s)                        # cast + visibility veil (over course)
    dust_wall(surf, s, rng)                   # looming wall (buries lower scene)
    sand_particles(surf, s, rng)
    b = Bird()
    b.x = BIRD_X
    b.y = int(H * 0.42)
    b.vy = 0
    b.draw(surf)                              # Pip crisp on top
    draw_bird_sand(surf, s, rng)
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
