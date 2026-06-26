"""DESIGN 3 — NEON BASELINER (Tennis).

Scratch exploration only — NOT registered in store_skins.BUILDERS; production
art is untouched. Pip the scarlet macaw kitted for a hard-court NIGHT session
under the lights: a sleek VOLT headband, an athletic-cut cobalt+lime polo with
a diagonal volt slash, a volt wristband, and the hero read — a TECH GRAPHITE
racket (electric-blue frame, lime throat/bumper, volt strings on a near-black
void) held up in the near wing so the head still breaks the top/back silhouette.

This is the COLD high-saturation kit of the tennis set: the deliberate
night-read champion. The strings glow volt-green on a near-black bed and the
frame is electric blue, so on a dark sky the racket is the brightest, coolest
mass on the figure and the SPORT reads before the bird does. By day the same
saturation holds up because every cloth/frame value carries a dark contour.

The polo is painted OVER the scarlet body (the head stays the macaw so Pip is
still a parrot). All cloth + wristband sit INSIDE the base bird footprint; only
the headband touches the head (crown open) and only the racket head breaks the
outline as a held prop — nothing balloons the body, nothing drops below the
feet. NO ball: it ships as a separate matching parcel, so the racket carries
the tennis read alone.

Headless render: tools/render_tennis_design_3.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Electric-blue + volt/lime modern sportswear. The frame is electric blue with
# a lime throat/bumper so the racket is two-tone (frame vs. throat) and reads as
# a tech graphite stick, not a flat ring; the strings are VOLT on a near-black
# void so the bed glows at night without forming a second bright disc. Every
# cloth value carries a deep-cobalt contour so the saturated kit stays crisp on
# a bright DAY sky too.
_NB_BLUE     = (20, 80, 200)          # #1450C8 electric-blue frame + polo field
_NB_BLUE_D   = (12, 46, 120)          # #0C2E78 deep cobalt shade / contour
_NB_BLUE_H   = (74, 140, 240)         # frame top sheen so the oval reads round
_NB_VOLT     = (182, 242, 58)         # #B6F23A volt/lime accent + strings
_NB_VOLT_D   = (120, 168, 30)         # volt shade (rounds the throat / band)
_NB_VOLT_H   = (218, 255, 132)        # volt highlight glint
_NB_WHITE    = (242, 244, 240)        # #F2F4F0 white trim / placket
_NB_WHITE_D  = (188, 194, 196)        # trim shade
_NB_VOID     = (16, 18, 24)           # near-black strung-face void (no disc)
_NB_GRIP     = (21, 23, 28)           # #15171C matte grip wrap
_NB_GRIP_H   = (70, 76, 88)           # grip wrap highlight tick
_NB_MESH     = (10, 38, 96)           # dark cobalt mesh side panel (body shade)


def _racket(surf, hx, hy, hr):
    """The hero prop AND the sole tennis tell. A tech-graphite OVAL head — an
    electric-blue frame with a lime throat/bumper and a VOLT strung bed on a
    near-black void — over a wrapped matte grip. Held up so the head breaks the
    back/top silhouette. Built to read at 40px on a DARK sky: the cool blue ring
    + glowing volt mesh is the brightest cold mass on an otherwise warm bird."""
    # Tall tennis oval read as ONE clean frame ring around an OPEN strung face;
    # no inner disc, so it never becomes a circle-inside-a-circle.
    rw, rh = int(hr * 1.7), int(hr * 2.1)
    face = pygame.Rect(hx - rw, hy - rh, rw * 2, rh * 2)

    # Near-black void + VOLT strings: the bed glows green on its own dark bed so
    # at night the strung face is luminous, yet stays a mesh (not a filled disc)
    # because the void between the lines keeps the centre dark at downscale.
    clip_prev = surf.get_clip()
    surf.set_clip(face)
    pygame.draw.ellipse(surf, _NB_VOID, face)
    for gx in range(face.left + 3, face.right - 2, 3):          # mains
        pygame.draw.line(surf, _NB_VOLT, (gx, face.top + 1), (gx, face.bottom - 1), 1)
    for gy in range(face.top + 3, face.bottom - 2, 3):          # crosses
        pygame.draw.line(surf, _NB_VOLT_D, (face.left + 1, gy), (face.right - 1, gy), 1)
    surf.set_clip(clip_prev)

    # ONE bold electric-blue frame ring with a 1px cobalt keyline on the OUTER
    # edge for crispness on a bright sky, plus a top sheen so the oval reads
    # ROUND, and a thin lime BUMPER on the head's crown (the tech-frame tell).
    pygame.draw.ellipse(surf, _NB_BLUE_D, face.inflate(2, 2), 1)    # outer keyline
    pygame.draw.ellipse(surf, _NB_BLUE, face, 3)                    # the frame
    pygame.draw.arc(surf, _NB_BLUE_H, face.inflate(-1, -1), 0.5, 2.6, 1)  # top sheen
    pygame.draw.arc(surf, _NB_VOLT, face.inflate(-2, -2), 3.6, 5.8, 2)    # lime bumper

    # Throat — two LIME struts splaying from the grip into the head, the racket
    # Y. Lime here (vs. the blue frame) so the throat separates from the frame
    # and survives even when the cross strings vanish at downscale.
    ty = hy + rh
    pygame.draw.line(surf, _NB_VOLT_D, (hx - 1, ty + 5), (hx - rw + 2, ty - 2), 5)
    pygame.draw.line(surf, _NB_VOLT_D, (hx + 1, ty + 5), (hx + rw - 2, ty - 2), 5)
    pygame.draw.line(surf, _NB_VOLT, (hx - 1, ty + 4), (hx - rw + 3, ty - 1), 3)
    pygame.draw.line(surf, _NB_VOLT, (hx + 1, ty + 4), (hx + rw - 3, ty - 1), 3)

    # Matte grip dropping into the near wing (kept inside the silhouette), with
    # wrap ticks + a lime butt cap so the handle reads as a wrapped grip end.
    hbx, hby = hx, ty + 5
    htx, hty = hx + 4, hby + 12
    pygame.draw.line(surf, _NB_GRIP, (hbx, hby), (htx, hty), 6)
    pygame.draw.line(surf, _NB_GRIP_H, (hbx - 1, hby), (htx - 1, hty), 1)
    for t in (0.35, 0.7):
        wx = hbx + (htx - hbx) * t
        wy = hby + (hty - hby) * t
        pygame.draw.line(surf, _NB_GRIP_H, (wx - 2, wy + 1), (wx + 2, wy - 1), 1)
    pygame.draw.circle(surf, _NB_VOLT, (int(htx), int(hty)), 2)     # butt cap
    pygame.draw.circle(surf, _NB_VOLT_H, (int(htx) - 1, int(hty) - 1), 1)


def _paint(surf, _a):
    # --- Athletic-cut POLO on the FRONT CHEST (BELOW the head) ------------------
    # Matched to the baseball jersey's vertical position (top ~HY+8, hem ~HY+23,
    # collar V never rising into the head) so the cloth sits on the chest and
    # NOTHING covers Pip's beak/eye/face. Electric-blue field with a deep-cobalt
    # lower shade so it reads round, and a dark contour so it stays crisp on a
    # bright day sky. Held inside the footprint so it never balloons the bird.
    polo = [(HX - 13, HY + 8), (HX - 14, HY + 16), (HX - 11, HY + 23),
            (HX + 9, HY + 23), (HX + 12, HY + 16), (HX + 11, HY + 8),
            (HX + 4, HY + 9), (HX - 5, HY + 9)]
    _poly(surf, _NB_BLUE_D, polo)
    # Lit upper body of the cloth so the blue isn't flat.
    _poly(surf, _NB_BLUE, [(HX - 12, HY + 9), (HX - 12, HY + 17),
                           (HX + 10, HY + 17), (HX + 10, HY + 9),
                           (HX + 4, HY + 10), (HX - 5, HY + 10)])
    pygame.draw.line(surf, _NB_BLUE_H, (HX - 11, HY + 10), (HX + 8, HY + 10), 1)

    # Dark mesh SIDE PANEL on the off-side — a cool cobalt wedge that tucks the
    # waist so the polo reads as an athletic cut, not a flat box.
    _poly(surf, _NB_MESH, [(HX + 7, HY + 11), (HX + 12, HY + 16),
                           (HX + 9, HY + 23), (HX + 7, HY + 22)])

    # White-trimmed collar V + placket at the polo's own top — sits ON the chest,
    # never in the head. The white trim is the crispest light edge on the kit.
    _poly(surf, _NB_WHITE, [(HX - 5, HY + 9), (HX + 4, HY + 9), (HX, HY + 13)])
    _poly(surf, _NB_WHITE_D, [(HX - 3, HY + 10), (HX + 2, HY + 10), (HX, HY + 12)])
    pygame.draw.line(surf, _NB_WHITE, (HX, HY + 13), (HX, HY + 20), 1)     # placket
    pygame.draw.line(surf, _NB_WHITE_D, (HX + 1, HY + 13), (HX + 1, HY + 20), 1)

    # ONE bold diagonal VOLT slash across the chest — the single lime tell that
    # survives downscale. Cobalt-edged then volt then a bright core so the slash
    # keeps a lit centre after the shrink. Dropped with the polo so it stays on
    # the chest, NOT crossing the collar.
    pygame.draw.line(surf, _NB_BLUE_D, (HX - 12, HY + 13), (HX + 6, HY + 22), 4)
    pygame.draw.line(surf, _NB_VOLT, (HX - 12, HY + 13), (HX + 6, HY + 22), 3)
    pygame.draw.line(surf, _NB_VOLT_H, (HX - 11, HY + 14), (HX + 4, HY + 20), 1)

    # --- VOLT WRISTBAND at the near wing root ----------------------------------
    # A terry band at the cuff — a sport tell that stays inside the silhouette.
    # Volt over cobalt so it pops on both day and night; a hint on the far cuff.
    for wx, wy in ((HX + 11, HY + 20), (HX - 13, HY + 19)):
        pygame.draw.line(surf, _NB_BLUE_D, (wx - 3, wy - 3), (wx + 3, wy + 3), 6)
        pygame.draw.line(surf, _NB_VOLT, (wx - 3, wy - 3), (wx + 3, wy + 3), 3)
        pygame.draw.line(surf, _NB_VOLT_H, (wx - 2, wy - 2), (wx + 2, wy + 2), 1)

    # --- Sleek VOLT HEADBAND (keeps the macaw head reading; crown OPEN) ---------
    # A thin electric-blue band wrapping the brow with a lime edge — the only
    # headgear that touches the head. No brim/dome: the crown stays open so Pip
    # is unmistakably the macaw, and the band reads as modern sweatband, not a
    # cap. Sits at the brow line below the crown so it never covers the eye/beak.
    by = CROWN_Y + 4
    pygame.draw.line(surf, _NB_BLUE_D, (HX - 11, by + 1), (HX + 13, by - 1), 5)   # contour
    pygame.draw.line(surf, _NB_BLUE, (HX - 11, by), (HX + 13, by - 2), 4)         # blue band
    pygame.draw.line(surf, _NB_VOLT, (HX - 11, by - 2), (HX + 13, by - 4), 1)     # lime top edge
    pygame.draw.line(surf, _NB_VOLT, (HX - 11, by + 2), (HX + 13, by), 1)         # lime bottom edge
    pygame.draw.line(surf, _NB_BLUE_H, (HX - 9, by - 1), (HX + 6, by - 2), 1)     # sheen
    # A tiny volt brand notch at the band's centre — a modern sportswear tell.
    pygame.draw.circle(surf, _NB_VOLT_H, (HX + 1, by - 1), 1)

    # --- RACKET drawn LAST so it OVERLAYS the polo/clothing ---------------------
    # Like the baseball BAT, painted last so the whole prop — head, throat and
    # grip — rests fully IN FRONT of the body. The grip drops into the near wing
    # over the chest; the oval head still breaks the top/back silhouette against
    # open sky, where its cold blue frame + glowing volt bed win the night read.
    _racket(surf, HX - 21, CROWN_Y + 2, 7)


build = store_skins._make_skin(_paint)
