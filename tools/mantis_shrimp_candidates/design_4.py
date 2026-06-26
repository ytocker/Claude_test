"""MANTIS SHRIMP full redesign — DESIGN 4: CHIBI POW. An adorable big-round-head
pocket shrimp: oversized sparkle goggle-eyes, a tiny tapering body + heart
tail-fan, and little cream mitten-clubs doing an eager pat-pat. Head-heavy
cuteness. Scratch only."""
import pygame

from tools.mantis_shrimp_candidates._chassis import (
    make_skin, new, aaellipse, strike, recoil, club_targets, arm, round_club,
    orb_eye, stalk, tail_fan, BCX, BCY, HCX, HCY, CROWN_Y,
)

CORAL = (255, 158, 181)
CORAL_D = (224, 106, 138)        # saturated rim anchor
CORAL_H = (255, 206, 220)
CREAM = (255, 217, 194)          # mitten cream
TEAL  = (63, 208, 216)           # eye teal
DARK  = (122, 47, 70)            # spot + blush line
RIM   = (180, 70, 100)


def build(wing_angle_deg):
    surf = new()
    s = strike(wing_angle_deg)
    rcx, rcy = recoil(s)
    # Chibi: head dominates, body is a small nub behind-left.
    bcx, bcy = BCX - 4 + rcx, BCY + 4 + rcy
    hcx, hcy = HCX - 2 + rcx, HCY + 2 + rcy

    # Tiny tapering body + heart tail-fan behind.
    aaellipse(surf, CORAL_D, (bcx - 6, bcy + 1), 9, 8)
    aaellipse(surf, CORAL, (bcx - 6, bcy), 8, 7)
    # Little teal heart tail-fan so it reads as a shrimp, not an octopus.
    for dx in (-2, 2):
        pygame.draw.circle(surf, CORAL_D, (bcx - 16 + dx, bcy - 1), 3)
        pygame.draw.circle(surf, CORAL, (bcx - 16 + dx, bcy - 2), 2)
    for dy in (-4, 0, 4):
        pygame.draw.polygon(surf, TEAL,
                            [(bcx - 14, bcy), (bcx - 20, bcy + dy), (bcx - 18, bcy + dy)])

    # Rear mitten (bigger + rim-outlined so the club reads at 40px).
    pat = int(s * 2)
    arm(surf, (bcx + 4, bcy + 3), (bcx + 9, bcy + 5 - pat), RIM, CORAL_D)
    round_club(surf, (bcx + 11, bcy + 4 - pat), 6, rim=RIM, col=CREAM, hi=(255, 240, 224))

    # ── HERO: oversized round head.
    aaellipse(surf, CORAL_D, (hcx + 1, hcy + 1), 14, 13)
    aaellipse(surf, CORAL, (hcx, hcy), 13, 12)
    aaellipse(surf, CORAL_H, (hcx - 4, hcy - 5), 6, 4)
    # Tiny leopard spot + blush.
    pygame.draw.circle(surf, DARK, (hcx + 7, hcy - 4), 2)
    pygame.draw.circle(surf, (255, 150, 170), (hcx - 6, hcy + 5), 2)
    pygame.draw.circle(surf, (255, 150, 170), (hcx + 8, hcy + 5), 2)
    # Tiny happy mouth.
    pygame.draw.arc(surf, DARK, (hcx - 2, hcy + 4, 8, 6), 3.6, 5.8, 2)

    # Oversized sparkle goggle-eyes on short stubby stalks.
    for sgn, tx in ((-1, hcx - 5), (1, hcx + 6)):
        base = (hcx + sgn * 3, hcy - 4)
        tip = (tx, hcy - 9 + rcy)
        stalk(surf, base, tip, rim=RIM, col=CORAL_D, w=3)
        orb_eye(surf, tip[0], tip[1], 6, core=TEAL, rim=RIM, hi=False)
        # Big anime sparkle + small lower catch-light.
        pygame.draw.circle(surf, (255, 255, 255), (tip[0] - 2, tip[1] - 2), 2)
        pygame.draw.circle(surf, (255, 255, 255), (tip[0] + 2, tip[1] + 2), 1)

    # Near mitten — bigger so the "two clubs up front" silhouette survives 40px.
    arm(surf, (hcx + 6, hcy + 6), (hcx + 12, hcy + 1 - pat), RIM, CORAL_D, w=4)
    round_club(surf, (hcx + 15, hcy - 2 - pat), 7, rim=RIM, col=CREAM, hi=(255, 240, 224))
    if s > 0.6:
        pygame.draw.circle(surf, (255, 200, 220), (hcx + 18, hcy - 4), 2, 1)
    return surf


build = make_skin(build)
