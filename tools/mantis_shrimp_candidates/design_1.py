"""MANTIS SHRIMP full redesign — DESIGN 1: PEACOCK PRISM. The technicolor reef
jewel: emerald leopard-spotted carapace, orange-red somite edges, a metallic-blue
tail-fan, split green/magenta stalk eyes, and green→orange raptorial clubs that
punch with the flap. Scratch only."""
import pygame

from tools.mantis_shrimp_candidates._chassis import (
    make_skin, new, aaellipse, strike, recoil, club_targets, arm, round_club,
    orb_eye, stalk, tail_fan, BCX, BCY, HCX, HCY, CROWN_Y,
)

BODY  = (31, 168, 106)          # emerald
BODY_D = (12, 92, 62)           # dark green rim/anchor
BODY_H = (120, 224, 170)
RIM   = (12, 92, 62)
SOM   = (255, 106, 43)          # orange-red somite edge
BLUE  = (30, 159, 190)          # tail-fan blue (desaturated so the eye stays focal)
RED   = (224, 60, 70)           # setae rib
MAG   = (232, 51, 140)          # eye magenta
HI    = (255, 244, 214)
CLUB  = (255, 120, 60)
CLUB_H = (255, 179, 90)         # warm-light knuckle so the punch separates


def build(wing_angle_deg):
    surf = new()
    s = strike(wing_angle_deg)
    rcx, rcy = recoil(s)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy
    sh, rs, re, rf, ne, nf = club_targets(bcx, bcy, hcx, hcy, s)

    # Rear club (behind body).
    arm(surf, rs, re, RIM, BODY_D); arm(surf, re, rf, RIM, BODY_D)
    round_club(surf, rf, 6, rim=RIM, col=(214, 86, 40), hi=CLUB)

    # Blue tail-fan + segmented abdomen behind.
    tail_fan(surf, bcx - 7, bcy + 1, body=BODY, body_d=BODY_D, edge=BLUE, rib=RED)

    # Emerald carapace dome.
    aaellipse(surf, BODY_D, (bcx + 1, bcy + 1), 17, 14)
    aaellipse(surf, BODY, (bcx, bcy), 16, 13)
    aaellipse(surf, BODY_H, (bcx - 3, bcy - 4), 8, 4)
    # Orange-red somite trailing edges (3 bands).
    for off in (-7, 0, 7):
        pygame.draw.line(surf, SOM, (bcx + off, bcy - 11), (bcx + off, bcy + 11), 2)
    # Leopard spots — just TWO, each big enough (dark core + white ring) to
    # survive 40px instead of turning to mud.
    for sx, sy in ((bcx - 6, bcy - 4), (bcx + 6, bcy + 2)):
        pygame.draw.circle(surf, HI, (sx, sy), 3, 1)
        pygame.draw.circle(surf, BODY_D, (sx, sy), 2)
    pygame.draw.ellipse(surf, BODY_D, (bcx - 16, bcy - 13, 32, 26), 1)

    # Head.
    aaellipse(surf, BODY_D, (hcx, hcy + 1), 11, 10)
    aaellipse(surf, BODY, (hcx - 1, hcy), 10, 9)

    # Candy-striped stalk eyes with split green/magenta orbs.
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        base = (hcx + sgn * 2, hcy - 3)
        tip = (tx, hcy - 9 + rcy)
        stalk(surf, base, tip, rim=RIM, col=SOM)
        orb_eye(surf, tip[0], tip[1], 5, core=BODY, rim=RIM, mid=MAG, band=True)

    # Lead club — the haymaker, nudged forward so it breaks the body outline.
    nf = (nf[0] + 2, nf[1])
    arm(surf, sh, ne, RIM, BODY_D); arm(surf, ne, nf, RIM, BODY_D)
    round_club(surf, nf, 8, rim=RIM, col=CLUB, hi=CLUB_H,
               spark=(190, 255, 240) if s > 0.6 else None)
    return surf


build = make_skin(build)
