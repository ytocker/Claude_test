"""DESIGN 1 — THE STRIKER (Soccer / Football).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a soccer striker: a bold royal-blue + white
vertical-striped team jersey carries the read, with a clean white squad number,
a captain's gold armband on the near wing, and full leg kit — tall knee-high
team SOCKS + cleats at the feet line. No ball: the kit alone (striped shirt +
socks) is the soccer tell, so a matching ball can ship as a separate parcel.

The jersey is painted OVER the scarlet body (the head stays the macaw so Pip
still reads as a parrot). All kit is held INSIDE the base bird footprint: socks
+ cleats sit on the feet line (~HY+16..27), nothing balloons the torso or drops
below the feet, only a thin sweatband touches the head.

Headless render: tools/sports_candidates/render_design_1.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Royal-blue + white striped kit; gold captain's armband; team socks + cleats.
# Three jersey-blue values so the vertical stripes still separate from each
# other (and from the white) after the 40px downscale — the striped shirt is
# now the single highest-contrast mass on the figure, so it is THE soccer read.
_SOC_BLUE    = (42, 91, 208)        # #2A5BD0 jersey royal blue
_SOC_BLUE_D  = (24, 54, 132)        # stripe shadow / jersey line work
_SOC_BLUE_H  = (88, 134, 240)       # collar / sleeve highlight
_SOC_WHITE   = (244, 244, 248)      # #F4F4F8 white stripe / number
_SOC_GOLD    = (255, 206, 84)       # #FFCE54 captain's armband (one step up)
_SOC_GOLD_H  = (255, 234, 158)      # armband glint
_SOC_GOLD_D  = (96, 70, 16)         # crisp dark underline so it reads as kit
_SOC_SOCK    = (42, 91, 208)        # knee-high team sock (jersey blue)
_SOC_SOCK_D  = (24, 54, 132)        # sock shading
_SOC_CLEAT   = (32, 34, 44)         # cleat boot
_SOC_CLEAT_H = (74, 80, 98)         # cleat upper highlight


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _paint(surf, _a):
    # --- Striped team JERSEY over the torso (THE soccer read) -------------------
    # A clean jersey block clipped to the chest, filled royal-blue, then bold
    # white vertical stripes laid over it. Kept inside the body footprint (top at
    # the shoulders ~BCY-12, hem at ~BCY+11) so it never balloons the bird; the
    # sleeve caps reach the wing roots so the kit reads as worn, not a bib.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 11),
              (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _SOC_BLUE, jersey)

    # Vertical white stripes — wide 3px bars on a 6px pitch so they survive the
    # downscale as distinct crisp bars, not 1px mud. Clipped to the jersey.
    clip_prev = surf.get_clip()
    surf.set_clip(pygame.Rect(BCX - 16, BCY - 12, 32, 24))
    for sx in range(BCX - 13, BCX + 15, 6):
        pygame.draw.rect(surf, _SOC_WHITE, (sx, BCY - 12, 3, 25))
        pygame.draw.line(surf, _SOC_BLUE_D, (sx - 1, BCY - 12), (sx - 1, BCY + 13), 1)
    surf.set_clip(clip_prev)

    # Re-edge the jersey so the stripes don't leak past the cloth contour, and
    # add a shoulder-seam shadow so the sleeves read as set-in.
    pygame.draw.polygon(surf, _SOC_BLUE_D, jersey, 1)
    pygame.draw.line(surf, _SOC_BLUE_D, (BCX - 13, BCY - 8), (BCX + 11, BCY - 8), 1)

    # Crew collar — a small blue/white notch at the neck so the jersey reads as
    # a team shirt, not just stripes.
    _poly(surf, _SOC_BLUE_H, [(BCX - 5, BCY - 12), (BCX + 4, BCY - 12),
                              (BCX + 2, BCY - 9), (BCX - 3, BCY - 9)])
    pygame.draw.line(surf, _SOC_WHITE, (BCX - 4, BCY - 11), (BCX + 3, BCY - 11), 1)

    # Squad NUMBER "9" — drawn as ONE bold white digit sitting in a cleared blue
    # gap (a blue plate knocks out the stripes behind it) so it reads as a clean
    # number, not a smudge merging with the stripes. A dark edge holds its shape.
    nx, ny = BCX - 2, BCY + 1
    # Blue plate clears the stripes so the digit gets a clean field around it.
    pygame.draw.ellipse(surf, _SOC_BLUE, (nx - 7, ny - 9, 14, 17))
    pygame.draw.ellipse(surf, _SOC_BLUE_D, (nx - 7, ny - 9, 14, 17), 1)
    # Bowl of the 9.
    pygame.draw.ellipse(surf, _SOC_BLUE_D, (nx - 5, ny - 7, 10, 9))
    pygame.draw.ellipse(surf, _SOC_WHITE, (nx - 4, ny - 6, 8, 7))
    pygame.draw.ellipse(surf, _SOC_BLUE, (nx - 2, ny - 4, 4, 4))
    # Tail of the 9 dropping from the bowl's lower-right.
    pygame.draw.line(surf, _SOC_BLUE_D, (nx + 4, ny - 2), (nx + 1, ny + 7), 4)
    pygame.draw.line(surf, _SOC_WHITE, (nx + 4, ny - 2), (nx + 1, ny + 7), 2)

    # --- Captain's gold ARMBAND on the near (right) wing ------------------------
    # A bright gold band wrapping the upper near wing with a crisp dark underline
    # + a glint — one value brighter than Pip's natural yellow wing patch so it
    # reads as kit, not plumage.
    ax, ay = BCX + 13, BCY - 4
    pygame.draw.line(surf, _SOC_GOLD_D, (ax - 4, ay - 5), (ax + 4, ay + 5), 6)
    pygame.draw.line(surf, _SOC_GOLD, (ax - 3, ay - 4), (ax + 3, ay + 4), 4)
    pygame.draw.line(surf, _SOC_GOLD_H, (ax - 2, ay - 4), (ax + 1, ay), 1)

    # --- Tall team SOCKS + cleats at the feet line (replaces the ball tell) -----
    # Knee-high socks are an unmistakable footballer mark. Each leg: a tall
    # jersey-blue sock with a white hoop band near the top, then a dark cleat
    # hugging the feet line. Everything sits ON the feet line (~HY+16..27),
    # nothing drops below it, so the bird keeps its true size.
    for fx in (28, 35):
        # Knee-high sock — taller than a band so it reads as a footballer's sock.
        pygame.draw.line(surf, _SOC_SOCK_D, (fx + 1, HY + 15), (fx + 1, HY + 23), 5)
        pygame.draw.line(surf, _SOC_SOCK, (fx, HY + 15), (fx, HY + 23), 4)
        # White hoop band near the top of the sock (classic kit detail).
        pygame.draw.line(surf, _SOC_WHITE, (fx - 1, HY + 16), (fx + 1, HY + 16), 4)
        pygame.draw.line(surf, _SOC_BLUE_H, (fx - 1, HY + 19), (fx + 1, HY + 19), 1)
        # Cleat boot hugging the feet line — dark upper + a bright white sole
        # stripe so the feet read as boots, plus two stud ticks on the sole.
        pygame.draw.ellipse(surf, _SOC_CLEAT_H, (fx - 4, HY + 22, 9, 5))
        pygame.draw.ellipse(surf, _SOC_CLEAT, (fx - 4, HY + 23, 9, 4))
        pygame.draw.line(surf, _SOC_WHITE, (fx - 3, HY + 24), (fx + 2, HY + 24), 1)
        for tx in (fx - 2, fx + 1):
            pygame.draw.line(surf, _SOC_CLEAT, (tx, HY + 26), (tx, HY + 27), 2)

    # --- Optional thin sweatband on the head (keeps the macaw reading) ----------
    # A slim royal-blue band across the brow with one white edge — a sport tell
    # that doesn't add headgear bulk, so Pip's macaw head stays recognizable.
    pygame.draw.line(surf, _SOC_BLUE_D, (HX - 11, CROWN_Y + 6), (HX + 12, CROWN_Y + 5), 4)
    pygame.draw.line(surf, _SOC_BLUE, (HX - 11, CROWN_Y + 5), (HX + 12, CROWN_Y + 4), 2)
    pygame.draw.line(surf, _SOC_WHITE, (HX - 9, CROWN_Y + 4), (HX + 6, CROWN_Y + 3), 1)


build = store_skins._make_skin(_paint)
