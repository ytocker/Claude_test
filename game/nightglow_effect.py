"""V5 PUNCH+ in-world NIGHTGLOW visual effect.

Faithful port of tools/render_nightglow_variants.py:variant_punch_plus
(lines 303–316 of that file). The user approved
docs/screenshots/nightglow_variants/variant_5_punch_plus.png as the
agreed in-world design; this module produces the same composite.

Recipe (mirrors the tool's `_compose`, lines 208–222):

    1. Dim the whole scene (alpha-130 dark overlay).
    2. Restore pillar STONE BODIES on top — un-dimmed sandstone.
    3. 4 silhouette-clean additive aura halos around the glow
       targets (vegetation + coins + powerups + Pip).
    4. Recolour those glow targets via a luminance→green palette
       ramp so the original sprite colours are fully replaced
       (no warm bleed-through). Blit normally on top.
    5. One extra silhouette-clean additive halo for the bright
       rim accent.

Numpy is imported at module load so the init cost is paid once at
game launch instead of as a stutter on first nightglow pickup.
Per-frame cost on dummy SDL: ~9–11 ms (vs ~7 ms baseline).
"""

import numpy as np
import pygame
import pygame.surfarray

from game.config import W, H
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


# Constants — EXACT copies of tools/render_nightglow_variants.py's
# variant_punch_plus parameters. Do not touch without re-doing the
# variant comparison screenshots the user already signed off on.
_DARK_OVERLAY_TINT  = (4, 8, 16)
_DARK_OVERLAY_ALPHA = 130

_RECOL_DARK   = (8,   60,  22)
_RECOL_BRIGHT = (220, 255, 230)

_AURA_LAYERS = (
    (0.022, (30, 170, 25),   160),   # wide outer aura
    (0.05,  (55, 215, 45),   185),
    (0.13,  (90, 240, 75),   195),
    (0.28,  (120, 250, 105), 170),
)
_EXTRA_TOP_LAYER = (0.20, (90, 230, 75), 70)


def _build_layers(world, sx: int, sy: int):
    """Render two side surfaces:

      bodies        — pillar stone columns only (no decorations)
      glow_targets  — pillar VEGETATION + coins + powerups + Pip

    These are re-renders of what's already on screen, split into
    the two roles the composite needs. KFC pillars draw as one
    cached bitmap so they go onto `bodies` whole (their fries/
    buckets won't glow during nightglow — corner-case overlap of
    two powerups). The split for normal pipes uses `_paint_stone` +
    the variant's `decorate` callable from game.pillar_variants."""
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


def _recolour_in_place(surface: pygame.Surface) -> None:
    """Replace every visible RGB on `surface` with a green of
    equivalent brightness on the V5 ramp. Alpha is untouched so
    the silhouette survives. Per-pixel numpy work — ~3 ms for a
    360×640 surface on dummy SDL.

    Ramp: L=0 (black)→dark green, L=1 (white)→bright green-white.
    Matches tools/render_nightglow_variants.py:luminance_to_palette
    (lines 137–161 of that file)."""
    rgb = pygame.surfarray.array3d(surface).astype(np.float32)
    L = (0.30 * rgb[..., 0]
       + 0.59 * rgb[..., 1]
       + 0.11 * rgb[..., 2]) / 255.0
    bright = np.array(_RECOL_BRIGHT, dtype=np.float32)
    dark   = np.array(_RECOL_DARK,   dtype=np.float32)
    out = np.clip(dark + (bright - dark) * L[..., None],
                  0, 255).astype(np.uint8)
    px = pygame.surfarray.pixels3d(surface)
    px[:] = out
    del px  # release surface lock before caller blits


def _silhouette_halo(targets: pygame.Surface, scale: float,
                    color: tuple, alpha: int) -> pygame.Surface:
    """One additive halo layer. Paints uniform `color` over the
    alpha mask of `targets`, blurs via downsample+upsample, then
    pre-multiplies RGB by the per-pixel alpha so BLEND_RGBA_ADD
    contributes only where the silhouette has coverage. `alpha`
    controls overall halo strength.

    Mirrors tools/render_nightglow_variants.py:_halo (lines 172–
    200 of that file)."""
    sil = pygame.Surface((W, H), pygame.SRCALPHA)
    sil.fill((*color, 255))
    src_a = pygame.surfarray.array_alpha(targets)
    sil_a = pygame.surfarray.pixels_alpha(sil)
    sil_a[:] = src_a
    del sil_a  # release lock before smoothscale
    sw, sh = max(2, int(W * scale)), max(2, int(H * scale))
    small = pygame.transform.smoothscale(sil, (sw, sh))
    big = pygame.transform.smoothscale(small, (W, H))
    a_arr = pygame.surfarray.array_alpha(big).astype(np.float32) / 255.0
    factor = a_arr * (alpha / 255.0)
    rgb_view = pygame.surfarray.pixels3d(big)
    rgb_view[:] = np.clip(rgb_view.astype(np.float32)
                           * factor[..., None],
                           0, 255).astype(np.uint8)
    del rgb_view  # release lock before caller blits
    return big


def apply_nightglow(screen: pygame.Surface, world, sx: int, sy: int,
                    strength: float) -> None:
    """Apply the V5 PUNCH+ composite to `screen` AFTER entities are
    already drawn. `strength` ∈ [0, 1] scales every alpha so the
    effect can fade in at activation and fade out at expiry.

    Five-pass composite matching the screenshot tool's `_compose`
    (lines 208–222 of tools/render_nightglow_variants.py)."""
    if strength <= 0:
        return
    bodies, glow_targets = _build_layers(world, sx, sy)

    # 1. Dim the whole scene.
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((*_DARK_OVERLAY_TINT,
                  int(_DARK_OVERLAY_ALPHA * strength)))
    screen.blit(overlay, (0, 0))

    # 2. Restore pillar bodies un-dimmed.
    screen.blit(bodies, (0, 0))

    # 3. Four additive aura halos.
    for scale, col, a in _AURA_LAYERS:
        screen.blit(
            _silhouette_halo(glow_targets, scale, col,
                             int(a * strength)),
            (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 4. Luminance-recoloured entities on top — full colour
    #    replacement, no warm bleed.
    recol = glow_targets.copy()
    _recolour_in_place(recol)
    if strength < 1.0:
        # Fade the recolour layer in at activation / out at expiry
        # by scaling per-pixel alpha. Without this, partial-strength
        # frames would still fully replace entity colours.
        a = pygame.surfarray.pixels_alpha(recol)
        a[:] = (a.astype(np.uint32)
                * int(255 * strength) // 255).astype(np.uint8)
        del a
    screen.blit(recol, (0, 0))

    # 5. Extra top glow — bright rim accent.
    scale, col, a = _EXTRA_TOP_LAYER
    screen.blit(
        _silhouette_halo(glow_targets, scale, col,
                         int(a * strength)),
        (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
