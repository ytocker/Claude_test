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
dark whiskers whose fine tips break the cheek past the beak; the goatee is one
clean pointed wedge keyed LIGHTER than the body and rimmed by a near-black
separator (so it holds on the rust palette where a dark core would vanish),
capped by the single P['ring'] chin bead. The hatchet head is a chunky flat
WEDGE thrust into open sky past the beak — a straight top, a full-width leading
cutting arc carrying a continuous bright-steel edge — so it names "axe" at
distance. Drawn at NATIVE res (a supersample smears the small bit).

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

    # ── SHORT POINTED GOATEE: ONE clean pointed wedge hanging clearly BELOW the
    #    beak line — no busy keyed-core/plait detail (it turns to mud at 40px). A
    #    single slightly-longer triangle, keyed LIGHTER than the body (beard_hi)
    #    so it survives on BLOODAXE where a dark core would vanish, ringed by a
    #    1px near-black separator so it never melts into the chest. The P['ring']
    #    bead is the ONLY bead near the chin and unambiguously caps the tip.
    key = P["keyline"][:3]
    cx, top = 53, 52
    goatee = [(cx - 3, top), (cx + 3, top), (cx, top + 9)]                      # one long point
    pygame.draw.polygon(surf, key, [(cx - 4, top - 1), (cx + 4, top - 1),
                                    (cx, top + 11)])                            # near-black rim
    _poly(surf, beard_hi, goatee)                                              # light pointed tuft
    pygame.draw.line(surf, beard, (cx, top + 1), (cx, top + 8), 1)             # central shade seam
    # The ONE chin bead — capping the goatee point, clear of the helm braid rings.
    pygame.draw.circle(surf, key, (cx, top + 10), 3)                           # bead seat (near-black)
    pygame.draw.circle(surf, ring, (cx, top + 10), 2)                          # ring bead
    pygame.draw.circle(surf, bone, (cx - 1, top + 9), 1)                       # bead glint


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
    sx, sy = 67, 48          # hatchet socket, pushed further into OPEN SKY past the beak
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

    # ── bearded HATCHET HEAD thrust FORWARD into clear sky past the beak, redrawn
    #    as a CHUNKY FLAT WEDGE (not a lump): a crisp STRAIGHT top edge runs
    #    forward (ux), the leading CUTTING ARC fans the full width (px) from an
    #    up-forward top corner down to a long bearded bottom hook, so the
    #    silhouette reads unmistakably as an axe blade. ~28% larger than before.
    #    Dark-keyed back, bright steel face, and a continuous bright-steel edge.
    cx, cy = sx, sy

    def pt(f, p):
        return (cx + ux * f + px * p, cy + uy * f + py * p)

    # leading cutting-edge corners (top -> bottom) and the back heels.
    edge_top = pt(15, -3)     # forward-TOP toe of the blade
    edge_bot = pt(11, 14)     # long bearded bottom hook (most edge on the underside)
    top_back = pt(2, -6)      # crisp straight TOP back corner
    bot_back = pt(-1, 10)     # bottom-back heel
    head = [top_back, edge_top, edge_bot, bot_back, pt(-2, 2)]
    _poly(surf, blade_dk, head)
    # bright steel FACE inset, leaving a dark-keyed back rim so the wedge has body.
    face = [pt(2, -3), pt(12, -1), pt(9, 11), pt(1, 8), pt(1, 0)]
    _poly(surf, blade, face)
    pygame.draw.line(surf, blade_hi, pt(4, -2), pt(11, 0), 1)        # top-face sheen
    # CONTINUOUS 2px bright-steel EDGE down the full leading cutting arc — the
    # single feature that names "axe" at distance.
    pygame.draw.line(surf, blade_hi, edge_top, edge_bot, 2)
    pygame.draw.line(surf, white, edge_top, pt(13, 6), 1)           # whitest near the toe
    pygame.draw.circle(surf, white, (int(edge_top[0]), int(edge_top[1])), 1)  # toe spark
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
