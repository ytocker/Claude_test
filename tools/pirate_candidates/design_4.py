"""OLD SEA-DOG — the grizzled veteran pirate candidate for the redesign.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_pirate`` is untouched.

Concept (DESIGN 4): the buccaneer aged into a weathered old salt. We KEEP the
pirate identity — battered tricorn, gold brim, white skull cockade — but pack
the FACE with character the original head-only pirate never had: a grey braided
beard hanging under the beak with gold bead rings, a stubby clay pipe poking
forward off the beak with a curling smoke wisp, a deep-red headscarf knotted at
the side with two tails trailing behind, and DOUBLE stacked gold hoops.

The 40px read, in order of value: (1) a pirate silhouette broken by the tricorn
up off the crown, (2) the white skull + gold brim as the anchor pop, (3) a
clear grey beard MASS contrasting against the scarlet head so "old/bearded"
reads at thumbnail, (4) the scarf tails + pipe wisp breaking the outline so the
character reads as a grizzled veteran. Every object is mass + one bright accent
so the stack survives the brutal downscale.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Beard greys dropped to a CLEAR mid-grey (not near-white) so the beard reads as
# one rounded grey MASS distinct from the single brightest white on the figure —
# the skull. Keeping the beard near-white made beard+skull fuse into one pale
# column at 40px (the "bib" failure); a mid-grey mass + lone white skull fixes it.
_BEARD    = (169, 172, 182)        # #A9ACB6 weathered mid-grey main mass
_BEARD_D  = (120, 123, 134)        # #787B86 braid shadow / diagonal parting
_BEARD_H  = (231, 233, 238)        # #E7E9EE thin near-edge catch only, never a stripe

_SCARF    = (162, 48, 38)          # #A23026 deep-red headscarf
_SCARF_D  = (108, 28, 22)          # #6C1C16 knot / fold shadow
_SCARF_H  = (206, 92, 78)          # #CE5C4E lifted scarf highlight

# Pipe pushed to a DARK clay silhouette so the stem reads as a solid shape against
# the sky rather than a pale line that washes out at 40px; the ember is the only
# bit small enough to survive downscale, so it carries the whole "pipe" read.
_PIPE_CLAY = (92, 70, 52)          # dark clay stem silhouette against sky
_PIPE_CLAY_D = (58, 44, 32)        # darkest clay edge
_PIPE_EMBER = (232, 120, 56)       # #E87838 warm ember ring
_PIPE_CORE  = (255, 220, 130)      # #FFDC82 hot ember core
_SMOKE    = (210, 214, 224, 220)   # cool-grey smoke curl, high alpha to survive

# Reuse the original pirate's felt + gold so the tricorn matches the live look.
_FELT     = (74, 78, 96)
_FELT_D   = (48, 52, 70)
_FELT_H   = (120, 126, 150)
_GOLD     = (255, 205, 70)
_GOLD_H   = (255, 240, 160)
_SKULL    = (244, 246, 240)


def _paint(surf, wing_angle_deg):
    # The scarf tails + smoke wisp drift with the wing beat so the old salt
    # feels alive in motion; base wing angles run negative on the downbeat.
    flick = int(round(wing_angle_deg * 0.12))

    # ── Headscarf (drawn FIRST, under the tricorn) wrapping the crown, with a
    #    side knot and two tails trailing OFF the back of the head into open sky.
    #    These tails are the cheap, legible "old character" hero cue — pushed
    #    well PAST the back silhouette so they read as motion against open sky,
    #    not as body lines. Scarf is promoted to the signature over the beard.
    bx, by = HX - 11, CROWN_Y + 6           # side-knot anchor, back-left of head
    for k, spread in ((0, 0), (1, 6)):
        t0 = (bx + 1, by + k * 2)
        t1 = (bx - 15, by + 4 + flick + spread)
        t2 = (bx - 28, by + 9 + flick * 2 + spread)
        pygame.draw.lines(surf, _SCARF_D, False, [t0, t1, t2], 5)
        pygame.draw.lines(surf, _SCARF, False, [t0, t1, t2], 3)
        pygame.draw.lines(surf, _SCARF_H, False, [t0, t1, t2], 1)

    # Scarf band across the brow, wrapping the crown under where the hat sits.
    band = [(HX - 13, CROWN_Y + 9), (HX + 13, CROWN_Y + 7),
            (HX + 13, CROWN_Y + 3), (HX - 13, CROWN_Y + 5)]
    _poly(surf, _SCARF, band)
    pygame.draw.line(surf, _SCARF_H, (HX - 11, CROWN_Y + 5),
                     (HX + 11, CROWN_Y + 4), 1)
    pygame.draw.line(surf, _SCARF_D, (HX - 12, CROWN_Y + 8),
                     (HX + 12, CROWN_Y + 6), 1)
    # Side knot lump where the tails root.
    pygame.draw.circle(surf, _SCARF_D, (bx, by), 3)
    pygame.draw.circle(surf, _SCARF, (bx, by), 2)

    # ── Bold DOUBLE-hoop earring accent on the near (right) cheek, the two hoops
    #    ~5px apart and set OUTSIDE the beard mass so the gold reads against the
    #    scarlet cheek. A bright glint sells "metal" at thumbnail scale.
    ex = HX - 12
    for ey in (HY + 8, HY + 13):
        pygame.draw.circle(surf, _GOLD, (ex, ey), 4, 2)
        pygame.draw.circle(surf, (255, 240, 160), (ex - 1, ey - 1), 1)
    pygame.draw.circle(surf, (255, 240, 160), (ex - 1, HY + 7), 1)   # #FFF0A0 glint

    # ── Grey beard as a ROUNDED MASS (not a striped column). The top edge is a
    #    near-HORIZONTAL line anchored TIGHT under the beak base (~HY+3, spanning
    #    HX-5..HX+11) so the beard reads as a jaw, not a bib hung off the chest;
    #    it flares to max width around HY+7..9 and closes to a soft ROUNDED
    #    bottom by ~HY+12. No long vertical tips reach the tail — that braided
    #    column was what produced the barcode/bib look on downscale.
    # Shadow underbody first, offset down-right, so the mass has a rounded
    # lower edge rather than a hard polygon cut.
    _poly(surf, _BEARD_D, [
        (HX - 4, HY + 5), (HX + 11, HY + 6), (HX + 12, HY + 9),
        (HX + 8, HY + 13), (HX + 1, HY + 14), (HX - 6, HY + 11)])
    # Main rounded grey mass.
    mass = [(HX - 5, HY + 3), (HX + 2, HY + 2), (HX + 11, HY + 3),
            (HX + 12, HY + 7), (HX + 9, HY + 12), (HX + 2, HY + 13),
            (HX - 5, HY + 11), (HX - 7, HY + 7)]
    _poly(surf, _BEARD, mass)
    # Rounded chin caps soften the silhouette so it never reads as a flat block.
    pygame.draw.circle(surf, _BEARD, (HX + 2, HY + 11), 3)
    pygame.draw.circle(surf, _BEARD, (HX + 7, HY + 9), 3)

    # DIAGONAL parting lines RADIATING from the chin point — never vertical, so
    # they cannot align into stripes when the sprite is shrunk to 40px.
    chin = (HX + 3, HY + 12)
    for ex, ey in ((HX - 4, HY + 4), (HX + 1, HY + 3), (HX + 8, HY + 4)):
        pygame.draw.line(surf, _BEARD_D, chin, (ex, ey), 2)
    # ONE thin near-edge highlight catch along the near jaw — 1px, never a
    # full-height stripe; the skull stays the single brightest white.
    pygame.draw.line(surf, _BEARD_H, (HX - 6, HY + 6), (HX - 3, HY + 10), 1)

    # Two gold bead rings tucked at the rounded bottom edge as accents (no long
    # braids dangling) — they punctuate the mass without breaking the round shape.
    for tx, ty in ((HX + 1, HY + 13), (HX + 6, HY + 11)):
        pygame.draw.circle(surf, _GOLD, (tx, ty), 2)
        pygame.draw.circle(surf, _GOLD_H, (tx, ty - 1), 1)

    # ── Battered tricorn worn on TOP of the scarf, lifted off the crown so the
    #    brim breaks the outline (same felt + gold + skull as the live pirate,
    #    kept as the anchor read). A couple of dents/nicks read it as "battered".
    cy = CROWN_Y - 3
    brim = [(HX - 17, cy + 5), (HX - 5, cy - 7), (HX + 4, cy - 8),
            (HX + 16, cy + 4), (HX + 6, cy + 9), (HX - 6, cy + 9)]
    _poly(surf, _FELT_D, brim)
    inner = [(HX - 14, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
             (HX + 13, cy + 3), (HX + 5, cy + 7), (HX - 5, cy + 7)]
    _poly(surf, _FELT, inner)
    # Battered dent — a darker notch chewed out of the crown peak.
    _poly(surf, _FELT_D, [(HX - 2, cy - 6), (HX + 1, cy - 6),
                          (HX, cy - 3), (HX - 2, cy - 3)])
    _poly(surf, _FELT_H, [(HX - 4, cy - 5), (HX - 2, cy - 6),
                          (HX - 2, cy - 2), (HX - 4, cy - 2)])
    # Continuous bright gold brim band — the strongest non-skull read.
    bandpts = [(HX - 15, cy + 4), (HX - 4, cy - 5), (HX + 3, cy - 6),
               (HX + 14, cy + 3)]
    pygame.draw.lines(surf, _GOLD, False, bandpts, 2)
    pygame.draw.lines(surf, _GOLD_H, False,
                      [(HX - 13, cy + 3), (HX - 4, cy - 6), (HX + 3, cy - 7)], 1)

    # ── White skull cockade dead-centre-front — the pirate anchor pop.
    sx, sy = HX, cy + 1
    pygame.draw.circle(surf, _SKULL, (sx, sy), 4)
    _poly(surf, _SKULL, [(sx - 3, sy + 2), (sx + 3, sy + 2),
                         (sx + 1, sy + 5), (sx - 1, sy + 5)])
    pygame.draw.circle(surf, (40, 30, 40), (sx - 2, sy - 1), 1)
    pygame.draw.circle(surf, (40, 30, 40), (sx + 2, sy - 1), 1)

    # ── Short clay pipe gripped in the beak, drawn LAST so nothing covers it.
    #    The bowl is pulled IN to ~x58 so it sits FULLY on the 64px canvas (it was
    #    clipping the edge before). The stem is a thick DARK clay silhouette so it
    #    survives against the sky; the bowl carries a 2px ember + hot core, the one
    #    detail small + bright enough to read "pipe" at 40px.
    stem_root = (HX + 12, HY + 1)               # at the beak base, well on-canvas
    bowl = (58, HY + 6)                          # bowl mouth, fully in bounds
    pygame.draw.line(surf, _PIPE_CLAY_D, stem_root, (bowl[0], bowl[1] - 1), 5)
    pygame.draw.line(surf, _PIPE_CLAY, stem_root, (bowl[0], bowl[1] - 1), 3)
    # Bowl cup rising off the stem end.
    pygame.draw.line(surf, _PIPE_CLAY_D, (bowl[0], bowl[1]),
                     (bowl[0] - 1, bowl[1] - 5), 5)
    pygame.draw.line(surf, _PIPE_CLAY, (bowl[0], bowl[1]),
                     (bowl[0] - 1, bowl[1] - 5), 3)
    # Ember at the bowl mouth — 2px glow + a 1px hot core, the survivor accent.
    pygame.draw.circle(surf, _PIPE_EMBER, (bowl[0] - 1, bowl[1] - 5), 2)
    pygame.draw.circle(surf, _PIPE_CORE, (bowl[0] - 1, bowl[1] - 5), 1)

    # Smoke: a high-alpha cool-grey curl clearing the crown into OPEN SKY, drifting
    # with the beat so it reads as motion and breaks the upper outline.
    sm = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    wisp = [(bowl[0] - 1, bowl[1] - 7),
            (bowl[0] - 4, bowl[1] - 12 + flick),
            (bowl[0], bowl[1] - 17 + flick),
            (bowl[0] - 5, bowl[1] - 22 + flick * 2)]
    pygame.draw.lines(sm, _SMOKE, False, wisp, 2)
    surf.blit(sm, (0, 0))


build = store_skins._make_skin(_paint)
