"""WIDE GLIDER — redesign candidates for the secret PAPER PLANE skin.

Five from-scratch takes on ONE concept: a broad FLAT-WING paper glider (a wide
delta / "Harrier"-style fold) seen 3/4 from above-behind, nosing RIGHT. This is
deliberately a DIFFERENT silhouette from the production dollar-bill dart — the
dart is a narrow triangle reaching forward; the glider is a WIDE planform that
reads as a slow soaring craft.

Contract (mirrors game/animal_paper_plane.py so a winning take lifts straight
into a standalone game module):

  * `build_glider_wide_vN(wing_angle_deg) -> pygame.Surface`  one flat frame on
    a 64x84 SRCALPHA canvas, mass centred at (32, 44).
  * NOSE POINTS RIGHT (forward). The bird faces right; the glider noses right.
  * No wings — the 4 base poses (_WING_ANGLES 50..-40) become a gentle
    BANK/FLUTTER + slow nose-bob + a soaring pitch sway, since a wide glider
    rides air rather than flaps.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a LOCAL
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_glider_wide": ...}` registry at the bottom.

North star: "a skin lives or dies at 40px in motion." A wide-but-thin wing can
vanish at gameplay scale, so every take leans on ONE bold WIDE silhouette + a
hard-value FOLD: a bright lit upper facet vs a distinctly darker under/shadow
facet, split along the centre keel, plus a baked 1px self-rim so the planform
holds on day AND night skies without any host outline.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)


# canvas constants (match game/animal_paper_plane.py)
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # mass centre -> (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3deg) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flutter(angle_deg):
    """Map a base wing angle (_WING_ANGLES runs 50->-40) to a centred -1..+1
    'catching air' factor that drives the soaring bank + nose-bob. No wings, so
    all the flap energy goes into the whole sheet swaying as it rides air."""
    return ((angle_deg + 40) / 90.0 - 0.5) * 2.0


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts], width)


def _bank(pts, cx, cy, roll_deg, bob, pitch=0.0):
    """Roll a point list about (cx, cy), lift by `bob`, and add a slow forward
    `pitch` shear (nose lifts/drops) so the whole rigid folded sheet sways as
    one — the most paper-honest read of 'flap' for a wingless glider."""
    r = math.radians(roll_deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        # Pitch shears y by horizontal distance from the mass centre: the nose
        # (positive dx, right) rises/falls opposite the tail.
        out.append((cx + dx * cos_r - dy * sin_r,
                    cy + dx * sin_r + dy * cos_r + bob + dx * pitch))
    return out


def _self_rim(surf, rim_color):
    """Bake a 1px self-rim hugging the painted silhouette so the planform reads
    on any sky without leaning on the host outline. Built from the alpha mask
    and stamped UNDER the art so it only shows as a clean lip."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_color, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


# Roll clamps keep the wide planform from rolling so far it collapses edge-on.
_ROLL_MAX = 5.0


# =============================================================================
# V1 - WIDE DELTA (white printer paper)
#
# The archetypal wide delta: a broad triangle whose trailing edge spans nearly
# the full canvas width, a blunt-ish nose, and a single centre keel splitting a
# bright LIT half from a shadowed half. Big, slow, unmistakably a glider.
# =============================================================================
_V1_TOP    = (244, 246, 250)        # lit upper facet (bright white paper)
_V1_TOP_H  = (255, 255, 255)        # leading-edge catch-light
_V1_UNDER  = (176, 188, 206)        # shadowed under-fold (cool grey, ~28% down)
_V1_UNDER_D = (150, 164, 186)       # deepest under wedge
_V1_KEEL   = (118, 130, 152)        # centre fold spine (hard value break)
_V1_RIM    = (96, 108, 132)


def build_glider_wide_v1(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 4.5))
    bob = -f * 1.2
    pitch = f * 0.06

    # Wide delta planform, nose RIGHT. The trailing edge is the far-left vertical
    # span; the nose is a blunt forward point.
    nose      = (BCX + 24, BCY)
    far_tip   = (BCX - 19, BCY - 17)        # upper (lit) trailing corner
    near_tip  = (BCX - 19, BCY + 17)        # lower (shadow) trailing corner
    tail_in   = (BCX - 12, BCY)             # trailing-edge notch toward keel

    def bk(pts):
        return _bank(pts, BCX, BCY, roll, bob, pitch)

    # UNDER (lower) half first.
    _poly(surf, _V1_UNDER, bk([nose, near_tip, tail_in]))
    _poly(surf, _V1_UNDER_D, bk([nose, near_tip, (BCX - 4, BCY + 6)]))
    # TOP (lit) half.
    _poly(surf, _V1_TOP, bk([nose, far_tip, tail_in]))
    _poly(surf, _V1_TOP_H, bk([nose, (BCX + 6, BCY - 7), (BCX + 9, BCY - 1)]))

    # HARD centre keel (the fold spine) nose -> trailing notch.
    a, b = bk([nose, tail_in])
    pygame.draw.line(surf, _V1_KEEL, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    return _self_rim(surf, _V1_RIM)


# =============================================================================
# V2 - SQUARE HARRIER (manila / kraft paper)
#
# A near-square stubby planform: short fuselage, almost-straight trailing edge,
# wide blunt nose. The "Harrier" read - boxy, flat, slow. Warm manila paper so
# it separates from V1's cool white. A raised fuselage strip down the centre.
# =============================================================================
_V2_TOP    = (226, 204, 158)        # lit manila facet
_V2_TOP_H  = (244, 228, 190)        # leading highlight
_V2_UNDER  = (168, 144, 100)        # shadow facet (~28% down)
_V2_UNDER_D = (144, 122, 82)
_V2_KEEL   = (110, 92, 60)
_V2_STRIP  = (200, 178, 132)        # raised fuselage strip (lit)
_V2_RIM    = (92, 76, 50)


def build_glider_wide_v2(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 4.0))
    bob = -f * 1.1
    pitch = f * 0.05

    # Square, stubby planform: wings reach far left/right with little taper.
    nose     = (BCX + 18, BCY)
    far_lead = (BCX + 10, BCY - 18)         # broad swept leading corner (upper)
    far_tail = (BCX - 18, BCY - 16)         # upper trailing corner
    near_lead = (BCX + 10, BCY + 18)
    near_tail = (BCX - 18, BCY + 16)
    tail_in  = (BCX - 14, BCY)

    def bk(pts):
        return _bank(pts, BCX, BCY, roll, bob, pitch)

    # UNDER half (lower wing + its trailing block).
    _poly(surf, _V2_UNDER, bk([nose, near_lead, near_tail, tail_in]))
    _poly(surf, _V2_UNDER_D, bk([tail_in, near_tail, (BCX - 4, BCY + 6)]))
    # TOP half.
    _poly(surf, _V2_TOP, bk([nose, far_lead, far_tail, tail_in]))
    _poly(surf, _V2_TOP_H, bk([nose, far_lead, (BCX + 4, BCY - 5)]))

    # Raised centre fuselage strip (lit), bordered by the hard keel.
    _poly(surf, _V2_STRIP, bk([(BCX + 16, BCY - 2), (BCX - 12, BCY - 3),
                               (BCX - 12, BCY + 1), (BCX + 16, BCY + 2)]))
    a, b = bk([nose, tail_in])
    pygame.draw.line(surf, _V2_KEEL, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    return _self_rim(surf, _V2_RIM)


# =============================================================================
# V3 - SWEPT GLIDER (pale blue construction paper)
#
# A wide planform with strongly SWEPT-back leading edges - a fast-soaring arrow
# delta. Sharper nose than V1/V2 but still WIDE at the trailing span. Pale-blue
# construction paper, so the colour identity differs again. The sweep gives a
# dynamic leading line the eye tracks at speed.
# =============================================================================
_V3_TOP    = (198, 222, 244)        # lit pale-blue facet
_V3_TOP_H  = (228, 240, 252)
_V3_UNDER  = (138, 168, 204)        # shadow facet
_V3_UNDER_D = (114, 146, 186)
_V3_KEEL   = (84, 114, 156)
_V3_RIM    = (70, 98, 138)


def build_glider_wide_v3(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3
    pitch = f * 0.07

    # Swept delta: nose forward + right, leading edges rake back to a WIDE
    # trailing span. Wider than tall so it reads as a glider, not a dart.
    nose      = (BCX + 25, BCY - 1)
    far_tip   = (BCX - 20, BCY - 18)
    near_tip  = (BCX - 20, BCY + 18)
    tail_in   = (BCX - 13, BCY)

    def bk(pts):
        return _bank(pts, BCX, BCY, roll, bob, pitch)

    # UNDER half.
    _poly(surf, _V3_UNDER, bk([nose, near_tip, tail_in]))
    _poly(surf, _V3_UNDER_D, bk([nose, near_tip, (BCX - 6, BCY + 5)]))
    # TOP half + a swept inner facet line accentuating the rake.
    _poly(surf, _V3_TOP, bk([nose, far_tip, tail_in]))
    _poly(surf, _V3_TOP_H, bk([nose, (BCX + 4, BCY - 8), (BCX + 8, BCY - 2)]))
    # Mid-wing crease echoing the swept leading edge (lit/shadow sub-split).
    c, d = bk([(BCX + 14, BCY - 5), far_tip])
    pygame.draw.line(surf, _V3_UNDER, (int(c[0]), int(c[1])),
                     (int(d[0]), int(d[1])), 1)

    a, b = bk([nose, tail_in])
    pygame.draw.line(surf, _V3_KEEL, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    return _self_rim(surf, _V3_RIM)


# =============================================================================
# V4 - WINGLET DELTA (white, with up-folded wingtips)
#
# The wide delta of V1 but with the wingtips UP-FOLDED into little winglets -
# the cleanest tip read: two dark vertical fins breaking the trailing corners so
# the wide span never blurs into the sky. The premium "real glider" detail.
# =============================================================================
_V4_TOP    = (242, 246, 252)
_V4_TOP_H  = (255, 255, 255)
_V4_UNDER  = (172, 186, 206)
_V4_UNDER_D = (146, 162, 186)
_V4_KEEL   = (112, 126, 150)
_V4_WINGLET = (120, 136, 162)       # up-folded tip fin (catches edge light)
_V4_WINGLET_D = (88, 102, 128)
_V4_RIM    = (92, 106, 132)


def build_glider_wide_v4(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 4.5))
    bob = -f * 1.2
    pitch = f * 0.06

    nose      = (BCX + 23, BCY)
    far_tip   = (BCX - 17, BCY - 16)
    near_tip  = (BCX - 17, BCY + 16)
    tail_in   = (BCX - 11, BCY)

    def bk(pts):
        return _bank(pts, BCX, BCY, roll, bob, pitch)

    # UNDER + TOP wide-delta halves.
    _poly(surf, _V4_UNDER, bk([nose, near_tip, tail_in]))
    _poly(surf, _V4_UNDER_D, bk([nose, near_tip, (BCX - 4, BCY + 6)]))
    _poly(surf, _V4_TOP, bk([nose, far_tip, tail_in]))
    _poly(surf, _V4_TOP_H, bk([nose, (BCX + 6, BCY - 7), (BCX + 9, BCY - 1)]))

    # Up-folded WINGLETS at both trailing corners: a small fin standing proud of
    # the planform. Far (upper) winglet leans away (lit edge), near leans toward.
    _poly(surf, _V4_WINGLET, bk([far_tip, (BCX - 21, BCY - 22),
                                 (BCX - 14, BCY - 20), (BCX - 13, BCY - 14)]))
    _poly(surf, _V4_WINGLET_D, bk([near_tip, (BCX - 21, BCY + 22),
                                   (BCX - 14, BCY + 20), (BCX - 13, BCY + 14)]))

    a, b = bk([nose, tail_in])
    pygame.draw.line(surf, _V4_KEEL, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    return _self_rim(surf, _V4_RIM)


# =============================================================================
# V5 - KEEL GLIDER (manila, deep central fuselage strip)
#
# Wide flat wings flanking a BOLD raised central keel/fuselage strip that runs
# the full length and stands proud as its own lit-vs-shadow ridge. The fuselage
# is the hero here: a chunky paper spine the eye locks onto, with the wings as
# broad flat shelves to either side. Warm manila, distinct from V2's stubby box.
# =============================================================================
_V5_WING   = (208, 186, 142)        # flat wing shelf (lit, manila)
_V5_WING_D = (160, 138, 98)         # shadow wing shelf (far/under)
_V5_KEEL_L = (236, 220, 182)        # raised keel ridge - lit top
_V5_KEEL_S = (150, 128, 88)         # raised keel ridge - shadow side
_V5_KEEL_C = (104, 86, 56)          # keel crease (hard break)
_V5_RIM    = (88, 72, 48)


def build_glider_wide_v5(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 4.0))
    bob = -f * 1.1
    pitch = f * 0.05

    nose      = (BCX + 22, BCY)
    far_tip   = (BCX - 18, BCY - 17)
    near_tip  = (BCX - 18, BCY + 17)
    tail_in   = (BCX - 12, BCY)

    def bk(pts):
        return _bank(pts, BCX, BCY, roll, bob, pitch)

    # Far (upper) flat wing shelf — in shadow because it tilts away from light.
    _poly(surf, _V5_WING_D, bk([nose, far_tip, tail_in]))
    # Near (lower) flat wing shelf — lit, facing the viewer/light.
    _poly(surf, _V5_WING, bk([nose, near_tip, tail_in]))

    # BOLD raised central keel running nose -> tail, drawn as two facets so the
    # spine itself has a lit top and a shadow side — a chunky paper fuselage.
    keel_top = bk([nose, (BCX - 14, BCY - 4), (BCX - 14, BCY), (BCX + 18, BCY)])
    keel_sh  = bk([nose, (BCX - 14, BCY), (BCX - 14, BCY + 4), (BCX + 18, BCY + 1)])
    _poly(surf, _V5_KEEL_S, keel_sh)
    _poly(surf, _V5_KEEL_L, keel_top)
    # Hard crease along the very top of the keel ridge.
    a, b = bk([nose, (BCX - 14, BCY - 4)])
    pygame.draw.line(surf, _V5_KEEL_C, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 2)
    # Bright nose catch-light on the keel point.
    nx, ny = bk([(BCX + 18, BCY - 1)])[0]
    pygame.draw.circle(surf, (252, 244, 220), (int(nx), int(ny)), 2)
    return _self_rim(surf, _V5_RIM)


# label -> getter dict (mirrors creature_skins.BUILDERS shape)
get_glider_wide_v1 = _make_prebuilt_skin(build_glider_wide_v1)
get_glider_wide_v2 = _make_prebuilt_skin(build_glider_wide_v2)
get_glider_wide_v3 = _make_prebuilt_skin(build_glider_wide_v3)
get_glider_wide_v4 = _make_prebuilt_skin(build_glider_wide_v4)
get_glider_wide_v5 = _make_prebuilt_skin(build_glider_wide_v5)

BUILDERS = {
    "glider_wide_v1": get_glider_wide_v1,
    "glider_wide_v2": get_glider_wide_v2,
    "glider_wide_v3": get_glider_wide_v3,
    "glider_wide_v4": get_glider_wide_v4,
    "glider_wide_v5": get_glider_wide_v5,
}
