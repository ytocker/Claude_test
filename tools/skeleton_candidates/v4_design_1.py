"""v4 SKELETON · design_1 — RADIOGRAPH.

A true medical x-ray look: cool blue-white bones glowing softly THROUGH the
dark translucent body, with a gentle bloom/halo so the bones read as emitting
light through tissue. The dominant hooked beak bone is the brightest, most
salient element — its own extra bloom makes it the hero.

The radiograph glow is built by painting the COMPLETE shared skeleton onto a
private SRCALPHA layer, smoothscaling a copy down then back up (a cheap blur)
to make a soft halo, blitting that halo additively UNDER the crisp bones, then
the crisp bones on top. Anatomy is the shared `paint_skeleton` — nothing is
dropped or reinvented here; only the bone *material* (cool luminous blue-white,
no dark keyline so it reads as light, not ink) and the bloom are ours.
"""
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB
from game import store_skins

# Luminous bluish-white radiograph palette. No `sh` keyline — on a real x-ray
# plate bone is brighter than its surroundings, never ringed in dark ink, so the
# legibility comes from the bloom halo instead. `beak` is pushed toward
# white-hot so the dominant hooked beak bone is the brightest thing on the bird.
STYLE = dict(
    bone=(210, 225, 255),
    hi=(245, 250, 255),
    sh=None,
    w_long=3, w_rib=2, w_fine=2,
    beak=(238, 246, 255),
)

# Cool steel-blue tint for the bloom so the glow reads as cold radiograph light.
_GLOW_TINT = (150, 185, 255)


def _blur(surf, factor):
    """Cheap separable-ish blur: shrink then grow with bilinear smoothscale."""
    w, h = surf.get_size()
    sw, sh = max(1, int(w / factor)), max(1, int(h / factor))
    small = pygame.transform.smoothscale(surf, (sw, sh))
    return pygame.transform.smoothscale(small, (w, h))


def _bloom_from(layer, factor, alpha, tint):
    """A soft tinted halo from a bone layer: blur it, recolour to the cold glow
    tint while keeping the blurred alpha, scale brightness with `alpha`."""
    blurred = _blur(layer, factor)
    glow = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    glow.fill((*tint, 255))
    # Carry the blurred shape's alpha onto the flat tint.
    glow.blit(blurred, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    glow.set_alpha(alpha)
    return glow


def _paint(surf, angle):
    # Skeleton on its own transparent layer so the glow is built from bone only,
    # not from the dark flesh underneath.
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    XB.paint_skeleton(layer, angle, style=STYLE)

    # Wide soft outer halo + tighter inner glow, both added beneath the crisp
    # bones so the bones look like they emit light through the tissue. Kept
    # restrained so the fine structure (ribs, spine knobs, legs) still reads
    # rather than washing into one blob.
    wide = _bloom_from(layer, 6.5, 95, _GLOW_TINT)
    tight = _bloom_from(layer, 3.0, 120, _GLOW_TINT)
    surf.blit(wide, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(tight, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Extra white-hot bloom concentrated on the dominant beak bone so it is the
    # clear hero. Mask the bone layer to the beak region before blooming, and
    # stack a tight + soft pass so the hook reads as the brightest thing here.
    beak = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    beak.blit(layer, (0, 0), pygame.Rect(50, 50, 24, 22))
    surf.blit(_bloom_from(beak, 3.0, 130, (190, 215, 255)),
              (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(_bloom_from(beak, 1.6, 175, (225, 238, 255)),
              (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Crisp bones on top so the structure stays sharp inside its own glow.
    surf.blit(layer, (0, 0))

    # White-hot core re-strike on the dominant beak so the hook is unmistakably
    # the hero — drawn last, over its own bloom.
    pygame.draw.polygon(surf, (250, 252, 255),
                           [(56, 39), (64, 42), (65, 46), (61, 46),
                            (57, 44), (55, 42)])


build = store_skins._make_skin(_paint, base_fn=XB.bone_parrot)
