"""RAIDER — lean seafarer Viking FACE + held DANE-AXE (scratch exploration).

The counterpoint to the bulky horned raiders: a wiry seafarer read built on
LENGTH, not bulk. The mustache plaits down into ONE long single rope-braid
beard — a plaited cord cinched by P['ring'] bindings that hangs well below the
chest, its tip trailing slightly with the wing beat so the bird reads as
"flying fast". The weapon is a TALL DANE-AXE: a long thin haft held nearly
vertical along the body (butt low at the belly with a visible knuckled grip),
its compact crescent head breaking the silhouette above the crown. The tall
poleaxe line is the silhouette tell that separates this from the broad-bladed
bruiser raiders.

Reads at 40px as: narrowed eye + framed beak, a single long rope hanging under
the chin, and a tall vertical pole topped by a small crescent. Exploration
only; nothing here is registered in store_skins.BUILDERS.
"""
import pygame

from tools.viking_face_candidates import _shared as S

HX, HY, CROWN_Y = 47, 41, 31


def _paint_face(surf, wing_angle, P):
    beard = P["beard"]
    beard_hi = P["beard_hi"]
    ring = P["ring"]

    # The bird faces RIGHT in this composite (head at HX, beak poking out at
    # x≈55-61), so every face landmark sits on the head's front/right and the
    # rope-braid hangs from the chin just under the beak.

    # ── Narrowed, determined EYE under the helm brow at ~(51,43): an almond of
    # eye_skin so it survives the downscale, a heavy lid pressing it into a
    # squint, low pupil + glint so it reads "squinting into the spray".
    ex, ey = 51, 43
    pygame.draw.ellipse(surf, P["eye_skin"], (ex - 4, ey - 2, 9, 5))
    pygame.draw.line(surf, beard, (ex - 4, ey - 2), (ex + 4, ey - 3), 2)   # heavy lid
    pygame.draw.circle(surf, P["eye_pupil"], (ex + 1, ey + 1), 2)
    pygame.draw.circle(surf, P["eye_glint"], (ex, ey), 1)

    # ── BRAIDED MUSTACHE framing the beak. Two plaited cords sweep off the lip
    # around the beak base (which pokes through at x≈55-61) and draw INWARD to a
    # chin bind. Each cord is a short stack of offset segments reading as plait.
    mcx, mcy = HX + 6, HY + 8          # under the beak base
    # Outer (right) cord sweeps out past the beak then curls down and inboard to
    # the chin bind at (HX+3, mcy+11).
    rm = [(mcx + 10, mcy - 3), (mcx + 12, mcy + 1), (mcx + 8, mcy + 6),
          (HX + 3, mcy + 9)]
    pygame.draw.lines(surf, beard, False, rm, 3)
    pygame.draw.lines(surf, beard_hi, False, [(x, y - 1) for x, y in rm[:3]], 1)
    pygame.draw.circle(surf, beard, (mcx + 12, mcy + 1), 2)   # curled lit tip
    # Inner (left) cord under the cheek, also drawing down to the chin bind.
    lm = [(mcx - 8, mcy - 1), (mcx - 9, mcy + 3), (mcx - 4, mcy + 7),
          (HX + 3, mcy + 9)]
    pygame.draw.lines(surf, beard, False, lm, 3)
    pygame.draw.lines(surf, beard_hi, False, [(x, y - 1) for x, y in lm[:3]], 1)
    pygame.draw.circle(surf, beard, (mcx - 9, mcy + 3), 2)
    # Plait ticks across each mustache wing so they read woven, not smeared.
    for cx, cy in ((mcx + 8, mcy + 1), (mcx - 6, mcy + 2)):
        pygame.draw.line(surf, beard_hi, (cx - 2, cy - 1), (cx + 2, cy + 1), 1)

    # ── Chin bind where the two mustache cords gather before the single braid
    # drops — a metal ring hiding the join. Pulled inboard (toward head centre)
    # so the rope hangs under the chin with clear daylight between it and the
    # near-vertical axe haft on the body's right edge.
    jx, jy = HX + 3, mcy + 11
    pygame.draw.circle(surf, ring, (jx, jy), 3)
    pygame.draw.circle(surf, P["bone"], (jx, jy), 2)
    pygame.draw.circle(surf, P["helm_hi"], (jx - 1, jy - 1), 1)

    # ── SINGLE LONG ROPE-BRAID BEARD from the chin bind straight down past the
    # chest; the TIP trails sideways with the wing beat (the ninja-headband
    # flick). Three P['ring'] bindings cinch it so the read is "one decorated
    # rope", not a beard blob.
    flick = int(round(wing_angle * 0.12))
    seg = [
        (jx, jy + 2),
        (jx + 1, jy + 9),
        (jx - 1, jy + 16),
        (jx + 1, jy + 23),
        (jx + flick, jy + 29),         # trailing tip, animated
    ]
    pygame.draw.lines(surf, beard, False, seg, 5)            # dark cord body
    pygame.draw.lines(surf, beard_hi, False, seg, 2)         # lit round core
    # Plait cross-ticks down the cord between the bindings → the woven look.
    for i, ty in enumerate((jy + 6, jy + 12, jy + 19, jy + 26)):
        bx = jx + (1 if i % 2 else -1)
        pygame.draw.line(surf, beard, (bx - 3, ty - 1), (bx + 3, ty + 1), 1)
        pygame.draw.line(surf, beard_hi, (bx - 2, ty), (bx + 2, ty + 1), 1)
    # Three metal ring bindings cinching the rope at intervals.
    for ry, rr in ((jy + 9, 3), (jy + 17, 3), (jy + 25, 2)):
        pygame.draw.circle(surf, ring, (jx, ry), rr)
        pygame.draw.circle(surf, P["bone"], (jx, ry), rr - 1)
        pygame.draw.circle(surf, P["helm_hi"], (jx - 1, ry - 1), 1)
    # Frayed split tip below the lowest ring so the rope visibly ends.
    tipx, tipy = jx + flick, jy + 29
    pygame.draw.line(surf, beard, (jx, jy + 26), (tipx - 2, tipy + 3), 2)
    pygame.draw.line(surf, beard, (jx, jy + 26), (tipx + 2, tipy + 2), 2)
    pygame.draw.line(surf, beard_hi, (jx, jy + 26), (tipx, tipy + 1), 1)


def _paint_axe(surf, wing_angle, P):
    blade = P["blade"]
    blade_dk = P["blade_dk"]
    blade_hi = P["blade_hi"]
    haft = P["haft"]
    haft_hi = P["haft_hi"]
    white = P["white"]

    # The Dane-axe is held near-VERTICAL down the body's NEAR (right) side so it
    # never crosses the centred rope-braid: butt LOW at the belly, head UP past
    # the crown. A faint sway with the wing beat sells "carried", not a mast.
    sway = int(round(wing_angle * 0.06))

    # Anchor points: knuckled grip low at the belly, head high above the crown.
    # Tilted a few px off true-vertical so the long pole reads as held.
    bx, by = 62, 59                   # butt of the haft at the belly, right side
    hx, hy = 64 + sway, CROWN_Y - 13  # haft top, where the head is socketed
    ux, uy = hx - bx, hy - by
    ln = max(1.0, (ux * ux + uy * uy) ** 0.5)
    ux, uy = ux / ln, uy / ln
    px, py = -uy, ux                  # perpendicular, for thickness/blade offset

    # ── Long thin HAFT (the Dane-axe tell). Dark core + a lit edge stripe so it
    # reads as a turned wooden pole, with a few binding wraps near the grip.
    pygame.draw.line(surf, haft, (bx, by), (hx, hy), 3)
    pygame.draw.line(surf, haft_hi, (bx - px, by - py), (hx - px, hy - py), 1)
    for t in (0.18, 0.26, 0.34):
        wx, wy = bx + ux * ln * t, by + uy * ln * t
        pygame.draw.line(surf, haft_hi, (wx + px * 2, wy + py * 2),
                         (wx - px * 2, wy - py * 2), 1)

    # ── Visible KNUCKLED GRIP at the belly: a claw/fist wrapping the butt so the
    # axe is unmistakably HELD. Three knuckle nubs + a dark seam, like the knight
    # grip, in the body/haft tone.
    grip = (bx - 2, by - 1)
    pygame.draw.circle(surf, haft, grip, 4)
    pygame.draw.circle(surf, haft_hi, (grip[0], grip[1] - 1), 3)
    for k in (-2, 0, 2):
        pygame.draw.circle(surf, blade_dk, (grip[0] + k, grip[1] - 2), 1)
    pygame.draw.line(surf, blade_dk, (grip[0] - 3, grip[1] + 1),
                     (grip[0] + 3, grip[1] + 1), 1)
    # Butt cap below the fist so the haft visibly bottoms out.
    pygame.draw.circle(surf, blade_dk, (bx, by + 2), 2)
    pygame.draw.circle(surf, blade_hi, (bx - 1, by + 1), 1)

    # ── COMPACT CRESCENT HEAD socketed at the haft top, breaking the silhouette
    # above the crown. Pronounced upper + lower horns and a thin swept edge =
    # the Dane-axe profile, kept small/light so the pole — not the blade —
    # dominates the read. The head sits to the OUTER (near) side of the haft.
    so = 1.5   # socket offset along the haft so the head straddles the top
    sx, sy = hx + ux * so, hy + uy * so      # socket centre on the haft
    eo = 13    # how far the cutting edge reaches outward from the haft
    horn_up = (sx + px * 4 + ux * 6, sy + py * 4 + uy * 6)
    horn_dn = (sx + px * 4 - ux * 6, sy + py * 4 - uy * 6)
    edge_up = (sx + px * eo + ux * 4, sy + py * eo + uy * 4)
    edge_dn = (sx + px * eo - ux * 4, sy + py * eo - uy * 4)
    edge_mid = (sx + px * (eo + 1), sy + py * (eo + 1))
    # Dark backing crescent first (the bevel/shadow side).
    S._poly(surf, blade_dk, [(sx, sy), horn_up, edge_up, edge_mid, edge_dn, horn_dn])
    # Bright blade face inset toward the socket so the bevel shows as a rim.
    face = [
        (sx + px * 1.5, sy + py * 1.5),
        (horn_up[0] + px * 0.5, horn_up[1] + py * 0.5),
        (edge_up[0] - ux * 1.0, edge_up[1] - uy * 1.0),
        (edge_dn[0] + ux * 1.0, edge_dn[1] + uy * 1.0),
        (horn_dn[0] + px * 0.5, horn_dn[1] + py * 0.5),
    ]
    S._poly(surf, blade, face)
    # Swept cutting edge: a bright honed line along the crescent's outer rim,
    # plus a white glint where the light catches the upper horn.
    pygame.draw.line(surf, blade_hi, edge_up, edge_mid, 1)
    pygame.draw.line(surf, blade_hi, edge_mid, edge_dn, 1)
    pygame.draw.line(surf, white,
                     (edge_up[0] - ux, edge_up[1] - uy),
                     (edge_mid[0] - ux, edge_mid[1] - uy), 1)
    pygame.draw.circle(surf, white, (int(horn_up[0]), int(horn_up[1])), 1)
    # Tip of the haft poking just above the socket (langet/cap detail).
    cap = (hx - ux * 2, hy - uy * 2)
    pygame.draw.circle(surf, P["ring"], (int(cap[0]), int(cap[1])), 1)


build_ironclad = S.make_build(_paint_face, _paint_axe, S.IRONCLAD)
build_bloodaxe = S.make_build(_paint_face, _paint_axe, S.BLOODAXE)
