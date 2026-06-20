"""Candidate AURORA STAG skins for the ANIMALS Store — round-1 exploration.

A LEGENDARY spectacle skin: a hooved land mammal (NOT a bird) as the flex.
The silhouette is a noble deer head/forebody crowned by a vast branching
antler-rack; the signature 40px tell is that rack rendered as flowing
northern-lights ribbons studded with floating white star-points — a glowing
crown that reads against bright-day AND night skies.

There is NO live particle system feeding the sprite: the aurora glow + the
star-points are BAKED into each of the 4 flat frames. The "flap" (there are
no wings) is reinterpreted as the aurora antlers rippling like curtains
across the 4 base wing poses — the gradient bands and star positions shift
frame-to-frame so the crown shimmers — plus a small ear-flick on the up-pose.

Contract mirrors game/animal_skins.py so the winner lifts straight in:

  * `build_aurora_stag_vN(wing_angle_deg) -> pygame.Surface`  one flat frame
    on a 64×84 SRCALPHA canvas. Body mass centred at (32,44); head near
    (44,34); the rack reaches UP into the top ~24px of headroom.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_aurora_stag_v1": get_..., ...}` registry at the bottom.

Body anchoring: collision is a fixed 14px circle at the body centre, so every
variant keeps the body mass pinned at (32,44) even though the antlers are
tall — the rack never drags the body off-centre.
"""
import math
import pygame

from game import parrot
from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (rack reaches up into the headroom) ────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom for the antler-rack
DY          = 12                # body offset down into the tall canvas

# Body / head anchors in composite space (base anchors + DY on y).
BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


# ── aurora palette (per the brief) ───────────────────────────────────────────
BODY      = (30, 42, 58)        # #1E2A3A deep slate-blue
BODY_D    = (20, 30, 44)
BODY_H    = (58, 78, 104)
BODY_DUSK = (62, 78, 104)       # lighter dusky body for the pale variants
BODY_DUSK_D = (44, 58, 82)
BODY_DUSK_H = (110, 132, 166)
MUZZLE    = (16, 22, 32)
AUR_GREEN = (61, 242, 192)      # #3DF2C0
AUR_VIO   = (122, 92, 255)      # #7A5CFF
AUR_PINK  = (255, 107, 194)     # #FF6BC2
AUR_GOLD  = (255, 214, 120)     # warm accent for the pink/gold scheme
STAR      = (255, 255, 255)


# ── shared factory (local copy of animal_skins._make_prebuilt_skin) ──────────
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


# ── tiny shared drawing helpers ──────────────────────────────────────────────
def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _eye(surf, cx, cy, r, *, iris=(20, 22, 30), white=(250, 250, 245),
         glint=True):
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    if glint:
        pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                           max(1, r // 3))


def _flap(angle_deg):
    """0..1 'up' factor; _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _glow_dot(surf, color, pos, r, alpha=120):
    """Soft additive-ish glow blob baked into the frame (no live particles)."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        a = int(alpha * (1 - rr / r) ** 1.4)
        pygame.draw.circle(g, (*color, a), (r, r), rr)
    surf.blit(g, (int(pos[0] - r), int(pos[1] - r)),
              special_flags=pygame.BLEND_RGBA_ADD)


def _star(surf, pos, size, color=STAR, glow=AUR_GREEN):
    """A floating 4-point star-point with a soft coloured halo, baked in."""
    x, y = int(pos[0]), int(pos[1])
    _glow_dot(surf, glow, (x, y), size * 3, alpha=110)
    pygame.draw.line(surf, color, (x - size, y), (x + size, y), 1)
    pygame.draw.line(surf, color, (x, y - size), (x, y + size), 1)
    pygame.draw.circle(surf, color, (x, y), max(1, size // 2))


def _aurora_ribbon(surf, pts, width, frame_t, cols, *, alpha=255):
    """A flowing aurora ribbon along a poly-spine. The colour cycles through
    `cols` down the ribbon and SHIFTS by frame_t so the curtain shimmers
    across the 4 frames — that is the baked-in 'ripple'."""
    n = len(pts)
    for i in range(n - 1):
        t = (i / max(1, n - 2) + frame_t) % 1.0
        # cycle through the supplied aurora colours
        seg = t * (len(cols) - 1)
        ci = int(seg)
        col = _lerp(cols[ci], cols[min(ci + 1, len(cols) - 1)], seg - ci)
        # taper width toward the tip
        w = max(1, int(width * (1 - 0.55 * i / max(1, n - 1))))
        pygame.draw.line(surf, (*col, alpha), pts[i], pts[i + 1], w)


def _ear(surf, base, sgn, flick, col, col_d):
    """A deer ear; `flick` lifts/rotates the tip on the up-pose."""
    bx, by = base
    tipx = bx + sgn * (6 + int(flick * 2))
    tipy = by - 9 + int(flick * 3)
    pygame.draw.polygon(surf, col_d,
                        [(bx, by), (tipx, tipy), (bx + sgn * 3, by - 2)])
    pygame.draw.polygon(surf, col,
                        [(bx + sgn, by - 1), (tipx - sgn, tipy + 2),
                         (bx + sgn * 3, by - 2)])


def _deer_head(surf, body, body_d, body_h, *, regal=True, dusk=False):
    """Shared noble deer head/forebody anchored at the body centre.

    Returns the (skull-left, skull-right) ear-base x's so each variant can
    grow its own rack from a consistent skull."""
    # Forebody / chest mass (kept centred at BCX,BCY for fair collision).
    _aaellipse(surf, body_d, (BCX + 1, BCY + 2), 16, 16)
    _aaellipse(surf, body, (BCX, BCY), 15, 15)
    _aaellipse(surf, body_h, (BCX - 4, BCY - 4), 7, 5)
    # Neck sweeping up to the head.
    pygame.draw.polygon(surf, body_d,
                        [(BCX + 4, BCY - 6), (BCX + 14, BCY - 12),
                         (HCX - 2, HCY + 8), (BCX + 2, BCY + 2)])
    pygame.draw.polygon(surf, body,
                        [(BCX + 5, BCY - 5), (BCX + 13, BCY - 11),
                         (HCX - 3, HCY + 7), (BCX + 4, BCY + 1)])

    # Long noble muzzle/head.
    _aaellipse(surf, body_d, (HCX, HCY + 1), 11, 9)
    _aaellipse(surf, body, (HCX - 1, HCY), 10, 8)
    # Tapered snout wedge.
    snout = [(HCX + 4, HCY - 4), (HCX + 15, HCY + 1),
             (HCX + 13, HCY + 6), (HCX + 3, HCY + 6)]
    pygame.draw.polygon(surf, body, snout)
    pygame.draw.polygon(surf, body_d, snout, 1)
    pygame.draw.circle(surf, MUZZLE, (HCX + 13, HCY + 2), 2)   # nose
    # Soft cheek highlight.
    _aaellipse(surf, body_h, (HCX - 3, HCY - 2), 4, 3)
    # Eye — regal almond vs gentle round.
    if regal:
        _eye(surf, HCX + 2, HCY - 1, 3, iris=(14, 16, 24))
        pygame.draw.line(surf, body_d, (HCX - 1, HCY - 3),
                         (HCX + 4, HCY - 3), 1)        # stern brow
    else:
        _eye(surf, HCX + 2, HCY, 4, iris=(18, 20, 30))
    return (HCX - 6, HCX + 1)


def _branch(surf, root, sgn, frame_t, cols, *, tines, length, spread,
            width, star_size, dusk_glow):
    """Grow ONE branching aurora antler from a skull root.

    A main beam curving up + outward, with `tines` forking off it; each beam
    + tine is an aurora ribbon, and every fork point + the tips carry a
    star-point. `frame_t` shimmers the gradient + nudges the tips so the rack
    ripples across the 4 frames."""
    rx, ry = root
    # Main beam as a curving poly-spine.
    beam = []
    steps = 6
    for i in range(steps + 1):
        t = i / steps
        bx = rx + sgn * spread * t
        by = ry - length * t - 2
        # gentle outward S-curve + per-frame shimmer wobble
        bx += sgn * 4 * math.sin(t * math.pi)
        bx += sgn * 1.5 * math.sin(frame_t * math.tau + t * 4)
        beam.append((bx, by))
    # soft glow underlay so the rack reads as light, then the bright ribbon.
    for (px, py) in beam[::2]:
        _glow_dot(surf, dusk_glow, (px, py), 5, alpha=70)
    _aurora_ribbon(surf, beam, width, frame_t, cols)

    # Tines forking off the upper half of the beam, alternating reach.
    for k in range(tines):
        bi = 2 + k                       # fork point up the beam
        if bi >= len(beam):
            break
        fx, fy = beam[bi]
        tlen = length * (0.42 - 0.04 * k)
        tine = []
        for i in range(4):
            t = i / 3
            tx = fx + sgn * spread * 0.5 * t
            ty = fy - tlen * t
            ty += -3 * math.sin(t * math.pi)         # curve the tine up
            tx += sgn * 1.2 * math.sin(frame_t * math.tau + k)
            tine.append((tx, ty))
        _aurora_ribbon(surf, tine, max(1, width - 1), frame_t, cols)
        _star(surf, tine[-1], star_size, glow=cols[k % len(cols)])

    # Brow-tine sweeping forward low on the beam (classic stag tell).
    bx0, by0 = beam[1]
    brow = [(bx0, by0), (bx0 + sgn * 5, by0 - 3), (bx0 + sgn * 9, by0 - 7)]
    _aurora_ribbon(surf, brow, max(1, width - 1), frame_t, cols)
    _star(surf, brow[-1], star_size, glow=cols[-1])
    # Crowning star at the very tip of the main beam.
    _star(surf, beam[-1], star_size + 1, glow=cols[(len(cols) - 1)])


# ═════════════════════════════════════════════════════════════════════════════
# v1 · CLASSIC SPECTRUM CROWN — symmetric branching rack, full-spectrum
#      gradient (green→violet→pink), dense star-points, dark body, regal.
#      The "default" legendary: a textbook stag rack made of northern lights.
# ═════════════════════════════════════════════════════════════════════════════
def build_aurora_stag_v1(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                       # 0 down → 1 up
    ft = (f * 0.5)                                   # shimmer phase per frame
    cols = (AUR_GREEN, AUR_VIO, AUR_PINK)

    skull_l, skull_r = _deer_head(surf, BODY, BODY_D, BODY_H, regal=True)
    # Ears tucked under the rack, small flick on the up-pose.
    flick = max(0.0, (f - 0.5) * 2)
    _ear(surf, (skull_l - 1, HCY - 4), -1, flick, BODY, BODY_D)
    _ear(surf, (skull_r + 2, HCY - 5), +1, flick, BODY, BODY_D)

    # Symmetric branching rack from each skull root.
    _branch(surf, (skull_l + 2, HCY - 5), -1, ft, cols,
            tines=3, length=26, spread=12, width=4, star_size=3,
            dusk_glow=AUR_VIO)
    _branch(surf, (skull_r, HCY - 5), +1, ft, cols,
            tines=3, length=26, spread=12, width=4, star_size=3,
            dusk_glow=AUR_VIO)
    # Extra scattered star dust between the beams for density.
    rng = ((HCX - 6, CROWN_Y), (HCX + 4, CROWN_Y - 4), (HCX, CROWN_Y + 4))
    for i, p in enumerate(rng):
        _star(surf, (p[0], p[1] + int(math.sin(ft * math.tau + i) * 2)),
              2, glow=cols[i % 3])
    # Slim deer legs hinting the hooved body.
    for fx in (28, 37):
        pygame.draw.line(surf, BODY_D, (fx, BCY + 13), (fx, BCY + 19), 2)
        pygame.draw.line(surf, MUZZLE, (fx, BCY + 19), (fx, BCY + 21), 2)
    return surf


get_aurora_stag_v1 = _make_prebuilt_skin(build_aurora_stag_v1)


# ═════════════════════════════════════════════════════════════════════════════
# v2 · TWIN CURTAIN RIBBONS — two tall sweeping translucent CURTAINS instead of
#      branchy antlers; layered green/violet sheets that hang like real
#      northern-lights drapery, sparse bright stars, gentle expression.
#      Reads as a soft glowing veil rising from the head.
# ═════════════════════════════════════════════════════════════════════════════
def _curtain(surf, root, sgn, frame_t, cols, height, width):
    """A hanging aurora curtain: a tall translucent sheet with a wavy bottom
    and vertical light-streaks, sweeping up + outward from the head."""
    rx, ry = root
    cols_top, cols_bot = cols
    # Build the sheet as a column of horizontal slabs, colour graded top→bottom
    # and rippled left/right per frame (the curtain billow).
    layers = 9
    sheet = []
    top_pts, bot_pts = [], []
    for i in range(layers + 1):
        t = i / layers
        y = ry - height * t
        cx = rx + sgn * (5 + 9 * t) + sgn * 3 * math.sin(
            frame_t * math.tau + t * 3)
        hw = width * (0.55 + 0.6 * t)
        top_pts.append((cx - hw, y))
        bot_pts.append((cx + hw, y))
    poly = top_pts + bot_pts[::-1]
    # Two translucent passes (violet under, green over) for layered drapery.
    for col, dx, a in ((cols_bot, sgn * 2, 90), (cols_top, 0, 110)):
        shifted = [(px + dx, py) for (px, py) in poly]
        sub = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
        pygame.draw.polygon(sub, (*col, a), shifted)
        surf.blit(sub, (0, 0))
    # Bright vertical light-streaks (the aurora "rays").
    for j in range(3):
        t0 = 0.15 + j * 0.3
        i0 = int(t0 * layers)
        x0 = (top_pts[i0][0] + bot_pts[i0][0]) / 2
        pygame.draw.line(surf, (*cols_top, 150),
                         (x0, ry - height * 0.15),
                         (x0 + sgn * 4, ry - height), 1)
    # Soft glow along the crest + a few sparse stars riding the top edge.
    _glow_dot(surf, cols_top, top_pts[-1], 7, alpha=90)
    for j, t in enumerate((0.55, 0.85)):
        i0 = int(t * layers)
        p = ((top_pts[i0][0] + bot_pts[i0][0]) / 2, top_pts[i0][1])
        _star(surf, p, 3, glow=cols_top)


def build_aurora_stag_v2(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    ft = f                                           # full-range billow phase

    skull_l, skull_r = _deer_head(surf, BODY, BODY_D, BODY_H, regal=False)
    flick = max(0.0, (f - 0.5) * 2)
    _ear(surf, (skull_l - 1, HCY - 4), -1, flick, BODY, BODY_D)
    _ear(surf, (skull_r + 2, HCY - 5), +1, flick, BODY, BODY_D)

    # Two big curtains: green-over-violet, sweeping up and apart.
    _curtain(surf, (skull_l + 2, HCY - 4), -1, ft,
             (AUR_GREEN, AUR_VIO), height=30, width=4)
    _curtain(surf, (skull_r, HCY - 4), +1, ft + 0.4,
             (AUR_GREEN, AUR_VIO), height=30, width=4)
    # A single high star crowning the gap between curtains.
    _star(surf, (HCX - 1, CROWN_Y - 9 + int(math.sin(ft * math.tau) * 2)),
          3, glow=AUR_PINK)
    for fx in (28, 37):
        pygame.draw.line(surf, BODY_D, (fx, BCY + 13), (fx, BCY + 19), 2)
        pygame.draw.line(surf, MUZZLE, (fx, BCY + 19), (fx, BCY + 21), 2)
    return surf


get_aurora_stag_v2 = _make_prebuilt_skin(build_aurora_stag_v2)


# ═════════════════════════════════════════════════════════════════════════════
# v3 · WIDE MAJESTIC RACK — very WIDE low-spread rack with many tines, a warm
#      PINK/GOLD aurora scheme (the rare "fire-sky" aurora), solid glowing
#      ribbons, lighter dusky-blue body. The big-game-trophy flex.
# ═════════════════════════════════════════════════════════════════════════════
def build_aurora_stag_v3(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    ft = f * 0.5
    cols = (AUR_PINK, AUR_GOLD, (255, 240, 200))

    skull_l, skull_r = _deer_head(surf, BODY_DUSK, BODY_DUSK_D, BODY_DUSK_H,
                                  regal=True, dusk=True)
    flick = max(0.0, (f - 0.5) * 2)
    _ear(surf, (skull_l - 1, HCY - 4), -1, flick, BODY_DUSK, BODY_DUSK_D)
    _ear(surf, (skull_r + 2, HCY - 5), +1, flick, BODY_DUSK, BODY_DUSK_D)

    # Wide, lower, many-tined rack: short beams, big horizontal spread.
    _branch(surf, (skull_l + 2, HCY - 5), -1, ft, cols,
            tines=4, length=20, spread=18, width=4, star_size=3,
            dusk_glow=AUR_PINK)
    _branch(surf, (skull_r, HCY - 5), +1, ft, cols,
            tines=4, length=20, spread=18, width=4, star_size=3,
            dusk_glow=AUR_PINK)
    # Warm haze behind the whole rack so it glows like a sunset aurora.
    _glow_dot(surf, AUR_PINK, (HCX - 2, CROWN_Y + 2), 16, alpha=55)
    _glow_dot(surf, AUR_GOLD, (HCX - 2, CROWN_Y), 11, alpha=45)
    for fx in (28, 37):
        pygame.draw.line(surf, BODY_DUSK_D, (fx, BCY + 13), (fx, BCY + 19), 2)
        pygame.draw.line(surf, MUZZLE, (fx, BCY + 19), (fx, BCY + 21), 2)
    return surf


get_aurora_stag_v3 = _make_prebuilt_skin(build_aurora_stag_v3)


# ═════════════════════════════════════════════════════════════════════════════
# v4 · LYRE TWIN-BEAM — two BOLD curving lyre-shaped main beams sweeping up and
#      inward (minimal branching → maximum silhouette), violet→green, a big
#      star crowning each tip, very dark body, fierce expression. The cleanest
#      40px read: two glowing arcs + two stars.
# ═════════════════════════════════════════════════════════════════════════════
def build_aurora_stag_v4(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    ft = f * 0.5
    cols = (AUR_VIO, AUR_GREEN)

    skull_l, skull_r = _deer_head(surf, BODY_D, (12, 18, 28), BODY_H,
                                  regal=True)
    flick = max(0.0, (f - 0.5) * 2)
    _ear(surf, (skull_l - 1, HCY - 4), -1, flick, BODY_D, (12, 18, 28))
    _ear(surf, (skull_r + 2, HCY - 5), +1, flick, BODY_D, (12, 18, 28))

    # Two big lyre beams: out, up, then curving back INWARD to near-touch.
    for sgn, root in ((-1, (skull_l + 2, HCY - 5)), (+1, (skull_r, HCY - 5))):
        rx, ry = root
        beam = []
        steps = 8
        for i in range(steps + 1):
            t = i / steps
            # outward then inward sweep (lyre): sin gives the belly of the arc
            bx = rx + sgn * (3 + 14 * math.sin(t * math.pi * 0.85))
            by = ry - 30 * t
            bx += sgn * 1.5 * math.sin(ft * math.tau + t * 3)  # shimmer
            beam.append((bx, by))
        # thick soft glow underlay → bold bright ribbon (high contrast tell).
        for (px, py) in beam[::2]:
            _glow_dot(surf, AUR_VIO, (px, py), 6, alpha=80)
        _aurora_ribbon(surf, beam, 5, ft, cols)
        # one short inner tine for a hint of "rack", plus the tip crown-star.
        fx, fy = beam[3]
        tine = [(fx, fy), (fx + sgn * 5, fy - 6), (fx + sgn * 7, fy - 12)]
        _aurora_ribbon(surf, tine, 3, ft, cols)
        _star(surf, tine[-1], 3, glow=AUR_GREEN)
        _star(surf, beam[-1], 4, glow=AUR_PINK)     # big crowning tip star
    for fx in (28, 37):
        pygame.draw.line(surf, BODY_D, (fx, BCY + 13), (fx, BCY + 19), 2)
        pygame.draw.line(surf, MUZZLE, (fx, BCY + 19), (fx, BCY + 21), 2)
    return surf


get_aurora_stag_v4 = _make_prebuilt_skin(build_aurora_stag_v4)


# ═════════════════════════════════════════════════════════════════════════════
# v5 · CONSTELLATION ANTLERS — the rack drawn as a STAR-CONSTELLATION lattice:
#      bright star-nodes linked by thin glowing aurora lines (like a join-the-
#      dots antler). Full spectrum, high star density, gentle expression. The
#      most ethereal, "celestial" take — the antlers are literally made of stars.
# ═════════════════════════════════════════════════════════════════════════════
def build_aurora_stag_v5(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    ft = f
    cols = (AUR_GREEN, AUR_VIO, AUR_PINK)

    skull_l, skull_r = _deer_head(surf, BODY, BODY_D, BODY_H, regal=False)
    flick = max(0.0, (f - 0.5) * 2)
    _ear(surf, (skull_l - 1, HCY - 4), -1, flick, BODY, BODY_D)
    _ear(surf, (skull_r + 2, HCY - 5), +1, flick, BODY, BODY_D)

    # Node lattice per side: (x,y) constellation points + the edges joining
    # them. Nodes drift slightly per frame so the constellation "breathes".
    def lattice(sgn, root):
        rx, ry = root
        # base nodes up the beam, fanning outward; a couple of tine tips.
        base = [
            (rx + sgn * 1,  ry - 2),     # 0 root
            (rx + sgn * 6,  ry - 9),     # 1
            (rx + sgn * 4,  ry - 17),    # 2
            (rx + sgn * 11, ry - 15),    # 3 outer tine tip
            (rx + sgn * 8,  ry - 25),    # 4 upper
            (rx + sgn * 15, ry - 24),    # 5 outer upper tip
            (rx + sgn * 9,  ry - 32),    # 6 crown tip
            (rx + sgn * 2,  ry - 11),    # 7 brow tip (forward)
        ]
        # per-frame drift
        nodes = [(x + math.sin(ft * math.tau + i) * 1.3,
                  y + math.cos(ft * math.tau + i) * 1.0)
                 for i, (x, y) in enumerate(base)]
        edges = [(0, 1), (1, 2), (2, 4), (4, 6), (1, 7),
                 (2, 3), (4, 5)]
        return nodes, edges

    for sgn, root in ((-1, (skull_l + 2, HCY - 4)), (+1, (skull_r, HCY - 4))):
        nodes, edges = lattice(sgn, root)
        # thin glowing aurora connector lines, colour cycling along the rack.
        for ei, (a, b) in enumerate(edges):
            col = cols[ei % len(cols)]
            _glow_dot(surf, col, nodes[a], 4, alpha=55)
            pygame.draw.line(surf, (*col, 200), nodes[a], nodes[b], 1)
        # bright star-points at every node — the rack IS stars.
        for ni, p in enumerate(nodes):
            sz = 3 if ni in (3, 5, 6, 7) else 2     # tips bigger
            _star(surf, p, sz, glow=cols[ni % len(cols)])

    # A faint full-spectrum halo unifying the celestial crown.
    _glow_dot(surf, AUR_VIO, (HCX - 1, CROWN_Y - 2), 18, alpha=40)
    for fx in (28, 37):
        pygame.draw.line(surf, BODY_D, (fx, BCY + 13), (fx, BCY + 19), 2)
        pygame.draw.line(surf, MUZZLE, (fx, BCY + 19), (fx, BCY + 21), 2)
    return surf


get_aurora_stag_v5 = _make_prebuilt_skin(build_aurora_stag_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Candidate registry (one winner lifts into game/animal_skins.py as
# "skin_aurora_stag").
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_aurora_stag_v1": get_aurora_stag_v1,
    "skin_aurora_stag_v2": get_aurora_stag_v2,
    "skin_aurora_stag_v3": get_aurora_stag_v3,
    "skin_aurora_stag_v4": get_aurora_stag_v4,
    "skin_aurora_stag_v5": get_aurora_stag_v5,
}
