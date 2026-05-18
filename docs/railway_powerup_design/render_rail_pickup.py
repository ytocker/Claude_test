"""Render the pickup moment of RAILS UP! — Pip in the wagon mid-air.

The exact frame this shows:
  - Player just collected the rail orb.
  - Western Trestle rail has materialised on the next 7 pillars ahead;
    pillars 1–4 are on screen, the rest continue off-screen right
    (sells the "spans 7" idea).
  - Wagon wraps Pip instantly — but gravity is still pulling it down.
    Wheels haven't touched the rail yet, so the rail hasn't taken over.
  - "RAILS UP!" pickup label drifts above the cart.

Falling-motion is read from the small cream streaks above the cart
(motion blur points opposite to motion).

Run:  python docs/railway_powerup_design/render_rail_pickup.py
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from game.config import W, H, GROUND_Y, PIPE_W  # noqa: E402
from game import biome  # noqa: E402
from game.draw import (  # noqa: E402
    get_sky_surface_biome, draw_mountains, draw_cloud, draw_ground,
)
from game.entities import Pipe  # noqa: E402

from render_cart_designs import (  # noqa: E402
    SCALE, W2, H2, CLOUD_LAYOUT,
    paint_wagon, paint_rail_hires, blit_hires_bird,
)

# 4 pipes — tighter spacing than the cart-design renders so we can fit
# four on screen + imply the remaining 3 of the 7 off-screen right. The
# 4th pipe is positioned so only its leading edge enters the frame.
PIPE_LAYOUT_PICKUP = (
    ( 18, 300, 170),
    (110, 255, 170),
    (210, 325, 170),
    (320, 270, 170),
)


def build_base_native(pipes, palette, bucket):
    surf = pygame.Surface((W, H))
    sky = get_sky_surface_biome(W, H, GROUND_Y, palette, bucket)
    surf.blit(sky, (0, 0))
    for bx, by, sc, var in CLOUD_LAYOUT:
        draw_cloud(surf, bx, by, sc, variant=var)
    draw_mountains(surf, 0.0, GROUND_Y, W,
                   palette['mtn_far'], palette['mtn_near'])
    draw_ground(surf, GROUND_Y, W, H, 0.0,
                palette['ground_top'], palette['ground_mid'], (60, 40, 25))
    for p in pipes:
        p.draw(surf, palette)
    return surf


def paint_label_at(surf, x_hi, y_hi, *, text="RAILS UP!", size_game=24,
                   base_col=(220, 150, 80)):
    """FloatText 'powerup' style label at an explicit hi-res position."""
    font = pygame.font.SysFont("Arial", size_game * SCALE, bold=True)
    base = font.render(text, True, base_col)
    bw, bh = base.get_size()
    light = tuple(int(base_col[i] + (255 - base_col[i]) * 0.45) for i in range(3))
    grad = pygame.Surface((bw, bh), pygame.SRCALPHA)
    for y in range(bh):
        t = y / max(1, bh - 1)
        c = tuple(int(light[i] + (base_col[i] - light[i]) * t) for i in range(3))
        pygame.draw.line(grad, c, (0, y), (bw, y))
    body = base.copy()
    body.blit(grad, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    dark = tuple(max(0, c // 4) for c in base_col)
    outline = font.render(text, True, dark)
    off = max(2, SCALE)
    for ox, oy in ((-off, 0), (off, 0), (0, -off), (0, off),
                   (-off + 1, -off + 1), (-off + 1, off - 1),
                   (off - 1, -off + 1), (off - 1, off - 1)):
        surf.blit(outline, (x_hi - bw // 2 + ox, y_hi - bh // 2 + oy))
    surf.blit(body, (x_hi - bw // 2, y_hi - bh // 2))


def paint_fall_streaks(surf, cx, top_y):
    """Cream streaks pointing UP from above the cart — sells the fall."""
    cream = (250, 240, 215)
    layer = pygame.Surface((W2, H2), pygame.SRCALPHA)
    for i in range(5):
        sx = cx - 10 * SCALE + i * 5 * SCALE
        y_start = top_y - 4 * SCALE
        y_end   = top_y - (18 + i * 3) * SCALE
        a = 80 + i * 25
        thickness = max(2, SCALE - i // 3)
        pygame.draw.line(layer, (*cream, a),
                         (sx, y_start), (sx, y_end), thickness)
    surf.blit(layer, (0, 0))


def render(out_path):
    phase = 0.78
    palette = biome.palette_for_phase(phase)
    bucket = biome.phase_bucket(phase)
    pipes = [Pipe(x, gy, gh) for (x, gy, gh) in PIPE_LAYOUT_PICKUP]
    for p in pipes:
        p.rail_active = True

    base = build_base_native(pipes, palette, bucket)
    big = pygame.transform.smoothscale(base, (W2, H2))
    paint_rail_hires(big, pipes)

    # Pip + wagon mid-air. Centre over pipe 2 horizontally, ~50 game-px
    # above pipe 2's rail so the wheel-rail gap reads clearly.
    mid = pipes[1]
    cart_cx = int((mid.x + PIPE_W / 2) * SCALE)
    rail_y_hi = int((mid.gap_y + mid.gap_h / 2) * SCALE)
    AIR_GAP = 55 * SCALE
    cart_anchor_y = rail_y_hi - AIR_GAP  # treat as if rail were here

    # Cart wheels first (drawn at the air position, not on the real rail).
    paint_wagon(big, cart_cx, cart_anchor_y, layer="wheels")
    # Pip lifted to sit in the cart — same PIP_LIFT (30 game-px) as the
    # cart-design renders.
    bird_y_hi = cart_anchor_y - 30 * SCALE - 2 * SCALE
    blit_hires_bird(big, cart_cx, bird_y_hi)
    # Cart body covers Pip's lower half.
    paint_wagon(big, cart_cx, cart_anchor_y, layer="body")

    # Falling-motion streaks above the cart.
    cart_body_top_hi = cart_anchor_y - 2 * 5 * SCALE - 18 * SCALE
    paint_fall_streaks(big, cart_cx, cart_body_top_hi)

    # Pickup label drifts up just above the cart.
    label_y_hi = cart_body_top_hi - 28 * SCALE
    paint_label_at(big, cart_cx, label_y_hi)

    pygame.image.save(big, out_path)


def main():
    out = os.path.join(HERE, "rail_pickup_moment.png")
    render(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
