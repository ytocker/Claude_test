"""Render 5 NIGHTGLOW visual-variant mockups for review.

Iteration 3 — building on Variant 3 (BLOOM) from the previous pass:

  • The neon-green effect is now more DOMINANT — the tint actually
    overrides the original hue, not just nudges it.
  • Auras are MUCH wider/brighter.
  • The effect is applied ONLY to Pip + coins + powerups + the pillar
    VEGETATION (foliage on top). Pillar STONE BODIES stay in their
    natural moonlit-sandstone colour so the world still feels grounded.

To isolate vegetation from stone we render pipes in two passes by
calling `_paint_stone` (body) and the variant's `decorate` callable
(vegetation) onto separate Surfaces — see `_VARIANTS` in
`game/pillar_variants.py`.

Run headless:
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
        python tools/render_nightglow_variants.py
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

from game import biome
from game.config import W, H, PIPE_W, COIN_R, POWERUP_R, GROUND_Y, BIRD_X
from game.draw import draw_mountains, draw_ground
from game.entities import Bird, Coin, PowerUp, Pipe
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


# ─── scene composition ──────────────────────────────────────────────────────

def _build_entities():
    pal = biome.palette_for_phase(0.64375)
    # Force a vegetation-rich variant on both pipes so the screenshot reliably
    # shows the body/vegetation split.
    pipe_a = Pipe(x=70.0,  gap_y=H * 0.50, gap_h=170.0)
    pipe_b = Pipe(x=240.0, gap_y=H * 0.42, gap_h=160.0)
    # Pin to "overgrown" variant idx if present so foliage is generous.
    overgrown_idx = next(
        (i for i, v in enumerate(_VARIANTS)
         if v[2].__name__ == "decorate_overgrown"),
        0,
    )
    pipe_a.seed = overgrown_idx + VARIANT_COUNT * 7        # stays at overgrown
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
    """Return four layers + refs:

        backdrop       — sky + mountains + ground.
        pillar_bodies  — stone columns only (NO vegetation). Unaffected
                         by the night-glow treatment; sits on top of
                         the darkened backdrop.
        glow_targets   — vegetation + coins + powerup + Pip — the
                         elements that get tinted/auraed.
        empty (unused) — kept for clarity, callers ignore.
    """
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

    # Pillars: paint stone onto pillar_bodies, paint decorate (vegetation +
    # ornaments) onto glow_targets.
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


# ─── shared building blocks ─────────────────────────────────────────────────

def _dark_overlay(surf, alpha, tint=(4, 8, 16)):
    layer = pygame.Surface((W, H), pygame.SRCALPHA)
    layer.fill((*tint, alpha))
    surf.blit(layer, (0, 0))


def _dominant_green(targets, tint_mid=(70, 255, 100),
                    overlay_color=(50, 200, 70),
                    overlay_alpha=140):
    """Strong override: multiply pushes hue toward green; then a coloured
    overlay (alpha-blended) pushes texture further into green-only.
    Returns a NEW surface — the input is not mutated."""
    out = targets.copy()
    mul = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    mul.fill((*tint_mid, 255))
    out.blit(mul, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # Re-stamp the alpha so the overlay is gated by the silhouette.
    overlay = pygame.Surface(out.get_size(), pygame.SRCALPHA)
    overlay.fill((*overlay_color, overlay_alpha))
    overlay.blit(targets, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    out.blit(overlay, (0, 0))
    return out


def _blur(surface, scale, color=None):
    """Cheap downsample-upsample blur. If color is given, multiply into it."""
    sw = max(2, int(W * scale))
    sh = max(2, int(H * scale))
    small = pygame.transform.smoothscale(surface, (sw, sh))
    big = pygame.transform.smoothscale(small, (W, H))
    if color is not None:
        tint = pygame.Surface((W, H), pygame.SRCALPHA)
        tint.fill((*color, 255))
        big.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return big


def _bloom_stack(scene, targets, layers, blend=pygame.BLEND_RGBA_ADD):
    """Apply a stack of blurred-silhouette glows to `scene` (additive
    by default). `layers` is an iterable of (scale, color_rgb, alpha)."""
    for scale, col, alpha in layers:
        glow = _blur(targets, scale, col)
        glow.set_alpha(alpha)
        scene.blit(glow, (0, 0), special_flags=blend)


def _compose(backdrop, pillar_bodies, glow_targets, dark_alpha,
             aura_layers, tinted, extra_top_glow=None):
    """Standard 5-pass composite shared by every variant:
        1. backdrop                — sky/mountains/ground
        2. dark overlay            — dims the world
        3. pillar bodies           — un-tinted, restored on top of darkness
        4. aura/bloom stack        — wide additive glows behind targets
        5. tinted glow targets     — the actual sprites in green form
        (optional) extra_top_glow  — a final additive top-up
    """
    scene = backdrop.copy()
    _dark_overlay(scene, dark_alpha)
    scene.blit(pillar_bodies, (0, 0))
    _bloom_stack(scene, glow_targets, aura_layers)
    scene.blit(tinted, (0, 0))
    if extra_top_glow is not None:
        for scale, col, alpha in extra_top_glow:
            glow = _blur(glow_targets, scale, col)
            glow.set_alpha(alpha)
            scene.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── VARIANT 1 — RADIANT ────────────────────────────────────────────────────
# Strong tint + dual bloom (tight + wide). Reads as "moonlit phosphor".

def variant_radiant(backdrop, bodies, targets, refs):
    tinted = _dominant_green(targets,
                             tint_mid=(60, 255, 90),
                             overlay_color=(40, 220, 70),
                             overlay_alpha=160)
    return _compose(
        backdrop, bodies, targets, dark_alpha=130,
        aura_layers=(
            (0.04, (50, 200, 70),  200),
            (0.10, (90, 255, 110), 220),
            (0.22, (120, 255, 140),190),
        ),
        tinted=tinted,
        extra_top_glow=((0.05, (180, 255, 200), 100),),
    )


# ─── VARIANT 2 — INCANDESCENT ───────────────────────────────────────────────
# Bright near-white hot cores on top of green-tinted sprite + dramatic outer
# halo. Looks like the targets are glowing embers.

def variant_incandescent(backdrop, bodies, targets, refs):
    tinted = _dominant_green(targets,
                             tint_mid=(80, 255, 110),
                             overlay_color=(40, 220, 60),
                             overlay_alpha=170)
    scene = _compose(
        backdrop, bodies, targets, dark_alpha=140,
        aura_layers=(
            (0.05, (50, 200, 70),  220),
            (0.13, (90, 255, 120), 200),
            (0.28, (60, 230, 80),  170),
        ),
        tinted=tinted,
    )
    # Hot core: tightest blur recoloured white-green, blended additively.
    core = _blur(targets, 0.30, (220, 255, 230))
    core.set_alpha(150)
    scene.blit(core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    core2 = _blur(targets, 0.50, (255, 255, 255))
    core2.set_alpha(120)
    scene.blit(core2, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── VARIANT 3 — MEGABLOOM ──────────────────────────────────────────────────
# 5-radius bloom stack for maximum haze, plus a strong tint. The "this
# thing is RADIATING" option.

def variant_megabloom(backdrop, bodies, targets, refs):
    tinted = _dominant_green(targets,
                             tint_mid=(70, 255, 100),
                             overlay_color=(40, 210, 60),
                             overlay_alpha=180)
    return _compose(
        backdrop, bodies, targets, dark_alpha=125,
        aura_layers=(
            (0.03, (40, 180, 60),   180),
            (0.06, (60, 220, 80),   200),
            (0.12, (90, 255, 110),  220),
            (0.20, (110, 255, 130), 200),
            (0.32, (140, 255, 160), 170),
        ),
        tinted=tinted,
        extra_top_glow=(
            (0.06, (140, 255, 160), 120),
            (0.16, (180, 255, 200), 90),
        ),
    )


# ─── VARIANT 4 — TOXIC ──────────────────────────────────────────────────────
# Vivid almost-monochrome green + chromatic ghost (slight offset) +
# blue-cyan outer rim suggesting radioactive plant glow.

def variant_toxic(backdrop, bodies, targets, refs):
    tinted = _dominant_green(targets,
                             tint_mid=(50, 255, 80),
                             overlay_color=(20, 230, 40),
                             overlay_alpha=210)

    scene = backdrop.copy()
    _dark_overlay(scene, 135)
    scene.blit(bodies, (0, 0))

    # Outer rim: wide blue-cyan halo behind everything else.
    cyan_rim = _blur(targets, 0.06, (60, 220, 200))
    cyan_rim.set_alpha(170)
    scene.blit(cyan_rim, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Mid green bloom.
    for scale, col, a in (
            (0.05, (40, 200, 60),  220),
            (0.11, (70, 255, 100), 220),
            (0.22, (110, 255, 140),190),
    ):
        glow = _blur(targets, scale, col)
        glow.set_alpha(a)
        scene.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Chromatic ghost: same tinted layer offset by ±1 px in opposite hues.
    ghost_a = tinted.copy()
    ghost_a.set_alpha(95)
    scene.blit(ghost_a, (-1, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # main:
    scene.blit(tinted, (0, 0))
    # cyan smear on the far side:
    cyan_smear = pygame.Surface((W, H), pygame.SRCALPHA)
    cyan_smear.fill((60, 220, 200, 255))
    cyan_smear.blit(targets, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    cyan_smear.set_alpha(80)
    scene.blit(cyan_smear, (2, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── VARIANT 5 — OVERDRIVE ──────────────────────────────────────────────────
# Strong tint + bloom + radial sun-rays + central white-hot core. Maximum
# "this is ALIVE" feel.

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


def variant_overdrive(backdrop, bodies, targets, refs):
    tinted = _dominant_green(targets,
                             tint_mid=(70, 255, 100),
                             overlay_color=(40, 220, 60),
                             overlay_alpha=190)

    scene = backdrop.copy()
    _dark_overlay(scene, 135)
    scene.blit(bodies, (0, 0))

    # Bloom backdrop.
    for scale, col, a in (
            (0.05, (50, 200, 70),  220),
            (0.12, (90, 255, 110), 220),
            (0.25, (130, 255, 150),190),
    ):
        glow = _blur(targets, scale, col)
        glow.set_alpha(a)
        scene.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Radial rays from each glow-eligible centre.
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
    # Vegetation crowns (above each pillar top) get short rays too.
    for p in refs["pipes"]:
        cx = int(p.x + PIPE_W / 2)
        cy = int(p.gap_y - p.gap_h / 2 - 20)
        _draw_radial_rays(scene, cx, cy,
                          length=80, count=10, color=NEON,
                          alpha_start=160, phase=math.pi / 8, width=1)

    scene.blit(tinted, (0, 0))

    # White-hot inner cores on top.
    core = _blur(targets, 0.40, (255, 255, 255))
    core.set_alpha(170)
    scene.blit(core, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return scene


# ─── driver ─────────────────────────────────────────────────────────────────

VARIANTS = [
    ("variant_1_radiant.png",      variant_radiant),
    ("variant_2_incandescent.png", variant_incandescent),
    ("variant_3_megabloom.png",    variant_megabloom),
    ("variant_4_toxic.png",        variant_toxic),
    ("variant_5_overdrive.png",    variant_overdrive),
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
