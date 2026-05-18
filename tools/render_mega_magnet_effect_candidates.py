"""Render 5 MEGA MAGNET active-field candidates next to the live regular
Magnet aura.

The regular Magnet's active visual is the warm gold force-field around
the bird (`game/scenes.py:1032-1085`): 3 nested rings + an inner radial
glow, all breathing on a single pulse. The user wants the Mega
Magnet's active field to be the same look, but much larger.

Each variant is one way of "scaling up" — pure scale, denser rings,
thicker rings, outer shell. All 5 use the same Solar Gold palette so
the relationship to the regular magnet stays obvious.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_effect_candidates.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

_OUT = os.path.join(_REPO, "docs", "mega_magnet_effects")
os.makedirs(_OUT, exist_ok=True)

pygame.init()
pygame.font.init()

from game.config import MAGNET_RADIUS  # noqa: E402  — 82


# ── shared field renderer — matches game/scenes.py verbatim ────────────────
# Parametric so each Mega variant is one call with different inputs.


# Default 3-ring layout from scenes.py:1067-1070
DEFAULT_RINGS = (
    # (rfac, phase, alpha, width, breath_scale, ring_col)
    (1.00, 0.0,  180, 3, 1.00, (255, 220, 100)),
    (0.78, 0.6,  140, 2, 0.85, (255, 195,  60)),
    (0.55, 1.2,  100, 2, 0.70, (235, 165,  35)),
)


def draw_field(surf, cx, cy, t_pulse_phase,
               rad=MAGNET_RADIUS,
               rings=DEFAULT_RINGS,
               glow_alpha_peak=72,
               width_mul=1):
    """One call replicates the regular field; rad / rings / width_mul
    let each Mega variant scale up.

    Parameters mirror the live renderer (scenes.py:1032-1085) — the
    only additions are `rings` (override the ring stack) and
    `width_mul` (multiply each ring's stroke width)."""
    t_pulse = t_pulse_phase * 5.5
    field = pygame.Surface((int(rad * 2 + 8), int(rad * 2 + 8)),
                           pygame.SRCALPHA)
    lcx, lcy = int(rad + 4), int(rad + 4)

    BREATH = 0.30
    s_outer = math.sin(t_pulse + 0.0)
    u_outer = (s_outer + 1) / 2
    outer_factor = 1.0 - BREATH * (1.0 - u_outer)
    glow_rad = rad * outer_factor

    # Inner radial glow — bell-curve falloff peaking near outer edge.
    GLOW_COL = (245, 175, 40)
    for i in range(18, 0, -1):
        r = int(glow_rad * i / 18)
        inner_t = i / 18
        bell = math.exp(-((inner_t - 0.85) ** 2) / 0.15)
        a = int(glow_alpha_peak * bell)
        if a > 0:
            pygame.draw.circle(field, (*GLOW_COL, a), (lcx, lcy), r)

    # Rings.
    AA_COL = (255, 240, 180)
    for rfac, phase, alpha, width, breath_scale, ring_col in rings:
        amp = BREATH * breath_scale
        s = math.sin(t_pulse + phase)
        u = (s + 1) / 2
        rr = int(rad * rfac * (1.0 - amp * (1.0 - u)))
        w = max(1, int(width * width_mul))
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr + 1, w)
        pygame.draw.circle(field, (*AA_COL, alpha // 3),
                           (lcx, lcy), rr - 1, w)
        pygame.draw.circle(field, (*ring_col, alpha),
                           (lcx, lcy), rr, w)

    surf.blit(field, (cx - lcx, cy - lcy))


# ── regular reference ───────────────────────────────────────────────────────


def draw_regular(surf, cx, cy, pulse_phase):
    draw_field(surf, cx, cy, pulse_phase)


# ── 5 mega variants ─────────────────────────────────────────────────────────


def draw_v1_scale_17(surf, cx, cy, pulse_phase):
    """1.7× pure scale — same 3 rings, modest "much larger"."""
    draw_field(surf, cx, cy, pulse_phase, rad=MAGNET_RADIUS * 1.7)


def draw_v2_scale_22(surf, cx, cy, pulse_phase):
    """2.2× pure scale — clearly much larger."""
    draw_field(surf, cx, cy, pulse_phase, rad=MAGNET_RADIUS * 2.2)


def draw_v3_denser_5_rings(surf, cx, cy, pulse_phase):
    """2.0× scale with 5 nested rings (denser fill)."""
    rings = (
        (1.00, 0.0,  170, 3, 1.00, (255, 220, 100)),
        (0.84, 0.4,  150, 2, 0.92, (255, 205,  80)),
        (0.68, 0.8,  130, 2, 0.85, (255, 195,  60)),
        (0.52, 1.2,  110, 2, 0.75, (240, 175,  45)),
        (0.36, 1.6,   90, 2, 0.65, (220, 155,  30)),
    )
    draw_field(surf, cx, cy, pulse_phase,
               rad=MAGNET_RADIUS * 2.0, rings=rings)


def draw_v4_thicker_rings(surf, cx, cy, pulse_phase):
    """2.0× scale, ring strokes ~2× thicker — beefier."""
    draw_field(surf, cx, cy, pulse_phase,
               rad=MAGNET_RADIUS * 2.0, width_mul=2)


def draw_v5_outer_shell(surf, cx, cy, pulse_phase):
    """2.0× scale + a wide outer shell ring at 1.25× the base rad —
    gives the field an extra "halo" beyond the main 3-ring stack."""
    rings = (
        (1.25, -0.4,  90, 2, 0.55, (250, 200, 80)),  # outer shell
        (1.00,  0.0, 180, 3, 1.00, (255, 220, 100)),
        (0.78,  0.6, 140, 2, 0.85, (255, 195,  60)),
        (0.55,  1.2, 100, 2, 0.70, (235, 165,  35)),
    )
    draw_field(surf, cx, cy, pulse_phase,
               rad=MAGNET_RADIUS * 2.0, rings=rings,
               glow_alpha_peak=84)


# ── scene backdrop ──────────────────────────────────────────────────────────
# Light gameplay context so the user can read the field at real scale
# against the actual game's sky/ground colours.


CELL_W = 360
CELL_H = 360
BAND_H = 50
FRAME_W = CELL_W * 2
FRAME_H = CELL_H + BAND_H

BIRD_R = 14
BIRD_RED = (240, 55, 55)
BIRD_BEAK = (255, 185, 0)


def _scene_bg(cell):
    # Vertical sky gradient — same colour family as game/draw.py.
    top = (25, 60, 130)
    mid = (40, 110, 180)
    bot = (60, 160, 210)
    for y in range(CELL_H):
        if y < CELL_H * 0.5:
            t = y / (CELL_H * 0.5)
            c = (int(top[0] + (mid[0] - top[0]) * t),
                 int(top[1] + (mid[1] - top[1]) * t),
                 int(top[2] + (mid[2] - top[2]) * t))
        else:
            t = (y - CELL_H * 0.5) / (CELL_H * 0.5)
            c = (int(mid[0] + (bot[0] - mid[0]) * t),
                 int(mid[1] + (bot[1] - mid[1]) * t),
                 int(mid[2] + (bot[2] - mid[2]) * t))
        pygame.draw.line(cell, c, (0, y), (CELL_W, y))
    # A couple of pillars for spatial reference at real game scale —
    # NOT redrawing the world, just two thin green bars so the field's
    # size is legible against in-game geometry.
    pipe_w = 56
    for px, gap_y, gap_h in ((40, 200, 130), (CELL_W - 90, 220, 130)):
        half = gap_h // 2
        for r in (pygame.Rect(px, 0, pipe_w, gap_y - half),
                  pygame.Rect(px, gap_y + half, pipe_w, CELL_H - (gap_y + half))):
            pygame.draw.rect(cell, (45, 185, 45), r)
            pygame.draw.rect(cell, (20, 100, 20), r, 2)
            pygame.draw.line(cell, (110, 240, 110),
                             (r.x + 6, r.y), (r.x + 6, r.bottom), 3)


def _draw_bird(surf, x, y):
    pygame.draw.circle(surf, BIRD_RED, (x, y), BIRD_R)
    pygame.draw.circle(surf, (170, 25, 25), (x, y), BIRD_R, 2)
    pygame.draw.circle(surf, (255, 170, 50), (x + 1, y + 4), 6)
    pygame.draw.polygon(surf, BIRD_BEAK,
                        [(x + BIRD_R - 2, y - 3),
                         (x + BIRD_R + 8, y),
                         (x + BIRD_R - 2, y + 3)])
    pygame.draw.circle(surf, (255, 255, 255), (x + 4, y - 4), 3)
    pygame.draw.circle(surf, (0, 0, 0), (x + 5, y - 4), 1)


def _label(surf, x, y, w, h, line1, line2=None):
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    band.fill((0, 0, 0, 200))
    pygame.draw.line(band, (255, 215, 0), (0, 0), (w, 0), 1)
    f1 = pygame.font.SysFont(None, 24)
    t1 = f1.render(line1, True, (255, 240, 200))
    band.blit(t1, t1.get_rect(midtop=(w // 2, 6)))
    if line2:
        f2 = pygame.font.SysFont(None, 16)
        t2 = f2.render(line2, True, (180, 200, 220))
        band.blit(t2, t2.get_rect(midtop=(w // 2, 30)))
    surf.blit(band, (x, y))


VARIANTS = (
    ("v1_scale_17",     "MEGA — 1.7× scale",         draw_v1_scale_17),
    ("v2_scale_22",     "MEGA — 2.2× scale",         draw_v2_scale_22),
    ("v3_dense_5rings", "MEGA — 2.0× + 5 rings",     draw_v3_denser_5_rings),
    ("v4_thick_rings",  "MEGA — 2.0× + thick rings", draw_v4_thicker_rings),
    ("v5_outer_shell",  "MEGA — 2.0× + outer shell", draw_v5_outer_shell),
)


def render_comparison(title, draw_mega):
    frame = pygame.Surface((FRAME_W, FRAME_H))
    bird_x, bird_y = CELL_W // 2, CELL_H // 2
    pulse = 0.45  # near the field's "exhale" peak so rings are visible
    for ci, drawer in enumerate((
            lambda s: draw_regular(s, bird_x, bird_y, pulse),
            lambda s: draw_mega(s, bird_x, bird_y, pulse))):
        cell = pygame.Surface((CELL_W, CELL_H))
        _scene_bg(cell)
        drawer(cell)
        _draw_bird(cell, bird_x, bird_y)
        frame.blit(cell, (ci * CELL_W, 0))
    pygame.draw.line(frame, (10, 20, 40), (CELL_W, 0), (CELL_W, CELL_H), 2)
    _label(frame, 0, CELL_H, CELL_W, BAND_H,
           "REGULAR", f"r = {MAGNET_RADIUS:.0f}px (game/scenes.py)")
    _label(frame, CELL_W, CELL_H, CELL_W, BAND_H, title)
    return frame


def render_contact_sheet():
    n = len(VARIANTS)
    sheet = pygame.Surface((FRAME_W, FRAME_H * n + 2 * (n - 1)))
    sheet.fill((5, 10, 20))
    for i, (_slug, title, fn) in enumerate(VARIANTS):
        f = render_comparison(title, fn)
        sheet.blit(f, (0, i * (FRAME_H + 2)))
    return sheet


def main():
    for slug, title, fn in VARIANTS:
        f = render_comparison(title, fn)
        pygame.image.save(f, os.path.join(_OUT, f"{slug}.png"))
    sheet = render_contact_sheet()
    pygame.image.save(sheet, os.path.join(_OUT, "00_contact_sheet.png"))
    print(f"wrote {len(VARIANTS) + 1} images to {_OUT}")


if __name__ == "__main__":
    main()
