"""Concept EYE-ORB for `skin_ufo` — a glowing sentient plasma sphere.

The redesign's failure mode was domed saucers you couldn't tell apart at 40px.
This concept escapes that by being a different CATEGORY of object: not a metal
craft at all, but a floating LIGHT. A perfect circle whose identity lives in the
GLOW and the concentric eye structure — no dome, no rim, no hardware — so at a
glance it reads "alien energy orb / blinking eye", never "saucer".

The life-tell is a slow breathing blink with no wings and no live particles:
the white core CONTRACTS to a pinpoint and BLOOMS back over the 4 baked frames,
while a faint inner ring EXPANDS as the core shrinks. That moving bright/dark
boundary is the loudest grayscale signal in the set — a colourblind player still
sees a pulse, not a static dot.

Contract mirrors game/animal_ufo.py so a winner lifts straight in:
  * build(wing_angle_deg) -> 64x84 SRCALPHA Surface, orb mass centred at (32,44).
  * 4 iris-pulse frames driven from _WING_ANGLES=(50,20,-10,-40).
  * drawn UPRIGHT (velocity tilt is applied later by the cached getter).
"""
import pygame

from game.parrot import _WING_ANGLES, _aaellipse


# ── canvas + anchors (mirror animal_ufo.py / animal_skins.py) ────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY            # orb centre → (32, 44); 14px collision circle


# ── palette ──────────────────────────────────────────────────────────────────
# core #FFFFFF -> iris #48D1FF -> rim #1B4E8C, with a baked additive bloom.
CORE      = (255, 255, 255)
IRIS_HI   = (150, 230, 255)       # brightened iris so the body survives downscale
IRIS      = (72, 209, 255)        # #48D1FF
IRIS_DEEP = (40, 150, 214)        # iris→rim transition so the gradient is smooth
RIM       = (27, 78, 140)         # #1B4E8C
RIM_DARK  = (16, 48, 92)          # the orb's shadowed lower belly (gives volume)
BLOOM     = (96, 198, 255)        # additive halo colour (blooms hard at night)

# A near-black keyline ring is MANDATORY: a bright cyan orb on the day biome's
# pale-blue top band (sky_bot ≈ (170,220,245)) would otherwise dissolve at the
# edges. This thin dark contour holds the circle against the brightest sky.
KEYLINE   = (14, 42, 74)          # #0E2A4A

# Orb radius. The bright OPAQUE body must be the dominant mass at 40px (a small
# body lost inside a wide faint bloom reads as a dark vignette + a dot), so the
# hard orb runs as large as the 14px collision read allows; the bloom is kept a
# TIGHT corona just past the rim, not a wide wash, for the same reason.
ORB_R = 15


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 frame index. _WING_ANGLES runs 50→-40, so the
    blink advances one step per pose and loops as a slow breathing pulse."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Breathing-blink keyframes, indexed by phase 0..3. The eye opens wide, narrows,
# pinches to a pinpoint, then re-opens — an inhale/exhale, not a hard on/off.
#   core_r : white pupil radius (the contracting bright mass — the loud tell)
#   ring_t : inner cyan ring radius as a fraction of (ORB_R) — EXPANDS as the
#            core shrinks, so a bright boundary visibly travels outward.
#   bloom  : outer halo intensity multiplier (the orb "breathes" brightness too)
_PULSE = (
    # phase 0 — wide open: fat bright pupil, ring tucked in close, soft bloom
    {"core_r": 4.6, "ring_t": 0.46, "bloom": 0.92},
    # phase 1 — narrowing: pupil smaller, ring stepping outward
    {"core_r": 2.8, "ring_t": 0.64, "bloom": 1.00},
    # phase 2 — pinpoint blink: pupil a hot pinpoint, ring at the rim, peak bloom
    {"core_r": 1.2, "ring_t": 0.84, "bloom": 1.14},
    # phase 3 — re-opening: pupil swelling back, ring relaxing inward
    {"core_r": 2.8, "ring_t": 0.64, "bloom": 1.00},
)


def _glow_dot(surf, center, r, color, *, halo=2.4, intensity=1.0):
    """Baked radial bloom, stamped additively to a scratch surface so it blooms
    over night skies without punching holes in the orb. Mirrors animal_ufo's
    _glow_dot helper (the bloom is the orb's whole identity, so it runs big and
    bright — this corona is what sells "glowing light", not "metal craft")."""
    cx, cy = center
    rad = int(r * halo) + 2
    g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    # Many thin shells -> a smooth feathered falloff rather than hard steps.
    shells = 10
    for i in range(shells, 0, -1):
        t = i / shells
        a = int((18 + 54 * (1.0 - t)) * intensity)
        rr = int(rad * t)
        pygame.draw.circle(g, (*color, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)


def _radial_orb(surf, cx, cy, r, inner, outer):
    """The orb body as a smooth inner->outer radial gradient. The body is mostly
    BRIGHT iris cyan; only the outermost ~3px deepens toward the rim colour, so
    the orb reads as a luminous SPHERE, not a dark disc with a dot. The bright
    mass has to WIN against the gradient or it looks like a black hole."""
    from game.draw import lerp_color
    edge = 1.6                                      # razor-thin dark falloff at rim
    for i in range(r, 0, -1):
        d = r - i                                   # 0 at rim, grows inward
        t = max(0.0, 1.0 - d / edge)                # 1 only in the rim band
        col = lerp_color(inner, outer, t)
        pygame.draw.circle(surf, col, (cx, cy), i)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    k = _PULSE[ph]
    cx, cy = BCX, BCY

    # 1) OUTER BLOOM — a soft corona of light AROUND the orb. Drawn first and
    # additive so at night it blooms past the rim into the dark sky; the opaque
    # body then covers its centre, so the bloom only shows as a halo OUTSIDE the
    # circle (and never bleaches the body to white). Breathes with the blink.
    _glow_dot(surf, (cx, cy), ORB_R, BLOOM, halo=1.7, intensity=1.7 * k["bloom"])

    # 2) ORB BODY — a luminous cyan sphere, drawn OPAQUE so it carries its own
    # gradient instead of summing with the bloom. A BRIGHT iris field feathers
    # only to a MID cyan at the rim (never to the dark navy that would muddy the
    # whole disc to a vignette at 40px). No dome, no hardware: the whole mass is
    # light, and the bright cyan must stay the dominant colour.
    _radial_orb(surf, cx, cy, ORB_R, IRIS_HI, IRIS_DEEP)
    # An additive cyan lift across the body so the orb READS AS AN EMITTER (light,
    # not paint) and stays bright cyan after the smoothscale to 40px. A gentle
    # falloff (not a hot centre) keeps the pupil from bleaching the iris field.
    lift = pygame.Surface((ORB_R * 2 + 2, ORB_R * 2 + 2), pygame.SRCALPHA)
    for i in range(ORB_R, 0, -1):
        a = int(20 + 26 * (i / ORB_R))               # brighter toward the rim band
        pygame.draw.circle(lift, (*IRIS, a), (ORB_R + 1, ORB_R + 1), i)
    surf.blit(lift, (cx - ORB_R - 1, cy - ORB_R - 1),
              special_flags=pygame.BLEND_RGBA_ADD)

    # 3) IRIS RING — the expanding boundary. A MID-cyan annulus (deeper than the
    # bright body so it reads as a structural edge, but not the near-black that
    # would mud the orb at small scale) whose radius grows as the core shrinks,
    # so a visible boundary travels OUTWARD across the blink — the loudest
    # grayscale tell of the set.
    ring_r = int(ORB_R * k["ring_t"])
    ring_w = max(2, int(round(3.2 - 1.6 * k["ring_t"])))
    pygame.draw.circle(surf, IRIS_DEEP, (cx, cy), ring_r, ring_w)

    # 4) CORE PUPIL — the contracting bright mass (the loudest tell). A solid hot
    # white pupil with a thin cyan-white halo ring (NOT a big additive bloom,
    # which would bleach the orb). Kept small so the cyan iris field stays the
    # dominant colour; at the pinpoint frame the pupil is a tiny intense spark.
    core_r = max(1, int(round(k["core_r"])))
    pygame.draw.circle(surf, (180, 238, 255), (cx, cy), core_r + 2)   # cyan halo
    pygame.draw.circle(surf, CORE, (cx, cy), core_r)                  # white pupil

    # 5) DAY KEYLINE — mandatory thin dark ring around the orb's outer edge, drawn
    # BELOW the rim glow. Without it the bright cyan orb dissolves into the pale
    # day sky. It is SEMI-transparent (not a hard black ring) so it darkens the
    # edge just enough to bite against a bright sky without reading as a black
    # vignette circle at 40px — a fully opaque keyline is what turns the orb into
    # "a dark ring + a dot" on downscale.
    key = pygame.Surface((ORB_R * 2 + 2, ORB_R * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(key, (*KEYLINE, 165), (ORB_R + 1, ORB_R + 1), ORB_R, 2)
    surf.blit(key, (cx - ORB_R - 1, cy - ORB_R - 1))

    # 6) RIM GLOW — a bright additive cyan corona that starts AT the body rim and
    # fades outward. Drawn LAST so it lifts up over the keyline's inner edge and
    # bridges the opaque body straight into its outer bloom: without it the wide
    # soft bloom leaves a dark gap that downscales to the very "dark vignette +
    # dot" failure this concept must avoid. At night this is the hard glow.
    rim = pygame.Surface((ORB_R * 2 + 16, ORB_R * 2 + 16), pygame.SRCALPHA)
    rc = ORB_R + 8
    for d in range(7, -2, -1):
        a = int(150 * (1.0 - (d + 2) / 9) * k["bloom"])
        pygame.draw.circle(rim, (*BLOOM, a), (rc, rc), ORB_R + d, 1)
    surf.blit(rim, (cx - rc, cy - rc), special_flags=pygame.BLEND_RGBA_ADD)

    return surf


# Expose the pose set so render harnesses can introspect the 4 frames.
WING_ANGLES = _WING_ANGLES
