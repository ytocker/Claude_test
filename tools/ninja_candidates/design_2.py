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
    wrapped grip + a ring pommel. Drawn tail->tip so the X can angle each."""
    dx, dy = tip_x - tail_x, tip_y - tail_y
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L          # blade axis
    px, py = -uy, ux                 # perpendicular (blade width)

    # Grip start (a little out from the pommel) and blade start (mid-length).
    gx, gy = tail_x + ux * 4, tail_y + uy * 4
    bx, by = tail_x + ux * (L * 0.46), tail_y + uy * (L * 0.46)

    # Charcoal wrapped handle.
    pygame.draw.line(surf, CHARCOAL, (gx, gy), (bx, by), 4)
    pygame.draw.line(surf, CHARCOAL_HI, (gx, gy), (bx, by), 1)
    for t in (0.25, 0.5, 0.75):     # whipping bands across the grip
        wx, wy = gx + (bx - gx) * t, gy + (by - gy) * t
        pygame.draw.line(surf, (8, 9, 12),
                         (wx + px * 2, wy + py * 2), (wx - px * 2, wy - py * 2), 1)

    # Ring pommel.
    pygame.draw.circle(surf, STEEL_D, (int(tail_x), int(tail_y)), 3, 1)
    pygame.draw.circle(surf, STEEL_HI, (int(tail_x - px), int(tail_y - py)), 1)

    # Steel leaf blade — a diamond from the grip shoulder to the tip.
    sw = 3.0                         # shoulder half-width
    shoulder_l = (bx + px * sw, by + py * sw)
    shoulder_r = (bx - px * sw, by - py * sw)
    pygame.draw.polygon(surf, STEEL,
                        [shoulder_l, (tip_x, tip_y), shoulder_r,
                         (bx + ux * 2, by + uy * 2)])
    pygame.draw.polygon(surf, STEEL_D,
                        [shoulder_l, (tip_x, tip_y), shoulder_r,
                         (bx + ux * 2, by + uy * 2)], 1)
    # Centre fuller + tip glint carry the metal read at 40px.
    pygame.draw.line(surf, STEEL_HI, (bx + ux * 2, by + uy * 2),
                     (tip_x - ux * 2, tip_y - uy * 2), 1)
    pygame.draw.circle(surf, STEEL_HI, (int(tip_x), int(tip_y)), 1)


def _paint(surf, wing_angle_deg):
    # Flap phase drives the scarf flick: angle runs roughly -10..+18 across the
    # 4 frames, so the scarf lifts on the up-stroke and trails on the down.
    flap = max(0.0, wing_angle_deg) / 18.0

    # ── BACK · crossed kunai X, handles up past the crown ────────────────────
    # Drawn first so the body/scarf overlap their lower halves naturally.
    cx, cy = HX - 2, CROWN_Y + 6      # crossing point just behind the shoulders
    # NW->SE blade and NE->SW blade; pommels rise above the crown.
    _kunai(surf, cx - 9, cy - 13, cx + 11, cy + 11)
    _kunai(surf, cx + 9, cy - 13, cx - 11, cy + 11)
    # A binding wrap at the crossing knots the X together.
    pygame.draw.circle(surf, CHARCOAL, (cx, cy), 3)
    pygame.draw.circle(surf, CHARCOAL_HI, (cx - 1, cy - 1), 1)

    # ── NECK · charcoal scarf streaming back past the tail (dynamic) ──────────
    # Anchored at the throat, sweeping down-left off the tail; the tip lifts
    # with the flap so it animates as the most alive element.
    lift = int(flap * 6)
    nx, ny = HX - 4, HY + 8
    p0 = (nx, ny)
    p1 = (nx - 14, ny + 6 - lift)
    p2 = (nx - 28, ny + 14 - lift * 2)
    tip = (nx - 40, ny + 8 - lift * 3)
    # Body of the scarf as a tapering ribbon (two edges + fill).
    upper = [p0, p1, p2, tip]
    lower = [(p0[0], p0[1] + 7), (p1[0], p1[1] + 8),
             (p2[0], p2[1] + 6), (tip[0], tip[1] + 3)]
    pygame.draw.polygon(surf, CHARCOAL, upper + lower[::-1])
    pygame.draw.lines(surf, (10, 11, 15), False, lower, 2)
    pygame.draw.lines(surf, CHARCOAL_HI, False, upper, 1)
    # A forked, split tail so the end reads as cloth, not a bar.
    pygame.draw.polygon(surf, CHARCOAL,
                        [tip, (tip[0] - 8, tip[1] - 3 - lift),
                         (tip[0] - 6, tip[1] + 2 - lift)])
    pygame.draw.polygon(surf, CHARCOAL,
                        [(tip[0], tip[1] + 5), (tip[0] - 9, tip[1] + 7 - lift),
                         (tip[0] - 5, tip[1] + 9 - lift)])

    # ── BODY · charcoal obi with crimson cross-lacing down the front ─────────
    oy = HY + 13
    pygame.draw.rect(surf, CHARCOAL, (HX - 16, oy, 22, 7), border_radius=2)
    pygame.draw.line(surf, CHARCOAL_HI, (HX - 15, oy + 1), (HX + 4, oy + 1), 1)
    # Crimson lacing crossing the obi (the cross-tie pattern).
    for i in range(3):
        lx = HX - 13 + i * 7
        pygame.draw.line(surf, CRIMSON_HI, (lx, oy), (lx + 4, oy + 7), 2)
        pygame.draw.line(surf, CRIMSON_HI, (lx + 4, oy), (lx, oy + 7), 2)
    # Knotted side end of the obi with a short hanging tongue.
    pygame.draw.circle(surf, CRIMSON, (HX - 16, oy + 3), 3)
    pygame.draw.polygon(surf, CRIMSON,
                        [(HX - 18, oy + 4), (HX - 14, oy + 4), (HX - 16, oy + 11)])

    # ── BODY · a single shuriken tucked at the hip/sash (small star detail) ──
    sx, sy = HX - 14, oy + 1
    store_skins._star5(surf, sx, sy, 3, STEEL)
    pygame.draw.circle(surf, CHARCOAL, (sx, sy), 1)

    # ── WING/LEG · black wrist & shin wraps (a couple of bands each) ─────────
    for wx in (HX - 7, HX - 3):       # forearm wraps near the wing root
        pygame.draw.line(surf, CHARCOAL, (wx, HY + 22), (wx + 3, HY + 26), 3)
        pygame.draw.line(surf, CHARCOAL_HI, (wx, HY + 22), (wx + 3, HY + 26), 1)
    for fx in (HX - 19, HX - 13):     # shin wraps above the feet
        pygame.draw.line(surf, CHARCOAL, (fx, HY + 24), (fx, HY + 28), 3)

    # ── HEAD · crimson face wrap + black eye-slit band ───────────────────────
    # Wrap fold across the lower face (crimson, ties into the body plumage).
    pygame.draw.polygon(surf, CRIMSON_SH,
                        [(HX - 9, HY + 3), (HX + 13, HY + 1),
                         (HX + 12, HY + 9), (HX - 8, HY + 10)])
    pygame.draw.line(surf, CRIMSON_HI, (HX - 7, HY + 4), (HX + 11, HY + 2), 1)
    # Black eye-slit band wrapping the brow — the can't-miss face tell.
    pygame.draw.line(surf, CHARCOAL, (HX - 11, HY + 1), (HX + 13, HY - 3), 6)
    pygame.draw.line(surf, (10, 11, 15), (HX - 11, HY + 2), (HX + 13, HY - 2), 1)
    # Two cold eye glints peering out of the slit.
    pygame.draw.circle(surf, STEEL_HI, (HX + 1, HY - 1), 1)
    pygame.draw.circle(surf, STEEL_HI, (HX + 8, HY - 2), 1)

    # ── HEAD · steel forehead plate (diamond) centred on the brow, glinting ──
    px, py = HX + 1, HY - 6
    plate = [(px, py - 4), (px + 5, py), (px, py + 4), (px - 5, py)]
    pygame.draw.polygon(surf, STEEL_D, plate)
    inner = [(px, py - 3), (px + 4, py), (px, py + 3), (px - 4, py)]
    pygame.draw.polygon(surf, STEEL, inner)
    pygame.draw.line(surf, STEEL_HI, (px - 2, py - 1), (px, py - 3), 1)  # glint
    pygame.draw.circle(surf, STEEL_HI, (px - 1, py - 1), 1)


build = store_skins._make_skin(_paint, base_fn=_crimson_base)
