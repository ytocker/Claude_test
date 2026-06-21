"""UFO Store skin REDESIGN — Round 2 exploration (5 concepts).

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
    a baked high-value keyline around the FULL silhouette (top edge AND lower
    lip) so the craft stays ONE connected shape on the bright day band and the
    belly survives night; glows bloom at night.

ROUND 2 — applies the art-director critique:
  * Every dark hull now carries a CONTINUOUS keyline (top + lower lip), not just
    the upper arc — Crystal & Aurora no longer collapse into a black blob on the
    bright day band, and Ember/Crystal bellies survive night.
  * Every life-cycle tell is built from a VALUE/SIZE swing (not hue alone), so it
    survives a grayscale colourblind check and reads at 40px: Chrome's chase
    rides the dark lower lip with a wide lit/dim swing; Ember's core throbs hard
    and its plate seams are high-value; Scout's iris dilates from a tight pupil
    to a wide open eye; Aurora pairs every hue step with a grow step; Crystal
    runs ONE travelling bright facet + a hard core throb.
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


def _rim_chase(surf, cx, cy, rx, ry, n, phase, base, lit, *, contour=(16, 12, 8),
               lip_drop=1):
    """A ring of n rim lights wrapped on the FRONT lip of the disc. The lit pair
    at `phase` glows bright + larger; the rest sit small + dim but visible, so
    the eye tracks the lit pair ADVANCING one notch per frame — rotation, not a
    twinkle. `lip_drop` nudges the whole chase DOWN onto the darker lower lip so
    a bright equator band can't swallow it. Lit/dim contrast (size + value +
    dark contour) is wide enough that no two adjacent dots ever read as 'on'."""
    for i in range(n):
        t = (i + 0.5) / n
        lx = int(cx - rx + (2 * rx) * t)
        ly = int(cy + ry * (1.0 - 0.5 * abs(0.5 - t) * 2) + lip_drop)
        d = (i - phase) % n
        if d == 0 or d == 1:
            # Wide lit/dim swing: leading dot is biggest + brightest, trailing
            # a touch smaller — the value step alone (not hue) tracks rotation.
            if d == 0:
                _glow_dot(surf, (lx, ly), 3, lit, halo=2.2, contour=contour)
            else:
                mid = tuple(int(c * 0.55 + 255 * 0.45) for c in lit)
                _glow_dot(surf, (lx, ly), 2, mid, halo=2.0, contour=contour)
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


def _keyline_full(surf, cx, cy, rx, ry, top_col, lip_col, *, top_w=2, lip_w=1):
    """A CONTINUOUS high-value keyline around the whole disc silhouette: a bright
    top arc PLUS a fainter lower-lip arc. The art-director gate — a near-black
    hull needs an unbroken bright contour so it reads as ONE connected craft on
    the bright day band (not a crown floating over a black blob) and so the belly
    edge survives the night sky. The lower lip is dimmer than the top so the disc
    still reads as top-lit metal, but it never goes pure black."""
    rect = pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))
    # lower lip first (so the brighter top arc wins any overlap at the sides)
    pygame.draw.arc(surf, lip_col, rect, math.radians(200), math.radians(340), lip_w)
    pygame.draw.arc(surf, top_col, rect, math.radians(20), math.radians(160), top_w)


def _lerp(a, b, t):
    # clamp: some gradients drive t slightly past [0,1] (e.g. t**0.7 at the
    # equator) which would otherwise overshoot a channel past 255.
    return tuple(max(0, min(255, int(a[i] + (b[i] - a[i]) * t))) for i in range(3))


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 1 · CHROME CLASSIC
#   A polished mirror-chrome saucer: cool steel hull with a baked sky-reflection
#   gradient band (the chrome 'tell'), a tight cyan glass dome, and a crisp WHITE
#   rim chase dropped onto the DARK lower lip so the lit pair punches against the
#   bright equator. The most premium, showroom-clean read of the classic disc.
# ═════════════════════════════════════════════════════════════════════════════
C1_HULL_DARK  = (40, 50, 66)
C1_HULL_MID   = (120, 140, 162)
C1_HULL_HI    = (224, 236, 248)     # mirror highlight band
C1_HULL_LO    = (44, 54, 72)        # chrome shadow under the equator (the dark lip)
C1_KEYLINE    = (245, 250, 255)
C1_LIP        = (150, 178, 206)     # cooler, dimmer lower-lip keyline
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

    # Continuous keyline (bright top + cooler lower lip) so the whole disc reads
    # as one hard chrome shape on day AND night.
    _keyline_full(surf, BCX, BCY - 1, rx - 1, ry + 1, C1_KEYLINE, C1_LIP)
    # Chase rides the DARK lower lip (lip_drop=3) so the lit pair punches instead
    # of being swallowed by the bright equator highlight band.
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C1_RIM_DIM, C1_RIM_LIT,
               contour=(20, 28, 42), lip_drop=3)

    # tight cyan glass dome with a deep gradient + a hard OFF-AXIS specular glint
    dome_rx, dome_ry, dy = 11, 9, BCY - 8
    _aaellipse(surf, C1_DOME_RING, (BCX, dy + 1), dome_rx, dome_ry)
    for row in range(-dome_ry, 2):
        t = (row + dome_ry) / dome_ry
        col = _lerp(C1_DOME_DEEP, C1_DOME_GLASS, t ** 0.8)
        span = (dome_rx - 1) * math.sqrt(max(0.0, 1.0 - (row / dome_ry) ** 2))
        pygame.draw.line(surf, col, (BCX - span, dy + row), (BCX + span, dy + row))
    # glint pushed high-left + a faint streak tail so it reads as a REFLECTION
    # catching the sky, not a centred painted stripe.
    _aaellipse(surf, C1_GLINT, (BCX - 5, dy - 5), 3, 2)
    pygame.draw.line(surf, (210, 235, 250), (BCX - 6, dy - 3), (BCX - 1, dy - 5), 1)
    pygame.draw.line(surf, C1_KEYLINE, (BCX - dome_rx + 4, dy - dome_ry + 3),
                     (BCX + dome_rx - 4, dy - dome_ry + 3), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 2 · EMBER DRIFTER
#   A hand-built copper-plated saucer: warm bronze riveted hull with HIGH-VALUE
#   panel seams radiating from the dome (so the riveted-plate identity survives
#   40px — read plates, not a smooth shell), a deep amber dome over a core that
#   THROBS hard frame-to-frame, an amber rim chase, and an ember beam. Warmer,
#   more crafted and 'lived-in' than the matte production amber.
# ═════════════════════════════════════════════════════════════════════════════
C2_HULL_DARK  = (58, 30, 14)
C2_HULL_MID   = (150, 86, 38)
C2_HULL_HI    = (224, 158, 86)
C2_PANEL_HI   = (255, 206, 138)     # HIGH-VALUE plate seam (catches the light)
C2_PANEL_LO   = (40, 20, 10)        # shadow side of the seam
C2_RIVET      = (255, 224, 168)
C2_KEYLINE    = (255, 224, 154)
C2_LIP        = (176, 104, 48)      # warm lower-lip keyline (never pure black)
C2_RIM_DIM    = (96, 52, 18)
C2_RIM_LIT    = (255, 184, 78)
C2_DOME_GLASS = (255, 158, 64)
C2_DOME_DEEP  = (120, 48, 16)
C2_DOME_CORE  = (255, 236, 160)
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
    # Riveted PLATE seams radiating from the dome: a bright catch-light edge with
    # a 1px dark shadow beside it. Drawn as paired lines so the disc reads as
    # bolted facets/plates — the identity that has to survive 40px (a smooth
    # gradient alone collapses into the production amber). Beams differ per plate.
    for i in range(7):
        ang = math.radians(-168 + i * 28)
        x2 = BCX + math.cos(ang) * (rx - 2)
        y2 = BCY + math.sin(ang) * (ry - 1) * 0.62
        # shadow first (down-right), then the high-value seam over it
        pygame.draw.line(surf, C2_PANEL_LO, (BCX + 1, BCY - 1), (x2 + 1, y2 + 1), 1)
        pygame.draw.line(surf, C2_PANEL_HI, (BCX, BCY - 2), (x2, y2), 1)
    # a row of warm rivets along the upper shoulder (plate fasteners)
    for i in range(7):
        t = (i + 0.5) / 7
        rxp = int(BCX - (rx - 6) + (2 * (rx - 6)) * t)
        ryp = int(BCY - ry * 0.5)
        pygame.draw.circle(surf, C2_PANEL_LO, (rxp, ryp + 1), 1)
        surf.set_at((rxp, ryp), C2_RIVET)

    # Continuous keyline (bright top + warm lower lip) — belly survives night.
    _keyline_full(surf, BCX, BCY - 1, rx - 1, ry, C2_KEYLINE, C2_LIP)
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C2_RIM_DIM, C2_RIM_LIT,
               contour=(30, 16, 8), lip_drop=2)

    # Amber dome over a core that THROBS HARD: a wide bright→dim swing (r and the
    # halo step together) so the pulse — not hue — is the 40px life tell.
    dome_rx, dome_ry, dy = 12, 9, BCY - 8
    _aaellipse(surf, C2_RING, (BCX, dy + 1), dome_rx, dome_ry)
    _aaellipse(surf, C2_DOME_GLASS, (BCX, dy), dome_rx - 1, dome_ry - 1)
    _aaellipse(surf, C2_DOME_DEEP, (BCX, dy + 2), 5, 4)
    # hot (phase 0/2): big bright core; cold (1/3): small dim ember — a wide swing
    if ph % 2 == 0:
        _glow_dot(surf, (BCX, dy + 1), 4, C2_DOME_CORE, halo=2.8,
                  contour=None, core=(255, 252, 232))
    else:
        _glow_dot(surf, (BCX, dy + 1), 2, _lerp(C2_DOME_DEEP, C2_DOME_CORE, 0.4),
                  halo=1.6, contour=None, core=(255, 226, 170))
    pygame.draw.line(surf, C2_KEYLINE, (BCX - dome_rx + 4, dy - dome_ry + 3),
                     (BCX + dome_rx - 4, dy - dome_ry + 3), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 3 · AURORA GLASS
#   A translucent iridescent saucer: an oil-slick hull that shifts teal→violet
#   across its face, a prismatic dome, and a MULTICOLOUR rim chase where the lit
#   pair cycles hue AND grows with the phase (so it survives desaturation). A
#   continuous bright keyline now wraps the full silhouette so the jewel hull
#   stays one connected shape on the bright day band.
# ═════════════════════════════════════════════════════════════════════════════
C3_HULL_A     = (58, 42, 104)       # violet edge (lifted for day legibility)
C3_HULL_B     = (40, 116, 144)      # teal centre
C3_HULL_C     = (122, 56, 128)      # magenta edge
C3_HULL_DARK  = (16, 14, 34)
C3_KEYLINE    = (228, 240, 255)
C3_LIP        = (150, 168, 214)     # cool lower-lip keyline (closes the shape)
C3_DOME_GLASS = (190, 235, 255)
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
        vy = 1.0 - (row + ry) / (2 * ry) * 0.5       # top brighter
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

    # Continuous keyline: the gate fix. A bright top arc PLUS a cool lower-lip arc
    # so the translucent hull stays one connected craft on the bright day sky.
    _keyline_full(surf, BCX, BCY - 1, rx - 1, ry, C3_KEYLINE, C3_LIP)

    # Multicolour rim chase: the lit pair takes this frame's hue — and the lit
    # dot also GROWS, so a colourblind/grayscale read still tracks the rotation.
    lit = C3_RIM_HUES[ph]
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C3_RIM_DIM, lit,
               contour=(24, 22, 44), lip_drop=2)

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
# CONCEPT 4 · SCOUT ORB  (BOLD / out-there — the premium tech object)
#   No saucer, no dome: a single spherical scout DRONE. A glass-eye sphere lit
#   from the top (bright crown, DARK lower hemisphere) with a hard specular
#   hotspot high-left, a dark IRIS whose pupil DILATES across the frames (tight →
#   wide open, a blink/breathe) and two BOLD high-contrast guard lamps. Reads as
#   a drone, not a glowing pearl.
# ═════════════════════════════════════════════════════════════════════════════
C4_ORB_CORE   = (210, 255, 246)
C4_ORB_MID    = (60, 200, 200)
C4_ORB_DEEP   = (20, 96, 116)
C4_ORB_LOWER  = (10, 44, 58)        # darker LOWER hemisphere → 3D sphere read
C4_ORB_DARK   = (6, 26, 36)
C4_IRIS       = (8, 26, 36)
C4_PUPIL      = (215, 255, 250)
C4_KEYLINE    = (224, 255, 250)
C4_LIP        = (60, 150, 168)      # lower-lip keyline (closes the dark belly)
C4_SPEC       = (255, 255, 255)
C4_GUARD_LIT  = (220, 255, 250)
C4_GUARD_DIM  = (24, 90, 108)
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

    # Spherical body lit from the upper-left: a bright crown grading to a clearly
    # DARK lower hemisphere, so the orb reads as a 3D lit sphere — a drone shell,
    # not a flat glowing ball.
    for row in range(-R, R + 1):
        span = math.sqrt(max(0.0, R * R - row * row))
        x0, x1 = int(BCX - span), int(BCX + span)
        for x in range(x0, x1 + 1):
            dx = x - BCX
            dy = row
            d = math.sqrt(dx * dx + dy * dy) / R
            # vertical lift: top half bright, bottom half pushed dark
            vlift = (dy + R) / (2 * R)            # 0 top → 1 bottom
            shade = 1.0 - 0.5 * ((dx + 5) / R) - 0.95 * vlift
            shade = max(0.0, min(1.0, shade))
            if d > 0.84:
                col = _lerp(C4_ORB_LOWER, C4_ORB_DARK, (d - 0.84) / 0.16)
            elif vlift > 0.58:
                # lower hemisphere: dark teal shell
                col = _lerp(C4_ORB_DEEP, C4_ORB_LOWER, (vlift - 0.58) / 0.42)
            else:
                col = _lerp(C4_ORB_DEEP, C4_ORB_CORE, shade)
            surf.set_at((x, BCY + row), col)

    # Continuous keyline: bright top crown + a closing lower lip so the dark
    # belly hemisphere survives both the day band and night.
    _keyline_full(surf, BCX, BCY, R - 1, R - 1, C4_KEYLINE, C4_LIP, top_w=2, lip_w=2)

    # IRIS eye: a solid DARK iris disc (the eye well) whose bright PUPIL DILATES
    # with the frame — tight pupil on frame 0 → wide open on frame 2 → back, the
    # "blink/breathe" tell. The dark iris stays dominant so the read is an EYE,
    # not a bright blob; the pupil grows as a tight, contained light (size swing,
    # grayscale-safe) rather than a bloom that swallows the iris ring.
    iris_r = 10
    open_t = (0.28, 0.62, 1.0, 0.62)[ph]         # pupil dilation cycle
    _aaellipse(surf, C4_IRIS, (BCX, BCY + 1), iris_r, iris_r - 1)
    pygame.draw.circle(surf, C4_ORB_DEEP, (BCX, BCY + 1), iris_r, 1)
    pupil_r = max(2, int(2 + (iris_r - 3) * open_t))
    # contained pupil: small halo + a hard bright disc, no wide bloom
    _glow_dot(surf, (BCX, BCY + 1), pupil_r, C4_PUPIL, halo=1.5, contour=None,
              core=(255, 255, 255))

    # Hard specular hotspot high-left on the GLASS shell (above the iris) — the
    # "glass eye" premium read that sells it as a polished drone lens.
    _aaellipse(surf, C4_SPEC, (BCX - 8, BCY - 9), 3, 2)
    surf.set_at((BCX - 9, BCY - 10), (255, 255, 255))

    # Two BOLD high-contrast guard lamps (3px lit) that swap sides per frame, so
    # they actually read at 40px instead of vanishing as a faint ring.
    side = 1 if ph % 2 == 0 else -1
    for s in (side, -side):
        gx = BCX + s * (R + 1)
        gy = BCY - 2
        if s == side:
            _glow_dot(surf, (gx, gy), 3, C4_GUARD_LIT, halo=2.2, contour=(8, 26, 36))
        else:
            pygame.draw.circle(surf, (8, 26, 36), (gx, gy), 2)
            pygame.draw.circle(surf, C4_GUARD_DIM, (gx, gy), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# CONCEPT 5 · CRYSTAL SHARD-CRAFT  (BOLD / out-there)
#   A faceted crystalline disc cut from flat gem planes. The glowing CORE is now
#   the primary tell — it throbs HARD frame-to-frame — and instead of every facet
#   flickering (which read as noise) a SINGLE bright facet highlight travels one
#   step around the crown per frame. A continuous bright keyline wraps the whole
#   silhouette (top ridges + lower lip) so the hard geometry survives a bright
#   sky as one connected shape, not a bright crown over a black blob.
# ═════════════════════════════════════════════════════════════════════════════
C5_FACET_DARK = (52, 34, 82)
C5_FACET_MID  = (104, 72, 162)
C5_FACET_HI   = (196, 168, 248)     # the one travelling lit facet
C5_EDGE       = (236, 226, 255)
C5_LIP        = (186, 164, 226)     # lower-lip keyline (closes the belly)
C5_CORE       = (224, 188, 255)
C5_CORE_HOT   = (255, 244, 255)
C5_UNDER      = (28, 18, 48)
C5_RIM_LIT    = (214, 178, 255)
C5_RIM_DIM    = (70, 50, 110)
C5_BEAM       = (190, 150, 255)


def _facet(surf, pts, color, edge):
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, edge, pts, 1)


def build_crystal(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 26, 10

    _beam(surf, BCX, BCY + 4, 14, 28, C5_BEAM, ph, strength=1.0)

    # dark crystalline underside (a shallow inverted prism). The two lower cut
    # edges get a bright keyline so the belly POINT survives the day band — the
    # ellipse lip-arc alone can't trace this trapezoid's hard lower silhouette.
    under = [(BCX - rx + 3, BCY + 1), (BCX + rx - 3, BCY + 1),
             (BCX + 8, BCY + ry), (BCX - 8, BCY + ry)]
    pygame.draw.polygon(surf, C5_UNDER, under)
    pygame.draw.line(surf, C5_LIP, under[1], under[2], 1)   # right cut edge
    pygame.draw.line(surf, C5_LIP, under[0], under[3], 1)   # left cut edge
    pygame.draw.line(surf, C5_LIP, under[3], under[2], 1)   # belly edge

    # faceted top disc — a fan of angular planes around a peak above centre.
    peak = (BCX, BCY - 9)
    rim = []
    seg = 8
    for i in range(seg + 1):
        ang = math.radians(180 + (i / seg) * 180)   # left→right across the top
        rim.append((BCX + math.cos(ang) * rx, BCY + math.sin(ang) * ry * 0.5 + 1))
    # ONE bright facet travels one step per frame (a moving catch-light, not an
    # all-over shimmer that reads as flicker/noise). The rest alternate mid/dark
    # as static cut geometry.
    lit_facet = (ph * 2) % seg
    for i in range(seg):
        if i == lit_facet or i == (lit_facet + 1) % seg:
            col = C5_FACET_HI
        else:
            col = C5_FACET_MID if i % 2 == 0 else C5_FACET_DARK
        _facet(surf, [peak, rim[i], rim[i + 1]], col, C5_EDGE)

    # bright cut keyline along the top ridge silhouette
    pygame.draw.line(surf, C5_EDGE, rim[0], peak, 1)
    pygame.draw.line(surf, C5_EDGE, rim[-1], peak, 1)
    # Continuous keyline: bright top ridge + a closing lower lip so the faceted
    # disc reads as ONE connected gem on the bright day band and at night.
    _keyline_full(surf, BCX, BCY, rx - 1, ry, C5_EDGE, C5_LIP)

    # rim chase of facet sparks along the front edge (geometry, not lamps)
    _rim_chase(surf, BCX, BCY, rx - 4, ry, 8, ph, C5_RIM_DIM, C5_RIM_LIT,
               contour=(30, 20, 50), lip_drop=2)

    # glowing core in the crystal heart — the PRIMARY tell, throbbing HARD.
    if ph % 2 == 0:
        _glow_dot(surf, (BCX, BCY - 4), 5, C5_CORE, halo=2.9, contour=None,
                  core=C5_CORE_HOT)
        pygame.draw.line(surf, C5_CORE_HOT, (BCX, BCY - 2), peak, 1)
    else:
        _glow_dot(surf, (BCX, BCY - 4), 2, _lerp(C5_UNDER, C5_CORE, 0.5),
                  halo=1.6, contour=None, core=C5_CORE)
    return surf


# ── internal registry for the render sheet ONLY (not a game skin id) ─────────
CONCEPTS = (
    ("CHROME CLASSIC", build_chrome),
    ("EMBER DRIFTER", build_ember),
    ("AURORA GLASS", build_aurora),
    ("SCOUT ORB", build_scout),
    ("CRYSTAL SHARD", build_crystal),
)
