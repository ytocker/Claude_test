"""UFO Store skin REDESIGN — Round 1 exploration (5 concepts).

The current production look (matte-amber domed saucer with a chasing rim-light
ring + pulsing tractor beam) is the right DIRECTION; this module re-explores its
EXECUTION across five distinct, individually-shippable takes. Three are refined
spins on the classic DOMED SAUCER silhouette; two go bolder (a glowing scout orb
and a faceted crystal shard-craft).

This file lives under docs/ and is NEVER imported by the game. It deliberately
does NOT register any `skin_*` id in a BUILDERS dict — every concept is exposed
only as an internal `build_<name>(wing_angle_deg) -> Surface`. The render sheet
wraps each through the production cached-getter pattern so the 40px truth test
matches in-game rendering exactly.

HARD CONTRACT (shared by all five, mirrors game/animal_ufo.py):
  * 64x84 SRCALPHA canvas; dominant mass centred at BCX,BCY = (32,44) so the
    fixed 14px collision circle stays on the hull.
  * 4 baked frames from _WING_ANGLES = (50,20,-10,-40). NO wings — the "flap"
    is a baked LIFE-CYCLE animation (rim chase / beam pulse / orb throb / core
    spin / facet shimmer). NO live particles.
  * Draw UPRIGHT — velocity tilt is applied OUTSIDE via rotozoom.
  * Bold silhouette + one clear "tell" at 40px on DAY and NIGHT. Dark hulls get
    a baked high-value keyline so they survive the bright day band; glows bloom
    at night.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _aaellipse


# ── canvas + anchors (mirror animal_skins.py / animal_ufo.py) ────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # body mass centre → (32, 44)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 frame index. _WING_ANGLES runs 50→-40 across
    the four poses, so a per-frame step reads as one cyclic advance."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# ── shared baked-light primitives (adapted from animal_ufo.py) ───────────────
def _glow_dot(surf, center, r, color, *, halo=2.0, contour=(18, 12, 8),
              core=(255, 248, 230)):
    """A baked light: a soft additive halo (blooms at night) stamped to a
    scratch surface so it never punches transparent holes in the hull, plus a
    bright core and an optional dark contour that keeps it legible on a bright
    day sky and for colourblind players (no leaning on hue alone)."""
    cx, cy = center
    rad = int(r * halo) + 2
    g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    for i in range(3, 0, -1):
        a = 36 + (3 - i) * 26
        rr = int(rad * i / 3)
        pygame.draw.circle(g, (*color, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)
    if contour is not None:
        pygame.draw.circle(surf, contour, (cx, cy), r + 1)
    pygame.draw.circle(surf, color, (cx, cy), r)
    if core is not None:
        pygame.draw.circle(surf, core, (cx, cy), max(1, r - 1))


def _rim_chase(surf, cx, cy, rx, ry, n, phase, base, lit, *, contour=(16, 12, 8)):
    """A ring of n rim lights wrapped on the FRONT lip of the disc. The lit pair
    at `phase` glows bright + larger; the rest sit small + dim but visible, so
    the eye tracks the lit pair ADVANCING one notch per frame — rotation, not a
    twinkle. Lit/dim contrast (size + value + dark contour) is wide enough that
    no two adjacent dots ever read as both 'on'."""
    for i in range(n):
        t = (i + 0.5) / n
        lx = int(cx - rx + (2 * rx) * t)
        ly = int(cy + ry * (1.0 - 0.5 * abs(0.5 - t) * 2) + 1)
        d = (i - phase) % n
        if d == 0 or d == 1:
            bright = lit if d == 0 else tuple(int(c * 0.55 + 255 * 0.45) for c in lit)
            _glow_dot(surf, (lx, ly), 2, bright, halo=2.0, contour=contour)
        else:
            pygame.draw.circle(surf, contour, (lx, ly), 2)
            pygame.draw.circle(surf, base, (lx, ly), 1)


def _beam(surf, cx, top_y, width, length, color, phase, *, strength=1.0):
    """A baked downward tractor cone. PULSES with the cycle: phase 0/2 widen,
    1/3 narrow, so the beam breathes in time — the clearest 'alive' signal.
    Additive so it glows over night skies; the top rows ramp in from zero so the
    bloom never washes up over the disc's lower lip and erodes the silhouette."""
    pulse = 1.0 + (0.26 if phase % 2 == 0 else -0.10) * strength
    w = int(width * pulse)
    beam = pygame.Surface((w * 2 + 6, length + 4), pygame.SRCALPHA)
    bx = w + 3
    for i in range(length):
        t = i / length
        spread = int(w * (0.35 + 0.65 * t))
        rise = min(1.0, t / 0.30)
        a = int(96 * strength * rise * (1.0 - t) ** 1.2)
        pygame.draw.line(beam, (*color, a), (bx - spread, i), (bx + spread, i))
    for i in range(length):
        t = i / length
        spread = max(1, int(w * 0.4 * (0.3 + 0.7 * t)))
        rise = min(1.0, t / 0.30)
        a = int(64 * strength * rise * (1.0 - t))
        pygame.draw.line(beam, (255, 255, 255, a), (bx - spread, i), (bx + spread, i))
    surf.blit(beam, (cx - bx, top_y), special_flags=pygame.BLEND_RGBA_ADD)


def _keyline_arc(surf, cx, cy, rx, ry, color, width=2):
    """A 1-2px high-value lip along the UPPER edge of an ellipse. Drawn as an
    arc so only the top rim catches the 'light' — the cue that survives a bright
    sky and sells the disc as a hard-edged shape rather than a soft blob."""
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    pygame.draw.arc(surf, color, rect, math.radians(20), math.radians(160), width)


def _lerp(a, b, t):
    # clamp: some gradients drive t slightly past [0,1] (e.g. t**0.7 at the
    # equator) which would otherwise overshoot a channel past 255.
    return tuple(max(0, min(255, int(a[i] + (b[i] - a[i]) * t))) for i in range(3))


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 1 · CHROME CLASSIC
#   A polished mirror-chrome saucer: cool steel hull with a baked sky-reflection
#   gradient band (the chrome 'tell'), a tight cyan glass dome, and a crisp WHITE
#   rim chase. The most premium, showroom-clean read of the classic silhouette.
# ═════════════════════════════════════════════════════════════════════════════
C1_HULL_DARK  = (40, 50, 66)
C1_HULL_MID   = (120, 140, 162)
C1_HULL_HI    = (224, 236, 248)     # mirror highlight band
C1_HULL_LO    = (58, 70, 90)        # chrome shadow under the equator
C1_KEYLINE    = (245, 250, 255)
C1_RIM_DIM    = (70, 96, 120)
C1_RIM_LIT    = (235, 250, 255)
C1_DOME_GLASS = (150, 220, 245)
C1_DOME_DEEP  = (40, 110, 150)
C1_DOME_RING  = (70, 92, 116)
C1_GLINT      = (255, 255, 255)
C1_BEAM       = (170, 230, 255)


def build_chrome(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 26, 9

    _beam(surf, BCX, BCY + 4, 14, 28, C1_BEAM, ph, strength=0.95)

    # Underside + body, then a horizontal mirror gradient: dark top → bright
    # equator highlight → dark belly, the unmistakable chrome read.
    _aaellipse(surf, C1_HULL_LO, (BCX, BCY + 3), rx, ry + 1)
    for row in range(-ry, ry + 1):
        t = (row + ry) / (2 * ry)
        # double-peaked value: bright equator band, darker top & belly
        v = 1.0 - abs(t - 0.42) * 2.0
        v = max(0.0, min(1.0, v))
        col = _lerp(C1_HULL_DARK, C1_HULL_HI, v ** 1.3)
        span = rx * math.sqrt(max(0.0, 1.0 - (row / ry) ** 2))
        pygame.draw.line(surf, col, (BCX - span, BCY + row), (BCX + span, BCY + row))
    # crisp bright equator streak (the mirror line)
    pygame.draw.line(surf, C1_HULL_HI, (BCX - rx + 6, BCY - 1), (BCX + rx - 6, BCY - 1), 1)

    _keyline_arc(surf, BCX, BCY - 1, rx - 1, ry, C1_KEYLINE)
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C1_RIM_DIM, C1_RIM_LIT,
               contour=(28, 36, 50))

    # tight cyan glass dome with a deep gradient + a hard specular glint
    dome_rx, dome_ry, dy = 11, 9, BCY - 8
    _aaellipse(surf, C1_DOME_RING, (BCX, dy + 1), dome_rx, dome_ry)
    for row in range(-dome_ry, 2):
        t = (row + dome_ry) / dome_ry
        col = _lerp(C1_DOME_DEEP, C1_DOME_GLASS, t ** 0.8)
        span = (dome_rx - 1) * math.sqrt(max(0.0, 1.0 - (row / dome_ry) ** 2))
        pygame.draw.line(surf, col, (BCX - span, dy + row), (BCX + span, dy + row))
    _aaellipse(surf, C1_GLINT, (BCX - 4, dy - 4), 3, 2)
    pygame.draw.line(surf, C1_KEYLINE, (BCX - dome_rx + 4, dy - dome_ry + 3),
                     (BCX + dome_rx - 4, dy - dome_ry + 3), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 2 · EMBER DRIFTER
#   A hand-built copper-plated saucer: warm bronze riveted hull panels, a deep
#   amber-orange glass dome over a glowing core, an amber rim chase, and an
#   ember tractor beam. Warmer, more crafted and 'lived-in' than the matte
#   production amber — a steampunk-tinged classic.
# ═════════════════════════════════════════════════════════════════════════════
C2_HULL_DARK  = (58, 30, 14)
C2_HULL_MID   = (150, 86, 38)
C2_HULL_HI    = (224, 158, 86)
C2_PANEL_LINE = (40, 20, 10)
C2_RIVET      = (255, 214, 150)
C2_KEYLINE    = (255, 220, 150)
C2_RIM_DIM    = (96, 52, 18)
C2_RIM_LIT    = (255, 176, 70)
C2_DOME_GLASS = (255, 158, 64)
C2_DOME_DEEP  = (120, 48, 16)
C2_DOME_CORE  = (255, 232, 150)
C2_RING       = (92, 50, 22)
C2_BEAM       = (255, 168, 80)


def build_ember(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 26, 10

    _beam(surf, BCX, BCY + 4, 15, 30, C2_BEAM, ph, strength=1.1)

    _aaellipse(surf, C2_HULL_DARK, (BCX, BCY + 3), rx, ry + 1)
    # bronze body with a top-lit vertical gradient (warm metal sheen)
    for row in range(-ry, ry + 1):
        t = (row + ry) / (2 * ry)
        col = _lerp(C2_HULL_HI, C2_HULL_DARK, t ** 0.85)
        span = rx * math.sqrt(max(0.0, 1.0 - (row / ry) ** 2))
        pygame.draw.line(surf, col, (BCX - span, BCY + row), (BCX + span, BCY + row))
    # riveted panel seams radiating from centre (hand-built plates)
    for i in range(6):
        ang = math.radians(-160 + i * 28)
        x2 = BCX + math.cos(ang) * (rx - 2)
        y2 = BCY + math.sin(ang) * (ry - 1) * 0.6
        pygame.draw.line(surf, C2_PANEL_LINE, (BCX, BCY - 2), (x2, y2), 1)
    # a row of warm rivets along the upper shoulder
    for i in range(7):
        t = (i + 0.5) / 7
        rxp = int(BCX - (rx - 6) + (2 * (rx - 6)) * t)
        ryp = int(BCY - ry * 0.55)
        pygame.draw.circle(surf, C2_RIVET, (rxp, ryp), 1)

    _keyline_arc(surf, BCX, BCY - 1, rx - 1, ry, C2_KEYLINE)
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C2_RIM_DIM, C2_RIM_LIT,
               contour=(30, 16, 8))

    # amber dome over a glowing core that brightens on the wide-beam frames
    dome_rx, dome_ry, dy = 12, 9, BCY - 8
    _aaellipse(surf, C2_RING, (BCX, dy + 1), dome_rx, dome_ry)
    _aaellipse(surf, C2_DOME_GLASS, (BCX, dy), dome_rx - 1, dome_ry - 1)
    _aaellipse(surf, C2_DOME_DEEP, (BCX, dy + 2), 5, 4)
    core_r = 3 if ph % 2 == 0 else 2          # core throbs with the beam pulse
    _glow_dot(surf, (BCX, dy + 1), core_r, C2_DOME_CORE, halo=2.2,
              contour=None, core=(255, 248, 220))
    pygame.draw.line(surf, C2_KEYLINE, (BCX - dome_rx + 4, dy - dome_ry + 3),
                     (BCX + dome_rx - 4, dy - dome_ry + 3), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 3 · AURORA GLASS
#   A translucent iridescent saucer: an oil-slick hull that shifts teal→violet
#   across its face, a prismatic dome, and a MULTICOLOUR rim chase where the lit
#   pair cycles hue with the phase. The boldest take on the classic silhouette —
#   a high-value, jewel-like premium read that blooms hard at night.
# ═════════════════════════════════════════════════════════════════════════════
C3_HULL_A     = (44, 30, 78)        # violet edge
C3_HULL_B     = (28, 86, 110)       # teal centre
C3_HULL_C     = (96, 40, 100)       # magenta edge
C3_HULL_DARK  = (16, 14, 34)
C3_KEYLINE    = (220, 235, 255)
C3_DOME_GLASS = (180, 230, 255)
C3_DOME_DEEP  = (60, 60, 150)
C3_GLINT      = (255, 255, 255)
C3_BEAM       = (180, 200, 255)
# rim chase hue cycles per phase for the prismatic 'alive' tell
C3_RIM_HUES = ((120, 245, 255), (190, 130, 255), (120, 255, 190), (255, 150, 240))
C3_RIM_DIM  = (60, 64, 110)


def build_aurora(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 26, 9

    _beam(surf, BCX, BCY + 4, 14, 28, C3_BEAM, ph, strength=1.0)

    _aaellipse(surf, C3_HULL_DARK, (BCX, BCY + 3), rx, ry + 1)
    # oil-slick: horizontal-position-driven hue shift violet→teal→magenta, with
    # a vertical value falloff so it still reads as a domed metal disc.
    for row in range(-ry, ry + 1):
        span = rx * math.sqrt(max(0.0, 1.0 - (row / ry) ** 2))
        vy = 1.0 - (row + ry) / (2 * ry) * 0.55      # top brighter
        x0 = int(BCX - span)
        x1 = int(BCX + span)
        for x in range(x0, x1 + 1):
            u = (x - (BCX - rx)) / (2 * rx)
            if u < 0.5:
                base = _lerp(C3_HULL_A, C3_HULL_B, u * 2)
            else:
                base = _lerp(C3_HULL_B, C3_HULL_C, (u - 0.5) * 2)
            col = tuple(int(c * vy) for c in base)
            surf.set_at((x, BCY + row), col)
    # bright iridescent equator streak
    pygame.draw.line(surf, (200, 230, 255), (BCX - rx + 6, BCY - 1),
                     (BCX + rx - 6, BCY - 1), 1)

    _keyline_arc(surf, BCX, BCY - 1, rx - 1, ry, C3_KEYLINE)

    # multicolour rim chase: the lit pair takes this frame's hue
    lit = C3_RIM_HUES[ph]
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C3_RIM_DIM, lit,
               contour=(24, 22, 44))

    # prismatic dome
    dome_rx, dome_ry, dy = 11, 9, BCY - 8
    _aaellipse(surf, (40, 44, 96), (BCX, dy + 1), dome_rx, dome_ry)
    for row in range(-dome_ry, 2):
        t = (row + dome_ry) / dome_ry
        col = _lerp(C3_DOME_DEEP, C3_DOME_GLASS, t ** 0.7)
        span = (dome_rx - 1) * math.sqrt(max(0.0, 1.0 - (row / dome_ry) ** 2))
        pygame.draw.line(surf, col, (BCX - span, dy + row), (BCX + span, dy + row))
    # a thin prism rainbow stripe across the glass
    pygame.draw.line(surf, (255, 180, 220), (BCX - 5, dy + 1), (BCX + 5, dy - 1), 1)
    _aaellipse(surf, C3_GLINT, (BCX - 4, dy - 4), 3, 2)
    pygame.draw.line(surf, C3_KEYLINE, (BCX - dome_rx + 4, dy - dome_ry + 3),
                     (BCX + dome_rx - 4, dy - dome_ry + 3), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 4 · SCOUT ORB  (BOLD / out-there)
#   No saucer, no dome: a single glowing spherical scout drone. The dominant
#   mass is a luminous orb with a dark IRIS 'eye' that OPENS and THROBS across
#   the four frames (the life-cycle tell), wrapped by an orbiting halo ring of
#   three guard-lights that advances one notch per frame. Reads as a living
#   floating eye — alien but instantly legible at 40px.
# ═════════════════════════════════════════════════════════════════════════════
C4_ORB_CORE   = (190, 255, 240)
C4_ORB_MID    = (60, 200, 200)
C4_ORB_DEEP   = (18, 90, 110)
C4_ORB_DARK   = (8, 34, 46)
C4_IRIS       = (10, 30, 40)
C4_PUPIL      = (210, 255, 250)
C4_KEYLINE    = (220, 255, 250)
C4_RING       = (40, 150, 170)
C4_GUARD_LIT  = (210, 255, 250)
C4_GUARD_DIM  = (30, 110, 130)
C4_BEAM       = (120, 245, 235)


def build_scout(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    R = 17                                       # orb radius (the dominant mass)

    _beam(surf, BCX, BCY + R - 4, 12, 24, C4_BEAM, ph, strength=0.85)

    # soft outer aura (additive — blooms at night)
    aura = pygame.Surface((R * 4, R * 4), pygame.SRCALPHA)
    for i in range(4, 0, -1):
        a = 18 + (4 - i) * 14
        pygame.draw.circle(aura, (*C4_ORB_MID, a), (R * 2, R * 2), int(R * (0.7 + i * 0.18)))
    surf.blit(aura, (BCX - R * 2, BCY - R * 2), special_flags=pygame.BLEND_RGBA_ADD)

    # spherical body: radial value falloff, top-lit
    for row in range(-R, R + 1):
        span = math.sqrt(max(0.0, R * R - row * row))
        x0, x1 = int(BCX - span), int(BCX + span)
        for x in range(x0, x1 + 1):
            dx = x - BCX
            dy = row
            d = math.sqrt(dx * dx + dy * dy) / R
            # light from upper-left
            shade = 1.0 - 0.5 * ((dx + 4) / R) - 0.4 * ((dy + 2) / R)
            shade = max(0.0, min(1.0, shade))
            if d > 0.82:
                col = _lerp(C4_ORB_DEEP, C4_ORB_DARK, (d - 0.82) / 0.18)
            else:
                col = _lerp(C4_ORB_DEEP, C4_ORB_CORE, shade * (1.0 - d * 0.5))
            surf.set_at((x, BCY + row), col)

    # keyline rim so the dark lower hemisphere survives the bright day sky
    pygame.draw.circle(surf, C4_KEYLINE, (BCX, BCY), R, 1)
    _keyline_arc(surf, BCX, BCY, R - 1, R - 1, C4_KEYLINE, width=2)

    # IRIS eye: a dark ring whose pupil opens/throbs with the frame (the tell).
    iris_r = 9
    open_t = (0.4, 0.7, 1.0, 0.7)[ph]            # pupil dilation cycle
    pygame.draw.circle(surf, C4_IRIS, (BCX, BCY), iris_r)
    pygame.draw.circle(surf, C4_ORB_DEEP, (BCX, BCY), iris_r, 1)
    pupil_r = max(2, int(iris_r * 0.55 * open_t) + 2)
    _glow_dot(surf, (BCX, BCY), pupil_r, C4_PUPIL, halo=2.4, contour=None,
              core=(255, 255, 255))

    # orbiting halo ring of 3 guard lights — one notch advance per frame
    n = 6
    for i in range(n):
        ang = math.radians(-90 + i * (360 / n) + ph * (360 / n))
        gx = int(BCX + math.cos(ang) * (R + 3))
        gy = int(BCY + math.sin(ang) * (R + 3) * 0.5)
        if i % 2 == 0:
            _glow_dot(surf, (gx, gy), 2, C4_GUARD_LIT, halo=1.8, contour=(10, 30, 40))
        else:
            pygame.draw.circle(surf, (10, 30, 40), (gx, gy), 2)
            pygame.draw.circle(surf, C4_GUARD_DIM, (gx, gy), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 5 · CRYSTAL SHARD-CRAFT  (BOLD / out-there)
#   A faceted crystalline disc cut from flat gem planes rather than a smooth
#   hull: angular top facets in cool amethyst, a glowing core that pulses light
#   up through the crystal (the facets brighten on alternating frames), and a
#   sharp white keyline along every cut edge so the hard geometry survives a
#   bright sky. The 'tell' is the throbbing core + a chasing facet shimmer.
# ═════════════════════════════════════════════════════════════════════════════
C5_FACET_DARK = (44, 28, 70)
C5_FACET_MID  = (104, 70, 162)
C5_FACET_HI   = (176, 150, 235)
C5_EDGE       = (235, 225, 255)
C5_CORE       = (220, 180, 255)
C5_CORE_HOT   = (255, 240, 255)
C5_UNDER      = (24, 14, 40)
C5_RIM_LIT    = (210, 170, 255)
C5_RIM_DIM    = (70, 50, 110)
C5_BEAM       = (190, 150, 255)


def _facet(surf, pts, color, edge):
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, edge, pts, 1)


def build_crystal(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 26, 10
    hot = ph % 2 == 0                            # facets brighten on wide frames

    _beam(surf, BCX, BCY + 4, 14, 28, C5_BEAM, ph, strength=1.0)

    # dark crystalline underside (a shallow inverted prism)
    pygame.draw.polygon(surf, C5_UNDER, [
        (BCX - rx + 3, BCY + 1), (BCX + rx - 3, BCY + 1),
        (BCX + 8, BCY + ry), (BCX - 8, BCY + ry)])

    # faceted top disc — a fan of angular planes around a peak above centre.
    peak = (BCX, BCY - 9)
    rim = []
    seg = 8
    for i in range(seg + 1):
        ang = math.radians(180 + (i / seg) * 180)   # left→right across the top
        rim.append((BCX + math.cos(ang) * rx, BCY + math.sin(ang) * ry * 0.5 + 1))
    base_mid = _lerp(C5_FACET_MID, C5_FACET_HI, 0.35) if hot else C5_FACET_MID
    for i in range(seg):
        # alternate facet brightness; on hot frames lift the whole fan.
        if (i + ph) % 2 == 0:
            col = C5_FACET_HI if hot else base_mid
        else:
            col = base_mid if hot else C5_FACET_DARK
        _facet(surf, [peak, rim[i], rim[i + 1]], col, C5_EDGE)

    # bright cut keyline along the top ridge silhouette
    pygame.draw.line(surf, C5_EDGE, rim[0], peak, 1)
    pygame.draw.line(surf, C5_EDGE, rim[-1], peak, 1)
    _keyline_arc(surf, BCX, BCY, rx - 1, ry, C5_EDGE)

    # rim chase of facet sparks along the front edge (geometry, not lamps)
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C5_RIM_DIM, C5_RIM_LIT,
               contour=(30, 20, 50))

    # glowing core in the crystal heart that throbs with the frame
    core_r = 4 if hot else 3
    _glow_dot(surf, (BCX, BCY - 4), core_r, C5_CORE, halo=2.6, contour=None,
              core=C5_CORE_HOT)
    # a hot light shaft up the central ridge
    pygame.draw.line(surf, C5_CORE_HOT, (BCX, BCY - 2), peak, 1)
    return surf


# ── internal registry for the render sheet ONLY (not a game skin id) ─────────
CONCEPTS = (
    ("CHROME CLASSIC", build_chrome),
    ("EMBER DRIFTER", build_ember),
    ("AURORA GLASS", build_aurora),
    ("SCOUT ORB", build_scout),
    ("CRYSTAL SHARD", build_crystal),
)
