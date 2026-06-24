"""v4 SKELETON · design_3 — NEON / BIOLUMINESCENT (scratch exploration only).

The bones are the LIGHT SOURCE. A saturated cyan-green skeleton emits a TIGHT
emissive aura that hugs each bone (not a body-filling cloud) over a near-black
flesh body, so the bird reads as a glowing x-ray that sings hardest on the
night sky but still resolves into countable bones at 40px. Anatomy is fixed in
`_v4_xray_base`; this file only changes the bone *material*: fat solid emissive
shafts, a thin hugging glow, a re-struck near-opaque crisp core on top, and a
beak bone that out-glows the head as the hero. A thin cool keyline holds the
body's silhouette on the bright day sky; the eye socket and inter-rib voids are
punched back in after the bloom so the structure reads as a skeleton.

NOT registered in store_skins.BUILDERS. Production is untouched.
"""
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB
from game.store_skins import COMPOSITE_W, COMPOSITE_H


# Neon palette: cyan-green core, a near-white hot-core, and a green halo tint.
NEON_CORE = (150, 255, 220)        # saturated cyan-green — the emitting bone
NEON_HOT = (235, 255, 245)         # white-green hot-core down each bone
HALO_TINT = (60, 230, 180)         # outer glow bleeding into the dark flesh
BEAK_CORE = (215, 255, 242)        # beak glows brightest/whitest — the hero
SOCKET = (8, 9, 16)                # dark gaps that say "skeleton"
BODY_EDGE = (46, 102, 88)          # thin cool keyline holding the silhouette

# Style used to PAINT onto the isolated neon layer. No dark keyline (we want the
# bones to emit, not be outlined); highlights off so the post-pass owns the
# hot-core. FAT solid shafts so each bone is a countable emissive rod the glow
# only hugs — not a body-filling cloud.
STYLE = dict(
    bone=NEON_CORE, hi=None, sh=None,
    w_long=4, w_rib=3, w_fine=2, beak=BEAK_CORE,
)

# Near-black flesh — lifted ~15-20% vs round_1 so the dark body still holds a
# shape on the bright day sky and against green foliage, while staying dark
# enough that the neon bones remain the only real light source.
_FLESH = XB._pal(
    tail=[(13, 15, 25), (17, 19, 31), (21, 24, 38), (25, 28, 44)],
    tail_line=(8, 9, 16),
    body_shadow=(8, 9, 16),
    body_main=(17, 19, 31),
    body_chest=(21, 24, 38),
    body_belly=(27, 31, 47),
    sheen=None,
    wing_main=(14, 16, 27),
    wing_dark=(8, 9, 16),
    wing_tip=(20, 23, 35),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=(11, 13, 21),
    head_main=(20, 23, 35),
    head_cheek=(26, 30, 45),
    head_crown=(30, 34, 50),
    lens_frame=(0, 0, 0), lens_body=(0, 0, 0),
    lens_tint=None, lens_glint=None,
    beak_main=(17, 19, 31),
    beak_dark=(10, 11, 19),
    beak_gloss=(23, 26, 40),
    foot=(13, 15, 25),
)


def _flesh_base(angle_deg):
    return XB._build_parrot_with_palette(angle_deg, _FLESH, draw_lenses=False)


def _hot_core(surf):
    """Re-strike a near-white hot-core line down the long bones so the centre
    of each bone reads as the brightest point of the emission — what sells a
    glowing tube rather than a flat coloured stick. The cranium dome is held
    QUIET (no bright tick) so the beak stays the unmistakable brightest bone."""
    XB.polybone(surf, NEON_HOT, XB._SPINE, 1)
    XB.polybone(surf, NEON_HOT, XB._KEEL, 1)
    for r0 in XB._RIB_ROOTS:
        XB.polybone(surf, NEON_HOT, XB._rib_curve(r0), 1)
    # Skull rim only — a quiet socketed cranium, no bright dome tick.
    pygame.draw.circle(surf, NEON_CORE, (XB.HX, XB.HY), 11, 1)


def _reopen_negative_space(surf):
    """Punch the dark gaps back in so the bloom can't fill the eye socket — that
    dark void is a big part of what reads as 'skull' rather than a glowing
    blob. Called both on the bone layer and on the final composite."""
    pygame.draw.circle(surf, SOCKET, (XB.HX + 3, XB.HY - 1), 4)
    pygame.draw.circle(surf, NEON_CORE, (XB.HX + 3, XB.HY - 1), 4, 1)


def _beak_hero(surf):
    """The dominant beak bone — the brightest, whitest, slightly LARGER bone,
    re-painted last so it out-glows the quiet skull. Forward-projecting hooked
    raptor outline extended a touch so the front spike is unmistakable at 40px."""
    upper = [(53, 36), (68, 42), (69, 47), (63, 47), (57, 44), (53, 41)]
    lower = [(54, 45), (64, 46), (63, 49), (54, 47)]
    pygame.draw.polygon(surf, BEAK_CORE, upper)
    pygame.draw.polygon(surf, BEAK_CORE, lower)
    pygame.draw.line(surf, NEON_HOT, (54, 39), (67, 43), 2)   # culmen hot-core
    pygame.draw.line(surf, NEON_HOT, (54, 45), (63, 46), 1)   # lower-jaw hot edge
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
    tinted = pygame.Surface(layer.get_size(), pygame.SRCALPHA)
    tinted.fill((*color, 255))
    tinted.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    tinted.set_alpha(alpha)
    return tinted


def _paint(surf, angle):
    """Paint the neon skeleton: a thin cool keyline holds the body; the bones
    get a TIGHT hugging aura + a near-opaque crisp core; the eye socket is
    punched back in last so the structure reads at 40px."""
    # Thin cool keyline around the whole opaque silhouette so the dark body keeps
    # a shape on the bright day sky / green foliage. Bones stay the light source.
    outline = pygame.mask.from_surface(surf).outline()
    if len(outline) > 1:
        pygame.draw.lines(surf, BODY_EDGE, True, outline, 1)

    # Isolated bone layer (full anatomy + hot-core + reopened socket + beak).
    layer = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    XB.paint_skeleton(layer, angle, style=STYLE)
    _hot_core(layer)
    _reopen_negative_space(layer)
    _beak_hero(layer)

    # TIGHT aura: gutted the widest pass; mid pulled in; tight glow near-full —
    # a thin emissive halo hugging each bone instead of a body-filling cloud.
    aura = _tint(_blur(layer, 5), HALO_TINT, 55)
    halo_mid = _tint(_blur(layer, 4), HALO_TINT, 90)
    glow_tight = _blur(layer, 2)
    glow_tight.set_alpha(180)

    surf.blit(aura, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    surf.blit(halo_mid, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    surf.blit(glow_tight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Near-opaque crisp emissive core on top — solid countable shafts the glow
    # only wraps; then re-punch the socket so the bloom can't refill it.
    surf.blit(layer, (0, 0))
    _reopen_negative_space(surf)


def _make():
    from game import store_skins
    return store_skins._make_skin(_paint, base_fn=_flesh_base)


build = _make()
