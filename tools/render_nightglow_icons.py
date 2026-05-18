"""Render 5 GLOW-IN-THE-DARK STAR sticker candidates for NIGHTGLOW.

User confirmed STAR (icon 1) is the right concept but the execution
needs to feel like an actual phosphor vinyl sticker — not a flat
cartoon shape with a thick outline. Reference: IKEA / Universe-brand
ceiling glow-stars in a dark room. They have:

  • A pale lime-pistachio fill (strontium-aluminate phosphor, roughly
    (200, 250, 130) — yellower than pure neon green).
  • NO hard outline. The shape edge softens into the surrounding glow.
  • A strong ambient halo around them ("re-emission" of stored light).
  • Often a faint glossy highlight from the vinyl top surface.

Five star treatments to pick from, all on the same dark backdrop:

    1. CLASSIC — soft-edged 5-point, even halo, the canonical take.
    2. GLOSSY  — same star + a slim plastic-vinyl gloss highlight.
    3. CHUNKY  — rounded points, fatter body (older sticker style).
    4. SHARP   — long pointy 5-point, dramatic spikes.
    5. SHEET   — main star + two tiny companion stars (sticker-sheet
                  layout — gives the icon a sense of "set of stars").

The chosen one gets ported into entities.py's _draw_nightglow_icon at
~52 px native scale.

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

# Strontium-aluminate phosphor green — slightly yellow-leaning, the
# colour real GITD stickers actually emit. NOT pure neon green.
PHOSPHOR_CORE  = (215, 252, 145)   # solid sticker fill
PHOSPHOR_RIM   = (170, 235, 110)   # slightly darker rim for soft edge
PHOSPHOR_HOT   = (245, 255, 215)   # vinyl gloss highlight
HALO_DEEP      = (90, 200, 50)
HALO_MID       = (140, 240, 100)
HALO_BRIGHT    = (190, 255, 150)


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


def _star_points(cx, cy, r_outer, r_inner, n=5, rot=-math.pi / 2):
    """N-point star polygon."""
    pts = []
    for i in range(n * 2):
        a = rot + i * math.pi / n
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _aa_star(cx, cy, r_outer, r_inner, color):
    """Render an anti-aliased star: draw it at 4× on a transparent
    surface, then smoothscale down. Result has soft edges that look
    like a real die-cut sticker, not jaggy pixel polygons."""
    SS = 4
    big_size = (r_outer * 2 + 8) * SS
    s = pygame.Surface((big_size, big_size), pygame.SRCALPHA)
    bcx = big_size // 2
    pts = _star_points(bcx, bcx, r_outer * SS, r_inner * SS)
    pygame.draw.polygon(s, color, pts)
    out_size = big_size // SS
    out = pygame.transform.smoothscale(s, (out_size, out_size))
    return out, (cx - out_size // 2, cy - out_size // 2)


def _ambient_halo(surf, cx, cy, radius, alpha_peak, color=HALO_MID):
    """Soft additive radial halo — the 'phosphor glow' signature."""
    pad = radius + 4
    aura = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -2):
        t = r / radius
        a = int(alpha_peak * (1.0 - t) ** 1.6)
        if a <= 0:
            continue
        pygame.draw.circle(aura, (*color, a), (pad, pad), r)
    surf.blit(aura, (cx - pad, cy - pad),
              special_flags=pygame.BLEND_RGBA_ADD)


# ─── VARIANT 1 — CLASSIC ────────────────────────────────────────────────────

def variant_classic(surf):
    cx, cy = CENTER, CENTER
    # Layered halos — wide soft + tight bright = phosphor glow.
    _ambient_halo(surf, cx, cy, 105, 130, HALO_DEEP)
    _ambient_halo(surf, cx, cy, 80,  170, HALO_MID)
    _ambient_halo(surf, cx, cy, 50,  140, HALO_BRIGHT)

    # Soft-edged star body
    star_img, pos = _aa_star(cx, cy, r_outer=70, r_inner=29, color=PHOSPHOR_CORE)
    surf.blit(star_img, pos)
    # Subtle inner rim (slightly darker) — sticker depth without an outline
    inner, ipos = _aa_star(cx, cy, r_outer=66, r_inner=27, color=PHOSPHOR_CORE)
    surf.blit(inner, ipos)


# ─── VARIANT 2 — GLOSSY (vinyl finish highlight) ────────────────────────────

def variant_glossy(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx, cy, 105, 130, HALO_DEEP)
    _ambient_halo(surf, cx, cy, 80,  170, HALO_MID)
    _ambient_halo(surf, cx, cy, 50,  140, HALO_BRIGHT)

    star_img, pos = _aa_star(cx, cy, r_outer=70, r_inner=29, color=PHOSPHOR_CORE)
    surf.blit(star_img, pos)

    # Glossy vinyl sheen: a small bright elliptical highlight blip in
    # the upper-left lobe of the star where light would catch on a
    # plastic surface. Drawn directly on top of the star body — sized
    # so it sits inside the silhouette without any masking gymnastics.
    gloss_layer = pygame.Surface((60, 28), pygame.SRCALPHA)
    pygame.draw.ellipse(gloss_layer, (*PHOSPHOR_HOT, 200),
                        gloss_layer.get_rect())
    # Smooth the edge by re-blitting at slight offsets in lower alpha
    soft = pygame.Surface((60, 28), pygame.SRCALPHA)
    pygame.draw.ellipse(soft, (*PHOSPHOR_HOT, 90),
                        soft.get_rect().inflate(8, 4))
    surf.blit(soft, (cx - 38, cy - 36),
              special_flags=pygame.BLEND_RGBA_ADD)
    surf.blit(gloss_layer, (cx - 30, cy - 32))

    # Tiny sparkle pop at the upper-right corner of the star — sells the
    # "shiny vinyl" read further.
    pygame.draw.circle(surf, (255, 255, 255), (cx + 26, cy - 24), 2)


# ─── VARIANT 3 — CHUNKY (rounded points, fatter body) ───────────────────────

def variant_chunky(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx, cy, 110, 140, HALO_DEEP)
    _ambient_halo(surf, cx, cy, 85,  180, HALO_MID)
    _ambient_halo(surf, cx, cy, 55,  150, HALO_BRIGHT)

    # Chunkier: inner radius bumped up so points are stubbier.
    star_img, pos = _aa_star(cx, cy, r_outer=72, r_inner=42, color=PHOSPHOR_CORE)
    surf.blit(star_img, pos)

    # Round each tip by drawing a small circle there.
    for i in range(5):
        a = -math.pi / 2 + i * math.tau / 5
        tx = cx + 72 * math.cos(a)
        ty = cy + 72 * math.sin(a)
        pygame.draw.circle(surf, PHOSPHOR_CORE, (int(tx), int(ty)), 7)


# ─── VARIANT 4 — SHARP (long dramatic points) ───────────────────────────────

def variant_sharp(surf):
    cx, cy = CENTER, CENTER
    _ambient_halo(surf, cx, cy, 110, 130, HALO_DEEP)
    _ambient_halo(surf, cx, cy, 80,  170, HALO_MID)
    _ambient_halo(surf, cx, cy, 50,  140, HALO_BRIGHT)

    # Sharper: smaller inner radius gives long pointy spikes.
    star_img, pos = _aa_star(cx, cy, r_outer=82, r_inner=22, color=PHOSPHOR_CORE)
    surf.blit(star_img, pos)


# ─── VARIANT 5 — SHEET (main star + 2 companions, sticker-sheet layout) ─────

def variant_sheet(surf):
    cx, cy = CENTER, CENTER

    # Main star
    _ambient_halo(surf, cx, cy, 100, 130, HALO_DEEP)
    _ambient_halo(surf, cx, cy, 75,  170, HALO_MID)
    main, mpos = _aa_star(cx, cy, r_outer=58, r_inner=24, color=PHOSPHOR_CORE)
    surf.blit(main, mpos)

    # Companion 1 — upper right
    _ambient_halo(surf, cx + 70, cy - 65, 38, 130, HALO_MID)
    c1, c1pos = _aa_star(cx + 70, cy - 65, r_outer=24, r_inner=10,
                          color=PHOSPHOR_CORE)
    surf.blit(c1, c1pos)

    # Companion 2 — lower left
    _ambient_halo(surf, cx - 70, cy + 55, 32, 130, HALO_MID)
    c2, c2pos = _aa_star(cx - 70, cy + 55, r_outer=18, r_inner=8,
                          color=PHOSPHOR_CORE)
    surf.blit(c2, c2pos)


# ─── driver ─────────────────────────────────────────────────────────────────

ICONS = [
    ("icon_1_classic.png", variant_classic),
    ("icon_2_glossy.png",  variant_glossy),
    ("icon_3_chunky.png",  variant_chunky),
    ("icon_4_sharp.png",   variant_sharp),
    ("icon_5_sheet.png",   variant_sheet),
]


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots", "nightglow_icons")
    os.makedirs(out_dir, exist_ok=True)
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
