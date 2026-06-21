"""Production JET FIGHTER redesign — FLYING-WING STEALTH, converged build.

Winner of the round-1 explore: v2 · YF-23 DIAMOND (Black Widow II). A TAILLESS
flying wing replacing the production STEEL RAPTOR's pointy dart — an angular
four-corner diamond kite (sharp nose, wide mid-chord shoulders, pointed tail
apex), gunmetal low-observable finish, BURIED engine (no plume).

The identity is the WIDE TAILLESS DIAMOND — it must read as clearly NOT a dart
even at 40px. A wide-but-thin shape flattens into a blob at gameplay size, so
the read is carried by a hard chordwise TOP-FACET-vs-SHADOW value split down
the diamond's central crease, plus a TWO-ACCENT hierarchy that sells "most
expensive secret skin":

  * the WARM focal point — a single thin AMBER cockpit slit on the spine (the
    one warm accent, and the brightest pixel in the whole sprite); and
  * the COOL edge — a 1px blue TRACE on the leading edges (a darker, cooler
    "charged panel-line" tell that lifts gunmetal off any sky).

Round-2 convergence (art-director, ship v2):

  * Burner BURIED, not bolted on. The central exhaust is an embedded SLOT sunk
    into the trailing facet shadow — ~30% smaller, with only a faint 1-2px
    ember — so the diamond silhouette edge stays unbroken at 40px. No marble.
  * ONE warm accent total. The amber cockpit slit is the sole warm focal
    point; there is no bright burner competing with it.
  * Chordwise value gap widened ~15% (top facet up, shadow facet down) so the
    central crease stays a HARD line through the downscale on a night sky.
  * Day-sky floor cooled: the gunmetal is nudged a hair cooler/darker so it
    doesn't brown out against warm day stone, while the top-facet-vs-shadow
    split still reads on the orange sky.
  * Leading-edge blue thinned to a 1px whisper TRACE — present enough to be
    the day-sky lifeline, quiet enough to read as an edge, not an outline.
  * Accessibility: warm slit + cool edge separate by VALUE and POSITION (slit
    is the brightest pixel on the centre spine; blue is a darker leading edge)
    so the two accents still read in greyscale / for colourblind players.

Contract (mirrors game/animal_jet_fighter.py so this lifts straight in):

  * `build_flyingwing(wing_angle_deg) -> pygame.Surface`: ONE flat frame on a
    64×84 SRCALPHA canvas, mass centred at (32,44). Drawn NOSE-RIGHT, UPRIGHT,
    LEVEL (clean top-down planform). Rotation/flip is NOT baked — the game
    applies the inverted nose-up attitude later.
  * 4 poses = a subtle BURIED-EMBER PULSE + ±1px pitch, baked per frame (no
    live particles); the buried slot keeps the ember subtle/embedded.
  * `get_flyingwing` via `_make_prebuilt_skin`; a label→getter `BUILDERS`.

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
    """±1px nose pitch so the wing visibly 'breathes' with the buried ember."""
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
# YF-23 DIAMOND — production palette.
#
# Day-floor cooled vs the round-1 explore: the gunmetal mid/shadow are pushed a
# hair cooler + darker (more blue in the channel, lower value) so the finish
# never browns out against warm sandstone. The TOP facet is lifted and the
# SHADOW facet dropped so the chordwise gap is ~15% wider — the central crease
# stays a hard line at 40px on night. Two accents only: AMBER slit (warm, the
# brightest pixel) + a thin BLUE edge trace (cool, a darker leading edge).
# ═════════════════════════════════════════════════════════════════════════════
_D_TOP   = (112, 124, 144)       # lit top facet — lifted for a wider value gap
_D_BODY  = (54, 62, 78)          # cooler/darker gunmetal mid (day-floor fix)
_D_SHAD  = (26, 31, 44)          # aft shadow facet — dropped for the gap
_D_EDGE  = (16, 20, 30)          # darker-than-body rim
_D_GLOW  = (74, 138, 196)        # cool-blue edge TRACE — a DARKER cool edge
_D_KEEL  = (96, 106, 126)        # centre-keel highlight (below the amber slit)
_D_AMBER   = (255, 182, 64)      # the one warm accent — amber cockpit slit
_D_AMBER_H = (255, 232, 158)     # slit hot core — the single brightest pixel
_D_EMBER   = (196, 92, 52)       # buried-slot ember (deep, never a focal point)


def build_flyingwing(wing_angle_deg):
    surf = _new()
    p = _pulse(wing_angle_deg)
    pit = _pitch(wing_angle_deg)
    nx = 7 + pit
    tail = nx + 50
    span = 24
    midx = nx + 30                # widest point (diamond shoulders)

    # Diamond kite outline: nose → shoulder → tail apex (mirror for bottom).
    top = [(nx, BCY), (midx, BCY - span), (tail, BCY)]
    outline = top + _mirror_pts(top, BCY)
    pygame.draw.polygon(surf, _D_BODY, outline)

    # Hard chordwise facet split: bright forward triangle, dark aft triangle.
    # The wide value gap (top lifted, shadow dropped) is what keeps the central
    # crease a hard line when the diamond shrinks to a 40px blob candidate.
    for sgn in (-1, 1):
        pygame.draw.polygon(surf, _D_TOP,
                            [(nx, BCY), (midx, BCY - sgn * span),
                             (midx - 4, BCY - sgn * 6)])
        pygame.draw.polygon(surf, _D_SHAD,
                            [(midx, BCY - sgn * span), (tail, BCY),
                             (midx - 4, BCY - sgn * 6)])

    # BURIED ENGINE SLOT: a dark embedded trough sunk into the aft shadow facet,
    # well inboard of the tail apex so the silhouette EDGE stays unbroken. The
    # slot is drawn in shadow-value, then a faint ember halo + a 1px core — the
    # exhaust reads as recessed, never as a sphere bolted onto the back.
    slot_cx = tail - 12
    pygame.draw.polygon(surf, _D_EDGE,
                        [(slot_cx - 4, BCY - 2), (slot_cx + 5, BCY - 1),
                         (slot_cx + 5, BCY + 1), (slot_cx - 4, BCY + 2)])
    ember = _embedded_glow(int(3 + p * 2), _D_EMBER, int(70 + p * 70))
    _blit_c(surf, ember, (slot_cx + 1, BCY))
    pygame.draw.circle(surf, _D_EMBER, (slot_cx + 1, BCY),
                       1 if p < 0.6 else 2)

    # Outline last so the slot/ember never breaks the diamond's edge.
    pygame.draw.polygon(surf, _D_EDGE, outline, 1)

    # Centre keel highlight running nose→tail (reads the spine through facets),
    # kept BELOW the amber slit in value so the slit stays the brightest pixel.
    pygame.draw.polygon(surf, _D_KEEL,
                        [(nx + 3, BCY - 2), (midx, BCY - 2),
                         (tail - 6, BCY), (midx, BCY + 2), (nx + 3, BCY + 2)])

    # COOL EDGE: a 1px blue TRACE on the leading edges — a whisper, not an
    # outline. It is the day-sky lifeline (lifts gunmetal off orange stone by
    # colour) but stays a DARKER cool edge so the warm slit owns the highlight.
    for sgn in (-1, 1):
        pygame.draw.line(surf, _D_GLOW, (nx + 1, BCY),
                         (midx, BCY - sgn * span), 1)

    # WARM ACCENT: the single thin AMBER cockpit slit on the centre spine — the
    # premium signature and the brightest pixel in the sprite. Warm focal point
    # + cool edge = the two-accent hierarchy that sells the most-expensive skin;
    # they separate by VALUE + POSITION so they survive greyscale.
    pygame.draw.polygon(surf, _D_AMBER,
                        [(nx + 8, BCY - 1), (nx + 18, BCY - 1),
                         (nx + 16, BCY + 1), (nx + 8, BCY + 1)])
    pygame.draw.circle(surf, _D_AMBER_H, (nx + 9, BCY), 1)
    return surf


# ── getter + label registry (mirrors animal_jet_fighter BUILDERS) ────────────
get_flyingwing = _make_prebuilt_skin(build_flyingwing)

BUILDERS = {"skin_flyingwing": get_flyingwing}
