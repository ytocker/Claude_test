"""POLAR EXPLORER penguin — design_3 of the penguin store-skin redesign.

The character/charm pick: a penguin bundled for its own habitat, stacking the
most winter gear of any concept. The 40px hero reads are the chunky knitted
bobble-beanie pom-pom above the crown AND a fat striped scarf flaring past
the body outline — two silhouette breaks from two directions, instantly "cozy
adventurer" at thumbnail size.

Built on the same chassis as ``animal_skins.build_penguin``. Scratch-only —
NOT registered in ``animal_skins.BUILDERS``.
"""
import pygame

from game.animal_skins import (
    _make_prebuilt_skin, _new, _aaellipse, _rot_blit, _eye, _flap,
    BCX, BCY, HCX, HCY, CROWN_Y,
)

# ── POLAR EXPLORER palette ────────────────────────────────────────────────────
_EX_BACK   = (30, 34, 51)           # #1E2233 navy head/back
_EX_BACK_D = (18, 20, 34)
_EX_BACK_H = (78, 86, 112)
_EX_BELLY  = (247, 244, 236)        # #F7F4EC white belly/face
_EX_BELLY_D = (212, 210, 202)
_EX_BEAK   = (255, 138, 30)         # #FF8A1E orange beak/feet
_EX_BEAK_D = (198, 96, 16)
_EX_CHEEK  = (255, 158, 150)        # rosy cold-nipped cheek
_EX_RED    = (210, 75, 75)          # #D24B4B scarf/beanie red stripe
_EX_BLUE   = (59, 125, 216)         # #3B7DD8 scarf/beanie blue stripe
_EX_CREAM  = (245, 230, 200)        # #F5E6C8 pom-pom / knit highlight
_EX_GOGGLE = (150, 132, 96)         # smoky amber-grey lens (kept off the scarf blue)
_EX_RUBBER = (60, 48, 36)           # warm brown goggle strap (distinct from cool scarf)
_EX_RIM    = (78, 86, 112)          # #4E5670 cool rim-light for night separation


def _explorer_flipper(angle_deg):
    """Standard penguin flipper with a knit-cuff mitten stripe at the tip."""
    w = pygame.Surface((34, 44), pygame.SRCALPHA)
    pts = [(18, 10), (26, 16), (22, 34), (14, 30)]
    pygame.draw.polygon(w, _EX_BACK_D, pts)
    pygame.draw.polygon(w, _EX_BACK, [(18, 11), (24, 17), (20, 30), (15, 27)])
    pygame.draw.line(w, _EX_BACK_H, (18, 13), (22, 18), 1)
    # Knit mitten cuff at the tip — red then blue band.
    pygame.draw.line(w, _EX_RED,  (15, 30), (22, 32), 2)
    pygame.draw.line(w, _EX_BLUE, (15, 33), (22, 35), 2)
    return pygame.transform.rotate(w, angle_deg * 0.7)


def build_explorer(wing_angle_deg):
    surf = _new()
    f = _flap(wing_angle_deg)

    # Stubby tail.
    pygame.draw.polygon(surf, _EX_BACK_D,
                        [(13, BCY + 8), (6, BCY + 14), (18, BCY + 14)])
    # Egg body (navy back).
    _aaellipse(surf, _EX_BACK_D, (BCX + 1, BCY + 1), 17, 18)
    _aaellipse(surf, _EX_BACK, (BCX, BCY), 16, 17)
    # Cool rim-light on the upper-left back so the navy body keeps a silhouette
    # against the night sky (the lower-back edge otherwise dissolves).
    pygame.draw.arc(surf, _EX_RIM, (BCX - 16, BCY - 16, 22, 26), 1.3, 3.1, 2)
    # White belly oval.
    _aaellipse(surf, _EX_BELLY, (BCX + 1, BCY + 3), 11, 14)
    _aaellipse(surf, _EX_BELLY_D, (BCX + 1, BCY + 9), 9, 6)

    # Far flipper (with mitten cuff).
    _rot_blit(surf, _explorer_flipper(wing_angle_deg * 0.5 - 16), (BCX + 11, BCY))

    # ── Fat striped scarf flaring from the neck ──
    # A chunky red/blue band wrapping the lower head + neck, with a tail that
    # stays a continuous tapering flag from neck → tip (an intermediate point
    # bridges the gap so it never detaches into a floating bar). Sway is clamped
    # so the tip never clears the body edge, and the tail carries a dark outline
    # so it always reads as "scarf in front of body."
    scarf_tail_x = BCX - 11 - int(f * 2)   # clamped flap-driven side-sway
    scarf_tail_y = BCY - 2 + int(f * 2)
    scarf_pts = [
        (HCX - 9, HCY + 9),
        (HCX + 8, HCY + 9),
        (HCX + 7, HCY + 13),
        (BCX - 7, BCY - 3),                 # bridge point — keeps the flag solid
        (scarf_tail_x + 4, scarf_tail_y + 5),
        (scarf_tail_x, scarf_tail_y),
        (BCX - 8, BCY - 6),                 # upper bridge back to the wrap
        (HCX - 6, HCY + 13),
    ]
    # Red base layer + dark outline so it reads in front of the body at any sway.
    pygame.draw.polygon(surf, _EX_RED, scarf_pts)
    pygame.draw.polygon(surf, _EX_BACK_D, scarf_pts, 1)
    # Blue stripe across the middle.
    pygame.draw.line(surf, _EX_BLUE,
                     (HCX - 8, HCY + 11), (HCX + 7, HCY + 11), 3)
    # Cream highlight edge.
    pygame.draw.line(surf, _EX_CREAM,
                     (HCX - 7, HCY + 9), (HCX + 7, HCY + 9), 1)

    # Head dome (navy, no crest — beanie sits on top).
    _aaellipse(surf, _EX_BACK_D, (HCX, HCY + 2), 12, 12)
    _aaellipse(surf, _EX_BACK, (HCX - 1, HCY + 1), 11, 11)
    # White face mask.
    _aaellipse(surf, _EX_BELLY, (HCX, HCY + 3), 8, 8)
    # Rosy cold-nipped cheek.
    pygame.draw.circle(surf, _EX_CHEEK, (HCX - 3, HCY + 4), 3)
    # Eyes.
    _eye(surf, HCX - 2, HCY, 3)
    _eye(surf, HCX + 5, HCY, 3)

    # ── Snow-goggles on the brow ──
    # Two smoky amber-grey lenses with a warm rubber bridge — kept off the cool
    # scarf blue so the two never merge into one band at 40px.
    for gx in (HCX - 3, HCX + 5):
        pygame.draw.circle(surf, _EX_RUBBER, (gx, HCY - 3), 4)
        pygame.draw.circle(surf, _EX_GOGGLE, (gx, HCY - 3), 3)
        pygame.draw.circle(surf, (235, 222, 190), (gx - 1, HCY - 4), 1)  # glint
    pygame.draw.line(surf, _EX_RUBBER, (HCX, HCY - 3), (HCX + 2, HCY - 3), 2)

    # Orange beak (unchanged — rosy cold-nipped read).
    pygame.draw.polygon(surf, _EX_BEAK,
                        [(HCX + 2, HCY + 4), (HCX + 11, HCY + 6),
                         (HCX + 2, HCY + 8)])
    pygame.draw.polygon(surf, _EX_BEAK_D,
                        [(HCX + 2, HCY + 4), (HCX + 11, HCY + 6),
                         (HCX + 2, HCY + 8)], 1)

    # ── HERO: chunky bobble-beanie pushing past the crown ──
    # Brim band, ribbed dome, pom-pom circle above CROWN_Y. Drawn last so it
    # sits on top of the head and goggles. Alternating red/blue knit ridges.
    brim_y = CROWN_Y + 6
    # Brim fold band.
    pygame.draw.ellipse(surf, _EX_RED,
                        (HCX - 9, brim_y, 18, 5))
    pygame.draw.ellipse(surf, _EX_BLUE,
                        (HCX - 9, brim_y + 2, 18, 4))
    # Dome cap.
    _aaellipse(surf, _EX_RED,  (HCX - 1, brim_y - 3), 9, 7)
    _aaellipse(surf, _EX_BLUE, (HCX - 1, brim_y - 5), 8, 5)
    # Knit ridge lines on the dome.
    for dy in (brim_y - 2, brim_y - 5):
        pygame.draw.line(surf, _EX_CREAM, (HCX - 7, dy), (HCX + 5, dy), 1)
    # Cream pom-pom above the crown — bobs 1px with the flap so the head motion
    # ties into the body.
    pom_y = CROWN_Y - 3 - int(f)
    pygame.draw.circle(surf, _EX_CREAM, (HCX - 1, pom_y), 5)
    pygame.draw.circle(surf, (255, 248, 230), (HCX - 2, pom_y - 1), 3)  # sheen

    # Near flipper (with mitten cuff).
    _rot_blit(surf, _explorer_flipper(wing_angle_deg), (BCX - 6, BCY + 1))

    # Orange webbed feet, set a touch wider with a gap so they read as two feet,
    # not one orange paddle, at 40px.
    for fx in (26, 38):
        pygame.draw.polygon(surf, _EX_BEAK,
                            [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 4, BCY + 20), (fx - 4, BCY + 20)])
        pygame.draw.polygon(surf, _EX_BEAK_D,
                            [(fx - 3, BCY + 16), (fx + 3, BCY + 16),
                             (fx + 4, BCY + 20), (fx - 4, BCY + 20)], 1)
    return surf


build = _make_prebuilt_skin(build_explorer)
