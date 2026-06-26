"""DESIGN 1 — WIMBLEDON WHITES (Tennis).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
art stays untouched. Pip the scarlet macaw kitted in the all-white grass-court
heritage look: a bright white POLO with a royal-green collar V + a green/aubergine
twin placket stripe and chest crest, a thin terry HEADBAND at the brow (crown left
OPEN so the macaw still reads), green/white wristbands, and the hero read — a
classic WOOD-FRAME racket held up so the cream oval breaks the back/top
silhouette.

This is the "pure tennis tradition" take in the set, so the differentiator is
the WOOD racket (warm cream/ivory frame, NOT green) with a tan leather grip, and
the royal-green + Wimbledon-aubergine trim. The tennis BALL ships separately, so
the racket + whites must carry the read alone — the frame is drawn large and in
three values so the oval survives the 40px downscale.

The whites are painted OVER the scarlet body (the head stays the macaw so Pip
still reads as a parrot). Cloth, headband + wristbands are held INSIDE the base
bird footprint; only the headband touches the brow and only the racket head
breaks the outline as a held prop — nothing below the feet line, nothing
balloons the body.

Headless render: tools/render_tennis_design_1.py.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Wimbledon palette — all-white kit, royal-green + aubergine trim, warm wood
# frame. The polo gets a cool LOWER shade so the white reads ROUND against a
# bright day sky without washing out, and a dark contour so it stays crisp. The
# racket frame is a warm CREAM wood (three values) so the OVAL HEAD reads as a
# round wood frame at 40px — the cream separates from both the sky and the
# scarlet wing the way a green frame could not.
_WIM_WHITE   = (246, 246, 242)        # #F6F6F2 polo white
_WIM_WHITE_D = (210, 212, 206)        # cool lower shade (rounds the cloth)
_WIM_WHITE_DD= (172, 176, 170)        # deep fold / contour so white stays crisp
_WIM_WHITE_H = (255, 255, 252)        # lit highlight
_WIM_GREEN   = (30, 122, 60)          # #1E7A3C royal green trim
_WIM_GREEN_D = (18, 84, 40)           # green shadow
_WIM_GREEN_H = (84, 184, 112)         # green highlight
_WIM_PURPLE  = (75, 46, 102)          # #4B2E66 aubergine (Wimbledon purple)
_WIM_PURPLE_H= (118, 84, 150)         # aubergine highlight
# Wood pushed toward a clearer AMBER (more saturation, not lighter) so the ring
# stays visibly warm/cream and never desaturates to dingy grey beside the cool
# polo white when the night palette cools everything.
_WIM_WOOD    = (224, 188, 120)        # #E0BC78 amber wood frame body (warmer)
_WIM_WOOD_D  = (158, 126, 70)         # wood shaded side so the oval reads round
_WIM_WOOD_H  = (252, 232, 168)        # bright top-left glint (stays warm at night)
_WIM_GRIP    = (122, 90, 51)          # #7A5A33 tan leather grip
_WIM_GRIP_D  = (70, 48, 26)           # grip shadow / butt cap / keyline (darker)
_WIM_GRIP_H  = (168, 134, 88)         # grip wrap tick glint
_WIM_STRING  = (238, 238, 232)        # pale strings (lit, on the void)
_WIM_STR_DIM = (110, 116, 120)        # low-contrast strings deeper on the void
_WIM_VOID    = (32, 36, 42)           # #20242A flatter near-black window (less green)


def _racket(surf, hx, hy, hr):
    """The hero prop AND the sole tennis tell (the ball ships separately). A
    classic WOOD-FRAME oval strung head + tan leather grip, held up so the cream
    oval breaks the back/top silhouette. The whole read rides on the warm wood
    RING (three values so it reads round at 40px) + the throat Y + the wrapped
    grip; the cream frame is the differentiator from the green-framed set."""
    # Oval strung head — a tall ellipse read as ONE clean wood frame around an
    # OPEN strung face. Interior left a dark VOID so it never forms a second
    # disc; the cream ring is the single survivor at downscale.
    rw, rh = int(hr * 1.7), int(hr * 2.1)        # tall tennis-racket oval
    face = pygame.Rect(hx - rw, hy - rh, rw * 2, rh * 2)

    # Dark void + a clean string MESH: pale mains/crosses lit on near-black so
    # the strings read as a tight bed up close, yet the centre stays empty at
    # 40px (the dim value lets the mesh fall away, leaving the wood ring).
    clip_prev = surf.get_clip()
    surf.set_clip(face)
    pygame.draw.ellipse(surf, _WIM_VOID, face)
    for gx in range(face.left + 3, face.right - 2, 3):
        col = _WIM_STRING if (gx - face.left) % 6 < 3 else _WIM_STR_DIM
        pygame.draw.line(surf, col, (gx, face.top + 1), (gx, face.bottom - 1), 1)
    for gy in range(face.top + 3, face.bottom - 2, 3):
        col = _WIM_STRING if (gy - face.top) % 6 < 3 else _WIM_STR_DIM
        pygame.draw.line(surf, col, (face.left + 1, gy), (face.right - 1, gy), 1)
    surf.set_clip(clip_prev)

    # ONE wood frame ring in three values — a dark keyline for crisp separation
    # from the sky, the amber body, and a top-left glint so the oval reads as a
    # rounded WOOD frame, not a flat hoop. No second full ring (avoids the
    # circle-inside-a-circle), just shading on the single oval.
    pygame.draw.ellipse(surf, _WIM_GRIP_D, face.inflate(3, 3), 1)   # outer keyline
    pygame.draw.ellipse(surf, _WIM_WOOD_D, face, 3)                 # frame base (shaded)
    pygame.draw.ellipse(surf, _WIM_WOOD, face.inflate(-1, -1), 2)   # amber body
    # Head-side keyline: a 1px dark arc on the lower-right of the frame (the edge
    # nearest the white headband) so the warm ring never shares an edge with the
    # band — it survives even when both desaturate at night.
    pygame.draw.arc(surf, _WIM_GRIP_D, face.inflate(2, 2), -1.6, 0.6, 1)
    # Bright top-left glint arc so the wood stays warm/cream against the sky.
    pygame.draw.arc(surf, _WIM_WOOD_H, face.inflate(-1, -1), 0.5, 2.6, 1)

    # Throat — a green-strut Y splaying from the grip into the head. The thin
    # green struts are the heritage colour cue on the otherwise cream frame and
    # the second tell when the strings vanish at downscale.
    ty = hy + rh
    pygame.draw.line(surf, _WIM_GREEN_D, (hx - 1, ty + 5), (hx - rw + 2, ty - 2), 4)
    pygame.draw.line(surf, _WIM_GREEN_D, (hx + 1, ty + 5), (hx + rw - 2, ty - 2), 4)
    pygame.draw.line(surf, _WIM_WOOD,   (hx - 1, ty + 4), (hx - rw + 3, ty - 1), 3)
    pygame.draw.line(surf, _WIM_WOOD,   (hx + 1, ty + 4), (hx + rw - 3, ty - 1), 3)
    pygame.draw.line(surf, _WIM_GREEN,  (hx - 1, ty + 4), (hx - rw + 3, ty - 1), 1)
    pygame.draw.line(surf, _WIM_GREEN,  (hx + 1, ty + 4), (hx + rw - 3, ty - 1), 1)

    # Wrapped tan-leather GRIP dropping into the near wing (kept inside the
    # silhouette). Dark base + lit wrap so the leather reads as a handle.
    hbx, hby = hx, ty + 5
    htx, hty = hx + 4, hby + 12
    pygame.draw.line(surf, _WIM_GRIP_D, (hbx, hby), (htx, hty), 6)
    pygame.draw.line(surf, _WIM_GRIP,   (hbx, hby), (htx, hty), 5)
    pygame.draw.line(surf, _WIM_GRIP_H, (hbx - 1, hby), (htx - 1, hty), 1)
    # Cross-wrap ticks so the handle reads as a leather grip, not a smooth rod.
    for t in (0.3, 0.55, 0.8):
        wx = hbx + (htx - hbx) * t
        wy = hby + (hty - hby) * t
        pygame.draw.line(surf, _WIM_GRIP_D, (wx - 3, wy + 2), (wx + 3, wy - 2), 1)
        pygame.draw.line(surf, _WIM_GRIP_H, (wx - 2, wy + 1), (wx + 2, wy - 1), 1)
    # Butt cap — a tan disc flaring the grip end.
    pygame.draw.circle(surf, _WIM_GRIP_D, (int(htx), int(hty)), 3)
    pygame.draw.circle(surf, _WIM_GRIP, (int(htx), int(hty) - 1), 2)


def _paint(surf, _a):
    # --- White collared POLO on the FRONT CHEST (BELOW the head) ---------------
    # Vertically matched to the baseball jersey (top ~HY+8, hem ~HY+23, NO collar
    # rising into the head) so the cloth sits on the chest and NOTHING covers
    # Pip's beak/eye/face. White-filled with a cool lower shade so it reads round
    # plus a dark contour so it stays crisp on a bright day sky. Held inside the
    # footprint (~HX-13..HX+11) so it never balloons the bird.
    polo = [(HX - 13, HY + 8), (HX - 14, HY + 16), (HX - 11, HY + 23),
            (HX + 9, HY + 23), (HX + 12, HY + 16), (HX + 11, HY + 8),
            (HX + 4, HY + 9), (HX - 5, HY + 9)]
    _poly(surf, _WIM_WHITE_D, polo)
    # Lit upper body of the cloth so the white isn't flat; cool lower shade left
    # exposed at the hem rounds the torso.
    _poly(surf, _WIM_WHITE, [(HX - 12, HY + 9), (HX - 12, HY + 17),
                             (HX + 10, HY + 17), (HX + 10, HY + 9),
                             (HX + 4, HY + 10), (HX - 5, HY + 10)])
    pygame.draw.line(surf, _WIM_WHITE_H, (HX - 11, HY + 10), (HX + 8, HY + 10), 1)
    # Cool-white rim highlight tracing the upper-left shoulder so the cloth reads
    # rounder where it catches the sky light.
    pygame.draw.line(surf, _WIM_WHITE_H, (HX - 13, HY + 9), (HX - 13, HY + 15), 1)
    # Crisp dark contour so the white polo separates from the day sky / pillars.
    pygame.draw.polygon(surf, _WIM_WHITE_DD, polo, 1)

    # Royal-green collar V at the polo's OWN top — sits ON the chest, never in
    # the head. Thickened to a 3px block so the green reads as a 2px+ cluster at
    # 40px instead of vanishing as a hairline.
    pygame.draw.line(surf, _WIM_GREEN_D, (HX - 6, HY + 8), (HX, HY + 13), 3)
    pygame.draw.line(surf, _WIM_GREEN_D, (HX + 5, HY + 8), (HX, HY + 13), 3)
    pygame.draw.line(surf, _WIM_GREEN,  (HX - 6, HY + 8), (HX, HY + 12), 2)
    pygame.draw.line(surf, _WIM_GREEN,  (HX + 5, HY + 8), (HX, HY + 12), 2)
    pygame.draw.line(surf, _WIM_GREEN_H,(HX - 5, HY + 8), (HX - 1, HY + 11), 1)

    # Green + aubergine placket running down the buttoned front — thickened so
    # the heritage pair survives the downscale: a 2px green block flanked by a
    # 2px aubergine accent so at least one of each registers at 40px.
    pygame.draw.line(surf, _WIM_GREEN,  (HX - 1, HY + 12), (HX - 1, HY + 22), 2)
    pygame.draw.line(surf, _WIM_PURPLE, (HX + 1, HY + 13), (HX + 1, HY + 21), 2)
    pygame.draw.line(surf, _WIM_GREEN_H,(HX - 1, HY + 12), (HX - 1, HY + 15), 1)

    # Small chest CREST — a tiny green shield with an aubergine pip, the club
    # badge that lifts the plain white field at hero scale.
    cxr = pygame.Rect(HX + 4, HY + 13, 5, 6)
    pygame.draw.ellipse(surf, _WIM_GREEN, cxr)
    pygame.draw.ellipse(surf, _WIM_GREEN_D, cxr, 1)
    pygame.draw.circle(surf, _WIM_PURPLE_H, (HX + 6, HY + 16), 1)

    # --- Green-and-white WRISTBANDS at the wing roots --------------------------
    # Terry bands at the cuffs — a sport tell held inside the silhouette. Dropped
    # with the polo so they sit at the wing roots, not floating. The FAR (right)
    # cuff carries the full band; the NEAR (lower-left) cuff is shrunk ~1px and
    # tucked toward the wing so it doesn't pile into the grip/throat clump and
    # the tan grip can read as one clean diagonal.
    pygame.draw.line(surf, _WIM_GREEN_D, (HX + 8, HY + 17), (HX + 14, HY + 23), 6)
    pygame.draw.line(surf, _WIM_WHITE,   (HX + 8, HY + 17), (HX + 14, HY + 23), 3)
    pygame.draw.line(surf, _WIM_GREEN,   (HX + 9, HY + 18), (HX + 13, HY + 22), 1)
    wx, wy = HX - 14, HY + 20
    pygame.draw.line(surf, _WIM_GREEN_D, (wx - 2, wy - 2), (wx + 2, wy + 2), 5)
    pygame.draw.line(surf, _WIM_WHITE,   (wx - 2, wy - 2), (wx + 2, wy + 2), 2)

    # --- Terry HEADBAND at the brow (crown left OPEN) --------------------------
    # The only headgear that touches the head — a thin white terry band across
    # the brow with a green+purple twin stripe, the heritage tell up top. The
    # crown stays OPEN above it so Pip still clearly reads as the macaw.
    by = CROWN_Y + 5
    band = [(HX - 10, by - 2), (HX + 13, by - 4), (HX + 14, by + 1),
            (HX - 10, by + 3)]
    _poly(surf, _WIM_WHITE_D, band)
    _poly(surf, _WIM_WHITE, [(HX - 10, by - 2), (HX + 13, by - 4),
                             (HX + 13, by - 1), (HX - 10, by)])
    pygame.draw.line(surf, _WIM_WHITE_H, (HX - 9, by - 2), (HX + 11, by - 4), 1)
    # ONE bolder 2px green band wrapping the brow + a single aubergine accent dot
    # — the 1px twin stripe washed out at 40px, so the green is thickened to a
    # 2px block and the Wimbledon purple is concentrated into one readable dot.
    pygame.draw.line(surf, _WIM_GREEN,  (HX - 10, by), (HX + 13, by - 2), 2)
    pygame.draw.line(surf, _WIM_GREEN_H,(HX - 10, by - 1), (HX + 4, by - 2), 1)
    pygame.draw.circle(surf, _WIM_PURPLE, (HX + 11, by - 2), 2)
    pygame.draw.circle(surf, _WIM_PURPLE_H, (HX + 11, by - 2), 1)
    pygame.draw.line(surf, _WIM_WHITE_DD, (HX - 10, by + 2), (HX + 13, by), 1)

    # --- RACKET drawn LAST so it OVERLAYS the polo/clothing ---------------------
    # Like the baseball BAT, the racket is painted last so the whole prop — head,
    # throat and grip — rests fully IN FRONT of the body. The grip drops into the
    # near wing over the chest; the amber oval head breaks the top/back silhouette
    # against open sky. Shifted up-and-left to ~(HX-24, CROWN_Y-2) so the oval
    # clears the white headband and never shares an edge with it at 40px.
    _racket(surf, HX - 24, CROWN_Y - 2, 7)


build = store_skins._make_skin(_paint)
