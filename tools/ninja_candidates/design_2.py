"""CRIMSON FANG — Blood Assassin Kunoichi (ninja redesign candidate design_2).

Scratch exploration only — not registered in store_skins.BUILDERS and it does
NOT touch the live skin_ninja. The aggressive crimson counterpart to the black
shinobi: the whole macaw is re-plumaged blood-crimson (true body recolour via
the 24-slot palette system, so the read is "elite assassin tier", not a black
bird with a red hat), then layered with steel + charcoal assassin objects.

Two instant 40px tells, the brief's north star:
  1) a wrapped face with a black eye-slit band + a steel forehead plate, and
  2) an X of two crossed kunai breaking the back outline up past the crown,
backed by a charcoal scarf streaming well past the tail (the dynamic element,
flicked by the wing/flap so it never reads as a static stripe).
"""
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y, PARROT_DY, COMPOSITE_W, COMPOSITE_H
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette


# ── Palette ───────────────────────────────────────────────────────────────────
# #8B0A1A body / #B71C2B highlight / #16181E charcoal / #D9DCE3 steel /
# #5E0710 crimson shadow. Named locals mirror the brief's swatches.
CRIMSON      = (139, 10, 26)
CRIMSON_HI   = (183, 28, 43)
CHARCOAL     = (22, 24, 30)
CHARCOAL_HI  = (52, 56, 66)
STEEL        = (217, 220, 227)
STEEL_HI     = (245, 247, 250)
STEEL_D      = (150, 156, 168)
CRIMSON_SH   = (94, 7, 16)


# Crimson re-plumage of the macaw. Wraps/wing kept charcoal so the assassin
# cloth (vs the crimson body) reads even before the back weapons; lenses
# dropped (lens_glint=None) so the steel eye-slit band can own the brow.
P_CRIMSON = _pal(
    tail=[(74, 6, 14), (104, 8, 20), (139, 10, 26), (168, 22, 36)],
    tail_line=(48, 4, 10),
    body_shadow=CRIMSON_SH,
    body_main=CRIMSON,
    body_chest=CRIMSON_HI,
    body_belly=(150, 16, 30),
    sheen=(255, 180, 180, 70),
    wing_main=CHARCOAL,            # charcoal wing = cloth contrast on the crimson
    wing_dark=(12, 13, 18),
    wing_tip=(72, 14, 22),
    wing_secondary=None,
    wing_highlight=CHARCOAL_HI,
    head_shadow=CRIMSON_SH,
    head_main=CRIMSON,
    head_cheek=CRIMSON_HI,
    head_crown=(150, 16, 30),
    lens_frame=CHARCOAL,
    lens_body=(10, 11, 15),
    lens_tint=None,
    lens_glint=None,               # eye-slit band replaces the aviators
    beak_main=(40, 40, 46),        # blacked-out beak so the steel plate pops
    beak_dark=(14, 14, 18),
    beak_gloss=(96, 98, 106),
    foot=(28, 22, 24),
)


def _crimson_base(angle_deg):
    # Recoloured body without the aviator lenses — the kunoichi wrap owns the face.
    return _build_parrot_with_palette(angle_deg, P_CRIMSON, draw_lenses=False)


# ── Paint: the layered assassin objects ──────────────────────────────────────

def _kunai(surf, tail_x, tail_y, tip_x, tip_y):
    """A ringed-pommel kunai (throwing dagger): steel leaf blade + charcoal
    wrapped grip + a ring pommel. Drawn tail->tip so the X can angle each.
    Sized so the crossed pair is the dominant silhouette-breaker at 40px:
    fat grip (6px) + a wide blade shoulder so each diagonal survives the
    NEAREST shrink as a solid bar, not a thread."""
    dx, dy = tip_x - tail_x, tip_y - tail_y
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L          # blade axis
    px, py = -uy, ux                 # perpendicular (blade width)

    # Grip start (a little out from the pommel) and blade start (mid-length).
    gx, gy = tail_x + ux * 4, tail_y + uy * 4
    bx, by = tail_x + ux * (L * 0.46), tail_y + uy * (L * 0.46)

    # Charcoal wrapped handle — fat enough to read as a bar after the shrink.
    pygame.draw.line(surf, CHARCOAL, (gx, gy), (bx, by), 6)
    pygame.draw.line(surf, CHARCOAL_HI, (gx, gy), (bx, by), 2)

    # Ring pommel — a solid steel disc (no 1px hoop to vanish at scale).
    pygame.draw.circle(surf, STEEL_D, (int(tail_x), int(tail_y)), 3)
    pygame.draw.circle(surf, STEEL_HI, (int(tail_x - ux), int(tail_y - uy)), 2)

    # Steel leaf blade — a wide diamond from the grip shoulder to the tip.
    sw = 4.5                         # shoulder half-width (was 3.0)
    shoulder_l = (bx + px * sw, by + py * sw)
    shoulder_r = (bx - px * sw, by - py * sw)
    pygame.draw.polygon(surf, STEEL,
                        [shoulder_l, (tip_x, tip_y), shoulder_r,
                         (bx + ux * 2, by + uy * 2)])
    pygame.draw.polygon(surf, STEEL_D,
                        [shoulder_l, (tip_x, tip_y), shoulder_r,
                         (bx + ux * 2, by + uy * 2)], 2)
    # Centre fuller carries the metal read at 40px (2px min).
    pygame.draw.line(surf, STEEL_HI, (bx + ux * 2, by + uy * 2),
                     (tip_x - ux * 3, tip_y - uy * 3), 2)


def _paint(surf, wing_angle_deg):
    # Flap phase drives the scarf flick: angle runs roughly -10..+18 across the
    # 4 frames, so the scarf lifts on the up-stroke and trails on the down.
    flap = max(0.0, wing_angle_deg) / 18.0

    # ── BACK · crossed kunai X, the single dominant silhouette-breaker ───────
    # Drawn first so the body/scarf overlap their lower halves naturally. The
    # crossing sits behind the shoulders; both pommels are pushed clearly above
    # CROWN_Y and the diagonals span ~22px so the X is unmistakable at 40px.
    cx, cy = HX - 3, CROWN_Y + 5      # crossing point just behind the shoulders
    # Pommels at y = CROWN_Y - 8 (well above the crown), tips down past the back.
    _kunai(surf, cx - 11, cy - 13, cx + 13, cy + 12)   # NW->SE
    _kunai(surf, cx + 11, cy - 13, cx - 13, cy + 12)   # NE->SW
    # A fat binding wrap knots the X together at the crossing.
    pygame.draw.circle(surf, CHARCOAL, (cx, cy), 4)
    pygame.draw.circle(surf, CHARCOAL_HI, (cx - 1, cy - 1), 2)

    # ── NECK · charcoal scarf streaming back past the tail (dynamic) ──────────
    # Anchored at the throat, sweeping down-left off the tail; the tip lifts
    # with the flap so it animates as the most alive element.
    lift = int(flap * 6)
    nx, ny = HX - 3, HY + 6
    # The streaming tip angles UP and further back so its forked end clears the
    # crimson tail outline instead of merging into it — the scarf rides ABOVE
    # the tail line and reads as a separate trailing element, not tail mass.
    p0 = (nx, ny)
    p1 = (nx - 15, ny - 3 - lift)
    p2 = (nx - 31, ny - 9 - lift * 2)
    tip = (nx - 45, ny - 16 - lift * 3)
    # Body of the scarf as a tapering ribbon (two edges + fill).
    upper = [p0, p1, p2, tip]
    lower = [(p0[0], p0[1] + 7), (p1[0], p1[1] + 7),
             (p2[0], p2[1] + 6), (tip[0], tip[1] + 4)]
    pygame.draw.polygon(surf, CHARCOAL, upper + lower[::-1])
    pygame.draw.lines(surf, (10, 11, 15), False, lower, 2)
    # Lifted highlight along the FULL upper run — the value break that separates
    # the charcoal scarf from the crimson tail behind it at a glance.
    pygame.draw.lines(surf, CHARCOAL_HI, False, upper, 2)
    # A forked, split tail so the end reads as cloth, not a bar.
    pygame.draw.polygon(surf, CHARCOAL,
                        [tip, (tip[0] - 9, tip[1] - 4 - lift),
                         (tip[0] - 6, tip[1] + 2 - lift)])
    pygame.draw.polygon(surf, CHARCOAL,
                        [(tip[0], tip[1] + 5), (tip[0] - 10, tip[1] + 6 - lift),
                         (tip[0] - 5, tip[1] + 9 - lift)])

    # ── BODY · flat charcoal obi band + one crimson knot ─────────────────────
    # The cross-lacing is gone: the ONLY X on the costume is the kunai up top,
    # so the back weapons own the hero read. The obi is a clean charcoal band
    # with a single crimson knot at its near end.
    oy = HY + 13
    pygame.draw.rect(surf, CHARCOAL, (HX - 16, oy, 22, 7), border_radius=2)
    pygame.draw.line(surf, CHARCOAL_HI, (HX - 15, oy + 1), (HX + 4, oy + 1), 2)
    # One crimson knot with a short hanging tongue at the near (left) end.
    pygame.draw.circle(surf, CRIMSON, (HX - 16, oy + 3), 3)
    pygame.draw.circle(surf, CRIMSON_HI, (HX - 17, oy + 2), 1)
    pygame.draw.polygon(surf, CRIMSON,
                        [(HX - 18, oy + 4), (HX - 14, oy + 4), (HX - 16, oy + 11)])

    # ── WING/LEG · black wrist & shin wraps (a couple of bands each) ─────────
    for wx in (HX - 7, HX - 3):       # forearm wraps near the wing root
        pygame.draw.line(surf, CHARCOAL, (wx, HY + 22), (wx + 3, HY + 26), 3)
        pygame.draw.line(surf, CHARCOAL_HI, (wx, HY + 22), (wx + 3, HY + 26), 2)
    for fx in (HX - 19, HX - 13):     # shin wraps above the feet
        pygame.draw.line(surf, CHARCOAL, (fx, HY + 24), (fx, HY + 28), 3)

    # ── HEAD · one readable ninja mask: crimson wrap + a single eye-slit ─────
    # Wrap fold across the lower face (crimson, ties into the body plumage).
    pygame.draw.polygon(surf, CRIMSON_SH,
                        [(HX - 9, HY + 3), (HX + 13, HY + 1),
                         (HX + 12, HY + 9), (HX - 8, HY + 10)])
    pygame.draw.line(surf, CRIMSON_HI, (HX - 7, HY + 4), (HX + 11, HY + 2), 2)
    # Solid charcoal band wrapping the brow with ONE continuous thin steel slit
    # INSIDE it — a horizontal slit reads as "masked face"; no eye dots (two
    # dots read as eyes and break the wrapped-face tell).
    pygame.draw.line(surf, CHARCOAL, (HX - 11, HY + 1), (HX + 13, HY - 3), 6)
    pygame.draw.line(surf, STEEL, (HX - 9, HY), (HX + 11, HY - 3), 2)  # slit

    # ── HEAD · steel forehead plate: solid diamond + one corner highlight ────
    # Nudged up 1px and the gap to the slit darkened with the charcoal band
    # value, so plate and slit read as TWO marks (plate above, slit below) and
    # don't fuse into one steel blob when the NEAREST shrink collapses the row.
    px, py = HX + 1, HY - 7
    pygame.draw.line(surf, CHARCOAL, (px - 5, py + 4), (px + 5, py + 4), 1)  # dark divider
    plate = [(px, py - 4), (px + 5, py), (px, py + 4), (px - 5, py)]
    pygame.draw.polygon(surf, STEEL, plate)
    pygame.draw.circle(surf, STEEL_HI, (px - 2, py - 1), 2)  # single corner glint


build = store_skins._make_skin(_paint, base_fn=_crimson_base)
