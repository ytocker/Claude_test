"""Render 5 SKATEBOARD icon variants with progressively larger
Jolly Roger skulls.

The live `_draw_skateboard_icon` (`game/entities.py:2364+`) uses
a 23 × 18 SS skull on a 96 × 96 native / SS=6 canvas. At game
pickup scale the bottom-of-skull jaw + teeth merge into a smudge.
These 5 candidates keep the same crossed-deck X composition and
palette but scale the skull (and its eyes/nose/jaw/teeth) up.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_skull_size_variants.py
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

pygame.init()
pygame.display.set_mode((1, 1))

from tools.render_helmet_side_view_variants import (
    build_world, render_play_scene, _label_band,
)


_OUT = os.path.join(_REPO, "docs", "screenshots",
                    "skateboard_skull_size")
os.makedirs(_OUT, exist_ok=True)


# Kit palette (matches the live icon).
DOME   = (10, 10, 18)
CHROME = (200, 200, 210)
BONE   = (240, 240, 230)
CREAM  = (245, 240, 230)
RED    = (200, 50, 50)

SS = 6
NATIVE_W = NATIVE_H = 96


def _paint_icon(surf, cx, cy, pulse, sk_w, sk_h):
    """Paint the Jolly Roger composition onto `surf` at (cx, cy).
    `sk_w` and `sk_h` are the SKULL dimensions in SS units;
    every skull sub-feature scales proportionally so the
    candidate's look stays balanced."""
    cy_bob = cy + int(math.sin(pulse * 1.0) * 2)
    big = pygame.Surface((NATIVE_W * SS, NATIVE_H * SS),
                          pygame.SRCALPHA)
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Two crossed skateboard decks behind the skull (unchanged).
    for angle in (35, -35):
        sub_w = 46 * SS
        sub_h = 9 * SS
        sub = pygame.Surface((sub_w + 4 * SS, sub_h + 4 * SS),
                              pygame.SRCALPHA)
        d = pygame.Rect(0, 0, sub_w, sub_h)
        d.center = (sub.get_width() // 2, sub.get_height() // 2)
        pygame.draw.rect(sub, CHROME, d, border_radius=2 * SS)
        pygame.draw.rect(sub, DOME, d.inflate(-2 * SS, -2 * SS),
                         border_radius=SS)
        for sign in (-1, 1):
            wx = d.centerx + sign * (sub_w // 2 - 3 * SS)
            pygame.draw.circle(sub, CREAM, (wx, d.centery),
                               int(3 * SS))
            pygame.draw.circle(sub, RED, (wx, d.centery),
                               int(1.4 * SS))
        rotated = pygame.transform.rotate(sub, angle)
        big.blit(rotated, rotated.get_rect(center=(bx, by)))

    # Skull. All features below derive from this rect, so the
    # whole face scales uniformly.
    sk = pygame.Rect(0, 0, sk_w * SS, sk_h * SS)
    sk.center = (bx, by - SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.2 * SS))

    # Eye sockets — radius and offset scale with skull width.
    eye_r = int(sk_w * SS * 0.108)            # was 2.5 SS on a 23-SS skull
    eye_x_off = int(sk_w * SS * 0.20)         # was ~5 SS
    eye_y_off = int(sk_h * SS * 0.06)         # was ~1 SS above centre
    for ex in (sk.centerx - eye_x_off,
               sk.centerx + eye_x_off):
        pygame.draw.circle(big, DOME,
                           (ex, sk.centery - eye_y_off), eye_r)

    # Nose triangle — height + half-width scale with skull height.
    nose_top_y = sk.centery + int(sk_h * SS * 0.18)
    nose_bot_y = sk.centery + int(sk_h * SS * 0.32)
    nose_hw = int(sk_w * SS * 0.045)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - nose_hw, nose_top_y),
        (sk.centerx + nose_hw, nose_top_y),
        (sk.centerx,           nose_bot_y),
    ])

    # Jaw line — width tracks skull width; sits 2 SS above bottom.
    jaw_hw = int(sk_w * SS * 0.26)
    jaw_y = sk.bottom - int(sk_h * SS * 0.12)
    pygame.draw.line(big, DOME,
                     (sk.centerx - jaw_hw, jaw_y),
                     (sk.centerx + jaw_hw, jaw_y),
                     max(1, int(1.2 * SS)))

    # Teeth — 5 short vertical lines instead of 3 so larger
    # skulls show off more teeth without looking sparse.
    teeth_n = 5
    teeth_span = int(sk_w * SS * 0.40)
    teeth_top = jaw_y - int(sk_h * SS * 0.18)
    teeth_bot = jaw_y + int(sk_h * SS * 0.08)
    for i in range(teeth_n):
        t = i / (teeth_n - 1)
        tx = sk.centerx - teeth_span // 2 + int(t * teeth_span)
        pygame.draw.line(big, DOME, (tx, teeth_top),
                         (tx, teeth_bot),
                         max(1, int(1.2 * SS)))

    # Smoothscale-down + blit.
    icon = pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))
    surf.blit(icon, icon.get_rect(center=(cx, cy_bob)))


def draw_v1_subtle(surf, cx, cy, pulse):
    _paint_icon(surf, cx, cy, pulse, sk_w=26, sk_h=21)


def draw_v2_moderate(surf, cx, cy, pulse):
    _paint_icon(surf, cx, cy, pulse, sk_w=28, sk_h=23)


def draw_v3_clear(surf, cx, cy, pulse):
    _paint_icon(surf, cx, cy, pulse, sk_w=30, sk_h=25)


def draw_v4_bold(surf, cx, cy, pulse):
    _paint_icon(surf, cx, cy, pulse, sk_w=33, sk_h=27)


def draw_v5_max(surf, cx, cy, pulse):
    _paint_icon(surf, cx, cy, pulse, sk_w=36, sk_h=29)


VARIANTS = [
    ("V1_subtle",   draw_v1_subtle,
     "V1: skull 26x21 SS (+13% w, +17% h) — smallest readable bump"),
    ("V2_moderate", draw_v2_moderate,
     "V2: skull 28x23 SS (+22% w, +28% h) — mouth clearly readable"),
    ("V3_clear",    draw_v3_clear,
     "V3: skull 30x25 SS (+30% w, +39% h) — skull dominant"),
    ("V4_bold",     draw_v4_bold,
     "V4: skull 33x27 SS (+43% w, +50% h) — skull is the silhouette"),
    ("V5_max",      draw_v5_max,
     "V5: skull 36x29 SS (+57% w, +61% h) — decks frame the edges"),
]


# ── output ──────────────────────────────────────────────────────────────────

def _icon_zoom_png(draw_fn, label):
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_fn(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    big = pygame.transform.scale(base, (NATIVE_W * 6, NATIVE_H * 6))
    pygame.draw.rect(big, (255, 215, 0), big.get_rect(), 2)
    return big


def _ingame_png(draw_fn, label):
    world = build_world()
    frame = render_play_scene(world)
    icon_cx = int(world.bird.x) + 110
    icon_cy = int(world.bird.y)
    base = pygame.Surface((NATIVE_W, NATIVE_H), pygame.SRCALPHA)
    draw_fn(base, NATIVE_W // 2, NATIVE_H // 2, pulse=1.6)
    frame.blit(base, base.get_rect(center=(icon_cx, icon_cy)))
    return frame


def main():
    saved = []
    for label, fn, caption in VARIANTS:
        icon_zoom = _icon_zoom_png(fn, label)
        ingame    = _ingame_png(fn, label)
        zoom_path   = os.path.join(_OUT, f"{label}.png")
        ingame_path = os.path.join(_OUT, f"{label}_ingame.png")
        pygame.image.save(icon_zoom, zoom_path)
        pygame.image.save(ingame, ingame_path)
        saved.append((label, caption, icon_zoom))
        print(f"saved {zoom_path}")
        print(f"saved {ingame_path}")

    cell_w = saved[0][2].get_width()
    cell_h = saved[0][2].get_height()
    band_h = 56
    gap    = 12
    sheet_w = len(saved) * cell_w + (len(saved) - 1) * gap + 24
    sheet_h = cell_h + band_h + 24
    sheet = pygame.Surface((sheet_w, sheet_h))
    sheet.fill((10, 12, 24))
    for idx, (label, caption, icon) in enumerate(saved):
        x = 12 + idx * (cell_w + gap)
        sheet.blit(icon, (x, 12))
        band = _label_band(cell_w, label, caption, height=band_h)
        sheet.blit(band, (x, 12 + cell_h))
    sheet_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(sheet, sheet_path)
    print(f"saved {sheet_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_skull_size")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
