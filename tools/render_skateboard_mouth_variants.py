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


# ── 5 punk-style mouths (research: Misfits, Black Flag, Vans,
# Suicidal Tendencies, Powell Peralta, classic Jolly Roger). ──

def _mouth_p1_misfits(big, sk, jaw_y):
    """P1 — Misfits "Crimson Ghost" grin. A horizontal upper-jaw
    line with 7 downward-pointing triangle teeth hanging from
    it. No bottom jaw bar — the line IS the upper jaw, the teeth
    hang below it like in the Misfits skull logo."""
    span = 12 * SS
    upper_y = jaw_y - int(SS * 0.5)
    # Upper-jaw line.
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, upper_y),
                     (sk.centerx + span // 2, upper_y),
                     max(1, int(1.2 * SS)))
    # 7 downward triangles hanging from the line.
    n = 7
    tooth_h = int(2.4 * SS)
    half_w = max(1, int(SS * 0.55))
    for i in range(n):
        t = i / (n - 1)
        tx = sk.centerx - span // 2 + int(t * span)
        pygame.draw.polygon(big, DOME, [
            (tx - half_w, upper_y),
            (tx + half_w, upper_y),
            (tx,          upper_y + tooth_h),
        ])


def _mouth_p2_sawtooth(big, sk, jaw_y):
    """P2 — Pure zigzag / W-shape sawtooth at jaw_y, no horizontal
    jaw bar. Spike-y stencil-punk vibe."""
    span = 13 * SS
    peaks = 5            # number of valleys (the W has 5 valleys)
    amp = int(2.5 * SS)
    pts = []
    n_segs = peaks * 2
    for i in range(n_segs + 1):
        t = i / n_segs
        x = sk.centerx - span // 2 + int(t * span)
        y = jaw_y + (amp if (i % 2 == 0) else -amp)
        pts.append((x, y))
    pygame.draw.lines(big, DOME, False, pts,
                      max(1, int(1.4 * SS)))


def _mouth_p3_stitched(big, sk, jaw_y):
    """P3 — Stitched bandana. Horizontal bar with 4 diagonal X
    cross-stitches across it. Reads as sewn-shut punk mouth."""
    span = 11 * SS
    pygame.draw.line(big, DOME,
                     (sk.centerx - span // 2, jaw_y),
                     (sk.centerx + span // 2, jaw_y),
                     max(1, int(1.4 * SS)))
    stitch_h = int(2.0 * SS)
    stitch_w = int(2.0 * SS)
    n = 4
    for i in range(n):
        t = (i + 0.5) / n
        cx0 = sk.centerx - span // 2 + int(t * span)
        # Two short diagonal strokes forming an X centred on the bar.
        pygame.draw.line(big, DOME,
                         (cx0 - stitch_w // 2, jaw_y - stitch_h // 2),
                         (cx0 + stitch_w // 2, jaw_y + stitch_h // 2),
                         max(1, int(SS * 0.7)))
        pygame.draw.line(big, DOME,
                         (cx0 - stitch_w // 2, jaw_y + stitch_h // 2),
                         (cx0 + stitch_w // 2, jaw_y - stitch_h // 2),
                         max(1, int(SS * 0.7)))


def _mouth_p4_missing_tooth(big, sk, jaw_y):
    """P4 — Missing-tooth grin. Like M2's square teeth row but the
    CENTRE tooth is missing (gap), plus a small downward red
    triangle drip hanging from the gap (tiny punk accent)."""
    pygame.draw.line(big, DOME,
                     (sk.centerx - 6 * SS, jaw_y),
                     (sk.centerx + 6 * SS, jaw_y),
                     max(1, int(1.2 * SS)))
    teeth_n = 5
    tooth_w = int(1.6 * SS)
    tooth_h = int(2.6 * SS)
    span = 10 * SS
    for i in range(teeth_n):
        if i == teeth_n // 2:
            continue  # missing centre tooth
        t = i / (teeth_n - 1)
        tx = sk.centerx - span // 2 + int(t * span)
        rect = pygame.Rect(0, 0, tooth_w, tooth_h)
        rect.midbottom = (tx, jaw_y - max(1, SS // 3))
        pygame.draw.rect(big, DOME, rect)
    # Red drip hanging from the centre gap.
    drip_top_y = jaw_y + int(SS * 0.4)
    pygame.draw.polygon(big, RED, [
        (sk.centerx - int(SS * 0.9), drip_top_y),
        (sk.centerx + int(SS * 0.9), drip_top_y),
        (sk.centerx,                  drip_top_y + int(2.4 * SS)),
    ])


def _mouth_p5_checker(big, sk, jaw_y):
    """P5 — Vans-checkerboard. 5 alternating black/white square
    teeth sitting on a jaw line. Pure skate-culture quotation."""
    pygame.draw.line(big, DOME,
                     (sk.centerx - 6 * SS, jaw_y),
                     (sk.centerx + 6 * SS, jaw_y),
                     max(1, int(1.2 * SS)))
    teeth_n = 5
    tooth_w = int(1.8 * SS)
    tooth_h = int(2.6 * SS)
    span = 10 * SS
    for i in range(teeth_n):
        t = i / (teeth_n - 1)
        tx = sk.centerx - span // 2 + int(t * span)
        rect = pygame.Rect(0, 0, tooth_w, tooth_h)
        rect.midbottom = (tx, jaw_y - max(1, SS // 3))
        col = DOME if (i % 2 == 0) else BONE
        pygame.draw.rect(big, col, rect)
        # Tiny dark outline so the white squares still read against
        # the bone skull.
        pygame.draw.rect(big, DOME, rect, max(1, SS // 3))


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


def draw_p1_misfits(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_p1_misfits)


def draw_p2_sawtooth(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_p2_sawtooth)


def draw_p3_stitched(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_p3_stitched)


def draw_p4_missing_tooth(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_p4_missing_tooth)


def draw_p5_checker(surf, cx, cy, pulse):
    _paint_face(surf, cx, cy, pulse, _mouth_p5_checker)


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
    ("P1_misfits",       draw_p1_misfits,
     "P1: Misfits Crimson-Ghost grin — 7 triangle fangs"),
    ("P2_sawtooth",      draw_p2_sawtooth,
     "P2: pure W-shape sawtooth — stencil-punk spike"),
    ("P3_stitched",      draw_p3_stitched,
     "P3: stitched bandana — bar + 4 X-stitches"),
    ("P4_missing_tooth", draw_p4_missing_tooth,
     "P4: missing-tooth grin + red drip — pirate rocker"),
    ("P5_checker",       draw_p5_checker,
     "P5: Vans-checker — alternating black/white square teeth"),
]

# Subset used for the 6-cell M5+punk comparison sheet.
COMPARISON_LABELS = (
    "M5_pirate_grin",
    "P1_misfits", "P2_sawtooth", "P3_stitched",
    "P4_missing_tooth", "P5_checker",
)


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

    def _build_sheet(cells, columns=None):
        """Lay out cells in a grid. `columns` defaults to len(cells)
        (single row). Returns the rendered surface."""
        if columns is None:
            columns = len(cells)
        rows = (len(cells) + columns - 1) // columns
        s_w = columns * cell_w + (columns - 1) * gap + 24
        s_h = rows * (cell_h + band_h) + (rows - 1) * gap + 24
        s = pygame.Surface((s_w, s_h))
        s.fill((10, 12, 24))
        for idx, (label, caption, icon) in enumerate(cells):
            r = idx // columns
            c = idx % columns
            x = 12 + c * (cell_w + gap)
            y = 12 + r * (cell_h + band_h + gap)
            s.blit(icon, (x, y))
            band = _label_band(cell_w, label, caption, height=band_h)
            s.blit(band, (x, y + cell_h))
        return s

    # Full 10-cell contact sheet (M1-M5 + P1-P5) — 5 per row.
    full = _build_sheet(saved, columns=5)
    full_path = os.path.join(_OUT, "00_contact_sheet.png")
    pygame.image.save(full, full_path)
    print(f"saved {full_path}")

    # 6-cell punk-comparison sheet (M5 + P1-P5) — 3 per row.
    by_label = {label: (label, caption, icon)
                for (label, caption, icon) in saved}
    comparison_cells = [by_label[l] for l in COMPARISON_LABELS
                        if l in by_label]
    punk = _build_sheet(comparison_cells, columns=3)
    punk_path = os.path.join(_OUT, "00_punk_comparison.png")
    pygame.image.save(punk, punk_path)
    print(f"saved {punk_path}")

    base = ("https://raw.githubusercontent.com/ytocker/skybit/"
            "v5_powerups/docs/screenshots/skateboard_mouth_variants")
    print()
    print(f"{base}/00_contact_sheet.png")
    for label, caption, _ in saved:
        print(f"{base}/{label}.png  -- {caption}")
        print(f"{base}/{label}_ingame.png")


if __name__ == "__main__":
    main()
