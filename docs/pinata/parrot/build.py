"""LOTERÍA PARROT PIÑATA secret flyer skin — "El Perico" concept build.

The Lotería card-deck parrot rebuilt as a crepe-paper piñata: a fat
round-bellied perched bird whose two tells are an oversized HOOKED-DOWN beak
and a long down-sweeping crepe-fringe TAIL. It must read as a "parrot piñata"
at 40px and stay distinct from Skybit's existing toucan (a long FLAT beak) and
flamingo (long LEGS + neck): El Perico has a short hooked beak, a round body,
a big swinging tail, and NO long legs or neck.

The 4-frame tell is TAIL-FRINGE WAG + HEAD BOB (no wings, no particles): the
long crepe tail sweeps side to side like a horizontal pendulum — the LARGEST
moving silhouette element — while the head gives a small counter-bob. It
survives grayscale because it is a big pale-edged tail blade swinging across a
fixed round body, a value+position change rather than a hue trick.

Contract mirrors game/animal_ufo.py so a winner lifts straight in:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame,
    body mass centred at (BCX,BCY)=(32,44); drawn UPRIGHT (no baked rotation —
    velocity tilt is applied later by the cached getter).
  * driven by `game.parrot._WING_ANGLES = (50,20,-10,-40)` → tail sweep + bob.
"""
import math
import pygame

from game.parrot import _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # round body centre → (32, 44)

BODY_RX, BODY_RY = 16, 17       # fat round-bellied perched-bird mass
HEAD_RX, HEAD_RY = 11, 10       # chunky head, set high-right on the body
TAIL_PIVOT_X = 32               # the tail hangs from the lower body and swings
TAIL_PIVOT_Y = 56               # pivot just below the body so the blade sweeps
TAIL_LEN = 22                   # long down-sweeping crepe tail (the moving line)
TAIL_HALF = 9                   # half-width of the tail blade — kept BOLD/WIDE


# ── palette ──────────────────────────────────────────────────────────────────
# Lotería festival colours: green body, red head, yellow+blue wing-band stripe,
# cream beak. A cream crepe-fringe keyline rims the body + tail so the saturated
# party colours survive the night sky; the yellow/red bands and cream beak are
# the high-value anchors that carry the read in the dark.
BODY_GREEN   = ( 52, 178,  74)   # #34B24A green body
BODY_GREEN_D = ( 32, 126,  52)   # shaded lower body
BODY_GREEN_H = ( 96, 214, 116)   # upper-body sheen
HEAD_RED     = (226,  58,  46)   # #E23A2E red head
HEAD_RED_D   = (170,  36,  30)   # shaded head underside
HEAD_RED_H   = (255, 118, 104)   # crown highlight

BAND_YELLOW  = (244, 193,  46)   # #F4C12E yellow wing-band stripe
BAND_BLUE    = ( 46, 111, 214)   # #2E6FD6 blue wing-band stripe
BEAK_CREAM   = (247, 233, 200)   # #F7E9C8 cream beak
BEAK_CREAM_D = (206, 184, 138)   # shaded beak underside

FRINGE       = (255, 246, 222)   # cream crepe fringe rim / night keyline
FRINGE_DK    = (212, 192, 152)   # fringe shade so the rim has its own form
TAIL_GREEN   = ( 40, 150,  62)   # tail body (slightly deeper than the belly)
TAIL_GREEN_D = ( 26, 104,  44)   # tail shade
EYE_DARK     = ( 28,  20,  24)   # eye pip
EYE_WHITE    = (255, 255, 255)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 wag-stage index. _WING_ANGLES runs 50→-40,
    so stage advances 0→3 across the four poses, driving the tail pendulum."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Tail sweep angle (deg from straight-down, +right) per stage — a horizontal
# pendulum: right → centre → left → centre, so the long tail blade is visibly
# the largest moving silhouette element across the loop.
_TAIL_SWEEP_BY_STAGE = (26.0, 4.0, -26.0, 4.0)

# Head bob (px, +down) per stage — a small counter-bob opposite the tail so the
# whole body reads as "alive" without spreading a wing. Kept subtle so the head
# colour-block stays put and the red-head/green-body read never breaks.
_HEAD_BOB_BY_STAGE = (-1.0, 0.0, -1.0, 1.0)


def _tail(surf, sweep_deg):
    """The long down-sweeping crepe-fringe tail — the signature moving line.
    A BOLD wide blade pivoting from just below the body, swinging side to side.
    Drawn as a stacked wedge with three crepe-fringe ribs and a fully
    fringe-keylined edge so it stays a fat pale-edged blade (never a thin
    needle that mushes) at 40px on both day and night skies."""
    a = math.radians(90 + sweep_deg)     # 90° = straight down; sweep tilts it
    cx, cy = TAIL_PIVOT_X, TAIL_PIVOT_Y
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx                     # perpendicular = blade half-width axis

    # blade quad: a wide root at the pivot tapering to a slightly narrower,
    # fringe-scalloped tip far below — long and bold, the largest moving shape.
    root_hw, tip_hw = TAIL_HALF, TAIL_HALF - 2
    tip_x = cx + dx * TAIL_LEN
    tip_y = cy + dy * TAIL_LEN
    rl = (cx + px * root_hw, cy + py * root_hw)
    rr = (cx - px * root_hw, cy - py * root_hw)
    tl = (tip_x + px * tip_hw, tip_y + py * tip_hw)
    tr = (tip_x - px * tip_hw, tip_y - py * tip_hw)

    # shaded back half then the lit tail colour, so the blade has form
    pygame.draw.polygon(surf, TAIL_GREEN_D, [rl, tl, tr, rr])
    lit = [rl, tl, ((tl[0] + tr[0]) / 2, (tl[1] + tr[1]) / 2),
           ((rl[0] + rr[0]) / 2, (rl[1] + rr[1]) / 2)]
    pygame.draw.polygon(surf, TAIL_GREEN, lit)

    # alternating yellow/blue crepe ribs banded across the blade so the tail
    # carries the Lotería stripe even when swinging (and reads in grayscale as
    # a rhythmic light/dark ladder down the blade)
    for i in range(1, 4):
        t = i / 4.0
        mx = cx + dx * TAIL_LEN * t
        my = cy + dy * TAIL_LEN * t
        hw = root_hw + (tip_hw - root_hw) * t
        c = BAND_YELLOW if i % 2 == 1 else BAND_BLUE
        pygame.draw.line(surf, c, (mx + px * hw, my + py * hw),
                         (mx - px * hw, my - py * hw), 2)

    # cream crepe-fringe keyline around the whole blade — the night-survival rim
    pygame.draw.polygon(surf, FRINGE, [rl, tl, tr, rr], 2)
    # fringe-scalloped tip pom so the tail never tapers to an invisible point
    for k in (-1, 0, 1):
        fx = tip_x + px * (k * 3)
        fy = tip_y + py * (k * 3)
        pygame.draw.circle(surf, FRINGE, (int(fx), int(fy)), 2)
        pygame.draw.circle(surf, FRINGE_DK, (int(fx), int(fy)), 2, 1)


def _body(surf, cx, cy):
    """The fat round-bellied body — the dominant central green mass with a
    yellow+blue Lotería wing-band stripe wrapped across the flank and a cream
    crepe-fringe rim keyline so the green survives the night sky."""
    _aaellipse(surf, BODY_GREEN_D, (cx, cy + 2), BODY_RX, BODY_RY)       # shadow
    _aaellipse(surf, BODY_GREEN, (cx, cy), BODY_RX, BODY_RY)             # body
    _aaellipse(surf, BODY_GREEN_H, (cx - 4, cy - 6), BODY_RX - 7, BODY_RY - 9)

    # Lotería wing-band stripe: a folded yellow→blue chevron across the flank,
    # the card-deck parrot's banded wing read without spreading an actual wing.
    band_y = cy + 1
    pygame.draw.line(surf, BAND_YELLOW, (cx - BODY_RX + 3, band_y - 3),
                     (cx + BODY_RX - 5, band_y - 1), 3)
    pygame.draw.line(surf, BAND_BLUE, (cx - BODY_RX + 3, band_y + 2),
                     (cx + BODY_RX - 5, band_y + 4), 3)
    # a couple of crepe seam ticks above the band so the body reads as layered
    # crepe paper, not a flat ball
    for tx in range(cx - BODY_RX + 5, cx + BODY_RX - 4, 5):
        pygame.draw.line(surf, FRINGE_DK, (tx, cy - 9), (tx, cy - 6), 1)

    # cream crepe-fringe rim keyline around the whole body (night survival)
    pygame.draw.ellipse(surf, FRINGE,
                        pygame.Rect(cx - BODY_RX, cy - BODY_RY,
                                    BODY_RX * 2, BODY_RY * 2), 2)


def _head_and_beak(surf, cx, cy, bob):
    """The chunky RED head set high-right on the body with the oversized
    HOOKED-DOWN beak — the two reads (red head colour-block + hooked beak) that
    separate El Perico from the long-flat-beaked toucan. The head sits high so
    its red block stays clear of the parcel and the green body below it."""
    hx, hy = cx + 6, cy - 12 + int(bob)     # head high-right on the body

    _aaellipse(surf, HEAD_RED_D, (hx, hy + 1), HEAD_RX, HEAD_RY)   # head shadow
    _aaellipse(surf, HEAD_RED, (hx, hy), HEAD_RX, HEAD_RY)         # red head
    _aaellipse(surf, HEAD_RED_H, (hx - 2, hy - 5), HEAD_RX - 5, 3) # crown sheen
    # cream rim keyline so the red head survives the night sky as its own block
    pygame.draw.ellipse(surf, FRINGE,
                        pygame.Rect(hx - HEAD_RX, hy - HEAD_RY,
                                    HEAD_RX * 2, HEAD_RY * 2), 1)

    # eye — a dark pip with a glint, set forward so it reads as a face at 40px
    ex, ey = hx + 3, hy - 1
    pygame.draw.circle(surf, FRINGE, (ex, ey), 3)
    pygame.draw.circle(surf, EYE_DARK, (ex + 1, ey), 2)
    pygame.draw.circle(surf, EYE_WHITE, (ex, ey - 1), 1)

    # ── oversized HOOKED-DOWN beak (the headline tell) ──
    # An upper mandible that juts forward then HOOKS sharply down past a short
    # lower mandible — a fat parrot hook, never a long flat toucan blade. Kept
    # cream (the night high-value anchor) with a darker hook tip.
    bx = hx + HEAD_RX - 2                 # beak root at the front of the head
    by = hy + 1
    upper = [
        (bx, by - 4),                     # top of the cere where it meets head
        (bx + 11, by - 2),                # juts forward
        (bx + 11, by + 6),                # then hooks sharply DOWN
        (bx + 7, by + 8),                 # the curved hook tip
        (bx + 5, by + 3),
        (bx, by + 2),
    ]
    pygame.draw.polygon(surf, BEAK_CREAM, upper)
    pygame.draw.polygon(surf, BEAK_CREAM_D, upper, 1)
    # short lower mandible tucked under the hook
    lower = [(bx, by + 3), (bx + 6, by + 4), (bx + 5, by + 8), (bx, by + 6)]
    pygame.draw.polygon(surf, BEAK_CREAM_D, lower)
    # gloss on the upper mandible + the dark hook-tip notch so the hook reads
    pygame.draw.line(surf, FRINGE, (bx + 1, by - 2), (bx + 9, by - 1), 1)
    pygame.draw.circle(surf, HEAD_RED_D, (bx + 7, by + 7), 1)
    # a dark cere nostril where the beak meets the face
    pygame.draw.circle(surf, HEAD_RED_D, (bx + 1, by - 2), 1)


def _perch_feet(surf, cx, cy):
    """Two short stubby perch-claws tucked under the belly. Deliberately SHORT
    — El Perico is a perched piñata-bird with NO long legs (the flamingo's
    tell), so the feet are tiny cream nubs that don't add a vertical line."""
    for fx in (cx - 5, cx + 4):
        pygame.draw.line(surf, BEAK_CREAM_D, (fx, cy + BODY_RY - 4),
                         (fx, cy + BODY_RY), 2)
        pygame.draw.circle(surf, BEAK_CREAM, (fx, cy + BODY_RY), 2)
        pygame.draw.circle(surf, BEAK_CREAM_D, (fx, cy + BODY_RY), 2, 1)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    sweep = _TAIL_SWEEP_BY_STAGE[ph]
    bob = _HEAD_BOB_BY_STAGE[ph]
    cx, cy = BCX, BCY

    # 1) Tail FIRST (behind/below) so the round body overlaps its root and the
    #    silhouette reads as one chunky bird with a long swinging tail, not a
    #    detached blade. It is the largest moving element across the loop.
    _tail(surf, sweep)

    # 2) Short perch-claws behind the belly so the body sits over their roots.
    _perch_feet(surf, cx, cy)

    # 3) Fat round green body — the dominant central mass.
    _body(surf, cx, cy)

    # 4) Red head + oversized hooked beak high-right, with the small head bob.
    _head_and_beak(surf, cx, cy, bob)

    return surf
