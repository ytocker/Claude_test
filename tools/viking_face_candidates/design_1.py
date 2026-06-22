"""DESIGN 1 — WARCHIEF: a Viking PARROT face (one fierce eye + a bold handlebar
mustache + a forked twin-braid beard) wearing the frozen base costume, holding a
big single-bit bearded axe diagonally across the body.

Scratch exploration only — wrapped by ``_shared.make_build`` in BOTH palettes
(IRONCLAD / BLOODAXE); NOT registered in ``store_skins.BUILDERS``, so the live
``skin_viking`` is untouched.

Reads at 40px because the three face landmarks each own one value tier and one
silhouette: the EYE is a dark almond punched under the helm brow with a white
glint, the MUSTACHE is one bold dark bar with ENDS sweeping UP past the beak so
it breaks the cheek outline, and the BEARD forks into two fat ring-capped braids
with a clean V-notch between them (facial hair, not a blob). The axe pose is
modelled on ``knight_skin._sword`` — grip LOW at the belly with a few dark claw
pixels gripping the haft, head sweeping UP past the shoulder so it breaks the
silhouette and is never occluded (drawn last).
"""
import pygame

from tools.viking_face_candidates import _shared as S
from game.store_skins import HX, HY, CROWN_Y, _poly


def _paint_face(surf, wing_angle, P):
    """One fierce eye under the helm brow, a handlebar mustache framing the beak,
    and a forked twin-braid beard with ring-capped tips below.

    The composite head sits at (HX,HY)=(47,41) with the beak poking RIGHT at
    x≈55-61,y≈41-48 and the helm nasal bar dropping at x≈HX+1..HX+4 down to
    y≈46. So the face lives to the RIGHT of and BELOW that nasal: eye in the
    cheek under the brow, mustache hugging the beak base, beard forking down
    over the body."""
    beard, beard_hi = P["beard"], P["beard_hi"]
    ring, bone, white = P["ring"], P["bone"], P["white"]
    eye_skin, eye_pupil, eye_glint = P["eye_skin"], P["eye_pupil"], P["eye_glint"]
    dark = _shade(beard)

    # ── one fierce EYE in the cheek, just right of the nasal and below the brow
    #    band, so it always clears the helm. Heavy brow line + pale almond +
    #    dark pupil + white glint give the glare.
    ex, ey = 49, 45
    pygame.draw.line(surf, eye_pupil, (ex - 5, ey - 4), (ex + 4, ey - 3), 3)  # heavy brow
    pygame.draw.ellipse(surf, eye_skin, (ex - 5, ey - 2, 11, 6))             # almond white
    pygame.draw.circle(surf, eye_pupil, (ex + 1, ey + 1), 3)                 # pupil
    pygame.draw.circle(surf, eye_glint, (ex, ey - 1), 1)                    # glint

    # ── handlebar MUSTACHE hugging the beak base, ENDS sweeping UP so they break
    #    the cheek outline. Kept right of the nasal and low enough that the beak
    #    still pokes out above-right (x≈58-61).
    mcx, mcy = 50, 50
    _poly(surf, beard, [
        (mcx - 6, mcy - 1), (mcx + 6, mcy - 1),       # top edge, under the beak
        (mcx + 9, mcy - 6),                           # RIGHT end sweeps UP
        (mcx + 6, mcy - 3), (mcx + 2, mcy + 3),       # right droop
        (mcx - 3, mcy + 3), (mcx - 6, mcy - 2),       # left droop
        (mcx - 9, mcy - 6),                           # LEFT end sweeps UP
        (mcx - 6, mcy - 1),
    ])
    pygame.draw.circle(surf, beard, (mcx + 9, mcy - 6), 2)   # curled right tip
    pygame.draw.circle(surf, beard, (mcx - 9, mcy - 6), 2)   # curled left tip
    pygame.draw.line(surf, beard_hi, (mcx - 4, mcy - 1), (mcx + 4, mcy - 1), 1)  # lit ridge

    # ── forked twin-braid BEARD hanging from the chin over the body, two fat
    #    braids splaying apart with a clean V-notch between and a P['ring'] band
    #    capping each tip.
    by0 = 53
    for sgn, bx in ((-1, 46), (1, 53)):
        # Each fat braid is a dark base column with a BRIGHTER lit face on its
        # outer flank, so the two braids hold their own silhouette against the
        # body rather than merging into one dark blob.
        for j in range(5):
            yy = by0 + j * 3
            xx = bx + sgn * (j + 1)                    # the braids splay apart going down
            r = 4 - (j // 3)
            pygame.draw.circle(surf, dark, (xx, yy), r)
            pygame.draw.circle(surf, beard, (xx + sgn, yy - 1), max(1, r - 1))  # lit outer flank
        for j in range(4):                             # plaited cross-weave ticks
            yy = by0 + 1 + j * 3
            xx = bx + sgn * (j + 1)
            pygame.draw.line(surf, beard_hi, (xx, yy), (xx + sgn * 2, yy - 1), 1)
        # ring-capped braid tip — a bright metal band that pops on the dark braid.
        tipx, tipy = bx + sgn * 6, by0 + 14
        pygame.draw.circle(surf, dark, (tipx, tipy + 1), 3)
        pygame.draw.rect(surf, ring, (tipx - 3, tipy - 2, 6, 4))
        pygame.draw.line(surf, P["helm_hi"], (tipx - 2, tipy - 2), (tipx + 2, tipy - 2), 1)
        pygame.draw.circle(surf, bone, (tipx, tipy + 3), 1)   # tassel
    # V-notch: a wedge of body-colour driven up between the braids so the FORK
    # reads as two braids, not one mass. A bright centre seam sharpens the split.
    _poly(surf, dark, [(49, by0 + 13), (46, by0 + 2), (52, by0 + 2)])
    pygame.draw.line(surf, eye_pupil, (49, by0 + 2), (49, by0 + 11), 1)
    pygame.draw.line(surf, beard_hi, (47, by0 + 3), (47, by0 + 9), 1)
    pygame.draw.line(surf, beard_hi, (51, by0 + 3), (51, by0 + 9), 1)


def _paint_axe(surf, wing_angle, P):
    """A big SINGLE-BIT bearded axe held diagonally across the body — pose
    modelled on knight_skin._sword: grip LOW at the belly with dark claw pixels
    on the haft, the bearded head sweeping UP past the shoulder, never occluded."""
    blade, blade_dk, blade_hi = P["blade"], P["blade_dk"], P["blade_hi"]
    haft, haft_hi, white = P["haft"], P["haft_hi"], P["white"]
    eye_pupil = P["eye_pupil"]

    # Haft rises on the RIGHT of the face: grip low at the belly claw zone, neck
    # up past the near shoulder, kept right of x≈56 so the pole never crosses the
    # eye/mustache/beard while the head still fits the 64px canvas.
    gx, gy = 49, 61          # grip — claw zone at the belly
    tx, ty = 59, 31          # neck just below the axe head, up past the shoulder
    ux, uy = tx - gx, ty - gy
    ln = (ux * ux + uy * uy) ** 0.5 or 1.0
    ux, uy = ux / ln, uy / ln
    px, py = -uy, ux         # perpendicular, for haft thickness

    # ── wooden HAFT, dark keyed core + lit flank so the pole reads on any sky.
    for w, col in ((3, haft), (1, haft_hi)):
        pygame.draw.line(surf, col,
                         (gx + px * (w * 0.0), gy + py * (w * 0.0)),
                         (tx, ty), 3 if col is haft else 1)
    pygame.draw.line(surf, haft, (gx, gy), (tx, ty), 3)
    pygame.draw.line(surf, haft_hi, (gx - px, gy - py), (tx - px, ty - py), 1)
    # Butt-cap below the grip so the pole doesn't float.
    pygame.draw.line(surf, haft, (gx, gy), (gx - ux * 4, gy - uy * 4), 3)

    # ── claw GRIP: a few dark knuckle pixels wrapping the haft at the belly so
    #    the axe reads as HELD, not floating.
    for k in (-1, 0, 1):
        kx = gx - ux * 2 + px * k * 2
        ky = gy - uy * 2 + py * k * 2
        pygame.draw.circle(surf, eye_pupil, (int(kx), int(ky)), 2)
    pygame.draw.circle(surf, haft_hi, (gx - 1, gy - 1), 1)

    # ── bearded AXE HEAD crowning the haft, fitted to the 64px canvas: a single
    #    big bit whose lower edge "beards" DOWN toward the haft (the defining
    #    Viking shape), cutting edge facing up-and-right. Dark keyed back/cheek,
    #    bright steel face, WHITE edge glint on the chopping arc.
    #    Helper: a point at axial distance `u` up the haft + perpendicular `p`
    #    out toward the bit (right). Clamped to x≤62 so nothing clips.
    def H(u, p):
        return (min(62, int(tx + ux * u + px * p)), int(ty + uy * u + py * p))

    head = [
        H(-2, 0),    # eye/socket at the haft
        H(6, 1),     # top horn of the bit
        H(7, 7),     # cutting-edge top corner
        H(2, 9),     # widest bite (mid edge)
        H(-5, 7),    # bearded lower hook sweeping back down to the haft
        H(-4, 1),    # back-bottom at the haft
    ]
    _poly(surf, blade_dk, head)
    face = [H(5, 2), H(6, 6), H(1, 7), H(-3, 5), H(-1, 2)]   # bright steel cheek
    _poly(surf, blade, face)
    pygame.draw.line(surf, blade_hi, H(5, 3), H(2, 6), 1)    # cheek highlight
    # WHITE edge glint along the chopping arc — the axe's hero sparkle.
    pygame.draw.line(surf, white, H(7, 7), H(2, 9), 1)
    pygame.draw.circle(surf, white, H(7, 7), 1)


def _shade(rgb):
    """A darker sibling of a base colour for braid-lobe value alternation,
    derived so it works in either palette without a dedicated role."""
    return tuple(max(0, int(c * 0.62)) for c in rgb)


build_ironclad = S.make_build(_paint_face, _paint_axe, S.IRONCLAD)
build_bloodaxe = S.make_build(_paint_face, _paint_axe, S.BLOODAXE)
