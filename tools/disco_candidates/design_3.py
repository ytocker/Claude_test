"""DISCO Design 3 — ROLLER GROOVE.

A late-70s roller-rink kid over Pip's natural macaw plumage (red head / blue
wings / yellow beak stay visible — the costume layers on top, no re-plumage).
The athletic primary-color outlier of the disco set, and the ONLY costume in
the roster defined by footwear: fat-wheeled QUAD SKATES carry the read at 40px,
with a terry sweatband + striped ribbed tank stacking the "kitted-out skater"
silhouette above them.

Built on the natural `_build_frame` base so the red brow, blue wing, and yellow
beak read through the terry/stripe accents — the whole gag is a parrot dressed
for the rink, not a recolour.
"""
import math

import pygame

from game.store_skins import _make_skin, HX, HY, CROWN_Y
from game.parrot import _build_frame

# Late-70s rink palette: teal + orange + yellow terry stripes, boot-white,
# and a hot toe-stop/short red so the ground gear pops off the scarlet body.
_TEAL     = (47, 182, 196)
_ORANGE   = (242, 92, 42)
_YELLOW   = (244, 208, 63)
_WHITE    = (245, 245, 245)
_WHITE_D  = (198, 200, 206)     # terry / boot shade so the towelling rounds
_SEAM     = (32, 44, 52)        # dark tonal knit seam — beats a white barcode
_SHORT    = (214, 51, 90)       # satin hot-pants / wheel red family
_WHEEL    = (214, 46, 46)       # bright quad wheel
_WHEEL_K  = (20, 20, 20)        # dark keyline so the wheel reads round at 40px
_WHEEL_G  = (255, 255, 255)     # round rim glint
_SOLE     = (120, 74, 44)       # brown boot sole
_HUB      = (24, 22, 26)        # black axle hub dot
_TOESTOP  = (206, 40, 60)       # beefed red toe-stop — quad silhouette tell
_BLUR     = (150, 150, 158)     # motion-blur streak
_STARGOLD = (255, 200, 0)       # iron-on decal gold
_STARK    = (28, 24, 16)        # decal keyline


def _terry_band(surf, x0, x1, y, h=3):
    """One terrycloth band — white towelling with a shade row under it and the
    signature teal+orange stripe pair riding the TOP edge, the read that says
    'sweatband' rather than a plain white bar."""
    pygame.draw.rect(surf, _WHITE_D, (x0, y + 1, x1 - x0, h))
    pygame.draw.rect(surf, _WHITE, (x0, y, x1 - x0, h))
    # Two thin colour stripes along the top so the band reads as terry trim.
    pygame.draw.line(surf, _TEAL, (x0, y), (x1, y), 1)
    pygame.draw.line(surf, _ORANGE, (x0, y - 1), (x1, y - 1), 1)


def _paint_roller(surf, _a):
    # ── BODY · chunky ribbed TANK TOP ────────────────────────────────────────
    # Three FAT teal/orange/yellow bands (not eight thin ones) with a dark knit
    # seam between — a white barcode competed with the yellow beak and mushed at
    # 40px, so the seam is tonal now. Kept narrow at the top so natural red
    # plumage still shows through the shoulder/armhole.
    for ty, col in ((45, _TEAL), (50, _ORANGE), (55, _YELLOW)):
        pygame.draw.rect(surf, col, (30, ty, 15, 4))
        pygame.draw.line(surf, _SEAM, (30, ty + 4), (45, ty + 4), 1)

    # ── BODY · satin HOT-PANTS ───────────────────────────────────────────────
    # A small bright satin block at the hip below the tank, with a single lit
    # highlight so the "satin" sheen reads. Rounded so it sits like shorts.
    pygame.draw.rect(surf, _SHORT, (24, 60, 16, 6), border_radius=2)
    pygame.draw.line(surf, (238, 120, 156), (26, 61), (36, 61), 1)   # satin sheen

    # ── WING · terry WRISTBAND + star iron-on decal ──────────────────────────
    # Terry cuff at the wing base — same towelling read as the brow band, so the
    # kit feels matched. A solid gold 5-point star iron-on decal sits on the
    # CLEAN blue wing field (clear of the stripe zone) as the personalised patch.
    _terry_band(surf, 30, 38, 52, h=3)
    _star5_solid(surf, 40, 44, 5, _STARGOLD)

    # ── HEAD · terry SWEATBAND across the brow ───────────────────────────────
    # A towelling band lifted up onto the brow/crown (HY-7) with the teal+orange
    # stripe pair on its top edge — sits clear of the eye line, red head crowns
    # above it.
    _terry_band(surf, 38, 58, HY - 7, h=3)

    # ── FEET · QUAD ROLLER SKATES (the signature) ────────────────────────────
    # The hero read, sized up ~35% so the footwear WINS the silhouette: a chunky
    # white boot, brown sole, two fat red quad wheels each ringed with a dark
    # keyline + white rim glint so they read circular at 40px, a beefed red
    # toe-stop, and a fat horizontal motion streak trailing the back wheel — the
    # moving-skate tell no other costume has.
    bx, by = 23, 69
    wy = by + 11
    pygame.draw.line(surf, _BLUR, (bx - 8, wy), (bx + 2, wy), 2)      # motion streak
    pygame.draw.rect(surf, _WHITE_D, (bx, by + 1, 16, 7), border_radius=2)
    pygame.draw.rect(surf, _WHITE, (bx, by, 16, 7), border_radius=2)
    pygame.draw.line(surf, _TEAL, (bx + 2, by + 1), (bx + 13, by + 1), 1)  # lace stripe
    pygame.draw.rect(surf, _SOLE, (bx, by + 7, 16, 2))               # brown sole
    for wx in (bx + 4, bx + 13):                                      # two fat quad wheels
        pygame.draw.circle(surf, _WHEEL, (wx, wy), 4)
        pygame.draw.circle(surf, _WHEEL_K, (wx, wy), 4, 1)           # dark round keyline
        pygame.draw.circle(surf, _WHEEL_G, (wx - 1, wy - 2), 1)      # round rim glint
        pygame.draw.circle(surf, _HUB, (wx, wy), 1)                  # axle hub
    pygame.draw.circle(surf, _TOESTOP, (bx + 16, by + 6), 2)         # beefed red toe-stop


def _star5_solid(surf, cx, cy, r, color):
    """5-point star iron-on decal — solid gold fill with a dark keyline so it
    reads as a stitched patch on the blue wing, not a wireframe."""
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, _STARK, pts, 1)


build = _make_skin(_paint_roller, base_fn=_build_frame)
