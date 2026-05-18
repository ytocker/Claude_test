"""Render 5 NIGHTGLOW powerup ICON design candidates.

V5 PUNCH+ was approved as the in-world visual treatment. Now the icon
on the pickup token itself needs to HINT at what the powerup does
("world goes dark, important things glow neon green"). Five distinct
visual metaphors are explored, each drawn at 2× game scale on a dark
night background so the details read clearly:

    1. CRESCENT — moon + sparkles → "night begins"
    2. LANTERN  — light source in dark → "stuff will glow"
    3. ORB      — pure energy sphere → "magical illumination"
    4. EYE      — nocturnal eye → "night vision"
    5. FIREFLY  — bioluminescent bug → "small green glow"

Each PNG is 240×240, a single icon centred so the user can compare
designs side-by-side without external context. The chosen design will
then be ported into entities.py's _draw_nightglow_icon at native scale.

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

# Approved palette from V5_punch_plus.
GREEN_DEEP   = (40, 200, 30)
GREEN_MID    = (90, 240, 70)
GREEN_BRIGHT = (140, 250, 110)
GREEN_GLOW   = (180, 255, 160)
WHITE_HOT    = (230, 255, 220)


def _dark_backdrop() -> pygame.Surface:
    surf = pygame.Surface((CANVAS, CANVAS)).convert()
    # Vertical gradient: night top → slightly lighter night bottom.
    for y in range(CANVAS):
        t = y / CANVAS
        r = int(4 + (12 - 4) * t)
        g = int(8 + (20 - 8) * t)
        b = int(22 + (38 - 22) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (CANVAS, y))
    # Scatter a few stars for context.
    import random as _r
    rng = _r.Random(11)
    for _ in range(18):
        x = rng.randint(0, CANVAS - 1)
        y = rng.randint(0, CANVAS - 1)
        a = rng.randint(140, 220)
        pygame.draw.circle(surf, (220, 220, 200), (x, y), 1)
    return surf


def _add_radial_aura(surf, cx, cy, radius, color, alpha_peak):
    """Smooth additive radial aura at (cx, cy) — the V5 PUNCH+ glow
    signature compressed into a single icon-scale halo."""
    pad = radius + 4
    aura = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        t = r / radius                    # 1.0 outer → ~0 inner
        a = int(alpha_peak * (1.0 - t) ** 1.5)
        if a <= 0:
            continue
        pygame.draw.circle(aura, (*color, a), (pad, pad), r)
    surf.blit(aura, (cx - pad, cy - pad), special_flags=pygame.BLEND_RGBA_ADD)


# ─── ICON 1 — CRESCENT (moon + sparkles) ────────────────────────────────────

def icon_crescent(surf):
    cx, cy = CENTER, CENTER

    # Wide aura
    _add_radial_aura(surf, cx, cy, 80, GREEN_DEEP, 140)
    _add_radial_aura(surf, cx, cy, 60, GREEN_MID, 180)

    # Crescent: filled circle minus a shifted darker circle.
    moon_layer = pygame.Surface((140, 140), pygame.SRCALPHA)
    pygame.draw.circle(moon_layer, GREEN_GLOW, (70, 70), 42)
    pygame.draw.circle(moon_layer, WHITE_HOT, (70, 70), 38)
    pygame.draw.circle(moon_layer, (0, 0, 0, 0), (90, 60), 36)  # bite-out
    surf.blit(moon_layer, (cx - 70, cy - 70))

    # Sparkle stars (4-point flares) scattered around.
    sparkles = ((-58, -42, 5), (52, -50, 4), (60, 40, 6), (-50, 50, 4),
                (-30, -70, 3), (35, 65, 3))
    for sx_o, sy_o, sz in sparkles:
        x, y = cx + sx_o, cy + sy_o
        pygame.draw.line(surf, WHITE_HOT, (x - sz, y), (x + sz, y), 2)
        pygame.draw.line(surf, WHITE_HOT, (x, y - sz), (x, y + sz), 2)
        pygame.draw.circle(surf, WHITE_HOT, (x, y), 1)


# ─── ICON 2 — LANTERN (light source in the dark) ────────────────────────────

def icon_lantern(surf):
    cx, cy = CENTER, CENTER

    # Wide green aura
    _add_radial_aura(surf, cx, cy + 6, 90, GREEN_DEEP, 150)
    _add_radial_aura(surf, cx, cy + 6, 65, GREEN_MID, 180)

    # Top hook + chain
    pygame.draw.arc(surf, (180, 180, 170),
                    pygame.Rect(cx - 10, cy - 78, 20, 14), 0, math.pi, 2)
    pygame.draw.line(surf, (180, 180, 170),
                     (cx, cy - 70), (cx, cy - 50), 2)

    # Lantern frame: rectangle with rounded top + base.
    frame = pygame.Rect(cx - 28, cy - 50, 56, 80)
    pygame.draw.rect(surf, (40, 40, 50), frame.inflate(8, 8), border_radius=6)
    pygame.draw.rect(surf, (90, 90, 100), frame, border_radius=4)

    # Glass panel
    glass = frame.inflate(-10, -16)
    pygame.draw.rect(surf, (15, 35, 22), glass, border_radius=3)

    # Inner glow — bright green flame core
    flame = pygame.Surface((glass.width, glass.height), pygame.SRCALPHA)
    fcx, fcy = glass.width // 2, glass.height // 2 + 4
    for r, col in ((24, GREEN_DEEP),
                   (18, GREEN_MID),
                   (12, GREEN_BRIGHT),
                   (7,  WHITE_HOT)):
        pygame.draw.circle(flame, col, (fcx, fcy), r)
    surf.blit(flame, glass.topleft)

    # Cross-brace silhouette on glass
    pygame.draw.line(surf, (60, 60, 70),
                     (glass.left, glass.centery), (glass.right, glass.centery), 1)
    pygame.draw.line(surf, (60, 60, 70),
                     (glass.centerx, glass.top), (glass.centerx, glass.bottom), 1)


# ─── ICON 3 — ORB (pure energy sphere) ──────────────────────────────────────

def icon_orb(surf):
    cx, cy = CENTER, CENTER

    # Extra wide aura — this icon IS the glow
    _add_radial_aura(surf, cx, cy, 110, GREEN_DEEP, 170)
    _add_radial_aura(surf, cx, cy, 80,  GREEN_MID,  200)
    _add_radial_aura(surf, cx, cy, 55,  GREEN_BRIGHT, 210)

    # Solid core
    pygame.draw.circle(surf, GREEN_BRIGHT, (cx, cy), 32)
    pygame.draw.circle(surf, GREEN_GLOW,   (cx, cy), 24)
    pygame.draw.circle(surf, WHITE_HOT,    (cx, cy), 14)
    pygame.draw.circle(surf, (255, 255, 255), (cx - 5, cy - 5), 5)

    # Two thin orbiting rings (energy field hint)
    ring = pygame.Surface((CANVAS, CANVAS), pygame.SRCALPHA)
    pygame.draw.ellipse(ring, (*GREEN_GLOW, 160),
                        pygame.Rect(cx - 70, cy - 22, 140, 44), 2)
    pygame.draw.ellipse(ring, (*GREEN_GLOW, 130),
                        pygame.Rect(cx - 60, cy - 60, 120, 120), 1)
    surf.blit(ring, (0, 0))


# ─── ICON 4 — EYE (nocturnal night-vision) ──────────────────────────────────

def icon_eye(surf):
    cx, cy = CENTER, CENTER

    # Aura
    _add_radial_aura(surf, cx, cy, 90, GREEN_DEEP, 150)
    _add_radial_aura(surf, cx, cy, 65, GREEN_MID, 175)

    # Almond eye outline — two arcs forming the eye shape.
    eye_w, eye_h = 110, 56
    eye_rect = pygame.Rect(cx - eye_w // 2, cy - eye_h // 2, eye_w, eye_h)
    # Lid (top + bottom arcs)
    pygame.draw.ellipse(surf, WHITE_HOT, eye_rect, 3)
    # White sclera fill
    sclera_layer = pygame.Surface((eye_w, eye_h), pygame.SRCALPHA)
    pygame.draw.ellipse(sclera_layer, (210, 240, 215), sclera_layer.get_rect())
    surf.blit(sclera_layer, eye_rect.topleft)
    # Iris: glowing green disc
    pygame.draw.circle(surf, GREEN_DEEP, (cx, cy), 24)
    pygame.draw.circle(surf, GREEN_MID, (cx, cy), 20)
    pygame.draw.circle(surf, GREEN_BRIGHT, (cx, cy), 14)
    # Slit pupil (vertical, cat-like)
    pygame.draw.ellipse(surf, (10, 30, 15),
                        pygame.Rect(cx - 3, cy - 14, 6, 28))
    # Iris highlight
    pygame.draw.circle(surf, WHITE_HOT, (cx - 6, cy - 6), 4)
    # Eyelash hints
    for dx in (-44, -28, 28, 44):
        pygame.draw.line(surf, WHITE_HOT,
                         (cx + dx, cy - eye_h // 2 - 2),
                         (cx + dx + (1 if dx > 0 else -1), cy - eye_h // 2 - 9),
                         2)


# ─── ICON 5 — FIREFLY (bioluminescent bug) ──────────────────────────────────

def icon_firefly(surf):
    # Diagonal motion — bug in mid-flight, glowing rear trailing back.
    cx, cy = CENTER, CENTER

    # Trail of light particles (behind / lower-left)
    trail = ((-70, 50, 14, 60),
             (-55, 38, 18, 90),
             (-40, 25, 22, 130),
             (-22, 12, 26, 170))
    for dx, dy, r, a in trail:
        _add_radial_aura(surf, cx + dx, cy + dy, r, GREEN_MID, a)

    # Wide bright aura at firefly body
    _add_radial_aura(surf, cx, cy, 95, GREEN_DEEP, 170)
    _add_radial_aura(surf, cx, cy, 60, GREEN_MID, 200)

    # Body — small dark beetle shape
    pygame.draw.ellipse(surf, (35, 50, 30),
                        pygame.Rect(cx - 18, cy - 12, 38, 24))
    pygame.draw.ellipse(surf, (60, 80, 50),
                        pygame.Rect(cx - 16, cy - 11, 28, 20))
    # Wing split line
    pygame.draw.line(surf, (25, 35, 22),
                     (cx, cy - 11), (cx, cy + 11), 1)
    # Head
    pygame.draw.circle(surf, (45, 60, 40), (cx - 18, cy), 6)
    # Antennae
    pygame.draw.line(surf, (45, 60, 40), (cx - 22, cy - 3), (cx - 30, cy - 14), 1)
    pygame.draw.line(surf, (45, 60, 40), (cx - 22, cy + 3), (cx - 30, cy + 14), 1)
    # Tiny eye dots
    pygame.draw.circle(surf, WHITE_HOT, (cx - 21, cy - 1), 1)

    # Glowing tail — the signature firefly lantern.
    tail_cx = cx + 20
    pygame.draw.circle(surf, GREEN_BRIGHT, (tail_cx, cy), 12)
    pygame.draw.circle(surf, GREEN_GLOW,   (tail_cx, cy), 9)
    pygame.draw.circle(surf, WHITE_HOT,    (tail_cx, cy), 5)
    pygame.draw.circle(surf, (255, 255, 255), (tail_cx, cy), 2)


# ─── driver ─────────────────────────────────────────────────────────────────

ICONS = [
    ("icon_1_crescent.png", icon_crescent),
    ("icon_2_lantern.png",  icon_lantern),
    ("icon_3_orb.png",      icon_orb),
    ("icon_4_eye.png",      icon_eye),
    ("icon_5_firefly.png",  icon_firefly),
]


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots", "nightglow_icons")
    os.makedirs(out_dir, exist_ok=True)
    for fname, fn in ICONS:
        scene = _dark_backdrop()
        fn(scene)
        out_path = os.path.join(out_dir, fname)
        pygame.image.save(scene, out_path)
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
