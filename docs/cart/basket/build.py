"""HAND-BASKET secret flyer skin — concept build.

A deep red plastic carry-basket replaces the bird. The IDENTITY is the
"quick trip" silhouette: a deep U-shaped bucket with TWO thin folding
handle loops that meet in a peak above the centre, and NO wheels. That
twin-handle peak over a solid bucket is the icon; the absence of wheels
is what makes it distinct from any rolling cart.

There are NO wings and NO live particles. The 4-frame tell is the
CARGO — three chunky grocery lumps poking OVER the rim bob and re-stack
across the frames while the handles sway slightly. The cargo IS the
animation; in grayscale it survives as moving high-contrast blobs over
the rim line, and the deep red bucket holds its value on both day and
night skies with the pale rim highlight as the night keyline.

IMPORTANT — the skin draws NO parcel/gift-box of its own. The game
composites Pip's real parcel hanging BELOW the flyer centre; this skin
renders only groceries-poking-over-the-rim so the live parcel reads as
the distinct "cargo slung under the basket". Anything box-shaped on the
basket front would collide with that real parcel (two stacked parcels).
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + anchors (mirror animal_ufo.py / animal_skins.py) ────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # flyer/bird centre → (32, 44)


# ── geometry ─────────────────────────────────────────────────────────────────
# The GAME composites Pip's real parcel at a FIXED spot: centred, hanging 12px
# below the bird centre (32,44) → parcel centre at canvas y≈56, and the 22px
# parcel sprite reaches up to a TOP edge at canvas y≈45. So the whole basket is
# pinned into the UPPER half of the 64×84 canvas, with its rounded base ABOVE
# y≈40 — that leaves a clean band of sky between the basket base and the parcel
# top, and the live read is "basket up top, parcel dangling beneath on the
# sling", never "parcel sitting on the basket front". The bucket is therefore
# anchored to its OWN base line (BOT_Y), not to the bird centre.
RIM_HALF   = 21                # half-width of the top rim line
BOT_HALF   = 16                # half-width of the bottom (narrower → flared U)
BOT_Y      = 35                # bottom of the bucket — base ellipse reaches ~41,
                               # ~4px of sky above the parcel top at ~45 while the
                               # handle apex keeps ~2px headroom under the canvas top
RIM_Y      = BOT_Y - 18        # top rim line — an 18px bucket wall in the upper
                               # canvas (shallower than r2 so the base clears the
                               # parcel, still unmistakably a flared bucket)
RIM_THICK  = 4                 # the bold lip cap thickness


# ── palette ──────────────────────────────────────────────────────────────────
# Deep red plastic holds value on day AND night; the pale rim highlight is the
# night keyline. Groceries are a multi-pop trio so the jostle reads in colour
# and as high-contrast blobs in grayscale.
BASKET_RED   = (214, 69, 62)    # #D6453E  body
BASKET_SHADE = (146, 36, 31)    # #92241F  inner wall / shaded side
RIM_HI       = (242, 201, 197)  # #F2C9C5  rim highlight (night keyline)
BASKET_DEEP  = (104, 24, 20)    # darker still — the bucket interior void
SLOT_LINE    = (170, 48, 42)    # vertical basket-slot ribs (texture, subtle)

HANDLE_RED   = (196, 58, 52)    # handle loops — a touch darker than the body
# Two keyline strengths: a softer day highlight (so the loop doesn't read as a
# plasticky-glossy rail against the bright sky) and the full pale keyline that
# the house outline already gives the loop at night. We bake the SOFT one.
HANDLE_HI    = (224, 150, 142)  # softened day highlight — ~10% pulled down

# Grocery trio is tuned for DISTINCT GRAYSCALE VALUES so the jostle reads as
# three separate lumps re-stacking even with hue removed: the green fruit is
# pushed to a MID value, the bottle to a darker-saturated value, and the bread
# stays light — three rungs on the value ladder, dark→mid→light.
GROC_GREEN   = (78, 134, 52)    # darker apple — lands MID-grey, not pale
GROC_GREEN_D = (50, 92, 34)
GROC_BOTTLE  = (196, 64, 78)    # juice bottle — DARK value rung, distinct hue
GROC_BOTTLE_D = (138, 40, 52)
GROC_BREAD   = (240, 232, 214)  # #F0E8D6  baguette / bread — the LIGHT rung
GROC_BREAD_D = (198, 186, 158)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 jostle frame. `_WING_ANGLES` runs
    50→20→-10→-40, so each pose advances the cargo bob/restack one step."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# ── bucket ───────────────────────────────────────────────────────────────────
def _bucket(surf):
    """Draw the deep U-shaped basket body: a flared trapezoid with a rounded
    bottom, a darker interior void at the top, vertical slot ribs for the
    plastic-basket read, and a bold lipped rim cap with a pale highlight."""
    lx_top, rx_top = BCX - RIM_HALF, BCX + RIM_HALF
    lx_bot, rx_bot = BCX - BOT_HALF, BCX + BOT_HALF

    # Body trapezoid (flared walls). Bottom corners rounded by overlaying a
    # squashed ellipse so the U-base reads soft, not boxy.
    body = [
        (lx_top, RIM_Y),
        (rx_top, RIM_Y),
        (rx_bot, BOT_Y),
        (lx_bot, BOT_Y),
    ]
    pygame.draw.polygon(surf, BASKET_RED, body)
    _aaellipse(surf, BASKET_RED, (BCX, BOT_Y), BOT_HALF, 6)

    # Shaded right wall — a slim darker wedge gives the bucket roundness so it
    # doesn't read as a flat card at 40px.
    pygame.draw.polygon(surf, BASKET_SHADE, [
        (BCX + 4, RIM_Y),
        (rx_top, RIM_Y),
        (rx_bot, BOT_Y),
        (BCX + 2, BOT_Y),
    ])
    # restate the body left-of-centre so the shade is only a side sliver
    pygame.draw.polygon(surf, BASKET_RED, [
        (lx_top, RIM_Y),
        (BCX + 4, RIM_Y),
        (BCX + 2, BOT_Y),
        (lx_bot, BOT_Y),
    ])

    # Vertical slot ribs — the open-weave plastic basket tell. Kept low-contrast
    # so they're texture at 40px, not noise.
    for i in range(-3, 4):
        t = i / 3.0
        x_top = int(BCX + t * (RIM_HALF - 3))
        x_bot = int(BCX + t * (BOT_HALF - 3))
        pygame.draw.line(surf, SLOT_LINE, (x_top, RIM_Y + 3), (x_bot, BOT_Y - 3), 1)

    # Interior void at the top — a dark inner-wall band so groceries sit INSIDE
    # the basket and the rim reads as a hollow opening, not a solid block.
    inner = [
        (lx_top + 2, RIM_Y),
        (rx_top - 2, RIM_Y),
        (rx_top - 5, RIM_Y + 7),
        (lx_top + 5, RIM_Y + 7),
    ]
    pygame.draw.polygon(surf, BASKET_DEEP, inner)
    _aaellipse(surf, BASKET_DEEP, (BCX, RIM_Y + 1), RIM_HALF - 2, 4)

    # Bold rim cap — the single most important horizontal line. A thick lip with
    # a pale top highlight that becomes the night keyline.
    pygame.draw.line(surf, BASKET_SHADE, (lx_top, RIM_Y + 1), (rx_top, RIM_Y + 1),
                     RIM_THICK)
    _aaellipse(surf, BASKET_RED, (lx_top, RIM_Y), 3, RIM_THICK // 2 + 1)
    _aaellipse(surf, BASKET_RED, (rx_top, RIM_Y), 3, RIM_THICK // 2 + 1)
    pygame.draw.line(surf, RIM_HI, (lx_top + 1, RIM_Y - 1), (rx_top - 1, RIM_Y - 1), 2)


# ── handles ──────────────────────────────────────────────────────────────────
def _handles(surf, sway):
    """Twin folding handle loops rising from the rim to a peak above centre.
    `sway` (px) nudges the loop apexes toward/away across frames so the handles
    breathe with the cargo. The loops are thin but fattened enough (3px) that
    the read survives at 40px; the bold bucket carries the silhouette anyway."""
    base_y = RIM_Y - 1
    # anchor feet on the rim — each handle is hinged near the rim shoulders.
    l_foot = BCX - 12
    r_foot = BCX + 12
    # Handle rise is sized so the twin loops crown near the canvas top without
    # clipping — the bucket sits higher now, so a 14px rise keeps the apex in
    # frame while still arcing a clear head above the rim.
    peak_y = RIM_Y - 14
    # The two loop apexes stay PARTED at centre so the "twin folding handle"
    # silhouette survives at 40px (round 1 fused into one hump). A wider base
    # parting (±4 + sway) plus the dark interior gap below keep the apex open.
    l_apex = (BCX - 4 - sway, peak_y)
    r_apex = (BCX + 4 + sway, peak_y)

    # Each handle is an arc-like loop drawn as a thick poly-line from its rim
    # foot up to the apex. A subtle inner highlight catches the keyline.
    def _loop(foot_x, apex, lean):
        ctrl_x = foot_x + lean
        pts = []
        for k in range(0, 11):
            t = k / 10.0
            # quadratic-ish bend: foot → control → apex
            x = (1 - t) * (1 - t) * foot_x + 2 * (1 - t) * t * ctrl_x + t * t * apex[0]
            y = (1 - t) * (1 - t) * base_y + 2 * (1 - t) * t * (peak_y + 4) + t * t * apex[1]
            pts.append((x, y))
        pygame.draw.lines(surf, HANDLE_RED, False, pts, 4)
        # softer day highlight along the top-outer of the loop (not a glossy rail)
        pygame.draw.lines(surf, HANDLE_HI, False, pts[3:], 1)
        # a small hinge knuckle where the handle meets the rim
        pygame.draw.circle(surf, BASKET_SHADE, (int(foot_x), int(base_y)), 2)

    _loop(l_foot, l_apex, lean=5)
    _loop(r_foot, r_apex, lean=-5)

    # 1px interior shadow gap down the centre of the apex: carve a dark sliver
    # BETWEEN the two loops so they never merge into one solid hump. Drawn as a
    # thin vertical dark line from just below the apexes down into the opening.
    gap_x = BCX
    pygame.draw.line(surf, BASKET_DEEP, (gap_x, peak_y - 1), (gap_x, peak_y + 9), 1)


# ── groceries (the 4-frame tell) ─────────────────────────────────────────────
def _round_fruit(surf, cx, cy, r, base, shade):
    _aaellipse(surf, shade, (cx, cy + 1), r, r)
    _aaellipse(surf, base, (cx, cy), r, r - 1)
    _aaellipse(surf, (255, 255, 255), (cx - r // 2, cy - r // 2), 1, 1)


def _bottle(surf, cx, top_y, h, base, shade):
    """A bottle neck poking over the rim: a slim capsule with a darker cap.
    Drawn as the DARK value rung so it separates from the bread in grayscale."""
    pygame.draw.line(surf, shade, (cx + 1, top_y), (cx + 1, top_y + h), 5)
    pygame.draw.line(surf, base, (cx, top_y), (cx, top_y + h), 5)
    pygame.draw.circle(surf, base, (cx, top_y), 2)
    pygame.draw.circle(surf, (54, 44, 40), (cx, top_y - 1), 2)   # dark cap


def _bread(surf, cx, cy, length, base, shade):
    """A baguette tip angled out of the rim — an elongated tan capsule."""
    a = (cx - length // 2, cy + 4)
    b = (cx + length // 2, cy - 4)
    pygame.draw.line(surf, shade, (a[0], a[1] + 1), (b[0], b[1] + 1), 6)
    pygame.draw.line(surf, base, a, b, 5)
    # score marks along the loaf
    for k in (-2, 0, 2):
        mx = cx + k * 4
        my = cy + 1 - k
        pygame.draw.line(surf, shade, (mx - 1, my - 2), (mx + 1, my + 2), 1)


def _groceries(surf, phase):
    """Three chunky lumps poking OVER the rim — NOT a box on the basket front.
    Every lump's body sits at or ABOVE the rim line so the read is "groceries
    spilling over the top", leaving the basket front clean for the live parcel
    slung below. Each frame bobs and re-stacks the trio so the cargo visibly
    jostles across the 4 poses — the cargo IS the animation."""
    # per-phase vertical bob (px) for [fruit, bottle, bread] — they take turns
    # rising/sinking so the eye reads a re-stacking jostle, not a uniform bounce.
    bob = [
        (0, -2, 1),    # phase 0: bottle high, bread mid
        (-2, 0, 0),    # phase 1: fruit rises
        (1, 1, -2),    # phase 2: bread pops up
        (-1, -1, 2),   # phase 3: settle, bread sinks
    ][phase]
    # slight horizontal shuffle so lumps re-stack rather than just bob in place.
    shuf = [0, -1, 1, 0][phase]

    # Anchor lumps to the rim TOP, not the basket interior, so none of them
    # drops onto the front face (where it would read as a parcel/gift box).
    rim = RIM_Y

    # bottle — the DARK value rung, centre-right, the tall pop poking highest.
    _bottle(surf, BCX + 7 - shuf, rim - 14 + bob[1], 11, GROC_BOTTLE, GROC_BOTTLE_D)

    # green round fruit — the MID value rung, left, the heaviest blob, riding
    # ON the rim line (its lower half tucks just behind the lip cap).
    _round_fruit(surf, BCX - 9 + shuf, rim - 5 + bob[0], 6, GROC_GREEN, GROC_GREEN_D)

    # baguette tip — the LIGHT value rung, angled out over the rim between the
    # other two. Lifted so it crowns the rim rather than lying across the front.
    _bread(surf, BCX + 1 + shuf, rim - 8 + bob[2], 17, GROC_BREAD, GROC_BREAD_D)


# ── frame builder ────────────────────────────────────────────────────────────
def build(wing_angle_deg):
    """One flat upright frame on the 64x84 canvas. NO rotation baked — velocity
    tilt is applied by the getter later. Draw order: handles behind the rim,
    then the bucket, then groceries sitting in the opening, then the handles'
    visible upper arcs restated so they read as looping over the cargo."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    # sway swings the handle apexes a touch each frame, in sympathy with cargo.
    sway = [2, 0, -2, 0][ph]

    # Handles drawn first (their lower legs sit behind the rim cap).
    _handles(surf, sway)

    # Bucket body over the handle feet.
    _bucket(surf)

    # Groceries sit inside the rim opening — the moving tell.
    _groceries(surf, ph)

    # Restate just the upper handle arcs so the loops clearly pass OVER the
    # cargo silhouette (a basket you carry, not a crate).
    _handles_top(surf, sway)

    return surf


def _handles_top(surf, sway):
    """Redraw only the upper third of each handle loop so it reads as arcing
    above the groceries. Cheap: reuses the same bend math as `_handles`."""
    base_y = RIM_Y - 1
    peak_y = RIM_Y - 14
    for foot_x, apex_dx, lean in ((BCX - 12, -4 - sway, 5), (BCX + 12, 4 + sway, -5)):
        apex = (BCX + apex_dx, peak_y)
        ctrl_x = foot_x + lean
        pts = []
        for k in range(5, 11):
            t = k / 10.0
            x = (1 - t) * (1 - t) * foot_x + 2 * (1 - t) * t * ctrl_x + t * t * apex[0]
            y = (1 - t) * (1 - t) * base_y + 2 * (1 - t) * t * (peak_y + 4) + t * t * apex[1]
            pts.append((x, y))
        pygame.draw.lines(surf, HANDLE_RED, False, pts, 4)
        pygame.draw.lines(surf, HANDLE_HI, False, pts, 1)
    # re-carve the interior shadow gap so the apexes stay two distinct loops
    # even after the upper arcs are restated over the cargo.
    pygame.draw.line(surf, BASKET_DEEP, (BCX, peak_y - 1), (BCX, peak_y + 9), 1)


if __name__ == "__main__":
    # local smoke-build (no display needed beyond dummy driver)
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))
    for a in _WING_ANGLES:
        s = build(a)
        assert s.get_size() == (COMPOSITE_W, COMPOSITE_H)
    print("build OK")
