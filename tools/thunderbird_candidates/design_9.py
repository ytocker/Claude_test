"""TESLA CROWN — a Tesla-coil thunderbird whose head is the coil terminal.

Inverts the usual bright-bird idea: the raptor body is a dark charcoal STAGE
so the true hero — a corona-arc halo of lightning leaping off the crown — reads
as the single brightest thing on screen. Arcs launch from a white-hot terminal
knob on the skull, curl 12-16px above the head, and land back on the shoulders,
forming a spark diadem. A 3-pass glow (wide add-halo, mid yellow, white core)
keeps every arc luminous down to 40px, where the crown of sparks + the terminal
knob are the whole identity. Wings and body stay near-black on purpose: contrast
is what makes the electric crown pop, so nothing below competes with it. On the
down-stroke frame the arcs bloom taller and brighter for a Tesla-snap pulse.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44
HCX, HCY = 44, 34
CROWN_Y = 24

# Charcoal STAGE — kept dark so the electric crown is the brightest thing.
BODY_SHADOW = (10, 12, 16)      # #0A0C10 — offset drop shadow
BODY_MAIN   = (26, 29, 38)      # #1A1D26 — charcoal shell
WING_DARK   = (20, 23, 30)      # #14171E — near-black wing panels
BEAK_DARK   = (40, 44, 52)      # #282C34 — beak charcoal
COOL_RIM    = (100, 120, 160)   # #6478A0 — subtle cool back-rim
LEAD_EDGE   = (80, 100, 140)    # #64648C-ish cool leading-edge highlight

# The electric crown — dominant values live here, not in the body.
COIL_YELLOW = (255, 232, 26)    # #FFE81A — dominant arc colour
CORONA_WHITE = (255, 255, 255)  # white-hot core
TERMINAL_GOLD = (255, 192, 26)  # #FFC01A — terminal knob body
OZONE_BLUE  = (127, 216, 255)   # #7FD8FF — single cool trace in the hottest arc


def _flap(a):
    return (a + 40) / 90.0


def _strike(a):
    # 1 on the down-stroke power frame (angle=50), 0 on wings-up (angle=-40).
    return _flap(a)


def _add_line(surf, color, p0, p1, w):
    """Additive stroke so overlapping arc glow accumulates into a bloom instead
    of flatly overwriting — the corona reads brighter where arcs cross."""
    layer = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.line(layer, color, p0, p1, w)
    surf.blit(layer, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _polyline(surf, color, pts, w, additive=False):
    for i in range(len(pts) - 1):
        if additive:
            _add_line(surf, color, pts[i], pts[i + 1], w)
        else:
            pygame.draw.line(surf, color, pts[i], pts[i + 1], w)


def _bezier(p0, p1, p2, steps=10):
    """Quadratic curve sampler — arcs are drawn as smooth polylines so the
    3-pass glow stacks cleanly along the same path."""
    out = []
    for s in range(steps + 1):
        t = s / steps
        u = 1 - t
        x = u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]
        y = u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]
        out.append((x, y))
    return out


def _corona_arc(surf, start, peak, land, bloom, hot=False):
    """One lightning arc drawn with the load-bearing 3-pass glow: a wide
    additive halo, a mid yellow body, then a white-hot core. ``bloom`` scales
    width/brightness so the down-stroke frame snaps harder. ``hot`` threads a
    single ozone-blue trace inside the very brightest arc."""
    pts = _bezier(start, peak, land, steps=12)

    # Pass 1 — wide additive halo (soft yellow bloom around the strike).
    halo_w = max(4, int(5 * bloom))
    _polyline(surf, (255, 220, 0, int(40 * bloom)), pts, halo_w, additive=True)

    # Pass 2 — mid yellow body. Widen to 3 when blooming so it survives 40px.
    mid_w = 3 if bloom >= 1.0 else 2
    _polyline(surf, COIL_YELLOW, pts, mid_w)

    # Optional cool ozone trace just inside the hottest arc.
    if hot:
        _polyline(surf, OZONE_BLUE, pts, 1)

    # Pass 3 — white-hot core.
    _polyline(surf, CORONA_WHITE, pts, 1)


def _spark(surf, origin, direction, length, bloom):
    """Short wingtip / tail spark that flicks upward toward the main halo."""
    ang = direction + math.sin(origin[0] * 1.7) * 0.3
    mx = origin[0] + math.cos(ang) * length * 0.5 + 2
    my = origin[1] + math.sin(ang) * length * 0.5
    tip = (origin[0] + math.cos(ang) * length,
           origin[1] + math.sin(ang) * length - 2)
    pts = [origin, (mx, my), tip]
    _polyline(surf, (255, 220, 0, int(48 * bloom)), pts, 3, additive=True)
    _polyline(surf, COIL_YELLOW, pts, 2)
    _polyline(surf, CORONA_WHITE, pts, 1)


def _glow_blit(surf, cx, cy, r, color, alpha):
    """Tight additive corona puff — used above the head, NOT over the body,
    so the glow crowns the bird rather than washing the dark stage."""
    g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    for k in range(r, 0, -1):
        a = int(alpha * (k / r) ** 2)
        pygame.draw.circle(g, (*color, a), (r, r), r - (r - k))
    surf.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)


def _wing_pts(base_x, side, strike):
    """Solid swept raptor wing. Tip lifts on the up-stroke, sweeps down on the
    power frame. Kept as one clean polygon so the near-black panel stays a
    quiet backdrop to the crown."""
    lift = int((1 - strike) * 12)
    drop = int(strike * 8)
    return [
        (base_x, CROWN_Y + 8),
        (base_x + side * 14, CROWN_Y + 3 - lift),
        (base_x + side * 30, CROWN_Y + 11 - lift + drop),
        (base_x + side * 26, CROWN_Y + 22 - lift * 0.4 + drop),
        (base_x + side * 12, BCY + 6),
        (base_x + side * 4, BCY - 2),
    ]


def _build_frame(wing_angle_deg):
    surf = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    strike = _strike(wing_angle_deg)         # 1 down-stroke … 0 up-stroke
    bloom = 0.85 + strike * 0.4              # arcs snap taller/brighter down

    # --- Dark wing panels behind the body (drawn first so body overlaps root).
    for side in (-1, 1):
        base_x = BCX + side * 5
        wpts = _wing_pts(base_x, side, strike)
        pygame.draw.polygon(surf, WING_DARK, wpts)
        # Thin cool leading-edge highlight along the top two segments.
        pygame.draw.line(surf, LEAD_EDGE, wpts[0], wpts[1], 1)
        pygame.draw.line(surf, LEAD_EDGE, wpts[1], wpts[2], 1)

    # --- Tail: dark wedge trailing low-left with two bright arc-tip sparks.
    tail = [
        (BCX - 10, BCY + 10),
        (BCX - 22, BCY + 20),
        (BCX - 18, BCY + 24),
        (BCX - 6, BCY + 18),
    ]
    pygame.draw.polygon(surf, WING_DARK, tail)
    pygame.draw.line(surf, LEAD_EDGE, tail[0], tail[1], 1)

    # --- Body: 3-layer charcoal ellipses (shadow / main / cool back-rim).
    _aaellipse(surf, BODY_SHADOW, (BCX + 1, BCY + 1), 16, 14)
    _aaellipse(surf, BODY_MAIN, (BCX, BCY), 16, 14)
    # Subtle cool-rim arc along the back-top edge.
    rim = pygame.Rect(BCX - 15, BCY - 15, 30, 26)
    pygame.draw.arc(surf, COOL_RIM, rim, math.radians(35), math.radians(150), 2)

    # --- Chest conduction line: one bright yellow sternum stripe head->belly.
    pygame.draw.line(surf, COIL_YELLOW, (BCX + 3, HCY + 6), (BCX + 1, BCY + 12), 2)

    # --- Tail-tip sparks.
    _spark(surf, (BCX - 22, BCY + 20), math.radians(-70), 8, bloom)
    _spark(surf, (BCX - 19, BCY + 23), math.radians(-55), 7, bloom)

    # --- Talons: charged charcoal claws with a yellow glow dot at each tip.
    for side in (-1, 1):
        tx = BCX + side * 6
        ty = BCY + 13
        for k in (-1, 1):
            cx = tx + k * 3
            ctip = (cx, ty + 6)
            pygame.draw.line(surf, BODY_MAIN, (tx, ty), ctip, 2)
            _glow_blit(surf, ctip[0], ctip[1], 3, COIL_YELLOW, 150)
            pygame.draw.circle(surf, COIL_YELLOW, ctip, 1)

    # --- Head: smooth charcoal skull (shadow + main).
    _aaellipse(surf, BODY_SHADOW, (HCX + 1, HCY + 1), 10, 10)
    _aaellipse(surf, BODY_MAIN, (HCX, HCY), 9, 9)

    # --- Beak: dark hooked polygon.
    pygame.draw.polygon(surf, BEAK_DARK, [
        (HCX + 8, HCY),
        (HCX + 16, HCY + 2),
        (HCX + 12, HCY + 4),
        (HCX + 9, HCY + 5),
    ])

    # --- Atmosphere: tight corona glow ABOVE the head (crowns, not washes).
    _glow_blit(surf, HCX, CROWN_Y - 8, 20, (255, 245, 160), 50)

    # --- THE HERO: corona-arc halo. Arcs leap from the terminal knob, peak
    # 12-16px over the head, and land back on the shoulders as a spark diadem.
    term = (HCX, CROWN_Y - 4)   # terminal knob top = arc launch point
    # Landing anchors spread across both shoulders/back.
    lands = [
        (HCX - 20, CROWN_Y + 6),
        (HCX - 12, CROWN_Y + 2),
        (HCX - 4, CROWN_Y),
        (HCX + 6, CROWN_Y + 1),
        (HCX + 13, CROWN_Y + 5),
        (HCX + 18, CROWN_Y + 10),
    ]
    for i, land in enumerate(lands):
        # Peak between launch and landing, lifted high above the crown; the
        # amount varies per arc and blooms on the power stroke.
        midx = (term[0] + land[0]) / 2 + math.sin(i * 1.3) * 4
        peak_lift = (13 + (i % 3) * 3) * bloom
        peak = (midx, CROWN_Y - 4 - peak_lift)
        _corona_arc(surf, term, peak, land, bloom, hot=(i == 2))

    # --- Wingtip arcs: each tip sheds a short spark reconnecting up toward the
    # halo, tying the diadem to the wings.
    for side in (-1, 1):
        base_x = BCX + side * 5
        wpts = _wing_pts(base_x, side, strike)
        tip = wpts[2]
        _spark(surf, tip, math.radians(-120 if side == 1 else -60), 8, bloom)

    # --- Terminal knob: the arcs' origin and the single brightest point.
    pygame.draw.circle(surf, TERMINAL_GOLD, (HCX, CROWN_Y), 4)
    _glow_blit(surf, HCX, CROWN_Y, 6, CORONA_WHITE, 180)
    pygame.draw.circle(surf, CORONA_WHITE, (HCX, CROWN_Y), 2)

    # --- Eye: yellow glow dot with white core.
    ex, ey = HCX + 1, HCY - 1
    _glow_blit(surf, ex, ey, 5, COIL_YELLOW, 150)
    pygame.draw.circle(surf, COIL_YELLOW, (ex, ey), 3)
    pygame.draw.circle(surf, CORONA_WHITE, (ex, ey), 2)

    return surf


_state = {"frames": None, "rot": {}}


def _frames():
    if _state["frames"] is None:
        _state["frames"] = [
            _add_outline(_build_frame(a)) for a in _WING_ANGLES
        ]
    return _state["frames"]


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    idx = frame_idx % len(_WING_ANGLES)
    key = (idx, round(tilt_deg / 3) * 3)
    rot = _state["rot"]
    if key not in rot:
        rot[key] = pygame.transform.rotozoom(_frames()[idx], key[1], 1.0)
    return rot[key]
