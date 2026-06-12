"""Look-dev mockup for the "Pagoda Warren" concept.

Neighbouring pagoda-pillars are pushed close together so their vertical
gaps fuse into a single continuous winding corridor. This script renders a
candidate sheet — 5 corridor archetypes (rows) x 3 times of day (columns) —
and overlays the REAL parrot sprite plus a dotted feasible flight path so a
reviewer can SEE the corridor is threadable.

The single goal is to prove PASSABILITY: every corridor is generated from a
small set of gap centres, and the asserts below reject any layout that the
real bird physics couldn't fly. No game/ files are touched and no game state
is mutated — we only call the existing draw entry points.

    PYTHONPATH=. python tools/render_warren_mockup.py
"""
import math
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.config import (
    W, H, GROUND_Y, PIPE_W, GAP_START, BIRD_R, PIPE_HITBOX_SHRINK,
    FLAP_V, GRAVITY, SCROLL_BASE,
)
from game.biome import palette_for_phase, lerp_color
from game.pillar_pagodas import draw_pillar_pair
from game.parrot import get_parrot


# ── physics-derived passability budget ───────────────────────────────────────
# One flap rises FLAP_V**2 / (2*GRAVITY) px before gravity wins. That is the
# hard ceiling on how much altitude the bird can buy per tap, and it anchors
# every "is this slope flyable" check below.
FLAP_RISE = (FLAP_V * FLAP_V) / (2.0 * GRAVITY)          # ~84 px
EFFECTIVE_R = BIRD_R - PIPE_HITBOX_SHRINK                # forgiven hitbox = 10 px

GAP_H_MIN, GAP_H_MAX = 150, 185        # per-pagoda gap height window
DRIFT_MAX = 70                         # per-pagoda gap-centre vertical step
SPACING_MIN, SPACING_MAX = 90, 140     # centre-to-centre, tighter than PIPE_SPACING

# Keep the threaded corridor off the sky ceiling and off the ground band so
# the parrot always has real estate above and below the path.
CEIL_PAD = 70
FLOOR_PAD = 70
GAP_CY_MIN = CEIL_PAD + GAP_H_MAX // 2
GAP_CY_MAX = GROUND_Y - FLOOR_PAD - GAP_H_MAX // 2


# ── corridor archetypes ──────────────────────────────────────────────────────
# Each returns a list of pagodas: (x_centre, gap_cy, gap_h, seed). x_centre is
# the pillar centre; the union of [gap_cy-gap_h/2, gap_cy+gap_h/2] forms the
# winding passage. Seeds pick the pagoda variant (seed % 11) so each row owns a
# coherent architectural family.

def _gentle_sine_tube(x0):
    """Smooth S-curve, generous gaps — the welcoming intro warren."""
    out, x = [], x0
    base = 300
    for i in range(6):
        cy = base + math.sin(i * 0.85) * 60       # 60 px sweep < DRIFT_MAX
        out.append((x, cy, 182, 0))               # stupa_canopy family, big gaps
        x += 132
    return out


def _terraced_staircase(x0):
    """Stepped landings: gap descends then climbs in fair 58 px treads."""
    out, x = [], x0
    treads = [250, 308, 366, 366, 308, 250]       # plateau in the middle
    for i, cy in enumerate(treads):
        out.append((x, cy, 172, 3))               # horyuji family
        x += 120
    return out


def _chevron_zigzag(x0):
    """Alternating diagonal — steeper, pushed toward the drift ceiling but
    still inside it. Spacing held wide-ish so each leg stays flyable."""
    out, x = [], x0
    lo, hi = 268, 336                             # 68 px alternation < 70
    for i in range(6):
        cy = lo if i % 2 == 0 else hi
        out.append((x, cy, 158, 5))               # toji family, tighter gaps
        x += 134                                  # widest spacing for the steep legs
    return out


def _braided_offset(x0):
    """Alternating high/low pagodas interleave into a woven tube; the gap
    centre wanders gently while the silhouettes overlap heavily."""
    out, x = [], x0
    base = 312
    for i in range(7):
        cy = base + math.sin(i * 1.15) * 46 + (12 if i % 2 else -12)
        out.append((x, cy, 168, 8))               # baoen family
        x += 108                                  # tightest braid spacing
    return out


def _straight_undulating(x0):
    """Tight near-uniform corridor with a slight wander — the classic
    'thread the needle' tunnel."""
    out, x = [], x0
    base = 318
    for i in range(7):
        cy = base + math.sin(i * 1.6) * 22        # shallow 22 px wander
        out.append((x, cy, 156, 10))              # palsangjeon family, snug gaps
        x += 100
    return out


DESIGNS = [
    ("Gentle Sine Tube", _gentle_sine_tube),
    ("Terraced Staircase", _terraced_staircase),
    ("Chevron Zig-Zag", _chevron_zigzag),
    ("Braided Offset", _braided_offset),
    ("Straight Undulating Tunnel", _straight_undulating),
]

TIMES = [("DAY", 0.05), ("SUNSET", 0.36), ("NIGHT", 0.64)]


# ── passability proof ────────────────────────────────────────────────────────

def assert_passable(name, pagodas):
    """Reject any corridor the real bird physics couldn't fly. Asserts mirror
    the brief's budget exactly so the rendered sheet is provably fair."""
    prev = None
    for i, (x, cy, gap_h, _seed) in enumerate(pagodas):
        assert GAP_H_MIN <= gap_h <= GAP_H_MAX, \
            f"{name}: gap_h {gap_h} outside [{GAP_H_MIN},{GAP_H_MAX}]"
        assert GAP_CY_MIN <= cy <= GAP_CY_MAX, \
            f"{name}: gap centre {cy} too close to ceiling/ground"
        if prev is not None:
            px, pcy, pgap_h, _ = prev
            spacing = x - px
            assert SPACING_MIN <= spacing <= SPACING_MAX, \
                f"{name}: spacing {spacing} outside warren window"
            drift = abs(cy - pcy)
            assert drift <= DRIFT_MAX, \
                f"{name}: drift {drift} > {DRIFT_MAX}"
            # Consecutive gaps must share vertical room so the union is one
            # continuous passage the bird never has to leave.
            top = max(cy - gap_h / 2, pcy - pgap_h / 2)
            bot = min(cy + gap_h / 2, pcy + pgap_h / 2)
            overlap = bot - top
            assert overlap >= 2 * EFFECTIVE_R + 8, \
                f"{name}: gaps {i-1}->{i} overlap {overlap:.0f}px too thin"
            # The centre-line climb between two pillars must be buyable inside
            # the travel time (spacing / SCROLL_BASE). A single flap rises
            # FLAP_RISE; require the demanded rise to stay under what the
            # available taps can deliver with margin.
            travel_s = spacing / SCROLL_BASE
            taps = max(1, math.floor(travel_s / 0.34))   # ~0.34 s per useful tap
            climb_budget = FLAP_RISE * taps
            rise = max(0.0, pcy - cy)                     # upward demand
            assert rise <= climb_budget, \
                f"{name}: needs {rise:.0f}px climb, budget {climb_budget:.0f}px"
        prev = (x, cy, gap_h, _seed)
    return True


# ── rendering ────────────────────────────────────────────────────────────────

def draw_sky_ground(surf, w, h, palette):
    """Self-contained vertical sky gradient + ground band, sized to the wide
    strip cell (the cached helpers assume the 360px canvas width)."""
    top = palette['sky_top']
    mid = palette['sky_mid']
    bot = palette['sky_bot']
    for y in range(GROUND_Y):
        t = y / GROUND_Y
        if t < 0.5:
            c = lerp_color(top, mid, t * 2)
        else:
            c = lerp_color(mid, bot, (t - 0.5) * 2)
        pygame.draw.line(surf, c, (0, y), (w, y))
    # Ground band.
    for y in range(GROUND_Y, h):
        t = (y - GROUND_Y) / max(1, h - GROUND_Y)
        c = lerp_color(palette['ground_top'], palette['ground_mid'], t)
        pygame.draw.line(surf, c, (0, y), (w, y))
    # Soft horizon seam so the ground reads as grounded, not pasted.
    pygame.draw.line(surf, palette['ground_top'], (0, GROUND_Y), (w, GROUND_Y))


def draw_corridor_fill(surf, pagodas, color):
    """Faint highlight of the threadable passage — the union of the gaps —
    so the eye reads the winding tube before the dotted path even lands."""
    band = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    pts_top, pts_bot = [], []
    for (x, cy, gap_h, _s) in pagodas:
        pts_top.append((x, cy - gap_h / 2 + EFFECTIVE_R))
        pts_bot.append((x, cy + gap_h / 2 - EFFECTIVE_R))
    poly = pts_top + pts_bot[::-1]
    if len(poly) >= 3:
        pygame.draw.polygon(band, color, poly)
    surf.blit(band, (0, 0))


def draw_flight_path(surf, pagodas):
    """Dotted centre-line through the gap centres — the feasible thread.
    A light spline-ish sampling keeps the dots smooth between pillars."""
    xs = [p[0] for p in pagodas]
    cys = [p[1] for p in pagodas]
    samples = []
    steps = 14
    for i in range(len(pagodas) - 1):
        for s in range(steps):
            t = s / steps
            tt = t * t * (3 - 2 * t)               # smoothstep between centres
            x = xs[i] + (xs[i + 1] - xs[i]) * t
            y = cys[i] + (cys[i + 1] - cys[i]) * tt
            samples.append((x, y))
    samples.append((xs[-1], cys[-1]))
    for i, (x, y) in enumerate(samples):
        if i % 2 == 0:
            pygame.draw.circle(surf, (255, 255, 255), (int(x), int(y)), 3)
            pygame.draw.circle(surf, (40, 200, 120), (int(x), int(y)), 2)


def render_cell(cell_w, cell_h, design_fn, phase):
    """One gameplay strip: sky/ground + close-packed pagodas + passage
    highlight + dotted path + the real parrot threading a gap."""
    palette = palette_for_phase(phase)
    surf = pygame.Surface((cell_w, cell_h))
    draw_sky_ground(surf, cell_w, cell_h, palette)

    # First pagoda offset in from the left so the warren reads as on-screen.
    pagodas = design_fn(70)
    assert_passable(design_fn.__name__, pagodas)

    draw_corridor_fill(surf, pagodas, (255, 244, 180, 46))

    for idx, (x, cy, gap_h, seed) in enumerate(pagodas):
        top_h = cy - gap_h / 2
        bot_y = cy + gap_h / 2
        top_rect = pygame.Rect(int(x - PIPE_W / 2), 0, PIPE_W, int(top_h))
        bot_rect = pygame.Rect(int(x - PIPE_W / 2), int(bot_y),
                               PIPE_W, int(GROUND_Y - bot_y))
        draw_pillar_pair(surf, top_rect, bot_rect, palette, seed,
                         phase=phase, is_rush=False, pillar_index=idx + 1)

    draw_flight_path(surf, pagodas)

    # Parrot threading a mid-corridor gap, tilted slightly into the descent so
    # it reads as actively flying the line.
    px_idx = len(pagodas) // 2
    bx = (pagodas[px_idx][0] + pagodas[px_idx + 1][0]) / 2 \
        if px_idx + 1 < len(pagodas) else pagodas[px_idx][0]
    # interpolate path y at bx
    a, b = pagodas[px_idx], pagodas[px_idx + 1] if px_idx + 1 < len(pagodas) else pagodas[px_idx]
    t = (bx - a[0]) / (b[0] - a[0]) if b[0] != a[0] else 0.0
    tt = t * t * (3 - 2 * t)
    by = a[1] + (b[1] - a[1]) * tt
    tilt = -12 if by > a[1] else 14
    bird = get_parrot(1, tilt)
    surf.blit(bird, (int(bx - bird.get_width() / 2),
                     int(by - bird.get_height() / 2)))
    return surf


def main():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((W, H))   # video context for convert/blit paths

    CELL_W, CELL_H = 960, 640
    SCALE = 0.42                      # shrink wide strips into a tidy grid
    sw, sh = int(CELL_W * SCALE), int(CELL_H * SCALE)

    cols = len(TIMES)
    rows = len(DESIGNS)
    PAD = 22
    GAP = 12
    ROW_LBL = 150     # left gutter for design names
    COL_LBL = 26
    TITLE_H = 46

    canvas_w = ROW_LBL + cols * sw + (cols - 1) * GAP + PAD * 2
    canvas_h = TITLE_H + COL_LBL + rows * sh + (rows - 1) * GAP + PAD * 2
    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((22, 24, 32))

    f_title = pygame.font.SysFont(None, 36, bold=True)
    f_col = pygame.font.SysFont(None, 24, bold=True)
    f_row = pygame.font.SysFont(None, 22, bold=True)

    title = f_title.render("PAGODA WARREN — passability look-dev", True,
                           (240, 240, 245))
    canvas.blit(title, (PAD, PAD - 4))

    x0 = PAD + ROW_LBL
    y0 = PAD + TITLE_H + COL_LBL

    for c, (tname, _phase) in enumerate(TIMES):
        cx = x0 + c * (sw + GAP)
        lbl = f_col.render(tname, True, (210, 215, 225))
        canvas.blit(lbl, (cx + (sw - lbl.get_width()) // 2,
                          y0 - COL_LBL + 2))

    for r, (dname, design_fn) in enumerate(DESIGNS):
        ry = y0 + r * (sh + GAP)
        # design name in the left gutter, vertically centred on the row
        for li, line in enumerate(_wrap(dname, 14)):
            lbl = f_row.render(line, True, (235, 225, 160))
            canvas.blit(lbl, (PAD, ry + sh // 2 - 12 + li * 18))
        for c, (tname, phase) in enumerate(TIMES):
            cell = render_cell(CELL_W, CELL_H, design_fn, phase)
            scaled = pygame.transform.smoothscale(cell, (sw, sh))
            cx = x0 + c * (sw + GAP)
            pygame.draw.rect(canvas, (70, 78, 100),
                             pygame.Rect(cx - 1, ry - 1, sw + 2, sh + 2), 1)
            canvas.blit(scaled, (cx, ry))

    out_dir = os.path.join("docs", "pagoda_warren")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "round_1.png")
    pygame.image.save(canvas, out_path)
    print(f"saved {out_path}  ({canvas_w}x{canvas_h})")
    print("all passability asserts passed")


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    main()
