"""DESIGN 4 — THE REFEREE (Soccer / Football, v5).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so
production stays untouched. Pip the scarlet macaw kitted as the match
official. The jersey reads as actual CLOTHING through shirt-construction
elements: a referee V-neck collar at the true neckline, a centre placket
seam, a garment outline with dual rim-lights, and the hero match props
(yellow + red booking cards plus the steel whistle).

The kit is true near-black so the read is BLACK at the 40px downscale, not a
charcoal-blue plane: the lit plane is a single 2px sliver on the near edge.
White is rationed hard — the collar V at the neckline and the boot/sock
stripes only — so the steel whistle disc and the paired booking cards own the
eye. The dual rim-lights (cool grey on the far back contour, neutral on the
near front) are the only thing that keeps a true-black garment from dissolving
into the night sky.

v5 fixes per art-direction: the V-neck collar is lifted UP to the actual
neckline (just below the chin) and widened so it reads above the props; the
bright hero elements are rationed (cards made dominant and overlapped, the
whistle lanyard darkened to a dull cord so only the disc stays metal-bright,
the front sleeve cuff darkened so it stops fighting the props); the cap brim
is thickened and angled so it never reads as a flat forehead band.

Headless render: tools/soccer_candidates/render_design_4.py.
"""
import pygame

from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
BCX, BCY = 32, 52

# Near-black referee kit. The lit plane is kept dark on purpose so the read is
# BLACK, not a charcoal-blue plane; white + steel + yellow are the only
# high-value notes, reserved for the neckline collar and hero props.
_REF_BLACK = (26, 28, 34)     # true near-black jersey body
_REF_LIT   = (36, 38, 46)     # lit plane (barely visible, 2px sliver only)
_REF_RIM   = (40, 42, 50)     # garment outline
_REF_BACK  = (120, 124, 130)  # far-side rim-light (carries the night separation)
_REF_WHITE = (230, 235, 245)  # collar V
_REF_YCRD  = (255, 221, 70)   # yellow card
_REF_RCRD  = (220, 50, 40)    # red card
_REF_WSTL  = (180, 185, 195)  # whistle steel
_REF_LANY  = (80, 85, 95)     # dark lanyard cord — NOT white, so only the disc is bright
_REF_CUFF  = (60, 65, 70)     # darkened front sleeve cuff (no longer a bright note)
_BOOT_D    = (26, 24, 32)
_BOOT_S    = (200, 205, 215)
_SHORTS_D  = (20, 24, 30)
_SOCK_D    = (26, 28, 34)


def _paint(surf, _a):
    # Full-body referee jersey polygon — left edge anchored on BCX so the kit
    # wraps the WHOLE visible body (x=20..58), reading as a worn garment rather
    # than a chest patch.
    jersey = [
        (BCX - 10, HY + 7),   # left shoulder
        (BCX - 12, HY + 17),  # left hip
        (BCX - 8,  HY + 23),  # left hem
        (HX + 8,   HY + 23),  # right hem
        (HX + 11,  HY + 18),  # right hip
        (HX + 9,   HY + 8),   # right shoulder
    ]

    # 1 — PEAKED OFFICIALS CAP. Drawn first so the body/jersey overlaps its
    #     base; a forward-brimmed dome on the crown, never a brow headband, so
    #     the open macaw face is preserved. The brim is a thickened, tilted
    #     leading edge (2px) with a clear angular shape so it never reads as a
    #     flat horizontal forehead band.
    pygame.draw.ellipse(surf, _REF_BLACK, (HX - 8, CROWN_Y + 2, 17, 9))
    pygame.draw.ellipse(surf, (36, 38, 46), (HX - 7, CROWN_Y + 2, 15, 7))   # subtle dome highlight
    # Angular forward brim: dark wedge underlay, then a 2px tilted leading edge
    # that dips toward the tip so the brim peaks forward, not flat across the brow.
    pygame.draw.polygon(surf, _REF_BLACK, [
        (HX - 1, CROWN_Y + 8), (HX + 13, CROWN_Y + 7),
        (HX + 12, CROWN_Y + 11), (HX - 1, CROWN_Y + 11)])
    pygame.draw.line(surf, (70, 72, 76),
                     (HX + 1, CROWN_Y + 11), (HX + 11, CROWN_Y + 12), 1)  # gap line under the dome
    pygame.draw.line(surf, (220, 225, 235),
                     (HX + 1, CROWN_Y + 8), (HX + 13, CROWN_Y + 10), 2)  # 2px thick tilted leading edge

    # 2 — BLACK SOCKS (knee-high) with a 2px white hoop band on the upper sock.
    #     The shadow stripe gives the black sock an edge against the night sky.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, (18, 20, 26), (fx + 1, HY + 13), (fx + 1, HY + 25), 6)  # shadow
        pygame.draw.line(surf, _SOCK_D, (fx, HY + 13), (fx, HY + 25), 5)
        pygame.draw.line(surf, (200, 205, 215), (fx - 2, HY + 24), (fx + 3, HY + 24), 2)  # upper-sock white hoop

    # 3 — BOOTS with a 2px white sole stripe.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_S, (fx - 3, HY + 26), (fx + 3, HY + 26), 2)  # white sole stripe

    # 4 — BLACK SHORTS just under the jersey hem.
    pygame.draw.line(surf, _SHORTS_D, (BCX - 8, HY + 24), (HX + 8, HY + 24), 4)

    # 5 — JERSEY BODY (true black). The lit plane is a single 2px sliver on the
    #     near edge so the read stays BLACK rather than a grey chest plane.
    _poly(surf, _REF_BLACK, jersey)
    pygame.draw.line(surf, _REF_LIT, (HX + 9, HY + 9), (HX + 10, HY + 17), 2)  # lit sliver

    # 6 — GARMENT OUTLINE with DUAL RIM-LIGHTS. The cool-grey back rim + neutral
    #     front outline + full polygon edge are the only thing that separates a
    #     true-black garment from the night sky and from Pip's own scarlet body.
    pygame.draw.lines(surf, (120, 124, 130), False,
                      [(BCX - 10, HY + 7), (BCX - 12, HY + 17), (BCX - 8, HY + 23)], 2)  # back rim (left)
    pygame.draw.lines(surf, (100, 102, 108), False,
                      [(HX + 9, HY + 8), (HX + 11, HY + 18), (HX + 8, HY + 23)], 1)      # front outline (right)
    pygame.draw.polygon(surf, _REF_RIM, jersey, 1)

    # 7 — CENTRE PLACKET seam down the shirt front.
    pygame.draw.line(surf, (38, 40, 46), (HX, HY + 11), (HX, HY + 21), 1)

    # 8 — SLEEVE CUFFS. The far (back) cuff stays a faint construction edge; the
    #     near (front) cuff is darkened so it no longer competes with the hero
    #     props clustered on the front of the chest.
    pygame.draw.line(surf, (90, 95, 102), (BCX - 10, HY + 12), (BCX - 3, HY + 12), 2)  # back cuff, muted
    pygame.draw.line(surf, _REF_CUFF, (HX + 4, HY + 12), (HX + 10, HY + 12), 2)        # front cuff, darkened

    # 9 — V-NECK COLLAR (referee style), lifted UP to the ACTUAL neckline on the
    #     shoulders just below the chin — clear of the card/whistle cluster below.
    #     Two 2px WHITE arms from the shoulders (HX∓5, HY+5) converging to a crisp
    #     V-point at (HX, HY+9). Kept as pure white lines so the V reads as the
    #     highest note up top, above every prop.
    pygame.draw.line(surf, _REF_WHITE, (HX - 5, HY + 5), (HX, HY + 9), 2)   # left arm
    pygame.draw.line(surf, _REF_WHITE, (HX + 5, HY + 5), (HX, HY + 9), 2)   # right arm

    # 10 — LANYARD + WHISTLE (drawn BEFORE the cards so the cards sit in front).
    #      The lanyard is a DARK dull cord (never white) so it stops reading as a
    #      bright stripe; the 5px steel disc at its base is the only metal-bright
    #      note, the single glint that says "referee".
    pygame.draw.line(surf, _REF_LANY, (HX - 2, HY + 11), (HX + 1, HY + 18), 1)  # dark lanyard V
    pygame.draw.line(surf, _REF_LANY, (HX + 4, HY + 11), (HX + 1, HY + 18), 1)
    wx, wy = HX + 1, HY + 19
    pygame.draw.circle(surf, (100, 104, 112), (wx, wy), 3)   # disc shadow ring (5px dia)
    pygame.draw.circle(surf, _REF_WSTL, (wx, wy), 2)         # steel disc
    pygame.draw.circle(surf, (225, 230, 240), (wx - 1, wy - 1), 1)  # glint

    # 11 — YELLOW + RED CARDS — the HERO props, drawn LAST so they are in front of
    #      the whistle, collar and jersey. Both 9×11: the red card sits behind,
    #      offset 2px right + 2px down so both corners show, with a 1px dark gap
    #      between them. This paired card mass is the dominant bright read at 40px.
    yl, yt = HX - 10, HY + 14
    # Red card behind, offset 2px right + 2px down.
    pygame.draw.rect(surf, (140, 28, 22), (yl + 2, yt + 2, 9, 11))   # red shade edge
    pygame.draw.rect(surf, _REF_RCRD,     (yl + 2, yt + 2, 8, 11))   # red card 9x11 (lit face)
    # 1px dark gap, then the yellow card on top.
    pygame.draw.rect(surf, (18, 18, 22), (yl - 1, yt - 1, 11, 13))   # dark gap so the two cards read apart
    pygame.draw.rect(surf, (180, 140, 0), (yl, yt, 9, 11))           # yellow shade edge
    pygame.draw.rect(surf, _REF_YCRD,     (yl, yt, 8, 11))           # yellow card 9x11 (lit face)
    pygame.draw.line(surf, (255, 240, 120), (yl + 1, yt + 1), (yl + 6, yt + 1), 1)  # top glint


build = _make_skin(_paint)
