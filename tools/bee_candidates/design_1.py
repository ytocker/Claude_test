"""BUG/INSECT redesign — design_1 AZUREWING (Blue Morpho Butterfly).

The wings are the hero. A slim ink body hides behind two great overlapping
sails of structural blue that fill nearly the whole 64px canvas; a per-frame
cyan overlay fakes the morpho's angle-dependent iridescent shift, and a wide
ink margin studded with white eye-flecks keeps the silhouette reading as a
butterfly at 40px on pale day sky.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre
HCX, HCY = 44, 34          # head
CROWN_Y = 24

# ── palette ──────────────────────────────────────────────────────────────────
ROYAL   = (27, 58, 143)    # deep royal — wing base, shaded lobes
BLUE    = (47, 123, 255)   # structural blue — the hero field
CYAN     = (95, 225, 255)  # cyan iridescent highlight (per-frame shimmer)
INK     = (11, 14, 26)     # scalloped margin / head / antenna clubs
WHITE   = (234, 244, 255)  # scale-white eye-flecks
THORAX  = (20, 15, 35)     # body


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 0 = fully down-stroke (wings wide open), 1 = fully up-stroke (edge-on).
    return (a + 40) / 90.0


def _rot_blit(surf, s, anchor):
    surf.blit(s, s.get_rect(center=anchor).topleft)


# Right-wing outer contour at full open pose (down-stroke). Forewing lobe rises
# toward the crown; hindwing lobe drops to a rounded tail. Mirrored about the
# body axis (x=BCX) for the left wing so the span reads symmetric.
_WING_R = [
    (31, 33),   # inner top, tucked against the thorax
    (40, 16),   # forewing rise
    (51, 13),   # forewing apex tip
    (60, 23),   # forewing outer shoulder
    (59, 35),   # outer notch between fore/hind wing
    (55, 46),   # hindwing outer
    (47, 58),   # hindwing rounded tail
    (37, 55),   # hindwing inner-bottom
    (32, 46),   # inner bottom, back to the thorax
]


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def _inset(pts, frac):
    """Shrink a polygon toward its centroid — the gap becomes the ink margin.
    A centroid inset thickens the margin at the extremities, which reads as the
    morpho's scalloped border and survives the 40px shrink."""
    cx, cy = _centroid(pts)
    return [(x + (cx - x) * frac, y + (cy - y) * frac) for x, y in pts]


def _transform(pts, side, spread, nx):
    """Place a wing: mirror for the left side, narrow it horizontally toward the
    body on the up-stroke (edge-on), and lift it as the stroke rises."""
    out = []
    for x, y in pts:
        dx = (x - BCX) * side
        out.append((BCX + dx * nx, y - spread))
    return out


def _wing_mask(pts):
    m = _new()
    pygame.draw.polygon(m, (255, 255, 255, 255), pts)
    return m


def _draw_wing(surf, side, spread, nx, fi):
    margin = _transform(_WING_R, side, spread, nx)
    fill = _inset(margin, 0.22)                     # ~5-6px ink border

    # Ink margin first (the separator that holds the read on pale sky), then
    # the royal underlayer and the bright structural-blue field on top.
    pygame.draw.polygon(surf, INK, margin)
    pygame.draw.polygon(surf, ROYAL, fill)
    inner = _inset(fill, 0.16)
    pygame.draw.polygon(surf, BLUE, inner)

    # Per-frame cyan shimmer, clipped to the wing fill so no stray glow escapes.
    # Offsetting the highlight ellipse by frame index fakes the morpho's
    # angle-dependent iridescence as the wings beat.
    fcx, fcy = _centroid(fill)
    shift = (fi - 1.5) * 4
    sh = _new()
    _aaellipse(sh, (*CYAN, 120), (fcx + shift * side, fcy - 6), 15, 12)
    sh.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sh, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # White eye-flecks marching down the forewing margin (morpho apex spots) and
    # a couple of ink scallop-notches on the outer edge for the border texture.
    fore = [margin[1], margin[2], margin[3], margin[4]]
    for i, (mx, my) in enumerate(fore):
        cx, cy = fcx, fcy
        px = mx + (cx - mx) * 0.14
        py = my + (cy - my) * 0.14
        pygame.draw.circle(surf, WHITE, (int(px), int(py)), 2)
    pygame.draw.circle(surf, INK, (int(margin[5][0]), int(margin[5][1])), 2)


def _draw_body(surf):
    # Slim abdomen tapering down-left, drawn under the thorax bead.
    pygame.draw.polygon(surf, THORAX, [
        (BCX - 3, BCY), (BCX + 3, BCY),
        (BCX - 8, BCY + 14), (BCX - 11, BCY + 14),
    ])
    # Hair-thin legs tucked under the thorax — deliberately subtle.
    for i in range(3):
        ly = BCY + 3 + i * 3
        pygame.draw.line(surf, (*INK, 170), (BCX - 1, ly), (BCX - 6, ly + 4), 1)
        pygame.draw.line(surf, (*INK, 170), (BCX + 1, ly), (BCX + 5, ly + 4), 1)
    # Thorax.
    _aaellipse(surf, THORAX, (BCX, BCY), 5, 7)
    _aaellipse(surf, (40, 30, 60), (BCX - 1, BCY - 2), 2, 4)   # faint sheen


def _draw_head(surf):
    # Clubbed antennae sweeping up to the crown, each ending in an ink ball.
    for (tx, ty) in ((HCX - 4, CROWN_Y - 2), (HCX + 3, CROWN_Y - 4)):
        sx, sy = HCX + (1 if tx > HCX else -1), HCY - 3
        mx, my = (sx + tx) / 2 + (2 if tx > HCX else -2), (sy + ty) / 2
        pts = [(sx, sy), (mx, my), (tx, ty)]
        pygame.draw.lines(surf, INK, False, pts, 1)
        pygame.draw.circle(surf, INK, (tx, ty), 2)
    # Head bead with a tiny catch-light.
    pygame.draw.circle(surf, INK, (HCX, HCY), 5)
    pygame.draw.circle(surf, (70, 90, 150), (HCX - 2, HCY - 2), 1)


def _draw_glow(surf):
    # Soft blue halo so the structural blue pops against bright day sky.
    glow = _new()
    for r, a in ((30, 8), (22, 9), (14, 9)):
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*BLUE, a), (r, r), r)
        glow.blit(g, (BCX - 2 - r, BCY - 8 - r))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    try:
        fi = _WING_ANGLES.index(int(round(wing_angle_deg)))
    except ValueError:
        fi = 0
    spread = int(f * 18)           # lift the wings as the stroke rises
    nx = 1.0 - 0.55 * f            # narrow toward edge-on on the up-stroke

    _draw_glow(surf)
    # Far (left) wing behind the body, near (right) wing in front of the roots.
    _draw_wing(surf, -1, spread, nx, fi)
    _draw_body(surf)
    _draw_wing(surf, +1, spread, nx, fi)
    _draw_head(surf)
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
