"""Render 5 SKATEBOARD-icon variants with DIFFERENT mouth styles.

User feedback on the previous size-only batch: the (original)
mouth — 3 vertical teeth lines passing THROUGH a horizontal jaw
line — reads as creepy / grimacing. This batch keeps the face
size fixed at 27 × 22 SS (the moderate V3 from before) and the
crossed-deck X composition / palette unchanged; only the
mouth shape varies.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_skateboard_mouth_variants.py
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
                    "skateboard_mouth_variants")
os.makedirs(_OUT, exist_ok=True)


# Kit palette (matches the live icon).
DOME   = (10, 10, 18)
CHROME = (200, 200, 210)
BONE   = (240, 240, 230)
CREAM  = (245, 240, 230)
RED    = (200, 50, 50)

SS = 6
NATIVE_W = NATIVE_H = 96
SK_W = 27       # fixed face size for this batch
SK_H = 22


# ── shared face painter ─────────────────────────────────────────────────────

def _paint_face(surf, cx, cy, pulse, mouth_fn):
    """Paint the Jolly Roger composition with the standard
    crossed-decks behind, the standard skull + eyes + nose, and
    a per-variant `mouth_fn(big, sk, jaw_y)` that draws the
    mouth on top of the skull at jaw_y."""
    cy_bob = cy + int(math.sin(pulse * 1.0) * 2)
    big = pygame.Surface((NATIVE_W * SS, NATIVE_H * SS),
                          pygame.SRCALPHA)
    bx = big.get_width() // 2
    by = big.get_height() // 2

    # Two crossed skateboard decks behind the skull.
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

    # Skull ellipse.
    sk = pygame.Rect(0, 0, SK_W * SS, SK_H * SS)
    sk.center = (bx, by - SS)
    pygame.draw.ellipse(big, BONE, sk)
    pygame.draw.ellipse(big, DOME, sk, int(1.2 * SS))

    # Eyes — same fractional position as the previous batch.
    eye_r = int(SK_W * SS * 0.108)
    eye_x_off = int(SK_W * SS * 0.20)
    eye_y = sk.top + int(SK_H * SS * 0.36)
    for ex in (sk.centerx - eye_x_off,
               sk.centerx + eye_x_off):
        pygame.draw.circle(big, DOME, (ex, eye_y), eye_r)

    # Nose — original-sized triangle at 0.55 fractional y.
    nose_top_y = sk.top + int(SK_H * SS * 0.55)
    nose_bot_y = nose_top_y + int(2.5 * SS)
    pygame.draw.polygon(big, DOME, [
        (sk.centerx - SS, nose_top_y),
        (sk.centerx + SS, nose_top_y),
        (sk.centerx,      nose_bot_y),
    ])

    # Per-variant mouth at jaw_y = 0.72 fractional from top.
    jaw_y = sk.top + int(SK_H * SS * 0.72)
    mouth_fn(big, sk, jaw_y)

    # Smoothscale-down + blit.
    icon = pygame.transform.smoothscale(big, (NATIVE_W, NATIVE_H))
    surf.blit(icon, icon.get_rect(center=(cx, cy_bob)))


# ── 5 mouth variants ────────────────────────────────────────────────────────

def _mouth_smile_arc(big, sk, jaw_y):
    """M1 — Single curved smile arc, no teeth. The friendliest /
    least-creepy option."""
    # Draw an arc as the bottom half of a thin ellipse.
    arc_w = 14 * SS
    arc_h = 5 * SS
    arc_rect = pygame.Rect(0, 0, arc_w, arc_h)
    arc_rect.midtop = (sk.centerx, jaw_y - 2 * SS)
    pygame.draw.arc(big, DOME, arc_rect,
                    math.radians(180), math.radians(360),
                    max(1, int(1.4 * SS)))


def _mouth_square_teeth(big, sk, jaw_y):
    """M2 — Row of small filled square teeth sitting ABOVE a
    horizontal jaw line. Cartoon-grid style."""
    # Horizontal jaw line beneath the teeth.
    pygame.draw.line(big, DOME,
                     (sk.centerx - 6 * SS, jaw_y),
                     (sk.centerx + 6 * SS, jaw_y),
                     max(1, int(1.2 * SS)))
    # 5 small filled square teeth above the jaw, evenly spaced.
    teeth_n = 5
    tooth_w = int(1.6 * SS)
    tooth_h = int(2.6 * SS)
    span = 10 * SS
    for i in range(teeth_n):
        t = i / (teeth_n - 1)
        tx = sk.centerx - span // 2 + int(t * span)
        rect = pygame.Rect(0, 0, tooth_w, tooth_h)
        rect.midbottom = (tx, jaw_y - max(1, SS // 3))
        pygame.draw.rect(big, DOME, rect)


def _mouth_teeth_above_jaw(big, sk, jaw_y):
    """M3 — Original 3-tooth idea but teeth only EXTEND UPWARD
    from the jaw line (no longer pass through it). Removes the
    grimace look while keeping the tooth count."""
    pygame.draw.line(big, DOME,
                     (sk.centerx - 6 * SS, jaw_y),
                     (sk.centerx + 6 * SS, jaw_y),
                     max(1, int(1.2 * SS)))
    for tx in (-4 * SS, 0, 4 * SS):
        pygame.draw.line(big, DOME,
                         (sk.centerx + tx, jaw_y - 4 * SS),
                         (sk.centerx + tx, jaw_y - max(1, SS // 3)),
                         int(1.2 * SS))


def _mouth_simple_bar(big, sk, jaw_y):
    """M4 — Just a horizontal bar, no teeth. Minimalist."""
    pygame.draw.line(big, DOME,
                     (sk.centerx - 7 * SS, jaw_y),
                     (sk.centerx + 7 * SS, jaw_y),
                     max(1, int(1.6 * SS)))


def _mouth_pirate_grin(big, sk, jaw_y):
    """M5 — Curved smile with 2 small tooth dots — happy pirate /
    skater vibe. The arc is the lower half of an ellipse (same
    geometry as M1) plus 2 small filled squares hanging from the
    arc for tooth hints."""
    arc_w = 14 * SS
    arc_h = 5 * SS
    arc_rect = pygame.Rect(0, 0, arc_w, arc_h)
    arc_rect.midtop = (sk.centerx, jaw_y - 2 * SS)
    pygame.draw.arc(big, DOME, arc_rect,
                    math.radians(180), math.radians(360),
                    max(1, int(1.4 * SS)))
    # 2 small filled-square tooth hints on the arc's upper edge.
    for tx in (-2 * SS, 2 * SS):
        rect = pygame.Rect(0, 0, int(1.6 * SS), int(1.8 * SS))
        rect.midtop = (sk.centerx + tx, jaw_y - 2 * SS)
        pygame.draw.rect(big, DOME, rect)


def draw_m1_smile_arc(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_smile_arc)


def draw_m2_square_teeth(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_square_teeth)


def draw_m3_teeth_above(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_teeth_above_jaw)


def draw_m4_simple_bar(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_simple_bar)


def draw_m5_pirate_grin(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_pirate_grin)


VARIANTS = [
    ("M1_smile_arc",     draw_m1_smile_arc,
     "M1: single curved smile arc, no teeth — friendliest"),
    ("M2_square_teeth",  draw_m2_square_teeth,
     "M2: 5 square teeth above a jaw line — cartoon grid"),
    ("M3_teeth_above",   draw_m3_teeth_above,
     "M3: original 3 teeth but ABOVE the jaw line — no grimace"),
    ("M4_simple_bar",    draw_m4_simple_bar,
     "M4: just a horizontal bar, no teeth — minimalist"),
    ("M5_pirate_grin",   draw_m5_pirate_grin,
     "M5: curved arc + 2 tooth hints — happy pirate"),
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
            "v5_powerups/docs/screenshots/skateboard_mouth_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
