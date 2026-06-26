"""DESIGN 5 — THE ACE (Tennis).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted as a tennis pro: a crisp white collared POLO with a single
bold green diagonal sash painted over the torso, green-and-white wristbands, a
brow VISOR, and the hero read — a green OVAL strung RACKET held up in the near
wing (the head breaks the silhouette like the pirate cutlass tip).

The tennis BALL is deliberately gone: it ships as a separate matching PARCEL
item, so the costume must read as tennis from the RACKET + kit alone. That puts
the whole burden on the racket, so the OVAL ring is drawn large + bold with a
dark outer halo and the throat Y-struts carried strong — the strung head is the
unmistakable tell now.

The polo is painted OVER the scarlet body (the head stays the macaw so Pip still
reads as a parrot). All cloth + wristbands are held INSIDE the base bird
footprint; only the visor sits at the brow and only the racket head breaks the
outline as a held prop — nothing below the feet line, nothing balloons the body.

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
_TEN_BALL_C  = (20, 40, 18)           # near-black ball contour — pops it off the wing
_TEN_GRIP    = (40, 44, 52)           # dark racket grip wrap
_TEN_GRIP_H  = (96, 100, 110)         # grip wrap highlight


# Body centre in composite space (parrot body centre (32,32) + PARROT_DY=20).
BCX, BCY = 32, 52


def _racket(surf, hx, hy, hr):
    """The hero prop AND now the SOLE tennis tell (the ball ships separately).
    An OVAL strung racket head + a wrapped handle, held up so the head breaks the
    back/top silhouette. With nothing else to lean on, the read at 40px rides
    entirely on the bold green RING + its dark halo + the throat Y-struts, so the
    oval is drawn a touch larger and the frame thicker in three values, and the
    handle anchors it into the near wing below."""
    # Oval strung head — a tall ellipse. A dark void fill first so the green ring
    # reads as a rim around an open face, then the bold frame ring on top.
    rw, rh = int(hr * 1.7), int(hr * 2.1)        # tall tennis-racket oval (bumped)
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

    # Dark OUTER halo a couple px proud of the frame so the green ring always
    # separates from the day sky AND from the OTHER greens nearby (visor band +
    # green wing). With the ball gone this halo is what keeps the oval a clean
    # silhouette break at 40px, so it is drawn 2px and on both targets' skies.
    pygame.draw.ellipse(surf, _TEN_GREEN_D, face.inflate(4, 4), 2)

    # Bold green frame RING — the whole 40px read now. Drawn dark-then-bright in
    # three values and thicker than before so the oval keeps a lit, unmistakable
    # rim after the downscale.
    pygame.draw.ellipse(surf, _TEN_GREEN_D, face, 5)
    pygame.draw.ellipse(surf, _TEN_GREEN, face.inflate(-3, -3), 3)
    pygame.draw.ellipse(surf, _TEN_GREEN_H, face.inflate(-3, -3), 1)

    # Throat — two green struts splaying from the handle into the head, the
    # signature racket Y. With the ball gone this is the second tell, so it is
    # carried bolder so the V survives even when the cross strings vanish.
    ty = hy + rh
    pygame.draw.line(surf, _TEN_GREEN_D, (hx - 1, ty + 5), (hx - rw + 2, ty - 2), 5)
    pygame.draw.line(surf, _TEN_GREEN_D, (hx + 1, ty + 5), (hx + rw - 2, ty - 2), 5)
    pygame.draw.line(surf, _TEN_GREEN, (hx - 1, ty + 4), (hx - rw + 3, ty - 1), 3)
    pygame.draw.line(surf, _TEN_GREEN, (hx + 1, ty + 4), (hx + rw - 3, ty - 1), 3)

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
    mass on the figure — the second half of the instant tennis read.

    A near-black contour RING circles the whole ball first so the neon sphere
    pops off the busy rainbow wing the way the racket frame pops off the sky;
    without it the lime ball melts into the lime/scarlet feathers at 40px."""
    # Dark contour disc one px proud all round — the ring that survives downscale.
    pygame.draw.circle(surf, _TEN_BALL_C, (cx, cy), r + 1)
    pygame.draw.circle(surf, _TEN_BALL_D, (cx, cy + 1), r)
    pygame.draw.circle(surf, _TEN_BALL, (cx, cy), r)
    pygame.draw.circle(surf, _TEN_BALL_H, (cx - r // 2, cy - r // 2), max(1, r // 2))
    pygame.draw.circle(surf, _TEN_BALL_C, (cx, cy), r, 1)      # crisp dark rim
    # The two pale curved seams (the tennis-ball swoosh) — short arcs left/right.
    pygame.draw.arc(surf, _TEN_BALL_S, (cx - r - 2, cy - r, r + 1, r * 2),
                    -1.1, 1.1, 2)
    pygame.draw.arc(surf, _TEN_BALL_S, (cx + 1, cy - r, r + 1, r * 2),
                    math.pi - 1.1, math.pi + 1.1, 2)


def _paint(surf, _a):
    # --- White collared POLO on the FRONT CHEST ---------------------------------
    # Re-anchored to HX/HY (the same on-body position as the baseball jersey) so
    # the cloth sits up on the chest/front, not low toward the tail. White-filled
    # with a cool lower shade so it reads round, plus a dark contour so it stays
    # crisp on a bright day sky. Top at the shoulders (~HY+5), hem ~HY+23 — held
    # inside the footprint so it never balloons the bird.
    polo = [(HX - 14, HY + 5), (HX - 15, HY + 14), (HX - 11, HY + 23),
            (HX + 9, HY + 23), (HX + 12, HY + 14), (HX + 10, HY + 5),
            (HX + 4, HY + 2), (HX - 5, HY + 2)]
    _poly(surf, _TEN_POLO_D, polo)
    # Lit upper body of the cloth so the white isn't flat.
    _poly(surf, _TEN_POLO, [(HX - 13, HY + 5), (HX - 13, HY + 16),
                            (HX + 10, HY + 16), (HX + 10, HY + 5),
                            (HX + 4, HY + 2), (HX - 5, HY + 2)])
    pygame.draw.line(surf, _TEN_POLO_H, (HX - 11, HY + 6), (HX + 8, HY + 6), 1)
    # Crisp dark contour so the white polo separates from the day sky / pillars.
    pygame.draw.polygon(surf, _TEN_POLO_DD, polo, 1)

    # ONE bold diagonal SASH across the white chest — the single green tell that
    # survives the downscale. Dark-edged then bright so the sash keeps a lit core
    # after the shrink.
    pygame.draw.line(surf, _TEN_GREEN_D, (HX - 12, HY + 7), (HX + 9, HY + 21), 4)
    pygame.draw.line(surf, _TEN_GREEN, (HX - 12, HY + 7), (HX + 9, HY + 21), 3)
    pygame.draw.line(surf, _TEN_GREEN_H, (HX - 11, HY + 8), (HX + 7, HY + 19), 1)

    # --- Green-and-white WRISTBANDS at the wing roots ---------------------------
    # A terry band on the near wing (and a hint on the far) — a sport tell that
    # stays inside the silhouette.
    for wx, wy in ((HX + 11, HY + 18), (HX - 13, HY + 17)):
        pygame.draw.line(surf, _TEN_GREEN_D, (wx - 3, wy - 3), (wx + 3, wy + 3), 6)
        pygame.draw.line(surf, _TEN_POLO, (wx - 3, wy - 3), (wx + 3, wy + 3), 3)
        pygame.draw.line(surf, _TEN_GREEN, (wx - 2, wy - 2), (wx + 2, wy + 2), 1)

    # NOTE: the tennis BALL is intentionally NOT drawn — it ships as a separate
    # matching PARCEL item, so the racket + kit carry the tennis read alone. The
    # _tennis_ball helper is kept below unused in case the parcel reuses it.

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

    # --- RACKET drawn LAST so it OVERLAYS the polo/clothing ----------------------
    # Like the baseball BAT, the racket is painted last so the whole prop — head,
    # throat and handle — rests fully IN FRONT of the body, not buried behind it.
    # The handle drops into the near wing over the chest; the oval head still
    # breaks the top/back silhouette against open sky.
    _racket(surf, HX - 21, CROWN_Y + 2, 7)


build = store_skins._make_skin(_paint)
