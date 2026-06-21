"""HEART PIÑATA — secret flyer skin concept (round 2).

A flying candy-heart piñata that replaces the bird. The whole identity is one
job: a bold two-lobe heart with a pronounced cleft, dressed in horizontal
crepe-fringe bands (the universal piñata cue), that reads "heart" instantly at
40px. There are NO wings and NO live particles — the four flap poses are a
baked SEAM-GLOW SWING down the vertical centre cleft:

    frame 0  thin warm line, faint glow      (sealed)
    frame 1  seam brightens, glow widens
    frame 2  full bright bloom + a single gold sugar-spark above the cleft
    frame 3  glow falls back to a thin warm line

ROUND 2 — kill the "T". Round 1 ran the WHITE top crepe band straight across the
gold seam, so at 40px / grayscale the bright white bar + the vertical seam read
as a medical-cross "T". The fix: the top white band now stops ~4px CLEAR on
either side of centre, so the gold seam runs through an unbroken red/coral field
and the brightest grayscale shape is a single VERTICAL bar — never a "T". The
seam itself is now a pure vertical GOLD WEDGE (widest at the cleft, tapering to
the point) with one hot sugar-white core column dead-centre and NO horizontal
competitor. The flap tell is sold in GLOW (radius + brightness swing + a 1px
lateral peel of the cream rim edges), not in how wide the heart gapes.

This is deliberately a SINGLE vertical split down a symmetric lobed shape (not
a radial crack) so it can't be confused with a cracked egg/shell concept. In
grayscale it survives as a centre-line value bloom — the seam glow is the
brightest pixels on the sprite, dead-centre, as a vertical bar.

Night read: the warm gold seam-glow is the bright anchor; a pale cream rim
keylines the LOBE TOPS so the red doesn't vanish into a dark sky. Day read: the
saturated red/coral fringe holds against a pale sky and the cream rim keylines
the silhouette. The heart is lifted a few px and its point sharpened/narrowed so
the tip clears Pip's parcel knot instead of fusing into one brown blob.

Contract mirrors game/animal_ufo.py: 64x84 SRCALPHA canvas, dominant heart mass
centred at (BCX,BCY)=(32,44); `build(wing_angle_deg)->Surface`; frames driven
from parrot._WING_ANGLES.
"""
import pygame

from game.parrot import _add_outline, _aaellipse  # noqa: F401  (kept for parity)


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # heart mass centre → (32, 44)

# Heart geometry. The lobes sit ABOVE centre and the point hangs just below, so
# the dominant mass + the seam tell stay centred on the 14px collision circle.
# The whole heart is lifted ~3px vs round 1 and the point pulled in/up, so the
# tip clears Pip's parcel knot (composited below by the game) instead of fusing
# into one brown blob on the day frame.
LOBE_RX, LOBE_RY = 13, 11       # each top lobe radius
LOBE_DX = 9                     # half-distance between the two lobe centres
LOBE_CY = BCY - 9               # lobe centres sit above body centre (lifted)
POINT_Y = BCY + 14              # the bottom tip of the heart (raised + sharper)
POINT_TUCK = 3                  # narrow the triangle base → a sharper point


# ── palette (crepe fringe red→coral→white, gold seam, cream rim) ─────────────
FRINGE_RED   = (226, 42, 72)    # #E22A48  bottom fringe bands
FRINGE_CORAL = (242, 96, 122)   # #F2607A  mid fringe bands
FRINGE_WHITE = (255, 255, 255)  # #FFFFFF  top fringe band (keylines at night)
SEAM_GOLD    = (255, 213, 106)  # #FFD56A  sugary seam glow
RIM_CREAM    = (255, 244, 230)  # #FFF4E6  cream rim / fringe keyline
FRINGE_SHADE = (176, 26, 54)    # darker red for the underside of each fringe row
CANDY_PINK   = (255, 168, 192)  # the peeking heart-candy body
CANDY_HOT    = (255, 96, 138)   # candy's own little cleft shadow
SUGAR_WHITE  = (255, 252, 244)  # hottest core of the seam glow / spill highlight


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (50→-40 across the four poses) to a 0..3 seam phase."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Per-phase seam drive: (rim-peel px, glow radius, glow alpha mul, spark 0/1).
# The motion is sold in GLOW, not gape — phase 2 is a clear bright bloom with a
# single gold sugar-spark; phase 0/3 fall back to a thin warm line. The rim-peel
# only laterally offsets the two cream seam edges by ~1px so the seam shimmers.
_SEAM = {
    0: (0.5, 3.0, 0.55, 0.0),
    1: (1.0, 4.6, 0.85, 0.0),
    2: (1.4, 6.4, 1.20, 1.0),
    3: (0.8, 3.6, 0.65, 0.0),
}


def _heart_mask_surface():
    """An opaque heart silhouette (alpha mask) used to clip the fringe bands so
    every band is trimmed exactly to the heart edge. Drawn once per build."""
    m = _new()
    # Two lobes + a triangle to the point = a filled heart. Simple, robust, and
    # crisp at 40px — far more reliable than a single polygon sweep.
    _aaellipse(m, (255, 255, 255), (BCX - LOBE_DX, LOBE_CY), LOBE_RX, LOBE_RY)
    _aaellipse(m, (255, 255, 255), (BCX + LOBE_DX, LOBE_CY), LOBE_RX, LOBE_RY)
    # Narrower triangle base (POINT_TUCK) → the sides converge sooner, giving a
    # sharper tip that doesn't merge with the parcel knot below.
    pygame.draw.polygon(m, (255, 255, 255), [
        (BCX - LOBE_RX - LOBE_DX + 1 + POINT_TUCK, LOBE_CY + 2),
        (BCX + LOBE_RX + LOBE_DX - 1 - POINT_TUCK, LOBE_CY + 2),
        (BCX, POINT_Y),
    ])
    return m


# Half-width of the CLEAR channel kept down the centre of the WHITE top band.
# Round 1's "T" came from a white bar crossing the gold seam. Round 2 keeps a
# WIDE clear channel (no white anywhere near centre) AND only lets the single
# topmost crepe row carry the white — and only out on the OUTER lobe shoulders.
# That puts two small white crests left + right of a coral crown, so the bright
# grayscale mass is the vertical core, flanked by two separated dots, never a
# horizontal bar joining over the seam.
WHITE_CHANNEL = 8


def _fringe_body(top_y, bot_y):
    """Render the horizontal crepe-fringe bands as a full rectangle, then the
    caller clips it to the heart mask. Bands run RED (bottom) → CORAL (mid) →
    WHITE (top), the real piñata stacking order, with a fringed lower lip and a
    1px shade line per row so the layered-paper depth survives shrink-down.

    Only the SINGLE topmost row is white, split into two outer side panels with
    a WIDE clear coral channel down the centre, so no bright horizontal bar ever
    crosses the gold seam — the seam runs through colour, not white, and the two
    white crests sit out on the lobe shoulders as separated dots."""
    band = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    rows = []
    y = bot_y
    step = 4
    # Build band colours from bottom to top across the heart's vertical extent.
    span = bot_y - top_y
    top_t = 0.0
    while y > top_y - step:
        t = (bot_y - y) / max(1, span)        # 0 at bottom, 1 at top
        top_t = max(top_t, t)
        rows.append([y, t])
        y -= step
    for r in rows:
        t = r[1]
        if t < 0.42:
            r.append((FRINGE_RED, False))
        elif t < top_t - 0.001:               # everything but the crown → coral
            r.append((FRINGE_CORAL, False))
        else:                                  # only the single topmost row
            r.append((FRINGE_WHITE, True))

    for (ry, _t, (col, white)) in rows:
        rect = pygame.Rect(0, ry - step, COMPOSITE_W, step + 1)
        if white:
            # coral bed across the whole crown row, white only on the two outer
            # shoulders well clear of the centre channel.
            pygame.draw.rect(band, FRINGE_CORAL, rect)
            lw = BCX - WHITE_CHANNEL
            rw = BCX + WHITE_CHANNEL
            pygame.draw.rect(band, col, pygame.Rect(0, ry - step, lw, step + 1))
            pygame.draw.rect(band, col,
                             pygame.Rect(rw, ry - step, COMPOSITE_W - rw, step + 1))
        else:
            pygame.draw.rect(band, col, rect)
        # 1px darker shade along the band's lower edge → stacked-paper depth.
        shade = FRINGE_SHADE if col is FRINGE_RED else tuple(
            max(0, int(c * 0.82)) for c in col)
        pygame.draw.line(band, shade, (0, ry - 1), (COMPOSITE_W, ry - 1))
        # tiny fringe teeth along the lower edge so the lip reads as cut paper.
        for fx in range(2, COMPOSITE_W, 5):
            pygame.draw.line(band, shade, (fx, ry), (fx, ry + 1))
    return band


def _seam_glow(surf, peel, glow_r, glow_mul, spark_t):
    """The vertical SEAM down the centre cleft, drawn as a pure GOLD WEDGE —
    widest at the cleft, tapering to the point — with one hot sugar-white core
    column dead-centre and NO horizontal competitor. The flap tell is sold in
    GLOW (radius + brightness swing via glow_r/glow_mul) and a 1px lateral peel
    of the two cream rim edges, not in how wide the heart gapes. The whole tell
    lives on the centre line so grayscale shows a clean central VERTICAL bar."""
    seam_top = LOBE_CY - 2
    seam_bot = POINT_Y - 3
    seam_h = seam_bot - seam_top

    # Additive gold WEDGE — widest at the cleft, pinching to the point. Two soft
    # layers so the bloom has a body + a hotter inner gold. Brightness swings
    # with glow_mul so phase 2 reads as a clear bloom and 0/3 as a thin line.
    glow = pygame.Surface((int(glow_r * 2) + 8, seam_h + 8), pygame.SRCALPHA)
    gw = glow.get_width() // 2
    for i in range(seam_h):
        t = i / seam_h
        w = glow_r * (1.0 - 0.62 * t)         # wedge taper toward the point
        for mul, alpha in ((1.0, 60), (0.5, 130)):
            rr = max(1, int(w * mul))
            a = min(255, int(alpha * glow_mul))
            pygame.draw.line(glow, (*SEAM_GOLD, a), (gw - rr, i), (gw + rr, i))
    surf.blit(glow, (BCX - gw, seam_top), special_flags=pygame.BLEND_RGBA_ADD)

    # Two cream rim edges peeled apart by `peel` (~1px) — the lateral shimmer
    # that animates the seam without gaping the heart. They flank the core, not
    # cross it, so nothing reads horizontal.
    pygame.draw.line(surf, RIM_CREAM,
                     (BCX - peel, seam_top + 1),
                     (BCX - peel * 0.4, seam_bot - 2), 1)
    pygame.draw.line(surf, RIM_CREAM,
                     (BCX + peel, seam_top + 1),
                     (BCX + peel * 0.4, seam_bot - 2), 1)

    # ONE hot sugar-white core column dead-centre — the single brightest pixels,
    # a vertical bar. Slightly thicker at the cleft so the wedge reads as gold.
    pygame.draw.line(surf, SUGAR_WHITE, (BCX, seam_top + 2), (BCX, seam_bot - 2), 1)
    pygame.draw.line(surf, SUGAR_WHITE, (BCX, seam_top + 2), (BCX, seam_top + 5), 1)

    # Phase-2 only: a single 2px gold sugar-spark popping just above the cleft —
    # replaces the round-1 candy dab (invisible at 40px). Reads as a flash of
    # escaping sugar at the moment of the bloom.
    if spark_t > 0.0:
        sx, sy = BCX, seam_top - 4
        _aaellipse(surf, SEAM_GOLD, (sx, sy), 2, 2)
        _aaellipse(surf, SUGAR_WHITE, (sx, sy), 1, 1)


def build(wing_angle_deg):
    """One flat 64x84 frame: a crepe-fringe heart piñata with a baked
    vertical seam-split driven by the flap phase. Drawn UPRIGHT — velocity tilt
    is applied later by the getter, so no rotation is baked here."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    peel, glow_r, glow_mul, spark_t = _SEAM[ph]

    mask = _heart_mask_surface()
    top_y = LOBE_CY - LOBE_RY
    bot_y = POINT_Y

    # 1) crepe fringe bands, clipped to the heart silhouette.
    fringe = _fringe_body(top_y, bot_y)
    fringe.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(fringe, (0, 0))

    # 2) cream rim keyline around the whole heart — holds the red against a dark
    # night sky and a pale day sky alike. Built from the mask edge.
    rim = pygame.mask.from_surface(mask, threshold=8)
    edge = rim.to_surface(setcolor=RIM_CREAM, unsetcolor=(0, 0, 0, 0))
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        surf.blit(edge, (dx, dy))
    # restamp the fringe so the rim sits only OUTSIDE, not over the bands.
    surf.blit(fringe, (0, 0))

    # 2b) NIGHT ANCHOR: a thin cream rim arc on each LOBE CROWN. With the white
    # top band now broken at the centre, this keeps the lobes keylined against a
    # dark sky so the silhouette never dissolves. Each arc hugs only the OUTER
    # crown of its lobe (and stops short of the centre seam) so the two arcs read
    # as two separate crests, never a continuous horizontal line over the seam.
    crown = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for cx, (a0, a1) in ((BCX - LOBE_DX, (1.15, 2.7)),
                         (BCX + LOBE_DX, (0.44, 1.99))):
        rect = pygame.Rect(cx - LOBE_RX + 2, LOBE_CY - LOBE_RY + 1,
                           (LOBE_RX - 2) * 2, (LOBE_RY) * 2)
        pygame.draw.arc(crown, RIM_CREAM, rect, a0, a1, 1)
    crown.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(crown, (0, 0))

    # 3) a soft top-lobe sheen so the rounded candy form catches light.
    sheen = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(sheen, (255, 255, 255, 60), (BCX - LOBE_DX - 2, LOBE_CY - 4), 5, 3)
    _aaellipse(sheen, (255, 255, 255, 45), (BCX + LOBE_DX - 2, LOBE_CY - 4), 4, 2)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(sheen, (0, 0))

    # 4) the vertical seam GOLD WEDGE — the signature tell, drawn last so the
    # glow + spark sit on top of the fringe and read as a vertical bar at centre.
    _seam_glow(surf, peel, glow_r, glow_mul, spark_t)

    return surf


# Smoke test when run directly (no display needed under SDL dummy).
if __name__ == "__main__":
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    for a in (50, 20, -10, -40):
        s = build(a)
        print("frame", a, "->", s.get_size())
