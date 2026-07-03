"""Shared draw logic for basketball v4 kit — polygon-over-parrot approach.

The natural parrot plumage shows through the armhole areas; no body recolor.
The jersey is drawn as a polygon panel on top of the base parrot sprite,
matching real NBA tank anatomy: two narrow straps flanking a deep neckline gap,
a deep U-shaped armhole scoop, and a full-width chest panel below the underarm.
"""
import pygame


def draw_basketball_kit(
    surf, BCX, BCY, HX, HY, CROWN_Y, poly_fn,
    jersey, jersey_d, jersey_h,  # jersey fill / dark-edge / highlight
    trim, trim_d,                 # trim accent (white or gold)
    num_col, num_d, number,       # jersey number colour / shadow / digit
    shoe, shoe_d, shoe_ac,        # shoe main / sole-shadow / accent stripe
    band_accent=None,             # headband midline + knot colour; defaults to jersey
):
    """Draw full basketball kit over the natural parrot sprite."""
    bm = band_accent if band_accent is not None else jersey

    # --- CHEST PANEL (below the underarm line, full width) -------------------
    # Runs from BCY-4 to BCY+14, covering the lower two-thirds of the body oval.
    poly_fn(surf, jersey, [
        (BCX-13, BCY-4),  (BCX+13, BCY-4),
        (BCX+12, BCY+14), (BCX-12, BCY+14),
    ])
    # Dark left side panel — 3-D curvature on the off-side of the torso.
    poly_fn(surf, jersey_d, [
        (BCX-13, BCY-4),  (BCX-9,  BCY-4),
        (BCX-9,  BCY+14), (BCX-12, BCY+14),
    ])
    # Highlight streak near the near (right) edge.
    pygame.draw.line(surf, jersey_h, (BCX+9, BCY-3), (BCX+9, BCY+12), 2)

    # --- SHOULDER STRAPS (angled inward toward neckline) ---------------------
    # Each strap is ~5 px wide; the 14 px neckline gap between their inner edges
    # reads unmistakably as a deep U-neck, not a crew collar.
    # Left strap — shifts slightly right as it rises to simulate angling over shoulder.
    poly_fn(surf, jersey, [
        (BCX-12, BCY-4),  (BCX-7,  BCY-4),
        (BCX-5,  BCY-12), (BCX-10, BCY-12),
    ])
    pygame.draw.line(surf, jersey_d, (BCX-12, BCY-4), (BCX-10, BCY-12), 1)
    # Right strap
    poly_fn(surf, jersey, [
        (BCX+7,  BCY-4),  (BCX+12, BCY-4),
        (BCX+10, BCY-12), (BCX+5,  BCY-12),
    ])
    pygame.draw.line(surf, jersey_h, (BCX+11, BCY-4), (BCX+9, BCY-12), 1)

    # --- ARMHOLE SHADOW ARCS -------------------------------------------------
    # Curved dark lines at the scoop edges make the armhole read as a cut-out
    # (not just empty space) — the parrot's wing plumage shows through the gap.
    pygame.draw.arc(surf, jersey_d, (BCX+3,  BCY-8, 12, 12), -0.9, 1.3, 2)
    pygame.draw.arc(surf, jersey_d, (BCX-15, BCY-8, 12, 12),  1.8, 4.0, 2)

    # --- U-NECKLINE trim piping ----------------------------------------------
    pygame.draw.lines(surf, trim, False,
                      [(BCX-5, BCY-12), (BCX-1, BCY-9),
                       (BCX+3, BCY-9),  (BCX+6, BCY-12)], 2)

    # --- JERSEY NUMBER -------------------------------------------------------
    _draw_number(surf, BCX, BCY + 5, number, num_col, num_d)

    # --- HEM PIPING ----------------------------------------------------------
    pygame.draw.line(surf, trim, (BCX-11, BCY+13), (BCX+11, BCY+13), 1)

    # --- WRISTBAND on near wing (forearm sweatband) --------------------------
    wrx, wry = BCX + 12, BCY + 8
    pygame.draw.line(surf, trim_d, (wrx-3, wry+4), (wrx+5, wry-2), 6)
    pygame.draw.line(surf, trim,   (wrx-3, wry+4), (wrx+5, wry-2), 4)
    pygame.draw.line(surf, jersey, (wrx-2, wry+3), (wrx+4, wry-2), 1)

    # --- BROW HEADBAND -------------------------------------------------------
    # Thick trim-coloured band hugging the crown; jersey-coloured midline + knot
    # is the "tied-on" tell that reads as worn kit.
    by = CROWN_Y + 5
    pygame.draw.line(surf, trim_d, (HX-12, by+1), (HX+13, by),   7)
    pygame.draw.line(surf, trim,   (HX-12, by),   (HX+13, by-1), 5)
    pygame.draw.line(surf, bm,     (HX-11, by),   (HX+12, by-1), 2)   # midline
    pygame.draw.line(surf, trim,   (HX-10, by-2), (HX+5,  by-2), 1)   # glint
    pygame.draw.circle(surf, bm, (HX-12, by), 3)                        # knot
    pygame.draw.line(surf, jersey_d, (HX-13, by+2), (HX-16, by+5), 2)  # tail

    # --- HIGH-TOP SHOES ------------------------------------------------------
    for fx in (26, 34):
        pygame.draw.rect(surf, shoe_d, (fx-4, HY+22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, shoe,   (fx-4, HY+21, 9, 4), border_radius=2)
        pygame.draw.line(surf, shoe_ac, (fx-3, HY+23), (fx+4, HY+23), 1)
        pygame.draw.line(surf, shoe_d,  (fx-4, HY+27), (fx+5, HY+27), 2)
        pygame.draw.line(surf, trim,    (fx-3, HY+21), (fx+1, HY+21), 1)


def _draw_number(surf, BCX, BCY, number, col, shadow):
    """Render a 1- or 2-digit block number centred on (BCX, BCY)."""
    digits = number.strip()
    if len(digits) == 1:
        _draw_digit(surf, BCX, BCY, digits[0], col, shadow, scale=1.2)
    elif len(digits) == 2:
        _draw_digit(surf, BCX-5, BCY, digits[0], col, shadow, scale=1.0)
        _draw_digit(surf, BCX+5, BCY, digits[1], col, shadow, scale=1.0)


def _draw_digit(surf, cx, cy, d, col, shad, scale=1.0):
    """Draw a single block digit centred at (cx, cy) using line segments."""
    w = int(5 * scale)
    h = int(8 * scale)
    t = max(2, int(3 * scale))

    def seg(x0, y0, x1, y1):
        pygame.draw.line(surf, shad, (cx+x0+1, cy+y0+1), (cx+x1+1, cy+y1+1), t)
        pygame.draw.line(surf, col,  (cx+x0,   cy+y0),   (cx+x1,   cy+y1),   t)

    if d == '0':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(+w,+h,-w,+h); seg(-w,+h,-w,-h)
    elif d == '1':
        seg(-1,-h,-1,+h); seg(-w,-h,-1,-h)
    elif d == '2':
        seg(-w,-h,+w,-h); seg(+w,-h,+w, 0)
        seg(+w, 0,-w, 0); seg(-w, 0,-w,+h); seg(-w,+h,+w,+h)
    elif d == '3':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(-w, 0,+w, 0); seg(-w,+h,+w,+h)
    elif d == '4':
        seg(-w,-h,-w, 0); seg(-w, 0,+w, 0); seg(+w,-h,+w,+h)
    elif d == '5':
        seg(+w,-h,-w,-h); seg(-w,-h,-w, 0)
        seg(-w, 0,+w, 0); seg(+w, 0,+w,+h); seg(+w,+h,-w,+h)
    elif d == '6':
        seg(+w,-h,-w,-h); seg(-w,-h,-w,+h)
        seg(-w, 0,+w, 0); seg(+w, 0,+w,+h); seg(+w,+h,-w,+h)
    elif d == '7':
        seg(-w,-h,+w,-h); seg(+w,-h,-w,+h)
    elif d == '8':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(-w, 0,+w, 0); seg(-w,+h,+w,+h); seg(-w,-h,-w,+h)
    elif d == '9':
        seg(-w,-h,+w,-h); seg(+w,-h,+w,+h)
        seg(-w, 0,+w, 0); seg(-w,-h,-w, 0); seg(+w,+h,-w,+h)
