"""Production PAPER PLANE skin — concept STUNT / FIGHTER FOLD (`stunt_fold`).

Round-2 convergence: a SINGLE production build of the art-director's winner
V1 · RED RACING STRIPE — a clean Grand-Prix paper jet. Where the production
dollar-bill dart is a calm glider, this is the DYNAMIC alternative: a swept
delta hull whose value structure IS the livery.

The whole craft reads as THREE hard, flat, matte-paper values at gameplay
scale:

  * a bright WHITE lit top facet (the upper wing, above the keel crease),
  * a saturated RED keel band whose TOP EDGE is the fold crease itself — a
    hard white/red value boundary, not an airbrushed free-floating stripe,
  * a distinctly darker UNDER-fold below, so the keel crease is the hardest
    value break on the craft.

Contract (mirrors game/animal_paper_plane.py so this lifts straight into a
standalone game module):

  * `build_stunt_fold(wing_angle_deg) -> pygame.Surface`  draws ONE flat frame
    on a 64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * the craft's mass is centred at the BODY anchor (32, 44) — collision is a
    fixed 14px circle there, so the jet keeps its centre of mass on that point
    no matter how far the nose reaches.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_stunt_fold": get_stunt_fold}` at the bottom.

North star: "a skin lives or dies at 40px in motion." Nose points RIGHT
(forward). The 4 base wing poses become a snappy BANK/FLUTTER + nose-bob,
clamped so a stunt roll never flattens the delta to a sliver. A baked 1px
self-rim keeps the silhouette legible on day AND night skies. Matte finish —
flat facets, ONE hard crease, no glossy specular ramp (that drags toward a
plastic toy).
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline,
)


# ── canvas constants (match game/animal_paper_plane.py) ──────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body / mass centre → (32, 44)


# ── shared factory (local copy of _make_prebuilt_skin) ───────────────────────
def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle). Lazy 4-frame build + per-(frame, 3°) rotation cache,
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


def _poly(surf, color, pts, width=0):
    pygame.draw.polygon(surf, color, [(int(x), int(y)) for x, y in pts], width)


def _flutter(angle_deg):
    """Map a base wing angle (_WING_ANGLES runs 50→-40) to a centred −1..+1
    'catching air' factor. There are no wings, so the flap energy goes entirely
    into the jet snapping into a bank-roll + nose-bob."""
    return ((angle_deg + 40) / 90.0 - 0.5) * 2.0


def _bank(pts, cx, cy, roll_deg, bob):
    """Roll a point list about (cx, cy) and lift it by `bob`. The whole craft
    pivots about its mass centre so the silhouette banks as one rigid folded
    sheet — the cheapest paper-honest read of 'flap'."""
    r = math.radians(roll_deg)
    cos_r, sin_r = math.cos(r), math.sin(r)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        out.append((cx + dx * cos_r - dy * sin_r,
                    cy + dx * sin_r + dy * cos_r + bob))
    return out


# A stunt jet may bank a touch harder than the glider dart, but the roll is
# clamped so the delta never collapses edge-on to a sliver at gameplay scale.
_ROLL_MAX = 7.0


# ═════════════════════════════════════════════════════════════════════════════
# V1 · RED RACING STRIPE — the production fighter fold.
#
# The hull is a swept delta in 3/4 view. The KEEL crease runs nose→tail and is
# the spine of the whole read. Three flat matte facets meet at it:
#
#   * TOP facet  — the upper wing, lit bright white, ABOVE the crease.
#   * KEEL band  — saturated racing red, BELOW the crease. Its TOP edge IS the
#                  crease line, so the white→red boundary is a hard fold value
#                  break, never an airbrushed band floating in white.
#   * UNDER-fold — the lower wing dropping away beneath the keel, distinctly
#                  darker than both, so the keel crease is the hardest break.
#
# Matte discipline: flat fills only, ONE crisp crease, a single small nose
# bevel for fold-honesty — no glossy specular ramp.
# ═════════════════════════════════════════════════════════════════════════════
_PAL = {
    "top":      (244, 246, 250),    # bright white lit top facet
    "top_h":    (255, 255, 255),    # nose leading-edge bevel (flat, not gloss)
    "red":      (216, 40, 44),      # saturated racing red keel band
    "red_d":    (150, 22, 28),      # red keel in deeper shade toward the tail
    # Under-fold runs ~10% deeper than a neutral mid-grey so on a NIGHT sky the
    # white-top → under-fold delta never collapses to one mid-grey sliver; the
    # white top facet stays at full value, so the three-value read holds dark.
    "under":    (108, 116, 132),    # darker under-fold (hard value drop)
    "under_d":  (80, 88, 104),      # deepest under-fold wedge
    "crease":   (70, 76, 90),       # the fold spine (reads under the red lip)
    "rim":      (54, 60, 74),       # baked 1px self-rim — silhouette guarantee
}


def _hull_pts():
    """Anchor points for the swept-delta hull. Moderate sweep + a sharp nose
    reaching well past the mass centre. Returned in hull space (pre-bank)."""
    nose = (BCX + 25, BCY - 1)          # sharp pointed tip, far forward (right)
    far_tip = (BCX - 15, BCY - 12)      # swept-back UPPER wing trailing point
    near_tip = (BCX - 13, BCY + 14)     # swept-back LOWER wing trailing point
    tail = (BCX - 16, BCY)              # keel root at the back
    return nose, far_tip, near_tip, tail


def build_stunt_fold(wing_angle_deg):
    """One flat fighter-fold frame. The livery is the value structure, so the
    paint and the fold are drawn as ONE thing: white top / red keel / dark
    under-fold, all meeting at the keel crease."""
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 6.5))
    bob = -f * 1.4

    nose, far_tip, near_tip, tail = _hull_pts()

    # The keel crease line nose→tail. Every facet is keyed to it so the three
    # values share ONE hard boundary instead of three soft edges.
    keel_back = (BCX - 16, BCY)

    # ── UNDER-fold (lower wing, deepest shadow) — drawn first ────────────────
    # The whole lower facet drops away beneath the keel; a deeper wedge along
    # the trailing under-edge sets the value floor so the crease is the hardest
    # break on the craft.
    _poly(surf, _PAL["under"],
          _bank([nose, near_tip, keel_back], BCX, BCY, roll, bob))
    _poly(surf, _PAL["under_d"],
          _bank([nose, near_tip, (BCX - 6, BCY + 5)], BCX, BCY, roll, bob))

    # ── RED keel band — its TOP edge IS the crease ───────────────────────────
    # A tapered wedge hugging the keel: top edge nose→tail rides the crease
    # line exactly, bottom edge sits a few px below. White lives ABOVE this
    # edge; red lives BELOW it; the boundary is the fold. The far (tail) end is
    # shaded so the band carries its own light-to-dark without any gloss ramp.
    red_top_nose = (BCX + 23, BCY - 1)
    red_top_tail = keel_back
    red_bot_nose = (BCX + 22, BCY + 3)
    red_bot_tail = (BCX - 14, BCY + 4)
    _poly(surf, _PAL["red"],
          _bank([red_top_nose, red_top_tail, red_bot_tail, red_bot_nose],
                BCX, BCY, roll, bob))
    # Deeper red toward the tail so the keel band reads as folded paper, not a
    # flat decal — a value step, NOT a specular highlight.
    _poly(surf, _PAL["red_d"],
          _bank([(BCX - 4, BCY), red_top_tail, red_bot_tail, (BCX - 4, BCY + 3)],
                BCX, BCY, roll, bob))

    # ── TOP facet (lit upper wing) — fills everything ABOVE the crease ───────
    # Drawn AFTER the red so the crease edge is a clean white→red boundary; the
    # red band's top edge and this facet's lower edge are the SAME crease line.
    _poly(surf, _PAL["top"],
          _bank([nose, far_tip, keel_back, red_top_nose], BCX, BCY, roll, bob))
    # A single flat nose bevel where the top folds meet at the point — a hard
    # facet, not a gloss highlight (matte-paper finish).
    _poly(surf, _PAL["top_h"],
          _bank([nose, (BCX + 8, BCY - 6), (BCX + 11, BCY - 1)],
                BCX, BCY, roll, bob))

    # ── HARD keel crease — the fold spine, drawn last over the seam ──────────
    # A thin dark line riding the white/red boundary so the value break is
    # unambiguous at 40px and the red band reads as crisply BELOW the fold.
    a, b = _bank([(BCX + 24, BCY - 1), keel_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _PAL["crease"], (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 2)

    return _rim(surf, _PAL["rim"])


def _rim(surf, rim_col):
    """Bake a 1px self-rim from the painted alpha mask, stamped UNDER the art so
    it shows only as a clean 1px lip — the silhouette guarantee on any sky, no
    glow halo, no doubled 2px outline on the swept trailing edge."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_col, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Getter + registry. Lifts straight into game/animal_paper_plane.py as
# "skin_stunt_fold".
# ─────────────────────────────────────────────────────────────────────────────
get_stunt_fold = _make_prebuilt_skin(build_stunt_fold)

BUILDERS = {"skin_stunt_fold": get_stunt_fold}
