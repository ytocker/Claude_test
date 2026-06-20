"""Production PAPER PLANE skin for the coin Store — folded DOLLAR-BILL dart.

A secret ultra-premium NON-creature flyer: the player's flapping bird becomes
a folded banknote dart. There are no wings — the 4 base wing poses are
reinterpreted as a gentle BANK/FLUTTER: the dart rolls a few degrees and the
nose bobs as it catches air, the way a real paper plane sways in flight.

Contract (mirrors game/animal_skins.py so this lifts straight into a standalone
game/animal_paper_plane.py):

  * `build_paper_plane(wing_angle_deg) -> pygame.Surface`  draws one flat frame
    on a 64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * the craft's mass is centred at the BODY anchor (32, 44) — collision is a
    fixed 14px circle there, so the dart keeps its centre of mass on that point
    regardless of how far the nose reaches.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_paper_plane": get_paper_plane}` at the bottom.

North star: "a skin lives or dies at 40px in motion." The dart leans on ONE
bold triangular silhouette + a hard-value FOLD: a bright upper facet and a
distinctly darker under-fold meeting at a crisp central crease. The pale
portrait medallion (ringed so it holds its shape, not a bloom) reads as the
banknote signature, and a baked self-rim keeps the silhouette legible on day
AND night skies without leaning on any host outline.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── canvas constants (match game/animal_skins.py) ────────────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body / mass centre → (32, 44)


# ── shared factory (local copy of animal_skins._make_prebuilt_skin) ──────────
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


# ═════════════════════════════════════════════════════════════════════════════
# DOLLAR-BILL DART (3/4 view) — the premium tell: folded from a banknote.
#
# Value structure does the heavy lifting at 40px:
#   * the LIT upper facet is pushed bright money-green,
#   * the UNDER-fold is a distinctly darker green (~28% darker), so the central
#     crease is a HARD value break — the FOLD, not the hue, says "folded paper",
#   * a baked darker-green self-rim keeps the dart legible on any sky,
#   * a pale portrait medallion with a thin dark-green containment RING reads as
#     an intentional banknote oval (holds shape on bright day, never blooms).
# Gold denomination pips are HERO-only (invisible noise at 40px), gated below.
# ═════════════════════════════════════════════════════════════════════════════
_TOP     = (138, 186, 144)          # lit upper facet (lifted bright green)
_TOP_H   = (182, 218, 186)          # nose / leading-edge highlight
_UNDER   = (58, 100, 74)            # shadowed under-fold (~28% darker)
_UNDER_D = (42, 80, 60)             # deepest under-fold wedge
_CREASE  = (30, 58, 44)             # central fold spine (hard break)
_RIM     = (34, 64, 48)             # baked self-rim — silhouette guarantee
_OVAL    = (224, 238, 222)          # pale portrait medallion
_OVAL_RING = (46, 84, 60)           # dark-green containment ring (shape, not bloom)
_GOLD    = (236, 206, 120)          # corner numerals (hero-only)

# Roll is clamped so the bank-roll "flap" never flattens the dart to a sliver:
# at 3/4 view the under-fold collapses if the craft rolls too far edge-on.
_ROLL_MAX = 5.5


def build_paper_plane(wing_angle_deg, hero=False):
    """One flat dart frame. `hero` adds size-only flourishes (gold pips) that
    are deliberately omitted at gameplay scale where they read as noise."""
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 5.0))
    bob = -f * 1.3

    # Crisp dart geometry. The top swept edge runs nose→far_tip as a single
    # straight line so the triangular dart silhouette is unambiguous; the nose
    # is a tight point reaching well past the mass centre.
    nose = (BCX + 25, BCY - 1)
    far_tip = (BCX - 14, BCY - 13)
    near_tip = (BCX - 12, BCY + 14)
    centre_back = (BCX - 16, BCY)

    # ── UNDER-fold first (lower facet, in shadow) ────────────────────────────
    near = _bank([nose, near_tip, centre_back], BCX, BCY, roll, bob)
    _poly(surf, _UNDER, near)
    # A deepest wedge along the trailing under-edge deepens the value floor.
    _poly(surf, _UNDER_D, _bank([nose, near_tip, (BCX - 5, BCY + 5)],
                                BCX, BCY, roll, bob))

    # ── TOP facet (lit upper wing) ───────────────────────────────────────────
    far = _bank([nose, far_tip, centre_back], BCX, BCY, roll, bob)
    _poly(surf, _TOP, far)
    # Leading-edge highlight at the nose where the top folds meet at the point.
    _poly(surf, _TOP_H, _bank([nose, (BCX + 7, BCY - 6), (BCX + 9, BCY - 1)],
                              BCX, BCY, roll, bob))

    # ── HERO: portrait medallion on the lit far wing ─────────────────────────
    # Ring first, pale fill inside, so it reads as a contained oval (a deliberate
    # banknote medallion) rather than a soft bloom on bright day.
    # Pulled up onto the lit facet (clear of the crease) so the hard fold break
    # below it stays unbroken and the oval reads as its own contained medallion.
    ox, oy = _bank([(BCX - 1, BCY - 7)], BCX, BCY, roll, bob)[0]
    _aaellipse(surf, _OVAL_RING, (int(ox), int(oy)), 5, 6)
    _aaellipse(surf, _OVAL, (int(ox), int(oy)), 4, 5)

    # ── HARD central crease (the fold spine) ─────────────────────────────────
    # 3px so the value break between the lit top facet and the dark under-fold
    # is unambiguous at 40px — the FOLD carries "folded paper", not the colour.
    a, b = _bank([nose, centre_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)

    if hero:
        # Gold denomination pips live only at hero scale.
        for cx, cy in _bank([(BCX + 13, BCY - 11), (BCX - 10, BCY - 2)],
                            BCX, BCY, roll, bob):
            pygame.draw.circle(surf, _GOLD, (int(cx), int(cy)), 1)

    # ── baked self-rim ───────────────────────────────────────────────────────
    # A 1px darker-green ring hugging the WHOLE dart silhouette so it never
    # depends on the host's house outline — and no glow halo (keep glow
    # restraint). Built from the painted alpha mask so it traces the true outer
    # edge, then stamped UNDER the art so it only shows as a clean 1px lip.
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=_RIM, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


def build_paper_plane_hero(wing_angle_deg):
    return build_paper_plane(wing_angle_deg, hero=True)


get_paper_plane = _make_prebuilt_skin(build_paper_plane)
get_paper_plane_hero = _make_prebuilt_skin(build_paper_plane_hero)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry. Lifts straight into a standalone game module as
# "skin_paper_plane".
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {"skin_paper_plane": get_paper_plane}
