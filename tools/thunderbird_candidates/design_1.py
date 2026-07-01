"""STORM HERALD — thunderbird skin candidate (Design 1, exploration only).

A hunched raptor whose body reads as a stacked thundercloud: storm-navy
ovals darkening toward the belly, a single bold zig-zag bolt cracking down
the chest, torn-cumulus wing edges, and a lone hot-white eye that is the
brightest survivor of the 40px shrink. The electric mood peaks on the
power-flap frame (frame 0, wing_angle=50), where a spark bridges the
wingtips; the down-stroke frame reads as the thunderclap with its branch
arcs brightest. Scratch builder — NOT registered in store_skins.BUILDERS.
"""
import math
import pygame
from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y = 24

# Storm palette.
NAVY  = (27, 36, 54)     # #1B2436 storm-navy — deepest cloud / belly
GREY  = (58, 74, 99)     # #3A4A63 cloud-grey — mid mass
RAIN  = (143, 180, 232)  # #8FB4E8 rain-blue — cool rim light
BOLT  = (234, 244, 255)  # #EAF4FF bolt-white — lightning + glow
SPARK = (255, 246, 200)  # #FFF6C8 spark-core — hottest points


# The wing angle carries the flap phase: 50 is the top of the power-flap,
# -40 the bottom of the down-stroke (the thunderclap). Mapping it to 0..1
# lets the branch arcs and spark bridge pulse with the motion instead of
# being static overlays.
def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    return 1.0 - _flap(a)


def _soft_glow(radius, color, alpha):
    """A radial-ish soft disc built from stacked fading rings — the blue-white
    storm halo. Cheap and cached-by-caller, so per-ring cost is fine."""
    size = radius * 2
    g = pygame.Surface((size, size), pygame.SRCALPHA)
    steps = max(6, radius // 2)
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(radius * t)
        a = int(alpha * (1.0 - t) ** 1.6)
        pygame.draw.circle(g, (*color, a), (radius, radius), r)
    return g


def _bolt_line(surf, p0, p1, color, width, jag, seed):
    """A jagged lightning segment between two points — the chest bolt and the
    branch arcs. Deterministic zig from a seed so frames stay stable."""
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / length, dx / length  # perpendicular
    segs = 4
    pts = []
    for i in range(segs + 1):
        t = i / segs
        # Pseudo-random but deterministic lateral kick.
        k = math.sin(seed * 12.9898 + i * 78.233) * 43758.5453
        off = (k - math.floor(k) - 0.5) * jag * (1.0 if 0 < i < segs else 0.0)
        px = x0 + dx * t + nx * off
        py = y0 + dy * t + ny * off
        pts.append((px, py))
    pygame.draw.lines(surf, color, False, pts, width)
    return pts


def _torn_wing(angle_deg, phase):
    """A ragged cumulus wing: a torn-edged storm-cloud polygon with a cool
    rain-blue rim and thin branching arcs that brighten on the down-stroke."""
    w = pygame.Surface((54, 54), pygame.SRCALPHA)
    cx, cy = 26, 28

    # Torn primary silhouette — a bumpy fan so the trailing edge reads as
    # ragged storm cloud rather than a clean feather.
    outer = [
        (24, 24), (40, 15), (46, 20), (49, 30), (45, 33),
        (48, 38), (40, 40), (36, 45), (30, 41), (24, 44), (20, 36),
    ]
    pygame.draw.polygon(w, GREY, outer)
    # Darker underside wedge for volume.
    pygame.draw.polygon(w, NAVY, [(24, 24), (30, 41), (24, 44), (20, 36)])
    # Cool rim light along the leading edge.
    pygame.draw.lines(w, RAIN, False, [(24, 24), (40, 15), (46, 20), (49, 30)], 2)

    # Branching charge arcs — brightest as the wing slams down (thunderclap).
    arc_glow = int(70 + 170 * phase)
    arc_col = (BOLT[0], BOLT[1], BOLT[2], arc_glow)
    a_surf = pygame.Surface((54, 54), pygame.SRCALPHA)
    _bolt_line(a_surf, (26, 22), (44, 22), arc_col, 1, 3.0, 1.0)
    _bolt_line(a_surf, (24, 30), (46, 31), arc_col, 1, 3.5, 2.0)
    _bolt_line(a_surf, (26, 37), (42, 39), arc_col, 1, 3.0, 3.0)
    w.blit(a_surf, (0, 0))

    return pygame.transform.rotate(w, angle_deg)


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    phase = _flap(wing_angle_deg)      # 0 at bottom, 1 at top of stroke
    strike = _strike(wing_angle_deg)   # inverse — peaks on the down-stroke

    # Soft blue-white storm halo behind the whole body.
    halo = _soft_glow(30, RAIN, 90)
    surf.blit(halo, halo.get_rect(center=(BCX, BCY + 2)))

    # --- Far wing (behind the body) ---
    far = _torn_wing(wing_angle_deg * 0.75, strike)
    surf.blit(far, far.get_rect(center=(BCX - 6, BCY - 6)))

    # --- Body: three stacked storm-cloud ovals, darker toward the belly ---
    _aaellipse(surf, NAVY, (BCX + 1, BCY + 10), 17, 11)   # belly (darkest)
    _aaellipse(surf, GREY, (BCX, BCY + 2), 18, 13)        # mid mass
    _aaellipse(surf, (72, 90, 118), (BCX - 1, BCY - 6), 15, 10)  # upper, lit
    # Cool rim highlight where storm light catches the top of the cloud body.
    rim = pygame.Surface((30, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(rim, (*RAIN, 150), rim.get_rect())
    surf.blit(rim, (BCX - 15, BCY - 14))

    # --- Talons: forked arc-bolts with a spark glow underneath ---
    for tx in (BCX - 6, BCX + 6):
        spk = _soft_glow(6, SPARK, 120)
        surf.blit(spk, spk.get_rect(center=(tx, BCY + 22)))
        pygame.draw.lines(surf, RAIN, False,
                          [(tx - 3, BCY + 17), (tx, BCY + 21), (tx - 2, BCY + 24)], 2)
        pygame.draw.lines(surf, RAIN, False,
                          [(tx + 3, BCY + 17), (tx, BCY + 21), (tx + 2, BCY + 24)], 2)
        pygame.draw.line(surf, BOLT, (tx, BCY + 18), (tx, BCY + 22), 1)

    # --- Chest bolt: one bold zig-zag cracking down the front ---
    bolt_pts = [
        (BCX + 2, BCY - 9), (BCX - 3, BCY - 1), (BCX + 2, BCY - 1),
        (BCX - 4, BCY + 11), (BCX + 4, BCY - 2), (BCX - 1, BCY - 2),
        (BCX + 4, BCY - 9),
    ]
    # Glow underlay then hot core so the bolt blooms against the dark cloud.
    glow_bolt = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(glow_bolt, (*BOLT, 70), bolt_pts)
    glow_bolt = pygame.transform.smoothscale(
        pygame.transform.smoothscale(glow_bolt, (COMPOSITE_W // 2, COMPOSITE_H // 2)),
        (COMPOSITE_W, COMPOSITE_H))
    surf.blit(glow_bolt, (0, 0))
    pygame.draw.polygon(surf, BOLT, bolt_pts)
    pygame.draw.polygon(surf, SPARK, [
        (BCX + 2, BCY - 8), (BCX - 1, BCY - 2), (BCX + 1, BCY - 2), (BCX - 2, BCY + 8),
    ])

    # --- Near wing (over the body) ---
    near = _torn_wing(wing_angle_deg, strike)
    surf.blit(near, near.get_rect(center=(BCX + 4, BCY - 8)))

    # --- Spark bridge between wingtips on the power-flap frame ---
    if phase > 0.85:
        rad = math.radians(wing_angle_deg)
        tip = 22
        lx = BCX + 4 - math.cos(rad) * tip - 8
        ly = BCY - 8 - math.sin(rad) * tip
        rx = BCX + 4 + math.cos(rad) * tip
        ry = BCY - 8 - math.sin(rad) * tip
        _bolt_line(surf, (lx, ly), (rx, ry), (*SPARK, 230), 2, 6.0, 9.0)
        _bolt_line(surf, (lx, ly), (rx, ry), (*BOLT, 160), 1, 9.0, 4.0)

    # --- Head: hunched, broad — a dark storm-cloud skull ---
    _aaellipse(surf, GREY, (HCX, HCY + 1), 11, 10)
    _aaellipse(surf, (72, 90, 118), (HCX - 1, HCY - 3), 8, 6)  # lit crown
    pygame.draw.arc(surf, RAIN, pygame.Rect(HCX - 11, HCY - 9, 20, 18),
                    0.4, 2.6, 2)  # cool rim on the crown

    # --- Crest: three back-swept jagged bolt-spikes, tips electric white ---
    for i, (base_x, base_y, tip_x, tip_y) in enumerate((
        (HCX - 4, CROWN_Y + 2, HCX - 14, CROWN_Y - 8),
        (HCX,     CROWN_Y,     HCX - 8,  CROWN_Y - 12),
        (HCX + 4, CROWN_Y + 2, HCX - 1,  CROWN_Y - 11),
    )):
        mid_x = (base_x + tip_x) / 2 + 2
        mid_y = (base_y + tip_y) / 2
        pygame.draw.polygon(surf, GREY, [
            (base_x - 2, base_y + 2), (mid_x, mid_y), (tip_x, tip_y),
            (mid_x + 2, mid_y + 1), (base_x + 2, base_y + 2),
        ])
        # Electric-white tip.
        pygame.draw.line(surf, BOLT, (mid_x, mid_y), (tip_x, tip_y), 2)
        pygame.draw.circle(surf, SPARK, (int(tip_x), int(tip_y)), 1)

    # --- Beak: hooked raptor, slate with a cool gloss ---
    beak_pts = [(HCX + 8, HCY - 2), (HCX + 15, HCY + 1), (HCX + 11, HCY + 5),
                (HCX + 7, HCY + 3)]
    pygame.draw.polygon(surf, (36, 46, 66), beak_pts)
    pygame.draw.polygon(surf, NAVY, beak_pts, 1)
    pygame.draw.line(surf, RAIN, (HCX + 8, HCY - 1), (HCX + 13, HCY + 1), 1)

    # --- Eye: single hot-white glowing point (the brightest survivor of 40px) ---
    eye = (HCX + 2, HCY)
    eglow = _soft_glow(9, BOLT, 150)
    surf.blit(eglow, eglow.get_rect(center=eye))
    pygame.draw.circle(surf, NAVY, eye, 4)
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
