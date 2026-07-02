"""BUG/INSECT redesign — design_2 SUNSET MOTH (Madagascan sunset moth,
Chrysiridia rhipheus).

The showpiece of the Uraniidae: a jet-black day-flying moth whose broad wings
carry curved bands of molten rainbow iridescence and end in a short row of
scalloped tails with a pale cream fringe. As with AZUREWING the wings are the
whole story — a slim ink body hides behind two obsidian sails that fill the
canvas wall-to-wall; concentric arced bands of magenta → emerald → orange hug
the wing curve, and a per-frame POLYCHROME hue-sweep rotates which colour
dominates across the four flap frames so the iridescence appears to flow.
Black filamentous antennae (no clubs — it is a moth) keep the read honest.

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
CREAM    = (242, 228, 176)  # fringe cream — scalloped tail dots
THORAX   = (16, 12, 22)     # slim body

# Brightened cousins of the band trio for the additive shimmer sweep — the same
# rotation the bands use, so the flare colour agrees with the band it lights.
SHIMMER = [(255, 120, 190), (120, 255, 180), (255, 190, 120), (255, 120, 190)]


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _flap(a):
    # 0 = fully down-stroke (wings wide open), 1 = fully up-stroke (edge-on).
    return (a + 40) / 90.0


# Right-wing outer contour at the full-open pose. A broad triangular forewing
# throws its apex up-and-out to reach the 62px edge; the hindwing hangs below
# and its bottom margin is cut into three short scalloped lobes (the sunset
# moth's stubby tails) rather than one long streamer. Inner edge sits ~2px off
# the body axis so the mirrored left wing nearly meets it as one silhouette.
_WING_R = [
    (34, 29),   # 0 inner top, ~2px off the body axis
    (45, 14),   # 1 forewing leading rise
    (56, 11),   # 2 forewing apex — up and out
    (62, 21),   # 3 forewing outer shoulder — fills the width
    (61, 33),   # 4 forewing trailing outer
    (59, 41),   # 5 hindwing outer shoulder
    (56, 49),   # 6 scallop lobe A (outer tail)      ← fringe tip
    (52, 45),   # 7 notch
    (49, 53),   # 8 scallop lobe B (main tail)       ← fringe tip
    (44, 47),   # 9 notch
    (40, 52),   # 10 scallop lobe C (inner tail)     ← fringe tip
    (36, 46),   # 11 notch
    (34, 44),   # 12 inner bottom, ~2px off the body axis
]
SCALLOP_TIPS = (6, 8, 10)


def _centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)


def _inset(pts, frac):
    """Shrink a polygon toward its centroid so concentric copies read as bands
    hugging the wing curve. Insetting preserves the scalloped bottom lobes as
    they close in, which keeps the tail read alive through the shrink."""
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
    # Rotate the magenta/emerald/orange trio by the frame index so a different
    # colour owns the outer band each beat — frame 0 magenta, 1 emerald, 2
    # orange, 3 back toward magenta — the polychrome analogue of the morpho
    # shimmer.
    r = fi % 3
    trio = [MAGENTA, EMERALD, ORANGE]
    return trio[r:] + trio[:r]


def _draw_wing(surf, side, spread, nx, fi):
    margin = _transform(_WING_R, side, spread, nx)

    # Obsidian margin holds the silhouette; then three concentric arced bands of
    # the rotated rainbow trio are stamped outer→inner, each smaller inset laid
    # over the last, with a dark core so the wing centre stays black like the
    # real moth. A tiny per-frame drift on the ring stops makes the bands appear
    # to breathe outward and in, so even the two frames that share a colour
    # rotation read as different beats.
    drift = (fi - 1.5) * 0.015
    fracs = [0.14 + drift, 0.33 + drift, 0.52 + drift, 0.71]
    bands = _bands_for(fi)

    pygame.draw.polygon(surf, OBSIDIAN, margin)
    for frac, col in zip(fracs[:3], bands):
        pygame.draw.polygon(surf, col, _inset(margin, frac))
    pygame.draw.polygon(surf, OBSIDIAN, _inset(margin, fracs[3]))

    # Per-frame polychrome shimmer clipped to the wing face: a bright column of
    # ellipses in the frame's lead colour sweeps across the wing (same screen
    # direction on both wings, so it flows as one gesture), faking the molten
    # angle-dependent flare that gives the sunset moth its name.
    fill = _inset(margin, 0.11)
    fcx, fcy = _centroid(fill)
    shift = (fi - 1.5) * 5
    scol = SHIMMER[fi]
    sh = _new()
    for k in range(3):
        _aaellipse(sh, (*scol, 58), (fcx + shift, fcy - 11 + k * 9), 7, 4)
    _aaellipse(sh, (255, 255, 255, 40), (fcx + shift * 0.6, fcy - 4), 4, 3)
    sh.blit(_wing_mask(fill), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surf.blit(sh, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Cream fringe: pale scale-dots marching along the scalloped tail tips — the
    # non-hue accessibility anchor that survives 40px on both skies.
    for idx in SCALLOP_TIPS:
        mx, my = margin[idx]
        pygame.draw.circle(surf, CREAM, (int(mx), int(my)), 2)


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
    # sprout a ring around the glow itself. The halo takes the frame's lead band
    # colour so the bloom agrees with the wing and reads on a dark night sky.
    out = outlined.copy()
    w, h = out.get_size()
    cx, cy = w // 2, h // 2 - 2
    col = _bands_for(fi)[0]
    glow = pygame.Surface((w, h), pygame.SRCALPHA)
    for r, a in ((32, 8), (24, 8), (16, 6)):
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
