"""MANTIS SHRIMP full redesign — DESIGN 5: EMBER FORGE. A charcoal cracked-rock
torpedo seamed with glowing lava veins, smouldering ember eyes, and white-hot
anvil-head clubs that flash + spark on the punch. The warm showpiece. Scratch
only."""
import math
import pygame

from tools.mantis_shrimp_candidates._chassis import (
    make_skin, new, aaellipse, strike, recoil, club_targets, arm, hammer_club,
    orb_eye, stalk, tail_fan, glow_dot, shade, BCX, BCY, HCX, HCY, CROWN_Y,
)

ROCK  = (42, 35, 32)            # charcoal
ROCK_D = (18, 13, 11)           # deep crack-shadow / anchor
ROCK_H = (78, 66, 60)
LAVA  = (255, 90, 30)           # lava orange
LAVA_Y = (255, 194, 51)         # lava yellow
HOT   = (255, 240, 192)         # white-hot core
RUST  = (122, 42, 18)
RIM   = (18, 13, 11)


def _vein(surf, pts, pulse):
    pygame.draw.lines(surf, shade(LAVA, pulse), False, pts, 2)
    pygame.draw.lines(surf, shade(LAVA_Y, pulse), False, pts, 1)


def build(wing_angle_deg):
    surf = new()
    s = strike(wing_angle_deg)
    pulse = 0.8 + 0.4 * s
    rcx, rcy = recoil(s)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy
    sh, rs, re, rf, ne, nf = club_targets(bcx, bcy, hcx, hcy, s)

    # Rear anvil club (behind), dark with a hot face.
    arm(surf, rs, re, RIM, ROCK_D, w=4); arm(surf, re, rf, RIM, ROCK_D, w=4)
    hammer_club(surf, rf, rs, 6, rim=RIM, col=ROCK, hi=ROCK_H, face=LAVA_Y)

    # Dark tail-fan with glowing orange rib edges.
    tail_fan(surf, bcx - 7, bcy + 1, body=ROCK, body_d=ROCK_D, edge=ROCK_H, rib=LAVA)

    # Charcoal carapace with a warm lit top-rim so the silhouette reads on bright
    # day sky without depending on the glow.
    aaellipse(surf, ROCK_D, (bcx + 1, bcy + 1), 17, 14)
    aaellipse(surf, ROCK, (bcx, bcy), 16, 13)
    aaellipse(surf, ROCK_H, (bcx - 3, bcy - 4), 7, 3)
    pygame.draw.arc(surf, (122, 74, 48), (bcx - 16, bcy - 14, 32, 24), 0.5, 2.7, 2)
    # ONE bold horizontal lava crack per segment (branching veins read as noise
    # at 40px); they pulse brighter with the strike.
    _vein(surf, [(bcx - 12, bcy - 5), (bcx - 4, bcy - 4)], pulse)
    _vein(surf, [(bcx - 6, bcy + 4), (bcx + 3, bcy + 5)], pulse)
    _vein(surf, [(bcx + 2, bcy - 3), (bcx + 10, bcy - 2)], pulse)
    pygame.draw.ellipse(surf, ROCK_D, (bcx - 16, bcy - 13, 32, 26), 1)

    # Head.
    aaellipse(surf, ROCK_D, (hcx, hcy + 1), 11, 10)
    aaellipse(surf, ROCK, (hcx - 1, hcy), 10, 9)

    # Smouldering ember eyes on basalt stalks.
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        base = (hcx + sgn * 2, hcy - 3)
        tip = (tx, hcy - 9 + rcy)
        stalk(surf, base, tip, rim=RIM, col=ROCK_D)
        glow_dot(surf, tip[0], tip[1], 3, LAVA)
        orb_eye(surf, tip[0], tip[1], 5, core=LAVA, rim=RIM, hi=False)
        pygame.draw.circle(surf, LAVA_Y, (tip[0], tip[1]), 2)
        pygame.draw.circle(surf, HOT, (tip[0], tip[1]), 1)

    # Lead anvil — pushed forward to break the body outline; white-hot face on
    # the punch + rising ember sparks.
    nf = (nf[0] + 2, nf[1])
    arm(surf, sh, ne, RIM, ROCK_D, w=4); arm(surf, ne, nf, RIM, ROCK_D, w=4)
    glow_dot(surf, nf[0], nf[1], int(3 + s * 3), LAVA)
    face = HOT if s > 0.6 else LAVA_Y
    hammer_club(surf, nf, sh, 8, rim=RIM, col=ROCK, hi=ROCK_H, face=face)
    if s > 0.6:
        for dx, dy in ((3, -7), (6, -4), (1, -10)):
            pygame.draw.circle(surf, LAVA_Y, (nf[0] + dx, nf[1] + dy), 1)
    return surf


build = make_skin(build)
