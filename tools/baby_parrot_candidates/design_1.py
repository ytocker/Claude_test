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
_HC_DOWN_DD = (186, 152, 86)       # one step deeper, for chest wisps off pale belly


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


def _broken_rim(left, right, teeth, depth, baseline_dy):
    """The hard broken lower edge of the shell as a left→right point list: the
    baseline rides flat, then dips into a few BIG triangular teeth. Few + deep
    is the whole point — a child draws a cracked egg as 3 fat jagged teeth, not
    a fine comb, and only fat teeth survive the shrink to 40px. Each tooth is a
    down-vert flanked by two baseline verts, so the V-notches between teeth read
    as hard cracks once their edges are stroked dark."""
    pts = []
    span = right[0] - left[0]
    steps = teeth * 2
    for i in range(steps + 1):
        t = i / steps
        x = left[0] + span * t
        y = left[1] + (right[1] - left[1]) * t
        # Odd verts are the deep tooth tips; even verts ride the baseline.
        pts.append((x, y + (depth if i % 2 else baseline_dy)))
    return pts


def _shard(surf, pts):
    """A single eggshell shard — a flat off-white polygon with a hard crack-shadow
    keyline stroked around its WHOLE perimeter so it reads as a crisp chip of
    shell (a value break), not a soft smudge, when small."""
    pygame.draw.polygon(surf, _HC_SHELL, pts)
    pygame.draw.polygon(surf, _HC_SHELL_D, pts, 1)            # hard keyline
    pygame.draw.line(surf, _HC_SHELL_H, pts[0], pts[1], 1)    # one lit edge


def _wisp(surf, x, y, dx, dy):
    """One short damp down-wisp — a 2px tapered fluff poking PAST the silhouette
    so the sleek macaw outline reads broken/fuzzy (the No.1 baby tell). A darker
    backing one step deeper than the cream gives the wisp its own value contrast
    so it survives on the cream body and on bright sky alike."""
    tip = (x + dx, y + dy)
    side = (x + (-dy) * 0.4, y + dx * 0.4)
    pygame.draw.polygon(surf, _HC_DOWN_D,
                        [(x + 1, y + 1), (side[0] + 1, side[1] + 1),
                         (tip[0] + 1, tip[1] + 1)])
    pygame.draw.polygon(surf, _HC_DOWN, [(x, y), side, tip])


def _chest_wisp(surf, x, y, dx, dy):
    """A chest down-wisp with a deeper backing than the body wisps so it reads
    against the pale peach belly, and a longer reach so its tip clears the belly
    silhouette by a clear ~3px (it has to BREAK the outline to register)."""
    tip = (x + dx, y + dy)
    side = (x + (-dy) * 0.4, y + dx * 0.4)
    pygame.draw.polygon(surf, _HC_DOWN_DD,
                        [(x + 1, y + 1), (side[0] + 1, side[1] + 1),
                         (tip[0] + 1, tip[1] + 1)])
    pygame.draw.polygon(surf, _HC_DOWN, [(x, y), side, tip])


def _paint_eggcap(surf):
    """The hero half-eggshell cap — the read this skin lives or dies on. A LOW +
    WIDE shell cap (not a sphere) perched on the crown, with a hard crack-shadow
    keyline stroked around its whole perimeter so it never floats as soft cotton
    on navy, a broken lower edge of THREE big jagged teeth whose V-notches are
    stroked dark to read as hard cracks, and one slightly-jagged crack line
    across the dome face so it reads as a curved shell surface — not a glossy
    pom-pom. No soft catch-lights, by design: the keyline + crack do all the
    work and survive the shrink to 40px on both skies."""
    # Anchored a touch higher than the crown so the egg always perches CLEAR of
    # the head/back across all four frames instead of merging into the silhouette.
    cx, cy = HX - 2, CROWN_Y - 6
    rx, ry = 14, 7                       # flat + wide = "shell cap", never "ball"

    cap = pygame.Surface((rx * 2 + 8, ry * 2 + 14), pygame.SRCALPHA)
    ccx, ccy = rx + 4, ry + 4

    # Solid dome fill, then carve the lower edge away with the colour-key so the
    # bottom becomes a row of 3 fat crack teeth instead of a clean arc.
    pygame.draw.ellipse(cap, _HC_SHELL, (ccx - rx, ccy - ry, rx * 2, ry * 2))
    rim = _broken_rim((ccx - rx, ccy + 1), (ccx + rx, ccy + 1),
                      teeth=3, depth=ry + 9, baseline_dy=-1)
    cut = rim + [(ccx + rx + 6, ccy + ry + 10), (ccx - rx - 6, ccy + ry + 10)]
    pygame.draw.polygon(cap, (0, 0, 0, 0), cut)

    # Hard keyline around the whole shell: stroke the dome arc (upper half of the
    # ellipse) AND every tooth edge in shell-shadow so the perimeter is crisp.
    pygame.draw.arc(cap, _HC_SHELL_D,
                    (ccx - rx, ccy - ry, rx * 2, ry * 2),
                    0.18, math.pi - 0.18, 2)
    pygame.draw.lines(cap, _HC_SHELL_D, False, rim, 2)

    # ONE horizontal shell-crack across the dome face — a slightly-jagged dark
    # line so the cap reads as a curved cracked shell, not a smooth bright blob.
    crk_y = ccy - 1
    pygame.draw.lines(cap, _HC_SHELL_D, False,
                      [(ccx - rx + 3, crk_y), (ccx - 3, crk_y - 2),
                       (ccx + 2, crk_y + 1), (ccx + rx - 3, crk_y - 1)], 1)

    cap = pygame.transform.rotate(cap, 13)   # knocked-askew tilt toward the face
    surf.blit(cap, cap.get_rect(center=(cx, cy)))


def _paint_hatchling(surf, _a):
    # OVERLAY ZONES — each "baby" tell is a hard shape with its own value break
    # so the read holds at 40px; nothing competes with the egg-cap hero.

    # 1 · FACE SHARD — ONE bold shell chip sitting ON TOP of the upper-left lens
    #     rim so it visibly breaks the lens circle's outline (the money gag: the
    #     egg hatched right onto Pip's shades). One fat triangle (~6px wide) with
    #     the same hard keyline as the cap, big enough to survive 40px. A 2px wet
    #     down-curl flicks off the cheek just below it.
    _shard(surf, [(HX - 12, HY - 5), (HX - 4, HY - 8), (HX - 5, HY + 1)])
    _wisp(surf, HX - 10, HY + 4, -4, 3)       # wet cheek down-curl

    # 2 · CHEST DOWN — two damp natal-down wisps whose tips poke a clear ~3px past
    #     the belly silhouette (newly hatched = stuck-down fluff), breaking the
    #     lower-front outline so the bird reads babyish. Deeper backing than the
    #     cap so they hold against the pale peach belly.
    _chest_wisp(surf, 25, 57, -5, 5)
    _chest_wisp(surf, 28, 62, -3, 6)

    # 3 · WING STUBBY ILLUSION — a rounded bright mid-highlight blob fakes a
    #     pudgy half-grown wing (no geometry change), with a damp-fluff tuck at
    #     the wing tip so even the wing reads downy. Back/tail shell debris was
    #     dropped — at 1× it only read as noise that muddied the silhouette.
    pygame.draw.circle(surf, (255, 246, 206), (30, 50), 4)
    pygame.draw.circle(surf, _HC_CREAM, (31, 51), 2)
    _wisp(surf, 20, 42, -4, -2)               # damp fluff at the wingtip

    # 4 · HERO EGG-CAP — drawn last so it sits clean over the crown.
    _paint_eggcap(surf)


# Body recolour through the palette system + the eggshell overlay, wrapped by the
# house _make_skin contract (lazy flat build + per-(frame, 3°) rotation cache).
build = store_skins._make_skin(
    _paint_hatchling,
    base_fn=lambda a: _build_parrot_with_palette(a, P_HATCHLING),
)
