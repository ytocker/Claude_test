"""design_1 · HATCHLING — RARE baby-parrot exploration (scratch only).

Pip "just broke out of the egg": a cream-yellow baby macaw wearing a cracked
half-eggshell cap, one loose shell shard slipping over the upper-left aviator
lens, and damp natal-down wisps escaping the cracks. The hero read is the
broken-egg silhouette — a domed off-white shell cap with a hard zig-zag rim
tilted off the crown — a shape no other skin in the roster owns. It says
"baby — it literally just hatched" before any detail resolves.

North star is "lives or dies at 40px on BOTH skies". The cap is built as a
solid ≥3px dome (a single bold off-white shape that holds a value break over
both bright day and dark night sky), with a crack-shadow under-rim so the
zig-zag teeth survive downscale instead of mushing into a pale blob. The body
is recoloured to a warm cream-yellow (clear of cockatoo white, hyacinth blue
and moonbloom lilac) so "baby" is sold by PALETTE + OVERLAY at the fixed macaw
size — never by shrinking. The aviators STAY (Pip's tell), warmed to amber.

PRISM model — cap, shards, flecks and down-wisps are all polygons + lines over
a cream recolour; no back-layer is needed. Exploration only — NEVER registered
in store_skins.BUILDERS.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# Hatchling palette — warm cream-yellow body with an ochre shadow that owns the
# line work, a soft peach belly/chest so the underside reads downy-warm, and
# amber-warmed aviators. The shell colours live ONLY in the overlay so the
# eggshell reads as a separate hard object, not plumage. Cream-yellow is held
# above cockatoo white in saturation and well clear of hyacinth cobalt /
# moonbloom lilac.
_HC_CREAM   = (244, 227, 168)      # #F4E3A8 body cream-yellow
_HC_SHADOW  = (216, 184, 106)      # #D8B86A ochre body/feather shadow
_HC_PEACH   = (246, 201, 160)      # #F6C9A0 soft peach belly/chest
_HC_SHELL   = (242, 237, 224)      # #F2EDE0 shell off-white
_HC_SHELL_D = (200, 185, 138)      # #C8B98A shell-crack shadow
_HC_SHELL_H = (255, 252, 244)      # shell lit highlight (catch on the dome)
_HC_AMBER   = (232, 184, 106)      # #E8B86A warm-amber aviator glint
_HC_DOWN    = (250, 236, 192)      # damp natal-down wisp (warm off-cream)
_HC_DOWN_D  = (214, 182, 110)      # down-wisp shadow so wisps read on cream sky


# Full cream-yellow re-plumage. Shadow slots run a punchy ochre so the body
# already carries a cream→ochre value range under the pale shell cap (the cap
# must still read as a brighter, separate object). Chest + belly stay peach so
# the underside reads soft/babyish. The shell off-white is kept OUT of the base
# plumage so the eggshell overlay is the only near-white shape on the bird.
# Aviators retinted amber-warm (cosy hatchling glow, not the steely adult tint).
P_HATCHLING = _pal(
    tail=[(196, 162, 92), (214, 184, 110), (232, 208, 142), (244, 227, 168)],
    tail_line=_HC_SHADOW,
    body_shadow=_HC_SHADOW,
    body_main=_HC_CREAM,
    body_chest=(248, 216, 176),
    body_belly=_HC_PEACH,
    sheen=(255, 248, 224, 120),
    wing_main=(236, 214, 146),
    wing_dark=_HC_SHADOW,
    wing_tip=(248, 232, 190),
    wing_secondary=None,               # single-hue cream — no contrast feather
    wing_highlight=(255, 250, 224),
    head_shadow=_HC_SHADOW,
    head_main=_HC_CREAM,
    head_cheek=(248, 214, 172),
    head_crown=(238, 216, 150),
    lens_frame=(206, 158, 96),         # warm amber rims
    lens_body=(54, 42, 30),
    lens_tint=(232, 184, 106, 130),    # amber lens tint
    lens_glint=(255, 248, 230),
    beak_main=(244, 206, 150),
    beak_dark=(184, 132, 78),
    beak_gloss=(255, 246, 224),
    foot=(196, 150, 92),
)


def _zigzag_rim(left, right, teeth, depth, baseline_dy):
    """Build the hard broken lower rim of the shell as a list of points running
    left→right, alternating up at the baseline and down into a tooth. A crisp
    zig-zag (not a smooth curve) is what reads as a CRACKED egg at 40px, so the
    teeth are kept few + deep enough to survive downscale."""
    pts = []
    span = right[0] - left[0]
    for i in range(teeth + 1):
        t = i / teeth
        x = left[0] + span * t
        y = left[1] + (right[1] - left[1]) * t
        # Even verts ride the rim baseline; odd verts dip down into a crack tooth.
        pts.append((x, y + (depth if i % 2 else baseline_dy)))
    return pts


def _shard(surf, pts):
    """A single eggshell shard — a flat off-white polygon with a crack-shadow
    keyline + one lit edge so it reads as a hard chip of shell (a value break),
    not a smudge, when small."""
    pygame.draw.polygon(surf, _HC_SHELL_D, [(x + 1, y + 1) for x, y in pts])
    pygame.draw.polygon(surf, _HC_SHELL, pts)
    pygame.draw.line(surf, _HC_SHELL_H, pts[0], pts[1], 1)   # lit edge
    pygame.draw.line(surf, _HC_SHELL_D, pts[1], pts[2], 1)   # crack-shadow edge


def _wisp(surf, x, y, dx, dy):
    """One short damp down-wisp — a 2px tapered fluff poking PAST the silhouette
    so the sleek macaw outline reads broken/fuzzy (the No.1 baby tell). A dark
    backing 1px behind gives the wisp its own value contrast so it survives on
    the cream body and on bright sky alike."""
    tip = (x + dx, y + dy)
    side = (x + (-dy) * 0.4, y + dx * 0.4)
    pygame.draw.polygon(surf, _HC_DOWN_D,
                        [(x + 1, y + 1), (side[0] + 1, side[1] + 1),
                         (tip[0] + 1, tip[1] + 1)])
    pygame.draw.polygon(surf, _HC_DOWN, [(x, y), side, tip])


def _paint_eggcap(surf):
    """The hero half-eggshell cap. A domed off-white ellipse tilted ~15° off the
    crown so it breaks the silhouette to one side, capped by a hard zig-zag
    broken lower rim with a crack-shadow band beneath it so the teeth read as
    SHELL, not as a soft hat. One tiny shard perches on top. Built solid + ≥3px
    so the whole cap holds as one bright shape at thumbnail size on both skies."""
    # Cap sits up off the crown and tilts screen-left (toward the face shard) so
    # the egg looks freshly knocked askew. Anchored above CROWN_Y.
    cx, cy = HX - 3, CROWN_Y - 4
    rx, ry = 13, 10

    # Dome — drawn on its own SRCALPHA layer, rotated ~15°, so the tilt breaks the
    # crown outline cleanly. The dome is the solid bright mass; the rim teeth are
    # carved by overpainting the body colour back in below the baseline.
    cap = pygame.Surface((rx * 2 + 6, ry * 2 + 6), pygame.SRCALPHA)
    ccx, ccy = rx + 3, ry + 3
    # Crack-shadow seat first (a 1px darker dome behind) so the shell has an
    # under-rim value break that survives downscale.
    pygame.draw.ellipse(cap, _HC_SHELL_D,
                        (ccx - rx, ccy - ry + 1, rx * 2, ry * 2))
    pygame.draw.ellipse(cap, _HC_SHELL,
                        (ccx - rx, ccy - ry, rx * 2, ry * 2))
    # Lit catch on the upper-left of the dome so it reads round + glossy-damp.
    pygame.draw.ellipse(cap, _HC_SHELL_H,
                        (ccx - rx + 2, ccy - ry + 1, rx, ry - 2), 0)
    pygame.draw.ellipse(cap, _HC_SHELL,
                        (ccx - rx + 4, ccy - ry + 3, rx, ry - 2), 0)

    # Hard zig-zag broken rim: cut the lower half away with the transparent
    # colour-key so the bottom edge is a row of crack teeth, not a clean dome.
    rim = _zigzag_rim((ccx - rx + 1, ccy + 1), (ccx + rx - 1, ccy + 1),
                      teeth=6, depth=ry + 3, baseline_dy=2)
    rim = rim + [(ccx + rx + 4, ccy + ry + 5), (ccx - rx - 4, ccy + ry + 5)]
    pygame.draw.polygon(cap, (0, 0, 0, 0), rim)
    # Re-stroke the surviving teeth tips with a crack-shadow line so each tooth
    # has a hard dark base — the read that says "broken shell".
    teeth_line = _zigzag_rim((ccx - rx + 1, ccy + 1), (ccx + rx - 1, ccy + 1),
                             teeth=6, depth=ry + 1, baseline_dy=2)
    pygame.draw.lines(cap, _HC_SHELL_D, False, teeth_line, 1)

    cap = pygame.transform.rotate(cap, 15)
    surf.blit(cap, cap.get_rect(center=(cx, cy)))

    # One tiny shell shard perched on top of the dome (debris balanced on the egg).
    _shard(surf, [(cx + 3, cy - 9), (cx + 8, cy - 11), (cx + 6, cy - 6)])


def _paint_hatchling(surf, _a):
    # OVERLAY ZONES — each "baby" tell is a hard shape with its own value break
    # so the read holds at 40px; nothing competes with the egg-cap hero.

    # 1 · FACE SHARD — a loose shell chip hangs over the upper-LEFT (far) aviator
    #     lens so the egg literally hatched onto Pip's shades. The far lens body
    #     sits at ~(HX-4, HY); the shard overlaps its upper rim. A 2px wet
    #     down-curl flicks off the cheek just below.
    _shard(surf, [(HX - 11, HY - 6), (HX - 2, HY - 8), (HX - 5, HY)])
    _shard(surf, [(HX - 9, HY - 4), (HX - 3, HY - 5), (HX - 6, HY - 1)])
    _wisp(surf, HX - 9, HY + 4, -4, 3)        # wet cheek down-curl

    # 2 · CHEST DOWN — two short damp natal-down wisps poke past the belly
    #     silhouette (newly hatched = stuck-down fluff, not fully fluffy yet),
    #     breaking the lower-front outline so it reads babyish.
    _wisp(surf, 24, 58, -4, 4)
    _wisp(surf, 27, 62, -2, 5)

    # 3 · BACK / TAIL DEBRIS — a couple of speckled shell-fleck dots + one stray
    #     shard by the tail root, the leftover crumbs of the break. Flecks are
    #     2px off-white with a 1px crack-shadow seat so they hold as specks.
    for fx, fy in ((18, 48), (15, 54), (21, 44)):
        pygame.draw.circle(surf, _HC_SHELL_D, (fx + 1, fy + 1), 2)
        pygame.draw.circle(surf, _HC_SHELL, (fx, fy), 1)
    _shard(surf, [(12, 64), (18, 62), (15, 68)])

    # 4 · WING STUBBY ILLUSION — a rounded bright mid-highlight blob fakes a
    #     pudgy half-grown wing (no geometry change), with a damp-fluff tuck at
    #     the wing tip so even the wing reads downy.
    pygame.draw.circle(surf, (255, 246, 206), (30, 50), 4)
    pygame.draw.circle(surf, _HC_CREAM, (31, 51), 2)
    _wisp(surf, 20, 42, -4, -2)               # damp fluff at the wingtip

    # 5 · HERO EGG-CAP — drawn last so it sits clean over the crown.
    _paint_eggcap(surf)


# Body recolour through the palette system + the eggshell overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_hatchling,
    base_fn=lambda a: _build_parrot_with_palette(a, P_HATCHLING),
)
