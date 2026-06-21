"""HAND TRUCK / SACK BARROW — secret flyer skin concept (round 2).

A flying two-wheel hand truck (dolly) replaces Pip. The universal read is a
tall steel **I**: a long near-VERTICAL handle-frame standing on the trailing
edge as the dominant silhouette, a warm squared box-block hugging its front, a
single bold spoked wheel at the foot, and a toe-plate jutting forward. It is
industrial, upright, angular — the ONLY tall standing frame-rig in the cart
set, so it can never be mistaken for a basket or a wagon.

Round-1 read as a "wagon of boxes": the box stack out-massed the frame, the
whole rig sheared right as one block (no vertical anchor), and the two muddy
wheels + sub-pixel spoke vanished at 40px. Round 2 inverts the gestalt — the
FRAME is the silhouette, the boxes ride it as a more upright block, the lean is
a gentle wheels-forward TIP (not a uniform shear), and one bold spoked wheel
carries the roll.

There are NO wings and NO live particles. The "flap" is reinterpreted as two
combined big-value motions baked into the 4 frames:
  * the strapped box-block SHIFT/SETTLE 1-2px (as if bouncing on the toe plate),
  * the single bold front wheel runs a 4-phase spoke cycle (+ → × → + → ×).
Both survive grayscale (a value flip / position shift, not a hue change).

The 40px trap for a frame-rig is the long arm reading as a thin stick that
vanishes. So the load-bearing read is a SOLID dark-steel BAR (not wire), stood
near-vertical so it never sub-pixels into the sky, with an #EDF1F4 highlight
keyline down the leading edge that doubles as the night silhouette read.

Contract mirrors game/animal_ufo.py so the winner lifts straight into a
production module:
  * `build(wing_angle_deg) -> pygame.Surface` — one flat 64x84 SRCALPHA frame;
    dominant frame+box mass centred at (BCX, BCY) = (32, 44).
  * 4 box-settle + wheel-spin frames driven by `_WING_ANGLES = (50, 20, -10, -40)`.
  * drawn UPRIGHT with a GENTLE ~9° back-TIP baked in (NOT a per-frame
    rotation, and pivoted at the wheel so it tips wheels-forward / handle-back
    like a real dolly) — kept gentle so the engine's velocity tilt still reads
    as a dive, not a fight with the baked lean.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # dominant frame+box mass centre → (32, 44)

# Gentle back-TIP baked into the whole rig. Round 1's 15° uniform shear tipped
# load + frame together with no vertical anchor and read as a leaning block.
# Round 2 cuts it to ~9° and pivots the tip about the WHEEL/foot, so the foot
# stays planted and the handle swings back — a real dolly tipped onto its
# wheels. Gentle enough that the engine's later velocity tilt still reads as a
# dive rather than fighting the baked lean.
LEAN_DEG = 9
_LEAN_K = math.tan(math.radians(LEAN_DEG))
# Pivot the tip at the wheel/foot, not the body centre, so the vertical handle
# stays vertical-ish and the rig tips wheels-forward instead of shearing whole.
_PIVOT_Y = BCY + 18


# ── dark-steel frame + kraft cargo palette ───────────────────────────────────
# The frame is solid steel with a single bright keyline edge that does double
# duty: it holds the silhouette against a bright DAY sky (a dark bar otherwise
# dissolves) and IS the read at NIGHT (a lit edge glowing out of the dark).
FRAME_STEEL = ( 78,  90, 100)   # #4E5A64 dark steel bar body
FRAME_SHADE = ( 50,  60,  68)   # shadow side of the bar
FRAME_KEY   = (237, 241, 244)   # #EDF1F4 highlight edge — the double-duty keyline
FRAME_EDGE  = ( 28,  35,  41)   # hard contour so the bar keeps a crisp edge

BOX_KRAFT   = (201, 154,  91)   # #C99A5B warm cardboard — pops against blue day
BOX_SHADE   = (138, 100,  51)   # #8A6433 cardboard shadow / box-seam valleys
BOX_HI      = (224, 186, 132)   # sunlit top flap of the kraft box
BOX_EDGE    = ( 74,  52,  28)   # box contour

STRAP_DARK  = ( 34,  40,  48)   # the tie-down strap crossing the box
STRAP_HI    = (120, 134, 146)   # strap buckle / catch-light

WHEEL_DARK  = ( 40,  46,  53)   # #282E35 near-black tyre
WHEEL_KEY   = (240, 244, 247)   # bright keyline ring — pops the wheel at night
WHEEL_HUB   = (216, 224, 232)   # bright hub plate the spoke cross is cut into
SPOKE_DARK  = ( 34,  40,  47)   # spoke cross cut across the FULL disc (value flip)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (50→-40) to a 0..3 step. Drives the box settle offset
    and the wheel spoke-cross orientation one notch per pose."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _lean(x, y):
    """Tip a point back by LEAN_DEG about the WHEEL/foot pivot. Points ABOVE the
    pivot swing back toward the handle; the foot stays planted — the motion of
    tipping a real dolly back onto its wheels, NOT a whole-body shear."""
    return (x - (y - _PIVOT_Y) * _LEAN_K, y)


def _lp(p):
    """Lean a point and round to ints for pygame draw calls."""
    lx, ly = _lean(p[0], p[1])
    return (int(round(lx)), int(round(ly)))


def _lpoly(pts):
    return [_lp(p) for p in pts]


def _wheel(surf, cx, cy, r, phase):
    """One BOLD near-black wheel with a bright keyline ring, a LARGE bright hub
    plate, and a spoke cross cut across the FULL disc as a VALUE FLIP (dark
    spokes on the bright plate). The cross orientation cycles + → × → + → ×
    across the four phases — the rolling tell that survives grayscale (a value
    flip inside a solid disc, not a hue change). The hub is sized big relative
    to the tyre and the spokes run edge-to-edge so the rotation reads at 40px.
    Placed AFTER the lean so the round wheel stays round."""
    pygame.draw.circle(surf, WHEEL_KEY, (cx, cy), r + 1)
    pygame.draw.circle(surf, WHEEL_DARK, (cx, cy), r)
    # large bright hub plate so the spoke cross has a high-value field to flip on
    hub_r = r - 1
    pygame.draw.circle(surf, WHEEL_HUB, (cx, cy), hub_r)
    # spokes run the FULL disc (a diameter line, not a radius) so the cross is a
    # hard dark value flip across the whole bright plate — survives 40px.
    ang0 = 0 if phase % 2 == 0 else 45
    for k in range(2):
        a = math.radians(ang0 + k * 90)
        dx = int(round(math.cos(a) * hub_r))
        dy = int(round(math.sin(a) * hub_r))
        pygame.draw.line(surf, SPOKE_DARK, (cx - dx, cy - dy), (cx + dx, cy + dy), 2)
    # dark centre cap so the spokes meet in a solid hub, not a smear
    pygame.draw.circle(surf, SPOKE_DARK, (cx, cy), 2)


def _bar(surf, p_top, p_bot, half_w, c_body, c_shade, c_key, c_edge):
    """A solid steel BAR (not wire): a filled quad from p_top to p_bot with a
    shadow side, a hard contour, and a 1px bright keyline down its LEADING
    (left/front) edge. The keyline is the double-duty read — it holds the
    silhouette on a bright sky and glows out of the dark at night."""
    (tx, ty), (bx, by) = p_top, p_bot
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

    # Box settle: the strapped block bounces 0..2px on the toe plate as the rig
    # rolls. Combined with the wheel spoke cycle this is the 4-frame tell.
    settle = (0, 2, 1, 2)[ph]

    # ── the I-frame geometry (in pre-lean coords; _lean tips it back) ────────
    # The dominant silhouette is the tall near-vertical handle bar standing on
    # the TRAILING (right) edge of the rig. The box-block rides its FRONT; the
    # bold wheel sits at the foot; the toe-plate juts forward of the wheel.
    frame_x = BCX + 11             # the handle bar stands on the BACK edge
    frame_top = BCY - 26           # top of the handle grip — full tall arm
    frame_bot = BCY + 20           # foot of the frame at the axle/toe

    # ── the long handle-frame bar (the I — drawn first, behind the load) ─────
    # Stood near-vertical and thicker than round 1 so it is the silhouette, not
    # a thin stick tucked behind the boxes.
    _bar(surf, (frame_x, frame_top), (frame_x, frame_bot), 3,
         FRAME_STEEL, FRAME_SHADE, FRAME_KEY, FRAME_EDGE)

    # handle grip: a short cross-bar across the top of the frame (the part a
    # worker grips). Bold so the "handle" read survives 40px and caps the I.
    pygame.draw.line(surf, FRAME_SHADE,
                     _lp((frame_x - 7, frame_top + 1)),
                     _lp((frame_x + 4, frame_top + 1)), 5)
    pygame.draw.line(surf, FRAME_STEEL,
                     _lp((frame_x - 7, frame_top)),
                     _lp((frame_x + 4, frame_top)), 3)
    pygame.draw.line(surf, FRAME_KEY,
                     _lp((frame_x - 7, frame_top - 1)),
                     _lp((frame_x + 4, frame_top - 1)), 1)

    # ── toe plate (foot, jutting FORWARD of the wheel) ──────────────────────
    # A short horizontal ledge in front of the foot — the lip a real hand truck
    # slides under a load. A bright keyline row along its leading edge gives the
    # "hand truck, not wagon" read even at 40px.
    toe_y = frame_bot + 2
    toe_front = BCX - 17
    toe_back = frame_x
    toe = _lpoly([(toe_front, toe_y - 1), (toe_back, toe_y - 1),
                  (toe_back, toe_y + 3), (toe_front, toe_y + 4)])
    pygame.draw.polygon(surf, FRAME_STEEL, toe)
    pygame.draw.polygon(surf, FRAME_EDGE, toe, 1)
    pygame.draw.line(surf, FRAME_KEY,
                     _lp((toe_front, toe_y - 1)), _lp((toe_back, toe_y - 1)), 1)

    # ── strapped box-block riding the FRONT of the frame ─────────────────────
    # ONE squared, upright block (a tall carton with a single lid seam) instead
    # of a sheared two-box stack — it reads as a load hugging the bar, not a
    # wagon of crates. Pulled UP so its mass sits ABOVE Pip's parcel (which the
    # game composites just below centre), not fused into it. Near-vertical
    # sides (only the 2px frame-tip shear) keep it squared.
    by0 = settle
    box_l = BCX - 16
    box_r = BCX + 6
    box_top = BCY - 19 + by0       # block top sits well above centre
    box_bot = BCY + 10 + by0       # base rests above the parcel zone
    block = _lpoly([(box_l, box_top), (box_r, box_top),
                    (box_r, box_bot), (box_l, box_bot)])
    pygame.draw.polygon(surf, BOX_KRAFT, block)
    pygame.draw.polygon(surf, BOX_EDGE, block, 1)
    # sunlit top flap + a lid seam so it reads as a real carton, not a slab
    pygame.draw.line(surf, BOX_HI, block[0], block[1], 2)
    lid_y = box_top + 9
    pygame.draw.line(surf, BOX_SHADE,
                     _lp((box_l, lid_y)), _lp((box_r, lid_y)), 1)
    pygame.draw.line(surf, BOX_HI,
                     _lp((box_l, lid_y + 1)), _lp((box_r, lid_y + 1)), 1)
    # a vertical seam splits the lid flaps so the top reads as a closed carton
    pygame.draw.line(surf, BOX_SHADE,
                     _lp(((box_l + box_r) // 2, box_top)),
                     _lp(((box_l + box_r) // 2, lid_y)), 1)
    # right face catches a sliver of frame-shade so the block has depth and
    # tucks against the bar rather than floating in front of it
    pygame.draw.polygon(surf, BOX_SHADE,
                        _lpoly([(box_r - 2, box_top), (box_r, box_top),
                                (box_r, box_bot), (box_r - 2, box_bot)]))

    # ── tie-down strap binding the block to the frame ───────────────────────
    # The strap is the "strapped load" cue and ties the block visually to the
    # bar so they read as one rig. Drawn bold + dark with a bright buckle.
    strap_y = box_top + 16
    pygame.draw.line(surf, STRAP_DARK,
                     _lp((box_l - 1, strap_y)), _lp((frame_x, strap_y - 1)), 3)
    buckle = _lp((BCX - 4, strap_y))
    pygame.draw.circle(surf, STRAP_DARK, buckle, 3)
    pygame.draw.circle(surf, STRAP_HI, (buckle[0] - 1, buckle[1] - 1), 1)

    # ── the single bold wheel at the foot (drawn LAST, over the frame) ───────
    # One clearly-spoked wheel reads better at 40px than two muddy discs. The
    # axle sits at the foot of the I; the wheel is stamped after the lean so it
    # stays a true circle.
    wheel_cx = int(round(_lean(frame_x - 3, frame_bot + 2)[0]))
    wheel_cy = frame_bot + 4
    _wheel(surf, wheel_cx, wheel_cy, 8, ph)

    return surf
