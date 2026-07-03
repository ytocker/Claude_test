"""BUG/INSECT redesign — design_4 MONARCH (Danaus plexippus).

The stained-glass classic. Two broad rounded playing-card wings fill the
canvas in bright monarch orange, carved into cells by heavy black veins that
radiate from the thorax, and framed by a thick black margin studded with a
double row of white flecks — the instantly-legible "orange butterfly" a player
recognises before they read anything else. A warm amber→deep-orange gradient
runs from the thorax root out to the wing edges. The whole read is built on
raw value contrast (bright orange over deep black), so it holds on both bright
day sky and night sky without a glow.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre — wings mount symmetric about here
HCX, HCY = 44, 34          # head, up-right along the insect axis
CROWN_Y = 24

# ── palette ──────────────────────────────────────────────────────────────────
MONARCH = (250, 132, 30)   # #FA841E — dominant wing fill, one step brighter so
                           # cells stay vivid orange (not brown) at 40px
INK     = (26, 19, 14)     # #1A130E — veins, margin, head, body
FLAKE   = (245, 241, 230)  # #F5F1E6 — margin dots + head/body specks
AMBER   = (255, 179, 71)   # #FFB347 — warm gradient core near the thorax
BRIGHT  = (255, 176, 80)   # #FFB050 — forewing-tip highlight (tips read bright)
SHADOW  = (208, 92, 26)    # #D05C1A — thin saturated edge only, not a wide ring


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 0 = fully down-stroke (wings wide open), 1 = fully up-stroke (edge-on).
    return (a + 40) / 90.0


# Right-wing outer contour at the full-open pose. A big ROUNDED forewing throws
# its apex up-and-out to fill the canvas width; a rounder hindwing lobe hangs
# below a shallow notch — the classic monarch playing-card silhouette. Inner
# edges sit ~2px off the body axis so the mirrored left wing nearly meets it,
# leaving a thin central channel for the black body.
_WING_R = [
    (34, 26),   # inner top, ~2px off the body axis
    (45, 13),   # forewing leading rise
    (56, 10),   # forewing apex — pushed up-and-out to fill the top corner
    (63, 20),   # forewing outer shoulder — reaches the canvas edge for width
    (62, 32),   # forewing trailing outer
    (60, 40),   # shallow notch between fore/hind wing (rounded card)
    (57, 48),   # hindwing outer
    (50, 54),   # hindwing rounded lobe
    (42, 56),   # hindwing bottom — rounded card, no drooping moth-tail point
    (34, 49),   # inner bottom, ~2px off the body axis
]


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def _inset(pts, frac):
    """Shrink a polygon toward its centroid — the gap becomes the ink margin."""
    cx, cy = _centroid(pts)
    return [(x + (cx - x) * frac, y + (cy - y) * frac) for x, y in pts]


def _transform(pts, side, spread, nx):
    """Place a wing: mirror for the left side, narrow it toward the body on the
    up-stroke (edge-on), and lift it as the stroke rises."""
    out = []
    for x, y in pts:
        dx = (x - BCX) * side
        out.append((BCX + dx * nx, y - spread))
    return out


def _wing_mask(pts):
    m = _new()
    pygame.draw.polygon(m, (255, 255, 255, 255), pts)
    return m


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.14)                     # thick ~6px black margin

    # Black margin first (the separator that carries the read on any sky), then
    # the orange field. SHADOW is now only a thin saturated rim; MONARCH covers
    # the cells so nothing near the margin reads brown at 40px.
    pygame.draw.polygon(surf, INK, margin)
    pygame.draw.polygon(surf, SHADOW, fill)
    inner = _inset(fill, 0.06)
    pygame.draw.polygon(surf, MONARCH, inner)

    fcx, fcy = _centroid(fill)
    rx, ry = margin[0]                               # wing root (inner-top)
    root = (rx + (fcx - rx) * 0.42, ry + (fcy - ry) * 0.42)
    core = _new()
    for r, col, a in ((16, MONARCH, 150), (12, AMBER, 185), (7, AMBER, 225)):
        _aaellipse(core, (*col, a), root, r, r * 0.82)
    # The forewing tip is where a monarch is brightest — blush it, don't darken.
    tip, lead = fill[2], fill[1]
    mid = ((tip[0] + lead[0]) / 2, (tip[1] + lead[1]) / 2)
    _aaellipse(core, (*BRIGHT, 200), tip, 7, 6)
    _aaellipse(core, (*BRIGHT, 225), mid, 4, 4)
    core.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(core, (0, 0))

    # Heavy black veins radiating from the thorax root out to the margin — the
    # stained-glass carve. Five main ribs to the wing extremities plus a thin
    # midrib give distinct orange cells without turning to noise at 40px.
    for idx in (2, 3, 4, 6, 7):
        pygame.draw.line(surf, INK, root, fill[idx], 2)
    pygame.draw.line(surf, INK, root, fill[1], 1)
    pygame.draw.line(surf, INK, root, fill[8], 1)

    # White margin flecks — the monarch's signature border dots. Kept crisp and
    # broken (identity is ORANGE first, dots second): a sparse 1px outer row
    # (one dot per edge segment) plus a finer 1px inner row as a second line, so
    # at 40px it reads as a dotted rim, never a frosted lace halo.
    outer = margin[1:9]
    for i in range(len(outer) - 1):
        a0, a1 = outer[i], outer[i + 1]
        ox = a0[0] + (fcx - a0[0]) * 0.14
        oy = a0[1] + (fcy - a0[1]) * 0.14
        pygame.draw.circle(surf, FLAKE, (int(ox), int(oy)), 1)
        for t in (0.0, 0.5):
            ex = a0[0] + (a1[0] - a0[0]) * t
            ey = a0[1] + (a1[1] - a0[1]) * t
            ix = ex + (fcx - ex) * 0.30
            iy = ey + (fcy - ey) * 0.30
            pygame.draw.circle(surf, FLAKE, (int(ix), int(iy)), 1)


def _draw_body(surf, lift=0):
    # Short black abdomen tapering to a point well above the hindwing lobe, so
    # it never drips out the bottom on the up-stroke. The whole body assembly
    # rides `lift` with the wings, keeping the tail tucked in every frame.
    L = lift
    pygame.draw.polygon(surf, INK, [
        (BCX - 3, BCY - L), (BCX + 3, BCY - L),
        (BCX + 1, BCY + 5 - L),
        (BCX - 3, BCY + 9 - L),                      # tail point, ~BCY+9
        (BCX - 5, BCY + 4 - L),
    ])
    for (fx, fy) in ((BCX - 1, BCY + 2), (BCX - 2, BCY + 6)):
        pygame.draw.circle(surf, FLAKE, (fx, fy - L), 1)
    # Furred thorax bead.
    _aaellipse(surf, INK, (BCX, BCY - L), 5, 7)
    pygame.draw.circle(surf, FLAKE, (BCX - 1, BCY - 2 - L), 1)


def _draw_head(surf, lift=0):
    # Two thin CLUBBED antennae (true butterfly) sweeping up-and-out to the
    # crown, each ending in an ink ball with a lighter tip pixel.
    L = lift
    for (tx, ty) in ((HCX - 6, CROWN_Y - L), (HCX + 4, CROWN_Y - L)):
        sx, sy = HCX + (1 if tx > HCX else -1), HCY - 4 - L
        mx = (sx + tx) / 2 + (2 if tx > HCX else -2)
        my = (sy + ty) / 2
        pygame.draw.lines(surf, INK, False,
                          [(sx, sy), (mx, my), (tx, ty)], 1)
        pygame.draw.circle(surf, INK, (tx, ty), 2)
        pygame.draw.circle(surf, AMBER, (tx, ty - 1), 1)
    # A thin warm ring gives the head bead a 1px value break from the dark
    # veins/thorax so it stays a distinct bead, not part of the wing mass.
    _aaellipse(surf, MONARCH, (HCX, HCY - L), 6, 6)
    _aaellipse(surf, INK, (HCX, HCY - L), 5, 5)
    pygame.draw.circle(surf, FLAKE, (HCX - 2, HCY - 1 - L), 1)
    pygame.draw.circle(surf, FLAKE, (HCX + 2, HCY - L), 1)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    # Butterfly wings raise by rotating about the body axis, so the flap read
    # comes mostly from the horizontal narrowing; a gentle shared lift adds life
    # without the abdomen ever poking below the wings.
    spread = int(f * 9)
    nx = 1.0 - 0.42 * f

    # Far (left) wing behind the body, near (right) wing in front of the roots.
    _draw_wing(surf, -1, spread, nx)
    _draw_body(surf, spread)
    _draw_wing(surf, +1, spread, nx)
    _draw_head(surf, spread)
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
