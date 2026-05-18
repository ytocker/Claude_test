"""Render 5 NIGHTGLOW visual-variant mockups for review.

Iteration 4 — building on V2 INCANDESCENT, with TRUE colour replacement:

The previous iteration tinted via BLEND_RGBA_MULT which only darkens
non-green channels — a red pixel (255,0,0) ended up (70,0,0), still
visibly red. The user wants "no trace of regular colours" (cf. how the
GHOST powerup fully recolours the parrot to a cool-blue spectral
palette).

The fix is a luminance→palette ramp via numpy/surfarray:
    L  = 0.30·R + 0.59·G + 0.11·B          (per-pixel brightness)
    out = lerp(dark_palette, bright_palette, L)
Every source colour is replaced by a green of equivalent brightness,
matching how GHOST replaces every parrot colour by a blue of equivalent
hue role (`game/dollar_parrot_ghost.py:146-177` defines `P_SPECTRAL`).

Numpy is fine here — this tool runs headless on the desktop, not in
the WASM build. For the eventual live-game implementation, the recolour
would be pre-cached once on NIGHTGLOW activation (mirroring
`_ensure_ghost_frames` in `game/parrot.py:700-707`).

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_nightglow_variants.py
"""

import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pygame
import pygame.surfarray

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

pygame.init()
pygame.display.set_mode((1, 1))

from game import biome
from game.config import W, H, PIPE_W, COIN_R, POWERUP_R, GROUND_Y, BIRD_X
from game.draw import draw_mountains, draw_ground
from game.entities import Bird, Coin, PowerUp, Pipe
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


# ─── scene composition (unchanged from iter 3) ──────────────────────────────

def _build_entities():
    pal = biome.palette_for_phase(0.64375)
    pipe_a = Pipe(x=70.0,  gap_y=H * 0.50, gap_h=170.0)
    pipe_b = Pipe(x=240.0, gap_y=H * 0.42, gap_h=160.0)
    overgrown_idx = next(
        (i for i, v in enumerate(_VARIANTS)
         if v[2].__name__ == "decorate_overgrown"),
        0,
    )
    pipe_a.seed = overgrown_idx + VARIANT_COUNT * 7
    pipe_b.seed = overgrown_idx + VARIANT_COUNT * 13
    pipes = [pipe_a, pipe_b]
    coins = [
        Coin(x=160.0, y=H * 0.46),
        Coin(x=205.0, y=H * 0.40),
    ]
    powerup = PowerUp(x=295.0, y=H * 0.32, kind="nightglow")
    bird = Bird()
    bird.x = BIRD_X
    bird.y = H * 0.50
    bird.frame_t = 0.4
    return pipes, coins, powerup, bird, pal


def _night_sky(surf):
    pal = biome.palette_for_phase(0.64375)
    top, mid, bot = pal["sky_top"], pal["sky_mid"], pal["sky_bot"]
    for y in range(H):
        if y < H * 0.45:
            t = y / (H * 0.45)
            c = tuple(int(top[i] + (mid[i] - top[i]) * t) for i in range(3))
        else:
            t = (y - H * 0.45) / (H * 0.55)
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * t) for i in range(3))
        pygame.draw.line(surf, c, (0, y), (W, y))


def _scatter_stars(surf, seed=7):
    import random as _r
    rng = _r.Random(seed)
    for _ in range(45):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, int(H * 0.55))
        pygame.draw.circle(surf, (240, 240, 230), (x, y), 1)


def render_layers():
    pipes, coins, powerup, bird, pal = _build_entities()

    backdrop = pygame.Surface((W, H)).convert()
    _night_sky(backdrop)
    _scatter_stars(backdrop)
    draw_mountains(backdrop, scroll=120.0, ground_y=GROUND_Y, w=W,
                   far_color=(40, 50, 100), near_color=(20, 30, 70))
    draw_ground(backdrop, ground_y=GROUND_Y, w=W, h=H, scroll=120.0,
                top_color=(35, 50, 80),
                mid_color=(20, 30, 55),
                bot_color=(10, 15, 30))

    pillar_bodies = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()
    glow_targets  = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()

    for p in pipes:
        top_sil, bot_sil, decorate = _VARIANTS[p.seed % VARIANT_COUNT]
        _paint_stone(pillar_bodies, p.top_rect, top_sil, pal, p.seed)
        _paint_stone(pillar_bodies, p.bot_rect, bot_sil, pal, p.seed + 1)
        decorate(glow_targets, p.top_rect, p.bot_rect, pal, p.seed)

    for c in coins:
        c.draw(glow_targets)
    powerup.draw(glow_targets)
    bird.draw(glow_targets, 0, 0)

    return backdrop, pillar_bodies, glow_targets, {
        "pipes":   pipes,
        "coins":   coins,
        "powerup": powerup,
        "bird":    bird,
    }


# ─── the new replacement primitive ──────────────────────────────────────────

def luminance_to_palette(surface: pygame.Surface,
                         dark=(8, 60, 20),
                         bright=(220, 255, 230),
                         gamma: float = 1.0) -> pygame.Surface:
    """Return a NEW Surface where every visible pixel is replaced by a
    colour interpolated from `dark` (at luminance 0) through `bright`
    (at luminance 1). `gamma` < 1 brightens, > 1 darkens. Alpha is
    preserved exactly so the silhouette is unchanged.

    This is the standard luminance-ramp colour-swap technique. It fully
    erases the source hue — a red pixel and a blue pixel of the same
    brightness become exactly the same green."""
    src = surface.copy()
    rgb_view = pygame.surfarray.pixels3d(src).astype(np.float32)
    L = (0.30 * rgb_view[..., 0]
       + 0.59 * rgb_view[..., 1]
       + 0.11 * rgb_view[..., 2]) / 255.0
    if gamma != 1.0:
        L = np.power(np.clip(L, 0.0, 1.0), gamma)
    dark_arr   = np.array(dark,   dtype=np.float32)
    bright_arr = np.array(bright, dtype=np.float32)
    out = dark_arr + (bright_arr - dark_arr) * L[..., None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    pygame.surfarray.pixels3d(src)[:] = out
    return src


# ─── shared building blocks (unchanged) ─────────────────────────────────────

def _dark_overlay(surf, alpha, tint=(4, 8, 16)):
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    layer.fill((*tint, alpha))
    surf.blit(layer, (0, 0))


def _halo(targets: pygame.Surface, scale: float, color, alpha: int):
    """Additive halo via multiply-tint of a blurred source. The blur
    spreads the source's alpha smoothly; the tint pushes any warm
    source pixels to near-black so the halo reads as the chosen colour
    when blended additively. Scale = downsample fraction (smaller = wider)."""
    sw, sh = max(2, int(W * scale)), max(2, int(H * scale))
    small = pygame.transform.smoothscale(targets, (sw, sh))
    big = pygame.transform.smoothscale(small, (W, H))
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((*color, 255))
    big.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    big.set_alpha(alpha)
    return big


def _bloom_stack(scene, targets, layers):
    """layers = iterable of (scale, color_rgb, alpha). Additively blitted."""
    for scale, col, alpha in layers:
        scene.blit(_halo(targets, scale, col, alpha),
                   (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _compose(backdrop, bodies, targets, dark_alpha,
             aura_layers, recoloured, extra_top=None):
    """Standard composite: backdrop → dark overlay → pillar bodies →
    coloured halos → recoloured entities (full colour replacement) →
    optional extra-top glows. The recoloured layer guarantees that
    every entity pixel the player looks AT is pure green; any halo
    bleed from the source colours sits BEHIND that layer."""
    scene = backdrop.copy()
    _dark_overlay(scene, dark_alpha)
    scene.blit(bodies, (0, 0))
    _bloom_stack(scene, targets, aura_layers)
    scene.blit(recoloured, (0, 0))
    if extra_top is not None:
        _bloom_stack(scene, targets, extra_top)
    return scene


def _draw_radial_rays(scene, cx, cy, length, count, color,
                      alpha_start, phase=0.0, width=2):
    pad = length + 4
    rays = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    for i in range(count):
        a = (i / count) * math.tau + phase
        for step in range(10, length, 5):
            t = step / length
            alpha = int(alpha_start * (1.0 - t) ** 1.6)
            if alpha <= 0:
                continue
            px = pad + step * math.cos(a)
            py = pad + step * math.sin(a)
            pygame.draw.circle(rays, (*color, alpha),
                               (int(px), int(py)), width)
    scene.blit(rays, (cx - pad, cy - pad),
               special_flags=pygame.BLEND_RGBA_ADD)


# ─── VARIANT 1 — TRUE GLOW (the family reference) ───────────────────────────

def variant_true_glow(backdrop, bodies, targets, refs):
    recol = luminance_to_palette(targets,
                                 dark=(8, 60, 20),
                                 bright=(220, 255, 230))
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.04, (50, 200, 70),   200),
            (0.10, (90, 255, 110),  220),
            (0.22, (130, 255, 160), 200),
        ),
        recoloured=recol,
        extra_top=((0.05, (180, 255, 200), 90),),
    )


# ─── VARIANT 2 — EMBER (hot white cores) ────────────────────────────────────

def variant_ember(backdrop, bodies, targets, refs):
    recol = luminance_to_palette(targets,
                                 dark=(15, 50, 25),
                                 bright=(255, 255, 255),
                                 gamma=0.85)
    scene = _compose(
        backdrop, bodies, targets, dark_alpha=140,
        aura_layers=(
            (0.05, (50, 200, 70),   220),
            (0.13, (90, 255, 120),  220),
            (0.28, (60, 230, 80),   190),
        ),
        recoloured=recol,
    )
    # White-hot ember cores additively on top. The tight inner blur
    # (scale 0.30+) keeps the brightening confined to entity centres.
    for scale, col, a in ((0.30, (200, 255, 220), 100),
                          (0.50, (220, 255, 230),  75)):
        scene.blit(_halo(targets, scale, col, a),
                   (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── VARIANT 3 — DEEP GLOW (moody, atmospheric) ─────────────────────────────

def variant_deep_glow(backdrop, bodies, targets, refs):
    recol = luminance_to_palette(targets,
                                 dark=(5, 40, 15),
                                 bright=(140, 230, 170))
    return _compose(
        backdrop, bodies, targets, dark_alpha=145,
        aura_layers=(
            (0.03, (35, 140, 50),   180),
            (0.06, (55, 190, 75),   200),
            (0.12, (80, 220, 100),  210),
            (0.20, (100, 240, 130), 200),
            (0.32, (130, 255, 160), 180),
        ),
        recoloured=recol,
        extra_top=(
            (0.08, (140, 240, 180),  90),
            (0.18, (170, 255, 210),  70),
        ),
    )


# ─── VARIANT 4 — LANTERN (light beams) ──────────────────────────────────────

def variant_lantern(backdrop, bodies, targets, refs):
    recol = luminance_to_palette(targets,
                                 dark=(10, 70, 25),
                                 bright=(230, 255, 230))
    scene = backdrop.copy()
    _dark_overlay(scene, 135)
    scene.blit(bodies, (0, 0))

    _bloom_stack(scene, targets, (
        (0.05, (50, 200, 70),   220),
        (0.12, (90, 255, 110),  220),
        (0.25, (130, 255, 160), 190),
    ))

    NEON = (140, 255, 170)
    for c in refs["coins"]:
        _draw_radial_rays(scene, int(c.x), int(c.y),
                          length=80, count=12, color=NEON,
                          alpha_start=170, phase=0.4, width=1)
    m = refs["powerup"]
    _draw_radial_rays(scene, int(m.x), int(m.y),
                      length=110, count=14, color=NEON,
                      alpha_start=200, phase=0.0, width=2)
    b = refs["bird"]
    _draw_radial_rays(scene, int(b.x), int(b.y),
                      length=120, count=16, color=NEON,
                      alpha_start=210, phase=0.6, width=2)
    for p in refs["pipes"]:
        cx = int(p.x + PIPE_W / 2)
        cy = int(p.gap_y - p.gap_h / 2 - 20)
        _draw_radial_rays(scene, cx, cy,
                          length=80, count=10, color=NEON,
                          alpha_start=160, phase=math.pi / 8, width=1)

    scene.blit(recol, (0, 0))

    scene.blit(_halo(targets, 0.40, (220, 255, 230), 110),
               (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── VARIANT 5 — AURORA (chromatic ribbon) ──────────────────────────────────

def variant_aurora(backdrop, bodies, targets, refs):
    # Slight cyan tilt at the bright end so highlights shimmer.
    recol = luminance_to_palette(targets,
                                 dark=(10, 80, 40),
                                 bright=(200, 255, 240))
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.04, (40, 200, 100),  200),  # deep green inner
            (0.10, (80, 240, 150),  220),  # mid green
            (0.20, (140, 255, 200), 210),  # mint
            (0.34, (170, 255, 230), 180),  # outer mint-cyan ribbon
        ),
        recoloured=recol,
        extra_top=(
            (0.07, (180, 255, 220), 100),
            (0.20, (200, 255, 240),  75),
        ),
    )


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_true_glow.png",  variant_true_glow),
    ("variant_2_ember.png",      variant_ember),
    ("variant_3_deep_glow.png",  variant_deep_glow),
    ("variant_4_lantern.png",    variant_lantern),
    ("variant_5_aurora.png",     variant_aurora),
]


def main() -> int:
    out_dir = os.path.join(_REPO, "docs", "screenshots", "nightglow_variants")
    os.makedirs(out_dir, exist_ok=True)

    backdrop, bodies, targets, refs = render_layers()
    for fname, fn in VARIANTS:
        frame = fn(backdrop, bodies, targets, refs)
        out_path = os.path.join(out_dir, fname)
        pygame.image.save(frame, out_path)
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
