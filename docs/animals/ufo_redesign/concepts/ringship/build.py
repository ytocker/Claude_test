"""Concept: THE RINGSHIP (Torus) for `skin_ufo`.

The legendary showpiece of the set: a spinning halo craft. There is no hull,
no dome, no wings — the PROPULSION IS THE RING. A clean shaded annulus with a
TRULY see-through hole through its middle gives it a one-of-a-kind "O" outline
that no solid saucer/wedge/pod in the set can mimic. The negative-space hole —
real sky/stars visible through it — is the instant 40px tell, and in play it
HOSTS Pip's parcel as the single focal object seated in the open ring.

Signature tell (no wings, no live particles): the ring SPINS. A narrow
white-hot crest TRAVELS around the rim across the 4 poses — 12 → 3 → 6 → 9
o'clock — reading as rotation. Because the tell is a high-value crest sweeping
a darker ring, it survives grayscale and colourblind play (no reliance on hue).

Round-3 topology fix (the make-or-break gate): rounds 1-2 refilled the open
hole — first with a brown bowl, then with a cyan one — because an additive
inward glow + a fat central pip + a too-narrow gap let colour bleed across the
aperture, and the getter's outline pass (`pygame.mask.from_surface(threshold=8)`)
then froze that bleed into an opaque disc. Round 3 ABANDONS the inward glow
entirely and ships a FLATTER hard-edged open ring: a cleanly shaded ceramic
annulus with a crisp inner keyline, NO inner glow/gel, and a GENEROUSLY WIDE
transparent gap that survives both the 1px outline growth AND the smoothscale
down to 40px with margin. The separate amber centre pip is dropped to a tiny
glint so Pip's parcel — composited by the game — owns the centre uncontested.
The hole is punched LAST with a hard mask so nothing can refill it.

Contract mirrors game/animal_ufo.py: build(wing_angle_deg) -> 64x84 SRCALPHA
Surface, ring centred at (32,44), drawn UPRIGHT (no baked rotation; the velocity
tilt is applied later by the getter). The torus is the dominant mass; Pip's
parcel reads as hosted within the lower arc of the open hole.
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
# the donut hole. Round 3 WIDENS the hole (inner ~0.55 of outer) so the open-sky
# gap survives the getter's 1px outline growth AND the smoothscale to ~40px with
# clear margin — a narrow gap was what let cyan dominate the visible hole. A
# slight vertical squash (RY < RX) gives a touch of perspective without
# flattening the hole.
OUT_RX, OUT_RY = 30, 27           # outer ring → ~60px wide
IN_RX,  IN_RY  = 17, 15           # inner hole (~0.57 / 0.56 of outer) → wide open
HOLE_RATIO = IN_RX / OUT_RX       # ≈ 0.57  (guard: must stay ≥ ~0.45 post-fix)

# The whole hole is open sky now — no protected centre disc, no central bead.
# Pip's parcel (composited by the game) is the focal object hosted in the gap.
# A single tiny glint may ride the upper inner rim as a spark of life, but it is
# pinned to the SOLID rim, never floated in the open gap (which would refill it).


# ── palette ──────────────────────────────────────────────────────────────────
# A FLATTER hard-edged ceramic/metal annulus: a shaded cyan ring body with a
# crisp dark inner keyline and a near-white travelling crest. No inner glow, no
# gel in the gap — the sky shows through cleanly. Night bloom is allowed ONLY on
# the OUTER edge (see _outer_rim_glow), never inward.
RING_LIGHT  = (88, 196, 232)      # #58C4E8  lit cyan (upper-left of the ring)
RING_MID    = (46, 134, 172)      # mid ring value
RING_DARK   = (24, 78, 104)       # #184E68  shaded cyan (lower-right)
RING_DEEP   = (14, 48, 66)        # deepest shadow band on the lower-right body
INNER_BEVEL = (176, 236, 252)     # bright catch on the upper inner rim (round read)
INNER_KEY   = (6, 22, 32)         # crisp dark inner keyline (holds the gap edge)
HILITE      = (224, 250, 255)     # #E0FAFF  comet crest body (near-white)
HILITE_HOT  = (255, 255, 255)     # white-hot tip of the crest
KEYLINE     = (8, 26, 36)         # dark hairline on the OUTER rim (day hold)
RIM_GLOW    = (120, 224, 255)     # restrained cyan rim-glow on the OUTER edge only

GLINT       = (255, 244, 210)     # tiny warm spark pinned to the solid upper rim
# alt MAGENTA colorway: RING_LIGHT (224,128,206); RING_DARK (110,32,92);
#                       HILITE (255,236,252); RIM_GLOW (255,150,236)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 spin frame. _WING_ANGLES runs 50→-40 across
    the four poses, so each pose advances the comet crest one quarter-turn
    around the torus (12 → 3 → 6 → 9 o'clock)."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Clock position (pygame screen degrees, 0°=east/3-o'clock, CCW positive) of the
# crest CENTRE per phase. 12→3→6→9 o'clock reads as a clockwise spin: top,
# right, bottom, left. (90, 0, -90, 180) places the crest there.
_ARC_CENTER_DEG = (90, 0, -90, 180)


def _ring_body(surf):
    """The flat-ish ring body, shaded light→dark from upper-left to lower-right
    so the annulus reads as a solid ROUND tube WITHOUT any inner glow. Concentric
    offset ellipses build the band between OUT and IN radii; the lower-right is
    rolled down to RING_DEEP so the ring has real value range. Drawing the whole
    disc and letting the hole-punch carve the centre keeps the band seamless."""
    # full disc, darkest first, lightening toward the upper-left lit edge
    _aaellipse(surf, RING_DARK,  (BCX, BCY), OUT_RX, OUT_RY)
    _aaellipse(surf, RING_DEEP,  (BCX + 2, BCY + 3), OUT_RX - 2, OUT_RY - 2)
    _aaellipse(surf, RING_DARK,  (BCX - 1, BCY - 1), OUT_RX - 3, OUT_RY - 3)
    _aaellipse(surf, RING_MID,   (BCX - 2, BCY - 2), OUT_RX - 5, OUT_RY - 5)
    _aaellipse(surf, RING_LIGHT, (BCX - 4, BCY - 4), OUT_RX - 8, OUT_RY - 7)
    # roll the value back DOWN toward the hole so the inner lip reads shaded, and
    # the upper inner rim stays a touch brighter (the bevel below lifts it more)
    _aaellipse(surf, RING_MID,   (BCX + 2, BCY + 3), IN_RX + 8, IN_RY + 7)
    _aaellipse(surf, RING_DARK,  (BCX + 2, BCY + 3), IN_RX + 4, IN_RY + 4)


def _inner_rim(surf):
    """The inner lip of the open hole: a CRISP dark keyline so the sky edge is
    hard, plus a LIFTED upper-left bevel (~20% brighter than round 2) so the
    tube reads round from inside against the now-darker, open aperture. No glow,
    no gel — just two thin strokes hugging the inner radius."""
    # lifted bevel on the upper-left inner rim (the hole's own shoulder highlight)
    bev = pygame.Rect(int(BCX - IN_RX - 1), int(BCY - IN_RY - 1),
                      int((IN_RX + 1) * 2), int((IN_RY + 1) * 2))
    pygame.draw.arc(surf, INNER_BEVEL, bev,
                    math.radians(55), math.radians(175), 2)
    # crisp dark inner keyline all the way round (holds the gap edge on bright sky)
    rect = pygame.Rect(int(BCX - IN_RX), int(BCY - IN_RY),
                       int(IN_RX * 2), int(IN_RY * 2))
    pygame.draw.ellipse(surf, INNER_KEY, rect, 1)


def _gloss(surf):
    """A thin upper-left gel highlight on the OUTER tube — a slim crescent that
    says 'glassy craft', kept narrow so it never reads as a glass bead."""
    gloss_rect = pygame.Rect(int(BCX - OUT_RX + 3), int(BCY - OUT_RY + 2),
                             int((OUT_RX - 3) * 2), int((OUT_RY - 2) * 2))
    gloss = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.arc(gloss, (255, 255, 255, 150), gloss_rect,
                    math.radians(108), math.radians(168), 2)
    surf.blit(gloss, (0, 0))


def _outer_rim_glow(surf, night_strength=1.0):
    """A restrained cyan rim-glow hugging ONLY the OUTER edge of the torus.
    Drawn on rings at OUT_RX..OUT_RX+2 — strictly OUTWARD of the body — so it can
    never bleed inward across the aperture. Additive so it shows faintly on day
    and blooms a touch more in the night composite, while the silhouette stays
    crisp (2-3px halo)."""
    glow = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    for i, a in enumerate((30, 18, 10)):
        rx, ry = OUT_RX + i, OUT_RY + i
        rect = pygame.Rect(int(BCX - rx), int(BCY - ry), int(rx * 2), int(ry * 2))
        pygame.draw.ellipse(glow, (*RIM_GLOW, int(a * night_strength)), rect, 2)
    surf.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)


def _spin_crest(surf, ph):
    """The travelling spin tell: a NARROW white-hot crest segment riding the MID
    line of the ring body, with the rest of the rim left notably darker. The
    crest is a tight ~22° head stacked to a white-hot tip; it walks 12→3→6→9
    o'clock across the phases so a single hot arc appears to orbit the ring. A
    short dim wake trails it for direction — kept brief so the crest stays a
    distinct travelling segment, not a soft smear."""
    mid_rx = (OUT_RX + IN_RX) / 2 + 1
    mid_ry = (OUT_RY + IN_RY) / 2 + 1
    rect = pygame.Rect(int(BCX - mid_rx), int(BCY - mid_ry),
                       int(mid_rx * 2), int(mid_ry * 2))
    c = math.radians(_ARC_CENTER_DEG[ph])

    # short dim wake just BEHIND the crest → reads as direction of travel
    wake = tuple(int(HILITE[i] * 0.32 + RING_LIGHT[i] * 0.68) for i in range(3))
    wlo = c + math.radians(14)
    whi = wlo + math.radians(40)
    pygame.draw.arc(surf, wake, rect, wlo, whi, 3)

    # narrow bright head stacked to a white-hot tip
    head = math.radians(11)
    pygame.draw.arc(surf, HILITE, rect, c - head, c + head, 4)
    pygame.draw.arc(surf, HILITE_HOT, rect,
                    c - head * 0.40, c + head * 0.40, 3)


def _keyline_ring(surf, cx, cy, rx, ry, color, width=1):
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.ellipse(surf, color, rect, width)


def _rim_glint(surf, ph):
    """A tiny warm spark of life pinned to the SOLID upper inner rim (never the
    open gap). It tracks just inboard of the crest's clock position so the ring
    feels energised, but because it sits ON the ring body it can't refill the
    hole. Dropped almost to nothing — Pip's parcel owns the centre."""
    # ride the upper rim; offset slightly toward the crest for a 'sparking' feel
    ca = math.radians((_ARC_CENTER_DEG[ph] + 90) % 360)
    gx = int(BCX + (IN_RX + 2) * math.cos(ca) * 0.0 + 0)  # pin near top centre
    # keep it simply on the top-inner rim so it always lands on solid pixels
    gx = BCX - 3
    gy = BCY - IN_RY - 1
    pygame.draw.circle(surf, GLINT, (gx, gy), 1)


def _punch_hole_last(surf):
    """Zero the alpha of the OPEN HOLE as the FINAL step. A hard white mask with
    a black (zero-alpha) ellipse at the inner radius multiplies the surface,
    clearing the ENTIRE central gap to true transparency. Done last so neither
    the crest nor the getter's outline pass can refill it: the hole is GENUINELY
    transparent and sky / stars (and Pip's parcel) show through it in play. No
    centre disc is spared — the whole hole is open."""
    mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    # carve the open-sky hole with a HARD edge: draw a filled aa-ellipse of
    # zero alpha, then a 1px erosion ring so the multiply leaves a clean rim and
    # no feathered cyan survives just inside the keyline.
    _aaellipse(mask, (0, 0, 0, 0), (BCX, BCY), IN_RX, IN_RY)
    surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # second pass: hard-zero a 1px-smaller ellipse with draw.ellipse (no AA) so
    # the very edge pixels are unambiguously transparent before the outline grows
    hard = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    hard.fill((255, 255, 255, 255))
    rect = pygame.Rect(int(BCX - IN_RX + 1), int(BCY - IN_RY + 1),
                       int((IN_RX - 1) * 2), int((IN_RY - 1) * 2))
    pygame.draw.ellipse(hard, (0, 0, 0, 0), rect)
    surf.blit(hard, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)

    # 1. Flat-ish shaded ring body (no inner glow).
    _ring_body(surf)

    # 2. Restrained outer rim-glow + thin gloss (OUTWARD-only polish).
    _outer_rim_glow(surf)
    _gloss(surf)

    # 3. Travelling white-hot crest (the spin tell).
    _spin_crest(surf, ph)

    # 4. Crisp inner rim: dark keyline + lifted bevel (round read against the gap).
    _inner_rim(surf)

    # 5. Outer keyline so the donut holds on a bright DAY sky.
    _keyline_ring(surf, BCX, BCY, OUT_RX, OUT_RY, KEYLINE, 1)

    # 6. A tiny glint pinned to the solid rim (life without owning the centre).
    _rim_glint(surf, ph)

    # 7. Punch the open-sky hole LAST → the whole gap is truly see-through.
    _punch_hole_last(surf)

    return surf
