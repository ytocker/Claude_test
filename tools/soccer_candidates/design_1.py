"""DESIGN 1 — THE STRIKER (Soccer / Football), v6.

Scratch exploration only — NOT registered in store_skins.BUILDERS, so production
is untouched. Pip the scarlet macaw kitted as a modern outfield striker.

v6 goal (R2): make the collar read as a real crew-neck NECKHOLE and free the
squad number from the sash. The critical fix is that the ring's open centre now
shows the parrot's SCARLET neck, not jersey blue — so it reads as an opening in
the shirt rather than a white token floating on the chest:
  * the collar rect is raised to straddle the jersey top edge (HY+8), half over
    the scarlet neck above it, half over the jersey below — and the neck patch
    inside the ring is repainted scarlet BEFORE the white ring, so the hollow
    centre is body-coloured;
  * the squad "9" is dropped clear below the collar and left of the sash, with a
    band of plain jersey blue isolating it from both — built as a ring top plus a
    descender so it reads as a digit at 40px;
  * knee-high socks carry a solid white hoop band BELOW the jersey hem and a boot
    ellipse at the foot, kept cooler/darker than the shirt so leg and jersey
    never merge;
  * white sleeve hems (3px) where the wings exit the fabric.
Kept from R1: royal-blue jersey polygon, 2px navy garment outline, two-zone
back/chest shading, and the gold diagonal sash on the RIGHT half only.
"""

import pygame
from game.store_skins import HX, HY, CROWN_Y, _poly, _make_skin

# Body-centre anchor in COMPOSITE space — the kit hangs off the torso, not the
# head, so it gets its own reference point below the beak/crown head anchors.
BCX, BCY = 32, 52

# ── kit palette ───────────────────────────────────────────────────────────────
# Two-zone jersey: the back (behind the body centre) sits in shadow so the lit
# chest panel reads as the front of a worn shirt rather than a flat fill.
_STR_BACK  = (25,  70, 180)   # dark blue — back zone (x < BCX)
_STR_CHEST = (40,  95, 210)   # lighter blue — chest zone (x > BCX)
_STR_OUT   = (10,  30,  92)   # dark navy garment outline
_STR_HI    = (60, 100, 220)   # highlight / front seam
_COLLAR_W  = (235, 240, 250)  # white collar ring (outer stroke)
_NECK_RED  = (200,  40,  40)  # scarlet neck showing through the crew-neck hole
_SLEEVE    = (220, 220, 240)  # white sleeve trim
_GOLD      = (240, 190,  30)  # diagonal sash
_GOLD_SH   = (200, 160,  20)  # sash shadow edge
_NUM_W     = (245, 248, 255)  # squad number "9"
_SOCK_N    = (18,  40, 130)   # dark-navy knee-high sock
_SOCK_SH   = (12,  28,  98)   # sock shadow side
_SOCK_H    = (225, 228, 240)  # white sock hoop band
_BOOT_D    = (24,  22,  30)   # dark boot
_BOOT_H    = (200, 205, 215)  # boot sole / stripe glint

# Full-body jersey silhouette in COMPOSITE space (shared by fill + outline so
# the garment boundary always matches the fabric it traces). Top stays at HY+8 —
# nothing climbs onto the forehead.
_JERSEY = [
    (BCX - 10, HY + 8),   # left shoulder  (22, 49)
    (BCX - 13, HY + 17),  # left hip       (19, 58)
    (BCX - 8,  HY + 23),  # left hem       (24, 64)
    (HX + 8,   HY + 23),  # right hem      (55, 64)
    (HX + 11,  HY + 18),  # right hip      (58, 59)
    (HX + 9,   HY + 8),   # right shoulder (56, 49)
]


def _paint(surf, _a):
    # 1 — SOCKS + BOOTS below the jersey hem (HY+23), drawn first so the kit
    # layers cleanly over their tops. Two knee-high strips (left + right), each a
    # navy column with a shadow side; a solid white hoop band at HY+25 (below the
    # hem so it clears the blue), then a boot ellipse at HY+28. Kept darker/cooler
    # than the jersey so leg and shirt never merge into one blue mass at 40px.
    for x0 in (HX - 12, HX + 2):
        pygame.draw.rect(surf, _SOCK_SH, (x0, HY + 23, 6, 7))      # shadow base
        pygame.draw.rect(surf, _SOCK_N, (x0, HY + 23, 5, 7))       # navy column
        pygame.draw.line(surf, _SOCK_H, (x0, HY + 25), (x0 + 5, HY + 25), 2)  # hoop
        pygame.draw.ellipse(surf, _BOOT_D, (x0 - 2, HY + 28, 10, 4))  # boot
        pygame.draw.line(surf, _BOOT_H, (x0 - 1, HY + 30), (x0 + 6, HY + 30), 1)

    # 2 — JERSEY body, two-zone. Back fills the whole silhouette dark; the chest
    # panel overlays the front half lighter, faking a lit front face.
    _poly(surf, _STR_BACK, _JERSEY)
    chest = [
        (BCX, HY + 8), (BCX, HY + 23), (HX + 8, HY + 23),
        (HX + 11, HY + 18), (HX + 9, HY + 8),
    ]
    _poly(surf, _STR_CHEST, chest)

    # 3 — GOLD diagonal sash across the chest, kept to the RIGHT half so its
    # bottom never crosses the left-of-centre "9". Top pulled DOWN to HY+11 so it
    # never overlaps the collar zone above it.
    pygame.draw.line(surf, _GOLD, (HX + 8, HY + 11), (HX + 1, HY + 22), 3)
    pygame.draw.line(surf, _GOLD_SH, (HX + 9, HY + 12), (HX + 2, HY + 22), 1)

    # 4 — SQUAD NUMBER "9" dropped clear BELOW the collar and LEFT of the sash,
    # with plain jersey blue isolating it from both. A ring top (7×5 hollow) plus
    # a descender stroke reads as a digit rather than a smear at 40px.
    nx, ny = HX - 8, HY + 16
    pygame.draw.ellipse(surf, _NUM_W, (nx, ny, 7, 5), 1)   # ring top of the 9
    pygame.draw.rect(surf, _NUM_W, (nx + 5, ny + 3, 2, 6))  # descender stroke

    # 5 — garment outline tracing the full jersey perimeter.
    pygame.draw.polygon(surf, _STR_OUT, _JERSEY, 2)

    # 6 — front-panel centre seam.
    pygame.draw.line(surf, _STR_HI, (HX - 1, HY + 12), (HX, HY + 21), 1)

    # 7 — white sleeve hems where the wings exit the fabric, at 3px so the cuffs
    # survive the downscale.
    pygame.draw.line(surf, _SLEEVE, (BCX - 10, HY + 12), (BCX - 3, HY + 12), 3)
    pygame.draw.line(surf, _SLEEVE, (HX + 4, HY + 12), (HX + 11, HY + 12), 3)

    # 8 — crew-neck COLLAR ring, drawn last. Raised so its centre sits at ~y=46
    # (HY+5) and the ring STRADDLES the jersey top edge (HY+8): half over the
    # scarlet neck above, half over the jersey below. The inside of the ring is
    # repainted SCARLET first so the hollow centre is body-coloured — that is the
    # neckhole read that sells the shirt as worn, instead of a white token on blue.
    collar_rect = pygame.Rect(HX - 8, HY + 2, 16, 9)
    pygame.draw.ellipse(surf, _NECK_RED, collar_rect.inflate(-6, -4))
    pygame.draw.ellipse(surf, _COLLAR_W, collar_rect, 2)


build = _make_skin(_paint)
