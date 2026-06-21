"""CACTUS PINATA secret flyer skin — round-1 concept builder.

A prickly saguaro piñata in a tiny sombrero. The point is the SILHOUETTE: a
tall vertical trunk with two THICK upturned side-arms (a "U" of arms) capped by
a small tilted straw sombrero — the only top-heavy vertical in the piñata set,
so it reads as "cactus" at 40px before any colour resolves.

There are NO wings and NO live particles. The 4-frame tell is a FRINGE-FLUTTER
SWAY: the trunk stays planted while the horizontal crepe fringe bands and the
sombrero lean left → centre → right → centre. That survives grayscale because
the pale cream fringe edges shift and the hat tilts — a readable wobble carried
by value, not hue.

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
GREEN_HI    = (60, 168, 69)     # #3CA845 lit band
GREEN_LO    = (46, 125, 56)     # #2E7D38 shadow band
GREEN_EDGE  = (34, 96, 44)      # darker trunk edge for roundness
RIB_SHADE   = (40, 110, 50)     # vertical rib shading
STRAW       = (231, 197, 106)   # #E7C56A sombrero straw
STRAW_LO    = (196, 160, 78)    # sombrero shadow
STRAW_HI    = (247, 224, 156)   # sombrero highlight band
FRINGE      = (251, 243, 221)   # #FBF3DD cream crepe fringe (the night keyline)
FLOWER_PINK = (244, 138, 184)   # pink flower dot
FLOWER_CORE = (255, 246, 250)   # white flower centre
SPINE       = (250, 244, 222)   # pale spine ticks (double as fringe keyline)

# Three green band tones cycled down the trunk so the crepe layers read as
# stacked papier-mâché rings even at small size.
BANDS = (GREEN_HI, GREEN_LO, GREEN_HI, GREEN_LO, GREEN_HI, GREEN_LO)


def _new():
    return pygame.Surface((COMPOSITE_W, COMPOSITE_H), pygame.SRCALPHA)


def _phase(angle_deg):
    """Map a wing angle (_WING_ANGLES: 50→-40) to a 0..3 sway step. The lean
    of the fringe + sombrero advances one notch per pose so the four frames
    read left → centre → right → centre."""
    return int(round((50 - angle_deg) / 30.0)) % 4


# Sway lean per phase, in pixels of horizontal fringe shift. Phase 1/3 are the
# centred rest poses; 0 leans left, 2 leans right — a small wobble, NOT a
# full-body rotation (velocity tilt is applied later by the engine).
_LEAN = (-2.4, 0.0, 2.4, 0.0)
_HAT_TILT = (-9.0, 0.0, 9.0, 0.0)   # sombrero brim lean in degrees


def _trunk_band(surf, cy, half_w, h, color, lean):
    """One horizontal crepe band of the trunk, drawn as a rounded rect whose
    horizontal offset is the per-band fringe shift. Returns (left, right) x of
    the band so the fringe + flowers can pin to its real edges."""
    cx = BCX + lean
    rect = pygame.Rect(int(cx - half_w), int(cy - h / 2), int(half_w * 2), int(h))
    pygame.draw.rect(surf, color, rect, border_radius=max(2, h // 2))
    return rect


def _draw_arm(surf, base_x, base_y, side, lean):
    """A THICK upturned saguaro arm: a short horizontal stub off the trunk that
    bends UP into a vertical nub. Built from two fat capsules so it survives
    40px as a solid stub, not a thin prong. `side` is -1 (left) / +1 (right)."""
    lx = base_x + side * lean * 0.5     # arms drift with the sway, gently
    elbow_x = lx + side * 9
    # horizontal stub
    pygame.draw.line(surf, GREEN_LO, (lx, base_y), (elbow_x, base_y), 9)
    pygame.draw.line(surf, GREEN_HI, (lx, base_y - 1), (elbow_x, base_y - 1), 5)
    # vertical upturn nub
    top_y = base_y - 13
    pygame.draw.line(surf, GREEN_LO, (elbow_x, base_y), (elbow_x, top_y), 9)
    pygame.draw.line(surf, GREEN_HI, (elbow_x - side * 1, base_y), (elbow_x - side * 1, top_y), 5)
    # rounded cap on the arm tip
    pygame.draw.circle(surf, GREEN_HI, (int(elbow_x), int(top_y)), 4)
    pygame.draw.circle(surf, GREEN_EDGE, (int(elbow_x), int(top_y)), 4, 1)
    # a pale spine tick on the arm tip — keylines the green at night
    pygame.draw.circle(surf, SPINE, (int(elbow_x - side * 2), int(top_y - 2)), 1)
    return elbow_x, top_y


def _flower(surf, x, y):
    """A small pink-and-white flower dot: 4 pink petals around a white core.
    Bright enough to pop against the night sky."""
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        pygame.draw.circle(surf, FLOWER_PINK, (int(x + dx), int(y + dy)), 1)
    pygame.draw.circle(surf, FLOWER_CORE, (int(x), int(y)), 1)


def _sombrero(surf, cx, cy, tilt):
    """A small tilted straw sombrero: a wide flat brim ellipse + a low crown,
    rotated by `tilt` degrees so the hat leans with the sway. Drawn to a scratch
    surface and rotozoomed so the lean is a real tilt, not a redraw."""
    pad = 26
    s = pygame.Surface((pad * 2, pad * 2), pygame.SRCALPHA)
    ox, oy = pad, pad
    # brim
    _aaellipse(s, STRAW_LO, (ox, oy + 3), 17, 6)
    _aaellipse(s, STRAW, (ox, oy + 1), 17, 5)
    # turned-up brim edge keyline (cream) — reads the hat at night
    pygame.draw.ellipse(s, FRINGE, pygame.Rect(ox - 17, oy - 4, 34, 11), 1)
    # crown
    _aaellipse(s, STRAW_LO, (ox, oy - 3), 8, 6)
    _aaellipse(s, STRAW, (ox, oy - 4), 7, 5)
    _aaellipse(s, STRAW_HI, (ox - 1, oy - 6), 5, 2)
    # decorative band around the crown base
    pygame.draw.line(s, FLOWER_PINK, (ox - 7, oy - 2), (ox + 7, oy - 2), 2)
    rot = pygame.transform.rotozoom(s, tilt, 1.0)
    rr = rot.get_rect(center=(cx, cy))
    surf.blit(rot, rr.topleft)


def build(wing_angle_deg):
    """One CACTUS PINATA frame on a 64×84 SRCALPHA canvas. The trunk + arms
    silhouette is the read; the per-band fringe shift + tilting sombrero are the
    sway tell. Drawn UPRIGHT — no baked body rotation."""
    surf = _new()
    ph = _phase(wing_angle_deg)
    lean = _LEAN[ph]
    hat_tilt = _HAT_TILT[ph]

    half_w = 9                       # trunk half-width — a fat, readable column
    # Trunk spans well above and below centre, but the visual mass sits at BCY.
    top_y = BCY - 22
    bot_y = BCY + 22
    band_h = 7
    n_bands = 6

    # ── arms first so the trunk overlaps their inner roots ──────────────────
    arm_base_y = BCY - 6
    _draw_arm(surf, BCX - half_w + 2, arm_base_y, -1, lean)
    _draw_arm(surf, BCX + half_w - 2, arm_base_y, +1, lean)

    # ── trunk as stacked crepe bands, each with its own sway offset so the
    #    fringe ripples down the body (top leans most, base barely moves). ────
    rib_x = BCX
    for i in range(n_bands):
        t = i / (n_bands - 1)
        cy = top_y + (bot_y - top_y) * t
        # bands near the top sway more than the planted base → a flutter, not a
        # rigid slide.
        band_lean = lean * (1.0 - 0.7 * t)
        color = BANDS[i % len(BANDS)]
        rect = _trunk_band(surf, cy, half_w, band_h + 1, color, band_lean)
        # vertical rib shading down the centre for roundness
        pygame.draw.line(surf, RIB_SHADE,
                         (rect.centerx - 3, rect.top + 1),
                         (rect.centerx - 3, rect.bottom - 1), 1)
        pygame.draw.line(surf, GREEN_EDGE,
                         (rect.right - 1, rect.top + 1),
                         (rect.right - 1, rect.bottom - 1), 1)
        rib_x = rect.centerx

        # ── crepe fringe: a cream keyline + ticked lower edge between bands.
        #    This is the part that VISIBLY shifts frame to frame (the sway) and
        #    the pale value that survives grayscale + keylines the green at
        #    night. ────────────────────────────────────────────────────────
        fy = rect.bottom
        pygame.draw.line(surf, FRINGE, (rect.left + 1, fy), (rect.right - 1, fy), 1)
        for fx in range(rect.left + 2, rect.right - 1, 3):
            pygame.draw.line(surf, FRINGE, (fx, fy), (fx, fy + 2), 1)

        # spine ticks on the band edges (pale) double as a night keyline
        pygame.draw.circle(surf, SPINE, (rect.left + 1, rect.centery), 1)
        pygame.draw.circle(surf, SPINE, (rect.right - 2, rect.centery), 1)

    # ── flower dots: a couple on the upper trunk + one per arm tip area ──────
    _flower(surf, rib_x - 3 + lean * 0.5, top_y + 4)
    _flower(surf, rib_x + 4 + lean * 0.4, top_y + band_h * 2)
    _flower(surf, BCX - 13 + lean * 0.5, BCY - 17)
    _flower(surf, BCX + 13 + lean * 0.5, BCY - 16)

    # ── sombrero perched on top of the trunk, leaning with the sway ─────────
    _sombrero(surf, BCX + lean, top_y - 4, hat_tilt)

    return surf
