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

# The day edge is held ENTIRELY by light: a bright light-cyan hairline plus the
# additive rim-light. There is deliberately NO dark contour anywhere on the orb.
# Round 1/2 leaned on a navy keyline that, summed with a body rim that ramped down
# to navy, downscaled to "dark hardware donut + a dot" — the precise read this
# concept exists to avoid. A will-o'-wisp has no containing line; its silhouette
# edge is the BRIGHTEST part. So containment is a faint BRIGHT hairline only.
HAIRLINE  = (170, 235, 255)       # light-cyan containment (bright, never dark)

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
    # Many thin shells -> a smooth feathered falloff rather than hard steps. The
    # falloff is gamma-shaped (t**2.2) so the OUTER shells die to near-zero alpha
    # fast: the house silhouette outline (game/parrot._add_outline) draws a 1px DARK
    # ring around any pixel with alpha > 8, so a long low-alpha additive tail would
    # earn a dark ring out in the faint wash — the day annulus this concept must
    # kill. A steep tail keeps the outline hugging the BRIGHT disc rim (where opaque
    # pixels cover it) while the bloom stays hot near the body, so night still
    # "glows out of black" unchanged but day carries no dark contour in the wash.
    shells = 12
    for i in range(shells, 0, -1):
        t = i / shells                              # 1 at rim region, ->0 outward
        a = int((10 + 88 * (1.0 - t) ** 2.2) * intensity)
        rr = int(rad * t)
        pygame.draw.circle(g, (*color, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)


def _radial_orb(surf, cx, cy, r, inner, mid, outer):
    """The orb body as a smooth inner->mid radial gradient that BOTTOMS OUT on
    luminous mid-cyan at the silhouette edge — never on navy. There is NO dark
    perimeter: the outermost ~3px hold a wide bright mid-cyan band, so the disc
    ramps from a hot core DOWN to a still-LUMINOUS cyan rim and then straight into
    the additive bloom. Measured at the boundary the orb is BRIGHTER and higher
    chroma than the day sky behind it, so the first read is "light", not "dark
    ring + dot". `outer` (the navy rim colour) is intentionally unused here — the
    edge treatment is entirely light, by design.
    """
    from game.draw import lerp_color
    # Widened mid band pushed OUTBOARD: the bright iris core only begins to lift
    # several px in, and the whole outer shell stays on/above mid-cyan. The disc's
    # last pixel IS mid-cyan (no deepening), so nothing on the orb is darker or
    # lower-chroma than the sky.
    mid_band = 7.5                                  # bright iris ramps to mid here
    for i in range(r, 0, -1):
        d = r - i                                   # 0 at rim, grows inward
        # never go below mid-cyan; ramp UP toward the bright core moving inward.
        t = max(0.0, (d - 2.0) / mid_band)          # stay flat on mid for outer ~2px
        col = lerp_color(mid, inner, min(1.0, t))
        pygame.draw.circle(surf, col, (cx, cy), i)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    k = _PULSE[ph]
    cx, cy = BCX, BCY

    # The corona reaches this far; the silhouette is capped here so the house
    # outline (game/parrot._add_outline) lands as ONE thin ring out in the wash.
    term = ORB_R + 9

    # 0) OPAQUE GLOW BASE — a fully-opaque bright-cyan radial filling the whole
    # silhouette out to `term`. The house outline is drawn UNDER the sprite and a
    # semi-transparent additive corona would let that dark ring BLEED THROUGH on a
    # day sky (the grey annulus this concept must kill). By laying an OPAQUE bright
    # base first, every silhouette pixel is alpha 255 and luminous cyan, so the
    # outline can only show as a 1px ring OUTSIDE the disc. The corona's per-frame
    # FLARE is BAKED into this opaque base (its brightness/reach scale with
    # k["bloom"]) rather than relying on a semi-transparent additive layer on top —
    # that keeps the flare tell intact while never letting a dark pixel show
    # through. The colour stays luminous cyan, brightest near the body and fading to
    # a still-above-day-sky cyan at the corona rim (never below the sky's value).
    from game.draw import lerp_color
    flare = k["bloom"]
    # The flare is BAKED as a bright-cyan-white front that swells OUTWARD through the
    # opaque corona as the orb pulses: at the pinpoint frame the bright front pushes
    # far out (the orb visibly flares); on calm frames it tucks back near the body.
    # `hot_to` is the normalised radius the bright front reaches, so a moving bright
    # boundary travels with the blink — a strong, day-safe flare with no dark pixel.
    fnorm = min(1.0, (flare - 0.82) / 0.58)         # 0 calm .. 1 at the pinpoint
    hot_to = 0.12 + 0.74 * fnorm                     # bright front reach (travels out)
    # corona rim colour: DIM (but still above day sky) on calm frames, BRIGHT cyan on
    # the flare so the whole corona visibly swells brighter the instant the pupil
    # pinches — a bigger calm→flare jump makes the pulse read at a glance.
    rim_col = lerp_color((100, 168, 218), (150, 218, 252), fnorm)
    for rr in range(term, ORB_R - 1, -1):
        t = (rr - ORB_R) / float(term - ORB_R)      # 0 at body edge, 1 at corona rim
        if t <= hot_to:
            # the lit flare front: bright cyan-white near the body fading to mid-cyan
            u = t / max(0.001, hot_to)
            col = lerp_color((150, 224, 255), IRIS_MID, u)
        else:
            # beyond the front: cyan fading to the (flare-dependent) corona rim colour
            u = (t - hot_to) / max(0.001, 1.0 - hot_to)
            col = lerp_color(IRIS_MID, rim_col, u)
        pygame.draw.circle(surf, (*col, 255), (cx, cy), rr)

    # 1) OUTER BLOOM — a GENTLE additive lift over the glow base, kept light so it
    # doesn't saturate the corona to flat white (which would swallow the baked flare
    # FRONT in step 0). The loud pulse tell now lives in that opaque travelling
    # front; this layer only adds a soft cyan halo just past the rim. It sits on the
    # opaque base, so on day it tints the base brighter — no dark outline can bleed
    # through — and on night it warms the bloom a touch without flattening the flare.
    _glow_dot(surf, (cx, cy), ORB_R, BLOOM,
              halo=1.5 + 0.35 * k["bloom"], intensity=0.55 * k["bloom"])

    # 2) ORB BODY — a luminous cyan sphere, drawn OPAQUE so it carries its own
    # gradient instead of summing with the bloom. A BRIGHT iris field ramps DOWN to
    # a still-LUMINOUS mid-cyan rim — the disc bottoms out on mid-cyan, never on
    # navy, so no body pixel is darker or lower chroma than the day sky behind it.
    # No dome, no hardware: the whole mass is light, brightest at the edge inward.
    _radial_orb(surf, cx, cy, ORB_R, IRIS_HI, IRIS_MID, IRIS_MID)
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

    # 5) DAY CONTAINMENT — a faint BRIGHT light-cyan hairline at the very edge,
    # drawn BELOW the rim glow. There is deliberately NO dark contour: a dark
    # keyline summed with a dark body rim into the "hardware donut" this concept
    # exists to avoid. Containment is achieved with LIGHT — a 1px luminous hairline
    # at low alpha that crisps the silhouette against the brightest day sky while
    # keeping the edge brighter than the sky, so the first read is a glowing
    # spirit-light with a crisp BRIGHT boundary, never a dark band.
    key = pygame.Surface((ORB_R * 2 + 2, ORB_R * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(key, (*HAIRLINE, 70), (ORB_R + 1, ORB_R + 1), ORB_R, 1)
    surf.blit(key, (cx - ORB_R - 1, cy - ORB_R - 1))

    # 6) RIM GLOW — a bright additive cyan corona riding the TRUE OUTER edge of the
    # disc. The hot cyan-white rim-light is the BRIGHTEST ring in the whole orb and
    # sits on the outermost 2-3px of the silhouette, so the very first thing the
    # eye catches at the boundary is a luminous edge that falls OUTWARD into bloom.
    # Drawn LAST so it caps the body straight into its outer wash: the day read is
    # "the glow IS the shape", with the edge as its brightest part — zero dark
    # containment. The corona FLARES at the pinpoint frame, hotter and wider, so
    # the orb visibly pulses the instant the pupil pinches shut.
    pad = 16
    rim = pygame.Surface((ORB_R * 2 + pad * 2, ORB_R * 2 + pad * 2), pygame.SRCALPHA)
    rc = ORB_R + pad
    # Hot cyan-white rim-light riding the OUTERMOST 3px of the disc — the brightest
    # ring in the orb. Centred on the silhouette boundary (ORB_R) and reaching one
    # px out, so the edge pixel itself is the brightest, falling outward into bloom.
    for d in range(-2, 1):
        a = min(255, int((205 + 18 * d) * min(1.35, 0.95 + 0.32 * k["bloom"])))
        pygame.draw.circle(rim, (*RIMLIGHT, a), (rc, rc), ORB_R + d, 1)
    # cyan bloom feathering outward from the bright edge, flaring at the pinpoint.
    # The house silhouette outline (game/parrot._add_outline) traces a 1px DARK ring
    # around any pixel with alpha > 8 — a soft additive tail that lingers at low
    # alpha would get that dark ring drawn at the FAINT bloom edge, re-introducing
    # the very annulus this concept must avoid. So the bloom alpha is forced to fall
    # BELOW that threshold within a tight radius (steep cutoff) and the outermost
    # visible shell is kept BRIGHT cyan-white at high alpha, so wherever the outline
    # mask bites it lands on a luminous edge covered by bright pixels — never a dark
    # halo out in the dim wash.
    reach = int(round(5 + 3 * (k["bloom"] - 0.86)))
    for d in range(reach, 0, -1):
        f = 1.0 - d / (reach + 1)
        # bright cyan-white near the rim shading to cyan outward, alpha ramped so the
        # outer 1-2px die to ~0 (under the outline threshold) for a clean bright edge.
        col = RIMLIGHT if d <= 2 else BLOOM
        a = int(190 * (f ** 1.6) * k["bloom"])
        pygame.draw.circle(rim, (*col, a), (rc, rc), ORB_R + d, 1)
    surf.blit(rim, (cx - rc, cy - rc), special_flags=pygame.BLEND_RGBA_ADD)

    # 7) BRIGHT DISC-EDGE CAP — the house outline (game/parrot._add_outline) is drawn
    # UNDER the sprite and traces a 1px DARK ring on the alpha>8 contour. Where a
    # semi-transparent bloom sits over that ring it BLEEDS THROUGH, muting the rim to
    # grey — the day annulus this concept must kill. The cure is an OPAQUE bright
    # cyan ring riding the body's true edge (ORB_R..ORB_R+2): it fully covers the
    # outline so the first read at the silhouette is a luminous edge, never a grey
    # band. Kept THIN and hugging the disc so the soft additive bloom (for the
    # night glow + pinpoint flare) can still extend OUTWARD past it untouched.
    for d in range(0, 3):
        col = lerp_color(RIMLIGHT, IRIS_HI, d / 2.0)
        pygame.draw.circle(surf, (*col, 255), (cx, cy), ORB_R + 2 - d, 2)

    # 8) BLOOM ALPHA CLIFF — the additive corona (rim glow + _glow_dot) feathers a
    # low-alpha tail PAST the opaque base; on a DAY sky the outline would trace that
    # faint terminus far out. A single sharp cliff at `term` (full-strength inside,
    # alpha 0 outside) forces the outline to land as ONE thin 1px ring at the corona
    # rim, never a band over the bright disc. On NIGHT the corona inside the cliff
    # still blooms and FLARES with the blink, and the outline ring is invisible on
    # the black sky. `term` matches the opaque base so the silhouette is one clean
    # bright disc — only the unusable additive overshoot is cut.
    clip = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.circle(clip, (255, 255, 255, 255), (cx, cy), term)
    surf.blit(clip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return surf


# Expose the pose set so render harnesses can introspect the 4 frames.
WING_ANGLES = _WING_ANGLES
