"""BUG/INSECT redesign — design_5 ATLASWING (Atlas moth, Attacus atlas).

The wings are the whole story. Two enormous ANGULAR sails fill the canvas
wall-to-wall; each forewing apex hooks out into a pointed SNAKE-HEAD tip with a
dark eye-dot — the Atlas moth's cobra-mimicry tell and the only jagged,
non-rounded silhouette in the set. Big cream TRIANGULAR WINDOWS are punched
semi-transparent so the day sky bleeds faintly through them (a technique unique
to this candidate). A stout rust/ochre banded body and broad feathery comb
antennae seat the read as a moth, not a butterfly.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre
# Head kept ON the body axis: a dorsal-spread moth reads strongest symmetric,
# and a centred head lets the two hooked forewings mirror cleanly at 40px.
HCX, HCY = 32, 27
CROWN_Y = 14

# ── palette ──────────────────────────────────────────────────────────────────
RUST   = (155, 74, 42)     # #9B4A2A Atlas Rust — DOMINANT wing field
MAROON = (94, 35, 32)      # #5E2320 deep maroon — outer margin / forewing base
OCHRE  = (216, 154, 84)    # #D89A54 ochre submarginal band + body bands
CREAM  = (243, 230, 200)   # #F3E6C8 translucent triangular window panes
DARK   = (36, 21, 18)      # #241512 snake-tip / eye-dot / body outline
OCHRE_HI = (238, 190, 128) # warm highlight for the body gradient / catch-lights

WINDOW_ALPHA = 100         # low enough that sky bleeds faintly through the panes


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 1 = up-stroke (wings lifted, edge-on), 0 = down-stroke (wings wide open).
    return (a + 40) / 90.0


# Right-wing outer contour at the full-open down-stroke. Straight polygon
# segments keep the whole outline ANGULAR — the deliberate non-rounded odd-one-
# out of the set. The forewing throws its leading edge up and out to x=63 and
# HOOKS: the apex spikes to a snake-head point (index 5) then cuts back under
# itself, leaving a cobra-head silhouette that survives the shrink. The
# hindwing below is large but still faceted, not an egg. Inner edges sit ~1px
# off the body axis so the mirrored pair nearly touches into one moth.
_WING_R = [
    (33, 30),   # 0  inner top, ~1px off axis
    (43, 20),   # 1  forewing leading edge
    (47, 12),   # 2  leading rise
    (55,  9),   # 3  toward the apex
    (60,  8),   # 4  apex base — start of the hook
    (63,  3),   # 5  SNAKE-HEAD TIP (eye-dot lands here)
    (61, 11),   # 6  hook cuts back under itself
    (58, 16),   # 7  forewing outer
    (57, 23),   # 8  forewing trailing
    (54, 28),   # 9  notch between fore- and hind-wing
    (58, 34),   # 10 hindwing outer shoulder
    (56, 45),   # 11 hindwing outer
    (48, 55),   # 12 hindwing lower outer
    (40, 58),   # 13 hindwing bottom lobe
    (34, 51),   # 14 inner bottom
    (33, 40),   # 15 inner mid, back to the axis
]

# Cream window triangles in the same right-wing space: one big pane in the
# forewing, one in the hindwing. Punched semi-transparent so they read as gaps
# in the wing where the sky shows through.
_WINDOWS_R = [
    [(44, 21), (55, 15), (50, 27)],   # forewing pane, pointing to the apex
    [(43, 37), (53, 41), (44, 49)],   # hindwing pane
]


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def _inset(pts, frac):
    """Shrink a polygon toward its centroid so successive fills leave concentric
    rings — that's how the maroon margin / ochre submarginal band / rust field
    stack up without any per-edge maths."""
    cx, cy = _centroid(pts)
    return [(x + (cx - x) * frac, y + (cy - y) * frac) for x, y in pts]


def _transform(pts, side, spread, nx):
    """Place a wing: mirror across the body axis for the left side, narrow it
    horizontally toward the axis on the up-stroke (edge-on), and lift it as the
    stroke rises. Shared by the outline AND its window triangles so the panes
    track the wing through the flap."""
    out = []
    for x, y in pts:
        dx = (x - BCX) * side
        out.append((BCX + dx * nx, y - spread))
    return out


def _punch_windows(ws, tris):
    """Turn the window triangles into true translucent panes: paint them cream
    over the opaque wing, then clamp ONLY their alpha down with a MIN blit so
    the composite lets sky through them instead of laying cream on top of rust.
    A MIN reducer leaves RGB untouched (255 everywhere) and only lowers alpha
    inside the triangles."""
    for tri in tris:
        pygame.draw.polygon(ws, CREAM, tri)
    reducer = _new()
    reducer.fill((255, 255, 255, 255))
    for tri in tris:
        pygame.draw.polygon(reducer, (255, 255, 255, WINDOW_ALPHA), tri)
    ws.blit(reducer, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)

    # Concentric rings = the Atlas moth's banding, but RUST has to dominate: a
    # deep-maroon margin, then only a THIN ochre submarginal band, then the
    # broad rust field that owns most of the wing. Windows punch that field.
    ws = _new()
    pygame.draw.polygon(ws, MAROON, margin)
    pygame.draw.polygon(ws, OCHRE, _inset(margin, 0.07))
    pygame.draw.polygon(ws, RUST, _inset(margin, 0.15))

    tris = [_transform(t, side, spread, nx) for t in _WINDOWS_R]
    _punch_windows(ws, tris)
    surf.blit(ws, (0, 0))

    # The snake-head eye at the hooked apex sells the cobra mimicry — a cream
    # sclera ring around a dark pupil with a warm catch, riding the transformed
    # apex vertex so it tracks the hook through the flap.
    ex, ey = margin[5]
    ex, ey = int(round(ex)), int(round(ey))
    cy = ey + 3
    if 1 <= ex < COMPOSITE_W - 1 and 1 <= cy < COMPOSITE_H - 1:
        pygame.draw.circle(surf, CREAM, (ex, cy), 3)
        pygame.draw.circle(surf, DARK, (ex, cy), 2)
        surf.set_at((ex, cy - 1), OCHRE_HI)


# Stout fusiform body: (y, half-width) keyframes, swelling at the thorax and
# tapering to a blunt abdomen tip. Wider than a butterfly's — moths are chunky.
_BODY_SEG = [(30, 2.6), (34, 5.4), (40, 6.4), (44, 6.1),
             (50, 5.2), (57, 3.6), (66, 1.6)]


def _body_halfw(y):
    seg = _BODY_SEG
    if y <= seg[0][0]:
        return seg[0][1]
    if y >= seg[-1][0]:
        return seg[-1][1]
    for (y0, w0), (y1, w1) in zip(seg, seg[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return w0 + (w1 - w0) * t
    return seg[-1][1]


def _draw_body(surf):
    left, right = [], []
    for y, hw in _BODY_SEG:
        left.append((BCX - hw, y))
        right.append((BCX + hw, y))
    poly = right + left[::-1]
    pygame.draw.polygon(surf, RUST, poly)

    # Rust/ochre abdominal bands with thin dark separators — the tell that keeps
    # the body reading as a banded moth abdomen even when the wings dominate.
    for i, y in enumerate(range(34, 62, 4)):
        hw = _body_halfw(y)
        col = OCHRE if i % 2 == 0 else MAROON
        pygame.draw.line(surf, col, (BCX - hw, y), (BCX + hw, y), 2)
        pygame.draw.line(surf, DARK, (BCX - hw, y + 2), (BCX + hw, y + 2), 1)

    # Warm inner gradient: a soft lit edge down the upper-left of the body so the
    # rust has volume rather than reading flat.
    pygame.draw.line(surf, OCHRE_HI, (BCX - 3, 33), (BCX - 2, 52), 1)
    # Fuzzy thorax mass for a plush, moth-like shoulder.
    _aaellipse(surf, MAROON, (BCX, 41), 6, 5)
    _aaellipse(surf, RUST, (BCX - 1, 40), 4, 3)
    _aaellipse(surf, OCHRE_HI, (BCX - 2, 39), 1, 1)


def _feather(surf, base, tip, teeth):
    """A bipectinate (comb) antenna: a shaft with short teeth fanning off both
    sides, shortening toward the tip. Reads unmistakably as a moth even shrunk —
    butterflies get clubbed antennae, moths get these feathers."""
    pygame.draw.line(surf, DARK, base, tip, 2)
    bx, by = base
    tx, ty = tip
    for i in range(1, teeth + 1):
        t = i / (teeth + 1)
        px = bx + (tx - bx) * t
        py = by + (ty - by) * t
        ln = 4.2 * (1 - t) + 1.5
        pygame.draw.line(surf, DARK, (px, py), (px - ln, py + ln * 0.35), 1)
        pygame.draw.line(surf, DARK, (px, py), (px + ln, py + ln * 0.35), 1)


def _draw_head(surf):
    # Broad feathery antennae first, sweeping up and out to the crown.
    _feather(surf, (HCX - 2, HCY - 2), (HCX - 10, CROWN_Y), 5)
    _feather(surf, (HCX + 2, HCY - 2), (HCX + 10, CROWN_Y), 5)
    # Small dark-rust head bead with two pin eyes and a warm catch.
    pygame.draw.circle(surf, MAROON, (HCX, HCY), 4)
    pygame.draw.circle(surf, DARK, (HCX - 2, HCY), 1)
    pygame.draw.circle(surf, DARK, (HCX + 2, HCY), 1)
    surf.set_at((HCX - 1, HCY - 2), OCHRE_HI)


def _apply_glow(surf):
    # Faint warm halo so the rust pops on bright day sky. Additive and applied
    # AFTER the outline so the outline traces only the crisp moth silhouette.
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for r, a in ((30, 6), (20, 7), (12, 7)):
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*RUST, a), (r, r), r)   # rust, not ochre — keep it warm-red not yellow
        glow.blit(g, (BCX + 2 - r, BCY - 4 - r))   # +2 for _add_outline pad
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = int(f * 16)            # lift the wings as the stroke rises
    nx = 1.0 - 0.28 * f             # narrow them toward edge-on on the up-stroke

    _draw_wing(surf, -1, spread, nx)
    _draw_wing(surf, +1, spread, nx)
    _draw_body(surf)
    _draw_head(surf)
    return surf


def _finish(wing_angle_deg):
    f = _add_outline(_build_frame(wing_angle_deg))
    _apply_glow(f)
    return f


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        _state["frames"] = [_finish(a) for a in _WING_ANGLES]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
