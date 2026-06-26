"""THE BALLER — the basketball-player candidate (DESIGN 2 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched.

Concept: dress Pip as a pro hooper. The hero silhouette-break is the orange
BASKETBALL held high at the near wing/chest — a clean round disc with dark seam
lines, the single most legible sport-prop, so the SPORT reads before the bird
does. The torso wears a sleeveless PURPLE tank jersey (bold flat colour + a big
white number) painted over the scarlet, a white HEADBAND crosses the brow, a
wristband banks the near wing, and chunky high-top SNEAKERS sit on the feet
line. Pip's scarlet macaw head/beak/eye stay in the open so it still reads as a
parrot wearing a kit.

At 40px the read, in order of value: (1) the orange seamed ball held low on the
near side over the purple jersey (the instant "basketball" — the largest single
shape, kept OFF the orange beak/wing so it never dissolves), (2) the sleeveless
purple tank, (3) the white brow headband, then the number + wristband +
high-tops. Every kit piece stays INSIDE the base bird footprint — the ball only
breaks the lower-near silhouette slightly, the headband hugs the crown, nothing
dangles below the feet.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Bold flat team colours. The purple jersey is a mid-dark value so the white
# number + trim pop on it, and so it separates from both the scarlet head above
# and a bright day sky; the ball orange is the saturated hero, dark-seamed so
# the round prop reads as a basketball and not just an orange dot.
_BB_JERSEY   = (106, 45, 168)        # #6A2DA8 tank purple
_BB_JERSEY_D = (74, 28, 122)         # jersey shadow / side panel
_BB_JERSEY_H = (140, 80, 206)        # jersey highlight
_BB_TRIM     = (242, 242, 242)       # #F2F2F2 white number / trim
_BB_TRIM_D   = (196, 196, 204)       # number shadow so it reads on light sky
_BB_BALL     = (232, 118, 30)        # #E8761E ball orange
_BB_BALL_D   = (190, 92, 22)         # ball shaded lower half
_BB_BALL_H   = (255, 168, 86)        # ball top highlight (the round read)
_BB_SEAM     = (92, 40, 12)          # deep red-brown seam — darker than the old
                                     # #7A3A12 so it holds against orange at 40px,
                                     # but not so black it merges with the shaded base
_BB_SHOE     = (242, 242, 242)       # white high-top
_BB_SHOE_D   = (188, 190, 198)       # shoe shadow / sole
_BB_SHOE_AC  = (106, 45, 168)        # purple shoe accent stripe


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── SLEEVELESS TANK JERSEY painted over the torso. A flat purple panel with a
    #    darker side seam + a lighter inner sheen so the cloth has form, then two
    #    shoulder STRAPS up toward the wing roots so the "sleeveless tank" reads
    #    rather than a full shirt. Held INSIDE the base footprint (hem ~HY+22) so
    #    the bird keeps its true size.
    jersey = [(BCX - 14, BCY - 7), (BCX + 13, BCY - 8), (BCX + 15, BCY + 2),
              (BCX + 13, BCY + 14), (BCX - 12, BCY + 14), (BCX - 15, BCY + 2)]
    _poly(surf, _BB_JERSEY, jersey)
    # Darker side panel down the off side so the tank has a dressed-up form.
    _poly(surf, _BB_JERSEY_D, [(BCX - 15, BCY + 1), (BCX - 11, BCY - 1),
                               (BCX - 9, BCY + 13), (BCX - 12, BCY + 14)])
    # Inner sheen down the near side.
    pygame.draw.line(surf, _BB_JERSEY_H, (BCX + 9, BCY - 5), (BCX + 11, BCY + 10), 2)
    # The deep scoop neck + the two shoulder straps (sleeveless cut) — the scarlet
    # chest shows through the scoop so the tank reads as a vest, not a full shirt.
    _poly(surf, _BB_JERSEY, [(BCX - 13, BCY - 7), (BCX - 7, BCY - 9),
                             (BCX - 6, BCY - 3), (BCX - 11, BCY - 2)])   # off strap
    _poly(surf, _BB_JERSEY, [(BCX + 12, BCY - 8), (BCX + 6, BCY - 10),
                             (BCX + 5, BCY - 4), (BCX + 10, BCY - 3)])   # near strap
    pygame.draw.line(surf, _BB_JERSEY_H, (BCX + 11, BCY - 9), (BCX + 6, BCY - 9), 1)
    # White trim piping along the scoop neckline + the hem so the kit reads sporty.
    pygame.draw.lines(surf, _BB_TRIM, False,
                      [(BCX - 6, BCY - 3), (BCX - 1, BCY - 1), (BCX + 5, BCY - 3)], 1)
    pygame.draw.line(surf, _BB_TRIM, (BCX - 11, BCY + 13), (BCX + 12, BCY + 13), 1)

    # ── WHITE NUMBER across the chest — the "jersey" tell, dialled back so the
    #    relocated ball owns the focal near-side. ~18% smaller and shifted off-near
    #    (toward the off shoulder); two stacked rounded boxes, shadowed 1px
    #    down-left so it survives on a light day sky. Read order is now ball → tank
    #    → headband → number.
    nx, ny = BCX - 7, BCY + 2
    pygame.draw.ellipse(surf, _BB_TRIM_D, (nx - 4, ny - 8, 8, 7))       # top loop shadow
    pygame.draw.ellipse(surf, _BB_TRIM_D, (nx - 4, ny - 2, 8, 9))       # bottom loop shadow
    pygame.draw.ellipse(surf, _BB_TRIM, (nx - 4, ny - 8, 7, 7))
    pygame.draw.ellipse(surf, _BB_TRIM, (nx - 4, ny - 2, 7, 8))
    pygame.draw.ellipse(surf, _BB_JERSEY, (nx - 2, ny - 6, 4, 3))       # punch the top hole
    pygame.draw.ellipse(surf, _BB_JERSEY, (nx - 2, ny, 4, 5))           # punch the bottom hole

    # ── HIGH-TOP SNEAKERS on the feet line. Chunky white boots with a purple
    #    accent stripe + a grey sole, sitting ON the feet line (~HY+24..27), never
    #    below it, so the bird stays its true size.
    for fx in (26, 34):
        pygame.draw.rect(surf, _BB_SHOE_D, (fx - 4, HY + 22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, _BB_SHOE, (fx - 4, HY + 21, 9, 4), border_radius=2)
        pygame.draw.line(surf, _BB_SHOE_AC, (fx - 3, HY + 23), (fx + 4, HY + 23), 1)
        pygame.draw.line(surf, _BB_SHOE_D, (fx - 4, HY + 27), (fx + 5, HY + 27), 2)  # sole
        pygame.draw.line(surf, _BB_TRIM, (fx - 3, HY + 21), (fx + 1, HY + 21), 1)    # toe glint

    # ── WRISTBAND banking the near wing — a short white band with a thin purple
    #    midline so the hooper's forearm reads kitted, not bare plumage.
    wrx, wry = BCX + 11, BCY + 8
    pygame.draw.line(surf, _BB_SHOE_D, (wrx - 3, wry + 3), (wrx + 4, wry - 1), 5)
    pygame.draw.line(surf, _BB_TRIM, (wrx - 3, wry + 3), (wrx + 4, wry - 1), 3)
    pygame.draw.line(surf, _BB_JERSEY, (wrx - 2, wry + 2), (wrx + 3, wry - 1), 1)

    # ── BASKETBALL held at the chest/hip on the LOW NEAR side — the HERO, and the
    #    LARGEST single shape in the kit. Pulled OFF the orange beak/wing (where it
    #    used to dissolve, orange-on-orange) down onto the mid-dark PURPLE jersey,
    #    where saturated orange pops hardest. It breaks the lower-near silhouette
    #    slightly so the prop reads as held in front of the body. r=11 makes it
    #    bigger than the white "8".
    cx, cy, r = BCX + 8, BCY + 6, 11
    pygame.draw.circle(surf, _BB_BALL_D, (cx, cy + 2), r)              # thin shaded crescent base
    pygame.draw.circle(surf, _BB_BALL, (cx, cy), r)                    # orange body owns the disc
    # Small top-left highlight so the ball reads round WITHOUT eating seam area.
    pygame.draw.circle(surf, _BB_BALL_H, (cx - 3, cy - 4), 3)
    pygame.draw.circle(surf, _BB_BALL, (cx - 2, cy - 3), 2)            # soften the highlight edge
    # THREE iconic seams: one vertical spine + two opposing curved side-arcs (no
    # centred horizontal), 2px in a deep red-brown — bold enough to survive on the
    # orange at 40px, thin enough that the orange body still dominates so the prop
    # reads as a basketball (not a beach ball, not a dark blob).
    pygame.draw.line(surf, _BB_SEAM, (cx, cy - r + 1), (cx, cy + r - 1), 2)
    pygame.draw.arc(surf, _BB_SEAM, (cx - r - 4, cy - r, r + 4, 2 * r), -1.15, 1.15, 2)
    pygame.draw.arc(surf, _BB_SEAM, (cx, cy - r, r + 4, 2 * r), 2.0, 4.3, 2)

    # ── HEADBAND across the brow — anchored ~1px DOWN onto the brow so it reads as
    #    "worn" hugging the crown (rather than a band floating above the head), with
    #    a thin purple midline + a tiny purple KNOT at the off-temple. Leaves Pip's
    #    eye + beak in the open below it.
    by = CROWN_Y + 5
    pygame.draw.line(surf, _BB_SHOE_D, (HX - 12, by + 1), (HX + 13, by), 6)   # band shadow
    pygame.draw.line(surf, _BB_TRIM, (HX - 12, by), (HX + 13, by - 1), 4)
    pygame.draw.line(surf, _BB_JERSEY, (HX - 11, by), (HX + 12, by - 1), 1)   # purple midline
    pygame.draw.line(surf, _BB_TRIM, (HX - 10, by - 2), (HX + 4, by - 2), 1)  # top glint
    # Tiny purple knot tied at the off-temple — the "worn band" tell.
    pygame.draw.circle(surf, _BB_JERSEY, (HX - 12, by), 2)
    pygame.draw.line(surf, _BB_JERSEY_D, (HX - 13, by + 2), (HX - 15, by + 4), 2)  # short tail


build = store_skins._make_skin(_paint)
