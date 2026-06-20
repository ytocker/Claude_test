"""Candidate UFO Store skin — round-1 exploration (5 variants).

A secret ultra-premium NON-creature flyer: the player's flapping bird becomes
a domed alien saucer. There are NO wings — the "flap" is reinterpreted as a
CHASING RIM-LIGHT CYCLE: the ring of lights around the disc rim lights up in
sequence across the 4 base poses, and the tractor beam pulses, giving the craft
life without a wing-beat.

Contract (mirrors game/animal_skins.py so the winner lifts straight into a
production game/animal_ufo.py):

  * `build_<name>(wing_angle_deg) -> pygame.Surface`  one flat frame on a
    64x84 SRCALPHA canvas; saucer body mass centred at (32,44).
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {label: getter}` registry at the bottom.

North star: one bold silhouette (domed saucer disc) + one tell (the glowing
rim-light ring). Reads at 40px on day AND night, struck most at night where
the baked glow blooms. SPECTACLE is baked into the 4 frames — no live
particles.
"""
import math
import pygame

from game.parrot import _WING_ANGLES, _add_outline, _aaellipse


# ── canvas + anchors (mirror animal_skins.py) ────────────────────────────────
COMPOSITE_W = 64
COMPOSITE_H = 84
DY = 12
BCX, BCY = 32, 32 + DY          # saucer body centre → (32, 44)
DOME_Y = BCY - 9                # dome sits just above the disc


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter, mirroring the
    production factory: lazy 4-frame build + per-(frame, 3°) rotation cache,
    each frame outlined with the house silhouette outline."""
    state = {"frames": None, "rot": {}}

    def getter(frame_idx, tilt_deg):
        if state["frames"] is None:
            state["frames"] = [_add_outline(build_fn(a)) for a in _WING_ANGLES]
        frames = state["frames"]
        frame_idx %= len(frames)
        key = (frame_idx, int(round(tilt_deg / 3.0)) * 3)
        s = state["rot"].get(key)
        if s is None:
            s = pygame.transform.rotozoom(frames[frame_idx], key[1], 1.0)
            state["rot"][key] = s
        return s

    return getter


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle to a 0..3 frame index (the chase step). _WING_ANGLES
    runs 50→-40 across the four poses, so the lights advance one notch per
    pose and the cycle reads as motion."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _glow_dot(surf, center, r, color, *, halo=2.2):
    """A baked rim light: a soft additive halo (blooms at night) + a bright
    core + a hot white pip, all stamped to a scratch surface so the additive
    bloom never punches transparent holes in the saucer body."""
    cx, cy = center
    rad = int(r * halo) + 3
    g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    for i in range(4, 0, -1):
        a = 40 + (4 - i) * 30
        rr = int(rad * i / 4)
        pygame.draw.circle(g, (*color, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)
    pygame.draw.circle(surf, color, (cx, cy), r)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), max(1, r - 1))


def _rim_lights(surf, cx, cy, rx, ry, n, phase, base, lit, *, y_squash=0.0):
    """A ring of n rim lights wrapped on the front edge of the disc. The two
    lights nearest `phase` glow bright (`lit`) with a baked halo; the rest sit
    dim (`base`). y_squash nudges the ring down onto the disc's leading lip."""
    for i in range(n):
        t = i / n
        ang = math.pi * (0.15 + 0.7 * t)          # front-facing arc only
        lx = int(cx + math.cos(ang) * rx * 2 - rx)
        # lay the dots along the lower front lip of the ellipse
        lx = int(cx - rx + (2 * rx) * t)
        ly = int(cy + ry * (1.0 - 0.5 * abs(0.5 - t) * 2) + y_squash)
        d = (i - phase) % n
        on = d == 0 or d == 1
        if on:
            bright = lit if d == 0 else tuple(int(c * 0.7 + 255 * 0.3) for c in lit)
            _glow_dot(surf, (lx, ly), 2, bright)
        else:
            pygame.draw.circle(surf, base, (lx, ly), 2)
            pygame.draw.circle(surf, tuple(min(255, c + 30) for c in base),
                               (lx, ly), 1)


def _tractor_beam(surf, cx, top_y, width, length, color, phase, *, strength=1.0):
    """A baked downward cone of light from the saucer underside. It PULSES
    with the chase: phase 0/2 widen, 1/3 narrow, so the beam breathes in time
    with the rim chase. Drawn additive so it glows over night skies."""
    pulse = 1.0 + (0.18 if phase % 2 == 0 else -0.06) * strength
    w = int(width * pulse)
    beam = pygame.Surface((w * 2 + 6, length + 4), pygame.SRCALPHA)
    bx = w + 3
    for i in range(length):
        t = i / length
        spread = int(w * (0.35 + 0.65 * t))
        a = int(95 * strength * (1.0 - t) ** 1.3)
        pygame.draw.line(beam, (*color, a),
                         (bx - spread, i), (bx + spread, i))
    # brighter inner shaft
    for i in range(length):
        t = i / length
        spread = max(1, int(w * 0.4 * (0.3 + 0.7 * t)))
        a = int(70 * strength * (1.0 - t))
        pygame.draw.line(beam, (255, 255, 255, a),
                         (bx - spread, i), (bx + spread, i))
    surf.blit(beam, (cx - bx, top_y), special_flags=pygame.BLEND_RGBA_ADD)


# ═════════════════════════════════════════════════════════════════════════════
# V1 · CLASSIC CHROME — chrome-silver shallow disc, green glass dome with a
#     tiny grey alien, cyan rim lights, green tractor beam. The archetype.
# ═════════════════════════════════════════════════════════════════════════════
def build_ufo_v1(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 26, 9

    # Tractor beam first so the disc overlaps its top.
    _tractor_beam(surf, BCX, BCY + 4, 13, 30, (90, 255, 170), ph)

    # Chrome disc: dark underside, bright top, hot specular band.
    _aaellipse(surf, (96, 104, 120), (BCX, BCY + 3), rx, ry + 1)      # underside
    _aaellipse(surf, (208, 218, 232), (BCX, BCY), rx, ry)            # body
    _aaellipse(surf, (240, 248, 255), (BCX - 5, BCY - 3), rx - 8, 4)  # top sheen
    pygame.draw.line(surf, (150, 160, 178), (BCX - rx + 4, BCY + 2),
                     (BCX + rx - 4, BCY + 2), 1)

    # Rim-light ring chasing around the front lip.
    _rim_lights(surf, BCX, BCY, rx - 3, ry, 8, ph, (40, 70, 90), (80, 230, 255))

    # Green glass dome with a tiny alien silhouette.
    _aaellipse(surf, (40, 120, 90), (BCX, DOME_Y + 1), 13, 11)
    _aaellipse(surf, (90, 220, 150), (BCX, DOME_Y), 12, 10)
    _aaellipse(surf, (170, 255, 210), (BCX - 4, DOME_Y - 3), 5, 4)    # glass glint
    # alien head + eyes
    pygame.draw.circle(surf, (120, 150, 130), (BCX, DOME_Y + 2), 5)
    pygame.draw.ellipse(surf, (20, 24, 30), (BCX - 4, DOME_Y, 3, 4))
    pygame.draw.ellipse(surf, (20, 24, 30), (BCX + 1, DOME_Y, 3, 4))
    # dome rim ring
    pygame.draw.line(surf, (200, 210, 224), (BCX - 12, DOME_Y + 7),
                     (BCX + 12, DOME_Y + 7), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V2 · BRUSHED STEEL · MAGENTA — wider, flatter brushed-steel disc, smoky-dark
#     dome (no alien), magenta rim lights, NO tractor beam. Sleek + menacing.
# ═════════════════════════════════════════════════════════════════════════════
def build_ufo_v2(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 28, 8

    # Wide flat brushed-steel disc.
    _aaellipse(surf, (70, 74, 86), (BCX, BCY + 3), rx, ry + 1)
    _aaellipse(surf, (150, 158, 172), (BCX, BCY), rx, ry)
    _aaellipse(surf, (188, 196, 210), (BCX, BCY - 2), rx - 4, ry - 3)
    # brushed striations
    for sx in range(-rx + 6, rx - 5, 5):
        pygame.draw.line(surf, (120, 128, 142),
                         (BCX + sx, BCY - 2), (BCX + sx, BCY + 4), 1)
    _aaellipse(surf, (230, 236, 246), (BCX - 6, BCY - 3), 8, 2)       # sheen

    # Dense magenta rim chase (more, smaller lights — high-tech read).
    _rim_lights(surf, BCX, BCY, rx - 3, ry, 11, ph, (70, 30, 55), (255, 70, 200))

    # Smoky dark dome, low + wide.
    _aaellipse(surf, (44, 40, 58), (BCX, DOME_Y + 2), 14, 9)
    _aaellipse(surf, (80, 70, 104), (BCX, DOME_Y), 12, 8)
    _aaellipse(surf, (150, 90, 190), (BCX - 4, DOME_Y - 2), 5, 3)     # reflection
    pygame.draw.line(surf, (170, 178, 192), (BCX - 12, DOME_Y + 6),
                     (BCX + 12, DOME_Y + 6), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V3 · MATTE STEALTH · AMBER — matte dark egg-tall craft, tall amber dome with
#     a tiny alien, warm amber rim lights + a wide amber tractor beam. The
#     "night-ops" abductor — biggest glow against a dark sky.
# ═════════════════════════════════════════════════════════════════════════════
def build_ufo_v3(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 24, 10

    # Big warm tractor beam (the hero glow at night).
    _tractor_beam(surf, BCX, BCY + 5, 16, 32, (255, 196, 90), ph, strength=1.2)

    # Matte dark disc, slightly egg-deep.
    _aaellipse(surf, (24, 26, 34), (BCX, BCY + 3), rx, ry + 1)
    _aaellipse(surf, (48, 52, 64), (BCX, BCY), rx, ry)
    _aaellipse(surf, (66, 72, 88), (BCX - 3, BCY - 4), rx - 8, 4)
    pygame.draw.line(surf, (30, 32, 42), (BCX - rx + 4, BCY + 1),
                     (BCX + rx - 4, BCY + 1), 1)

    # Amber rim chase.
    _rim_lights(surf, BCX, BCY, rx - 3, ry, 9, ph, (70, 48, 20), (255, 188, 70))

    # Tall amber glass dome with alien.
    _aaellipse(surf, (110, 70, 20), (BCX, DOME_Y - 1), 12, 13)
    _aaellipse(surf, (240, 180, 70), (BCX, DOME_Y - 2), 10, 11)
    _aaellipse(surf, (255, 230, 160), (BCX - 4, DOME_Y - 6), 4, 4)
    # big-eyed alien silhouette
    pygame.draw.circle(surf, (90, 60, 30), (BCX, DOME_Y), 5)
    pygame.draw.ellipse(surf, (24, 18, 12), (BCX - 4, DOME_Y - 2, 3, 5))
    pygame.draw.ellipse(surf, (24, 18, 12), (BCX + 1, DOME_Y - 2, 3, 5))
    pygame.draw.line(surf, (60, 64, 78), (BCX - 11, DOME_Y + 8),
                     (BCX + 11, DOME_Y + 8), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V4 · OIL-SLICK IRIDESCENT — a rainbow-anodised metal saucer (teal→violet→
#     gold facets), a clear crystal dome, prismatic rim lights cycling colour
#     with the chase, thin violet tractor beam. The flashiest premium read.
# ═════════════════════════════════════════════════════════════════════════════
_OIL_BANDS = [(40, 180, 180), (70, 110, 220), (150, 80, 210),
              (220, 110, 160), (240, 190, 90)]


def build_ufo_v4(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 26, 9

    _tractor_beam(surf, BCX, BCY + 4, 11, 28, (190, 120, 255), ph)

    # Iridescent banded disc — horizontal oil-slick stripes shifting by phase
    # so the metal itself appears to shimmer as the lights chase.
    _aaellipse(surf, (40, 30, 60), (BCX, BCY + 3), rx, ry + 1)
    band = pygame.Surface((rx * 2, ry * 2), pygame.SRCALPHA)
    n = len(_OIL_BANDS)
    for i in range(ry * 2):
        col = _OIL_BANDS[(i + ph) % n]
        pygame.draw.line(band, col, (0, i), (rx * 2, i))
    mask = pygame.Surface((rx * 2, ry * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(mask, (255, 255, 255, 255), mask.get_rect())
    band.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(band, (BCX - rx, BCY - ry))
    _aaellipse(surf, (255, 255, 255), (BCX - 6, BCY - 4), 7, 2)       # specular

    # Prismatic rim chase — lit colour rotates with the phase.
    prism = [(120, 255, 255), (160, 160, 255), (255, 150, 255), (255, 220, 140)]
    _rim_lights(surf, BCX, BCY, rx - 3, ry, 8, ph, (60, 50, 80), prism[ph])

    # Clear crystal dome (cool bluish glass).
    _aaellipse(surf, (120, 150, 200), (BCX, DOME_Y + 1), 13, 11)
    _aaellipse(surf, (190, 220, 255), (BCX, DOME_Y), 11, 9)
    _aaellipse(surf, (255, 255, 255), (BCX - 4, DOME_Y - 3), 5, 4)
    # faint prismatic facet lines
    for dx in (-6, 0, 6):
        pygame.draw.line(surf, (prism[ph]),
                         (BCX + dx, DOME_Y - 7), (BCX + dx // 2, DOME_Y + 6), 1)
    pygame.draw.line(surf, (220, 230, 245), (BCX - 12, DOME_Y + 7),
                     (BCX + 12, DOME_Y + 7), 1)
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# V5 · RETRO TIN-TOY · SATURN — a 1950s litho tin-toy saucer: cream + red
#     enamel disc with a riveted Saturn ring, primary-colour bulb rim lights,
#     a red-capped dome porthole, no beam. Charming, toy-like, day-friendly.
# ═════════════════════════════════════════════════════════════════════════════
def build_ufo_v5(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = 22, 9

    # Saturn ring around the disc (drawn first, sticks out past the body).
    ring = pygame.Surface((COMPOSITE_W, 22), pygame.SRCALPHA)
    pygame.draw.ellipse(ring, (210, 180, 120), (1, 1, COMPOSITE_W - 2, 20), 4)
    pygame.draw.ellipse(ring, (250, 230, 170), (1, 1, COMPOSITE_W - 2, 20), 2)
    surf.blit(ring, (0, BCY - 11))

    # Cream enamel disc with a red belly stripe (tin-litho).
    _aaellipse(surf, (190, 60, 50), (BCX, BCY + 3), rx, ry + 1)        # red underside
    _aaellipse(surf, (250, 240, 220), (BCX, BCY), rx, ry)             # cream body
    pygame.draw.line(surf, (210, 70, 60), (BCX - rx + 3, BCY + 3),
                     (BCX + rx - 3, BCY + 3), 3)                       # red stripe
    _aaellipse(surf, (255, 255, 245), (BCX - 5, BCY - 3), rx - 9, 3)   # sheen
    # rivets along the seam
    for sx in range(-rx + 5, rx - 4, 6):
        pygame.draw.circle(surf, (170, 150, 110), (BCX + sx, BCY - 1), 1)

    # Primary-colour BULB rim lights (red/yellow/blue/green carnival bulbs).
    bulbs = [(255, 90, 70), (255, 210, 70), (90, 170, 255), (110, 230, 120)]
    n = 8
    for i in range(n):
        t = i / n
        lx = int(BCX - (rx - 4) + (2 * (rx - 4)) * t)
        ly = int(BCY + ry * (1.0 - abs(0.5 - t)) - 1)
        col = bulbs[i % len(bulbs)]
        if (i - ph) % n in (0, 1):
            _glow_dot(surf, (lx, ly), 2, col)
        else:
            pygame.draw.circle(surf, tuple(int(c * 0.55) for c in col), (lx, ly), 2)
            pygame.draw.circle(surf, col, (lx, ly), 1)

    # Red-capped porthole dome (a single round window, toy-like).
    _aaellipse(surf, (200, 60, 50), (BCX, DOME_Y - 1), 12, 10)         # red cap
    pygame.draw.circle(surf, (120, 200, 230), (BCX, DOME_Y + 1), 7)    # blue glass
    pygame.draw.circle(surf, (220, 245, 255), (BCX - 2, DOME_Y - 1), 3)
    pygame.draw.circle(surf, (250, 240, 220), (BCX, DOME_Y + 1), 7, 1)  # chrome ring
    # antenna ball on top — a cheeky tin-toy tell
    pygame.draw.line(surf, (180, 180, 180), (BCX, DOME_Y - 10),
                     (BCX, DOME_Y - 15), 1)
    _glow_dot(surf, (BCX, DOME_Y - 16), 2,
              bulbs[ph] if False else (255, 90, 70))
    return surf


get_ufo_v1 = _make_prebuilt_skin(build_ufo_v1)
get_ufo_v2 = _make_prebuilt_skin(build_ufo_v2)
get_ufo_v3 = _make_prebuilt_skin(build_ufo_v3)
get_ufo_v4 = _make_prebuilt_skin(build_ufo_v4)
get_ufo_v5 = _make_prebuilt_skin(build_ufo_v5)


BUILDERS = {
    "V1 · Classic Chrome (cyan/green)": get_ufo_v1,
    "V2 · Brushed Steel (magenta)":     get_ufo_v2,
    "V3 · Matte Stealth (amber)":       get_ufo_v3,
    "V4 · Oil-Slick Iridescent":        get_ufo_v4,
    "V5 · Retro Tin-Toy (Saturn)":      get_ufo_v5,
}
