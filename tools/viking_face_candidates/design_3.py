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
    # A near-black separator that holds in BOTH palettes — used as a one-px
    # outline tick so the dark mustache/beard never melts into the same-family
    # body brown (IRONCLAD's failure mode was a value-less brown stack).
    kl = P["keyline"][:3]

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
    # A near-black UNDER-stroke runs beneath each cord first so the mustache wins
    # one clean value step against the body brown (the IRONCLAD legibility fix).
    mcx, mcy = HX + 6, HY + 8          # under the beak base
    # Outer (right) cord sweeps out past the beak then curls down and inboard to
    # the chin bind at (HX+3, mcy+11).
    rm = [(mcx + 10, mcy - 3), (mcx + 12, mcy + 1), (mcx + 8, mcy + 6),
          (HX + 3, mcy + 9)]
    pygame.draw.lines(surf, kl, False, [(x, y + 1) for x, y in rm], 4)   # outline tick
    pygame.draw.lines(surf, beard, False, rm, 3)
    pygame.draw.lines(surf, beard_hi, False, [(x, y - 1) for x, y in rm[:3]], 1)  # lit plait
    pygame.draw.circle(surf, beard, (mcx + 12, mcy + 1), 2)   # curled lit tip
    # Inner (left) cord under the cheek, also drawing down to the chin bind.
    lm = [(mcx - 8, mcy - 1), (mcx - 9, mcy + 3), (mcx - 4, mcy + 7),
          (HX + 3, mcy + 9)]
    pygame.draw.lines(surf, kl, False, [(x, y + 1) for x, y in lm], 4)
    pygame.draw.lines(surf, beard, False, lm, 3)
    pygame.draw.lines(surf, beard_hi, False, [(x, y - 1) for x, y in lm[:3]], 1)
    pygame.draw.circle(surf, beard, (mcx - 9, mcy + 3), 2)
    # Plait ticks across each mustache wing so they read woven, not smeared.
    for cx, cy in ((mcx + 8, mcy + 1), (mcx - 6, mcy + 2)):
        pygame.draw.line(surf, beard_hi, (cx - 2, cy - 1), (cx + 2, cy + 1), 1)

    # ── Chin bind where the two mustache cords gather before the single braid
    # drops — the gather-KNOT where mustache becomes beard. One slightly larger
    # ring with a lit rim, ringed in near-black so it reads as a hard bound knot
    # (not a smudge) and so mustache and beard visibly meet at a single point.
    jx, jy = HX + 3, mcy + 11
    pygame.draw.circle(surf, kl, (jx, jy), 4)            # hard knot outline
    pygame.draw.circle(surf, ring, (jx, jy), 3)
    pygame.draw.circle(surf, P["bone"], (jx, jy), 2)
    pygame.draw.circle(surf, P["helm_hi"], (jx - 1, jy - 1), 1)   # lit rim

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
    haft_hi = P["haft_hi"]
    white = P["white"]
    # The haft must read DARKER than the beaded braid in BOTH palettes — the
    # IRONCLAD mush came from haft + braid beads being the same gold. We force a
    # dedicated dark wood core off the keyline so the pole is always the darkest
    # vertical strand and the braid stays the lighter beaded one.
    kl = P["keyline"][:3]
    haft_core = tuple((a + b) // 2 for a, b in zip(P["haft"], kl))  # darkened wood

    # The Dane-axe is held near-VERTICAL down the body's NEAR (right) side so it
    # never crosses the centred rope-braid: butt LOW at the belly, head UP past
    # the crown. A faint sway with the wing beat sells "carried", not a mast.
    sway = int(round(wing_angle * 0.06))

    # Anchor points: knuckled grip low at the belly, head high above the crown.
    # The head is socketed higher than before so its crescent clears the helm
    # horns with open sky between horn-tip and blade.
    bx, by = 62, 59                   # butt of the haft at the belly, right side
    hx, hy = 64 + sway, CROWN_Y - 18  # haft top, lifted to break the sky cleanly
    ux, uy = hx - bx, hy - by
    ln = max(1.0, (ux * ux + uy * uy) ** 0.5)
    ux, uy = ux / ln, uy / ln
    px, py = -uy, ux                  # perpendicular, for thickness/blade offset

    # ── Long thin HAFT (the Dane-axe tell). A DARK wood core with a single lit
    # edge stripe so it reads as a turned pole that is unmistakably darker than
    # the beaded braid; a few binding wraps near the grip.
    pygame.draw.line(surf, kl, (bx, by), (hx, hy), 4)            # near-black underline
    pygame.draw.line(surf, haft_core, (bx, by), (hx, hy), 3)     # dark wood core
    pygame.draw.line(surf, haft_hi, (bx - px, by - py), (hx - px, hy - py), 1)  # lit edge
    for t in (0.18, 0.26, 0.34):
        wx, wy = bx + ux * ln * t, by + uy * ln * t
        pygame.draw.line(surf, haft_hi, (wx + px * 2, wy + py * 2),
                         (wx - px * 2, wy - py * 2), 1)

    # ── Visible KNUCKLED GRIP at the belly: a claw/fist wrapping the butt so the
    # axe is unmistakably HELD. A dark wrap SEAM where the claw meets the haft
    # (value darker than both body and haft) plus three knuckle nubs reads as
    # fingers closing over the pole.
    grip = (bx - 2, by - 1)
    pygame.draw.circle(surf, kl, grip, 5)                       # dark seam ring
    pygame.draw.circle(surf, haft_core, grip, 4)
    pygame.draw.circle(surf, haft_hi, (grip[0], grip[1] - 1), 3)
    pygame.draw.line(surf, kl, (grip[0] - 4, grip[1] + 1),
                     (grip[0] + 4, grip[1] + 1), 1)             # wrap seam across the haft
    for k in (-2, 1, 4):                                        # knuckle hint over the haft
        pygame.draw.circle(surf, kl, (grip[0] + k, grip[1] - 3), 1)
        pygame.draw.circle(surf, haft_hi, (grip[0] + k, grip[1] - 4), 1)
    # Butt cap below the fist so the haft visibly bottoms out.
    pygame.draw.circle(surf, kl, (bx, by + 2), 2)
    pygame.draw.circle(surf, haft_hi, (bx - 1, by + 1), 1)

    # ── DANE-AXE BLADE socketed at the haft top and pulled clearly to the OUTER
    # (near) side so the crescent breaks the SKY, not the helm. Enlarged ~35% over
    # the old compact head and rebuilt around ONE hard CONVEX cutting edge: a deep
    # belly that bows outward from a short toe and a long heel, honed by a bright
    # rim line so the silhouette reads as a blade, not a second horn.
    so = 1.0   # socket sits just below the haft top
    sx, sy = hx + ux * so, hy + uy * so      # socket centre on the haft
    eo = 17    # outward reach of the cutting belly (≈35% longer than before)
    toe = (sx + px * (eo - 4) + ux * 9, sy + py * (eo - 4) + uy * 9)   # upper point
    heel = (sx + px * (eo - 5) - ux * 8, sy + py * (eo - 5) - uy * 8)  # lower point
    belly = (sx + px * eo, sy + py * eo)                              # deepest bow
    socket_up = (sx + ux * 5, sy + uy * 5)
    socket_dn = (sx - ux * 4, sy - uy * 4)
    # Dark backing crescent (the bevel/shadow side of the blade).
    S._poly(surf, blade_dk,
            [socket_up, toe, belly, heel, socket_dn])
    # Bright blade face inset toward the socket so the dark bevel shows as a rim.
    face = [
        (socket_up[0] + px * 1.5, socket_up[1] + py * 1.5),
        (toe[0] - ux * 1.0, toe[1] - uy * 1.0),
        (belly[0] - px * 2.0, belly[1] - py * 2.0),
        (heel[0] + ux * 1.0, heel[1] + uy * 1.0),
        (socket_dn[0] + px * 1.5, socket_dn[1] + py * 1.5),
    ]
    S._poly(surf, blade, face)
    # ONE hard honed cutting edge: a bright convex rim sweeping toe→belly→heel,
    # doubled with a white inner glint at the belly where the light catches the
    # bevel — the unmistakable "sharp axe" read.
    pygame.draw.line(surf, blade_hi, toe, belly, 2)
    pygame.draw.line(surf, blade_hi, belly, heel, 2)
    pygame.draw.line(surf, white,
                     (toe[0] - ux, toe[1] - uy), (belly[0] - ux, belly[1] - uy), 1)
    pygame.draw.circle(surf, white, (int(belly[0] - px), int(belly[1] - py)), 1)
    # Near-black keyline along the socket so the blade detaches from the haft.
    pygame.draw.line(surf, kl, socket_up, socket_dn, 1)
    # Tip of the haft poking just above the socket (langet/cap detail).
    cap = (hx - ux * 2, hy - uy * 2)
    pygame.draw.circle(surf, P["ring"], (int(cap[0]), int(cap[1])), 1)


build_ironclad = S.make_build(_paint_face, _paint_axe, S.IRONCLAD)
build_bloodaxe = S.make_build(_paint_face, _paint_axe, S.BLOODAXE)
