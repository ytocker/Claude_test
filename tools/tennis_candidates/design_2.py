"""DESIGN 2 — CLAY COURT (Tennis, Roland-Garros terracotta).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
art stays untouched. Pip the scarlet macaw kitted for the European clay season:
a white VISOR with a terracotta brow band, a warm-white POLO with a terracotta
side panel + orange placket piping, an ochre wristband on the near wing, and the
hero read — ONE bold clay-orange OVAL racket held up so the head still breaks the
back/top silhouette.

This is the warm-tone kit of the tennis set: the whole figure leans dusty orange
and ochre against cream so it reads as sun-baked clay, never the cool tournament
green of the base. The racket frame is the single most saturated mass, so the
SPORT reads off the orange oval before the bird does.

The polo is painted OVER the scarlet body (the head stays the macaw so Pip still
reads as a parrot). All cloth + wristband sit INSIDE the base bird footprint;
only the visor touches the brow and only the racket head breaks the outline as a
held prop — nothing balloons the body, nothing drops below the feet line.

NO ball (it ships as a separate matching parcel), so the racket carries the read
alone — hence the oval is drawn large + bold in three frame values with strong
throat struts so it survives the 40px downscale.

Headless render: tools/render_tennis_design_2.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Warm clay-court palette — terracotta + ochre on a cream white, with a dark
# clay shadow for contour and a near-black grip. The polo carries a cool-leaning
# shade value so the cream cloth still reads ROUND against a bright day sky
# without going muddy; the racket frame is one bold clay-orange ring (three
# values) so the OVAL HEAD survives downscale even when the thin strings vanish.
_CL_WHITE    = (244, 241, 234)        # #F4F1EA warm white polo/visor field
_CL_WHITE_D  = (210, 204, 192)        # cool lower shade (rounds the cream cloth)
_CL_WHITE_DD = (176, 168, 154)        # deep fold / contour so cream stays crisp
_CL_WHITE_H  = (253, 251, 244)        # cream highlight
_CL_TERRA    = (201, 98, 46)          # #C9622E terracotta racket frame + panel
_CL_TERRA_D  = (138, 62, 28)          # #8A3E1C clay shadow / deep frame
_CL_TERRA_H  = (228, 138, 84)         # terracotta highlight (frame top sheen)
_CL_OCHRE    = (224, 138, 60)         # #E08A3C ochre placket piping + wristband
_CL_OCHRE_H  = (244, 178, 110)        # ochre highlight
_CL_CREAM    = (236, 224, 204)        # #ECE0CC cream throat bridge / strings
_CL_STRING   = (236, 232, 222)        # warm-white strings (mains + crosses)
_CL_VOID     = (44, 30, 22)           # dark open-face void (no inner disc)
_CL_STR_DIM  = (120, 86, 64)          # low-contrast strings sitting on the void
_CL_GRIP     = (44, 38, 34)           # #2C2622 dark grip wrap
_CL_GRIP_H   = (104, 92, 82)          # grip wrap highlight


def _racket(surf, hx, hy, hr):
    """The hero prop AND the SOLE tennis tell (the ball ships separately). A clay
    -orange OVAL strung head + a wrapped handle held up so the head breaks the
    back/top silhouette. With nothing else to lean on, the read at 40px rides on
    the bold terracotta RING + its dark halo + the throat Y-struts, so the oval
    is drawn a touch larger and the frame thicker in THREE values, and the handle
    anchors it into the near wing below."""
    # Oval strung head — a tall ellipse read as ONE clean frame ring around an
    # OPEN strung face. A single bold clay frame with a dark VOID interior so it
    # never forms a circle-inside-a-circle.
    rw, rh = int(hr * 1.7), int(hr * 2.1)        # tall tennis-racket oval
    face = pygame.Rect(hx - rw, hy - rh, rw * 2, rh * 2)

    # Dark void interior + LOW-contrast warm strings so the inside reads as an
    # open strung face, NOT a filled bright disc. At 40px the centre stays empty
    # and only the frame survives.
    clip_prev = surf.get_clip()
    surf.set_clip(face)
    pygame.draw.ellipse(surf, _CL_VOID, face)
    for gx in range(face.left + 3, face.right - 2, 4):
        pygame.draw.line(surf, _CL_STR_DIM, (gx, face.top + 1), (gx, face.bottom - 1), 1)
    for gy in range(face.top + 3, face.bottom - 2, 4):
        pygame.draw.line(surf, _CL_STR_DIM, (face.left + 1, gy), (face.right - 1, gy), 1)
    # Two brighter strings crossing the lit upper-left quadrant so the mains read
    # as actual strings, not just texture, at hero scale.
    pygame.draw.line(surf, _CL_STRING, (face.centerx - 3, face.top + 2),
                     (face.centerx - 3, face.bottom - 2), 1)
    pygame.draw.line(surf, _CL_STRING, (face.left + 2, face.centery - 3),
                     (face.right - 2, face.centery - 3), 1)
    surf.set_clip(clip_prev)

    # ONE bold clay frame ring in THREE values: a dark keyline on the OUTER edge
    # for contrast against the sky, the terracotta frame itself, then a warm
    # sheen arc on the upper-left so the oval reads ROUND, not a flat ring.
    pygame.draw.ellipse(surf, _CL_TERRA_D, face.inflate(2, 2), 1)   # outer keyline
    pygame.draw.ellipse(surf, _CL_TERRA, face, 3)                   # the frame
    pygame.draw.arc(surf, _CL_TERRA_H, face.inflate(-1, -1), 0.6, 2.4, 1)  # top sheen

    # Throat — two clay struts splaying from the handle into the head, the
    # signature racket Y, with a CREAM throat bridge tucked between them. Carried
    # bold so the V survives even when the cross strings vanish at 40px.
    ty = hy + rh
    pygame.draw.line(surf, _CL_TERRA_D, (hx - 1, ty + 5), (hx - rw + 2, ty - 2), 5)
    pygame.draw.line(surf, _CL_TERRA_D, (hx + 1, ty + 5), (hx + rw - 2, ty - 2), 5)
    pygame.draw.line(surf, _CL_TERRA, (hx - 1, ty + 4), (hx - rw + 3, ty - 1), 3)
    pygame.draw.line(surf, _CL_TERRA, (hx + 1, ty + 4), (hx + rw - 3, ty - 1), 3)
    # Cream throat bridge — the small filled wedge between the struts.
    _poly(surf, _CL_CREAM, [(hx - 1, ty + 3), (hx + 1, ty + 3),
                            (hx + 2, ty - 1), (hx - 2, ty - 1)])

    # Wrapped handle dropping into the near wing (kept inside the silhouette).
    hbx, hby = hx, ty + 5
    htx, hty = hx + 4, hby + 12
    pygame.draw.line(surf, _CL_GRIP, (hbx, hby), (htx, hty), 6)
    pygame.draw.line(surf, _CL_GRIP_H, (hbx - 1, hby), (htx - 1, hty), 1)
    # Grip-wrap ticks so the handle reads as a leather grip, not a bare dowel.
    for t in (0.35, 0.7):
        wx = hbx + (htx - hbx) * t
        wy = hby + (hty - hby) * t
        pygame.draw.line(surf, _CL_GRIP_H, (wx - 2, wy + 1), (wx + 2, wy - 1), 1)
    pygame.draw.circle(surf, _CL_TERRA, (int(htx), int(hty)), 2)   # butt cap
    pygame.draw.circle(surf, _CL_TERRA_D, (int(htx), int(hty)), 2, 1)


def _paint(surf, _a):
    # --- Warm-white POLO on the FRONT CHEST (BELOW the head) ---------------------
    # Matched to the baseball jersey's vertical position (top ~HY+8, hem ~HY+23,
    # collar V never rising into the head) so the cloth sits on the chest and
    # NOTHING covers Pip's beak/eye/face. Cream-filled with a cool lower shade so
    # it reads round, plus a dark clay contour so it stays crisp on a bright sky.
    polo = [(HX - 13, HY + 8), (HX - 14, HY + 16), (HX - 11, HY + 23),
            (HX + 9, HY + 23), (HX + 12, HY + 16), (HX + 11, HY + 8),
            (HX + 4, HY + 9), (HX - 5, HY + 9)]
    _poly(surf, _CL_WHITE_D, polo)
    # Lit upper body of the cloth so the cream isn't flat.
    _poly(surf, _CL_WHITE, [(HX - 12, HY + 9), (HX - 12, HY + 18),
                            (HX + 10, HY + 18), (HX + 10, HY + 9),
                            (HX + 4, HY + 10), (HX - 5, HY + 10)])
    pygame.draw.line(surf, _CL_WHITE_H, (HX - 11, HY + 10), (HX + 8, HY + 10), 1)

    # Terracotta SIDE PANEL down the off-side (far-wing) edge — the warm-tone
    # block that gives the kit its clay-season colour without a green in sight.
    _poly(surf, _CL_TERRA, [(HX + 6, HY + 9), (HX + 11, HY + 9),
                            (HX + 12, HY + 16), (HX + 9, HY + 23),
                            (HX + 6, HY + 22)])
    _poly(surf, _CL_TERRA_H, [(HX + 6, HY + 10), (HX + 8, HY + 10),
                              (HX + 8, HY + 14), (HX + 6, HY + 15)])  # panel sheen
    pygame.draw.line(surf, _CL_TERRA_D, (HX + 6, HY + 9), (HX + 6, HY + 22), 1)

    # Small collar V at the polo's own top — sits ON the chest, never in the head.
    _poly(surf, _CL_WHITE_DD, [(HX - 5, HY + 9), (HX + 4, HY + 9),
                               (HX, HY + 13)])
    # Ochre placket PIPING down the centre — two thin verticals flanking the
    # opening so the polo has a buttoned front, the warm accent stripe.
    pygame.draw.line(surf, _CL_OCHRE, (HX - 1, HY + 12), (HX - 1, HY + 22), 2)
    pygame.draw.line(surf, _CL_OCHRE_H, (HX - 1, HY + 13), (HX - 1, HY + 20), 1)
    # Crisp dark clay contour so the cream polo separates from sky / pillars.
    pygame.draw.polygon(surf, _CL_WHITE_DD, polo, 1)

    # --- Ochre WRISTBAND at the near wing root -----------------------------------
    # A terry band on the near wing — a sport tell that stays inside the
    # silhouette, in warm ochre to match the placket and visor accents.
    wx, wy = HX - 13, HY + 19
    pygame.draw.line(surf, _CL_TERRA_D, (wx - 3, wy - 3), (wx + 3, wy + 3), 6)
    pygame.draw.line(surf, _CL_OCHRE, (wx - 3, wy - 3), (wx + 3, wy + 3), 3)
    pygame.draw.line(surf, _CL_OCHRE_H, (wx - 2, wy - 2), (wx + 2, wy + 2), 1)

    # --- Brow VISOR (keeps the macaw head reading) -------------------------------
    # A white sun visor: a curved brim sweeping over the beak + a terracotta band
    # across the brow, crown left OPEN so Pip still reads as the macaw. The only
    # headgear touching the head.
    by = CROWN_Y + 5
    brim = [(HX - 9, by), (HX + 14, by - 2), (HX + 18, by + 3),
            (HX + 14, by + 4), (HX - 9, by + 4)]
    _poly(surf, _CL_WHITE_D, brim)
    _poly(surf, _CL_WHITE, [(HX - 9, by), (HX + 14, by - 2), (HX + 16, by + 2),
                            (HX - 9, by + 2)])
    pygame.draw.line(surf, _CL_TERRA_D, (HX + 14, by - 2), (HX + 18, by + 3), 2)
    pygame.draw.line(surf, _CL_WHITE_H, (HX - 8, by), (HX + 12, by - 2), 1)
    # Terracotta band wrapping the brow above the brim — the clay accent up top.
    pygame.draw.line(surf, _CL_TERRA, (HX - 10, by - 1), (HX + 13, by - 3), 4)
    pygame.draw.line(surf, _CL_TERRA_H, (HX - 9, by - 2), (HX + 11, by - 4), 1)
    pygame.draw.line(surf, _CL_TERRA_D, (HX - 10, by + 1), (HX + 13, by - 1), 1)

    # --- RACKET drawn LAST so it OVERLAYS the polo/clothing -----------------------
    # Painted last so the whole prop — head, throat, handle — rests fully IN FRONT
    # of the body, not buried behind it. The handle drops into the near wing over
    # the chest; the oval head breaks the top/back silhouette against open sky.
    _racket(surf, HX - 21, CROWN_Y + 2, 7)


build = store_skins._make_skin(_paint)
