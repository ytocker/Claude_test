"""design_2 · PRISM LORIKEET — EPIC parrot-rarity exploration (scratch only).

The faceted/geometric parrot: hard crystalline geometry against the whole
tab's soft feathers. Pip keeps his aviators (tinted crystal-teal) and a
cool crystal-teal body with an amethyst undertone, then ONE bold signature
zone carries the 40px read — a cluster of 3 angular CRYSTAL SHARDS fanning
up past the crown. Sharp flat facets with bright white edge highlights, NOT
plumes; prismatic refraction glints (teal→amethyst→rose triangular sparks)
on the chest + wing; and 2-3 floating diamond sparkles off the back.

The north star is "lives or dies at 40px": the shard crest breaks the
silhouette above the crown, and each facet is a flat fill split by a hard
white edge so it stays sharp and readable when downscaled. Exploration
only — NEVER registered in store_skins.BUILDERS.
"""
import pygame

from game import store_skins
from game.store_skins import HX, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Crystal palette: cool teal mass, amethyst undertone, rose refraction, and a
# pure white facet glint that owns every sharp edge.
_PRISM_TEAL   = (94, 215, 208)     # #5ED7D0 crystal teal
_PRISM_AMETH  = (185, 140, 240)    # #B98CF0 amethyst
_PRISM_ROSE   = (255, 154, 208)    # #FF9AD0 rose refraction
_PRISM_GLINT  = (255, 255, 255)    # facet glint
_PRISM_DEEP   = (46, 110, 120)     # #2E6E78 deep teal


# Full crystal-teal re-plumage with an amethyst undertone: the tail/wing line
# work runs the deepest teal so facets read against the body, the chest carries
# the amethyst shift, and aviators are RETAINED (tinted crystal-teal — Pip's
# signature) rather than dropped, since the shard crest owns the silhouette.
P_PRISM = _pal(
    tail=[(36, 92, 102), (52, 132, 134), (78, 178, 176), (118, 210, 204)],
    tail_line=_PRISM_DEEP,
    body_shadow=(40, 100, 110),
    body_main=_PRISM_TEAL,
    body_chest=(150, 196, 224),       # cooled amethyst-leaning chest
    body_belly=(132, 224, 216),
    sheen=(230, 248, 255, 110),
    wing_main=(70, 176, 178),
    wing_dark=_PRISM_DEEP,
    wing_tip=(150, 232, 224),
    wing_secondary=(150, 122, 210),   # amethyst secondary so the wing refracts
    wing_highlight=(214, 250, 246),
    head_shadow=(40, 100, 110),
    head_main=_PRISM_TEAL,
    head_cheek=(132, 224, 216),
    head_crown=(120, 206, 224),
    lens_frame=(150, 122, 210),       # amethyst rims keep the aviators on-theme
    lens_body=(24, 40, 56),
    lens_tint=(120, 220, 220, 130),
    lens_glint=(255, 255, 255),
    beak_main=(120, 210, 210),
    beak_dark=_PRISM_DEEP,
    beak_gloss=(220, 250, 248),
    foot=(70, 140, 150),
)


def _facet(surf, pts, fill, *, edge=_PRISM_GLINT, edge_w=1):
    """A flat crystal facet: a hard single-colour fill with a bright edge so
    it reads as polished geometry, not a feather. The white edge is what keeps
    the shard sharp once the sprite is downscaled to the store thumbnail."""
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, edge, pts, edge_w)


def _shard(surf, root, tip, half, *, light, dark):
    """One angular crystal shard from `root` up to `tip`, split down the spine
    into a lit face and a shadowed face so it reads as a 3-D faceted prism. A
    white spine highlight runs root→tip as the hero edge that survives 40px."""
    rx, ry = root
    tx, ty = tip
    # Two faces meeting at the spine; the base is `half` wide each side of root.
    _facet(surf, [(rx - half, ry), (rx, ry - 1), (tx, ty)], dark, edge_w=1)
    _facet(surf, [(rx, ry - 1), (rx + half, ry), (tx, ty)], light, edge_w=1)
    pygame.draw.line(surf, _PRISM_GLINT, (rx, ry - 1), (tx, ty), 1)
    pygame.draw.line(surf, _PRISM_GLINT, (tx, ty), (tx, ty + 3), 1)


def _diamond(surf, cx, cy, r, fill):
    """A floating refraction diamond (rotated square) with a white core glint —
    the aura sparkle that scatters off the back."""
    _facet(surf, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill,
           edge_w=1)
    pygame.draw.circle(surf, _PRISM_GLINT, (cx, cy), 1)


def _paint_prism(surf, _a):
    base_y = CROWN_Y + 4   # roots just above the crystal crown

    # 1 · HERO: 3 angular crystal shards fanning up PAST the crown. The centre
    #     shard is tallest and the outer two splay out so the cluster reads as a
    #     gem cluster breaking the silhouette, not a feather plume. Lit faces are
    #     teal, shadowed faces deep-teal, with amethyst/rose tips for refraction.
    shards = (
        (HX - 7, base_y + 1, HX - 13, base_y - 14, 4, _PRISM_AMETH, _PRISM_DEEP),
        (HX - 1, base_y,     HX - 2,  base_y - 24, 5, _PRISM_TEAL,  _PRISM_DEEP),
        (HX + 6, base_y + 1, HX + 12, base_y - 16, 4, _PRISM_ROSE,  _PRISM_DEEP),
    )
    for rx, ry, tx, ty, half, light, dark in shards:
        _shard(surf, (rx, ry), (tx, ty), half, light=light, dark=dark)
    # A small teal facet seats the cluster onto the crown so it reads anchored.
    _facet(surf, [(HX - 9, base_y + 2), (HX + 8, base_y + 2),
                  (HX + 5, base_y - 3), (HX - 6, base_y - 3)], _PRISM_TEAL)

    # 2 · Prismatic refraction glints on the CHEST — three hard triangular
    #     sparks cycling teal→amethyst→rose, the spectrum tell that nothing
    #     else on the tab has. Each is a tiny flat facet with a white edge.
    chest = (
        (26, 50, _PRISM_TEAL),
        (32, 55, _PRISM_AMETH),
        (24, 58, _PRISM_ROSE),
    )
    for cx, cy, col in chest:
        _facet(surf, [(cx, cy - 3), (cx + 3, cy + 2), (cx - 3, cy + 2)], col)

    # 3 · One bright triangular refraction spark on the WING leading edge so the
    #     faceted read reaches the wing too.
    _facet(surf, [(40, 44), (45, 47), (40, 49)], _PRISM_AMETH)
    pygame.draw.line(surf, _PRISM_ROSE, (40, 44), (45, 47), 1)

    # 4 · AURA: floating diamond sparkles drifting off the back into open sky,
    #     decreasing in size so they read as scattered light, not body marks.
    _diamond(surf, HX - 20, CROWN_Y + 6, 3, _PRISM_ROSE)
    _diamond(surf, HX - 25, CROWN_Y + 16, 2, _PRISM_TEAL)
    _diamond(surf, HX - 16, CROWN_Y + 22, 2, _PRISM_AMETH)


# Body recolour through the palette system + the crystal overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_prism,
    base_fn=lambda a: _build_parrot_with_palette(a, P_PRISM),
)
