"""Candidate JET FIGHTER redesign — NAVAL INTERCEPTOR (`naval`) round-1.

Five from-scratch takes on ONE concept: an F-14 Tomcat / Top Gun-style
carrier interceptor. The identity that separates this from the current
gunmetal "Steel Raptor" is the NAVY structure: variable-sweep WINGS, TWIN
canted tail fins, a long two-seat fuselage, wide-spaced engine nacelles
with a twin afterburner.

There is no flapping. The 4 base wing poses (`parrot._WING_ANGLES`) are
reinterpreted as an AFTERBURNER PULSE (+ a touch of nose pitch): the baked
twin exhaust flares and shrinks across the 4 frames. No live particle
system — the spectacle is baked per frame so both build targets stay
identical and cheap.

Contract (mirrors game/animal_jet_fighter.py so the winner lifts straight
into a production game/animal_jet_fighter.py):

  * `build_naval_vN(wing_angle_deg) -> pygame.Surface`  draws ONE flat frame
    on a 64×84 SRCALPHA canvas, fuselage mass centred at (32,44).
  * The jet is drawn NOSE-RIGHT, UPRIGHT, LEVEL (clean top-down planform).
    NO baked rotation/flip — the game applies the inverted nose-up
    presentation later; here it just nudges right.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from
    `_make_prebuilt_skin(build_fn)` (4 flat frames + per-(frame, 3°)
    rotation cache, each outlined with the house silhouette outline).
  * `BUILDERS = {"skin_naval": get_naval}` registers the round's lead build
    so the review sheet + production registry agree on one key.

The 5 sub-takes explore the F-14's distinctive variables so the
art-director can pick a direction:

  v1 LOW-VIS PROWLER   wings-forward soaring, twin tail, low-vis TPS greys,
                       long radar nose. The understated tactical read.
  v2 FLEET DEFENDER    wings swept back fast, classic Light-Gull-Gray over
                       white with a bold red squadron stripe + modex "201".
  v3 JOLLY ROGERS      wings mid-sweep, sea-black livery with a small white
                       skull motif + yellow tail caps. The showpiece.
  v4 GOLD ACE          navy-blue + gold, single tall tail variant (deck-test
                       bird), blunt nose, gold leading-edge chevrons.
  v5 SWING-WING STRIKE wings hard-back interceptor dash, gunship-grey with a
                       single bold high-vis stripe, long nose, max burner.

Why the geometry sits where it does: collision is a fixed 14px circle at the
BODY centre, so the fuselage mass stays at (32,44) on the 64×84 canvas for
fairness — wings/stabs may span wider, but the body stays anchored so the
in-game center-blit rotation maths still holds.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + body anchor (mirror animal_jet_fighter composite layout) ────────
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
    """Afterburner throttle 0..1 from the wing angle: the 4 poses (50→-40)
    triangle-wrap to bright-bright in the centre, dim-dim at the ends — a
    heartbeat the eye reads as thrust at 40px without strobing."""
    t = (50 - angle_deg) / 90.0          # 50→0, 20→.33, -10→.67, -40→1
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """Tiny nose pitch (px) across the 4 frames so the jet 'breathes' with
    the burner instead of sitting dead-still. ±1px is enough at 40px."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


def _glow(radius, color, alpha=120):
    """Soft radial halo baked once — the warm aura behind the burner.
    Concentric fading rings so the glow supports the silhouette, never
    swallows it. Caller caps the radius to the rear third of the jet."""
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 8
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = int(radius * i / steps)
        pygame.draw.circle(s, (*color, a), (radius, radius), r)
    return s


def _baked_flame(length, width, core, mid, outer):
    """Bake ONE afterburner plume on its own SRCALPHA surface: layered
    teardrop (outer haze → mid → white-hot core) + shock-diamond beads. The
    core stays NARROW vs the haze so two plumes keep two distinct white
    cores at 40px even when their soft hazes kiss.

    The plume's LEFT edge is the nozzle mouth and it streams RIGHT, so a
    nose-RIGHT jet blits it pointing aft (off the tail to the right)."""
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
    # White-hot pinch right at the nozzle mouth (tight bright core seed).
    pygame.draw.circle(surf, (255, 255, 255, 255), (w - pad - 2, cy),
                       max(1, width // 8))
    for k in range(1, 3):
        dx = w - pad - int(length * 0.16 * k) - 2
        rad = max(1, width // 10 - (k - 1))
        pygame.draw.circle(surf, (255, 250, 232, 235), (dx, cy), rad)
    return surf


def _twin_burner(surf, tail_x, p, noz_dy, *, core, mid, outer, halo):
    """Twin afterburner aft of the tail: each nozzle gets its OWN tight halo
    (not one fused blob), halo radius capped to the rear so peak glow stays
    behind the silhouette. Returns the nozzle-mouth y-pair so the caller can
    paint glowing nozzle mouths to root the flames."""
    flame_len = int(13 + p * 11)
    halo_r = int((10 + p * 5) * 0.84)
    glow = _glow(halo_r, halo, alpha=int(60 + p * 60))
    flame = _baked_flame(flame_len, 8, core, mid, outer)
    ys = (BCY - noz_dy, BCY + noz_dy)
    for ny in ys:
        _blit_c(surf, glow, (tail_x + flame_len // 2 + 2, ny))
        surf.blit(flame, (tail_x - flame.get_width() + flame_len + 4,
                          ny - flame.get_height() // 2))
    return ys


# Shared warm flame colour temperature across all liveries (the afterburner
# tell is consistent; only the airframe livery changes per sub-take).
_F_CORE  = (255, 255, 244)
_F_MID   = (255, 168, 60)
_F_OUTER = (236, 72, 36)
_F_HALO  = (255, 150, 64)
_NOZ_HOT = (255, 206, 130)
_NOZ_WHT = (255, 255, 245)


def _nozzles(surf, tail_x, ys):
    for ny in ys:
        pygame.draw.circle(surf, _NOZ_HOT, (tail_x, ny), 2)
        pygame.draw.circle(surf, _NOZ_WHT, (tail_x - 1, ny), 1)


# ═════════════════════════════════════════════════════════════════════════════
# Shared structural primitive: a NAVAL INTERCEPTOR planform drawn NOSE-RIGHT.
#
# The five builds all start from this skeleton and then differ in wing sweep,
# tail count, nose length, and (most of all) LIVERY. Keeping the airframe in
# one helper guarantees they read as the SAME jet wearing five paint jobs,
# while the brief's variables (sweep / tail / nose / livery) stay knobs.
#
# `sweep` 0..1   : 0 = wings forward (soaring), 1 = wings hard-back (fast).
# `nose`  px     : how far the radar nose juts past the body (long vs blunt).
# `twin_tail`    : True = twin canted fins (F-14 identity); False = single.
# Colours are passed in so each livery owns its value structure.
# ═════════════════════════════════════════════════════════════════════════════
def _naval_airframe(surf, p, pit, *, sweep, nose, twin_tail,
                    body, body_d, body_h, edge, wing, wing_d, wing_h,
                    canopy, canopy_h, draw_glove=True):
    # Nose RIGHT (+x), exhaust streams off the tail to the LEFT-of-mouth/right.
    tail_x = 14 - pit
    nose_base_x = 46
    nose_tip_x = nose_base_x + nose

    # ── Wide-spaced engine nacelles (the F-14 "tunnel" body) drawn first so
    #    the central fuselage spine overlaps their inner edges. ──────────────
    nac_dy = 7
    for sgn in (-1, 1):
        ny = BCY + sgn * nac_dy
        pygame.draw.polygon(surf, body_d, [
            (tail_x, ny - 3), (nose_base_x - 6, ny - 4),
            (nose_base_x - 6, ny + 4), (tail_x, ny + 3)])
        pygame.draw.polygon(surf, body, [
            (tail_x + 2, ny - 2), (nose_base_x - 8, ny - 3),
            (nose_base_x - 8, ny + 2), (tail_x + 2, ny + 2)])

    # ── Twin canted tail fins (or one tall fin) — the navy identity. ────────
    if twin_tail:
        for sgn in (-1, 1):
            pygame.draw.polygon(surf, body_d, [
                (tail_x + 6, BCY + sgn * 4), (tail_x - 6, BCY + sgn * 13),
                (tail_x - 9, BCY + sgn * 12), (tail_x - 2, BCY + sgn * 3)])
            pygame.draw.polygon(surf, body, [
                (tail_x + 5, BCY + sgn * 5), (tail_x - 4, BCY + sgn * 11),
                (tail_x - 1, BCY + sgn * 4)])
    else:
        pygame.draw.polygon(surf, body_d, [
            (tail_x + 7, BCY - 2), (tail_x - 7, BCY - 16),
            (tail_x - 11, BCY - 15), (tail_x - 1, BCY - 1)])
        pygame.draw.polygon(surf, body, [
            (tail_x + 6, BCY - 3), (tail_x - 5, BCY - 13),
            (tail_x - 2, BCY - 2)])

    # ── Horizontal stabilators (small all-moving rear tailplanes). ──────────
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, body_d, [
            (tail_x + 4, BCY + sgn * 3), (tail_x - 5, BCY + sgn * 9),
            (tail_x + 1, BCY + sgn * 4)])

    # ── Variable-sweep wings. sweep blends a forward soar vs a swept dart.
    #    Each wing: dark underside, lit top facet, value leading-edge line. ──
    root_x = nose_base_x - 16
    # Forward (sweep 0) the tip sits ahead + wide; back (sweep 1) it tucks aft.
    tip_x = root_x - 2 - sweep * 22
    tip_dy = 22 - sweep * 5
    glove_x = root_x + 8
    for sgn in (-1, 1):
        if draw_glove:
            # Fixed wing-glove fairing root that stays put as the wing swings.
            pygame.draw.polygon(surf, body_d, [
                (root_x, BCY + sgn * 4), (glove_x + 4, BCY + sgn * 8),
                (glove_x + 6, BCY + sgn * 5), (root_x + 2, BCY + sgn * 2)])
        pygame.draw.polygon(surf, wing_d, [
            (root_x, BCY + sgn * 3), (tip_x - 1, BCY + sgn * tip_dy),
            (tip_x + 5, BCY + sgn * tip_dy), (root_x + 9, BCY + sgn * 5)])
        pygame.draw.polygon(surf, wing, [
            (root_x + 1, BCY + sgn * 3), (tip_x + 1, BCY + sgn * (tip_dy - 2)),
            (root_x + 8, BCY + sgn * 5)])
        pygame.draw.polygon(surf, wing_h, [
            (root_x + 2, BCY + sgn * 3), (root_x + 11, BCY + sgn * 6),
            (tip_x + 4, BCY + sgn * (tip_dy - 5)),
            (tip_x + 2, BCY + sgn * (tip_dy - 4))])
        pygame.draw.line(surf, edge, (root_x, BCY + sgn * 3),
                         (tip_x, BCY + sgn * tip_dy), 1)
        # Wingtip rail with a small accent cap.
        pygame.draw.line(surf, wing_h, (tip_x, BCY + sgn * tip_dy),
                         (tip_x + 6, BCY + sgn * tip_dy), 2)

    # ── Long tandem fuselage: nacelle tunnel + central radar nose spear. ────
    body_pts = [
        (nose_tip_x, BCY),
        (nose_base_x, BCY - 4),
        (root_x + 4, BCY - 6),
        (tail_x + 2, BCY - 5),
        (tail_x, BCY),
        (tail_x + 2, BCY + 5),
        (root_x + 4, BCY + 6),
        (nose_base_x, BCY + 4),
    ]
    pygame.draw.polygon(surf, body, body_pts)
    pygame.draw.polygon(surf, edge, body_pts, 1)
    # Spine highlight catching light down the centreline.
    pygame.draw.polygon(surf, body_h, [
        (nose_base_x - 2, BCY - 3), (root_x + 4, BCY - 4),
        (tail_x + 4, BCY - 3), (tail_x + 4, BCY - 1),
        (root_x + 4, BCY - 1), (nose_base_x - 2, BCY - 1)])
    # Radar nose-cone shade so the long spear reads as a cone, not a needle.
    pygame.draw.polygon(surf, body_d, [
        (nose_tip_x, BCY), (nose_base_x + 2, BCY - 2),
        (nose_base_x + 2, BCY + 2)])

    return tail_x, nose_tip_x, nose_base_x, root_x


def _tandem_canopy(surf, x, canopy, canopy_h):
    """Two-seat tandem canopy: a stretched bubble with a faint frame split —
    the cool CONSTANT anchor across all 4 frames, colourblind-distinct from
    the warm burner."""
    _aaellipse(surf, canopy, (x, BCY), 6, 3)
    pygame.draw.line(surf, canopy_h, (x, BCY - 2), (x, BCY + 2), 1)
    _aaellipse(surf, canopy_h, (x + 2, BCY - 1), 2, 1)
    pygame.draw.circle(surf, canopy_h, (x + 3, BCY - 1), 1)


# ═════════════════════════════════════════════════════════════════════════════
# v1 · LOW-VIS PROWLER — wings FORWARD (soaring), TWIN tail, long radar nose,
#   low-vis Tactical-Paint-Scheme greys (Aggressor over Gunship). The
#   understated tactical read; value structure does all the work, no colour.
# ═════════════════════════════════════════════════════════════════════════════
_V1_BODY   = (128, 134, 144)
_V1_BODY_D = (82, 88, 100)
_V1_BODY_H = (176, 182, 192)
_V1_EDGE   = (52, 56, 66)
_V1_WING   = (112, 118, 130)
_V1_WING_D = (72, 78, 90)
_V1_WING_H = (160, 166, 178)
_V1_CANOPY = (70, 96, 120)            # low-vis dark-glass canopy
_V1_CANOPY_H = (150, 186, 210)


def build_naval_v1(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    ys = _twin_burner(surf, 14 - pit, p, 7, core=_F_CORE, mid=_F_MID,
                      outer=_F_OUTER, halo=_F_HALO)
    tail_x, nose_tip_x, nose_base_x, root_x = _naval_airframe(
        surf, p, pit, sweep=0.05, nose=11, twin_tail=True,
        body=_V1_BODY, body_d=_V1_BODY_D, body_h=_V1_BODY_H, edge=_V1_EDGE,
        wing=_V1_WING, wing_d=_V1_WING_D, wing_h=_V1_WING_H,
        canopy=_V1_CANOPY, canopy_h=_V1_CANOPY_H)
    # Low-vis tail flash: a single subtly-darker bar on each fin (no colour).
    for sgn in (-1, 1):
        pygame.draw.line(surf, _V1_BODY_D, (tail_x - 2, BCY + sgn * 6),
                         (tail_x - 5, BCY + sgn * 11), 1)
    _tandem_canopy(surf, nose_base_x - 6, _V1_CANOPY, _V1_CANOPY_H)
    _nozzles(surf, tail_x, ys)
    # Tiny dark low-vis national-insignia ghost on the wing root (value tell).
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _V1_BODY_D, (root_x + 4, BCY + sgn * 12), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v2 · FLEET DEFENDER — wings SWEPT BACK (fast), TWIN tail, blunt-ish nose,
#   classic Light-Gull-Gray over white with a BOLD red squadron stripe + a
#   white modex "201" on the tail. The colourful high-vis 1970s carrier look.
# ═════════════════════════════════════════════════════════════════════════════
_V2_BODY   = (196, 200, 206)          # light gull gray
_V2_BODY_D = (146, 150, 158)
_V2_BODY_H = (236, 238, 242)
_V2_EDGE   = (96, 100, 110)
_V2_WING   = (188, 192, 200)
_V2_WING_D = (140, 144, 152)
_V2_WING_H = (232, 234, 240)
_V2_RED    = (212, 52, 46)            # bold squadron stripe
_V2_CANOPY = (60, 130, 180)
_V2_CANOPY_H = (180, 224, 248)
_V2_WHITE  = (248, 248, 246)


def build_naval_v2(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    ys = _twin_burner(surf, 14 - pit, p, 7, core=_F_CORE, mid=_F_MID,
                      outer=_F_OUTER, halo=_F_HALO)
    tail_x, nose_tip_x, nose_base_x, root_x = _naval_airframe(
        surf, p, pit, sweep=0.85, nose=7, twin_tail=True,
        body=_V2_BODY, body_d=_V2_BODY_D, body_h=_V2_BODY_H, edge=_V2_EDGE,
        wing=_V2_WING, wing_d=_V2_WING_D, wing_h=_V2_WING_H,
        canopy=_V2_CANOPY, canopy_h=_V2_CANOPY_H)
    # BOLD squadron stripe: a red band wrapping the rear fuselage spine — the
    # high-vis tell that reads as STRUCTURE (a value+hue bar) at 40px.
    pygame.draw.polygon(surf, _V2_RED, [
        (tail_x + 6, BCY - 5), (tail_x + 12, BCY - 5),
        (tail_x + 12, BCY + 5), (tail_x + 6, BCY + 5)])
    pygame.draw.polygon(surf, _V2_BODY_H, [
        (tail_x + 6, BCY - 5), (tail_x + 12, BCY - 5),
        (tail_x + 12, BCY - 4), (tail_x + 6, BCY - 4)])
    # Red tail-fin caps with a white modex bar (the "201" stand-in at scale).
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _V2_RED, [
            (tail_x - 1, BCY + sgn * 10), (tail_x - 6, BCY + sgn * 13),
            (tail_x - 9, BCY + sgn * 12), (tail_x - 4, BCY + sgn * 9)])
        pygame.draw.line(surf, _V2_WHITE, (tail_x - 3, BCY + sgn * 10),
                         (tail_x - 6, BCY + sgn * 12), 1)
    # Red wing-leading-edge accent (small warm tell, value-clear on the gray).
    for sgn in (-1, 1):
        pygame.draw.line(surf, _V2_RED, (root_x + 1, BCY + sgn * 3),
                         (root_x - 6, BCY + sgn * 13), 1)
    _tandem_canopy(surf, nose_base_x - 6, _V2_CANOPY, _V2_CANOPY_H)
    _nozzles(surf, tail_x, ys)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v3 · JOLLY ROGERS — wings MID-SWEEP, TWIN tail, long nose, sea-black livery
#   with a small WHITE skull-and-crossbones motif on the spine + yellow tail
#   caps. VF-84's famous showpiece; the most "premium / secret" feeling.
# ═════════════════════════════════════════════════════════════════════════════
_V3_BODY   = (44, 48, 58)             # sea black
_V3_BODY_D = (24, 26, 34)
_V3_BODY_H = (92, 98, 112)
_V3_EDGE   = (12, 14, 20)
_V3_WING   = (40, 44, 54)
_V3_WING_D = (22, 24, 32)
_V3_WING_H = (84, 90, 104)
_V3_GOLD   = (244, 198, 64)           # yellow tail caps
_V3_BONE   = (238, 240, 244)          # skull white
_V3_CANOPY = (78, 150, 196)
_V3_CANOPY_H = (180, 224, 248)


def build_naval_v3(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    ys = _twin_burner(surf, 14 - pit, p, 7, core=_F_CORE, mid=_F_MID,
                      outer=_F_OUTER, halo=_F_HALO)
    tail_x, nose_tip_x, nose_base_x, root_x = _naval_airframe(
        surf, p, pit, sweep=0.45, nose=10, twin_tail=True,
        body=_V3_BODY, body_d=_V3_BODY_D, body_h=_V3_BODY_H, edge=_V3_EDGE,
        wing=_V3_WING, wing_d=_V3_WING_D, wing_h=_V3_WING_H,
        canopy=_V3_CANOPY, canopy_h=_V3_CANOPY_H)
    # GOLD full tail-fin caps — the high-value tell that lifts the black off a
    # night sky and frames the silhouette's twin-tail identity.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _V3_GOLD, [
            (tail_x + 1, BCY + sgn * 7), (tail_x - 6, BCY + sgn * 13),
            (tail_x - 9, BCY + sgn * 12), (tail_x - 2, BCY + sgn * 6)])
    # Small white skull motif on the spine: a bone-white round + two cross
    # struts. Kept BOLD (a clear white blob, not fussy decal lines) so it
    # survives the downscale as "there is a pale mark on the back".
    sx, sy = root_x + 1, BCY
    pygame.draw.circle(surf, _V3_BONE, (sx, sy), 3)
    pygame.draw.circle(surf, _V3_BODY_D, (sx - 1, sy - 1), 1)   # eye socket
    pygame.draw.circle(surf, _V3_BODY_D, (sx + 1, sy - 1), 1)
    # Crossbones: two short pale bars under the skull.
    pygame.draw.line(surf, _V3_BONE, (sx - 4, sy + 3), (sx + 4, sy + 3), 2)
    pygame.draw.line(surf, _V3_BONE, (sx - 4, sy + 3), (sx - 5, sy + 2), 2)
    pygame.draw.line(surf, _V3_BONE, (sx + 4, sy + 3), (sx + 5, sy + 2), 2)
    _tandem_canopy(surf, nose_base_x - 6, _V3_CANOPY, _V3_CANOPY_H)
    _nozzles(surf, tail_x, ys)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v4 · GOLD ACE — wings FORWARD-MID, SINGLE tall tail (a deck-test / aggressor
#   variant), BLUNT nose, navy-blue airframe with GOLD leading-edge chevrons
#   and a gold spine. The luxe "ace" read; single tail deliberately contrasts
#   v1-v3 to show the brief's tail variable.
# ═════════════════════════════════════════════════════════════════════════════
_V4_BODY   = (38, 56, 104)            # navy blue
_V4_BODY_D = (22, 36, 74)
_V4_BODY_H = (84, 110, 168)
_V4_EDGE   = (14, 22, 48)
_V4_WING   = (34, 52, 98)
_V4_WING_D = (20, 34, 70)
_V4_WING_H = (78, 104, 162)
_V4_GOLD   = (246, 196, 78)
_V4_GOLD_H = (255, 230, 150)
_V4_CANOPY = (120, 200, 230)
_V4_CANOPY_H = (210, 240, 252)


def build_naval_v4(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    ys = _twin_burner(surf, 14 - pit, p, 7, core=_F_CORE, mid=_F_MID,
                      outer=_F_OUTER, halo=_F_HALO)
    tail_x, nose_tip_x, nose_base_x, root_x = _naval_airframe(
        surf, p, pit, sweep=0.25, nose=5, twin_tail=False,
        body=_V4_BODY, body_d=_V4_BODY_D, body_h=_V4_BODY_H, edge=_V4_EDGE,
        wing=_V4_WING, wing_d=_V4_WING_D, wing_h=_V4_WING_H,
        canopy=_V4_CANOPY, canopy_h=_V4_CANOPY_H)
    # GOLD spine band running the fuselage — the luxe value tell on the navy.
    pygame.draw.polygon(surf, _V4_GOLD, [
        (nose_base_x - 2, BCY - 1), (root_x + 4, BCY - 2),
        (tail_x + 4, BCY - 1), (tail_x + 4, BCY + 1),
        (root_x + 4, BCY), (nose_base_x - 2, BCY + 1)])
    pygame.draw.line(surf, _V4_GOLD_H, (nose_base_x - 2, BCY - 1),
                     (root_x + 4, BCY - 2), 1)
    # Gold leading-edge chevrons on each wing — bold, value-clear on navy.
    sweep_tip_x = root_x - 2 - 0.25 * 22
    for sgn in (-1, 1):
        pygame.draw.line(surf, _V4_GOLD, (root_x + 1, BCY + sgn * 3),
                         (sweep_tip_x, BCY + sgn * (22 - 0.25 * 5)), 2)
    # Gold cap on the single tall tail.
    pygame.draw.polygon(surf, _V4_GOLD, [
        (tail_x + 1, BCY - 9), (tail_x - 6, BCY - 15),
        (tail_x - 9, BCY - 14), (tail_x - 2, BCY - 8)])
    _tandem_canopy(surf, nose_base_x - 6, _V4_CANOPY, _V4_CANOPY_H)
    _nozzles(surf, tail_x, ys)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v5 · SWING-WING STRIKE — wings HARD-BACK (max interceptor dash), TWIN tail,
#   LONG radar nose, gunship-grey with ONE bold high-vis stripe + the hottest
#   burner. The "fast" extreme of the sweep variable; aggressive arrowhead.
# ═════════════════════════════════════════════════════════════════════════════
_V5_BODY   = (96, 104, 116)           # gunship gray
_V5_BODY_D = (58, 64, 76)
_V5_BODY_H = (148, 156, 168)
_V5_EDGE   = (34, 38, 48)
_V5_WING   = (88, 96, 108)
_V5_WING_D = (52, 58, 70)
_V5_WING_H = (140, 148, 160)
_V5_HIVIZ  = (255, 176, 40)           # one bold high-vis stripe
_V5_CANOPY = (64, 140, 190)
_V5_CANOPY_H = (180, 224, 248)


def build_naval_v5(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    # Hottest burner of the set: wider nozzle gap + bigger plume read.
    ys = _twin_burner(surf, 14 - pit, p, 8, core=_F_CORE, mid=_F_MID,
                      outer=_F_OUTER, halo=_F_HALO)
    tail_x, nose_tip_x, nose_base_x, root_x = _naval_airframe(
        surf, p, pit, sweep=1.0, nose=12, twin_tail=True,
        body=_V5_BODY, body_d=_V5_BODY_D, body_h=_V5_BODY_H, edge=_V5_EDGE,
        wing=_V5_WING, wing_d=_V5_WING_D, wing_h=_V5_WING_H,
        canopy=_V5_CANOPY, canopy_h=_V5_CANOPY_H)
    # ONE bold high-vis stripe slashing diagonally down the rear fuselage —
    # the single deliberate signature (value+hue) that rescues the night read.
    pygame.draw.polygon(surf, _V5_HIVIZ, [
        (root_x + 2, BCY - 5), (root_x - 4, BCY - 4),
        (tail_x + 6, BCY + 5), (tail_x + 12, BCY + 4)])
    pygame.draw.line(surf, _V5_BODY_H, (root_x + 2, BCY - 5),
                     (tail_x + 12, BCY + 4), 1)
    # High-vis chevron on each swept wingtip.
    sweep_tip_x = root_x - 2 - 1.0 * 22
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _V5_HIVIZ,
                           (int(sweep_tip_x + 3), BCY + sgn * 17), 1)
    _tandem_canopy(surf, nose_base_x - 6, _V5_CANOPY, _V5_CANOPY_H)
    _nozzles(surf, tail_x, ys)
    return surf


# ─────────────────────────────────────────────────────────────────────────────
# Candidate registry. label → getter for the review sheet. `skin_naval` keys
# the lead build so it matches the production registry shape; the four other
# takes are exposed under explicit vN labels for the round sheet.
# ─────────────────────────────────────────────────────────────────────────────
get_naval_v1 = _make_prebuilt_skin(build_naval_v1)
get_naval_v2 = _make_prebuilt_skin(build_naval_v2)
get_naval_v3 = _make_prebuilt_skin(build_naval_v3)
get_naval_v4 = _make_prebuilt_skin(build_naval_v4)
get_naval_v5 = _make_prebuilt_skin(build_naval_v5)

VARIANTS = {
    "naval_v1": ("LOW-VIS PROWLER", "wings-fwd · twin tail · long nose · TPS grey",
                 get_naval_v1),
    "naval_v2": ("FLEET DEFENDER", "swept · twin tail · gull-gray/red stripe + modex",
                 get_naval_v2),
    "naval_v3": ("JOLLY ROGERS", "mid-sweep · twin tail · sea-black + skull/gold caps",
                 get_naval_v3),
    "naval_v4": ("GOLD ACE", "fwd-mid · SINGLE tail · navy-blue + gold chevrons",
                 get_naval_v4),
    "naval_v5": ("SWING-WING STRIKE", "hard-back · twin tail · gunship + hi-vis stripe",
                 get_naval_v5),
}

# Production-shaped registry: the lead candidate keys `skin_naval`.
BUILDERS = {"skin_naval": get_naval_v1}
