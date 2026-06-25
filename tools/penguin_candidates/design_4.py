"""PENGUIN store-skin candidate — DESIGN 4: SCUBA DIVER (snorkel goof).

The aquatic in-joke: a flightless swimmer geared up to swim. Hero read is the
domed cyan dive-mask over the eyes plus a J-curved snorkel hooking up past the
crown — cyan is a colour no other penguin concept uses, so it owns the
silhouette at 40px. Built on the shared penguin chassis (navy-back / white-
belly egg, 4-pose flipper flap) so it lifts straight into game/animal_skins.py.

Scratch exploration only — exposes ``build`` but is intentionally NOT registered
in animal_skins.BUILDERS.
"""
import math
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye, _flap,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# Navy back/head + warm-white belly split — the one penguin constant.
NAVY    = (30, 34, 51)              # #1E2233
NAVY_D  = (20, 23, 38)
NAVY_H  = (74, 82, 110)
BELLY   = (247, 244, 236)          # #F7F4EC
BELLY_D = (210, 212, 218)
CYAN    = (25, 182, 196)           # #19B6C4 lens + fin accents
CYAN_H  = (150, 232, 240)          # bright lens glint
RUBBER  = (34, 42, 51)             # #222A33 mask rim + snorkel tube
BEAK    = (255, 138, 30)           # #FF8A1E beak + feet
BEAK_D  = (200, 96, 18)
BUBBLE  = (207, 246, 251)          # #CFF6FB drifting bubbles


def _dive_fin(angle_deg):
    """Penguin flipper widened into a paddle-like swim-fin: broader trailing
    tip + a cyan leading-edge accent so it reads 'fin' not bare flipper. Same
    angle*0.7 damping as the base flipper so it flaps identically."""
    w = pygame.Surface((36, 44), pygame.SRCALPHA)
    # Wider blade than _pen_flipper — fat paddle bottom.
    blade = [(19, 9), (28, 16), (26, 36), (12, 32), (15, 16)]
    pygame.draw.polygon(w, NAVY_D, blade)
    pygame.draw.polygon(w, NAVY, [(19, 10), (26, 17), (24, 32), (14, 29)])
    # Full-length 2px cyan leading edge so the "swim-fin" tell survives downscale.
    pygame.draw.line(w, CYAN, (19, 11), (25, 34), 2)
    pygame.draw.line(w, CYAN_H, (19, 12), (22, 17), 1)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def build_diver(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)            # 1 = flipper up; drives bubble drift

    # Stubby tail.
    pygame.draw.polygon(surf, NAVY_D,
                        [(13, BCY + 8), (6, BCY + 14), (18, BCY + 14)])
    # Egg body (navy back).
    _aaellipse(surf, NAVY_D, (BCX + 1, BCY + 1), 17, 18)
    _aaellipse(surf, NAVY, (BCX, BCY), 16, 17)
    # Cool rim-light on the upper-left back so the navy body keeps its silhouette
    # against the night sky — without it only the belly + mask float at night.
    pygame.draw.arc(surf, NAVY_H, (BCX - 16, BCY - 16, 22, 26), 1.3, 3.1, 2)
    # White belly oval — the high-contrast split.
    _aaellipse(surf, BELLY, (BCX + 1, BCY + 3), 11, 14)
    _aaellipse(surf, BELLY_D, (BCX + 1, BCY + 9), 9, 6)

    # Far fin behind the body — nudged out so it's not swallowed by the body.
    _rot_blit(surf, _dive_fin(wing_angle_deg * 0.5 - 16), (BCX + 13, BCY))

    # Head merges into body (penguin little-neck).
    _aaellipse(surf, NAVY_D, (HCX, HCY + 2), 12, 12)
    _aaellipse(surf, NAVY, (HCX - 1, HCY + 1), 11, 11)
    # White face mask kept — the belly tone wrapping onto the face.
    _aaellipse(surf, BELLY, (HCX, HCY + 3), 8, 8)

    # ── HERO 2: J-curved snorkel hooking UP past the crown ──
    # Drawn before the mask so the mask rim caps its lower mouthpiece elbow.
    # A thick rubber spine: mouthpiece elbow at the cheek → up the side of the
    # head → over the crown → a short forward hook at the tip.
    snk = [
        (HCX + 8, HCY + 4),                 # mouthpiece elbow at the cheek
        (HCX + 10, HCY - 4),
        (HCX + 9, CROWN_Y - 2),
        (HCX + 5, CROWN_Y - 9),             # rises well past CROWN_Y (=24)
        (HCX - 1, CROWN_Y - 11),            # crests the top
        (HCX - 5, CROWN_Y - 8),             # forward hook tip
    ]
    # Fat rubber tube (5px) with a cyan highlight stripe down its outer edge so
    # it reads as cyan dive-gear at 40px, not a thin black wire.
    pygame.draw.lines(surf, RUBBER, False, snk, 5)
    pygame.draw.lines(surf, CYAN, False, snk, 2)         # cyan gear sheen
    snk_tip = snk[-1]
    # Cyan mouthpiece nub at the elbow.
    pygame.draw.circle(surf, CYAN, (HCX + 8, HCY + 5), 2)

    # ── HERO 1: domed cyan dive-mask over the eye zone ──
    # Dark rubber rim oval, inset pale-cyan lens, eyes MAGNIFIED through it.
    mcx, mcy = HCX + 1, HCY - 1
    _aaellipse(surf, RUBBER, (mcx, mcy), 11, 9)          # rubber rim
    _aaellipse(surf, CYAN, (mcx, mcy), 9, 7)             # glass lens
    # Top-left lens glint — sells the domed glass.
    _aaellipse(surf, CYAN_H, (mcx - 3, mcy - 3), 4, 2)
    # Enlarged happy eyes seen through the lens (bigger than the bare r=3).
    _eye(surf, mcx - 4, mcy, 4, white=(250, 250, 248))
    _eye(surf, mcx + 4, mcy, 4, white=(250, 250, 248))

    # Small orange beak peeking BELOW the mask.
    pygame.draw.polygon(surf, BEAK,
                        [(HCX + 2, HCY + 7), (HCX + 11, HCY + 9),
                         (HCX + 2, HCY + 11)])
    pygame.draw.polygon(surf, BEAK_D,
                        [(HCX + 2, HCY + 7), (HCX + 11, HCY + 9),
                         (HCX + 2, HCY + 11)], 1)

    # ── Bubbles drifting up-and-off the snorkel tip (moving aquatic tell) ──
    # Sizes grow as they rise; a small per-frame drift keyed to the flap so
    # they shimmer with motion. Each gets a tiny white glint.
    drift = int((f - 0.5) * 3)
    # Start at the tip and rise mostly vertically so the column reads as bubbles
    # blown FROM the snorkel, not drifting off into empty sky.
    for i, (dx, dy, r) in enumerate(((-1, -3, 2), (-2, -9, 2), (-3, -16, 3))):
        bx = snk_tip[0] + dx + drift
        by = snk_tip[1] + dy - i
        pygame.draw.circle(surf, BUBBLE, (bx, by), r)
        pygame.draw.circle(surf, CYAN, (bx, by), r, 1)
        pygame.draw.circle(surf, (255, 255, 255), (bx - 1, by - 1), 1)

    # Near fin over the body.
    _rot_blit(surf, _dive_fin(wing_angle_deg), (BCX - 6, BCY + 1))

    # Elongated orange fin-feet — broader + longer than the stubby penguin web.
    for fx in (27, 38):
        pygame.draw.polygon(surf, BEAK,
                            [(fx - 4, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 6, BCY + 21), (fx - 6, BCY + 21)])
        pygame.draw.polygon(surf, BEAK_D,
                            [(fx - 4, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 6, BCY + 21), (fx - 6, BCY + 21)], 1)
        # Cyan fin-ray accents echoing the dive theme.
        for rx in (fx - 2, fx + 1):
            pygame.draw.line(surf, CYAN, (rx, BCY + 17), (rx + 1, BCY + 20), 1)
    return surf


build = _make_prebuilt_skin(build_diver)
