"""design_4 — JARL: the noble lord.

The dignified ruler of the five Viking takes. Where the others lean into raw
aggression, the Jarl reads as composure earned: a calm, level eye; a neatly
groomed, symmetrical mustache framing the beak; and a full, combed, rounded
beard pinched at its centre by one ornate ring into a tapered point — the
grooming of a man with servants.

The axe is the tell of rank, not a threat held forward: a compact ornate
BEARDED axe carried at a relaxed regal OVER-THE-SHOULDER hold. The head rides
behind and above the near shoulder so it breaks the top silhouette (a crown of
steel), and the haft angles forward across the body down to a visible gripping
claw at the belly. Still unmistakably an axe, still unmistakably held — just
worn the way a lord wears a sceptre.

The axe geometry is modeled on game/knight_skin.py::_sword: a straight haft
from a low grip to a high head, with the broad bearded blade flaring off the
head end. Scratch exploration only — not registered in store_skins.BUILDERS.
"""
import math

import pygame

from tools.viking_face_candidates import _shared as S


# Composite anchors (64x100 space). HX/HY = head centre, CROWN_Y = helm crown.
HX, HY, CROWN_Y = 47, 41, 31


def _paint_face(surf, wing_angle, P):
    """A NEAT, NOBLE face: a calm level eye, a groomed mustache framing the
    beak, and a rounded combed beard cinched by one ornate ring into a point.
    Drawn ON TOP of the helm brow so the eye stays legible under the nasal."""
    beard, beard_hi = P["beard"], P["beard_hi"]
    ring = P["ring"]
    white = P["white"]

    # The face sits on the HEAD/beak zone (the bird looks right; the beak is at
    # x~55-61). Beard hangs below the chin and down the jaw toward the body, the
    # mustache frames the beak, and the eye reads under the helm brow at ~(51,43).

    # ── rounded full beard (a groomed wedge under the chin, not a blob) ───────
    # Widest at the jaw just under the cheek, pinched at the ring, tapering to a
    # single point. Centred on the head (ring ~(52,55)) so it clasps the chin —
    # not floating out on the belly.
    ring_x, ring_y = 50, 55               # clasp centre (under the chin)
    jaw_l, jaw_r = 43, 57                 # jawline width, hugging the beak base
    jaw_y = 48
    tip_x, tip_y = 49, 62                 # tapered point below the clasp
    # Outer beard mass: jaw -> bulge -> pinch at the ring -> point -> back up.
    _shape = [
        (jaw_l, jaw_y),
        (jaw_l, 52),
        (ring_x - 6, ring_y - 1),         # pinch in toward the ring (near side)
        (ring_x - 4, ring_y + 3),
        (tip_x, tip_y),                   # tapered point
        (ring_x + 5, ring_y + 3),
        (ring_x + 7, ring_y - 1),         # pinch in toward the ring (far side)
        (jaw_r, 52),
        (jaw_r, jaw_y),
        (52, 47),                         # under-beak notch so the beak shows
    ]
    pygame.draw.polygon(surf, beard, _shape)
    # A 1px darker edge under the jaw so the beard separates from the brown body.
    pygame.draw.lines(surf, P["eye_pupil"], False,
                      [(jaw_l, 52), (ring_x - 6, ring_y - 1), (ring_x - 4, ring_y + 3),
                       (tip_x, tip_y), (ring_x + 5, ring_y + 3),
                       (ring_x + 7, ring_y - 1), (jaw_r, 52)], 1)

    # Combed strand lines — symmetrical, converging on the ring/point so the
    # beard reads as parted hair gathered by the clasp, not a textured slab.
    # `bone` (much lighter than the brown body) catches the comb so the beard
    # pops as groomed hair against the body; `beard_hi` fills between.
    # Combed hair radiating from the cheeks toward the ring/point — staggered
    # lengths so they read as parted strands, not two parallel bars. `bone`
    # (much lighter than the body) catches a few; `beard_hi` fills the rest.
    bone = P["bone"]
    strands = [
        ((jaw_l + 1, jaw_y + 2), (ring_x - 4, 53), bone),
        ((jaw_l + 3, 51), (ring_x - 3, ring_y + 1), beard_hi),
        ((51, jaw_y + 3), (tip_x, tip_y - 2), beard_hi),
        ((jaw_r - 1, jaw_y + 2), (ring_x + 4, 53), bone),
        ((jaw_r - 3, 51), (ring_x + 3, ring_y + 1), beard_hi),
    ]
    for a, b, col in strands:
        pygame.draw.line(surf, col, a, b, 1)
    # A lit top rim on the cheek mass (bone) so the rounded groomed form reads.
    pygame.draw.line(surf, bone, (jaw_l + 1, jaw_y + 1), (52, jaw_y + 1), 1)

    # ── ornate ring clasping the beard's centre, pinching it to the point ────
    # Drawn a touch larger and brighter so the single clasp is unmistakable as
    # the Jarl's grooming detail even against the dark beard mass.
    pygame.draw.circle(surf, beard, (ring_x, ring_y), 5)        # recess shadow
    pygame.draw.circle(surf, ring, (ring_x, ring_y), 4)
    pygame.draw.circle(surf, beard, (ring_x, ring_y), 2)        # hollow centre
    pygame.draw.circle(surf, ring, (ring_x, ring_y), 4, 1)      # raised rim
    pygame.draw.circle(surf, white, (ring_x - 1, ring_y - 1), 1)  # bead glint

    # ── groomed mustache framing the beak (neat, symmetric sweep) ────────────
    # Two combed wings sitting across the base of the gold beak (where the dark
    # hair pops against the light beak), sweeping out and curling down at the
    # corners — trimmed, not bushy.
    mcx, must_y = 55, 45
    for sgn in (-1, 1):
        rootx = mcx + sgn * 1
        midx = mcx + sgn * 5
        tipx = mcx + sgn * 8
        wing = [
            (rootx, must_y - 1),
            (midx, must_y),
            (tipx, must_y + 3),           # outer tip curls down past the beak
            (midx, must_y + 3),
            (rootx, must_y + 2),
        ]
        pygame.draw.polygon(surf, beard, wing)
        pygame.draw.line(surf, beard_hi, (rootx, must_y), (tipx, must_y + 2), 1)

    # ── the calm commanding eye (drawn last so the brow never covers it) ─────
    ex, ey = 51, 43
    # almond skin field
    pygame.draw.ellipse(surf, P["eye_skin"], (ex - 4, ey - 3, 9, 6))
    pygame.draw.ellipse(surf, beard, (ex - 4, ey - 3, 9, 6), 1)   # soft lid line
    # level pupil — gazing forward, composed
    pygame.draw.circle(surf, P["eye_pupil"], (ex + 1, ey), 2)
    pygame.draw.circle(surf, P["eye_glint"], (ex, ey - 1), 1)     # life glint
    # a calm level brow above (not the angry diagonal of a berserker)
    pygame.draw.line(surf, beard, (ex - 4, ey - 4), (ex + 4, ey - 4), 2)
    pygame.draw.line(surf, beard_hi, (ex - 3, ey - 5), (ex + 3, ey - 5), 1)


def _paint_axe(surf, wing_angle, P):
    """A compact ornate BEARDED axe at a relaxed regal OVER-THE-SHOULDER hold.

    Geometry mirrors knight_skin._sword: a straight haft from a low GRIP (claw
    at the belly) up to a high HEAD behind/above the near shoulder, with the
    broad bearded blade flaring off the head end so it breaks the top
    silhouette. Drawn LAST, so the held axe is never occluded."""
    blade, blade_dk, blade_hi = P["blade"], P["blade_dk"], P["blade_hi"]
    haft, haft_hi = P["haft"], P["haft_hi"]
    white = P["white"]
    ring = P["ring"]

    # The bird faces RIGHT, so the NEAR shoulder is on the right. A regal
    # over-the-shoulder carry rests the head up-and-right above that shoulder
    # (breaking the TOP silhouette), with the haft angling down-LEFT across the
    # body to the gripping claw at the belly.
    # Grip at the belly, head up-right above the near shoulder. The haft is
    # routed to the RIGHT of the beard (kept clear of the face band) so the
    # groomed face stays legible — the axe is carried beside the head, not over
    # it.
    gx, gy = 46, 60          # grip / claw at the belly
    hx, hy = 63, 25          # haft head end, above the near (right) shoulder
    ux, uy = hx - gx, hy - gy
    ln = math.hypot(ux, uy) or 1.0
    ux, uy = ux / ln, uy / ln          # unit along haft (grip -> head)
    px, py = -uy, ux                    # unit perpendicular (points up-right)

    # ── haft: a turned wooden shaft from grip to head ────────────────────────
    pygame.draw.line(surf, blade_dk, (gx, gy), (hx, hy), 5)      # dark keyline
    pygame.draw.line(surf, haft, (gx, gy), (hx, hy), 3)
    pygame.draw.line(surf, haft_hi,
                     (gx - px, gy - py), (hx - px, hy - py), 1)  # lit edge
    # one bronze binding ring high on the shaft (clear of the face) — the ornate,
    # lordly touch without cluttering the groomed beard.
    wx, wy = gx + (hx - gx) * 0.62, gy + (hy - gy) * 0.62
    pygame.draw.line(surf, ring, (wx + px * 2.0, wy + py * 2.0),
                     (wx - px * 2.0, wy - py * 2.0), 2)
    pygame.draw.line(surf, white, (wx + px * 1.4, wy + py * 1.4),
                     (wx - px * 0.2, wy - py * 0.2), 1)

    # ── axe head: a compact bearded blade flaring off the head end ───────────
    # Socket where the head seats on the haft, a little below the very top butt.
    sx, sy = hx - ux * 3, hy - uy * 3
    butt = (hx + ux * 3, hy + uy * 3)                  # the poll / butt at top
    # The blade flares OUTWARD (toward +perp, away from the body) with the
    # classic bearded silhouette: a swept cutting edge that dips well below the
    # socket toward the haft (the "beard" of a bearded axe).
    top_horn = (sx + px * 12 - ux * 3, sy + py * 12 - uy * 3)   # upper horn
    edge_mid = (sx + px * 13 + ux * 4, sy + py * 13 + uy * 4)   # cutting arc
    beard_lo = (sx + px * 8 + ux * 10, sy + py * 8 + uy * 10)   # the beard hook
    heel = (sx + px * 2 + ux * 8, sy + py * 2 + uy * 8)         # back to haft
    blade_poly = [butt, top_horn, edge_mid, beard_lo, heel]
    pygame.draw.polygon(surf, blade_dk, blade_poly)
    # inner lit face, inset toward the socket
    inner = [
        (butt[0] + px * 1.5, butt[1] + py * 1.5),
        (top_horn[0] - px * 2.5, top_horn[1] - py * 2.5),
        (edge_mid[0] - px * 2.5, edge_mid[1] - py * 2.5),
        (beard_lo[0] - px * 2.0, beard_lo[1] - py * 2.0),
        (heel[0] + px * 1.0, heel[1] + py * 1.0),
    ]
    pygame.draw.polygon(surf, blade, inner)
    # bright honed cutting edge along the outer arc (horn -> mid -> beard)
    pygame.draw.line(surf, blade_hi, top_horn, edge_mid, 2)
    pygame.draw.line(surf, blade_hi, edge_mid, beard_lo, 2)
    pygame.draw.line(surf, white, top_horn, edge_mid, 1)
    # a forge-spark glint on the cheek of the blade
    glint_x = sx + px * 6 + ux * 2
    glint_y = sy + py * 6 + uy * 2
    pygame.draw.circle(surf, white, (int(glint_x), int(glint_y)), 1)
    # socket band where blade meets haft (bronze, ornate)
    pygame.draw.line(surf, ring, (sx + px * 3, sy + py * 3),
                     (sx - px * 1, sy - py * 1), 2)

    # ── the gripping claw at the belly, closed over the haft ─────────────────
    pygame.draw.circle(surf, P["beard"], (gx, gy), 3)             # paw shadow
    pygame.draw.circle(surf, haft, (gx, gy), 2)                   # wood through grip
    for k in (-1, 0, 1):                                          # three toes over haft
        cxk = gx - 2 + k * 2
        pygame.draw.line(surf, P["beard"], (cxk, gy - 2), (cxk, gy + 2), 1)
    pygame.draw.circle(surf, P["beard_hi"], (gx + 1, gy - 1), 1)


build_ironclad = S.make_build(_paint_face, _paint_axe, S.IRONCLAD)
build_bloodaxe = S.make_build(_paint_face, _paint_axe, S.BLOODAXE)
