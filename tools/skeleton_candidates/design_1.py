"""SKELETON redesign candidate — design_1: BONEWHITE.

Scratch exploration only (never registered in store_skins.BUILDERS). The fix
for the muted ivory-on-navy original is a value split, not a recolour: crank
the bone to pure WHITE, drop the flesh to near-black, and wrap a dark keyline
so the white survives even the brightest day sky. The skeleton read is the
whole costume — skull + socketed eyes, a bold paired rib ladder, a vertebra
spine, a finger-bone wing that clatters across the 4 flap poses, and bone legs.

Built like the live _build_skeleton_redraw: a full body redraw per wing angle,
wrapped by store_skins._make_prebuilt_skin so it picks up the _WING_ANGLES
flap poses, the outline pass, and the rotation cache for free.

Round 2 — at 40px the two sockets must stay distinct holes (≥2px white bridge
+ ≥2px white cranium above), the wing must read as radiating WHITE finger-bones
(no solid dark cape field), a #3A3D47 keyline must rim the white so it never
sits on bright sky, a vertebra spine carries the centerline, and the grin is a
committed white tooth bar — not a smudge.
"""
import math
import pygame

from game.store_skins import SPRITE_W, SPRITE_H, _make_prebuilt_skin, _poly
from game.parrot import _aaellipse


# Pure white is the brightest element; the body is near-black so the value
# split alone carries the read. The keyline sits between bone and sky.
_BONE    = (255, 255, 255)
_BONE_SH = (230, 233, 240)         # cool under-edge (#E6E9F0) for roundness
_BODY    = (21, 22, 28)            # near-black "flesh" + socket interiors (#15161C)
_BODY_D  = (12, 13, 18)
_KEY     = (58, 61, 71)            # keyline rim (#3A3D47) so white reads on day sky


def _key_dot(surf, p, r):
    """Stamp a 1px keyline rim just outside a white bone tip so it never sits
    directly on bright sky — the outline pass adds a near-black edge, this adds
    the cooler #3A3D47 the critique calls for."""
    pygame.draw.circle(surf, _KEY, p, r + 1, 1)


def _finger_wing(angle_deg):
    """Wing as THREE radiating finger-bones (leading/mid/trailing phalanges)
    fanning from a bone wrist. Round 2 fanned five bones that crowded to sub-2px
    gaps and mushed at 40px; three well-separated 2px-white bones with a 4px
    keyline read as discrete bones across all 4 flap poses. The fan is ~30%
    wider so the gaps stay open, and the tips reach far enough that — once the
    body ellipse is shrunk — the white fingers OVERHANG the dark silhouette into
    the sky/keyline and visibly clatter, the way the base macaw wing breaks the
    body outline. Each phalange is keyline-rimmed so it holds on the day sky."""
    w = pygame.Surface((56, 56), pygame.SRCALPHA)
    wrist = (22, 30)

    # Three splayed tips fanned ~30% wider than the old five — a long leading
    # finger up-and-out, a mid finger, and a shorter trailing one. The wide
    # angular spread keeps a clear dark gap between each white bone.
    tips = [(54, 12), (52, 30), (38, 48)]
    for tip in tips:
        # Keyline underlay (drawn fatter first) so a #3A3D47 rim hugs each bone.
        pygame.draw.line(w, _KEY, wrist, tip, 4)
        _key_dot(w, tip, 2)
    pygame.draw.circle(w, _KEY, wrist, 4)              # wrist keyline

    for i, tip in enumerate(tips):
        col = _BONE if i < 2 else _BONE_SH
        pygame.draw.line(w, col, wrist, tip, 2)        # the bone itself
        pygame.draw.circle(w, _BONE, tip, 2)           # knuckle cap
        # A mid-bone joint pip for the segmented phalange look.
        mid = ((wrist[0] + tip[0]) // 2, (wrist[1] + tip[1]) // 2)
        pygame.draw.circle(w, _BONE_SH, mid, 1)
    pygame.draw.circle(w, _BONE, wrist, 3)             # wrist knob
    pygame.draw.circle(w, _BODY_D, wrist, 1)
    return pygame.transform.rotate(w, angle_deg)


def _vertebra(surf, p0, p1, beads):
    """A short bead column from p0 to p1 — the spine tell. Keyline-rimmed so
    the centerline reads even where it crosses the dark body."""
    for i in range(beads):
        t = i / (beads - 1)
        x = int(p0[0] + (p1[0] - p0[0]) * t)
        y = int(p0[1] + (p1[1] - p0[1]) * t)
        pygame.draw.circle(surf, _KEY, (x, y), 2, 1)
        pygame.draw.circle(surf, _BONE, (x, y), 2)
        pygame.draw.circle(surf, _BONE_SH, (x, y), 2, 1)


def _build_design1(wing_angle_deg):
    surf = pygame.Surface((SPRITE_W, SPRITE_H), pygame.SRCALPHA)

    # Tail + body + head as near-black masses (the value floor the bone sits on).
    # Round 2 left a solid near-black field exactly where the wing fingers fan,
    # so the wing read as a dark blob with white speckle. The body ellipse is
    # shrunk ~15% (r18×13 → r15×11) and the tail pulled in, so the WHITE wing
    # phalanges now overhang PAST this dark silhouette into the sky/keyline and
    # visibly clatter instead of disappearing into the back-mass.
    tail = [(4, 28), (16, 26), (21, 35), (12, 40)]
    _poly(surf, _BODY, tail)
    pygame.draw.polygon(surf, _BODY_D, tail, 1)
    # ONE clean white tail-feather bone — round 2 had two competing white
    # clusters aft of the skull fighting the ribcage read; one keyed bone keeps
    # the tail a single quiet tell.
    pygame.draw.line(surf, _KEY,  (19, 30), (5, 33), 3)        # feather-bone keyline
    pygame.draw.line(surf, _BONE, (19, 30), (5, 33), 1)        # white tail-feather bone
    _aaellipse(surf, _BODY_D, (33, 33), 16, 12)
    _aaellipse(surf, _BODY, (32, 32), 15, 11)
    _aaellipse(surf, _BODY_D, (48, 21), 13, 12)
    _aaellipse(surf, _BODY, (47, 20), 12, 11)

    # Spine — vertebra beads from the skull base down toward the ribcage.
    _vertebra(surf, (42, 26), (24, 38), 6)

    # Ribcage — THREE paired white rib-arcs off a central sternum, keyline-rimmed
    # underneath so they survive on bright sky. Round 2 packed four rungs at ~4px
    # so they mushed into the wing; three rungs at ~5px vertical spacing read as
    # distinct rungs, and they sit forward/below the wing wrist (chest) so wing
    # and ribcage never share pixels.
    pygame.draw.line(surf, _KEY,  (37, 27), (26, 42), 4)        # sternum keyline
    pygame.draw.line(surf, _BONE, (37, 28), (26, 41), 2)        # sternum
    for i, ty in enumerate((30, 35, 40)):
        sx = 36 - i * 3
        # Each rung is a pair of arcs sweeping out either side of the sternum.
        pygame.draw.arc(surf, _BONE, (sx - 12, ty - 5, 13, 12),
                        math.radians(20), math.radians(150), 2)
        pygame.draw.arc(surf, _BONE_SH, (sx - 1, ty - 5, 13, 12),
                        math.radians(30), math.radians(160), 2)

    # Wing — three radiating finger-bones, seated UP-AND-BACK off the chest so
    # the fan clears the ribcage and overhangs the shrunk body into the sky.
    wing = _finger_wing(wing_angle_deg)
    surf.blit(wing, wing.get_rect(center=(30, 24)).topleft)
    # A 1px dark gap between the wing wrist and the ribcage so the eye parses
    # skull → ribs → wing as three separate tells, not one merged cluster.
    pygame.draw.line(surf, _BODY_D, (31, 32), (28, 38), 1)

    # Leg bones — thin paired bones with knob knees + 3-claw bone feet, each
    # keyline-rimmed so the tips read against the ground.
    for hx, fx in ((28, 27), (34, 35)):
        knee = (hx, 45)
        foot = (fx, 49)
        pygame.draw.line(surf, _KEY,  (hx, 40), knee, 4)        # thigh keyline
        pygame.draw.line(surf, _KEY,  knee, foot, 4)            # shin keyline
        pygame.draw.line(surf, _BONE, (hx, 41), knee, 2)        # thigh
        pygame.draw.circle(surf, _BONE, knee, 2)                # knob knee
        pygame.draw.line(surf, _BONE, knee, foot, 2)            # shin
        for dx in (-2, 0, 2):
            pygame.draw.line(surf, _BONE_SH, foot, (foot[0] + dx, foot[1] + 3), 2)

    # ── Skull — bright white cranium tall enough to seat two DISTINCT sockets
    # with a solid white nasal bridge between and a white crown above them.
    # Keyline first (a hair larger) so the white dome never touches the sky.
    _aaellipse(surf, _KEY,     (47, 19), 11, 10)
    _aaellipse(surf, _BONE,    (47, 19), 10, 9)                 # cranium
    _aaellipse(surf, _BONE_SH, (47, 23), 9, 5)                 # under-edge shade
    _aaellipse(surf, _BONE,    (47, 22), 8, 5)                 # jaw/muzzle front

    # Two big hollow eye sockets — distinct ~4px PURE near-black teardrop holes
    # with a ≥2px white nasal bridge between (x 44↔51 leaves white at x 47-48)
    # and ≥2px white cranium above (sockets sit at y 20, crown top at y ~10).
    for ex in (43, 51):
        # Teardrop: a round top tapering to a point toward the nose centre.
        nose_dir = 1 if ex < 47 else -1
        pts = [(ex - 2, 19), (ex + 2, 19), (ex + 2, 21),
               (ex + nose_dir * 1, 24), (ex - 2, 21)]
        _poly(surf, _BODY_D, pts)
        pygame.draw.circle(surf, _BODY_D, (ex, 20), 2)
        pygame.draw.circle(surf, _KEY,    (ex, 20), 2, 1)      # faint socket rim
    pygame.draw.circle(surf, (255, 255, 255), (52, 18), 1)     # life glint

    # Small triangular nose hollow, centred on the bridge below the sockets.
    _poly(surf, _BODY_D, [(46, 25), (48, 25), (47, 28)])

    # Tooth grin — a committed 2px WHITE tooth bar with two dark notches.
    pygame.draw.line(surf, _BONE, (43, 28), (51, 28), 2)       # tooth bar
    for nx in (46, 49):
        pygame.draw.line(surf, _BODY_D, (nx, 27), (nx, 30), 1) # notch gaps

    # Beak — near-black beak with a crisp white bone outline.
    beak_pts = [(55, 22), (61, 25), (58, 29), (52, 27)]
    _poly(surf, _BODY, beak_pts)
    pygame.draw.polygon(surf, _KEY, beak_pts, 2)
    pygame.draw.polygon(surf, _BONE, beak_pts, 1)

    return surf


build = _make_prebuilt_skin(_build_design1)
