"""DESIGN 1 — THE STRIKER (Soccer / Football).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a soccer striker: a royal-blue + white vertical-striped
team jersey with a big number painted over the torso, a captain's gold armband
on the near wing, shin-guards + cleats at the feet line, and the hero read — a
bold pure-white soccer ball floated on the jersey, central and high-contrast.

The jersey is painted OVER the scarlet body (the head stays the macaw so Pip
still reads as a parrot). All kit is held INSIDE the base bird footprint: the
ball rides the chest while shin-guards + cleats sit on the feet line
(~HY+22..27), nothing balloons the torso, only a thin sweatband touches the head.

Headless render: tools/sports_candidates/render_design_1.py.
"""
import math

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Royal-blue + white striped kit; black-&-white ball; gold captain's armband.
# Three jersey-blue values so the vertical stripes still separate from each
# other (and from the white) after the 40px downscale; the ball is near-white
# with hard near-black hexagon patches so the SPORT is the highest-contrast
# mass on the whole figure — the instant soccer read.
_SOC_BLUE    = (42, 91, 208)        # #2A5BD0 jersey royal blue
_SOC_BLUE_D  = (28, 62, 150)        # stripe shadow / jersey line work
_SOC_BLUE_H  = (88, 134, 240)       # collar / sleeve highlight
_SOC_WHITE   = (242, 242, 242)      # #F2F2F2 white stripe / ball body
_SOC_WHITE_D = (198, 200, 208)      # ball shade so the sphere reads round
_SOC_PATCH   = (22, 22, 22)         # #161616 ball hexagon patches
_SOC_GOLD    = (232, 194, 74)       # #E8C24A captain's armband
_SOC_GOLD_H  = (255, 232, 150)      # armband glint
_SOC_GUARD   = (226, 228, 234)      # plastic shin-guard
_SOC_GUARD_D = (168, 172, 182)      # shin-guard shadow
_SOC_CLEAT   = (54, 58, 70)         # cleat — lifted off black so it isn't the
_SOC_CLEAT_H = (92, 98, 116)        #   ball's dark twin; lighter outline tells it apart
_SOC_SOCK    = (28, 62, 150)        # team sock (jersey-blue-dark)


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _soccer_ball(surf, cx, cy, r):
    """The HERO mass: a pure-white sphere carrying ONE bold central black
    pentagon and two short seam stubs. At 40px the geodesic net is just noise —
    a single high-contrast pentagon on a true-white ball is the cleanest,
    fastest 'SOCCER' read, so this is drawn as the brightest, most central mark
    on the whole figure (a 1px lower-right shade is the only shading)."""
    # Pure-white body so it out-contrasts every blue/white jersey stripe; a
    # single 1px lower-right crescent gives roundness without greying the ball.
    pygame.draw.circle(surf, _SOC_WHITE_D, (cx, cy + 1), r)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), r)

    # Central black pentagon — the unmistakable soccer signature, sized big so
    # it survives the downscale as one decisive dark shape.
    s = r * 0.52
    pent = []
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        pent.append((cx + s * math.cos(a), cy + s * math.sin(a)))
    _poly(surf, _SOC_PATCH, pent)

    # Two short black seam stubs poking in from the rim — just enough to say
    # 'panelled ball' without the partial-patch clutter that muddied round 1.
    for ang in (math.radians(150), math.radians(30)):
        ex = cx + r * math.cos(ang)
        ey = cy + r * math.sin(ang)
        ix = cx + (r * 0.48) * math.cos(ang)
        iy = cy + (r * 0.48) * math.sin(ang)
        pygame.draw.line(surf, _SOC_PATCH, (ix, iy), (ex, ey), 2)


def _paint(surf, _a):
    # --- Striped team JERSEY over the torso -------------------------------------
    # A clean jersey block clipped to the chest, filled royal-blue, then white
    # vertical stripes laid over it. Kept inside the body footprint (top at the
    # shoulders ~HY+5, hem at ~HY+22) so it never balloons the bird; the sleeve
    # caps reach to the wing roots so the kit reads as worn, not a bib.
    jersey = [(BCX - 15, BCY - 9), (BCX - 16, BCY - 1), (BCX - 14, BCY + 11),
              (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 9),
              (BCX + 4, BCY - 12), (BCX - 6, BCY - 12)]
    _poly(surf, _SOC_BLUE, jersey)

    # Vertical white stripes — few + wide (3px) so they survive downscale as
    # distinct bars, not 1px mud. Drawn as tall blue/white pairs across the
    # torso width, each clipped to the jersey by a clip rect.
    clip_prev = surf.get_clip()
    jrect = pygame.Rect(BCX - 16, BCY - 12, 32, 24)
    surf.set_clip(jrect)
    for i, sx in enumerate(range(BCX - 14, BCX + 15, 6)):
        pygame.draw.rect(surf, _SOC_WHITE, (sx, BCY - 12, 3, 25))
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

    # Squad NUMBER "9" — DEMOTED so the ball wins: ~20% smaller and slid left so
    # its centre sits over a BLUE stripe gap, where a white digit reads cleanly
    # instead of washing into a white stripe. Dark edge kept so it holds shape.
    nx, ny = BCX - 4, BCY - 1
    # Outline pass (dark) then the white fill, so the digit pops on the blue.
    pygame.draw.ellipse(surf, _SOC_BLUE_D, (nx - 4, ny - 7, 8, 8))
    pygame.draw.ellipse(surf, _SOC_WHITE, (nx - 3, ny - 6, 6, 6))
    # Knock a hole back into the bowl so it reads as a "9" loop, not a blob.
    pygame.draw.ellipse(surf, _SOC_BLUE, (nx - 1, ny - 4, 3, 3))
    # Tail of the 9 dropping from the bowl's lower-right.
    pygame.draw.line(surf, _SOC_BLUE_D, (nx + 4, ny - 3), (nx + 1, ny + 6), 5)
    pygame.draw.line(surf, _SOC_WHITE, (nx + 4, ny - 3), (nx + 1, ny + 6), 2)

    # --- Captain's gold ARMBAND on the near (right) wing ------------------------
    # A bright gold band wrapping the upper near wing with a glint — the only
    # warm note, so it reads as the captain's armband against the blue kit.
    ax, ay = BCX + 13, BCY - 4
    # One crisp dark edge under the gold so the band doesn't read as one of
    # Pip's yellow wing patches.
    pygame.draw.line(surf, (78, 60, 18), (ax - 4, ay - 5), (ax + 4, ay + 5), 6)
    pygame.draw.line(surf, _SOC_GOLD, (ax - 3, ay - 4), (ax + 3, ay + 4), 4)
    pygame.draw.line(surf, _SOC_GOLD_H, (ax - 2, ay - 4), (ax + 1, ay), 1)

    # --- Shin-guards + team socks + cleats at the feet line ---------------------
    # Both held ON the feet line (~HY+22..27), nothing below it, so the bird
    # stays its true size. Each leg: a team sock, a plastic shin-guard plate over
    # it, then a black cleat with a studded sole tick.
    for fx in (28, 35):
        # Team sock band above the foot.
        pygame.draw.line(surf, _SOC_SOCK, (fx, HY + 17), (fx, HY + 22), 4)
        pygame.draw.line(surf, _SOC_WHITE, (fx - 1, HY + 18), (fx - 1, HY + 20), 1)
        # Shin-guard plate (rounded plastic) over the shin.
        pygame.draw.ellipse(surf, _SOC_GUARD_D, (fx - 3, HY + 16, 6, 8))
        pygame.draw.ellipse(surf, _SOC_GUARD, (fx - 3, HY + 16, 5, 7))
        pygame.draw.line(surf, (255, 255, 255), (fx - 1, HY + 17), (fx - 1, HY + 20), 1)
        # Cleat hugging the feet line — slate-grey (not black) with a lighter
        # outline and a bright WHITE sole stripe so the feet read as feet and
        # never collide with the now-elsewhere dark of the ball.
        pygame.draw.ellipse(surf, _SOC_CLEAT_H, (fx - 4, HY + 22, 9, 5))
        pygame.draw.ellipse(surf, _SOC_CLEAT, (fx - 4, HY + 23, 9, 4))
        pygame.draw.line(surf, _SOC_WHITE, (fx - 3, HY + 24), (fx + 2, HY + 24), 1)  # sole stripe
        # Two stud ticks on the sole (kept ON the feet line, not below).
        for tx in (fx - 2, fx + 1):
            pygame.draw.line(surf, _SOC_CLEAT, (tx, HY + 26), (tx, HY + 27), 2)

    # --- HERO: pure-white soccer ball floated on the JERSEY ---------------------
    # Lifted OFF the feet line and onto the chest so it sits clear of the cleats
    # with a jersey-colour gap between them, drawn LAST + large so it is the
    # highest-contrast, most central mass on the figure — the instant soccer read.
    _soccer_ball(surf, BCX + 11, BCY + 6, 9)

    # --- Optional thin sweatband on the head (keeps the macaw reading) ----------
    # A slim royal-blue band across the brow with one white edge — a sport tell
    # that doesn't add headgear bulk, so Pip's macaw head stays recognizable.
    pygame.draw.line(surf, _SOC_BLUE_D, (HX - 11, CROWN_Y + 6), (HX + 12, CROWN_Y + 5), 4)
    pygame.draw.line(surf, _SOC_BLUE, (HX - 11, CROWN_Y + 5), (HX + 12, CROWN_Y + 4), 2)
    pygame.draw.line(surf, _SOC_WHITE, (HX - 9, CROWN_Y + 4), (HX + 6, CROWN_Y + 3), 1)


build = store_skins._make_skin(_paint)
