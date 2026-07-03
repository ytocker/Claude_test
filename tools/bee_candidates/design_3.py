"""LUNAWING — Luna moth (Actias luna) candidate for `skin_bee` (scratch).

Where AZUREWING is a hard structural-blue sail, LUNAWING is soft and lunar:
pale-lime wings that fill the canvas, and — the whole point — TWO long ribbon
HINDWING TAILS that sweep down-left toward the abdomen. Those tails are the
40px identity; nothing else on a casual sprite trails like a luna moth, so they
are drawn bold and kept clear of the wing mass. An amber eyespot rides each
forewing and a maroon leading stripe caps the top edge, and a green moonlit
bloom pulses brightest on the down-stroke so the pale moth still reads on a
dark night sky.

Exploration only — NOT registered in store_skins.BUILDERS. Production art stays
untouched until a winner is picked.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre
HCX, HCY = 44, 34          # head — upper-right on the insect axis
CROWN_Y = 24               # antennae fan to here

# ── palette ──────────────────────────────────────────────────────────────────
LIME    = (184, 233, 134)  # #B8E986 Luna Lime — dominant wing fill
MOONMINT = (228, 247, 197) # #E4F7C5 Moonmint — upper-wing highlight band
PLUM    = (122, 46, 59)    # #7A2E3B Plum Edge — forewing stripe + tail edge
AMBER   = (232, 161, 60)   # #E8A13C Eye Amber — eyespot ring
CREAM   = (240, 234, 210)  # #F0EAD2 Body Cream — head + antennae
MIDCREAM = (206, 198, 172)  # muted cream so the body recedes under the wings
EDGE    = (150, 199, 104)  # shaded lime rim under the fill
WINDOW  = (232, 244, 214)  # pale eyespot window
WHITE   = (246, 250, 236)  # catch-lights
GLOW    = (150, 235, 130)  # moonlit bloom


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 0 = deepest down-stroke (wings wide, angle -40), 1 = top up-stroke (50).
    return (a + 40) / 90.0


# Right-wing outer contour at the wide down-stroke. A rounded forewing lobe
# throws its apex up-and-out to fill the 64px width; a rounded hindwing hangs
# below a shallow notch and drops to the tail root. Mirrored for the left side.
_WING_R = [
    (34, 33),   # 0 inner top, near the body axis
    (43, 22),   # 1 forewing leading rise
    (52, 19),   # 2 forewing apex — up and out
    (61, 25),   # 3 forewing outer shoulder — fills the width
    (62, 34),   # 4 forewing outer trailing
    (57, 41),   # 5 shallow notch fore/hind
    (56, 49),   # 6 hindwing outer
    (47, 57),   # 7 hindwing lower lobe — tail root
    (39, 56),   # 8 hindwing bottom inner
    (34, 47),   # 9 inner bottom, near the body axis
]


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def _inset(pts, frac):
    cx, cy = _centroid(pts)
    return [(x + (cx - x) * frac, y + (cy - y) * frac) for x, y in pts]


def _transform(pts, side, spread, nx):
    """Place a wing: mirror for the left side, narrow horizontally toward the
    body on the up-stroke, and lift it as the stroke rises."""
    out = []
    for x, y in pts:
        dx = (x - BCX) * side
        out.append((BCX + dx * nx, y - spread))
    return out


def _stroke(pts, spread, nx):
    # Same lift/narrow as a wing but for absolute (already-placed) points —
    # used for the tails, which are authored in final position, not mirrored.
    return [(BCX + (x - BCX) * nx, y - spread) for x, y in pts]


def _wing_mask(pts):
    m = _new()
    pygame.draw.polygon(m, (255, 255, 255, 255), pts)
    return m


def _eyespot(surf, cx, cy):
    # Concentric luna eyespot: amber ring, thin maroon rim, a pale translucent
    # window with a dark upper arc, and a white glint. The one non-lime accent
    # per wing — a hue anchor that survives the shrink.
    pygame.draw.circle(surf, AMBER, (cx, cy), 4)
    pygame.draw.circle(surf, PLUM, (cx, cy), 4, 1)
    _aaellipse(surf, WINDOW, (cx, cy), 2, 2)
    pygame.draw.arc(surf, PLUM, pygame.Rect(cx - 2, cy - 2, 5, 5),
                    math.radians(200), math.radians(345), 1)
    pygame.draw.circle(surf, WHITE, (cx - 1, cy - 1), 1)


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.09)

    # Shaded lime rim, then the broad lime field. The rim + the sprite outline
    # do the separator job that AZUREWING's ink margin does, but stay pale so
    # the moth keeps its ghostly moonlit value.
    pygame.draw.polygon(surf, EDGE, margin)
    pygame.draw.polygon(surf, LIME, fill)

    # Moonmint highlight band across the upper wing, clipped to the fill so it
    # reads as light skating off the scales rather than a painted stripe.
    fcx, fcy = _centroid(fill)
    band = _new()
    _aaellipse(band, (*MOONMINT, 205), (fcx, fcy - 9), 13, 5)
    band.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(band, (0, 0))

    # Maroon stripe that runs the full leading-and-outer edge of the forewing,
    # not just the top arch — a wing-margin band, so it stops reading as an
    # eyebrow arched over the eyespot.
    lead = [(int(x), int(y))
            for x, y in (margin[1], margin[2], margin[3], margin[4])]
    pygame.draw.lines(surf, PLUM, False, lead, 3)

    # One amber eyespot on the forewing, pulled a touch in from the apex. The
    # two wings are mirrored, so nudge the eyespot to a different height per
    # side — broken symmetry kills the paired-eyes / owl-face read.
    ex = int(fcx + (margin[2][0] - fcx) * 0.14)
    ey = int(fcy - 4 + (2 if side > 0 else -1))
    _eyespot(surf, ex, ey)


def _tail(surf, root, ctrl, tip):
    """One elongated, slightly twisted hindwing ribbon along a quadratic bezier.
    Width tapers from the root, thins through the shaft, then flares into a small
    spatulate paddle — the twist of a real luna tail — with a maroon edge so the
    ribbon stays crisp against the wing behind it."""
    def bez(t):
        mt = 1 - t
        return (mt * mt * root[0] + 2 * mt * t * ctrl[0] + t * t * tip[0],
                mt * mt * root[1] + 2 * mt * t * ctrl[1] + t * t * tip[1])

    n = 12
    left, right = [], []
    for i in range(n + 1):
        t = i / n
        c = bez(t)
        # Half-width profile, thickened so the streamer reads as a ribbon and
        # not a leg: 3.2 at root -> 2.0 shaft -> 3.6 spatulate paddle flare.
        if t < 0.82:
            hw = 3.2 + (2.0 - 3.2) * (t / 0.82)
        else:
            hw = 2.0 + (3.6 - 2.0) * ((t - 0.82) / 0.18)
        nxt = bez(min(1.0, t + 0.02))
        dx, dy = nxt[0] - c[0], nxt[1] - c[1]
        L = math.hypot(dx, dy) or 1.0
        nx_, ny_ = -dy / L, dx / L
        left.append((c[0] + nx_ * hw, c[1] + ny_ * hw))
        right.append((c[0] - nx_ * hw, c[1] - ny_ * hw))
    poly = left + right[::-1]
    pygame.draw.polygon(surf, LIME, poly)
    # Plum on the TRAILING (lower) edge only — one shaded rim reads as a lit,
    # rounded ribbon; outlining both edges made it a hollow stick.
    pygame.draw.lines(surf, PLUM, False,
                      [(int(x), int(y)) for x, y in right], 2)
    # Mint sheen down the shaft so the tail doesn't read as a flat stick.
    for i in range(2, n - 2, 2):
        cx, cy = bez(i / n)
        pygame.draw.circle(surf, MOONMINT, (int(cx), int(cy)), 1)


def _draw_tails(surf, spread, nx, sway):
    # Two long ribbons splaying into a clear V toward the canvas floor — this
    # splay is the ONLY luna identity claim, so the tips diverge hard (back to
    # x~10, front to x~34) and both drop near y~82. Lifted a touch less than the
    # wings so they trail, and swayed per frame for life.
    lift = int(spread * 0.7)
    # Back (outer) tail — sweeps down-and-out to the far-left corner.
    a = _stroke([(24, 54), (15 + sway, 69), (10 + sway, 82)], lift, nx)
    _tail(surf, a[0], a[1], a[2])
    # Front (inner) tail — stays more central so the pair opens into a V.
    b = _stroke([(43, 54), (39 + sway, 69), (34 + sway, 82)], lift, nx)
    _tail(surf, b[0], b[1], b[2])


def _antenna(surf, base, tip):
    # Feathery comb antenna: a shaft with short paired teeth — thicker and
    # bushier than a clubbed butterfly pair, the luna/saturniid signature.
    pygame.draw.line(surf, CREAM, base, tip, 2)
    steps = 7
    for i in range(1, steps):
        t = i / steps
        px = base[0] + (tip[0] - base[0]) * t
        py = base[1] + (tip[1] - base[1]) * t
        pygame.draw.line(surf, CREAM, (px - 4, py - 1), (px + 4, py + 1), 1)


def _draw_body(surf):
    # Short fuzzy body angling down-left off the head. Kept muted mid-cream and
    # small so it recedes — the wings and tails must out-contrast it, and the
    # slim abdomen no longer smothers the tail roots below.
    _aaellipse(surf, MIDCREAM, (BCX, BCY), 4, 6)             # thorax
    _aaellipse(surf, (184, 176, 152), (BCX - 3, BCY + 3), 3, 5)  # abdomen
    for k in range(2):
        pygame.draw.line(surf, (168, 160, 138),
                         (BCX - 5, BCY + 1 + k * 4),
                         (BCX + 2, BCY + 1 + k * 4), 1)
    _aaellipse(surf, MOONMINT, (BCX - 1, BCY - 3), 2, 2)     # thorax sheen


def _draw_head(surf):
    _antenna(surf, (HCX - 1, HCY - 3), (HCX - 6, CROWN_Y))
    _antenna(surf, (HCX + 1, HCY - 3), (HCX + 5, CROWN_Y + 1))
    _aaellipse(surf, CREAM, (HCX, HCY), 5, 4)                 # fuzzy head
    for ex in (HCX - 2, HCX + 3):
        pygame.draw.circle(surf, (46, 34, 30), (ex, HCY + 1), 1)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = int(f * 16)               # lift the wings as the stroke rises
    nx = 1.0 - 0.28 * f                # narrow horizontally on the up-stroke
    try:
        fi = _WING_ANGLES.index(int(round(wing_angle_deg)))
    except ValueError:
        fi = 0
    sway = (fi - 1.5) * 1.6            # tails drift for life across the cycle

    # Far (left) wing, near (right) wing, then the tails over the hindwing hem,
    # then body + head so the fuzzy thorax caps the tail roots.
    _draw_wing(surf, -1, spread, nx)
    _draw_wing(surf, +1, spread, nx)
    _draw_tails(surf, spread, nx, sway)
    _draw_body(surf)
    _draw_head(surf)
    return surf


def _apply_glow(outlined, fi):
    # Green moonlit bloom BEHIND the outlined moth, brightest on the down-stroke
    # (fi 3) so the pale sprite still separates from a dark night sky. Built as
    # additive circles on a clear plate, with the finished sprite laid on top —
    # done AFTER _add_outline so the outline mask never swallowed the glow.
    # Wide pulse contrast (0.5 up-stroke -> 1.0 down-stroke) so the down-beat
    # visibly blooms rather than sitting as a flat green vignette.
    scale = {3: 1.0, 2: 0.75, 1: 0.60, 0: 0.50}.get(fi, 0.6)
    w, h = outlined.get_size()
    # Centre the halo lower so the bloom also lifts the trailing tails off a
    # dark night sky, not just the wing mass.
    cx, cy = w // 2, h // 2 - 2
    halo = pygame.Surface((w, h), pygame.SRCALPHA)
    for r, base in ((32, 40), (23, 48), (15, 58)):
        a = int(base * scale)
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*GLOW, a), (r, r), r)
        halo.blit(g, (cx - r, cy - r), special_flags=pygame.BLEND_RGBA_ADD)
    halo.blit(outlined, (0, 0))
    return halo


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [
            _apply_glow(_add_outline(_build_frame(a)), i)
            for i, a in enumerate(_WING_ANGLES)
        ]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
