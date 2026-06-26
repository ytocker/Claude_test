"""DESIGN 1 — THE STRIKER (Soccer / Football), v3.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw kitted as a modern outfield striker.

v3 fix — the headline change is a FULL-BODY jersey. v2's shirt only covered the
right chest (x=33..58), leaving the left half of the body bare scarlet, so the
costume read as a bib, not a kit. The body spans x=13..51 in composite space;
the new jersey polygon wraps x=20..58 (~36px wide) so the whole visible torso is
clothed. Two overlapping blue zones (darker back + lighter right chest) plus a
1px seam fold make the cloth read as draped 3D fabric instead of a flat slab on
both day and night sky. Gold diagonal sash + a white block "9" carry the team
read; knee-high navy socks with white hoops, dark cleats, and a grey shorts hem
finish the kit below. NO headgear / headband — the crown stays open (striker).
"""
import pygame

from game import store_skins
from game.store_skins import HX, HY, CROWN_Y, _poly

# Body centre in composite space (parrot body centre (32,32) + PARROT_DY).
BCX, BCY = 32, 52

# Full-body royal-blue kit. Cool blue is maximally separated from Pip's scarlet
# plumage in both hue and value, so the wrapped shirt reads as cloth, not bird.
# Two blue values (back shadow + lit chest) round the fabric; gold sash + white
# numeral carry the team read; navy socks + grey shorts + dark cleats finish it.
# Back zone is raised to a true medium blue so the left/back of the kit stays
# visible against the night sky (16,18,30) — the old (21,30,130) sank into it.
_JKT_BACK  = (40, 70, 180)    # back / shadow zone (medium blue, night-safe)
_JKT_CHEST = (34, 85, 216)    # chest / lit zone (lighter)
_JKT_FOLD  = (27, 79, 200)    # seam fold between the two zones
_JKT_SASH  = (255, 205, 60)   # gold diagonal sash
_JKT_NUM   = (244, 244, 248)  # white squad number
_JKT_RIM   = (150, 170, 235)  # light rim on the left/top silhouette edge
_JKT_SH    = (16, 22, 96)     # dark navy jersey outline (right edge, vs sky)
_SOCK_NAVY = (15, 26, 120)    # navy sock pillar
_SOCK_HOOP = (244, 244, 248)  # white sock hoop band
_BOOT_D    = (26, 24, 32)     # dark cleat
_BOOT_SOLE = (200, 200, 210)  # sole highlight
_SHORTS    = (170, 175, 190)  # grey shorts (lighter — reads vs socks/boots)


def _paint(surf, _a):
    # ── 1 · KNEE-HIGH SOCKS first (back of the stack) — two navy pillars, one per
    #    foot, with a bare-body gap between them so the legs never bridge into a
    #    single bar. Each sock carries a bright white hoop band near the top so the
    #    classic kit stripe survives the 40px downscale on night sky.
    #    Socks widened to 6px and the white hoop pulled to 3px at HY+16 so the two
    #    legs + boots don't fuse into one navy blob at the 40px downscale.
    for fx in (HX - 9, HX + 1):
        pygame.draw.line(surf, _SOCK_NAVY, (fx, HY + 13), (fx, HY + 25), 6)
        pygame.draw.line(surf, _SOCK_HOOP, (fx - 1, HY + 16), (fx + 2, HY + 16), 3)

    # ── 2 · BOOTS (cleats) at the sock hem — a compact dark ellipse with a bright
    #    full-width sole stripe + two stud ticks beneath so the foot reads as a
    #    studded boot distinct from the navy sock above it.
    for fx in (HX - 9, HX + 1):
        pygame.draw.ellipse(surf, _BOOT_D, (fx - 4, HY + 23, 9, 5))
        pygame.draw.line(surf, _BOOT_SOLE, (fx - 4, HY + 26), (fx + 4, HY + 26), 1)
        for tx in (fx - 2, fx + 2):
            pygame.draw.line(surf, _BOOT_D, (tx, HY + 27), (tx, HY + 28), 2)

    # ── 3 · GREY SHORTS band just below the jersey hem so a clear shorts zone shows
    #    between shirt and socks (the kit reads as shirt + shorts + socks, not one
    #    long tunic). A 5px lighter-grey band fills HY+22..27 so it doesn't murk into
    #    the boots; a darker lower line gives the hem a shadow edge.
    pygame.draw.rect(surf, _SHORTS, (BCX - 8, HY + 22, (HX + 8) - (BCX - 8), 5))
    pygame.draw.line(surf, (100, 104, 116), (BCX - 8, HY + 27), (HX + 8, HY + 27), 1)

    # ── 4 · FULL-BODY JERSEY — the headline. The polygon wraps the WHOLE visible
    #    torso (left edge at BCX-10=22, right edge at HX+11=58, ~36px wide), so the
    #    left half is no longer bare scarlet. Painted as TWO overlapping zones: the
    #    whole shirt in the darker back blue, then the right-chest in the lighter
    #    lit blue, so the cloth reads as draped 3D fabric. A 1px seam fold down the
    #    body centre is the fabric crease; a 1px navy outline crisps the silhouette.
    jersey = [
        (BCX - 10, HY + 7),   # left shoulder  (22, 48)
        (BCX - 12, HY + 17),  # left hip       (20, 58)
        (BCX - 8,  HY + 23),  # left hem       (24, 64)
        (HX + 8,   HY + 23),  # right hem      (55, 64)
        (HX + 11,  HY + 18),  # right hip      (58, 59)
        (HX + 9,   HY + 8),   # right shoulder (56, 49)
    ]
    chest_zone = [
        (BCX,      HY + 7),   # seam top
        (BCX,      HY + 23),  # seam hem
        (HX + 8,   HY + 23),  # right hem
        (HX + 11,  HY + 18),  # right hip
        (HX + 9,   HY + 8),   # right shoulder
    ]
    _poly(surf, _JKT_BACK, jersey)          # whole jersey, darker zone
    _poly(surf, _JKT_CHEST, chest_zone)     # right chest, lit zone
    pygame.draw.line(surf, _JKT_FOLD, (BCX, HY + 7), (BCX, HY + 23), 1)  # seam fold
    pygame.draw.polygon(surf, _JKT_SH, jersey, 1)                         # outline
    # The left/top silhouette sits against the bird's dark body, not sky, so a dark
    # outline there is invisible — a LIGHT rim line lifts that edge off Pip on night.
    pygame.draw.lines(surf, _JKT_RIM, False,
                      [(BCX - 10, HY + 7), (BCX - 12, HY + 17), (BCX - 8, HY + 23)], 2)

    # ── 5 · GOLD DIAGONAL SASH across the right chest — the team mark. A 3px gold
    #    band over the lit zone with a 1px lighter highlight along its upper edge so
    #    it holds as a bright diagonal on both day and night.
    pygame.draw.line(surf, _JKT_SASH, (HX + 2, HY + 9), (HX - 6, HY + 19), 3)
    pygame.draw.line(surf, (255, 230, 100), (HX + 1, HY + 9), (HX - 5, HY + 18), 1)

    # ── 6 · SQUAD NUMBER "9" — a white block numeral on the chest, big enough to
    #    stay legible after the downscale. Rendered once via the system font and
    #    blitted centred on the lit zone.
    font = pygame.font.SysFont("arial", 10, bold=True)
    glyph = font.render("9", True, _JKT_NUM)
    surf.blit(glyph, glyph.get_rect(center=(HX + 1, HY + 16)))


build = store_skins._make_skin(_paint)
