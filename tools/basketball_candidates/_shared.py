"""Shared draw logic for basketball v3 kit candidates.

All 5 designs share the same structure — sleeveless tank jersey + baggy shorts
+ brow headband. Only the palette and jersey number change per design.
"""
import pygame


def draw_basketball_kit(
    surf, BCX, BCY, HX, CROWN_Y, poly_fn,
    jersey_d,       # dark outline / shadow for jersey
    strap,          # shoulder strap colour
    strap_d,        # strap shadow
    num_col,        # jersey number colour
    num_d,          # number drop-shadow colour
    number,         # digit string: "1", "23", "33", etc.
    shorts,         # shorts fill
    shorts_d,       # shorts outline / shadow
    waist,          # waistband accent
    band,           # headband fill
    band_d,         # headband shadow
    knot,           # headband knot/bow colour
):
    """Draw the full kit onto surf.  Call from _paint(surf, _a)."""

    # --- Body oval outline -----------------------------------------------
    pygame.draw.ellipse(surf, jersey_d, (BCX-19, BCY-14, 38, 28), 1)

    # --- Sleeveless TANK shoulder straps ---------------------------------
    # Two thin diagonals over the shoulders; bare jersey visible between them.
    pygame.draw.line(surf, strap_d, (BCX-16, BCY-13), (BCX-11, BCY+4), 3)
    pygame.draw.line(surf, strap,   (BCX-15, BCY-13), (BCX-10, BCY+4), 2)
    pygame.draw.line(surf, strap_d, (BCX+14, BCY-13), (BCX+9,  BCY+4), 3)
    pygame.draw.line(surf, strap,   (BCX+13, BCY-13), (BCX+8,  BCY+4), 2)
    # Collar neckline
    pygame.draw.line(surf, strap, (BCX-7, BCY-13), (BCX+5, BCY-13), 2)

    # --- Jersey number ---------------------------------------------------
    _draw_number(surf, BCX, BCY, number, num_col, num_d)

    # --- Hem seam --------------------------------------------------------
    pygame.draw.ellipse(surf, jersey_d, (BCX-10, BCY+5, 22, 2), 1)

    # --- Baggy shorts (longer + wider than soccer) -----------------------
    pygame.draw.ellipse(surf, shorts,   (BCX-12, BCY+5, 26, 16))
    pygame.draw.ellipse(surf, shorts_d, (BCX-12, BCY+5, 26, 16), 1)
    # Waistband accent — 3px so it reads at 40px as the jersey/shorts divider
    pygame.draw.line(surf, waist, (BCX-11, BCY+6), (BCX+12, BCY+6), 3)
    # Inseam shadow triangle
    poly_fn(surf, shorts_d, [
        (BCX-1, BCY+16), (BCX+3, BCY+16), (BCX+1, BCY+19)
    ])

    # --- Brow HEADBAND ---------------------------------------------------
    pygame.draw.line(surf, band_d, (HX-12, CROWN_Y+7), (HX+12, CROWN_Y+6), 5)
    pygame.draw.line(surf, band,   (HX-11, CROWN_Y+6), (HX+11, CROWN_Y+5), 4)
    # Knot/bow on the right side
    pygame.draw.circle(surf, knot,   (HX+10, CROWN_Y+5), 3)
    pygame.draw.circle(surf, band_d, (HX+10, CROWN_Y+5), 3, 1)
    # White highlight strip on headband
    pygame.draw.line(surf, (255,255,255,80), (HX-10, CROWN_Y+5), (HX+8, CROWN_Y+4), 1)


def _draw_number(surf, BCX, BCY, number, col, shadow):
    """Render up to 2-digit block number centred on the jersey chest."""
    digits = number.strip()
    if len(digits) == 1:
        _draw_digit(surf, BCX, BCY-1, digits[0], col, shadow, scale=1.2)
    elif len(digits) == 2:
        _draw_digit(surf, BCX-5, BCY-1, digits[0], col, shadow, scale=1.0)
        _draw_digit(surf, BCX+5, BCY-1, digits[1], col, shadow, scale=1.0)


def _draw_digit(surf, cx, cy, d, col, shad, scale=1.0):
    """Draw a single block digit centred at (cx, cy)."""
    w = int(5 * scale)   # half-width
    h = int(8 * scale)   # half-height
    t = max(2, int(3 * scale))  # stroke thickness

    def seg(x0, y0, x1, y1):
        # draw shadow offset then main
        pygame.draw.line(surf, shad,  (cx+x0+1, cy+y0+1), (cx+x1+1, cy+y1+1), t)
        pygame.draw.line(surf, col,   (cx+x0,   cy+y0),   (cx+x1,   cy+y1),   t)

    if d == '0':
        seg(-w, -h, +w, -h); seg(+w, -h, +w, +h)
        seg(+w, +h, -w, +h); seg(-w, +h, -w, -h)
    elif d == '1':
        seg(-1, -h, -1, +h)
        seg(-w, -h, -1, -h)
    elif d == '2':
        seg(-w, -h, +w, -h); seg(+w, -h, +w,  0)
        seg(+w,  0, -w,  0); seg(-w,  0, -w, +h)
        seg(-w, +h, +w, +h)
    elif d == '3':
        seg(-w, -h, +w, -h); seg(+w, -h, +w, +h)
        seg(-w,  0, +w,  0); seg(-w, +h, +w, +h)
    elif d == '4':
        seg(-w, -h, -w,  0); seg(-w,  0, +w,  0)
        seg(+w, -h, +w, +h)
    elif d == '5':
        seg(+w, -h, -w, -h); seg(-w, -h, -w,  0)
        seg(-w,  0, +w,  0); seg(+w,  0, +w, +h)
        seg(+w, +h, -w, +h)
    elif d == '6':
        seg(+w, -h, -w, -h); seg(-w, -h, -w, +h)
        seg(-w,  0, +w,  0); seg(+w,  0, +w, +h)
        seg(+w, +h, -w, +h)
    elif d == '7':
        seg(-w, -h, +w, -h); seg(+w, -h, -w, +h)
    elif d == '8':
        seg(-w, -h, +w, -h); seg(+w, -h, +w, +h)
        seg(-w,  0, +w,  0); seg(-w, +h, +w, +h)
        seg(-w, -h, -w, +h)
    elif d == '9':
        seg(-w, -h, +w, -h); seg(+w, -h, +w, +h)
        seg(-w,  0, +w,  0); seg(-w, -h, -w,  0)
        seg(+w, +h, -w, +h)
