"""Render 5 SHRINK-pickup visual-FX mockups for review.

Five distinct treatments of "the moment Pip touches the blue mushroom",
each a single static frame composed on the same base scene:

  variant_1_vacuum_implode   — particles spiral INWARD to Pip (the opposite
                                of the standard _pickup_burst outward fan)
  variant_2_drink_me_bubble  — Pip caged in an iridescent soap-bubble that's
                                squeezing him down (Alice / drink-me potion)
  variant_3_squash_ghosts    — a stack of after-images at descending scales
                                shows the squish in a single Mario-style frame
  variant_4_iris_rings       — concentric cyan rings collapse from screen
                                edges inward, like an iris-wipe vignette
  variant_5_stardust_pool    — a luminous cyan puddle pools under Pip and
                                sends starflakes drifting upward (potion VFX)

All five render against the same base scene (daytime sky + 2 sandstone
pillars + 2 coins + Pip at SHRINK_SCALE) so the only thing that changes
between variants is the activation FX layer. Run headless:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_shrink_pickup_variants.py

Outputs land in docs/shrink_pickup_variants/.
"""

import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game import biome
from game.config import (
    W, H, GROUND_Y, BIRD_X, BIRD_R, SHRINK_SCALE, POWERUP_R,
)
from game.draw import draw_mountains, draw_ground
from game.entities import Bird, Coin, Pipe, FloatText
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


# ── Palette + colours ───────────────────────────────────────────────────────

SHRINK_HI    = ( 80, 180, 240)
SHRINK_OUT   = ( 30,  90, 160)
SHRINK_LIGHT = (170, 220, 250)
SHRINK_WHITE = (235, 245, 255)
SHRINK_DEEP  = ( 12,  40,  90)

OUT_DIR = os.path.join(_REPO, "docs", "shrink_pickup_variants")


# ── Base scene (identical across all 5) ─────────────────────────────────────

def _build_base():
    """Compose the daytime backdrop + 2 pillars + 2 coins. The base scene
    is intentionally identical for every variant so reviewers can A/B the
    FX layer in isolation."""
    pal = biome.palette_for_phase(0.05)        # bright day, before golden hour
    backdrop = pygame.Surface((W, H)).convert()
    top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
    for y in range(H):
        if y < H * 0.45:
            t = y / (H * 0.45)
            c = tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3))
        else:
            t = (y - H * 0.45) / (H * 0.55)
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * t) for i in range(3))
        pygame.draw.line(backdrop, c, (0, y), (W, y))
    draw_mountains(backdrop, scroll=120.0, ground_y=GROUND_Y, w=W)
    draw_ground(backdrop, ground_y=GROUND_Y, w=W, h=H, scroll=120.0)

    # Two pillars framing the bird, picking pleasant variants.
    pipe_a = Pipe(x=180.0, gap_y=H * 0.48, gap_h=170.0)
    pipe_b = Pipe(x=320.0, gap_y=H * 0.40, gap_h=160.0)
    pipe_a.seed = 7 * VARIANT_COUNT + 2
    pipe_b.seed = 11 * VARIANT_COUNT + 4
    for p in (pipe_a, pipe_b):
        top_sil, bot_sil, decorate = _VARIANTS[p.seed % VARIANT_COUNT]
        _paint_stone(backdrop, p.top_rect, top_sil, pal, p.seed)
        _paint_stone(backdrop, p.bot_rect, bot_sil, pal, p.seed + 1)
        decorate(backdrop, p.top_rect, p.bot_rect, pal, p.seed)

    # A couple of coins ahead so the scene reads as live gameplay.
    Coin(x=240.0, y=H * 0.46).draw(backdrop)
    Coin(x=280.0, y=H * 0.42).draw(backdrop)
    return backdrop


def _draw_shrunk_bird(surf, cx, cy):
    """Pip already at SHRINK_SCALE — the pickup just landed."""
    bird = Bird()
    bird.x, bird.y = cx, cy
    bird.frame_t = 0.4
    bird.shrink_active = True
    bird.draw(surf)


def _bird_pos():
    return BIRD_X, int(H * 0.50)


# ── FloatText overlay shared by all variants ────────────────────────────────

def _stamp_label(surf, cx, cy):
    """Mimic the in-game 'SHRINK!' FloatText label at peak life (t≈0.5)."""
    ft = FloatText("SHRINK!", cx, cy - 30, SHRINK_HI,
                   size=30, life=1.3, vy=-30, style="powerup")
    ft.life = 0.95            # fully visible, no fade-in / fade-out
    ft.draw(surf)


# ── VARIANT 1 ── VACUUM IMPLODE ────────────────────────────────────────────
#
# Particles spiral INWARD toward the bird — the inversion of the standard
# _pickup_burst outward fan. Tail-trails behind each mote suggest the
# convergence is fast and just about to land. Inspired by the
# miniaturisation VFX in the Streets-of-Rogue shrink-ray and the
# Wonderland drink-me iconography (sparkles funnelling toward the drinker).

def variant_vacuum_implode(base):
    scene = base.copy()
    cx, cy = _bird_pos()
    rng = random.Random(1)

    # Faint inward radial gradient (darker at rim, light at centre) so the
    # camera reads as "focusing in" on Pip.
    iris = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(220, 40, -8):
        a = int(8 + (220 - r) * 0.5)
        pygame.draw.circle(iris, (*SHRINK_DEEP, min(110, a)), (cx, cy), r, 6)
    scene.blit(iris, (0, 0))

    # Implosion motes — 70 sparkles on inward trajectories at varying
    # distances-from-centre and offsets-along-tail.
    for i in range(70):
        ang  = rng.uniform(0, math.tau)
        dist = rng.uniform(28, 150)
        x = cx + math.cos(ang) * dist
        y = cy + math.sin(ang) * dist
        tail_len = rng.uniform(10, 26)
        # Trail = a faint line opposite the centre direction.
        ex = x + math.cos(ang) * tail_len
        ey = y + math.sin(ang) * tail_len
        col = rng.choice((SHRINK_HI, SHRINK_LIGHT, SHRINK_WHITE))
        pygame.draw.line(scene, (*col, 200), (ex, ey), (x, y), 2)
        # Bright head sparkle.
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(s, (*col, 230), (5, 5), 3)
        scene.blit(s, (int(x - 5), int(y - 5)),
                   special_flags=pygame.BLEND_RGBA_ADD)

    # Bright cyan core where the implosion is converging.
    core = pygame.Surface((W, H), pygame.SRCALPHA)
    for r, a in ((34, 60), (22, 110), (12, 180)):
        pygame.draw.circle(core, (*SHRINK_LIGHT, a), (cx, cy), r)
    scene.blit(core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    _draw_shrunk_bird(scene, cx, cy)
    _stamp_label(scene, cx, cy)
    return scene


# ── VARIANT 2 ── DRINK ME BUBBLE ───────────────────────────────────────────
#
# Pip is caged in an iridescent translucent soap-bubble that's pressing in
# on him. The bubble has a faint cyan tint, a pearlescent rim highlight,
# and a few tiny sparkle motes glinting on its surface. Reads like the
# Wonderland drink-me potion taking effect — slow, magical, contained
# (vs. variant 1's energetic implosion).

def variant_drink_me_bubble(base):
    scene = base.copy()
    cx, cy = _bird_pos()
    rng = random.Random(2)
    R = 36                                       # bubble radius
    # Outer soft halo first so the bubble feels luminous from inside.
    halo = pygame.Surface((W, H), pygame.SRCALPHA)
    for r, a in ((R + 20, 18), (R + 12, 32), (R + 4, 48)):
        pygame.draw.circle(halo, (*SHRINK_LIGHT, a), (cx, cy), r)
    scene.blit(halo, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Bird inside the bubble — drawn BEFORE the bubble fill so the bubble
    # tints + glazes him.
    _draw_shrunk_bird(scene, cx, cy)

    # Bubble translucent fill (cool cyan wash).
    bub = pygame.Surface((R * 2 + 4, R * 2 + 4), pygame.SRCALPHA)
    pygame.draw.circle(bub, (*SHRINK_LIGHT, 70), (R + 2, R + 2), R)
    scene.blit(bub, (cx - R - 2, cy - R - 2))

    # Iridescent rim — three nested arcs in shifting hues.
    rim_palette = (
        (SHRINK_WHITE, 0,   math.pi * 0.55),     # top-left highlight
        ((200, 230, 255), math.pi * 0.45, math.pi * 1.15),
        ((180, 220, 255), math.pi * 1.05, math.pi * 1.85),
        (SHRINK_HI, math.pi * 1.75, math.pi * 2.35),
        ((140, 200, 240), math.pi * 2.25, math.pi * 2.95),
    )
    for col, a0, a1 in rim_palette:
        rect = pygame.Rect(cx - R, cy - R, R * 2, R * 2)
        pygame.draw.arc(scene, col, rect, a0, a1, 3)
    pygame.draw.circle(scene, SHRINK_OUT, (cx, cy), R, 1)

    # Specular kiss on the top-left of the bubble.
    spec = pygame.Surface((20, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(spec, (255, 255, 255, 220), spec.get_rect())
    scene.blit(spec, (cx - R + 6, cy - R + 4))
    spec2 = pygame.Surface((8, 6), pygame.SRCALPHA)
    pygame.draw.ellipse(spec2, (255, 255, 255, 180), spec2.get_rect())
    scene.blit(spec2, (cx + R - 18, cy + R - 14))

    # Tiny glint motes drifting OFF the bubble surface as it forms.
    for _ in range(14):
        ang  = rng.uniform(0, math.tau)
        dist = R + rng.uniform(4, 28)
        x = cx + math.cos(ang) * dist
        y = cy + math.sin(ang) * dist
        col = rng.choice((SHRINK_WHITE, SHRINK_LIGHT))
        pygame.draw.circle(scene, col, (int(x), int(y)), 2)

    _stamp_label(scene, cx, cy)
    return scene


# ── VARIANT 3 ── SQUASH GHOSTS ─────────────────────────────────────────────
#
# Five after-images of Pip at descending scales stacked at the same
# screen position, fading from translucent → opaque on the smallest copy.
# A puff of dust at Pip's feet sells the squash impact. References
# Mario's smoke-flash transformation and classic animation squash-and-
# stretch principles. Reads in a single still frame.

def variant_squash_ghosts(base):
    scene = base.copy()
    cx, cy = _bird_pos()
    bird = Bird()
    bird.x, bird.y = cx, cy
    bird.frame_t = 0.4

    # Five frames: 1.00 → 0.60 (= SHRINK_SCALE). Earlier scales are
    # painted with progressively lower alpha so the eye lands on the
    # smallest "current" Pip.
    from game import parrot
    frame_idx = int(bird.frame_t) % len(parrot.FRAMES)
    tilt = bird.tilt_deg
    base_img = parrot.get_parrot(frame_idx, tilt)
    bw, bh = base_img.get_size()
    stages = [
        (1.00,  70),
        (0.90, 100),
        (0.80, 140),
        (0.70, 180),
        (SHRINK_SCALE, 255),
    ]
    for scale, alpha in stages:
        w, h = max(1, int(bw * scale)), max(1, int(bh * scale))
        img = pygame.transform.smoothscale(base_img, (w, h))
        img = img.copy()
        img.set_alpha(alpha)
        scene.blit(img, (int(cx - w / 2), int(cy - h / 2)))

    # Compression bands — three short horizontal cyan streaks above and
    # below Pip, suggesting the squish-arrows in a comic-book panel.
    for sign in (-1, +1):
        for k, dx in enumerate((-18, 0, 18)):
            y = cy + sign * (18 + k * 0)
            x = cx + dx
            col = (*SHRINK_HI, 220)
            tri = [(x - 5, y - sign * 3),
                   (x + 5, y - sign * 3),
                   (x,     y + sign * 3)]
            pygame.draw.polygon(scene, col, tri)

    # Dust puff at Pip's "feet": three light cyan ellipses with a couple
    # of small motes flying out.
    for r, dx, dy, a in ((10, -12, 18, 180),
                         (13,   2, 22, 200),
                         (9,   14, 18, 170)):
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*SHRINK_WHITE, a), (r + 1, r + 1), r)
        scene.blit(s, (cx + dx - r - 1, cy + dy - r - 1))
    for dx in (-22, -16, 18, 24):
        pygame.draw.circle(scene, SHRINK_LIGHT,
                           (cx + dx, cy + 20 + (dx % 5)), 2)

    _stamp_label(scene, cx, cy)
    return scene


# ── VARIANT 4 ── IRIS RINGS ────────────────────────────────────────────────
#
# Concentric cyan rings closing in on Pip — like an iris-wipe vignette
# zeroing in on the now-smaller hero. Each ring is at a different radius
# / alpha / line-width so the cascade reads as motion-frozen. Inspired
# by the iris-shrink transitions in old cartoons and the iris-wipe
# blender example. Pillars stay visible behind the rings so the player
# still has spatial context.

def variant_iris_rings(base):
    scene = base.copy()
    cx, cy = _bird_pos()

    # Subtle dark vignette tightens reader focus toward the rings.
    vig = pygame.Surface((W, H), pygame.SRCALPHA)
    for r in range(max(W, H), 200, -10):
        a = max(0, int((r - 200) * 0.08))
        pygame.draw.circle(vig, (0, 0, 0, min(20, a)), (cx, cy), r, 12)
    scene.blit(vig, (0, 0))

    # Six rings at descending radius. Inner rings stay bright + thick;
    # outer rings get thinner + fainter to read as motion blur.
    ring_specs = (
        (220, 1, 60),
        (180, 2, 90),
        (140, 2, 130),
        (100, 3, 180),
        ( 64, 4, 220),
        ( 36, 5, 255),
    )
    for r, w, a in ring_specs:
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.circle(s, (*SHRINK_HI, a), (cx, cy), r, w)
        scene.blit(s, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Spoke streaks at the cardinals + diagonals: short cyan dashes
    # pointing inward, suggesting the rings are still collapsing.
    for k in range(12):
        ang = k * math.tau / 12
        x0 = cx + math.cos(ang) * 75
        y0 = cy + math.sin(ang) * 75
        x1 = cx + math.cos(ang) * 110
        y1 = cy + math.sin(ang) * 110
        pygame.draw.line(scene, SHRINK_LIGHT, (x0, y0), (x1, y1), 2)

    # Tight bright core under the bird.
    core = pygame.Surface((W, H), pygame.SRCALPHA)
    for r, a in ((28, 100), (18, 160), (10, 230)):
        pygame.draw.circle(core, (*SHRINK_WHITE, a), (cx, cy), r)
    scene.blit(core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    _draw_shrunk_bird(scene, cx, cy)
    _stamp_label(scene, cx, cy)
    return scene


# ── VARIANT 5 ── STARDUST POOL ─────────────────────────────────────────────
#
# A small luminous cyan puddle under Pip, with starflakes drifting
# upward. Whimsical, potion-like — Pip is wading in the very magic that
# just shrank him. Inspired by Alice-in-Wonderland drink-me potion VFX
# and the Mini-Mushroom puff in Mario.

def variant_stardust_pool(base):
    scene = base.copy()
    cx, cy = _bird_pos()
    rng = random.Random(5)

    # Cyan puddle: 3 stacked ellipses at descending alpha for the
    # liquid-surface feel.
    for w, h, a in ((90, 18, 80),
                    (74, 14, 130),
                    (60, 10, 200)):
        s = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*SHRINK_HI, a),
                            pygame.Rect(2, 2, w, h))
        scene.blit(s, (cx - w // 2 - 2, cy + 16 - h // 2),
                   special_flags=pygame.BLEND_RGBA_ADD)
    # Brighter pearl rim on the puddle's near edge.
    pygame.draw.arc(scene, SHRINK_WHITE,
                    pygame.Rect(cx - 30, cy + 12, 60, 10),
                    math.pi * 0.05, math.pi * 0.95, 2)

    _draw_shrunk_bird(scene, cx, cy)

    # Starflakes drifting up from the puddle.
    def _star(surf, x, y, r, col, alpha=230):
        s = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.line(s, (*col, alpha),
                         (r + 2, 1),        (r + 2, r * 2 + 3), 2)
        pygame.draw.line(s, (*col, alpha),
                         (1, r + 2),        (r * 2 + 3, r + 2), 2)
        pygame.draw.line(s, (*col, alpha // 2),
                         (3, 3),            (r * 2 + 1, r * 2 + 1), 1)
        pygame.draw.line(s, (*col, alpha // 2),
                         (r * 2 + 1, 3),    (3, r * 2 + 1), 1)
        surf.blit(s, (int(x - r - 2), int(y - r - 2)),
                  special_flags=pygame.BLEND_RGBA_ADD)

    # Lots of small flakes drifting up + a few large featured ones.
    for _ in range(22):
        x = cx + rng.uniform(-30, 30)
        y = cy + 18 - rng.uniform(0, 70)
        r = rng.choice((2, 3, 3, 4))
        col = rng.choice((SHRINK_LIGHT, SHRINK_WHITE, SHRINK_HI))
        _star(scene, x, y, r, col,
              alpha=int(120 + (1 - (cy + 18 - y) / 70) * 130))
    # Three centrepiece sparkles framing Pip.
    _star(scene, cx - 14, cy - 12, 5, SHRINK_WHITE)
    _star(scene, cx + 18, cy +  2, 5, SHRINK_WHITE)
    _star(scene, cx + 2,  cy - 28, 4, SHRINK_LIGHT)

    # Ribbon-trail: a soft cyan curl wrapping Pip's silhouette.
    for k in range(40):
        t = k / 40
        ang = math.pi * 0.6 + t * math.tau * 1.2
        rad = 24 + 10 * math.sin(t * math.tau * 2)
        x = cx + math.cos(ang) * rad
        y = cy + math.sin(ang) * rad * 0.65
        r = 2 if k % 5 else 3
        a = int(120 + 80 * math.sin(t * math.pi))
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*SHRINK_LIGHT, a), (r + 1, r + 1), r)
        scene.blit(s, (int(x - r - 1), int(y - r - 1)),
                   special_flags=pygame.BLEND_RGBA_ADD)

    _stamp_label(scene, cx, cy)
    return scene


# ── Driver ─────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    base = _build_base()
    variants = (
        ("variant_1_vacuum_implode",  variant_vacuum_implode),
        ("variant_2_drink_me_bubble", variant_drink_me_bubble),
        ("variant_3_squash_ghosts",   variant_squash_ghosts),
        ("variant_4_iris_rings",      variant_iris_rings),
        ("variant_5_stardust_pool",   variant_stardust_pool),
    )
    for name, fn in variants:
        out = fn(base)
        path = os.path.join(OUT_DIR, name + ".png")
        pygame.image.save(out, path)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
