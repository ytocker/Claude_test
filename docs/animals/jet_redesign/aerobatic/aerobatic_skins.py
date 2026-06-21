"""Production JET redesign — AEROBATIC TEAM JET · BLUE ANGEL, round-2 converged.

The priciest secret skin re-imagined as an AIR-SHOW DISPLAY jet (Blue Angels
energy): a near-black NAVY gloss body wearing ONE bold GOLD spear nose-to-tail.
There is no flapping — the 4 base wing poses (`parrot._WING_ANGLES`) are an
AFTERBURNER PULSE: a baked cool exhaust glow flares and shrinks across the 4
frames and the nose pitches a touch. No live particles; the spectacle is baked.

Round-2 direction (art-director, SHIP v1 BLUE ANGEL):

  * The GOLD spear is the SINGLE dominant graphic — one uninterrupted stroke
    nose-cap → spine → tail, widened so it reads as ONE diagonal at 40px, not a
    thin line plus bits. It is the only livery tell.
  * Body stays almost pure NAVY: the gold wing leading-edges are gone, so the
    spear is the only gold mass and owns the focal hierarchy.
  * A subtle COOL self-rim is baked onto the navy body (top-right per the skin
    light direction) so the silhouette holds on night sky without the gold.
  * Burner is COOL and SMALL — pulled down ~20% so gold owns the read.
  * The 40px NEAREST read resolves to exactly TWO values + ONE accent: dark
    navy body, light rim, gold spear.

Contract (mirrors game/animal_jet_fighter.py so this lifts straight into a
production game/animal_jet_fighter.py later):

  * `build_aerobatic(wing_angle_deg) -> pygame.Surface`  draws ONE flat frame
    on a 64×84 SRCALPHA canvas, fuselage mass centred at (32,44), NOSE-RIGHT /
    UPRIGHT / LEVEL (clean planform). Rotation/flip is applied by the game
    later — we do NOT bake it here.
  * `get_aerobatic`: a cached `(frame_idx, tilt_deg) -> Surface` getter from the
    local `_make_prebuilt_skin(build_aerobatic)`.
  * `BUILDERS = {"skin_aerobatic": get_aerobatic}` for the review sheet and the
    production registry.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, so the fuselage mass stays near (32,44) for fairness — wings may
span wider, but the body stays anchored so the in-game center-blit rotation
maths still holds.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + body anchor (mirror the production jet layout) ───────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
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
    two frames and shrinks at the ends — a heartbeat the eye reads as thrust."""
    t = (50 - angle_deg) / 90.0
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the jet visibly 'breathes'
    with the burner instead of sitting dead-still. ±1px is enough at 40px."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _baked_flame(length, width, core, mid, outer):
    """Bake ONE afterburner plume onto its own SRCALPHA surface: a layered
    teardrop — outer haze → mid → white-hot core — with shock-diamond beads.
    Pre-baking keeps both build targets identical and cheap.

    Drawn NOSE-RIGHT planform: the jet's nose is RIGHT (+x), so the exhaust
    streams LEFT (−x). The plume's BRIGHT mouth sits at the surface's RIGHT
    edge (the nozzle) and tapers to the LEFT, so callers blit it trailing aft."""
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
            # mouth at the RIGHT edge → taper leftwards (exhaust streams aft).
            x = w - pad - t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy - r))
        for i in range(n + 1):
            t = (n - i) / n
            x = w - pad - t * ln
            r = hw * math.sin(math.pi * (0.15 + 0.85 * (1.0 - t))) * (1.0 - 0.15 * t)
            pts.append((x, cy + r))
        layer = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(layer, (*col, alpha), pts)
        surf.blit(layer, (0, 0))

    teardrop(outer, length,             width / 2.0,  140)
    teardrop(mid,   int(length * 0.74), width / 3.0,  210)
    teardrop(core,  int(length * 0.46), width / 5.0,  255)
    # White-hot pinch right at the nozzle mouth.
    pygame.draw.circle(surf, (255, 255, 255, 255), (w - pad - 2, cy), max(1, width // 8))
    for k in range(1, 3):
        dx = w - pad - int(length * 0.16 * k) - 2
        rad = max(1, width // 10 - (k - 1))
        pygame.draw.circle(surf, (255, 250, 232, 235), (dx, cy), rad)
    return surf


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the cool aura behind the burner. Held
    small (rear-third) so it supports the silhouette without swallowing it,
    and so the gold spear stays the focal point, not the flame."""
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


# Twin nozzles on a WIDE vertical gap so two white cores stay distinct at 40px.
_NOZ_DY = 8


def _burner(surf, tail_x, p, *, core, mid, outer, glow_col):
    """Twin cool afterburner: each nozzle gets its own tight halo + plume,
    capped to the rear AND pulled ~20% smaller/dimmer than the fighter burner
    so the GOLD spear owns the focal hierarchy, not the flame. Drawn NOSE-RIGHT,
    so plumes stream LEFT of the tail."""
    flame_len = int((13 + p * 11) * 0.80)
    halo_r = int((10 + p * 5) * 0.84 * 0.80)
    glow = _glow(halo_r, glow_col, alpha=int((60 + p * 60) * 0.80))
    flame = _baked_flame(flame_len, 7, core, mid, outer)
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        _blit_c(surf, glow, (tail_x - flame_len // 2 + 2, ny))
        surf.blit(flame, (tail_x + 2 - flame.get_width(), ny - flame.get_height() // 2))


def _nozzle_mouths(surf, tail_x):
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        pygame.draw.circle(surf, (210, 226, 255), (tail_x, ny), 2)
        pygame.draw.circle(surf, (245, 250, 255), (tail_x + 1, ny), 1)


# ═════════════════════════════════════════════════════════════════════════════
# Planform builders (NOSE-RIGHT, UPRIGHT, LEVEL). SHARP DELTA — the team-jet
# read. Wings are kept almost pure NAVY (a darker value edge only) so they add
# no competing gold mass; the gold lives ONLY in the spine spear.
# ═════════════════════════════════════════════════════════════════════════════
def _tail_fins(surf, tail_x, body_d):
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, body_d, [
            (tail_x + 6, BCY + sgn * 4), (tail_x - 6, BCY + sgn * 13),
            (tail_x - 9, BCY + sgn * 12), (tail_x - 2, BCY + sgn * 3)])


def _delta_wings(surf, nose_x, tail_x, body, body_d, body_h, edge):
    """Sharp delta swept hard back from mid-fuselage (NOSE-RIGHT). Value-only
    shading — dark underside, lit top facet, dark leading-edge line — so the
    wing reads by LUMINANCE on day AND night with no gold accent."""
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, body_d, [
            (nose_x - 18, BCY + sgn * 2), (tail_x + 2, BCY + sgn * 20),
            (tail_x - 4, BCY + sgn * 20), (tail_x + 6, BCY + sgn * 6)])
        pygame.draw.polygon(surf, body, [
            (nose_x - 19, BCY + sgn * 2), (tail_x + 4, BCY + sgn * 18),
            (tail_x + 7, BCY + sgn * 6)])
        pygame.draw.polygon(surf, body_h, [
            (nose_x - 20, BCY + sgn * 2), (nose_x - 30, BCY + sgn * 7),
            (tail_x + 8, BCY + sgn * 7), (tail_x + 7, BCY + sgn * 6)])
        pygame.draw.line(surf, edge, (nose_x - 19, BCY + sgn * 2),
                         (tail_x + 4, BCY + sgn * 18), 1)


def _fuselage(surf, nose_x, tail_x, body, body_h, edge):
    """Long dart arrowhead fuselage (NOSE-RIGHT). Returns the body polygon so
    the spear livery can be clipped to it via a mask blit."""
    body_poly = [(nose_x, BCY), (nose_x - 16, BCY - 6), (tail_x - 4, BCY - 5),
                 (tail_x - 6, BCY), (tail_x - 4, BCY + 5), (nose_x - 16, BCY + 6)]
    pygame.draw.polygon(surf, body, body_poly)
    pygame.draw.polygon(surf, body_h,
                        [(nose_x - 4, BCY - 1), (nose_x - 16, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    pygame.draw.polygon(surf, edge, body_poly, 1)
    return body_poly


def _clip_to_body(surf, shape_surf, body_poly):
    """Blit a livery overlay but keep only the part that lands on the fuselage,
    so the gold spear can be drawn freely then trimmed to the body silhouette
    (the spear reads as paint ON the jet, not floating)."""
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body_poly)
    shape_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(shape_surf, (0, 0))


def _canopy(surf, nose_x, canopy, canopy_h):
    _aaellipse(surf, canopy, (nose_x - 14, BCY), 5, 3)
    _aaellipse(surf, canopy_h, (nose_x - 12, BCY - 1), 2, 1)
    pygame.draw.circle(surf, canopy_h, (nose_x - 12, BCY - 1), 1)


# ═════════════════════════════════════════════════════════════════════════════
# BLUE ANGEL — deep near-black NAVY gloss, sharp delta. The livery is ONE bold
# GOLD spear running nose-cap → spine → tail. Navy/gold is the premium read AND
# colourblind-safe on value alone (no red/blue distinction relied on).
# ═════════════════════════════════════════════════════════════════════════════
_BA_BODY   = (24, 42, 110)        # deep navy, near-black so gold pops
_BA_BODY_D = (12, 24, 72)
_BA_BODY_H = (58, 88, 178)
_BA_EDGE   = (8, 16, 52)
_BA_RIM    = (150, 186, 255)      # cool self-rim — holds the night silhouette
_BA_GOLD   = (255, 200, 52)
_BA_GOLD_D = (206, 150, 20)
_BA_GOLD_H = (255, 236, 158)


def build_aerobatic(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 52 - pit
    tail_x = 14

    # Cool, small burner first so it sits behind the body and reads quiet.
    _burner(surf, tail_x, p, core=(244, 250, 255), mid=(150, 190, 255),
            outer=(56, 104, 224), glow_col=(96, 150, 255))
    _tail_fins(surf, tail_x, _BA_BODY_D)
    _delta_wings(surf, nose_x, tail_x, _BA_BODY, _BA_BODY_D, _BA_BODY_H, _BA_EDGE)
    body_poly = _fuselage(surf, nose_x, tail_x, _BA_BODY, _BA_BODY_H, _BA_EDGE)

    # ── LIVERY: ONE uninterrupted GOLD spear, nose-cap → spine → tail ────────
    # Drawn as a single tapering wedge polygon (no separate spine line), wide at
    # the nose and tapering to the tail, so it reads as ONE bold diagonal at
    # 40px — the only gold mass on the jet.
    spear = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(spear, _BA_GOLD, [
        (nose_x, BCY),                       # sharp nose tip
        (nose_x - 13, BCY - 5),              # nose-cap shoulder (top)
        (tail_x + 3, BCY - 2),               # spine taper to tail (top)
        (tail_x + 1, BCY),                   # tail point
        (tail_x + 3, BCY + 2),               # spine taper to tail (bottom)
        (nose_x - 13, BCY + 5)])             # nose-cap shoulder (bottom)
    # Warm top-facet highlight along the spear's upper edge (light top-right):
    # one stroke, so the spear catches a gloss without breaking into bits.
    pygame.draw.polygon(spear, _BA_GOLD_H, [
        (nose_x - 2, BCY - 1), (nose_x - 12, BCY - 4),
        (tail_x + 3, BCY - 1)])
    # Thin darker keel under the spear's lower edge so it reads dimensional.
    pygame.draw.line(spear, _BA_GOLD_D, (nose_x - 12, BCY + 4),
                     (tail_x + 3, BCY + 1), 1)
    _clip_to_body(surf, spear, body_poly)

    # ── Baked COOL self-rim on the navy body (top-right per skin light dir) ──
    # A thin light edge tracing the upper fuselage chine + the upper wing
    # leading edges, so the navy silhouette holds on a dark night sky WITHOUT
    # leaning on the gold. Value-based, colourblind-safe.
    pygame.draw.line(surf, _BA_RIM, (nose_x - 4, BCY - 5),
                     (tail_x - 1, BCY - 4), 1)
    for sgn in (-1, 1):
        # Only the TOP wing's leading edge gets the bright rim; the bottom gets
        # a fainter hint so the light stays directional, not a full outline.
        rim_col = _BA_RIM if sgn == -1 else (96, 124, 196)
        pygame.draw.line(surf, rim_col, (nose_x - 20, BCY + sgn * 2),
                         (tail_x + 6, BCY + sgn * 17), 1)

    _canopy(surf, nose_x, (40, 70, 150), (170, 206, 255))
    _nozzle_mouths(surf, tail_x)
    return surf


get_aerobatic = _make_prebuilt_skin(build_aerobatic)


# ─────────────────────────────────────────────────────────────────────────────
# Production registry: the single registered skin lifts into
# game/animal_jet_fighter.py as the AEROBATIC TEAM JET (BLUE ANGEL).
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {"skin_aerobatic": get_aerobatic}
