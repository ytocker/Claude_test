"""BUG/INSECT redesign — design_5 ATLASWING (Atlas moth, Attacus atlas).

The wings are the whole story. Two WIDE ANGULAR sails spread horizontally,
their leading edges rising to nearly meet along the top axis so the silhouette
reads as one flat-topped moth — never two peaked "ears" over a head. Each
forewing corner hooks out sideways into a pointed SNAKE-HEAD tip with a dark
eye-dot riding a cream field — the Atlas moth's cobra-mimicry tell and the only
jagged, non-rounded silhouette in the set. One bold cream TRIANGULAR WINDOW per
wing is punched semi-transparent so the day sky bleeds through it. A deep-maroon
outer margin wraps the whole edge for value pop on both bright and dark skies. A
stout rust/ochre banded body and broad feathery comb antennae — swept clear of
the wing junction — seat the read as a moth, not a butterfly.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre
# Head kept ON the body axis, but seated LOW (below where the two forewings
# close flat at the top) so it can never read as a face between two ear-peaks.
HCX, HCY = 32, 29
CROWN_Y = 13

# ── palette ──────────────────────────────────────────────────────────────────
RUST   = (155, 74, 42)     # #9B4A2A Atlas Rust — DOMINANT wing field
MAROON = (94, 35, 32)      # #5E2320 deep maroon — outer margin / forewing base
OCHRE  = (216, 154, 84)    # #D89A54 ochre submarginal band + body bands
CREAM  = (243, 230, 200)   # #F3E6C8 translucent triangular window panes
DARK   = (36, 21, 18)      # #241512 snake-tip / eye-dot / body outline
OCHRE_HI = (238, 190, 128) # warm highlight for the body gradient / catch-lights

WINDOW_ALPHA = 55          # low enough that sky visibly bleeds through the panes


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 1 = up-stroke (wings lifted, edge-on), 0 = down-stroke (wings wide open).
    return (a + 40) / 90.0


# Right-wing outer contour at the full-open down-stroke. Straight polygon
# segments keep the whole outline ANGULAR — the deliberate non-rounded odd-one-
# out of the set. The leading edge rises to the TOP AXIS (index 0 sits on x=32,
# high) so the mirrored pair closes into one flat-topped moth with no central
# V-notch — that kills the fox/cat-face pareidolia. The forewing corner then
# hooks SIDEWAYS to the widest point (index 4) and cuts back under itself
# (index 5, a concave undercut), leaving a cobra-head apex. The hindwing below
# is large but still faceted, not an egg.
_WING_R = [
    (32, 15),   # 0  inner top ON the axis — the top edge stays LEVEL across
    (44, 15),   # 1  leading edge holds level (no upward peak = no ear)
    (54, 15),   # 2  level toward the apex
    (61, 16),   # 3  apex base
    (63, 20),   # 4  SNAKE-HEAD TIP — hooks sideways/DOWN to the widest point
    (59, 23),   # 5  concave undercut back beneath the tip
    (60, 28),   # 6  forewing trailing
    (55, 32),   # 7  shallow notch between fore- and hind-wing
    (59, 39),   # 8  hindwing outer shoulder
    (56, 47),   # 9  hindwing outer
    (48, 55),   # 10 hindwing lower outer
    (39, 57),   # 11 hindwing bottom lobe
    (34, 50),   # 12 inner bottom
    (32, 33),   # 13 inner mid, back on the axis
]

# The snake-head eye rides HERE — a point that sits squarely inside the forewing
# cream window so the dark pupil has cream contrast, not lost on the dark tip.
_EYE_R = (55, 21)

# One bold cream window per wing (fewer/bigger survives 40px). The forewing pane
# reaches up to cradle the eye; the hindwing pane is a single clear triangle.
_WINDOWS_R = [
    [(45, 17), (61, 18), (52, 29)],   # forewing pane — the eye rides this cream
    [(42, 37), (55, 42), (44, 52)],   # hindwing pane
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
    # A crisp 1px dark rim re-opaques each pane's border so the translucent panes
    # stay defined windows instead of bleeding into the rust field at 40px.
    for tri in tris:
        pygame.draw.polygon(ws, DARK, tri, 1)


def _draw_wing(surf, side, spread, nx):
    margin = _transform(_WING_R, side, spread, nx)

    # Concentric rings = the Atlas moth's banding. A WIDE deep-maroon outer
    # margin now carries the whole edge dark (that's what holds the angular
    # silhouette against BOTH bright day and dark night sky), then a thin ochre
    # submarginal band, then the broad rust field. Windows punch that field.
    ws = _new()
    pygame.draw.polygon(ws, MAROON, margin)
    pygame.draw.polygon(ws, OCHRE, _inset(margin, 0.13))
    pygame.draw.polygon(ws, RUST, _inset(margin, 0.24))

    tris = [_transform(t, side, spread, nx) for t in _WINDOWS_R]
    _punch_windows(ws, tris)
    surf.blit(ws, (0, 0))

    # The snake-head eye sells the cobra mimicry — a dark pupil with a warm
    # catch, sitting on the forewing CREAM field (transformed with the wing so
    # it tracks the hook through the flap) for hard contrast at 40px.
    ex, ey = _transform([_EYE_R], side, spread, nx)[0]
    ex, ey = int(round(ex)), int(round(ey))
    if 1 <= ex < COMPOSITE_W - 1 and 1 <= ey < COMPOSITE_H - 1:
        pygame.draw.circle(surf, DARK, (ex, ey), 2)
        surf.set_at((ex, ey - 1), OCHRE_HI)


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
    # Feathery antennae swept OUT over the forewing shoulders — kept well clear
    # of the wing junction so they can never read as ears above a face.
    _feather(surf, (HCX - 2, HCY - 1), (HCX - 13, CROWN_Y), 5)
    _feather(surf, (HCX + 2, HCY - 1), (HCX + 13, CROWN_Y), 5)
    # A small DARK thorax knob — deliberately recessive (no pin eyes, no
    # catch-light) so the two hooked apex eye-dots own the focal hierarchy
    # instead of competing with a bright central "face" bead.
    pygame.draw.circle(surf, DARK, (HCX, HCY), 3)


def _apply_glow(surf):
    # A whisper of a halo — MAROON-tinted and low-alpha so it never cooks the
    # earthy maroon into neon orange. The deep-maroon outer margin does the real
    # silhouette-holding work; this only softens the edge against bright sky.
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for r, a in ((30, 3), (20, 3), (12, 4)):
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*MAROON, a), (r, r), r)
        glow.blit(g, (BCX + 2 - r, BCY - 4 - r))   # +2 for _add_outline pad
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    spread = int(f * 11)            # lift the wings as the stroke rises (top-safe)
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
