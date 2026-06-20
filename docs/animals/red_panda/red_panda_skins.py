"""Candidate RED PANDA Store skin — round-1 exploration (5 distinct takes).

A NEW from-scratch creature for the ANIMALS tab: a round russet fluffball with
a fat cream-and-rust RINGED TAIL curling up behind it and a white face-mask.
The skin is the player's flappy bird: it animates over the 4 base wing poses
(`parrot._WING_ANGLES`, 50→-40) and is rotated by dive/climb tilt by the shared
getter factory.

Contract mirrors game/animal_skins.py so the winner lifts straight in:

  * `build_red_panda_vN(wing_angle_deg) -> pygame.Surface`  one flat 64×84 frame.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)` — 4 flat frames + per-(frame, 3°) rotation
    cache, each run through `parrot._add_outline`.
  * `BUILDERS = {"v1 Cozy Curl": get_v1, ...}` label→getter dict at the bottom.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, so the body mass stays anchored at BCX/BCY (32,44) regardless of
how far the tail arcs — the fat tail is silhouette flourish, never collision
mass. The tall canvas gives ear/tail headroom while the body keeps the base
anchor so the in-game centre-blit rotation maths still holds.

North star: "a skin lives or dies at 40px in motion." Every take leans on the
ringed-tail arc + white face-mask as the two reads that must survive 40px.

There is NO red panda flight in nature, so the "flap" is reinterpreted as a
LEAP-AND-BALANCE: the big tail sweeps UP on the down-pose (counterweight for
lift) and the paws tuck on the up-pose.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (ear + tail-arc headroom) ──────────────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12                # body offset down into the tall canvas

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter — lazy 4-frame build +
    per-(frame, 3°) rotation cache, each frame house-outlined."""
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


def _eye(surf, cx, cy, r, *, iris=(58, 26, 12), white=(255, 250, 244),
         glint=True):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 1))
    if glint:
        pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                           max(1, r // 3))


def _flap(angle_deg):
    """0..1 'pose is up'. _WING_ANGLES runs 50→-40, so 0 = deep down-pose
    (tail swept high), 1 = up-pose (paws tucked)."""
    return (angle_deg + 40) / 90.0


def _rot_blit(surf, wing, anchor):
    surf.blit(wing, wing.get_rect(center=anchor).topleft)


# ── shared red-panda palette (varied per version below) ──────────────────────
FUR     = (193, 68, 14)         # #C1440E russet
FUR_D   = (150, 48, 8)
FUR_H   = (224, 110, 44)
RING    = (122, 42, 12)         # #7A2A0C dark tail ring
CREAM   = (255, 244, 230)       # #FFF4E6 mask + belly + tail bands
CREAM_D = (228, 210, 188)
EYEDK   = (58, 26, 12)          # #3A1A0C eyes + nose
LEGDK   = (74, 36, 16)          # near-black legs


def _paw_pair(surf, by, f, col=LEGDK):
    """Two little forepaws that TUCK up on the up-pose (f→1) and hang on the
    down-pose (f→0) — the 'leap-and-balance' read."""
    drop = int(6 - f * 5)
    for fx in (27, 37):
        pygame.draw.line(surf, col, (fx, by), (fx, by + drop), 3)
        pygame.draw.circle(surf, col, (fx, by + drop), 2)


# ═════════════════════════════════════════════════════════════════════════════
# v1 · COZY CURL — the classic cuddly fluffball. Round body, broad white face
#     mask, modest rounded ears, and a fat ringed tail curling UP and over
#     behind the back in a tight C. The cuddliest, most "storybook" read.
#     40px tell: the cream-and-rust ringed C-arc hugging the back + wide mask.
# ═════════════════════════════════════════════════════════════════════════════
def _ringed_tail_arc(surf, cx, cy, r, width, n_rings, span, start,
                     fur=FUR, ring=RING, cream=CREAM, tip_cream=True):
    """A fat ringed tail laid along a circular arc. `span`/`start` in radians.
    Draws alternating fur/ring/cream bands as thick chords plus a cream tip.
    The arc is the silhouette signature, so it is fat and high-contrast."""
    steps = max(n_rings * 2, 8)
    for i in range(steps + 1):
        t = i / steps
        a = start + span * t
        px = cx + math.cos(a) * r
        py = cy + math.sin(a) * r
        band = int(t * n_rings * 2) % 2
        col = ring if band else fur
        pygame.draw.circle(surf, col, (int(px), int(py)), width)
    # Cream highlight bands threaded along the lit (upper) edge.
    for i in range(n_rings):
        t = (i + 0.5) / n_rings
        a = start + span * t
        px = cx + math.cos(a) * (r + width * 0.45)
        py = cy + math.sin(a) * (r + width * 0.45)
        pygame.draw.circle(surf, cream, (int(px), int(py)), max(1, width // 3))
    if tip_cream:
        a = start + span
        px = cx + math.cos(a) * r
        py = cy + math.sin(a) * r
        pygame.draw.circle(surf, cream, (int(px), int(py)), width)


def _ear(surf, cx, cy, r, sgn, back=FUR_D, inner=CREAM):
    pygame.draw.circle(surf, back, (cx, cy), r)
    pygame.draw.circle(surf, inner, (cx + sgn, cy + 1), max(1, r - 2))


def _mask(surf, hx, hy, w, h, *, brow=True):
    """White panda face-mask: cheek blobs + a centre blaze, with rust
    tear-track lines back to the eyes."""
    _aaellipse(surf, CREAM, (hx - 4, hy + 2), w, h)
    _aaellipse(surf, CREAM, (hx + 5, hy + 2), w, h)
    _aaellipse(surf, CREAM, (hx, hy + 3), 4, h)
    if brow:
        for dx in (-5, 6):
            pygame.draw.line(surf, FUR_D, (hx + dx, hy - 3),
                             (hx + dx + (1 if dx > 0 else -1), hy + 4), 2)


def build_red_panda_v1(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1 - f)                       # tail sweeps up on the down-pose

    # Fat ringed tail curling UP behind the back (a tight C hugging the body).
    tcx, tcy = BCX - 2, BCY + 4
    base = math.radians(150)
    arc = _ringed_tail_arc
    arc(surf, tcx, tcy, 20, 7, 5,
        span=math.radians(150) + lift * math.radians(20),
        start=base)

    # Plump round body.
    _aaellipse(surf, FUR_D, (BCX + 1, BCY + 2), 18, 17)
    _aaellipse(surf, FUR, (BCX, BCY), 17, 16)
    _aaellipse(surf, CREAM, (BCX + 2, BCY + 6), 10, 9)        # belly
    _aaellipse(surf, FUR_H, (BCX - 4, BCY - 5), 7, 5)

    _paw_pair(surf, BCY + 12, f)

    # Round head with the broad white mask.
    _aaellipse(surf, FUR_D, (HCX, HCY + 1), 13, 12)
    _aaellipse(surf, FUR, (HCX - 1, HCY), 12, 11)
    _ear(surf, HCX - 8, CROWN_Y + 4, 5, -1)
    _ear(surf, HCX + 7, CROWN_Y + 4, 5, +1)
    _mask(surf, HCX, HCY, 7, 8)

    _eye(surf, HCX - 4, HCY, 3)
    _eye(surf, HCX + 5, HCY, 3)
    pygame.draw.circle(surf, EYEDK, (HCX, HCY + 6), 2)        # nose
    pygame.draw.line(surf, EYEDK, (HCX, HCY + 7), (HCX, HCY + 9), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v2 · REACHING LEAPER — dynamic & athletic. Body leans forward into the dive,
#     forepaws reach ahead, and the tail whips LOW-back then high in a long
#     upward S. Reads as a mid-leap acrobat. Tail is a sweeping streamer, not
#     a cozy curl. 40px tell: the long upward tail whip + forward lean.
# ═════════════════════════════════════════════════════════════════════════════
def _tail_streamer(surf, pts, widths, n_rings):
    """A tail drawn as a tapering ringed streamer along a poly-spine. Bands
    alternate fur/ring; the tip band is cream. `widths` per spine point."""
    # Densify the spine for smooth banding.
    dense, dw = [], []
    for i in range(len(pts) - 1):
        for s in range(6):
            t = s / 6
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
            w = widths[i] + (widths[i + 1] - widths[i]) * t
            dense.append((int(x), int(y)))
            dw.append(max(2, int(w)))
    for i, (p, w) in enumerate(zip(dense, dw)):
        band = int(i / len(dense) * n_rings * 2) % 2
        is_tip = i >= len(dense) - 4
        col = CREAM if is_tip else (RING if band else FUR)
        pygame.draw.circle(surf, col, p, w)
    # Cream rim highlights.
    for i in range(n_rings):
        idx = int((i + 0.5) / n_rings * (len(dense) - 1))
        pygame.draw.circle(surf, CREAM, dense[idx], max(1, dw[idx] // 3))


def build_red_panda_v2(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1 - f)

    # Long upward tail whip: from behind-low up to a high curl, sweeping with f.
    tip_y = CROWN_Y + 2 - int(lift * 6)
    _tail_streamer(
        surf,
        [(BCX - 4, BCY + 6), (16, BCY + 2), (12, BCY - 12),
         (20, CROWN_Y + 6), (28, tip_y)],
        [9, 8, 7, 5, 3],
        n_rings=5,
    )

    # Forward-leaning egg body.
    _aaellipse(surf, FUR_D, (BCX + 2, BCY + 1), 17, 15)
    _aaellipse(surf, FUR, (BCX + 1, BCY), 16, 14)
    _aaellipse(surf, CREAM, (BCX + 5, BCY + 4), 9, 8)
    _aaellipse(surf, FUR_H, (BCX - 2, BCY - 5), 6, 4)

    # Reaching forepaws thrust forward (the leap).
    reach = int(2 + lift * 4)
    for fx, fy in ((30, BCY + 11), (38, BCY + 9)):
        pygame.draw.line(surf, LEGDK, (fx, fy), (fx + reach + 4, fy + 3), 3)
        pygame.draw.circle(surf, LEGDK, (fx + reach + 4, fy + 3), 2)

    # Head pushed forward.
    _aaellipse(surf, FUR_D, (HCX + 1, HCY + 1), 12, 11)
    _aaellipse(surf, FUR, (HCX, HCY), 11, 10)
    _ear(surf, HCX - 6, CROWN_Y + 5, 5, -1)
    _ear(surf, HCX + 8, CROWN_Y + 4, 5, +1)
    _mask(surf, HCX + 1, HCY, 6, 7)

    _eye(surf, HCX - 2, HCY - 1, 3)
    _eye(surf, HCX + 6, HCY - 1, 3)
    pygame.draw.polygon(surf, EYEDK,                          # snout-forward nose
                        [(HCX + 8, HCY + 3), (HCX + 12, HCY + 4),
                         (HCX + 8, HCY + 6)])
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v3 · BIG-TAIL HERO — the TAIL is the brand. A huge, fat, many-ringed plume
#     looms behind a deliberately small body, filling the upper-left like a
#     question-mark. Tail-forward branding: the ringed arc is unmissable even
#     when the rest shrinks. 40px tell: a giant ringed banana arc over the back.
# ═════════════════════════════════════════════════════════════════════════════
def build_red_panda_v3(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1 - f)

    # GIANT ringed tail arc sweeping from low-back up over the head.
    tcx, tcy = BCX + 2, BCY + 8
    _ringed_tail_arc(
        surf, tcx, tcy, 26, 9, 6,
        span=math.radians(160) + lift * math.radians(18),
        start=math.radians(140),
    )

    # Smaller body (so the tail dominates), sat low-right.
    bcy = BCY + 3
    _aaellipse(surf, FUR_D, (BCX + 5, bcy + 1), 14, 13)
    _aaellipse(surf, FUR, (BCX + 4, bcy), 13, 12)
    _aaellipse(surf, CREAM, (BCX + 6, bcy + 4), 8, 7)
    _aaellipse(surf, FUR_H, (BCX, bcy - 4), 5, 3)

    _paw_pair(surf, bcy + 10, f)

    # Head.
    _aaellipse(surf, FUR_D, (HCX + 1, HCY + 1), 12, 11)
    _aaellipse(surf, FUR, (HCX, HCY), 11, 10)
    _ear(surf, HCX - 6, CROWN_Y + 5, 5, -1)
    _ear(surf, HCX + 8, CROWN_Y + 5, 5, +1)
    _mask(surf, HCX, HCY, 6, 7)

    _eye(surf, HCX - 3, HCY, 3)
    _eye(surf, HCX + 5, HCY, 3)
    pygame.draw.circle(surf, EYEDK, (HCX + 1, HCY + 5), 2)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v4 · CHIBI ROUND — maximum mascot charm. Oversized head, huge sparkly eyes,
#     tiny tucked body and paws, a short FAT tail curling up tight beside the
#     cheek like a comma. Warmest, baby-cute, gacha-charming read.
#     40px tell: the giant-eyed white mask face + the chunky comma tail.
# ═════════════════════════════════════════════════════════════════════════════
def build_red_panda_v4(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1 - f)

    # Short fat comma tail curling up tight on the left.
    tcx, tcy = BCX - 6, BCY + 2
    _ringed_tail_arc(
        surf, tcx, tcy, 13, 9, 4,
        span=math.radians(150) + lift * math.radians(16),
        start=math.radians(165),
    )

    # Tiny tucked body low in the frame.
    bcy = BCY + 6
    _aaellipse(surf, FUR_D, (BCX + 1, bcy + 1), 13, 11)
    _aaellipse(surf, FUR, (BCX, bcy), 12, 10)
    _aaellipse(surf, CREAM, (BCX + 1, bcy + 3), 7, 6)
    # Little tucked paws.
    for fx in (28, 36):
        pygame.draw.circle(surf, LEGDK, (fx, bcy + 8 - int(f * 2)), 2)

    # OVERSIZED head dominating the frame.
    hcy = HCY + 1
    _aaellipse(surf, FUR_D, (HCX - 1, hcy + 1), 16, 15)
    _aaellipse(surf, FUR, (HCX - 2, hcy), 15, 14)
    # Big rounded ears with cream interiors.
    _ear(surf, HCX - 12, CROWN_Y + 2, 6, -1)
    _ear(surf, HCX + 8, CROWN_Y + 2, 6, +1)

    # Broad mask covering most of the face.
    _aaellipse(surf, CREAM, (HCX - 7, hcy + 2), 8, 9)
    _aaellipse(surf, CREAM, (HCX + 5, hcy + 2), 8, 9)
    _aaellipse(surf, CREAM, (HCX - 1, hcy + 4), 5, 8)
    for dx in (-7, 7):                                        # rust tear-tracks
        pygame.draw.line(surf, FUR_D, (HCX + dx, hcy - 4),
                         (HCX + dx, hcy + 3), 2)

    # HUGE sparkly eyes — the charm.
    _eye(surf, HCX - 6, hcy, 5)
    _eye(surf, HCX + 4, hcy, 5)
    pygame.draw.circle(surf, EYEDK, (HCX - 1, hcy + 7), 3)    # big nose
    pygame.draw.circle(surf, (110, 60, 36), (HCX - 2, hcy + 6), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v5 · FOXY BANDIT — sleeker & sharper, more fox-like. Big tufted POINTED ears,
#     a bold "bandit" face-mask (sharp rust mask around the eyes over a cream
#     muzzle), and a slimmer tail with FEWER, BOLDER rings and a big bright
#     cream tip. Cooler, more graphic, less plush. 40px tell: pointed-ear
#     silhouette + bandit mask + strong white tail-tip flag.
# ═════════════════════════════════════════════════════════════════════════════
def _pointed_ear(surf, cx, cy, sgn, back=FUR_D, inner=CREAM, tuft=CREAM_D):
    pygame.draw.polygon(surf, back,
                        [(cx - 4, cy + 6), (cx + sgn * 2, cy - 8),
                         (cx + 5, cy + 5)])
    pygame.draw.polygon(surf, inner,
                        [(cx - 1, cy + 4), (cx + sgn * 1, cy - 3),
                         (cx + 3, cy + 4)])
    # Lynx-style tuft.
    pygame.draw.line(surf, tuft, (cx + sgn * 2, cy - 8),
                     (cx + sgn * 4, cy - 12), 1)


def build_red_panda_v5(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    lift = (1 - f)

    # Slimmer tail: fewer, bolder rings + a big bright cream tip "flag".
    tcx, tcy = BCX - 2, BCY + 6
    _ringed_tail_arc(
        surf, tcx, tcy, 22, 6, 4,
        span=math.radians(140) + lift * math.radians(22),
        start=math.radians(150),
    )
    # Emphasise the bright cream tip flag.
    a = math.radians(150) + math.radians(140) + lift * math.radians(22)
    px = tcx + math.cos(a) * 22
    py = tcy + math.sin(a) * 22
    pygame.draw.circle(surf, CREAM, (int(px), int(py)), 7)
    pygame.draw.circle(surf, CREAM_D, (int(px), int(py)), 7, 1)

    # Leaner body.
    _aaellipse(surf, FUR_D, (BCX + 2, BCY + 1), 16, 14)
    _aaellipse(surf, FUR, (BCX + 1, BCY), 15, 13)
    _aaellipse(surf, CREAM, (BCX + 3, BCY + 4), 8, 7)
    _aaellipse(surf, FUR_H, (BCX - 3, BCY - 4), 6, 4)

    _paw_pair(surf, BCY + 10, f)

    # Sleeker head with a pointier muzzle.
    _aaellipse(surf, FUR_D, (HCX, HCY + 1), 12, 11)
    _aaellipse(surf, FUR, (HCX - 1, HCY), 11, 10)
    _pointed_ear(surf, HCX - 7, CROWN_Y + 4, -1)
    _pointed_ear(surf, HCX + 8, CROWN_Y + 4, +1)

    # Bandit mask: cream muzzle + a sharp rust mask band across the eyes.
    _aaellipse(surf, CREAM, (HCX, HCY + 4), 9, 7)             # cream lower face
    pygame.draw.polygon(surf, FUR_D,                          # rust eye-band
                        [(HCX - 9, HCY - 3), (HCX + 8, HCY - 3),
                         (HCX + 7, HCY + 2), (HCX - 8, HCY + 2)])
    # Cream brow dots above the band for the panda spectacle look.
    pygame.draw.circle(surf, CREAM, (HCX - 4, HCY - 2), 2)
    pygame.draw.circle(surf, CREAM, (HCX + 4, HCY - 2), 2)

    _eye(surf, HCX - 4, HCY, 3, iris=(20, 12, 6))
    _eye(surf, HCX + 4, HCY, 3, iris=(20, 12, 6))
    # Pointed muzzle + nose.
    pygame.draw.polygon(surf, CREAM,
                        [(HCX + 2, HCY + 3), (HCX + 11, HCY + 5),
                         (HCX + 2, HCY + 8)])
    pygame.draw.circle(surf, EYEDK, (HCX + 9, HCY + 5), 2)
    return surf


# ── getters + label→getter registry (mirrors animal_skins.BUILDERS) ──────────
get_v1 = _make_prebuilt_skin(build_red_panda_v1)
get_v2 = _make_prebuilt_skin(build_red_panda_v2)
get_v3 = _make_prebuilt_skin(build_red_panda_v3)
get_v4 = _make_prebuilt_skin(build_red_panda_v4)
get_v5 = _make_prebuilt_skin(build_red_panda_v5)

BUILDERS = {
    "v1 Cozy Curl":     get_v1,
    "v2 Reaching Leaper": get_v2,
    "v3 Big-Tail Hero": get_v3,
    "v4 Chibi Round":   get_v4,
    "v5 Foxy Bandit":   get_v5,
}
