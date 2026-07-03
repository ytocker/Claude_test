"""TESLA CROWN — a Tesla-coil thunderbird whose head is the coil terminal.

Inverts the usual bright-bird idea: the raptor body is a dark charcoal STAGE
so the true hero — a corona-arc crown of lightning — reads as the single
brightest thing on screen. A short coil POST rises off the skull to a white-hot
terminal knob (the one brightest point); four widely-spread arcs leap from it,
curl high above the head, and land on the shoulders as a spiked diadem, while
one legible arc per wingtip wires the circuit down into the wings. A 3-pass
glow (thin add-halo, mid yellow, white core) keeps arcs luminous and SEPARATE
down to 40px. Wings and body stay near-black with a razor dark edge so nothing
below competes with the crown. The crown breathes tall on the power stroke and
short on the up-stroke for an unmistakable Tesla-snap pulse across frames.
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
STERNUM_OCHRE = (120, 90, 15)   # dim dark ochre — sternum texture, not a beacon
DARK_NAVY   = (8, 10, 14)       # razor-sharp body edge for pale-blue day sky


def _aaellipse_outline(surf, color, center, rx, ry, w=1):
    """1px ellipse outline — used to lay a razor-sharp dark edge on the body."""
    cx, cy = center
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, w)


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
    single ozone-blue trace inside the very brightest arc. The halo is kept
    deliberately thin and faint so four separated arcs read as distinct crown
    spikes instead of merging into one orange bloom."""
    pts = _bezier(start, peak, land, steps=12)

    # Pass 1 — narrow, faint additive halo. Low alpha + width keeps neighbouring
    # arcs from bleeding into each other, so the diadem reads as spikes.
    _polyline(surf, (255, 220, 0, 18), pts, 2, additive=True)

    # Pass 2 — mid yellow body. Widen to 3 when blooming so it survives 40px.
    mid_w = 3 if bloom >= 1.0 else 2
    _polyline(surf, COIL_YELLOW, pts, mid_w)

    # Optional cool ozone trace just inside the hottest arc.
    if hot:
        _polyline(surf, OZONE_BLUE, pts, 1)

    # Pass 3 — white-hot core.
    _polyline(surf, CORONA_WHITE, pts, 1)


def _wingtip_arc(surf, tip, land):
    """One legible arc per wingtip curving up toward the crown landing zone, so
    the electric circuit reads complete from tip to diadem. A single 3-point
    polyline (not a scatter of invisible sparks) is what actually survives the
    gameplay downscale."""
    midx = (tip[0] + land[0]) / 2
    midy = min(tip[1], land[1]) - 6
    pts = [tip, (midx, midy), land]
    _polyline(surf, (255, 220, 0, 18), pts, 3, additive=True)
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
    # Widened crown-height breathing: short on the up-stroke, tall on the
    # power stroke, so the Tesla-snap grow/shrink is unmistakable across frames.
    peak_scale = 0.55 + strike * 0.90        # 0.55 up-stroke … 1.45 down-stroke

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

    # --- Chest conduction line: a dim dark-ochre sternum stripe. Kept as quiet
    # texture, NOT a beacon, so the terminal knob stays the only bright point.
    pygame.draw.line(surf, STERNUM_OCHRE, (BCX + 3, HCY + 6), (BCX + 1, BCY + 12), 2)

    # --- Talons: charged charcoal claws. No glow dots — the crown owns the
    # brightness budget, so the talons stay dark structure only.
    for side in (-1, 1):
        tx = BCX + side * 6
        ty = BCY + 13
        for k in (-1, 1):
            ctip = (tx + k * 3, ty + 6)
            pygame.draw.line(surf, BODY_MAIN, (tx, ty), ctip, 2)

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

    # --- Body/wing hard edge: a 1px very-dark-navy border on top of the outline
    # so the charcoal stage keeps a razor-sharp silhouette against pale-blue day.
    for side in (-1, 1):
        base_x = BCX + side * 5
        pygame.draw.polygon(surf, DARK_NAVY, _wing_pts(base_x, side, strike), 1)
    _aaellipse_outline(surf, DARK_NAVY, (BCX, BCY), 16, 14)

    # --- THE HERO: corona-arc halo. Four widely-spread arcs leap from the coil
    # terminal, peak high over the head, and land on the shoulders. Four (not
    # six) with forced gaps read as a spiked CROWN, not an orange blob.
    term = (HCX, CROWN_Y - 4)   # terminal knob top = arc launch point
    lands = [
        (HCX - 20, CROWN_Y + 8),
        (HCX - 8, CROWN_Y + 1),
        (HCX + 8, CROWN_Y + 2),
        (HCX + 19, CROWN_Y + 9),
    ]
    for i, land in enumerate(lands):
        # Widen the breathing delta so the crown visibly grows tall on the
        # power stroke and shrinks on the up-stroke — the Tesla-snap tell.
        midx = (term[0] + land[0]) / 2 + math.sin(i * 1.3) * 3
        peak_lift = (13 + (i % 2) * 4) * peak_scale
        peak = (midx, CROWN_Y - 4 - peak_lift)
        _corona_arc(surf, term, peak, land, bloom, hot=(i == 1))

    # --- Wingtip arcs: one legible arc per tip curving up to the crown landing
    # zone, so the diadem visibly wires into the wings.
    tip_land = [(HCX - 12, CROWN_Y + 3), (HCX + 12, CROWN_Y + 3)]
    for side, land in zip((-1, 1), tip_land):
        base_x = BCX + side * 5
        tip = _wing_pts(base_x, side, strike)[2]
        _wingtip_arc(surf, tip, land)

    # --- Coil post: a short bright stem from the skull up to the terminal knob.
    # The "post + ball + corona" motif is the Tesla-coil read — not just a bird
    # with a lightning halo.
    pygame.draw.line(surf, COIL_YELLOW, (HCX, CROWN_Y + 2), (HCX, CROWN_Y - 4), 2)

    # --- Terminal knob: the arcs' origin and the single brightest point.
    pygame.draw.circle(surf, TERMINAL_GOLD, (HCX, CROWN_Y), 4)
    _glow_blit(surf, HCX, CROWN_Y, 6, CORONA_WHITE, 180)
    pygame.draw.circle(surf, CORONA_WHITE, (HCX, CROWN_Y), 2)

    # --- Eye: a small cool-white pinpoint, no yellow glow, so it never competes
    # with the terminal knob for the single brightest point.
    ex, ey = HCX + 1, HCY - 1
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
