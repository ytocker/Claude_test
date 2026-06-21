"""Concept: THE BIO-JELLYFISH for `skin_ufo`.

The organic counterpoint to a set of hard-edged saucers and slabs. A smooth
translucent DOME BELL on top whose scalloped lower margin overhangs a SPRAY of
thin drifting TENDRILS — a clear jellyfish outline that NOTHING else in the set
has. The bell dominates the top; the strands splay outward like seaweed below
it, in front of Pip's parcel. The 40px read is "a domed bell with a spray of
drifting strands beneath" — never a face, never a box, never two legs.

Why the round-2 shape moves: at 40px the round-1 build collapsed into a HUNCHED
HUMANOID — the symmetric crown dots paired as EYES, the parcel read as a TORSO,
and the two outer tendrils (with bright tip-dots) read as bent LEGS with FEET.
This rebuild deliberately breaks that gestalt:
  · crown dots moved UP onto the dome APEX and made ASYMMETRIC (offset, unequal)
    so they never pair as eyes at the mid-bell eye line;
  · 5 THIN tendrils of OFFSET lengths that wave/curl and splay OUTWARD past the
    bell centre — a seaweed spray, not two planted legs; no bright tip-dots;
  · bell pushed HIGHER + WIDER so the dome owns the top ~60% as one mass and its
    margin OVERHANGS the tendril cluster (a real jelly's bell is wider than its
    tendrils) — breaking the head/torso/legs vertical rhythm;
  · the scalloped fringe overhang exaggerated to be the silhouette tell — the
    one bumpy organic margin no saucer can have.

Signature tell (no wings, no live particles): a PULSE. The bell squashes and
stretches across the 4 frames (tall-narrow → wide-flat) like a real jelly
contracting to propel itself, and the tendrils trail with a slight phase lag.
It's a SHAPE change, so the motion survives grayscale — it doesn't lean on a
glow. Bioluminescent dots on the bell dome give the alive, deep-sea feel.

Contract mirrors game/animal_ufo.py: build(wing_angle_deg) -> 64x84 SRCALPHA
Surface; bell mass centred at (32,44); tendrils extend below but the bell (the
main read) stays clearly above centre so it frames Pip's parcel rather than
hiding behind it. Drawn UPRIGHT — no baked rotation (velocity tilt added later).
"""
import math
import pygame

from game.parrot import _add_outline, _aaellipse  # noqa: F401 (parity w/ prod)


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY            # bell body centre → (32, 44)

# The bell is a WIDE round dome — wider than round 1 so its margin overhangs the
# tendril roots (a jelly's bell is broader than its tendril cluster; that
# overhang is what stops the lower half reading as a body+legs). Its RESTING
# half-size; each frame scales these to squash/stretch. The apex is pushed
# HIGHER (BELL_TOP_DY) so the dome owns the top ~60% as one mass.
BELL_RX, BELL_RY = 21, 16         # resting bell half-width / half-height
BELL_TOP_DY = 19                  # bell apex above BCY (pushed high)


# ── palette ──────────────────────────────────────────────────────────────────
# Translucent bell: a vertical gradient from a brighter rim up top to a deep
# purple core low in the bell, with a near-white dome highlight cap. The DAY
# variant deepens the core + brightens the rim for value contrast against a
# bright sky; NIGHT lets the dome bloom.
BELL_HI     = (185, 140, 255)     # #B98CFF  bright translucent upper bell
BELL_LO     = (94, 58, 168)       # #5E3AA8  deep purple core (low in the bell)
DOME_HILITE = (232, 217, 255)     # #E8D9FF  bright dome highlight cap
BELL_RIM    = (212, 186, 255)     # bright rim keyline (holds shape on bright sky)
BELL_CORE   = (66, 38, 122)       # deepest inner shadow under the dome
TENDRIL     = (122, 79, 208)      # #7A4FD0  tendril strands
TENDRIL_LO  = (84, 50, 156)       # tendril shadow side
BIO_DOT     = (94, 242, 208)      # #5EF2D0  bioluminescent dots
BIO_GLOW    = (140, 255, 224)     # hot bioluminescent core


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 pulse frame. _WING_ANGLES runs 50→-40 across
    the four poses; the bell steps from contracted (tall-narrow) to expanded
    (wide-flat) and back, reading as one propulsion pulse per flap."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Per-frame bell SHAPE — the whole tell. A real jelly CONTRACTS (tall, narrow)
# to push water, then RELAXES (wide, flat). Across the cycle:
#   f0 most contracted (tall-narrow) → f1 mid → f2 expanded (wide-flat) →
#   f3 mid-recovering. The width/height swap is large enough to read at 40px as
#   a clear shape change, not a wobble. (rx_mul, ry_mul, fringe_drop).
_PULSE = [
    (0.84, 1.18, 0),    # f0 contracted: narrow + tall, fringe tucked up
    (0.94, 1.05, 1),    # f1 relaxing
    (1.16, 0.84, 3),    # f2 expanded: wide + flat, fringe flares down
    (1.02, 0.96, 2),    # f3 recovering
]

# Tendrils TRAIL the bell — they react one phase-step behind, so when the bell
# is contracted the tendrils are still drifting out from the previous expansion
# (the lag that sells organic motion). We index the wave by (phase-1).
_TENDRIL_LAG = 1


def _bell_dims(ph):
    rx_mul, ry_mul, fringe = _PULSE[ph]
    return BELL_RX * rx_mul, BELL_RY * ry_mul, fringe


def _bell_gradient(surf, cx, cy, rx, ry):
    """Stamp a vertical bell gradient (deep core low → bright up top) clipped to
    the bell ellipse. A translucent jelly needs the value ramp so it reads as a
    domed gel volume, not a flat purple blob. Slightly translucent overall so
    it feels gelatinous; the bright rim keyline restores hard shape on a bright
    sky."""
    top = int(cy - ry)
    bot = int(cy + ry)
    span = max(1, bot - top)
    grad = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for y in range(top, bot + 1):
        t = (y - top) / span          # 0 at apex → 1 at fringe
        # Bright near the top dome, deepening to the purple core, then a touch
        # of rim lift at the very bottom edge so the fringe doesn't read muddy.
        if t < 0.55:
            k = t / 0.55
            col = tuple(int(BELL_HI[i] + (BELL_LO[i] - BELL_HI[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            col = tuple(int(BELL_LO[i] + (BELL_RIM[i] - BELL_LO[i]) * (k * 0.5)) for i in range(3))
        # Translucent gel: a little see-through, denser toward the core.
        a = 224 - int(36 * (1.0 - abs(0.5 - t) * 2))
        pygame.draw.line(grad, (*col, a), (0, y), (COMPOSITE_W, y))
    # Mask the gradient to the bell ellipse (a HALF-rounded dome: full ellipse,
    # the fringe gets cut by the scalloped margin drawn after).
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(mask, (255, 255, 255, 255), (cx, cy), rx, ry)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (0, 0))


def _fringe(surf, cx, fringe_y, rx, drop, color, rim_color):
    """The scalloped lower margin of the bell — the SILHOUETTE TELL. Round 1's
    fringe was invisible at 40px, so the lower half read as a torso. Here the
    lobes are FATTER and hang BELOW the bell rim with a clear bumpy overhang,
    distinct from the thin tendrils that fall further below — that bumpy organic
    margin is the one shape no saucer can have. Lobes OVERHANG the tendril roots
    (the bell is wider than the strand cluster). It flares DOWN on the expanded
    frame and tucks UP on the contracted frame. Each lobe gets a small bright
    rim cap so the scallop edge reads as the lit lip of the bell."""
    n = 6
    span = rx * 1.04          # the scallop reaches just PAST the bell rim → overhang
    for i in range(n):
        t = (i + 0.5) / n
        lx = int(cx - span + (2 * span) * t)
        # lobes hang lower toward the centre (a gentle arc), plus the pulse drop;
        # a deeper baseline sag than round 1 so the overhang is unmistakable.
        sag = drop + 3 + int(3 * (1.0 - abs(0.5 - t) * 2))
        ly = int(fringe_y + sag)
        rr = 4 if 0 < i < n - 1 else 3
        pygame.draw.circle(surf, color, (lx, ly), rr)
        # bright cap on the upper edge of each lobe → the lit scallop lip
        pygame.draw.circle(surf, rim_color, (lx, ly - rr + 1), max(1, rr - 2))


def _tendril(surf, x0, y0, length, amp, freq, phase, curl, color, shade):
    """One THIN wavy/curling tendril. Round 1 used 3 chunky strands that planted
    like legs; here each strand is slimmer (≈2px root → 1px tip) and carries a
    CURL bias so its free end drifts OUTWARD like seaweed instead of hanging
    straight down. The taper + sine sway + curl keep the strands from ever
    forming a clean X or a planted post. The `phase` (driven by the trailing
    bell pulse) sways it with a lag behind the bell. No bright tip-dot — those
    read as feet/shoes. Returns the tip point."""
    pts = []
    steps = 13
    for i in range(steps + 1):
        t = i / steps
        # taper the sway: small near the root, fuller toward the free tip.
        sway = amp * (0.15 + 0.85 * t)
        # CURL: a steady outward lean that grows toward the tip (t**2) so the
        # strand splays away from the body axis like drifting seaweed.
        bend = curl * (t * t)
        x = x0 + math.sin(phase + t * freq * math.pi) * sway + bend
        y = y0 + t * length
        pts.append((x, y))
    # Stamp graduated round dots: a SLIM tapering worm (≈2px root → 1px tip).
    for i, (x, y) in enumerate(pts):
        t = i / steps
        w = max(1, int(round(2.4 - 1.4 * t)))   # ~2px root → ~1px tip
        pygame.draw.circle(surf, shade, (int(x + 1), int(y)), w)
    for i, (x, y) in enumerate(pts):
        t = i / steps
        w = max(1, int(round(2.4 - 1.4 * t)))
        pygame.draw.circle(surf, color, (int(x), int(y)), w)
    tx, ty = pts[-1]
    return (int(tx), int(ty))


def _bio_dot(surf, center, r, *, halo=2.0):
    """A baked bioluminescent dot: a soft additive aqua halo (blooms at night)
    + a hot core. Stamped on a scratch surface so the additive bloom never
    punches holes in the body. These now live ONLY on the dome (not at the eye
    line, not on the tendril tips) so they read as glands lighting the bell, not
    eyes or feet. Kept TIGHT (small halo) so they never bleed into a band."""
    cx, cy = center
    rad = int(r * halo) + 1
    g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    for i in range(3, 0, -1):
        a = 38 + (3 - i) * 28
        rr = int(rad * i / 3)
        pygame.draw.circle(g, (*BIO_DOT, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, BIO_DOT, (cx, cy), r)
    pygame.draw.circle(surf, BIO_GLOW, (cx, cy), max(1, r - 1))


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry, fringe = _bell_dims(ph)
    rx, ry = int(round(rx)), int(round(ry))

    # The bell apex stays anchored near the top; as it squashes/stretches the
    # CENTRE shifts so the apex (the read) holds roughly in place while the
    # fringe travels — that's how a real jelly pulses from a fixed crown.
    apex_y = BCY - BELL_TOP_DY
    bell_cy = apex_y + ry
    fringe_y = bell_cy + ry - 2

    # ── tendrils first, so the bell + fringe overlap their roots ──────────────
    # FIVE thin strands whose roots cluster in a NARROW span (±9) well inside the
    # bell margin — so the bell overhangs them and they never look like a pair of
    # legs spanning the body's full width. Their LENGTHS are offset (no two equal)
    # and they CURL outward by an amount that grows from the centre, so the spray
    # splays like seaweed and never plants as two posts or crosses into an X.
    # The tendril wave PHASE trails the bell pulse by one step (the lag).
    tph = _phase_to_wave((ph - _TENDRIL_LAG) % 4)
    tend_top = fringe_y - 1
    #         x-root      length  amp   curl (outward lean, signed)
    strands = [
        (BCX - 9, 27, 4.0, -7.0),   # far-left, leans left, short
        (BCX - 4, 35, 3.2, -3.0),   # inner-left, longer
        (BCX + 0, 31, 2.6,  0.0),   # centre, straightest, mid length
        (BCX + 5, 38, 3.4,  3.5),   # inner-right, longest
        (BCX + 9, 24, 4.2,  7.5),   # far-right, leans right, shortest
    ]
    for i, (rxr, ln, am, curl) in enumerate(strands):
        # alternate the sway phase so adjacent strands drift in different
        # directions — a non-uniform, lifelike spray rather than a parallel comb.
        ph_off = tph + (math.pi * (i % 2)) + i * 0.4
        _tendril(surf, rxr, tend_top, ln, am, 2.4, ph_off, curl,
                 TENDRIL, TENDRIL_LO)

    # ── translucent bell body (vertical gel gradient) ─────────────────────────
    _bell_gradient(surf, BCX, bell_cy, rx, ry)

    # Deep inner shadow low under the dome → reads as a hollow gel volume.
    _aaellipse(surf, (*BELL_CORE, 150), (BCX, bell_cy + ry // 3), rx - 6, ry // 2)

    # Bright dome highlight cap high on the bell (the wet, lit crown).
    _aaellipse(surf, DOME_HILITE, (BCX - 3, bell_cy - ry // 2), rx - 9, ry // 3 + 1)
    # a small hot specular pip on the crown
    _aaellipse(surf, (255, 255, 255), (BCX - 5, bell_cy - ry // 2 - 1), 2, 1)

    # Bright rim keyline arc over the top of the dome — the high-value lip that
    # holds the translucent body's shape against a bright DAY sky.
    rect = pygame.Rect(BCX - rx, bell_cy - ry, rx * 2, ry * 2)
    pygame.draw.arc(surf, BELL_RIM, rect, math.radians(15), math.radians(165), 2)

    # ── scalloped fringe margin (the organic tell) ────────────────────────────
    _fringe(surf, BCX, fringe_y, rx, fringe, BELL_LO, BELL_RIM)

    # ── bioluminescent accents: ASYMMETRIC pair high on the DOME APEX ─────────
    # The whole face-fix lives here. Round 1's two equal dots at mid-bell paired
    # as EYES. These sit UP on the dome apex (above the eye line entirely), are
    # OFFSET (not mirrored) and UNEQUAL in size, and a third tiny gland sits off
    # to one side — three uneven glints can't resolve into a symmetric pair of
    # eyes. They read as bio-glands lighting the top of the bell.
    apex = bell_cy - int(ry * 0.62)
    _bio_dot(surf, (BCX - 4, apex - 1), 2, halo=1.8)      # larger, left of centre, high
    _bio_dot(surf, (BCX + 6, apex + 3), 1, halo=1.6)      # smaller, lower + further right
    _bio_dot(surf, (BCX + 1, apex - 4), 1, halo=1.5)      # tiny third gland near the crown

    return surf


def _phase_to_wave(ph):
    """Map a 0..3 pulse index to a sine PHASE for the tendril sway, so the
    strands advance smoothly around the wave rather than jumping."""
    return (ph / 4.0) * 2.0 * math.pi
