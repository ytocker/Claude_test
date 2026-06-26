"""THE SLUGGER — Pip as a baseball player (DESIGN 4 of the SPORTS set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: the baseball read is carried by TWO bold shapes that survive the 40px
downscale — a classic curved-brim CAP low on the head, and a tapered wooden BAT
slung diagonally BEHIND the body (the proven pirate-cutlass technique: painted
first so the torso covers the mid-shaft and only the fat barrel + knob overshoot
the silhouette against open sky). The torso is a pinstripe jersey (white field +
thin navy verticals + a big number) so the kit reads at hero scale, with a
catcher's mitt on the near wing and cleats at the feet line. Pip's macaw
head/beak/eye stay clear so it stays "parrot dressed as a ballplayer."

At 40px, in order of value: (1) a tapered wooden bat breaking the back outline,
(2) the curved-brim navy cap on the crown, (3) the white pinstripe jersey mass,
(4) the brown mitt + cleats. The bat carries a bright tan highlight edge and a
dark shadow side so the cylinder still reads as a bat after downscale; the cap's
brim is one continuous bold wedge so the headgear reads as a ball cap, not a
generic hat.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Wood bat — three values so the tapered cylinder keeps form at 40px (a flat
# single-value bar reads as a stick, not a bat).
_BSB_BAT     = (201, 162, 75)      # #C9A24B tan barrel body
_BSB_BAT_D   = (138, 106, 46)      # #8A6A2E shaded underside
_BSB_BAT_H   = (232, 204, 130)     # bright top glint so the barrel reads round
_BSB_KNOB    = (138, 106, 46)      # darker knob/handle end

# Cap + pinstripe navy (the team colour).
_BSB_NAVY    = (27, 42, 107)       # #1B2A6B cap shell + pinstripes
_BSB_NAVY_D  = (18, 28, 74)        # brim/under-shadow
_BSB_NAVY_H  = (60, 84, 168)       # cap top sheen

# Jersey white.
_BSB_WHITE   = (242, 242, 242)     # #F2F2F2 jersey field
_BSB_WHITE_D = (198, 200, 210)     # jersey shade

# Catcher's mitt brown + cleats.
_BSB_MITT    = (110, 67, 38)       # #6E4326 mitt leather
_BSB_MITT_H  = (150, 96, 56)       # mitt highlight / pocket lacing
_BSB_CLEAT   = (32, 34, 44)        # near-black cleats
_BSB_CLEAT_H = (96, 100, 114)      # cleat rim glint


def _paint(surf, _a):
    # ── WOODEN BAT slung diagonally BEHIND the body (painted FIRST so the torso
    #    covers the mid-shaft; only the fat barrel + knob overshoot the back/
    #    shoulder outline against the sky — same slung-prop trick as the pirate
    #    cutlass). The handle starts low at the near wing/waist; the bat sweeps
    #    up-and-back so the BARREL (the fat end) is what clears the silhouette.
    #    Tip stays well above the feet line — a slung prop, never dangling.
    handle = (HX - 1, HY + 22)        # thin grip end, low at the near wing
    barrel = (HX - 25, CROWN_Y + 1)   # fat barrel end, breaking the back outline
    # Taper: draw the shaft in two segments so the handle is thin and the barrel
    # is fat — a constant-width line reads as a pipe, not a bat.
    mid = ((handle[0] + barrel[0]) // 2, (handle[1] + barrel[1]) // 2)
    pygame.draw.line(surf, _BSB_BAT_D, handle, mid, 4)    # thin handle, shadow
    pygame.draw.line(surf, _BSB_BAT, handle, mid, 3)
    pygame.draw.line(surf, _BSB_BAT_D, mid, barrel, 8)    # fat barrel, shadow
    pygame.draw.line(surf, _BSB_BAT, mid, barrel, 6)
    # Bright top glint along the barrel so the cylinder reads as round wood at
    # 40px (offset to the upper edge of the slung diagonal).
    pygame.draw.line(surf, _BSB_BAT_H, (mid[0], mid[1] - 2),
                     (barrel[0] + 1, barrel[1] - 2), 2)
    pygame.draw.line(surf, _BSB_BAT_H, (handle[0] - 1, handle[1] - 1),
                     (mid[0], mid[1] - 1), 1)
    # Rounded barrel cap so the fat end reads as the bat's tip, not a cut bar.
    pygame.draw.circle(surf, _BSB_BAT, barrel, 4)
    pygame.draw.circle(surf, _BSB_BAT_H, (barrel[0], barrel[1] - 1), 2)
    pygame.draw.circle(surf, _BSB_BAT_D, (barrel[0] + 1, barrel[1] + 2), 1)
    # Knob at the handle end — the little flare that says "this is the grip".
    pygame.draw.circle(surf, _BSB_KNOB, handle, 3)
    pygame.draw.circle(surf, _BSB_BAT, (handle[0], handle[1] - 1), 1)

    # ── PINSTRIPE JERSEY over the torso (white field hugging the body, held
    #    INSIDE the base bird footprint — bottom ~HY+23 — so nothing balloons the
    #    silhouette). White is the brightest mass so the kit reads at hero scale;
    #    thin navy verticals + a number sell "baseball jersey".
    jersey = [(HX - 13, HY + 8), (HX - 14, HY + 18), (HX - 10, HY + 23),
              (HX + 8, HY + 23), (HX + 11, HY + 18), (HX + 9, HY + 8)]
    _poly(surf, _BSB_WHITE, jersey)
    # Soft shade down the off-side so the jersey reads as a rounded torso.
    _poly(surf, _BSB_WHITE_D, [(HX + 4, HY + 9), (HX + 11, HY + 18),
                               (HX + 8, HY + 23), (HX + 5, HY + 22)])
    # Thin navy pinstripes — kept to three clean verticals; a denser stripe set
    # collapsed into grey mud at 40px, so three reads as "pinstripe" cleanly.
    for sx in (HX - 8, HX - 1, HX + 6):
        pygame.draw.line(surf, _BSB_NAVY, (sx, HY + 9), (sx, HY + 22), 1)
    # Navy placket + collar so the jersey has a front opening, not a blank field.
    pygame.draw.line(surf, _BSB_NAVY, (HX - 2, HY + 8), (HX - 2, HY + 22), 1)
    _poly(surf, _BSB_NAVY, [(HX - 6, HY + 7), (HX + 4, HY + 7),
                            (HX + 2, HY + 10), (HX - 4, HY + 10)])  # collar band
    # Big jersey NUMBER — a bold navy "7" reads as a uniform number at hero scale.
    pygame.draw.line(surf, _BSB_NAVY, (HX - 5, HY + 13), (HX + 1, HY + 13), 2)
    pygame.draw.line(surf, _BSB_NAVY, (HX + 1, HY + 13), (HX - 3, HY + 21), 2)

    # ── CATCHER'S MITT on the near wing — a rounded brown leather mass with a
    #    pale lacing arc so it reads as a mitt's pocket, tucked inside the body.
    mx, my = HX - 13, HY + 15
    pygame.draw.circle(surf, _BSB_MITT, (mx, my), 6)
    pygame.draw.circle(surf, _BSB_MITT_H, (mx - 1, my - 2), 2)   # pocket sheen
    # Lacing arc across the pocket + a webbing notch at the top (the mitt read).
    pygame.draw.arc(surf, _BSB_MITT_H, (mx - 5, my - 5, 10, 10), 0.4, 2.7, 1)
    _poly(surf, _BSB_MITT, [(mx - 3, my - 6), (mx, my - 9), (mx + 3, my - 6)])  # web
    pygame.draw.line(surf, _BSB_MITT_H, (mx, my - 8), (mx, my - 5), 1)

    # ── CLEATS at the feet line (~HY+24..27) — dark spiked shoes tucked at the
    #    jersey hem so they sit on the base bird's feet, not below them.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, _BSB_CLEAT, (fx, HY + 23, 8, 5), border_radius=2)
        pygame.draw.line(surf, _BSB_CLEAT_H, (fx, HY + 24), (fx + 7, HY + 24), 1)
        # Three tiny spike teeth under the sole — the cleat read.
        for tx in (fx + 1, fx + 4, fx + 7):
            pygame.draw.line(surf, _BSB_CLEAT, (tx, HY + 28), (tx, HY + 29), 1)

    # ── CLASSIC BALL CAP on the crown — a rounded navy shell sitting LOW on the
    #    head (so the macaw face still shows) + a bold curved brim projecting
    #    forward over the beak. The brim is one continuous wedge so the headgear
    #    reads unmistakably as a ball cap, not a generic dome.
    cy = CROWN_Y + 2
    # Rounded crown shell — an ellipse hugging the top of the head.
    pygame.draw.ellipse(surf, _BSB_NAVY, (HX - 11, cy - 6, 22, 13))
    pygame.draw.ellipse(surf, _BSB_NAVY_D, (HX - 11, cy - 6, 22, 13), 1)
    # Top sheen so the dome reads as round, not flat.
    pygame.draw.ellipse(surf, _BSB_NAVY_H, (HX - 6, cy - 5, 9, 5))
    # Button on the crown's top centre (the classic cap stud).
    pygame.draw.circle(surf, _BSB_NAVY_H, (HX, cy - 5), 1)
    # Curved BRIM projecting forward over the beak — a bold wedge with an
    # under-shadow so it reads as a separate visor, the key "ball cap" cue.
    brim = [(HX + 2, cy + 4), (HX + 16, cy + 2), (HX + 17, cy + 6),
            (HX + 3, cy + 8)]
    _poly(surf, _BSB_NAVY, brim)
    _poly(surf, _BSB_NAVY_D, [(HX + 3, cy + 7), (HX + 17, cy + 6),
                              (HX + 16, cy + 8), (HX + 3, cy + 9)])  # brim shade
    pygame.draw.line(surf, _BSB_NAVY_H, (HX + 3, cy + 4), (HX + 15, cy + 2), 1)  # brim glint
    # A small white "team mark" on the cap front so it's not a blank navy dome.
    pygame.draw.circle(surf, _BSB_WHITE, (HX + 3, cy), 2)
    pygame.draw.circle(surf, _BSB_NAVY, (HX + 3, cy), 1)


build = store_skins._make_skin(_paint)
