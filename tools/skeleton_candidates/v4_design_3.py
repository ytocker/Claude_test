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


# Cloak treatment: the dark back mass is redrawn as a hooded open-front cloak in
# _FLESH's near-black cloth tones, lit only by a thin cyan-green emissive rim on
# the hood + tattered hem — the same neon hue the bones emit — so the cloth reads
# as dark fabric lit from within by the glowing skeleton, while the open front and
# recessed face opening keep the ribcage/spine/skull/beak as the brightest hero.
CLOAK_GLOW = (70, 235, 185)        # neon rim, matched to HALO_TINT so cloth + bone share a light
CLOAK_EDGE = (40, 120, 102)        # faint cool fabric crease lift (kept dim under the glow)


def _flesh_base(angle_deg):
    return XB.cloak_base(angle_deg, _FLESH, glow=CLOAK_GLOW, edge=CLOAK_EDGE)


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


CLOAK_DARK = (10, 12, 22)          # re-punched cloth: kills the bloom over the cowl/back
COWL_RIM = (110, 240, 215)         # hard ~75% cyan rim on the FRONT edge of the hood opening
HEM_UNDER = (50, 200, 165)         # faint cyan under-rim catching light along the tattered hem


def _reserve_dark_margin(surf, base_outline):
    """Reserve a dark cloth band the bone bloom CANNOT cross, so a dark cloak
    silhouette frames the glowing skeleton instead of a bloom-flooded blob.

    The skeleton's own bloom bleeds clear to the silhouette edge, erasing every
    band of dark cloth — worst at night, where the flooded edge merges into the
    navy sky. After the bloom we (1) re-punch the cowl cloth arcing over the
    crown to true dark, and (2) re-stroke the captured cloak OUTLINE as a fat
    near-black margin hugging the whole back/tail/hood/hem silhouette. Because
    the bones live in the interior, that edge band carries no bone shafts, so the
    dark frame survives while the glowing skeleton stays untouched in the middle."""
    # (1) cowl cloth ABOVE the skull crown — a true-dark band arcing over the head,
    # kept clear of the skull face so the lit skull still peers out of the hood.
    cowl = [(x, y + XB.DY) for (x, y) in
            [(38, 14), (42, 7), (47, 4), (53, 7), (58, 13), (57, 17),
             (52, 12), (47, 10), (42, 12), (39, 17)]]
    pygame.draw.polygon(surf, CLOAK_DARK, cowl)

    # (1b) back-drape shoulder band — a true-dark cloth strip along the TOP of the
    # back drape (the shoulder-to-tail upper edge) so the bloom can't merge the
    # back of the cloak into the sky. Kept above the spine so no bone is buried.
    drape = [(x, y + XB.DY) for (x, y) in
             [(13, 28), (20, 24), (28, 22), (36, 22), (40, 25),
              (33, 26), (27, 27), (20, 28), (14, 31)]]
    pygame.draw.polygon(surf, CLOAK_DARK, drape)

    # (2) fat dark margin band tracing the cloak silhouette outline. Width 4 walls
    # the bloom OUT of a cloth rim around the entire back/tail/hood/hem mass.
    if len(base_outline) > 1:
        pygame.draw.lines(surf, CLOAK_DARK, True, base_outline, 4)


def _cloak_rim(surf, base_outline):
    """Re-strike the cloak's defining fabric EDGES on top of the reserved dark
    margin, in the bone hue, so the dark cloth reads as a hood + tattered drape
    lit from within — not a glowing blob. Kept to hard thin edges (not bloom) so
    the skeleton stays the hero."""
    hood = [(x, y + XB.DY) for (x, y) in XB._HOOD_RIM]
    hem = [(x, y + XB.DY) for (x, y) in XB._HEM_EDGE]

    # Thin neon outline holds the whole cloak shape against night navy.
    if len(base_outline) > 1:
        pygame.draw.lines(surf, BODY_EDGE, True, base_outline, 1)

    # Hard ~75% cyan cowl-front rim: a single bright line along the FRONT edge of
    # the hood opening (the arc over+behind the skull) so the hood separates from
    # the darker crown band rather than dissolving into it.
    pygame.draw.lines(surf, COWL_RIM, False, hood, 1)

    # Tattered hem with a cyan under-rim: trace the hard hem teeth so the drape
    # edge catches light on the navy, then tick the tooth tips so the ragged
    # bottom reads as cloth, not bone.
    pygame.draw.lines(surf, HEM_UNDER, False, hem, 1)
    for hx, hy in ((7, 45), (13, 46), (18, 47), (24, 49)):
        pygame.draw.line(surf, COWL_RIM, (hx, hy + XB.DY), (hx, hy + XB.DY + 2), 1)


def _paint(surf, angle):
    """Paint the neon skeleton: a thin cool keyline holds the body; the bones
    get a TIGHT hugging aura + a near-opaque crisp core; the eye socket is
    punched back in last so the structure reads at 40px."""
    # Capture the cloak silhouette outline BEFORE any bloom expands the alpha —
    # this is the dark-cloth edge we both keyline now and wall the bloom out of
    # later (the additive halo would otherwise erase the whole cloak rim).
    base_outline = pygame.mask.from_surface(surf).outline()

    # Thin cool keyline around the whole opaque silhouette so the dark body keeps
    # a shape on the bright day sky / green foliage. Bones stay the light source.
    if len(base_outline) > 1:
        pygame.draw.lines(surf, BODY_EDGE, True, base_outline, 1)

    # Isolated bone layer (full anatomy + hot-core + reopened socket + beak).
    layer = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    XB.paint_skeleton(layer, angle, style=STYLE)
    _hot_core(layer)
    _reopen_negative_space(layer)
    _beak_hero(layer)

    # TIGHT aura, pulled IN ~1px globally vs round_3 so it can never reach the
    # reserved cloth margin: widest pass pulled WAY back so the dark cloak cloth
    # shows between bones; mid trimmed; tight glow trimmed off near-full.
    aura = _tint(_blur(layer, 7), HALO_TINT, 30)
    halo_mid = _tint(_blur(layer, 5), HALO_TINT, 64)
    glow_tight = _blur(layer, 3)
    glow_tight.set_alpha(150)

    surf.blit(aura, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    surf.blit(halo_mid, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    surf.blit(glow_tight, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    # Reserve a near-black cloth band the bloom CANNOT cross, so a dark cloak
    # silhouette frames the glow rather than a flooded blob.
    _reserve_dark_margin(surf, base_outline)
    # Near-opaque crisp emissive core on top — solid countable shafts the glow
    # only wraps; then re-punch the socket so the bloom can't refill it.
    surf.blit(layer, (0, 0))
    _reopen_negative_space(surf)
    # Re-strike the cloak's fabric edges last (cowl-front rim + tattered hem
    # under-rim + thin outline) so the dark cloth reads as a cloak lit from
    # within and the shape holds against night navy.
    _cloak_rim(surf, base_outline)


def _make():
    from game import store_skins
    return store_skins._make_skin(_paint, base_fn=_flesh_base)


build = _make()
