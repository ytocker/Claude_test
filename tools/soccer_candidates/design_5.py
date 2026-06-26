"""DESIGN 5 — THE ULTRA (Soccer / Football — supporter / fan).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a match-day terrace fan rather than a player: the SET's
only NON-player, the loudest break from the clean athletic kits. The read is
carried by KNITWEAR, not a kit — a chunky club SCARF looped at the neck with
two fringed tails streaming down the chest (drawn LAST, the hero), a bobble
BEANIE on the crown, a WHITE-hooped jersey on the torso, and a dab of cheek
face-paint. Club purple + gold.

Two-garment legibility is the whole job at 40px, so the jersey and the scarf
deliberately speak DIFFERENT stripe languages: the replica TOP is white hoops
on purple (a cheap club shirt), while the chunky SCARF is gold hoops on purple.
White-vs-gold is what splits the torso into two reads instead of one striped
mass. The two scarf tails are kept apart by a strip of bare scarlet chest and
staggered hard in length so they read as two streamers, not a bib.

The costume is painted OVER the scarlet body (head stays the macaw so Pip still
reads as a parrot). Everything is held INSIDE the base bird footprint: the
beanie sits on the crown, the scarf tails stop above the feet line, and nothing
balloons the torso — the knit silhouette alone says "fan", not "player".

Headless render: tools/soccer_candidates/render_design_5.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Club purple + gold, with a deep-purple knit value so the chunky scarf and the
# striped shirt still separate after the 40px downscale. Three values per
# material (knit, gold) keep the knitwear reading as round/woolly, not flat.
_ULT_PURP    = (122, 31, 162)       # #7A1FA2 club purple (jersey / scarf body)
_ULT_PURP_D  = (42, 19, 64)         # #2A1340 deep purple knit shadow / linework
_ULT_PURP_H  = (158, 78, 196)       # purple highlight (knit crowns / collar)
_ULT_GOLD    = (244, 194, 13)       # #F4C20D club gold (scarf stripes / band)
_ULT_GOLD_H  = (255, 226, 120)      # gold glint
_ULT_GOLD_D  = (120, 90, 10)        # crisp gold underline so it reads as kit
_ULT_WHITE   = (244, 244, 248)      # #F4F4F8 white (jersey hoops / pompom glint)
_ULT_WHITE_D = (170, 172, 188)      # cool white shade — undercut on jersey hoops
_ULT_CHEEK   = (232, 160, 180)      # #E8A0B4 cheek face-paint dab


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _fringe_zigzag(surf, color, x0, x1, y, depth, teeth):
    """A bold notched ZIGZAG silhouette along a tail end → the ragged frayed
    HEM of a knit scarf. Drawn as a filled triangle fan (2px-class teeth) so the
    jagged edge survives the 40px downscale where thin internal ticks vanish.
    Hand-stepped per candidate so each keeps its own fringe geometry."""
    span = max(1, x1 - x0)
    pts = [(x0, y)]
    for i in range(teeth):
        tx0 = x0 + round(span * i / teeth)
        tx1 = x0 + round(span * (i + 1) / teeth)
        mid = (tx0 + tx1) // 2
        pts.append((mid, y + depth))     # tooth tip dips below the hem
        pts.append((tx1, y))             # back up to the hem line
    pts.append((x1, y))
    _poly(surf, color, pts)


def _paint(surf, _a):
    # --- WHITE-hooped club JERSEY over the torso --------------------------------
    # The supporter's replica top: club purple filled, then bold WHITE horizontal
    # hoops (deliberately NOT gold — gold is reserved for the scarf, so the two
    # garments read as two distinct stripe palettes instead of one striped mass).
    # Kept inside the footprint (top ~BCY-12, hem ~BCY+11) so it never balloons.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 11),
              (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _ULT_PURP, jersey)

    # White hoops — 2px bands on a 5px pitch, with a cool-white undercut so the
    # bar reads as cloth, not a gap. Clipped to the jersey so they don't leak.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 16, BCY - 12, 32, 24))
    for sy in range(BCY - 6, BCY + 11, 5):
        pygame.draw.line(surf, _ULT_WHITE, (BCX - 16, sy), (BCX + 15, sy), 2)
        pygame.draw.line(surf, _ULT_WHITE_D, (BCX - 16, sy + 2), (BCX + 15, sy + 2), 1)
    surf.set_clip(clip_prev)
    pygame.draw.polygon(surf, _ULT_PURP_D, jersey, 1)

    # --- Cheek face-paint dab (a fan tell, off the macaw cheek) -----------------
    # A soft purple/pink diagonal swipe on the near cheek — supporter war-paint.
    # One value so it reads as paint on feather, not a mask.
    pygame.draw.line(surf, _ULT_CHEEK, (HX - 7, HY + 3), (HX - 1, HY + 6), 3)
    pygame.draw.line(surf, _ULT_GOLD, (HX - 6, HY + 1), (HX - 2, HY + 3), 1)

    # --- Bobble BEANIE on the crown (round, with a pompom) ----------------------
    # A knit cap pulled over the crown: a rounded purple dome, a folded ribbed
    # brim with a gold band, and a gold POMPOM bobble standing proud on top.
    cap_cx, cap_top = HX, CROWN_Y - 3
    # Dome — an ellipse capping the head. Deep-purple base, a MID-purple body, and
    # only a small lit cap near the crown: keeping the dome darker than the gold
    # band gives the band (and bobble) clear value separation so the hat doesn't
    # collapse into one gold blob.
    pygame.draw.ellipse(surf, _ULT_PURP_D, (cap_cx - 14, cap_top - 1, 28, 18))
    pygame.draw.ellipse(surf, _ULT_PURP, (cap_cx - 13, cap_top, 26, 16))
    pygame.draw.ellipse(surf, _ULT_PURP_H, (cap_cx - 9, cap_top + 1, 13, 6))
    # Vertical knit ribs across the dome so it reads chunky-knit, not smooth.
    for rx in range(cap_cx - 11, cap_cx + 12, 4):
        pygame.draw.line(surf, _ULT_PURP_D, (rx, cap_top + 2), (rx, cap_top + 11), 1)
    # Folded ribbed brim — a gold band hugging the head, the classic beanie cuff.
    pygame.draw.line(surf, _ULT_GOLD_D, (cap_cx - 14, cap_top + 12), (cap_cx + 14, cap_top + 12), 5)
    pygame.draw.line(surf, _ULT_GOLD, (cap_cx - 14, cap_top + 11), (cap_cx + 14, cap_top + 11), 3)
    pygame.draw.line(surf, _ULT_GOLD_H, (cap_cx - 11, cap_top + 10), (cap_cx + 2, cap_top + 10), 1)
    # POMPOM bobble — a bigger round ball lifted clear ABOVE the dome line with a
    # dark rim and a bright white glint, so the bobble pops as a distinct sphere
    # proud of the crown rather than blending into the gold band below.
    bob_x, bob_y = cap_cx, cap_top - 5
    pygame.draw.circle(surf, _ULT_PURP_D, (bob_x, bob_y), 6)   # dark rim halo
    pygame.draw.circle(surf, _ULT_GOLD_D, (bob_x, bob_y), 5)
    pygame.draw.circle(surf, _ULT_GOLD, (bob_x, bob_y), 4)
    pygame.draw.circle(surf, _ULT_WHITE, (bob_x - 1, bob_y - 2), 2)
    pygame.draw.circle(surf, _ULT_GOLD_H, (bob_x + 1, bob_y), 1)

    # --- Chunky knit SCARF looped at the neck (HERO — drawn LAST) ----------------
    # The signature. A thick scarf loops across the throat then drops two fringed
    # tails down the chest. GOLD hoops on purple (vs the jersey's white hoops)
    # make the scarf its own garment. A 2px deep-purple rim on the loop and both
    # tails reads the knit as chunky and keeps it separate from the shirt under
    # it. Tails stay within the footprint width and stop above the feet line.
    ny = BCY - 9
    # The neck loop — a fat band wrapping the throat, with a knot dip at centre
    # where the two tails leave from. Shadow underlay first for thickness.
    loop = [(BCX - 14, ny - 3), (BCX + 14, ny - 3), (BCX + 13, ny + 4),
            (BCX + 4, ny + 4), (BCX, ny + 7), (BCX - 4, ny + 4),
            (BCX - 13, ny + 4)]
    _poly(surf, _ULT_PURP_D, loop)
    loop_in = [(BCX - 12, ny - 1), (BCX + 12, ny - 1), (BCX + 11, ny + 3),
               (BCX + 3, ny + 3), (BCX, ny + 5), (BCX - 3, ny + 3),
               (BCX - 11, ny + 3)]
    _poly(surf, _ULT_PURP, loop_in)
    # Gold hoops across the loop so the scarf carries the gold language.
    for gx in (BCX - 9, BCX - 4, BCX + 4, BCX + 9):
        pygame.draw.line(surf, _ULT_GOLD, (gx, ny - 1), (gx, ny + 3), 2)
    pygame.draw.line(surf, _ULT_PURP_H, (BCX - 11, ny - 1), (BCX + 11, ny - 1), 1)
    pygame.draw.polygon(surf, _ULT_PURP_D, loop, 2)

    # Two fringed TAILS streaming down the chest, split by a wide strip of bare
    # scarlet chest so the negative space reads them as TWO streamers, not a bib.
    # Each tail is a gold-EDGED purple strap (a continuous 1px gold rim down both
    # sides + gold rungs) so it reads as the gold scarf laid OVER the white-hooped
    # shirt — gold edges vs white bars is the contrast that keeps the strap on top
    # of the jersey legible. The near (right) tail hangs much longer and drops its
    # fringe onto bare scarlet BELOW the jersey hem; the far (left) tail is short
    # and tucked, so the two are staggered hard. Drawn LAST → fully on top.
    def _tail(x0, x1, top, btm, lit_left):
        # A gold-rimmed purple knit strap with rungs and a zigzag-fringe hem.
        body = [(x0, top), (x1, top), (x1, btm), (x0, btm)]
        _poly(surf, _ULT_PURP_D, body)
        _poly(surf, _ULT_PURP, [(x0 + 1, top + 1), (x1 - 1, top + 1),
                                (x1 - 1, btm - 1), (x0 + 1, btm - 1)])
        # Continuous gold side-rails make the strap pop off the white-hooped shirt.
        pygame.draw.line(surf, _ULT_GOLD, (x0, top), (x0, btm), 1)
        pygame.draw.line(surf, _ULT_GOLD, (x1, top), (x1, btm), 1)
        # Gold knit rungs across the strap.
        for hy in range(top + 3, btm - 1, 4):
            pygame.draw.line(surf, _ULT_GOLD, (x0 + 1, hy), (x1 - 1, hy), 1)
        if lit_left:
            pygame.draw.line(surf, _ULT_PURP_H, (x0 + 2, top + 1), (x0 + 2, btm - 2), 1)
        # Bold zigzag fringe at the hem — survives the downscale as a ragged edge.
        _fringe_zigzag(surf, _ULT_GOLD, x0 - 1, x1 + 1, btm, 3, 3)
        _fringe_zigzag(surf, _ULT_PURP_D, x0 - 1, x1 + 1, btm + 1, 2, 3)

    # Near tail (right): long — its fringe lands at BCY+13, just past the hem, on
    # bare scarlet. Left edge BCX+4 with the far tail's right edge BCX-3 leaves a
    # ~7px bare-scarlet channel down the chest centre between the two streamers.
    _tail(BCX + 4, BCX + 9, ny + 5, BCY + 13, lit_left=True)
    # Far tail (left): short, tucked — fringe at BCY+4, well above the near hem.
    _tail(BCX - 9, BCX - 4, ny + 5, BCY + 4, lit_left=False)


build = store_skins._make_skin(_paint)
