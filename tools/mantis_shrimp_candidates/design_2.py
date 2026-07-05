"""MANTIS SHRIMP full redesign — DESIGN 2: ABYSS GLOWER. A near-black deep-sea
body defined by cyan bioluminescent seam-glow + glowing eye-orbs, with clubs
whose tips burn molten orange-white on the punch — a dark shape wearing light.
Scratch only."""
import pygame

from tools.mantis_shrimp_candidates._chassis import (
    make_skin, new, aaellipse, strike, recoil, club_targets, arm, round_club,
    orb_eye, stalk, tail_fan, glow_dot, shade, BCX, BCY, HCX, HCY, CROWN_Y,
)

BODY  = (28, 58, 94)            # deep blue (a real value anchor for day sky)
BODY_D = (10, 22, 40)
BODY_R = (70, 120, 168)         # lit top-edge rim
SEG   = (19, 49, 78)            # segment shade
CYAN  = (35, 224, 255)          # bioluminescent glow
CYAN_C = (155, 246, 255)        # glow core
HOT   = (255, 138, 30)          # hot club-tip
HOT_C = (255, 231, 176)
RIM   = (8, 16, 30)


def build(wing_angle_deg):
    surf = new()
    s = strike(wing_angle_deg)
    rcx, rcy = recoil(s)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy
    sh, rs, re, rf, ne, nf = club_targets(bcx, bcy, hcx, hcy, s)

    # Rear club — dark with a glowing knuckle tip.
    arm(surf, rs, re, RIM, SEG); arm(surf, re, rf, RIM, SEG)
    glow_dot(surf, rf[0], rf[1], 3, HOT)
    round_club(surf, rf, 6, rim=RIM, col=(40, 26, 18), hi=HOT)

    # Dark tail-fan with cyan rib-glow.
    tail_fan(surf, bcx - 7, bcy + 1, body=BODY, body_d=BODY_D, edge=SEG, rib=CYAN)

    # Deep-blue carapace with a lit top-edge rim so the silhouette reads on
    # bright day sky (not only by glow).
    aaellipse(surf, BODY_D, (bcx + 1, bcy + 1), 17, 14)
    aaellipse(surf, BODY, (bcx, bcy), 16, 13)
    pygame.draw.arc(surf, BODY_R, (bcx - 16, bcy - 14, 32, 24), 0.5, 2.7, 2)
    # Electric-cyan seam lines tracing the segment joints (glow pulses with strike).
    seam = shade(CYAN, 0.7 + 0.3 * s)
    for off in (-9, -3, 3, 9):
        pygame.draw.line(surf, seam, (bcx + off, bcy - 11), (bcx + off, bcy + 11), 1)
    # A row of photophore glow dots down the side.
    for dx in (-8, -3, 2, 7):
        pygame.draw.circle(surf, CYAN_C, (bcx + dx, bcy + 8), 1)
    pygame.draw.ellipse(surf, BODY_D, (bcx - 16, bcy - 13, 32, 26), 1)

    # Head.
    aaellipse(surf, BODY_D, (hcx, hcy + 1), 11, 10)
    aaellipse(surf, BODY, (hcx - 1, hcy), 10, 9)

    # Glowing cyan eye-orbs on short dark stalks.
    for sgn, tx in ((-1, hcx - 4), (1, hcx + 5)):
        base = (hcx + sgn * 2, hcy - 3)
        tip = (tx, hcy - 9 + rcy)
        stalk(surf, base, tip, rim=RIM, col=SEG)
        orb_eye(surf, tip[0], tip[1], 6, core=CYAN, rim=RIM, glow=CYAN)
        pygame.draw.circle(surf, CYAN_C, (tip[0], tip[1]), 2)

    # Lead club — a SOLID painted hot core (reads at 1× without glow) that flares
    # white-hot on the punch, plus the night glow.
    nf = (nf[0] + 2, nf[1])
    arm(surf, sh, ne, RIM, SEG); arm(surf, ne, nf, RIM, SEG)
    glow_dot(surf, nf[0], nf[1], int(3 + s * 3), HOT)
    round_club(surf, nf, 8, rim=RIM, col=HOT, hi=HOT_C if s > 0.6 else (255, 170, 70),
               spark=HOT_C)
    return surf


build = make_skin(build)
