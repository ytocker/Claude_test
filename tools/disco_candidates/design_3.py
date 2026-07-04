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
import pygame

from game.store_skins import _make_skin, HX, HY, CROWN_Y
from game.parrot import _build_frame

# Late-70s rink palette: teal + orange + yellow terry stripes, boot-white,
# and a hot toe-stop/short red so the ground gear pops off the scarlet body.
_TEAL     = (47, 182, 196)
_ORANGE   = (242, 92, 42)
_YELLOW   = (244, 208, 63)
_WHITE    = (245, 245, 245)
_WHITE_D  = (198, 200, 206)     # terry shade so the towelling rounds
_SHORT    = (214, 51, 90)       # satin hot-pants / wheel red family
_WHEEL    = (210, 50, 50)       # bright quad wheel
_WHEEL_H  = (240, 120, 110)     # wheel rim glint (reads round at 40px)
_SOLE     = (120, 74, 44)       # brown boot sole
_HUB      = (24, 22, 26)        # black axle hub dot
_BLUR     = (150, 150, 158)     # 1px motion-blur streak
_STARGOLD = (255, 220, 0)       # iron-on decal


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
    # ── BODY · striped ribbed TANK TOP ───────────────────────────────────────
    # Alternating 2px teal/orange/yellow ribbed bands across the chest. Drawn
    # first so the sweatband/wristband/skates layer cleanly over the top and
    # bottom, and kept inside the body footprint so nothing balloons the
    # silhouette. Natural red plumage still shows at the armhole/shoulder edges.
    tank_cols = (_TEAL, _ORANGE, _YELLOW)
    for i, ty in enumerate(range(42, 58, 2)):
        pygame.draw.rect(surf, tank_cols[i % 3], (28, ty, 18, 2))
    # A darker rib seam every other band so the ribbing reads as knit, not paint.
    for ty in range(43, 58, 4):
        pygame.draw.line(surf, _WHITE_D, (28, ty), (46, ty), 1)

    # ── BODY · satin HOT-PANTS ───────────────────────────────────────────────
    # A small bright satin block at the hip below the tank, with a single lit
    # highlight so the "satin" sheen reads. Rounded so it sits like shorts.
    pygame.draw.rect(surf, _SHORT, (24, 58, 16, 6), border_radius=2)
    pygame.draw.line(surf, (238, 120, 156), (26, 59), (36, 59), 1)   # satin sheen

    # ── WING · terry WRISTBAND + star iron-on decal ──────────────────────────
    # Terry cuff at the wing base — same towelling read as the brow band, so the
    # kit feels matched. A tiny gold 5-point star iron-on decal sits at the wing
    # centre as the personalised patch.
    _terry_band(surf, 30, 38, 50, h=3)
    _star5_outline(surf, 41, 47, 3, _STARGOLD)

    # ── HEAD · terry SWEATBAND across the brow ───────────────────────────────
    # A towelling band over the brow with the teal+orange stripe pair on its
    # top edge. Sits just under the crown so the red head still crowns above it.
    _terry_band(surf, 38, 58, HY - 5, h=3)

    # ── FEET · QUAD ROLLER SKATES (the signature) ────────────────────────────
    # The hero read: a white boot, a thin brown sole, and two bright red quad
    # wheels each with a black axle hub. A 1px grey streak trails the back wheel
    # so the skate reads as MOVING — the tell no other costume has.
    boot_x, boot_y = 24, 70
    pygame.draw.line(surf, _BLUR, (boot_x - 5, 77), (boot_x, 77), 1)  # motion streak
    pygame.draw.rect(surf, _WHITE_D, (boot_x, boot_y + 1, 12, 5), border_radius=1)
    pygame.draw.rect(surf, _WHITE, (boot_x, boot_y, 12, 5), border_radius=1)
    pygame.draw.line(surf, _TEAL, (boot_x + 1, boot_y + 1), (boot_x + 10, boot_y + 1), 1)
    pygame.draw.rect(surf, _SOLE, (boot_x, boot_y + 5, 12, 2))       # brown sole
    for wx in (boot_x + 3, boot_x + 9):                               # two quad wheels
        pygame.draw.circle(surf, _WHEEL, (wx, boot_y + 8), 3)
        pygame.draw.circle(surf, _WHEEL_H, (wx - 1, boot_y + 7), 1)
        pygame.draw.circle(surf, _HUB, (wx, boot_y + 8), 1)
    pygame.draw.circle(surf, _SHORT, (boot_x + 11, boot_y + 4), 1)    # red toe-stop


def _star5_outline(surf, cx, cy, r, color):
    """5-point star OUTLINE — the iron-on decal on the wing. Outline (not filled)
    so the blue plumage shows through the star's centre like a real patch."""
    import math
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    pygame.draw.polygon(surf, color, pts, 1)


build = _make_skin(_paint_roller, base_fn=_build_frame)
