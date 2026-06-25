"""design_2 · PRISM LORIKEET — EPIC parrot-rarity exploration (scratch only).

The faceted/geometric parrot: hard crystalline geometry against the whole
tab's soft feathers. The R1 win was the 3-shard crest — it reads unmistakably
as crystal at 40px — so it's protected and sharpened here. The R2 work is
making the crystalline language carry BELOW the crown so the bird stops
reading as "lorikeet + spiky hat": LARGE flat facet planes split the
back/wing into a lit teal plane and an amethyst shadow plane with a single
white spine between them, the muddy multi-hue chest sparks are replaced by
two LARGE hard facet glints (one rose, one amethyst) that survive downscale,
the aviators regain a crystal tint + bright top rim with a sliver of sky
between lens and crest, and a pair of 4-point diamond sparkles drift off the
back into open sky.

The north star is "lives or dies at 40px": every signature is a flat fill
split by a hard white edge so it stays sharp and reads as polished geometry,
not feathers. Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import pygame

from game import store_skins
from game.store_skins import HX, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Crystal palette: cool teal mass, amethyst undertone, rose refraction, and a
# pure white facet glint that owns every sharp edge. The deep teal is the
# keyline that holds shards apart from sky and from the body mass.
_PRISM_TEAL   = (94, 215, 208)     # #5ED7D0 crystal teal
_PRISM_AMETH  = (185, 140, 240)    # #B98CF0 amethyst
_PRISM_ROSE   = (255, 154, 208)    # #FF9AD0 rose refraction
_PRISM_GLINT  = (255, 255, 255)    # facet glint
_PRISM_DEEP   = (46, 110, 120)     # #2E6E78 deep teal keyline


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


def _facet(surf, pts, fill, *, edge=_PRISM_GLINT, edge_w=2):
    """A flat crystal facet: a hard single-colour fill with a bright edge so
    it reads as polished geometry, not a feather. The white edge is what keeps
    the shard sharp once the sprite is downscaled to the store thumbnail; ≥2px
    by default so the edge survives the 40px downscale."""
    pygame.draw.polygon(surf, fill, pts)
    pygame.draw.polygon(surf, edge, pts, edge_w)


def _shard(surf, root, tip, half, *, light, dark, sky_edge=False):
    """One angular crystal shard from `root` up to `tip`, split down the spine
    into a lit face and a shadowed face so it reads as a 3-D faceted prism. A
    full-white spine highlight runs root→tip as the hero edge that survives
    40px. When `sky_edge`, a deep-teal keyline traces the outer edges so the
    shard tip holds against bright day sky instead of dropping out."""
    rx, ry = root
    tx, ty = tip
    # Two faces meeting at the spine; the base is `half` wide each side of root.
    left = [(rx - half, ry), (rx, ry - 1), (tx, ty)]
    right = [(rx, ry - 1), (rx + half, ry), (tx, ty)]
    _facet(surf, left, dark, edge_w=1)
    _facet(surf, right, light, edge_w=1)
    if sky_edge:
        # Deep-teal outline on the sky-facing edges so the point doesn't vanish.
        pygame.draw.line(surf, _PRISM_DEEP, (rx - half, ry), (tx, ty), 1)
        pygame.draw.line(surf, _PRISM_DEEP, (rx + half, ry), (tx, ty), 1)
    # Full-white spine — the brightest, sharpest edge, drawn last so it owns the
    # centre of the shard at any size.
    pygame.draw.line(surf, _PRISM_GLINT, (rx, ry - 1), (tx, ty), 2)


def _diamond(surf, cx, cy, r, fill):
    """A floating refraction diamond (rotated square) with a white core glint —
    the aura sparkle that scatters off the back. The white core is ≥2px so it
    holds the 'crystal sparkle' read at thumbnail size."""
    _facet(surf, [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill,
           edge_w=1)
    pygame.draw.circle(surf, _PRISM_GLINT, (cx, cy), 2)


def _paint_prism(surf, _a):
    base_y = CROWN_Y + 4   # roots just above the crystal crown

    # 1 · BODY FACET PLANES (painted first, under the crest, so the crystalline
    #     language carries below the crown). Two LARGE flat planes split the
    #     back/wing into a lit teal face and an amethyst shadow face, divided by
    #     a single hard white spine — the same faceted grammar as the crest, so
    #     the whole bird reads as cut crystal, not a soft body wearing a hat.
    spine = [(20, 39), (31, 45), (43, 47)]   # back ridge, up-right toward wing
    lit = [(20, 39), (31, 45), (43, 47), (40, 53), (28, 52), (18, 46)]
    shadow = [(20, 39), (18, 46), (14, 50), (16, 41)]
    _facet(surf, lit, (110, 224, 216), edge_w=1)         # lit teal plane
    _facet(surf, shadow, (108, 92, 168), edge_w=1)       # amethyst shadow plane
    pygame.draw.lines(surf, _PRISM_GLINT, False, spine, 2)  # the white spine

    # 2 · CHEST/WING GLINTS: replace the R1 muddy multi-hue specks with TWO
    #     LARGE hard facets — one rose, one amethyst — each a flat triangle with
    #     a ≥2px white edge, pointed like the crest shards. Two notes, two hues:
    #     the spectrum tell without scattering into mud at 40px.
    _facet(surf, [(28, 49), (35, 54), (27, 58)], _PRISM_ROSE)      # chest rose
    _facet(surf, [(40, 43), (47, 46), (40, 51)], _PRISM_AMETH)     # wing amethyst

    # 3 · HERO: 3 angular crystal shards fanning up PAST the crown — the R1 win,
    #     protected. The centre shard is tallest and the outer two splay out so
    #     the cluster reads as a gem cluster breaking the silhouette. The
    #     right-most shard gets the deep-teal sky-edge so its tip holds on day
    #     sky (R1 it dropped out). Painted after the body so it sits on top.
    shards = (
        (HX - 7, base_y + 1, HX - 13, base_y - 14, 4, _PRISM_AMETH, _PRISM_DEEP, False),
        (HX - 1, base_y,     HX - 2,  base_y - 24, 5, _PRISM_TEAL,  _PRISM_DEEP, True),
        (HX + 6, base_y + 1, HX + 12, base_y - 16, 4, _PRISM_ROSE,  _PRISM_DEEP, True),
    )
    for rx, ry, tx, ty, half, light, dark, sky_edge in shards:
        _shard(surf, (rx, ry), (tx, ty), half, light=light, dark=dark,
               sky_edge=sky_edge)
    # A small teal facet seats the cluster onto the crown so it reads anchored,
    # leaving a sliver of body between the crown facet and the aviator top rim.
    _facet(surf, [(HX - 9, base_y + 2), (HX + 8, base_y + 2),
                  (HX + 5, base_y - 3), (HX - 6, base_y - 3)], _PRISM_TEAL,
           edge_w=1)

    # 4 · AVIATOR RE-READ: a 1px bright top rim across both lenses so Pip's
    #     signature glasses catch the light again under the crest. A faint
    #     crystal tint already lives in the palette lens_tint; the rim is the
    #     hard top edge that separates lens from face at a glance.
    pygame.draw.line(surf, (214, 250, 246), (40, 44), (46, 44), 2)
    pygame.draw.line(surf, (214, 250, 246), (49, 44), (54, 44), 2)

    # 5 · AURA: two 4-point diamond sparkles drifting off the back into OPEN sky
    #     (kept off the near-black card edge), white cores ≥2px so they read as
    #     scattered crystal light, not body marks. Held to two so the bird stays
    #     epic, not legendary.
    _diamond(surf, HX - 19, CROWN_Y + 5, 3, _PRISM_ROSE)
    _diamond(surf, HX - 24, CROWN_Y + 15, 2, _PRISM_TEAL)


# Body recolour through the palette system + the crystal overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_prism,
    base_fn=lambda a: _build_parrot_with_palette(a, P_PRISM),
)
