"""DESIGN 1 — THE GOLDEN BOOT (Soccer / Football).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw as the tournament top-scorer: the hero read
is a pair of ENORMOUS gleaming GOLD CLEATS that anchor the silhouette at the
feet, with a slim gold trophy peeking up behind the shoulders. There is NO
jersey — the scarlet body stays fully visible, so the gold reads as trophy metal
against red rather than a costume fill.

Bottom-weighting the brightest mass at the boots is the whole idea: at 40px the
eye lands on two big gold shapes first, then the trophy break above the
shoulders, then the small stud-motif echoes (wingtips + a thin crown lace band).
Every gold object carries a bright highlight + a bronze shadow so it reads as
struck metal, not a flat gold blob.
"""

import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body-centre anchor in COMPOSITE space — the trophy hangs off the shoulders,
# not the head, so it gets its own reference point below the beak/crown anchors.
BCX, BCY = 32, 52

# ── golden palette ────────────────────────────────────────────────────────────
# Three gold values (body / highlight / bronze shadow) so every metal shape reads
# as struck gold at the downscale instead of a flat fill; the dark sole doubles
# as the stud colour so the boots keep a grounded base edge.
_GOLD      = (232, 185,  35)   # main boot gold
_GOLD_HI   = (255, 243, 160)   # boot / trophy highlight glint
_GOLD_SH   = (138,  90,   0)   # bronze shadow under the metal
_BOOT_SOLE = ( 44,  44,  44)   # dark sole + stud ticks + burned "9"
_TROPHY    = (240, 200,  50)   # trophy gold


def _paint(surf, _a):
    # 1 — GOLD TROPHY behind the shoulders, drawn FIRST so the scarlet body/wings
    # overlap its base and only the cup + stem poke up 5-6px above the shoulder
    # line into open sky. A narrow stem widening to a two-handled cup; bronze
    # shadow underlay on the right so the metal reads round, a highlight up the
    # left so it glints.
    tx = BCX + 1                       # trophy centre x, just right of body centre
    cup_top = BCY - 14                 # ~y=38, above the shoulder mass
    # foot + stem (thin bright column rising out from behind the shoulders)
    _poly(surf, _GOLD_SH, [(tx - 2, BCY - 6), (tx + 3, BCY - 6),
                           (tx + 2, BCY - 8), (tx - 1, BCY - 8)])   # base plinth
    pygame.draw.line(surf, _GOLD_SH, (tx + 1, BCY - 8), (tx + 1, cup_top + 4), 3)
    pygame.draw.line(surf, _TROPHY,  (tx,     BCY - 8), (tx,     cup_top + 4), 2)
    # cup bowl — a squat V/U of gold flaring at the rim
    cup = [(tx - 5, cup_top), (tx + 5, cup_top),
           (tx + 3, cup_top + 5), (tx - 3, cup_top + 5)]
    _poly(surf, _GOLD_SH, [(x + 1, y) for x, y in cup])
    _poly(surf, _TROPHY, cup)
    # two side handles + a rim glint so the trophy silhouette is unmistakable
    pygame.draw.arc(surf, _TROPHY, (tx - 9, cup_top, 6, 6), -1.2, 1.9, 2)
    pygame.draw.arc(surf, _TROPHY, (tx + 3, cup_top, 6, 6),  1.2, 4.4, 2)
    pygame.draw.line(surf, _GOLD_HI, (tx - 4, cup_top + 1), (tx + 3, cup_top + 1), 1)

    # 2 — GOLDEN BOOTS: the hero shapes. Two oversized gleaming cleats at the feet,
    # each a bronze-shadowed sole under a bright gold upper, so the eye lands here
    # first at 40px. Drawn as a shadow ellipse, the gold upper, a bright highlight
    # stripe across the toe, and dark stud ticks along the bottom. The right boot
    # gets a burned-in "9" (the top-scorer's number).
    for bx in (HX - 18, HX - 2):       # left boot, then right boot
        # dark sole shadow sitting just under the gold upper — grounds the boot
        pygame.draw.ellipse(surf, _BOOT_SOLE, (bx, HY + 25, 14, 5))
        # bronze underside so the upper reads as rounded metal, not a decal
        pygame.draw.ellipse(surf, _GOLD_SH, (bx, HY + 24, 14, 8))
        # the big gold upper
        pygame.draw.ellipse(surf, _GOLD, (bx, HY + 23, 14, 8))
        # bright highlight stripe across the toe box — the gleam
        pygame.draw.line(surf, _GOLD_HI, (bx + 3, HY + 25), (bx + 11, HY + 25), 2)
        # dark stud ticks along the bottom edge — the cleat read
        for sx in (bx + 3, bx + 7, bx + 11):
            pygame.draw.line(surf, _BOOT_SOLE, (sx, HY + 30), (sx, HY + 31), 2)

    # Burned "9" in dark on the RIGHT boot — the star striker's squad number.
    rbx = HX - 2
    pygame.draw.ellipse(surf, _BOOT_SOLE, (rbx + 3, HY + 24, 4, 3), 1)   # ring top
    pygame.draw.line(surf, _BOOT_SOLE, (rbx + 6, HY + 25), (rbx + 5, HY + 28), 1)  # tail

    # 3 — WINGTIP ACCENTS: small gold stud rectangles at each wing tip, echoing
    # the boot studs up the body so the gold motif ties top-to-bottom instead of
    # stranding all the metal at the feet. Bronze shadow + gold cap = one tiny
    # struck-metal tick per tip.
    for wx, wy in ((BCX - 12, BCY - 2), (HX + 8, BCY - 2)):
        pygame.draw.rect(surf, _GOLD_SH, (wx, wy, 3, 3))
        pygame.draw.rect(surf, _GOLD, (wx, wy, 3, 2))
        pygame.draw.line(surf, _GOLD_HI, (wx, wy), (wx + 2, wy), 1)

    # 4 — LACE BAND: a thin 2px gold band across the CROWN — a subtle winner's
    # crown detail up top, not a brow line, so the head keeps a quiet gold note
    # that rhymes with the boots without a second heavy shape competing with them.
    pygame.draw.line(surf, _GOLD, (HX - 8, CROWN_Y), (HX + 8, CROWN_Y), 2)
    pygame.draw.line(surf, _GOLD_HI, (HX - 6, CROWN_Y - 1), (HX + 2, CROWN_Y - 1), 1)


build = _make_skin(_paint)
