"""design_1 · THORNCREST MACAW — EPIC parrot-wave2 exploration (scratch only).

The tab's only BOTANICAL parrot: a deep rose-red macaw with a wild briar-rose
growing out of his head. The read is one hero shape — a single arching bramble
cane springing up-and-back past the crown, studded with hard ivory thorns and
capped by one bloomed heraldic rose that juts past the silhouette. It says "the
bird with a rose growing out of its head" before you can read any detail.

North star is "lives or dies at 40px". The cane is dark briar-green (a value
break against both the rose body and the sky), the thorns are pure ivory (the
one bright spec on the green that survives downscale), and the bloom is a tight
crimson→blush 5-petal whorl with ONE bright highlight petal so the flower reads
as a flower, not a red dot. Everything below the crown is held to ONE accent per
zone — a shoulder cane-wrap with two small leaf pairs + a bud, and a thin
thorn-line ticking the wing leading edge — so nothing busies the 40px crest read.

Matte pigment throughout, NO glow: the warmth is pure local colour so it can
never be confused with wave-1's emissive MAGMA / SOLAR. PRISM model — crest,
thorns, bloom, leaves are all polygons + lines over a rose recolour; no
back-layer is needed. Exploration only — NEVER registered in store_skins.BUILDERS.
"""
import pygame

from game import store_skins
from game.store_skins import HX, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Thorncrest palette — deep rose-red body with a wine shadow that owns the line
# work, a blush belly/petal-highlight bright, dark briar-green for the vine so it
# reads as botanical structure (not a feather), and pure ivory for thorns + petal
# spec. Warmth is bought with saturated local RED, never emission, so it stays
# clear of MAGMA/SOLAR.
# R2: the body skewed dark maroon/liver on bright DAY sky at 40px. The body
# slots are lifted ~12% in value + saturation toward a punchier rose so he reads
# clearly ROSE-red on BOTH skies — the spec hex #B5294A is kept as the named
# brand colour but the working body_main is the lifted tone. Wine shadow stays
# deep so the dark→light ramp survives.
_TC_ROSE   = (181, 41, 74)         # #B5294A rose-red body (brand reference)
_TC_ROSE_HI = (205, 52, 88)        # lifted working rose — reads on bright day sky
_TC_WINE   = (122, 23, 48)         # #7A1730 wine shadow / keyline
_TC_BLUSH  = (242, 182, 196)       # #F2B6C4 blush belly + petal highlight
_TC_GREEN  = (47, 107, 58)         # #2F6B3A briar green (the cane)
_TC_GREEN_D = (30, 72, 40)         # deep briar shadow under the cane
_TC_GREEN_H = (104, 168, 96)       # leaf/cane lit edge so the vine reads round
_TC_IVORY  = (239, 231, 210)       # #EFE7D2 ivory thorn + petal spec
_TC_CRIMSON = (200, 38, 66)        # bloom mid — between rose body + wine core
_TC_AMBER  = (232, 150, 120)       # rose-amber aviator tint warmth


# Full rose-red re-plumage. The shadow slots run deep wine so the body already
# carries a dark→light range (the crest sits on a saturated, not pale, head); the
# belly + chest stay blush so the rose-bloom highlight echoes down the body. Briar
# green is deliberately kept OUT of the base plumage — it belongs only to the
# overlaid vine so the cane reads as a separate growing thing, not a feather.
# Aviators retinted rose-amber (warm, the brief's "leaf glint" lands in overlay).
P_THORNCREST = _pal(
    tail=[(96, 20, 42), (140, 30, 58), (176, 46, 76), (206, 96, 118)],
    tail_line=_TC_WINE,
    body_shadow=(132, 30, 56),
    body_main=_TC_ROSE_HI,
    body_chest=(222, 122, 144),
    body_belly=_TC_BLUSH,
    sheen=(255, 224, 230, 130),
    wing_main=(188, 46, 82),
    wing_dark=(110, 24, 46),
    wing_tip=(228, 156, 174),
    wing_secondary=None,               # single-hue rose — no contrast feather
    wing_highlight=(238, 188, 200),
    head_shadow=(132, 30, 56),
    head_main=_TC_ROSE_HI,
    head_cheek=(220, 130, 150),
    head_crown=(206, 80, 108),
    lens_frame=(214, 132, 110),        # warm rose-amber rims
    lens_body=(58, 24, 30),
    lens_tint=(232, 150, 120, 130),    # rose-amber lens tint
    lens_glint=(255, 244, 230),
    beak_main=(228, 160, 150),
    beak_dark=(150, 70, 60),
    beak_gloss=(255, 244, 232),
    foot=(150, 70, 64),
)


def _thorn(surf, bx, by, dx, dy):
    """One hard ivory thorn springing off the OUTER (convex) edge of the cane at
    (bx,by) toward (bx+dx, by+dy). R2: enlarged to a wide ≥3px base + a fat ivory
    body so it reads as an unmistakable outward spike that breaks the green
    silhouette at 40px (the R1 thorns dissolved). A wine-dark backing + keyline
    seats it on the cane and gives the bright/dark value jump that survives
    downscale."""
    # A wide base perpendicular to the spike direction so the triangle is fat,
    # not a hairline. 3px each side of root → 6px base.
    if abs(dx) >= abs(dy):
        b0, b1 = (bx, by - 3), (bx, by + 3)
    else:
        b0, b1 = (bx - 3, by), (bx + 3, by)
    tip = (bx + dx, by + dy)
    # Dark backing offset 1px outward = a hard shadow rim under the bright thorn.
    sx = 1 if dx >= 0 else -1
    sy = 1 if dy >= 0 else -1
    pygame.draw.polygon(surf, _TC_GREEN_D,
                        [(b0[0] + sx, b0[1] + sy), (b1[0] + sx, b1[1] + sy),
                         (tip[0] + sx, tip[1] + sy)])
    pygame.draw.polygon(surf, _TC_IVORY, [b0, b1, tip])
    pygame.draw.line(surf, _TC_WINE, b0, tip, 1)             # crisp keyline edge


def _leaf(surf, cx, cy, dx, dy):
    """A small briar leaf — a green lozenge with a lit upper edge + a midrib, so
    the shoulder cane-wrap reads as foliage at hero size without adding clutter
    at 40px (it just reads as a green tick on the shoulder)."""
    tip = (cx + dx, cy + dy)
    base = (cx - dx // 2, cy - dy // 2)
    side = (cx + dy // 2, cy - dx // 2)
    side2 = (cx - dy // 2, cy + dx // 2)
    pygame.draw.polygon(surf, _TC_GREEN, [base, side, tip, side2])
    pygame.draw.line(surf, _TC_GREEN_H, base, side, 1)       # lit upper edge
    pygame.draw.line(surf, _TC_GREEN_D, base, tip, 1)        # midrib


def _bloom(surf, cx, cy):
    """The hero rose at the cane tip — a tight 5-petal heraldic whorl, crimson on
    the outer ring fading to a wine core, with ONE bright blush highlight petal +
    an ivory spec so it reads unmistakably as a FLOWER (not a red dot) when small.
    The bloom is sized to JUT past the crown silhouette — the egg-breaking shape."""
    # Outer petal ring — five rounded petals around the core.
    petals = (
        (cx, cy - 6, 4),
        (cx + 6, cy - 2, 4),
        (cx + 4, cy + 5, 4),
        (cx - 4, cy + 5, 4),
        (cx - 6, cy - 2, 4),
    )
    for px, py, r in petals:
        pygame.draw.circle(surf, _TC_CRIMSON, (px, py), r)
        pygame.draw.circle(surf, _TC_WINE, (px, py), r, 1)   # petal separation
    # One bright highlight petal (upper-left) so the bloom catches light.
    pygame.draw.circle(surf, _TC_BLUSH, (cx - 4, cy - 4), 3)
    pygame.draw.circle(surf, _TC_WINE, (cx - 4, cy - 4), 3, 1)
    # Wine core whorl + an ivory spec centre — the flower's eye.
    pygame.draw.circle(surf, _TC_WINE, (cx, cy), 3)
    pygame.draw.circle(surf, _TC_CRIMSON, (cx, cy), 2)
    pygame.draw.circle(surf, _TC_IVORY, (cx - 1, cy - 1), 1)


def _paint_crest(surf):
    """The hero briar-cane crest. R2 re-anchor: the cane now EMERGES from the
    BACK of the crown — its root sits 3px INTO the skull silhouette behind the
    aviators (screen-left of the face) — and arches a SHORT way up-and-BACK so
    the rose sits just past the crown, not floating on a long wire. It stays
    entirely ABOVE and BEHIND the crown and never crosses the face. Drawn as a
    thick green stroke (dark under-stroke + lit over-stroke = a round woody cane)
    so it reads as one bold shape at thumbnail size."""
    # Root buried in the back-skull (behind the aviators at ~x50), arching up and
    # back toward the tail. ~35% shorter reach than R1 so the bloom lands close
    # to the crown — "rose growing out of his head", not held aloft.
    cane = [
        (HX - 6, CROWN_Y + 4),     # root, 3px into the back of the skull
        (HX - 9, CROWN_Y - 1),
        (HX - 12, CROWN_Y - 6),    # apex of the short arch
        (HX - 14, CROWN_Y - 9),    # neck into the bloom
    ]
    bloom_c = (HX - 16, CROWN_Y - 13)

    # A wine-dark briar-edge UNDER-stroke (also the red/green separation line that
    # stops the complementary colours shimmering at 40px), then the green cane
    # body, then a lit over-stroke so the stem reads round and woody.
    pygame.draw.lines(surf, _TC_WINE, False, cane, 6)
    pygame.draw.lines(surf, _TC_GREEN_D, False, cane, 5)
    pygame.draw.lines(surf, _TC_GREEN, False, cane, 3)
    pygame.draw.lines(surf, _TC_GREEN_H, False, cane[:2], 1)   # lit base highlight

    # 2 fat ivory thorns on the OUTER (convex, sky-facing screen-left) edge of the
    # arch so they break the green silhouette as hard outward spikes. Two clean
    # beats three muddy at 40px (R2 fix).
    _thorn(surf, HX - 10, CROWN_Y - 2, -5, -3)
    _thorn(surf, HX - 13, CROWN_Y - 7, -5, -1)

    # The hero bloom caps the tip, sitting just past the crown.
    _bloom(surf, *bloom_c)


def _paint_thorncrest(surf, _a, *, crest=True):
    # BODY ACCENT — ONE per zone so nothing competes with the crest at 40px.

    # 1 · SHOULDER ACCENT — cut to ONE clean note (R2): a short green wrap stub
    #     carrying a SINGLE small leaf-pair near where the cane meets the back, so
    #     the vine reads as part of the bird without the R1 leaf-cluster collapsing
    #     into a dark smear over the wine shadow at 40px. A wine-dark briar-edge
    #     under-stroke separates the green from the red so the complementary pair
    #     doesn't shimmer (and reads for colourblind players).
    wrap = [(38, 43), (33, 46)]
    pygame.draw.lines(surf, _TC_WINE, False, wrap, 5)
    pygame.draw.lines(surf, _TC_GREEN_D, False, wrap, 4)
    pygame.draw.lines(surf, _TC_GREEN, False, wrap, 2)
    _leaf(surf, 36, 44, 3, -4)
    _leaf(surf, 35, 47, -2, 4)

    # 2 · WING LEADING-EDGE THORN-LINE: a single thin briar line ticking down the
    #     wing's leading edge with three tiny thorn flicks — one accent that reads
    #     as the vine grazing the wing, not a second busy zone. A wine under-stroke
    #     keeps the green off the red without shimmer.
    edge = [(44, 40), (40, 37), (35, 35)]
    pygame.draw.lines(surf, _TC_WINE, False, edge, 3)
    pygame.draw.lines(surf, _TC_GREEN, False, edge, 2)
    for tx, ty in edge:
        pygame.draw.line(surf, _TC_IVORY, (tx, ty), (tx - 2, ty - 2), 1)

    # 3 · AVIATOR LEAF GLINT: a tiny green leaf-tick glinting on the upper rim of
    #     the near lens so the rose-amber aviators tie into the botanical theme
    #     (the palette already warms the lens; this is the single themed accent).
    _leaf(surf, 52, 39, 2, -3)

    # 4 · HERO CREST — the briar-cane + thorns + bloom. Split into its own helper
    #     so the round sheet can render a crest-masked proof that the rose body
    #     alone holds its silhouette on both skies.
    if crest:
        _paint_crest(surf)


# Body recolour through the palette system + the briar overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_thorncrest,
    base_fn=lambda a: _build_parrot_with_palette(a, P_THORNCREST),
)

# Crest-masked variant — the SAME skin with the briar crest suppressed, so the
# round sheet can prove the rose body alone holds its silhouette on both skies.
# Exploration harness only; never a shippable skin.
build_no_crest = store_skins._make_skin(
    lambda s, a: _paint_thorncrest(s, a, crest=False),
    base_fn=lambda a: _build_parrot_with_palette(a, P_THORNCREST),
)
