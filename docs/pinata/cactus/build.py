"""CACTUS PINATA secret flyer skin — round-2 concept builder.

A prickly saguaro piñata in a tiny sombrero. The whole concept lives in the
SILHOUETTE: a tall green trunk with two upturned side-arms raised like a
classic saguaro, capped by a SMALL straw sombrero, planted on a rounded base.
It is the only top-heavy two-armed vertical in the piñata set, so it must read
"cactus" at 40px before any colour resolves.

Round-1 failed grayscale: the wide hat brim + ribbed trunk read as a BOLT
(round cap on a screw) and the trunk fused with Pip's parcel into a mushroom.
Round-2 fixes both by SHAPE, not colour:

  * NEGATIVE SPACE — each arm is split from the trunk by a transparent notch so
    the "trunk + two raised arms" reads in pure black. The arms are dropped low
    and the brim is narrowed so the ARM SPAN, not the hat, is the widest point.
  * SEPARATION — the trunk stops in a defined rounded base well above the canvas
    floor, with clear air below it, so the player sees "cactus, THEN gift".
  * 4 CHUNKY crepe bands (was 6 thin ones) with strong hi/lo value contrast, so
    the bands read as stacked papier-mâché rings, not screw threads.

The 4-frame tell is a FRINGE FLUTTER: the trunk stays planted while the crepe
fringe bands ripple horizontally with ALTERNATING phase per band (a wave down
the body) and the sombrero leans a little. Frames 1 and 3 carry DISTINCT
mid-flutter offsets so the loop reads as continuous motion, not a 2-pose blink.

Mirrors the contract in game/animal_ufo.py so a winner lifts straight into a
production module: 64×84 SRCALPHA canvas, dominant trunk mass centred at
(32,44), `build(wing_angle_deg) -> Surface`, driven by parrot._WING_ANGLES.
"""
import math
import pygame

from game.parrot import _add_outline, _aaellipse  # noqa: F401 (parity import)


# ── canvas + anchors (mirror animal_ufo.py / animal_skins.py) ────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # dominant trunk mass centre → (32, 44)


# ── palette (per brief) ──────────────────────────────────────────────────────
# Trunk green is pushed COOL + saturated so it never melts into the warm brown
# of Pip's parcel below — the two objects must separate by hue as well as gap.
GREEN_HI    = (74, 186, 86)     # #4ABA56 lit band (raised for hi/lo contrast)
GREEN_LO    = (38, 112, 50)     # #267032 shadow band (dropped for contrast)
GREEN_EDGE  = (26, 80, 38)      # darkest trunk edge for roundness + notch wall
RIB_SHADE   = (32, 96, 44)      # vertical rib shading
STRAW       = (231, 197, 106)   # #E7C56A sombrero straw
STRAW_LO    = (196, 160, 78)    # sombrero shadow
STRAW_HI    = (247, 224, 156)   # sombrero highlight band
FRINGE      = (251, 243, 221)   # #FBF3DD cream crepe fringe (the night keyline)
FLOWER_PINK = (244, 138, 184)   # pink flower dot
FLOWER_CORE = (255, 246, 250)   # white flower centre
SPINE       = (250, 244, 222)   # pale spine ticks (double as fringe keyline)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (_WING_ANGLES: 50→-40) to a 0..3 sway step. The flutter
    advances one notch per pose so the four frames read as a continuous wave."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Per-phase base lean of the whole body, in px. Phases 1 and 3 are NOT identical
# rest poses — they carry opposite micro-leans so frame 1 ≠ frame 3 and the loop
# reads left → mid-right → right → mid-left, a continuous orbit.
_LEAN = (-2.6, 0.9, 2.6, -0.9)
_HAT_TILT = (-8.0, 3.0, 8.0, -3.0)   # sombrero brim lean in degrees


def _band_flutter(band_i, ph):
    """Horizontal flutter offset (px) for one crepe band in one phase. Bands
    ALTERNATE phase (even vs odd band index push opposite ways) so a wave
    travels down the trunk rather than the whole column sliding rigidly. The
    wave's direction reverses with the body lean, and phases 1/3 sample the wave
    a quarter-cycle apart so the two 'centre-ish' poses differ."""
    # A travelling sine: argument mixes band row and the phase clock.
    arg = (band_i * 0.9) + (ph * math.pi / 2.0)
    amp = 1.7
    return math.sin(arg) * amp


# ── geometry constants — tuned so ARM SPAN is the widest mass, brim is narrow ─
TRUNK_HALF   = 6                 # trunk half-width (slimmer than R1's 9)
ARM_SPAN     = 15                # how far an arm reaches out from trunk centre
NOTCH        = 4                 # transparent air-gap carved trunk↔arm (px)


def _flower(surf, x, y):
    """A small pink-and-white flower dot: 4 pink petals around a white core."""
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        pygame.draw.circle(surf, FLOWER_PINK, (int(x + dx), int(y + dy)), 1)
    pygame.draw.circle(surf, FLOWER_CORE, (int(x), int(y)), 1)


def _arm(surf, side, lean):
    """One upturned saguaro arm drawn as an L: a short horizontal stub off the
    trunk that bends UP into a tall vertical riser. CRUCIAL: the stub starts
    OUTSIDE the trunk wall by NOTCH px, leaving a transparent vertical gap so
    the silhouette reads as trunk + separate raised arm (not a bolt cap).

    `side` is -1 (left) / +1 (right). Arms sit LOW on the trunk (around BCY) and
    their tips stop short of the sombrero brim, so the widest point of the whole
    shape is the ARM SPAN and there is air between arm tip and hat."""
    drift = lean * 0.35                     # arms drift gently with the sway
    inner_x = BCX + side * (TRUNK_HALF + NOTCH) + drift   # leaves the notch gap
    tip_x = BCX + side * ARM_SPAN + drift
    stub_y = BCY + 4                         # arms attach LOW on the trunk
    top_y = BCY - 12                         # riser top — below the hat brim

    th = 7                                   # arm thickness — fat enough at 40px
    # horizontal stub (low value base + lit top so the arm has its own roundness)
    pygame.draw.line(surf, GREEN_LO, (inner_x, stub_y), (tip_x, stub_y), th)
    pygame.draw.line(surf, GREEN_HI, (inner_x, stub_y - 1), (tip_x, stub_y - 1), th - 4)
    # vertical riser
    pygame.draw.line(surf, GREEN_LO, (tip_x, stub_y), (tip_x, top_y), th)
    pygame.draw.line(surf, GREEN_HI, (tip_x - side, stub_y), (tip_x - side, top_y), th - 4)
    # rounded elbow + rounded tip cap so the arm is a smooth saguaro L
    pygame.draw.circle(surf, GREEN_LO, (int(tip_x), int(stub_y)), th // 2)
    pygame.draw.circle(surf, GREEN_HI, (int(tip_x - side), int(top_y)), th // 2)
    pygame.draw.circle(surf, GREEN_EDGE, (int(tip_x), int(top_y)), th // 2, 1)
    # pale spine ticks up the riser — keylines the green at night
    pygame.draw.circle(surf, SPINE, (int(tip_x - side * 2), int(top_y)), 1)
    pygame.draw.circle(surf, SPINE, (int(tip_x - side * 2), int((top_y + stub_y) // 2)), 1)
    # a flower on the arm shoulder for the night pop
    _flower(surf, tip_x, top_y - 1)
    return tip_x


def _carve_notch(surf, side, lean):
    """Punch a TRANSPARENT vertical slot between the trunk wall and the arm
    riser so the negative space survives grayscale (and the house outline traces
    BOTH edges). Done after trunk + arms are drawn, as an explicit alpha cut —
    the read of 'two raised arms' depends on this gap, so we guarantee it rather
    than hope overlap leaves it."""
    drift = lean * 0.35
    inner = BCX + side * TRUNK_HALF + lean      # trunk outer wall
    outer = BCX + side * (TRUNK_HALF + NOTCH) + drift   # arm riser inner wall
    x0, x1 = sorted((int(inner), int(outer)))
    # the slot runs from just under the arm-tip top to the stub joint
    slot = pygame.Rect(x0, BCY - 11, max(1, x1 - x0), 15)
    surf.fill((0, 0, 0, 0), slot)


def _sombrero(surf, cx, cy, tilt):
    """A SMALL tilted straw sombrero. Narrower than round 1 (brim radius 11, was
    17) so the hat is NOT the widest mass — the arm span wins. A flat brim
    ellipse + a low crown, rotated by `tilt` so the hat leans with the sway."""
    pad = 20
    s = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    ox, oy = pad, pad
    brim_rx = 11
    # brim
    _aaellipse(s, STRAW_LO, (ox, oy + 2), brim_rx, 4)
    _aaellipse(s, STRAW, (ox, oy + 1), brim_rx, 4)
    # turned-up brim edge keyline (cream) — reads the hat at night
    pygame.draw.ellipse(s, FRINGE, pygame.Rect(ox - brim_rx, oy - 3, brim_rx * 2, 8), 1)
    # crown
    _aaellipse(s, STRAW_LO, (ox, oy - 3), 6, 5)
    _aaellipse(s, STRAW, (ox, oy - 4), 5, 4)
    _aaellipse(s, STRAW_HI, (ox - 1, oy - 5), 3, 2)
    # decorative band around the crown base
    pygame.draw.line(s, FLOWER_PINK, (ox - 5, oy - 2), (ox + 5, oy - 2), 2)
    rot = pygame.transform.rotozoom(s, tilt, 1.0)
    rr = rot.get_rect(center=(cx, cy))
    surf.blit(rot, rr.topleft)


def build(wing_angle_deg):
    """One CACTUS PINATA frame on a 64×84 SRCALPHA canvas. Trunk + two raised
    arms (separated by carved notches) is the read; the per-band fringe flutter
    + leaning sombrero are the sway tell. Drawn UPRIGHT — no baked body
    rotation."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    lean = _LEAN[ph]
    hat_tilt = _HAT_TILT[ph]

    # Trunk runs from just under the hat down to a rounded base. The base STOPS
    # well above the canvas floor so there is clear air between cactus and the
    # parcel the game composites below — "cactus, THEN gift", two objects.
    top_y = BCY - 17
    base_y = BCY + 18              # rounded base centre (leaves ~12px air below)
    band_h = 8                    # CHUNKY bands (was ~7 across 6 → now 4)
    n_bands = 4

    # ── arms BEFORE the trunk so the trunk overlaps their inner roots, then we
    #    carve the notch back out for guaranteed negative space ───────────────
    _arm(surf, -1, lean)
    _arm(surf, +1, lean)

    # ── trunk as 4 stacked crepe bands, each with its own flutter offset so the
    #    fringe ripples down the body in a travelling wave ─────────────────────
    span = base_y - top_y
    last_cx = BCX
    for i in range(n_bands):
        t = i / (n_bands - 1)
        cy = top_y + span * t
        # base lean tapers toward the planted base; flutter alternates per band.
        band_lean = lean * (1.0 - 0.55 * t) + _band_flutter(i, ph)
        cx = BCX + band_lean
        hi = (i % 2 == 0)
        color = GREEN_HI if hi else GREEN_LO
        # bottom band is the rounded BASE — drawn wider + fully rounded so the
        # trunk visibly TERMINATES instead of trailing toward the parcel.
        is_base = (i == n_bands - 1)
        hw = TRUNK_HALF + (1 if is_base else 0)
        bh = band_h + (2 if is_base else 1)
        rect = pygame.Rect(int(cx - hw), int(cy - bh / 2), int(hw * 2), int(bh))
        radius = hw if is_base else max(3, bh // 2)
        pygame.draw.rect(surf, color, rect, border_radius=radius)
        # vertical rib shading + lit edge for trunk roundness
        pygame.draw.line(surf, RIB_SHADE, (rect.centerx - 2, rect.top + 1),
                         (rect.centerx - 2, rect.bottom - 1), 1)
        pygame.draw.line(surf, GREEN_EDGE, (rect.right - 1, rect.top + 1),
                         (rect.right - 1, rect.bottom - 1), 1)
        last_cx = rect.centerx

        # ── crepe fringe: a strong cream keyline + ticked lower edge at the seam
        #    between bands. This is the part that VISIBLY shifts frame to frame
        #    (the flutter) and the pale value that survives grayscale + keylines
        #    the green at night. Only between bands, not under the base. ───────
        if not is_base:
            fy = rect.bottom
            pygame.draw.line(surf, FRINGE, (rect.left + 1, fy), (rect.right - 1, fy), 1)
            for fx in range(rect.left + 1, rect.right, 3):
                pygame.draw.line(surf, FRINGE, (fx, fy), (fx, fy + 2), 1)

    # ── carve the negative-space notches between trunk wall and each arm ──────
    _carve_notch(surf, -1, lean)
    _carve_notch(surf, +1, lean)

    # ── flowers on the upper trunk for the night pop (arm flowers drawn in _arm)
    _flower(surf, last_cx - 3 + lean * 0.4, top_y + band_h)

    # ── small sombrero perched on top, leaning with the sway, with an air gap
    #    above the trunk crown so it reads as a separate hat ───────────────────
    _sombrero(surf, BCX + lean, top_y - 6, hat_tilt)

    return surf
