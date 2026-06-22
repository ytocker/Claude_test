"""design_5 — SKIRMISHER: the lean quick-raider Viking face + a light single-hand
bearded HATCHET held FORWARD and low (ready-to-throw stance).

The other holds carry a war-axe ACROSS the body; the Skirmisher instead grips a
short hatchet out in front of the belly with the head pointing FORWARD/out past
the chest, the short haft angling forward and low — a fast hunter about to loose.
The face reads as facial hair, not a brute's bib: a sharp ALMOND eye (pale lid +
heavy dark brow + pupil + glint), a THIN POINTED mustache swept past the beak,
and a short POINTED GOATEE tapering to ONE bead-capped point — lighter than the
brute beards, beak kept visible.

Reads at 40px because each landmark owns one value tier and one silhouette: the
eye is a pale almond punched under a heavy dark brow; the mustache is two thin
dark whiskers whose fine tips break the cheek past the beak; the goatee is a
single narrow tuft separated from the brown body by a darker keyed core, capped
by a P['ring'] bead. The axe is drawn at NATIVE res (a supersample smears the
small bit) with a dark-keyed back, bright steel face, and a white edge glint.

Scratch exploration only — NOT registered in store_skins.BUILDERS; the live
skin_viking is untouched.
"""
import pygame

from tools.viking_face_candidates import _shared as S
from game.store_skins import _poly


def _shade(rgb):
    """A darker sibling of a base colour so facial hair / the haft separate from
    the brown body without needing a dedicated palette role."""
    return tuple(max(0, int(c * 0.6)) for c in rgb)


def _paint_face(surf, wing_angle, P):
    """An alert almond eye, a thin pointed mustache swept past the beak, and a
    short pointed goatee with a bead. The head sits at (47,41), the beak pokes
    RIGHT at x≈55-61, the helm nasal drops at x≈48..51 down to y≈46 — so the
    face lives just right of and below that nasal."""
    beard, beard_hi = P["beard"], P["beard_hi"]
    ring, bone = P["ring"], P["bone"]
    eye_skin, eye_pupil, eye_glint = P["eye_skin"], P["eye_pupil"], P["eye_glint"]
    dark = _shade(beard)

    # ── ALERT EYE: a forward-raked almond (NOT round) in the cheek, right of the
    #    nasal and clear of the helm brow band. A dark eye-socket patch behind a
    #    BIG pale lid + a heavy angled brow + a pupil packed to the beak-side
    #    corner = a focused hunting glare that survives the 40px shrink.
    ex, ey = 51, 44
    _poly(surf, dark, [(ex - 6, ey + 1), (ex - 2, ey - 4),
                       (ex + 6, ey - 2), (ex, ey + 4)])                        # socket shadow
    pygame.draw.line(surf, eye_pupil, (ex - 5, ey - 4), (ex + 4, ey - 2), 2)   # hard angled brow
    _poly(surf, eye_skin, [(ex - 5, ey + 1), (ex - 1, ey - 3),
                           (ex + 5, ey - 1), (ex, ey + 3)])                    # big almond lid
    pygame.draw.circle(surf, eye_pupil, (ex + 2, ey - 1), 2)                    # forward pupil
    pygame.draw.circle(surf, eye_glint, (ex + 3, ey - 2), 1)                    # glint

    # ── THIN POINTED MUSTACHE: one fine whisker each side of the beak base,
    #    tapering to a sharp tip that sweeps DOWN-and-out past the cheek outline,
    #    leaving the beak visible in the gap between them. Sits BELOW the eye so
    #    the two landmarks don't merge.
    mcy = 50
    for sgn, rootx in ((-1, 52), (1, 55)):
        tipx, tipy = rootx + sgn * 6, mcy + 3
        _poly(surf, beard, [
            (rootx, mcy - 1), (rootx + sgn, mcy + 2),
            (rootx + sgn * 4, mcy + 2), (tipx, tipy),
        ])
        pygame.draw.line(surf, beard_hi, (rootx, mcy - 1), (tipx, tipy), 1)     # lit ridge
        pygame.draw.circle(surf, beard, (tipx, tipy), 1)                        # fine tip

    # ── SHORT POINTED GOATEE: a compact chin tuft DIRECTLY below the mustache,
    #    tapering to ONE point, kept lighter than the brute beards with a darker
    #    keyed core so it separates from the brown body, capped by a ring bead.
    cx, top = 53, 51
    _poly(surf, dark, [(cx - 4, top), (cx + 4, top), (cx + 2, top + 4),
                       (cx, top + 7), (cx - 2, top + 4)])                       # keyed core
    _poly(surf, beard, [(cx - 3, top + 1), (cx + 3, top + 1),
                        (cx + 1, top + 4), (cx, top + 6), (cx - 1, top + 4)])    # lighter tuft
    pygame.draw.line(surf, beard_hi, (cx - 2, top + 2), (cx + 1, top + 4), 1)   # plait sheen
    # Bright bead at the goatee tip — a high-value dot (like the braid rings on
    # the brutes) so the chin point still names the goatee at 40px.
    pygame.draw.circle(surf, dark, (cx, top + 8), 3)                           # bead seat
    pygame.draw.circle(surf, ring, (cx, top + 8), 2)                           # ring bead
    pygame.draw.circle(surf, bone, (cx - 1, top + 7), 1)                       # bead glint


def _paint_axe(surf, wing_angle, P):
    """A light single-hand bearded HATCHET held FORWARD and low: the gripping claw
    out in front of the belly, the short haft angling forward, the bearded head
    thrust FORWARD/out past the chest (ready-to-throw). Native-res so the small
    bit stays crisp."""
    blade, blade_dk, blade_hi = P["blade"], P["blade_dk"], P["blade_hi"]
    haft, haft_hi, white = P["haft"], P["haft_hi"], P["white"]
    bone = P["bone"]
    dark = _shade(haft)

    # Grip in front of the belly; the short haft runs FORWARD-and-UP to a socket
    # at BEAK level, so the bearded head thrusts out into the clear sky directly
    # in FRONT of the beak with the edge leading FORWARD (a ready-to-throw lunge).
    # That open-sky placement reads at 40px; it sits below the helm horn and right
    # of the face, distinct from the across-body holds whose heads ride up past
    # the SHOULDER behind the head.
    gx, gy = 45, 57          # gripping claw at the belly
    sx, sy = 64, 49          # hatchet socket, forward at beak level (clear of the horn)
    ux, uy = sx - gx, sy - gy
    ln = (ux * ux + uy * uy) ** 0.5 or 1.0
    ux, uy = ux / ln, uy / ln
    px, py = -uy, ux         # haft normal (points up-forward of the haft)

    # ── short wooden HAFT with a dark keyed core + lit flank, butt-spike behind
    #    the grip so the pole doesn't float.
    butt = (gx - ux * 5, gy - uy * 5)
    pygame.draw.line(surf, dark, butt, (sx, sy), 4)
    pygame.draw.line(surf, haft, butt, (sx, sy), 3)
    pygame.draw.line(surf, haft_hi, (gx + px, gy + py), (sx + px, sy + py), 1)
    for t in (0.5, 0.72):                                       # lashing wraps near head
        wx, wy = gx + (sx - gx) * t, gy + (sy - gy) * t
        pygame.draw.line(surf, dark, (wx + px * 2, wy + py * 2),
                         (wx - px * 2, wy - py * 2), 1)
    pygame.draw.circle(surf, dark, (int(butt[0]), int(butt[1])), 2)   # butt cap

    # ── bearded HATCHET HEAD thrust FORWARD of the socket into clear sky in front
    #    of the beak: ux leads FORWARD (the pointed toe), the long lower beard
    #    hooks DOWN (more edge on the bottom, the defining bearded shape). Chunky
    #    enough to survive the 40px shrink. Dark keyed back, bright steel face
    #    inset, white edge glint on the leading arc.
    cx, cy = sx, sy
    head = [
        (cx - ux * 2 - px * 5, cy - uy * 2 - py * 5),    # back-top heel
        (cx + ux * 11 - px * 4, cy + uy * 11 - py * 4),  # leading TOE (forward point)
        (cx + ux * 12 + px * 3, cy + uy * 12 + py * 3),  # cutting-edge front-top
        (cx + ux * 7 + px * 11, cy + uy * 7 + py * 11),  # bearded HOOK (forward-down, widest)
        (cx - ux * 1 + px * 9, cy - uy * 1 + py * 9),    # lower heel
        (cx - ux * 2 + px * 3, cy - uy * 2 + py * 3),    # back-bottom inner
    ]
    _poly(surf, blade_dk, head)
    face = [
        (cx + ux * 9 - px * 2, cy + uy * 9 - py * 2),
        (cx + ux * 9 + px * 2, cy + uy * 9 + py * 2),
        (cx + ux * 6 + px * 9, cy + uy * 6 + py * 9),
        (cx + ux * 1 + px * 7, cy + uy * 1 + py * 7),
        (cx + ux * 1 + px * 2, cy + uy * 1 + py * 2),
    ]
    _poly(surf, blade, face)
    pygame.draw.line(surf, blade_hi,
                     (cx + ux * 8 + px * 1, cy + uy * 8 + py * 1),
                     (cx + ux * 5 + px * 8, cy + uy * 5 + py * 8), 1)
    # WHITE edge glint along the leading cutting arc — the hero sparkle.
    pygame.draw.line(surf, white,
                     (cx + ux * 11 - px * 3, cy + uy * 11 - py * 3),
                     (cx + ux * 7 + px * 9, cy + uy * 7 + py * 9), 1)
    pygame.draw.circle(surf, white, (int(cx + ux * 11 - px * 4), int(cy + uy * 11 - py * 4)), 1)  # toe spark
    # iron socket where the haft passes through.
    pygame.draw.circle(surf, blade_dk, (int(cx), int(cy)), 2)
    pygame.draw.circle(surf, blade_hi, (int(cx + px), int(cy - py)), 1)

    # ── claw GRIP closing OVER the haft at the belly (haft/bone tones — no 'foot'
    #    role) so the hatchet reads HELD, not floating.
    for k in (-1, 0, 1):
        kx, ky = gx + px * k * 2, gy + py * k * 2
        pygame.draw.circle(surf, dark, (int(kx), int(ky)), 2)
    pygame.draw.line(surf, bone, (gx, gy), (gx + 3, gy + 3), 1)
    pygame.draw.line(surf, bone, (gx - 2, gy), (gx, gy + 3), 1)
    pygame.draw.circle(surf, haft_hi, (gx - 1, gy - 1), 1)


build_ironclad = S.make_build(_paint_face, _paint_axe, S.IRONCLAD)
build_bloodaxe = S.make_build(_paint_face, _paint_axe, S.BLOODAXE)
