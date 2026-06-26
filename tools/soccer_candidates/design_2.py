"""DESIGN 2 — THE GOALKEEPER (Soccer / Football), v2.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
art stays untouched.

v2 fixes the kit anchor: the jersey now rides the SAME HX,HY polygon the
baseball Slugger uses (top edge y=49, hem y=64) instead of the old BCX,BCY
block that floated too far left and too high. Nothing in the jersey rises above
y=49, and there is NO headband of any kind across the crown or brow.

Concept: the soccer read is carried by ONE cue no other sport shares — a pair of
OVERSIZED bright-orange goalkeeper GLOVES, one fat padded mitt on each wing-hand.
They're the HERO: drawn LAST so they sit proud in front of the body, each ringed
by a dark contour halo so the orange pops off the lime jersey and the night sky
alike. Beneath them a high-visibility lime keeper jersey, a dark shorts band,
hooped socks, and dark boots finish the kit without competing. Pip's macaw
head/beak/eye stay clear so it reads "parrot keeper".
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, _poly

# High-visibility keeper jersey — vivid lime so it survives the dark NIGHT sky.
_GK_JERSEY   = (68, 204, 68)       # #44CC44 hi-vis lime field
_GK_JERSEY_D = (40, 150, 44)       # shaded off-side
_GK_JERSEY_H = (138, 232, 120)     # collar / top sheen

# Goalkeeper gloves — bright safety orange, the HERO read. A white knuckle band
# + cross-strap carry a value break that survives the 40px downscale and keeps
# the mitts legible even at night when orange sits on scarlet.
_GK_GLOVE    = (255, 140, 0)       # #FF8C00 padded mitt body
_GK_GLOVE_H  = (255, 192, 98)      # padding highlight
_GK_GLOVE_D  = (188, 90, 0)        # finger-gap / crease shade
_GK_HALO     = (26, 18, 10)        # dark contour halo so the orange pops
_GK_STRAP    = (244, 246, 250)     # white knuckle band + cross-strap accent

# Shorts + boots — near-black kit darks.
_GK_DARK     = (30, 32, 40)        # shorts band + boots
_GK_DARK_H   = (78, 82, 96)        # rim glint

# Socks — green with a white hoop.
_GK_SOCK     = (34, 120, 40)       # green socks (tie to the jersey)
_GK_SOCK_H   = (240, 244, 240)     # white hoop band


def _paint(surf, _a):
    # ── HI-VIS JERSEY on the EXACT baseball-jersey polygon (the corrected
    #    anchor): top edge at HY+8 (=49) so nothing rises above y=49, hem at
    #    HY+23 (=64), held inside the base bird footprint.
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _GK_JERSEY, jersey)
    # Soft shade down the off-side so the jersey reads as a rounded torso.
    _poly(surf, _GK_JERSEY_D, [(HX + 4, HY + 9), (HX + 11, HY + 18),
                               (HX + 8, HY + 23), (HX + 5, HY + 22)])
    # Collar V at the jersey top — a small bright notch so the kit reads as a
    # keeper shirt, not a blank field. Sits at the top edge (y=49), not above it.
    _poly(surf, _GK_JERSEY_H, [(HX - 4, HY + 8), (HX + 2, HY + 8),
                               (HX - 1, HY + 12)])
    pygame.draw.line(surf, _GK_JERSEY_D, (HX - 4, HY + 8), (HX - 1, HY + 12), 1)
    pygame.draw.line(surf, _GK_JERSEY_D, (HX + 2, HY + 8), (HX - 1, HY + 12), 1)

    # ── SHORTS — a small dark band sitting just under the jersey hem so there's
    #    a kit break between shirt and legs (between hem HY+23 and the socks).
    _poly(surf, _GK_DARK, [(HX - 10, HY + 22), (HX + 8, HY + 22),
                           (HX + 7, HY + 26), (HX - 9, HY + 26)])
    pygame.draw.line(surf, _GK_DARK_H, (HX - 9, HY + 23), (HX + 7, HY + 23), 1)

    # ── SOCKS — two short green pillars at the foot positions, each with one
    #    white hoop band near the top (the classic football sock).
    for fx in (HX - 9, HX + 1):
        pygame.draw.rect(surf, _GK_SOCK, (fx, HY + 26, 7, 6))
        pygame.draw.line(surf, _GK_SOCK_H, (fx, HY + 27), (fx + 6, HY + 27), 1)

    # ── BOOTS — dark wedges at the feet line, tucked on the base bird's feet.
    for fx in (HX - 10, HX):
        pygame.draw.rect(surf, _GK_DARK, (fx, HY + 31, 9, 4), border_radius=2)
        pygame.draw.line(surf, _GK_DARK_H, (fx, HY + 32), (fx + 8, HY + 32), 1)
        # Three tiny stud dots so the boot reads as a football boot.
        for tx in (fx + 1, fx + 4, fx + 7):
            pygame.draw.line(surf, _GK_DARK, (tx, HY + 35), (tx, HY + 36), 1)

    # ── GOALKEEPER GLOVES — the HERO, drawn LAST so they sit in front of the
    #    jersey. Two SMALLER mitts (≈10×12 logical, down ~35% from v1) pulled
    #    INWARD so they ride ON the green jersey, never on the macaw's own orange
    #    tail/wing where they'd vanish. They're ASYMMETRIC — the far mitt is
    #    raised into a catching pose and the near mitt sits lower — so the
    #    silhouette reads as two distinct hands rather than one pair of wings.
    #    A white knuckle band + cross-strap on each gives a value break that the
    #    downscale keeps even when orange would otherwise disappear on scarlet.
    #
    #    (cx, cy, thumb-on-inner-left?): far glove high, near glove low.
    for cx, cy, thumb_left in ((HX - 7, HY + 12, False), (HX + 4, HY + 18, True)):
        # Dark contour halo — a slightly larger mitt behind so the orange always
        # carries a black edge against any background.
        pygame.draw.ellipse(surf, _GK_HALO, (cx - 6, cy - 6, 11, 14))
        # Fat padded palm — the main orange mass, now compact.
        pygame.draw.ellipse(surf, _GK_GLOVE, (cx - 5, cy - 5, 9, 12))
        # Four blunt finger pads riding the top with a 2px dark channel between
        # each so the fingers stay carved and readable at gameplay scale.
        for i, fxo in enumerate((-4, -1, 2, 5)):
            pygame.draw.rect(surf, _GK_GLOVE, (cx + fxo, cy - 8, 2, 5),
                             border_radius=1)
            if i:
                pygame.draw.line(surf, _GK_GLOVE_D, (cx + fxo - 1, cy - 8),
                                 (cx + fxo - 1, cy - 3), 2)
        # Exaggerated thumb — a clear side nub on the inner edge so the mitt
        # silhouette reads as 4-fingers + thumb, not a plain disc.
        if thumb_left:
            pygame.draw.ellipse(surf, _GK_GLOVE, (cx - 8, cy - 1, 5, 6))
            pygame.draw.ellipse(surf, _GK_HALO, (cx - 8, cy - 1, 5, 6), 1)
        else:
            pygame.draw.ellipse(surf, _GK_GLOVE, (cx + 3, cy - 1, 5, 6))
            pygame.draw.ellipse(surf, _GK_HALO, (cx + 3, cy - 1, 5, 6), 1)
        # Padding highlight so the mitt reads as round, padded leather.
        pygame.draw.ellipse(surf, _GK_GLOVE_H, (cx - 3, cy - 3, 4, 4))
        # White knuckle-guard band across the top of the palm — the bright value
        # break that the 40px downscale keeps on day and night alike.
        pygame.draw.line(surf, _GK_STRAP, (cx - 4, cy - 2), (cx + 4, cy - 2), 2)
        # White cross-strap diagonally over the palm — second value break, makes
        # the orange mass read unmistakably as a glove.
        pygame.draw.line(surf, _GK_STRAP, (cx - 4, cy + 4), (cx + 4, cy - 1), 1)
        # Wrist cuff strap so the glove anchors to the wing.
        pygame.draw.rect(surf, _GK_GLOVE_D, (cx - 4, cy + 6, 8, 3),
                         border_radius=1)
        pygame.draw.line(surf, _GK_STRAP, (cx - 3, cy + 6), (cx + 3, cy + 6), 1)


build = store_skins._make_skin(_paint)
