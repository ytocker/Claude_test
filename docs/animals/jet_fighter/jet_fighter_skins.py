"""Candidate JET FIGHTER store skins — round-1 exploration.

The priciest secret skin turns the player's flapping macaw into a sleek
NON-creature war machine. There is no flapping: the 4 base wing poses
(`parrot._WING_ANGLES`) are reinterpreted as an AFTERBURNER PULSE — the
baked exhaust glow flares and shrinks across the 4 frames and the nose
pitches a touch. No live particle system; the spectacle is baked per frame.

Contract (mirrors game/animal_skins.py so the winner lifts straight into a
production game/animal_jet_fighter.py later):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  draws one flat frame
    on a 64×84 SRCALPHA canvas, fuselage mass centred at (32,44).
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)` (4 flat frames + per-(frame, 3°) rotation
    cache, each outlined with the house silhouette outline).
  * a label→getter dict at the bottom for the review sheet.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, so the fuselage mass stays near the base bird's body centre
((32,44) on the 64×84 canvas) for fairness — wings may span wider, but the
body stays anchored so the in-game center-blit rotation maths still holds.

North star: one bold swept-wing silhouette + one tell (the glowing
afterburner) that both survive the 40px downscale on day AND night.
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
    to a 0..1 'throttle' so the baked flame flares brightest on one frame and
    shrinks toward the next — a heartbeat the eye reads as engine thrust."""
    # 50→0.0, 20→0.33, -10→0.67, -40→1.0, then triangle-wrap for a pulse.
    t = (50 - angle_deg) / 90.0
    return 1.0 - abs(t * 2.0 - 1.0)          # peak in the middle two frames


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the jet visibly 'breathes'
    with the burner instead of sitting dead-still. ±1px is enough at 40px."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _baked_flame(length, width, core, mid, outer, *, diamonds=True):
    """Bake an afterburner plume onto its own SRCALPHA surface: a layered
    teardrop of additive-feeling rings — outer haze → mid → white-hot core —
    with optional shock-diamond beads down the centre. Pre-baking (vs a live
    particle system) keeps both build targets identical and cheap.

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
            # Fat near the mouth, tapering to a point at the tail.
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

    teardrop(outer, length,            width / 2.0,        150)
    teardrop(mid,    int(length * 0.78), width / 2.6,       210)
    teardrop(core,   int(length * 0.50), width / 4.2,       255)
    # White-hot pinch right at the nozzle mouth.
    pygame.draw.circle(surf, (255, 255, 255, 255), (pad + 2, cy), max(2, width // 6))
    if diamonds:
        # Shock diamonds: a few bright beads marching down the core.
        for k in range(1, 4):
            dx = pad + int(length * 0.12 * k) + 3
            rad = max(1, width // 8 - k)
            pygame.draw.circle(surf, (255, 250, 230, 230), (dx, cy), rad)
    return surf


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the premium 'wow' aura behind the burner.
    Concentric fading rings so the glow supports the silhouette, never swallows."""
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
# v1 · STEEL RAPTOR — top-down planform, gunmetal steel + red accents, sharp
#     delta wings, twin canted tail fins, TWIN afterburner. The textbook
#     "fighter jet" read: arrowhead body, swept delta, hot twin flames aft.
# ═════════════════════════════════════════════════════════════════════════════
_R_BODY   = (118, 126, 138)
_R_BODY_D = (78, 84, 96)
_R_BODY_H = (176, 184, 196)
_R_EDGE   = (52, 56, 66)
_R_RED    = (214, 58, 52)
_R_CANOPY = (60, 150, 196)
_R_CANOPY_H = (170, 224, 248)


def build_jet_fighter_v1(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    # Jet flies LEFT: nose points left (−x), exhaust streams right (+x).
    nose_x = 12 + pit
    tail_x = 50

    # Twin afterburner: baked glow halo then layered flame, aft of the nozzles.
    flame_len = int(14 + p * 12)
    glow = _glow(int(13 + p * 8), (255, 150, 60), alpha=int(70 + p * 70))
    _blit_c(surf, glow, (tail_x + flame_len // 2, BCY))
    flame = _baked_flame(flame_len, 9, (255, 255, 240), (255, 170, 60),
                         (240, 70, 36))
    for ny in (BCY - 6, BCY + 6):
        surf.blit(flame, (tail_x - 2, ny - flame.get_height() // 2))

    # Twin canted tail fins (drawn before body so body overlaps their root).
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _R_BODY_D, [
            (tail_x - 6, BCY + sgn * 4), (tail_x + 6, BCY + sgn * 13),
            (tail_x + 9, BCY + sgn * 12), (tail_x + 2, BCY + sgn * 3)])

    # Delta wing pair, swept hard back from mid-fuselage.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _R_BODY_D, [
            (nose_x + 18, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 20),
            (tail_x + 4, BCY + sgn * 20), (tail_x - 6, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _R_BODY, [
            (nose_x + 19, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 18),
            (tail_x - 7, BCY + sgn * 6)])
        # Red leading-edge accent.
        pygame.draw.line(surf, _R_RED, (nose_x + 19, BCY + sgn * 2),
                         (tail_x - 4, BCY + sgn * 18), 1)
        # Wingtip missile rail.
        pygame.draw.line(surf, _R_BODY_H, (tail_x - 4, BCY + sgn * 18),
                         (tail_x + 4, BCY + sgn * 18), 2)

    # Dart fuselage: long arrowhead.
    body = [(nose_x, BCY), (nose_x + 16, BCY - 6), (tail_x + 4, BCY - 5),
            (tail_x + 6, BCY), (tail_x + 4, BCY + 5), (nose_x + 16, BCY + 6)]
    pygame.draw.polygon(surf, _R_BODY, body)
    pygame.draw.polygon(surf, _R_EDGE, body, 1)
    # Top centreline highlight (catches light along the spine).
    pygame.draw.polygon(surf, _R_BODY_H,
                        [(nose_x + 4, BCY - 1), (nose_x + 16, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    # Nose cone tip + radar dot.
    pygame.draw.polygon(surf, _R_BODY_D,
                        [(nose_x, BCY), (nose_x + 7, BCY - 2),
                         (nose_x + 7, BCY + 2)])
    pygame.draw.circle(surf, _R_RED, (nose_x + 1, BCY), 1)

    # Bubble canopy just aft of the nose.
    _aaellipse(surf, _R_CANOPY, (nose_x + 14, BCY), 5, 3)
    _aaellipse(surf, _R_CANOPY_H, (nose_x + 12, BCY - 1), 2, 1)
    # Twin engine nozzles glowing where the flames root.
    for ny in (BCY - 6, BCY + 6):
        pygame.draw.circle(surf, (255, 200, 120), (tail_x, ny), 2)
    return surf


get_jet_fighter_v1 = _make_prebuilt_skin(build_jet_fighter_v1)


# ═════════════════════════════════════════════════════════════════════════════
# v2 · TOP GUN NAVY — aggressive 3/4 view, navy-blue + white livery, variable
#     swept wings, a big prominent bubble canopy, SINGLE fat afterburner. The
#     hot-shot carrier jet: bold blue body, white star roundel, gold trim.
# ═════════════════════════════════════════════════════════════════════════════
_N_BODY   = (38, 64, 122)
_N_BODY_D = (24, 42, 84)
_N_BODY_H = (88, 124, 190)
_N_WHITE  = (236, 240, 248)
_N_GOLD   = (244, 200, 90)
_N_CANOPY = (40, 60, 84)
_N_CANOPY_H = (150, 210, 240)


def build_jet_fighter_v2(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 8 + pit
    tail_x = 48

    # Single big afterburner with a generous halo (the 3/4 view shows one
    # nozzle face-on, so the plume is fat and centred).
    flame_len = int(16 + p * 14)
    glow = _glow(int(14 + p * 9), (120, 180, 255), alpha=int(60 + p * 60))
    _blit_c(surf, glow, (tail_x + flame_len // 2, BCY + 2))
    flame = _baked_flame(flame_len, 12, (255, 255, 250), (140, 200, 255),
                         (70, 120, 230))
    surf.blit(flame, (tail_x - 2, BCY + 2 - flame.get_height() // 2))

    # Tall single tail fin canted back (3/4 view reads one fin).
    pygame.draw.polygon(surf, _N_BODY_D, [
        (tail_x - 8, BCY - 4), (tail_x - 2, BCY - 17),
        (tail_x + 3, BCY - 16), (tail_x + 2, BCY - 3)])
    pygame.draw.line(surf, _N_GOLD, (tail_x - 6, BCY - 6),
                     (tail_x - 1, BCY - 15), 1)

    # Swept wings: near wing low-front, far wing high-back for 3/4 depth.
    # Far wing (top, partly behind body).
    pygame.draw.polygon(surf, _N_BODY_D, [
        (nose_x + 22, BCY - 4), (tail_x - 4, BCY - 16),
        (tail_x, BCY - 14), (tail_x - 8, BCY - 3)])
    # Near wing (bottom, foreground).
    pygame.draw.polygon(surf, _N_BODY, [
        (nose_x + 20, BCY + 3), (tail_x - 2, BCY + 18),
        (tail_x + 5, BCY + 17), (tail_x - 6, BCY + 5)])
    pygame.draw.polygon(surf, _N_BODY_H, [
        (nose_x + 21, BCY + 3), (tail_x - 5, BCY + 15),
        (tail_x - 7, BCY + 6)])
    pygame.draw.line(surf, _N_WHITE, (nose_x + 20, BCY + 3),
                     (tail_x - 2, BCY + 18), 1)

    # Chunky fuselage, slightly 3/4 (deeper belly than spine).
    body = [(nose_x, BCY + 1), (nose_x + 14, BCY - 7), (tail_x, BCY - 6),
            (tail_x + 4, BCY + 1), (tail_x, BCY + 8), (nose_x + 14, BCY + 7)]
    pygame.draw.polygon(surf, _N_BODY, body)
    pygame.draw.polygon(surf, _N_BODY_H,
                        [(nose_x + 4, BCY - 5), (nose_x + 14, BCY - 6),
                         (tail_x, BCY - 5), (tail_x, BCY - 2)])
    pygame.draw.polygon(surf, _N_BODY_D, body, 1)
    # White nose flash + gold trim band.
    pygame.draw.polygon(surf, _N_WHITE,
                        [(nose_x, BCY + 1), (nose_x + 9, BCY - 3),
                         (nose_x + 9, BCY + 4)])
    pygame.draw.line(surf, _N_GOLD, (nose_x + 9, BCY - 3),
                     (nose_x + 9, BCY + 4), 1)
    # White star roundel on the fuselage spine.
    pygame.draw.circle(surf, _N_WHITE, (nose_x + 24, BCY - 2), 3)
    pygame.draw.circle(surf, _N_BODY_D, (nose_x + 24, BCY - 2), 3, 1)

    # Big prominent canopy (the hero of a 3/4 jet).
    _aaellipse(surf, _N_CANOPY, (nose_x + 14, BCY - 2), 6, 4)
    _aaellipse(surf, _N_CANOPY_H, (nose_x + 12, BCY - 3), 3, 2)
    pygame.draw.circle(surf, (255, 255, 255), (nose_x + 11, BCY - 4), 1)
    # Nozzle glow ring.
    pygame.draw.circle(surf, (200, 230, 255), (tail_x + 1, BCY + 2), 3)
    return surf


get_jet_fighter_v2 = _make_prebuilt_skin(build_jet_fighter_v2)


# ═════════════════════════════════════════════════════════════════════════════
# v3 · DESERT STRIKE — top-down, desert-tan camo + olive splotches, FORWARD-
#     swept wings (Su-47 flair), TWIN exhaust, underwing missile pylons. A
#     rugged ground-attack look: warm sand body, brown camo, orange burner.
# ═════════════════════════════════════════════════════════════════════════════
_D_BODY   = (196, 168, 116)
_D_BODY_D = (150, 124, 80)
_D_BODY_H = (224, 202, 158)
_D_CAMO   = (120, 110, 72)
_D_EDGE   = (96, 78, 48)
_D_CANOPY = (96, 120, 96)
_D_MISSILE = (170, 78, 56)


def build_jet_fighter_v3(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 12 + pit
    tail_x = 49

    # Twin afterburner, warm desert orange.
    flame_len = int(13 + p * 11)
    glow = _glow(int(12 + p * 7), (255, 140, 50), alpha=int(60 + p * 70))
    _blit_c(surf, glow, (tail_x + flame_len // 2, BCY))
    flame = _baked_flame(flame_len, 8, (255, 252, 230), (255, 160, 50),
                         (220, 64, 30))
    for ny in (BCY - 5, BCY + 5):
        surf.blit(flame, (tail_x - 2, ny - flame.get_height() // 2))

    # Twin tail fins, low and stubby (ground-attack stance).
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _D_BODY_D, [
            (tail_x - 4, BCY + sgn * 3), (tail_x + 5, BCY + sgn * 11),
            (tail_x + 8, BCY + sgn * 10), (tail_x + 1, BCY + sgn * 2)])

    # FORWARD-swept wings: tips sweep toward the NOSE — distinctive silhouette.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _D_BODY_D, [
            (tail_x - 6, BCY + sgn * 3), (nose_x + 16, BCY + sgn * 19),
            (nose_x + 22, BCY + sgn * 19), (tail_x - 2, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _D_BODY, [
            (tail_x - 7, BCY + sgn * 4), (nose_x + 18, BCY + sgn * 17),
            (tail_x - 3, BCY + sgn * 6)])
        # Olive camo splotch on each wing.
        pygame.draw.circle(surf, _D_CAMO,
                           (nose_x + 26, BCY + sgn * 12), 2)
        # Underwing missile pylon + missile.
        pygame.draw.line(surf, _D_EDGE, (nose_x + 24, BCY + sgn * 14),
                         (nose_x + 22, BCY + sgn * 14), 2)
        pygame.draw.polygon(surf, _D_MISSILE,
                            [(nose_x + 16, BCY + sgn * 15),
                             (nose_x + 26, BCY + sgn * 15),
                             (nose_x + 14, BCY + sgn * 15)])

    # Broad fuselage.
    body = [(nose_x, BCY), (nose_x + 15, BCY - 6), (tail_x + 2, BCY - 5),
            (tail_x + 5, BCY), (tail_x + 2, BCY + 5), (nose_x + 15, BCY + 6)]
    pygame.draw.polygon(surf, _D_BODY, body)
    pygame.draw.polygon(surf, _D_EDGE, body, 1)
    # Camo splotches + spine highlight.
    pygame.draw.polygon(surf, _D_BODY_H,
                        [(nose_x + 5, BCY - 1), (nose_x + 15, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    pygame.draw.circle(surf, _D_CAMO, (nose_x + 22, BCY + 2), 3)
    pygame.draw.circle(surf, _D_CAMO, (nose_x + 30, BCY - 3), 2)
    # Sharp nose + sand-painted cone.
    pygame.draw.polygon(surf, _D_BODY_D,
                        [(nose_x, BCY), (nose_x + 7, BCY - 2),
                         (nose_x + 7, BCY + 2)])
    # Canopy.
    _aaellipse(surf, _D_CANOPY, (nose_x + 13, BCY), 5, 3)
    _aaellipse(surf, (190, 220, 190), (nose_x + 11, BCY - 1), 2, 1)
    for ny in (BCY - 5, BCY + 5):
        pygame.draw.circle(surf, (255, 190, 110), (tail_x + 1, ny), 2)
    return surf


get_jet_fighter_v3 = _make_prebuilt_skin(build_jet_fighter_v3)


# ═════════════════════════════════════════════════════════════════════════════
# v4 · STEALTH PHANTOM — top-down, matte-black faceted stealth airframe
#     (F-117/B-2 angular planform), a COLD cyan-core afterburner. The contrast
#     piece: near-black silhouette saved by electric-cyan glow + edge lighting.
# ═════════════════════════════════════════════════════════════════════════════
_S_BODY   = (38, 40, 50)
_S_BODY_D = (22, 24, 32)
_S_FACET  = (60, 64, 80)
_S_EDGE   = (96, 200, 224)          # electric edge-light
_S_CANOPY = (20, 60, 70)


def build_jet_fighter_v4(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 10 + pit
    tail_x = 48

    # COLD afterburner: cyan-white core, electric-blue plume + big halo so the
    # near-black jet still throws a premium glow at night.
    flame_len = int(15 + p * 13)
    glow = _glow(int(15 + p * 10), (70, 220, 255), alpha=int(70 + p * 80))
    _blit_c(surf, glow, (tail_x + flame_len // 2, BCY))
    flame = _baked_flame(flame_len, 10, (240, 255, 255), (120, 230, 255),
                         (40, 150, 240))
    surf.blit(flame, (tail_x - 2, BCY - flame.get_height() // 2))

    # Sharp faceted diamond planform (single blended wing-body, B-2 vibe).
    plan = [(nose_x, BCY),
            (nose_x + 20, BCY - 6), (nose_x + 30, BCY - 20),
            (tail_x - 4, BCY - 4), (tail_x + 4, BCY),
            (tail_x - 4, BCY + 4), (nose_x + 30, BCY + 20),
            (nose_x + 20, BCY + 6)]
    pygame.draw.polygon(surf, _S_BODY, plan)
    # Faceted top panels (lighter triangles catch starlight).
    pygame.draw.polygon(surf, _S_FACET,
                        [(nose_x + 4, BCY - 1), (nose_x + 20, BCY - 5),
                         (nose_x + 30, BCY - 18), (nose_x + 24, BCY - 2)])
    pygame.draw.polygon(surf, _S_BODY_D,
                        [(nose_x + 4, BCY + 1), (nose_x + 20, BCY + 5),
                         (nose_x + 30, BCY + 18), (nose_x + 24, BCY + 2)])
    # Twin canted stealth fins.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _S_BODY_D, [
            (tail_x - 8, BCY + sgn * 3), (tail_x - 1, BCY + sgn * 12),
            (tail_x + 3, BCY + sgn * 11), (tail_x - 3, BCY + sgn * 2)])

    # HERO tell at night: electric edge-light tracing the leading edges.
    pygame.draw.lines(surf, _S_EDGE, False,
                      [(nose_x, BCY - 0), (nose_x + 20, BCY - 6),
                       (nose_x + 30, BCY - 20)], 1)
    pygame.draw.lines(surf, _S_EDGE, False,
                      [(nose_x, BCY + 0), (nose_x + 20, BCY + 6),
                       (nose_x + 30, BCY + 20)], 1)
    # Glowing cyan spine seam + nozzle.
    pygame.draw.line(surf, _S_EDGE, (nose_x + 16, BCY), (tail_x - 4, BCY), 1)
    pygame.draw.circle(surf, (180, 250, 255), (tail_x, BCY), 2)
    # Faceted dark canopy with a cyan glint.
    _aaellipse(surf, _S_CANOPY, (nose_x + 16, BCY), 5, 3)
    pygame.draw.circle(surf, _S_EDGE, (nose_x + 14, BCY - 1), 1)
    # Nose vertex bright point so the sharp tip survives downscale.
    pygame.draw.circle(surf, (160, 240, 255), (nose_x + 1, BCY), 1)
    return surf


get_jet_fighter_v4 = _make_prebuilt_skin(build_jet_fighter_v4)


# ═════════════════════════════════════════════════════════════════════════════
# v5 · CHROME ACE — aggressive 3/4 airshow jet, polished chrome/silver body
#     with a bold red-and-gold racing livery sweep, twin tail, single hot
#     afterburner + a wisp of smoke-trail. The showy, premium crowd-pleaser.
# ═════════════════════════════════════════════════════════════════════════════
_C_CHROME  = (208, 216, 226)
_C_CHROME_D = (150, 160, 174)
_C_CHROME_H = (252, 254, 255)
_C_STEEL   = (96, 104, 118)
_C_RED     = (220, 48, 52)
_C_GOLD    = (248, 198, 84)
_C_CANOPY  = (44, 56, 78)
_C_CANOPY_H = (180, 220, 246)


def build_jet_fighter_v5(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 9 + pit
    tail_x = 48

    # Smoke-trail wisp (airshow signature), faint and aft.
    smoke = pygame.Surface((22, 14), pygame.SRCALPHA)
    for i, a in ((0, 90), (1, 60), (2, 36)):
        pygame.draw.circle(smoke, (235, 235, 240, a), (14 - i * 5, 7), 5 - i)
    surf.blit(smoke, (tail_x + 8, BCY - 5))

    # Single hot afterburner with a gold-warm halo.
    flame_len = int(15 + p * 13)
    glow = _glow(int(13 + p * 9), (255, 180, 70), alpha=int(60 + p * 70))
    _blit_c(surf, glow, (tail_x + flame_len // 2, BCY + 2))
    flame = _baked_flame(flame_len, 11, (255, 255, 248), (255, 190, 70),
                         (240, 80, 40))
    surf.blit(flame, (tail_x - 2, BCY + 2 - flame.get_height() // 2))

    # Twin tail fins, chrome with red caps.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _C_STEEL, [
            (tail_x - 6, BCY + sgn * 3), (tail_x + 3, BCY + sgn * 13),
            (tail_x + 7, BCY + sgn * 12), (tail_x, BCY + sgn * 2)])
        pygame.draw.circle(surf, _C_RED,
                           (tail_x + 4, BCY + sgn * 12), 1)

    # Swept wings, chrome with a gold racing stripe.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _C_CHROME_D, [
            (nose_x + 20, BCY + sgn * 2), (tail_x - 2, BCY + sgn * 19),
            (tail_x + 4, BCY + sgn * 18), (tail_x - 6, BCY + sgn * 5)])
        pygame.draw.polygon(surf, _C_CHROME, [
            (nose_x + 21, BCY + sgn * 2), (tail_x - 4, BCY + sgn * 16),
            (tail_x - 7, BCY + sgn * 5)])
        pygame.draw.line(surf, _C_GOLD, (nose_x + 21, BCY + sgn * 3),
                         (tail_x - 4, BCY + sgn * 15), 1)

    # Chrome fuselage with a bold red→gold lightning livery sweep.
    body = [(nose_x, BCY + 1), (nose_x + 14, BCY - 6), (tail_x, BCY - 6),
            (tail_x + 5, BCY + 1), (tail_x, BCY + 8), (nose_x + 14, BCY + 7)]
    pygame.draw.polygon(surf, _C_CHROME, body)
    # Chrome sheen band (bright spine, dark belly = polished metal read).
    pygame.draw.polygon(surf, _C_CHROME_H,
                        [(nose_x + 4, BCY - 4), (nose_x + 14, BCY - 5),
                         (tail_x, BCY - 5), (tail_x, BCY - 2)])
    pygame.draw.polygon(surf, _C_CHROME_D,
                        [(nose_x + 6, BCY + 4), (tail_x, BCY + 4),
                         (tail_x, BCY + 7), (nose_x + 12, BCY + 7)])
    # Red livery sweep along the body, ending in a gold spear.
    pygame.draw.polygon(surf, _C_RED,
                        [(nose_x + 2, BCY + 2), (nose_x + 22, BCY - 1),
                         (tail_x - 2, BCY + 1), (nose_x + 22, BCY + 3)])
    pygame.draw.polygon(surf, _C_GOLD,
                        [(nose_x + 20, BCY), (nose_x + 28, BCY + 1),
                         (nose_x + 20, BCY + 2)])
    pygame.draw.polygon(surf, _C_STEEL, body, 1)
    # Sharp nose.
    pygame.draw.polygon(surf, _C_STEEL,
                        [(nose_x, BCY + 1), (nose_x + 7, BCY - 1),
                         (nose_x + 7, BCY + 3)])
    pygame.draw.circle(surf, _C_RED, (nose_x + 1, BCY + 1), 1)
    # Big airshow canopy.
    _aaellipse(surf, _C_CANOPY, (nose_x + 13, BCY - 1), 6, 4)
    _aaellipse(surf, _C_CANOPY_H, (nose_x + 11, BCY - 2), 3, 2)
    pygame.draw.circle(surf, (255, 255, 255), (nose_x + 10, BCY - 3), 1)
    pygame.draw.circle(surf, (255, 210, 130), (tail_x + 1, BCY + 2), 3)
    return surf


get_jet_fighter_v5 = _make_prebuilt_skin(build_jet_fighter_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Label → getter registry for the review sheet. The winner becomes the single
# registered "skin_jet_fighter": get_jet_fighter in game/animal_jet_fighter.py.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "v1 · STEEL RAPTOR":   get_jet_fighter_v1,
    "v2 · TOP GUN NAVY":   get_jet_fighter_v2,
    "v3 · DESERT STRIKE":  get_jet_fighter_v3,
    "v4 · STEALTH PHANTOM": get_jet_fighter_v4,
    "v5 · CHROME ACE":     get_jet_fighter_v5,
}
