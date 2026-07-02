"""BUG/INSECT redesign — design_2 SUNSET MOTH (Madagascan sunset moth,
Chrysiridia rhipheus).

The showpiece of the Uraniidae: a jet-black day-flying moth whose broad
OBSIDIAN wings carry a few slim ribbons of molten rainbow iridescence and end
in a shallow scalloped edge with a pale cream fringe. As with AZUREWING the
wings are the whole story — a slim ink body hides behind two black sails that
fill the canvas wall-to-wall; black owns the wing, and only three thin arced
ribbons hug the outer-mid curve. A per-frame POLYCHROME hue-sweep rotates a
four-colour wheel so a different band leads each of the four flap frames and the
iridescence appears to flow. Black filamentous antennae (no clubs — it is a
moth) keep the read honest.

Scratch exploration only — NOT registered in store_skins.BUILDERS. Production
art stays untouched until a winner is picked.
"""
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse

COMPOSITE_W, COMPOSITE_H = 64, 84
BCX, BCY = 32, 44          # thorax centre
HCX, HCY = 44, 34          # head — poked up-right off the body axis (3/4 pose)
CROWN_Y = 24

# ── palette ──────────────────────────────────────────────────────────────────
OBSIDIAN = (14, 11, 20)     # DOMINANT jet-black wing base / margin / core
MAGENTA  = (224, 52, 138)   # sunset magenta — rainbow band 1
EMERALD  = (31, 184, 107)   # prism emerald — rainbow band 2
ORANGE   = (255, 122, 26)   # ember orange — rainbow band 3
VIOLET   = (150, 74, 214)   # twilight violet — rainbow band 4 (frame distinct)
CREAM    = (242, 228, 176)  # fringe cream — scalloped trailing edge
THORAX   = (16, 12, 22)     # slim body

# A four-colour wheel drives the hue-sweep so every one of the four flap frames
# has a distinct lead band (no two beats share a colour, unlike a 3-cycle).
WHEEL = [MAGENTA, EMERALD, ORANGE, VIOLET]

# Brightened cousins of the wheel for the additive shimmer — one per frame,
# matching that frame's lead band so the flare colour agrees with the ribbon.
SHIMMER = [(255, 120, 190), (120, 255, 180), (255, 190, 120), (200, 140, 255)]


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 0 = fully down-stroke (wings wide open), 1 = fully up-stroke (edge-on).
    return (a + 40) / 90.0


# Right-wing outer contour at the full-open pose. A broad triangular forewing
# throws its apex up-and-out to reach the 62px edge; the hindwing hangs below
# and its bottom margin is cut into three SHALLOW, WIDE scalloped lobes (the
# sunset moth's stubby edge) rather than deep dangling tails. Inner edge sits
# ~2px off the body axis so the mirrored left wing nearly meets it as one
# silhouette.
_WING_R = [
    (34, 29),   # 0 inner top, ~2px off the body axis
    (45, 14),   # 1 forewing leading rise
    (56, 11),   # 2 forewing apex — up and out
    (62, 21),   # 3 forewing outer shoulder — fills the width
    (61, 33),   # 4 forewing trailing outer
    (59, 41),   # 5 hindwing outer shoulder
    (55, 47),   # 6 scallop lobe A tip
    (50, 43),   # 7 wide notch
    (45, 47),   # 8 scallop lobe B tip
    (40, 43),   # 9 wide notch
    (36, 46),   # 10 scallop lobe C tip
    (34, 43),   # 11 inner bottom, ~2px off the body axis
]
# Trailing scallop margin the cream fringe traces (hindwing shoulder → inner).
FRINGE_IDX = range(5, 12)


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def _inset(pts, frac):
    """Shrink a polygon toward its centroid so concentric copies read as ribbons
    hugging the wing curve. Insetting preserves the scalloped bottom lobes as
    they close in, which keeps the edge read alive through the shrink."""
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


def _bands_for(fi):
    # The three visible ribbons (outer→inner) are three consecutive entries of
    # the four-colour wheel, offset by the frame index — so frame 0 leads
    # magenta, 1 emerald, 2 orange, 3 violet, and every frame is a distinct beat.
    r = fi % 4
    return [WHEEL[(r + k) % 4] for k in range(3)]


def _draw_wing(surf, side, spread, nx, fi):
    margin = _transform(_WING_R, side, spread, nx)

    # Obsidian OWNS the wing: the whole face is filled black, then only three
    # SLIM iridescent ribbons are STROKED along inset copies of the wing
    # contour. A width-2 polygon outline gives a uniformly thin arc that hugs the
    # wing curve at a fixed inset — so the ribbon never fattens on the compact
    # hindwing (the filled-ring trap) and never touches the wing edge, leaving a
    # fat black margin and a fat black core. A small per-frame drift breathes the
    # ribbons outward and in.
    drift = (fi - 1.5) * 0.02
    centers = [0.40 + drift, 0.53 + drift, 0.66 + drift]
    bands = _bands_for(fi)

    pygame.draw.polygon(surf, OBSIDIAN, margin)
    for c, col in zip(centers, bands):
        pygame.draw.polygon(surf, col, _inset(margin, c), 2)

    # Per-frame polychrome shimmer rides the OUTER ribbon, not the wing core, so
    # the centre stays black: two soft ellipses in the frame's brightened lead
    # colour, clipped to the wing face, fake the molten angle-dependent flare
    # that gives the sunset moth its name.
    cx, cy = _centroid(margin)
    ox, oy = margin[3]                     # outer shoulder — the outer-mid wing
    ax = cx + (ox - cx) * 0.5
    ay = cy + (oy - cy) * 0.5
    shift = (fi - 1.5) * 3
    scol = SHIMMER[fi % 4]
    sh = _new()
    for k in range(2):
        _aaellipse(sh, (*scol, 30), (ax + shift, ay - 4 + k * 8), 6, 4)
    sh.blit(_wing_mask(_inset(margin, 0.11)), (0, 0),
            special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sh, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Cream fringe: a short pale stroke tracing the shallow scalloped trailing
    # margin — the non-hue accessibility anchor, thick enough to survive 40px.
    fringe = [(int(margin[i][0]), int(margin[i][1])) for i in FRINGE_IDX]
    pygame.draw.lines(surf, CREAM, False, fringe, 2)


def _draw_body(surf):
    # A short dark neck bridges the thorax up-right to the head (3/4 pose); the
    # near wing overlaps its base so only a sliver shows.
    pygame.draw.line(surf, THORAX, (BCX, BCY - 4), (HCX - 2, HCY + 2), 5)
    # Slim abdomen leaning down toward the lower-left, mostly hidden by wings.
    pygame.draw.polygon(surf, THORAX, [
        (BCX - 3, BCY), (BCX + 3, BCY),
        (BCX - 1, BCY + 15), (BCX - 5, BCY + 14),
    ])
    _aaellipse(surf, THORAX, (BCX, BCY), 5, 7)
    _aaellipse(surf, (34, 26, 44), (BCX - 1, BCY - 2), 2, 4)   # faint sheen


def _draw_head(surf):
    # Two thin BLACK filamentous antennae fanning up to the crown. No clubbed
    # tips — the tell that separates a moth from AZUREWING's butterfly clubs.
    for tx in (HCX - 4, HCX + 5):
        sx = HCX + (1 if tx > HCX else -1)
        sy = HCY - 3
        mx = (sx + tx) / 2 + (2 if tx > HCX else -2)
        my = (sy + CROWN_Y) / 2 - 1
        pygame.draw.lines(surf, OBSIDIAN, False,
                          [(sx, sy), (mx, my), (tx, CROWN_Y)], 1)
    # Small dark head with a faint catch-light.
    pygame.draw.circle(surf, OBSIDIAN, (HCX, HCY), 4)
    pygame.draw.circle(surf, (70, 58, 82), (HCX - 1, HCY - 1), 1)


def _build_frame(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)
    try:
        fi = _WING_ANGLES.index(int(round(wing_angle_deg)))
    except ValueError:
        fi = 0
    spread = int(f * 18)           # lift the wings as the stroke rises
    # Cap the horizontal narrowing so the edge-on up-stroke still reads winged;
    # the lifted spread angle carries the "wings raised" gesture.
    nx = 1.0 - 0.30 * f

    # Far (left) wing behind the body, near (right) wing over the roots.
    _draw_wing(surf, -1, spread, nx, fi)
    _draw_body(surf)
    _draw_wing(surf, +1, spread, nx, fi)
    _draw_head(surf)
    return surf


def _apply_glow(outlined, fi):
    # Outer glow goes on top of the ALREADY-outlined sprite: an additive halo
    # painted before the outline would trip _add_outline's silhouette mask and
    # sprout a ring around the glow itself. The halo is a whisper — low alpha and
    # a tight radius — so the obsidian body never blooms into a flame on a night
    # sky; it just lets the wing's lead colour breathe at the silhouette edge.
    out = outlined.copy()
    w, h = out.get_size()
    cx, cy = w // 2, h // 2 - 2
    col = _bands_for(fi)[0]
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    for r, a in ((24, 4), (18, 3), (12, 2)):
        g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(g, (*col, a), (r, r), r)
        glow.blit(g, (cx - r, cy - r))
    out.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return out


_state = {"frames": None, "rot": {}}


def build(frame_idx: int, tilt_deg: float) -> pygame.Surface:
    if _state["frames"] is None:
        base = [_add_outline(_build_frame(a)) for a in _WING_ANGLES]
        _state["frames"] = [_apply_glow(s, fi) for fi, s in enumerate(base)]
    frame_idx %= 4
    key = (frame_idx, int(round(tilt_deg / 3)) * 3)
    if key not in _state["rot"]:
        _state["rot"][key] = pygame.transform.rotozoom(
            _state["frames"][frame_idx], key[1], 1.0)
    return _state["rot"][key]
