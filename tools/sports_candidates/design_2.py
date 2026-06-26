"""THE BALLER — the basketball-player candidate (DESIGN 2 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: dress Pip as a pro hooper. There is NO ball — it ships separately as a
matching PARCEL item, so the costume has to read as BASKETBALL from the KIT
alone. The basketball tells are therefore carried entirely by the gear: a
clearly SLEEVELESS purple TANK singlet (bare shoulders + visible armhole curves
so it can't be mistaken for a t-shirt) with a big bold white NUMBER, a bold
brow HEADBAND hugging the crown with a purple knot, white WRISTBANDS banking the
near wing, and chunky high-top SNEAKERS on the feet line. Pip's scarlet macaw
head/beak/eye stay in the open so it still reads as a parrot wearing a kit.

At 40px the read, in order of value: (1) the sleeveless purple tank with its bare
shoulders + big white number (the singlet silhouette IS the "basketball" now the
ball is gone), (2) the white brow headband + purple knot, (3) the wristband, then
the high-tops. Every kit piece stays INSIDE the base bird footprint — nothing
dangles below the feet, the headband hugs the crown.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Bold flat team colours. The purple jersey is a mid-dark value so the white
# number + trim pop on it, and so it separates from both the scarlet head above
# and a bright day sky.
_BB_JERSEY   = (106, 45, 168)        # #6A2DA8 tank purple
_BB_JERSEY_D = (74, 28, 122)         # jersey shadow / side panel
_BB_JERSEY_H = (140, 80, 206)        # jersey highlight
_BB_TRIM     = (242, 242, 242)       # #F2F2F2 white number / trim
_BB_TRIM_D   = (196, 196, 204)       # number shadow so it reads on light sky
_BB_SHOE     = (242, 242, 242)       # white high-top
_BB_SHOE_D   = (188, 190, 198)       # shoe shadow / sole
_BB_SHOE_AC  = (106, 45, 168)        # purple shoe accent stripe


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── SLEEVELESS TANK / SINGLET painted over the torso. With the ball gone the
    #    singlet silhouette has to carry the basketball read, so the cut is made
    #    unmistakably sleeveless: a narrow body panel with DEEP armhole scoops on
    #    both sides that expose curved BARE SHOULDERS, plus thin shoulder straps —
    #    the classic basketball vest, never a t-shirt. Held inside the footprint
    #    (hem ~BCY+14) so the bird keeps its true size.
    jersey = [(BCX - 11, BCY - 6), (BCX + 10, BCY - 6),
              (BCX + 13, BCY + 2), (BCX + 12, BCY + 14),
              (BCX - 11, BCY + 14), (BCX - 13, BCY + 2)]
    _poly(surf, _BB_JERSEY, jersey)
    # Darker side panel down the off side so the tank has a dressed-up form.
    _poly(surf, _BB_JERSEY_D, [(BCX - 13, BCY + 1), (BCX - 9, BCY - 1),
                               (BCX - 8, BCY + 13), (BCX - 11, BCY + 14)])
    # Inner sheen down the near side.
    pygame.draw.line(surf, _BB_JERSEY_H, (BCX + 8, BCY - 4), (BCX + 10, BCY + 11), 2)

    # Thin shoulder STRAPS riding the wing roots — narrow enough that the bare
    # shoulder reads on the outside of each one (the sleeveless tell).
    _poly(surf, _BB_JERSEY, [(BCX - 11, BCY - 6), (BCX - 6, BCY - 9),
                             (BCX - 4, BCY - 5), (BCX - 8, BCY - 2)])   # off strap
    _poly(surf, _BB_JERSEY, [(BCX + 10, BCY - 6), (BCX + 5, BCY - 9),
                             (BCX + 3, BCY - 5), (BCX + 7, BCY - 2)])   # near strap
    # DEEP armhole scoops cut INTO the singlet on each side — a curved sliver of
    # the scarlet body shows in the gap between strap and side panel so the
    # bare-shouldered, sleeveless cut is explicit at 40px.
    pygame.draw.arc(surf, _BB_JERSEY_D, (BCX + 3, BCY - 7, 11, 14), -1.0, 1.4, 2)  # near armhole
    pygame.draw.arc(surf, _BB_JERSEY_D, (BCX - 14, BCY - 7, 11, 14), 1.7, 4.2, 2)  # off armhole
    # White trim piping along the scoop neckline + the hem so the kit reads sporty.
    pygame.draw.lines(surf, _BB_TRIM, False,
                      [(BCX - 5, BCY - 3), (BCX, BCY - 1), (BCX + 5, BCY - 3)], 1)
    pygame.draw.line(surf, _BB_TRIM, (BCX - 10, BCY + 13), (BCX + 11, BCY + 13), 1)

    # ── BIG WHITE NUMBER "8" across the chest — with the ball gone this is the
    #    jersey's headline tell, so it is re-centred on the singlet and enlarged
    #    to a crisp bold read: two stacked rounded loops, shadowed 1px down-left so
    #    it survives on a light day sky.
    nx, ny = BCX, BCY + 3
    pygame.draw.ellipse(surf, _BB_TRIM_D, (nx - 6, ny - 11, 12, 10))    # top loop shadow
    pygame.draw.ellipse(surf, _BB_TRIM_D, (nx - 6, ny - 2, 12, 12))     # bottom loop shadow
    pygame.draw.ellipse(surf, _BB_TRIM, (nx - 6, ny - 11, 11, 10))      # top loop
    pygame.draw.ellipse(surf, _BB_TRIM, (nx - 6, ny - 2, 11, 12))       # bottom loop
    pygame.draw.ellipse(surf, _BB_JERSEY, (nx - 3, ny - 8, 5, 4))       # punch top hole
    pygame.draw.ellipse(surf, _BB_JERSEY, (nx - 3, ny + 1, 5, 6))       # punch bottom hole

    # ── HIGH-TOP SNEAKERS on the feet line. Chunky white boots with a purple
    #    accent stripe + a grey sole, sitting ON the feet line (~HY+21..27), never
    #    below it, so the bird stays its true size.
    for fx in (26, 34):
        pygame.draw.rect(surf, _BB_SHOE_D, (fx - 4, HY + 22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, _BB_SHOE, (fx - 4, HY + 21, 9, 4), border_radius=2)
        pygame.draw.line(surf, _BB_SHOE_AC, (fx - 3, HY + 23), (fx + 4, HY + 23), 1)
        pygame.draw.line(surf, _BB_SHOE_D, (fx - 4, HY + 27), (fx + 5, HY + 27), 2)  # sole
        pygame.draw.line(surf, _BB_TRIM, (fx - 3, HY + 21), (fx + 1, HY + 21), 1)    # toe glint

    # ── WRISTBAND banking the near wing — now that the ball isn't covering this
    #    area it is the supporting basketball cue, so it's a bold white band with a
    #    thin purple midline, clearly a worn sweatband on the forearm.
    wrx, wry = BCX + 12, BCY + 8
    pygame.draw.line(surf, _BB_SHOE_D, (wrx - 3, wry + 4), (wrx + 5, wry - 2), 6)
    pygame.draw.line(surf, _BB_TRIM, (wrx - 3, wry + 4), (wrx + 5, wry - 2), 4)
    pygame.draw.line(surf, _BB_JERSEY, (wrx - 2, wry + 3), (wrx + 4, wry - 2), 1)

    # ── HEADBAND across the brow — the single most iconic non-ball basketball
    #    cue, so it is kept BOLD and hugging the crown: a thick white band anchored
    #    ~1px down onto the brow with a purple midline + a tiny purple KNOT and tail
    #    at the off-temple (the "tied on" tell). Leaves Pip's eye + beak in the open
    #    below it.
    by = CROWN_Y + 5
    pygame.draw.line(surf, _BB_SHOE_D, (HX - 12, by + 1), (HX + 13, by), 7)   # band shadow
    pygame.draw.line(surf, _BB_TRIM, (HX - 12, by), (HX + 13, by - 1), 5)
    pygame.draw.line(surf, _BB_JERSEY, (HX - 11, by), (HX + 12, by - 1), 2)   # purple midline
    pygame.draw.line(surf, _BB_TRIM, (HX - 10, by - 2), (HX + 5, by - 2), 1)  # top glint
    # Tiny purple knot + tail tied at the off-temple — the "worn band" tell.
    pygame.draw.circle(surf, _BB_JERSEY, (HX - 12, by), 3)
    pygame.draw.line(surf, _BB_JERSEY_D, (HX - 13, by + 2), (HX - 16, by + 5), 2)  # short tail


build = store_skins._make_skin(_paint)
