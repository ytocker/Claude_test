"""DESIGN 4 — RETRO '70s (Tennis, vintage cream).

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw kitted as a throwback club tennis pro: a
thick terry SWEATBAND with the iconic red/navy/red triple stripe across the
brow, an ecru/cream POLO with a retro SHAWL collar + red-and-navy chest piping
on the chest below the head, a matching wristband, and the hero read — a classic
WOOD racket (honey-tan frame, dark laminate edge, leather grip) held up in the
near wing so the head breaks the back/top silhouette.

Pushes FIDELITY in a warm vintage direction off the shipped tennis
(design_5): where that racket was one flat green plastic ring, this is a
two-tone WOOD frame (honey body + dark laminate keyline) so it reads as a 1970s
laminated-ash racket, not a modern composite. The tri-stripe sweatband and the
ecru cloth carry the era; nothing leans on a tennis ball (it ships as a separate
matching parcel), so the whole read rides on the racket + the warm kit.

The cloth is painted OVER the scarlet body; the macaw HEAD stays bare so Pip
still reads as a parrot. Everything is held INSIDE the base bird footprint —
only the sweatband touches the brow and only the racket head breaks the outline
as a held prop; nothing balloons the body or drops below the feet line.

Headless render: tools/render_tennis_design_4.py.
"""
import math
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Vintage cream + retro red/navy + honey WOOD. The ecru cloth gets a cool lower
# shade so it reads ROUND on a bright day sky without going flat, plus a dark
# contour so it stays crisp. The wood racket frame is carried in three values
# (honey body + bright sheen + dark laminate keyline) so the tall oval survives
# the downscale and reads as turned wood — the honey/laminate two-tone is the
# whole "wood not plastic" tell once the strings vanish at 40px.
_RT_ECRU     = (239, 230, 206)        # #EFE6CE ecru polo field
_RT_ECRU_D   = (205, 196, 170)        # ecru cool shade (rounds the cloth)
_RT_ECRU_DD  = (168, 160, 138)        # deep fold / contour so cream stays crisp
_RT_ECRU_H   = (250, 244, 224)        # ecru highlight
_RT_RED      = (194, 57, 43)          # #C2392B retro stripe red
_RT_RED_H    = (224, 96, 80)          # red sheen
_RT_NAVY     = (30, 42, 85)           # #1E2A55 retro stripe navy
_RT_NAVY_H   = (66, 84, 150)          # navy sheen
_RT_WOOD     = (181, 133, 63)         # #B5853F honey wood frame body
_RT_WOOD_H   = (224, 184, 116)        # bright wood sheen (rounds the oval)
_RT_WOOD_D   = (110, 74, 34)          # #6E4A22 dark laminate edge / keyline
_RT_STRING   = (228, 222, 200)        # warm gut strings on the void
_RT_VOID     = (40, 32, 24)           # dark warm open-face void (no inner disc)
_RT_STR_DIM  = (96, 84, 64)           # low-contrast strings on the void
_RT_GRIP     = (78, 54, 32)           # leather grip wrap (warm brown, not black)
_RT_GRIP_H   = (138, 102, 62)         # grip wrap highlight tick


def _racket(surf, hx, hy, hr):
    """The hero prop AND the sole tennis tell (the ball ships separately): a
    classic WOOD racket — a tall narrow oval strung head + a wrapped leather
    handle, held up so the head breaks the back/top silhouette. The read at 40px
    rides on the two-tone WOOD ring (honey body + dark laminate keyline) so it
    reads as turned wood, the throat Y, and the warm grip below."""
    # Tall narrow oval strung head — one clean frame ring around an OPEN strung
    # face. A solid inner disc would read as a circle-in-a-circle, so the
    # interior is a warm dark VOID with dim gut strings; only the frame survives.
    rw, rh = int(hr * 1.55), int(hr * 2.15)        # taller/narrower = vintage oval
    face = pygame.Rect(hx - rw, hy - rh, rw * 2, rh * 2)

    # Warm void interior + LOW-contrast warm strings so the inside reads as an
    # open strung face, not a filled bright disc. Mains + crosses both present so
    # a careful look reads the weave; at 40px they sink and the frame carries.
    clip_prev = surf.get_clip()
    surf.set_clip(face)
    pygame.draw.ellipse(surf, _RT_VOID, face)
    for gx in range(face.left + 3, face.right - 2, 3):
        pygame.draw.line(surf, _RT_STR_DIM, (gx, face.top + 1), (gx, face.bottom - 1), 1)
    for gy in range(face.top + 3, face.bottom - 2, 3):
        pygame.draw.line(surf, _RT_STR_DIM, (face.left + 1, gy), (face.right - 1, gy), 1)
    surf.set_clip(clip_prev)

    # Two-tone WOOD frame — a dark LAMINATE keyline on the outer edge (the
    # signature dark lacquer rim of a '70s laminated racket) + a honey body ring,
    # with a bright sheen arc up the near side so the oval reads as round turned
    # wood. This honey/laminate split is what reads "wood", not plastic.
    pygame.draw.ellipse(surf, _RT_WOOD_D, face.inflate(3, 3), 2)   # dark laminate edge
    pygame.draw.ellipse(surf, _RT_WOOD, face, 3)                   # honey frame body
    pygame.draw.arc(surf, _RT_WOOD_H, face.inflate(-1, -1),
                    math.radians(70), math.radians(200), 2)        # wood sheen arc

    # Throat — two honey struts splaying from the handle into the head, the
    # signature racket Y, with a tiny navy throat DECAL where they meet (the
    # painted brand badge a wood racket carries at the throat).
    ty = hy + rh
    pygame.draw.line(surf, _RT_WOOD_D, (hx - 1, ty + 5), (hx - rw + 2, ty - 2), 5)
    pygame.draw.line(surf, _RT_WOOD_D, (hx + 1, ty + 5), (hx + rw - 2, ty - 2), 5)
    pygame.draw.line(surf, _RT_WOOD, (hx - 1, ty + 4), (hx - rw + 3, ty - 1), 3)
    pygame.draw.line(surf, _RT_WOOD, (hx + 1, ty + 4), (hx + rw - 3, ty - 1), 3)
    pygame.draw.circle(surf, _RT_NAVY, (hx, ty + 1), 2)            # throat decal
    pygame.draw.circle(surf, _RT_RED, (hx, ty + 1), 1)

    # Wrapped LEATHER handle dropping into the near wing (kept inside the
    # silhouette). Warm brown wrap with cross-wrap ticks + a wood butt cap so the
    # grip reads as the leather-bound handle of a wood racket.
    hbx, hby = hx, ty + 5
    htx, hty = hx + 4, hby + 12
    pygame.draw.line(surf, _RT_WOOD_D, (hbx, hby), (htx, hty), 7)  # grip core
    pygame.draw.line(surf, _RT_GRIP, (hbx, hby), (htx, hty), 5)    # leather wrap
    for t in (0.3, 0.55, 0.8):                                     # cross-wrap ticks
        wx = hbx + (htx - hbx) * t
        wy = hby + (hty - hby) * t
        pygame.draw.line(surf, _RT_GRIP_H, (wx - 2, wy + 1), (wx + 2, wy - 1), 1)
    pygame.draw.circle(surf, _RT_WOOD, (int(htx), int(hty)), 2)    # wood butt cap
    pygame.draw.circle(surf, _RT_WOOD_H, (int(htx) - 1, int(hty) - 1), 1)


def _paint(surf, _a):
    # --- Ecru/cream POLO on the FRONT CHEST (BELOW the head) --------------------
    # Matched to the baseball jersey's vertical position (top ~HY+8, hem ~HY+23,
    # NO collar rising into the head) so the cloth sits on the chest and nothing
    # covers Pip's beak/eye/face. Ecru-filled with a cool lower shade so it reads
    # round, plus a dark contour so the warm cream stays crisp on a bright sky.
    polo = [(HX - 13, HY + 8), (HX - 14, HY + 16), (HX - 11, HY + 23),
            (HX + 9, HY + 23), (HX + 12, HY + 16), (HX + 11, HY + 8),
            (HX + 4, HY + 9), (HX - 5, HY + 9)]
    _poly(surf, _RT_ECRU_D, polo)
    # Lit upper body of the cloth so the cream isn't flat.
    _poly(surf, _RT_ECRU, [(HX - 12, HY + 9), (HX - 12, HY + 18),
                           (HX + 10, HY + 18), (HX + 10, HY + 9),
                           (HX + 4, HY + 10), (HX - 5, HY + 10)])
    pygame.draw.line(surf, _RT_ECRU_H, (HX - 11, HY + 10), (HX + 8, HY + 10), 1)

    # Navy SHORT-SLEEVE trim at the cuffs/shoulders — a short navy band at each
    # wing root so the retro polo has banded sleeves, not a blank field.
    pygame.draw.line(surf, _RT_NAVY, (HX - 13, HY + 10), (HX - 12, HY + 15), 2)
    pygame.draw.line(surf, _RT_NAVY, (HX + 11, HY + 10), (HX + 10, HY + 15), 2)

    # Retro red + navy CHEST PIPING down the placket — two thin vertical lines
    # framing a short button placket, the throwback club detail.
    pygame.draw.line(surf, _RT_RED, (HX - 4, HY + 11), (HX - 4, HY + 22), 2)
    pygame.draw.line(surf, _RT_NAVY, (HX + 1, HY + 11), (HX + 1, HY + 22), 2)
    for byb in (HY + 13, HY + 17, HY + 21):                        # placket buttons
        pygame.draw.circle(surf, _RT_NAVY, (HX - 2, byb), 1)

    # Retro SHAWL collar — a soft rounded navy-edged collar curving around the
    # neck base, sitting ON the chest (never up in the head). The shawl shape
    # (wider rounded lapels) is what dates it to the '70s vs a sharp modern V.
    shawl = [(HX - 6, HY + 9), (HX - 7, HY + 13), (HX - 3, HY + 12),
             (HX, HY + 14), (HX + 3, HY + 12), (HX + 6, HY + 13),
             (HX + 5, HY + 9)]
    _poly(surf, _RT_ECRU_DD, shawl)
    _poly(surf, _RT_ECRU, [(HX - 5, HY + 9), (HX - 5, HY + 12), (HX, HY + 13),
                           (HX + 4, HY + 12), (HX + 4, HY + 9)])
    pygame.draw.line(surf, _RT_NAVY, (HX - 6, HY + 9), (HX - 3, HY + 12), 1)  # navy collar edge
    pygame.draw.line(surf, _RT_NAVY, (HX + 5, HY + 9), (HX + 3, HY + 12), 1)

    # Crisp dark contour so the ecru polo separates from the day sky / pillars.
    pygame.draw.polygon(surf, _RT_ECRU_DD, polo, 1)

    # --- Matching terry WRISTBAND at the near wing root ------------------------
    # A cream terry band with the same red/navy stripe on the near wing — a sport
    # tell that stays inside the silhouette and ties to the sweatband.
    wx, wy = HX + 11, HY + 20
    pygame.draw.line(surf, _RT_ECRU_DD, (wx - 3, wy - 3), (wx + 3, wy + 3), 6)
    pygame.draw.line(surf, _RT_ECRU, (wx - 3, wy - 3), (wx + 3, wy + 3), 3)
    pygame.draw.line(surf, _RT_RED, (wx - 2, wy - 2), (wx + 2, wy + 2), 1)

    # NOTE: the tennis BALL is intentionally NOT drawn — it ships as a separate
    # matching PARCEL item, so the racket + kit carry the tennis read alone.

    # --- Thick terry SWEATBAND across the brow (the '70s signature) -------------
    # A wide cream terry brow band with the iconic red/navy/red triple stripe.
    # Only headgear that touches the head — the crown stays open so Pip is still
    # clearly the macaw. Wider/chunkier than a modern headband to date it.
    by = CROWN_Y + 4
    band = [(HX - 11, by - 3), (HX + 14, by - 4), (HX + 16, by + 3),
            (HX - 11, by + 4)]
    _poly(surf, _RT_ECRU_D, band)
    _poly(surf, _RT_ECRU, [(HX - 11, by - 3), (HX + 14, by - 4),
                           (HX + 15, by), (HX - 11, by + 1)])
    pygame.draw.line(surf, _RT_ECRU_H, (HX - 10, by - 2), (HX + 12, by - 3), 1)
    # The triple stripe — red / navy / red running along the band's middle.
    pygame.draw.line(surf, _RT_RED, (HX - 11, by - 1), (HX + 15, by - 2), 1)
    pygame.draw.line(surf, _RT_NAVY, (HX - 11, by), (HX + 15, by - 1), 1)
    pygame.draw.line(surf, _RT_RED, (HX - 11, by + 1), (HX + 15, by), 1)
    # Dark lower edge so the terry band separates from the macaw face beneath.
    pygame.draw.line(surf, _RT_ECRU_DD, (HX - 11, by + 4), (HX + 16, by + 3), 1)

    # --- RACKET drawn LAST so it OVERLAYS the polo/clothing ---------------------
    # Like the baseball BAT, the racket is painted last so the whole prop — head,
    # throat and handle — rests fully IN FRONT of the body. The handle drops into
    # the near wing over the chest; the oval head breaks the top/back silhouette
    # against open sky.
    _racket(surf, HX - 21, CROWN_Y + 2, 7)


build = store_skins._make_skin(_paint)
