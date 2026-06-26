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
# (honey body + bright sheen + dark laminate keyline) so the rounded oval
# survives the downscale and reads as turned wood — the honey/laminate two-tone
# is the "wood not plastic" tell, and a lifted mid-tan face keeps a full-pale
# string lattice visible so the head never collapses to an empty egg at 40px.
_RT_ECRU     = (239, 230, 206)        # #EFE6CE ecru polo field
_RT_ECRU_D   = (205, 196, 170)        # ecru cool shade (rounds the cloth)
_RT_ECRU_DD  = (168, 160, 138)        # deep fold / contour so cream stays crisp
_RT_ECRU_H   = (250, 244, 224)        # ecru highlight
_RT_RED      = (194, 57, 43)          # #C2392B retro stripe red
_RT_RED_H    = (224, 96, 80)          # red sheen
_RT_NAVY     = (30, 42, 85)           # #1E2A55 retro stripe navy
_RT_NAVY_M   = (54, 70, 130)          # mid navy — reads at NIGHT (deep navy drops out)
_RT_NAVY_H   = (66, 84, 150)          # navy sheen
_RT_WOOD     = (181, 133, 63)         # #B5853F honey wood frame body
_RT_WOOD_H   = (224, 184, 116)        # bright wood sheen (rounds the oval)
_RT_WOOD_D   = (110, 74, 34)          # #6E4A22 dark laminate edge / keyline
_RT_STRING   = (228, 222, 200)        # full-strength pale gut strings — the lattice must read
_RT_VOID     = (70, 60, 46)           # mid warm grey-tan face (lifted off the dark void)
_RT_GRIP     = (78, 54, 32)           # leather grip wrap (warm brown, not black)
_RT_GRIP_H   = (138, 102, 62)         # grip wrap highlight tick


def _racket(surf, hx, hy, hr):
    """The hero prop AND the sole tennis tell (the ball ships separately): a
    classic WOOD racket — a full rounded oval strung head + a wrapped leather
    handle, held so head→throat→grip→wing trace as one object. The 40px read
    rides on a BOLD two-tone WOOD frame (mass at the contour) wrapped around a
    visible pale string lattice on a lifted mid-tan face — never an empty egg."""
    # A FULLER, rounder oval (rw,rh ~1.7/1.9 vs the old 1.55/2.15) so the head
    # says "racket head," not "egg" — the old tall-narrow ring read as a void.
    rw, rh = int(round(hr * 1.7)), int(round(hr * 1.9))
    face = pygame.Rect(hx - rw, hy - rh, rw * 2, rh * 2)

    # LIFTED mid warm grey-tan face + FULL-strength pale strings (no dim variant)
    # so the open face shows a real string lattice at 40px instead of a dark
    # hole. Mains + crosses both at full value — the lattice is the inner read.
    clip_prev = surf.get_clip()
    surf.set_clip(face)
    pygame.draw.ellipse(surf, _RT_VOID, face)
    for gx in range(face.left + 2, face.right - 1, 3):
        pygame.draw.line(surf, _RT_STRING, (gx, face.top + 1), (gx, face.bottom - 1), 1)
    for gy in range(face.top + 2, face.bottom - 1, 3):
        pygame.draw.line(surf, _RT_STRING, (face.left + 1, gy), (face.right - 1, gy), 1)
    surf.set_clip(clip_prev)

    # BOLD two-tone WOOD frame — a 3px dark LAMINATE keyline (the signature dark
    # lacquer rim of a '70s laminated racket) wrapping a 4px honey body ring,
    # with a bright sheen arc up the near side. The frame is the whole read once
    # the strings sink, so it carries real mass and is the prop's boldest element.
    pygame.draw.ellipse(surf, _RT_WOOD_D, face.inflate(4, 4), 3)   # bold dark laminate edge
    pygame.draw.ellipse(surf, _RT_WOOD, face, 4)                   # bold honey frame body
    pygame.draw.arc(surf, _RT_WOOD_H, face.inflate(-2, -2),
                    math.radians(70), math.radians(200), 2)        # wood sheen arc

    # Throat — two THICK honey struts splaying from the handle into the head, the
    # signature racket Y, with a tiny navy throat DECAL where they meet (the
    # painted brand badge a wood racket carries at the throat). Thicker than the
    # round-1 struts so the eye traces head→throat→grip as one held object.
    ty = hy + rh
    pygame.draw.line(surf, _RT_WOOD_D, (hx - 1, ty + 6), (hx - rw + 2, ty - 2), 6)
    pygame.draw.line(surf, _RT_WOOD_D, (hx + 1, ty + 6), (hx + rw - 2, ty - 2), 6)
    pygame.draw.line(surf, _RT_WOOD, (hx - 1, ty + 5), (hx - rw + 3, ty - 1), 4)
    pygame.draw.line(surf, _RT_WOOD, (hx + 1, ty + 5), (hx + rw - 3, ty - 1), 4)
    pygame.draw.circle(surf, _RT_NAVY, (hx, ty + 1), 2)            # throat decal
    pygame.draw.circle(surf, _RT_RED, (hx, ty + 1), 1)

    # Wrapped LEATHER handle — LONGER and dropped into the near wing so the grip
    # visibly tucks the prop into Pip's body (no float). Warm brown wrap with
    # cross-wrap ticks + a wood butt cap so it reads as a leather-bound handle.
    hbx, hby = hx, ty + 6
    htx, hty = hx + 6, hby + 18
    pygame.draw.line(surf, _RT_WOOD_D, (hbx, hby), (htx, hty), 8)  # grip core
    pygame.draw.line(surf, _RT_GRIP, (hbx, hby), (htx, hty), 6)    # leather wrap
    for t in (0.3, 0.5, 0.7, 0.9):                                 # cross-wrap ticks
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

    # Navy CAP-SLEEVE bands at the wing roots — drawn as a clear filled cap shape
    # (not a 2px nick) so the banded-sleeve read survives 40px instead of reading
    # as an ambiguous dark speck. Navy nudged lighter so it holds at night too.
    _poly(surf, _RT_NAVY_M, [(HX - 13, HY + 9), (HX - 14, HY + 16),
                             (HX - 11, HY + 16), (HX - 11, HY + 9)])
    _poly(surf, _RT_NAVY_M, [(HX + 11, HY + 9), (HX + 12, HY + 16),
                             (HX + 9, HY + 16), (HX + 9, HY + 9)])

    # Retro red + navy CHEST PIPING down the placket — the ONE bold chest move:
    # two thin vertical stripes framing the placket. The round-1 button dots were
    # sub-pixel noise at 40px, so they're cut; the stripes + shawl V carry it.
    pygame.draw.line(surf, _RT_RED, (HX - 4, HY + 11), (HX - 4, HY + 22), 2)
    pygame.draw.line(surf, _RT_NAVY_M, (HX + 1, HY + 11), (HX + 1, HY + 22), 2)

    # Retro SHAWL collar — a soft rounded navy-edged collar curving around the
    # neck base, sitting ON the chest (never up in the head). The shawl shape
    # (wider rounded lapels) is what dates it to the '70s vs a sharp modern V.
    shawl = [(HX - 6, HY + 9), (HX - 7, HY + 13), (HX - 3, HY + 12),
             (HX, HY + 14), (HX + 3, HY + 12), (HX + 6, HY + 13),
             (HX + 5, HY + 9)]
    _poly(surf, _RT_ECRU_DD, shawl)
    _poly(surf, _RT_ECRU, [(HX - 5, HY + 9), (HX - 5, HY + 12), (HX, HY + 13),
                           (HX + 4, HY + 12), (HX + 4, HY + 9)])
    pygame.draw.line(surf, _RT_NAVY_M, (HX - 6, HY + 9), (HX - 3, HY + 12), 1)  # navy collar edge
    pygame.draw.line(surf, _RT_NAVY_M, (HX + 5, HY + 9), (HX + 3, HY + 12), 1)

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
    # The triple stripe — red / navy / red as 3 distinct 1px rows (the retro
    # signature). The middle navy uses the lighter mid-navy so it doesn't drop
    # out against the dark face at NIGHT — all three rows must read.
    pygame.draw.line(surf, _RT_RED, (HX - 11, by - 1), (HX + 15, by - 2), 1)
    pygame.draw.line(surf, _RT_NAVY_M, (HX - 11, by), (HX + 15, by - 1), 1)
    pygame.draw.line(surf, _RT_RED, (HX - 11, by + 1), (HX + 15, by), 1)
    # Dark lower edge so the terry band separates from the macaw face beneath.
    pygame.draw.line(surf, _RT_ECRU_DD, (HX - 11, by + 4), (HX + 16, by + 3), 1)

    # --- RACKET drawn LAST so it OVERLAYS the polo/clothing ---------------------
    # Like the baseball BAT, the racket is painted last so the whole prop — head,
    # throat and handle — rests fully IN FRONT of the body. Lowered + pulled in
    # from round-1 (which floated detached above-left) so the throat Y and the
    # LONGER grip visibly tuck into the near wing — head→throat→grip→wing trace
    # as one held object — while the oval head still breaks the back silhouette.
    _racket(surf, HX - 18, CROWN_Y + 6, 7)


build = store_skins._make_skin(_paint)
