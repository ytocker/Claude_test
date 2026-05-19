"""SKATEBOARD pickup activation FX — the chosen V4.3 design ported to
live code.

Composition (rendered ONCE per pickup, then blit with decreasing alpha
over the activation duration):

  • 14-spike yellow starburst at the pickup position, with an inner
    red ring, both outlined in ink.
  • 4 corner ink speed-slashes radiating toward the pickup position.
  • Tilted "SKATEBOARD!" caption on a red plate at the top of the
    screen (yellow→orange gradient, ink outline, plate tilted +5°).
  • Tilted "POW!" badge in the upper-right (red gradient, +15°).

Original mockup: docs/screenshots/skateboard_variants/final/chosen.png
and tools/render_skateboard_final.py.
"""

import math
import random

import pygame

from game.config import W, H
from game.hud import _font


INK = (15, 15, 15)
YELLOW = (255, 220, 30)
RED = (230, 60, 50)
PLATE_RED = (220, 50, 40)
WHITE = (255, 255, 255)


def _gradient_text(text, size, top_col, bot_col, outline, outline_w=3):
    """Vertical-gradient text fill with thick outline (ported from
    tools/render_skateboard_variants.py)."""
    font = _font(size)
    mask = font.render(text, True, WHITE)
    bw, bh = mask.get_size()
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = tuple(int(top_col[i] + (bot_col[i] - top_col[i]) * t)
                  for i in range(3))
        pygame.draw.line(grad, c, (0, y), (bw, y))
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    out = font.render(text, True, outline)
    pad = outline_w + 2
    surf = pygame.Surface((bw + pad * 2, bh + pad * 2), pygame.SRCALPHA)
    for dx in range(-outline_w, outline_w + 1):
        for dy in range(-outline_w, outline_w + 1):
            if dx * dx + dy * dy <= outline_w * outline_w and (dx or dy):
                surf.blit(out, (pad + dx, pad + dy))
    surf.blit(grad, (pad, pad))
    return surf


def render_activation_overlay(cx: int, cy: int,
                              rng_seed: int = 22) -> pygame.Surface:
    """Build the full activation overlay anchored at (cx, cy) in screen
    coords. Returns a transparent (W × H) surface — caller blits with
    a decreasing alpha to fade out. Pure function, deterministic given
    the same seed."""
    rng = random.Random(rng_seed)
    surf = pygame.Surface((W, H), pygame.SRCALPHA)

    # ── 14-spike starburst behind Pip (yellow outer, red inner). ────────
    spikes = 14
    inner_r = 70
    pts = []
    for i in range(spikes * 2):
        ang = i * math.pi / spikes - math.pi / 2
        r = (140 + rng.randint(-20, 25)) if i % 2 == 0 else inner_r
        pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
    pygame.draw.polygon(surf, YELLOW, pts)
    pygame.draw.polygon(surf, INK, pts, 5)
    inner_pts = [(cx + (p[0] - cx) * 0.65, cy + (p[1] - cy) * 0.65)
                 for p in pts]
    pygame.draw.polygon(surf, RED, inner_pts)
    pygame.draw.polygon(surf, INK, inner_pts, 3)

    # ── 4-corner ink speed-slashes pointing at the starburst. ───────────
    for x0, y0 in ((20, 20), (W - 20, 20),
                   (20, H - 80), (W - 20, H - 80)):
        for off in range(3):
            dx = (cx - x0) * 0.18
            dy = (cy - y0) * 0.18
            ox = (-1 if x0 < cx else 1) * (off * 8)
            oy = off * 4
            pygame.draw.line(surf, INK,
                             (x0 + ox, y0 + oy),
                             (x0 + ox + dx, y0 + oy + dy), 4)

    # ── SKATEBOARD! caption on a red plate, tilted +5°. ─────────────────
    txt = _gradient_text("SKATEBOARD!", 42,
                         top_col=(255, 255, 110),
                         bot_col=(255, 180, 10),
                         outline=INK, outline_w=5)
    bw, bh = txt.get_width() + 30, txt.get_height() + 18
    composite = pygame.Surface((bw + 12, bh + 12), pygame.SRCALPHA)
    ccx = composite.get_width() // 2
    ccy = composite.get_height() // 2
    plate_rect = pygame.Rect(0, 0, bw, bh)
    plate_rect.center = (ccx + 4, ccy + 4)
    pygame.draw.rect(composite, PLATE_RED, plate_rect, border_radius=10)
    pygame.draw.rect(composite, INK, plate_rect, 4, border_radius=10)
    composite.blit(txt, txt.get_rect(center=(ccx, ccy)).topleft)
    rotated = pygame.transform.rotate(composite, 5)
    surf.blit(rotated, rotated.get_rect(center=(W // 2, 75)))

    # ── POW! badge upper-right, tilted +15°. ────────────────────────────
    pow_txt = _gradient_text("POW!", 32,
                             top_col=(255, 90, 90),
                             bot_col=(220, 30, 30),
                             outline=INK, outline_w=4)
    pow_rot = pygame.transform.rotate(pow_txt, 15)
    surf.blit(pow_rot, pow_rot.get_rect(center=(W - 60, 130)))

    return surf
