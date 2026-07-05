"""THE SLUGGER — Pip as a baseball player (DESIGN 4 of the SPORTS set).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so production
is untouched.

Concept: the baseball read is carried by TWO bold shapes that survive the 40px
downscale — a big NAVY ball cap that owns the top of the silhouette (its shell
is the largest dark mass above a forward curved brim, so it beats the bird's own
green crown), and a tapered wooden BAT slung diagonally BEHIND the body (the
proven pirate-cutlass technique: painted first so the torso covers the mid-shaft
and the fat barrel overshoots PAST the back/tail outline into open sky, leaving
one clean tan diagonal). The torso is a pinstripe jersey (white field + thin
navy verticals + a big number) so the kit reads at hero scale; cleats sit at the
feet line. Pip's macaw head/beak/eye stay clear so it stays "parrot dressed as a
ballplayer."

At 40px, in order of value: (1) the navy cap shell winning the crown, (2) a fat
tan bat barrel breaking the back/tail outline against open sky, (3) the white
pinstripe jersey mass, (4) the cleats. The bat carries a wide bright tan glint
and a dark shadow side so the cylinder still reads as a bat after downscale; the
cap's brim is one continuous bold wedge so the headgear reads as a ball cap, not
a generic hat. No catcher's mitt — it was the lowest-value cue and merged with
the bat barrel into a brown blob, so the bat now slings into clear sky.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Wood bat — three values so the tapered cylinder keeps form at 40px (a flat
# single-value bar reads as a stick, not a bat). Barrel body lifted to a warm
# mid-tan so the cylinder stays bright and separates against the dark NIGHT sky
# instead of sinking to a brown smear at downscale.
_BSB_BAT     = (214, 176, 92)      # #D6B05C tan barrel body (lifted for night)
_BSB_BAT_D   = (150, 116, 52)      # #967434 shaded underside (kept thin)
_BSB_BAT_H   = (240, 214, 146)     # bright top glint so the barrel reads round
_BSB_KNOB    = (150, 116, 52)      # darker knob/handle end

# Cap + pinstripe navy (the team colour).
_BSB_NAVY    = (27, 42, 107)       # #1B2A6B cap shell + pinstripes
_BSB_NAVY_D  = (18, 28, 74)        # brim/under-shadow
_BSB_NAVY_H  = (60, 84, 168)       # cap top sheen

# Jersey white.
_BSB_WHITE   = (242, 242, 242)     # #F2F2F2 jersey field
_BSB_WHITE_D = (198, 200, 210)     # jersey shade

# Cleats.
_BSB_CLEAT   = (32, 34, 44)        # near-black cleats
_BSB_CLEAT_H = (96, 100, 114)      # cleat rim glint


def _paint(surf, _a):
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

    # ── CLEATS at the feet line (~HY+24..27) — dark spiked shoes tucked at the
    #    jersey hem so they sit on the base bird's feet, not below them.
    for fx in (HX - 11, HX - 1):
        pygame.draw.rect(surf, _BSB_CLEAT, (fx, HY + 23, 8, 5), border_radius=2)
        pygame.draw.line(surf, _BSB_CLEAT_H, (fx, HY + 24), (fx + 7, HY + 24), 1)
        # Three tiny spike teeth under the sole — the cleat read.
        for tx in (fx + 1, fx + 4, fx + 7):
            pygame.draw.line(surf, _BSB_CLEAT, (tx, HY + 28), (tx, HY + 29), 1)

    # ── CLASSIC BALL CAP on the crown — a BIG navy shell raised to sit ON TOP of
    #    the head so the navy is the largest dark mass at the crown and beats the
    #    bird's own green crown at 40px (the sport must read off the cap alone).
    #    A bold forward curved brim projects over the beak so the headgear reads
    #    unmistakably as a ball cap, not a generic dome.
    cy = CROWN_Y - 3
    # Rounded crown shell — a wide ellipse OWNING the top of the head (~26px),
    # raised so its navy mass dominates the green nape beneath it.
    pygame.draw.ellipse(surf, _BSB_NAVY, (HX - 13, cy - 5, 26, 15))
    pygame.draw.ellipse(surf, _BSB_NAVY_D, (HX - 13, cy - 5, 26, 15), 1)
    # Top sheen so the dome reads as round, not flat.
    pygame.draw.ellipse(surf, _BSB_NAVY_H, (HX - 7, cy - 4, 11, 6))
    # Button on the crown's top centre (the classic cap stud).
    pygame.draw.circle(surf, _BSB_NAVY_H, (HX, cy - 4), 1)
    # Curved BRIM projecting forward over the beak — a bold wedge with an
    # under-shadow so it reads as a separate visor, the key "ball cap" cue.
    brim = [(HX + 3, cy + 6), (HX + 18, cy + 4), (HX + 19, cy + 8),
            (HX + 4, cy + 10)]
    _poly(surf, _BSB_NAVY, brim)
    _poly(surf, _BSB_NAVY_D, [(HX + 4, cy + 9), (HX + 19, cy + 8),
                              (HX + 18, cy + 10), (HX + 4, cy + 11)])  # brim shade
    pygame.draw.line(surf, _BSB_NAVY_H, (HX + 4, cy + 6), (HX + 17, cy + 4), 1)  # brim glint
    # A small white "team mark" on the cap front so it's not a blank navy dome.
    pygame.draw.circle(surf, _BSB_WHITE, (HX + 4, cy + 2), 2)
    pygame.draw.circle(surf, _BSB_NAVY, (HX + 4, cy + 2), 1)

    # ── WOODEN BAT — drawn LAST so it OVERLAYS the jersey/clothing: the bat rests
    #    diagonally ACROSS the uniform, fully visible in front, rather than slung
    #    behind the torso. Handle/knob at the near wing over the jersey; the fat
    #    barrel runs up past the back/tail outline into open sky as one clean tan
    #    diagonal. Three values keep the tapered cylinder reading as a bat at 40px.
    handle = (HX + 1, HY + 21)        # grip end over the near wing / jersey
    barrel = (HX - 29, HY - 5)        # fat barrel end, out past the back outline
    mid = ((handle[0] + barrel[0]) // 2, (handle[1] + barrel[1]) // 2)
    # Underside shadow kept a thin sliver so the bright barrel holds the cylinder.
    pygame.draw.line(surf, _BSB_BAT_D, (handle[0], handle[1] + 1),
                     (mid[0], mid[1] + 1), 4)
    pygame.draw.line(surf, _BSB_BAT_D, (mid[0], mid[1] + 2),
                     (barrel[0], barrel[1] + 2), 9)
    # Bright barrel body — taper handle (3px) → barrel (7px).
    pygame.draw.line(surf, _BSB_BAT, handle, mid, 3)
    pygame.draw.line(surf, _BSB_BAT, mid, barrel, 7)
    # Wide bright top glint so the round tan cylinder survives at 40px day + night.
    pygame.draw.line(surf, _BSB_BAT_H, (mid[0] - 1, mid[1] - 2),
                     (barrel[0] + 1, barrel[1] - 2), 3)
    pygame.draw.line(surf, _BSB_BAT_H, (handle[0] - 1, handle[1] - 1),
                     (mid[0], mid[1] - 1), 2)
    # Rounded barrel cap so the fat end reads as the bat's tip.
    pygame.draw.circle(surf, _BSB_BAT, barrel, 5)
    pygame.draw.circle(surf, _BSB_BAT_H, (barrel[0] - 1, barrel[1] - 2), 2)
    pygame.draw.circle(surf, _BSB_BAT_D, (barrel[0] + 1, barrel[1] + 3), 1)
    # Knob at the handle end — the grip flare.
    pygame.draw.circle(surf, _BSB_KNOB, handle, 3)
    pygame.draw.circle(surf, _BSB_BAT, (handle[0], handle[1] - 1), 1)


build = store_skins._make_skin(_paint)
