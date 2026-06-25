"""DESIGN 4 — THE UNDERTAKER (gothic nightmare gentleman) for skin_tophat.

Scratch exploration only — NOT registered in store_skins.BUILDERS. The whole
outfit is near-black, so the defence against an all-dark blob is baked in three
ways: the BODY itself is recoloured to charcoal-black (a dedicated base palette,
not the scarlet macaw — otherwise a bright red body bleeds through the coat and
the figure stops reading as a mourning gentleman); a continuous 2px PALE COOL
rim-light runs the back edge of hat-crown + coat so the silhouette separates
from a night sky as one clean lit contour; and the pale wing-collar + the silver
skull-cane knob are the two bright masses that carry the night read at 40px.
"""
from __future__ import annotations

import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly
from game.dollar_parrot_ghost import _pal, _build_parrot_with_palette

# ── BODY palette ─────────────────────────────────────────────────────────────
# A mourning macaw: near-black charcoal body/wing/head with a faint cool sheen,
# so the bird under the coat is already a dark gentleman rather than a scarlet
# parrot showing through. Pale-grey beak + cool rim values tie it to the costume
# silver. Lenses off — the monocle is painted by the costume.
_UND_BODY = _pal(
    tail=[(14, 14, 18), (20, 20, 26), (28, 28, 36), (40, 40, 50)],
    tail_line=(6, 6, 10),
    body_shadow=(8, 8, 12),
    body_main=(22, 22, 28),
    body_chest=(34, 34, 42),
    body_belly=(28, 28, 36),
    sheen=(120, 124, 138, 70),
    wing_main=(18, 18, 24),
    wing_dark=(8, 8, 12),
    wing_tip=(46, 48, 58),
    wing_secondary=None,
    wing_highlight=(106, 110, 120),
    head_shadow=(8, 8, 12),
    head_main=(26, 26, 33),
    head_cheek=(44, 44, 54),
    head_crown=(40, 40, 50),
    lens_frame=(60, 60, 72),
    lens_body=(6, 6, 10),
    lens_tint=None,
    lens_glint=None,
    beak_main=(150, 150, 162),
    beak_dark=(70, 70, 82),
    beak_gloss=(210, 210, 222),
    foot=(20, 20, 26),
)


def _und_base(angle_deg):
    return _build_parrot_with_palette(angle_deg, _UND_BODY, draw_lenses=False)


# Costume palette. Three black values (coat / shadow-lift / charcoal lapel) so a
# mourning suit still separates from itself on a dark sky; pale ash carries the
# collar + every silver glint; the wilted rose is the lone warm accent.
_UND_COAT    = (12, 12, 16)        # #0C0C10 matte black coat/hat
_UND_LAPEL   = (60, 60, 72)        # #3C3C48 charcoal lapels (value lift off black)
_UND_PALE    = (201, 199, 206)     # #C9C7CE collar/skull/silver soft glow
_UND_RIM     = (106, 110, 120)     # #6A6E78 cool back-edge rim-light
_UND_ROSE    = (74, 14, 24)        # #4A0E18 wilted rose
_UND_ROSE_H  = (120, 30, 44)       # rose highlight petal
_UND_PALE_D  = (150, 150, 162)     # collar shade so it reads as cloth, not paper
_UND_PALE_H  = (236, 236, 244)     # #ECECF4 brightest silver glint
_UND_SKIN    = (176, 174, 182)     # gaunt pale-grey face accent


def _paint(surf, _a):
    # ── BEHIND: black cane slung diagonally, the silver skull knob breaking the
    # back outline. Painted first so the body covers the shaft mid-section and
    # only the knob + tip overshoot the silhouette. The knob is the hero glint,
    # held clear of the body so it stays a pale glowing bead at 40px on night.
    knob = (HX - 23, CROWN_Y + 1)
    foot = (HX - 4, HY + 30)
    pygame.draw.line(surf, _UND_COAT, knob, foot, 3)          # dark-on-dark shaft
    pygame.draw.line(surf, (20, 20, 26), (foot[0], foot[1]),  # tip overshoot
                     (foot[0] + 2, foot[1] + 4), 3)
    # Silver skull knob — a clean glowing bead: bright core + cool halo so it
    # survives downscale and reads as the costume's hero glint on any sky.
    kx, ky = knob
    pygame.draw.circle(surf, _UND_RIM, (kx, ky), 4)            # 1px cool halo
    pygame.draw.circle(surf, _UND_PALE, (kx, ky), 3)
    pygame.draw.circle(surf, _UND_PALE_H, (kx, ky), 3, 1)     # bright rim
    pygame.draw.circle(surf, _UND_PALE_H, (kx - 1, ky - 1), 1)  # glow core
    pygame.draw.circle(surf, _UND_COAT, (kx - 1, ky + 1), 1)  # eye sockets
    pygame.draw.circle(surf, _UND_COAT, (kx + 1, ky + 1), 1)

    # ── BODY: long black frock coat over the charcoal body. A tall slim tower
    # (the Undertaker silhouette) with a continuous 2px cool rim down the BACK
    # edge so the coat separates from a night sky. Widened charcoal lapels split
    # the front into a clear V band so the chest reads as a coat at 40px.
    coat = [(HX - 14, HY + 8), (HX - 16, HY + 30), (HX - 10, HY + 36),
            (HX + 8, HY + 36), (HX + 12, HY + 28), (HX + 10, HY + 8)]
    _poly(surf, _UND_COAT, coat)
    # Continuous 2px cool rim-light tracing the back (left) edge + shoulder —
    # the single device that keeps the all-dark silhouette legible on dark sky.
    pygame.draw.lines(surf, _UND_RIM, False,
                      [(HX - 14, HY + 8), (HX - 16, HY + 30),
                       (HX - 10, HY + 36)], 2)
    # Charcoal-grey lapels — a wide V opening from the collar down the chest, a
    # clear 3-4px value step off the black coat so the front reads at 40px.
    _poly(surf, _UND_LAPEL, [(HX - 5, HY + 9), (HX - 9, HY + 28),
                             (HX - 3, HY + 24), (HX - 1, HY + 9)])
    _poly(surf, _UND_LAPEL, [(HX + 7, HY + 9), (HX + 10, HY + 26),
                             (HX + 3, HY + 24), (HX + 2, HY + 9)])
    # The dark chest V between the lapels reads as the shirt-front gap.
    _poly(surf, _UND_COAT, [(HX - 1, HY + 11), (HX + 2, HY + 11),
                            (HX + 1, HY + 26), (HX, HY + 26)])
    # Jet button + thin silver watch-chain swag across the lower chest.
    pygame.draw.circle(surf, (4, 4, 8), (HX, HY + 24), 2)
    pygame.draw.circle(surf, _UND_LAPEL, (HX - 1, HY + 23), 1)
    pygame.draw.lines(surf, _UND_PALE_D, False,
                      [(HX - 5, HY + 20), (HX - 1, HY + 24), (HX + 5, HY + 20)], 1)
    pygame.draw.line(surf, _UND_PALE_H, (HX + 5, HY + 20), (HX + 6, HY + 18), 1)

    # ── FEET: black buttoned ankle boots with dull silver spat buttons. A value
    # step over the coat hem, poked below the body to break the lower outline;
    # a rim glint keeps them off a dark floor.
    for fx in (HX - 7, HX + 1):
        pygame.draw.rect(surf, _UND_COAT, (fx, HY + 33, 8, 8), border_radius=2)
        pygame.draw.line(surf, _UND_RIM, (fx, HY + 34), (fx, HY + 40), 1)
        pygame.draw.line(surf, _UND_COAT, (fx, HY + 41), (fx + 9, HY + 41), 2)  # sole
        pygame.draw.circle(surf, _UND_PALE_D, (fx + 6, HY + 35), 1)  # spat button
        pygame.draw.circle(surf, _UND_PALE_D, (fx + 6, HY + 38), 1)

    # ── NECK: pale ash wing-collar + black silk cravat. The brightest mass on
    # the whole figure — a crisp pale wedge under the beak that anchors the
    # silhouette read on night, paired with the silver skull knob.
    _poly(surf, _UND_PALE, [(HX - 7, HY + 4), (HX + 8, HY + 4),
                            (HX + 6, HY + 12), (HX - 1, HY + 16),
                            (HX - 5, HY + 12)])
    pygame.draw.line(surf, _UND_PALE_H, (HX - 6, HY + 5), (HX + 7, HY + 5), 1)
    _poly(surf, _UND_PALE_D, [(HX - 1, HY + 16), (HX - 5, HY + 12),
                              (HX - 3, HY + 13)])      # collar fold shade
    # Wing-collar tabs — two small pale points pinched at the throat.
    _poly(surf, _UND_PALE, [(HX - 4, HY + 11), (HX, HY + 14), (HX - 3, HY + 16)])
    _poly(surf, _UND_PALE, [(HX + 5, HY + 11), (HX, HY + 14), (HX + 4, HY + 16)])
    # Black silk cravat knot + drop.
    pygame.draw.circle(surf, _UND_COAT, (HX, HY + 14), 3)
    _poly(surf, _UND_COAT, [(HX - 2, HY + 15), (HX + 2, HY + 15),
                            (HX + 1, HY + 22), (HX - 1, HY + 22)])
    pygame.draw.circle(surf, _UND_LAPEL, (HX - 1, HY + 13), 1)  # silk sheen

    # ── HEAD: gaunt pale-grey face accent on the near cheek so the face reads as
    # a sunken pallor under the brim.
    pygame.draw.circle(surf, _UND_SKIN, (HX + 6, HY + 2), 4)
    pygame.draw.circle(surf, _UND_SKIN, (HX + 8, HY - 2), 3)

    # Thin drooping black moustache under the beak.
    pygame.draw.lines(surf, _UND_COAT, False,
                      [(HX + 2, HY + 4), (HX + 6, HY + 6), (HX + 7, HY + 10)], 2)
    pygame.draw.lines(surf, _UND_COAT, False,
                      [(HX + 11, HY + 4), (HX + 9, HY + 6), (HX + 9, HY + 10)], 2)

    # Smoked monocle on the NEAR eye — dark lens, silver rim, a thin chain.
    mx, my = HX + 8, HY - 1
    pygame.draw.circle(surf, (6, 6, 10), (mx, my), 4)       # smoked dark lens
    pygame.draw.circle(surf, _UND_PALE, (mx, my), 4, 1)     # silver rim
    pygame.draw.circle(surf, _UND_PALE_H, (mx - 1, my - 1), 1)  # rim glint
    pygame.draw.line(surf, _UND_PALE_D, (mx + 1, my + 4), (HX + 6, HY + 8), 1)

    # ── HAT: extra-tall matte-black topper. Brim, then a tall crown rising well
    # above CROWN_Y, with a continuous 2px PALE COOL rim down its back edge so
    # the black hat survives a night sky. A crepe mourning band + wilted rose
    # finish it.
    cy = CROWN_Y
    pygame.draw.ellipse(surf, _UND_COAT, (HX - 17, cy + 1, 34, 8))   # brim
    pygame.draw.ellipse(surf, _UND_LAPEL, (HX - 15, cy + 1, 30, 4))
    pygame.draw.line(surf, _UND_RIM, (HX - 13, cy + 1), (HX + 12, cy + 1), 1)

    top_y = cy - 22                       # extra-tall crown
    pygame.draw.rect(surf, _UND_COAT, (HX - 9, top_y, 18, 24))
    # Continuous 2px cool rim down the BACK (left) edge of the crown — joins the
    # coat back-rim into one clean lit contour so the whole figure separates
    # from a night sky as a single silhouette.
    pygame.draw.line(surf, _UND_RIM, (HX - 9, top_y + 2), (HX - 9, cy + 1), 2)
    pygame.draw.line(surf, _UND_LAPEL, (HX + 7, top_y + 2), (HX + 7, cy - 2), 1)  # front sheen
    # Cool top rim — keeps the crown top off a dark floor.
    pygame.draw.ellipse(surf, _UND_RIM, (HX - 9, top_y - 2, 18, 6))
    pygame.draw.ellipse(surf, _UND_COAT, (HX - 8, top_y - 1, 16, 4))
    pygame.draw.line(surf, _UND_PALE_D, (HX - 6, top_y - 1), (HX + 4, top_y - 1), 1)

    # Black crepe mourning band wrapping the crown base — a matte band a touch
    # off the coat black, edged with a thin cool line so it still reads as a band.
    pygame.draw.rect(surf, (7, 7, 11), (HX - 9, cy - 4, 18, 5))
    pygame.draw.line(surf, _UND_RIM, (HX - 9, cy - 4), (HX + 8, cy - 4), 1)

    # Small wilted dark rose tucked in the band on the near side — the lone warm
    # accent. A tight rose cluster + one drooping petal so it reads as a flower.
    rx, ry = HX + 6, cy - 2
    pygame.draw.circle(surf, _UND_ROSE, (rx, ry), 3)
    pygame.draw.circle(surf, _UND_ROSE_H, (rx - 1, ry - 1), 1)
    _poly(surf, _UND_ROSE, [(rx + 1, ry + 1), (rx + 4, ry + 3), (rx + 1, ry + 4)])
    pygame.draw.line(surf, (40, 50, 38), (rx - 2, ry + 2), (rx - 4, ry + 5), 1)  # wilted stem


build = store_skins._make_skin(_paint, base_fn=_und_base)
