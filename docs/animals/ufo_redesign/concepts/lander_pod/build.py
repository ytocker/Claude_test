"""LANDER POD concept — `skin_ufo` redesign.

A stout three-legged Apollo-style descent capsule hovering on stubby splayed
landing struts. The identity is the SILHOUETTE: a rounded trapezoid body (wide
flat top, narrower base) standing on THREE short A-frame legs that poke out
below, with footpads. Nothing else in the set has feet — the legs + the negative
space under the body ARE the read at 40px.

The motion tell is a single round porthole "eye" on the body that DILATES and
BRIGHTENS across the 4 life-cycle frames (small dark dot → wide bright bloom),
as if the pod is spinning up to lift off. The legs stay STATIC across all four
frames so the silhouette never wobbles, and the tell is a VALUE pop (dark dot vs
bright bloom) so it survives grayscale — not a hue shift.

Contract mirrors game/animal_ufo.py: build(wing_angle_deg) -> 64x84 SRCALPHA
Surface, body mass centred at (32,44), drawn UPRIGHT (no baked rotation). The 4
poses come from _WING_ANGLES=(50,20,-10,-40); the angle maps to porthole phase.
"""
import math
import pygame

from game.parrot import _aaellipse


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY            # body centre → (32, 44)

# Body trapezoid: wide flat TOP, narrower base. Half-widths + half-height.
# Kept compact so legs read at 40px without the body swallowing the frame.
TOP_HALF = 17                    # half-width of the wide flat top
BOT_HALF = 11                    # half-width of the narrower base
BODY_HALF_H = 13                 # half-height of the body block
TOP_Y = BCY - BODY_HALF_H        # y of the flat top edge
BOT_Y = BCY + BODY_HALF_H        # y of the base edge (legs hang below this)


# ── warm-metal palette ───────────────────────────────────────────────────────
# Body reads as brushed warm metal; legs + footpads are near-black struts that
# carry the "it has feet" read against a bright day band. Porthole runs from a
# dark dot to a hot amber bloom.
BODY_TOP   = (201, 205, 214)     # #C9CDD6 lit upper hull
BODY_MID   = (150, 158, 170)     # mid transition band
BODY_BASE  = (122, 130, 144)     # #7A8290 shaded base
BODY_DARK  = ( 86,  92, 104)     # deepest shade under the base lip
HULL_SEAM  = ( 96, 102, 114)     # panel seam lines
LEG_DARK   = ( 43,  48,  56)     # #2B3038 leg struts / footpads
LEG_EDGE   = ( 24,  27,  33)     # darker strut core for chunk
KEYLINE    = (238, 242, 250)     # baked high-value top lip (survives day sky)

PORT_RING  = ( 58,  62,  72)     # dark porthole bezel (always present)
PORT_GOLD  = (255, 210,  74)     # #FFD24A porthole glow
PORT_HOT   = (255, 243, 176)     # #FFF3B0 hot centre at full dilation

RCS_METAL  = (170, 176, 188)     # little thruster-quad nub highlights


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """_WING_ANGLES runs 50→-40 over the 4 poses; map to a 0..3 dilation step
    so the porthole opens up one notch per frame (powering up to lift)."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _body_polygon():
    """Rounded trapezoid outline points (wide flat top, narrower base). The
    corners are clipped so the shape reads stout + machined, not a sharp wedge."""
    c = 4   # corner clip
    return [
        (BCX - TOP_HALF + c, TOP_Y),
        (BCX + TOP_HALF - c, TOP_Y),
        (BCX + TOP_HALF,     TOP_Y + c),
        (BCX + BOT_HALF,     BOT_Y - c),
        (BCX + BOT_HALF - c, BOT_Y),
        (BCX - BOT_HALF + c, BOT_Y),
        (BCX - BOT_HALF,     BOT_Y - c),
        (BCX - TOP_HALF,     TOP_Y + c),
    ]


def _leg(surf, foot_x, foot_y, hip_x, hip_y):
    """One chunky splayed A-frame leg: two struts from two hip anchors down to a
    shared footpad, plus a round footpad. Struts are ≥3px so they survive 40px;
    legs are baked identically in every frame so the silhouette never wobbles."""
    # outer + inner strut of the A-frame, both anchored under the base lip
    pygame.draw.line(surf, LEG_DARK, (hip_x, hip_y), (foot_x, foot_y), 4)
    pygame.draw.line(surf, LEG_DARK, (BCX, hip_y - 1), (foot_x, foot_y), 3)
    # darker core seam down the main strut for a machined read
    pygame.draw.line(surf, LEG_EDGE, (hip_x, hip_y), (foot_x, foot_y), 1)
    # round footpad — the "foot" that nothing else in the set has
    pygame.draw.circle(surf, LEG_EDGE, (foot_x, foot_y), 4)
    pygame.draw.circle(surf, LEG_DARK, (foot_x, foot_y), 3)
    pygame.draw.circle(surf, RCS_METAL, (foot_x - 1, foot_y - 1), 1)


def _porthole(surf, cx, cy, phase):
    """The single round porthole 'eye'. Across phase 0→3 it DILATES (radius
    grows) and BRIGHTENS (dark dot → hot bloom). A constant dark bezel keeps it
    legible against the bright day sky; at higher phases an additive halo blooms
    (strongest at night). The value swing is large so it survives grayscale."""
    # dilation: pupil radius and brightness both ramp with phase
    t = phase / 3.0
    bezel_r = 6
    # always-present dark bezel ring (the dark porthole read on day)
    pygame.draw.circle(surf, (30, 33, 40), (cx, cy), bezel_r + 1)
    pygame.draw.circle(surf, PORT_RING, (cx, cy), bezel_r)

    pupil_r = int(round(1 + 4 * t))          # 1px dot → 5px wide aperture
    # blend the lit core colour from amber toward hot white as it opens
    core = tuple(int(PORT_GOLD[i] + (PORT_HOT[i] - PORT_GOLD[i]) * t)
                 for i in range(3))

    if phase == 0:
        # closed: a small dark pupil sitting in the bezel (the "off" state)
        pygame.draw.circle(surf, (22, 24, 30), (cx, cy), 2)
        pygame.draw.circle(surf, (70, 74, 86), (cx - 1, cy - 1), 1)
        return

    # additive bloom halo — grows with phase, blooms hardest at night
    halo_r = int(round(bezel_r * (1.0 + 1.4 * t)))
    g = pygame.Surface((halo_r * 2 + 2, halo_r * 2 + 2), pygame.SRCALPHA)
    gc = halo_r + 1
    for i in range(3, 0, -1):
        a = int((34 + (3 - i) * 30) * t)
        pygame.draw.circle(g, (*core, a), (gc, gc), int(halo_r * i / 3))
    surf.blit(g, (cx - gc, cy - gc), special_flags=pygame.BLEND_RGBA_ADD)

    # solid lit aperture + a hot pip so the centre always has a crisp value peak
    pygame.draw.circle(surf, core, (cx, cy), pupil_r)
    pygame.draw.circle(surf, PORT_HOT, (cx, cy), max(1, pupil_r - 2))
    # tiny dark catch-light keeps it reading as glass, not a flat disc
    pygame.draw.circle(surf, (120, 96, 30), (cx + pupil_r - 1, cy + 1),
                       max(1, pupil_r // 3))


def build(wing_angle_deg):
    """Return the 64x84 upright LANDER POD frame for one of the 4 poses."""
    surf = _new()
    ph = _phase(wing_angle_deg)

    # ── LEGS FIRST so the body overlaps their hips (clean "sitting on" read) ──
    # Three splayed legs: two front (left/right) + one centre poking forward,
    # all static. Footpads sit below the base so the negative space under the
    # body is unmistakably "a lander standing on feet".
    foot_y = BOT_Y + 13
    hip_y = BOT_Y - 2
    # left + right A-frames splay outward; the centre leg drops nearly straight
    _leg(surf, BCX - 17, foot_y, BCX - BOT_HALF + 2, hip_y)
    _leg(surf, BCX + 17, foot_y, BCX + BOT_HALF - 2, hip_y)
    # centre strut + its own pad, slightly forward/lower for a tripod read
    pygame.draw.line(surf, LEG_DARK, (BCX, hip_y - 1), (BCX, foot_y + 1), 4)
    pygame.draw.line(surf, LEG_EDGE, (BCX, hip_y - 1), (BCX, foot_y + 1), 1)
    pygame.draw.circle(surf, LEG_EDGE, (BCX, foot_y + 1), 4)
    pygame.draw.circle(surf, LEG_DARK, (BCX, foot_y + 1), 3)
    pygame.draw.circle(surf, RCS_METAL, (BCX - 1, foot_y), 1)

    # ── BODY — rounded trapezoid, vertical metal gradient (lit top → dark base) ─
    poly = _body_polygon()
    # soft drop shadow behind the base for a touch of depth
    pygame.draw.polygon(surf, (60, 64, 74),
                        [(x, y + 2) for (x, y) in poly])

    # vertical gradient fill clipped to the trapezoid: bright top → shaded base
    span = BOT_Y - TOP_Y
    for y in range(TOP_Y, BOT_Y + 1):
        u = (y - TOP_Y) / max(1, span)
        if u < 0.5:
            k = u / 0.5
            col = tuple(int(BODY_TOP[i] + (BODY_MID[i] - BODY_TOP[i]) * k)
                        for i in range(3))
        else:
            k = (u - 0.5) / 0.5
            col = tuple(int(BODY_MID[i] + (BODY_BASE[i] - BODY_MID[i]) * k)
                        for i in range(3))
        half = TOP_HALF + (BOT_HALF - TOP_HALF) * u
        pygame.draw.line(surf, col, (BCX - half, y), (BCX + half, y))

    # dark base lip so the body visually "sits" on the legs
    pygame.draw.line(surf, BODY_DARK, (BCX - BOT_HALF, BOT_Y),
                     (BCX + BOT_HALF, BOT_Y), 2)

    # two horizontal panel seams across the hull (machined descent-stage read)
    pygame.draw.line(surf, HULL_SEAM, (BCX - TOP_HALF + 3, TOP_Y + 7),
                     (BCX + TOP_HALF - 3, TOP_Y + 7), 1)
    pygame.draw.line(surf, HULL_SEAM, (BCX - 13, BCY + 3),
                     (BCX + 13, BCY + 3), 1)

    # tiny RCS thruster nubs on the upper shoulders (sci-fi descent-stage detail)
    for sx in (BCX - TOP_HALF + 1, BCX + TOP_HALF - 1):
        pygame.draw.circle(surf, BODY_DARK, (sx, TOP_Y + 3), 2)
        pygame.draw.circle(surf, RCS_METAL, (sx, TOP_Y + 2), 1)

    # ── baked high-value KEYLINE on the flat top edge (survives bright day) ──
    pygame.draw.line(surf, KEYLINE, (BCX - TOP_HALF + 4, TOP_Y),
                     (BCX + TOP_HALF - 4, TOP_Y), 2)
    # short lit chamfers down the upper corners so the metal edge reads hard
    pygame.draw.line(surf, KEYLINE, (BCX - TOP_HALF, TOP_Y + 4),
                     (BCX - TOP_HALF + 4, TOP_Y), 1)
    pygame.draw.line(surf, KEYLINE, (BCX + TOP_HALF, TOP_Y + 4),
                     (BCX + TOP_HALF - 4, TOP_Y), 1)

    # ── PORTHOLE TELL — round 'eye' on the body, AT/above centre (the parcel
    # hangs just below centre in play, so keep it high so the tell stays clear).
    _porthole(surf, BCX, BCY - 3, ph)

    return surf
