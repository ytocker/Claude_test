"""DESIGN 5 — NIGHT MATCH (Tennis, hard-court blue).

Scratch exploration only — NOT registered in store_skins.BUILDERS. Pip the
scarlet macaw kitted for a US/Australian-Open hard court under lights: a white
tennis CAP with one navy front accent + one cyan piping line, a white POLO with
a navy shoulder yoke and a single steep cyan chest sash, a cyan wristband, and
the hero read — a GRAPHITE racket held up in the near wing so the head breaks
the top/back silhouette.

The whole palette is built to POP on the NIGHT sky: white is the brightest
mass, cyan is the single saturated accent, and a COOL-LIGHT outer frame keyline
keeps the navy oval from vanishing against the dark night sky the way a
floodlit court rim catches the lights. Higher resolution here buys FEWER,
cleaner tells — two polo bands (navy yoke + one cyan sash), one navy cap
accent, one bright racket contour — not more competing layers. No ball — it
ships as a separate matching parcel, so the racket carries the read.

The cap silhouette (covered crown + forward curved brim) is deliberately
DIFFERENT from the visor/headband tennis variants so the night-match version is
distinct at a glance; the brim is lifted and shortened so a clear band of
scarlet face + the dark eye + the yellow beak stay visible UNDER it — Pip reads
as a parrot first, athlete second.
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly


# Hard-court blue kit — three carrying values (white field, navy structure,
# cyan accent) plus a deep navy contour and a dark grip. White is lifted near
# pure so the cloth stays the brightest mass on the NIGHT sky; cyan is the lone
# saturated tell so the sport reads before the bird; the navy yoke gives the
# white polo a dark anchor so it never washes out at 40px.
_TN_WHITE   = (244, 246, 248)        # #F4F6F8 polo / cap field
_TN_WHITE_D = (206, 212, 220)        # cool white shade (rounds the cloth/cap)
_TN_WHITE_DD = (168, 176, 188)       # deep fold / contour so white stays crisp
_TN_WHITE_H = (255, 255, 255)        # white highlight
_TN_NAVY    = (22, 48, 107)          # #16306B yoke / cap panel / frame
_TN_NAVY_D  = (12, 30, 74)           # #0C1E4A deep navy contour / frame shadow
_TN_NAVY_H  = (54, 86, 158)          # navy sheen so dark masses read round
_TN_FRAME_L = (168, 176, 188)        # #A8B0BC cool-light outer frame edge so the
                                     # navy oval keeps a bright contour on night
_TN_CYAN    = (43, 184, 224)         # #2BB8E0 sash / bumper / button / wristband
_TN_CYAN_D  = (24, 124, 158)         # cyan shade
_TN_CYAN_H  = (146, 224, 246)        # cyan highlight
_TN_STRING  = (236, 240, 244)        # white mains/crosses
_TN_STR_DIM = (96, 116, 150)         # low-contrast strings on the void
_TN_VOID    = (16, 24, 40)           # near-black open strung face (no inner disc)
_TN_GRIP    = (32, 36, 44)           # #20242C dark grip wrap
_TN_GRIP_H  = (84, 90, 102)          # grip wrap highlight


def _racket(surf, hx, hy, hr):
    """The hero prop and SOLE tennis tell. A GRAPHITE oval: a navy frame ring
    wrapped in a COOL-LIGHT outer keyline (so the oval keeps a bright contour
    against the navy night sky), with a cyan inner bumper line around an OPEN
    strung face (dark void + legible mains/crosses), a clean throat Y, a wrapped
    dark grip and a cyan butt cap. The bright rim + navy frame + cyan bumper
    keep the oval reading ROUND at 40px and separate it from the dark sky. Held
    up so the head breaks the back/top silhouette."""
    rw, rh = int(hr * 1.7), int(hr * 2.1)            # tall tennis-racket oval
    face = pygame.Rect(hx - rw, hy - rh, rw * 2, rh * 2)

    # Dark void interior + LOW-contrast strings so the inside reads as an open
    # strung face, never a filled bright disc. Mains + crosses both drawn so the
    # mesh is legible at hero scale; at 40px the centre stays empty and only the
    # frame + cyan bumper survive.
    clip_prev = surf.get_clip()
    surf.set_clip(face)
    pygame.draw.ellipse(surf, _TN_VOID, face)
    for gx in range(face.left + 3, face.right - 2, 3):
        pygame.draw.line(surf, _TN_STR_DIM, (gx, face.top + 1), (gx, face.bottom - 1), 1)
    for gy in range(face.top + 3, face.bottom - 2, 3):
        pygame.draw.line(surf, _TN_STR_DIM, (face.left + 1, gy), (face.right - 1, gy), 1)
    surf.set_clip(clip_prev)

    # Frame in THREE values so the oval reads round, but the OUTER keyline is a
    # COOL LIGHT (not navy): the navy frame disappears against the navy night
    # sky, so this bright contour is what separates the oval from the dark — the
    # floodlit-rim tell. Then the navy graphite frame, then a cyan inner bumper
    # line hugging the strings (the saturated accent). One clean ring each.
    pygame.draw.ellipse(surf, _TN_FRAME_L, face.inflate(2, 2), 1)  # bright outer rim
    pygame.draw.ellipse(surf, _TN_NAVY, face, 3)                   # graphite frame
    pygame.draw.ellipse(surf, _TN_NAVY_H, face.inflate(-1, -1), 1)  # top-edge sheen
    pygame.draw.ellipse(surf, _TN_CYAN, face.inflate(-4, -4), 1)   # cyan bumper line

    # Throat — two navy struts splaying from the handle into the head (the
    # signature racket Y), carried bold with a cyan inner glint so the V reads
    # even when the cross strings vanish.
    ty = hy + rh
    pygame.draw.line(surf, _TN_NAVY_D, (hx - 1, ty + 5), (hx - rw + 2, ty - 2), 5)
    pygame.draw.line(surf, _TN_NAVY_D, (hx + 1, ty + 5), (hx + rw - 2, ty - 2), 5)
    pygame.draw.line(surf, _TN_NAVY, (hx - 1, ty + 4), (hx - rw + 3, ty - 1), 3)
    pygame.draw.line(surf, _TN_NAVY, (hx + 1, ty + 4), (hx + rw - 3, ty - 1), 3)
    pygame.draw.line(surf, _TN_CYAN, (hx, ty + 3), (hx - rw + 4, ty - 1), 1)

    # Wrapped dark grip dropping into the near wing (kept inside the silhouette).
    hbx, hby = hx, ty + 5
    htx, hty = hx + 4, hby + 12
    pygame.draw.line(surf, _TN_GRIP, (hbx, hby), (htx, hty), 6)
    pygame.draw.line(surf, _TN_GRIP_H, (hbx - 1, hby), (htx - 1, hty), 1)
    # Grip-wrap ticks so the handle reads as a wrapped leather grip.
    for t in (0.35, 0.7):
        wx = hbx + (htx - hbx) * t
        wy = hby + (hty - hby) * t
        pygame.draw.line(surf, _TN_GRIP_H, (wx - 2, wy + 1), (wx + 2, wy - 1), 1)
    # Cyan butt cap — the colour tells the eye where the grip ends.
    pygame.draw.circle(surf, _TN_CYAN, (int(htx), int(hty)), 2)
    pygame.draw.circle(surf, _TN_CYAN_H, (int(htx) - 1, int(hty) - 1), 1)


def _paint(surf, _a):
    # --- White POLO on the FRONT CHEST (BELOW the head) -------------------------
    # Top ~HY+8, hem ~HY+23 (matched to the baseball jersey) so the cloth sits on
    # the chest below the head and NOTHING covers Pip's beak/eye/face. White-
    # filled with a cool lower shade so it reads round + a deep-navy contour so it
    # stays crisp on a bright day sky and pops off the dark night sky. Held inside
    # the footprint so it never balloons the bird.
    polo = [(HX - 13, HY + 8), (HX - 14, HY + 16), (HX - 11, HY + 23),
            (HX + 9, HY + 23), (HX + 12, HY + 16), (HX + 11, HY + 8),
            (HX + 4, HY + 9), (HX - 5, HY + 9)]
    _poly(surf, _TN_WHITE_D, polo)
    # Lit upper body of the cloth so the white isn't flat.
    _poly(surf, _TN_WHITE, [(HX - 12, HY + 9), (HX - 12, HY + 18),
                            (HX + 10, HY + 18), (HX + 10, HY + 9),
                            (HX + 4, HY + 10), (HX - 5, HY + 10)])
    pygame.draw.line(surf, _TN_WHITE_H, (HX - 11, HY + 10), (HX + 8, HY + 10), 1)

    # NAVY YOKE across the shoulders — the SINGLE navy structure band on the
    # polo (the collar-V is cut so the chest carries only TWO tells: this dark
    # yoke + the cyan sash). It anchors the white mass so it doesn't wash out and
    # gives the kit its hard-court navy. Sits ON the chest, never rising into the
    # head.
    yoke = [(HX - 12, HY + 9), (HX + 10, HY + 9), (HX + 9, HY + 13),
            (HX + 2, HY + 12), (HX - 4, HY + 12), (HX - 11, HY + 13)]
    _poly(surf, _TN_NAVY, yoke)
    pygame.draw.line(surf, _TN_NAVY_H, (HX - 11, HY + 10), (HX + 9, HY + 10), 1)

    # ONE thin, STEEP CYAN sash — the single saturated diagonal accent. Taken to
    # a 3px core and raised to cross nearer corner-to-corner (more diagonal reads
    # more obviously as a sash), with 1-2px of clear white kept between the
    # yoke-bottom and the sash-top so the two bands never merge into one bar.
    pygame.draw.line(surf, _TN_CYAN_D, (HX - 12, HY + 21), (HX + 10, HY + 14), 4)
    pygame.draw.line(surf, _TN_CYAN, (HX - 12, HY + 21), (HX + 10, HY + 14), 3)
    pygame.draw.line(surf, _TN_CYAN_H, (HX - 11, HY + 20), (HX + 8, HY + 15), 1)

    # Deep-navy contour so the white polo separates from sky / pillars day + night.
    pygame.draw.polygon(surf, _TN_NAVY_D, polo, 1)

    # --- CYAN WRISTBANDS at the wing roots --------------------------------------
    # A terry band on each cuff — a sport tell kept inside the silhouette. Navy-
    # cored then cyan so the band reads round and the colour pops at hero scale.
    for wx, wy in ((HX + 11, HY + 20), (HX - 13, HY + 19)):
        pygame.draw.line(surf, _TN_NAVY_D, (wx - 3, wy - 3), (wx + 3, wy + 3), 6)
        pygame.draw.line(surf, _TN_CYAN, (wx - 3, wy - 3), (wx + 3, wy + 3), 3)
        pygame.draw.line(surf, _TN_CYAN_H, (wx - 2, wy - 2), (wx + 2, wy + 2), 1)

    # --- White TENNIS CAP (covered crown + forward brim) ------------------------
    # A DIFFERENT silhouette from the visor/headband variants: a white ball-cap
    # shell owns the crown with a navy front panel + cyan button, and a forward
    # curved brim shades the beak — but the brim sits high enough that Pip's
    # beak/eye/face stay clear below it. Adapted from the baseball cap build.
    cy = CROWN_Y - 3
    # Rounded white crown shell raised to sit ON TOP of the head.
    pygame.draw.ellipse(surf, _TN_WHITE, (HX - 13, cy - 5, 26, 15))
    pygame.draw.ellipse(surf, _TN_WHITE_DD, (HX - 13, cy - 5, 26, 15), 1)
    pygame.draw.ellipse(surf, _TN_WHITE_H, (HX - 7, cy - 4, 11, 6))  # top sheen
    # ONE navy front panel + ONE cyan piping line — the cap's only two accents,
    # so it stays a LIGHT-touch silhouette and doesn't steal read from the polo
    # sash (the cyan button is dropped). The navy panel is the team colour; the
    # cyan piping along its base is the single bright tie to the kit.
    _poly(surf, _TN_NAVY, [(HX - 6, cy + 1), (HX + 9, cy - 1), (HX + 10, cy + 5),
                           (HX - 5, cy + 6)])
    pygame.draw.line(surf, _TN_NAVY_H, (HX - 5, cy + 1), (HX + 8, cy - 1), 1)
    pygame.draw.line(surf, _TN_CYAN, (HX - 5, cy + 6), (HX + 10, cy + 5), 1)
    # Forward curved BRIM — LIFTED 1px and SHORTENED ~2px on the right so it
    # stops well short of the eye: a clear band of scarlet face + the dark eye +
    # the yellow beak stay visible UNDER it at 40px, so Pip reads as a parrot
    # first. White wedge with a navy under-shadow so it reads as a separate brim.
    brim = [(HX + 3, cy + 4), (HX + 16, cy + 2), (HX + 17, cy + 6),
            (HX + 4, cy + 8)]
    _poly(surf, _TN_WHITE, brim)
    _poly(surf, _TN_NAVY_D, [(HX + 4, cy + 7), (HX + 17, cy + 6),
                             (HX + 16, cy + 8), (HX + 4, cy + 8)])  # brim shade
    pygame.draw.line(surf, _TN_WHITE_H, (HX + 4, cy + 4), (HX + 15, cy + 2), 1)

    # --- RACKET drawn LAST so it OVERLAYS the polo/clothing ----------------------
    # Painted last so the whole prop — head, throat, grip — rests fully IN FRONT
    # of the body. The grip drops into the near wing over the chest; the oval head
    # still breaks the top/back silhouette against open sky. Nudged ~2px LEFT so
    # the oval clears the white cap crown — two white-edged masses fuse at 40px
    # unless they keep a gap to breathe.
    _racket(surf, HX - 23, CROWN_Y + 2, 7)


build = store_skins._make_skin(_paint)
