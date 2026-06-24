"""v4 SKELETON · design_5 — ETCHED WOODCUT (scratch exploration only).

A vintage engraving / anatomy-plate look: the original Pip macaw skeleton drawn
as crisp WHITE LINE-ART — bones read as OUTLINED shapes (not solid fills) with
fine parallel hatching / cross-hatching for shading, struck over a charcoal
body. The full anatomy is fixed in `_v4_xray_base`; this file changes only the
bone *material* into hand-engraved linework and adds the hatching passes.

The engraving is built in three superimposed strikes, the way a real woodcut
plate layers tone:
  • a thin solid white SPINE-PASS from the shared painter places every bone in
    exactly the right anatomy (no bone can go missing), kept narrow so it reads
    as a contour line, not a fill;
  • a HATCHING pass lays short parallel white ticks ALONG the shafts and ACROSS
    the curved bones (ribs, skull, beak) for the engraved cross-hatch tone, plus
    a few darker shadow ticks struck into the flesh just beside each bone so the
    body reads as etched too;
  • the DOMINANT hooked beak bone is re-struck as the boldest single piece of
    line-art on the bird — a doubled contour with its own dense hatch — so it is
    unmistakably the hero even when the body hatching simplifies at 40px.

Flesh is cool charcoal (the woodcut "ink") so the white linework reads as
engraved bone showing through. NOT registered in store_skins.BUILDERS.
Production is untouched.
"""
import math
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB


# ── engraving inks ───────────────────────────────────────────────────────────
# Bone line-art is near-white but a hair cool so it sits like printed ink, not a
# glow. The hatch line is a dimmer grey so cross-hatch tone reads as SHADING
# rather than more solid bone; the shadow hatch struck into the flesh is darker
# than the charcoal body so the body itself looks etched.
INK_BONE   = (236, 238, 246)        # main white contour line
INK_HATCH  = (150, 158, 178)        # mid-grey engraving hatch (shading tone)
INK_DEEP   = (14, 15, 26)           # near-black crevice / socket ink
FLESH_DARK = (15, 16, 27)           # shadow hatch struck into the charcoal body
BEAK_INK   = (250, 251, 255)        # beak contour a touch brighter — the hero

# Thin bones so the shared painter lays CONTOUR LINES, not fat shafts. No `hi`
# (engraving has no specular), no cold `sh` keyline — the hatching carries the
# day-sky legibility instead of a fat outline.
STYLE = dict(
    bone=INK_BONE, hi=None, sh=None,
    w_long=1, w_rib=1, w_fine=1, beak=INK_BONE,
)


def _norm(p0, p1):
    """Unit direction + unit perpendicular for a segment, for hatch placement."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    d = math.hypot(dx, dy) or 1.0
    ux, uy = dx / d, dy / d
    return (ux, uy), (-uy, ux), d


def _hatch_along(surf, p0, p1, color, step=2.2, length=2.0, side=1, skip=0):
    """Strike short parallel ticks crossing the shaft p0→p1 at `step` spacing,
    each `length` long, offset to one `side`. This is the engraving cross-hatch
    that gives a bone its rounded, shaded body."""
    (ux, uy), (px, py), d = _norm(p0, p1)
    n = int(d / step)
    for i in range(skip, n):
        t = i / max(1, n)
        cx = p0[0] + ux * d * t
        cy = p0[1] + uy * d * t
        ax = cx
        ay = cy
        bx = cx + px * length * side
        by = cy + py * length * side
        pygame.draw.line(surf, color, (ax, ay), (bx, by), 1)


def _flesh_shadow(surf, p0, p1, side=1, step=3.0, length=2.0):
    """Dark ticks struck into the charcoal flesh just beside a bone, so the body
    reads as engraved tone (the woodcut hallmark) rather than flat ink."""
    (ux, uy), (px, py), d = _norm(p0, p1)
    n = int(d / step)
    for i in range(n):
        t = i / max(1, n)
        cx = p0[0] + ux * d * t + px * 2.0 * side
        cy = p0[1] + uy * d * t + py * 2.0 * side
        bx = cx + px * length * side
        by = cy + py * length * side
        pygame.draw.line(surf, FLESH_DARK, (cx, cy), (bx, by), 1)


def _hatch_polybone(surf, pts, color, side=1, step=2.2, length=2.0):
    for i in range(len(pts) - 1):
        _hatch_along(surf, pts[i], pts[i + 1], color, step, length, side)


def _engrave_pass(surf):
    """Lay the engraving tone over the already-placed white contour skeleton.

    Nothing here MOVES a bone — it only hatches the fixed anatomy so each bone
    bulges into a shaded, hand-cut tube and the flesh beside it reads etched."""
    DY = XB.DY

    # Spine: hatch along the shaft (round it) + a faint flesh shadow under it.
    _hatch_polybone(surf, XB._SPINE, INK_HATCH, side=1, step=2.4, length=2.0)
    _flesh_shadow(surf, XB._SPINE[0], XB._SPINE[-1], side=1)

    # Keel/sternum: a broad plate, so cross-hatch it on both sides for body.
    _hatch_polybone(surf, XB._KEEL, INK_HATCH, side=1, step=2.2, length=2.2)
    _hatch_polybone(surf, XB._KEEL, INK_HATCH, side=-1, step=3.0, length=1.6)

    # Ribs: each rib gets cross-ticks on its outer side (sells curved depth) and
    # a dark flesh shadow on the inner side so ribs read COUNTABLE and engraved.
    for r0 in XB._RIB_ROOTS:
        pts = XB._rib_curve(r0)
        _hatch_polybone(surf, pts, INK_HATCH, side=-1, step=2.2, length=2.2)
        _flesh_shadow(surf, pts[0], pts[-1], side=1, step=3.5, length=2.0)

    # Pelvis + legs: hatch the long bones; knees keep a small bright contour knob.
    pelvis = (22, 33 + DY)
    XB.knob(surf, INK_BONE, pelvis, 2)
    XB.knob(surf, INK_DEEP, (pelvis[0], pelvis[1] + 1), 1)
    for hipx, foot, splay in ((25, (26, 49 + DY), -3), (30, (36, 49 + DY), 3)):
        knee = (hipx + splay, 45 + DY)
        _hatch_along(surf, pelvis, knee, INK_HATCH, step=2.4, length=1.8, side=1)
        _hatch_along(surf, knee, foot, INK_HATCH, step=2.6, length=1.6, side=-1)
        XB.knob(surf, INK_BONE, knee, 1)

    # Tail bones: light hatch along each caudal ray.
    tail_root = XB._SPINE[-1]
    for tip in ((3, 35 + DY), (4, 41 + DY), (9, 42 + DY), (15, 39 + DY)):
        _hatch_along(surf, tail_root, tip, INK_HATCH, step=3.0, length=1.4, side=1)

    # Wing arm-bones are on a rotated sub-layer in the base; hatch a fixed hint
    # along the shoulder→wrist line in composite space so the wing reads engraved
    # without fighting the rotation (kept short so it never crosses the body).
    _hatch_along(surf, (30, 24 + DY), (40, 20 + DY), INK_HATCH,
                 step=2.4, length=1.6, side=-1)

    # Skull: cross-hatch the cranium dome (an arc of short ticks) and deepen the
    # orbit into a real hollow socket ringed in white line.
    cx, cy, r = XB.HX, XB.HY, 11
    for a in range(-150, 30, 22):          # ticks around the upper-left dome
        rad = math.radians(a)
        ox, oy = math.cos(rad), math.sin(rad)
        pygame.draw.line(surf, INK_HATCH,
                         (cx + ox * (r - 3), cy + oy * (r - 3)),
                         (cx + ox * (r - 1), cy + oy * (r - 1)), 1)
    pygame.draw.circle(surf, INK_DEEP, (cx + 3, cy - 1), 3)
    pygame.draw.circle(surf, INK_BONE, (cx + 3, cy - 1), 4, 1)
    pygame.draw.circle(surf, INK_BONE, (cx, cy), r, 1)   # crisp cranium contour


def _beak_hero(surf):
    """The dominant hooked beak bone — the boldest line-art on the bird. Drawn as
    a DOUBLED white contour (so the hook outline pops) with its own dense
    engraving hatch inside, hinged at the skull and projecting forward to a
    downturned raptor tip. Stays legible even when body hatch simplifies."""
    # A long, deeply hooked upper mandible (longer than the base footprint) and a
    # hinged lower jaw — outlined, not solid, in the engraving idiom.
    upper = [(54, 36), (62, 39), (68, 43), (69, 49), (64, 50),
             (60, 46), (56, 43), (54, 41)]
    lower = [(55, 45), (64, 47), (63, 51), (55, 48)]

    # Dark interior so the white outline + hatch read AS line-art on dark, then
    # the doubled bold contour.
    pygame.draw.polygon(surf, INK_DEEP, upper)
    pygame.draw.polygon(surf, INK_DEEP, lower)
    pygame.draw.polygon(surf, BEAK_INK, upper, 2)        # bold doubled outline
    pygame.draw.polygon(surf, BEAK_INK, lower, 1)

    # Dense parallel hatch filling the upper mandible body (follows the culmen),
    # the engraving tone that makes the hook read as solid heroic bone.
    for k in range(5):
        t = k / 4.0
        a = XB._lerp((54, 38), (62, 40), t)
        b = XB._lerp((58, 44), (67, 46), t)
        pygame.draw.line(surf, INK_HATCH, a, b, 1)
    # Bright culmen ridge (the top line of the hook) — the single boldest stroke.
    pygame.draw.lines(surf, BEAK_INK, False,
                      [(54, 37), (60, 38), (66, 42), (68, 47)], 2)
    pygame.draw.line(surf, INK_DEEP, (55, 45), (64, 47), 1)   # mandible gap
    pygame.draw.circle(surf, INK_DEEP, (58, 41), 1)           # nostril fossa


def _paint(surf, angle):
    """Paint the woodcut skeleton: lay the thin white contour anatomy, strike the
    engraving hatch over it, then re-cut the bold hero beak bone on top."""
    XB.paint_skeleton(surf, angle, style=STYLE)
    _engrave_pass(surf)
    _beak_hero(surf)


def _make():
    return XB._frames_from_paint(_paint)


build = _make()
