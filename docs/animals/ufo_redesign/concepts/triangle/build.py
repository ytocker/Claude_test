"""Concept: THE BLACK TRIANGLE (TR-3B) for `skin_ufo`.

The hard-edged counterpoint to a set full of rounded saucers. A broad flat
isosceles wedge — WIDER than tall — with three corner lights. ZERO curvature:
in pure black silhouette it must read as a triangle and nothing else, so the
instant 40px read is "black-triangle UFO", one of the most recognizable UFO
icons there is.

Signature tell (no wings, no live particles): a rotating beacon. The three
corner lights cycle which one is brightest around the rim — top vertex →
bottom-right → bottom-left → all-dim bloom — so a single light appears to chase
around the triangle. Pure brightness sequencing, so the tell survives in
grayscale and for colourblind players.

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
CORNER = 4                        # flat-clip length at each corner (rounded read)


# ── palette ──────────────────────────────────────────────────────────────────
# Subtle top-down body gradient (dark base → lighter top) + a high-value keyline
# on the LOWER edges (critical so the near-black slab survives a night sky).
HULL_TOP    = (58, 63, 74)        # #3A3F4A  lighter top of the gradient
HULL_BOT    = (35, 38, 46)        # #23262E  darker base
HULL_DARK   = (24, 26, 32)        # deepest underside shadow line
KEYLINE     = (154, 163, 178)     # #9AA3B2  high-value lip on the LOWER edges
PANEL_LINE  = (46, 50, 60)        # faint hull seam (breaks the flat mass subtly)

# Corner beacons — classic government-triangle red.
LIGHT_HUE   = (232, 71, 44)       # #E8472C
DOT_DIM     = (96, 30, 20)        # unlit corner dot
DOT_LIT     = (255, 96, 64)       # lit corner dot (brightest in the chase)
DOT_MID     = (190, 58, 40)       # partially-lit (the trailing corner)
# alt CYAN colorway: LIGHT_HUE (79,227,255); DOT_DIM (20,72,86);
#                    DOT_LIT (150,240,255); DOT_MID (52,168,200)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 beacon frame. _WING_ANGLES runs 50→-40 across
    the four poses; each pose advances the lit corner one step around the rim."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _corners():
    """The three beacon anchor points, clipped slightly inboard of the true
    vertices so the lights sit ON the slab rather than floating off its tips.
    Order: 0=top apex, 1=bottom-right, 2=bottom-left — matches the chase map."""
    apex = (BCX, BCY - APEX_DY + 3)
    br = (BCX + HALF_W - 5, BCY + BASE_DY - 2)
    bl = (BCX - HALF_W + 5, BCY + BASE_DY - 2)
    return [apex, br, bl]


def _wedge_points():
    """Outer outline of the flat wedge with corners flat-clipped, so the pure
    silhouette reads as a hard triangle yet has slightly broken (not needle)
    tips — the stealthy slab look."""
    apex_x, apex_y = BCX, BCY - APEX_DY
    by = BCY + BASE_DY
    rx, lx = BCX + HALF_W, BCX - HALF_W
    # Clip each of the three corners with a short bevel for rounded-slab read.
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
    # Build the gradient on a scratch surface, then mask it to the wedge shape.
    grad = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    for y in range(top_y, bot_y + 1):
        t = (y - top_y) / span
        col = tuple(int(HULL_TOP[i] + (HULL_BOT[i] - HULL_TOP[i]) * t) for i in range(3))
        pygame.draw.line(grad, (*col, 255), (0, y), (COMPOSITE_W, y))
    mask = pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)
    pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grad, (0, 0))


def _glow_dot(surf, center, r, color, *, halo=2.2, lit=True):
    """A baked corner beacon: a soft additive halo (blooms at night) + a solid
    core. Stamped to a scratch surface so the additive bloom never punches
    transparent holes in the slab. A dark contour keeps the dot legible on a
    bright day sky and in grayscale (the chase can't lean on hue alone)."""
    cx, cy = center
    rad = int(r * halo) + 2
    g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    bloom = 1.0 if lit else 0.42
    for i in range(3, 0, -1):
        a = int((34 + (3 - i) * 30) * bloom)
        rr = int(rad * i / 3)
        pygame.draw.circle(g, (*color, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, (14, 8, 6), (cx, cy), r + 1)        # contour
    pygame.draw.circle(surf, color, (cx, cy), r)
    if lit:                          # a hot white pip so the lit corner reads brightest
        pygame.draw.circle(surf, (255, 232, 214), (cx, cy), max(1, r - 1))


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

    # Faint hull seam from apex to base centre + a cross seam — three flat
    # panels — to break the dead-flat mass without adding curvature.
    apex = (BCX, BCY - APEX_DY + CORNER)
    base_mid = (BCX, BCY + BASE_DY - 2)
    pygame.draw.line(surf, PANEL_LINE, apex, base_mid, 1)
    pygame.draw.line(surf, PANEL_LINE,
                     (BCX - HALF_W + 9, BCY + 1), (BCX + HALF_W - 9, BCY + 1), 1)

    # High-value keyline on the LOWER edges only (apex→right-base, apex→left-base
    # are upper edges; the two long lower edges and the base catch the lip). A
    # near-black slab vanishes into a night sky — this pale lip holds the hard
    # triangle silhouette. Drawn thick (2px) so it survives the 40px downscale.
    rb = pts[3]      # right base corner
    lb = pts[4]      # left base corner
    r_sh = pts[2]    # right shoulder
    l_sh = pts[5]    # left shoulder
    ap_r = pts[1]    # apex right bevel
    ap_l = pts[0]    # apex left bevel
    pygame.draw.line(surf, KEYLINE, ap_r, r_sh, 2)   # right long edge
    pygame.draw.line(surf, KEYLINE, r_sh, rb, 2)     # right shoulder bevel
    pygame.draw.line(surf, KEYLINE, rb, lb, 2)       # base
    pygame.draw.line(surf, KEYLINE, lb, l_sh, 2)     # left shoulder bevel
    pygame.draw.line(surf, KEYLINE, l_sh, ap_l, 2)   # left long edge

    # Rotating beacon. The lit corner advances one step per pose around the rim:
    #   ph0 → apex   ph1 → bottom-right   ph2 → bottom-left   ph3 → all dim/bloom.
    # The TRAILING corner (one step back) glows mid-bright so the eye reads a
    # single light TRAVELLING, not a blink.
    lit_idx = ph % 3
    trail_idx = (ph - 1) % 3
    for i, c in enumerate(corners):
        if ph == 3:
            _glow_dot(surf, c, 3, LIGHT_HUE, halo=2.6, lit=False)   # all-dim bloom pose
        elif i == lit_idx:
            _glow_dot(surf, c, 3, DOT_LIT, halo=2.6, lit=True)
        elif i == trail_idx:
            _glow_dot(surf, c, 3, DOT_MID, halo=2.0, lit=False)
        else:
            _glow_dot(surf, c, 2, DOT_DIM, halo=1.6, lit=False)

    return surf
