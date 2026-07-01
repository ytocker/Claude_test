"""Soccer v4 DESIGN 3 — THE STREET BALLER.

Pip as a Brazilian-style pelada footballer: no jersey, the scarlet macaw
body stays bare and the kit is pure street signal. A side-knotted
green/yellow headband, scattered Brazil-colour paint-splatter dabs across
the torso (drawn OVER the body so the red still reads), a single green
ankle band, and a taped black/white ball swinging on a cord from the near
wing. Everything is asymmetric on purpose — scrappy, not uniformed — so it
reads as a distinct look from THE CAPTAIN even at the 40px truth scale.
"""
import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body centre anchors — the paint dabs and cord root off these so the
# splatter stays over the torso regardless of frame.
BCX, BCY = 32, 52

_GREEN = (0, 168, 89)         # Brazil green — headband / ankle / dabs
_GREEN_D = (0, 120, 62)       # green shadow for a little roundness
_YELLOW = (244, 208, 63)      # Brazil yellow — knot / dabs
_BALL_W = (245, 245, 245)     # ball leather white
_BALL_D = (20, 20, 20)        # ball pentagon patches + outline
_CORD = (80, 60, 40)          # tan cord the ball swings on


def _paint(surf, _a):
    # Single bright green ankle band on ONE ankle — the first asymmetry tell.
    pygame.draw.line(surf, _GREEN_D, (HX - 14, HY + 22), (HX - 8, HY + 22), 3)
    pygame.draw.line(surf, _GREEN, (HX - 14, HY + 21), (HX - 8, HY + 21), 3)

    # Paint-splatter dabs scattered over the bare scarlet torso — hand-placed,
    # not a lattice, ~4 green + 4 yellow, each 2-3px so they survive downscale
    # while leaving plenty of red showing between them.
    _dabs = [
        (BCX - 5, BCY - 8, 2, _GREEN),
        (BCX + 3, BCY - 5, 2, _YELLOW),
        (BCX - 2, BCY + 3, 3, _GREEN),
        (BCX + 6, BCY + 1, 2, _YELLOW),
        (BCX - 8, BCY - 1, 2, _YELLOW),
        (BCX + 1, BCY + 8, 2, _GREEN),
        (BCX - 6, BCY + 7, 2, _YELLOW),
        (BCX + 5, BCY - 9, 2, _GREEN),
    ]
    for dx, dy, r, col in _dabs:
        pygame.draw.circle(surf, col, (dx, dy), r)
    # A couple of tiny fleck taps so the splatter feels flung, not dotted.
    pygame.draw.circle(surf, _YELLOW, (BCX - 3, BCY - 3), 1)
    pygame.draw.circle(surf, _GREEN, (BCX + 3, BCY + 5), 1)

    # Side-knotted headband: a bright green band angled across the brow, just
    # above the beak on the near side, with the knot pushed to the RIGHT so it
    # reads off-centre (not a symmetric sweatband).
    pygame.draw.line(surf, _GREEN_D, (HX - 8, HY - 2), (HX + 6, HY - 3), 4)
    pygame.draw.line(surf, _GREEN, (HX - 8, HY - 3), (HX + 6, HY - 4), 4)
    # Yellow knot bump + two short trailing tails flicking off the side.
    pygame.draw.circle(surf, _YELLOW, (HX + 6, HY - 4), 3)
    pygame.draw.line(surf, _YELLOW, (HX + 7, HY - 4), (HX + 12, HY - 7), 2)
    pygame.draw.line(surf, _GREEN, (HX + 7, HY - 3), (HX + 12, HY - 1), 2)

    # Taped soccer ball swinging on a cord from the NEAR wing — drawn LAST so
    # it sits fully in front of the body. Cord roots at the wing exit and drops
    # to the ball centre; the ball is a black leather rim over a white shell
    # with a few dark pentagon patches so it reads as a real football.
    bx, by = HX + 14, HY + 10
    pygame.draw.line(surf, _CORD, (HX + 10, BCY - 4), (bx, by), 1)
    pygame.draw.circle(surf, _BALL_D, (bx, by), 7)      # leather outline
    pygame.draw.circle(surf, _BALL_W, (bx, by), 6)      # white shell
    pygame.draw.circle(surf, _BALL_D, (bx, by), 2)      # centre pentagon
    pygame.draw.circle(surf, _BALL_D, (bx + 3, by - 3), 1)   # upper-right patch
    pygame.draw.circle(surf, _BALL_D, (bx - 3, by - 3), 1)   # upper-left patch
    pygame.draw.circle(surf, _BALL_D, (bx + 4, by + 2), 1)   # lower-right patch
    pygame.draw.circle(surf, _BALL_D, (bx - 4, by + 2), 1)   # lower-left patch
    # Thin seam ticks linking the patches so it doesn't read as loose dots.
    pygame.draw.line(surf, _BALL_D, (bx, by - 2), (bx + 3, by - 3), 1)
    pygame.draw.line(surf, _BALL_D, (bx, by - 2), (bx - 3, by - 3), 1)


build = _make_skin(_paint)
