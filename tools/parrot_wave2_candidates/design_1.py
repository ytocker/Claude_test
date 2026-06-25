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
_TC_ROSE   = (181, 41, 74)         # #B5294A rose-red body
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
    body_shadow=(120, 26, 50),
    body_main=_TC_ROSE,
    body_chest=(214, 110, 132),
    body_belly=_TC_BLUSH,
    sheen=(255, 220, 228, 120),
    wing_main=(168, 38, 70),
    wing_dark=_TC_WINE,
    wing_tip=(224, 150, 168),
    wing_secondary=None,               # single-hue rose — no contrast feather
    wing_highlight=(236, 184, 198),
    head_shadow=(120, 26, 50),
    head_main=_TC_ROSE,
    head_cheek=(214, 120, 142),
    head_crown=(196, 70, 98),
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
    """One hard ivory thorn: a slim wine-edged spike springing off the cane at
    (bx,by) toward (bx+dx, by+dy). Ivory fill with a wine keyline so the point
    breaks the cane outline AND survives 40px as the single bright on the green."""
    # Perpendicular base so the spike reads as a triangle rooted on the cane.
    if abs(dx) >= abs(dy):
        b0, b1 = (bx, by - 2), (bx, by + 2)
    else:
        b0, b1 = (bx - 2, by), (bx + 2, by)
    tip = (bx + dx, by + dy)
    pygame.draw.polygon(surf, _TC_GREEN_D, [b0, b1, tip])    # wine-dark root shade
    pygame.draw.polygon(surf, _TC_IVORY,
                        [(b0[0], b0[1]), (b1[0], b1[1]), tip])
    pygame.draw.line(surf, _TC_WINE, b0, tip, 1)             # one keyline edge


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
    """The hero briar-cane crest: one arching dark-green cane springing from the
    back of the crown, sweeping UP-and-BACK past CROWN_Y, studded with ivory
    thorns, and capped by the bloomed rose jutting past the silhouette. Drawn as
    a thick green stroke (dark under-stroke + lit over-stroke = a round cane) so
    it reads as a single bold shape — the whole skin's read — at thumbnail size."""
    # Cane path: roots behind the crown, arcs up-left-and-back, bloom at the tip.
    # Up-and-back = toward the tail (screen-left), so it clears the head clean.
    cane = [
        (HX + 6, CROWN_Y + 5),     # root, just behind the crown
        (HX + 2, CROWN_Y - 2),
        (HX - 4, CROWN_Y - 8),
        (HX - 10, CROWN_Y - 13),   # apex of the arch
        (HX - 15, CROWN_Y - 17),   # neck into the bloom
    ]
    bloom_c = (HX - 19, CROWN_Y - 20)

    # Dark under-stroke (the cane's shadow side) then a thinner lit over-stroke so
    # the cane reads as a rounded woody stem, not a flat line.
    pygame.draw.lines(surf, _TC_GREEN_D, False, cane, 5)
    pygame.draw.lines(surf, _TC_GREEN, False, cane, 3)
    pygame.draw.lines(surf, _TC_GREEN_H, False, cane[:3], 1)   # lit base highlight

    # 3 ivory thorns springing off the OUTER (sky-facing) side of the arch so they
    # break the cane outline against the sky — the bright spec read on the green.
    _thorn(surf, HX + 1, CROWN_Y - 2, -4, -3)
    _thorn(surf, HX - 6, CROWN_Y - 10, -4, -2)
    _thorn(surf, HX - 12, CROWN_Y - 15, -3, 0)

    # The hero bloom caps the tip.
    _bloom(surf, *bloom_c)


def _paint_thorncrest(surf, _a, *, crest=True):
    # BODY ACCENT — ONE per zone so nothing competes with the crest at 40px.

    # 1 · SHOULDER CANE-WRAP: a short green cane segment wrapping the shoulder,
    #     carrying two small leaf pairs + one bud, so the vine reads as part of the
    #     bird without busying the silhouette. Held low on the back/shoulder.
    wrap = [(40, 43), (33, 46), (26, 47)]
    pygame.draw.lines(surf, _TC_GREEN_D, False, wrap, 4)
    pygame.draw.lines(surf, _TC_GREEN, False, wrap, 2)
    # Two leaf pairs off the wrap.
    _leaf(surf, 37, 44, 3, -4)
    _leaf(surf, 36, 47, -2, 4)
    _leaf(surf, 30, 45, 3, -4)
    _leaf(surf, 29, 48, -2, 4)
    # One small bud (a wine teardrop in a green calyx) on the wrap tip.
    pygame.draw.circle(surf, _TC_GREEN, (26, 47), 3)
    pygame.draw.circle(surf, _TC_CRIMSON, (26, 46), 2)
    pygame.draw.circle(surf, _TC_IVORY, (25, 45), 1)

    # 2 · WING LEADING-EDGE THORN-LINE: a single thin briar line ticking down the
    #     wing's leading edge with three tiny thorn flicks — one accent that reads
    #     as the vine grazing the wing, not a second busy zone.
    edge = [(44, 40), (40, 37), (35, 35)]
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
