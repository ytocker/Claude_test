"""Concept: THE BLACK TRIANGLE (TR-3B) for `skin_ufo`.

The hard-edged counterpoint to a set full of rounded saucers. A broad flat
isosceles wedge — WIDER than tall — with three corner lights. ZERO curvature:
in pure black silhouette it must read as a triangle and nothing else, so the
instant 40px read is "black-triangle UFO", one of the most recognizable UFO
icons there is.

Signature tell (no wings, no live particles): a rotating beacon. ONE corner
lights as a hot pip while the others stay dark, and the lit pip steps around
the rim — top vertex → bottom-right → bottom-left → all-dark — so a single
light appears to chase around the triangle. The SLAB is the dark mass; the
PIP is the bright accent ON it. Pure brightness sequencing, so the tell
survives in grayscale and for colourblind players.

Round-2 correction: round 1 drew the beacons as large DARK bulbs with a brown
halo + dark contour, which fractured the wedge into "three dark knobs / a
spider" and buried the lit fleck inside a dark surround. Now each lit corner is
a tiny luminous dot (white→red core, thin warm glow) that sits INSIDE the
slab's corner, and the wedge's straight 2px keyline edge passes cleanly behind
it — the triangle outline is the dominant shape, the lights are small accents.
Unlit corners carry NO dark bulb at all.

Contract mirrors game/animal_ufo.py: build(wing_angle_deg) -> 64x84 SRCALPHA
Surface, body mass centred at (32,44), drawn UPRIGHT (no baked rotation).
"""
import math
import pygame

from game.parrot import _add_outline, _aaellipse  # noqa: F401 (parity w/ prod)


# ── canvas + anchors (mirror animal_ufo.py) ──────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY            # triangle body centre → (32, 44)

# Geometry: a broad, shallow isosceles wedge. HALF_W >> HEIGHT keeps it WIDE so
# it never reads as a generic upward arrow. The apex sits ABOVE centre and the
# base BELOW, with the body mass straddling (32,44) for the 14px collision
# circle. Corners are clipped flat (not pointed) for the stealthy slab look.
HALF_W = 27                       # half the base width  → 54px wide
APEX_DY = 14                      # apex above BCY
BASE_DY = 9                       # base below BCY
CORNER = 4                        # flat-clip length at each corner (hard slab)


# ── palette ──────────────────────────────────────────────────────────────────
# Subtle top-down body gradient (dark base → lighter top) + a high-value keyline
# on ALL edges (critical so the near-black slab survives a night sky AND so the
# straight hard edges win at play-size over the small corner lights).
HULL_TOP    = (58, 63, 74)        # #3A3F4A  lighter top of the gradient
HULL_BOT    = (35, 38, 46)        # #23262E  darker base
HULL_DARK   = (24, 26, 32)        # deepest underside shadow line
KEYLINE     = (150, 159, 175)     # #9AA3B2  high-value lip carrying the wedge
SPECULAR    = (198, 206, 220)     # one crisp machined top-edge highlight line
PANEL_LINE  = (46, 50, 60)        # faint hull seam (dropped at size; texture only)

# Corner beacons — classic government-triangle red, but the VALUE is inverted
# from round 1: a hot bright core, NOT a dark bulb. The slab is the dark.
PIP_CORE_LIT = (255, 244, 232)    # hot near-white core of the lit pip (brightest)
PIP_RING_LIT = (255, 92, 58)      # thin warm-red ring just outside the lit core
PIP_TRAIL    = (236, 120, 80)     # the trailing pip — bright warm, one step dimmer
PIP_DARK     = (40, 22, 18)       # an UNLIT corner: a tiny recessed dot, no halo
# alt CYAN colorway: PIP_RING_LIT (90,224,255); PIP_TRAIL (120,206,230)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 beacon frame. _WING_ANGLES runs 50→-40 across
    the four poses; each pose advances the lit corner one step around the rim."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _corners():
    """The three beacon anchor points, pulled well INBOARD of the true vertices
    so a tiny pip sits cleanly inside the corner of the slab and the wedge's
    straight keyline edge passes behind it. Order: 0=top apex, 1=bottom-right,
    2=bottom-left — matches the chase map."""
    apex = (BCX, BCY - APEX_DY + 5)
    br = (BCX + HALF_W - 7, BCY + BASE_DY - 3)
    bl = (BCX - HALF_W + 7, BCY + BASE_DY - 3)
    return [apex, br, bl]


def _wedge_points():
    """Outer outline of the flat wedge with corners flat-clipped, so the pure
    silhouette reads as a hard triangle yet has slightly broken (not needle)
    tips — the stealthy slab look. Corners are CLIPPED FLAT (a short straight
    bevel), never rounded, so they stay genuinely hard at 40px."""
    apex_x, apex_y = BCX, BCY - APEX_DY
    by = BCY + BASE_DY
    rx, lx = BCX + HALF_W, BCX - HALF_W
    return [
        (apex_x - CORNER, apex_y + CORNER * 0.8),   # apex, left bevel
        (apex_x + CORNER, apex_y + CORNER * 0.8),   # apex, right bevel
        (rx - CORNER, by - CORNER),                 # right shoulder up
        (rx - CORNER * 0.4, by),                    # right base corner
        (lx + CORNER * 0.4, by),                    # left base corner
        (lx + CORNER, by - CORNER),                 # left shoulder up
    ]


def _fill_gradient(surf, pts):
    """Fill the wedge with a top-down body gradient by stamping horizontal
    bands clipped to the polygon. A flat slab needs the faint vertical ramp so
    it reads as lit metal, not a sticker."""
    top_y = BCY - APEX_DY
    bot_y = BCY + BASE_DY
    span = max(1, bot_y - top_y)
    grad = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for y in range(top_y, bot_y + 1):
        t = (y - top_y) / span
        col = tuple(int(HULL_TOP[i] + (HULL_BOT[i] - HULL_TOP[i]) * t) for i in range(3))
        pygame.draw.line(grad, (*col, 255), (0, y), (COMPOSITE_W, y))
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (0, 0))


def _pip(surf, center, state):
    """A corner beacon as a BRIGHT dot on the dark slab — value inverted from
    round 1. The lit pip is the single brightest value in the craft: a 1px
    hot-white core, a 2px warm-red ring, and a thin additive glow that stays
    INSIDE the corner (radius ~3px, never a bulb that replaces the corner). An
    unlit corner is just a 1px recessed dark dot — NO dark halo, so the wedge's
    straight keyline edge keeps owning the corner.

    state: "lit" | "trail" | "dark".
    """
    cx, cy = center
    if state == "dark":
        surf.set_at((int(cx), int(cy)), (*PIP_DARK, 255))
        return

    if state == "lit":
        ring, core, glow_a, glow_r = PIP_RING_LIT, PIP_CORE_LIT, 150, 3
    else:  # trailing pip — warm and clearly bright, but a notch under the lit one
        ring, core, glow_a, glow_r = PIP_TRAIL, PIP_TRAIL, 80, 3

    # Thin additive glow, clamped small so it never blooms past the corner — the
    # slab edge must still read straight behind it. Additive on a scratch surface
    # so it can never punch a transparent hole in the slab.
    g = pygame.Surface((glow_r * 2 + 2, glow_r * 2 + 2), pygame.SRCALPHA)
    gc = glow_r + 1
    for i in range(glow_r, 0, -1):
        a = int(glow_a * (glow_r - i + 1) / glow_r * 0.5)
        pygame.draw.circle(g, (*ring, a), (gc, gc), i)
    surf.blit(g, (cx - gc, cy - gc), special_flags=pygame.BLEND_RGBA_ADD)

    # Solid bright dot: warm ring (2px radius) then a hot core on top. The lit
    # core is deliberately a hair larger + near-white so it BEATS the pale
    # keyline in grayscale and stays the single brightest value in the craft.
    pygame.draw.circle(surf, ring, (int(cx), int(cy)), 2)
    if state == "lit":
        pygame.draw.circle(surf, core, (int(cx), int(cy)), 1)
        surf.set_at((int(cx), int(cy)), (255, 255, 255, 255))


def build(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    pts = _wedge_points()
    corners = _corners()

    # Soft drop-shadow slab a touch below, so the wedge sits on the sky instead
    # of floating — and so its lower edge stays defined before the keyline.
    shadow = [(x, y + 1.5) for (x, y) in pts]
    pygame.draw.polygon(surf, (*HULL_DARK, 235), shadow)

    # Body: top-down gradient masked to the wedge → flat lit-metal slab.
    _fill_gradient(surf, pts)

    ap_l = pts[0]    # apex left bevel
    ap_r = pts[1]    # apex right bevel
    r_sh = pts[2]    # right shoulder
    rb = pts[3]      # right base corner
    lb = pts[4]      # left base corner
    l_sh = pts[5]    # left shoulder

    # High-value keyline carrying the ENTIRE wedge outline (round 1 only lit the
    # lower edges, which let the corners halo and the slab dissolve at top). A
    # near-black slab vanishes into a night sky — this pale lip holds the hard
    # triangle silhouette. Drawn 2px so the straight edges WIN over the small
    # corner pips at the 40px downscale.
    edges = [(ap_r, r_sh), (r_sh, rb), (rb, lb), (lb, l_sh), (l_sh, ap_l), (ap_l, ap_r)]
    for a, b in edges:
        pygame.draw.line(surf, KEYLINE, a, b, 2)

    # ONE crisp machined-stealth specular highlight: a single bright line along
    # the upper-left long edge, inboard of the keyline (one bright line, not a
    # gradient wash). Sells "polished metal slab" without softening any corner.
    sp_a = (ap_l[0] + 1.5, ap_l[1] + 1.5)
    sp_b = ((ap_l[0] + l_sh[0]) / 2 + 1.5, (ap_l[1] + l_sh[1]) / 2 + 1.5)
    pygame.draw.line(surf, SPECULAR, sp_a, sp_b, 1)

    # Rotating beacon. ONE corner lights at a time; the lit corner advances one
    # step per pose around the rim:
    #   ph0 → apex   ph1 → bottom-right   ph2 → bottom-left   ph3 → all dark.
    # The TRAILING corner (one step back) glows warm-but-dimmer so the eye reads
    # a single light TRAVELLING, not a blink. The lit pip is the BRIGHTEST value
    # in the craft in every frame (grayscale-safe).
    lit_idx = ph % 3
    trail_idx = (ph - 1) % 3
    for i, c in enumerate(corners):
        if ph == 3:
            _pip(surf, c, "dark")                 # all-dark pose — beacon "off"
        elif i == lit_idx:
            _pip(surf, c, "lit")
        elif i == trail_idx:
            _pip(surf, c, "trail")
        else:
            _pip(surf, c, "dark")

    return surf
