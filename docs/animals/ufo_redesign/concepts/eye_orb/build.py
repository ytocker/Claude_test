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
# core warm-white -> iris #48D1FF -> rim #1B4E8C, with a baked additive bloom.
CORE      = (235, 250, 255)       # warmed pupil so it reads as living plasma
IRIS_HI   = (150, 230, 255)       # brightened iris so the body survives downscale
IRIS      = (72, 209, 255)        # #48D1FF
IRIS_MID  = (60, 182, 240)        # the new mid-value band that RAMPS into the rim
IRIS_DEEP = (40, 150, 214)        # iris→rim transition so the gradient is smooth
RIM       = (27, 78, 140)         # #1B4E8C
RIM_DARK  = (16, 48, 92)          # the orb's shadowed lower belly (gives volume)
BLOOM     = (96, 198, 255)        # additive halo colour (blooms hard at night)
RIMLIGHT  = (190, 240, 255)       # bright cyan-white sky-side rim-light

# The day edge is held by a FAINT keyline plus a bright additive rim-light, not a
# heavy dark contour. Round 1's thick near-opaque ring downscaled to a "dark
# hardware donut + a dot" — exactly the read this concept must avoid. Now the
# keyline is barely there and the cyan bloom is pushed OUTWARD so its inner edge
# overlaps and softens the keyline: the first read on day is "cyan glow with a
# crisp containing edge", never "dark ring with a light in it".
KEYLINE   = (16, 46, 80)          # slightly lifted off near-black

# Orb radius. The bright OPAQUE body must be the dominant mass at 40px (a small
# body lost inside a wide faint bloom reads as a dark vignette + a dot), so the
# hard orb runs as large as the 14px collision read allows; the bloom is a tight
# but BRIGHT corona just past the rim that bridges the body into its outer wash.
ORB_R = 15


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 frame index. _WING_ANGLES runs 50→-40, so the
    blink advances one step per pose and loops as a slow breathing pulse."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Breathing-blink keyframes, indexed by phase 0..3. The eye opens wide, narrows,
# pinches to a pinpoint, then re-opens — an inhale/exhale, not a hard on/off.
# Amplitude is cranked ~40% over round 1 so the per-frame delta reads in motion
# even after the smoothscale to 40px (target ≥2-3px of pupil travel per frame),
# and frames 1 and 3 are differentiated so the loop has FOUR distinct beats.
#   core_r : white pupil radius (the contracting bright mass — the loud tell)
#   ring_t : inner cyan ring radius as a fraction of (ORB_R) — EXPANDS as the
#            core shrinks, so a bright boundary visibly travels outward.
#   bloom  : outer halo intensity multiplier (the orb "breathes" brightness too)
_PULSE = (
    # phase 0 — wide open: FAT bright pupil, ring tucked right in, calm bloom
    {"core_r": 5.5, "ring_t": 0.40, "bloom": 0.86},
    # phase 1 — narrowing fast: pupil mid, ring already stepping out, rising bloom
    {"core_r": 3.4, "ring_t": 0.62, "bloom": 0.98},
    # phase 2 — pinpoint blink: pupil a hot spark, ring at the rim, bloom FLARES
    {"core_r": 0.8, "ring_t": 0.92, "bloom": 1.40},
    # phase 3 — re-opening: pupil swelling but distinct from phase 1, ring relaxing
    {"core_r": 2.2, "ring_t": 0.74, "bloom": 1.06},
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


def _radial_orb(surf, cx, cy, r, inner, mid, outer):
    """The orb body as a smooth inner->mid->outer radial gradient. The body is
    mostly BRIGHT iris cyan; it steps through a MID cyan band and only the
    outermost ~2px deepens toward the rim colour, so the value RAMPS down
    gradient-style into the bloom instead of hitting a dark contour wall. The
    bright mass has to WIN against the gradient or the orb looks like a dark disc.
    """
    from game.draw import lerp_color
    # The body's OUTER edge lands on the MID cyan, never the dark navy: the value
    # must ramp DOWN gradient-style into the bloom, and the dark-edge work is left
    # entirely to the faint keyline + bright rim-light. A dark body rim here is
    # what summed with the keyline into a "hardware donut" in round 1. `outer` is
    # accepted for palette continuity but only tints the last 1px a hair.
    mid_band = 5.0                                  # bright iris ramps to mid here
    for i in range(r, 0, -1):
        d = r - i                                   # 0 at rim, grows inward
        if d < 1:
            col = lerp_color(mid, outer, 0.35)      # barely deepen the outermost px
        else:
            t = max(0.0, 1.0 - (d - 1) / mid_band)
            col = lerp_color(mid, inner, t)
        pygame.draw.circle(surf, col, (cx, cy), i)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    k = _PULSE[ph]
    cx, cy = BCX, BCY

    # 1) OUTER BLOOM — a soft corona of light AROUND the orb. Drawn first and
    # additive so at night it blooms past the rim into the dark sky; the opaque
    # body then covers its centre, so the bloom only shows as a halo OUTSIDE the
    # circle (and never bleaches the body to white). Breathes with the blink, and
    # FLARES wide at the pinpoint frame so the orb visibly pulses brighter the
    # instant the pupil vanishes — that flare is the premium tell.
    _glow_dot(surf, (cx, cy), ORB_R, BLOOM,
              halo=1.6 + 0.45 * k["bloom"], intensity=1.7 * k["bloom"])

    # 2) ORB BODY — a luminous cyan sphere, drawn OPAQUE so it carries its own
    # gradient instead of summing with the bloom. A BRIGHT iris field steps
    # through a MID cyan band to a razor rim (never to the dark navy that would
    # muddy the whole disc to a vignette at 40px). No dome, no hardware: the whole
    # mass is light, and the bright cyan must stay the dominant colour.
    _radial_orb(surf, cx, cy, ORB_R, IRIS_HI, IRIS_MID, IRIS_DEEP)
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

    # 4) CORE PUPIL — the contracting bright mass (the loudest tell). A solid warm
    # plasma pupil with a thin cyan-white halo ring (NOT a big additive bloom,
    # which would bleach the orb). Kept small so the cyan iris field stays the
    # dominant colour; at the pinpoint frame the pupil is a tiny intense spark and
    # the corona flare (step 6) carries the brightness instead.
    core_r = max(1, int(round(k["core_r"])))
    pygame.draw.circle(surf, (180, 238, 255), (cx, cy), core_r + 2)   # cyan halo
    pygame.draw.circle(surf, CORE, (cx, cy), core_r)                  # warm pupil

    # 5) DAY KEYLINE — a FAINT thin dark ring at the very edge, drawn BELOW the rim
    # glow. Round 1's thick, near-opaque keyline downscaled to "a dark hardware
    # donut + a dot" — the precise failure this concept exists to avoid. So it is
    # now ~1px effective with low alpha: just enough to bite against the brightest
    # day sky, while the additive rim-light + bloom (step 6) lift cyan back OVER
    # its inner edge so the first read is glow with a crisp edge, not a dark band.
    key = pygame.Surface((ORB_R * 2 + 2, ORB_R * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(key, (*KEYLINE, 92), (ORB_R + 1, ORB_R + 1), ORB_R, 1)
    surf.blit(key, (cx - ORB_R - 1, cy - ORB_R - 1))

    # 6) RIM GLOW — a bright additive cyan corona pushed OUTWARD from the body rim.
    # Drawn LAST so it lifts cyan up over the keyline's inner edge and bridges the
    # opaque body straight into its outer bloom: this is what guarantees the day
    # read is "cyan glow + crisp edge" and not "dark vignette + dot". A hot
    # cyan-WHITE rim-light sits on the sky side just inside the keyline (a bright
    # containing edge beats a dark one), then the bloom feathers outward. The
    # whole corona FLARES at the pinpoint frame, hotter and wider, so the orb
    # visibly pulses the instant the pupil pinches shut.
    pad = 16
    rim = pygame.Surface((ORB_R * 2 + pad * 2, ORB_R * 2 + pad * 2), pygame.SRCALPHA)
    rc = ORB_R + pad
    # bright cyan-white rim-light hugging the body edge (the containing edge). It
    # runs hot and 3px wide so on day the FIRST read is a luminous crisp edge that
    # OVERLAPS and washes out the faint keyline, never a dark band.
    for d in range(0, 4):
        a = int((175 - 38 * d) * min(1.3, 0.9 + 0.3 * k["bloom"]))
        pygame.draw.circle(rim, (*RIMLIGHT, a), (rc, rc), ORB_R - 1 + d, 1)
    # cyan bloom feathering outward, flaring wider/hotter at the pinpoint
    reach = int(round(7 + 4 * (k["bloom"] - 0.86)))
    for d in range(reach, -2, -1):
        a = int(155 * (1.0 - (d + 2) / (reach + 2)) * k["bloom"])
        pygame.draw.circle(rim, (*BLOOM, a), (rc, rc), ORB_R + d, 1)
    surf.blit(rim, (cx - rc, cy - rc), special_flags=pygame.BLEND_RGBA_ADD)

    return surf


# Expose the pose set so render harnesses can introspect the 4 frames.
WING_ANGLES = _WING_ANGLES
