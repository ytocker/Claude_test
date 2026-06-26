"""Red panda — DESIGN 1: EMBER SCOUT (R1).

Bright-eyed forager mid-leap. The read at 40px is "round critter + huge
curled tail": a rounded acorn body, two clear triangular ears, and a thick
plush tail that sweeps up like a question-mark over the back-left.

Self-contained scratch builder (NOT registered in any BUILDERS dict; never
imports game.animal_red_panda). The tail is drawn first so the body overlaps
its root with no seam; the head is drawn last so it sits clean on top.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse

# Canvas / anchors (taller than the parrot sprite to fit the lifted tail).
COMPOSITE_W = 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY    = 32, 44        # body centre
HCX, HCY    = 44, 34        # head centre
CROWN_Y     = 24            # ear-root height

# Palette — warm rust forager.
BODY     = (193, 90, 46)    # base fur
SHADOW   = (126, 51, 26)    # deepest shade / underside
HIGH     = (242, 148, 78)   # forehead + belly gloss highlight
CREAM    = (246, 230, 204)  # eye-surround, inner ear, belly, tail rings
CREAM_D  = (214, 196, 166)  # cream in shade (AO)
ACCENT   = (58, 36, 24)     # nose, eye-line accent, dark detail
RING_SH  = (104, 42, 22)    # crescent ring shade edge


def _make_prebuilt_skin(build_fn):
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


def _flap(angle_deg):
    """0 = down-pose (high flap), 1 = up-pose (low flap).

    Maps _WING_ANGLES (50, 20, -10, -40) onto 0..1 so the tail can flex with
    the cadence: flap high -> tail dips a touch; flap low -> tail lifts."""
    return (40 - angle_deg) / 90.0


def _cheek_mask(surf, hcx, hcy, sgn):
    """Bold cream brow/cheek patch — the red-panda facial mask. A single
    teardrop wedge per side (two overlapping r4 discs) sweeping up-and-toward
    the ear, so it reads as the dominant white patch at 40px and the two sides
    don't merge into spectacles. sgn = -1 left, +1 right."""
    if sgn < 0:
        discs = [(hcx - 7, hcy + 1), (hcx - 9, hcy - 3)]
    else:
        discs = [(hcx + 9, hcy + 1), (hcx + 11, hcy - 3)]
    for px, py in discs:
        _aaellipse(surf, (252, 242, 222), (px, py), 4, 4)


def _eye(surf, cx, cy, r):
    """Small dark forward eye with a single catch-light; the cream mask is
    drawn separately so the two surrounds never fuse into goggles."""
    # Tear-track: a clean 1px dark notch at the inner eye corner (toward muzzle).
    pygame.draw.line(surf, ACCENT, (cx, cy + r), (cx, cy + r + 2), 1)
    # Eyeball — warm brown core (not near-black) reads as panda, not angry.
    pygame.draw.circle(surf, ACCENT, (cx, cy), r)
    pygame.draw.circle(surf, (42, 28, 20), (cx, cy), max(1, r - 1))
    # Catch-light.
    pygame.draw.circle(surf, (255, 252, 246), (cx - 1, cy - 1), 1)


def _ear(surf, cx, cy, sgn):
    """Triangular pointed ear with a high-contrast cream inner; sgn = -1 left,
    +1 right. Inner edge is pulled toward the flank so a clear russet valley
    sits between the two ear bases instead of one dark crown band."""
    # Inner edge shifted outward so the two ears leave a gap at the crown.
    tip   = (cx + sgn * 4, cy - 9)
    inner = (cx + sgn * 8, cy + 2)
    outer = (cx + sgn * 2, cy + 2)
    pygame.draw.polygon(surf, SHADOW, [tip, inner, outer])
    pygame.draw.polygon(surf, BODY,
                        [(tip[0], tip[1] + 1),
                         (inner[0] - sgn, inner[1]),
                         (outer[0] + sgn, outer[1])])
    # Bright high-contrast cream inner triangle.
    pygame.draw.polygon(surf, (252, 242, 222),
                        [(cx + sgn * 4, cy - 5),
                         (cx + sgn * 6, cy + 1),
                         (cx + sgn * 2, cy + 1)])


def _tail_curve():
    """Explicit Bezier-like spine of the tail from rump (lower-left) sweeping
    up-and-over to the left — a question-mark hook, NOT a circular arc.

    Returns a list of (x, y) control samples from root to tip."""
    p0 = (24, 56)   # root at the rump
    p1 = (10, 52)   # bulge out left
    p2 = (4,  34)   # climb up the left side
    p3 = (14, 22)   # crest, curling back to the right over the back
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = (mt * mt * mt * p0[0] + 3 * mt * mt * t * p1[0]
             + 3 * mt * t * t * p2[0] + t * t * t * p3[0])
        y = (mt * mt * mt * p0[1] + 3 * mt * mt * t * p1[1]
             + 3 * mt * t * t * p2[1] + t * t * t * p3[1])
        pts.append((x, y))
    return pts


def _tail(surf, f):
    """Thick plush tail built as overlapping circles along _tail_curve, radius
    tapering root->tip, with stacked CRESCENT rings that bend with the curve
    (every other 2-3 samples render cream instead of fur)."""
    pts = _tail_curve()
    n   = len(pts) - 1
    # Tail flex: low flap lifts the whole curve; high flap dips it.
    lift = (f - 0.5) * 6   # f=1 (up-pose) -> +3px lift, f=0 -> -3px dip
    pts  = [(x, y - lift * (i / n)) for i, (x, y) in enumerate(pts)]

    def radius(i):
        t = i / n
        return 10 - t * 5    # ~10 at root, ~5 at tip

    # Drop-shadow pass (offset down-right) so the plume reads as volume.
    for i, (x, y) in enumerate(pts):
        pygame.draw.circle(surf, SHADOW, (int(x + 1), int(y + 2)), int(radius(i)) + 1)

    # Base fur pass.
    for i, (x, y) in enumerate(pts):
        pygame.draw.circle(surf, BODY, (int(x), int(y)), int(radius(i)))

    # Crescent rings: alternate cream bands that bend with the tail. Each band
    # is a short stack of circles offset along the local curve normal so it
    # wraps the tail width as a soft crescent rather than a flat dot.
    for i in range(1, n, 2):
        # Cream on this band; russet gap on the next — alternating.
        x, y = pts[i]
        # Local tangent from neighbouring samples -> normal for the crescent.
        px, py = pts[i - 1]
        nx, ny = pts[min(i + 1, n)]
        tx, ty = (nx - px), (ny - py)
        tl = math.hypot(tx, ty) or 1.0
        ux, uy = -ty / tl, tx / tl          # unit normal
        rad = radius(i)
        # Shade rim of the crescent (toward the inner curve).
        for off in (-0.55, -0.2, 0.15, 0.5):
            cx = int(x + ux * off * rad)
            cy = int(y + uy * off * rad)
            pygame.draw.circle(surf, RING_SH, (cx, cy), max(2, int(rad * 0.52)))
        # Cream crescent body, pushed slightly to the outer flank. Cream is
        # wider than the russet gaps so the tail reads as "cream-banded".
        for off in (-0.4, -0.05, 0.3):
            cx = int(x + ux * off * rad)
            cy = int(y + uy * off * rad)
            pygame.draw.circle(surf, CREAM, (cx, cy), max(2, int(rad * 0.55)))

    # Cream-white terminal tip.
    tx, ty = pts[-1]
    pygame.draw.circle(surf, CREAM_D, (int(tx), int(ty)), 5)
    pygame.draw.circle(surf, (252, 244, 232), (int(tx - 1), int(ty - 1)), 3)


def _legs(surf, f):
    """Warm rust legs tucked tight under the body with small paw dots; tuck
    deeper on the up-pose. Rust (not near-black) so they read as fur, not
    detached blobs."""
    drop = int(5 - f * 3)
    for fx in (29, 35):
        pygame.draw.line(surf, SHADOW, (fx, BCY + 9), (fx, BCY + 9 + drop), 4)
        pygame.draw.circle(surf, SHADOW, (fx, BCY + 9 + drop), 3)
        pygame.draw.circle(surf, ACCENT, (fx - 1, BCY + 9 + drop), 1)


def _body(surf):
    """Soft teardrop acorn body, 4-layer shading + white belly with chin AO."""
    bcy = BCY + 1
    # Shadow underlay.
    _aaellipse(surf, SHADOW, (BCX + 4, bcy + 2), 15, 14)
    # Base.
    _aaellipse(surf, BODY,   (BCX + 3, bcy),     14, 13)
    # Mid highlight (upper-left lit flank).
    _aaellipse(surf, HIGH,   (BCX - 2, bcy - 5),  7, 5)
    # Belly patch with an AO shadow under the chin.
    _aaellipse(surf, CREAM_D, (BCX + 6, bcy + 1), 9, 9)   # AO ring
    _aaellipse(surf, CREAM,   (BCX + 6, bcy + 3), 8, 8)   # bright belly


def _head(surf, f):
    """Round head, slight upward alert tilt, big forward eyes + ears + nose."""
    hcx, hcy = HCX, HCY
    # Head ball — shadow, base, forehead gloss.
    _aaellipse(surf, SHADOW, (hcx + 1, hcy + 1), 14, 13)
    _aaellipse(surf, BODY,   (hcx,     hcy),     13, 12)
    _aaellipse(surf, HIGH,   (hcx - 3, hcy - 6),  7, 5)   # forehead gloss

    # Ears flanking the crown with a clear russet gap between their bases.
    _ear(surf, hcx - 8, CROWN_Y + 4, -1)
    _ear(surf, hcx + 9, CROWN_Y + 4, +1)

    # Bold cream brow/cheek mask first, anchored on the head centre so the two
    # teardrop wedges dominate as white patches without fusing into goggles.
    _cheek_mask(surf, hcx, hcy, -1)
    _cheek_mask(surf, hcx, hcy, +1)

    # Short cream muzzle wedge bridging the lower face, anchoring the T.
    elx, erx, ey = hcx - 1, hcx + 6, hcy - 2
    mcx = (elx + erx) // 2
    _aaellipse(surf, CREAM_D, (mcx, hcy + 7), 4, 3)
    _aaellipse(surf, CREAM,   (mcx, hcy + 6), 4, 3)

    # Eyes lifted to hcy-2 so a cream band separates them from the nose; nose
    # is a small 2px spot sitting inside the muzzle with cream above & below.
    # Together the two eyes + nose spot read as a clean T, no mouth competing.
    _eye(surf, elx, ey, 2)
    _eye(surf, erx, ey, 2)
    pygame.draw.circle(surf, ACCENT, (hcx + 1, hcy + 6), 2)


def build_ember_scout(wing_angle_deg):
    """Compose one frame for the given wing angle. Tail -> body -> legs -> head
    so the body overlaps the tail root (no seam) and the head reads cleanly."""
    surf = _new()
    f = _flap(wing_angle_deg)
    _tail(surf, f)
    _body(surf)
    _legs(surf, f)
    _head(surf, f)
    return surf


build = _make_prebuilt_skin(build_ember_scout)
