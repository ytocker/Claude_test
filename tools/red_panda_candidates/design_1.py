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
LEG_DARK = (40, 24, 16)     # tucked legs / paws
RUST_TR  = (150, 60, 30)    # rust tear-track
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


def _eye(surf, cx, cy, r):
    """Large forward eye on a cream surround with a rust tear-track below."""
    # Cream eye-surround patch behind the eye.
    _aaellipse(surf, CREAM_D, (cx, cy + 1), r + 3, r + 3)
    _aaellipse(surf, CREAM,   (cx, cy),     r + 3, r + 3)
    # Rust tear-track dropping from the inner corner.
    pygame.draw.line(surf, RUST_TR, (cx, cy + r), (cx + 1, cy + r + 4), 2)
    # Eyeball.
    pygame.draw.circle(surf, ACCENT, (cx, cy), r)
    pygame.draw.circle(surf, (16, 10, 8), (cx + 1, cy), max(2, r - 1))
    # Catch-light.
    pygame.draw.circle(surf, (255, 252, 246), (cx - 1, cy - 1), max(1, r // 3))


def _ear(surf, cx, cy, sgn):
    """Triangular pointed ear with a cream inner; sgn = -1 left, +1 right."""
    tip   = (cx + sgn * 4, cy - 9)
    inner = (cx + sgn * 9, cy + 2)
    outer = (cx - sgn * 5, cy + 2)
    pygame.draw.polygon(surf, SHADOW, [tip, inner, outer])
    pygame.draw.polygon(surf, BODY,
                        [(tip[0], tip[1] + 1),
                         (inner[0] - sgn, inner[1]),
                         (outer[0] + sgn, outer[1])])
    # Cream inner triangle.
    pygame.draw.polygon(surf, CREAM,
                        [(cx + sgn * 3, cy - 5),
                         (cx + sgn * 6, cy + 1),
                         (cx + sgn * 1, cy + 1)])


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
            pygame.draw.circle(surf, RING_SH, (cx, cy), max(2, int(rad * 0.6)))
        # Cream crescent body, pushed slightly to the outer flank.
        for off in (-0.4, -0.05, 0.3):
            cx = int(x + ux * off * rad)
            cy = int(y + uy * off * rad)
            pygame.draw.circle(surf, CREAM, (cx, cy), max(2, int(rad * 0.5)))

    # Cream-white terminal tip.
    tx, ty = pts[-1]
    pygame.draw.circle(surf, CREAM_D, (int(tx), int(ty)), 5)
    pygame.draw.circle(surf, (252, 244, 232), (int(tx - 1), int(ty - 1)), 3)


def _legs(surf, f):
    """Dark tucked legs with small paw dots; tuck deeper on the up-pose."""
    drop = int(7 - f * 4)
    for fx in (27, 37):
        pygame.draw.line(surf, LEG_DARK, (fx, BCY + 9), (fx, BCY + 9 + drop), 4)
        pygame.draw.circle(surf, LEG_DARK, (fx, BCY + 9 + drop), 3)
        pygame.draw.circle(surf, (60, 38, 26), (fx - 1, BCY + 8 + drop), 1)


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
    _aaellipse(surf, HIGH,   (hcx - 3, hcy - 6),  6, 4)   # forehead gloss

    # Ears flanking the crown.
    _ear(surf, hcx - 8, CROWN_Y + 4, -1)
    _ear(surf, hcx + 9, CROWN_Y + 4, +1)

    # Large forward-facing eyes (~60% body width apart), slight upward tilt.
    _eye(surf, hcx - 4, hcy - 1, 3)
    _eye(surf, hcx + 7, hcy - 1, 3)

    # Small dark nose + hint of a mouth.
    pygame.draw.circle(surf, ACCENT, (hcx + 1, hcy + 6), 2)
    pygame.draw.line(surf, ACCENT, (hcx + 1, hcy + 8), (hcx + 1, hcy + 10), 1)
    pygame.draw.line(surf, ACCENT, (hcx - 2, hcy + 10), (hcx + 1, hcy + 10), 1)
    pygame.draw.line(surf, ACCENT, (hcx + 1, hcy + 10), (hcx + 4, hcy + 10), 1)


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
