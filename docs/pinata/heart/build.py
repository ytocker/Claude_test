"""HEART PIÑATA — secret flyer skin concept (round 1).

A flying candy-heart piñata that replaces the bird. The whole identity is one
job: a bold two-lobe heart with a pronounced cleft, dressed in horizontal
crepe-fringe bands (the universal piñata cue), that reads "heart" instantly at
40px. There are NO wings and NO live particles — the four flap poses are a
baked SEAM-SPLIT & SPILL down the vertical centre cleft:

    frame 0  hairline seam, faint inner glow      (sealed)
    frame 1  seam parts, gold sugar-glow widens
    frame 2  seam at full gape, one heart-candy peeks out  (the spill)
    frame 3  seam reseals to a thin warm line       (back toward sealed)

This is deliberately a SINGLE vertical split down a symmetric lobed shape (not
a radial crack) so it can't be confused with a cracked egg/shell concept. In
grayscale it survives as a centre-line value bloom — the seam glow is the
brightest pixels on the sprite, dead-centre.

Night read: the warm gold seam-glow is the bright anchor; a pale cream
crepe-fringe keyline rims the top lobes so the red doesn't vanish into a dark
sky. Day read: the saturated red/coral fringe holds against a pale sky and the
cream rim keylines the silhouette.

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
LOBE_RX, LOBE_RY = 13, 11       # each top lobe radius
LOBE_DX = 9                     # half-distance between the two lobe centres
LOBE_CY = BCY - 6               # lobe centres sit above body centre
POINT_Y = BCY + 19              # the bottom tip of the heart


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


# Per-phase seam drive: (half-gape px, glow radius, candy-peek 0..1).
# Phase 2 is the full spill; 0 is sealed; 3 reseals on the way back.
_SEAM = {
    0: (0.6, 3.0, 0.0),
    1: (1.8, 4.6, 0.0),
    2: (3.0, 6.2, 1.0),
    3: (1.2, 3.8, 0.0),
}


def _heart_mask_surface():
    """An opaque heart silhouette (alpha mask) used to clip the fringe bands so
    every band is trimmed exactly to the heart edge. Drawn once per build."""
    m = _new()
    # Two lobes + a triangle to the point = a filled heart. Simple, robust, and
    # crisp at 40px — far more reliable than a single polygon sweep.
    _aaellipse(m, (255, 255, 255), (BCX - LOBE_DX, LOBE_CY), LOBE_RX, LOBE_RY)
    _aaellipse(m, (255, 255, 255), (BCX + LOBE_DX, LOBE_CY), LOBE_RX, LOBE_RY)
    pygame.draw.polygon(m, (255, 255, 255), [
        (BCX - LOBE_RX - LOBE_DX + 1, LOBE_CY + 2),
        (BCX + LOBE_RX + LOBE_DX - 1, LOBE_CY + 2),
        (BCX, POINT_Y),
    ])
    return m


def _fringe_body(top_y, bot_y):
    """Render the horizontal crepe-fringe bands as a full rectangle, then the
    caller clips it to the heart mask. Bands run RED (bottom) → CORAL (mid) →
    WHITE (top), the real piñata stacking order, with a fringed lower lip and a
    1px shade line per row so the layered-paper depth survives shrink-down."""
    band = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    rows = []
    y = bot_y
    step = 4
    # Build band colours from bottom to top across the heart's vertical extent.
    span = bot_y - top_y
    while y > top_y - step:
        t = (bot_y - y) / max(1, span)        # 0 at bottom, 1 at top
        if t < 0.42:
            col = FRINGE_RED
        elif t < 0.74:
            col = FRINGE_CORAL
        else:
            col = FRINGE_WHITE
        rows.append((y, col))
        y -= step

    for (ry, col) in rows:
        # solid band
        pygame.draw.rect(band, col, pygame.Rect(0, ry - step, COMPOSITE_W, step + 1))
        # 1px darker shade along the band's lower edge → stacked-paper depth.
        shade = FRINGE_SHADE if col is FRINGE_RED else tuple(
            max(0, int(c * 0.82)) for c in col)
        pygame.draw.line(band, shade, (0, ry - 1), (COMPOSITE_W, ry - 1))
        # tiny fringe teeth along the lower edge so the lip reads as cut paper.
        for fx in range(2, COMPOSITE_W, 5):
            pygame.draw.line(band, shade, (fx, ry), (fx, ry + 1))
    return band


def _seam_glow(surf, half_gape, glow_r, candy_t):
    """The vertical SEAM-SPLIT & SPILL down the centre cleft. An additive gold
    sugar-glow column blooms inside the split (brightest at night), capped by a
    hot sugar core, with one heart-candy peeking out at full spill (phase 2).
    The glow lives on the centre line so grayscale shows a clean central value
    bloom — the signature tell."""
    seam_top = LOBE_CY - 2
    seam_bot = POINT_Y - 4
    seam_h = seam_bot - seam_top

    # Additive glow column — soft wide bloom, narrowing toward the point.
    glow = pygame.Surface((int(glow_r * 2) + 8, seam_h + 8), pygame.SRCALPHA)
    gw = glow.get_width() // 2
    for i in range(seam_h):
        t = i / seam_h
        # taper: widest at the cleft, pinching to the point
        w = glow_r * (1.0 - 0.55 * t)
        for layer, (mul, alpha) in enumerate(((1.0, 70), (0.55, 120))):
            rr = max(1, int(w * mul))
            pygame.draw.line(glow, (*SEAM_GOLD, alpha),
                             (gw - rr, i), (gw + rr, i))
    surf.blit(glow, (BCX - gw, seam_top), special_flags=pygame.BLEND_RGBA_ADD)

    # The split itself: two cream rim edges peeled apart by `half_gape`, with a
    # hot sugar-white inner line — this is what makes the crack read as a SEAM.
    if half_gape > 0.7:
        pygame.draw.line(surf, RIM_CREAM,
                         (BCX - half_gape, seam_top + 1),
                         (BCX - half_gape * 0.4, seam_bot), 1)
        pygame.draw.line(surf, RIM_CREAM,
                         (BCX + half_gape, seam_top + 1),
                         (BCX + half_gape * 0.4, seam_bot), 1)
    # hot sugar core down the dead centre
    core_w = max(1, int(half_gape * 0.7))
    pygame.draw.line(surf, SUGAR_WHITE, (BCX, seam_top + 1), (BCX, seam_bot - 2),
                     core_w)

    # The candy peek: a tiny heart-candy emerging from the cleft at full spill.
    if candy_t > 0.0:
        cy = seam_top + 5
        r = int(3 * candy_t)
        if r >= 2:
            _aaellipse(surf, CANDY_PINK, (BCX - 2, cy), r, r)
            _aaellipse(surf, CANDY_PINK, (BCX + 2, cy), r, r)
            pygame.draw.polygon(surf, CANDY_PINK, [
                (BCX - r - 1, cy + 1), (BCX + r + 1, cy + 1), (BCX, cy + r + 3)])
            pygame.draw.line(surf, CANDY_HOT, (BCX, cy - 1), (BCX, cy + 1))
            _aaellipse(surf, SUGAR_WHITE, (BCX - 2, cy - 1), 1, 1)


def build(wing_angle_deg):
    """One flat 64x84 frame: a crepe-fringe heart piñata with a baked
    vertical seam-split driven by the flap phase. Drawn UPRIGHT — velocity tilt
    is applied later by the getter, so no rotation is baked here."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    half_gape, glow_r, candy_t = _SEAM[ph]

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

    # 3) a soft top-lobe sheen so the rounded candy form catches light.
    sheen = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    _aaellipse(sheen, (255, 255, 255, 60), (BCX - LOBE_DX - 2, LOBE_CY - 4), 5, 3)
    _aaellipse(sheen, (255, 255, 255, 45), (BCX + LOBE_DX - 2, LOBE_CY - 4), 4, 2)
    sheen.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(sheen, (0, 0))

    # 4) the vertical seam-split & spill — the signature tell, drawn last so the
    # glow + candy sit on top of the fringe and read at the centre line.
    _seam_glow(surf, half_gape, glow_r, candy_t)

    return surf


# Smoke test when run directly (no display needed under SDL dummy).
if __name__ == "__main__":
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    for a in (50, 20, -10, -40):
        s = build(a)
        print("frame", a, "->", s.get_size())
