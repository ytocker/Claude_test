"""design_1 · GLACIER MACAW — EPIC parrot-wave2 exploration (scratch only).

The tab's only COLD parrot: a frozen counterpart to wave 1's hot MAGMA. The
read is single-hue ice — one cool blue mass, white frost as the only bright —
so it never collides with PRISM's rainbow refraction (PRISM = many hues split
by hard facets; GLACIER = one hue, soft frost crackle + sharp icicles).

North star is "lives or dies at 40px". The hero is a fan of icicle spikes
breaking the crown silhouette — the same egg-breaking move as PRISM's shards
or the cockatoo crest — but rendered as translucent ice: a cool blue body
with a pure-WHITE frost-rimed tip on every spike, because white-on-blue is the
one value jump that survives downscale. Everything below the crown (frost-rime
crackle on the wing/back, hard chest glints, frost-dipped tail) repeats that
white-on-ice grammar so the whole bird reads as frozen, not a blue bird in a
spiky hat. Exploration only — NEVER registered in store_skins.BUILDERS.

R2 — the day-sky fix. R1's body was an even pale wash that de-saturated into
the bright day sky + its own frost whites and half-dissolved at 40px. The cure
is VALUE, bought mono-hue (no second accent colour, so it stays apart from
PRISM): a genuinely dark glacier-shadow is painted down the back, lower wing,
and belly underside so the body carries a real dark→light gradient, plus a 1px
near-navy rim on the sky-facing edges (top of back, leading wing) that day sky
otherwise leaves bare. Crackle is thinned, chest chips consolidated, sparkles
pulled tight to the tail — the scattered fine detail was noise that flattened
apparent contrast at 1×. The jagged 4-spike crest is kept EXACTLY as-is.
"""
import pygame

from game import store_skins
from game.store_skins import HX, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Glacier palette: one cool ice-blue mass, a cyan-slate shadow that owns the
# line work, and pure frost-white as the single bright that every signature
# tip lands on. ICE_GLINT is the mid bright used where white would blow out.
# Mono-hue throughout — the cold read is bought with VALUE (a real dark→light
# ice gradient), never a second accent colour, so it stays distinct from PRISM.
_GL_ICE    = (169, 216, 232)       # #A9D8E8 glacier ice body
_GL_SHADOW = (95, 147, 176)        # #5F93B0 cyan-slate shadow / keyline
_GL_FROST  = (234, 246, 255)       # #EAF6FF frost white (the only bright)
_GL_GLINT  = (199, 236, 255)       # #C7ECFF ice glint (sub-white)
_GL_DEEP   = (62, 104, 134)        # deep slate — mid keyline
# R2: a genuinely DARK structural ice tone. The R1 body de-saturated into the
# day sky + frost whites and half-dissolved at 40px; this near-navy slate is
# painted along the back/lower-wing/belly underside so the body holds a real
# dark→light gradient and a hard sky-facing edge on day. Same hue family — it
# buys contrast with darkness, not a new colour.
_GL_ABYSS  = (34, 66, 96)          # deep glacier-shadow — the day-sky anchor
_GL_RIM    = (24, 50, 76)          # 1px sky-facing rim, tuned for bright day sky


# Full ice-blue re-plumage. R2 deepens every STRUCTURAL slot (body/head shadow,
# wing dark, darkest tail) toward the new abyss tone so the base build already
# carries a dark→light value range instead of an even pale wash; the overlay
# then paints the hard dark back/belly gradient + sky rim on top. The belly stays
# near-white frosted, aviators RETAINED tinted pale cyan (Pip's signature) since
# the icicle crest owns the silhouette. Mono-hue — value + frost, not colour.
P_GLACIER = _pal(
    tail=[(40, 76, 106), (96, 150, 178), (146, 196, 216), (188, 224, 238)],
    tail_line=_GL_RIM,
    body_shadow=(54, 96, 128),         # deeper so the body underside reads dark
    body_main=_GL_ICE,
    body_chest=(206, 234, 244),
    body_belly=(228, 244, 252),       # near-white frosted belly (kept for the gradient top)
    sheen=(255, 255, 255, 150),
    wing_main=(132, 184, 208),
    wing_dark=_GL_ABYSS,               # lower-wing structure now genuinely dark
    wing_tip=(206, 234, 246),
    wing_secondary=None,              # single-hue ice — no contrast feather
    wing_highlight=(232, 246, 255),
    head_shadow=(54, 96, 128),
    head_main=_GL_ICE,
    head_cheek=(206, 234, 244),
    head_crown=(196, 228, 242),
    lens_frame=(150, 196, 220),       # pale-cyan rims keep the aviators on-theme
    lens_body=(22, 38, 56),
    lens_tint=(150, 220, 240, 130),   # pale cyan lens tint
    lens_glint=(255, 255, 255),
    beak_main=(176, 210, 228),
    beak_dark=_GL_DEEP,
    beak_gloss=(236, 248, 255),
    foot=(96, 134, 160),
)


def _icicle(surf, root_x, root_y, tip_y, half, *, body, edge):
    """One translucent icicle spike: a narrow ice-blue triangle whose TIP is a
    pure-white frost cap, the only note that survives 40px. A thin slate frost
    edge traces the sky-facing sides so the point holds against bright day sky
    instead of dropping out; a 1px white inner highlight reads as the ice
    catching light down its spine."""
    tri = [(root_x - half, root_y), (root_x + half, root_y), (root_x, tip_y)]
    pygame.draw.polygon(surf, body, tri)
    # Slate keyline on the two sky-facing edges so the spike never vanishes.
    pygame.draw.line(surf, edge, (root_x - half, root_y), (root_x, tip_y), 1)
    pygame.draw.line(surf, edge, (root_x + half, root_y), (root_x, tip_y), 1)
    # White frost cap on the upper third — the brightest, sharpest read.
    cap_y = tip_y + (root_y - tip_y) // 3
    cap_half = max(1, half - 1)
    pygame.draw.polygon(surf, _GL_FROST,
                        [(root_x - cap_half // 2 - 1, cap_y),
                         (root_x + cap_half // 2 + 1, cap_y),
                         (root_x, tip_y)])
    # 1px ice-light spine down the centre so each spike reads as faceted ice.
    pygame.draw.line(surf, _GL_GLINT, (root_x, root_y - 1), (root_x, cap_y), 1)


def _frost_branch(surf, x0, y0, x1, y1, branch):
    """A fine branching frost-rime line — the crackle that spreads cold across
    the back/wing. A bright white main stroke with two short feathered offshoots
    so it reads as growing frost, not a drawn line. Kept to white-on-ice so the
    crackle is a value tell that holds the cold read at thumbnail size."""
    pygame.draw.line(surf, _GL_FROST, (x0, y0), (x1, y1), 1)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    pygame.draw.line(surf, _GL_FROST, (mx, my), (mx + branch, my - 2), 1)
    pygame.draw.line(surf, _GL_FROST, (mx, my), (mx - branch // 2, my + 2), 1)


def _facet_glint(surf, cx, cy, r):
    """A hard rhombus ice glint on the chest — flat ice-glint fill with a dark
    slate keyline and ONE bright-white spec, pointed like an ice chip catching
    light. R2 enlarges these and cuts their count to a few big hard glints (the
    R1 scatter of small specks lowered apparent contrast at 1×); the dark
    keyline now anchors each chip against the pale chest so it holds at 40px."""
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    pygame.draw.polygon(surf, _GL_GLINT, pts)
    pygame.draw.polygon(surf, _GL_DEEP, pts, 1)
    pygame.draw.circle(surf, _GL_FROST, (cx, cy - 1), 1)   # one bright spec each


def _snow_sparkle(surf, cx, cy, r):
    """A drifting 4-point snow sparkle shedding off the back into open sky —
    a white plus-cross with a glint core; the 'cold air' aura tell, held to a
    couple so the bird stays epic, not legendary."""
    pygame.draw.line(surf, _GL_FROST, (cx - r, cy), (cx + r, cy), 1)
    pygame.draw.line(surf, _GL_FROST, (cx, cy - r), (cx, cy + r), 1)
    pygame.draw.circle(surf, _GL_GLINT, (cx, cy), 1)


def _paint_crest(surf, base_y):
    """The hero icicle crest — a fan of 4 spikes jutting UP past the crown
    (centre tallest, outers splayed + shortened so the cluster reads as a jagged
    frozen crown, not a single horn), seated on a frosted ridge. Kept EXACTLY as
    R1 per the art-director; isolated so a crest-masked body proof can skip it."""
    spikes = (
        (HX - 9, base_y + 1, base_y - 11, 3),
        (HX - 3, base_y,     base_y - 22, 4),
        (HX + 4, base_y,     base_y - 18, 4),
        (HX + 10, base_y + 1, base_y - 9, 3),
    )
    for rx, ry, ty, half in spikes:
        _icicle(surf, rx, ry, ty, half, body=_GL_ICE, edge=_GL_DEEP)
    # A frosted ridge seats the spikes onto the crown so the cluster reads
    # anchored, with a sliver of body left between the ridge and the aviators.
    pygame.draw.line(surf, _GL_FROST, (HX - 11, base_y + 1), (HX + 12, base_y + 1), 2)
    pygame.draw.line(surf, _GL_SHADOW, (HX - 11, base_y + 2), (HX + 12, base_y + 2), 1)


def _paint_glacier(surf, _a, *, crest=True):
    base_y = CROWN_Y + 3   # spike roots seated just into the crown

    # 0 · DAY-SKY VALUE FIX (painted FIRST, under everything): a real dark→light
    #     ice gradient so the body silhouette holds on bright day sky even with
    #     the crest removed. A deep glacier-shadow wedge runs the back ridge and
    #     wraps the lower-wing/belly underside; over it a 1px near-navy rim hugs
    #     the sky-facing edges (top of back + leading wing) that day sky leaves
    #     bare. Bought entirely with darker mono-ice — no second hue.
    back_shadow = [(15, 41), (24, 39), (34, 41), (33, 47), (22, 47), (14, 45)]
    pygame.draw.polygon(surf, _GL_ABYSS, back_shadow)
    belly_shadow = [(16, 56), (28, 60), (40, 58), (38, 63), (24, 64), (15, 60)]
    pygame.draw.polygon(surf, _GL_ABYSS, belly_shadow)
    # Soft inner step so the dark wedge reads as shaded ice, not a painted patch.
    pygame.draw.polygon(surf, _GL_DEEP,
                        [(18, 43), (28, 42), (33, 44), (30, 47), (20, 47)])
    # Hard sky-facing rim along the back-top + leading wing edge — the edge that
    # holds the silhouette against bright sky (night gets this free from the sky).
    pygame.draw.lines(surf, _GL_RIM, False,
                      [(14, 44), (20, 40), (28, 38), (36, 40), (43, 45)], 1)

    # 1 · BACK FROST-RIME CRACKLE (thinned ~40% from R1 — the scattered fine
    #     branches were noise that flattened apparent contrast at 1×). A single
    #     bright branching frost line spreads across the dark back wedge, where
    #     white-on-abyss is the cleanest possible cold tell.
    _frost_branch(surf, 19, 43, 30, 44, 3)

    # 2 · CHEST ICE GLINTS: consolidated to THREE large hard chips (was a noisy
    #     scatter), each ice-glint with a dark keyline + one bright spec so the
    #     chest reads as ice catching light without dissolving into the body.
    _facet_glint(surf, 30, 51, 4)
    _facet_glint(surf, 38, 55, 3)
    _facet_glint(surf, 24, 56, 3)

    # 3 · HERO: the jagged 4-spike icicle crest — kept EXACTLY as R1 (the wave's
    #     best signature). Split into its own helper only so the round sheet can
    #     render a crest-masked proof that the body alone reads on day sky.
    if crest:
        _paint_crest(surf, base_y)

    # 4 · AVIATOR RE-READ: a 1px frost rim across both lenses so Pip's signature
    #     glasses catch the cold light under the crest (the palette already cools
    #     the lens tint; the rim is the hard top edge separating lens from face).
    pygame.draw.line(surf, _GL_FROST, (40, 44), (46, 44), 2)
    pygame.draw.line(surf, _GL_FROST, (49, 44), (54, 44), 2)

    # 5 · TAIL FROST DIP: white frost capping the tail-feather tips (white→ice
    #     gradient already in the palette tail ramp; these are the hard frosted
    #     points so the tail reads dipped in frost, not just pale).
    for tx, ty in ((6, 63), (11, 65), (16, 64)):
        pygame.draw.polygon(surf, _GL_FROST,
                            [(tx - 2, ty), (tx + 2, ty), (tx, ty + 3)])
        pygame.draw.circle(surf, _GL_GLINT, (tx, ty + 1), 1)

    # 6 · AURA: ONE small snow sparkle tucked tight at the frosted tail (R1's
    #     two back-floaters read as detached debris/coins at gameplay scale, so
    #     they're pulled in next to the tail mass where they read as shed frost).
    _snow_sparkle(surf, 8, 60, 2)


# Body recolour through the palette system + the frost overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_glacier,
    base_fn=lambda a: _build_parrot_with_palette(a, P_GLACIER),
)

# Crest-masked variant — the SAME skin with the icicle crest suppressed, so the
# round sheet can prove the body alone holds its silhouette on day sky (the R2
# north-star check). Exploration harness only; never a shippable skin.
build_no_crest = store_skins._make_skin(
    lambda s, a: _paint_glacier(s, a, crest=False),
    base_fn=lambda a: _build_parrot_with_palette(a, P_GLACIER),
)
