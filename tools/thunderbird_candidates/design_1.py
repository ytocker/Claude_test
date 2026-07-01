"""STORM HERALD — thunderbird skin candidate (Design 1, exploration only).

An angular storm-raptor, NOT a round cloud-blob. The body leans forward
nose-down like a diving hawk; the beak juts past the head and a wing tip
pierces the round belly outline so the silhouette reads as a raptor, not
a potato. A thick double-stroked zig-zag bolt is the identity anchor — it
sits over the darkest belly patch with a hot spark core so it survives the
40px shrink. Two bold zig-spikes (not antenna hair) crown the head; compact
talons tuck under the body. No soft body halo — the silhouette carries the
form via an internal near-black→cloud-cap→rain-blue value ramp and a thin
rim-light on the back arc. Scratch builder — NOT registered in BUILDERS.
"""
import math
import pygame
from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 45, 33
CROWN_Y = 23

# Storm palette — wide value spread so the cloud-body has form at 40px.
BELLY = (14, 21, 36)      # #0E1524 deep-belly — darkest, bolt sits here
GREY  = (58, 74, 99)      # #3A4A63 cloud-grey — lower mid mass
CAP   = (90, 110, 140)    # #5A6E8C cloud-cap — top mass, distinctly lighter
RAIN  = (143, 180, 232)   # #8FB4E8 rain-blue — cool rim light
KEY   = (143, 180, 232)   # back-arc key-light rim
BOLT  = (234, 244, 255)   # #EAF4FF bolt-white — lightning
SPARK = (255, 246, 200)   # #FFF6C8 spark-core — hottest points
BEAK  = (36, 46, 66)      # slate beak


# The wing angle carries the flap phase: 50 is the top of the power-flap,
# -40 the bottom of the down-stroke (the thunderclap). Mapping it to 0..1
# lets the branch arcs and spark bridge pulse with the motion.
def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _bolt_line(surf, p0, p1, color, width, jag, seed):
    """A jagged lightning segment between two points — the branch arcs and
    spark bridge. Deterministic zig from a seed so frames stay stable."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length  # perpendicular
    segs = 4
    pts = []
    for i in range(segs + 1):
        t = i / segs
        k = math.sin(seed * 12.9898 + i * 78.233) * 43758.5453
        off = (k - math.floor(k) - 0.5) * jag * (1.0 if 0 < i < segs else 0.0)
        px = x0 + dx * t + nx * off
        py = y0 + dy * t + ny * off
        pts.append((px, py))
    pygame.draw.lines(surf, color, False, pts, width)
    return pts


def _torn_wing(angle_deg, phase, near):
    """A ragged cumulus wing that ends in a sharp raptor tip. `near` wings get
    a longer piercing point so the tip breaks the round body outline."""
    w = pygame.Surface((60, 60), pygame.SRCALPHA)

    # Torn primary silhouette. The trailing tip (last pts) is a sharp spike so
    # the wing pierces the body's circular edge instead of rounding it off.
    tip_reach = 8 if near else 3
    outer = [
        (26, 24), (42, 14), (48, 19), (51, 29),
        (54 + tip_reach, 33),  # sharp piercing tip
        (47, 36), (49, 41), (40, 42), (36, 47),
        (30, 42), (24, 45), (20, 37),
    ]
    pygame.draw.polygon(w, GREY, outer)
    # Darker underside wedge for volume.
    pygame.draw.polygon(w, BELLY, [(26, 24), (30, 42), (24, 45), (20, 37)])
    # Cap-lit upper leading area.
    pygame.draw.polygon(w, CAP, [(26, 24), (42, 14), (48, 19), (44, 24)])
    # Cool rim light along the leading edge.
    pygame.draw.lines(w, RAIN, False,
                      [(26, 24), (42, 14), (48, 19), (51, 29)], 2)

    # Branching charge arcs — brightest as the wing slams down (thunderclap).
    arc_glow = int(70 + 170 * phase)
    arc_col = (BOLT[0], BOLT[1], BOLT[2], arc_glow)
    a_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    _bolt_line(a_surf, (28, 22), (48, 22), arc_col, 1, 3.0, 1.0)
    _bolt_line(a_surf, (26, 31), (50, 32), arc_col, 1, 3.5, 2.0)
    w.blit(a_surf, (0, 0))

    return pygame.transform.rotate(w, angle_deg)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    phase = _flap(wing_angle_deg)      # 0 at bottom, 1 at top of stroke
    strike = _strike(wing_angle_deg)   # inverse — peaks on the down-stroke

    # --- Far wing (behind the body) ---
    far = _torn_wing(wing_angle_deg * 0.75, strike, near=False)
    surf.blit(far, far.get_rect(center=(BCX - 8, BCY - 6)))

    # --- Body: forward-leaning storm-cloud mass. The ellipses step in value
    # from near-black belly up to a lighter cloud-cap so the round form has
    # internal modelling at 40px. A ~5° nose-down lean gives it raptor thrust:
    # the upper mass is pushed toward the beak, the belly hangs back.
    _aaellipse(surf, BELLY, (BCX + 3, BCY + 11), 17, 10)   # belly (darkest)
    _aaellipse(surf, GREY, (BCX + 1, BCY + 3), 18, 12)     # lower mid mass
    _aaellipse(surf, CAP, (BCX + 3, BCY - 6), 15, 9)       # upper, lit, nosed fwd
    # Key-light rim on the back-top arc (the storm light catching the cloud).
    pygame.draw.arc(surf, KEY, pygame.Rect(BCX - 16, BCY - 16, 34, 22),
                    0.7, 2.5, 2)

    # --- Compact talons tucked under the belly (no floating "X") ---
    for tx, curl in ((BCX - 3, -1), (BCX + 5, 1)):
        ty = BCY + 20
        pygame.draw.polygon(surf, BEAK, [
            (tx, ty), (tx + curl * 3, ty + 4),
            (tx + curl, ty + 5), (tx - curl, ty + 2),
        ])
        pygame.draw.line(surf, RAIN, (tx, ty), (tx + curl * 3, ty + 4), 1)

    # --- Chest bolt: the identity anchor. Thick double-stroked zig-zag over
    # the darkest belly patch, with a hot spark core. Kept visible on every
    # frame (including the f3 down-stroke) so it never gets buried.
    bolt_pts = [
        (BCX + 3, BCY - 10), (BCX - 6, BCY - 1), (BCX + 2, BCY - 1),
        (BCX - 7, BCY + 13), (BCX + 6, BCY - 3), (BCX - 2, BCY - 3),
        (BCX + 7, BCY - 10),
    ]
    pygame.draw.lines(surf, BOLT, False, bolt_pts, 3)
    # Hot spark core down the centre of the zig.
    core_pts = [
        (BCX + 3, BCY - 9), (BCX - 3, BCY - 2), (BCX + 1, BCY - 2),
        (BCX - 3, BCY + 9),
    ]
    pygame.draw.lines(surf, SPARK, False, core_pts, 2)
    pygame.draw.circle(surf, (255, 255, 255), (BCX - 1, BCY + 1), 2)

    # --- Near wing (over the body) — its sharp tip pierces the body outline ---
    near = _torn_wing(wing_angle_deg, strike, near=True)
    surf.blit(near, near.get_rect(center=(BCX + 6, BCY - 8)))

    # --- Spark bridge between wingtips on the power-flap frame ---
    if phase > 0.85:
        rad = math.radians(wing_angle_deg)
        tip = 24
        lx = BCX + 6 - math.cos(rad) * tip - 8
        ly = BCY - 8 - math.sin(rad) * tip
        rx = BCX + 6 + math.cos(rad) * tip
        ry = BCY - 8 - math.sin(rad) * tip
        _bolt_line(surf, (lx, ly), (rx, ry), (*SPARK, 230), 2, 6.0, 9.0)
        _bolt_line(surf, (lx, ly), (rx, ry), (*BOLT, 160), 1, 9.0, 4.0)

    # --- Head: hunched storm-cloud skull, value-stepped like the body ---
    _aaellipse(surf, GREY, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, CAP, (HCX - 1, HCY - 3), 8, 6)  # lit crown
    pygame.draw.arc(surf, KEY, pygame.Rect(HCX - 11, HCY - 10, 20, 18),
                    0.6, 2.5, 2)  # cool rim on the crown

    # --- Crest: TWO bold zig-spikes reading as lightning prongs. A dark base
    # anchors each to the skull; a spark-white tip + dot electrifies it.
    for base_x, base_y, tip_x, tip_y in (
        (HCX - 5, CROWN_Y + 2, HCX - 15, CROWN_Y - 9),
        (HCX + 1, CROWN_Y,     HCX - 6,  CROWN_Y - 13),
    ):
        mid_x = (base_x + tip_x) / 2 + 3
        mid_y = (base_y + tip_y) / 2 + 1
        # Dark-based zig-zag prong body.
        pygame.draw.polygon(surf, GREY, [
            (base_x - 3, base_y + 3), (mid_x - 2, mid_y),
            (tip_x, tip_y), (mid_x + 2, mid_y + 1), (base_x + 3, base_y + 3),
        ])
        pygame.draw.polygon(surf, BELLY, [
            (base_x - 3, base_y + 3), (mid_x - 2, mid_y), (base_x, base_y + 1),
        ])
        # Electric-white tip + spark dot.
        pygame.draw.line(surf, BOLT, (mid_x, mid_y), (tip_x, tip_y), 2)
        pygame.draw.circle(surf, SPARK, (int(tip_x), int(tip_y)), 2)

    # --- Beak: hooked raptor, thrust ~4px past the head oval so it sticks out
    # directionally and breaks the round silhouette forward.
    beak_pts = [(HCX + 8, HCY - 3), (HCX + 18, HCY + 1), (HCX + 13, HCY + 6),
                (HCX + 7, HCY + 3)]
    pygame.draw.polygon(surf, BEAK, beak_pts)
    pygame.draw.polygon(surf, BELLY, beak_pts, 1)
    pygame.draw.line(surf, RAIN, (HCX + 8, HCY - 2), (HCX + 15, HCY + 1), 1)

    # --- Eye: single hot-white point (a bright survivor of 40px) ---
    eye = (HCX + 2, HCY)
    pygame.draw.circle(surf, BELLY, eye, 4)
    pygame.draw.circle(surf, BOLT, eye, 3)
    pygame.draw.circle(surf, SPARK, (eye[0], eye[1] - 1), 2)
    pygame.draw.circle(surf, (255, 255, 255), (eye[0], eye[1] - 1), 1)

    return surf


_cache = {}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    angle = _WING_ANGLES[frame_idx % len(_WING_ANGLES)]
    key = (frame_idx % len(_WING_ANGLES), round(tilt_deg / 3) * 3)
    if key not in _cache:
        _cache[key] = pygame.transform.rotozoom(
            _add_outline(_build_frame(angle)), key[1], 1.0)
    return _cache[key]
