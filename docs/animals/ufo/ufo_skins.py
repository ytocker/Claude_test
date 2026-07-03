"""Production UFO Store skin — `skin_ufo` (round-2 convergence).

A secret ultra-premium NON-creature flyer: the player's flapping bird becomes
a domed alien saucer. There are NO wings — the "flap" is reinterpreted as a
CHASING RIM-LIGHT CYCLE: two lit lights advance one notch per pose around the
FRONT lip of the disc, and the tractor beam widens/narrows in time, giving the
craft life without a wing-beat.

Round-2 lineage: the art-director picked V3 MATTE STEALTH (amber) for its
night "glow out of black", but with V1's disc-to-dome ratio grafted on so the
saucer ELLIPSE — not the dome — is the dominant mass at 40px. The matte hull
gets a baked high-value keyline on its upper edge so the silhouette survives a
bright DAY sky (which otherwise swallows a near-black disc), while still
reading as a craft glowing out of the dark at night.

Contract (mirrors game/animal_skins.py so the winner lifts straight into a
production game/animal_ufo.py):

  * `build_ufo(wing_angle_deg) -> pygame.Surface`  one flat frame on a
    64x84 SRCALPHA canvas; saucer body mass centred at (32,44), beam below.
  * a cached `(frame_idx, tilt_deg) -> Surface` getter from a local
    `_make_prebuilt_skin(build_fn)`.
  * `BUILDERS = {"skin_ufo": get_ufo}` registry at the bottom.

North star: one bold silhouette (a WIDE saucer disc) + one tell (the chasing
rim-light ring). Reads at 40px on day AND night; struck most at night where
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

# Borrow V1's disc-to-dome ratio: a WIDE shallow disc with a small, LOW dome,
# so the ellipse is the dominant mass and the disc reads as a disc even with
# the dome + beam removed.
DISC_RX, DISC_RY = 26, 9        # wide shallow saucer
DOME_RX, DOME_RY = 12, 9        # small, low dome
DOME_Y = BCY - 8                # dome sits just above the disc, not stacked tall


# ── canonical AMBER colourway (alt colorways kept commented for reference) ───
# The amber look the art-director shipped. To re-skin to an alt colorway, swap
# this block — every draw call below pulls from these names.
HULL_DARK   = (22, 24, 30)      # near-black underside (the "out of black" base)
HULL_BODY   = (44, 48, 60)      # matte hull
HULL_SHEEN  = (66, 72, 88)      # faint top sheen
KEYLINE     = (214, 196, 150)   # pale-amber lip — survives the brightest day sky
RIM_DIM     = (78, 54, 22)      # unlit rim dot
RIM_LIT     = (255, 190, 78)    # lit rim dot (the chase)
DOME_GLASS  = (236, 176, 70)    # amber dome glass
DOME_RIMLO  = (120, 78, 24)     # dome base ring (sits under the glass)
DOME_PUPIL  = (66, 40, 14)      # dark "occupant" pupil shape inside the glass
DOME_GLINT  = (255, 240, 196)   # bright specular glint on the glass
BEAM_COLOR  = (255, 196, 90)    # warm tractor beam

# alt CYAN colorway:    HULL same; KEYLINE (170,210,224); RIM_LIT (96,232,255)
#                       RIM_DIM (28,64,80); DOME_GLASS (120,210,235);
#                       DOME_PUPIL (18,46,58); BEAM_COLOR (110,235,255)
# alt MAGENTA colorway: HULL same; KEYLINE (224,186,212); RIM_LIT (255,96,206)
#                       RIM_DIM (78,26,58); DOME_GLASS (210,110,200);
#                       DOME_PUPIL (60,18,52); BEAM_COLOR (255,110,210)


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
    runs 50→-40 across the four poses, so the lit pair advances one notch per
    pose and the cycle reads as rotation."""
    return int(round((50 - angle_deg) / 30.0)) % 4


def _glow_dot(surf, center, r, color, *, halo=2.0, contour=True, core=True):
    """A baked rim light: a soft additive halo (blooms at night) + a bright
    core, stamped to a scratch surface so the additive bloom never punches
    transparent holes in the saucer body. A thin dark contour around the core
    keeps the chase legible on a BRIGHT day sky and for colourblind players
    (the chase can't lean on amber hue alone)."""
    cx, cy = center
    rad = int(r * halo) + 2
    g = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
    for i in range(3, 0, -1):
        a = 36 + (3 - i) * 26
        rr = int(rad * i / 3)
        pygame.draw.circle(g, (*color, a), (rad, rad), rr)
    surf.blit(g, (cx - rad, cy - rad), special_flags=pygame.BLEND_RGBA_ADD)
    if contour:
        pygame.draw.circle(surf, (18, 12, 8), (cx, cy), r + 1)
    pygame.draw.circle(surf, color, (cx, cy), r)
    if core:                       # a small hot pip, not a blob that merges
        pygame.draw.circle(surf, (255, 248, 230), (cx, cy), max(1, r - 1))


def _rim_lights(surf, cx, cy, rx, ry, n, phase, base, lit):
    """A ring of n rim lights wrapped on the FRONT lip of the disc. The 2
    lights at `phase` glow bright + larger (`lit`); the rest sit small + dim
    (`base`) but stay clearly visible so the eye can track the lit pair
    ADVANCING one notch left→right per frame — rotation, not a twinkle. The
    lit/dim contrast (size + value + a dark contour) is wide enough that no two
    adjacent dots ever read as both "on"."""
    for i in range(n):
        # span the full leading lip so the chase visibly travels across it.
        t = (i + 0.5) / n
        lx = int(cx - rx + (2 * rx) * t)
        ly = int(cy + ry * (1.0 - 0.5 * abs(0.5 - t) * 2) + 1)
        d = (i - phase) % n
        if d == 0 or d == 1:
            # leading dot brightest; both lit dots are larger than the dim ones.
            bright = lit if d == 0 else tuple(int(c * 0.55 + 255 * 0.45) for c in lit)
            _glow_dot(surf, (lx, ly), 2, bright, halo=2.0)
        else:
            # dim but visible: a contoured low-value pip — the "off" lamps the
            # eye reads the lit pair travelling against.
            pygame.draw.circle(surf, (16, 12, 8), (lx, ly), 2)
            pygame.draw.circle(surf, base, (lx, ly), 1)


def _tractor_beam(surf, cx, top_y, width, length, color, phase, *, strength=1.0):
    """A baked downward cone of light from the saucer underside. It PULSES
    with the chase: phase 0/2 widen, 1/3 narrow, so the beam breathes in time
    with the rim chase — the clearest "alive" signal. Drawn additive so it
    glows over night skies; the top rows are capped so the additive bloom never
    washes up over the disc's lower lip and erodes the silhouette at night."""
    # A bigger widen/narrow swing makes the pulse the clear "alive" tell.
    pulse = 1.0 + (0.26 if phase % 2 == 0 else -0.10) * strength
    w = int(width * pulse)
    beam = pygame.Surface((w * 2 + 6, length + 4), pygame.SRCALPHA)
    bx = w + 3
    for i in range(length):
        t = i / length
        spread = int(w * (0.35 + 0.65 * t))
        # Ramp alpha in from zero over the first ~30% so the beam never blooms
        # bright right under the lip; the disc keeps a clean lower silhouette.
        rise = min(1.0, t / 0.30)
        a = int(96 * strength * rise * (1.0 - t) ** 1.2)
        pygame.draw.line(beam, (*color, a),
                         (bx - spread, i), (bx + spread, i))
    # brighter inner shaft (also ramped in at the top)
    for i in range(length):
        t = i / length
        spread = max(1, int(w * 0.4 * (0.3 + 0.7 * t)))
        rise = min(1.0, t / 0.30)
        a = int(64 * strength * rise * (1.0 - t))
        pygame.draw.line(beam, (255, 255, 255, a),
                         (bx - spread, i), (bx + spread, i))
    surf.blit(beam, (cx - bx, top_y), special_flags=pygame.BLEND_RGBA_ADD)


# ═════════════════════════════════════════════════════════════════════════════
# PRODUCTION · MATTE STEALTH AMBER — V3's palette on V1's disc geometry.
#   Wide matte disc (the dominant mass) + small low amber dome (a bright glint
#   over a dark occupant pupil) + amber rim chase with a dark contour + a
#   pulsing amber beam. A baked pale-amber keyline rims the upper hull so the
#   near-black silhouette survives the brightest day sky.
# ═════════════════════════════════════════════════════════════════════════════
def build_ufo(wing_angle_deg):
    surf = _new()
    ph = _phase(wing_angle_deg)
    rx, ry = DISC_RX, DISC_RY

    # Tractor beam first so the disc overlaps (and caps) its top.
    _tractor_beam(surf, BCX, BCY + 4, 15, 30, BEAM_COLOR, ph, strength=1.15)

    # Matte dark disc — the dominant ellipse. Dark underside, hull body, sheen.
    _aaellipse(surf, HULL_DARK, (BCX, BCY + 3), rx, ry + 1)       # underside
    _aaellipse(surf, HULL_BODY, (BCX, BCY), rx, ry)              # body
    _aaellipse(surf, HULL_SHEEN, (BCX - 4, BCY - 4), rx - 9, 3)   # top sheen

    # Baked high-value keyline on the UPPER edge of the disc + dome shoulder.
    # A near-black hull vanishes into a bright day sky; this 1px pale-amber lip
    # holds the silhouette against the brightest day-biome band (sky_bot
    # ≈ (170,220,245)) without dimming the night "glow out of black".
    _keyline_arc(surf, BCX, BCY - 1, rx - 1, ry, KEYLINE)

    # Amber rim chase wrapped on the front lip (8 dots; the lit pair advances).
    _rim_lights(surf, BCX, BCY, rx - 4, ry, 8, ph, RIM_DIM, RIM_LIT)

    # Small, low amber dome (V1's ratio): a bright specular glint over a dark
    # occupant pupil — reads "occupied glass orb" at 40px without resolving to
    # noisy facial detail.
    _aaellipse(surf, DOME_RIMLO, (BCX, DOME_Y + 1), DOME_RX, DOME_RY)
    _aaellipse(surf, DOME_GLASS, (BCX, DOME_Y), DOME_RX - 1, DOME_RY - 1)
    # dark occupant pupil (a single soft shape, low in the orb)
    _aaellipse(surf, DOME_PUPIL, (BCX, DOME_Y + 2), 4, 4)
    # one bright specular glint high-left on the glass (the "occupied" read)
    _aaellipse(surf, DOME_GLINT, (BCX - 4, DOME_Y - 4), 3, 2)
    # keyline lip across the top of the dome glass
    pygame.draw.line(surf, KEYLINE,
                     (BCX - DOME_RX + 4, DOME_Y - DOME_RY + 3),
                     (BCX + DOME_RX - 4, DOME_Y - DOME_RY + 3), 1)
    return surf


def _keyline_arc(surf, cx, cy, rx, ry, color):
    """Bake a 1px high-value lip along the UPPER edge of the saucer ellipse.
    Drawn as an arc so only the top rim catches the "light", which is what
    survives a bright sky and sells the disc as a hard-edged metal shape."""
    rect = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    # top arc (≈ from 200° to 340°, i.e. the upper rim) in pygame's CCW radians
    pygame.draw.arc(surf, color, rect, math.radians(20), math.radians(160), 2)


# ── canonical getter + registry ──────────────────────────────────────────────
get_ufo = _make_prebuilt_skin(build_ufo)

BUILDERS = {"skin_ufo": get_ufo}
