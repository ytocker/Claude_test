"""Candidate PAPER PLANE skin — concept CLASSIC DART (round-1 exploration).

The iconic crisp WHITE printer-paper dart: sharp needle nose, a deep central
keel fold, clean swept facets. Timeless and minimal — the paper stays white /
cream, that is the whole point of this concept. There are no wings; the 4 base
wing poses (`parrot._WING_ANGLES`) are reinterpreted as a gentle BANK/FLUTTER:
the dart rolls a few degrees about its mass centre and the nose bobs as it
catches air, the way a real paper plane sways in flight.

Contract (mirrors game/animal_paper_plane.py so the WINNER lifts straight into
a standalone game/animal_paper_plane.py):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws one flat frame on a
    64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84), craft mass centred
    at (32, 44) — collision is a fixed 14px circle there.
  * NOSE POINTS RIGHT (forward) — drawn as-is, no host flip.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_dart_classic": get_dart_classic_v?}` registry.

North star: "a skin lives or dies at 40px in motion." Every take leans on ONE
bold triangular paper-airplane silhouette + a HARD-VALUE FOLD (bright upper
facet vs a distinctly darker under-fold meeting at a crisp central crease), and
bakes a 1px self-rim so the silhouette holds on day AND night without leaning on
a host outline. The five takes differ in FORM and SHADING of a white dart — view
angle, nose sharpness, keel depth, fold count, facet contrast, paper-shadow
temperature, and one optional faint accent.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── canvas constants (match game/animal_paper_plane.py) ──────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body / mass centre → (32, 44)


# ── shared factory (local copy of animal_paper_plane._make_prebuilt_skin) ────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache, each
    frame outlined with the house silhouette outline."""
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
    """Map a base wing angle (_WING_ANGLES runs 50→-40) to a centred −1..+1
    'catching air' factor. Drives the gentle bank-roll + nose-bob; there are no
    wings, so the flap energy goes entirely into the craft swaying."""
    return ((angle_deg + 40) / 90.0 - 0.5) * 2.0


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, pts, width)


def _bank(pts, cx, cy, roll_deg, bob):
    """Roll a point list a few degrees about (cx, cy) and lift it by `bob`.

    The whole craft pivots about its mass centre so the silhouette banks as one
    rigid folded sheet — the cheapest, most paper-plane-honest read of 'flap'."""
    r = math.radians(roll_deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * cos_r - dy * sin_r,
                    cy + dx * sin_r + dy * cos_r + bob))
    return out


def _self_rim(surf, rim_color):
    """Bake a 1px rim hugging the painted silhouette so the dart stays legible
    on day AND night skies without leaning on the host outline. Built from the
    alpha mask so it traces the TRUE outer edge, stamped UNDER the art so it
    only shows as a clean lip."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_color, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


# Roll clamp shared by all takes — the bank "flap" must never flatten the dart
# to a sliver (the under-fold collapses if the craft rolls too far edge-on).
_ROLL_MAX = 5.5


# ═════════════════════════════════════════════════════════════════════════════
# V1 · CLEAN SIDE PROFILE — the textbook dart, dead-on side view.
#
# One long isosceles silhouette: needle nose far right, a single straight top
# spine running nose→tail and a single bottom edge. The fold is a HARD value
# break — the upper facet is bright paper-white, the slim under-keel below the
# spine is a cool grey, meeting at a crisp central crease line. Minimal: no
# accents, no medallion. The purest read of "white paper dart".
# ═════════════════════════════════════════════════════════════════════════════
_V1_TOP   = (244, 246, 250)         # lit upper facet (bright paper white)
_V1_TOP_H = (255, 255, 255)         # nose / leading-edge specular
_V1_UNDER = (176, 186, 202)         # cool-grey under-keel (the shadow side)
_V1_UND_D = (150, 162, 182)         # deepest keel wedge
_V1_CREASE = (118, 130, 152)        # central fold spine (hard break)
_V1_RIM   = (96, 108, 132)          # baked self-rim


def build_dart_classic_v1(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    nose       = (BCX + 26, BCY - 1)
    tail_top   = (BCX - 16, BCY - 10)
    tail_bot   = (BCX - 16, BCY + 12)
    centre_back = (BCX - 17, BCY + 1)

    # Lower keel first (in shadow), then the lit upper facet on top.
    _poly(surf, _V1_UNDER, _bank([nose, tail_bot, centre_back], BCX, BCY, roll, bob))
    _poly(surf, _V1_UND_D, _bank([nose, tail_bot, (BCX - 4, BCY + 5)],
                                 BCX, BCY, roll, bob))
    _poly(surf, _V1_TOP, _bank([nose, tail_top, centre_back], BCX, BCY, roll, bob))
    # Leading-edge specular where the folds pinch to the needle nose.
    _poly(surf, _V1_TOP_H, _bank([nose, (BCX + 6, BCY - 6), (BCX + 9, BCY - 1)],
                                 BCX, BCY, roll, bob))

    a, b = _bank([nose, centre_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V1_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    return _self_rim(surf, _V1_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · SLIGHT 3/4 VIEW — both swept wings visible, tucked-back fuselage.
#
# Tilted so the eye sees the top of the dart: a high bright far-wing facet, a
# slightly darker near-wing facet below it, and a thin dark keel spine wedge
# between them. Reads as a real folded sheet seen from above-behind. Wider
# silhouette than V1 (two facets), warm-neutral paper so it stays clearly white.
# ═════════════════════════════════════════════════════════════════════════════
_V2_FAR   = (246, 247, 244)         # far (upper) wing — brightest
_V2_NEAR  = (210, 214, 218)         # near (lower) wing — half a stop down
_V2_NEAR_D = (184, 190, 198)        # near-wing shadow under the keel
_V2_KEEL  = (132, 140, 152)         # raised keel spine wedge
_V2_KEEL_H = (236, 238, 240)        # keel top highlight ridge
_V2_NOSE_H = (255, 255, 255)
_V2_RIM   = (104, 112, 128)


def build_dart_classic_v2(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    nose      = (BCX + 25, BCY - 2)
    far_tip   = (BCX - 15, BCY - 13)    # far wing trailing tip (up)
    near_tip  = (BCX - 13, BCY + 13)    # near wing trailing tip (down)
    keel_back = (BCX - 17, BCY)

    # Near (lower) wing facet first.
    _poly(surf, _V2_NEAR, _bank([nose, near_tip, keel_back], BCX, BCY, roll, bob))
    _poly(surf, _V2_NEAR_D, _bank([nose, near_tip, (BCX - 6, BCY + 4)],
                                  BCX, BCY, roll, bob))
    # Far (upper) wing facet — brightest, sits above the keel.
    _poly(surf, _V2_FAR, _bank([nose, far_tip, keel_back], BCX, BCY, roll, bob))

    # Raised keel spine between the two facets: a thin wedge nose→tail with a
    # bright top ridge so the central fold reads as a 3D ridge, not a flat line.
    _poly(surf, _V2_KEEL, _bank([nose, keel_back, (BCX - 4, BCY + 3)],
                                BCX, BCY, roll, bob))
    a, b = _bank([nose, keel_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V2_KEEL_H, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 2)
    _poly(surf, _V2_NOSE_H, _bank([nose, (BCX + 7, BCY - 5), (BCX + 8, BCY)],
                                  BCX, BCY, roll, bob))
    return _self_rim(surf, _V2_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · DEEP-KEEL RAZOR — extreme needle nose + a tall, dramatic keel fold.
#
# The most aggressive dart: a very long sharp nose reaching far past the mass
# centre and a DEEP under-keel (taller dark triangle) that drops well below the
# wing line. Maximum value contrast — bright white wing vs near-charcoal keel —
# so the fold is unmistakable at 40px. Cool steel-paper palette, fast & sharp.
# ═════════════════════════════════════════════════════════════════════════════
_V3_TOP   = (248, 250, 253)
_V3_TOP_H = (255, 255, 255)
_V3_KEEL  = (120, 132, 150)         # deep keel (strong, dark)
_V3_KEEL_D = (92, 104, 124)         # keel floor
_V3_CREASE = (74, 86, 106)          # crisp hard crease
_V3_RIM   = (78, 90, 110)


def build_dart_classic_v3(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    # Extra-long needle nose, tail pulled in tight → long razor triangle.
    nose       = (BCX + 30, BCY - 1)
    tail_top   = (BCX - 14, BCY - 9)
    keel_back  = (BCX - 16, BCY)
    keel_deep  = (BCX - 4, BCY + 16)    # the dramatic deep keel point

    # Deep keel triangle — a tall dark fold hanging below the wing.
    _poly(surf, _V3_KEEL, _bank([nose, keel_deep, keel_back], BCX, BCY, roll, bob))
    _poly(surf, _V3_KEEL_D, _bank([nose, keel_deep, (BCX + 4, BCY + 5)],
                                  BCX, BCY, roll, bob))
    # Bright upper wing facet.
    _poly(surf, _V3_TOP, _bank([nose, tail_top, keel_back], BCX, BCY, roll, bob))
    _poly(surf, _V3_TOP_H, _bank([nose, (BCX + 9, BCY - 5), (BCX + 11, BCY - 1)],
                                 BCX, BCY, roll, bob))

    # Hard crease nose→tail, thick so the value break carries at gameplay scale.
    a, b = _bank([nose, keel_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V3_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    return _self_rim(surf, _V3_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · NAKAMURA DOUBLE-FOLD — the refined dart with a second inner crease.
#
# A 3/4 view like V2 but with the Nakamura signature: an INNER wing-fold line
# parallel to the keel splits each wing into an inner darker band and an outer
# bright band. Two creases instead of one — reads as a more "engineered" fold.
# Soft cool-grey shadow palette; predominantly white with layered folds.
# ═════════════════════════════════════════════════════════════════════════════
_V4_OUT   = (245, 247, 250)         # outer bright wing band
_V4_IN    = (214, 220, 228)         # inner wing band (one fold deeper)
_V4_NEAR  = (190, 197, 208)         # near (lower) wing
_V4_NEAR_D = (166, 174, 188)
_V4_KEEL  = (120, 130, 148)
_V4_INNER_CREASE = (158, 168, 184)  # the soft inner Nakamura fold
_V4_CREASE = (96, 108, 130)         # hard central keel crease
_V4_RIM   = (96, 106, 124)


def build_dart_classic_v4(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    nose      = (BCX + 25, BCY - 2)
    far_tip   = (BCX - 15, BCY - 13)
    near_tip  = (BCX - 13, BCY + 13)
    keel_back = (BCX - 17, BCY)
    # Inner-fold landmark partway out the far wing.
    inner_mid = (BCX + 2, BCY - 6)
    inner_back = (BCX - 16, BCY - 4)

    # Near (lower) wing.
    _poly(surf, _V4_NEAR, _bank([nose, near_tip, keel_back], BCX, BCY, roll, bob))
    _poly(surf, _V4_NEAR_D, _bank([nose, near_tip, (BCX - 6, BCY + 4)],
                                  BCX, BCY, roll, bob))
    # Far wing: inner darker band (along the keel) then outer bright band.
    _poly(surf, _V4_IN, _bank([nose, inner_mid, inner_back, keel_back],
                              BCX, BCY, roll, bob))
    _poly(surf, _V4_OUT, _bank([nose, far_tip, inner_back, inner_mid],
                               BCX, BCY, roll, bob))
    # Inner (soft) Nakamura fold line running parallel to the keel.
    a, b = _bank([nose, inner_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V4_INNER_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 1)

    # Keel spine + hard central crease.
    _poly(surf, _V4_KEEL, _bank([nose, keel_back, (BCX - 4, BCY + 3)],
                                BCX, BCY, roll, bob))
    a, b = _bank([nose, keel_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V4_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    return _self_rim(surf, _V4_RIM)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · DOG-EAR ACCENT — clean white side dart with ONE subtle tell.
#
# The minimal V1 form, but with a single restrained accent so the skin has a
# tiny signature without losing its white-paper identity: a faint blue pencil
# stripe along the keel crease + a folded-corner "dog-ear" at the tail (a small
# turned-over paper triangle catching shadow). Everything else stays white.
# Warm cream paper here (vs V1's cool grey) so the set spans the temperature.
# ═════════════════════════════════════════════════════════════════════════════
_V5_TOP   = (248, 246, 238)         # warm cream paper
_V5_TOP_H = (255, 254, 250)
_V5_UNDER = (200, 196, 184)         # warm shadow under-keel
_V5_UND_D = (176, 170, 156)
_V5_CREASE = (146, 140, 126)        # central fold spine
_V5_PENCIL = (96, 124, 176)         # faint blue pencil accent stripe
_V5_DOGEAR = (210, 204, 190)        # turned-over corner (lit side)
_V5_DOGEAR_D = (162, 156, 142)      # dog-ear shadow crease
_V5_RIM   = (120, 114, 100)


def build_dart_classic_v5(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    nose       = (BCX + 26, BCY - 1)
    tail_top   = (BCX - 16, BCY - 10)
    tail_bot   = (BCX - 16, BCY + 12)
    centre_back = (BCX - 17, BCY + 1)

    _poly(surf, _V5_UNDER, _bank([nose, tail_bot, centre_back], BCX, BCY, roll, bob))
    _poly(surf, _V5_UND_D, _bank([nose, tail_bot, (BCX - 4, BCY + 5)],
                                 BCX, BCY, roll, bob))
    _poly(surf, _V5_TOP, _bank([nose, tail_top, centre_back], BCX, BCY, roll, bob))
    _poly(surf, _V5_TOP_H, _bank([nose, (BCX + 6, BCY - 6), (BCX + 9, BCY - 1)],
                                 BCX, BCY, roll, bob))

    # Folded-corner dog-ear at the upper tail: a small turned-over triangle that
    # catches shadow — the one bit of paper-fold storytelling, kept tiny.
    ear = _bank([tail_top, (BCX - 16, BCY - 3), (BCX - 9, BCY - 7)],
                BCX, BCY, roll, bob)
    _poly(surf, _V5_DOGEAR, ear)
    a, b = _bank([tail_top, (BCX - 9, BCY - 7)], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V5_DOGEAR_D, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 1)

    # Central crease + the faint pencil stripe just above it (the accent).
    a, b = _bank([nose, centre_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V5_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    pa, pb = _bank([(BCX + 18, BCY - 4), (BCX - 12, BCY - 6)],
                   BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V5_PENCIL, (int(pa[0]), int(pa[1])),
                     (int(pb[0]), int(pb[1])), 1)
    return _self_rim(surf, _V5_RIM)


# ── getters ──────────────────────────────────────────────────────────────────
get_dart_classic_v1 = _make_prebuilt_skin(build_dart_classic_v1)
get_dart_classic_v2 = _make_prebuilt_skin(build_dart_classic_v2)
get_dart_classic_v3 = _make_prebuilt_skin(build_dart_classic_v3)
get_dart_classic_v4 = _make_prebuilt_skin(build_dart_classic_v4)
get_dart_classic_v5 = _make_prebuilt_skin(build_dart_classic_v5)


# Label → getter, mirroring the review-sheet convention.
BUILDERS = {
    "v1 · clean side profile":   get_dart_classic_v1,
    "v2 · slight 3/4 view":      get_dart_classic_v2,
    "v3 · deep-keel razor":      get_dart_classic_v3,
    "v4 · nakamura double-fold": get_dart_classic_v4,
    "v5 · dog-ear accent":       get_dart_classic_v5,
}
