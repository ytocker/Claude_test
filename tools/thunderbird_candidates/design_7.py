"""BALL LIGHTNING — a hovering sphere of white-yellow charge that has just
barely organized itself into bird form.

The silhouette is dominated by a glowing ORB, not spread wings. A layered
concentric-circle body reads as a heavy fireball; the "bird" is only implied
by a smaller satellite head-orb fused top-right, a flame crest, and short
throbbing bolt-stubs where wings would be. Surface arcs skitter across the
sphere while a pair of breaching arcs shoot past the rim so electricity lands
in the SILHOUETTE (the true ball-lightning read at 40px). The read leans on
VALUE, not line: a dark amber shell separates the orb from a bright day sky,
the head carries its own dark rim so it reads as a separate satellite object,
and the body stays predominantly Fireball Yellow with white as the single
hottest point.
"""
import math
import random

import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
# Head pushed further out (top-right) so it reads as a SEPARATE satellite orb
# from the body at 40px, not a bump on the sphere.
HCX, HCY = 46, 32
CROWN_Y = 22

# Palette
NUCLEUS = (255, 255, 255)     # #FFFFFF white-hot core
FIREBALL = (255, 212, 0)      # #FFD400 dominant fireball yellow
EMBER = (255, 160, 0)         # #FFA000 ember gold
SCORCH = (255, 106, 0)        # #FF6A00 scorch orange
CORONA = (255, 243, 176)      # #FFF3B0 thin corona

# Concentric body layers: (radius, colour). Outer amber-dark ring is the
# value anchor on bright day; inner near-white/white are the night tell.
# The near-white layer is shrunk (r=5) and warmed so more Fireball Yellow
# shows in the mid-tones; white is the single hottest POINT, not the body.
_BODY_LAYERS = (
    (21, (40, 15, 0)),
    (18, (255, 160, 0)),
    (14, (255, 212, 0)),
    (10, (255, 235, 90)),
    (5, (255, 240, 140)),
    (3, (255, 255, 255)),
)


def _flap(a):
    """0 at wings-up (angle -40) … 1 at wings-down power stroke (angle 50)."""
    return (a + 40) / 90.0


def _add_glow(surf, cx, cy, r, color, alpha):
    """Additive radial puff so orb layers read as light, not paint. Stacked
    fading rings avoid a hard edge and let the ball bloom into the sky."""
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for k in range(r, 0, -1):
        a = int(alpha * (k / r) ** 2)
        pygame.draw.circle(g, (*color, a), (r * 2, r * 2), (r - k) + 2)
    surf.blit(g, (cx - r * 2, cy - r * 2), special_flags=pygame.BLEND_RGBA_ADD)


def _orb_stack(surf, cx, cy, layers, bump=0):
    """Draw a concentric filled-circle stack. The dark outer ring is drawn
    opaque (value anchor); the hot inner rings are additive so they glow."""
    for i, (r, col) in enumerate(layers):
        rr = r + bump
        if i == 0:
            # Solid amber-dark shell — the load-bearing value ring.
            pygame.draw.circle(surf, col, (cx, cy), rr)
        else:
            _add_glow(surf, cx, cy, rr, col, 235)


def _surface_arc(surf, cx, cy, seed, orb_r, breach=False):
    """A short electric arc skittering across the sphere surface. Reseeded per
    flap pose so the arcs crawl frame to frame (deterministic but varied).

    A breaching arc originates AT the rim and shoots outward past it, so the
    electricity lands in the SILHOUETTE at 40px — the core ball-lightning read
    that pure surface skitter can't deliver."""
    random.seed(seed)
    ang = random.uniform(-math.pi, math.pi)
    if breach:
        # Start on the rim; radiate straight outward and overshoot 8-10px so
        # the spike pokes through the dark rim circle drawn later.
        rad = orb_r * 0.9
        heading = ang + random.uniform(-0.35, 0.35)
        length = orb_r + random.uniform(8, 10)
    else:
        # Anchor somewhere on the visible upper hemisphere, run tangentially.
        ang = random.uniform(-math.pi * 0.95, math.pi * 0.05)
        rad = random.uniform(orb_r * 0.45, orb_r * 0.85)
        length = random.uniform(10, 15)
        heading = ang + math.pi / 2 + random.uniform(-0.6, 0.6)
    ax = cx + math.cos(ang) * rad
    ay = cy + math.sin(ang) * rad
    jag = random.uniform(2.5, 5.0)
    pts = []
    steps = 4
    for s in range(steps + 1):
        f = s / steps
        px = ax + math.cos(heading) * length * f
        py = ay + math.sin(heading) * length * f
        # Zig perpendicular to the heading for the lightning kink.
        z = jag * math.sin(f * math.pi * 2 + seed) * (1 - abs(f - 0.5) * 1.2)
        px += math.cos(heading + math.pi / 2) * z
        py += math.sin(heading + math.pi / 2) * z
        pts.append((px, py))
    # Outer gold halo under a bright white core.
    pygame.draw.lines(surf, (255, 220, 50), False,
                      [(round(x), round(y)) for x, y in pts], 3)
    pygame.draw.lines(surf, NUCLEUS, False,
                      [(round(x), round(y)) for x, y in pts], 1)


def _bolt_stub(surf, x0, y0, x1, y1, seed, width):
    """A short, thick, blunt bolt where a wing would be. It THROBS in/out with
    the stroke rather than sweeping — reinforces the orb-dominant silhouette."""
    random.seed(seed)
    pts = []
    steps = 3
    for s in range(steps + 1):
        f = s / steps
        px = x0 + (x1 - x0) * f
        py = y0 + (y1 - y0) * f
        if 0 < s < steps:
            px += random.uniform(-3, 3)
            py += random.uniform(-2, 2)
        pts.append((round(px), round(py)))
    pygame.draw.lines(surf, EMBER, False, pts, width + 2)
    pygame.draw.lines(surf, FIREBALL, False, pts, width)
    pygame.draw.lines(surf, CORONA, False, pts, max(1, width - 2))


def _build_frame(wing_angle_deg) -> pygame.Surface:
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _flap(wing_angle_deg)          # 1 on the down-stroke power frame
    down = wing_angle_deg == 50             # brightest full-orb pulse frame
    bump = 2 if down else 0                 # whole-orb brightness pulse

    # --- Atmosphere: a broad additive bloom behind everything so the orb
    # bleeds light into the sky.
    bloom = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.circle(bloom, (255, 200, 0, 40), (BCX, BCY), 28)
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # --- Tail: fading ember dots streaming out on a shallow down-left diagonal
    # so they read as a comet trail, not a vertical handle under the orb. The
    # underside is deliberately kept clear (no talon stack) — one element.
    for i, (dx, dy, r, a) in enumerate((
            (-10, 8, 4, 210), (-18, 14, 3, 160),
            (-26, 18, 2, 110), (-32, 21, 1, 70))):
        _add_glow(surf, BCX + dx, BCY + dy, r + 1, SCORCH, a)
        pygame.draw.circle(surf, FIREBALL, (BCX + dx, BCY + dy), r)

    # --- Wings: blunt bolt-stubs that THROB at silhouette scale. Down-stroke
    # shoves them well past the rim (reach ~25, thick); up-stroke sucks them
    # inside the corona (reach ~9, thin). The delta must pop at 40px, so both
    # reach AND width swing with the stroke.
    reach = 9 + int(strike * 16)            # 9 … 25 (past the r=21 rim on down)
    wing_w = 3 + int(round(strike * 3))     # 3 … 6
    for side in (-1, 1):
        # Origin follows the throb inward so up-stroke stubs hide in the corona.
        sx = BCX + side * (7 + int(strike * 7))
        sy = BCY
        # Two strokes fanning out per side.
        for k, spread in enumerate((-6, 6)):
            ex = BCX + side * reach
            ey = BCY + spread - int((1 - strike) * 4)
            _bolt_stub(surf, sx, sy, ex, ey,
                       seed=int(wing_angle_deg) + side * 10 + k, width=wing_w)

    # --- Body: the BIG dominant orb.
    _orb_stack(surf, BCX, BCY, _BODY_LAYERS, bump=bump)

    # --- Surface arcs: 3 skitter across the orb face. Reseeded per pose so
    # they crawl frame to frame. (The 2 breaching arcs are drawn LAST, after
    # the rim, so their spikes poke through it into the silhouette.)
    for i in range(3):
        _surface_arc(surf, BCX, BCY, seed=int(wing_angle_deg) + i, orb_r=18)

    # --- Head: a smaller satellite orb top-right. A dark crescent on its
    # body-side plus a thin dark rim opens a VALUE gap so the head reads as a
    # SEPARATE object from the body at 40px, not a bulge on the sphere.
    pygame.draw.circle(surf, (50, 25, 0, 200), (HCX - 3, HCY + 4), 8, 2)
    _add_glow(surf, HCX, HCY, 10, EMBER, 235)
    _add_glow(surf, HCX, HCY, 7, FIREBALL, 235)
    _add_glow(surf, HCX, HCY, 4, CORONA, 235)
    _add_glow(surf, HCX, HCY, 2, NUCLEUS, 250)
    pygame.draw.circle(surf, (255, 220, 90), (HCX, HCY), 6)
    pygame.draw.circle(surf, NUCLEUS, (HCX, HCY), 2)
    # Thin dark rim locks the head as its own silhouette on bright day.
    pygame.draw.circle(surf, (40, 15, 0, 230), (HCX, HCY), 8, 1)

    # Two spark-eyes with a glow behind.
    for ex_off in (-3, 3):
        ex, ey = HCX + ex_off, HCY - 1
        _add_glow(surf, ex, ey, 3, FIREBALL, 200)
        pygame.draw.circle(surf, (255, 255, 120), (ex, ey), 2)
        pygame.draw.circle(surf, NUCLEUS, (ex, ey), 1)

    # --- Crest: one flame-like bolt lick curling up from the head crown.
    crest = [
        (HCX - 2, HCY - 8),
        (HCX + 2, CROWN_Y + 3),
        (HCX - 3, CROWN_Y - 3),
        (HCX + 1, CROWN_Y - 8),
    ]
    pygame.draw.lines(surf, EMBER, False, crest, 4)
    pygame.draw.lines(surf, FIREBALL, False, crest, 2)
    pygame.draw.lines(surf, CORONA, False, crest, 1)

    # (No talons — the underside is left to the comet tail alone so the orb
    # doesn't sprout a "matchstick handle" of stacked elements beneath it.)

    # --- Dark rim circle around the outer orb. Darker + more opaque than R1 so
    # the ball holds its value against a pale-blue day sky and never dissolves.
    pygame.draw.circle(surf, (40, 15, 0, 240), (BCX, BCY), 21 + bump, 2)

    # --- Breaching arcs, drawn LAST so their spikes poke THROUGH the rim into
    # the silhouette — the core ball-lightning read at 40px. Two per pose,
    # reseeded so they jitter frame to frame.
    for i in range(2):
        _surface_arc(surf, BCX, BCY, seed=int(wing_angle_deg) * 7 + i * 31,
                     orb_r=20 + bump, breach=True)

    return surf


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
