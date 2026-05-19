"""V5 PUNCH+ in-world NIGHTGLOW visual effect.

When NIGHTGLOW is active, this module composites the agreed-upon
"world goes dark, important things glow neon green" treatment over
the rendered frame:

    1. Dim the whole scene (sky/mountains/ground/pillars).
    2. Restore pillar STONE BODIES on top — they stay un-dimmed.
    3. Silhouette-clean green halos around Pip + coins + powerups +
       pillar VEGETATION.
    4. Tint those glow targets toward green so the original sprite
       hues read as green-dominant.
    5. Brightening additive lift (silhouette-gated) so mid-tones don't
       look muddy.
    6. One extra additive top glow.

Direct port of tools/render_nightglow_variants.py:variant_punch_plus.

Implementation uses ONLY built-in pygame (no numpy, no surfarray) so
the buff stays fast on every build target (native desktop AND
pygbag/WASM) — early iterations did per-frame numpy ops that caused
severe lag on WASM. The trick that lets the halos avoid numpy is
Surface.premul_alpha(), which bakes `RGB *= alpha/255` into the
surface so BLEND_RGBA_ADD can be gated by the entity silhouette.
"""

import pygame

from game.config import W, H
from game.pillar_variants import _VARIANTS, VARIANT_COUNT, _paint_stone


# V5 PUNCH+ palette + halo stack — DO NOT touch without re-doing the
# variant comparison screenshots that the user already signed off on.
_DARK_OVERLAY_TINT  = (4, 8, 16)
_DARK_OVERLAY_ALPHA = 130

_AURA_LAYERS = (
    (0.022, (30, 170, 25),  160),   # wide outer aura
    (0.05,  (55, 215, 45),  185),
    (0.13,  (90, 240, 75),  195),
    (0.28,  (120, 250, 105),170),
)
_EXTRA_TOP_LAYER = (0.20, (90, 230, 75), 70)

# Green tint pushed into entity sprites in step 4 (multiply-blend).
# Crushes warm channels so red feathers / gold coin highlights read
# as green-dominant; a separate additive lift restores brightness.
_ENTITY_TINT = (110, 240, 130)

# Additive lift colour + strength (RGB pre-multiplied via premul_alpha
# so the lift is confined to the entity silhouette).
_LIFT_TINT       = (60, 200, 80)
_LIFT_STRENGTH   = 180


def _build_layers(world, sx: int, sy: int):
    """Render two side surfaces:

      bodies        — pillar stone columns only (no decorations)
      glow_targets  — pillar VEGETATION + coins + powerups + Pip

    These are re-renders of what's already on screen, but split into
    the two roles the composite needs. KFC pillars draw as one cached
    bitmap so they go onto `bodies` whole (their fries/buckets won't
    glow during nightglow — minor cost for a corner-case overlap of
    two powerups). The split for normal pipes uses _paint_stone +
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


def _halo(targets: pygame.Surface, scale: float,
          color: tuple, alpha: int) -> pygame.Surface:
    """One additive halo layer. Multiply-tints `targets` by `color`
    (so warm channels collapse to near-zero, leaving green-dominant
    blur material), downsample-upsamples for blur, pre-multiplies
    RGB by alpha via Surface.premul_alpha() so the additive blit is
    GATED BY THE ENTITY SILHOUETTE (otherwise BLEND_RGBA_ADD would
    paint the halo colour onto the whole canvas regardless of source
    alpha). Final BLEND_RGBA_MULT fill attenuates RGB by `alpha`
    for overall strength control."""
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

    # 3. Silhouette-gated aura halo stack.
    for scale, col, a in _AURA_LAYERS:
        screen.blit(_halo(glow_targets, scale, col, int(a * strength)),
                    (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 4. Green-tinted entities. Multiply by a bright green crushes
    #    the warm channels (red→dark-red, blue→dark-blue, green near
    #    full), then the additive lift below pushes mids back up.
    tinted = glow_targets.copy()
    tint = pygame.Surface((W, H), pygame.SRCALPHA)
    tint.fill((*_ENTITY_TINT, 255))
    tinted.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if strength < 1.0:
        tinted.fill((255, 255, 255, int(255 * strength)),
                    special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(tinted, (0, 0))

    # 5. Brightening additive lift confined to the silhouette via
    #    premul_alpha (so the lift never bleeds into surrounding sky).
    lift = glow_targets.copy()
    lift_tint = pygame.Surface((W, H), pygame.SRCALPHA)
    lift_tint.fill((*_LIFT_TINT, 255))
    lift.blit(lift_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    lift = lift.premul_alpha()
    s = int(_LIFT_STRENGTH * strength)
    lift.fill((s, s, s, 255), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(lift, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # 6. Extra top glow.
    scale, col, a = _EXTRA_TOP_LAYER
    screen.blit(_halo(glow_targets, scale, col, int(a * strength)),
                (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
