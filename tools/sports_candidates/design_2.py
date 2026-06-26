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

At 40px the read, in order of value: (1) the orange ball (the instant
"basketball"), (2) the sleeveless tank with the white number, (3) the white
brow headband, then (4) the wristband + high-tops. Every kit piece stays INSIDE
the base bird footprint — the ball is tucked at the chest, the headband only
touches the crown, nothing dangles below the feet.
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
_BB_SEAM     = (122, 58, 18)         # #7A3A12 dark seam lines
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

    # ── BIG WHITE NUMBER across the chest — the "jersey" tell. A bold blocky "8"
    #    drawn as two stacked rounded boxes, shadowed 1px down-left so it survives
    #    on a light day sky, kept off the near side where the ball sits.
    nx, ny = BCX - 4, BCY + 3
    pygame.draw.ellipse(surf, _BB_TRIM_D, (nx - 5, ny - 9, 10, 9))      # top loop shadow
    pygame.draw.ellipse(surf, _BB_TRIM_D, (nx - 5, ny - 2, 10, 11))     # bottom loop shadow
    pygame.draw.ellipse(surf, _BB_TRIM, (nx - 4, ny - 9, 9, 8))
    pygame.draw.ellipse(surf, _BB_TRIM, (nx - 4, ny - 2, 9, 10))
    pygame.draw.ellipse(surf, _BB_JERSEY, (nx - 2, ny - 7, 5, 4))       # punch the top hole
    pygame.draw.ellipse(surf, _BB_JERSEY, (nx - 2, ny, 5, 6))           # punch the bottom hole

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

    # ── BASKETBALL held high at the near wing/chest — the HERO. A clean round
    #    orange disc: a shaded lower half + a bright top highlight give it volume
    #    so it reads as a sphere (not a flat dot), and four dark seam lines (the
    #    vertical, the horizontal, plus the two curved side seams) make it
    #    unmistakably a basketball at 40px. Tucked at the chest so it stays inside
    #    the silhouette and overlaps the body rather than ballooning it.
    cx, cy, r = BCX + 16, BCY - 1, 9
    pygame.draw.circle(surf, _BB_BALL_D, (cx, cy + 1), r)              # shaded sphere base
    pygame.draw.circle(surf, _BB_BALL, (cx, cy), r)                    # body
    # Top-left highlight crescent — the single brightest note that rounds the ball.
    pygame.draw.circle(surf, _BB_BALL_H, (cx - 2, cy - 3), r - 4)
    pygame.draw.circle(surf, _BB_BALL, (cx, cy - 1), r - 3)            # blend the highlight in
    # Seam lines: vertical + horizontal through the centre, then the two curved
    # side seams that read as basketball-specific (not a beach ball).
    pygame.draw.line(surf, _BB_SEAM, (cx, cy - r + 1), (cx, cy + r - 1), 2)
    pygame.draw.line(surf, _BB_SEAM, (cx - r + 1, cy), (cx + r - 1, cy), 2)
    pygame.draw.arc(surf, _BB_SEAM, (cx - r - 3, cy - r, r + 3, 2 * r), -1.2, 1.2, 2)
    pygame.draw.arc(surf, _BB_SEAM, (cx, cy - r, r + 3, 2 * r), 2.0, 4.3, 2)
    pygame.draw.circle(surf, _BB_BALL_H, (cx - 3, cy - 4), 1)         # speck glint

    # ── HEADBAND across the brow — a white band over the scarlet head, dropped to
    #    sit just under the crown (may touch CROWN_Y) with a thin purple midline so
    #    it reads as a sweatband, not a bare line. The hero brow accent that ties
    #    the kit to the head while leaving Pip's eye + beak in the open below it.
    by = CROWN_Y + 4
    pygame.draw.line(surf, _BB_SHOE_D, (HX - 12, by + 1), (HX + 13, by), 6)   # band shadow
    pygame.draw.line(surf, _BB_TRIM, (HX - 12, by), (HX + 13, by - 1), 4)
    pygame.draw.line(surf, _BB_JERSEY, (HX - 11, by), (HX + 12, by - 1), 1)   # purple midline
    pygame.draw.line(surf, _BB_TRIM, (HX - 10, by - 2), (HX + 4, by - 2), 1)  # top glint


build = store_skins._make_skin(_paint)
