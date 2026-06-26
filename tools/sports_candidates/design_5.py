"""DESIGN 5 — THE ACE (Tennis).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a tennis pro: a crisp white collared POLO with a green
accent stripe painted over the torso, green-and-white wristbands, a brow VISOR,
the hero read — a green OVAL strung RACKET held up in the near wing (the head
breaks the silhouette like the pirate cutlass tip), and a bright neon-yellow
TENNIS BALL at the wing.

The polo is painted OVER the scarlet body (the head stays the macaw so Pip still
reads as a parrot). All cloth + ball + wristbands are held INSIDE the base bird
footprint; only the visor sits at the brow and only the racket head breaks the
outline as a held prop — nothing below the feet line, nothing balloons the body.

The 40px challenge is the strings: they are too thin to carry the read, so the
RACKET HEAD is a bold green RING (frame) over a neon-ball-matched void, and the
neon ball + green ring together carry "tennis" at the downscale — the cross
strings are only a near-detail bonus.

Headless render: tools/sports_candidates/render_design_5.py.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# White polo + tournament green; neon-green ball; clean white strings.
# The polo gets a cool shade value so the white cloth reads ROUND on a bright
# day sky without washing out, and a dark contour edge so it stays crisp. The
# racket frame is one bold mid-green ring (two values) so the OVAL HEAD survives
# the downscale even when the thin strings disappear; the ball is the single
# most saturated mass on the figure so the SPORT reads before the bird.
_TEN_POLO    = (244, 244, 240)        # #F4F4F0 polo white
_TEN_POLO_D  = (206, 208, 204)        # polo cool shade (rounds the cloth)
_TEN_POLO_DD = (170, 174, 172)        # deep fold / contour so white stays crisp
_TEN_POLO_H  = (255, 255, 252)        # polo highlight
_TEN_GREEN   = (42, 157, 74)          # #2A9D4A racket frame + accent stripe
_TEN_GREEN_D = (26, 107, 54)          # #1B6B36 green shadow / visor trim
_TEN_GREEN_H = (96, 206, 124)         # green highlight
_TEN_STRING  = (242, 242, 242)        # #F2F2F2 cross strings
_TEN_BALL    = (203, 232, 74)         # #CBE84A neon tennis-ball green
_TEN_BALL_D  = (162, 192, 52)         # ball shade so the sphere reads round
_TEN_BALL_H  = (230, 250, 150)        # ball curve highlight
_TEN_BALL_S  = (250, 252, 235)        # ball seam (the pale tennis swoosh)
_TEN_GRIP    = (40, 44, 52)           # dark racket grip wrap
_TEN_GRIP_H  = (96, 100, 110)         # grip wrap highlight


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _racket(surf, hx, hy, hr):
    """The hero prop: an OVAL strung racket head + a wrapped handle, held up so
    the head breaks the back/top silhouette. The read at 40px is carried by the
    bold green RING (the strings are a near-detail bonus, not the read), so the
    frame is drawn thick in two values and the throat/handle anchor it into the
    near wing below."""
    # Oval strung head — a tall ellipse. A dark void fill first so the green ring
    # reads as a rim around an open face, then the bold frame ring on top.
    rw, rh = int(hr * 1.5), int(hr * 1.9)        # tall tennis-racket oval
    face = pygame.Rect(hx - rw, hy - rh, rw * 2, rh * 2)

    # Cross strings INSIDE the face — thin pale lines on a faint dark mesh so the
    # near-detail reads as a strung face; clipped to the oval so they don't spill.
    clip_prev = surf.get_clip()
    surf.set_clip(face)
    # Faint backing so the white strings have something to sit on at the head.
    pygame.draw.ellipse(surf, (70, 86, 70), face)
    for gx in range(face.left + 2, face.right - 1, 4):
        pygame.draw.line(surf, _TEN_STRING, (gx, face.top + 1), (gx, face.bottom - 1), 1)
    for gy in range(face.top + 2, face.bottom - 1, 4):
        pygame.draw.line(surf, _TEN_STRING, (face.left + 1, gy), (face.right - 1, gy), 1)
    surf.set_clip(clip_prev)

    # Bold green frame RING — the actual 40px read. Drawn dark-then-bright so the
    # oval keeps a lit edge after the downscale.
    pygame.draw.ellipse(surf, _TEN_GREEN_D, face, 4)
    pygame.draw.ellipse(surf, _TEN_GREEN, face.inflate(-2, -2), 3)
    pygame.draw.ellipse(surf, _TEN_GREEN_H, face.inflate(-2, -2), 1)

    # Throat — two short green struts splaying from the handle into the head, the
    # signature racket Y that reads even when strings vanish.
    ty = hy + rh
    pygame.draw.line(surf, _TEN_GREEN_D, (hx - 1, ty + 5), (hx - rw + 2, ty - 1), 4)
    pygame.draw.line(surf, _TEN_GREEN_D, (hx + 1, ty + 5), (hx + rw - 2, ty - 1), 4)
    pygame.draw.line(surf, _TEN_GREEN, (hx - 1, ty + 4), (hx - rw + 3, ty), 2)
    pygame.draw.line(surf, _TEN_GREEN, (hx + 1, ty + 4), (hx + rw - 3, ty), 2)

    # Wrapped handle dropping into the near wing (kept inside the silhouette).
    hbx, hby = hx, ty + 5
    htx, hty = hx + 4, hby + 12
    pygame.draw.line(surf, _TEN_GRIP, (hbx, hby), (htx, hty), 6)
    pygame.draw.line(surf, _TEN_GRIP_H, (hbx - 1, hby), (htx - 1, hty), 1)
    # A couple of grip-wrap ticks so the handle reads as a leather grip.
    for t in (0.35, 0.7):
        wx = hbx + (htx - hbx) * t
        wy = hby + (hty - hby) * t
        pygame.draw.line(surf, _TEN_GRIP_H, (wx - 2, wy + 1), (wx + 2, wy - 1), 1)
    pygame.draw.circle(surf, _TEN_GREEN, (int(htx), int(hty)), 2)   # butt cap


def _tennis_ball(surf, cx, cy, r):
    """A bright neon tennis ball with the pale curved seam. The most saturated
    mass on the figure — the second half of the instant tennis read."""
    pygame.draw.circle(surf, _TEN_BALL_D, (cx, cy + 1), r)
    pygame.draw.circle(surf, _TEN_BALL, (cx, cy), r)
    pygame.draw.circle(surf, _TEN_BALL_H, (cx - r // 2, cy - r // 2), max(1, r // 2))
    pygame.draw.circle(surf, _TEN_BALL_D, (cx, cy), r, 1)      # holds a round edge
    # The two pale curved seams (the tennis-ball swoosh) — short arcs left/right.
    pygame.draw.arc(surf, _TEN_BALL_S, (cx - r - 2, cy - r, r + 1, r * 2),
                    -1.1, 1.1, 2)
    pygame.draw.arc(surf, _TEN_BALL_S, (cx + 1, cy - r, r + 1, r * 2),
                    math.pi - 1.1, math.pi + 1.1, 2)


def _paint(surf, _a):
    # --- Racket held UP in the near wing (painted FIRST so the body covers the
    # handle root and only the head + upper frame break the silhouette, like the
    # pirate cutlass tip). Head sits high-back so it clears against open sky. ----
    _racket(surf, HX - 20, CROWN_Y + 1, 7)

    # --- White collared POLO over the torso -------------------------------------
    # A clean cloth block clipped to the chest, white-filled with a cool lower
    # shade so it reads round, a dark contour so it stays crisp on a bright day
    # sky, then the green accent stripe + collar. Kept inside the footprint (top
    # at the shoulders ~HY+5, hem ~HY+22) so it never balloons the bird.
    polo = [(BCX - 14, BCY - 8), (BCX - 15, BCY - 1), (BCX - 13, BCY + 11),
            (BCX + 13, BCY + 11), (BCX + 15, BCY - 1), (BCX + 13, BCY - 8),
            (BCX + 4, BCY - 11), (BCX - 5, BCY - 11)]
    _poly(surf, _TEN_POLO_D, polo)
    # Lit upper body of the cloth so the white isn't flat.
    _poly(surf, _TEN_POLO, [(BCX - 13, BCY - 8), (BCX - 13, BCY + 3),
                            (BCX + 13, BCY + 3), (BCX + 13, BCY - 8),
                            (BCX + 4, BCY - 11), (BCX - 5, BCY - 11)])
    pygame.draw.line(surf, _TEN_POLO_H, (BCX - 11, BCY - 7), (BCX + 9, BCY - 7), 1)
    # Crisp dark contour so the white polo separates from the day sky / pillars.
    pygame.draw.polygon(surf, _TEN_POLO_DD, polo, 1)

    # Green accent stripe down the near side + along the hem — the team colour.
    pygame.draw.line(surf, _TEN_GREEN, (BCX + 11, BCY - 7), (BCX + 10, BCY + 9), 3)
    pygame.draw.line(surf, _TEN_GREEN_H, (BCX + 11, BCY - 6), (BCX + 11, BCY + 2), 1)
    pygame.draw.line(surf, _TEN_GREEN, (BCX - 12, BCY + 10), (BCX + 12, BCY + 10), 2)

    # Polo placket — a short vertical button strip + a green collar V so it reads
    # as a tennis polo, not a plain tee.
    pygame.draw.line(surf, _TEN_POLO_DD, (BCX, BCY - 9), (BCX, BCY + 2), 1)
    pygame.draw.circle(surf, _TEN_GREEN_D, (BCX, BCY - 5), 1)
    pygame.draw.circle(surf, _TEN_GREEN_D, (BCX, BCY - 1), 1)
    # Collar — two green-edged white flaps at the neck.
    _poly(surf, _TEN_POLO, [(BCX - 6, BCY - 11), (BCX, BCY - 6),
                            (BCX - 3, BCY - 11)])
    _poly(surf, _TEN_POLO, [(BCX + 5, BCY - 11), (BCX, BCY - 6),
                            (BCX + 2, BCY - 11)])
    pygame.draw.line(surf, _TEN_GREEN, (BCX - 6, BCY - 11), (BCX, BCY - 6), 1)
    pygame.draw.line(surf, _TEN_GREEN, (BCX + 5, BCY - 11), (BCX, BCY - 6), 1)

    # --- Green-and-white WRISTBANDS at the wing roots ---------------------------
    # A terry band on the near wing (and a hint on the far) — a sport tell that
    # stays inside the silhouette.
    for wx, wy in ((BCX + 13, BCY + 5), (BCX - 13, BCY + 4)):
        pygame.draw.line(surf, _TEN_GREEN_D, (wx - 3, wy - 3), (wx + 3, wy + 3), 6)
        pygame.draw.line(surf, _TEN_POLO, (wx - 3, wy - 3), (wx + 3, wy + 3), 3)
        pygame.draw.line(surf, _TEN_GREEN, (wx - 2, wy - 2), (wx + 2, wy + 2), 1)

    # --- HERO 2: neon TENNIS BALL at the near wing ------------------------------
    # Drawn LAST so it sits clearly in front — the brightest, most saturated mass
    # on the figure. Held inside the silhouette at the lower near wing, resting on
    # the feet line, never below it.
    _tennis_ball(surf, BCX + 12, HY + 19, 6)

    # --- Brow VISOR (keeps the macaw head reading) ------------------------------
    # A white sun visor: a green-trimmed band across the brow + a curved brim over
    # the beak. Only headgear that touches the head — the crown stays open so Pip
    # is still clearly the macaw.
    by = CROWN_Y + 5
    # Curved brim sweeping forward over the beak.
    brim = [(HX - 9, by), (HX + 14, by - 2), (HX + 18, by + 3),
            (HX + 14, by + 4), (HX - 9, by + 4)]
    _poly(surf, _TEN_POLO_D, brim)
    _poly(surf, _TEN_POLO, [(HX - 9, by), (HX + 14, by - 2), (HX + 16, by + 2),
                            (HX - 9, by + 2)])
    pygame.draw.line(surf, _TEN_GREEN_D, (HX + 14, by - 2), (HX + 18, by + 3), 2)
    pygame.draw.line(surf, _TEN_POLO_H, (HX - 8, by), (HX + 12, by - 2), 1)
    # Green band wrapping the brow above the brim.
    pygame.draw.line(surf, _TEN_GREEN, (HX - 10, by - 1), (HX + 13, by - 3), 4)
    pygame.draw.line(surf, _TEN_GREEN_H, (HX - 9, by - 2), (HX + 11, by - 4), 1)
    pygame.draw.line(surf, _TEN_GREEN_D, (HX - 10, by + 1), (HX + 13, by - 1), 1)


build = store_skins._make_skin(_paint)
