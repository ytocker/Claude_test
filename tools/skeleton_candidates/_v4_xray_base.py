"""Shared foundation for the v4 SKELETON x-ray explorations (scratch only).

The whole point of v4 is that every candidate is an x-ray of the EXACT
original Pip macaw — same silhouette, same beak location, same tail
location — with a COMPLETE skeleton inside it and a dominant beak bone.
Faithfulness comes for free by recolouring the real sprite geometry
(`_build_parrot_with_palette`) to a dark "flesh", then painting bones
*through* it.

To kill the "some bones are missing" failure for good, the anatomy lives
here ONCE: `paint_skeleton()` lays down the full bird skeleton (skull,
hollow eye-socket, dominant beak bone, cervical→caudal spine, full
ribcage + keel, shoulder + wing arm-bones and phalanges that flap in
register with the wing, pelvis, both legs, clawed feet, tail bones). The
five designs import it and differ ONLY in the STYLE dict + an optional
post-pass (bloom / glow / hatching) — so anatomy is identical and only the
bone *material* changes.

NOT registered in store_skins.BUILDERS. Production is untouched.
"""
import math
import pygame

from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette, _build_wing
from game.parrot import SPRITE_W, SPRITE_H
from game.store_skins import COMPOSITE_W, COMPOSITE_H, PARROT_DY


# ── dark translucent "flesh": the original silhouette, x-ray-dimmed ───────────
# Near-black cool charcoal so bright bone reads as showing THROUGH the body.
# A hair of lift on belly/crown keeps the silhouette alive on the night sky;
# the bones carry the read either way.
P_FLESH = _pal(
    tail=[(20, 22, 34), (26, 28, 42), (32, 35, 50), (38, 41, 58)],
    tail_line=(12, 13, 22),
    body_shadow=(12, 13, 22),
    body_main=(26, 28, 42),
    body_chest=(32, 35, 50),
    body_belly=(40, 44, 62),
    sheen=None,
    wing_main=(22, 24, 38),
    wing_dark=(13, 14, 24),
    wing_tip=(30, 33, 50),
    wing_secondary=None,
    wing_highlight=None,
    head_shadow=(16, 18, 28),
    head_main=(30, 33, 50),
    head_cheek=(38, 42, 60),
    head_crown=(42, 46, 66),
    lens_frame=(0, 0, 0), lens_body=(0, 0, 0),
    lens_tint=None, lens_glint=None,
    beak_main=(24, 26, 40),
    beak_dark=(14, 15, 26),
    beak_gloss=(34, 37, 56),
    foot=(20, 22, 34),
)


def bone_parrot(angle_deg):
    """The exact original macaw silhouette recoloured to dark flesh."""
    return _build_parrot_with_palette(angle_deg, P_FLESH, draw_lenses=False)


# ── the cloak: the dark "back" mass redrawn as a draped hooded cloak ──────────
# User ask: the black back of the parrot should read as a CLOAK. Instead of the
# plain body+tail ellipses, the body mass becomes a hooded, open-front cloak in
# NATIVE 64×60 space (same space as `_build_parrot_with_palette`, so the existing
# composite `paint_skeleton` skull/ribs/beak still land exactly): a cowl wraps the
# crown/back of the skull, the drape flares down the back into a tattered hem where
# the tail was, and an open V at the chest keeps the ribcage + spine + beak visible
# (the round_2 x-ray hero is NOT lost behind cloth). Cloth tones derive from the
# design's flesh palette so each design recolours the SAME cloak silhouette; opts
# hooks (edge / inner / hatch / glow) let a design add its own material treatment.


def _shade(c, f):
    """Multiply an RGB(A) toward black (f<1) or white (f>1), clamped."""
    return tuple(max(0, min(255, int(round(v * f)))) for v in c[:3])


# Cloak silhouette polygons, in native 64×60 coords (skull centre ~(47,21),
# body centre ~(32,32), tail mass to the left, feet ~(28..36, 45..49)).
# The C2 critics were unanimous: at 40px a cloak only reads by SILHOUETTE, so the
# hem is cut as hard triangular teeth on the OUTER edge (interior notches dissolve)
# and the bottom edge zig-zags top→tip→top so `_add_outline` traces a ragged hem.
_CLOAK_DRAPE = [                                   # back drape with a hard-toothed tattered hem
    (13, 28), (20, 24), (28, 22), (36, 22), (42, 24), (46, 28),   # shoulders → top
    (45, 34), (42, 40),                                          # front-right fall
    (37, 48), (33, 42), (28, 50), (24, 41), (19, 49), (15, 40),  # hem teeth (R→L)
    (10, 48), (8, 38),                                           # last tooth → back edge
]
_CLOAK_CHEST = [                                   # open-front V (widened): dark interior the ribs show through
    (41, 24), (46, 31), (44, 41), (36, 47),
    (27, 47), (21, 40), (19, 29), (27, 24),
]
_HOOD_OUTER = [                                    # cowl cloth over crown/back/sides of skull, sharp peak
    (36, 31), (37, 16), (41, 8), (47, 4), (53, 8),
    (58, 15), (58, 24), (54, 30), (44, 32),
]
_HOOD_RIM = [(44, 32), (54, 30), (58, 24), (58, 15), (53, 8), (47, 4)]
# Hem highlight traces the toothed bottom edge so the rim catches the ragged hem.
_HEM_EDGE = [(8, 38), (10, 48), (15, 40), (19, 49), (24, 41), (28, 50),
             (33, 42), (37, 48), (42, 40)]
_FOLDS = [                                         # one long vertical fall + two shorter, all on the back drape
    [(29, 25), (26, 47)],
    [(21, 26), (17, 45)],
    [(14, 30), (12, 44)],
]


def cloak_base(angle_deg, palette, **opts):
    """Native 64×60 cloaked-Pip body: a hooded, open-front cloak replacing the
    plain body/tail ellipses, in the given flesh `palette`'s dark cloth tones.

    opts:
      cloth  — override the main cloak cloth colour (default palette body_main).
               Lever to LIFT the cloak value off near-navy so it reads on night.
      edge   — override hood-rim/hem highlight colour (default lifted belly tone)
      inner  — override chest-opening / hood-interior colour (default deep shadow)
      hatch  — if truthy, add etched fold hatching across the drape (woodcut)
      glow   — (r,g,b): faint emissive halo on hood rim + hem (neon / radiograph)
    """
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    cloth = opts.get('cloth') or palette['body_main']
    shadow = palette['tail_line']
    # Default rim clearly lifts off the cloth so the hood/hem read as fabric
    # edges even before a design adds its own material treatment.
    edge = opts.get('edge') or _shade(cloth, 2.4)
    inner = opts.get('inner') or _shade(palette['body_shadow'], 0.55)
    glow = opts.get('glow')

    # back + bottom drape (the cloak mass), then fold shadows so it reads as cloth
    pygame.draw.polygon(surf, cloth, _CLOAK_DRAPE)
    for a, b in _FOLDS:
        pygame.draw.line(surf, shadow, a, b, 2)
    if opts.get('hatch'):
        for off in range(-6, 30, 5):                # diagonal etched hatching
            pygame.draw.line(surf, shadow, (10 + off, 24), (off, 46), 1)

    # open-front chest: dark recessed interior the ribcage/spine read against,
    # framed by a 2px shadow gap so the bright bones win the opening at 40px
    pygame.draw.polygon(surf, inner, _CLOAK_CHEST)
    pygame.draw.polygon(surf, shadow, _CLOAK_CHEST, 2)

    # wing flaps over the drape (dark backing for the wing-bone layer, and it
    # reads as the cloak swaying with the flap)
    wing = _build_wing(angle_deg, palette)
    surf.blit(wing, wing.get_rect(center=(34, 28)).topleft)

    # hood cowl over the skull, with a dark interior so the skull sits recessed,
    # plus a hard shadow crescent rim so the skull "peers out of a hole"
    pygame.draw.polygon(surf, cloth, _HOOD_OUTER)
    face = pygame.Rect(38, 9, 20, 24)
    pygame.draw.ellipse(surf, inner, face)                         # face opening
    pygame.draw.ellipse(surf, shadow, face, 2)                     # recess crescent

    # faint emissive edge first (sits under the crisp highlight)
    if glow is not None:
        g = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)
        pygame.draw.lines(g, (*glow, 90), False, _HOOD_RIM, 3)
        pygame.draw.lines(g, (*glow, 90), False, _HEM_EDGE, 3)
        surf.blit(g, (0, 0))

    # crisp lighter rim on the hood + tattered hem so it reads as fabric
    pygame.draw.lines(surf, edge, False, _HOOD_RIM, 1)
    pygame.draw.lines(surf, edge, False, _HEM_EDGE, 1)

    # feet poking out below the hem
    pygame.draw.line(surf, palette['foot'], (28, 47), (26, 51), 2)
    pygame.draw.line(surf, palette['foot'], (34, 47), (36, 51), 2)

    return surf


def cloak_parrot(angle_deg):
    """Default cloaked base on the shared P_FLESH tones (smoke-test / fallback)."""
    return cloak_base(angle_deg, P_FLESH)


def _frames_from_cloak(paint_fn, palette, **opts):
    """Like `_frames_from_paint` but on the cloak base: 4 outlined frames with the
    skeleton painted over a palette-driven hooded cloak."""
    from game import store_skins
    return store_skins._make_skin(
        paint_fn, base_fn=lambda a: cloak_base(a, palette, **opts))


# ── anatomy, in COMPOSITE space (base coords + PARROT_DY on y) ────────────────
# Original anchors (parrot.py): head centre (47,21) r~11; beak quad
# (55,21)(61,24)(58,28)(52,26); body centre (32,32) r 19×14; wing centre
# (34,28); feet (28,45)/(34,45). +PARROT_DY(20) on every y to reach composite.
DY = PARROT_DY
HX, HY = 47, 21 + DY                       # skull centre → (47,41)
WING_CENTER = (34, 28 + DY)                # (34,48) — matches _build_wing blit

# Cervical → thoracic → lumbar → caudal vertebra centres (skull base to tail).
_SPINE = [(43, 23 + DY), (39, 25 + DY), (34, 27 + DY), (29, 29 + DY),
          (24, 31 + DY), (19, 33 + DY), (14, 34 + DY)]

# ── avian ribcage ─────────────────────────────────────────────────────────────
# A bird ribcage reads as a rounded BASKET: each rib springs off the thoracic
# spine, bows OUT and DOWN around the chest, then curves FORWARD to land on a
# deep breastbone (the keel/sternum). At 40px it only reads as a cage if there
# are ENOUGH ribs at an EVEN pitch with a clear top (spine) and bottom (keel)
# boundary — a few straight slashes read as claw-marks, not bone.
#
# 6 rib roots, evenly pitched along the thoracic spine, spreading BACK from the
# shoulder (x 37) to the lumbar region (x 20). Roots sit on the spine = the
# cage's top/back boundary.
_RIB_ROOTS = [(37, 25 + DY), (34, 26 + DY), (31, 28 + DY),
              (27, 29 + DY), (24, 31 + DY), (20, 32 + DY)]
# Sternum/keel: the breastbone the ribs sweep FORWARD onto. It is a short deep
# plate at the FRONT-BOTTOM of the chest (x 30→39, the avian "boat keel"), so
# every rib arcs from its spread-out spine root forward-and-down to land here —
# the convergence is what makes the chest read as a rounded basket, not a fence
# of parallel bars. The keel is the cage's hard bottom-front boundary.
_KEEL = [(39, 41 + DY), (38, 44 + DY), (36, 46 + DY),
         (33, 47 + DY), (31, 46 + DY), (30, 44 + DY)]

# Wing arm-bones + phalanges in the 50×50 WING-LOCAL space (so they rotate
# with the wing exactly like the feather polygon does).
_WING_LOCAL = {
    "humerus": [(24, 24), (35, 18)],
    "radius":  [(35, 18), (46, 25)],
    "phalanges": [
        [(46, 25), (45, 14)],
        [(46, 25), (49, 22)],
        [(46, 25), (40, 31)],
        [(42, 22), (45, 16)],
    ],
    "joints": [(24, 24), (35, 18), (46, 25)],
}


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _rib_curve(i):
    """Rib `i` as a smooth C-curve: springs off the spine root, bows OUT and
    DOWN around the chest, then sweeps FORWARD onto its keel landing — a single
    rib of the basket. Quadratic Bézier root→belly-control→keel so the curve
    actually bends (the old version was nearly straight, reading as a slash).

    Accepts either a rib index OR a root tuple (the frozen designs 1/3/4/5
    iterate `for r0 in _RIB_ROOTS` and pass the root), so both call styles work.
    """
    if not isinstance(i, int):
        i = _RIB_ROOTS.index(i)
    root = _RIB_ROOTS[i]
    keel = _KEEL[i]
    # Belly control point pushed DOWN and BACK (lower x) of the root→keel chord
    # so the rib bulges OUT into a rounded basket wall before sweeping forward to
    # the keel. Back ribs (high i, roots far behind the keel) get a deeper, more
    # lateral bulge so the cage rounds off at the back instead of going straight.
    bulge = 5.0 + i * 0.8                       # deeper toward the back
    back = 2.5 + i * 1.2                        # push the belly behind the chord
    cx = (root[0] + keel[0]) / 2 - back
    cy = max(root[1], keel[1]) + bulge
    ctrl = (cx, cy)
    pts = []
    for s in range(9):
        t = s / 8.0
        u = 1 - t
        x = u * u * root[0] + 2 * u * t * ctrl[0] + t * t * keel[0]
        y = u * u * root[1] + 2 * u * t * ctrl[1] + t * t * keel[1]
        pts.append((x, y))
    return pts


# ── styled stroke primitives ─────────────────────────────────────────────────

def stroke(surf, color, p0, p1, w):
    """A bone shaft with rounded caps."""
    pygame.draw.line(surf, color, p0, p1, w)
    r = max(1, w // 2)
    pygame.draw.circle(surf, color, (int(round(p0[0])), int(round(p0[1]))), r)
    pygame.draw.circle(surf, color, (int(round(p1[0])), int(round(p1[1]))), r)


def polybone(surf, color, pts, w):
    for i in range(len(pts) - 1):
        stroke(surf, color, pts[i], pts[i + 1], w)


def knob(surf, color, p, r):
    pygame.draw.circle(surf, color, (int(round(p[0])), int(round(p[1]))), r)


# Default STYLE keys a design can override:
#   bone   — main bone colour (the bright element)
#   hi     — highlight rim (None to skip)
#   sh     — keyline/shadow under bone for day-sky legibility (None to skip)
#   w_long / w_rib / w_fine — stroke widths for long bones / ribs / fine bones
#   beak   — dominant-beak fill colour (defaults to bone)
DEFAULT_STYLE = dict(
    bone=(238, 240, 246), hi=(255, 255, 255), sh=(20, 22, 34),
    w_long=3, w_rib=2, w_fine=2, beak=None,
)


def _wing_bone_layer(angle_deg, style):
    """Render wing arm-bones + phalanges in local space, rotate by the wing
    angle, return the rotated surface and its blit topleft for WING_CENTER."""
    w = pygame.Surface((50, 50), pygame.SRCALPHA)
    col, sh, hi = style["bone"], style["sh"], style["hi"]
    wl, wf = style["w_long"], style["w_fine"]
    if sh is not None:
        stroke(w, sh, *_WING_LOCAL["humerus"], wl + 2)
        stroke(w, sh, *_WING_LOCAL["radius"], wl + 2)
        for ph in _WING_LOCAL["phalanges"]:
            stroke(w, sh, *ph, wf + 1)
    stroke(w, col, *_WING_LOCAL["humerus"], wl)
    stroke(w, col, *_WING_LOCAL["radius"], wl)
    for ph in _WING_LOCAL["phalanges"]:
        stroke(w, col, *ph, wf)
    for j in _WING_LOCAL["joints"]:
        knob(w, col, j, max(2, wl - 1))
        if hi is not None:
            knob(w, hi, (j[0] - 1, j[1] - 1), 1)
    rot = pygame.transform.rotate(w, angle_deg)
    tl = rot.get_rect(center=WING_CENTER).topleft
    return rot, tl


def paint_skeleton(surf, angle_deg, style=None):
    """Paint the COMPLETE bird skeleton onto the composite (over dark flesh).

    Designs pass a STYLE dict for the bone material; anatomy is fixed here so
    no bone can go missing. Wing phalanges rotate in register with `angle_deg`.
    """
    st = dict(DEFAULT_STYLE)
    if style:
        st.update(style)
    bone, hi, sh = st["bone"], st["hi"], st["sh"]
    wl, wr, wf = st["w_long"], st["w_rib"], st["w_fine"]
    beak_col = st["beak"] or bone

    # ── keyline pass (drawn first, slightly fatter, for day-sky legibility) ──
    if sh is not None:
        for i in range(len(_RIB_ROOTS)):
            polybone(surf, sh, _rib_curve(i), wr + 1)
        polybone(surf, sh, _SPINE, wl + 1)
        polybone(surf, sh, _KEEL, wr + 1)

    # ── wing arm-bones + phalanges (behind the body bones, flapping) ─────────
    layer, tl = _wing_bone_layer(angle_deg, st)
    surf.blit(layer, tl)

    # ── ribcage ──────────────────────────────────────────────────────────────
    for i in range(len(_RIB_ROOTS)):
        polybone(surf, bone, _rib_curve(i), wr)
    polybone(surf, bone, _KEEL, wr)                     # sternum/keel

    # ── spine + vertebra knobs ───────────────────────────────────────────────
    polybone(surf, bone, _SPINE, wl)
    for v in _SPINE:
        knob(surf, bone, v, max(2, wl - 1))
        if hi is not None:
            knob(surf, hi, (v[0] - 1, v[1] - 1), 1)

    # ── pelvis + two legs + clawed feet ──────────────────────────────────────
    pelvis = (22, 33 + DY)
    knob(surf, bone, pelvis, wl)
    for hipx, foot, splay in ((25, (26, 49 + DY), -3), (30, (36, 49 + DY), 3)):
        knee = (hipx + splay, 45 + DY)
        stroke(surf, bone, pelvis, knee, wl)            # femur
        stroke(surf, bone, knee, foot, wf)              # tibia
        # 3-toe claw
        for dx in (-3, 0, 3):
            stroke(surf, bone, foot, (foot[0] + dx, foot[1] + 3), max(1, wf - 1))

    # ── tail bones (caudal vertebrae fanning into the original tail) ─────────
    tail_root = _SPINE[-1]
    for tip in ((3, 35 + DY), (4, 41 + DY), (9, 42 + DY), (15, 39 + DY)):
        stroke(surf, bone, tail_root, tip, wf)

    # ── skull + hollow eye-socket ────────────────────────────────────────────
    skull_r = 11
    if sh is not None:
        pygame.draw.circle(surf, sh, (HX, HY), skull_r + 1, wf + 1)
    pygame.draw.circle(surf, bone, (HX, HY), skull_r, wf)
    pygame.draw.circle(surf, bone, (HX - 1, HY - 4), 5, max(1, wf - 1))  # cranium dome
    # hollow eye socket (dark, ringed in bone)
    pygame.draw.circle(surf, (8, 9, 16), (HX + 3, HY - 1), 4)
    pygame.draw.circle(surf, bone, (HX + 3, HY - 1), 4, max(1, wf - 1))
    knob(surf, bone, (HX + 2, HY - 2), 1)

    # ── DOMINANT beak bone (the signature element) ───────────────────────────
    # Original beak sits forward of the skull, tip ~(61,44) composite. Built up
    # into an oversized hooked avian beak-bone that PROJECTS FORWARD (not up):
    # long upper mandible curving to a downward raptor hook, hinged lower jaw,
    # nostril notch — the biggest, most-salient bone on the bird.
    upper = [(54, 37), (66, 42), (67, 47), (62, 47), (57, 44), (54, 42)]
    lower = [(55, 45), (63, 46), (62, 49), (55, 47)]
    if sh is not None:
        pygame.draw.polygon(surf, sh, [(p[0], p[1] + 1) for p in upper])
    pygame.draw.polygon(surf, beak_col, upper)
    pygame.draw.polygon(surf, beak_col, lower)
    pygame.draw.line(surf, st["sh"] or beak_col, (55, 44), (63, 45), 1)  # mandible gap
    knob(surf, (8, 9, 16), (57, 41), 1)                 # nostril
    if hi is not None:
        pygame.draw.line(surf, hi, (55, 39), (65, 43), 1)  # culmen gloss


def _frames_from_paint(paint_fn):
    """Helper for designs: build the 4 outlined, x-ray frames via the standard
    skin factory using bone_parrot as the dark-flesh base."""
    from game import store_skins
    return store_skins._make_skin(paint_fn, base_fn=bone_parrot)
