"""THE PRO — basketball candidate DESIGN 1 of 5 (modern NBA, refined).

Scratch exploration only; NOT registered in store_skins.BUILDERS, so the live
roster is untouched. There is NO ball — it ships separately as a parcel, so the
KIT alone has to carry the basketball read.

Why this baseline leans hard on hoops-specific silhouette: the prior scratch
build read almost like the soccer kit, so THE PRO doubles down on the three
universal basketball tells that soccer does NOT share —

  1. a sleeveless TANK with bare shoulders + deep armhole scoops + thin straps
     (curved slivers of the scarlet body show through the armholes — the
     sleeveless tell, never a t-shirt or a soccer jersey),
  2. BAGGY KNEE shorts with a side stripe (vs soccer's short shorts + tall
     socks — the single loudest lower-body separator), and
  3. chunky white HIGH-TOPS with an accent stripe + grey sole (vs cleats).

Supporting cues: a big bold white number, a thin brow headband, a wristband on
the near wing. Court-orange / black / white palette so it can't be confused
with the soccer set's colours either. Pip's scarlet macaw head/beak/eye stay in
the open below the headband, so it still reads as a parrot wearing a kit.

Footprint law: every piece stays inside the base bird footprint — the headband
hugs the crown, the shorts hem sits above the feet line, and the high-tops sit
ON the feet line (~HY+21..27), never below it.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Court palette — orange tank is the hero value, mid-bright so the white number
# and black trim both pop on it and so it separates from the scarlet head above
# and a bright day sky. Three cloth values per garment for crisp form.
_ORANGE    = (224, 99, 43)           # #E0632B court orange (tank + shorts body)
_ORANGE_D  = (170, 66, 24)           # cloth shadow / armhole depth
_ORANGE_H  = (244, 140, 86)          # cloth highlight / near-side sheen
_BLACK     = (26, 28, 34)            # #1A1C22 trim / contour
_WHITE     = (244, 244, 248)         # #F4F4F8 number / piping / high-top
_WHITE_D   = (198, 202, 212)         # number shadow so it reads on light sky
_ACCENT    = (59, 107, 214)          # #3B6BD6 stripe accent
_SOLE      = (200, 204, 212)         # #C8CCD4 sole grey


def _paint(surf, _a):
    # Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
    BCX, BCY = 32, 52

    # ── BAGGY KNEE SHORTS first (behind the tank hem). The baggy long cut is a
    #    key separator from soccer's short shorts, so the legs are drawn WIDE
    #    and dropped to a low knee-length hem (~BCY+14) with an outward flare —
    #    a clearly loose, long short, not a fitted brief.
    shorts = [(BCX - 12, BCY + 5), (BCX + 13, BCY + 5),
              (BCX + 14, BCY + 14), (BCX + 2, BCY + 13),
              (BCX + 1, BCY + 14), (BCX - 13, BCY + 14)]
    _poly(surf, _ORANGE, shorts)
    # Centre vent split between the two baggy legs (the loose-short tell).
    pygame.draw.line(surf, _ORANGE_D, (BCX + 1, BCY + 8), (BCX + 1, BCY + 14), 2)
    # Lower-leg shading so each baggy leg has volume.
    _poly(surf, _ORANGE_D, [(BCX - 13, BCY + 11), (BCX - 7, BCY + 11),
                            (BCX - 8, BCY + 14), (BCX - 13, BCY + 14)])
    # Contrast SIDE STRIPE down the near baggy leg — black band carrying a thin
    # accent line, the modern uniform side panel.
    pygame.draw.line(surf, _BLACK, (BCX + 12, BCY + 6), (BCX + 13, BCY + 14), 3)
    pygame.draw.line(surf, _ACCENT, (BCX + 12, BCY + 6), (BCX + 13, BCY + 14), 1)

    # ── SLEEVELESS TANK over the torso. The cut is made unmistakably sleeveless:
    #    a narrow body panel with DEEP armhole scoops on both sides that expose
    #    curved BARE SHOULDERS, plus thin shoulder straps — the classic vest.
    jersey = [(BCX - 10, BCY - 6), (BCX + 9, BCY - 6),
              (BCX + 12, BCY + 1), (BCX + 11, BCY + 7),
              (BCX - 10, BCY + 7), (BCX - 12, BCY + 1)]
    _poly(surf, _ORANGE, jersey)
    # Three-value cloth shading: a shadowed off side + a near-side sheen so the
    # tank has rounded form, not a flat block.
    _poly(surf, _ORANGE_D, [(BCX - 12, BCY), (BCX - 8, BCY - 2),
                            (BCX - 7, BCY + 6), (BCX - 10, BCY + 7)])
    _poly(surf, _ORANGE_H, [(BCX + 9, BCY - 4), (BCX + 12, BCY + 1),
                            (BCX + 10, BCY + 6), (BCX + 8, BCY + 5)])

    # Thin shoulder STRAPS riding the wing roots — narrow enough that the bare
    # scarlet shoulder reads on the OUTSIDE of each strap (the sleeveless tell).
    _poly(surf, _ORANGE, [(BCX - 10, BCY - 6), (BCX - 5, BCY - 9),
                          (BCX - 3, BCY - 5), (BCX - 7, BCY - 2)])   # off strap
    _poly(surf, _ORANGE, [(BCX + 9, BCY - 6), (BCX + 4, BCY - 9),
                          (BCX + 2, BCY - 5), (BCX + 6, BCY - 2)])   # near strap

    # DEEP armhole scoops cut INTO the singlet on each side — a curved sliver of
    # the scarlet body shows in the gap between strap and side panel, so the
    # bare-shouldered cut is explicit even at the 40px truth read.
    pygame.draw.arc(surf, _ORANGE_D, (BCX + 2, BCY - 8, 12, 15), -1.1, 1.3, 2)  # near
    pygame.draw.arc(surf, _ORANGE_D, (BCX - 14, BCY - 8, 12, 15), 1.8, 4.2, 2)  # off
    # Black trim piping along the scoop neckline + the hem so the kit reads sharp.
    pygame.draw.lines(surf, _BLACK, False,
                      [(BCX - 4, BCY - 3), (BCX, BCY - 1), (BCX + 5, BCY - 3)], 1)
    pygame.draw.line(surf, _BLACK, (BCX - 9, BCY + 6), (BCX + 10, BCY + 6), 1)

    # ── BIG WHITE NUMBER "23" across the chest — the jersey headline. Drawn as
    #    two clean bold digits, shadowed 1px down-left so they survive on a light
    #    day sky. The "2" is a slim zig glyph, the "3" two stacked half-loops.
    nx, ny = BCX, BCY
    _draw_2(surf, nx - 6, ny - 5, _WHITE_D, _WHITE)
    _draw_3(surf, nx + 1, ny - 5, _WHITE_D, _WHITE)

    # ── HIGH-TOP SNEAKERS on the feet line. Chunky white boots with a black +
    #    accent stripe and a grey sole, sitting ON the feet line (~HY+21..27),
    #    never below it, so the bird keeps its true size. The bulky high collar
    #    is the hoops-shoe tell vs a low cleat.
    for fx in (26, 34):
        # Grey sole + a slim midsole shadow.
        pygame.draw.line(surf, _SOLE, (fx - 4, HY + 27), (fx + 5, HY + 27), 2)
        # Chunky white boot body with a high ankle collar.
        pygame.draw.rect(surf, _WHITE_D, (fx - 4, HY + 22, 9, 5), border_radius=2)
        pygame.draw.rect(surf, _WHITE, (fx - 4, HY + 20, 9, 5), border_radius=2)
        # Accent stripe swooping across the side, with a black lace flash above.
        pygame.draw.line(surf, _ACCENT, (fx - 3, HY + 24), (fx + 4, HY + 22), 2)
        pygame.draw.line(surf, _BLACK, (fx - 2, HY + 21), (fx + 1, HY + 21), 1)
        pygame.draw.line(surf, _WHITE, (fx - 3, HY + 20), (fx, HY + 20), 1)  # toe glint

    # ── WRISTBAND banking the near wing — the supporting basketball cue: a bold
    #    white sweatband with a thin accent midline, clearly worn on the forearm.
    wrx, wry = BCX + 12, BCY + 9
    pygame.draw.line(surf, _WHITE_D, (wrx - 3, wry + 4), (wrx + 5, wry - 2), 6)
    pygame.draw.line(surf, _WHITE, (wrx - 3, wry + 4), (wrx + 5, wry - 2), 4)
    pygame.draw.line(surf, _ACCENT, (wrx - 2, wry + 3), (wrx + 4, wry - 2), 1)

    # ── THIN BROW HEADBAND across the brow — the iconic non-ball hoops cue. A
    #    slim white band anchored ~1px down onto the brow with a black midline +
    #    a tiny accent flash, hugging the crown and leaving Pip's eye + beak in
    #    the open below it.
    by = CROWN_Y + 5
    pygame.draw.line(surf, _WHITE_D, (HX - 12, by + 1), (HX + 13, by), 6)   # shadow
    pygame.draw.line(surf, _WHITE, (HX - 12, by), (HX + 13, by - 1), 4)
    pygame.draw.line(surf, _BLACK, (HX - 11, by), (HX + 12, by - 1), 1)     # midline
    pygame.draw.line(surf, _ACCENT, (HX - 4, by - 1), (HX + 3, by - 1), 1)  # accent flash


def _draw_2(surf, x, y, sh, fg):
    """Slim bold '2' glyph (top bar, diagonal, base bar), 1px down-left shadow."""
    def glyph(c, ox, oy):
        pygame.draw.line(surf, c, (x + ox, y + oy), (x + 6 + ox, y + oy), 2)        # top
        pygame.draw.line(surf, c, (x + 6 + ox, y + oy), (x + 6 + ox, y + 4 + oy), 2)
        pygame.draw.line(surf, c, (x + 6 + ox, y + 4 + oy), (x + ox, y + 9 + oy), 2)  # diag
        pygame.draw.line(surf, c, (x + ox, y + 9 + oy), (x + 7 + ox, y + 9 + oy), 2)  # base
    glyph(sh, -1, 1)
    glyph(fg, 0, 0)


def _draw_3(surf, x, y, sh, fg):
    """Bold '3' glyph (two stacked right-bulging half-loops), 1px down-left shadow."""
    def glyph(c, ox, oy):
        pygame.draw.lines(surf, c, False,
                          [(x + ox, y + oy), (x + 5 + ox, y + oy),
                           (x + 6 + ox, y + 4 + oy), (x + 2 + ox, y + 4 + oy)], 2)   # top loop
        pygame.draw.lines(surf, c, False,
                          [(x + 2 + ox, y + 4 + oy), (x + 6 + ox, y + 4 + oy),
                           (x + 5 + ox, y + 9 + oy), (x + ox, y + 9 + oy)], 2)        # bottom loop
    glyph(sh, -1, 1)
    glyph(fg, 0, 0)


build = store_skins._make_skin(_paint)
