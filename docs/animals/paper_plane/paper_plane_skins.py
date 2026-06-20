"""Candidate PAPER PLANE skins for the coin Store — round-1 exploration.

A secret ultra-premium NON-creature flyer: the player's flapping bird becomes
a folded paper dart. There are no wings — the 4 base wing poses are reinterpreted
as a gentle BANK/FLUTTER: the dart rolls a few degrees and the nose bobs as it
catches air, the way a real paper plane sways in flight.

Contract (mirrors game/animal_skins.py so the winner lifts straight into a
standalone game/animal_paper_plane.py):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws one flat frame on a
    64×84 SRCALPHA canvas (COMPOSITE_W=64, COMPOSITE_H=84).
  * the craft's mass is centred at the BODY anchor (32, 44) — collision is a
    fixed 14px circle there, so every dart keeps its centre of mass on that
    point regardless of how far the nose reaches.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_paper_plane": get_paper_plane_vN, ...}` at the bottom.

North star: "a skin lives or dies at 40px in motion." Every dart leans on ONE
bold triangular silhouette + ONE high-contrast signature — the central fold
crease splitting a bright top facet from a shadowed under-fold — so the folded
paper reads on day AND night skies.
"""
import math
import pygame

from game import parrot
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
# V1 · NOTEBOOK DART (side view) — the cleanest classic: a long pointed dart in
#      plain notebook white, split by a single dark central crease into a bright
#      upper facet and a cool-grey under-fold. The keel fin stands up at the
#      fold. Signature 40px tell: the sharp triangle + the crease line.
# ═════════════════════════════════════════════════════════════════════════════
_V1_TOP    = (250, 250, 246)        # lit upper paper
_V1_TOP_H  = (255, 255, 255)        # nose highlight
_V1_UNDER  = (196, 202, 214)        # shadowed under-fold (cool grey)
_V1_UNDER_D = (168, 176, 192)
_V1_CREASE = (120, 128, 146)        # central fold line
_V1_FIN    = (228, 232, 240)


def build_paper_plane_v1(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = f * 7.0                   # gentle bank
    bob = -f * 1.5                   # nose lifts as it catches air

    nose = (BCX + 24, BCY)
    tail_top = (BCX - 16, BCY - 11)
    tail_mid = (BCX - 12, BCY)
    tail_bot = (BCX - 16, BCY + 11)

    # Under-fold (the swept lower wing) — drawn first, sits in shadow.
    under = _bank([nose, tail_mid, tail_bot], BCX, BCY, roll, bob)
    _poly(surf, _V1_UNDER, under)
    _poly(surf, _V1_UNDER_D, _bank([nose, tail_bot, (BCX - 6, BCY + 6)],
                                   BCX, BCY, roll, bob))

    # Top facet (the lit upper wing).
    top = _bank([nose, tail_top, tail_mid], BCX, BCY, roll, bob)
    _poly(surf, _V1_TOP, top)
    # Nose highlight where the two top folds meet at the point.
    _poly(surf, _V1_TOP_H, _bank([nose, (BCX + 6, BCY - 5), (BCX + 8, BCY)],
                                 BCX, BCY, roll, bob))

    # The vertical keel fin standing up along the central fold (the silhouette
    # break that says 'folded', not a flat triangle).
    fin = _bank([(BCX - 12, BCY), (BCX - 14, BCY - 9), (BCX - 2, BCY)],
                BCX, BCY, roll, bob)
    _poly(surf, _V1_FIN, fin)
    _poly(surf, _V1_CREASE, fin, 1)

    # The HERO central crease: nose → tail, the spine of the fold.
    crease = _bank([nose, tail_mid], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V1_CREASE,
                     (int(crease[0][0]), int(crease[0][1])),
                     (int(crease[1][0]), int(crease[1][1])), 2)
    return surf


get_paper_plane_v1 = _make_prebuilt_skin(build_paper_plane_v1)


# ═════════════════════════════════════════════════════════════════════════════
# V2 · LINED-PAPER DART (3/4 view) — a slightly top-down three-quarter dart so
#      BOTH swept wings show. Plain white with the iconic faint BLUE rule lines
#      + a single red margin stripe running down the centre fold. Signature
#      40px tell: two bright wing-vees + the red centre stripe.
# ═════════════════════════════════════════════════════════════════════════════
_V2_WING   = (249, 250, 247)        # lit wing paper
_V2_WING_D = (210, 216, 226)        # shadowed near wing
_V2_WING_DD = (184, 190, 204)
_V2_RULE   = (150, 178, 222, 150)   # faint blue notebook rule
_V2_MARGIN = (224, 96, 96)          # red margin / centre stripe
_V2_CREASE = (130, 138, 156)


def build_paper_plane_v2(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = f * 6.0
    bob = -f * 1.2
    spread = 1.0 + f * 0.06          # wings flex a hair as it catches air

    nose = (BCX + 23, BCY - 1)
    centre_back = (BCX - 15, BCY + 1)
    # Two swept wings fanning out from the central fold (3/4 view).
    far_tip = (BCX - 13, BCY - int(13 * spread))
    near_tip = (BCX - 11, BCY + int(15 * spread))

    # Far wing (top, fully lit).
    far = _bank([nose, far_tip, centre_back], BCX, BCY, roll, bob)
    _poly(surf, _V2_WING, far)
    # Near wing (lower, angled toward viewer → shadowed).
    near = _bank([nose, near_tip, centre_back], BCX, BCY, roll, bob)
    _poly(surf, _V2_WING_D, near)
    _poly(surf, _V2_WING_DD, _bank([nose, near_tip, (BCX - 4, BCY + 6)],
                                   BCX, BCY, roll, bob))

    # Faint blue notebook rules across the lit far wing — the paper-type tell.
    rule = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for ry in (-9, -5, -1):
        a, b = _bank([(BCX + 14, BCY + ry), (BCX - 11, BCY + ry - 2)],
                     BCX, BCY, roll, bob)
        pygame.draw.line(rule, _V2_RULE, (int(a[0]), int(a[1])),
                         (int(b[0]), int(b[1])), 1)
    # Clip the rules to the far-wing triangle so they don't bleed off the paper.
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _poly(mask, (255, 255, 255, 255), far)
    rule.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(rule, (0, 0))

    # HERO: the red margin stripe running the central fold + the crease.
    a, b = _bank([nose, centre_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V2_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    pygame.draw.line(surf, _V2_MARGIN, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 1)
    return surf


get_paper_plane_v2 = _make_prebuilt_skin(build_paper_plane_v2)


# ═════════════════════════════════════════════════════════════════════════════
# V3 · NEWSPAPER DART (side view) — folded from newsprint: warm off-white grey
#      paper with a faint column of grey "text" speckle + a single bold black
#      headline bar. Crisp facet shading. Signature 40px tell: the dark
#      headline bar slashing across the bright fold.
# ═════════════════════════════════════════════════════════════════════════════
_V3_TOP    = (228, 226, 216)        # newsprint off-white
_V3_TOP_H  = (244, 243, 236)
_V3_UNDER  = (176, 176, 170)        # shadowed under-fold
_V3_UNDER_D = (150, 150, 146)
_V3_CREASE = (96, 96, 94)
_V3_TEXT   = (120, 120, 116)        # grey column text
_V3_HEAD   = (40, 40, 42)           # bold headline bar


def build_paper_plane_v3(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = f * 7.0
    bob = -f * 1.4

    nose = (BCX + 24, BCY)
    tail_top = (BCX - 16, BCY - 12)
    tail_mid = (BCX - 12, BCY)
    tail_bot = (BCX - 16, BCY + 11)

    under = _bank([nose, tail_mid, tail_bot], BCX, BCY, roll, bob)
    _poly(surf, _V3_UNDER, under)
    _poly(surf, _V3_UNDER_D, _bank([nose, tail_bot, (BCX - 5, BCY + 6)],
                                   BCX, BCY, roll, bob))

    top = _bank([nose, tail_top, tail_mid], BCX, BCY, roll, bob)
    _poly(surf, _V3_TOP, top)

    # Newsprint texture clipped to the lit top facet.
    tex = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    rng = (7, 11, 13, 17, 19, 23)    # deterministic speckle offsets
    for i, ox in enumerate(range(BCX - 10, BCX + 18, 3)):
        oy = BCY - 8 + (rng[i % len(rng)] % 5)
        for k in range(3):
            tex.fill(_V3_TEXT, (ox, oy + k * 3, 2, 1))
    # The bold headline bar — the 40px hero.
    a, b = _bank([(BCX - 8, BCY - 8), (BCX + 12, BCY - 6)], BCX, BCY, roll, bob)
    pygame.draw.line(tex, _V3_HEAD, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _poly(mask, (255, 255, 255, 255), top)
    tex.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(tex, (0, 0))

    _poly(surf, _V3_TOP_H, _bank([nose, (BCX + 7, BCY - 5), (BCX + 9, BCY)],
                                 BCX, BCY, roll, bob))

    # Keel fin.
    fin = _bank([(BCX - 12, BCY), (BCX - 14, BCY - 9), (BCX - 2, BCY)],
                BCX, BCY, roll, bob)
    _poly(surf, _V3_UNDER, fin)
    _poly(surf, _V3_CREASE, fin, 1)

    crease = _bank([nose, tail_mid], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V3_CREASE, (int(crease[0][0]), int(crease[0][1])),
                     (int(crease[1][0]), int(crease[1][1])), 2)
    return surf


get_paper_plane_v3 = _make_prebuilt_skin(build_paper_plane_v3)


# ═════════════════════════════════════════════════════════════════════════════
# V4 · DOLLAR-BILL DART (3/4 view) — the premium tell: folded from a banknote.
#      Money-green paper, an ornate oval "portrait" medallion at the centre
#      fold, gold corner numerals. Signature 40px tell: the green craft + the
#      pale portrait oval glowing at its heart. Ties into Skybit's $-economy.
# ═════════════════════════════════════════════════════════════════════════════
_V4_TOP    = (122, 168, 132)        # bill green (lit)
_V4_TOP_H  = (168, 206, 174)
_V4_UNDER  = (74, 116, 90)          # shadowed under-fold
_V4_UNDER_D = (54, 92, 70)
_V4_CREASE = (40, 70, 52)
_V4_OVAL   = (214, 232, 214)        # pale portrait medallion
_V4_OVAL_D = (150, 184, 158)
_V4_GOLD   = (236, 206, 120)        # corner numerals


def build_paper_plane_v4(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = f * 6.0
    bob = -f * 1.3

    nose = (BCX + 23, BCY - 1)
    centre_back = (BCX - 15, BCY + 1)
    far_tip = (BCX - 13, BCY - 13)
    near_tip = (BCX - 11, BCY + 14)

    far = _bank([nose, far_tip, centre_back], BCX, BCY, roll, bob)
    _poly(surf, _V4_TOP, far)
    near = _bank([nose, near_tip, centre_back], BCX, BCY, roll, bob)
    _poly(surf, _V4_UNDER, near)
    _poly(surf, _V4_UNDER_D, _bank([nose, near_tip, (BCX - 4, BCY + 5)],
                                   BCX, BCY, roll, bob))
    _poly(surf, _V4_TOP_H, _bank([nose, (BCX + 6, BCY - 6), (BCX + 8, BCY - 1)],
                                 BCX, BCY, roll, bob))

    # HERO: the pale portrait medallion on the lit far wing.
    ox, oy = _bank([(BCX + 2, BCY - 6)], BCX, BCY, roll, bob)[0]
    _aaellipse(surf, _V4_OVAL_D, (int(ox), int(oy)), 6, 7)
    _aaellipse(surf, _V4_OVAL, (int(ox), int(oy)), 5, 6)
    # Gold corner numeral pips (the "denomination").
    for cx, cy in (_bank([(BCX + 12, BCY - 11), (BCX - 9, BCY - 2)],
                         BCX, BCY, roll, bob)):
        pygame.draw.circle(surf, _V4_GOLD, (int(cx), int(cy)), 1)

    # Central crease + fold spine.
    a, b = _bank([nose, centre_back], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V4_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 2)
    return surf


get_paper_plane_v4 = _make_prebuilt_skin(build_paper_plane_v4)


# ═════════════════════════════════════════════════════════════════════════════
# V5 · KRAFT GLIDER (top-down view, slightly crumpled) — folded from rugged
#      brown kraft paper, seen more from ABOVE so the full arrowhead reads. A
#      hand-drawn doodle star on one wing, a couple of soft crumple creases for
#      a lived-in feel. Signature 40px tell: the warm-brown arrowhead + the
#      central V-fold valley running its length.
# ═════════════════════════════════════════════════════════════════════════════
_V5_LEFT   = (198, 158, 110)        # lit left wing
_V5_LEFT_H = (224, 190, 142)
_V5_RIGHT  = (158, 120, 78)         # shadowed right wing
_V5_RIGHT_D = (132, 98, 62)
_V5_VALLEY = (104, 76, 48)          # central V-fold valley (darkest)
_V5_CREASE = (120, 88, 56)
_V5_DOODLE = (84, 60, 38)


def build_paper_plane_v5(wing_angle_deg):
    surf = _new()
    f = _flutter(wing_angle_deg)
    roll = f * 8.0                   # top-down → bank reads as a wider yaw-sway
    bob = -f * 1.0

    nose = (BCX + 22, BCY)
    back_left = (BCX - 16, BCY - 15)
    back_right = (BCX - 16, BCY + 15)
    tail_notch = (BCX - 10, BCY)

    # Left (upper) wing — lit.
    left = _bank([nose, back_left, tail_notch], BCX, BCY, roll, bob)
    _poly(surf, _V5_LEFT, left)
    _poly(surf, _V5_LEFT_H, _bank([nose, (BCX + 2, BCY - 7), (BCX + 8, BCY - 1)],
                                  BCX, BCY, roll, bob))
    # Right (lower) wing — shadowed.
    right = _bank([nose, back_right, tail_notch], BCX, BCY, roll, bob)
    _poly(surf, _V5_RIGHT, right)
    _poly(surf, _V5_RIGHT_D, _bank([nose, back_right, (BCX - 4, BCY + 7)],
                                   BCX, BCY, roll, bob))

    # HERO: the central V-fold valley running nose→tail (the deep crease that
    # tells 'top-down folded arrow' the instant you see it).
    a, b = _bank([nose, tail_notch], BCX, BCY, roll, bob)
    pygame.draw.line(surf, _V5_VALLEY, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 3)
    pygame.draw.line(surf, _V5_CREASE, (int(a[0]), int(a[1])),
                     (int(b[0]), int(b[1])), 1)

    # Soft crumple creases (the lived-in 'slightly crumpled' read).
    for p0, p1 in (((BCX + 6, BCY - 6), (BCX - 8, BCY - 9)),
                   ((BCX - 2, BCY + 4), (BCX - 12, BCY + 9))):
        a, b = _bank([p0, p1], BCX, BCY, roll, bob)
        pygame.draw.line(surf, _V5_CREASE, (int(a[0]), int(a[1])),
                         (int(b[0]), int(b[1])), 1)

    # Hand-drawn doodle star on the lit left wing — the charm beat.
    sx, sy = _bank([(BCX - 6, BCY - 7)], BCX, BCY, roll, bob)[0]
    pts = []
    for k in range(5):
        ang = -math.pi / 2 + k * 2 * math.pi / 5
        pts.append((sx + math.cos(ang) * 3, sy + math.sin(ang) * 3))
    for k in range(5):
        a = pts[k]
        b = pts[(k + 2) % 5]
        pygame.draw.line(surf, _V5_DOODLE, (int(a[0]), int(a[1])),
                         (int(b[0]), int(b[1])), 1)
    return surf


get_paper_plane_v5 = _make_prebuilt_skin(build_paper_plane_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Candidate registry. The winner is renamed get_paper_plane and registered as
# "skin_paper_plane" in the production module.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "v1_notebook":   get_paper_plane_v1,
    "v2_lined":      get_paper_plane_v2,
    "v3_newspaper":  get_paper_plane_v3,
    "v4_dollar":     get_paper_plane_v4,
    "v5_kraft":      get_paper_plane_v5,
}

LABELS = {
    "v1_notebook":  ("V1 NOTEBOOK", "sharp triangle + dark central crease"),
    "v2_lined":     ("V2 LINED-PAPER", "two wing-vees + red centre stripe"),
    "v3_newspaper": ("V3 NEWSPRINT", "bold black headline bar on the fold"),
    "v4_dollar":    ("V4 DOLLAR-BILL", "green craft + pale portrait oval"),
    "v5_kraft":     ("V5 KRAFT (top-down)", "brown arrowhead + V-fold valley"),
}
