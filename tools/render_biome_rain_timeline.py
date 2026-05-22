"""One-shot tool — render a chart of rain intensity over the
biome cycle, with thresholds and event markers annotated. Output:
    docs/screenshots/biome_rain_timeline.png

Run from repo root:
    SDL_VIDEODRIVER=dummy python -m tools.render_biome_rain_timeline
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from game.weather import rain_intensity
from game import biome


CYCLE = biome.CYCLE_SECONDS   # 320.0 s

# Canvas
W, H = 1600, 760
LEFT, RIGHT = 90, W - 60        # plot area horizontal bounds
TOP, BOTTOM = 110, H - 110     # plot area vertical bounds
PLOT_W = RIGHT - LEFT
PLOT_H = BOTTOM - TOP

# Colours
BG          = ( 22,  24,  32)
PANEL       = ( 30,  34,  44)
GRID        = ( 52,  58,  72)
GRID_HI     = ( 70,  78,  96)
AXIS        = (170, 178, 200)
LABEL       = (230, 235, 245)
TITLE       = (255, 255, 255)
SUBTLE      = (140, 150, 175)

# Curve + threshold colours
RAIN_LINE   = (130, 195, 240)
RAIN_FILL   = ( 50, 110, 190)
SHAKE_LINE  = (255, 200,  90)
SHAKE_FILL  = (255, 200,  90)
BOLT_LINE   = (255,  90,  90)
BOLT_FILL   = (255, 100, 110)
EVENT_DOT   = (255, 240, 200)


def x_at(t):
    return LEFT + int((t / CYCLE) * PLOT_W)


def y_at(rain):
    return BOTTOM - int(rain * PLOT_H)


def time_label(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m}:{s:02d}"


def main():
    surf = pygame.Surface((W, H))
    surf.fill(BG)

    font_title = pygame.font.SysFont("Arial", 28, bold=True)
    font_sub   = pygame.font.SysFont("Arial", 16)
    font_axis  = pygame.font.SysFont("Arial", 14)
    font_event = pygame.font.SysFont("Arial", 14, bold=True)
    font_event_sub = pygame.font.SysFont("Arial", 12)

    # ── title ───────────────────────────────────────────────────
    title = font_title.render(
        "Biome cycle — rain intensity, coin-shake window, lightning window",
        True, TITLE)
    surf.blit(title, (LEFT, 30))
    sub = font_sub.render(
        "Full cycle = 320 s = 5:20  ·  rain = sunset drizzle bump + "
        "dusk storm bump + night residual bump",
        True, SUBTLE)
    surf.blit(sub, (LEFT, 64))

    # ── plot panel ──────────────────────────────────────────────
    pygame.draw.rect(surf, PANEL, (LEFT, TOP, PLOT_W, PLOT_H))

    # ── compute sampled rain curve ──────────────────────────────
    n_samples = 1024
    rain_pts = []
    for i in range(n_samples + 1):
        t = (i / n_samples) * CYCLE
        phase = (t / CYCLE) % 1.0
        rain_pts.append((t, rain_intensity(phase)))

    # ── shade coin-shake region (rain > 0.20) ───────────────────
    shake_band = []
    for t, r in rain_pts:
        if r > 0.20:
            shake_band.append((x_at(t), y_at(r)))
    if shake_band:
        # Build filled polygon: top edge along curve, bottom edge
        # along the 0.20 threshold line
        first_t = next(t for t, r in rain_pts if r > 0.20)
        last_t  = next(t for t, r in reversed(rain_pts) if r > 0.20)
        poly = [(x_at(first_t), y_at(0.20))]
        for t, r in rain_pts:
            if r > 0.20:
                poly.append((x_at(t), y_at(r)))
        poly.append((x_at(last_t), y_at(0.20)))
        # Use a semi-transparent overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(overlay, (*SHAKE_FILL, 50), poly)
        surf.blit(overlay, (0, 0))

    # ── shade lightning region (rain > 0.85) ────────────────────
    bolt_band = [(t, r) for t, r in rain_pts if r > 0.85]
    if bolt_band:
        first_t = bolt_band[0][0]
        last_t  = bolt_band[-1][0]
        poly = [(x_at(first_t), y_at(0.85))]
        for t, r in bolt_band:
            poly.append((x_at(t), y_at(r)))
        poly.append((x_at(last_t), y_at(0.85)))
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.polygon(overlay, (*BOLT_FILL, 90), poly)
        surf.blit(overlay, (0, 0))

    # ── grid: horizontal (rain levels) ──────────────────────────
    for level in (0.0, 0.20, 0.40, 0.60, 0.80, 0.85, 1.00):
        y = y_at(level)
        col = GRID_HI if level in (0.20, 0.85) else GRID
        # Dashed line for thresholds
        if level == 0.20 or level == 0.85:
            for x in range(LEFT, RIGHT, 12):
                pygame.draw.line(surf, col, (x, y), (x + 6, y), 2)
        else:
            pygame.draw.line(surf, col, (LEFT, y), (RIGHT, y), 1)
        lab = font_axis.render(f"{level:.2f}", True, AXIS)
        surf.blit(lab, (LEFT - lab.get_width() - 8,
                        y - lab.get_height() // 2))

    # Annotate threshold labels at the right edge
    for level, name, col in ((0.20, "coin-shake threshold (0.20)",
                              SHAKE_LINE),
                              (0.85, "lightning trigger (0.85)",
                               BOLT_LINE)):
        y = y_at(level)
        text = font_event_sub.render(name, True, col)
        surf.blit(text, (RIGHT - text.get_width() - 6,
                          y - text.get_height() - 2))

    # ── grid: vertical (time markers every 30 s) ────────────────
    for sec in range(0, int(CYCLE) + 1, 30):
        x = x_at(sec)
        pygame.draw.line(surf, GRID, (x, TOP), (x, BOTTOM), 1)
        lab = font_axis.render(time_label(sec), True, AXIS)
        surf.blit(lab, (x - lab.get_width() // 2, BOTTOM + 6))

    # Axis labels
    yax = font_sub.render("rain intensity", True, LABEL)
    yax_rot = pygame.transform.rotate(yax, 90)
    surf.blit(yax_rot, (LEFT - 70, TOP + (PLOT_H - yax_rot.get_height()) // 2))
    xax = font_sub.render("time within cycle (m:ss)", True, LABEL)
    surf.blit(xax, (LEFT + (PLOT_W - xax.get_width()) // 2,
                     BOTTOM + 36))

    # ── plot the rain curve (filled below + crisp line) ─────────
    curve_pts = [(x_at(t), y_at(r)) for t, r in rain_pts]
    fill_pts = [(x_at(0), y_at(0))] + curve_pts + [(x_at(CYCLE), y_at(0))]
    fill_overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.polygon(fill_overlay, (*RAIN_FILL, 110), fill_pts)
    surf.blit(fill_overlay, (0, 0))
    pygame.draw.lines(surf, RAIN_LINE, False, curve_pts, 3)

    # ── event markers ───────────────────────────────────────────
    events = [
        # (time_s, label, sub_label, anchor) anchor: 'above'/'below'
        (  0.0, "0:00", "DAY noon — dry", "above"),
        ( 73.6, "1:14", "rain begins", "below"),
        ( 89.6, "1:30", "coins start shaking", "above"),
        (112.0, "1:52", "sunset rain peak  (~0.55)", "below"),
        (147.2, "2:27", "test-mode start  (phase 0.46)", "above"),
        (153.6, "2:34", "lightning trigger opens", "below"),
        (160.0, "2:40", "PEAK STORM  (rain = 1.0)", "above"),
        (166.4, "2:47", "lightning trigger closes", "below"),
        (198.4, "3:18", "night-residual rain peak", "above"),
        (214.4, "3:34", "coins stop shaking", "below"),
        (230.4, "3:50", "rain ends — quiet night", "above"),
    ]

    for t_s, t_lab, descr, anchor in events:
        phase = (t_s / CYCLE) % 1.0
        rain = rain_intensity(phase)
        x = x_at(t_s)
        y = y_at(rain)

        # Vertical guide line
        pygame.draw.line(surf, GRID_HI, (x, TOP), (x, BOTTOM), 1)
        # Event dot
        pygame.draw.circle(surf, (40, 30, 20), (x, y), 7)
        pygame.draw.circle(surf, EVENT_DOT, (x, y), 5)
        pygame.draw.circle(surf, (255, 255, 255), (x - 1, y - 1), 2)

        # Label — alternate above/below to avoid overlap
        time_text = font_event.render(t_lab, True, TITLE)
        descr_text = font_event_sub.render(descr, True, LABEL)
        tw = max(time_text.get_width(), descr_text.get_width()) + 12
        th = time_text.get_height() + descr_text.get_height() + 8
        if anchor == "above":
            box_y = y - th - 14
            line_y2 = y - 8
        else:
            box_y = y + 18
            line_y2 = y + 8
        # Clamp to plot bounds
        box_y = max(TOP + 4, min(BOTTOM - th - 4, box_y))
        box_x = x - tw // 2
        box_x = max(LEFT + 4, min(RIGHT - tw - 4, box_x))
        # Connector line from dot to label box
        if anchor == "above":
            pygame.draw.line(surf, GRID_HI,
                             (x, line_y2), (x, box_y + th),
                             1)
        else:
            pygame.draw.line(surf, GRID_HI,
                             (x, line_y2), (x, box_y),
                             1)
        # Label background
        bg_rect = pygame.Rect(box_x - 4, box_y - 2,
                              tw + 8, th + 4)
        bg = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        surf.blit(bg, bg_rect.topleft)
        pygame.draw.rect(surf, GRID_HI, bg_rect, 1)
        # Time label
        surf.blit(time_text,
                  (box_x + (tw - time_text.get_width()) // 2,
                   box_y))
        # Description
        surf.blit(descr_text,
                  (box_x + (tw - descr_text.get_width()) // 2,
                   box_y + time_text.get_height() + 4))

    # ── legend (bottom-right corner of plot) ────────────────────
    legend_items = [
        (RAIN_LINE,  "rain intensity"),
        (SHAKE_FILL, "coin-shake window"),
        (BOLT_FILL,  "lightning-strike window"),
    ]
    lg_x = RIGHT - 230
    lg_y = TOP + 14
    for col, text in legend_items:
        pygame.draw.rect(surf, col, (lg_x, lg_y + 4, 20, 4))
        lt = font_event_sub.render(text, True, LABEL)
        surf.blit(lt, (lg_x + 28, lg_y))
        lg_y += 22

    # Save
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "biome_rain_timeline.png")
    pygame.image.save(surf, out_path)
    print(f"saved {out_path}  ({W}x{H})")


if __name__ == "__main__":
    main()
