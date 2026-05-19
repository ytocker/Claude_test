"""V5 PUNCH+ in-world NIGHTGLOW visual effect.

When NIGHTGLOW is active, this module composites the agreed-upon
"world goes dark, important things glow neon green" treatment over
the rendered frame:

    1. Dim the whole scene (sky/mountains/ground/pillars).
    2. Restore pillar STONE BODIES on top — they stay un-dimmed.
    3. Silhouette-clean green halos around Pip + coins + powerups +
       pillar VEGETATION.
    4. Recolour those glow targets via a luminance→green palette ramp
       so the original sprite colours are fully replaced (no red Pip,
       no gold coin trace) — mirroring how GHOST mode swaps the
       parrot's reds to cool-blue spectral colours.
    5. One extra additive top glow.

Direct port of tools/render_nightglow_variants.py:variant_punch_plus.
Endpoints + halo stack exactly match the approved screenshot.

Numpy/surfarray is used per frame for the luminance recolour and the
halo alpha pre-multiplication (BLEND_RGBA_ADD ignores source alpha
for RGB, so the only way to confine a uniform-colour silhouette halo
to entity neighbourhoods is to bake `RGB *= alpha` in).

If numpy is unavailable (e.g. on a stripped pygbag bundle), the
import is caught and `apply_nightglow` falls back to a simple dim-
plus-tint composite that still reads as "night mode + green glow"
but skips the per-pixel recolour. That way picking up the buff
NEVER crashes the run, regardless of bundle contents.
"""

try:
    import numpy as np
    import pygame.surfarray
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False

import pygame

from game.config import W, H
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


# V5 PUNCH+ palette + halo stack — DO NOT touch without re-doing the
# variant comparison screenshots that the user already signed off on.
_DARK_OVERLAY_TINT  = (4, 8, 16)
_DARK_OVERLAY_ALPHA = 130

_RECOL_DARK   = (8,   60,  22)
_RECOL_BRIGHT = (220, 255, 230)

_AURA_LAYERS = (
    (0.022, (30, 170, 25),  160),   # wide outer aura
    (0.05,  (55, 215, 45),  185),
    (0.13,  (90, 240, 75),  195),
    (0.28,  (120, 250, 105),170),
)
_EXTRA_TOP_LAYER = (0.20, (90, 230, 75), 70)


def _recolour_in_place(surface: pygame.Surface) -> None:
    """Replace every visible RGB on `surface` with a green of equivalent
    brightness on the V5 ramp. Alpha is untouched so the silhouette
    survives. Per-pixel work via numpy/surfarray — ~5–10 ms for a
    360×640 surface.

    Ramp: L=0 (black) → dark green, L=1 (white) → bright green-white.
    Matches tools/render_nightglow_variants.py:luminance_to_palette."""
    rgb = pygame.surfarray.pixels3d(surface).astype(np.float32)
    L = (0.30 * rgb[..., 0]
       + 0.59 * rgb[..., 1]
       + 0.11 * rgb[..., 2]) / 255.0
    bright = np.array(_RECOL_BRIGHT, dtype=np.float32)
    dark   = np.array(_RECOL_DARK,   dtype=np.float32)
    out = dark + (bright - dark) * L[..., None]
    pygame.surfarray.pixels3d(surface)[:] = np.clip(out, 0, 255).astype(np.uint8)


def _silhouette_halo(targets: pygame.Surface, scale: float,
                    color: tuple, alpha: int) -> pygame.Surface:
    """One additive halo layer. Paints uniform `color` over the alpha
    mask of `targets`, blurs via downsample+upsample, then pre-
    multiplies RGB by the per-pixel alpha so BLEND_RGBA_ADD only
    contributes where the source has coverage. `alpha` controls
    overall halo strength."""
    sil = pygame.Surface((W, H), pygame.SRCALPHA)
    sil.fill((*color, 255))
    pygame.surfarray.pixels_alpha(sil)[:] = pygame.surfarray.array_alpha(targets)
    sw, sh = max(2, int(W * scale)), max(2, int(H * scale))
    small = pygame.transform.smoothscale(sil, (sw, sh))
    big = pygame.transform.smoothscale(small, (W, H))
    rgb = pygame.surfarray.pixels3d(big)
    a = pygame.surfarray.array_alpha(big).astype(np.float32) / 255.0
    factor = a * (alpha / 255.0)
    rgb[:] = np.clip(rgb.astype(np.float32) * factor[..., None],
                     0, 255).astype(np.uint8)
    return big


def _build_layers(world, sx: int, sy: int):
    """Render two side surfaces:

      bodies        — pillar stone columns only (no decorations)
      glow_targets  — pillar VEGETATION + coins + powerups + Pip

    These are re-renders of what's already on screen, but split into
    the two roles the composite needs. KFC pillars draw as one cached
    bitmap so they go onto `bodies` whole (their fries/buckets won't
    glow during nightglow — minor cost for a corner-case overlap
    of two powerups). The split for normal pipes uses _paint_stone +
    the variant's decorate callable from game.pillar_variants."""
    pal = world.biome_palette
    bodies       = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()
    glow_targets = pygame.Surface((W, H), pygame.SRCALPHA).convert_alpha()

    kfc_visual = world.bird.kfc_active
    for p in world.pipes:
        if p.is_kfc and kfc_visual:
            p.draw(bodies, pal, kfc_visual=True)
            continue
        top_sil, bot_sil, decorate = _VARIANTS[p.seed % VARIANT_COUNT]
        _paint_stone(bodies, p.top_rect, top_sil, pal, p.seed)
        _paint_stone(bodies, p.bot_rect, bot_sil, pal, p.seed + 1)
        decorate(glow_targets, p.top_rect, p.bot_rect, pal, p.seed)

    triple_active = world.triple_timer > 0
    kfc_active = world.bird.kfc_active
    for c in world.coins:
        c.draw(glow_targets, kfc_active=kfc_active,
               triple_active=triple_active)
    for m in world.powerups:
        m.draw(glow_targets)
    world.bird.draw(glow_targets, sx, sy,
                    flipped=world.reverse_timer > 0)

    return bodies, glow_targets


def _halo_no_numpy(targets: pygame.Surface, scale: float,
                  color: tuple, alpha: int) -> pygame.Surface:
    """Halo layer built without numpy. Multiply-tints the source by
    `color` (so warm channels get crushed), blurs via downsample +
    upsample, then uses Surface.premul_alpha() to pre-multiply RGB by
    the per-pixel alpha — that gates the additive blit by the entity
    silhouette so the green doesn't paint the whole canvas. Final
    fill(BLEND_RGBA_MULT) scales the RGB by `alpha` for strength."""
    base = targets.copy()
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((*color, 255))
    base.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    sw, sh = max(2, int(W * scale)), max(2, int(H * scale))
    small = pygame.transform.smoothscale(base, (sw, sh))
    big = pygame.transform.smoothscale(small, (W, H))
    pm = big.premul_alpha()
    pm.fill((alpha, alpha, alpha, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return pm


def _apply_fallback(screen: pygame.Surface, world, sx: int, sy: int,
                    strength: float) -> None:
    """Numpy-free composite that still confines the green to Pip +
    coins + powerups + pillar vegetation — NEVER paints over the
    whole canvas. Uses multiply-tint instead of per-pixel luminance
    recolour, so entity colours retain a slight warm bleed (red
    feathers will look a touch warm-green vs the numpy path's pure
    green-white). Halo gating uses Surface.premul_alpha() so additive
    layers are confined to entity silhouettes."""
    bodies, glow_targets = _build_layers(world, sx, sy)

    # 1. Dim the scene.
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((*_DARK_OVERLAY_TINT,
                  int(_DARK_OVERLAY_ALPHA * strength)))
    screen.blit(overlay, (0, 0))

    # 2. Restore pillar bodies un-dimmed.
    screen.blit(bodies, (0, 0))

    # 3. Aura halo stack — silhouette-clean via premul_alpha.
    for scale, col, a in _AURA_LAYERS:
        screen.blit(_halo_no_numpy(glow_targets, scale, col,
                                   int(a * strength)),
                    (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 4. Green-tinted entities. Multiply by a bright green crushes
    #    the warm channels (red→dark-red, blue→dark-blue, green stays
    #    near full), then a brightening additive pass lifts the
    #    mids so they don't read as muddy.
    tinted = glow_targets.copy()
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((110, 240, 130, 255))
    tinted.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if strength < 1.0:
        tinted.fill((255, 255, 255, int(255 * strength)),
                    special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(tinted, (0, 0))
    # Bright additive top-up confined to the entity silhouette via
    # premul_alpha, so even the multiply-darkened mids get lifted.
    lift = glow_targets.copy()
    lift_tint = pygame.Surface((W, H), pygame.SRCALPHA)
    lift_tint.fill((60, 200, 80, 255))
    lift.blit(lift_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    lift = lift.premul_alpha()
    lift.fill((int(180 * strength), int(180 * strength),
               int(180 * strength), 255),
              special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(lift, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 5. Extra top glow.
    scale, col, a = _EXTRA_TOP_LAYER
    screen.blit(_halo_no_numpy(glow_targets, scale, col,
                               int(a * strength)),
                (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def apply_nightglow(screen: pygame.Surface, world, sx: int, sy: int,
                    strength: float) -> None:
    """Apply the V5 PUNCH+ composite to `screen` AFTER entities are
    already drawn. `strength` ∈ [0, 1] scales every alpha so the
    effect can fade in at activation and fade out at expiry."""
    if strength <= 0:
        return
    if not _HAS_NUMPY:
        _apply_fallback(screen, world, sx, sy, strength)
        return
    bodies, glow_targets = _build_layers(world, sx, sy)

    # 1. Dim the whole scene.
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((*_DARK_OVERLAY_TINT,
                  int(_DARK_OVERLAY_ALPHA * strength)))
    screen.blit(overlay, (0, 0))

    # 2. Restore pillar bodies un-dimmed.
    screen.blit(bodies, (0, 0))

    # 3. Additive halo stack around glow targets.
    for scale, col, a in _AURA_LAYERS:
        screen.blit(_silhouette_halo(glow_targets, scale, col,
                                     int(a * strength)),
                    (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 4. Recoloured entities on top — full colour replacement.
    recol = glow_targets.copy()
    _recolour_in_place(recol)
    # Honour the strength fade by adjusting the recoloured layer's
    # per-pixel alpha. At low strength the original entities (already
    # rendered to `screen` and now dimmed) show through more.
    if strength < 1.0:
        a = pygame.surfarray.pixels_alpha(recol)
        a[:] = (a.astype(np.uint32) * int(255 * strength) // 255).astype(np.uint8)
    screen.blit(recol, (0, 0))

    # 5. Extra top glow.
    scale, col, a = _EXTRA_TOP_LAYER
    screen.blit(_silhouette_halo(glow_targets, scale, col,
                                 int(a * strength)),
                (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
