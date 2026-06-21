"""Concept: THE RINGSHIP (Torus) for `skin_ufo`.

The legendary showpiece of the set: a spinning donut/halo craft. There is no
hull, no dome, no wings — the PROPULSION IS THE RING. A thick torus with a
VISIBLE see-through hole through its middle and a small glowing bead suspended
in the dead centre give it a one-of-a-kind "O with a dot" outline that no
solid saucer/wedge/pod in the set can mimic. The negative-space hole is the
instant 40px tell.

Signature tell (no wings, no live particles): the ring SPINS. A bright
highlight ARC travels around the torus across the 4 poses — 12 → 3 → 6 → 9
o'clock — reading as rotation, while the centre bead steadily pulses. Because
the tell is a high-value arc sweeping a mid-value ring, it survives grayscale
and colourblind play (no reliance on hue).

Contract mirrors game/animal_ufo.py: build(wing_angle_deg) -> 64x84 SRCALPHA
Surface, ring centred at (32,44), drawn UPRIGHT (no baked rotation; the velocity
tilt is applied later by the getter). Pip's parcel hangs just below centre in
play, so the ring is centred high enough that the hole + bead + arc all read
ABOVE/AROUND the parcel.
"""
import math
import pygame

from game.parrot import _add_outline, _aaellipse  # noqa: F401 (parity w/ prod)


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY            # torus centre → (32, 44)

# Torus geometry. The OUTER radius defines the disc; the INNER radius punches
# the donut hole. The inner radius is kept at ~0.46 of the outer so the hole
# stays generously open — the brief flags that below ~0.35 the hole closes at
# 40px and the craft collapses into a solid disc. A slight vertical squash
# (RY < RX) gives the torus a touch of perspective without flattening the hole.
OUT_RX, OUT_RY = 26, 23           # outer ellipse → ~52px wide ring
IN_RX,  IN_RY  = 12, 10           # inner hole (0.46 / 0.43 of outer) → stays open
HOLE_RATIO = IN_RX / OUT_RX       # ≈ 0.46  (guard: must stay ≥ ~0.35)


# ── palette ──────────────────────────────────────────────────────────────────
# A shaded cyan torus, a near-white travelling highlight arc, and a hot amber
# centre bead. Inner + outer keylines (a dark hairline on both rims) hold the
# donut shape against a bright DAY sky; at NIGHT the ring + bead bloom for the
# legendary glow tier.
RING_LIGHT  = (58, 160, 201)      # #3AA0C9  lit cyan (upper-left of the torus)
RING_DARK   = (22, 70, 94)        # #16465E  shaded cyan (lower-right of the torus)
RING_DEEP   = (14, 46, 62)        # deepest inner-shadow band
HILITE      = (207, 246, 255)     # #CFF6FF  travelling rotation arc
KEYLINE     = (8, 26, 36)         # dark hairline on inner + outer rims (day hold)

BEAD_CORE   = (255, 226, 90)      # #FFE25A  hot amber centre bead
BEAD_HOT    = (255, 248, 214)     # white-hot pip at the bead's heart
BEAD_GLOW   = (255, 214, 96)      # bead bloom (night legendary glow)
# alt MAGENTA colorway: RING_LIGHT (201,90,178); RING_DARK (92,22,78);
#                       HILITE (255,224,250); BEAD_CORE (120,236,255)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 spin frame. _WING_ANGLES runs 50→-40 across
    the four poses, so each pose advances the highlight arc one quarter-turn
    around the torus (12 → 3 → 6 → 9 o'clock)."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Clock position (in pygame screen degrees, 0°=east/3-o'clock, CCW positive) of
# the highlight-arc CENTRE per phase. 12→3→6→9 o'clock reads as a clockwise
# spin: top, right, bottom, left. (90, 0, -90, 180) places the arc there.
_ARC_CENTER_DEG = (90, 0, -90, 180)
_ARC_SPAN_DEG = 78                # how much of the rim the bright arc covers


def _ring_band(surf, cx, cy, rx, ry, color, width):
    """A torus band drawn as a thick anti-aliased ellipse outline. Stacking a
    few of these (large→small, light→dark) cheaply fakes the tube shading of a
    torus without per-pixel work."""
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


def _punch_hole(surf, cx, cy, rx, ry):
    """Cut a TRUE transparent donut hole through the torus. The ring is drawn
    on `surf`; multiplying an opaque-where-outside / zero-alpha-where-inside
    mask zeroes the hole's alpha, so the sky shows through it in play. This is
    what gives the unique see-through "O" silhouette — a solid inner fill would
    read as a plain disc."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    _aaellipse(mask, (0, 0, 0, 0), (cx, cy), rx, ry)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def _spin_arc(surf, cx, cy, rx, ry, center_deg, color, width):
    """The travelling rotation highlight: a bright arc segment riding the MID
    line of the torus tube, centred at `center_deg` and spanning ~78°. Across
    the 4 phases its centre walks 12→3→6→9 o'clock, so a single bright crest
    appears to orbit the ring — the spin tell. A short trailing arc at lower
    value sells direction of travel (a comet-like wake), not a strobe."""
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    half = math.radians(_ARC_SPAN_DEG / 2)
    c = math.radians(center_deg)
    # leading bright crest
    pygame.draw.arc(surf, color, rect, c - half, c + half, width)
    pygame.draw.arc(surf, color, rect, c - half * 0.5, c + half * 0.5, width + 1)
    # trailing wake (one step behind the crest → reads as motion, not a blink)
    wake = tuple(int(ch * 0.45 + RING_LIGHT[i] * 0.55) for i, ch in enumerate(color))
    pygame.draw.arc(surf, wake, rect, c + half, c + half * 2.0, width)


def _keyline_ring(surf, cx, cy, rx, ry, color, width=1):
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


def _bead(surf, cx, cy, ph):
    """The centre bead suspended in the donut hole: a baked additive bloom (so
    it blooms at night without punching the ring) + a hot amber core + a white
    pip. It PULSES steadily with the spin (slightly larger on even phases) so
    the heart of the craft feels alive while the ring rotates around it."""
    pulse = 1.0 if ph % 2 == 0 else 0.82
    rad = int(9 * pulse) + 2
    g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    for i in range(3, 0, -1):
        a = int((30 + (3 - i) * 26) * pulse)
        rr = int(rad * i / 3)
        pygame.draw.circle(g, (*BEAD_GLOW, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)
    r = int(4 * pulse) + 1
    pygame.draw.circle(surf, KEYLINE, (cx, cy), r + 1)          # dark contour (day hold)
    pygame.draw.circle(surf, BEAD_CORE, (cx, cy), r)
    pygame.draw.circle(surf, BEAD_HOT, (cx - 1, cy - 1), max(1, r - 2))


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)

    # ── 1. The torus tube ────────────────────────────────────────────────────
    # Build the ring on its own scratch surface so the hole-punch (which zeroes
    # alpha) can't bite into the centre bead, which is composited afterwards.
    ring = _new()
    # Fill the full outer ellipse, then shade with concentric darker bands so the
    # tube reads round (lit toward upper-left, shaded toward lower-right). The
    # hole is punched after, leaving a clean torus cross-section.
    _aaellipse(ring, RING_DARK, (BCX, BCY), OUT_RX, OUT_RY)
    _aaellipse(ring, RING_LIGHT, (BCX - 2, BCY - 2), OUT_RX - 2, OUT_RY - 2)
    _aaellipse(ring, RING_DARK, (BCX + 2, BCY + 3), OUT_RX - 6, OUT_RY - 6)
    _aaellipse(ring, RING_DEEP, (BCX + 1, BCY + 2), IN_RX + 5, IN_RY + 5)

    # ── 2. Punch the see-through donut hole (the signature negative space) ────
    _punch_hole(ring, BCX, BCY, IN_RX, IN_RY)

    # ── 3. Rim keylines so the donut holds on a bright DAY sky ────────────────
    # Without these the cyan torus + its hole blur into a pale sky. A dark
    # hairline on BOTH the outer rim and the inner-hole rim hard-edges the "O".
    _keyline_ring(ring, BCX, BCY, OUT_RX, OUT_RY, KEYLINE, 1)
    _keyline_ring(ring, BCX, BCY, IN_RX, IN_RY, KEYLINE, 1)

    # ── 4. The travelling spin highlight ─────────────────────────────────────
    # Rides the MID line of the tube (between inner & outer radii). Walks one
    # quarter-turn per phase → the ring reads as rotating.
    mid_rx = (OUT_RX + IN_RX) / 2
    mid_ry = (OUT_RY + IN_RY) / 2
    _spin_arc(ring, BCX, BCY, mid_rx, mid_ry, _ARC_CENTER_DEG[ph], HILITE, 3)

    surf.blit(ring, (0, 0))

    # ── 5. The centre bead, floating in the hole ─────────────────────────────
    _bead(surf, BCX, BCY, ph)

    return surf
