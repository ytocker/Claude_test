"""THE GRIDIRON — the American-football candidate (DESIGN 3 of the SPORTS set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so no live
skin is touched.

Concept: dress Pip as a helmeted gridiron player. The HERO is the football
HELMET — a rounded navy shell over the head + a CAGE FACEMASK wrapping the FRONT
of the face over the beak — the strongest, most armoured head silhouette of the
whole sports collection. A hint of Pip's eye shows above the cage so the bird
stays a parrot, not a mascot.

No football: the ball ships separately as a matching PARCEL item, so the costume
must read "American football" from the HELMET + kit alone. That works because
the cage facemask over the beak is the instant gridiron tell at any size.

The body is a bulky PADDED JERSEY: navy with a big white number, and the
shoulder pads are SUGGESTED by a raised, shaded shoulder SHAPE painted over the
existing silhouette — never extra width (the collision footprint is fixed).

At 40px the read, in order of value: (1) the rounded navy helmet shell with its
white crown stripe, (2) the dark cage facemask wrapping the beak (the instant
"American football" tell), (3) the navy padded jersey with a bold white number.
Helmet may rise above CROWN_Y; everything else stays inside the base footprint.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Team navy carries three values so the rounded shell still reads as a curved
# helmet (not a flat blob) after the 40px downscale; the jersey reuses the same
# family so helmet + jersey read as one kit.
_GR_NAVY    = (27, 42, 107)        # #1B2A6B team navy — helmet shell / jersey
_GR_NAVY_D  = (16, 26, 72)         # shadow / shell underside
_GR_NAVY_H  = (58, 80, 168)        # lit top of the shell + raised shoulder
_GR_MASK    = (236, 240, 248)      # bright facemask bars — highest-value face note
_GR_FRAME   = (10, 12, 22)         # near-black cage frame so the bars sit in dark gaps
_GR_WHITE   = (242, 242, 242)      # #F2F2F2 jersey number / stripe
_GR_BLACK   = (24, 24, 28)         # eye-black smudge


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── PADDED JERSEY over the torso. The SHOULDER PADS are SUGGESTED by a raised,
    #    lit navy shoulder yoke painted over the existing body — it adds value/shape,
    #    NOT width, so the collision footprint is untouched (footprint law). A darker
    #    underside seam below the yoke sells the pad bulk overhanging the chest.
    # Yoke spans the upper torso WITHIN the silhouette; the lit top edge reads as
    # the rounded pad cap catching light.
    yoke = [(BCX - 14, BCY - 6), (BCX - 7, BCY - 11), (BCX + 7, BCY - 11),
            (BCX + 15, BCY - 5), (BCX + 14, BCY + 1), (BCX - 13, BCY + 1)]
    _poly(surf, _GR_NAVY, yoke)
    # Lit cap along the top of each shoulder so the pads read as raised volume.
    pygame.draw.line(surf, _GR_NAVY_H, (BCX - 13, BCY - 5), (BCX - 7, BCY - 9), 2)
    pygame.draw.line(surf, _GR_NAVY_H, (BCX + 6, BCY - 9), (BCX + 14, BCY - 4), 2)
    # Dark seam under the pad line — the overhang shadow that gives the bulk depth.
    pygame.draw.line(surf, _GR_NAVY_D, (BCX - 12, BCY), (BCX + 13, BCY), 2)

    # Lower jersey body below the pads (navy) so the whole torso is one kit colour.
    jersey = [(BCX - 13, BCY + 1), (BCX + 14, BCY + 1), (BCX + 12, BCY + 12),
              (BCX - 11, BCY + 12)]
    _poly(surf, _GR_NAVY, jersey)
    pygame.draw.line(surf, _GR_NAVY_D, (BCX - 11, BCY + 11), (BCX + 12, BCY + 11), 1)
    # No white shoulder stripe: at 40px a bright bar on the shoulder reads as part of
    # the facemask. Keep the cage the ONLY high-value note up top so it wins the read.

    # ── BIG WHITE NUMBER on the chest. One CRISP "8" as two stacked loops drawn in
    #    bold 2px stroke with NO shadow ring, so at 40px it stays a single clean shape
    #    instead of a fuzzy doubled blob. Centred inside the lower jersey panel.
    nx, ny = BCX + 1, BCY + 6
    pygame.draw.circle(surf, _GR_WHITE, (nx, ny - 2), 3, 2)         # upper loop
    pygame.draw.circle(surf, _GR_WHITE, (nx, ny + 4), 4, 2)         # lower loop

    # ── HELMET — the HERO. A rounded navy SHELL domes over the head (rising above
    #    CROWN_Y, the only element allowed to), three-valued so the curve reads as a
    #    hard shell. The shell brow drops to a JAW that sweeps forward past the cheek
    #    to meet the cage, so the facemask reads as bolted to the shell, not floating.
    hcx, hcy = HX + 1, HY - 2
    # Shell mass: domed top + a jaw that sweeps DOWN-AND-FORWARD to the cheek so the
    # cage bolts onto solid shell (never hanging in open air). Shadow underlay first.
    shell = [(hcx - 12, hcy + 8), (hcx - 13, hcy - 3), (hcx - 8, hcy - 12),
             (hcx + 4, hcy - 14), (hcx + 13, hcy - 9), (hcx + 16, hcy - 2),
             (hcx + 15, hcy + 4), (hcx + 9, hcy + 9), (hcx + 1, hcy + 9),
             (hcx - 4, hcy + 12)]
    _poly(surf, _GR_NAVY_D, [(x, y + 1) for x, y in shell])
    _poly(surf, _GR_NAVY, shell)
    # Lit dome across the top so the shell reads as a curved hard surface.
    pygame.draw.line(surf, _GR_NAVY_H, (hcx - 8, hcy - 9), (hcx + 4, hcy - 11), 3)
    pygame.draw.line(surf, _GR_NAVY_H, (hcx + 4, hcy - 11), (hcx + 12, hcy - 6), 2)
    # White center stripe over the dome — the helmet's hero trim, crown to brow.
    pygame.draw.line(surf, _GR_WHITE, (hcx - 1, hcy - 14), (hcx, hcy - 2), 2)
    # Ear-hole — a navy/black dot where a real shell vents, so it reads as a helmet.
    pygame.draw.circle(surf, _GR_NAVY_D, (hcx - 6, hcy + 3), 3)
    pygame.draw.circle(surf, _GR_BLACK, (hcx - 6, hcy + 3), 1)

    # ── A hint of Pip behind the mask: the near eye showing UNDER the shell brow and
    #    ABOVE the cage, so the parrot stays legible and the player reads "athlete."
    #    Drawn BEFORE the cage so the lower bars read as passing in front of the face.
    ex, ey = hcx + 7, hcy + 1
    pygame.draw.circle(surf, _GR_WHITE, (ex, ey), 2)
    pygame.draw.circle(surf, (30, 26, 34), (ex + 1, ey), 1)

    # ── FACEMASK — a DARK-FRAMED CAGE wrapping the FRONT of the face OVER THE BEAK:
    #    the hero gridiron tell. It hangs from the shell jaw and reaches forward across
    #    the beak, so it reads as "a cage on the face," not a box beside the head.
    #    Read recipe at 40px: a solid near-black frame field (the cage shadow + the
    #    dark gaps that DEFINE a facemask) with TWO clearly-horizontal bright bars +
    #    ONE vertical post laid across it. Kept boldly horizontal so the bars never
    #    tangle into a hook at the downscale.
    # Cage field: a near-black trapezoid SEATED on the forward shell face, hung under
    # the brow and reaching forward across the beak. It stays INSIDE the shell jaw so
    # it never floats in open air. The beak pokes into the open lower gap → "cage on
    # the face." Slightly taller at the back (cheek) so it follows the face line.
    cheek_x, beak_x = hcx + 3, hcx + 15     # cage rides the shell face, over the beak
    top_y, bot_y = hcy + 2, hcy + 9
    field = [(cheek_x - 1, top_y - 1), (beak_x, top_y),
             (beak_x, bot_y - 1), (cheek_x - 1, bot_y)]
    pygame.draw.polygon(surf, _GR_FRAME, field)
    # TWO bright, clearly-horizontal bars spanning the full cage width with a dark gap
    # between — the unmistakable facemask read. Upper bar sits just under the eye; the
    # lower bar crosses the front of the beak.
    pygame.draw.line(surf, _GR_MASK, (cheek_x, top_y + 1), (beak_x - 1, top_y + 1), 2)
    pygame.draw.line(surf, _GR_MASK, (cheek_x, bot_y - 2), (beak_x - 1, bot_y - 2), 2)
    # ONE vertical post near the beak tip tying the bars; the dark field shows through
    # as the cage gaps either side of it.
    pygame.draw.line(surf, _GR_MASK, (beak_x - 2, top_y + 1), (beak_x - 2, bot_y - 1), 2)
    # A short back post at the cheek where the cage bolts to the shell — sells "attached
    # to the helmet," not floating.
    pygame.draw.line(surf, _GR_MASK, (cheek_x, top_y + 1), (cheek_x, bot_y - 1), 1)
    # EYE-BLACK smudge just under the showing eye — the athlete tell, kept off the cage.
    pygame.draw.line(surf, _GR_BLACK, (ex - 1, ey + 2), (ex + 2, ey + 2), 1)


build = store_skins._make_skin(_paint)
