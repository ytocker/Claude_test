"""Render 5 NIGHTGLOW powerup ICON design candidates — sticker style.

The previous icon set was too painterly. The user asked for a
glow-in-the-dark sticker aesthetic: flat solid shapes, lime-green
phosphorescent fill, dark outline, slight ambient halo on the dark
backdrop. Five recognisable GITD-sticker silhouettes that each hint at
the NIGHTGLOW effect ("world goes dark, things glow neon-green"):

    1. STAR      — the classic 5-point ceiling sticker
    2. MOON      — sleepy crescent moon with face
    3. GHOST     — friendly cartoon ghost
    4. MUSHROOM  — speckled toadstool
    5. BOLT      — lightning bolt

Each PNG is 240×240, a single sticker centred on a dark night
backdrop. The chosen design will be ported into entities.py's
_draw_nightglow_icon at ~52×52 native scale.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_nightglow_icons.py
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


CANVAS = 240
CENTER = CANVAS // 2

# Phosphorescent green-yellow — the classic GITD-pigment colour. Brighter
# and more yellow than the in-world halo green so the sticker visibly
# pops as a printed-vinyl thing under dark light.
STICKER_FILL      = (185, 255, 130)
STICKER_HIGHLIGHT = (235, 255, 200)
STICKER_OUTLINE   = (60, 160, 40)
STICKER_DEEP      = (35, 110, 25)


def _dark_backdrop() -> pygame.Surface:
    surf = pygame.Surface((CANVAS, CANVAS)).convert()
    for y in range(CANVAS):
        t = y / CANVAS
        r = int(4 + (12 - 4) * t)
        g = int(8 + (20 - 8) * t)
        b = int(22 + (38 - 22) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (CANVAS, y))
    import random as _r
    rng = _r.Random(11)
    for _ in range(18):
        x = rng.randint(0, CANVAS - 1)
        y = rng.randint(0, CANVAS - 1)
        pygame.draw.circle(surf, (220, 220, 200), (x, y), 1)
    return surf


def _ambient_halo(surf, cx, cy, radius, alpha_peak):
    """Soft ambient glow that says 'this is glowing in the dark'."""
    pad = radius + 4
    aura = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        t = r / radius
        a = int(alpha_peak * (1.0 - t) ** 1.5)
        if a <= 0:
            continue
        pygame.draw.circle(aura, (130, 240, 90, a), (pad, pad), r)
    surf.blit(aura, (cx - pad, cy - pad),
              special_flags=pygame.BLEND_RGBA_ADD)


def _sticker_polygon(surf, points, highlight_offset_y=-4):
    """Draw a flat polygon sticker: fill + outline + top highlight rim."""
    pygame.draw.polygon(surf, STICKER_OUTLINE,
                        [(x + dx, y + dy) for x, y in points
                         for dx, dy in [(0, 0)]],
                        0)  # base/outline (slightly larger via outline thickness)
    pygame.draw.polygon(surf, STICKER_OUTLINE, points, 0)
    # Fill, inset by 3px (achieved by drawing fill, then a darker outline 3px wide)
    pygame.draw.polygon(surf, STICKER_FILL, points, 0)
    pygame.draw.polygon(surf, STICKER_OUTLINE, points, 4)


# ─── ICON 1 — STAR (classic 5-point ceiling sticker) ────────────────────────

def icon_star(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx, cy, 95, 170)

    # 5-point star
    r_outer = 78
    r_inner = 33
    points = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        points.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    pygame.draw.polygon(surf, STICKER_FILL, points)
    pygame.draw.polygon(surf, STICKER_OUTLINE, points, 5)

    # Top-edge highlight — a smaller star, offset up, drawn in highlight colour.
    hl = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = (r_outer - 14) if i % 2 == 0 else (r_inner - 6)
        hl.append((cx + r * math.cos(a), cy - 6 + r * math.sin(a)))
    pygame.draw.polygon(surf, STICKER_HIGHLIGHT, hl)
    pygame.draw.polygon(surf, STICKER_FILL, hl, 3)  # blend back to fill

    # Tiny central white pop
    pygame.draw.circle(surf, (255, 255, 255), (cx - 4, cy - 14), 4)


# ─── ICON 2 — MOON (sleepy crescent with face) ──────────────────────────────

def icon_moon(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx, cy, 95, 170)

    # Crescent: large fill circle minus a shifted "bite" circle.
    # Render onto its own SRCALPHA layer so we can punch the bite cleanly.
    layer = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
    pygame.draw.circle(layer, STICKER_OUTLINE, (cx, cy), 76)
    pygame.draw.circle(layer, STICKER_FILL,    (cx, cy), 72)
    pygame.draw.circle(layer, (0, 0, 0, 0),    (cx + 28, cy - 18), 64)

    # Highlight rim along the left edge of the crescent (top-left where light hits)
    pygame.draw.circle(layer, STICKER_HIGHLIGHT, (cx - 4, cy - 4), 70)
    pygame.draw.circle(layer, STICKER_FILL,      (cx - 1, cy - 1), 66)
    pygame.draw.circle(layer, (0, 0, 0, 0),      (cx + 28, cy - 18), 64)

    surf.blit(layer, (0, 0))

    # Face: closed sleepy eye + tiny smile, positioned on the visible (left) lobe.
    eye_x, eye_y = cx - 22, cy - 4
    # Closed eye = a small arc
    pygame.draw.arc(surf, STICKER_DEEP,
                    pygame.Rect(eye_x - 9, eye_y - 5, 18, 10),
                    math.pi, math.tau, 3)
    # Tiny smile
    pygame.draw.arc(surf, STICKER_DEEP,
                    pygame.Rect(cx - 30, cy + 14, 18, 12),
                    math.pi + 0.3, math.tau - 0.3, 3)
    # Cheek blush
    pygame.draw.circle(surf, (140, 220, 90), (cx - 30, cy + 8), 3)


# ─── ICON 3 — GHOST (friendly cartoon ghost) ────────────────────────────────

def icon_ghost(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx + 2, cy, 95, 175)

    # Body: rounded-top + wavy bottom hem.
    # Build silhouette as a polygon: a big half-circle on top, vertical sides,
    # wavy zig-zag bottom.
    top_r = 60
    body_w = top_r * 2
    body_h = 120
    left  = cx - top_r
    right = cx + top_r
    top_y = cy - 56
    bot_y = top_y + body_h

    pts = []
    # Top arc — 19 samples
    for i in range(19):
        a = math.pi + (math.pi * i / 18)
        pts.append((cx + top_r * math.cos(a), top_y + top_r + top_r * math.sin(a)))
    # Right side down
    pts.append((right, bot_y - 16))
    # Wavy hem (3 humps)
    hem_xs = [right, right - 20, right - 40, right - 60, right - 80, right - 100, left]
    hem_ys = [bot_y - 16, bot_y - 4, bot_y - 16, bot_y - 4, bot_y - 16, bot_y - 4, bot_y - 16]
    for x, y in zip(hem_xs, hem_ys):
        pts.append((x, y))
    # Close back up left side
    pts.append((left, top_y + top_r))

    pygame.draw.polygon(surf, STICKER_OUTLINE, pts)
    # Inset fill
    fill_pts = [(x + (1 if x > cx else -1) * 4, y - 1) for x, y in pts]
    pygame.draw.polygon(surf, STICKER_FILL, fill_pts)
    pygame.draw.polygon(surf, STICKER_OUTLINE, fill_pts, 4)

    # Highlight strip down the left side
    pygame.draw.line(surf, STICKER_HIGHLIGHT,
                     (cx - top_r + 14, top_y + 30), (cx - top_r + 14, bot_y - 30), 6)

    # Face: two oval eyes + 'o' mouth
    pygame.draw.ellipse(surf, STICKER_DEEP,
                        pygame.Rect(cx - 22, cy - 16, 12, 18))
    pygame.draw.ellipse(surf, STICKER_DEEP,
                        pygame.Rect(cx + 10, cy - 16, 12, 18))
    # Eye highlight pops
    pygame.draw.circle(surf, (255, 255, 255), (cx - 14, cy - 11), 2)
    pygame.draw.circle(surf, (255, 255, 255), (cx + 18, cy - 11), 2)
    # Mouth
    pygame.draw.ellipse(surf, STICKER_DEEP,
                        pygame.Rect(cx - 7, cy + 12, 14, 16))


# ─── ICON 4 — MUSHROOM (speckled toadstool) ─────────────────────────────────

def icon_mushroom(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx, cy - 6, 95, 165)

    # Stem
    stem_rect = pygame.Rect(cx - 18, cy + 6, 36, 60)
    pygame.draw.rect(surf, STICKER_OUTLINE, stem_rect.inflate(4, 4),
                     border_radius=8)
    pygame.draw.rect(surf, STICKER_FILL, stem_rect, border_radius=6)
    pygame.draw.rect(surf, STICKER_HIGHLIGHT,
                     pygame.Rect(cx - 14, cy + 10, 8, 50), border_radius=4)

    # Cap — wide half-dome (drawn as a rotated ellipse via Rect clipping).
    cap_w, cap_h = 150, 90
    cap_top = cy - 50
    cap_rect = pygame.Rect(cx - cap_w // 2, cap_top, cap_w, cap_h)
    # Outline
    outline_layer = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
    pygame.draw.ellipse(outline_layer, STICKER_OUTLINE, cap_rect.inflate(8, 8))
    pygame.draw.ellipse(outline_layer, STICKER_FILL, cap_rect)
    # Crop the bottom half so it reads as a dome
    pygame.draw.rect(outline_layer, (0, 0, 0, 0),
                     pygame.Rect(0, cy + 8, CANVAS, CANVAS))
    surf.blit(outline_layer, (0, 0))

    # Cap base line (curved underside)
    pygame.draw.line(surf, STICKER_OUTLINE,
                     (cx - cap_w // 2, cy + 6), (cx + cap_w // 2, cy + 6), 4)
    # Highlight rim along top of the cap
    hl_rect = cap_rect.inflate(-20, -20)
    hl_rect.y -= 8
    hl_layer = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
    pygame.draw.ellipse(hl_layer, STICKER_HIGHLIGHT, hl_rect)
    pygame.draw.rect(hl_layer, (0, 0, 0, 0),
                     pygame.Rect(0, cy - 12, CANVAS, CANVAS))
    surf.blit(hl_layer, (0, 0))

    # Spots
    for sx, sy, sr in ((cx - 36, cy - 30, 10),
                       (cx + 28, cy - 26, 12),
                       (cx + 50, cy - 8, 7),
                       (cx - 60, cy - 10, 7),
                       (cx + 4,  cy - 36, 8)):
        pygame.draw.circle(surf, STICKER_OUTLINE, (sx, sy), sr + 1)
        pygame.draw.circle(surf, STICKER_DEEP,    (sx, sy), sr)


# ─── ICON 5 — BOLT (lightning) ──────────────────────────────────────────────

def icon_bolt(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx, cy, 95, 175)

    # Classic Z-zigzag bolt — narrow at top, wider in middle, narrow at bottom.
    bolt = [
        (cx - 12, cy - 85),
        (cx + 26, cy - 85),
        (cx + 6,  cy - 18),
        (cx + 36, cy - 18),
        (cx - 10, cy + 85),
        (cx + 6,  cy + 18),
        (cx - 30, cy + 18),
        (cx - 4,  cy - 18),
        (cx - 26, cy - 18),
    ]
    # Outline pad
    pygame.draw.polygon(surf, STICKER_OUTLINE, bolt)
    # Inset fill
    inset = []
    for px, py in bolt:
        dx = 4 if px > cx else -4
        dy = 4 if py > cy else -4
        inset.append((px + dx, py + dy))
    # Just shrink toward centre by 4px for the fill
    inset = [((px + cx) // 2 if False else int(cx + (px - cx) * 0.92),
              int(cy + (py - cy) * 0.92)) for px, py in bolt]
    pygame.draw.polygon(surf, STICKER_FILL, inset)
    pygame.draw.polygon(surf, STICKER_OUTLINE, inset, 3)

    # Bright highlight stripe along the left edge of the bolt
    hl_pts = [
        (cx - 8, cy - 78),
        (cx - 2, cy - 78),
        (cx - 16, cy - 12),
        (cx - 10, cy - 12),
        (cx - 4, cy + 80),
        (cx - 10, cy + 80),
        (cx - 4, cy + 12),
        (cx - 12, cy + 12),
    ]
    pygame.draw.polygon(surf, STICKER_HIGHLIGHT, hl_pts)


# ─── driver ─────────────────────────────────────────────────────────────────

ICONS = [
    ("icon_1_star.png",     icon_star),
    ("icon_2_moon.png",     icon_moon),
    ("icon_3_ghost.png",    icon_ghost),
    ("icon_4_mushroom.png", icon_mushroom),
    ("icon_5_bolt.png",     icon_bolt),
]


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots", "nightglow_icons")
    os.makedirs(out_dir, exist_ok=True)
    # Wipe any previous candidates so the directory only ever shows the
    # current set.
    for fn in os.listdir(out_dir):
        if fn.endswith(".png"):
            os.remove(os.path.join(out_dir, fn))
    for fname, fn in ICONS:
        scene = _dark_backdrop()
        fn(scene)
        out_path = os.path.join(out_dir, fname)
        pygame.image.save(scene, out_path)
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
