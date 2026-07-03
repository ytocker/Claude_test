"""Shared draw logic for basketball v4 kit — polygon-over-parrot approach.

The natural parrot plumage shows through armhole areas; no body recolor.
The jersey is drawn as a polygon panel on top of the base parrot sprite.
The parrot's face is explicitly restored on top at the end so it always
overlays the jersey — the right strap and chest-panel edge behind the head
read naturally as hidden behind the bird's turned head.
"""
import pygame


def draw_basketball_kit(
    surf, BCX, BCY, HX, HY, CROWN_Y, poly_fn,
    jersey, jersey_d, jersey_h,
    trim, trim_d,
    num_col, num_d, number,
    shoe, shoe_d, shoe_ac,
    band_accent=None,
):
    """Draw full basketball kit over the natural parrot sprite."""
    bm = band_accent if band_accent is not None else jersey

    # --- Save the parrot face region BEFORE drawing anything ---------------
    # HX=47 sits 15 px right of BCX=32, so the right strap and chest-panel
    # edge overlap with the face. We restore the face at the very end so Pip's
    # head always sits in front of the jersey, matching how a turned-head bird
    # would naturally occlude the far shoulder of its own tank.
    face_x = HX - 9                               # = 38
    face_y = CROWN_Y - 1                          # = 30
    face_w = min(surf.get_width() - face_x, 28)   # up to canvas right edge
    face_h = HY + 12 - face_y                     # = 22 (crown → below beak)
    face_rect = pygame.Rect(face_x, face_y, face_w, face_h)
    face_backup = surf.subsurface(face_rect).copy()

    # --- CHEST PANEL (below the underarm line, full width) -----------------
    poly_fn(surf, jersey, [
        (BCX-13, BCY-4),  (BCX+13, BCY-4),
        (BCX+12, BCY+14), (BCX-12, BCY+14),
    ])
    poly_fn(surf, jersey_d, [
        (BCX-13, BCY-4),  (BCX-9,  BCY-4),
        (BCX-9,  BCY+14), (BCX-12, BCY+14),
    ])
    pygame.draw.line(surf, jersey_h, (BCX+9, BCY-3), (BCX+9, BCY+12), 2)

    # --- SHOULDER STRAPS (angled inward toward neckline) -------------------
    # Two narrow straps flanking a deep 14-px U-neck gap; deep armhole below.
    poly_fn(surf, jersey, [
        (BCX-12, BCY-4),  (BCX-7,  BCY-4),
        (BCX-5,  BCY-12), (BCX-10, BCY-12),
    ])
    pygame.draw.line(surf, jersey_d, (BCX-12, BCY-4), (BCX-10, BCY-12), 1)
    poly_fn(surf, jersey, [
        (BCX+7,  BCY-4),  (BCX+12, BCY-4),
        (BCX+10, BCY-12), (BCX+5,  BCY-12),
    ])
    pygame.draw.line(surf, jersey_h, (BCX+11, BCY-4), (BCX+9,  BCY-12), 1)

    # --- ARMHOLE SHADOW ARCS -----------------------------------------------
    pygame.draw.arc(surf, jersey_d, (BCX+3,  BCY-8, 12, 12), -0.9, 1.3, 2)
    pygame.draw.arc(surf, jersey_d, (BCX-15, BCY-8, 12, 12),  1.8, 4.0, 2)

    # --- U-NECKLINE trim ---------------------------------------------------
    pygame.draw.lines(surf, trim, False,
                      [(BCX-5, BCY-12), (BCX-1, BCY-9),
                       (BCX+3, BCY-9),  (BCX+6, BCY-12)], 2)

    # --- JERSEY NUMBER (shifted left so the face blit doesn't occlude it) --
    # Number lives in the LEFT portion of the chest panel (x ≈ 24–36) which is
    # safely left of the face-restore region (x ≥ 38). Bold 4-px strokes.
    _draw_number(surf, BCX - 2, BCY + 7, number, num_col, num_d)

    # --- HEM PIPING --------------------------------------------------------
    pygame.draw.line(surf, trim, (BCX-11, BCY+13), (BCX+11, BCY+13), 1)

    # --- WRISTBAND on near wing -------------------------------------------
    wrx, wry = BCX + 12, BCY + 8
    pygame.draw.line(surf, trim_d, (wrx-3, wry+4), (wrx+5, wry-2), 6)
    pygame.draw.line(surf, trim,   (wrx-3, wry+4), (wrx+5, wry-2), 4)
    pygame.draw.line(surf, jersey, (wrx-2, wry+3), (wrx+4, wry-2), 1)

    # --- BROW HEADBAND -----------------------------------------------------
    by = CROWN_Y + 5
    pygame.draw.line(surf, trim_d, (HX-12, by+1), (HX+13, by),   7)
    pygame.draw.line(surf, trim,   (HX-12, by),   (HX+13, by-1), 5)
    pygame.draw.line(surf, bm,     (HX-11, by),   (HX+12, by-1), 2)
    pygame.draw.line(surf, trim,   (HX-10, by-2), (HX+5,  by-2), 1)
    pygame.draw.circle(surf, bm, (HX-12, by), 3)
    pygame.draw.line(surf, jersey_d, (HX-13, by+2), (HX-16, by+5), 2)

    # --- HIGH-TOP SHOES ---------------------------------------------------
    for fx in (26, 34):
        pygame.draw.rect(surf, shoe_d, (fx-4, HY+22, 9, 6), border_radius=2)
        pygame.draw.rect(surf, shoe,   (fx-4, HY+21, 9, 4), border_radius=2)
        pygame.draw.line(surf, shoe_ac, (fx-3, HY+23), (fx+4, HY+23), 1)
        pygame.draw.line(surf, shoe_d,  (fx-4, HY+27), (fx+5, HY+27), 2)
        pygame.draw.line(surf, trim,    (fx-3, HY+21), (fx+1, HY+21), 1)

    # --- RESTORE PARROT FACE on top of all jersey elements -----------------
    # This ensures the head/beak always reads in front of the shirt, which is
    # the correct layering for a bird whose head is turned over its shoulder.
    surf.blit(face_backup, face_rect.topleft)


def _draw_number(surf, cx, cy, number, col, shadow):
    """Render a single bold digit centred at (cx, cy)."""
    digits = number.strip()
    # Always render as single digit for maximum legibility at 40px
    d = digits[0] if digits else '0'
    _draw_digit(surf, cx, cy, d, col, shadow, scale=1.1)


def _draw_digit(surf, cx, cy, d, col, shad, scale=1.0):
    """Draw a bold block digit centred at (cx, cy)."""
    w = int(5 * scale)
    h = int(8 * scale)
    t = max(3, int(4 * scale))   # bold: 4-px strokes at scale 1.0

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
