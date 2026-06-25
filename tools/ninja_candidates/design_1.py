"""SHADOWSTRIKE — classic black-shadow shinobi candidate for the ninja redraw.

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_ninja`` is untouched.

ROUND 2 re-base: the round-1 read failed because the base frame carried full
scarlet/blue/yellow macaw plumage, so SHADOWSTRIKE looked like the default
bird wearing a few dark accents. The concept IS a black bird, so the body is
now re-plumaged near-black through the 24-slot palette system (the way the
crimson/disco skins recolour the whole macaw) — every plumage, wing, head,
beak and foot slot floods to #11131A with #1F2430 cloth-highlight planes for
form. The aviator lenses are dropped so the wrap owns the face. With ALL
scarlet/blue/yellow gone, the costume accents finally read as crimson lines on
black instead of red-on-red.

At 40px the read is, in order of value: (1) a near-black bird-shaped shadow,
(2) a bright metal eye-slit looking forward, (3) a single steel-tipped ninjato
slung corner-to-corner — both tips glinting past the silhouette so it breaks
the egg shape no other costume has, and (4) crimson headband + trailing tails
and the obi as the only colour. Everything is held to mass + ONE accent per
object so the stack doesn't go mushy when it shrinks.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette

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


# Near-black re-plumage of the whole macaw. Every slot is shadow-black with a
# slightly lifted cloth-highlight on the chest/crown so the dark mass doesn't
# read as a flat void on night sky; tail/wing line work uses the deepest tone.
# Beak + foot blacked too (note 4: keep the beak/eye area dark) so nothing warm
# survives. Lenses are dropped by the base call so the eye-slit owns the face.
P_SHADOW = _pal(
    tail=[(13, 15, 21), (15, 17, 23), (19, 21, 28), (24, 27, 35)],
    tail_line=(8, 9, 13),
    body_shadow=(11, 12, 17),
    body_main=_BLACK,
    body_chest=(24, 27, 35),
    body_belly=(19, 21, 28),
    sheen=(120, 130, 150, 40),
    wing_main=(14, 16, 22),
    wing_dark=(8, 9, 13),
    wing_tip=(28, 31, 40),
    wing_secondary=None,
    wing_highlight=_CLOTH_H,
    head_shadow=(11, 12, 17),
    head_main=_BLACK,
    head_cheek=(20, 22, 30),
    head_crown=(24, 27, 35),
    lens_frame=(20, 22, 30),
    lens_body=(8, 9, 13),
    lens_tint=None,
    lens_glint=None,
    beak_main=(20, 22, 30),
    beak_dark=(8, 9, 13),
    beak_gloss=(48, 52, 64),
    foot=(18, 20, 26),
)


def _shadow_base(angle_deg):
    # Black bird with no aviators — the face wrap + eye-slit own the head.
    return _build_parrot_with_palette(angle_deg, P_SHADOW, draw_lenses=False)


def _paint(surf, wing_angle_deg):
    # Headband tails flick with the wing beat so the shadow feels alive; the
    # base wing angles run negative-on-downbeat, so a small share reads as the
    # ribbons trailing the dive.
    flick = int(round(wing_angle_deg * 0.12))

    # ── ninjato slung corner-to-corner (drawn FIRST, behind the body/head so
    #    only the ends poke out — the hero silhouette-breaker). One straight bar
    #    from below-left of the tail up to above-right past the crown. On a
    #    black body the HARD STEEL at BOTH tips is the single highest-value note
    #    at 40px, so each end overshoots the silhouette and gets a metal glint.
    lo = (HX - 31, HY + 28)        # scabbard butt, out past the tail
    hi = (HX + 19, CROWN_Y - 18)   # handle tip, up past the crown
    # Scabbard body: a thick black bar with a crimson sageo cord so the long
    # diagonal still reads as an object and not a stray outline at 40px.
    pygame.draw.line(surf, _SHADOW, lo, hi, 7)
    pygame.draw.line(surf, _BLACK, lo, hi, 5)
    pygame.draw.line(surf, _CLOTH_H,
                     (lo[0] + 2, lo[1] - 2), (hi[0] - 2, hi[1] + 2), 1)
    # The crimson sageo cord runs the whole length — the one accent line, and
    # it sits between two dark edges so the crimson reads as a line, not a wash.
    pygame.draw.line(surf, _CRIMSON,
                     (lo[0] + 1, lo[1] - 3), (hi[0] - 1, hi[1] + 3), 1)

    # Direction unit vector of the bar, to place guard + wraps + tips along it.
    dx, dy = hi[0] - lo[0], hi[1] - lo[1]
    blen = math.hypot(dx, dy)
    ux, uy = dx / blen, dy / blen
    px, py = -uy, ux                 # perpendicular, for the square guard

    # Square guard (tsuba) where the handle meets the blade, near the crown.
    gx = hi[0] - ux * 13
    gy = hi[1] - uy * 13
    guard = [
        (gx + px * 5, gy + py * 5), (gx - px * 5, gy - py * 5),
        (gx - px * 5 + ux * 3, gy - py * 5 + uy * 3),
        (gx + px * 5 + ux * 3, gy + py * 5 + uy * 3),
    ]
    _poly(surf, _BLACK, guard)
    pygame.draw.line(surf, _METAL_D, (gx + px * 4, gy + py * 4),
                     (gx - px * 4, gy - py * 4), 1)

    # Wrapped handle (tsuka) above the guard, poking past the crown — a couple
    # of cord-wrap ticks, then a HARD steel pommel cap glinting at the tip so
    # the top end of the sword clearly breaks the crown outline.
    for t in (4, 9):
        hxp = hi[0] - ux * t
        hyp = hi[1] - uy * t
        pygame.draw.line(surf, _CLOTH_H, (hxp + px * 2, hyp + py * 2),
                         (hxp - px * 2, hyp - py * 2), 1)
    pygame.draw.circle(surf, _METAL_D, (int(hi[0]), int(hi[1])), 3)
    pygame.draw.circle(surf, _METAL, (int(hi[0]), int(hi[1])), 2)
    pygame.draw.circle(surf, (255, 255, 255), (int(hi[0] - 1), int(hi[1] - 1)), 1)

    # Steel scabbard-butt cap (kojiri) glinting at the LOW tip past the tail —
    # the second hard metal note. The _METAL core is widened to r3 (was r2) so
    # both sword tips throw an EQUAL-weight steel break at 40px on night, where
    # the low tip was the softer of the two reads.
    pygame.draw.circle(surf, _METAL_D, (int(lo[0]), int(lo[1])), 4)
    pygame.draw.circle(surf, _METAL, (int(lo[0]), int(lo[1])), 3)
    pygame.draw.circle(surf, (255, 255, 255), (int(lo[0] + 1), int(lo[1] - 1)), 1)
    pygame.draw.circle(surf, (255, 255, 255), (int(lo[0]), int(lo[1] - 1)), 1)

    # ── headband tails streaming off the BACK of the skull (drawn before the
    #    head wrap so the wrap roots them). Two crimson ribbons, ~1 feather
    #    longer than R1 and aimed to trail OFF the silhouette into open sky
    #    (up-left, away from the body) so they read as motion, not body lines.
    bx, by = HX - 11, CROWN_Y + 2   # back-of-skull anchor
    for k, spread in ((0, 0), (1, 4)):
        t0 = (bx, by + k * 2)
        t1 = (bx - 13, by - 1 + flick + spread)
        t2 = (bx - 25, by + 2 + flick * 2 + spread)
        pygame.draw.lines(surf, _CRIMSON_D, False, [t0, t1, t2], 3)
        pygame.draw.lines(surf, _CRIMSON, False, [t0, t1, t2], 2)
    pygame.draw.line(surf, _CRIMSON_H, (bx, by), (bx - 11, by - 1 + flick), 1)

    # ── full face wrap (fukumen): black cloth over the whole head from the
    #    beak-base up past the crown, leaving a horizontal eye-slit.
    pygame.draw.ellipse(surf, _SHADOW, (HX - 13, CROWN_Y - 1, 26, 25))
    pygame.draw.ellipse(surf, _BLACK, (HX - 12, CROWN_Y, 24, 23))
    # Crown highlight so the black skull-cap doesn't vanish on night sky.
    pygame.draw.ellipse(surf, _CLOTH_H, (HX - 6, CROWN_Y + 1, 10, 4))
    # Lower-face wrap fold across the beak base, with a single cloth crease.
    fold = [(HX - 11, HY + 3), (HX + 12, HY + 1),
            (HX + 12, HY + 9), (HX - 10, HY + 11)]
    _poly(surf, _BLACK, fold)
    pygame.draw.line(surf, _CLOTH_H, (HX - 9, HY + 6), (HX + 10, HY + 4), 1)

    # Eye-slit: a bright metal band so Pip still reads as looking forward —
    # the keeper note, framed dark so it reads as a slit, not a bar.
    pygame.draw.rect(surf, (8, 9, 13), (HX - 6, HY - 3, 19, 7), border_radius=3)
    pygame.draw.rect(surf, _METAL, (HX - 4, HY - 1, 15, 3), border_radius=1)
    # Two darker pupils sitting in the slit so it reads as eyes, not a bar.
    pygame.draw.circle(surf, (20, 22, 30), (HX, HY), 1)
    pygame.draw.circle(surf, (20, 22, 30), (HX + 8, HY), 1)

    # ── hachimaki band over the wrap (crimson) — the brow accent that ties the
    #    trailing tails to the head. Dark cloth on both sides keeps it a line.
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

    # ── lower wing/tail back-edge rim: a single 1px cloth-highlight stroke
    #    tracing the underside silhouette that faces open sky, so the dark mass
    #    keeps a crisp lower edge against dark night backgrounds. Pure edge rim —
    #    no interior detail — held one tone above shadow so the day read (where
    #    the body already separates on bright sky) is untouched.
    pygame.draw.lines(surf, _CLOTH_H, False,
                      [(15, 40), (22, 44), (28, 47), (38, 47), (45, 43)], 1)

    # ── forearm wrap: ONE thicker black band near the wing root (R1's three
    #    1px-spaced bands went to mush at 40px) with a single crimson tie so the
    #    wing reads as a bound shinobi arm, not bare plumage.
    wrx, wry = 40, 47
    pygame.draw.line(surf, _SHADOW, (wrx - 6, wry + 1), (wrx + 7, wry - 2), 5)
    pygame.draw.line(surf, _BLACK, (wrx - 6, wry + 1), (wrx + 7, wry - 2), 3)
    pygame.draw.line(surf, _CRIMSON, (wrx - 5, wry - 1), (wrx + 6, wry - 3), 1)


build = store_skins._make_skin(_paint, base_fn=_shadow_base)
