"""DESIGN 5 — THE ULTRA (Soccer / Football — supporter / fan).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a match-day terrace fan rather than a player: the SET's
only NON-player, the loudest break from the clean athletic kits. The read is
carried by KNITWEAR, not a kit — a chunky club SCARF looped at the neck with
two fringed tails streaming down the chest (drawn LAST, the hero), a bobble
BEANIE on the crown, a horizontal-striped jersey on the torso, and a dab of
cheek face-paint. Club purple + gold.

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
_ULT_GOLD    = (244, 194, 13)       # #F4C20D club gold (stripes / pompom / band)
_ULT_GOLD_H  = (255, 226, 120)      # gold glint
_ULT_GOLD_D  = (120, 90, 10)        # crisp gold underline so it reads as kit
_ULT_WHITE   = (244, 244, 248)      # #F4F4F8 white (jersey stripe / sparkle)
_ULT_CHEEK   = (232, 160, 180)      # #E8A0B4 cheek face-paint dab


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _knit_ticks(surf, color, x0, y0, x1, y1, n, length):
    """Short ticks fanned along a tail end → the frayed FRINGE of a knit scarf.
    Hand-stepped (not a loop helper elsewhere) so each candidate keeps its own
    fringe geometry; the ticks must survive the downscale as a ragged edge."""
    for i in range(n):
        t = i / max(1, n - 1)
        bx = round(x0 + (x1 - x0) * t)
        by = round(y0 + (y1 - y0) * t)
        pygame.draw.line(surf, color, (bx, by), (bx, by + length), 1)


def _paint(surf, _a):
    # --- Horizontal-striped club JERSEY over the torso --------------------------
    # A jersey block clipped to the chest, filled club purple, then bold gold
    # HORIZONTAL hoops (this is the supporter's replica top — hooped, not the
    # vertical player stripe). Kept inside the footprint (top ~BCY-12, hem
    # ~BCY+11) so it never balloons the bird.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 11),
              (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _ULT_PURP, jersey)

    # Gold hoops — 2px bands on a 5px pitch so they survive the downscale as
    # distinct bars. Clipped to the jersey so they don't leak past the cloth.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 16, BCY - 12, 32, 24))
    for sy in range(BCY - 6, BCY + 11, 5):
        pygame.draw.line(surf, _ULT_GOLD, (BCX - 16, sy), (BCX + 15, sy), 2)
        pygame.draw.line(surf, _ULT_PURP_D, (BCX - 16, sy + 2), (BCX + 15, sy + 2), 1)
    surf.set_clip(clip_prev)
    pygame.draw.polygon(surf, _ULT_PURP_D, jersey, 1)

    # --- Cheek face-paint dab (a fan tell, off the macaw cheek) -----------------
    # A soft purple/pink diagonal swipe on the near cheek — supporter war-paint.
    # One value so it reads as paint on feather, not a mask.
    pygame.draw.line(surf, _ULT_CHEEK, (HX - 7, HY + 3), (HX - 1, HY + 6), 3)
    pygame.draw.line(surf, _ULT_GOLD, (HX - 6, HY + 1), (HX - 2, HY + 3), 1)

    # --- Bobble BEANIE on the crown (round, with a pompom) ----------------------
    # A knit cap pulled over the crown: a rounded purple dome, a folded ribbed
    # brim with a gold band, and a gold POMPOM bobble on top. Round dome + bobble
    # is the knitwear tell that pairs with the scarf for "fan".
    cap_cx, cap_top = HX, CROWN_Y - 3
    # Dome — an ellipse capping the head; deep-purple base then a lit crown so it
    # reads spherical, not a flat plate.
    pygame.draw.ellipse(surf, _ULT_PURP_D, (cap_cx - 14, cap_top - 1, 28, 18))
    pygame.draw.ellipse(surf, _ULT_PURP, (cap_cx - 13, cap_top, 26, 16))
    pygame.draw.ellipse(surf, _ULT_PURP_H, (cap_cx - 10, cap_top + 1, 16, 8))
    # Vertical knit ribs across the dome so it reads chunky-knit, not smooth.
    for rx in range(cap_cx - 11, cap_cx + 12, 4):
        pygame.draw.line(surf, _ULT_PURP_D, (rx, cap_top + 2), (rx, cap_top + 11), 1)
    # Folded ribbed brim — a gold band hugging the head, the classic beanie cuff.
    pygame.draw.line(surf, _ULT_GOLD_D, (cap_cx - 14, cap_top + 12), (cap_cx + 14, cap_top + 12), 5)
    pygame.draw.line(surf, _ULT_GOLD, (cap_cx - 14, cap_top + 11), (cap_cx + 14, cap_top + 11), 3)
    pygame.draw.line(surf, _ULT_GOLD_H, (cap_cx - 11, cap_top + 10), (cap_cx + 2, cap_top + 10), 1)
    # POMPOM bobble — a round gold ball on the crown with a white glint so it
    # reads spherical and pushes proud of the head silhouette.
    bob_x, bob_y = cap_cx, cap_top - 3
    pygame.draw.circle(surf, _ULT_GOLD_D, (bob_x, bob_y), 5)
    pygame.draw.circle(surf, _ULT_GOLD, (bob_x, bob_y), 4)
    pygame.draw.circle(surf, _ULT_GOLD_H, (bob_x - 1, bob_y - 1), 2)
    pygame.draw.circle(surf, _ULT_WHITE, (bob_x - 1, bob_y - 2), 1)

    # --- Chunky knit SCARF looped at the neck (HERO — drawn LAST) ----------------
    # The signature. A thick scarf loops across the throat then drops two fringed
    # tails down the chest. Two purple values + gold hoops read it as chunky
    # knit; the tails may break the lower silhouette but stay within the
    # footprint width and stop above the feet line (~BCY+11), so the bird keeps
    # its true size.
    ny = BCY - 9
    # The neck loop — a fat band wrapping the throat, with a knot dip at centre
    # where the two tails leave from. Shadow underlay first for thickness.
    loop = [(BCX - 14, ny - 3), (BCX + 14, ny - 3), (BCX + 13, ny + 4),
            (BCX + 4, ny + 4), (BCX, ny + 7), (BCX - 4, ny + 4),
            (BCX - 13, ny + 4)]
    _poly(surf, _ULT_PURP_D, loop)
    loop_in = [(BCX - 13, ny - 2), (BCX + 13, ny - 2), (BCX + 12, ny + 3),
               (BCX + 3, ny + 3), (BCX, ny + 6), (BCX - 3, ny + 3),
               (BCX - 12, ny + 3)]
    _poly(surf, _ULT_PURP, loop_in)
    # Gold hoops across the loop so the scarf matches the club hoops.
    for gx in (BCX - 9, BCX - 4, BCX + 4, BCX + 9):
        pygame.draw.line(surf, _ULT_GOLD, (gx, ny - 2), (gx, ny + 3), 2)
    pygame.draw.line(surf, _ULT_PURP_H, (BCX - 12, ny - 2), (BCX + 12, ny - 2), 1)

    # Two fringed TAILS streaming down the chest. Each tail = a deep-purple
    # shadow plank, a lit purple face, gold knit hoops, then a frayed fringe of
    # ticks at the bottom. The near (right) tail hangs longer/forward; the far
    # (left) tail is shorter, so they read as two separate streamers, not a bib.
    # Near tail (right) — longer, forward.
    nt = [(BCX + 1, ny + 5), (BCX + 7, ny + 5), (BCX + 8, BCY + 9),
          (BCX + 2, BCY + 9)]
    _poly(surf, _ULT_PURP_D, nt)
    nt_in = [(BCX + 2, ny + 6), (BCX + 6, ny + 6), (BCX + 7, BCY + 8),
             (BCX + 3, BCY + 8)]
    _poly(surf, _ULT_PURP, nt_in)
    for hy in range(ny + 9, BCY + 8, 4):
        pygame.draw.line(surf, _ULT_GOLD, (BCX + 2, hy), (BCX + 7, hy), 2)
    pygame.draw.line(surf, _ULT_PURP_H, (BCX + 3, ny + 6), (BCX + 3, BCY + 6), 1)
    _knit_ticks(surf, _ULT_GOLD, BCX + 2, BCY + 9, BCX + 7, BCY + 9, 4, 2)
    _knit_ticks(surf, _ULT_PURP_D, BCX + 3, BCY + 10, BCX + 6, BCY + 10, 3, 2)

    # Far tail (left) — shorter, slightly behind the near one.
    ft = [(BCX - 8, ny + 5), (BCX - 3, ny + 5), (BCX - 3, BCY + 3),
          (BCX - 9, BCY + 3)]
    _poly(surf, _ULT_PURP_D, ft)
    ft_in = [(BCX - 7, ny + 6), (BCX - 4, ny + 6), (BCX - 4, BCY + 2),
             (BCX - 8, BCY + 2)]
    _poly(surf, _ULT_PURP, ft_in)
    for hy in range(ny + 9, BCY + 2, 4):
        pygame.draw.line(surf, _ULT_GOLD, (BCX - 8, hy), (BCX - 4, hy), 2)
    pygame.draw.line(surf, _ULT_PURP_H, (BCX - 7, ny + 6), (BCX - 7, BCY), 1)
    _knit_ticks(surf, _ULT_GOLD, BCX - 8, BCY + 3, BCX - 4, BCY + 3, 4, 2)
    _knit_ticks(surf, _ULT_PURP_D, BCX - 7, BCY + 4, BCX - 5, BCY + 4, 2, 2)


build = store_skins._make_skin(_paint)
