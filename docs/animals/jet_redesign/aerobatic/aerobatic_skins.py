"""Candidate JET FIGHTER redesign — AEROBATIC TEAM JET, round-1 exploration.

The priciest secret skin, re-imagined as an AIR-SHOW DISPLAY jet (Blue
Angels / Thunderbirds / Red Arrows energy): high-gloss, brightly liveried,
the flashiest skin in the store. There is no flapping — the 4 base wing
poses (`parrot._WING_ANGLES`) are an AFTERBURNER PULSE: the baked exhaust
glow flares and shrinks and the nose pitches a touch. No live particles;
the spectacle is baked per frame. Some variants bake a tiny display
SMOKE-TRAIL puff (the show-jet tell) so long as it reads clean.

These are 5 genuinely different takes on ONE concept — they differ by
LIVERY (the bold structural colour shape that is the tell at 40px) and by
planform (sharp delta vs swept wing):

  v1 BLUE ANGEL   — deep navy gloss, GOLD nose + gold spear down the spine.
  v2 THUNDERBIRD  — white body, a red→blue ARROW sweeping down the fuselage.
  v3 RED ARROW    — all-red, white belly diamond + a white smoke-trail puff.
  v4 SUNBURST     — diagonal hard two-tone split (white / hot magenta-orange)
                    with a lightning bolt down the wing: a racing scheme.
  v5 GOLD JACKET  — black gloss with a gold chevron wrap + gold leading edges.

The livery is STRUCTURE — one bold high-contrast shape (a spear, an arrow,
a hard split, a chevron) — never fussy detail, so it survives the downscale
as a clean graphic.

Contract (mirrors game/animal_jet_fighter.py so the winner lifts straight
into production):

  * `build_aerobatic_vN(wing_angle_deg) -> pygame.Surface`  draws ONE flat
    frame on a 64×84 SRCALPHA canvas, fuselage mass centred at (32,44),
    NOSE-RIGHT / UPRIGHT / LEVEL (clean planform). Rotation/flip is applied
    by the game later — we do NOT bake it here.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from the local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_aerobatic": get_aerobatic, ...}` registry at the end.

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
    """Soft radial halo baked once — the warm aura behind the burner. Held
    small (rear-third) so it supports the silhouette without swallowing it."""
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
    """Shared twin-afterburner: each nozzle gets its own tight halo + plume,
    capped to the rear so the liveried nose stays the dominant read. Drawn
    NOSE-RIGHT, so plumes stream LEFT of the tail."""
    flame_len = int(13 + p * 11)
    halo_r = int((10 + p * 5) * 0.84)
    glow = _glow(halo_r, glow_col, alpha=int(60 + p * 60))
    flame = _baked_flame(flame_len, 8, core, mid, outer)
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        _blit_c(surf, glow, (tail_x - flame_len // 2 + 2, ny))
        surf.blit(flame, (tail_x + 2 - flame.get_width(), ny - flame.get_height() // 2))


def _nozzle_mouths(surf, tail_x):
    for ny in (BCY - _NOZ_DY, BCY + _NOZ_DY):
        pygame.draw.circle(surf, (255, 206, 130), (tail_x, ny), 2)
        pygame.draw.circle(surf, (255, 255, 245), (tail_x + 1, ny), 1)


def _smoke_puff(surf, tail_x, color):
    """Tiny baked display-smoke puff trailing the tail — the air-show tell.
    Kept low-alpha + soft so it reads as a coloured contrail, not a blob, and
    never fights the burner. Drawn NOSE-RIGHT → trails LEFT (aft) of the tail."""
    puff = pygame.Surface((26, 16), pygame.SRCALPHA)
    for i, (dx, r, a) in enumerate(((20, 5, 150), (14, 6, 110), (7, 7, 70), (1, 7, 36))):
        pygame.draw.circle(puff, (*color, a), (dx, 8), r)
    surf.blit(puff, (tail_x - 26, BCY - 8))


# ═════════════════════════════════════════════════════════════════════════════
# Shared planform builders (NOSE-RIGHT, UPRIGHT, LEVEL). Each livery variant
# composes: tail fins → wings → fuselage → livery shape → canopy → burner.
# `delta=True` draws a sharp single delta; otherwise a swept trapezoid wing.
# ═════════════════════════════════════════════════════════════════════════════
def _tail_fins(surf, tail_x, body_d):
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, body_d, [
            (tail_x + 6, BCY + sgn * 4), (tail_x - 6, BCY + sgn * 13),
            (tail_x - 9, BCY + sgn * 12), (tail_x - 2, BCY + sgn * 3)])


def _delta_wings(surf, nose_x, tail_x, body, body_d, body_h, edge):
    """Sharp delta swept hard back from mid-fuselage (NOSE-RIGHT)."""
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


def _swept_wings(surf, nose_x, tail_x, body, body_d, body_h, edge):
    """Trapezoidal swept wing with a squared tip — a different planform read
    from the pure delta (chunkier shoulder, straight trailing edge)."""
    for sgn in (-1, 1):
        root_x = nose_x - 14
        pygame.draw.polygon(surf, body_d, [
            (root_x, BCY + sgn * 3), (root_x - 16, BCY + sgn * 17),
            (root_x - 24, BCY + sgn * 17), (root_x - 14, BCY + sgn * 6)])
        pygame.draw.polygon(surf, body, [
            (root_x - 1, BCY + sgn * 3), (root_x - 15, BCY + sgn * 15),
            (root_x - 22, BCY + sgn * 15), (root_x - 14, BCY + sgn * 6)])
        pygame.draw.line(surf, body_h, (root_x - 1, BCY + sgn * 4),
                         (root_x - 16, BCY + sgn * 15), 1)
        pygame.draw.line(surf, edge, (root_x, BCY + sgn * 3),
                         (root_x - 16, BCY + sgn * 17), 1)


def _fuselage(surf, nose_x, tail_x, body, body_h, edge):
    """Long dart arrowhead fuselage (NOSE-RIGHT). Returns the body polygon so
    livery shapes can be clipped to it via a mask blit."""
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
    so a bold colour shape can be drawn freely then trimmed to the body
    silhouette (the livery reads as paint ON the jet, not floating)."""
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), body_poly)
    shape_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(shape_surf, (0, 0))


def _canopy(surf, nose_x, canopy, canopy_h):
    _aaellipse(surf, canopy, (nose_x - 14, BCY), 5, 3)
    _aaellipse(surf, canopy_h, (nose_x - 12, BCY - 1), 2, 1)
    pygame.draw.circle(surf, canopy_h, (nose_x - 12, BCY - 1), 1)


_CANOPY  = (60, 150, 205)
_CANOPY_H = (180, 230, 250)


# ═════════════════════════════════════════════════════════════════════════════
# v1 · BLUE ANGEL — deep navy gloss, sharp delta. LIVERY = a bold GOLD nose +
#     a gold SPEAR running the spine to the tail. Premium navy/gold.
# ═════════════════════════════════════════════════════════════════════════════
_BA_BODY  = (28, 52, 138)
_BA_BODY_D = (16, 32, 96)
_BA_BODY_H = (70, 104, 200)
_BA_EDGE  = (10, 20, 64)
_BA_GOLD  = (255, 204, 60)
_BA_GOLD_D = (212, 158, 24)
_BA_GOLD_H = (255, 234, 150)


def build_aerobatic_v1(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 52 - pit
    tail_x = 14

    _burner(surf, tail_x, p, core=(255, 255, 244), mid=(150, 190, 255),
            outer=(60, 110, 230), glow_col=(90, 140, 255))
    _tail_fins(surf, tail_x, _BA_BODY_D)
    _delta_wings(surf, nose_x, tail_x, _BA_BODY, _BA_BODY_D, _BA_BODY_H, _BA_EDGE)
    body_poly = _fuselage(surf, nose_x, tail_x, _BA_BODY, _BA_BODY_H, _BA_EDGE)

    # LIVERY: gold nose cap + a tapering gold spear down the spine to the tail.
    livery = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(livery, _BA_GOLD, [
        (nose_x, BCY), (nose_x - 12, BCY - 5), (nose_x - 12, BCY + 5)])
    pygame.draw.polygon(livery, _BA_GOLD, [
        (nose_x - 10, BCY - 3), (tail_x + 2, BCY - 1),
        (tail_x + 2, BCY + 1), (nose_x - 10, BCY + 3)])
    _clip_to_body(surf, livery, body_poly)
    pygame.draw.polygon(surf, _BA_GOLD_H, [
        (nose_x - 2, BCY - 1), (nose_x - 10, BCY - 2), (nose_x - 10, BCY)])
    # Gold leading-edge accent on the delta — ties the wing into the livery.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _BA_GOLD, (nose_x - 19, BCY + sgn * 2),
                         (tail_x + 6, BCY + sgn * 15), 1)

    _canopy(surf, nose_x, (40, 70, 150), (160, 200, 255))
    _nozzle_mouths(surf, tail_x)
    return surf


get_aerobatic_v1 = _make_prebuilt_skin(build_aerobatic_v1)


# ═════════════════════════════════════════════════════════════════════════════
# v2 · THUNDERBIRD — white gloss body, sharp delta. LIVERY = a bold RED→BLUE
#     ARROW sweeping down the fuselage (the air-show classic). The arrow IS
#     the silhouette tell. White reads brilliant on day AND night.
# ═════════════════════════════════════════════════════════════════════════════
_TB_BODY  = (244, 246, 250)
_TB_BODY_D = (196, 202, 216)
_TB_BODY_H = (255, 255, 255)
_TB_EDGE  = (120, 128, 150)
_TB_RED   = (224, 48, 52)
_TB_BLUE  = (32, 72, 190)
_TB_BLUE_H = (90, 130, 240)


def build_aerobatic_v2(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 52 - pit
    tail_x = 14

    _burner(surf, tail_x, p, core=(255, 255, 244), mid=(255, 170, 70),
            outer=(236, 80, 44), glow_col=(255, 150, 64))
    _tail_fins(surf, tail_x, (60, 90, 200))
    _delta_wings(surf, nose_x, tail_x, _TB_BODY, _TB_BODY_D, _TB_BODY_H, _TB_EDGE)
    body_poly = _fuselage(surf, nose_x, tail_x, _TB_BODY, _TB_BODY_H, _TB_EDGE)

    # LIVERY: a swept ARROW down the body — red leading wedge, blue trailing
    # tail-band, both clipped to the fuselage. A single high-contrast graphic.
    livery = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(livery, _TB_RED, [
        (nose_x, BCY), (nose_x - 8, BCY - 5), (nose_x - 22, BCY - 3),
        (nose_x - 14, BCY), (nose_x - 22, BCY + 3), (nose_x - 8, BCY + 5)])
    pygame.draw.polygon(livery, _TB_BLUE, [
        (nose_x - 22, BCY - 3), (nose_x - 34, BCY - 2),
        (nose_x - 34, BCY + 2), (nose_x - 22, BCY + 3), (nose_x - 14, BCY)])
    pygame.draw.polygon(livery, _TB_BLUE, [
        (tail_x + 10, BCY - 4), (tail_x + 2, BCY - 4),
        (tail_x + 2, BCY + 4), (tail_x + 10, BCY + 4)])
    _clip_to_body(surf, livery, body_poly)
    # Red wingtip flashes + blue inboard band so the arrow reads onto the wing.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _TB_RED, (nose_x - 19, BCY + sgn * 2),
                         (tail_x + 7, BCY + sgn * 14), 2)
        pygame.draw.circle(surf, _TB_BLUE, (tail_x + 5, BCY + sgn * 16), 2)

    _canopy(surf, nose_x, (40, 60, 150), (170, 200, 255))
    _nozzle_mouths(surf, tail_x)
    return surf


get_aerobatic_v2 = _make_prebuilt_skin(build_aerobatic_v2)


# ═════════════════════════════════════════════════════════════════════════════
# v3 · RED ARROW — all-red gloss, sharp delta. LIVERY = a bold WHITE belly
#     diamond + white leading edges, and a baked WHITE smoke-trail puff (the
#     Red Arrows tell). Pure, iconic, the most "display team" of the five.
# ═════════════════════════════════════════════════════════════════════════════
_RA_BODY  = (214, 38, 44)
_RA_BODY_D = (158, 22, 30)
_RA_BODY_H = (255, 96, 88)
_RA_EDGE  = (110, 14, 22)
_RA_WHITE = (250, 250, 248)
_RA_WHITE_D = (210, 212, 218)


def build_aerobatic_v3(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 52 - pit
    tail_x = 14

    # White display smoke first (furthest aft), then the burner over it.
    _smoke_puff(surf, tail_x, (236, 240, 246))
    _burner(surf, tail_x, p, core=(255, 255, 244), mid=(255, 180, 80),
            outer=(236, 80, 44), glow_col=(255, 150, 64))
    _tail_fins(surf, tail_x, _RA_BODY_D)
    _delta_wings(surf, nose_x, tail_x, _RA_BODY, _RA_BODY_D, _RA_BODY_H, _RA_EDGE)
    body_poly = _fuselage(surf, nose_x, tail_x, _RA_BODY, _RA_BODY_H, _RA_EDGE)

    # LIVERY: a bold white diamond down the centre of the fuselage + white nose.
    livery = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(livery, _RA_WHITE, [
        (nose_x, BCY), (nose_x - 10, BCY - 4), (nose_x - 10, BCY + 4)])
    pygame.draw.polygon(livery, _RA_WHITE, [
        (nose_x - 14, BCY), (nose_x - 28, BCY - 4),
        (tail_x + 6, BCY), (nose_x - 28, BCY + 4)])
    _clip_to_body(surf, livery, body_poly)
    # White leading edges — the Red Arrows wing flash.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _RA_WHITE, (nose_x - 19, BCY + sgn * 2),
                         (tail_x + 4, BCY + sgn * 18), 2)

    _canopy(surf, nose_x, (40, 60, 140), (170, 200, 255))
    _nozzle_mouths(surf, tail_x)
    return surf


get_aerobatic_v3 = _make_prebuilt_skin(build_aerobatic_v3)


# ═════════════════════════════════════════════════════════════════════════════
# v4 · SUNBURST RACER — swept wing (different planform). LIVERY = a HARD
#     diagonal two-tone split (white fore / hot magenta-orange aft) with a
#     yellow LIGHTNING bolt down the wing. A modern racing scheme, the most
#     graphic of the five.
# ═════════════════════════════════════════════════════════════════════════════
_SB_WHITE = (248, 248, 250)
_SB_WHITE_D = (206, 208, 216)
_SB_HOT   = (255, 70, 120)        # hot magenta
_SB_HOT_D = (210, 36, 92)
_SB_HOT_H = (255, 140, 170)
_SB_ORANGE = (255, 150, 40)
_SB_BOLT  = (255, 226, 60)
_SB_EDGE  = (120, 40, 70)


def build_aerobatic_v4(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 52 - pit
    tail_x = 14

    _burner(surf, tail_x, p, core=(255, 255, 244), mid=(255, 150, 90),
            outer=(255, 70, 120), glow_col=(255, 100, 150))
    _tail_fins(surf, tail_x, _SB_HOT_D)
    # Swept (not delta) wing in hot magenta with a lightning bolt.
    _swept_wings(surf, nose_x, tail_x, _SB_HOT, _SB_HOT_D, _SB_HOT_H, _SB_EDGE)
    for sgn in (-1, 1):
        root_x = nose_x - 14
        pygame.draw.lines(surf, _SB_BOLT, False, [
            (root_x - 3, BCY + sgn * 6), (root_x - 9, BCY + sgn * 9),
            (root_x - 7, BCY + sgn * 11), (root_x - 15, BCY + sgn * 14)], 2)

    # Body: hard diagonal split — white nose half, hot-magenta tail half.
    body_poly = [(nose_x, BCY), (nose_x - 16, BCY - 6), (tail_x - 4, BCY - 5),
                 (tail_x - 6, BCY), (tail_x - 4, BCY + 5), (nose_x - 16, BCY + 6)]
    pygame.draw.polygon(surf, _SB_WHITE, body_poly)
    split = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    # Diagonal so the split reads as a swept slash, not a vertical bar.
    pygame.draw.polygon(split, _SB_HOT, [
        (nose_x - 20, BCY - 6), (nose_x - 12, BCY + 6),
        (tail_x - 4, BCY + 6), (tail_x - 6, BCY - 6)])
    # A thin orange seam right on the diagonal — the sunburst edge.
    pygame.draw.line(split, _SB_ORANGE, (nose_x - 20, BCY - 6),
                     (nose_x - 12, BCY + 6), 2)
    _clip_to_body(surf, split, body_poly)
    pygame.draw.polygon(surf, _SB_EDGE, body_poly, 1)
    pygame.draw.polygon(surf, _SB_WHITE_D,
                        [(nose_x - 4, BCY - 4), (nose_x - 16, BCY - 4),
                         (nose_x - 16, BCY - 6), (nose_x - 4, BCY - 5)])

    _canopy(surf, nose_x, (40, 50, 80), (200, 210, 240))
    _nozzle_mouths(surf, tail_x)
    return surf


get_aerobatic_v4 = _make_prebuilt_skin(build_aerobatic_v4)


# ═════════════════════════════════════════════════════════════════════════════
# v5 · GOLD JACKET — black gloss body, sharp delta. LIVERY = a bold GOLD
#     CHEVRON wrapping the nose + gold leading edges + gold tail band. Black/
#     gold = the most "expensive" reading; gold survives on day AND night.
# ═════════════════════════════════════════════════════════════════════════════
_GJ_BODY  = (34, 36, 44)
_GJ_BODY_D = (18, 20, 26)
_GJ_BODY_H = (78, 82, 96)
_GJ_EDGE  = (8, 8, 12)
_GJ_GOLD  = (255, 200, 56)
_GJ_GOLD_D = (206, 150, 24)
_GJ_GOLD_H = (255, 234, 150)


def build_aerobatic_v5(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nose_x = 52 - pit
    tail_x = 14

    _burner(surf, tail_x, p, core=(255, 255, 244), mid=(255, 210, 110),
            outer=(255, 150, 50), glow_col=(255, 190, 80))
    _tail_fins(surf, tail_x, _GJ_BODY_D)
    _delta_wings(surf, nose_x, tail_x, _GJ_BODY, _GJ_BODY_D, _GJ_BODY_H, _GJ_EDGE)
    body_poly = _fuselage(surf, nose_x, tail_x, _GJ_BODY, _GJ_BODY_H, _GJ_EDGE)

    # LIVERY: a bold gold chevron wrapping the nose, a thin gold spine line,
    # and a gold tail band — black/gold reads premium and high-contrast.
    livery = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(livery, _GJ_GOLD, [
        (nose_x, BCY), (nose_x - 13, BCY - 5), (nose_x - 18, BCY - 4),
        (nose_x - 9, BCY), (nose_x - 18, BCY + 4), (nose_x - 13, BCY + 5)])
    pygame.draw.polygon(livery, _GJ_GOLD, [
        (nose_x - 9, BCY - 1), (tail_x + 4, BCY - 1),
        (tail_x + 4, BCY + 1), (nose_x - 9, BCY + 1)])
    pygame.draw.polygon(livery, _GJ_GOLD, [
        (tail_x + 9, BCY - 4), (tail_x + 3, BCY - 4),
        (tail_x + 3, BCY + 4), (tail_x + 9, BCY + 4)])
    _clip_to_body(surf, livery, body_poly)
    pygame.draw.polygon(surf, _GJ_GOLD_H, [
        (nose_x - 1, BCY - 1), (nose_x - 12, BCY - 4), (nose_x - 12, BCY - 3)])
    # Gold delta leading edges — the chevron continues onto the wing.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _GJ_GOLD, (nose_x - 19, BCY + sgn * 2),
                         (tail_x + 4, BCY + sgn * 18), 2)
        pygame.draw.circle(surf, _GJ_GOLD_H, (nose_x - 19, BCY + sgn * 2), 1)

    _canopy(surf, nose_x, (60, 55, 30), (255, 230, 150))
    _nozzle_mouths(surf, tail_x)
    return surf


get_aerobatic_v5 = _make_prebuilt_skin(build_aerobatic_v5)


# ─────────────────────────────────────────────────────────────────────────────
# Review-sheet registry. label → getter.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_aerobatic": get_aerobatic_v1,   # primary registered id (winner lifts here)
    "v1_blue_angel":  get_aerobatic_v1,
    "v2_thunderbird": get_aerobatic_v2,
    "v3_red_arrow":   get_aerobatic_v3,
    "v4_sunburst":    get_aerobatic_v4,
    "v5_gold_jacket": get_aerobatic_v5,
}
