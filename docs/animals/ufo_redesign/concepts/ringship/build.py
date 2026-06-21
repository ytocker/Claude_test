"""Concept: THE RINGSHIP (Torus) for `skin_ufo`.

The legendary showpiece of the set: a spinning donut/halo craft. There is no
hull, no dome, no wings — the PROPULSION IS THE RING. A thick torus with a
TRULY see-through hole through its middle and a small glowing bead floating in
the open sky inside that hole give it a one-of-a-kind "O with a dot" outline
that no solid saucer/wedge/pod in the set can mimic. The negative-space hole —
real sky/stars visible through it — is the instant 40px tell.

Signature tell (no wings, no live particles): the ring SPINS. A bright comet
crest TRAVELS around the torus across the 4 poses — 12 → 3 → 6 → 9 o'clock —
reading as rotation, while the centre bead steadily pulses. Because the tell is
a high-value crest sweeping a mid-value ring, it survives grayscale and
colourblind play (no reliance on hue).

Why the hole must be punched LAST: the outline pass the getter applies
(`pygame.mask.from_surface(threshold=8)`) promotes ANY non-trivial alpha to an
opaque silhouette pixel. Round 1 punched the hole, then the bead bloom washed
~alpha-30 amber back across the whole hole, and the outline then froze that
wash into an opaque brown bowl. So here: draw EVERYTHING (shading, comet,
bead + bloom), then zero the hole alpha as the final step with a hard mask, so
the open annulus is genuinely transparent and the outline can't refill it. The
bead is small (r≈5) and lives inside a protected centre disc the mask spares,
so it floats in open sky with the annulus reading clearly ANNULAR around it.

Contract mirrors game/animal_ufo.py: build(wing_angle_deg) -> 64x84 SRCALPHA
Surface, ring centred at (32,44), drawn UPRIGHT (no baked rotation; the velocity
tilt is applied later by the getter). Pip's parcel hangs just below centre in
play; the torus is enlarged so the ring is the dominant mass and the parcel
reads as hosted within the lower arc of the hole, not a box stacked beneath it.
"""
import math
import pygame

from game.parrot import _add_outline, _aaellipse  # noqa: F401 (parity w/ prod)


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY            # torus centre → (32, 44)

# Torus geometry. Round 1 read as "small ring on a big box"; the torus is grown
# ~18% so the ring is the dominant mass relative to Pip's parcel. The OUTER
# radius defines the disc; the INNER radius punches the donut hole. The hole is
# kept generously open (~0.42 of the outer) so it survives at 40px. A slight
# vertical squash (RY < RX) gives a touch of perspective without flattening the
# hole.
OUT_RX, OUT_RY = 30, 27           # grown outer ring → ~60px wide
IN_RX,  IN_RY  = 15, 13           # inner hole (~0.50 / 0.48 of outer) → wide open
HOLE_RATIO = IN_RX / OUT_RX       # ≈ 0.50  (guard: must stay ≥ ~0.35)

# Bead lives inside a small protected centre disc the hole-punch spares;
# everything between this disc and the inner rim is the OPEN-SKY annulus (true
# transparency). The pip is kept small so the annulus reads as a generous RING
# of sky all the way around it, not two crescents beside it.
BEAD_R = 4                        # clean hot-amber pip
PROTECT_R = BEAD_R + 1            # the punch mask spares a disc this size


# ── palette ──────────────────────────────────────────────────────────────────
# A shaded cyan torus, a near-white travelling comet crest, and a hot amber
# centre pip. Inner + outer keylines hold the donut shape against a bright DAY
# sky; at NIGHT the ring + bead bloom for the legendary glow tier.
RING_LIGHT  = (66, 176, 216)      # #42B0D8  lit cyan (upper-left of the torus)
RING_MID    = (40, 120, 156)      # mid tube value
RING_DARK   = (20, 66, 90)        # #14425A  shaded cyan (lower-right)
RING_DEEP   = (12, 42, 58)        # deepest inner-shadow band
INNER_BEVEL = (150, 224, 248)     # light catch on the inner rim (tube reads round)
HILITE      = (216, 248, 255)     # #D8F8FF  comet crest (near-white)
HILITE_HOT  = (255, 255, 255)     # white-hot tip of the crest
KEYLINE     = (8, 26, 36)         # dark hairline on inner + outer rims (day hold)
RIM_GLOW    = (120, 224, 255)     # restrained cyan rim-glow on the OUTER torus

BEAD_CORE   = (255, 226, 90)      # #FFE25A  hot amber centre pip
BEAD_HOT    = (255, 250, 224)     # white-hot heart of the pip
BEAD_GLOW   = (255, 214, 96)      # bead bloom (night legendary glow)
BEAD_SPARK  = (255, 255, 255)     # specular sparkle on the pip
# alt MAGENTA colorway: RING_LIGHT (212,108,190); RING_DARK (96,24,80);
#                       HILITE (255,232,252); BEAD_CORE (120,236,255)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 spin frame. _WING_ANGLES runs 50→-40 across
    the four poses, so each pose advances the comet crest one quarter-turn
    around the torus (12 → 3 → 6 → 9 o'clock)."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Clock position (pygame screen degrees, 0°=east/3-o'clock, CCW positive) of
# the comet-crest CENTRE per phase. 12→3→6→9 o'clock reads as a clockwise spin:
# top, right, bottom, left. (90, 0, -90, 180) places the crest there.
_ARC_CENTER_DEG = (90, 0, -90, 180)


def _ring_tube(surf):
    """The torus cross-section, shaded light→dark from upper-left to lower-right
    so the tube reads ROUND. Concentric offset ellipses cheaply fake the tube
    roll without per-pixel work; the inner bevel (a thin light catch just inside
    the hole rim) makes the tube look round from the INSIDE once the hole opens."""
    _aaellipse(surf, RING_DARK,  (BCX, BCY), OUT_RX, OUT_RY)
    _aaellipse(surf, RING_MID,   (BCX - 1, BCY - 1), OUT_RX - 2, OUT_RY - 2)
    _aaellipse(surf, RING_LIGHT, (BCX - 3, BCY - 3), OUT_RX - 5, OUT_RY - 5)
    # roll the value back down toward the hole so the inner lip reads shaded
    _aaellipse(surf, RING_MID,   (BCX + 2, BCY + 3), OUT_RX - 9, OUT_RY - 8)
    _aaellipse(surf, RING_DARK,  (BCX + 2, BCY + 3), IN_RX + 6, IN_RY + 6)
    _aaellipse(surf, RING_DEEP,  (BCX + 1, BCY + 2), IN_RX + 3, IN_RY + 3)
    # upper-left inner bevel: a thin bright catch on the inner rim so the tube
    # looks round from inside the hole (the hole's own "shoulder" highlight)
    bev = pygame.Rect(int(BCX - IN_RX - 2), int(BCY - IN_RY - 2),
                      int((IN_RX + 2) * 2), int((IN_RY + 2) * 2))
    pygame.draw.arc(surf, INNER_BEVEL, bev,
                    math.radians(60), math.radians(170), 2)


def _gloss(surf):
    """A thin upper-left gel highlight on the OUTER tube. Round 1's broad gloss
    read as a marble; this is cut to roughly half — a slim crescent that says
    'glassy craft', not 'glass bead'."""
    gloss_rect = pygame.Rect(int(BCX - OUT_RX + 3), int(BCY - OUT_RY + 2),
                             int((OUT_RX - 3) * 2), int((OUT_RY - 2) * 2))
    gloss = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(gloss, (255, 255, 255, 150), gloss_rect,
                    math.radians(108), math.radians(168), 2)
    surf.blit(gloss, (0, 0))


def _outer_rim_glow(surf, night_strength=1.0):
    """A restrained cyan rim-glow hugging the OUTER edge of the torus — NOT a
    full bloom of the whole ring (the brief flags glow restraint). Baked
    additively so it shows on day and blooms a touch more in the night
    composite. Kept to a 2-3px halo so the silhouette stays crisp."""
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i, a in enumerate((34, 22, 12)):
        rx, ry = OUT_RX + i, OUT_RY + i
        rect = pygame.Rect(int(BCX - rx), int(BCY - ry), int(rx * 2), int(ry * 2))
        pygame.draw.ellipse(glow, (*RIM_GLOW, int(a * night_strength)), rect, 2)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _spin_comet(surf, ph):
    """The travelling spin tell: a TIGHT, bright comet crest riding the MID line
    of the tube, with a desaturated wake pulled well behind it so frames read as
    MOTION, not a static window reflection. The crest walks 12→3→6→9 o'clock
    across the phases, so a single bright head appears to orbit the ring."""
    mid_rx = (OUT_RX + IN_RX) / 2
    mid_ry = (OUT_RY + IN_RY) / 2
    rect = pygame.Rect(int(BCX - mid_rx), int(BCY - mid_ry),
                       int(mid_rx * 2), int(mid_ry * 2))
    c = math.radians(_ARC_CENTER_DEG[ph])

    # Wake FIRST (under the crest): a long, dim, desaturated tail trailing the
    # crest by a wide angular gap → clear direction of travel, not a smear.
    wake = tuple(int(HILITE[i] * 0.40 + RING_LIGHT[i] * 0.60) for i in range(3))
    wake_lo = math.radians(_ARC_CENTER_DEG[ph]) + math.radians(20)
    wake_hi = wake_lo + math.radians(74)
    pygame.draw.arc(surf, wake, rect, wake_lo, wake_hi, 3)

    # Crest: a narrow bright head (~30° span) stacked to a white-hot tip, much
    # tighter and brighter than round 1's broad 78° smear.
    head = math.radians(15)
    pygame.draw.arc(surf, HILITE, rect, c - head, c + head, 4)
    pygame.draw.arc(surf, HILITE_HOT, rect,
                    c - head * 0.45, c + head * 0.45, 2)


def _keyline_ring(surf, cx, cy, rx, ry, color, width=1):
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


def _bead(surf, ph):
    """The centre pip floating in the OPEN hole: a tight additive bloom + a hot
    amber core + a white-hot heart + a specular sparkle. It PULSES with the spin
    (slightly larger on even phases). The bloom is kept INSIDE the protected
    centre disc so it can't wash the open-sky annulus — the hole-punch that runs
    after this spares only this disc, so the bead survives but the annulus stays
    transparent."""
    pulse = 1.0 if ph % 2 == 0 else 0.84
    r = int(BEAD_R * pulse)

    # tight bloom, contained well within the protected disc so it never bleeds
    # into the open annulus the punch will clear
    brad = PROTECT_R
    g = pygame.Surface((brad * 2, brad * 2), pygame.SRCALPHA)
    for i in range(3, 0, -1):
        a = int((40 + (3 - i) * 34) * pulse)
        pygame.draw.circle(g, (*BEAD_GLOW, a), (brad, brad), int(brad * i / 3))
    surf.blit(g, (BCX - brad, BCY - brad), special_flags=pygame.BLEND_RGBA_ADD)

    pygame.draw.circle(surf, KEYLINE, (BCX, BCY), r + 1)        # dark contour (day hold)
    pygame.draw.circle(surf, BEAD_CORE, (BCX, BCY), r)
    pygame.draw.circle(surf, BEAD_HOT, (BCX - 1, BCY - 1), max(1, r - 2))
    # specular sparkle: a tiny white glint so the day pip looks as alive as night
    surf.set_at((BCX - 2, BCY - 2), BEAD_SPARK)
    pygame.draw.circle(surf, BEAD_SPARK, (BCX - 1, BCY - 1), 1)


def _punch_hole_last(surf):
    """Zero the alpha of the OPEN ANNULUS as the FINAL step. A hard white mask
    with a black (zero-alpha) ring — outer edge at the inner rim, inner edge
    sparing the bead's protected disc — multiplies the surface, clearing only
    the sky annulus. Done last so neither the bead bloom nor the getter's
    outline pass can refill it: the annulus is GENUINELY transparent and sky /
    stars show through it in play."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    # carve the open-sky ring: zero-alpha out to the inner rim …
    _aaellipse(mask, (0, 0, 0, 0), (BCX, BCY), IN_RX, IN_RY)
    # … but restore alpha over the protected centre disc so the bead survives
    _aaellipse(mask, (255, 255, 255, 255), (BCX, BCY), PROTECT_R, PROTECT_R)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)

    # 1. Torus tube (shaded round) on its own scratch so the hole-punch can be
    #    applied to the ring + bead together as the very last step.
    _ring_tube(surf)

    # 2. Rim keylines so the donut holds on a bright DAY sky.
    _keyline_ring(surf, BCX, BCY, OUT_RX, OUT_RY, KEYLINE, 1)
    _keyline_ring(surf, BCX, BCY, IN_RX, IN_RY, KEYLINE, 1)

    # 3. Thin gloss + restrained outer rim-glow (premium polish, day == night).
    _gloss(surf)
    _outer_rim_glow(surf)

    # 4. Travelling comet crest (the spin tell).
    _spin_comet(surf, ph)

    # 5. The centre pip, floating in the hole.
    _bead(surf, ph)

    # 6. Punch the open-sky annulus LAST → the hole is truly see-through.
    _punch_hole_last(surf)

    return surf
