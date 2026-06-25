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
"""
import pygame

from game import store_skins
from game.store_skins import HX, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Glacier palette: one cool ice-blue mass, a cyan-slate shadow that owns the
# line work, and pure frost-white as the single bright that every signature
# tip lands on. ICE_GLINT is the mid bright used where white would blow out.
_GL_ICE    = (169, 216, 232)       # #A9D8E8 glacier ice body
_GL_SHADOW = (95, 147, 176)        # #5F93B0 cyan-slate shadow / keyline
_GL_FROST  = (234, 246, 255)       # #EAF6FF frost white (the only bright)
_GL_GLINT  = (199, 236, 255)       # #C7ECFF ice glint (sub-white)
_GL_DEEP   = (62, 104, 134)        # deepest slate — keyline that holds ice on day sky


# Full ice-blue re-plumage. The deepest slate runs the tail/wing line work so
# frost reads against the body; the belly is near-white frosted; aviators are
# RETAINED tinted pale cyan (Pip's signature) since the icicle crest owns the
# silhouette. Single hue throughout — the cold read is value + frost, not colour.
P_GLACIER = _pal(
    tail=[(70, 116, 146), (104, 158, 184), (146, 196, 216), (188, 224, 238)],
    tail_line=_GL_DEEP,
    body_shadow=(86, 138, 168),
    body_main=_GL_ICE,
    body_chest=(206, 234, 244),
    body_belly=(228, 244, 252),       # near-white frosted belly
    sheen=(255, 255, 255, 150),
    wing_main=(140, 192, 214),
    wing_dark=_GL_DEEP,
    wing_tip=(206, 234, 246),
    wing_secondary=None,              # single-hue ice — no contrast feather
    wing_highlight=(232, 246, 255),
    head_shadow=(86, 138, 168),
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
    """A hard rhombus ice glint on the chest — flat white with a slate keyline,
    pointed like an ice chip catching light. ≥2px so it survives downscale; the
    chest 'ice catching light' tell."""
    pts = [(cx, cy - r), (cx + r - 1, cy), (cx, cy + r), (cx - r + 1, cy)]
    pygame.draw.polygon(surf, _GL_FROST, pts)
    pygame.draw.polygon(surf, _GL_SHADOW, pts, 1)


def _snow_sparkle(surf, cx, cy, r):
    """A drifting 4-point snow sparkle shedding off the back into open sky —
    a white plus-cross with a glint core; the 'cold air' aura tell, held to a
    couple so the bird stays epic, not legendary."""
    pygame.draw.line(surf, _GL_FROST, (cx - r, cy), (cx + r, cy), 1)
    pygame.draw.line(surf, _GL_FROST, (cx, cy - r), (cx, cy + r), 1)
    pygame.draw.circle(surf, _GL_GLINT, (cx, cy), 1)


def _paint_glacier(surf, _a):
    base_y = CROWN_Y + 3   # spike roots seated just into the crown

    # 1 · BACK/WING FROST-RIME CRACKLE (painted first, under the crest, so the
    #     cold language carries below the crown — the bird is frozen all over,
    #     not just crowned). Fine white branching frost spreads from the back
    #     ridge out along the wing leading edge, plus a cool slate rim-light
    #     under the back so the ice mass keeps a crisp lower edge on night sky.
    pygame.draw.lines(surf, _GL_DEEP, False,
                      [(16, 46), (24, 49), (32, 50), (40, 48)], 1)  # rim-light
    _frost_branch(surf, 18, 44, 28, 46, 3)
    _frost_branch(surf, 27, 47, 38, 45, 3)
    _frost_branch(surf, 22, 41, 31, 43, 2)

    # 2 · CHEST ICE GLINTS: two hard white rhombus chips where the ice catches
    #     light — the flat-white-on-blue value note that reads at 40px (kept to
    #     two so the chest stays clean, not noisy like a scatter of specks).
    _facet_glint(surf, 30, 50, 3)
    _facet_glint(surf, 37, 54, 2)

    # 3 · HERO: a fan of 4 icicle spikes jutting UP past the crown — the
    #     egg-breaking signature. Centre spike tallest, outer ones splay out and
    #     shorten so the cluster reads as a jagged frozen crown, not a single
    #     horn. Painted after the body so it sits on top; each spike's white
    #     frost tip is the brightest note on the whole bird.
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

    # 6 · AURA: two drifting snow sparkles shedding off the back into OPEN sky
    #     (kept off the near-black card edge), the cold-air tell. Held to two so
    #     the skin stays epic.
    _snow_sparkle(surf, HX - 20, CROWN_Y + 4, 3)
    _snow_sparkle(surf, HX - 25, CROWN_Y + 14, 2)


# Body recolour through the palette system + the frost overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_glacier,
    base_fn=lambda a: _build_parrot_with_palette(a, P_GLACIER),
)
