"""Render the FINAL live helmet (game/entities.py:Bird._draw_helmet)
in-game, as a before/after side-by-side with the previous helmet.

For the "before" pass we restore the old draw function from git via
a stashed copy inlined here, so we don't have to checkout a prior
revision.

Usage:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_helmet_final.py
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_helmet_side_view_variants import (
    build_world, render_zoom, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_variants", "side_view_v2")


def _draw_old_helmet(bird, surf, cx, cy, flipped):
    """Old helmet (game/entities.py before this commit) — full
    ellipse, symmetric chinstraps, front skull, anchor (+15, -11).
    Inlined here so the before/after render works without a
    git checkout."""
    s = bird.shrink_scale
    hw = int(24 * s)
    hh = int(15 * s)
    pad = 4
    drop = int(12 * s)
    helm = pygame.Surface(
        (hw + pad * 2, hh + pad * 2 + drop), pygame.SRCALPHA)
    pygame.draw.ellipse(helm, (10, 10, 18),
                        pygame.Rect(pad, pad, hw, hh * 2))
    pygame.draw.ellipse(helm, (50, 50, 60),
                        pygame.Rect(pad + 3, pad + 1,
                                    max(2, hw - 8), max(2, hh - 4)))
    vent_y = pad + hh // 2 - 2
    for vx_frac in (0.30, 0.50, 0.70):
        vx = pad + int(hw * vx_frac)
        pygame.draw.line(helm, (10, 10, 18),
                         (vx - 1, vent_y), (vx + 1, vent_y), 1)
    pygame.draw.ellipse(helm, (200, 200, 210),
                        pygame.Rect(pad - 1, pad + hh - 1, hw + 2, 3))
    fin_top_y = pad - 3
    fin_base_y = pad + 2
    cx_s = pad + hw // 2
    fin_pts = [(cx_s - hw // 4, fin_base_y),
               (cx_s - hw // 5, fin_top_y),
               (cx_s + hw // 5, fin_top_y),
               (cx_s + hw // 4, fin_base_y)]
    pygame.draw.polygon(helm, (240, 240, 230), fin_pts)
    pygame.draw.polygon(helm, (10, 10, 18), fin_pts, 1)
    sk_w = max(4, int(7 * s))
    sk_h = max(3, int(5 * s))
    sk_rect = pygame.Rect(0, 0, sk_w, sk_h)
    sk_rect.center = (cx_s, pad + hh - 4)
    pygame.draw.ellipse(helm, (240, 240, 230), sk_rect)
    pygame.draw.ellipse(helm, (10, 10, 18), sk_rect, 1)
    eye_y = sk_rect.centery
    pygame.draw.circle(helm, (10, 10, 18),
                       (sk_rect.centerx - 1, eye_y), 1)
    pygame.draw.circle(helm, (10, 10, 18),
                       (sk_rect.centerx + 1, eye_y), 1)
    left_shoulder  = (pad + 3,      pad + hh + 1)
    right_shoulder = (pad + hw - 3, pad + hh + 1)
    buckle = (pad + hw // 2, pad + hh + drop - 2)
    pygame.draw.line(helm, (60, 60, 70), left_shoulder,  buckle, 2)
    pygame.draw.line(helm, (60, 60, 70), right_shoulder, buckle, 2)
    pygame.draw.circle(helm, (200, 50, 50), buckle, 2)
    tilt = -bird.tilt_deg if flipped else bird.tilt_deg
    y_off = 11 * s if flipped else -11 * s
    offset = pygame.math.Vector2(15 * s, y_off).rotate(-tilt)
    rotated = pygame.transform.rotate(helm, tilt)
    if flipped:
        rotated = pygame.transform.flip(rotated, False, True)
    r = rotated.get_rect(center=(int(cx + offset.x),
                                 int(cy + offset.y)))
    surf.blit(rotated, r.topleft)


def main():
    # AFTER — live helmet from game/entities.py.
    world_after = build_world()
    zoom_after = render_zoom(world_after, zoom=6, crop=60)

    # BEFORE — restore the old draw function via monkey-patch.
    world_before = build_world()
    world_before.bird._draw_helmet = (
        lambda surf, cx, cy, flipped, b=world_before.bird:
            _draw_old_helmet(b, surf, cx, cy, flipped)
    )
    zoom_before = render_zoom(world_before, zoom=6, crop=60)

    # Save the final zoom + gameplay frame for posterity.
    final_zoom_path = os.path.join(_OUT, "FINAL_v4_punk_mohawk.png")
    pygame.image.save(zoom_after, final_zoom_path)
    print(f"saved {final_zoom_path}")
    final_game_path = os.path.join(_OUT, "FINAL_v4_punk_mohawk_gameplay.png")
    pygame.image.save(render_play_scene(world_after), final_game_path)
    print(f"saved {final_game_path}")

    # Side-by-side before/after.
    zw, zh = zoom_after.get_size()
    band_h = 56
    gap = 12
    sheet = pygame.Surface((zw * 2 + gap + 24, zh + band_h + 24))
    sheet.fill((10, 12, 24))
    sheet.blit(zoom_before, (12, 12))
    sheet.blit(zoom_after,  (12 + zw + gap, 12))
    sheet.blit(_label_band(zw, "BEFORE",
                           "Old helmet — top-down ellipse, "
                           "symmetric chinstraps, anchor (+15, -11)",
                           height=band_h),
               (12, 12 + zh))
    sheet.blit(_label_band(zw, "AFTER",
                           "punk_mohawk_side — side-view dome, "
                           "single fin + strap, anchor (+20, -20)",
                           height=band_h),
               (12 + zw + gap, 12 + zh))
    sheet_path = os.path.join(_OUT, "FINAL_before_after.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_variants/"
            "side_view_v2")
    print()
    print(f"{base}/FINAL_before_after.png")
    print(f"{base}/FINAL_v4_punk_mohawk.png")
    print(f"{base}/FINAL_v4_punk_mohawk_gameplay.png")


if __name__ == "__main__":
    main()
