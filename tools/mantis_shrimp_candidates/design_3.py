"""MANTIS SHRIMP full redesign — DESIGN 3: KO GLADIATOR. A riveted steel mecha
brawler whose small plated body is dwarfed by two huge red-and-cream banded
boxing gauntlets — the gauntlets ARE the silhouette. Most theatrical punch
(star-burst + speed lines). Scratch only."""
import math
import pygame

from tools.mantis_shrimp_candidates._chassis import (
    make_skin, new, aaellipse, strike, recoil, club_targets, arm,
    orb_eye, stalk, tail_fan, BCX, BCY, HCX, HCY, CROWN_Y,
)

STEEL = (90, 107, 126)
STEEL_D = (46, 57, 71)          # plate shadow / anchor
STEEL_H = (201, 212, 222)
RED   = (224, 59, 59)           # gauntlet red
RED_D = (150, 34, 34)
CREAM = (244, 227, 194)         # gauntlet knuckle plate
GOLD  = (255, 200, 54)          # collar
AMBER = (255, 196, 70)          # visor orb
RIM   = (32, 40, 50)


def _gauntlet(surf, fist, r):
    """A big banded boxing gauntlet: red ball + cream knuckle plate + rivets."""
    pygame.draw.circle(surf, RIM, fist, r + 1)
    pygame.draw.circle(surf, RED_D, fist, r)
    pygame.draw.circle(surf, RED, (fist[0] - 1, fist[1] - 1), r - 1)
    # Cream knuckle plate (front band).
    pygame.draw.circle(surf, CREAM, (fist[0] + r - 3, fist[1]), max(2, r - 3))
    pygame.draw.circle(surf, RIM, (fist[0] + r - 3, fist[1]), max(2, r - 3), 1)
    pygame.draw.circle(surf, STEEL_H, (fist[0] - 2, fist[1] - 2), 2)  # rivet shine


def build(wing_angle_deg):
    surf = new()
    s = strike(wing_angle_deg)
    rcx, rcy = recoil(s)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy
    sh, rs, re, rf, ne, nf = club_targets(bcx, bcy, hcx, hcy, s)

    # Rear gauntlet (big, behind).
    arm(surf, rs, re, RIM, STEEL_D, w=4); arm(surf, re, rf, RIM, STEEL_D, w=4)
    _gauntlet(surf, rf, 9)

    # Bladed metal tail-fan.
    tail_fan(surf, bcx - 7, bcy + 1, body=STEEL, body_d=STEEL_D, edge=STEEL_H)

    # Plated steel body (smaller — the body is the handle).
    aaellipse(surf, STEEL_D, (bcx + 1, bcy + 1), 15, 12)
    aaellipse(surf, STEEL, (bcx, bcy), 14, 11)
    aaellipse(surf, STEEL_H, (bcx - 3, bcy - 4), 7, 3)
    # Three armour plate seams + rivet dots.
    for off in (-7, 0, 7):
        pygame.draw.line(surf, STEEL_D, (bcx + off, bcy - 10), (bcx + off, bcy + 10), 2)
        pygame.draw.circle(surf, STEEL_H, (bcx + off, bcy - 8), 1)
        pygame.draw.circle(surf, STEEL_H, (bcx + off, bcy + 8), 1)
    # Gold collar plate at the neck.
    pygame.draw.line(surf, GOLD, (bcx + 10, bcy - 8), (bcx + 12, bcy + 6), 3)
    pygame.draw.ellipse(surf, STEEL_D, (bcx - 14, bcy - 11, 28, 22), 1)

    # Head + armoured visor eyes.
    aaellipse(surf, STEEL_D, (hcx, hcy + 1), 10, 9)
    aaellipse(surf, STEEL, (hcx - 1, hcy), 9, 8)
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        tip = (tx, hcy - 8 + rcy)
        arm(surf, (hcx + sgn * 2, hcy - 3), tip, RIM, STEEL_D, w=3)
        orb_eye(surf, tip[0], tip[1], 4, core=AMBER, rim=RIM)

    # Speed lines + star-burst on the punch (behind the lead gauntlet).
    if s > 0.6:
        for ang in (-0.5, 0.0, 0.5):
            ex = nf[0] - int(math.cos(ang) * 16)
            ey = nf[1] - int(math.sin(ang) * 16)
            pygame.draw.line(surf, STEEL_H, (ex, ey), (nf[0] - 6, nf[1]), 1)

    # Lead gauntlet — the giant haymaker, the silhouette.
    arm(surf, sh, ne, RIM, STEEL_D, w=4); arm(surf, ne, nf, RIM, STEEL_D, w=4)
    _gauntlet(surf, nf, 11)
    if s > 0.7:
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            pygame.draw.line(surf, (255, 255, 255),
                             (nf[0] + int(math.cos(a) * 11), nf[1] + int(math.sin(a) * 11)),
                             (nf[0] + int(math.cos(a) * 15), nf[1] + int(math.sin(a) * 15)), 1)
    return surf


build = make_skin(build)
