"""Render 5 MEGA MAGNET icon candidates (Twin-Coil family) next to the
live regular Magnet.

Iteration 2 — based on V3 from round 1. Direction:
  * Twin-coil silhouette (copper windings on each leg)
  * Overall footprint matched to the regular powerup
  * Body arms thicker than the regular magnet
  * No wire connector across the top of the arch

Each variant is one treatment of the leg coils.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_mega_magnet_icon_candidates.py
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

_OUT = os.path.join(_REPO, "docs", "mega_magnet_icons")
os.makedirs(_OUT, exist_ok=True)

pygame.init()
pygame.font.init()

from game.entities import PowerUp  # noqa: E402


# ── shared primitives ───────────────────────────────────────────────────────


SKY_BG = (25, 60, 130)


def draw_regular_magnet(surf, cx, cy, pulse):
    """Live game renderer for the regular Magnet icon."""
    p = PowerUp(cx, cy, "magnet")
    p.pulse = pulse
    p.draw(surf)


def _chrome_pole(surf, tip_cx, leg_bot, arm_w):
    pygame.draw.rect(surf, (40, 42, 60),
                     (tip_cx - arm_w // 2 - 1, leg_bot - 4, arm_w + 2, 9),
                     border_radius=4)
    pygame.draw.rect(surf, (195, 210, 232),
                     (tip_cx - arm_w // 2, leg_bot - 3, arm_w, 7),
                     border_radius=3)
    pygame.draw.rect(surf, (238, 246, 255),
                     (tip_cx - arm_w // 2 + 1, leg_bot - 3, arm_w - 2, 3),
                     border_radius=2)


def _horseshoe_body(surf, cx, arch_cy, leg_bot, outer_r, inner_r,
                    body_col=(235, 35, 45), shadow_col=(80, 5, 8),
                    hi_col=(255, 95, 95)):
    """Same construction as game/entities.py:_draw_magnet but parametric."""
    sz = (outer_r + 4) * 2 + max(0, leg_bot - arch_cy)
    scratch = pygame.Surface((sz, sz), pygame.SRCALPHA)
    scx = sz // 2
    scy = outer_r + 4
    pygame.draw.circle(scratch, shadow_col, (scx, scy), outer_r + 2)
    pygame.draw.rect(scratch, shadow_col,
                     (scx - outer_r - 2, scy,
                      (outer_r + 2) * 2, leg_bot - arch_cy + 4))
    pygame.draw.circle(scratch, body_col, (scx, scy), outer_r + 1)
    pygame.draw.rect(scratch, body_col,
                     (scx - outer_r - 1, scy,
                      (outer_r + 1) * 2, leg_bot - arch_cy + 3))
    pygame.draw.circle(scratch, hi_col, (scx, scy), inner_r + 1, 2)
    pygame.draw.circle(scratch, hi_col, (scx, scy), outer_r, 2)
    pygame.draw.circle(scratch, (0, 0, 0, 0), (scx, scy), inner_r)
    pygame.draw.rect(scratch, (0, 0, 0, 0),
                     (scx - inner_r, scy, inner_r * 2, sz - scy))
    surf.blit(scratch, (cx - scx, arch_cy - scy))


def _lightning_arc(surf, left_cx, right_cx, arc_y0, pulse, segs=6):
    pts = [(left_cx, arc_y0)]
    for i in range(1, segs):
        t = i / segs
        x = int(left_cx + (right_cx - left_cx) * t)
        y = int(arc_y0 + math.sin(pulse * 11 + i * 1.7) * 4)
        pts.append((x, y))
    pts.append((right_cx, arc_y0))
    pygame.draw.lines(surf, (100, 195, 255), False, pts, 2)


# ── shared base geometry ────────────────────────────────────────────────────
# Same footprint as the regular Magnet (outer_r=13) so the icon visually
# sits in the same size class as every other powerup. Inner radius is
# smaller (3 vs 6) — that's the "thicker" the user asked for.

BASE_OUTER_R = 13
BASE_INNER_R = 3


def _base_geom(cy, pulse):
    cy_bob = cy + int(math.sin(pulse * 1.1) * 3)
    arch_cy = cy_bob - 3
    leg_bot = cy_bob + 13
    return cy_bob, arch_cy, leg_bot


def _common_finish(surf, cx, leg_bot, pulse,
                   outer_r=BASE_OUTER_R, inner_r=BASE_INNER_R):
    """Pole tips + lightning arc — identical across the 5 coil variants."""
    arm_w = outer_r - inner_r
    left_cx = cx - inner_r - arm_w // 2
    right_cx = cx + inner_r + arm_w // 2
    _chrome_pole(surf, left_cx, leg_bot, arm_w)
    _chrome_pole(surf, right_cx, leg_bot, arm_w)
    _lightning_arc(surf, left_cx, right_cx, leg_bot + 6, pulse)


# ── V1. Classic Copper — tight horizontal copper bands ─────────────────────


def draw_v1_copper_tight(surf, cx, cy, pulse):
    cy_bob, arch_cy, leg_bot = _base_geom(cy, pulse)
    _horseshoe_body(surf, cx, arch_cy, leg_bot, BASE_OUTER_R, BASE_INNER_R)
    arm_w = BASE_OUTER_R - BASE_INNER_R
    left_outer = cx - BASE_OUTER_R
    right_inner = cx + BASE_INNER_R
    band_h = 2
    gap = 1
    leg_top = arch_cy + 2
    for i in range(8):
        by = leg_top + i * (band_h + gap)
        if by + band_h > leg_bot - 1:
            break
        for x0 in (left_outer, right_inner):
            pygame.draw.rect(surf, (95, 50, 18), (x0, by, arm_w, band_h))
            pygame.draw.rect(surf, (215, 135, 55),
                             (x0, by, arm_w, max(1, band_h - 1)))
            pygame.draw.line(surf, (255, 205, 120),
                             (x0 + 1, by),
                             (x0 + arm_w - 2, by), 1)
    _common_finish(surf, cx, leg_bot, pulse)


# ── V2. Chunky 3-band — 3 thick copper bands per leg with rivet dots ────────


def draw_v2_copper_chunky(surf, cx, cy, pulse):
    cy_bob, arch_cy, leg_bot = _base_geom(cy, pulse)
    _horseshoe_body(surf, cx, arch_cy, leg_bot, BASE_OUTER_R, BASE_INNER_R)
    arm_w = BASE_OUTER_R - BASE_INNER_R
    left_outer = cx - BASE_OUTER_R
    right_inner = cx + BASE_INNER_R
    leg_top = arch_cy + 2
    leg_span = (leg_bot - 1) - leg_top
    band_n = 3
    band_h = 3
    gap = (leg_span - band_n * band_h) // (band_n + 1)
    for i in range(band_n):
        by = leg_top + gap + i * (band_h + gap)
        for x0 in (left_outer, right_inner):
            pygame.draw.rect(surf, (75, 35, 12), (x0, by, arm_w, band_h))
            pygame.draw.rect(surf, (220, 140, 60),
                             (x0, by, arm_w, band_h - 1))
            pygame.draw.line(surf, (255, 215, 130),
                             (x0 + 1, by),
                             (x0 + arm_w - 2, by), 1)
            # Rivet dot centered in the band
            rx = x0 + arm_w // 2
            ry = by + band_h // 2
            pygame.draw.circle(surf, (60, 30, 10), (rx, ry), 1)
    _common_finish(surf, cx, leg_bot, pulse)


# ── V3. Gold Bands — brighter palette (electroplated gold windings) ─────────


def draw_v3_gold(surf, cx, cy, pulse):
    cy_bob, arch_cy, leg_bot = _base_geom(cy, pulse)
    _horseshoe_body(surf, cx, arch_cy, leg_bot, BASE_OUTER_R, BASE_INNER_R)
    arm_w = BASE_OUTER_R - BASE_INNER_R
    left_outer = cx - BASE_OUTER_R
    right_inner = cx + BASE_INNER_R
    band_h = 2
    gap = 1
    leg_top = arch_cy + 2
    for i in range(8):
        by = leg_top + i * (band_h + gap)
        if by + band_h > leg_bot - 1:
            break
        for x0 in (left_outer, right_inner):
            pygame.draw.rect(surf, (130, 90, 0), (x0, by, arm_w, band_h))
            pygame.draw.rect(surf, (255, 200, 30),
                             (x0, by, arm_w, max(1, band_h - 1)))
            pygame.draw.line(surf, (255, 240, 140),
                             (x0 + 1, by),
                             (x0 + arm_w - 2, by), 1)
    _common_finish(surf, cx, leg_bot, pulse)


# ── V4. Spiral Wind — visible wire spiralling around each leg ───────────────


def draw_v4_spiral(surf, cx, cy, pulse):
    cy_bob, arch_cy, leg_bot = _base_geom(cy, pulse)
    _horseshoe_body(surf, cx, arch_cy, leg_bot, BASE_OUTER_R, BASE_INNER_R)
    arm_w = BASE_OUTER_R - BASE_INNER_R
    left_outer = cx - BASE_OUTER_R
    right_inner = cx + BASE_INNER_R
    leg_top = arch_cy + 2
    leg_bottom = leg_bot - 1
    # Render the coil as a stack of shallow ellipses — each "wrap" of the
    # wire is one ellipse showing the leg cross-section. Front of the
    # ellipse is bright (visible side of the wire), back is dark.
    wraps = 5
    for w in range(wraps):
        t = w / max(1, wraps - 1)
        wy = int(leg_top + t * (leg_bottom - leg_top - 2))
        for x0 in (left_outer, right_inner):
            # Dark back-side of the wrap (top half of the ellipse)
            pygame.draw.ellipse(surf, (70, 35, 12),
                                pygame.Rect(x0 - 1, wy - 1, arm_w + 2, 4))
            # Bright front of the wrap (bottom half) — only draw the lower
            # arc so the back stays slightly darker than the front.
            front = pygame.Surface((arm_w + 2, 5), pygame.SRCALPHA)
            pygame.draw.ellipse(front, (225, 145, 60),
                                pygame.Rect(0, -2, arm_w + 2, 5))
            surf.blit(front, (x0 - 1, wy))
            # Highlight curve along the bottom-front of the wrap
            pygame.draw.arc(surf, (255, 215, 140),
                            pygame.Rect(x0, wy, arm_w, 4),
                            math.pi, 2 * math.pi, 1)
    _common_finish(surf, cx, leg_bot, pulse)


# ── V5. Energized — copper bands + amber glow + spark dots ──────────────────


def draw_v5_energized(surf, cx, cy, pulse):
    cy_bob, arch_cy, leg_bot = _base_geom(cy, pulse)
    # Faint amber glow behind the legs only (not the arch) — signals
    # "current is flowing through the windings".
    glow = pygame.Surface((50, 30), pygame.SRCALPHA)
    a_peak = 50 + int(20 * (0.5 + 0.5 * math.sin(pulse * 4)))
    for rr in range(14, 4, -1):
        falloff = (14 - rr) / 10
        a = int(a_peak * (1 - falloff) ** 1.4)
        if a > 0:
            pygame.draw.ellipse(glow, (255, 180, 60, a),
                                pygame.Rect(25 - rr, 15 - rr // 2,
                                            rr * 2, rr))
    surf.blit(glow, (cx - 25, leg_bot - 8),
              special_flags=pygame.BLEND_RGBA_ADD)
    _horseshoe_body(surf, cx, arch_cy, leg_bot, BASE_OUTER_R, BASE_INNER_R)
    arm_w = BASE_OUTER_R - BASE_INNER_R
    left_outer = cx - BASE_OUTER_R
    right_inner = cx + BASE_INNER_R
    band_h = 2
    gap = 1
    leg_top = arch_cy + 2
    bands = []
    for i in range(8):
        by = leg_top + i * (band_h + gap)
        if by + band_h > leg_bot - 1:
            break
        for x0 in (left_outer, right_inner):
            pygame.draw.rect(surf, (95, 50, 18), (x0, by, arm_w, band_h))
            pygame.draw.rect(surf, (215, 135, 55),
                             (x0, by, arm_w, max(1, band_h - 1)))
            pygame.draw.line(surf, (255, 215, 130),
                             (x0 + 1, by),
                             (x0 + arm_w - 2, by), 1)
            bands.append((x0, by))
    # Pulsing spark dots — appear on one band per leg, cycling on pulse
    if bands:
        per_leg = len(bands) // 2
        if per_leg > 0:
            idx = int(pulse * 3) % per_leg
            for leg_i in range(2):
                bx, by = bands[leg_i * per_leg + idx]
                sx = bx + arm_w // 2
                sy = by + band_h // 2
                pygame.draw.circle(surf, (255, 250, 200), (sx, sy), 2)
                pygame.draw.circle(surf, (255, 220, 60), (sx, sy), 1)
    _common_finish(surf, cx, leg_bot, pulse)


# ── compositing ─────────────────────────────────────────────────────────────


VARIANTS = (
    ("v1_copper_tight",  "MEGA — Copper Tight",  draw_v1_copper_tight),
    ("v2_copper_chunky", "MEGA — Copper Chunky", draw_v2_copper_chunky),
    ("v3_gold",          "MEGA — Gold Bands",    draw_v3_gold),
    ("v4_spiral",        "MEGA — Spiral Wind",   draw_v4_spiral),
    ("v5_energized",     "MEGA — Energized",     draw_v5_energized),
)


CELL_W = 180
CELL_H = 170
BAND_H = 50
FRAME_W = CELL_W * 2
FRAME_H = CELL_H + BAND_H


def _cell_bg(cell):
    top = (40, 90, 160)
    bot = (18, 45, 105)
    for y in range(CELL_H):
        t = y / max(1, CELL_H - 1)
        c = (int(top[0] + (bot[0] - top[0]) * t),
             int(top[1] + (bot[1] - top[1]) * t),
             int(top[2] + (bot[2] - top[2]) * t))
        pygame.draw.line(cell, c, (0, y), (CELL_W, y))


def _label(surf, x, y, w, h, line1, line2=None):
    band = pygame.Surface((w, h), pygame.SRCALPHA)
    band.fill((0, 0, 0, 200))
    pygame.draw.line(band, (255, 215, 0), (0, 0), (w, 0), 1)
    f1 = pygame.font.SysFont(None, 22)
    t1 = f1.render(line1, True, (255, 240, 200))
    band.blit(t1, t1.get_rect(midtop=(w // 2, 6)))
    if line2:
        f2 = pygame.font.SysFont(None, 16)
        t2 = f2.render(line2, True, (180, 200, 220))
        band.blit(t2, t2.get_rect(midtop=(w // 2, 28)))
    surf.blit(band, (x, y))


def render_comparison(title, draw_mega):
    frame = pygame.Surface((FRAME_W, FRAME_H))
    for ci, drawer in enumerate((
            lambda s, cx, cy: draw_regular_magnet(s, cx, cy, pulse=1.2),
            lambda s, cx, cy: draw_mega(s, cx, cy, pulse=1.2))):
        cell = pygame.Surface((CELL_W, CELL_H))
        _cell_bg(cell)
        drawer(cell, CELL_W // 2, CELL_H // 2 - 8)
        frame.blit(cell, (ci * CELL_W, 0))
    pygame.draw.line(frame, (10, 20, 40), (CELL_W, 0), (CELL_W, CELL_H), 2)
    _label(frame, 0, CELL_H, CELL_W, BAND_H,
           "REGULAR", "current magnet (game/entities.py)")
    _label(frame, CELL_W, CELL_H, CELL_W, BAND_H, title)
    return frame


def render_contact_sheet():
    sheet = pygame.Surface((FRAME_W, FRAME_H * len(VARIANTS) + 2 * (len(VARIANTS) - 1)))
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
