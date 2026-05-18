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
    """Silhouette-clean halo. Paint a uniform `color` over the alpha
    mask of `targets`, blur, then PRE-MULTIPLY the RGB by alpha so
    additive blending is gated by silhouette coverage.

    CRITICAL: pygame's BLEND_RGBA_ADD adds source RGB to dest RGB
    UNCONDITIONALLY — source alpha is NOT used to gate the RGB
    contribution. So a silhouette with uniform colour and sparse alpha
    will, under additive blending, paint its colour onto every pixel
    of the destination regardless of alpha. The only way to confine the
    halo to entity neighbourhoods is to bake `RGB *= alpha/255` into
    the silhouette before blitting.

    `scale` = downsample fraction (larger = TIGHTER halo).
    `alpha` = halo strength 0–255."""
    sil = pygame.Surface((W, H), pygame.SRCALPHA)
    sil.fill((*color, 255))
    pygame.surfarray.pixels_alpha(sil)[:] = pygame.surfarray.array_alpha(targets)
    sw, sh = max(2, int(W * scale)), max(2, int(H * scale))
    small = pygame.transform.smoothscale(sil, (sw, sh))
    big = pygame.transform.smoothscale(small, (W, H))
    rgb = pygame.surfarray.pixels3d(big)
    a   = pygame.surfarray.array_alpha(big).astype(np.float32) / 255.0
    factor = a * (alpha / 255.0)
    rgb[:] = np.clip(rgb.astype(np.float32) * factor[..., None],
                     0, 255).astype(np.uint8)
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


# All 5 variants build on V4_PUNCH (user's pick) with two adjustments:
#   (1) drop or dial down the extra_top layer — that's what was making
#       Pip's silhouette too bright (recoloured + extra glow on top
#       saturated entity centres);
#   (2) add a very wide outer halo layer (scale 0.015–0.025) for more
#       spread — that's the "more aura" the user asked for.
# Bright recolour endpoint stays at (220, 255, 230) — the approved colour.


def _green_recolour(targets):
    return luminance_to_palette(targets,
                                dark=(8, 60, 22),
                                bright=(220, 255, 230))


# ─── VARIANT 1 — WIDE GLOW (one wide outer + V4's 3 core layers, dimmed) ────

def variant_wide_glow(backdrop, bodies, targets, refs):
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.025, (30, 170, 25),  160),   # NEW wide outer aura
            (0.05,  (55, 215, 45),  180),
            (0.13,  (85, 240, 70),  190),
            (0.28,  (115, 250, 100),160),
        ),
        recoloured=_green_recolour(targets),
    )


# ─── VARIANT 2 — ATMOSPHERIC (5 layers, gentle wide-to-tight progression) ───

def variant_atmospheric(backdrop, bodies, targets, refs):
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.02,  (25, 160, 20),  150),
            (0.05,  (50, 210, 40),  170),
            (0.10,  (70, 230, 55),  180),
            (0.20,  (100, 245, 85), 165),
            (0.32,  (120, 250, 100),130),
        ),
        recoloured=_green_recolour(targets),
    )


# ─── VARIANT 3 — DOUBLE-WIDE (two outer aura layers + tight inner) ──────────

def variant_double_wide(backdrop, bodies, targets, refs):
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.018, (25, 155, 18),  155),   # ultra-wide outer
            (0.04,  (40, 195, 30),  170),   # mid-wide
            (0.12,  (80, 235, 65),  180),
            (0.25,  (110, 248, 95), 150),
        ),
        recoloured=_green_recolour(targets),
    )


# ─── VARIANT 4 — DEEP AURA (very wide outer, 4 layers, soft) ────────────────

def variant_deep_aura(backdrop, bodies, targets, refs):
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.015, (22, 145, 16),  160),   # extreme wide outer
            (0.05,  (50, 205, 40),  165),
            (0.13,  (85, 235, 70),  175),
            (0.28,  (115, 248, 100),150),
        ),
        recoloured=_green_recolour(targets),
    )


# ─── VARIANT 5 — PUNCH+ (V4 base but with toned-down extra-top + wide outer) ─

def variant_punch_plus(backdrop, bodies, targets, refs):
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.022, (30, 170, 25),  160),   # NEW wide outer for the aura
            (0.05,  (55, 215, 45),  185),
            (0.13,  (90, 240, 75),  195),
            (0.28,  (120, 250, 105),170),
        ),
        recoloured=_green_recolour(targets),
        extra_top=(
            (0.20, (90, 230, 75), 70),       # much lower than V4's 130
        ),
    )


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_wide_glow.png",    variant_wide_glow),
    ("variant_2_atmospheric.png",  variant_atmospheric),
    ("variant_3_double_wide.png",  variant_double_wide),
    ("variant_4_deep_aura.png",    variant_deep_aura),
    ("variant_5_punch_plus.png",   variant_punch_plus),
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
