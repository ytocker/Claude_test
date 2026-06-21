"""BURRO PINATA — a flying donkey piñata flyer skin (Round-1 concept).

The piñata set needs five flyers that each read as their OWN distinct thing at
~40px. The burro's job is to be the only LEGGED CREATURE in the set: a boxy
crepe-fringe donkey body with a stubby upright head + two ear nubs and four
short tassel-tipped legs dangling on its festival rope. No bird, no wings.

Identity beats the contract has to protect at 40px:
  * SILHOUETTE — a side-profile 4-legged quadruped. Boxy body, short upright
    neck/head, two ear nubs, four little legs. The legs are SHORT, PAIRED
    (front pair + back pair), and tassel-tipped so they survive downscale as
    blobs rather than vanishing into hairline mush.
  * TELL (no wings / no particles) — TROT-SWAY. The whole body bobs up/down and
    all four legs swing out → tucked → out, a gentle festive trot as the piñata
    bounces on its rope. The leg-position delta is a pure SILHOUETTE change, so
    it survives grayscale.
  * COLOUR — tiered crepe-paper fringe bands: hot-pink / orange / turquoise,
    with a cream mane + cream leg-fringe. The cream keylines the dark body at
    night; the fringe scallops sell "piñata", not "toy horse".

Contract (mirrors game/animal_ufo.py so a winner lifts straight into a
production module):
  * `build(wing_angle_deg) -> pygame.Surface` — one flat frame, 64x84 SRCALPHA,
    body mass centred at (32,44), legs dangle below, drawn UPRIGHT (no tilt).
  * The 4 trot frames are driven by `_WING_ANGLES=(50,20,-10,-40)` → leg swing
    + body bob, consumed by `animal_ufo._make_prebuilt_skin`.
"""
import math
import pygame

from game.parrot import _aaellipse


# ── canvas + anchors (mirror animal_ufo.py / animal_skins.py) ────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # donkey body centre → (32, 44); 14px hit circle


# ── crepe-fringe colourway ───────────────────────────────────────────────────
# The body is built from three tiered fringe BANDS top→bottom so the piñata read
# is unmistakable. Each band carries a slightly darker "shadow" tone for the
# scallop undersides and the body's rounded volume.
PINK        = (242, 73, 126)     # #F2497E  top band
PINK_D      = (196, 48, 96)
ORANGE      = (245, 139, 31)     # #F58B1F  middle band
ORANGE_D    = (200, 104, 18)
TURQ        = (35, 194, 168)     # #23C2A8  lower band
TURQ_D      = (22, 150, 130)

CREAM       = (255, 241, 214)    # #FFF1D6  mane + fringe — the night keyline
CREAM_D     = (228, 206, 168)    # cream shadow / stitch
SNOUT       = (250, 232, 202)    # pale crepe snout tip
EAR_IN      = (255, 158, 120)    # warm inner-ear crepe
EYE         = (40, 26, 30)
EYE_GLINT   = (255, 255, 255)
HOOF        = (120, 86, 70)      # tassel knot / little hoof nub at each leg end

# Per-leg tassel colours cycle the festival palette so the dangling legs sparkle
# with all three crepe hues even when tiny.
TASSELS = (PINK, TURQ, ORANGE, PINK)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 trot frame. `_WING_ANGLES` runs 50→-40, so
    the four poses step the legs out → tucked → out and the body bob cycles."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Per-frame trot drivers, indexed by phase 0..3.
#   bob  — vertical body offset (px); a gentle bounce on the rope.
#   sway — leg swing amount; +out (legs splayed forward/back), -tuck (gathered).
_TROT = (
    # phase 0  legs OUT, body LOW on the bounce
    {"bob":  1, "sway":  1.0},
    # phase 1  legs mid, body rising
    {"bob": -1, "sway":  0.0},
    # phase 2  legs TUCKED, body HIGH at the top of the bounce
    {"bob": -2, "sway": -1.0},
    # phase 3  legs mid, body dropping
    {"bob":  0, "sway":  0.0},
)


def _fringe_band(surf, cx, cy, rx, ry, color, shadow, n_scallop, *, flip_dark=False):
    """A tiered crepe-paper fringe band: a filled rounded slab whose lower edge
    is cut into scallop nubs (the cut crepe fringe). `n_scallop` little arcs
    along the bottom sell the layered-paper read; a thin shadow line under the
    band gives the tier its overlap depth."""
    # main slab
    _aaellipse(surf, color, (cx, cy), rx, ry)
    # scallop fringe along the lower edge of the band
    step = (2 * rx) / n_scallop
    r_sc = max(2, int(step * 0.6))
    fy = cy + ry - 1
    for i in range(n_scallop):
        sx = int(cx - rx + step * (i + 0.5))
        # depth of fringe follows the band's curvature so the tier hangs round
        t = (sx - (cx - rx)) / (2 * rx)
        curve = math.sin(math.pi * t)
        pygame.draw.circle(surf, color, (sx, int(fy + curve * 1.5)), r_sc)
        # shadow notch between scallops for the cut-paper read
        pygame.draw.circle(surf, shadow, (int(sx + step * 0.5), int(fy + curve * 1.0)),
                           max(1, r_sc - 1))


def _leg(surf, hip_x, hip_y, swing, tassel_color, *, back=False):
    """One short tassel-tipped leg. The leg is a stubby crepe stub that ends in
    a fat tassel knot — short + paired + tassel-tipped so it survives 40px as a
    nub instead of a hairline. `swing` (+out / -tuck) drives the trot delta; the
    foot end moves, the hip stays pinned to the body so only the silhouette's
    lower edge animates."""
    # back legs swing opposite the front pair so the trot reads as a gait.
    s = -swing if back else swing
    foot_x = int(hip_x + s * 4)
    foot_y = int(hip_y + 11 - abs(s) * 1.5)
    knee_x = int(hip_x + s * 2)
    knee_y = int(hip_y + 6)
    # crepe leg stub — cream so it keylines the dark body at night
    pygame.draw.line(surf, CREAM_D, (hip_x, hip_y), (knee_x, knee_y), 5)
    pygame.draw.line(surf, CREAM, (hip_x, hip_y), (knee_x, knee_y), 3)
    pygame.draw.line(surf, CREAM_D, (knee_x, knee_y), (foot_x, foot_y), 5)
    pygame.draw.line(surf, CREAM, (knee_x, knee_y), (foot_x, foot_y), 3)
    # fat tassel knot at the foot (the part that reads at 40px)
    pygame.draw.circle(surf, HOOF, (foot_x, foot_y), 3)
    _aaellipse(surf, tassel_color, (foot_x, foot_y + 2), 3, 4)
    # three little tassel strands fanned below the knot
    for dx in (-2, 0, 2):
        pygame.draw.line(surf, tassel_color, (foot_x, foot_y + 1),
                         (foot_x + dx, foot_y + 6), 1)


def _ear(surf, base_x, base_y, lean, color):
    """An upright ear NUB — a small cream crepe triangle with a warm inner. Two
    of these on the head are the donkey tell. `lean` tips the tip outward a touch
    per side so the pair frames the head."""
    tip = (base_x + lean, base_y - 9)
    pts = [(base_x - 3, base_y), (base_x + 3, base_y), tip]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, EAR_IN, [(base_x - 1, base_y - 1),
                                       (base_x + 1, base_y - 1),
                                       (base_x + lean // 2, base_y - 6)])
    pygame.draw.polygon(surf, CREAM_D, pts, 1)


def build(wing_angle_deg):
    """One trot frame. Body mass + head sit at/above (32,44); the four legs
    dangle below to frame Pip's parcel. Drawn upright; velocity tilt applied
    downstream by the cached getter."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    bob = _TROT[ph]["bob"]
    sway = _TROT[ph]["sway"]

    cx = BCX
    cy = BCY + bob                  # whole body bobs on the rope

    # ── rope nub up top — the piñata hangs from a string ─────────────────────
    pygame.draw.line(surf, CREAM_D, (cx, cy - 22), (cx, cy - 16), 2)

    # ── LEGS first so the body slab overlaps the hips cleanly ────────────────
    # Front pair (toward +x / the head side) and back pair (toward -x). Short,
    # paired, tassel-tipped; the swing is the trot tell.
    hip_y = cy + 7
    _leg(surf, cx + 11, hip_y, sway, TASSELS[0], back=False)   # front-near
    _leg(surf, cx + 7,  hip_y, sway, TASSELS[1], back=False)   # front-far
    _leg(surf, cx - 9,  hip_y, sway, TASSELS[2], back=True)    # back-far
    _leg(surf, cx - 13, hip_y, sway, TASSELS[3], back=True)    # back-near

    # ── BODY — three tiered crepe-fringe bands stacked into a boxy mass ───────
    # Boxy (wide, fairly flat) so it reads as a creature's barrel, not a ball.
    # Top pink band, middle orange, lower turquoise — each fringed.
    _fringe_band(surf, cx - 1, cy - 4, 17, 7, PINK,   PINK_D,   8)   # top
    _fringe_band(surf, cx - 1, cy + 1, 17, 6, ORANGE, ORANGE_D, 8)   # middle
    _fringe_band(surf, cx - 1, cy + 6, 16, 6, TURQ,   TURQ_D,   8)   # lower

    # rounded body keyline (cream) along the TOP so the dark crepe survives a
    # bright day sky and glows against night.
    rect = pygame.Rect(cx - 1 - 17, cy - 4 - 7, 34, 14)
    pygame.draw.arc(surf, CREAM, rect, math.radians(15), math.radians(165), 2)

    # ── NECK + HEAD — stubby, upright, on the +x (front) shoulder ─────────────
    neck_x = cx + 13
    # short upright neck slab (orange crepe, fringed cream mane behind it)
    pygame.draw.polygon(surf, ORANGE, [
        (neck_x - 4, cy - 2), (neck_x + 5, cy - 9),
        (neck_x + 9, cy - 8), (neck_x + 4, cy + 3),
    ])
    pygame.draw.polygon(surf, ORANGE_D, [
        (neck_x - 4, cy - 2), (neck_x + 4, cy + 3), (neck_x - 1, cy + 2),
    ])

    # CREAM MANE — a fringed crest running up the back of the neck (the donkey
    # tell + the night keyline on the head).
    mane_pts = [(neck_x - 5, cy + 1), (neck_x - 1, cy - 10),
                (neck_x + 3, cy - 12), (neck_x + 1, cy - 4), (neck_x - 2, cy + 2)]
    pygame.draw.polygon(surf, CREAM, mane_pts)
    for k in range(4):
        my = cy - 9 + k * 3
        pygame.draw.line(surf, CREAM_D, (neck_x - 4 + k, my), (neck_x - 6 + k, my + 2), 1)

    # HEAD — a boxy crepe muzzle block tipped slightly down/forward.
    hx, hy = neck_x + 8, cy - 9
    _aaellipse(surf, PINK,  (hx, hy), 8, 6)            # head block (pink crepe)
    _aaellipse(surf, PINK_D, (hx, hy + 2), 8, 4)       # lower-jaw shadow
    # snout / muzzle tip
    _aaellipse(surf, SNOUT, (hx + 6, hy + 2), 4, 3)
    pygame.draw.circle(surf, EYE, (hx + 7, hy + 3), 1)     # nostril
    # cream keyline arc over the head top
    hrect = pygame.Rect(hx - 8, hy - 6, 16, 12)
    pygame.draw.arc(surf, CREAM, hrect, math.radians(10), math.radians(170), 2)

    # EARS — two upright nubs (the unmistakable donkey signal).
    _ear(surf, hx - 3, hy - 4, -3, CREAM)
    _ear(surf, hx + 2, hy - 5,  3, CREAM)

    # EYE — single side-profile eye with a glint.
    pygame.draw.circle(surf, EYE, (hx + 2, hy - 1), 2)
    pygame.draw.circle(surf, EYE_GLINT, (hx + 1, hy - 2), 1)

    return surf
