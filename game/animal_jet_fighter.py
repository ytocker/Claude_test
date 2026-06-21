"""Production JET FIGHTER store skin — STEEL RAPTOR, round-2 converged build.

The priciest secret skin turns the player's flapping macaw into a sleek
NON-creature war machine. There is no flapping: the 4 base wing poses
(`parrot._WING_ANGLES`) are reinterpreted as an AFTERBURNER PULSE — the
baked exhaust glow flares and shrinks across the 4 frames and the nose
pitches a touch. No live particle system; the spectacle is baked per frame.

Round-2 direction (art-director, ITERATE on v1 STEEL RAPTOR):

  * De-blobbed twin burner: the two nozzles sit on a WIDE gap so two
    white-hot cores stay distinct at 40px even on the hottest dive frame;
    each plume carries its own tight halo instead of one fused orange mass.
  * Burner supports, never swallows: peak glow is capped to the rear third
    of the silhouette so the arrowhead nose + delta stay the dominant read.
  * VALUE-based wing accent (not a single low-contrast red hue that dies on
    day): a darker gunmetal leading-edge outline + a brighter top-facet
    highlight, so the wing edge reads by LUMINANCE on both skies. Red is
    kept only as a small warm accent (radar dot, wingtip rail cap).
  * ONE premium signature: a thin WARM hot rim-light tracing the delta
    leading edges, tied to the burner's colour temperature. It is the
    "most expensive" tell AND it rescues the night silhouette (no chrome
    spine — one signature, picked deliberately).
  * Cool blue canopy dot is the CONSTANT anchor across all 4 frames,
    colourblind-distinct from the warm burner; it never washes out.

Contract (mirrors game/animal_skins.py so this lifts straight into a
production game/animal_jet_fighter.py later):

  * `build_jet_fighter(wing_angle_deg) -> pygame.Surface`  draws one flat
    frame on a 64×84 SRCALPHA canvas, fuselage mass centred at (32,44).
  * `get_jet_fighter`: a cached `(frame_idx, tilt_deg) -> Surface` getter
    from `_make_prebuilt_skin(build_jet_fighter)` (4 flat frames + per-
    (frame, 3°) rotation cache, each outlined with the house outline).
  * `BUILDERS = {"skin_jet_fighter": get_jet_fighter}` for the review sheet
    and the production registry.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, so the fuselage mass stays near the base bird's body centre
((32,44) on the 64×84 canvas) for fairness — wings may span wider, but the
body stays anchored so the in-game center-blit rotation maths still holds.
"""
import math
import pygame

from game import parrot
from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + body anchor (mirror animal_skins composite layout) ──────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # matches the creature composite height
DY          = 12
BCX, BCY = 32, 32 + DY          # fuselage centre → (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter for a full-body
    build_fn(angle): lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _pulse(angle_deg):
    """Afterburner pulse phase from the wing angle: the 4 poses (50→-40) map
    to a 0..1 'throttle' so the baked flame flares brightest on the middle
    two frames and shrinks at the ends — a heartbeat the eye reads as thrust.

    Triangle-wrapped so the read is bright-bright in the centre, dim-dim at
    the ends: a perceptible throttle pulse at 40px without strobing."""
    t = (50 - angle_deg) / 90.0          # 50→0, 20→.33, -10→.67, -40→1
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the jet visibly 'breathes'
    with the burner instead of sitting dead-still. ±1px is enough at 40px."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _baked_flame(length, width, core, mid, outer):
    """Bake ONE afterburner plume onto its own SRCALPHA surface: a layered
    teardrop — outer haze → mid → white-hot core — with shock-diamond beads
    down the centre. Pre-baking (vs a live particle system) keeps both build
    targets identical and cheap.

    The core layer is kept NARROW relative to the haze so that when two of
    these sit on the twin nozzles the two WHITE cores stay visually separate
    at 40px even though their soft outer hazes may kiss.

    Returns a surface whose LEFT edge is the nozzle mouth; the plume streams
    to the RIGHT, so callers blit it pointing aft and the jet flies left."""
    pad = 6
    w = length + pad * 2
    h = width + pad * 2
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cy = h // 2

    def teardrop(col, ln, hw, alpha):
        pts = []
        n = 14
        for i in range(n + 1):
            t = i / n
            x = pad + t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy - r))
        for i in range(n + 1):
            t = (n - i) / n
            x = pad + t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy + r))
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(layer, (*col, alpha), pts)
        surf.blit(layer, (0, 0))

    teardrop(outer, length,             width / 2.0,  140)
    teardrop(mid,   int(length * 0.74), width / 3.0,  210)
    teardrop(core,  int(length * 0.46), width / 5.0,  255)
    # White-hot pinch right at the nozzle mouth (a tight, bright core seed).
    pygame.draw.circle(surf, (255, 255, 255, 255), (pad + 2, cy), max(1, width // 8))
    # Shock diamonds: a couple of bright beads marching down the narrow core.
    for k in range(1, 3):
        dx = pad + int(length * 0.16 * k) + 2
        rad = max(1, width // 10 - (k - 1))
        pygame.draw.circle(surf, (255, 250, 232, 235), (dx, cy), rad)
    return surf


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the warm aura behind the burner.
    Concentric fading rings so the glow supports the silhouette, never
    swallows it. Radius is held small (rear-third cap) on the hottest frame
    by the caller so the nose stays the dominant read."""
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = int(radius * i / steps)
        pygame.draw.circle(s, (*color, a), (radius, radius), r)
    return s


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


# ═════════════════════════════════════════════════════════════════════════════
# STEEL RAPTOR — top-down planform, gunmetal steel, sharp delta wings, twin
#   canted tail fins, twin afterburner. The textbook "fighter jet" read:
#   arrowhead body, swept delta, two hot flames aft. Premium signature = a
#   thin WARM rim-light tracing the delta leading edges.
# ═════════════════════════════════════════════════════════════════════════════
_BODY    = (120, 128, 140)
_BODY_D  = (74, 80, 92)
_BODY_H  = (182, 190, 202)
_EDGE    = (44, 48, 58)          # darker-than-body gunmetal outline (value tell)
_RED     = (216, 60, 54)         # small warm accent only
_RIM     = (255, 196, 120)       # warm hot rim-light — THE premium signature
_RIM_HOT = (255, 232, 190)
_CANOPY  = (58, 150, 200)        # constant cool anchor
_CANOPY_H = (176, 228, 250)

# Twin nozzles sit on a WIDE vertical gap so the two white-hot cores never
# fuse into one orange mass at 40px (the round-1 de-blob fix).
_NOZ_DY = 8


def build_jet_fighter(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    # Jet flies LEFT: nose points left (−x), exhaust streams right (+x).
    nose_x = 12 + pit
    tail_x = 50

    # ── Twin afterburner ─────────────────────────────────────────────────
    # Each nozzle gets its OWN tight halo (not one shared blob), and the halo
    # radius is capped so peak glow stays in the rear third of the silhouette.
    flame_len = int(13 + p * 11)
    halo_r = int((10 + p * 5) * 0.84)        # ~16-20% smaller on the hot frame
    glow = _glow(halo_r, (255, 150, 64), alpha=int(60 + p * 60))
    flame = _baked_flame(flame_len, 8, (255, 255, 244), (255, 168, 60),
                         (236, 72, 36))
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        _blit_c(surf, glow, (tail_x + flame_len // 2 - 2, ny))
        surf.blit(flame, (tail_x - 2, ny - flame.get_height() // 2))

    # ── Twin canted tail fins (drawn before body so body overlaps the root) ─
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _BODY_D, [
            (tail_x - 6, BCY + sgn * 4), (tail_x + 6, BCY + sgn * 13),
            (tail_x + 9, BCY + sgn * 12), (tail_x + 2, BCY + sgn * 3)])

    # ── Delta wing pair, swept hard back from mid-fuselage ────────────────
    for sgn in (-1, 1):
        # Filled wing: dark underside band first, then the lit top facet.
        pygame.draw.polygon(surf, _BODY_D, [
            (nose_x + 18, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 20),
            (tail_x + 4, BCY + sgn * 20), (tail_x - 6, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _BODY, [
            (nose_x + 19, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 18),
            (tail_x - 7, BCY + sgn * 6)])
        # Brighter top-facet highlight: value-based wing read on day AND night.
        pygame.draw.polygon(surf, _BODY_H, [
            (nose_x + 20, BCY + sgn * 2), (nose_x + 30, BCY + sgn * 7),
            (tail_x - 8, BCY + sgn * 7), (tail_x - 7, BCY + sgn * 6)])
        # Darker gunmetal leading-edge OUTLINE — reads by luminance, not hue.
        pygame.draw.line(surf, _EDGE, (nose_x + 19, BCY + sgn * 2),
                         (tail_x - 4, BCY + sgn * 18), 1)
        # Wingtip missile rail with a tiny red accent cap.
        pygame.draw.line(surf, _BODY_H, (tail_x - 4, BCY + sgn * 18),
                         (tail_x + 4, BCY + sgn * 18), 2)
        pygame.draw.circle(surf, _RED, (tail_x + 4, BCY + sgn * 18), 1)

    # ── Dart fuselage: long arrowhead ─────────────────────────────────────
    body = [(nose_x, BCY), (nose_x + 16, BCY - 6), (tail_x + 4, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 4, BCY + 5), (nose_x + 16, BCY + 6)]
    pygame.draw.polygon(surf, _BODY, body)
    pygame.draw.polygon(surf, _EDGE, body, 1)
    # Top centreline highlight (catches light along the spine).
    pygame.draw.polygon(surf, _BODY_H,
                        [(nose_x + 4, BCY - 1), (nose_x + 16, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    # Nose cone tip + small red radar dot.
    pygame.draw.polygon(surf, _BODY_D,
                        [(nose_x, BCY), (nose_x + 7, BCY - 2),
                         (nose_x + 7, BCY + 2)])
    pygame.draw.circle(surf, _RED, (nose_x + 1, BCY), 1)

    # ── Premium signature: thin WARM rim-light on the delta leading edges ──
    # Tied to the burner colour temperature; lifts the gunmetal off a dark
    # night sky and is the single "most expensive" tell.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _RIM, (nose_x + 20, BCY + sgn * 2),
                         (tail_x - 5, BCY + sgn * 17), 1)
    # Hot spark at each leading-edge root where the rim is brightest.
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _RIM_HOT, (nose_x + 20, BCY + sgn * 2), 1)
    # Warm rim along the nose chine too, so the arrowhead glints.
    pygame.draw.line(surf, _RIM, (nose_x + 2, BCY - 1), (nose_x + 15, BCY - 5), 1)

    # ── Bubble canopy: the CONSTANT cool anchor across all 4 frames ───────
    _aaellipse(surf, _CANOPY, (nose_x + 14, BCY), 5, 3)
    _aaellipse(surf, _CANOPY_H, (nose_x + 12, BCY - 1), 2, 1)
    pygame.draw.circle(surf, _CANOPY_H, (nose_x + 12, BCY - 1), 1)
    # Twin engine nozzle mouths glowing where the flames root (wide gap).
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        pygame.draw.circle(surf, (255, 206, 130), (tail_x, ny), 2)
        pygame.draw.circle(surf, (255, 255, 245), (tail_x - 1, ny), 1)

    # Secret-skin signature: fly INVERTED with the nose pitched up. The planform
    # is drawn nose-left / canopy-up, so a 205° spin lands it nose-forward (the
    # bird faces right), belly-up, in a cocky nose-high attitude.
    return pygame.transform.rotate(surf, 205)


get_jet_fighter = _make_prebuilt_skin(build_jet_fighter)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry: the single registered skin lifts into
# game/animal_jet_fighter.py as get_jet_fighter.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {"skin_jet_fighter": get_jet_fighter}
