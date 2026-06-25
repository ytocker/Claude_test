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


# Beard greys are kept several values brighter than the scarlet head so the
# beard mass is the thing that reads as "old/bearded" at 40px — the whole
# concept dies if the beard fuses into the red head.
_BEARD    = (201, 203, 210)        # #C9CBD2 weathered grey
_BEARD_D  = (135, 138, 149)        # #878A95 braid shadow / parting lines
_BEARD_H  = (231, 233, 238)        # near-white highlight on the near braids

_SCARF    = (162, 48, 38)          # #A23026 deep-red headscarf
_SCARF_D  = (108, 28, 22)          # #6C1C16 knot / fold shadow
_SCARF_H  = (206, 92, 78)          # lifted scarf highlight

_PIPE_CLAY = (216, 195, 160)       # #D8C3A0 clay stem + bowl
_PIPE_CLAY_D = (160, 140, 108)
_PIPE_EMBER = (232, 120, 56)       # warm ember glow at the bowl
_SMOKE    = (224, 226, 232, 150)   # translucent smoke wisp

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
    #    side knot and two tails trailing OFF the back of the head into open sky
    #    so they break the silhouette as a motion cue, not body lines.
    bx, by = HX - 11, CROWN_Y + 6           # side-knot anchor, back-left of head
    for k, spread in ((0, 0), (1, 5)):
        t0 = (bx + 1, by + k * 2)
        t1 = (bx - 12, by + 3 + flick + spread)
        t2 = (bx - 22, by + 8 + flick * 2 + spread)
        pygame.draw.lines(surf, _SCARF_D, False, [t0, t1, t2], 4)
        pygame.draw.lines(surf, _SCARF, False, [t0, t1, t2], 3)
    pygame.draw.line(surf, _SCARF_H, (bx, by), (bx - 11, by + 3 + flick), 1)

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

    # ── DOUBLE stacked gold hoop earrings hanging off the near (right) cheek,
    #    set just OUTSIDE the beard mass so the gold rings stay visible against
    #    the scarlet head rather than disappearing into the grey braids.
    for r, ey in ((4, HY + 9), (3, HY + 15)):
        pygame.draw.circle(surf, _GOLD, (HX - 11, ey), r, 2)
        pygame.draw.circle(surf, _GOLD_H, (HX - 12, ey - 1), 1)

    # ── Braided grey beard MASS hanging under/around the beak. We frame UNDER
    #    the chin and let it flare wider than the head so the grey mass clearly
    #    breaks the lower silhouette; the beak (~61,41) stays clear so Pip can
    #    still chomp the pipe. Three braided tongues, each tipped with a gold
    #    bead ring, give the "old sea-dog" read.
    # Soft cheek-fuzz base behind the braids so the beard roots on the jaw,
    # hugging the lower face just under the beak base.
    cheek = [(HX - 5, HY + 3), (HX + 11, HY + 4),
             (HX + 9, HY + 10), (HX - 3, HY + 9)]
    _poly(surf, _BEARD_D, cheek)

    # Main beard fan: a compact grey mass dropping from the jaw. Kept tight and
    # UNDER the chin (roughly HY+4..HY+18) so it frames the face as a beard and
    # does NOT bleed down over the body/chest the way an oversized fan did.
    fan = [(HX - 6, HY + 4), (HX + 10, HY + 5),
           (HX + 10, HY + 12), (HX + 4, HY + 18),
           (HX - 2, HY + 18), (HX - 8, HY + 12)]
    _poly(surf, _BEARD, fan)
    # Parting lines carve the fan into braided tongues (shadow grey, ≥2px).
    pygame.draw.line(surf, _BEARD_D, (HX + 2, HY + 6), (HX + 1, HY + 17), 2)
    pygame.draw.line(surf, _BEARD_D, (HX + 7, HY + 6), (HX + 6, HY + 14), 2)
    # Near-side highlight braids catch light so the mass reads as plaited.
    pygame.draw.line(surf, _BEARD_H, (HX - 3, HY + 6), (HX - 3, HY + 15), 2)
    pygame.draw.line(surf, _BEARD_H, (HX + 4, HY + 6), (HX + 3, HY + 15), 1)

    # Three short braid tips poking below the main mass, each with a gold bead
    # ring — the tips break the lower outline and the gold beads are the accent.
    for tx, ty, blen in ((HX - 2, HY + 18, 4), (HX + 3, HY + 18, 4),
                         (HX + 7, HY + 15, 3)):
        pygame.draw.line(surf, _BEARD, (tx, ty - 3), (tx, ty + blen), 3)
        pygame.draw.line(surf, _BEARD_D, (tx + 1, ty - 3), (tx + 1, ty + blen), 1)
        # Gold bead ring partway down the braid.
        pygame.draw.circle(surf, _GOLD, (tx, ty + 1), 2)
        pygame.draw.circle(surf, _GOLD_H, (tx, ty), 1)

    # ── Short clay pipe gripped in the beak, the STEM poking clearly FORWARD
    #    past the beak tip so it breaks the front silhouette, then turning up to
    #    a small glowing bowl. Beak tip is ~(61,41); the stem roots just under it
    #    and runs right so it sits against the open sky, not buried in the head.
    stem_root = (59, HY + 2)
    stem_end = (stem_root[0] + 6, stem_root[1] - 4)
    pygame.draw.line(surf, _PIPE_CLAY_D, stem_root, stem_end, 4)
    pygame.draw.line(surf, _PIPE_CLAY,
                     (stem_root[0], stem_root[1] - 1),
                     (stem_end[0], stem_end[1] - 1), 2)
    # Bowl turns up at the forward end with a warm ember — pushed UP into clear
    # sky above-right of the beak so it clears the narrow right canvas edge.
    bowl = (stem_end[0] + 1, stem_end[1] - 6)
    pygame.draw.line(surf, _PIPE_CLAY_D, stem_end, bowl, 5)
    pygame.draw.line(surf, _PIPE_CLAY, (stem_end[0], stem_end[1] - 1),
                     (bowl[0], bowl[1] + 1), 3)
    pygame.draw.circle(surf, _PIPE_EMBER, (bowl[0], bowl[1] - 1), 2)
    pygame.draw.circle(surf, (255, 210, 120), (bowl[0], bowl[1] - 1), 1)

    # Smoke wisp: a taller translucent curl rising and drifting with the beat so
    # it breaks the silhouette up-forward. Drawn on a temp surface for alpha.
    sm = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    wisp = [(bowl[0], bowl[1] - 3),
            (bowl[0] + 4, bowl[1] - 9 + flick),
            (bowl[0] - 1, bowl[1] - 15 + flick),
            (bowl[0] + 4, bowl[1] - 21 + flick * 2)]
    pygame.draw.lines(sm, _SMOKE, False, wisp, 3)
    surf.blit(sm, (0, 0))

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


build = store_skins._make_skin(_paint)
