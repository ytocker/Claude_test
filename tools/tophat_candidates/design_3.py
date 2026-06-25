"""THE LORD — aristocratic-peer gentleman candidate (DESIGN 3 of 5).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
``skin_tophat`` is untouched.

Concept: keep the TOP HAT as the identity anchor, then dress Pip as a ceremonial
peer. The hero — the one mark that distinguishes this from the four vertical
gentleman concepts — is a bright RED-and-gold SASH running shoulder-to-hip as a
single bold DIAGONAL across a deep-navy coat. Medals are kept tiny and clustered
so they read as glints of metal, not clutter that muddies the sash at 40px. Navy
is carried at three values so the coat separates from the sky on day AND night.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Navy ceremonial coat — three values so the dark body separates from both a pale
# day sky and a near-black night sky (a single navy on night collapsed to nothing).
_LD_NAVY    = (27, 42, 82)         # #1B2A52
_LD_NAVY_D  = (16, 26, 54)
_LD_NAVY_H  = (58, 80, 134)        # raised edge so the coat reads on night sky

# Hat near-black with a crisp light rim so the black topper survives any sky.
_LD_HAT     = (16, 16, 24)         # #101018
_LD_HAT_D   = (8, 8, 14)
_LD_HAT_H   = (88, 90, 110)        # rim glint that keeps black off the sky floor

# Gold — sash border, hat band, medals, cane knob, monocle. Soft sheen, not flat.
_LD_GOLD    = (231, 194, 74)       # #E7C24A
_LD_GOLD_D  = (158, 128, 44)
_LD_GOLD_H  = (255, 232, 150)

# Sash field — the bold scarlet diagonal the gold borders frame.
_LD_SASH    = (180, 21, 34)        # #B41522
_LD_SASH_D  = (120, 14, 24)

# Jabot lace at the throat — soft off-white blob.
_LD_JABOT   = (237, 233, 221)      # #EDE9DD
_LD_JABOT_D = (196, 192, 178)

_LD_GREY    = (176, 178, 186)      # grey Vandyke goatee + moustache
_LD_GREY_D  = (120, 122, 132)
_LD_EBONY   = (28, 26, 32)         # ebony walking-stick shaft
_LD_SILVER  = (214, 218, 226)      # one silver medal so the cluster isn't all gold
_LD_SILVER_D = (150, 154, 164)
_LD_SHOE    = (18, 18, 24)         # court shoe black
_LD_SHOE_H  = (70, 72, 86)


def _medal(surf, cx, cy, face, face_d):
    """A round chest medal: tiny ribbon bar above a two-value disc with a glint.
    Kept ~5px so two or three cluster without muddying the sash at 40px."""
    pygame.draw.rect(surf, _LD_SASH_D, (cx - 2, cy - 4, 4, 2))        # ribbon bar
    pygame.draw.circle(surf, face_d, (cx, cy), 3)
    pygame.draw.circle(surf, face, (cx, cy), 2)
    pygame.draw.circle(surf, _LD_GOLD_H, (cx - 1, cy - 1), 1)         # glint


def _paint(surf, _a):
    # ── GOLD-TOPPED EBONY WALKING STICK slung diagonally BEHIND the body (painted
    #    first so the body covers all but the parts that overshoot the silhouette).
    #    The gold knob sits up near the slung wing; the shaft sweeps down past the
    #    lower body so the tip breaks the outline against open sky.
    knob = (HX - 6, HY + 18)
    tip  = (HX - 26, HY + 40)
    pygame.draw.line(surf, _LD_EBONY, (knob[0], knob[1]), (tip[0], tip[1]), 3)
    pygame.draw.line(surf, _LD_NAVY_H, (knob[0] - 1, knob[1] + 1),
                     (tip[0] - 1, tip[1] + 1), 1)                     # shaft glint
    pygame.draw.circle(surf, _LD_GOLD_D, knob, 4)
    pygame.draw.circle(surf, _LD_GOLD, knob, 3)
    pygame.draw.circle(surf, _LD_GOLD_H, (knob[0] - 1, knob[1] - 1), 1)
    _poly(surf, _LD_GOLD, [(tip[0] - 1, tip[1] - 1), (tip[0] + 2, tip[1] + 1),
                           (tip[0] - 2, tip[1] + 2)])                 # ferrule cap

    # ── NAVY CEREMONIAL COAT painted OVER the body. A trapezoid across body centre
    #    (~32,52) with gold-trim front edges + a small collar notch. Three navy
    #    values so the coat holds its shape against day AND night skies.
    coat = [(HX - 24, HY + 8), (HX - 4, HY + 6), (HX - 2, HY + 36),
            (HX - 26, HY + 38)]
    _poly(surf, _LD_NAVY_D, coat)
    inner = [(HX - 22, HY + 10), (HX - 5, HY + 8), (HX - 4, HY + 34),
             (HX - 24, HY + 35)]
    _poly(surf, _LD_NAVY, inner)
    # Raised highlight down the near front so the coat reads as a lit panel, not a
    # flat dark blob, on the night half.
    pygame.draw.line(surf, _LD_NAVY_H, (HX - 5, HY + 9), (HX - 4, HY + 33), 2)
    # Gold trim tracing the coat's front edge — the formalwear cue.
    pygame.draw.line(surf, _LD_GOLD_D, (HX - 4, HY + 7), (HX - 2, HY + 35), 2)
    pygame.draw.line(surf, _LD_GOLD, (HX - 4, HY + 7), (HX - 3, HY + 35), 1)

    # ── DIAGONAL RED+GOLD SASH (THE HERO). A single bold band shoulder-to-hip,
    #    gold-bordered on BOTH edges so it stays the dominant accent and survives
    #    the downscale. Drawn BEFORE the medals so the medals sit on top yet stay
    #    small; the sash is never let collapse to mud under them.
    sh = (HX - 2, HY + 6)            # high at the near shoulder
    hp = (HX - 26, HY + 34)          # low at the off hip
    pygame.draw.line(surf, _LD_GOLD_D, sh, hp, 11)                    # outer gold edge
    pygame.draw.line(surf, _LD_GOLD, sh, hp, 9)
    pygame.draw.line(surf, _LD_SASH_D, sh, hp, 6)                     # scarlet field
    pygame.draw.line(surf, _LD_SASH, (sh[0], sh[1] - 1), (hp[0], hp[1] - 1), 4)
    # One bright gold rail along the upper border — the glint that keeps the
    # diagonal singing at 40px against both skies.
    pygame.draw.line(surf, _LD_GOLD_H, (sh[0] + 3, sh[1] - 2),
                     (hp[0] + 3, hp[1] - 2), 1)

    # ── MEDALS clustered at the chest — two gold, one silver, each tiny. Set just
    #    off the sash so they read as a row of decorations without crowding the
    #    diagonal into clutter.
    _medal(surf, HX - 11, HY + 22, _LD_GOLD, _LD_GOLD_D)
    _medal(surf, HX - 16, HY + 25, _LD_SILVER, _LD_SILVER_D)
    _medal(surf, HX - 8, HY + 27, _LD_GOLD, _LD_GOLD_D)

    # ── JABOT lace at the throat — a soft off-white blob with a shadow underside
    #    so it reads as spilling lace, the bright value that frames the goatee.
    jx, jy = HX - 2, HY + 9
    pygame.draw.ellipse(surf, _LD_JABOT_D, (jx - 5, jy - 1, 10, 9))
    pygame.draw.ellipse(surf, _LD_JABOT, (jx - 4, jy - 1, 8, 7))
    pygame.draw.line(surf, _LD_JABOT_D, (jx, jy + 1), (jx, jy + 6), 1)  # lace fold

    # ── COURT SHOES over the feet — black with a gold buckle each, a small dark
    #    note that grounds the formal look without competing with the sash.
    for fx in (28, 34):
        pygame.draw.ellipse(surf, _LD_SHOE, (fx - 3, 64, 7, 5))
        pygame.draw.line(surf, _LD_SHOE_H, (fx - 2, 64), (fx + 2, 64), 1)
        pygame.draw.rect(surf, _LD_GOLD, (fx - 1, 65, 2, 2))           # buckle
        pygame.draw.rect(surf, _LD_GOLD_H, (fx - 1, 65, 1, 1))

    # ── TOP HAT (the identity anchor) — near-black topper with a crisp light top
    #    rim so it survives 40px, a GOLD band at the base, and a tiny gold cockade
    #    pin on the side. Same geometry family as the production redraw so it stays
    #    unmistakably a top hat.
    cy = CROWN_Y
    pygame.draw.ellipse(surf, _LD_HAT_D, (HX - 17, cy + 1, 34, 8))     # brim
    pygame.draw.ellipse(surf, _LD_HAT, (HX - 16, cy, 32, 5))
    pygame.draw.line(surf, _LD_HAT_H, (HX - 13, cy + 1), (HX + 13, cy + 1), 1)
    top_y = cy - 17
    pygame.draw.rect(surf, _LD_HAT_D, (HX - 9, top_y, 19, 19))         # tall crown
    pygame.draw.rect(surf, _LD_HAT, (HX - 8, top_y, 16, 18))
    pygame.draw.line(surf, _LD_HAT_H, (HX - 6, top_y + 1), (HX - 6, cy - 2), 2)
    pygame.draw.ellipse(surf, _LD_HAT_H, (HX - 9, top_y - 2, 19, 6))   # bright top rim
    pygame.draw.ellipse(surf, _LD_HAT, (HX - 8, top_y - 1, 17, 4))
    # Gold satin band at the crown base.
    pygame.draw.rect(surf, _LD_GOLD_D, (HX - 9, cy - 3, 19, 4))
    pygame.draw.rect(surf, _LD_GOLD, (HX - 9, cy - 3, 19, 3))
    pygame.draw.line(surf, _LD_GOLD_H, (HX - 8, cy - 3), (HX + 8, cy - 3), 1)
    # Tiny gold cockade pin on the near side of the band.
    pygame.draw.circle(surf, _LD_GOLD_H, (HX + 9, cy - 1), 2)
    pygame.draw.circle(surf, _LD_GOLD_D, (HX + 9, cy - 1), 2, 1)

    # ── FACE — grey pointed Vandyke goatee + thin moustache under the beak, and a
    #    gold-rimmed monocle on the near eye with a glint. The grey goatee reads as
    #    the noble's tell against the scarlet head.
    # Thin moustache spreading under the beak.
    pygame.draw.line(surf, _LD_GREY_D, (HX - 3, HY + 6), (HX + 8, HY + 6), 2)
    pygame.draw.line(surf, _LD_GREY, (HX - 2, HY + 5), (HX + 7, HY + 5), 1)
    # Pointed Vandyke goatee tapering to a chin point.
    _poly(surf, _LD_GREY_D, [(HX, HY + 8), (HX + 6, HY + 8), (HX + 2, HY + 15)])
    _poly(surf, _LD_GREY, [(HX + 1, HY + 8), (HX + 5, HY + 8), (HX + 2, HY + 13)])
    # Gold-rimmed monocle on the near eye + a thin cord.
    mx, my = HX + 6, HY
    pygame.draw.circle(surf, _LD_GOLD, (mx, my), 5, 2)
    pygame.draw.circle(surf, (255, 255, 255), (mx - 2, my - 2), 1)
    pygame.draw.line(surf, _LD_GOLD_D, (mx + 4, my + 3), (mx + 7, HY + 9), 1)


build = store_skins._make_skin(_paint)
