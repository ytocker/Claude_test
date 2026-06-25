"""design_3 · EMBERMOTH MACAW — EPIC parrot-wave2 exploration (scratch only).

The tab's only ENTOMOLOGY parrot: Pip "ascended" into a night-moth. The read is
one hero shape — a single forked moth-antenna plume sweeping up-and-back past the
crown like a luna-moth feeler, anchored by a bold eyespot disc where the plume
roots into the skull. It says "the bird that turned into a moth" before any
detail resolves.

North star is "lives or dies at 40px". The body is a velvety charcoal-mauve so it
reads DARK on bright day sky and the warm dusty-rose breast keeps it from going to
a void on navy night sky. The plume is a flat feathered comb-edge with hard ≥3px
teeth so it survives the downscale as a ragged fan that breaks the egg at the
top-rear corner. The one guaranteed-survives tell is the eyespot disc — a dark
ring + a cream pupil at the plume root, the single highest-contrast spot that
carries the read when everything else dissolves.

Matte pigment throughout, NO glow: the warmth is pure local colour (ember accent
on the wing edge, cream plume tips) so it never reads as wave-1's emissive
MAGMA/SOLAR. PRISM model — plume + eyespot are polygons + lines over a
charcoal-mauve recolour; no back-layer is needed. Exploration only — NEVER
registered in store_skins.BUILDERS.
"""
import pygame

from game import store_skins
from game.store_skins import HX, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Embermoth palette — a charcoal-mauve velvet body whose shadow slots stay deep so
# the whole bird reads as a dark moth-silhouette on bright sky, lifted only on the
# breast into a warm dusty-rose so it does not collapse to a void on navy. Cream
# is the one bright accent (eyespot pupil + plume tips), the plume body is a near-
# black mauve so the comb-teeth read against the sky, and a single warm ember note
# rides the wing leading edge. Warmth is bought with local colour, never emission.
_EM_BASE   = (43, 34, 48)          # #2B2230 charcoal-mauve base
_EM_BASE_D = (30, 23, 34)          # deeper mauve shadow slot (UPPER body / head)
# The LOWER-body shadow (tail + underbelly crescent) is lifted ~16% so the
# silhouette's bottom does not void out against navy night sky — kept separate
# from the upper-body shadow so the day-sky dark read is untouched up top.
_EM_FLOOR  = (46, 36, 52)          # lifted tail/underwing shadow floor
_EM_RIM    = (96, 58, 74)          # dark-mauve→rose rim along the bottom tail edge
_EM_ROSE   = (110, 74, 85)         # #6E4A55 dusty-rose breast
_EM_ROSE_H = (150, 104, 116)       # lit dusty-rose so the breast reads warm
_EM_CREAM  = (232, 197, 138)       # #E8C58A cream eyespot pupil + plume tips
_EM_PLUME  = (58, 44, 64)          # #3A2C40 plume body / eyespot dark ring
_EM_PLUME_D = (34, 26, 38)         # plume keyline / ring shadow
_EM_PLUME_H = (96, 78, 104)        # lit plume edge so the fronds read round
_EM_EMBER  = (199, 122, 90)        # #C77A5A warm ember accent on the wing edge
_EM_AMBER  = (168, 106, 60)        # #A86A3C smoked-amber aviator tint


# Full charcoal-mauve re-plumage. Shadow slots run deep so the body carries a
# dark→light range and the dark moth-silhouette reads on bright day sky; the
# chest/belly lift into dusty-rose so the bird stays warm and present on navy
# night sky. Cream is kept OUT of the base plumage — it belongs only to the
# overlaid eyespot + plume tips so those tells own the one bright value. Aviators
# retinted smoked amber (warm, in-key with the ember wing accent).
P_EMBERMOTH = _pal(
    tail=[(46, 36, 52), (56, 44, 64), (70, 52, 74), (94, 66, 82)],
    tail_line=_EM_PLUME_D,
    body_shadow=_EM_FLOOR,             # lifted lower-body floor (not the void)
    body_main=_EM_BASE,
    body_chest=_EM_ROSE,
    body_belly=_EM_ROSE_H,
    sheen=(180, 150, 165, 70),
    wing_main=(50, 39, 56),
    wing_dark=(30, 23, 34),
    wing_tip=(132, 92, 104),
    wing_secondary=None,               # single-hue velvet — no contrast feather
    wing_highlight=(118, 92, 110),
    head_shadow=_EM_BASE_D,
    head_main=_EM_BASE,
    head_cheek=(96, 70, 84),
    head_crown=(64, 50, 70),
    lens_frame=(176, 120, 86),         # warm smoked-amber rims
    lens_body=(34, 26, 32),
    lens_tint=(168, 106, 60, 120),     # smoked-amber lens tint
    lens_glint=None,                   # drawn in the overlay, shrunk to 1px so the
                                       # eyespot stays the brightest head-zone value
    beak_main=(186, 132, 110),
    beak_dark=(120, 74, 62),
    beak_gloss=(248, 226, 206),
    foot=(120, 80, 76),
)


def _frond(surf, base, tip, ctrl, teeth):
    """One feathered frond of the antenna-plume — a tapered dark spine from `base`
    toward `tip` (bowed through `ctrl`), combed on its OUTER edge with hard cream-
    tipped teeth. Each tooth is a fat ≥3px wedge so the frond survives the
    downscale as a ragged comb, not a smooth blade — the luna-moth feeler read.
    `teeth` is a list of (anchor_t, dx, dy): a point along the spine (0→1) and the
    outward direction of that tooth."""
    bx, by = base
    tx, ty = tip
    cx, cy = ctrl

    def _spine(t):
        # Quadratic bezier so the frond bows back like a real feeler.
        u = 1 - t
        return (u * u * bx + 2 * u * t * cx + t * t * tx,
                u * u * by + 2 * u * t * cy + t * t * ty)

    spine = [_spine(i / 12) for i in range(13)]
    # A dark under-stroke + plume-body spine + a lit edge so the frond reads as a
    # round feathered shaft and seats hard against the sky on both biomes.
    pygame.draw.lines(surf, _EM_PLUME_D, False, spine, 5)
    pygame.draw.lines(surf, _EM_PLUME, False, spine, 3)
    pygame.draw.lines(surf, _EM_PLUME_H, False, spine, 1)

    # Hard comb teeth along the outer edge — dark wedge backing + a cream tip so
    # each tooth carries the bright/dark value jump that survives 40px.
    for at, dx, dy in teeth:
        ax, ay = _spine(at)
        # A perpendicular base so the wedge is fat (≥3px), not a hairline.
        if abs(dx) >= abs(dy):
            b0, b1 = (ax, ay - 2), (ax, ay + 2)
        else:
            b0, b1 = (ax - 2, ay), (ax + 2, ay)
        ttip = (ax + dx, ay + dy)
        pygame.draw.polygon(surf, _EM_PLUME, [b0, b1, ttip])
        pygame.draw.line(surf, _EM_PLUME_D, b0, ttip, 1)
        # Cream caps the outer third of the tooth so the comb sparkles like dusted
        # moth-scales without losing the dark seat. A 3px tip-line so the ragged-
        # feeler read survives the navy downscale, where a 2px cream wash dissolved.
        midx = ax + dx * 0.50
        midy = ay + dy * 0.50
        pygame.draw.line(surf, _EM_CREAM, (midx, midy), ttip, 3)


def _eyespot(surf, cx, cy):
    """The hero eyespot disc on the crest — a hard near-black ring + warm-cream
    pupil, the one tell guaranteed to survive the 40px read. It is grown and
    hardened so that at 40px it resolves as an unmistakable ~5px bright core inside
    a hard dark ring — bigger than either aviator glint, so it out-values
    everything in the head zone. A moth ocellus, not a wet eye: matte cream pupil,
    no emissive bloom, so it stays pigment-finish in key with the truth tiles."""
    pygame.draw.circle(surf, _EM_ROSE, (cx, cy), 9)        # warm halo seat
    pygame.draw.circle(surf, _EM_PLUME_D, (cx, cy), 8)     # dark ring (outer)
    pygame.draw.circle(surf, (14, 10, 16), (cx, cy), 7)    # near-black ring core
    pygame.draw.circle(surf, _EM_CREAM, (cx, cy), 4)       # warm-cream pupil
    pygame.draw.circle(surf, _EM_EMBER, (cx, cy), 4, 1)    # ember inner rim
    # A single off-centre cream lift (no white pinprick) keeps the pupil round
    # without reading as a glossy/emissive glint at hero size.
    pygame.draw.circle(surf, (244, 218, 168), (cx - 1, cy - 1), 1)


def _paint_crest(surf):
    """The hero forked antenna-plume. It roots into the BACK of the crown (screen-
    left of the face, up-and-back toward the tail) and FORKS into two unequal
    fronds that fan past the silhouette like a luna-moth feeler — deliberately not
    symmetric horns, so it reads moth, not antlers. The longer rear frond sweeps
    furthest back to break the egg at the top-rear corner; the shorter inner frond
    fans up so the pair reads as a feather, not a single quill. The eyespot disc
    caps the root as the carry-the-read anchor."""
    root = (HX - 6, CROWN_Y + 5)       # buried 3px into the back of the skull

    # Longer outer frond — sweeps up-and-back furthest, the egg-breaker. More comb
    # teeth (5) on its OUTER (sky-facing, screen-left/up) edge so the ragged-feeler
    # read survives navy — the comb is what separates this from THORNCREST's smooth
    # briar crest.
    _frond(
        surf, root, (HX - 22, CROWN_Y - 14), (HX - 16, CROWN_Y - 2),
        teeth=[(0.22, -5, -1), (0.38, -6, -2), (0.54, -6, -2),
               (0.70, -5, -3), (0.86, -4, -4)],
    )
    # Shorter inner frond — fans up-and-slightly-back, narrower, so the two fronds
    # read as ONE forked feeler rather than twin horns. Extra tooth so it stays
    # ragged at 40px too.
    _frond(
        surf, root, (HX - 11, CROWN_Y - 17), (HX - 9, CROWN_Y - 5),
        teeth=[(0.34, -4, -2), (0.50, -4, -3), (0.66, -4, -4), (0.82, -3, -4)],
    )

    # The eyespot ocellus sits UP on the crest, in the fork of the two fronds —
    # a moth eyespot lives on the plume, not beside the real eye. Pulled up-and-
    # back off the brow so it clears the aviator eye by ≥8px and reads as crest
    # ornament. Drawn LAST so it sits clean over the spines where they fork.
    _eyespot(surf, HX - 8, CROWN_Y - 3)


def _paint_embermoth(surf, _a, *, crest=True):
    # AVIATOR GLINTS — kept but shrunk to 1px specs (the base palette glint is
    # suppressed) so the crest eyespot, not the shades, is the unambiguous
    # brightest point in the head zone at 40px. One spec per lens, the rear lens
    # dimmer so a single bright head-zone value belongs to the ocellus.
    pygame.draw.circle(surf, (224, 200, 174), (44, 18), 1)
    pygame.draw.circle(surf, (196, 174, 152), (54, 16), 1)

    # BODY ACCENT — ONE per zone so nothing competes with the crest at 40px.

    # 1 · WING LEADING-EDGE EMBER LINE: a single warm ember rim along the wing's
    #     top edge — the brief's one body accent — so the velvet wing carves off
    #     the dark body as a warm-lit plane and the flap stays legible. A dark
    #     under-stroke seats the ember so it never shimmers against the mauve.
    edge = [(46, 41), (40, 38), (34, 36)]
    pygame.draw.lines(surf, _EM_PLUME_D, False, edge, 3)
    pygame.draw.lines(surf, _EM_EMBER, False, edge, 2)

    # 1b· BOTTOM TAIL RIM: a thin dark-mauve→rose rim ticking the lower tail edge
    #     so the silhouette keeps a hard bottom edge on navy night sky — the lifted
    #     floor stops the void but the rim is what gives the tail tip a crisp seam
    #     the eye can still find against navy.
    rim = [(6, 38), (12, 40), (20, 39), (24, 36)]
    pygame.draw.lines(surf, _EM_PLUME_D, False, rim, 2)
    pygame.draw.lines(surf, _EM_RIM, False, rim, 1)

    # 2 · BREAST SCALE-DUST: two faint cream stipples on the dusty-rose breast so
    #     the body reads as powdery moth-scale velvet at hero size without adding a
    #     busy second zone (they vanish to nothing at 40px, by design — the eyespot
    #     is the only bright tell that must survive).
    for sx, sy in ((33, 50), (38, 53)):
        pygame.draw.circle(surf, (210, 180, 158), (sx, sy), 1)

    # 3 · HERO CREST — the forked antenna-plume + eyespot. Split into its own
    #     helper so the round sheet can render a crest-masked proof that the
    #     charcoal-mauve body alone holds its silhouette on both skies.
    if crest:
        _paint_crest(surf)


# Body recolour through the palette system + the moth overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_embermoth,
    base_fn=lambda a: _build_parrot_with_palette(a, P_EMBERMOTH),
)

# Crest-masked variant — the SAME skin with the antenna-plume + eyespot
# suppressed, so the round sheet can prove the charcoal-mauve body alone holds its
# silhouette on both skies. Exploration harness only; never a shippable skin.
build_no_crest = store_skins._make_skin(
    lambda s, a: _paint_embermoth(s, a, crest=False),
    base_fn=lambda a: _build_parrot_with_palette(a, P_EMBERMOTH),
)
