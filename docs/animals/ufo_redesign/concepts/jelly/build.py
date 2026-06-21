"""Concept: THE BIO-JELLYFISH for `skin_ufo`.

The organic counterpoint to a set of hard-edged saucers and slabs. A smooth
translucent DOME BELL on top with 3 thick wavy TENDRILS dangling below — a
clear jellyfish outline with a fringed lower margin that NOTHING else in the
set has. The tendrils are the silhouette tell: nothing else is soft/organic.
The 40px read is "a floating space jellyfish".

Signature tell (no wings, no live particles): a PULSE. The bell squashes and
stretches across the 4 frames (tall-narrow → wide-flat) like a real jelly
contracting to propel itself, and the tendrils trail with a slight phase lag.
It's a SHAPE change, so the motion survives grayscale — it doesn't lean on a
glow. Bioluminescent dots on the bell margin + tendril tips give the alive,
deep-sea feel.

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

# The bell is a wide round dome. Its RESTING half-size; each frame scales these
# to squash/stretch. Kept slightly wider than tall so the resting read is a
# dome, never a sphere. The bell apex sits well above BCY and the fringe just
# below it, so the bell mass clearly straddles (32,44) for the 14px collision
# circle while the dome dominates the top half.
BELL_RX, BELL_RY = 18, 15         # resting bell half-width / half-height
BELL_TOP_DY = 16                  # bell apex above BCY


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
# alt CYAN colorway: BELL_HI (140,210,255); BELL_LO (40,96,168);
#                    DOME_HILITE (214,238,255); TENDRIL (70,150,220);
#                    BIO_DOT (120,255,210)


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


def _fringe(surf, cx, fringe_y, rx, drop, color):
    """The scalloped lower margin of the bell — short rounded lobes hanging off
    the bell's bottom rim. This fringe is the organic tell that separates the
    jelly from every domed saucer in the set; it flares DOWN when the bell is
    expanded (frame 2) and tucks UP when contracted (frame 0). Drawn as a few
    overlapping circles so it stays a soft scallop, not a saw-tooth."""
    n = 5
    for i in range(n):
        t = (i + 0.5) / n
        lx = int(cx - rx * 0.92 + (2 * rx * 0.92) * t)
        # lobes hang lower toward the centre (a gentle arc), plus the pulse drop.
        sag = drop + 2 + int(2 * (1.0 - abs(0.5 - t) * 2))
        ly = int(fringe_y + sag)
        rr = 3 if 0 < i < n - 1 else 2
        pygame.draw.circle(surf, color, (lx, ly), rr)


def _tendril(surf, x0, y0, length, amp, freq, phase, color, shade):
    """One THICK wavy tendril hanging from the bell. Built as a sine-offset
    point list, then stroked by stamping fat circles along the path (round caps
    + round joins, no thin-line gaps) so it stays a chunky strand that survives
    the 40px downscale rather than dissolving into the bio-glow. A darker shade
    pass on one side gives a hint of round volume. The `phase` (driven by the
    trailing bell pulse) shifts the wave so the tendril sways with a lag behind
    the bell. Returns the tip point for the bioluminescent cap."""
    pts = []
    steps = 12
    for i in range(steps + 1):
        t = i / steps
        # taper the sway: small near the bell root, fuller toward the free tip.
        sway = amp * (0.2 + 0.8 * t)
        x = x0 + math.sin(phase + t * freq * math.pi) * sway
        y = y0 + t * length
        pts.append((x, y))
    # Stamp graduated round dots along the path so the strand is a solid worm
    # that tapers from a fat root to a slim tip — the chunky organic read.
    for i, (x, y) in enumerate(pts):
        t = i / steps
        w = max(1, int(round(3.0 - 1.6 * t)))   # ~3px root → ~1px tip
        pygame.draw.circle(surf, shade, (int(x + 1), int(y)), w)
    for i, (x, y) in enumerate(pts):
        t = i / steps
        w = max(1, int(round(3.0 - 1.6 * t)))
        pygame.draw.circle(surf, color, (int(x), int(y)), w)
    tx, ty = pts[-1]
    return (int(tx), int(ty))


def _bio_dot(surf, center, r, *, halo=2.0):
    """A baked bioluminescent dot: a soft additive aqua halo (blooms at night)
    + a hot core. Stamped on a scratch surface so the additive bloom never
    punches holes in the body. The dot is the deep-sea 'alive' accent on the
    tendril TIPS (high-value strand-tells) and a couple on the bell crown — kept
    TIGHT (small halo) so adjacent dots never bleed into one aqua band that
    erases the tendril read at 40px."""
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
    # The tendril wave PHASE trails the bell pulse by one step (the lag). Three
    # WELL-SEPARATED strands (roots spread wide across the fringe) so they read
    # as three distinct legs at 40px — the jellyfish silhouette tell — and the
    # outer two splay out from the centre rather than overlapping it.
    tph = _phase_to_wave((ph - _TENDRIL_LAG) % 4)
    tend_top = fringe_y - 1
    roots = [BCX - 11, BCX, BCX + 11]
    lengths = [30, 36, 30]
    amps = [5.0, 6.0, 5.0]
    tips = []
    for rxn, (rxr, ln, am) in enumerate(zip(roots, lengths, amps)):
        # outer tendrils sway in counter-phase to the centre one for a lifelike,
        # non-uniform drift; centre hangs longest (the classic jelly profile).
        ph_off = tph + (math.pi if rxn != 1 else 0.0)
        tip = _tendril(surf, rxr, tend_top, ln, am, 2.2, ph_off,
                       TENDRIL, TENDRIL_LO)
        tips.append(tip)

    # ── translucent bell body (vertical gel gradient) ─────────────────────────
    _bell_gradient(surf, BCX, bell_cy, rx, ry)

    # Deep inner shadow low under the dome → reads as a hollow gel volume.
    _aaellipse(surf, (*BELL_CORE, 150), (BCX, bell_cy + ry // 3), rx - 5, ry // 2)

    # Bright dome highlight cap high on the bell (the wet, lit crown).
    _aaellipse(surf, DOME_HILITE, (BCX - 3, bell_cy - ry // 2), rx - 8, ry // 3 + 1)
    # a small hot specular pip on the crown
    _aaellipse(surf, (255, 255, 255), (BCX - 5, bell_cy - ry // 2 - 1), 2, 1)

    # Bright rim keyline arc over the top of the dome — the high-value lip that
    # holds the translucent body's shape against a bright DAY sky.
    rect = pygame.Rect(BCX - rx, bell_cy - ry, rx * 2, ry * 2)
    pygame.draw.arc(surf, BELL_RIM, rect, math.radians(15), math.radians(165), 2)

    # ── scalloped fringe margin (the organic tell) ────────────────────────────
    _fringe(surf, BCX, fringe_y, rx, fringe, BELL_LO)
    # a brighter rim line just above the fringe so the lobes read as bell edge.
    pygame.draw.arc(surf, BELL_RIM,
                    pygame.Rect(BCX - rx, bell_cy - ry, rx * 2, ry * 2 + 4),
                    math.radians(200), math.radians(340), 2)

    # ── bioluminescent accents: a TIGHT pair on the crown + each tendril tip ──
    # No fringe band — those dots merged into one aqua smear that erased the
    # tendrils. Instead: two small glints on the dome crown (the alive 'eyes' of
    # the bell) + one hot dot per tendril TIP, which doubles as the strand-tell
    # so the eye counts three legs even when their mid-sections are faint.
    _bio_dot(surf, (BCX - 6, bell_cy - 2), 2, halo=1.8)
    _bio_dot(surf, (BCX + 6, bell_cy - 2), 2, halo=1.8)
    for tip in tips:
        _bio_dot(surf, tip, 2, halo=2.2)

    return surf


def _phase_to_wave(ph):
    """Map a 0..3 pulse index to a sine PHASE for the tendril sway, so the
    strands advance smoothly around the wave rather than jumping."""
    return (ph / 4.0) * 2.0 * math.pi
