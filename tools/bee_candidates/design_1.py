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
HCX, HCY = 32, 30          # head — on the body axis so the read stays symmetric
CROWN_Y = 20

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


# Right-wing outer contour at full open pose (down-stroke). A big triangular
# forewing throws its apex UP and OUT to fill nearly the full 64px width; a
# rounder hindwing lobe hangs below a deep notch. Inner edges sit ~2px off the
# body axis (x=BCX) so the mirrored left wing nearly touches it — one
# continuous butterfly outline instead of two islands.
_WING_R = [
    (34, 30),   # inner top, ~2px off the body axis
    (46, 14),   # forewing leading rise
    (56, 10),   # forewing apex vertex — up and out
    (62, 20),   # forewing outer shoulder — fills the width
    (60, 30),   # forewing trailing outer
    (59, 35),   # deep notch between fore/hind wing
    (57, 44),   # hindwing outer
    (50, 57),   # hindwing rounded tail lobe
    (40, 58),   # hindwing bottom
    (34, 47),   # inner bottom, ~2px off the body axis
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
    fill = _inset(margin, 0.12)                     # thin ~3-4px scalloped border

    # Ink margin first (the separator that holds the read on pale sky), then
    # the royal underlayer and a broad bright structural-blue field that fills
    # most of the wing face — that field is where the colour drama lives.
    pygame.draw.polygon(surf, INK, margin)
    pygame.draw.polygon(surf, ROYAL, fill)
    inner = _inset(fill, 0.08)
    pygame.draw.polygon(surf, BLUE, inner)

    # Per-frame cyan shimmer clipped to the wing fill. Three ellipses stacked
    # down the upper-inner half read as a coherent iridescent sweep, and a
    # brighter core at the wing root gives a real bright→dark value gradient.
    # The shift is the SAME screen direction on both wings so the shimmer
    # sweeps as one gesture rather than mirroring per side.
    fcx, fcy = _centroid(fill)
    rx, ry = margin[0]                               # wing root (inner-top)
    root = (rx + (fcx - rx) * 0.35, ry + (fcy - ry) * 0.35)
    shift = (fi - 1.5) * 4
    alpha = 120 if fi in (1, 2) else 90
    sh = _new()
    for k in range(3):
        _aaellipse(sh, (*CYAN, alpha),
                   (fcx + shift, fcy - 12 + k * 9), 8, 5)
    _aaellipse(sh, (215, 245, 255, min(255, alpha + 60)),
               (root[0] + shift * 0.5, root[1]), 6, 5)
    sh.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sh, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # White eye-flecks marching along the forewing margin (morpho apex spots).
    # Kept at 2px — the non-hue accessibility anchor at 40px / night sky.
    for (mx, my) in (margin[2], margin[3], margin[4]):
        px = mx + (fcx - mx) * 0.16
        py = my + (fcy - my) * 0.16
        pygame.draw.circle(surf, WHITE, (int(px), int(py)), 2)


def _draw_body(surf):
    # Slim abdomen hanging straight down the body axis, under the thorax bead.
    pygame.draw.polygon(surf, THORAX, [
        (BCX - 3, BCY), (BCX + 3, BCY),
        (BCX + 2, BCY + 14), (BCX - 2, BCY + 14),
    ])
    # A single suggested pair of hair-thin legs — the wings are the whole story
    # at 40px, so the body stays quiet.
    ly = BCY + 5
    pygame.draw.line(surf, (*INK, 160), (BCX - 1, ly), (BCX - 6, ly + 4), 1)
    pygame.draw.line(surf, (*INK, 160), (BCX + 1, ly), (BCX + 5, ly + 4), 1)
    # Thorax.
    _aaellipse(surf, THORAX, (BCX, BCY), 5, 7)
    _aaellipse(surf, (40, 30, 60), (BCX - 1, BCY - 2), 2, 4)   # faint sheen


def _draw_head(surf):
    # A symmetric pair of clubbed antennae sweeping up and out to the crown,
    # each ending in an ink ball.
    for (tx, ty) in ((HCX - 5, CROWN_Y), (HCX + 5, CROWN_Y)):
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
        glow.blit(g, (BCX - r, BCY - 8 - r))
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    try:
        fi = _WING_ANGLES.index(int(round(wing_angle_deg)))
    except ValueError:
        fi = 0
    spread = int(f * 18)           # lift the wings as the stroke rises
    # Cap the horizontal narrowing so even the edge-on up-stroke stays legibly
    # winged — the lifted `spread` angle carries the "wings raised" read.
    nx = 1.0 - 0.30 * f

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
