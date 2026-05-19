"""V5 PUNCH+ in-world NIGHTGLOW visual effect (pure-pygame).

Approximates tools/render_nightglow_variants.py:variant_punch_plus
using only built-in pygame primitives — no numpy, no surfarray.
Earlier numpy-based version used a true luminance→green ramp that
matched the screenshot pixel-for-pixel but forced pygbag to bundle
the numpy wheel into the WASM build, which made cold-start take
90 s+. Dropping numpy restores fast cold-start; the trade-off is
that the entity recolour is a strong multiply-tint instead of a
luminance ramp, so very-red sprite areas (Pip's feathers) carry a
slightly warmer green than the screenshot. Halo layers + scene
dimming + pillar-body restore are unchanged.

Composite:

    1. Dim the whole scene (alpha-130 dark overlay).
    2. Restore pillar STONE BODIES on top — un-dimmed sandstone.
    3. Two silhouette-gated additive aura halos (mid + tight).
    4. Multiply-tint recolour of glow targets so they read green.
    5. Additive lift, silhouette-gated, to brighten the tinted
       entities back up from the multiply's darkening.

The silhouette-gating uses Surface.premul_alpha() to bake
`RGB *= alpha/255` into the surface — that's what lets
BLEND_RGBA_ADD respect the entity silhouette without per-pixel work.

Halo count cut from 5 → 2 vs the screenshot tool's recipe to keep
per-frame cost inside the 60 FPS budget on WASM (each halo is a
smoothscale-down + smoothscale-up + premul + fill ≈ 4 ms at
360×640). The visual is approximate to the tool's variant_punch_plus
output but holds the same shape (sky dims, pillar bodies grounded,
vegetation + coins + powerups + Pip glow green).
"""

import pygame

from game.config import W, H
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


# Constants — same values as the screenshot tool's variant_punch_plus.
# Do not change without re-doing the variant comparison.
_DARK_OVERLAY_TINT  = (4, 8, 16)
_DARK_OVERLAY_ALPHA = 130

# Two halo layers (was 5 = 4 aura + 1 extra_top). Each smoothscale +
# premul_alpha is ~4 ms at 360×640, so 5 layers cost ~20 ms/frame which
# blew the 60 FPS budget on every build target. The remaining two
# cover the visible aura range: one mid-spread for atmospheric glow,
# one tighter for the bright rim. Matches the perf-tuned profile from
# commit b3e5703.
_AURA_LAYERS = (
    (0.08, (60, 220, 60),  190),   # mid-spread atmospheric glow
    (0.22, (110, 245, 95), 195),   # tight bright rim
)

# Entity recolour: multiply-tint by a strong green so warm channels
# collapse, then add a brightening green lift confined to the entity
# silhouette so the result reads as bright green-dominant rather than
# muddy dark green.
_ENTITY_TINT     = (110, 240, 130)
_LIFT_TINT       = (60, 200, 80)
_LIFT_STRENGTH   = 180


def _build_layers(world, sx: int, sy: int):
    """Render two side surfaces:

      bodies        — pillar stone columns only (no decorations)
      glow_targets  — pillar VEGETATION + coins + powerups + Pip

    These are re-renders of what's already on screen, split into
    the two roles the composite needs. KFC pillars draw as one
    cached bitmap so they go onto `bodies` whole. The split for
    normal pipes uses `_paint_stone` + the variant's `decorate`
    callable from game.pillar_variants."""
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


def _halo(targets: pygame.Surface, scale: float,
          color: tuple, alpha: int) -> pygame.Surface:
    """One additive halo layer. Multiply-tints `targets` by `color`
    (so the blurred material reads as the chosen colour), downsample-
    upsamples for blur, pre-multiplies RGB by alpha via
    Surface.premul_alpha() so the additive blit is GATED BY THE
    ENTITY SILHOUETTE (otherwise BLEND_RGBA_ADD would paint the halo
    colour onto the whole canvas regardless of source alpha). The
    final BLEND_RGBA_MULT fill scales the result by `alpha` for
    overall strength."""
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


def apply_nightglow(screen: pygame.Surface, world, sx: int, sy: int,
                    strength: float) -> None:
    """Apply the V5 PUNCH+ composite to `screen` AFTER entities are
    already drawn. `strength` ∈ [0, 1] scales every alpha so the
    effect can fade in at activation and fade out at expiry."""
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

    # 3. Four silhouette-gated additive aura halos.
    for scale, col, a in _AURA_LAYERS:
        screen.blit(_halo(glow_targets, scale, col, int(a * strength)),
                    (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 4. Multiply-tinted entities — warm channels collapse to dim, green
    #    stays near full.
    tinted = glow_targets.copy()
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((*_ENTITY_TINT, 255))
    tinted.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if strength < 1.0:
        tinted.fill((255, 255, 255, int(255 * strength)),
                    special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(tinted, (0, 0))

    # 5. Brightening additive lift, silhouette-gated via premul_alpha
    #    so the mid-tones of the tinted entities lift out of muddiness
    #    without bleeding into the surrounding sky.
    lift = glow_targets.copy()
    lift_tint = pygame.Surface((W, H), pygame.SRCALPHA)
    lift_tint.fill((*_LIFT_TINT, 255))
    lift.blit(lift_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    lift = lift.premul_alpha()
    s = int(_LIFT_STRENGTH * strength)
    lift.fill((s, s, s, 255), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(lift, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
