"""SANDSTORM — render from the LIVE wired weather code (so what you
see is the shipped event), plus the event TIMELINE GRAPH.

  stages_sheet.png   5 key frames (tease -> peak -> fade) composed
                     exactly like the game (draw_far behind the
                     mountains, Pip, then draw_front in front).
  timeline_graph.png the sand_intensity curve vs biome phase/seconds
                     with the stage bands + key markers.

Run from repo root:
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
      python -m tools.render_sandstorm
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import (
    W, H, GROUND_Y, BIRD_X,
    WEATHER_SAND_ACCUM_RATE as _A,
    WEATHER_SAND_MELT_BASE as _MB,
    WEATHER_SAND_MELT_FADE as _MF,
)
from game.entities import Bird
from game.weather import Weather, sand_intensity
from game import biome as _biome
from game.draw import get_sky_surface_biome, draw_mountains, draw_ground

pygame.init()
pygame.display.set_mode((W, H))

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                       "docs", "screenshots", "wind_themes", "sandstorm")
os.makedirs(OUT_DIR, exist_ok=True)

CY = _biome.CYCLE_SECONDS
TEST_START = 0.015


def sand_load_at(phase):
    """Simulate the bird's sand_load integrator from the deployed
    test-start to `phase`, so the stage frames show the true coat."""
    load = 0.0
    dt = 1 / 60.0
    t = 0.0
    target = (phase - TEST_START) * CY
    while t < target:
        ph = ((TEST_START * CY + t) / CY) % 1.0
        si = sand_intensity(ph)
        load = max(0.0, min(1.0, load + (_A * si - (_MB + _MF * (1 - si))) * dt))
        t += dt
    return load


def draw_pillars(surf):
    col, edge = (196, 170, 120), (150, 124, 80)
    gap_y, gap_h, pw, px = 250, 150, 56, int(W * 0.62)
    for rect in [(px, 0, pw, gap_y),
                 (px, gap_y + gap_h, pw, GROUND_Y - gap_y - gap_h)]:
        pygame.draw.rect(surf, col, rect, border_radius=6)
        pygame.draw.rect(surf, edge, rect, width=2, border_radius=6)


def scene(phase, weather):
    s = sand_intensity(phase)
    surf = pygame.Surface((W, H))
    pal = _biome.palette_for_phase(phase)
    bucket = int((phase % 1.0) * _biome.PHASE_BUCKETS) % _biome.PHASE_BUCKETS
    surf.blit(get_sky_surface_biome(W, H, GROUND_Y, pal, bucket), (0, 0))
    weather.phase = phase
    for _ in range(50):                       # warm the live mote pool
        weather.update(1 / 60.0, phase)
    weather.draw_far(surf)                    # behind the mountains
    draw_mountains(surf, 0, GROUND_Y, W, pal["mtn_far"], pal["mtn_near"])
    draw_ground(surf, GROUND_Y, W, H, 0,
                pal["ground_top"], pal["ground_mid"], (60, 40, 25))
    draw_pillars(surf)
    b = Bird()
    b.x = BIRD_X
    b.y = int(H * 0.42)
    b.vy = 0
    b.sand_load = sand_load_at(phase)
    b.draw(surf)                              # Pip + his sand coat
    weather.draw_front(surf)                  # engulfing sand in front of Pip
    return surf, s


def render_stage_sheet():
    frames = [(0.07, "tease"), (0.11, "encroaching"), (0.14, "worsening"),
              (0.16, "PEAK haboob"), (0.20, "fading")]
    weather = Weather()
    panels = []
    for ph, lbl in frames:
        surf, s = scene(ph, weather)
        panels.append((f"{lbl}  ph {ph:.2f}  s={s:.2f}", surf))
    margin, label_h = 10, 24
    sheet = pygame.Surface((len(panels) * (W + margin) + margin,
                            H + label_h + 2 * margin))
    sheet.fill((24, 26, 32))
    font = pygame.font.SysFont("Arial", 13, bold=True)
    for i, (lbl, surf) in enumerate(panels):
        x = margin + i * (W + margin)
        pygame.draw.rect(sheet, (70, 64, 50), (x - 2, margin - 2, W + 4, H + 4), 2)
        sheet.blit(surf, (x, margin))
        sheet.blit(font.render(lbl, True, (235, 220, 190)), (x + 4, margin + H + 4))
    out = os.path.join(OUT_DIR, "stages_sheet.png")
    pygame.image.save(sheet, out)
    print(f"saved {out}  {sheet.get_size()}")


def render_timeline():
    GW, GH, m = 940, 460, 78
    g = pygame.Surface((GW, GH))
    g.fill((250, 246, 238))
    x0, y0, x1, y1 = m, GH - m, GW - m, m + 26
    pmax = 0.26

    def px(ph):
        return x0 + (ph / pmax) * (x1 - x0)

    def py(v):
        return y0 - v * (y0 - y1)

    # stage-band shading under the curve
    for xx in range(int(x0), int(x1)):
        ph = (xx - x0) / (x1 - x0) * pmax
        s = sand_intensity(ph)
        if s <= 0:
            continue
        band = ((252, 236, 206) if s < 0.35 else
                (245, 214, 150) if s < 0.65 else (230, 182, 112))
        pygame.draw.line(g, band, (xx, py(s)), (xx, y0))
    # rain region (>=0.23)
    rain = pygame.Surface((int(x1 - px(0.23)), y0 - y1), pygame.SRCALPHA)
    rain.fill((90, 130, 200, 45))
    g.blit(rain, (int(px(0.23)), y1))
    # axes
    pygame.draw.line(g, (40, 40, 40), (x0, y0), (x1, y0), 2)
    pygame.draw.line(g, (40, 40, 40), (x0, y0), (x0, y1), 2)
    # curve
    pts = [(px(i / 400 * pmax), py(sand_intensity(i / 400 * pmax)))
           for i in range(401)]
    pygame.draw.lines(g, (150, 88, 36), False, pts, 3)
    font = pygame.font.SysFont("Arial", 16, bold=True)
    sm = pygame.font.SysFont("Arial", 12, bold=True)
    # vertical markers
    for ph, lbl, col, dy in [
            (TEST_START, "TEST START", (0, 130, 0), 0),
            (0.03, "tease begins", (140, 95, 30), 16),
            (0.15, "peak", (170, 90, 20), 0),
            (0.22, "clears", (140, 95, 30), 16),
            (0.23, "RAIN starts", (40, 80, 185), 0)]:
        pygame.draw.line(g, col, (px(ph), y1 - 6), (px(ph), y0), 1)
        t = sm.render(lbl, True, col)
        g.blit(t, (px(ph) - t.get_width() / 2, y1 - 20 - dy))
    # x ticks (phase + seconds)
    for ph in [0.0, 0.05, 0.10, 0.15, 0.20, 0.25]:
        pygame.draw.line(g, (40, 40, 40), (px(ph), y0), (px(ph), y0 + 5), 1)
        g.blit(sm.render(f"{ph:.2f}", True, (40, 40, 40)), (px(ph) - 12, y0 + 7))
        g.blit(sm.render(f"{int(ph * CY)}s", True, (120, 120, 120)),
               (px(ph) - 10, y0 + 23))
    for v in [0.0, 0.5, 1.0]:
        g.blit(sm.render(f"{v:.1f}", True, (40, 40, 40)), (x0 - 32, py(v) - 7))
    g.blit(font.render("SANDSTORM timeline — sand_intensity vs biome phase",
                       True, (30, 30, 30)), (m, 16))
    g.blit(sm.render("bands: tease  ->  encroaching  ->  peak haboob; "
                     "blue = sunset-rain window (no overlap)",
                     True, (90, 80, 60)), (m, GH - 22))
    out = os.path.join(OUT_DIR, "timeline_graph.png")
    pygame.image.save(g, out)
    print(f"saved {out}  {g.get_size()}")


def main():
    render_stage_sheet()
    render_timeline()


if __name__ == "__main__":
    main()
