"""Candidate SCI-FI ENERGY FIGHTER jet skins — round-1 exploration.

A futuristic spaceship-fighter redesign of the secret JET skin: an angular
FACETED hull with glowing NEON energy trim and a plasma afterburner — part
jet, part starship. Distinct from the warm/organic DRAGON & PHOENIX
legendaries: this is hard-edged, cool, neon-tech.

Five genuinely different sub-takes on the ONE concept, varying:
  * energy colour   — cyan / magenta / electric-violet / toxic-green / gold
  * hull style      — sleek arrowhead / heavy gunship / winged-X starship /
                      forward-swept / faceted diamond cruiser
  * glow amount     — subtle edge-piping vs full energy aura
  * engine          — single big plasma core vs twin plasma nozzles

Contract (mirrors game/animal_jet_fighter.py so the winner lifts straight in):

  * `build_scifi_vN(wing_angle_deg) -> pygame.Surface`  draws ONE flat frame
    on a 64×84 SRCALPHA canvas, hull mass centred at (32,44). Drawn
    NOSE-RIGHT, UPRIGHT, LEVEL (clean planform) — rotation is NOT baked; the
    game applies the inverted nose-up spin later.
  * The 4 poses are a PLASMA PULSE + a slight pitch. ALL glow (energy edges,
    engine plasma) is BAKED into the 4 frames and varied across them for the
    pulse — no live particle system.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)` — 4 flat frames + per-(frame, 3°) rotation
    cache, each outlined with the house silhouette outline.
  * `BUILDERS = {"skin_scifi": ...}` plus a label→getter dict for the sheet.

North star: reads at 40px day AND night — one bold angular hull silhouette +
a clear glowing energy tell, with a baked 1px self-rim so the hull never
dissolves into glow noise.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline


# ── canvas + hull anchor (mirror animal_jet_fighter composite layout) ────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # hull centre → (32, 44)


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
    """Plasma pulse phase from the wing angle: the 4 poses (50→-40) map to a
    0..1 'throttle' so the baked plasma flares brightest on the middle two
    frames and shrinks at the ends — a heartbeat the eye reads as thrust.

    Triangle-wrapped (bright-bright in the centre, dim-dim at the ends): a
    perceptible throttle pulse at 40px without strobing."""
    t = (50 - angle_deg) / 90.0          # 50→0, 20→.33, -10→.67, -40→1
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the hull visibly 'breathes'
    with the engine instead of sitting dead-still. ±1px is enough at 40px."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the neon aura behind the plasma core.
    Concentric fading rings so the glow supports the silhouette, never
    swallows it. ADD-blended so overlapping auras read as hot energy."""
    d = max(2, radius * 2)
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = max(1, int(radius * i / steps))
        pygame.draw.circle(s, (*color, a), (d // 2, d // 2), r)
    return s


def _plasma(length, width, core, mid, outer):
    """Bake ONE plasma exhaust plume on its own SRCALPHA surface: a layered
    teardrop — outer neon haze → mid → white-hot core — with shock-diamond
    beads down the centre. Pre-baking (vs a live particle system) keeps both
    build targets identical and cheap.

    The white core is kept NARROW relative to the haze so twin plumes keep
    two distinct cores at 40px even when their soft auras kiss.

    Returns a surface whose LEFT edge is the nozzle mouth; the plume streams
    RIGHT (the hull flies nose-right here, exhaust aft)."""
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

    teardrop(outer, length,             width / 2.0,  150)
    teardrop(mid,   int(length * 0.74), width / 3.0,  215)
    teardrop(core,  int(length * 0.46), width / 5.0,  255)
    # White-hot pinch at the nozzle mouth (a tight, bright core seed).
    pygame.draw.circle(surf, (255, 255, 255, 255), (pad + 2, cy), max(1, width // 8))
    for k in range(1, 3):
        dx = pad + int(length * 0.16 * k) + 2
        rad = max(1, width // 10 - (k - 1))
        pygame.draw.circle(surf, (245, 250, 255, 235), (dx, cy), rad)
    return surf


def _neon_edges(surf, edges, color, hot, width=1):
    """Trace a list of (p0, p1) segments as glowing neon piping: a soft wide
    underlay (the bloom) + a crisp bright line on top (the filament). This is
    the 'energy trim' tell — bake it so it reads premium without a live
    particle pass. Drawn on its own ADD-blended layer so crossing edges bloom."""
    bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for p0, p1 in edges:
        pygame.draw.line(bloom, (*color, 70), p0, p1, width + 4)
    for p0, p1 in edges:
        pygame.draw.line(bloom, (*color, 130), p0, p1, width + 2)
    surf.blit(bloom, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    for p0, p1 in edges:
        pygame.draw.line(surf, hot, p0, p1, width)


# ═════════════════════════════════════════════════════════════════════════════
# Shared canopy: a cool energy slit, the CONSTANT anchor that never washes out.
# ═════════════════════════════════════════════════════════════════════════════
def _energy_canopy(surf, cx, cy, color, hot):
    pygame.draw.polygon(surf, color,
                        [(cx - 3, cy), (cx + 1, cy - 2),
                         (cx + 5, cy), (cx + 1, cy + 2)])
    pygame.draw.line(surf, hot, (cx - 2, cy), (cx + 4, cy), 1)


# ═════════════════════════════════════════════════════════════════════════════
# v1 · CYAN INTERCEPTOR — sleek arrowhead hull, SUBTLE cyan edge-piping, a
#   single big plasma core. The minimal/elegant take: dark hull, one clean
#   glowing chevron tracing the leading edges, one bright engine eye.
# ═════════════════════════════════════════════════════════════════════════════
_C1_HULL   = (40, 52, 66)
_C1_HULL_D = (24, 32, 44)
_C1_HULL_H = (78, 96, 116)
_C1_EDGE   = (14, 20, 30)
_C1_NEON   = (40, 210, 255)
_C1_HOT    = (200, 250, 255)


def build_scifi_v1(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 56 + pit                    # nose RIGHT
    tail_x = 16

    # ── Single big plasma core out the back ──────────────────────────────
    plen = int(13 + p * 12)
    halo = _glow(int((11 + p * 6)), _C1_NEON, alpha=int(55 + p * 70))
    plume = _plasma(plen, 9, (250, 255, 255), (120, 235, 255), (30, 150, 210))
    plume = pygame.transform.flip(plume, True, False)   # streams LEFT (aft)
    _blit_c(surf, halo, (tail_x - plen // 2 + 2, BCY))
    surf.blit(plume, (tail_x + 2 - plume.get_width(), BCY - plume.get_height() // 2))

    # ── Swept delta wings (one bold pair) ────────────────────────────────
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _C1_HULL_D, [
            (nose_x - 20, BCY + sgn * 2), (tail_x + 4, BCY + sgn * 19),
            (tail_x - 2, BCY + sgn * 19), (tail_x + 8, BCY + sgn * 6)])
        pygame.draw.polygon(surf, _C1_HULL, [
            (nose_x - 21, BCY + sgn * 2), (tail_x + 6, BCY + sgn * 17),
            (tail_x + 9, BCY + sgn * 6)])

    # ── Arrowhead fuselage ───────────────────────────────────────────────
    body = [(nose_x, BCY), (nose_x - 16, BCY - 6), (tail_x - 4, BCY - 5),
            (tail_x - 6, BCY), (tail_x - 4, BCY + 5), (nose_x - 16, BCY + 6)]
    pygame.draw.polygon(surf, _C1_HULL, body)
    pygame.draw.polygon(surf, _C1_HULL_H,
                        [(nose_x - 4, BCY - 1), (nose_x - 16, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    pygame.draw.polygon(surf, _C1_EDGE, body, 1)

    # ── SUBTLE neon edge-piping: one clean chevron on the leading edges ──
    edges = []
    for sgn in (-1, 1):
        edges.append(((nose_x - 21, BCY + sgn * 2), (tail_x + 6, BCY + sgn * 17)))
    edges.append(((nose_x, BCY), (nose_x - 16, BCY - 6)))
    edges.append(((nose_x, BCY), (nose_x - 16, BCY + 6)))
    _neon_edges(surf, edges, _C1_NEON, _C1_HOT, 1)

    # ── Bright engine eye + canopy ───────────────────────────────────────
    pygame.draw.circle(surf, _C1_NEON, (tail_x - 4, BCY), 3)
    pygame.draw.circle(surf, (255, 255, 255), (tail_x - 5, BCY), 1)
    _energy_canopy(surf, nose_x - 12, BCY, _C1_NEON, _C1_HOT)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v2 · MAGENTA GUNSHIP — heavy WIDE hull, FULL magenta energy aura, TWIN plasma
#   engines. The aggressive bruiser: blocky chunky body, broad stubby wings,
#   a thick energy underglow, two hot cores aft.
# ═════════════════════════════════════════════════════════════════════════════
_C2_HULL   = (54, 40, 60)
_C2_HULL_D = (34, 24, 40)
_C2_HULL_H = (104, 84, 116)
_C2_EDGE   = (20, 12, 24)
_C2_NEON   = (255, 60, 200)
_C2_HOT    = (255, 200, 245)
_C2_NDY    = 7


def build_scifi_v2(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 54 + pit
    tail_x = 16

    # ── Full energy aura behind the whole tail (the 'aggressive' tell) ───
    big = _glow(int(15 + p * 6), _C2_NEON, alpha=int(45 + p * 45))
    surf.blit(big, big.get_rect(center=(tail_x + 2, BCY)).topleft,
              special_flags=pygame.BLEND_RGBA_ADD)

    # ── Twin plasma engines on a wide gap ────────────────────────────────
    plen = int(11 + p * 10)
    plume = _plasma(plen, 7, (255, 250, 255), (255, 130, 230), (200, 30, 150))
    plume = pygame.transform.flip(plume, True, False)
    for ny in (BCY - _C2_NDY, BCY + _C2_NDY):
        surf.blit(plume, (tail_x + 4 - plume.get_width(), ny - plume.get_height() // 2))

    # ── Broad stubby wings ───────────────────────────────────────────────
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _C2_HULL_D, [
            (nose_x - 26, BCY + sgn * 5), (nose_x - 30, BCY + sgn * 18),
            (tail_x + 2, BCY + sgn * 20), (tail_x + 6, BCY + sgn * 8)])
        pygame.draw.polygon(surf, _C2_HULL, [
            (nose_x - 26, BCY + sgn * 6), (nose_x - 29, BCY + sgn * 16),
            (tail_x + 4, BCY + sgn * 17), (tail_x + 7, BCY + sgn * 8)])

    # ── Chunky blocky fuselage ───────────────────────────────────────────
    body = [(nose_x, BCY), (nose_x - 12, BCY - 9), (tail_x + 2, BCY - 10),
            (tail_x - 4, BCY - 6), (tail_x - 4, BCY + 6), (tail_x + 2, BCY + 10),
            (nose_x - 12, BCY + 9)]
    pygame.draw.polygon(surf, _C2_HULL, body)
    pygame.draw.polygon(surf, _C2_HULL_H,
                        [(nose_x - 4, BCY - 2), (nose_x - 12, BCY - 6),
                         (tail_x, BCY - 6), (tail_x, BCY - 2)])
    pygame.draw.polygon(surf, _C2_EDGE, body, 1)

    # ── FULL energy trim: leading edges, hull spine, wing roots all piped ─
    edges = []
    for sgn in (-1, 1):
        edges.append(((nose_x, BCY), (tail_x + 2, BCY + sgn * 10)))
        edges.append(((nose_x - 26, BCY + sgn * 6), (nose_x - 29, BCY + sgn * 16)))
        edges.append(((nose_x - 29, BCY + sgn * 16), (tail_x + 4, BCY + sgn * 17)))
    _neon_edges(surf, edges, _C2_NEON, _C2_HOT, 1)

    # ── Twin engine eyes + canopy ────────────────────────────────────────
    for ny in (BCY - _C2_NDY, BCY + _C2_NDY):
        pygame.draw.circle(surf, _C2_NEON, (tail_x - 2, ny), 2)
        pygame.draw.circle(surf, (255, 255, 255), (tail_x - 3, ny), 1)
    _energy_canopy(surf, nose_x - 10, BCY, _C2_NEON, _C2_HOT)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v3 · VIOLET STARWING — a winged-X spaceship: four prong wings splayed like an
#   X, electric-violet trim, twin plasma engines. The most overt 'starship':
#   the X-prong silhouette is the bold tell, glowing cannon tips on each prong.
# ═════════════════════════════════════════════════════════════════════════════
_C3_HULL   = (46, 44, 70)
_C3_HULL_D = (28, 26, 48)
_C3_HULL_H = (96, 92, 134)
_C3_EDGE   = (16, 14, 28)
_C3_NEON   = (150, 90, 255)
_C3_HOT    = (224, 206, 255)
_C3_NDY    = 5


def build_scifi_v3(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 54 + pit
    tail_x = 18

    # ── Twin plasma engines (narrow gap, central thrust) ─────────────────
    plen = int(10 + p * 9)
    plume = _plasma(plen, 6, (252, 250, 255), (180, 130, 255), (110, 50, 200))
    plume = pygame.transform.flip(plume, True, False)
    halo = _glow(int(9 + p * 5), _C3_NEON, alpha=int(50 + p * 55))
    for ny in (BCY - _C3_NDY, BCY + _C3_NDY):
        _blit_c(surf, halo, (tail_x - plen // 2 + 2, ny))
        surf.blit(plume, (tail_x + 2 - plume.get_width(), ny - plume.get_height() // 2))

    # ── Four X-prong wings (the starship silhouette) ─────────────────────
    # Each prong is a long thin blade angled out from mid-hull, with a glowing
    # cannon tip. Two sweep up-back, two sweep down-back → an X.
    prongs = []
    for sgn in (-1, 1):
        for dy0, dy1 in ((4, 22), (-4, -22)):
            root = (nose_x - 22, BCY + sgn * dy0 * 0 + (dy0 if dy0 > 0 else 0) * 0)
            # root near mid-hull, tip splayed out + aft
            r = (nose_x - 20, BCY + (dy0))
            tpt = (tail_x - 2, BCY + (dy1))
            pygame.draw.polygon(surf, _C3_HULL_D, [
                (r[0], r[1] - sgn), (r[0], r[1] + sgn), (tpt[0], tpt[1])])
            pygame.draw.line(surf, _C3_HULL, (r[0], r[1]), (tpt[0], tpt[1]), 2)
            prongs.append((r, tpt))

    # ── Slim spear fuselage ──────────────────────────────────────────────
    body = [(nose_x, BCY), (nose_x - 14, BCY - 5), (tail_x + 2, BCY - 4),
            (tail_x - 2, BCY), (tail_x + 2, BCY + 4), (nose_x - 14, BCY + 5)]
    pygame.draw.polygon(surf, _C3_HULL, body)
    pygame.draw.polygon(surf, _C3_HULL_H,
                        [(nose_x - 4, BCY - 1), (nose_x - 14, BCY - 3),
                         (tail_x, BCY - 2), (tail_x, BCY - 1)])
    pygame.draw.polygon(surf, _C3_EDGE, body, 1)

    # ── Neon trim: each prong is piped, plus the nose chines ─────────────
    edges = [pr for pr in prongs]
    edges.append(((nose_x, BCY), (nose_x - 14, BCY - 5)))
    edges.append(((nose_x, BCY), (nose_x - 14, BCY + 5)))
    _neon_edges(surf, edges, _C3_NEON, _C3_HOT, 1)

    # ── Glowing cannon tips on each prong (the starwing signature) ───────
    for _, tpt in prongs:
        pygame.draw.circle(surf, _C3_NEON, tpt, 2)
        pygame.draw.circle(surf, (255, 255, 255), tpt, 1)
    # Twin engine eyes + canopy.
    for ny in (BCY - _C3_NDY, BCY + _C3_NDY):
        pygame.draw.circle(surf, _C3_NEON, (tail_x - 2, ny), 2)
    _energy_canopy(surf, nose_x - 11, BCY, _C3_NEON, _C3_HOT)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v4 · TOXIC STRIKER — FORWARD-SWEPT wings (rare, alien planform), toxic-green
#   neon piping, single plasma core with glowing side vents. The exotic take:
#   the wings sweep FORWARD (tips ahead of the roots) — an instantly unusual
#   silhouette — plus reactor side-vents that breathe green.
# ═════════════════════════════════════════════════════════════════════════════
_C4_HULL   = (38, 50, 40)
_C4_HULL_D = (24, 34, 26)
_C4_HULL_H = (84, 108, 80)
_C4_EDGE   = (14, 22, 16)
_C4_NEON   = (150, 255, 70)
_C4_HOT    = (228, 255, 190)


def build_scifi_v4(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 52 + pit
    tail_x = 18

    # ── Single plasma core ───────────────────────────────────────────────
    plen = int(12 + p * 11)
    halo = _glow(int(10 + p * 6), _C4_NEON, alpha=int(50 + p * 60))
    plume = _plasma(plen, 8, (250, 255, 248), (190, 255, 120), (90, 200, 50))
    plume = pygame.transform.flip(plume, True, False)
    _blit_c(surf, halo, (tail_x - plen // 2 + 2, BCY))
    surf.blit(plume, (tail_x + 2 - plume.get_width(), BCY - plume.get_height() // 2))

    # ── Forward-SWEPT wings: tips ahead of roots (the exotic tell) ───────
    for sgn in (-1, 1):
        root = (tail_x + 12, BCY + sgn * 5)
        tip  = (nose_x - 16, BCY + sgn * 19)        # tip is FORWARD of root
        pygame.draw.polygon(surf, _C4_HULL_D, [
            (root[0], root[1]), (tip[0], tip[1] + sgn),
            (tip[0] + 7, tip[1] - sgn * 2), (root[0] + 6, root[1] - sgn)])
        pygame.draw.polygon(surf, _C4_HULL, [
            (root[0] + 1, root[1]), (tip[0] + 1, tip[1]),
            (root[0] + 6, root[1] - sgn)])

    # ── Reactor side-vents that breathe green (glow scales with pulse) ───
    for sgn in (-1, 1):
        vent = pygame.Rect(0, 0, 6, 3)
        vent.center = (BCX, BCY + sgn * 10)
        vy = _glow(int(4 + p * 4), _C4_NEON, alpha=int(60 + p * 90))
        surf.blit(vy, vy.get_rect(center=vent.center).topleft,
                  special_flags=pygame.BLEND_RGBA_ADD)

    # ── Lean dart fuselage ───────────────────────────────────────────────
    body = [(nose_x, BCY), (nose_x - 15, BCY - 6), (tail_x, BCY - 5),
            (tail_x - 3, BCY), (tail_x, BCY + 5), (nose_x - 15, BCY + 6)]
    pygame.draw.polygon(surf, _C4_HULL, body)
    pygame.draw.polygon(surf, _C4_HULL_H,
                        [(nose_x - 4, BCY - 1), (nose_x - 15, BCY - 4),
                         (tail_x, BCY - 3), (tail_x, BCY - 1)])
    pygame.draw.polygon(surf, _C4_EDGE, body, 1)

    # ── Neon trim: forward-swept leading edges + side-vent slits + nose ──
    edges = []
    for sgn in (-1, 1):
        root = (tail_x + 12, BCY + sgn * 5)
        tip  = (nose_x - 16, BCY + sgn * 19)
        edges.append((tip, (tip[0] + 7, tip[1] - sgn * 2)))   # glowing wingtip rail
        edges.append((root, tip))
        edges.append(((BCX - 3, BCY + sgn * 10), (BCX + 3, BCY + sgn * 10)))  # vent slit
    edges.append(((nose_x, BCY), (nose_x - 15, BCY - 6)))
    edges.append(((nose_x, BCY), (nose_x - 15, BCY + 6)))
    _neon_edges(surf, edges, _C4_NEON, _C4_HOT, 1)

    # ── Engine eye + canopy ──────────────────────────────────────────────
    pygame.draw.circle(surf, _C4_NEON, (tail_x - 2, BCY), 3)
    pygame.draw.circle(surf, (255, 255, 255), (tail_x - 3, BCY), 1)
    _energy_canopy(surf, nose_x - 11, BCY, _C4_NEON, _C4_HOT)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v5 · GOLD SOVEREIGN — a FACETED diamond cruiser, GOLD energy trim with a full
#   aura, ONE huge plasma core. The premium/legendary take: a symmetric faceted
#   gem-hull with bright gold piping along every facet seam and a big gold core
#   — the 'most expensive' read of the five.
# ═════════════════════════════════════════════════════════════════════════════
_C5_HULL   = (60, 52, 34)
_C5_HULL_D = (40, 34, 20)
_C5_HULL_H = (120, 106, 70)
_C5_EDGE   = (24, 20, 10)
_C5_NEON   = (255, 200, 60)
_C5_HOT    = (255, 244, 200)


def build_scifi_v5(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 54 + pit
    tail_x = 16

    # ── Big single gold plasma core + full warm aura ─────────────────────
    plen = int(14 + p * 12)
    big = _glow(int(14 + p * 6), _C5_NEON, alpha=int(45 + p * 50))
    surf.blit(big, big.get_rect(center=(tail_x + 2, BCY)).topleft,
              special_flags=pygame.BLEND_RGBA_ADD)
    plume = _plasma(plen, 10, (255, 252, 240), (255, 210, 90), (220, 150, 30))
    plume = pygame.transform.flip(plume, True, False)
    surf.blit(plume, (tail_x + 2 - plume.get_width(), BCY - plume.get_height() // 2))

    # ── Faceted diamond hull: a symmetric gem with mid wing-points ───────
    # Outer diamond silhouette.
    diamond = [(nose_x, BCY), (nose_x - 22, BCY - 13),
               (tail_x + 4, BCY - 9), (tail_x - 4, BCY),
               (tail_x + 4, BCY + 9), (nose_x - 22, BCY + 13)]
    pygame.draw.polygon(surf, _C5_HULL_D, diamond)
    # Inner faceting: a top-lit centre facet + a darker lower facet.
    pygame.draw.polygon(surf, _C5_HULL, [
        (nose_x, BCY), (nose_x - 20, BCY - 11), (tail_x + 4, BCY - 7),
        (tail_x - 2, BCY)])
    pygame.draw.polygon(surf, _C5_HULL_H, [
        (nose_x - 2, BCY), (nose_x - 18, BCY - 9), (BCX, BCY - 5)])
    pygame.draw.polygon(surf, _C5_EDGE, diamond, 1)

    # ── Full GOLD energy trim on every facet seam (the premium tell) ─────
    edges = [
        ((nose_x, BCY), (nose_x - 22, BCY - 13)),
        ((nose_x - 22, BCY - 13), (tail_x + 4, BCY - 9)),
        ((nose_x, BCY), (nose_x - 22, BCY + 13)),
        ((nose_x - 22, BCY + 13), (tail_x + 4, BCY + 9)),
        ((nose_x, BCY), (tail_x - 2, BCY)),                 # centre keel seam
        ((nose_x - 22, BCY - 13), (nose_x - 22, BCY + 13)), # spine seam aft
    ]
    _neon_edges(surf, edges, _C5_NEON, _C5_HOT, 1)

    # ── Bright gold core eye + canopy gem ────────────────────────────────
    pygame.draw.circle(surf, _C5_NEON, (tail_x - 1, BCY), 3)
    pygame.draw.circle(surf, (255, 255, 255), (tail_x - 2, BCY), 1)
    _energy_canopy(surf, nose_x - 14, BCY, _C5_NEON, _C5_HOT)
    return surf


# ── getters + registries ─────────────────────────────────────────────────────
get_scifi_v1 = _make_prebuilt_skin(build_scifi_v1)
get_scifi_v2 = _make_prebuilt_skin(build_scifi_v2)
get_scifi_v3 = _make_prebuilt_skin(build_scifi_v3)
get_scifi_v4 = _make_prebuilt_skin(build_scifi_v4)
get_scifi_v5 = _make_prebuilt_skin(build_scifi_v5)

# label → (getter, read-tell) for the review sheet.
VARIANTS = [
    ("v1 · CYAN INTERCEPTOR",  get_scifi_v1,
     "sleek arrowhead · subtle cyan piping · 1 big plasma core"),
    ("v2 · MAGENTA GUNSHIP",   get_scifi_v2,
     "heavy wide hull · full magenta aura · twin plasma engines"),
    ("v3 · VIOLET STARWING",   get_scifi_v3,
     "winged-X starship · violet trim · twin engines + cannon tips"),
    ("v4 · TOXIC STRIKER",     get_scifi_v4,
     "forward-swept wings · toxic-green piping · core + side vents"),
    ("v5 · GOLD SOVEREIGN",    get_scifi_v5,
     "faceted diamond cruiser · gold full-seam trim · 1 huge core"),
]

# Production registry shape (one winner lifts to skin_scifi later).
BUILDERS = {"skin_scifi": get_scifi_v1}
