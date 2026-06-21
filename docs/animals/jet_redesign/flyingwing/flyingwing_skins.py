"""Candidate JET FIGHTER redesign — concept FLYING-WING STEALTH (round 1).

A radically different silhouette from the production STEEL RAPTOR (gunmetal
top-down dart + delta + twin canted tails + twin afterburner). This concept
is a TAILLESS flying wing: a wide chevron/boomerang span with sawtooth
trailing edges, faceted low-observable surfaces, a dark charcoal low-vis
finish, and BURIED engines (subtle embedded exhaust glow, never a plume).

The identity is the WIDE TAILLESS WING — it must read as clearly NOT a
pointy dart even at 40px. Because a wide-but-thin shape can vanish into a
blob at gameplay size, every sub-take leans on a hard TOP-FACET vs SHADOW
value split down the chord so the dark wing keeps internal structure, plus
a faint edge tell (rim, blue edge-glow, or amber cockpit slit) so it holds
on day AND night.

Five genuinely different sub-takes on THIS one concept:

  v1 B-2 CRESCENT   smooth swept crescent, B-2 "double-W" sawtooth trailing
                    edge, matte charcoal, centre-spine canopy bulge.
  v2 YF-23 DIAMOND  angular diamond planform (Black Widow II), hard chordwise
                    facet split, gunmetal with a faint COOL-BLUE edge-glow.
  v3 ARROWHEAD WING narrow sharp arrowhead span, two-tone panel facets, a
                    single thin AMBER cockpit slit as the premium tell.
  v4 SWEPT MANTA    very wide swept boomerang/manta span, deep sawtooth,
                    gunmetal + blue edge-glow, twin embedded burner cores.
  v5 OBSIDIAN SPLIT matte-black low-vis pushed to the limit: the read is the
                    pure TOP-FACET-vs-SHADOW split + one amber slit; minimal
                    sawtooth — the value-structure stress test.

Contract (mirrors game/animal_jet_fighter.py so the winner lifts straight in):

  * `build_flyingwing_vN(wing_angle_deg) -> pygame.Surface`: ONE flat frame
    on a 64×84 SRCALPHA canvas, mass centred at (32,44). Drawn NOSE-RIGHT,
    UPRIGHT, LEVEL (clean top-down planform). Rotation/flip is NOT baked —
    the game applies the inverted nose-up attitude later.
  * 4 poses = a subtle ENGINE-GLOW PULSE + ±1px pitch, baked per frame (no
    live particles); a buried-engine wing keeps the glow subtle/embedded.
  * `get_flyingwing_vN` via `_make_prebuilt_skin`; a label→getter `BUILDERS`.

Why the body mass stays at (32,44): collision is a fixed 14px circle at the
body centre, so the centre-of-mass stays anchored for fairness; the wing may
span wider than the body, but the centre never drifts.
"""
import math
import pygame

from game.parrot import SPRITE_W, _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + mass anchor (mirror animal_jet_fighter layout) ──────────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12
BCX, BCY = 32, 32 + DY          # mass centre → (32, 44)


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter: lazy 4-frame build +
    per-(frame, 3°) rotation cache, each frame run through the house outline."""
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


# ── shared pulse / pitch (mirror the production afterburner heartbeat) ────────
def _pulse(angle_deg):
    """0..1 'throttle' from the wing angle (50→-40): brightest on the middle
    two frames, dim at the ends — a heartbeat the eye reads as buried thrust."""
    t = (50 - angle_deg) / 90.0
    return 1.0 - abs(t * 2.0 - 1.0)


def _pitch(angle_deg):
    """±1px nose pitch so the wing visibly 'breathes' with the burner."""
    return int(round((_pulse(angle_deg) - 0.5) * 2.4))


def _embedded_glow(radius, color, alpha):
    """Soft radial halo for a BURIED exhaust: a flying wing has no plume, so
    the glow is small and sits low in the trailing-edge value, supporting the
    dark wing rather than blooming off it."""
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    steps = 7
    for i in range(steps, 0, -1):
        a = int(alpha * (i / steps) ** 2)
        r = max(1, int(radius * i / steps))
        pygame.draw.circle(s, (*color, a), (radius, radius), r)
    return s


def _blit_c(surf, src, center):
    surf.blit(src, src.get_rect(center=center).topleft)


def _mirror_pts(pts, axis_y):
    """Mirror a list of (x,y) about a horizontal axis (top half → bottom),
    returned in reverse so the two halves chain into one closed polygon."""
    return [(x, 2 * axis_y - y) for (x, y) in reversed(pts)]


# ═════════════════════════════════════════════════════════════════════════════
# v1 · B-2 CRESCENT — smooth swept crescent, B-2 "double-W" sawtooth trailing
#   edge, matte charcoal. The read: a broad symmetric flying wing with a
#   serrated back edge and a faint warm spine; no fuselage, no tail.
# ═════════════════════════════════════════════════════════════════════════════
_C_TOP   = (96, 102, 116)        # lit top facet
_C_BODY  = (62, 67, 80)          # mid charcoal
_C_SHAD  = (38, 42, 53)          # shadowed aft facet
_C_EDGE  = (24, 26, 34)          # darker-than-body rim (value tell)
_C_RIM   = (150, 158, 176)       # cool top rim-light
_C_GLASS = (70, 150, 196)        # cockpit blister
_C_BURN  = (255, 150, 70)        # buried burner warmth


def build_flyingwing_v1(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nx = 8 + pit                 # nose apex (right)
    span = 28                    # half-span (wide tailless wing)

    # ── buried twin burner glow at the trailing-edge notches (subtle) ────────
    burn_r = int(5 + p * 3)
    glow = _embedded_glow(burn_r, _C_BURN, int(40 + p * 50))
    for sgn in (-1, 1):
        _blit_c(surf, glow, (54, BCY + sgn * 9))

    # ── crescent planform: nose apex → swept wingtips → double-W back edge ───
    # Top half outline (apex, leading edge to tip, sawtooth trailing edge in
    # to the centre notch). The double-W is the B-2 tell.
    top = [
        (nx, BCY),                       # nose apex
        (nx + 18, BCY - 14),             # leading edge sweeping out
        (nx + 40, BCY - span),           # wingtip (far back + wide)
        (nx + 44, BCY - span + 3),       # tip trailing corner
        (nx + 34, BCY - 18),             # sawtooth peak
        (nx + 40, BCY - 13),             # sawtooth notch out
        (nx + 30, BCY - 7),              # sawtooth peak
        (nx + 36, BCY - 2),              # inner notch → centre
    ]
    outline = top + _mirror_pts(top, BCY)
    pygame.draw.polygon(surf, _C_BODY, outline)
    pygame.draw.polygon(surf, _C_EDGE, outline, 1)

    # Hard TOP-FACET vs SHADOW split down the chord so the wing never flattens:
    # a lit forward facet (toward the nose) over a darker aft facet.
    for sgn in (-1, 1):
        lit = [(nx, BCY), (nx + 18, BCY - sgn * 14),
               (nx + 40, BCY - sgn * span), (nx + 30, BCY - sgn * 12),
               (nx + 14, BCY - sgn * 5)]
        pygame.draw.polygon(surf, _C_TOP, lit)
        shad = [(nx + 14, BCY - sgn * 5), (nx + 30, BCY - sgn * 12),
                (nx + 40, BCY - sgn * span), (nx + 44, BCY - sgn * (span - 3)),
                (nx + 30, BCY - sgn * 7), (nx + 36, BCY - sgn * 2)]
        pygame.draw.polygon(surf, _C_SHAD, shad)

    # Centre spine ridge (catches light) + faint cool rim on the leading edges.
    pygame.draw.polygon(surf, _C_TOP,
                        [(nx + 2, BCY - 2), (nx + 20, BCY - 2),
                         (nx + 20, BCY + 2), (nx + 2, BCY + 2)])
    for sgn in (-1, 1):
        pygame.draw.line(surf, _C_RIM, (nx + 2, BCY - sgn * 1),
                         (nx + 40, BCY - sgn * span), 1)

    # Cockpit blister low in the spine (cool anchor, never washes out).
    _aaellipse(surf, _C_GLASS, (nx + 10, BCY), 4, 2)
    pygame.draw.circle(surf, (200, 230, 248), (nx + 9, BCY - 1), 1)
    # Buried nozzle mouths in the centre notch.
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _C_BURN, (52, BCY + sgn * 9), 2)
        pygame.draw.circle(surf, (255, 240, 210), (51, BCY + sgn * 9), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v2 · YF-23 DIAMOND — angular diamond planform (Black Widow II): a hard
#   four-corner kite with a sharp nose, wide mid-chord shoulders, and a
#   pointed tail apex. Gunmetal with a faint COOL-BLUE edge-glow tell.
# ═════════════════════════════════════════════════════════════════════════════
_D_TOP   = (104, 116, 134)
_D_BODY  = (60, 68, 84)
_D_SHAD  = (34, 39, 52)
_D_EDGE  = (20, 24, 34)
_D_GLOW  = (90, 168, 230)        # cool-blue low-observable edge-glow
_D_GLOW2 = (170, 214, 248)
_D_GLASS = (52, 132, 184)
_D_BURN  = (255, 138, 70)


def build_flyingwing_v2(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nx = 7 + pit
    tail = nx + 50
    span = 24
    midx = nx + 30                # widest point (diamond shoulders)

    # Buried single central burner glow (engines deep in the diamond).
    glow = _embedded_glow(int(6 + p * 3), _D_BURN, int(36 + p * 48))
    _blit_c(surf, glow, (tail - 6, BCY))

    # Diamond kite outline: nose → shoulder → tail apex (mirror for bottom).
    top = [(nx, BCY), (midx, BCY - span), (tail, BCY)]
    outline = top + _mirror_pts(top, BCY)
    pygame.draw.polygon(surf, _D_BODY, outline)

    # Hard chordwise facet split: bright forward triangle, dark aft triangle.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _D_TOP,
                            [(nx, BCY), (midx, BCY - sgn * span),
                             (midx - 4, BCY - sgn * 6)])
        pygame.draw.polygon(surf, _D_SHAD,
                            [(midx, BCY - sgn * span), (tail, BCY),
                             (midx - 4, BCY - sgn * 6)])
    pygame.draw.polygon(surf, _D_EDGE, outline, 1)

    # Centre keel highlight running nose→tail (reads the spine through facets).
    pygame.draw.polygon(surf, _D_TOP,
                        [(nx + 3, BCY - 2), (midx, BCY - 2),
                         (tail - 4, BCY), (midx, BCY + 2), (nx + 3, BCY + 2)])

    # Premium signature: a faint COOL-BLUE edge-glow tracing the leading edges
    # — a low-observable "charged panel-line" tell that lifts gunmetal off any
    # sky by colour, not just luminance.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _D_GLOW, (nx + 1, BCY),
                         (midx, BCY - sgn * span), 2)
        pygame.draw.line(surf, _D_GLOW2, (nx + 1, BCY),
                         (midx - 6, BCY - sgn * (span - 5)), 1)
    pygame.draw.circle(surf, _D_GLOW2, (nx + 1, BCY), 1)

    # Cockpit blister + buried central nozzle.
    _aaellipse(surf, _D_GLASS, (nx + 10, BCY), 4, 2)
    pygame.draw.circle(surf, (190, 224, 246), (nx + 9, BCY - 1), 1)
    pygame.draw.circle(surf, _D_BURN, (tail - 4, BCY), 2)
    pygame.draw.circle(surf, (255, 238, 206), (tail - 5, BCY), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v3 · ARROWHEAD WING — a narrow, sharply swept arrowhead span (tighter than
#   the crescent, more aggressive than the diamond). Two-tone PANEL facets
#   tile the surface; the premium tell is a single thin AMBER cockpit slit.
# ═════════════════════════════════════════════════════════════════════════════
_A_TOP   = (108, 110, 118)
_A_BODY  = (66, 68, 78)
_A_PANEL = (50, 52, 62)          # alternating darker panel facet
_A_SHAD  = (32, 34, 44)
_A_EDGE  = (18, 19, 27)
_A_RIM   = (158, 160, 170)
_A_AMBER = (255, 178, 60)        # thin amber cockpit slit — the premium tell
_A_AMBER_H = (255, 224, 150)
_A_BURN  = (255, 146, 74)


def build_flyingwing_v3(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nx = 6 + pit
    span = 22
    tipx = nx + 46
    backx = nx + 40              # trailing-edge root

    # Buried twin burner glow tucked at the wing root notches.
    glow = _embedded_glow(int(4 + p * 3), _A_BURN, int(34 + p * 46))
    for sgn in (-1, 1):
        _blit_c(surf, glow, (backx - 2, BCY + sgn * 6))

    # Sharp arrowhead outline: long nose, swept-back narrow tips, single
    # shallow trailing-edge sawtooth into the centre.
    top = [(nx, BCY), (tipx, BCY - span), (tipx + 3, BCY - span + 4),
           (nx + 32, BCY - 9), (backx, BCY - 4), (nx + 30, BCY - 1)]
    outline = top + _mirror_pts(top, BCY)
    pygame.draw.polygon(surf, _A_BODY, outline)

    # Two-tone PANEL facets: alternating spanwise wedges so the dark surface
    # reads as tiled low-observable panels, not a flat blob.
    for sgn in (-1, 1):
        # Forward lit panel.
        pygame.draw.polygon(surf, _A_TOP,
                            [(nx, BCY), (nx + 24, BCY - sgn * 11),
                             (nx + 14, BCY - sgn * 4)])
        # Mid darker panel.
        pygame.draw.polygon(surf, _A_PANEL,
                            [(nx + 24, BCY - sgn * 11), (tipx, BCY - sgn * span),
                             (nx + 32, BCY - sgn * 9), (nx + 14, BCY - sgn * 4)])
        # Aft shadow panel.
        pygame.draw.polygon(surf, _A_SHAD,
                            [(nx + 14, BCY - sgn * 4), (nx + 32, BCY - sgn * 9),
                             (backx, BCY - sgn * 4), (nx + 30, BCY - sgn * 1)])
    pygame.draw.polygon(surf, _A_EDGE, outline, 1)

    # Cool rim catches the swept leading edge (luminance tell on day + night).
    for sgn in (-1, 1):
        pygame.draw.line(surf, _A_RIM, (nx + 1, BCY),
                         (tipx, BCY - sgn * span), 1)

    # Premium signature: a single thin AMBER cockpit slit on the spine —
    # narrow, hot, unmistakable; the "most expensive" tell at 40px.
    pygame.draw.polygon(surf, _A_AMBER,
                        [(nx + 7, BCY - 1), (nx + 17, BCY - 1),
                         (nx + 15, BCY + 1), (nx + 7, BCY + 1)])
    pygame.draw.circle(surf, _A_AMBER_H, (nx + 8, BCY), 1)
    # Buried nozzles.
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _A_BURN, (backx - 2, BCY + sgn * 6), 2)
        pygame.draw.circle(surf, (255, 236, 200), (backx - 3, BCY + sgn * 6), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v4 · SWEPT MANTA — the WIDEST take: a manta-ray boomerang span swept far
#   back, deep aggressive sawtooth trailing edge, gunmetal with a blue
#   edge-glow AND twin embedded burner cores. Maximum tailless-wing identity.
# ═════════════════════════════════════════════════════════════════════════════
_M_TOP   = (98, 108, 128)
_M_BODY  = (56, 63, 78)
_M_SHAD  = (32, 37, 50)
_M_EDGE  = (18, 22, 32)
_M_GLOW  = (96, 176, 232)
_M_GLOW2 = (182, 220, 250)
_M_GLASS = (60, 140, 192)
_M_BURN  = (255, 142, 66)


def build_flyingwing_v4(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nx = 10 + pit
    span = 31                    # widest half-span of the set
    tipx = nx + 36

    # Twin embedded burner cores tucked into the deep sawtooth notches.
    burn_r = int(5 + p * 3)
    glow = _embedded_glow(burn_r, _M_BURN, int(42 + p * 52))
    for sgn in (-1, 1):
        _blit_c(surf, glow, (nx + 34, BCY + sgn * 11))

    # Manta boomerang: a long swept leading edge to wide low tips, then a deep
    # zig-zag trailing edge (two big sawteeth per side) back to a centre notch.
    top = [
        (nx, BCY),                       # nose
        (nx + 16, BCY - 11),
        (tipx, BCY - span),              # wide swept tip
        (tipx + 4, BCY - span + 4),
        (nx + 30, BCY - 20),             # outer sawtooth peak
        (nx + 37, BCY - 14),             # notch
        (nx + 27, BCY - 9),              # inner sawtooth peak
        (nx + 34, BCY - 3),              # → centre notch
    ]
    outline = top + _mirror_pts(top, BCY)
    pygame.draw.polygon(surf, _M_BODY, outline)

    # Hard top-facet vs shadow split: a big lit forward sweep over a dark
    # serrated aft band — the structure that keeps the wide wing from flatten.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _M_TOP,
                            [(nx, BCY), (nx + 16, BCY - sgn * 11),
                             (tipx, BCY - sgn * span), (nx + 26, BCY - sgn * 11),
                             (nx + 12, BCY - sgn * 4)])
        pygame.draw.polygon(surf, _M_SHAD,
                            [(nx + 12, BCY - sgn * 4), (nx + 26, BCY - sgn * 11),
                             (nx + 30, BCY - sgn * 20), (nx + 37, BCY - sgn * 14),
                             (nx + 27, BCY - sgn * 9), (nx + 34, BCY - sgn * 3)])
    pygame.draw.polygon(surf, _M_EDGE, outline, 1)

    # Premium: cool-blue edge-glow on the long leading edges + a centre keel.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _M_GLOW, (nx + 1, BCY),
                         (tipx, BCY - sgn * span), 2)
        pygame.draw.line(surf, _M_GLOW2, (nx + 1, BCY),
                         (nx + 18, BCY - sgn * 12), 1)
    pygame.draw.polygon(surf, _M_TOP,
                        [(nx + 3, BCY - 2), (nx + 22, BCY - 2),
                         (nx + 22, BCY + 2), (nx + 3, BCY + 2)])
    pygame.draw.circle(surf, _M_GLOW2, (nx + 1, BCY), 1)

    # Cockpit blister + twin buried nozzles.
    _aaellipse(surf, _M_GLASS, (nx + 11, BCY), 4, 2)
    pygame.draw.circle(surf, (206, 234, 250), (nx + 10, BCY - 1), 1)
    for sgn in (-1, 1):
        pygame.draw.circle(surf, _M_BURN, (nx + 32, BCY + sgn * 11), 2)
        pygame.draw.circle(surf, (255, 240, 208), (nx + 31, BCY + sgn * 11), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# v5 · OBSIDIAN SPLIT — matte-black low-vis pushed to the limit. No blue
#   glow, minimal sawtooth: the ENTIRE read is the hard TOP-FACET-vs-SHADOW
#   value split across a broad delta wing + one amber slit. The stress test
#   for whether value structure alone holds the wide dark wing at 40px.
# ═════════════════════════════════════════════════════════════════════════════
_O_TOP   = (84, 86, 94)          # the only "light" — a cold graphite facet
_O_BODY  = (46, 48, 56)
_O_SHAD  = (24, 25, 32)          # near-black aft facet
_O_EDGE  = (12, 13, 18)
_O_RIM   = (132, 134, 144)       # crisp cold rim — the night rescue
_O_AMBER = (255, 168, 52)
_O_AMBER_H = (255, 220, 140)
_O_BURN  = (255, 120, 60)


def build_flyingwing_v5(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nx = 7 + pit
    span = 26
    tipx = nx + 42

    # Deeply buried single burner — barely-there ember in the trailing notch.
    glow = _embedded_glow(int(4 + p * 2), _O_BURN, int(30 + p * 40))
    _blit_c(surf, glow, (nx + 38, BCY))

    # Broad clean delta wing with one shallow centre sawtooth notch.
    top = [(nx, BCY), (tipx, BCY - span), (tipx + 3, BCY - span + 4),
           (nx + 34, BCY - 6), (nx + 39, BCY - 2)]
    outline = top + _mirror_pts(top, BCY)
    pygame.draw.polygon(surf, _O_BODY, outline)

    # THE read: a single hard chordwise split. Forward half = cold graphite
    # facet; aft half = near-black shadow. The diagonal seam is sharp so the
    # wing always shows two values, never one blob, at 40px.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _O_TOP,
                            [(nx, BCY), (tipx, BCY - sgn * span),
                             (nx + 20, BCY - sgn * 7), (nx + 10, BCY - sgn * 2)])
        pygame.draw.polygon(surf, _O_SHAD,
                            [(nx + 10, BCY - sgn * 2), (nx + 20, BCY - sgn * 7),
                             (tipx, BCY - sgn * span), (tipx + 3, BCY - sgn * (span - 4)),
                             (nx + 34, BCY - sgn * 6), (nx + 39, BCY - sgn * 2)])
    pygame.draw.polygon(surf, _O_EDGE, outline, 1)

    # Crisp cold rim on the leading edges — the only thing rescuing the
    # near-black silhouette on a night sky (one signature, picked deliberately).
    for sgn in (-1, 1):
        pygame.draw.line(surf, _O_RIM, (nx + 1, BCY),
                         (tipx, BCY - sgn * span), 1)
    pygame.draw.circle(surf, _O_RIM, (nx + 1, BCY), 1)

    # One amber cockpit slit — the sole warm tell against all that black.
    pygame.draw.polygon(surf, _O_AMBER,
                        [(nx + 8, BCY - 1), (nx + 18, BCY - 1),
                         (nx + 16, BCY + 1), (nx + 8, BCY + 1)])
    pygame.draw.circle(surf, _O_AMBER_H, (nx + 9, BCY), 1)
    # Buried nozzle ember.
    pygame.draw.circle(surf, _O_BURN, (nx + 37, BCY), 2)
    pygame.draw.circle(surf, (255, 226, 190), (nx + 36, BCY), 1)
    return surf


# ── getters + label registry (mirrors creature_skins BUILDERS) ───────────────
get_flyingwing_v1 = _make_prebuilt_skin(build_flyingwing_v1)
get_flyingwing_v2 = _make_prebuilt_skin(build_flyingwing_v2)
get_flyingwing_v3 = _make_prebuilt_skin(build_flyingwing_v3)
get_flyingwing_v4 = _make_prebuilt_skin(build_flyingwing_v4)
get_flyingwing_v5 = _make_prebuilt_skin(build_flyingwing_v5)

BUILDERS = {
    "v1 B-2 CRESCENT":   get_flyingwing_v1,
    "v2 YF-23 DIAMOND":  get_flyingwing_v2,
    "v3 ARROWHEAD WING": get_flyingwing_v3,
    "v4 SWEPT MANTA":    get_flyingwing_v4,
    "v5 OBSIDIAN SPLIT": get_flyingwing_v5,
}
