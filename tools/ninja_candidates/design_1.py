"""SHADOWSTRIKE — classic black-shadow shinobi candidate for the ninja redraw.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_ninja`` is untouched. The current shipped ninja reads as a stray blue
blob (only its eye-slit carried), so the read here is rebuilt the way the
keeper skins do it: a signature shape pushed UP past the crown and OUT past
the tail. A single long ninjato slung corner-to-corner is the strongest
"NINJA" cue at 40px because it breaks the bird's egg silhouette into a
sword-on-the-back read no other costume in the roster has.

Everything stays near-black so the bird reads as a moving shadow against both
night and day sky; legibility between the stacked black objects comes from ONE
crimson accent line per object plus a hard cloth-highlight rim, never from
colour. The face wrap leaves a bright eye-slit so Pip still "looks" forward.
"""
import math
import pygame

from game import store_skins, parrot
from game.store_skins import HX, HY, CROWN_Y, _poly

# Shadow-black so the silhouette reads as one dark mass; the highlight cloth
# tone is the only thing separating stacked black objects from each other.
_BLACK   = (17, 19, 26)            # #11131A shadow body
_CLOTH_H = (31, 36, 48)            # #1F2430 cloth highlight (object separation)
_SHADOW  = (42, 47, 60)            # #2A2F3C wrap shadow / soft edge
_CRIMSON = (200, 16, 46)           # #C8102E crimson accent (one line per object)
_CRIMSON_D = (138, 12, 34)
_CRIMSON_H = (236, 70, 92)
_METAL   = (232, 234, 240)         # #E8EAF0 eye-slit + steel glint
_METAL_D = (150, 156, 170)


def _paint(surf, wing_angle_deg):
    # Headband tails flick with the wing beat so the shadow feels alive; the
    # base wing angles run negative-on-downbeat, so a small share reads as the
    # ribbons trailing the dive.
    flick = int(round(wing_angle_deg * 0.12))

    # ── ninjato slung corner-to-corner (drawn FIRST, behind the body/head so
    #    only the ends poke out — the hero silhouette-breaker). One straight bar
    #    from below-left of the tail up to above-right past the crown.
    lo = (HX - 30, HY + 26)        # scabbard butt, out past the tail
    hi = (HX + 18, CROWN_Y - 16)   # handle tip, up past the crown
    # Scabbard body: a thick black bar with a crimson throat-line so the long
    # diagonal still reads as an object and not a stray outline at 40px.
    pygame.draw.line(surf, _SHADOW, lo, hi, 7)
    pygame.draw.line(surf, _BLACK, lo, hi, 5)
    pygame.draw.line(surf, _CLOTH_H,
                     (lo[0] + 2, lo[1] - 2), (hi[0] - 2, hi[1] + 2), 1)
    # The crimson sageo cord runs the whole length — the one accent line.
    pygame.draw.line(surf, _CRIMSON,
                     (lo[0] + 1, lo[1] - 3), (hi[0] - 1, hi[1] + 3), 1)

    # Direction unit vector of the bar, to place guard + wraps along it.
    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    # Perpendicular, for the square guard.
    px, py = -uy, ux

    # Square guard (tsuba) two-thirds up, where the handle meets the blade.
    gx = hi[0] - ux * 14
    gy = hi[1] - uy * 14
    guard = [
        (gx + px * 5, gy + py * 5), (gx - px * 5, gy - py * 5),
        (gx - px * 5 + ux * 3, gy - py * 5 + uy * 3),
        (gx + px * 5 + ux * 3, gy + py * 5 + uy * 3),
    ]
    _poly(surf, _BLACK, guard)
    # Crimson tsuba wrap — accent line on the guard.
    pygame.draw.line(surf, _CRIMSON, (gx + px * 5, gy + py * 5),
                     (gx - px * 5, gy - py * 5), 2)
    pygame.draw.line(surf, _METAL_D, (gx + px * 4, gy + py * 4),
                     (gx - px * 4, gy - py * 4), 1)

    # Wrapped handle (tsuka) above the guard, poking past the crown — diamond
    # cord wraps shown as short crossing cloth-highlight ticks.
    for t in range(0, 14, 3):
        hxp = hi[0] - ux * t
        hyp = hi[1] - uy * t
        pygame.draw.line(surf, _CLOTH_H, (hxp + px * 2, hyp + py * 2),
                         (hxp - px * 2, hyp - py * 2), 1)
    # Pommel cap (kashira) glint at the very tip.
    pygame.draw.circle(surf, _METAL, (int(hi[0]), int(hi[1])), 2)
    pygame.draw.circle(surf, _METAL_D, (int(hi[0]), int(hi[1])), 2, 1)

    # ── headband tails streaming off the BACK of the skull (drawn before the
    #    head wrap so the wrap roots them). Two ribbons flicking with the beat.
    bx, by = HX - 11, CROWN_Y + 3   # back-of-skull anchor
    for k, spread in ((0, 0), (1, 4)):
        t0 = (bx, by + k * 2)
        t1 = (bx - 11, by + 2 + flick + spread)
        t2 = (bx - 20, by + 6 + flick * 2 + spread)
        pygame.draw.lines(surf, _CRIMSON_D, False, [t0, t1, t2], 3)
        pygame.draw.lines(surf, _CRIMSON, False, [t0, t1, t2], 2)
    pygame.draw.line(surf, _CRIMSON_H, (bx, by), (bx - 9, by + 2 + flick), 1)

    # ── full face wrap (fukumen): black cloth over the whole head from the
    #    beak-base up past the crown, leaving a horizontal eye-slit.
    pygame.draw.ellipse(surf, _SHADOW, (HX - 13, CROWN_Y - 1, 26, 25))
    pygame.draw.ellipse(surf, _BLACK, (HX - 12, CROWN_Y, 24, 23))
    # Crown highlight so the black skull-cap doesn't vanish on night sky.
    pygame.draw.ellipse(surf, _CLOTH_H, (HX - 6, CROWN_Y + 1, 10, 4))
    # Lower-face wrap fold across the beak base, with a cloth crease.
    fold = [(HX - 11, HY + 3), (HX + 12, HY + 1),
            (HX + 12, HY + 9), (HX - 10, HY + 11)]
    _poly(surf, _BLACK, fold)
    pygame.draw.line(surf, _CLOTH_H, (HX - 9, HY + 6), (HX + 10, HY + 4), 1)
    pygame.draw.line(surf, _SHADOW, (HX - 9, HY + 9), (HX + 10, HY + 7), 1)

    # Eye-slit: a bright metal band so Pip still reads as looking forward —
    # the single high-value note on the head, framed dark so it reads as a slit.
    pygame.draw.rect(surf, (8, 9, 13), (HX - 6, HY - 3, 19, 7), border_radius=3)
    pygame.draw.rect(surf, _METAL, (HX - 4, HY - 1, 15, 3), border_radius=1)
    # Two darker pupils sitting in the slit so it reads as eyes, not a bar.
    pygame.draw.circle(surf, (20, 22, 30), (HX, HY), 1)
    pygame.draw.circle(surf, (20, 22, 30), (HX + 8, HY), 1)

    # ── hachimaki band over the wrap (crimson) — the brow accent that ties the
    #    trailing tails to the head.
    by2 = CROWN_Y + 5
    pygame.draw.line(surf, _CRIMSON_D, (HX - 12, by2 + 1), (HX + 12, by2 - 1), 4)
    pygame.draw.line(surf, _CRIMSON, (HX - 12, by2), (HX + 12, by2 - 2), 3)
    pygame.draw.line(surf, _CRIMSON_H, (HX - 10, by2 - 1), (HX + 6, by2 - 2), 1)
    pygame.draw.circle(surf, _CRIMSON_D, (bx, by), 2)   # side knot

    # ── obi sash wrapped around the belly, knotted at the side with a hanging
    #    end. Body centre is ~(32, 52) in composite space.
    bcx, bcy = 31, 53
    sash = [(bcx - 17, bcy - 3), (bcx + 14, bcy - 6),
            (bcx + 15, bcy + 1), (bcx - 16, bcy + 4)]
    _poly(surf, _SHADOW, sash)
    sash2 = [(bcx - 17, bcy - 2), (bcx + 14, bcy - 5),
             (bcx + 14, bcy - 1), (bcx - 16, bcy + 2)]
    _poly(surf, _BLACK, sash2)
    pygame.draw.line(surf, _CLOTH_H, (bcx - 15, bcy - 2), (bcx + 12, bcy - 5), 1)
    # Side knot + short hanging end (crimson accent on the body object).
    kx, ky = bcx - 15, bcy
    pygame.draw.circle(surf, _CRIMSON_D, (kx, ky), 3)
    pygame.draw.circle(surf, _CRIMSON, (kx, ky), 2)
    _poly(surf, _CRIMSON_D, [(kx - 1, ky + 2), (kx + 3, ky + 2),
                             (kx + 1, ky + 9), (kx - 3, ky + 8)])
    _poly(surf, _CRIMSON, [(kx, ky + 3), (kx + 2, ky + 3),
                           (kx + 1, ky + 8), (kx - 1, ky + 8)])

    # ── forearm wraps: a few stacked black bands near the wing root so the
    #    wing reads as a bound shinobi arm, not bare plumage.
    wrx, wry = 40, 46
    for i in range(3):
        yy = wry + i * 3
        pygame.draw.line(surf, _BLACK, (wrx - 6, yy + 1), (wrx + 7, yy - 1), 3)
        pygame.draw.line(surf, _SHADOW, (wrx - 6, yy), (wrx + 7, yy - 2), 1)
    pygame.draw.line(surf, _CRIMSON, (wrx - 5, wry - 1), (wrx + 6, wry - 3), 1)

    # ── tabi: split-toe feet — darken and cleft the two foot tucks.
    for fx0, fx1, fy0, fy1 in ((26, 24, 65, 69), (34, 36, 65, 69)):
        pygame.draw.line(surf, _BLACK, (fx0, fy0), (fx1, fy1), 3)
        # Split-toe cleft.
        pygame.draw.line(surf, _SHADOW, (fx1 - 1, fy1 - 1), (fx1 + 1, fy1 - 3), 1)


build = store_skins._make_skin(_paint, base_fn=parrot._build_frame_bare)
