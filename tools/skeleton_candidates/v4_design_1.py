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

# Luminous bluish-white radiograph palette. A faint COOL-DARK keyline (`sh`)
# gives every bone a thin edge so ribs read as separate ribs and the structure
# survives the glow — the legibility no longer leans on the bloom alone. `beak`
# is pushed toward white-hot so the dominant hooked beak bone is the brightest.
STYLE = dict(
    bone=(200, 218, 252),
    hi=(245, 250, 255),
    sh=(40, 55, 95),
    w_long=3, w_rib=2, w_fine=2,
    beak=(238, 246, 255),
)

# Cool steel-blue tint for the bloom so the glow reads as cold radiograph light.
_GLOW_TINT = (150, 185, 255)

# Near-white bone-core colour for the crisp top re-strike that cuts the
# structure back through the halo.
_CORE = (236, 244, 255)


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


# A crisp cool steel-blue fabric edge so the hood arc + tattered hem read as
# CLOTH even under the bright bone bloom — without it the radiograph halo (same
# blue family) tends to swallow the cowl outline at gameplay size.
_CLOAK_EDGE = (118, 150, 210)


def _cloak(angle):
    """The cloaked-Pip base for this design: the dark back mass redrawn as a
    hooded open-front cloak, with a cool-blue emissive rim/hem so the cloth
    edge carries a faint radiograph luminance like the bones do."""
    return XB.cloak_base(angle, XB.P_FLESH, glow=_GLOW_TINT, edge=_CLOAK_EDGE)


def _silhouette_mask(angle):
    """A white-on-transparent mask of the CLOAKED body silhouette, used to keep
    the body bloom INSIDE the outline so the glow can't spill past the cloak and
    soften the read. Repointed from the old ellipse body to the cloak so the
    bloom clips to the new draped shape."""
    mask = pygame.Surface((store_skins.COMPOSITE_W, store_skins.COMPOSITE_H),
                          pygame.SRCALPHA)
    mask.blit(_cloak(angle), (0, store_skins.PARROT_DY))
    # Collapse to a flat white fill carrying only the body's alpha.
    white = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
    white.fill((255, 255, 255, 255))
    white.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return white


def _restrike_cores(surf):
    """Re-strike a 1px near-white core inside each long bone so the structure
    cuts back through the halo (the previous crisp pass matched the glow value
    and vanished). Uses the shared anatomy so cores sit exactly on the bones."""
    XB.polybone(surf, _CORE, XB._SPINE, 1)
    XB.polybone(surf, _CORE, XB._KEEL, 1)
    for r0 in XB._RIB_ROOTS:
        XB.polybone(surf, _CORE, XB._rib_curve(r0), 1)
    # Legs (femur + tibia), pelvis geometry mirrored from paint_skeleton.
    pelvis = (22, 33 + XB.DY)
    for hipx, foot, splay in ((25, (26, 49 + XB.DY), -3), (30, (36, 49 + XB.DY), 3)):
        knee = (hipx + splay, 45 + XB.DY)
        XB.stroke(surf, _CORE, pelvis, knee, 1)
        XB.stroke(surf, _CORE, knee, foot, 1)


def _paint(surf, angle):
    # Skeleton on its own transparent layer so the glow is built from bone only,
    # not from the dark flesh underneath.
    layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    XB.paint_skeleton(layer, angle, style=STYLE)

    # Thin halo HUGGING the bones — small radius, low alpha — so the glow no
    # longer fills the silhouette into one blob. Clipped to the body outline so
    # the body glow can't spill past the dark flesh and soften the read.
    body_glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    body_glow.blit(_bloom_from(layer, 8.0, 50, _GLOW_TINT), (0, 0),
                   special_flags=pygame.BLEND_RGB_ADD)
    body_glow.blit(_bloom_from(layer, 3.5, 70, _GLOW_TINT), (0, 0),
                   special_flags=pygame.BLEND_RGB_ADD)
    body_glow.blit(_silhouette_mask(angle), (0, 0),
                   special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(body_glow, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # The beak projects FORWARD of the flesh, so its glow is added unclipped —
    # but reduced ~40% from R1 so the hero now wins by hard-edged CONTRAST, not
    # by out-blooming the rest of the bird.
    beak = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    beak.blit(layer, (0, 0), pygame.Rect(50, 50, 24, 22))
    surf.blit(_bloom_from(beak, 3.0, 78, (190, 215, 255)),
              (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    surf.blit(_bloom_from(beak, 1.6, 105, (225, 238, 255)),
              (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    # Crisp bones on top, then near-white cores re-struck so structure cuts back
    # through the glow.
    surf.blit(layer, (0, 0))
    _restrike_cores(surf)

    # Enlarged white-hot beak core re-strike, drawn last over everything: the
    # hooked upper mandible is the single brightest, largest, hardest-edged bone
    # on the bird — the hero wins by contrast.
    upper = [(53, 36), (67, 42), (68, 47), (62, 47), (56, 44), (53, 41)]
    pygame.draw.polygon(surf, _CORE, upper)
    pygame.draw.polygon(surf, (252, 254, 255),
                        [(55, 38), (65, 42), (66, 45), (58, 42)])
    XB.knob(surf, (8, 9, 16), (57, 41), 1)              # nostril stays hollow


build = store_skins._make_skin(_paint, base_fn=_cloak)
