"""HAND TRUCK / SACK BARROW — secret flyer skin concept (round 1).

A flying two-wheel hand truck (dolly) replaces Pip. The universal read is a
tall narrow **L** — a long vertical handle-frame leaning back, a short toe-
plate at the floor, two wheels at the elbow, and a stack of kraft boxes
strapped to the frame. It is industrial, leaning, angular: the ONLY tall
leaning L-frame in the cart set, so it can never be mistaken for a basket.

There are NO wings and NO live particles. The "flap" is reinterpreted as two
combined big-value motions baked into the 4 frames:
  * the strapped boxes SHIFT/SETTLE 1-2px (as if bouncing on the toe plate),
  * the single front-visible wheel runs a 4-phase spoke cycle (+ → × → + → ×).
Both survive grayscale (a value flip / position shift, not a hue change).

The 40px trap for an L-frame is that the long arm can read as a thin stick
that vanishes. So the load-bearing read is a SOLID dark-steel BAR (not wire)
plus a BOLD warm box stack riding centre, with an #EDF1F4 highlight keyline
down the leading frame edge that doubles as the night silhouette read.

Contract mirrors game/animal_ufo.py so the winner lifts straight into a
production module:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame;
    dominant frame+box mass centred at (BCX, BCY) = (32, 44).
  * 4 box-settle + wheel-spin frames driven by `_WING_ANGLES = (50, 20, -10, -40)`.
  * drawn UPRIGHT with a MODEST ~15° back-lean baked in (NOT a per-frame
    rotation) — kept modest so the engine's velocity tilt still reads as a
    dive, not a fight with the baked lean.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # dominant frame+box mass centre → (32, 44)

# Modest back-lean baked into the whole rig. ~15° keeps the dolly "tipped back
# mid-roll" without fighting the velocity tilt the getter applies later — a
# tilt-down still reads as a dive. The lean is applied as a horizontal SHEAR
# about the body centre (top edges shift back-left, base shifts forward), so
# the rig leans without a costly per-frame rotation.
LEAN_DEG = 15
_LEAN_K = math.tan(math.radians(LEAN_DEG))


# ── dark-steel frame + kraft cargo palette ───────────────────────────────────
# The frame is solid steel with a single bright keyline edge that does double
# duty: it holds the silhouette against a bright DAY sky (a dark bar otherwise
# dissolves) and IS the read at NIGHT (a lit edge glowing out of the dark).
FRAME_STEEL = ( 70,  82,  92)   # #46525C dark steel bar body
FRAME_SHADE = ( 48,  58,  66)   # shadow side of the bar
FRAME_KEY   = (237, 241, 244)   # #EDF1F4 highlight edge — the double-duty keyline
FRAME_EDGE  = ( 30,  38,  44)   # hard contour so the bar keeps a crisp edge

BOX_KRAFT   = (201, 154,  91)   # #C99A5B warm cardboard — pops against blue day
BOX_SHADE   = (138, 100,  51)   # #8A6433 cardboard shadow / box-seam valleys
BOX_HI      = (224, 186, 132)   # sunlit top flap of the kraft box
BOX_EDGE    = ( 74,  52,  28)   # box contour

STRAP_DARK  = ( 38,  44,  52)   # the tie-down strap crossing the box
STRAP_HI    = (120, 134, 146)   # strap buckle / catch-light

WHEEL_DARK  = ( 43,  49,  56)   # #2B3138 near-black tyre
WHEEL_KEY   = (240, 244, 247)   # bright keyline ring — pops the wheel at night
WHEEL_HUB   = (210, 218, 226)   # bright hub plate the spoke cross is cut into
SPOKE_DARK  = ( 43,  49,  56)   # spoke cross cut into the bright hub (value flip)
WHEEL_BACK  = ( 30,  35,  41)   # the dimmer rear wheel behind the elbow


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (50→-40) to a 0..3 step. Drives the box settle offset
    and the wheel spoke-cross orientation one notch per pose."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _lean(x, y):
    """Shear a point back by LEAN_DEG about the body centre. Points ABOVE the
    centre shift back-left (toward the handle), points below shift forward —
    the same motion as tipping a real dolly back onto its wheels."""
    return (x - (y - BCY) * _LEAN_K, y)


def _lp(p):
    """Lean a point and round to ints for pygame draw calls."""
    lx, ly = _lean(p[0], p[1])
    return (int(round(lx)), int(round(ly)))


def _lpoly(pts):
    return [_lp(p) for p in pts]


def _wheel(surf, cx, cy, r, phase):
    """A BOLD near-black wheel with a bright keyline ring, a bright hub plate,
    and a spoke cross cut into the hub as a VALUE FLIP (dark spokes on the
    bright plate). The cross orientation cycles + → × → + → × across the four
    phases — the rolling tell that survives grayscale (a value flip inside a
    solid disc, not a hue change). Placed AFTER the lean so the round wheel
    stays round (a sheared circle would read as an ellipse)."""
    pygame.draw.circle(surf, WHEEL_KEY, (cx, cy), r + 1)
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), r)
    hub_r = r - 2
    pygame.draw.circle(surf, WHEEL_HUB, (cx, cy), hub_r)
    ang0 = 0 if phase % 2 == 0 else 45
    for k in range(4):
        a = math.radians(ang0 + k * 90)
        ex = cx + int(round(math.cos(a) * hub_r))
        ey = cy + int(round(math.sin(a) * hub_r))
        pygame.draw.line(surf, SPOKE_DARK, (cx, cy), (ex, ey), 2)
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), 2)


def _bar(surf, p_top, p_bot, half_w, c_body, c_shade, c_key, c_edge):
    """A solid leaning steel BAR (not wire): a filled quad from p_top to p_bot
    with a shadow side, a hard contour, and a 1px bright keyline down its
    LEADING (left/front) edge. The keyline is the double-duty read — it holds
    the silhouette on a bright sky and glows out of the dark at night."""
    (tx, ty), (bx, by) = p_top, p_bot
    # leading (front) edge is the LEFT side of the bar; trailing on the right.
    quad = _lpoly([(tx - half_w, ty), (tx + half_w, ty),
                   (bx + half_w, by), (bx - half_w, by)])
    pygame.draw.polygon(surf, c_body, quad)
    # shadow strip down the trailing half so the bar reads as a round tube
    shade = _lpoly([(tx, ty), (tx + half_w, ty), (bx + half_w, by), (bx, by)])
    pygame.draw.polygon(surf, c_shade, shade)
    pygame.draw.polygon(surf, c_edge, quad, 1)
    # bright keyline down the leading edge
    pygame.draw.line(surf, c_key, _lp((tx - half_w + 1, ty)),
                     _lp((bx - half_w + 1, by)), 2)


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)

    # Box settle: the strapped load bounces 0..2px on the toe plate as the rig
    # rolls. Combined with the wheel spoke cycle this is the 4-frame tell.
    settle = (0, 2, 1, 2)[ph]

    # ── the L-frame geometry (in pre-lean coordinates; _lean shears it) ──
    # Long arm of the L: a tall vertical handle-frame. Toe-plate: a short
    # horizontal ledge at the bottom. Wheels sit at the ELBOW where the two
    # meet. Everything is expressed relative to the body centre so the 14px
    # collision circle at (32,44) lands inside the dominant frame+box mass.
    frame_top = BCY - 24            # top of the handle grip
    frame_bot = BCY + 18            # bottom of the frame at the toe plate
    frame_x = BCX + 9               # the frame rides the BACK of the load

    # toe plate (foot of the L): a short horizontal ledge jutting FORWARD from
    # the base of the frame, the ledge the boxes rest on.
    toe_y = frame_bot
    toe_front = BCX - 16
    toe_back = frame_x + 3

    # ── rear wheel (drawn first, dimmer, peeking behind the elbow) ──────────
    elbow_y = frame_bot - 2
    _wheel_back_cx = int(round(_lean(frame_x + 2, elbow_y)[0])) + 3
    pygame.draw.circle(surf, WHEEL_BACK, (_wheel_back_cx, elbow_y + 6), 7)
    pygame.draw.circle(surf, (52, 60, 70), (_wheel_back_cx, elbow_y + 6), 7, 1)

    # ── the long handle-frame bar (back of the L) ───────────────────────────
    _bar(surf, (frame_x, frame_top), (frame_x, frame_bot), 3,
         FRAME_STEEL, FRAME_SHADE, FRAME_KEY, FRAME_EDGE)

    # handle grip: a short cross-bar across the top of the frame (the part a
    # worker grips). Bold so the "handle" read survives 40px.
    grip_l = _lp((frame_x - 6, frame_top + 1))
    grip_r = _lp((frame_x + 6, frame_top + 1))
    pygame.draw.line(surf, FRAME_SHADE, grip_l, grip_r, 5)
    pygame.draw.line(surf, FRAME_STEEL, grip_l, grip_r, 3)
    pygame.draw.line(surf, FRAME_KEY,
                     _lp((frame_x - 6, frame_top)), _lp((frame_x + 6, frame_top)), 1)

    # ── toe plate (foot of the L) ───────────────────────────────────────────
    toe = _lpoly([(toe_front, toe_y - 2), (toe_back, toe_y - 2),
                  (toe_back, toe_y + 3), (toe_front, toe_y + 3)])
    pygame.draw.polygon(surf, FRAME_STEEL, toe)
    pygame.draw.polygon(surf, FRAME_EDGE, toe, 1)
    pygame.draw.line(surf, FRAME_KEY,
                     _lp((toe_front, toe_y - 2)), _lp((toe_back, toe_y - 2)), 1)

    # ── strapped box stack riding the frame, settled onto the toe plate ─────
    # Two stacked kraft boxes are the warm mass that pops against the blue day
    # sky and reads as "a load". They sit centred so the collision circle is in
    # the box, and they SETTLE down by `settle` px each frame.
    by0 = settle
    # lower box (the bigger one resting on the toe plate)
    lo = [(BCX - 15, BCY - 1 + by0), (BCX + 9, BCY - 1 + by0),
          (BCX + 9, BCY + 14 + by0), (BCX - 15, BCY + 14 + by0)]
    lo = _lpoly(lo)
    pygame.draw.polygon(surf, BOX_KRAFT, lo)
    pygame.draw.polygon(surf, BOX_EDGE, lo, 1)
    # top sunlit flap + a seam down the middle so it reads as a real carton
    pygame.draw.line(surf, BOX_HI, lo[0], lo[1], 2)
    seam_t = _lp((BCX - 3, BCY - 1 + by0)); seam_b = _lp((BCX - 3, BCY + 14 + by0))
    pygame.draw.line(surf, BOX_SHADE, seam_t, seam_b, 1)

    # upper box (smaller, stacked on top, settles slightly more)
    by1 = settle + (1 if ph in (1, 3) else 0)
    up = [(BCX - 13, BCY - 13 + by1), (BCX + 6, BCY - 13 + by1),
          (BCX + 6, BCY - 1 + by1), (BCX - 13, BCY - 1 + by1)]
    up = _lpoly(up)
    pygame.draw.polygon(surf, BOX_KRAFT, up)
    pygame.draw.polygon(surf, BOX_EDGE, up, 1)
    pygame.draw.line(surf, BOX_HI, up[0], up[1], 2)
    # cross-flap seam on the top box lid
    flap_l = _lp((BCX - 4, BCY - 13 + by1)); flap_b = _lp((BCX - 4, BCY - 1 + by1))
    pygame.draw.line(surf, BOX_SHADE, flap_l, flap_b, 1)

    # ── tie-down strap crossing the whole stack to the frame ────────────────
    # The strap is the "strapped load" cue and ties the boxes visually to the
    # frame so they read as one rig, not a floating box. Drawn bold + dark with
    # a single bright buckle catch-light.
    strap_y = BCY + 4 + settle
    s_l = _lp((BCX - 16, strap_y)); s_r = _lp((frame_x, strap_y - 2))
    pygame.draw.line(surf, STRAP_DARK, s_l, s_r, 3)
    buckle = _lp((BCX - 2, strap_y - 1))
    pygame.draw.circle(surf, STRAP_DARK, buckle, 3)
    pygame.draw.circle(surf, STRAP_HI, (buckle[0] - 1, buckle[1] - 1), 1)

    # ── two wheels at the elbow (drawn LAST so they sit over the frame) ─────
    # The front-visible wheel runs the spoke cycle; placed after the lean so it
    # stays a true circle. The axle sits at the elbow of the L.
    wheel_cx = int(round(_lean(frame_x - 4, elbow_y + 5)[0]))
    wheel_cy = elbow_y + 6
    _wheel(surf, wheel_cx, wheel_cy, 7, ph)

    return surf
