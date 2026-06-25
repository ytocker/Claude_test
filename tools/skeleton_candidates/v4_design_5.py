"""v4 SKELETON · design_5 — ETCHED WOODCUT (scratch exploration only).

A vintage engraving / anatomy-plate look: the original Pip macaw skeleton drawn
as crisp WHITE LINE-ART — bones read as OUTLINED shapes (not solid fills) with
fine parallel hatching / cross-hatching for shading, struck over a charcoal
body. The full anatomy is fixed in `_v4_xray_base`; this file changes only the
bone *material* into hand-engraved linework and adds the hatching passes.

The bone CONTOUR is the meal; the hatch is seasoning. The whole skeleton reads
with the hatch pass turned off — that is the rule that keeps it legible at 40px.
Built in three superimposed strikes, the way a real woodcut plate layers tone:
  • a BOLD 2px white contour pass from the shared painter places every bone in
    exactly the right anatomy (no bone can go missing) over a near-black
    understroke that keeps the white lines alive against pale day clouds;
  • a thin, DIM, SPARSE hatch pass adds engraved tone on top — a few ticks along
    each shaft and across the lower curve of the ribs — clearly subordinate to
    the contours, never competing as line. No flesh-shadow ticks (they turned to
    noise at scale and destroyed the rib count), so the body stays clean charcoal;
  • the DOMINANT hooked beak bone is re-struck as the boldest single piece of
    line-art on the bird — a THICK 3px doubled contour with a pure-bone culmen
    ridge — so it out-values the skull by a clear margin even at 40px.

Flesh is cool charcoal (the woodcut "ink") so the white linework reads as
engraved bone showing through. NOT registered in store_skins.BUILDERS.
Production is untouched.
"""
import math
import pygame

from tools.skeleton_candidates import _v4_xray_base as XB


# ── engraving inks ───────────────────────────────────────────────────────────
# The BONE contour is the structure (the meal); the HATCH is seasoning. So the
# value gap between them is wide: bone reads near-white and bold, hatch sits a
# dim cool blue-grey so it clearly reads as TONE, never a competing line. The
# whole skeleton must read with the hatch pass turned off — hence the bold
# contours below and the near-black understroke for day-sky legibility.
INK_BONE   = (236, 238, 246)        # main white contour line — bright STRUCTURE
INK_HATCH  = (95, 105, 130)         # dim cool hatch — clearly subordinate TONE
INK_DEEP   = (14, 15, 26)           # near-black crevice / socket ink
INK_UNDER  = (8, 9, 16)             # near-black understroke under spine/keel/beak
BEAK_INK   = (252, 253, 255)        # beak contour pure bone — the hero

# ── the cloak's OWN tonal register (the round_4 fix) ─────────────────────────
# The memento-mori grammar is white bone over a hatched DARK cloak. The two
# hatch systems must separate by VALUE, not direction: the bone hatch stays
# bright + fine (INK_HATCH at ~40% white), the cloak fold hatch drops to a
# mid-grey ~60% of bone white AND coarsens its pitch — fewer, fatter diagonal
# strokes — so the engraved cloth is unmistakably a darker, heavier tone than
# the crisp white engraving on the bone. CLOTH lifts the drape off the navy
# background (+1 step over the darkest night bg) so the hatched cape has a
# surface to sit on and survives night; CLOAK_INNER drops the chest/hood lining
# to the same mid-grey so the white ribcage is the topmost layer in the open V.
CLOAK_CLOTH = (46, 51, 70)          # dark cool-grey cloth — a real surface at night
CLOAK_HATCH = (132, 138, 158)       # mid-grey fold hatch (~57% of bone white)
CLOAK_INNER = (74, 80, 100)         # lining/recess mid-grey, BELOW the white ribs

# Bold 2px bone contours so the skeleton survives with hatch OFF; the painter's
# `sh` understroke keeps those white lines from vanishing against pale day
# clouds. The hatch (added in _engrave_pass) is struck thin on top as tone only.
STYLE = dict(
    bone=INK_BONE, hi=None, sh=INK_UNDER,
    w_long=2, w_rib=2, w_fine=1, beak=INK_BONE,
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


def _hatch_polybone(surf, pts, color, side=1, step=3.6, length=2.0):
    for i in range(len(pts) - 1):
        _hatch_along(surf, pts[i], pts[i + 1], color, step, length, side)


def _engrave_pass(surf):
    """Lay the engraving tone over the already-placed white contour skeleton.

    Nothing here MOVES a bone — it only hatches the fixed anatomy so each bone
    bulges into a shaded, hand-cut tube and the flesh beside it reads etched."""
    DY = XB.DY

    # Hatch is seasoning struck thin on top of the already-bold contours: dim,
    # sparse, one side only. The flesh-shadow ticks are GONE — at 40px they were
    # pure noise that destroyed the rib count, so the body stays clean charcoal.

    # Spine: a single sparse hatch run along the shaft to round it.
    _hatch_polybone(surf, XB._SPINE, INK_HATCH, side=1, step=4.0, length=1.6)

    # Keel/sternum: light cross-hatch on the outer side only (no double pass).
    _hatch_polybone(surf, XB._KEEL, INK_HATCH, side=1, step=3.6, length=1.8)

    # Ribs stay 4 CLEAN curved contour lines (drawn bold by the base painter).
    # Only the lower-belly third of each gets a few dim ticks for curved depth,
    # so the ribs read countable, not hatched into mush.
    for r0 in XB._RIB_ROOTS:
        pts = XB._rib_curve(r0)
        lower = pts[len(pts) * 2 // 3:]
        _hatch_polybone(surf, lower, INK_HATCH, side=-1, step=4.0, length=1.6)

    # Pelvis + legs: sparse single-side hatch; knees keep a bright contour knob.
    pelvis = (22, 33 + DY)
    XB.knob(surf, INK_BONE, pelvis, 2)
    XB.knob(surf, INK_DEEP, (pelvis[0], pelvis[1] + 1), 1)
    for hipx, foot, splay in ((25, (26, 49 + DY), -3), (30, (36, 49 + DY), 3)):
        knee = (hipx + splay, 45 + DY)
        _hatch_along(surf, pelvis, knee, INK_HATCH, step=4.0, length=1.4, side=1)
        XB.knob(surf, INK_BONE, knee, 1)

    # Wing arm-bones are on a rotated sub-layer in the base; a single short hatch
    # hint along the shoulder→wrist line so the wing reads engraved without
    # fighting the rotation (kept short so it never crosses the body).
    _hatch_along(surf, (30, 24 + DY), (40, 20 + DY), INK_HATCH,
                 step=4.0, length=1.4, side=-1)

    # Skull: cross-hatch the cranium dome (an arc of short ticks) and deepen the
    # orbit into a real hollow socket ringed in white line.
    cx, cy, r = XB.HX, XB.HY, 11
    for a in range(-150, 30, 32):          # sparse ticks around the upper-left dome
        rad = math.radians(a)
        ox, oy = math.cos(rad), math.sin(rad)
        pygame.draw.line(surf, INK_HATCH,
                         (cx + ox * (r - 3), cy + oy * (r - 3)),
                         (cx + ox * (r - 1), cy + oy * (r - 1)), 1)
    pygame.draw.circle(surf, INK_DEEP, (cx + 3, cy - 1), 3)
    pygame.draw.circle(surf, INK_BONE, (cx + 3, cy - 1), 4, 1)
    pygame.draw.circle(surf, INK_BONE, (cx, cy), r, 1)   # crisp cranium contour


def _beak_hero(surf):
    """The dominant hooked beak bone — the boldest line-art on the bird, and it
    must out-value the skull by a clear margin at 40px. Drawn as a THICK 3px
    doubled white contour with a pure-bone culmen ridge as the single boldest
    stroke; interior hatch is cut to a couple of ticks so the contour stays the
    hero. Hinged at the skull, projecting forward to a downturned raptor tip."""
    # A long, deeply hooked upper mandible (longer than the base footprint) and a
    # hinged lower jaw — outlined, not solid, in the engraving idiom.
    upper = [(54, 36), (62, 39), (68, 43), (69, 49), (64, 50),
             (60, 46), (56, 43), (54, 41)]
    lower = [(55, 45), (64, 47), (63, 51), (55, 48)]

    # Near-black understroke (offset down-right) so the white beak outline holds
    # against pale day clouds; dark interior so the contour reads AS line-art.
    pygame.draw.polygon(surf, INK_UNDER, [(p[0] + 1, p[1] + 1) for p in upper])
    pygame.draw.polygon(surf, INK_DEEP, upper)
    pygame.draw.polygon(surf, INK_DEEP, lower)
    pygame.draw.polygon(surf, BEAK_INK, upper, 3)        # THICK bold contour
    pygame.draw.polygon(surf, BEAK_INK, lower, 2)

    # Just two dim ticks of interior tone — enough to say "engraved", not enough
    # to dim the hero. The contour and culmen carry the read.
    for t in (0.35, 0.65):
        a = XB._lerp((55, 39), (63, 41), t)
        b = XB._lerp((57, 44), (66, 46), t)
        pygame.draw.line(surf, INK_HATCH, a, b, 1)
    # Bright culmen ridge (the top line of the hook) — the single boldest stroke.
    pygame.draw.lines(surf, BEAK_INK, False,
                      [(54, 37), (60, 38), (66, 42), (68, 47)], 3)
    pygame.draw.line(surf, INK_DEEP, (55, 45), (64, 47), 1)   # mandible gap
    pygame.draw.circle(surf, INK_DEEP, (58, 41), 1)           # nostril fossa


def _paint(surf, angle):
    """Paint the woodcut skeleton: lay the thin white contour anatomy, strike the
    engraving hatch over it, then re-cut the bold hero beak bone on top."""
    XB.paint_skeleton(surf, angle, style=STYLE)
    _engrave_pass(surf)
    _beak_hero(surf)


# The dark "back" mass is a hooded open-front CLOAK (shared cloak base) in the
# woodcut idiom. round_4 fixes the hatch collision the art-director flagged:
# instead of the shared `hatch=True` (which strikes fine fold-hatch in the same
# near-black/dim register as the bone hatch — the two melt into mush), the cloak
# is given its OWN tonal register. We feed the hardened base a lifted CLOAK_CLOTH
# (so the drape is a real dark-cool-grey surface, not navy that night swallows)
# and a mid-grey CLOAK_INNER lining (so the white ribcage is unambiguously the
# top layer in the open V), turn the base hatch OFF, then strike our OWN coarse,
# mid-grey diagonal fold hatch — fewer, fatter strokes at a DARKER value than the
# bright fine bone hatch — clipped to the back-drape so the two engraving systems
# read as two tones (white bone vs darker cloth), never one mush.
CLOAK_EDGE = INK_BONE          # engraved keyline white traces the toothed hem/hood


def _drape_mask():
    """A 1-bit mask of the back-drape polygon so the coarse cloak hatch is
    clipped to the cloth and never crosses the open chest / bone field."""
    m = pygame.Surface((XB.SPRITE_W, XB.SPRITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(m, (255, 255, 255, 255), XB._CLOAK_DRAPE)
    # Carve the open chest back out so hatch never bleeds onto the rib field.
    pygame.draw.polygon(m, (0, 0, 0, 0), XB._CLOAK_CHEST)
    return m


_DRAPE_MASK = None


def _coarse_cloak_hatch(surf):
    """Strike the cloak's fold hatch in its OWN register: a COARSE diagonal pitch
    (fatter, wider-spaced than the fine bone hatch) at a mid-grey value ~60% of
    bone white. Clipped to the drape mask so the cloth tone stays on the cloak."""
    global _DRAPE_MASK
    h = pygame.Surface((XB.SPRITE_W, XB.SPRITE_H), pygame.SRCALPHA)
    # Coarse pitch (step 6 vs the bone hatch's ~2.2) and 2px strokes — a heavier,
    # darker engraving than the crisp fine white on the bone. The slant follows
    # the drape's diagonal fall so it reads as fold-shading on the cloth, and the
    # value (mid-grey) sits well below the bone white so the two registers never
    # collide into mush.
    for off in range(-12, 42, 6):
        pygame.draw.line(h, (*CLOAK_HATCH, 240),
                         (14 + off, 22), (off - 6, 51), 2)
    if _DRAPE_MASK is None:
        _DRAPE_MASK = _drape_mask()
    h.blit(_DRAPE_MASK, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(h, (0, 0))


def _cloak_base_r4(angle):
    """The hardened cloak base on lifted cloth tones (base hatch OFF), then our
    own coarse mid-grey fold hatch — the two-register woodcut cloak."""
    surf = XB.cloak_base(angle, XB.P_FLESH,
                         cloth=CLOAK_CLOTH, inner=CLOAK_INNER,
                         edge=CLOAK_EDGE, hatch=False)
    _coarse_cloak_hatch(surf)
    return surf


def _make():
    from game import store_skins
    return store_skins._make_skin(_paint, base_fn=_cloak_base_r4)


build = _make()
