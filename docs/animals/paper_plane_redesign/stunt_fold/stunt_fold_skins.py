"""Candidate PAPER PLANE skin — concept STUNT / FIGHTER FOLD (`stunt_fold`).

Round-1 exploration: five genuinely DIFFERENT takes on ONE concept — an
angular hot-rod paper JET. Where the production dollar-bill dart is a calm
glider, this concept is the most DYNAMIC candidate: swept-back delta wings,
an aggressive pointed nose, and a BOLD TWO-TONE LIVERY (racing keel stripe,
lightning bolt, chevron, blueprint outline, retro race number) carried as
STRUCTURE so it survives the 40px downscale.

Contract (mirrors game/animal_paper_plane.py so a winner lifts straight into a
standalone game module):

  * `build_stunt_fold_vN(wing_angle_deg) -> pygame.Surface`  draws ONE flat
    frame on a 64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * the craft's mass is centred at the BODY anchor (32, 44) — collision is a
    fixed 14px circle there, so the jet keeps its centre of mass on that point
    no matter how far the nose reaches.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * a `LABELS` dict maps a display label → getter for the render sheet.

North star: "a skin lives or dies at 40px in motion." Each jet leans on ONE
bold delta silhouette + a hard-value FOLD (a bright upper facet vs a distinctly
darker under-fold meeting at a crisp keel crease), with a baked 1px self-rim so
the silhouette holds on day AND night skies. The four base wing poses become a
snappy BANK/FLUTTER + nose-bob — clamped so a stunt roll never flattens the jet
to a sliver.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
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


def _rim(surf, rim_col):
    """Bake a 1px self-rim from the painted alpha mask, stamped UNDER the art so
    it shows only as a clean lip — the silhouette guarantee on any sky, no glow
    halo."""
    mask = pygame.mask.from_surface(surf, threshold=8)
    rim = mask.to_surface(setcolor=rim_col, unsetcolor=(0, 0, 0, 0))
    out = _new()
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        out.blit(rim, (dx, dy))
    out.blit(surf, (0, 0))
    return out


# A stunt jet may bank a touch harder than the glider dart, but the roll is
# clamped so the delta never collapses edge-on to a sliver at gameplay scale.
_ROLL_MAX = 7.0


# ═════════════════════════════════════════════════════════════════════════════
# Shared fighter-fold geometry.
#
# Every take draws the SAME aggressive delta hull so the concept reads as one
# family; the livery + sweep + nose are what differ. The hull is a swept delta:
# a tight pointed nose reaching well past the mass centre, a single straight
# swept top edge nose→far_tip, and a darker under-fold below the keel so the
# central crease is a HARD value break.
#
#   nose ........... pointed tip, far forward (right)
#   far_tip ........ swept-back upper wing trailing point
#   near_tip ....... swept-back lower wing trailing point
#   tail ........... keel root at the back
# ═════════════════════════════════════════════════════════════════════════════
def _hull_pts(sweep, nose_reach):
    """Return (nose, far_tip, near_tip, tail) for a given wing `sweep` (how far
    the trailing points pull back) and `nose_reach` (how aggressive the point).
    Higher sweep = a leaner, more swept-wing fighter."""
    nose = (BCX + nose_reach, BCY - 1)
    far_tip = (BCX - 13 - sweep, BCY - 12)
    near_tip = (BCX - 11 - sweep, BCY + 13)
    tail = (BCX - 15, BCY)
    return nose, far_tip, near_tip, tail


def _draw_hull(surf, pal, roll, bob, sweep, nose_reach):
    """Paint the two-facet delta hull (lit top + shadowed under-fold + hard keel
    crease + leading-edge nose highlight). Returns the banked anchor points so
    livery can be laid on top in hull space."""
    nose, far_tip, near_tip, tail = _hull_pts(sweep, nose_reach)

    # UNDER-fold (lower facet, in shadow) — drawn first.
    near = _bank([nose, near_tip, tail], BCX, BCY, roll, bob)
    _poly(surf, pal["under"], near)
    _poly(surf, pal["under_d"],
          _bank([nose, near_tip, (BCX - 4, BCY + 5)], BCX, BCY, roll, bob))

    # TOP facet (lit upper wing).
    far = _bank([nose, far_tip, tail], BCX, BCY, roll, bob)
    _poly(surf, pal["top"], far)
    # Leading-edge highlight where the top folds meet at the nose point.
    _poly(surf, pal["top_h"],
          _bank([nose, (BCX + 7, BCY - 6), (BCX + 10, BCY - 1)],
                BCX, BCY, roll, bob))

    return nose, far_tip, near_tip, tail


def _keel_crease(surf, crease_col, nose, tail, roll, bob, width=3):
    a, b = _bank([nose, tail], BCX, BCY, roll, bob)
    pygame.draw.line(surf, crease_col, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), width)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · RED RACING STRIPE on WHITE — a clean Grand-Prix paper jet. A bold red
#      keel stripe runs the full length of the lit top facet, so the livery IS
#      the value structure: white wing / red spine / shadowed under-fold.
#      Moderate sweep, sharp nose. The crowd-pleaser.
# ═════════════════════════════════════════════════════════════════════════════
_V1 = {
    "top":     (242, 244, 248),     # bright white paper
    "top_h":   (255, 255, 255),     # nose highlight
    "under":   (150, 158, 172),     # shadowed under-fold (hard value drop)
    "under_d": (112, 120, 136),
    "crease":  (78, 86, 100),
    "rim":     (60, 66, 80),
    "stripe":  (214, 44, 48),       # racing red
    "stripe_d": (158, 26, 32),
}


def build_stunt_fold_v1(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 6.5))
    bob = -f * 1.4
    nose, far_tip, near_tip, tail = _draw_hull(surf, _V1, roll, bob,
                                               sweep=2, nose_reach=25)

    # Red racing stripe: a tapered wedge from the nose down the keel, riding the
    # lit top facet just ABOVE the crease so the hard fold below stays unbroken.
    stripe = _bank([(BCX + 22, BCY - 2), (BCX - 13, BCY - 9),
                    (BCX - 14, BCY - 4), (BCX + 22, BCY)],
                   BCX, BCY, roll, bob)
    _poly(surf, _V1["stripe"], stripe)
    _poly(surf, _V1["stripe_d"],
          _bank([(BCX - 4, BCY - 6), (BCX - 14, BCY - 9),
                 (BCX - 14, BCY - 4), (BCX - 4, BCY - 3)],
                BCX, BCY, roll, bob))

    _keel_crease(surf, _V1["crease"], nose, tail, roll, bob)
    return _rim(surf, _V1["rim"])


# ═════════════════════════════════════════════════════════════════════════════
# V2 · NAVY + LIGHTNING BOLT — a deep-navy hull with a bright sky-cyan lightning
#      bolt slashing forward along the wing. High sweep (leanest fighter), very
#      aggressive nose. The bolt is a single jagged high-value shape: it reads
#      as energy at 40px, not fussy detail.
# ═════════════════════════════════════════════════════════════════════════════
_V2 = {
    "top":     (46, 64, 116),       # navy lit facet
    "top_h":   (96, 120, 184),      # nose sheen
    "under":   (24, 34, 70),        # deep shadowed under-fold
    "under_d": (16, 24, 52),
    "crease":  (12, 18, 40),
    "rim":     (140, 168, 220),     # PALE rim so the dark jet holds on night sky
    "bolt":    (120, 224, 255),     # electric cyan
    "bolt_h":  (224, 250, 255),
}


def build_stunt_fold_v2(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 7.0))
    bob = -f * 1.5
    nose, far_tip, near_tip, tail = _draw_hull(surf, _V2, roll, bob,
                                               sweep=4, nose_reach=27)

    # Lightning bolt: one bold jagged stroke from mid-keel forward to the nose,
    # a single connected high-value shape so it survives the downscale as a
    # streak of energy. Drawn on the lit top facet.
    bolt = _bank([(BCX + 20, BCY - 2), (BCX + 4, BCY - 7),
                  (BCX + 9, BCY - 4), (BCX - 8, BCY - 8),
                  (BCX - 3, BCY - 5), (BCX - 12, BCY - 7),
                  (BCX - 6, BCY - 3), (BCX + 6, BCY - 1),
                  (BCX + 2, BCY - 3), (BCX + 18, BCY + 1)],
                 BCX, BCY, roll, bob)
    _poly(surf, _V2["bolt"], bolt)
    # Hot core highlight along the spine of the bolt.
    core = _bank([(BCX + 19, BCY - 2), (BCX + 5, BCY - 6),
                  (BCX - 9, BCY - 7), (BCX - 5, BCY - 4)],
                 BCX, BCY, roll, bob)
    pygame.draw.lines(surf, _V2["bolt_h"], False,
                      [(int(x), int(y)) for x, y in core], 1)

    _keel_crease(surf, _V2["crease"], nose, tail, roll, bob)
    return _rim(surf, _V2["rim"])


# ═════════════════════════════════════════════════════════════════════════════
# V3 · BLACK + ORANGE CHEVRON — a matte-black stealth hull with a single bold
#      orange chevron (forward-pointing >) banded across the wing. The chevron
#      is a fat two-tone band, not a thin line, so its value contrast reads at
#      40px. Moderate-high sweep, sharp nose, a small CANARD foreplane.
# ═════════════════════════════════════════════════════════════════════════════
_V3 = {
    "top":     (52, 54, 62),        # matte charcoal lit facet
    "top_h":   (96, 98, 110),
    "under":   (28, 28, 34),        # near-black under-fold
    "under_d": (18, 18, 22),
    "crease":  (10, 10, 14),
    "rim":     (150, 152, 162),     # pale rim — the black hull needs the lip
    "chev":    (255, 138, 30),      # hot orange
    "chev_d":  (196, 92, 14),
}


def build_stunt_fold_v3(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 6.5))
    bob = -f * 1.4
    nose, far_tip, near_tip, tail = _draw_hull(surf, _V3, roll, bob,
                                               sweep=3, nose_reach=26)

    # Small canard foreplane: a tiny swept fin up near the nose breaks the hull
    # outline and screams "stunt jet". A bold shape, not a sliver.
    canard = _bank([(BCX + 12, BCY - 5), (BCX + 20, BCY - 11),
                    (BCX + 16, BCY - 4)], BCX, BCY, roll, bob)
    _poly(surf, _V3["top_h"], canard)
    _poly(surf, _V3["crease"], canard, 1)

    # Orange chevron: a fat forward-pointing band across the wing. Two stacked
    # strokes (bright + shadowed flank) so the > shape carries value contrast.
    chev = _bank([(BCX + 8, BCY - 6), (BCX + 14, BCY - 1),
                  (BCX + 8, BCY + 4), (BCX + 4, BCY + 4),
                  (BCX + 10, BCY - 1), (BCX + 4, BCY - 6)],
                 BCX, BCY, roll, bob)
    _poly(surf, _V3["chev"], chev)
    chev2 = _bank([(BCX - 2, BCY - 6), (BCX + 4, BCY - 1),
                   (BCX - 2, BCY + 4), (BCX - 6, BCY + 4),
                   (BCX, BCY - 1), (BCX - 6, BCY - 6)],
                  BCX, BCY, roll, bob)
    _poly(surf, _V3["chev_d"], chev2)

    _keel_crease(surf, _V3["crease"], nose, tail, roll, bob)
    return _rim(surf, _V3["rim"])


# ═════════════════════════════════════════════════════════════════════════════
# V4 · BLUEPRINT CYAN on WHITE — a drafting-blueprint paper jet: clean white
#      facets with a bold cyan fold-line scheme and a CYAN ROUNDEL badge on the
#      wing (the livery is a badge, not a keel stripe). Low-moderate sweep with
#      the widest, most readable delta. The technical / collectible look.
# ═════════════════════════════════════════════════════════════════════════════
_V4 = {
    "top":     (236, 244, 250),     # drafting white
    "top_h":   (255, 255, 255),
    "under":   (150, 178, 200),     # cool shadowed under-fold
    "under_d": (112, 146, 174),
    "crease":  (40, 120, 168),      # cyan keel crease (blueprint ink)
    "rim":     (38, 110, 158),
    "ink":     (40, 130, 180),      # blueprint cyan
    "ink_d":   (24, 92, 134),
    "badge":   (40, 130, 180),
}


def build_stunt_fold_v4(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 6.0))
    bob = -f * 1.3
    nose, far_tip, near_tip, tail = _draw_hull(surf, _V4, roll, bob,
                                               sweep=1, nose_reach=24)

    # Blueprint ink edge: a bold cyan line tracing the swept LEADING edge
    # nose→far_tip, so the technical-drawing read is a structural value line.
    lead = _bank([nose, far_tip], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V4["ink"], (int(lead[0][0]), int(lead[0][1])),
                     (int(lead[1][0]), int(lead[1][1])), 2)

    # Cyan roundel badge on the lit wing (livery as a BADGE, not a stripe).
    # Ring first, hollow centre, so it reads as a contained roundel at 40px.
    bx, by = _bank([(BCX - 2, BCY - 6)], BCX, BCY, roll, bob)[0]
    _aaellipse(surf, _V4["badge"], (int(bx), int(by)), 5, 5)
    _aaellipse(surf, _V4["top"], (int(bx), int(by)), 3, 3)
    _aaellipse(surf, _V4["ink_d"], (int(bx), int(by)), 2, 2)

    _keel_crease(surf, _V4["crease"], nose, tail, roll, bob)
    return _rim(surf, _V4["rim"])


# ═════════════════════════════════════════════════════════════════════════════
# V5 · RETRO RED/CREAM "53" RACER — a vintage air-race look: warm cream hull,
#      a wide red nose cone + tail band, and a bold race-NUMBER roundel ("5") on
#      the wing. The number is a chunky high-contrast glyph (a real legibility
#      gamble at 40px, so it's drawn FAT). Moderate sweep, classic blunt-sharp
#      nose. The most characterful / nostalgic take.
# ═════════════════════════════════════════════════════════════════════════════
_V5 = {
    "top":     (244, 232, 204),     # warm cream
    "top_h":   (255, 248, 228),
    "under":   (176, 158, 122),     # tan shadowed under-fold
    "under_d": (140, 122, 88),
    "crease":  (96, 80, 54),
    "rim":     (84, 68, 44),
    "red":     (208, 56, 48),       # race red
    "red_d":   (158, 34, 30),
    "disc":    (250, 240, 216),     # roundel field
    "num":     (208, 56, 48),       # race number
}


def build_stunt_fold_v5(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = max(-_ROLL_MAX, min(_ROLL_MAX, f * 6.0))
    bob = -f * 1.3
    nose, far_tip, near_tip, tail = _draw_hull(surf, _V5, roll, bob,
                                               sweep=2, nose_reach=25)

    # Red NOSE CONE — a bold colour block on the forward keel (classic racer).
    cone = _bank([(BCX + 25, BCY - 1), (BCX + 11, BCY - 7),
                  (BCX + 12, BCY + 6)], BCX, BCY, roll, bob)
    _poly(surf, _V5["red"], cone)
    _poly(surf, _V5["red_d"],
          _bank([(BCX + 25, BCY - 1), (BCX + 12, BCY + 6),
                 (BCX + 13, BCY + 1)], BCX, BCY, roll, bob))

    # Red TAIL band at the keel root, balancing the nose cone.
    tail_band = _bank([(BCX - 9, BCY - 9), (BCX - 15, BCY),
                       (BCX - 9, BCY + 9), (BCX - 6, BCY + 5),
                       (BCX - 11, BCY), (BCX - 6, BCY - 5)],
                      BCX, BCY, roll, bob)
    _poly(surf, _V5["red"], tail_band)

    # Race-number roundel on the lit wing: a cream disc with a FAT red "5".
    bx, by = _bank([(BCX + 2, BCY - 6)], BCX, BCY, roll, bob)[0]
    _aaellipse(surf, _V5["red_d"], (int(bx), int(by)), 6, 6)
    _aaellipse(surf, _V5["disc"], (int(bx), int(by)), 5, 5)
    # A chunky blocky "5" drawn as bold strokes so the glyph holds value mass.
    ix, iy = int(bx), int(by)
    pygame.draw.line(surf, _V5["num"], (ix - 2, iy - 3), (ix + 2, iy - 3), 2)
    pygame.draw.line(surf, _V5["num"], (ix - 2, iy - 3), (ix - 2, iy), 2)
    pygame.draw.line(surf, _V5["num"], (ix - 2, iy), (ix + 2, iy), 2)
    pygame.draw.line(surf, _V5["num"], (ix + 2, iy), (ix + 2, iy + 3), 2)
    pygame.draw.line(surf, _V5["num"], (ix - 2, iy + 3), (ix + 2, iy + 3), 2)

    _keel_crease(surf, _V5["crease"], nose, tail, roll, bob)
    return _rim(surf, _V5["rim"])


# ─────────────────────────────────────────────────────────────────────────────
# Getters + label→getter dict for the render sheet.
# A winner lifts into game/animal_paper_plane.py as `skin_stunt_fold`.
# ─────────────────────────────────────────────────────────────────────────────
get_stunt_fold_v1 = _make_prebuilt_skin(build_stunt_fold_v1)
get_stunt_fold_v2 = _make_prebuilt_skin(build_stunt_fold_v2)
get_stunt_fold_v3 = _make_prebuilt_skin(build_stunt_fold_v3)
get_stunt_fold_v4 = _make_prebuilt_skin(build_stunt_fold_v4)
get_stunt_fold_v5 = _make_prebuilt_skin(build_stunt_fold_v5)


LABELS = {
    "V1 · RED RACING STRIPE": ("get_stunt_fold_v1", get_stunt_fold_v1,
                               "white wing / red keel stripe · sharp delta"),
    "V2 · NAVY + LIGHTNING":  ("get_stunt_fold_v2", get_stunt_fold_v2,
                               "navy hull / cyan bolt · leanest sweep"),
    "V3 · BLACK + CHEVRON":   ("get_stunt_fold_v3", get_stunt_fold_v3,
                               "stealth black / orange chevron + canard"),
    "V4 · BLUEPRINT ROUNDEL": ("get_stunt_fold_v4", get_stunt_fold_v4,
                               "white / cyan ink + roundel badge · wide delta"),
    "V5 · RETRO '5' RACER":   ("get_stunt_fold_v5", get_stunt_fold_v5,
                               "cream / red nose cone + race number"),
}


# Mirror of the production registry shape (single winner lifts later).
BUILDERS = {
    "skin_stunt_fold_v1": get_stunt_fold_v1,
    "skin_stunt_fold_v2": get_stunt_fold_v2,
    "skin_stunt_fold_v3": get_stunt_fold_v3,
    "skin_stunt_fold_v4": get_stunt_fold_v4,
    "skin_stunt_fold_v5": get_stunt_fold_v5,
}
