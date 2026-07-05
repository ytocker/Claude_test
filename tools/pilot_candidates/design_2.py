"""Pilot costume — Design 2: ACE, the WW1/WW2 open-cockpit dogfighter.

Rework: the scarlet macaw is NOT recoloured. Pip keeps his natural red head,
blue wings and yellow beak — the ace kit is painted ON TOP as worn gear: a
dark leather flight helmet capping the crown, brass goggles shoved up on the
brow, a cream silk scarf streaming off the nape as a trailing pennant, a
shearling fur collar at the neckline, and a partial leather jacket patch on
the chest. The read is "the parrot wearing a pilot costume", not a brown bird.

Scratch exploration only — wired through _make_skin exactly like the production
store skins so the preview matches the shipped compositing, but never
registered in BUILDERS.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
import pygame
from game.store_skins import _make_skin, _poly, HX, HY, CROWN_Y


# Warm-brown flight-leather kit painted over the untouched scarlet macaw. The
# helmet is the darkest value so it caps the red head without hiding the face;
# the cream scarf is the single lightest note (and the motion tell); the tan
# fur + mid-brown jacket keep the chest reading as worn gear over red plumage.
_HELMET     = (60, 38, 18)          # dark leather flight cap (darkest mass)
_HELMET_H   = (120, 80, 40)         # seam highlight arc, crown→nape
_BRASS      = (62, 45, 18)          # goggle ring (weathered brass)
_BRASS_H    = (150, 110, 60)        # brass rim glint
_LENS       = (46, 60, 70)          # dark tinted goggle glass
_GLINT      = (238, 244, 250)       # lens/rivet white glint
_SCARF      = (230, 220, 200)       # cream silk pennant (lightest value)
_SCARF_D    = (186, 176, 156)       # scarf under-shadow
_SCARF_H    = (246, 240, 228)       # wind-lit upper edge
_FUR        = (185, 145, 90)        # shearling collar bump
_FUR_D      = (148, 112, 66)        # collar under-shadow (rounds each lump)
_FUR_H      = (210, 175, 120)       # fleece highlight fleck
_JACKET     = (80, 50, 25)          # leather jacket chest patch
_JACKET_H   = (112, 76, 42)         # jacket sheen so it reads as leather


def _paint(surf, wing_angle_deg):
    # ── 3 · Trailing cream scarf off the nape (hero motion tell) ────────────
    # Rooted at the nape and streaming BACK-and-DOWN, its forked tip overshooting
    # the tail into open sky so the cream crosses the left silhouette — that
    # break is the "diving ace" read. Cream, not red, so it never blends into the
    # scarlet plumage it lies over. Drawn first so the collar roots it at the neck.
    scarf = [(40, 37), (30, 41), (20, 45), (11, 49), (5, 51),
             (9, 53), (7, 56), (13, 52), (23, 48), (34, 43), (41, 40)]
    _poly(surf, _SCARF_D, [(x - 1, y + 1) for x, y in scarf])          # under-shadow
    _poly(surf, _SCARF, scarf)
    pygame.draw.lines(surf, _SCARF_H, False,
                      [(40, 37), (30, 41), (20, 45), (11, 49), (5, 51)], 1)
    pygame.draw.line(surf, _SCARF_H, (7, 56), (9, 53), 1)             # fork glint

    # ── 5 · Leather jacket chest patch (partial, red shows at the edges) ─────
    # A mid-brown leather oval over the upper breast so Pip reads as WEARING a
    # bomber jacket, without recolouring the body — the scarlet chest still
    # frames it on every side. One diagonal sheen sells the leather.
    pygame.draw.ellipse(surf, _JACKET, (30, 39, 15, 11))
    pygame.draw.line(surf, _JACKET_H, (33, 41), (42, 44), 1)

    # ── 4 · Shearling fur collar at the neckline ─────────────────────────────
    # A short arc of tan fleece bumps across the neck between the dark helmet and
    # the red chest — the dogfighter bomber-collar read. Cream-tan over a dark
    # rim so each lump reads round, with a fleck of brighter fleece on top.
    for bx, by in ((30, 42), (34, 40), (38, 39), (42, 40), (46, 42)):
        pygame.draw.circle(surf, _FUR_D, (bx, by + 1), 5)
        pygame.draw.circle(surf, _FUR, (bx, by), 4)
        pygame.draw.circle(surf, _FUR_H, (bx - 1, by - 1), 1)

    # ── 1 · Leather flight helmet capping the crown ──────────────────────────
    # A dark-brown shell over crown + back-of-head, its front edge kept above the
    # eye so the red face, aviators and yellow beak all read below it. This is the
    # deepest value on the bird, so the goggles pop off it.
    helmet = [(35, 41), (33, 34), (37, 28), (47, 26), (55, 29),
              (58, 34), (56, 37), (49, 36), (43, 38), (39, 43)]
    _poly(surf, _HELMET, helmet)
    # One seam highlight arc crown→nape so the leather reads as a rounded shell.
    pygame.draw.lines(surf, _HELMET_H, False,
                      [(53, 31), (47, 28), (41, 30), (37, 35), (36, 40)], 1)

    # ── 2 · Goggles shoved up on the brow (above the natural eye) ────────────
    # Two brass-ringed lenses parked high on the helmet forehead, well above the
    # aviators — the "just pulled up, ready to dive" tell. A 1px bridge joins
    # them; each lens gets a white glint so the glass reads at 40px.
    gy = 32
    for gx in (HX - 7, HX - 1):
        pygame.draw.circle(surf, _BRASS, (gx, gy), 4)
        pygame.draw.circle(surf, _LENS, (gx, gy), 3)
        pygame.draw.circle(surf, _BRASS_H, (gx, gy), 4, 1)
        pygame.draw.circle(surf, _GLINT, (gx - 1, gy - 1), 1)
    pygame.draw.line(surf, _BRASS, (HX - 6, gy - 2), (HX - 2, gy - 2), 1)  # nose bridge


build = _make_skin(_paint)
