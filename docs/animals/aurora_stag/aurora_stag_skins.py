"""Production AURORA STAG skin for the ANIMALS Store — round-2 (v4 winner).

A LEGENDARY spectacle skin: a hooved land mammal (NOT a bird) as the flex.
The silhouette is a noble deer head/forebody crowned by two bold curving
lyre-shaped antler-beams rendered as flowing northern-lights ribbons, each
tipped by a floating 4-point star — a glowing crown that reads against
bright-day AND night skies.

There is NO live particle system feeding the sprite: the aurora glow + the
star-points are BAKED into each of the 4 flat frames. The "flap" (there are
no wings) is reinterpreted as the aurora beams rippling like curtains across
the 4 base wing poses — a coherent chroma PHASE travels up each beam frame-to
-frame so the crown shimmers — plus a small ear-flick on the up-pose.

Round-2 chroma-first rebuild (art-director ITERATE on v4 LYRE BEAMS):
  * The beam MASS is saturated aurora (violet #7A5CFF / green #3DF2C0); pure
    white is reserved for the tip-stars and a thin 1px hot centerline only, so
    the crown keeps a chroma read when composited on a bright-day gradient.
  * A 1-2px deep-navy #1E2A3A halo is baked around every ribbon so the glow
    separates from a light sky in every biome (the day-sky insurance).
  * Exactly ONE short forward brow-tine per beam, low on the arc, flips the
    read from "lyre/horns" to "antlers" without muddying the silhouette.
  * The two arcs hold a clear negative gap as they sweep inward (no fused
    blob) and their spread is pulled in so the tips stay inside the 64px
    canvas through the full dive rotation.

Contract mirrors game/animal_skins.py so this lifts straight in:

  * `build_aurora_stag(wing_angle_deg) -> pygame.Surface`  one flat frame on a
    64x84 SRCALPHA canvas. Body mass centred at (32,44); head near (44,34);
    the rack reaches UP into the top ~24px of headroom.
  * `get_aurora_stag = _make_prebuilt_skin(build_aurora_stag)` — cached
    `(frame_idx, tilt_deg) -> Surface` getter.
  * `BUILDERS = {"skin_aurora_stag": get_aurora_stag}` registry at the bottom.

Body anchoring: collision is a fixed 14px circle at the body centre, so the
body mass stays pinned at (32,44) even though the antlers are tall — the rack
never drags the body off-centre.
"""
import math
import pygame

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


# ── aurora palette (cool full-spectrum violet↔green; NO pink/gold) ───────────
BODY      = (30, 42, 58)        # deep slate-blue
BODY_D    = (16, 24, 36)        # darker body for the fierce legendary read
BODY_DD   = (10, 16, 26)
BODY_H    = (58, 78, 104)
MUZZLE    = (10, 14, 22)
AUR_GREEN = (61, 242, 192)      # #3DF2C0  — saturated beam chroma
AUR_VIO   = (122, 92, 255)      # #7A5CFF  — saturated beam chroma
NAVY_HALO = (30, 42, 58)        # #1E2A3A  — dark contrast halo (day insurance)
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


def _eye(surf, cx, cy, r, *, iris=(14, 16, 24)):
    pygame.draw.circle(surf, (250, 250, 245), (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 2))
    pygame.draw.circle(surf, (255, 255, 255), (cx - r // 3, cy - r // 3),
                       max(1, r // 3))


def _flap(angle_deg):
    """0..1 'up' factor; _WING_ANGLES runs 50→-40 (down→up)."""
    return (angle_deg + 40) / 90.0


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _glow_dot(surf, color, pos, r, alpha=120):
    """Soft additive glow blob baked into the frame (no live particles)."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for rr in range(r, 0, -1):
        a = int(alpha * (1 - rr / r) ** 1.4)
        pygame.draw.circle(g, (*color, a), (r, r), rr)
    surf.blit(g, (int(pos[0] - r), int(pos[1] - r)),
              special_flags=pygame.BLEND_RGBA_ADD)


def _star(surf, pos, size, glow=AUR_GREEN):
    """The signature floating star: a tight WHITE 4-point star with a 1px
    coloured bloom, sitting on a small coloured halo. Kept crisp and bright so
    it survives the rotated dive frame at 40px — this is the legendary tell."""
    x, y = int(round(pos[0])), int(round(pos[1]))
    # soft coloured halo so the star reads as a light source, not a dot.
    _glow_dot(surf, glow, (x, y), size * 2 + 2, alpha=120)
    # 1px coloured bloom one pixel out from the white arms (the chroma rim).
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        pygame.draw.line(surf, (*glow, 220),
                         (x + dx * (size + 1), y + dy * (size + 1)),
                         (x + dx, y + dy), 1)
    # crisp white 4-point arms + hot core.
    pygame.draw.line(surf, STAR, (x - size, y), (x + size, y), 1)
    pygame.draw.line(surf, STAR, (x, y - size), (x, y + size), 1)
    pygame.draw.circle(surf, STAR, (x, y), max(1, size // 2 + 1))


def _aurora_ribbon(surf, pts, width, phase, *, hot=True):
    """A flowing aurora ribbon along a poly-spine.

    Drawn in THREE baked layers per segment so the beam owns a chroma read on
    a light sky AND separates from it:
      1. a deep-navy halo 1-2px wider than the core (dark contrast rim);
      2. the SATURATED violet↔green core (the beam mass — never near-white);
      3. an optional thin 1px white hot centerline (the only white in a beam).

    `phase` (0..1) slides the violet↔green blend up the ribbon frame-to-frame
    so a coherent chroma wave travels the beam — the baked-in 'ripple'."""
    n = len(pts)
    for i in range(n - 1):
        # coherent chroma phase travelling up the beam (not per-pixel jitter).
        t = (i / max(1, n - 2) + phase) % 1.0
        mix = 0.5 - 0.5 * math.cos(t * math.tau)        # smooth violet↔green
        col = _lerp(AUR_VIO, AUR_GREEN, mix)
        # taper width toward the tip.
        w = max(2, int(width * (1 - 0.45 * i / max(1, n - 1))))
        # 1) dark navy halo (baked day-sky separation).
        pygame.draw.line(surf, NAVY_HALO, pts[i], pts[i + 1], w + 3)
        # 2) saturated chroma core.
        pygame.draw.line(surf, col, pts[i], pts[i + 1], w)
        # 3) thin hot centerline — the only white inside the beam mass.
        if hot and w >= 3:
            pygame.draw.line(surf, (235, 245, 255), pts[i], pts[i + 1], 1)


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


def _deer_head(surf, body, body_d, body_h):
    """Noble deer head/forebody anchored at the body centre.

    Returns the (skull-left, skull-right) ear-base x's so the rack grows from
    a consistent skull."""
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
    snout = [(HCX + 4, HCY - 4), (HCX + 15, HCY + 1),
             (HCX + 13, HCY + 6), (HCX + 3, HCY + 6)]
    pygame.draw.polygon(surf, body, snout)
    pygame.draw.polygon(surf, body_d, snout, 1)
    pygame.draw.circle(surf, MUZZLE, (HCX + 13, HCY + 2), 2)   # nose
    _aaellipse(surf, body_h, (HCX - 3, HCY - 2), 4, 3)
    # Fierce regal almond eye + stern brow.
    _eye(surf, HCX + 2, HCY - 1, 3)
    pygame.draw.line(surf, body_d, (HCX - 1, HCY - 3), (HCX + 4, HCY - 3), 1)
    return (HCX - 6, HCX + 1)


# ═════════════════════════════════════════════════════════════════════════════
# AURORA STAG · LYRE-BEAM production build
#   Two bold curving lyre beams sweeping out, up, then inward to a held gap —
#   minimal branching for maximum silhouette. Each beam is a saturated
#   violet↔green aurora ribbon with a baked navy halo, ONE forward brow-tine
#   low on the arc (the antler tell), and a big 4-point star crowning its tip.
#   A coherent chroma phase travels up the beams across the 4 frames; the ears
#   flick on the up-pose.
# ═════════════════════════════════════════════════════════════════════════════
def build_aurora_stag(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)                  # 0 down → 1 up
    phase = f * 0.5                            # chroma wave phase per frame

    skull_l, skull_r = _deer_head(surf, BODY_D, BODY_DD, BODY_H)
    flick = max(0.0, (f - 0.5) * 2)
    _ear(surf, (skull_l - 1, HCY - 4), -1, flick, BODY_D, BODY_DD)
    _ear(surf, (skull_r + 2, HCY - 5), +1, flick, BODY_D, BODY_DD)

    # Two lyre beams. Spread is pulled in (belly 13px) so the arc tips stay
    # inside the 64px canvas through the full dive rotation. The inward sweep
    # is CAPPED well short of centre — each tip ends ~4px off the midline — so
    # the two beams hold a clear ≥2px negative gap instead of fusing into the
    # closed ring the first cut read as.
    for sgn, root in ((-1, (skull_l + 1, HCY - 5)), (+1, (skull_r, HCY - 5))):
        rx, ry = root
        beam = []
        steps = 8
        for i in range(steps + 1):
            t = i / steps
            # outward belly then a gentle inward lean: sin gives the arc belly,
            # a small late pull leans the upper beam toward — but not across —
            # centre, leaving the tips splayed apart at the crown.
            belly = 13 * math.sin(t * math.pi * 0.78)
            inward = 4.5 * max(0.0, (t - 0.6)) / 0.4     # capped late lean
            bx = rx + sgn * (3 + belly - inward)
            by = ry - 30 * t
            beam.append((bx, by))
        _aurora_ribbon(surf, beam, 5, phase)

        # ONE short forward brow-tine, low on the arc — the antler tell. It
        # juts FORWARD/up off the outer face of the beam so it reads as a tine,
        # not as more of the arc.
        bx0, by0 = beam[2]
        brow = [(bx0, by0 + 1),
                (bx0 + sgn * 6, by0 - 1),
                (bx0 + sgn * 9, by0 - 6)]
        _aurora_ribbon(surf, brow, 3, phase, hot=False)
        _star(surf, brow[-1], 2, glow=AUR_GREEN)

        # Big crowning 4-point tip-star — the signature.
        _star(surf, beam[-1], 4, glow=(AUR_VIO if sgn < 0 else AUR_GREEN))

    # Slim deer legs hinting the hooved body.
    for fx in (28, 37):
        pygame.draw.line(surf, BODY_DD, (fx, BCY + 13), (fx, BCY + 19), 2)
        pygame.draw.line(surf, MUZZLE, (fx, BCY + 19), (fx, BCY + 21), 2)
    return surf


get_aurora_stag = _make_prebuilt_skin(build_aurora_stag)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry (lifts into game/animal_skins.py as "skin_aurora_stag").
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_aurora_stag": get_aurora_stag,
}
