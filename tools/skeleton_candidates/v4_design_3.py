"""v4 SKELETON · design_3 — NEON / BIOLUMINESCENT (scratch exploration only).

The bones are the LIGHT SOURCE. A saturated cyan-green skeleton emits a soft
glow into a near-black flesh body, so the bird reads as a glowing x-ray that
sings hardest on the night sky. Anatomy is fixed in `_v4_xray_base`; this file
only changes the bone *material*: it paints the full skeleton onto an isolated
neon layer, builds a cheap blur (smoothscale down→up) for the outer halo, then
re-strikes a brighter core and a near-white hot line so the centre of every
bone glows. The dominant hooked beak bone is glowed hardest — the hero.

NOT registered in store_skins.BUILDERS. Production is untouched.
"""
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB
from game.store_skins import COMPOSITE_W, COMPOSITE_H


# Neon palette: cyan-green core, a near-white hot-core, and a green halo tint.
NEON_CORE = (150, 255, 220)        # saturated cyan-green — the emitting bone
NEON_HOT = (235, 255, 245)         # white-green hot-core down each bone
HALO_TINT = (60, 230, 180)         # outer glow bleeding into the dark flesh
BEAK_CORE = (170, 255, 230)        # beak glows a hair brighter — the hero

# Style used to PAINT onto the isolated neon layer. No dark keyline (we want the
# bones to emit, not be outlined); highlights off so the post-pass owns the
# hot-core. Slightly fatter shafts so the glow has mass to bloom from.
STYLE = dict(
    bone=NEON_CORE, hi=None, sh=None,
    w_long=3, w_rib=2, w_fine=2, beak=BEAK_CORE,
)

# Near-black flesh — even darker than the base default so the neon really sings.
# A whisper of cool lift on crown/belly keeps the silhouette alive on day sky.
_FLESH = XB._pal(
    tail=[(8, 9, 16), (11, 12, 20), (14, 16, 26), (17, 19, 30)],
    tail_line=(5, 6, 11),
    body_shadow=(5, 6, 11),
    body_main=(11, 12, 20),
    body_chest=(14, 16, 26),
    body_belly=(18, 21, 33),
    sheen=None,
    wing_main=(9, 10, 18),
    wing_dark=(5, 6, 11),
    wing_tip=(13, 15, 24),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=(7, 8, 14),
    head_main=(13, 15, 24),
    head_cheek=(17, 20, 31),
    head_crown=(20, 23, 35),
    lens_frame=(0, 0, 0), lens_body=(0, 0, 0),
    lens_tint=None, lens_glint=None,
    beak_main=(11, 12, 20),
    beak_dark=(6, 7, 13),
    beak_gloss=(15, 17, 27),
    foot=(8, 9, 16),
)


def _flesh_base(angle_deg):
    return XB._build_parrot_with_palette(angle_deg, _FLESH, draw_lenses=False)


def _hot_core(surf):
    """Re-strike a near-white hot-core line down the long bones so the centre
    of each bone reads as the brightest point of the emission — what sells a
    glowing tube rather than a flat coloured stick."""
    # Spine + keel centre lines.
    XB.polybone(surf, NEON_HOT, XB._SPINE, 1)
    XB.polybone(surf, NEON_HOT, XB._KEEL, 1)
    for r0 in XB._RIB_ROOTS:
        XB.polybone(surf, NEON_HOT, XB._rib_curve(r0), 1)
    # Skull rim + cranium dome hot tick.
    pygame.draw.circle(surf, NEON_HOT, (XB.HX, XB.HY), 11, 1)
    pygame.draw.circle(surf, NEON_HOT, (XB.HX - 1, XB.HY - 4), 5, 1)


def _beak_hero(surf):
    """The dominant beak bone — re-painted on top with the brightest core and a
    near-white culmen so it out-glows every other bone. Forward-projecting
    hooked raptor outline, matching the base anatomy's beak footprint."""
    upper = [(54, 37), (66, 42), (67, 47), (62, 47), (57, 44), (54, 42)]
    lower = [(55, 45), (63, 46), (62, 49), (55, 47)]
    pygame.draw.polygon(surf, BEAK_CORE, upper)
    pygame.draw.polygon(surf, BEAK_CORE, lower)
    pygame.draw.line(surf, NEON_HOT, (55, 39), (65, 43), 2)   # culmen hot-core
    pygame.draw.line(surf, NEON_HOT, (55, 45), (62, 46), 1)   # lower-jaw hot edge
    pygame.draw.circle(surf, (6, 7, 13), (57, 41), 1)         # hollow nostril


def _blur(layer, factor):
    """Cheap gaussian-ish blur: shrink then grow with smoothscale. Larger
    factor → softer/wider halo."""
    w, h = layer.get_size()
    sw, sh = max(1, w // factor), max(1, h // factor)
    small = pygame.transform.smoothscale(layer, (sw, sh))
    return pygame.transform.smoothscale(small, (w, h))


def _tint(layer, color, alpha):
    """Recolour a glow layer to `color` (keeping its alpha shape) and scale its
    opacity — for building the coloured halo from the bone-mask."""
    out = layer.copy()
    out.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    # ^ keeps source alpha, swaps RGB toward the tint (since mask RGB ~= core).
    tinted = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    tinted.fill((*color, 255))
    tinted.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    tinted.set_alpha(alpha)
    return tinted


def _paint(surf, angle):
    """Paint the neon skeleton: build it on an isolated layer, bloom it into a
    halo, then composite halo→glow→crisp core→hot-core onto the dark body."""
    # Isolated bone layer (full anatomy + beak hero + hot-core).
    layer = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    XB.paint_skeleton(layer, angle, style=STYLE)
    _beak_hero(layer)
    _hot_core(layer)

    # Outer halo: wide soft blur, green tint, additive so it reads as emitted
    # light bleeding into the near-black flesh.
    halo_wide = _tint(_blur(layer, 5), HALO_TINT, 150)
    halo_mid = _tint(_blur(layer, 3), HALO_TINT, 170)
    glow_tight = _blur(layer, 2)
    glow_tight.set_alpha(190)

    surf.blit(halo_wide, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    surf.blit(halo_mid, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    surf.blit(glow_tight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Crisp neon core on top so the bone shapes stay sharp inside the bloom.
    surf.blit(layer, (0, 0))


def _make():
    from game import store_skins
    return store_skins._make_skin(_paint, base_fn=_flesh_base)


build = _make()
