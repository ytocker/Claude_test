"""PUFFERFISH Store skin — round-2 convergence.

Round 1 explored five takes; the art-director picked **V4 STAR-BURST** (the
bold sea-urchin needle-halo) as the silhouette winner, but asked to graft
**V1**'s friendly face (big eyes + pouty O + blush) onto it, give the ball real
internal value structure, and make the inflate gag read in the BODY, not just
the spikes. This module now leads with ONE production build that folds in every
note; two small alts are kept only for side-by-side comparison.

Contract (mirrors game/animal_skins.py so the winner lifts straight in):

  * `build_pufferfish(wing_angle_deg) -> pygame.Surface`  one flat frame on a
    64×84 SRCALPHA canvas, BODY mass centred at (BCX,BCY)=(32,44).
  * `get_pufferfish = _make_prebuilt_skin(build_pufferfish)` — cached
    `(frame_idx, tilt_deg) -> Surface` getter.
  * `BUILDERS = {"skin_pufferfish": get_pufferfish, ...}` for the review sheet.

Body mass is pinned at (32,44) on EVERY frame so the fixed 14px collision
circle stays fair even fully inflated — the gag is read through the spike halo,
a small radius wobble, and a body-wide brightness pulse, never an oversized
creature. The face is locked to a FIXED offset from that body anchor across all
four poses so the eyes never slide between frames (a round-1 dive-frame bug).

North star: "a skin lives or dies at 40px in motion." The urchin needle-star
owns the silhouette; two distinct eye-dots + the pouty O carry charm; the
two-tone spikes and radial body gradient give every ray and the ball their own
value step so the read survives downscale on bright-day AND night skies.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (match game/animal_skins.py exactly) ───────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84                # headroom (pufferfish uses little of it)
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44); fixed every frame

# Face is locked to a FIXED offset from the body anchor (never per-frame), so
# the eyes hold position across level/dive frames. Tuned to sit high/right.
EYE_DX   = 6                    # half-spacing of the two eyes
EYE_OFF_X = 1                   # face cluster nudged right of body centre
EYE_OFF_Y = -3                  # and up toward the crown
MOUTH_DY = 8                    # O-mouth below the eye line


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter (local copy)."""
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


def _flap(angle_deg):
    """0..1 'wing is up' factor. _WING_ANGLES runs 50 (down) → -40 (up)."""
    return (angle_deg + 40) / 90.0


def _inflate(angle_deg):
    """Comedic pulse: 1.0 fully INFLATED on the down-pose, ~0.0 deflated on
    the up-pose. The down-stroke is the puff (body swells, spikes flare,
    whole ball brightens)."""
    return 1.0 - _flap(angle_deg)


def _shade(col, f):
    """Scale an RGB triple toward black/white. f<1 darkens, f>1 brightens;
    used for the body-wide inflate brightness pulse so the gag reads in the
    ball itself, clamped so the up-frame never crushes to mud."""
    return tuple(max(0, min(255, int(c * f))) for c in col)


def _eye(surf, cx, cy, r, *, iris=(58, 42, 18), white=(255, 250, 240)):
    """Friendly round eye: white, dark iris pushed slightly outward, top-left
    glint. Sized so the two stay as two DISTINCT dots even at 40px."""
    pygame.draw.circle(surf, white, (cx, cy), r)
    pygame.draw.circle(surf, iris, (cx + max(1, r // 4), cy), max(2, r - 1))
    pygame.draw.circle(surf, (255, 255, 255),
                       (cx - r // 3, cy - r // 3), max(1, r // 3))


def _radial_body(surf, cx, cy, r, core, mid, edge):
    """Soft radial value structure: a few concentric ellipses light core →
    mid → edge so the ball reads as a sphere with internal volume, not a flat
    disc. Cheap (3-4 draws) and downscale-safe — the steps blur into a
    gradient at 40px instead of vanishing."""
    _aaellipse(surf, edge, (cx + 1, cy + 1), r, r)            # dark rim/contact
    _aaellipse(surf, mid,  (cx, cy), r - 1, r - 1)            # mid mass
    # Light core offset up-left toward the key light (top-left convention).
    _aaellipse(surf, core, (cx - 2, cy - 2), r - 5, r - 5)
    # Crisp top-left specular for the wet-balloon sheen.
    _aaellipse(surf, _shade(core, 1.10), (cx - 5, cy - 6), 4, 3)


def _spike_ring(surf, cx, cy, r_in, length, n, col_base, col_tip, start=0.0,
                taper=0.42):
    """Radial halo of two-tone needle spikes around (cx,cy).

    Each ray is two stacked triangles: a darker BASE wedge rooted on the body
    rim and a brighter TIP wedge on its outer half. The value step per ray is
    what lets the urchin-star survive the 40px downscale — it never collapses
    to a flat starburst. This ring is THE silhouette tell."""
    half = math.radians((360.0 / n) * taper) * 0.5
    for i in range(n):
        a = start + (2 * math.pi) * i / n
        bx, by = math.cos(a), math.sin(a)
        l_a, r_a = a - half, a + half
        p_l = (cx + math.cos(l_a) * r_in, cy + math.sin(l_a) * r_in)
        p_r = (cx + math.cos(r_a) * r_in, cy + math.sin(r_a) * r_in)
        mid = (cx + bx * (r_in + length * 0.55),
               cy + by * (r_in + length * 0.55))
        tip = (cx + bx * (r_in + length), cy + by * (r_in + length))
        m_l = (cx + math.cos(l_a) * (r_in + length * 0.40),
               cy + math.sin(l_a) * (r_in + length * 0.40))
        m_r = (cx + math.cos(r_a) * (r_in + length * 0.40),
               cy + math.sin(r_a) * (r_in + length * 0.40))
        # Darker base wedge (full width at the rim, narrowing outward).
        pygame.draw.polygon(surf, col_base, [p_l, p_r, m_r, m_l])
        # Brighter tip wedge — the value step that keeps each ray distinct.
        pygame.draw.polygon(surf, col_tip, [m_l, m_r, tip])
        _ = mid


# ═════════════════════════════════════════════════════════════════════════════
# PRODUCTION · STAR-BURST PUFF + FRIENDLY FACE  (the ship candidate)
#   V4's symmetric urchin needle-star silhouette, two-tone rays, on a yellow
#   ball with real radial value structure. V1's big friendly eyes + pouty O +
#   blush carry charm. Inflate gag reads in the BODY: the whole ball brightens
#   ~10% and swells on the down-puff, dims and shrinks on the up-deflate.
# ═════════════════════════════════════════════════════════════════════════════
_BODY_CORE = (255, 226, 132)    # light core
_BODY_MID  = (246, 196, 78)     # golden mass
_BODY_EDGE = (206, 148, 40)     # dark rim / contact shadow
_BELLY     = (255, 244, 206)
_SPIKE_BASE = (200, 134, 28)    # one shade darker — spike base
_SPIKE_TIP  = (248, 198, 86)    # bright tip
_SPIKE_BASE2 = (182, 118, 24)   # inner staggered ring, dimmer for depth
_SPIKE_TIP2  = (236, 182, 66)
_DARK   = (52, 36, 14)
_BLUSH  = (255, 168, 120)
_LIP    = (140, 72, 64)         # warm dark for the pouty O (not pure black)


def build_pufferfish(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)           # 1.0 puffed (down) → 0.0 deflated
    r = 14 + int(inf * 2)                     # body swells on the puff
    spk = 7 + int(inf * 6)                    # spikes flare out (big pulse)
    cx, cy = BCX, BCY                         # body mass pinned every frame

    # Body-wide brightness pulse so the inflate gag reads in the BALL, not just
    # the spikes: brighten ~10% fully puffed, dim ~10% fully deflated. Restrained
    # — value step only, no bloom halo.
    bf = 0.90 + 0.20 * inf
    core = _shade(_BODY_CORE, bf)
    mid  = _shade(_BODY_MID, bf)
    edge = _shade(_BODY_EDGE, bf)
    sb, st = _shade(_SPIKE_BASE, bf), _shade(_SPIKE_TIP, bf)
    sb2, st2 = _shade(_SPIKE_BASE2, bf), _shade(_SPIKE_TIP2, bf)

    # Two staggered urchin rings (offset half a step) under the ball so roots
    # tuck behind the body. Outer ring brighter, inner dimmer → depth.
    _spike_ring(surf, cx, cy, r - 1, spk, 16, sb, st, start=0.0, taper=0.44)
    _spike_ring(surf, cx, cy, r - 3, spk - 2, 16, sb2, st2,
                start=math.pi / 16, taper=0.40)

    # Ball with internal radial value structure (core → mid → edge).
    _radial_body(surf, cx, cy, r, core, mid, edge)
    # Pale belly lifts the lower-front, anchoring the sphere read.
    _aaellipse(surf, _shade(_BELLY, bf), (cx - 1, cy + 4), r - 6, r - 7)

    # ── FACE · locked to a FIXED offset from the body anchor every frame ──
    fx = cx + EYE_OFF_X
    fy = cy + EYE_OFF_Y
    # Blush first so the eyes/mouth sit over it.
    pygame.draw.circle(surf, _BLUSH, (fx - EYE_DX - 2, fy + 5), 2)
    pygame.draw.circle(surf, _BLUSH, (fx + EYE_DX + 2, fy + 5), 2)
    # Big friendly eyes — two DISTINCT dots that survive 40px.
    _eye(surf, fx - EYE_DX, fy, 4, iris=_DARK)
    _eye(surf, fx + EYE_DX, fy, 4, iris=_DARK)
    # Pouty O-mouth (warm dark ring, not a black hole).
    pygame.draw.circle(surf, _LIP, (fx, fy + MOUTH_DY), 3)
    pygame.draw.circle(surf, (96, 48, 44), (fx, fy + MOUTH_DY), 2)
    pygame.draw.circle(surf, (200, 120, 110), (fx - 1, fy + MOUTH_DY - 1), 1)
    return surf


get_pufferfish = _make_prebuilt_skin(build_pufferfish)


# ═════════════════════════════════════════════════════════════════════════════
# ALT-A · TIGHTER NEEDLE STAR — same face, denser/finer 20-ray halo for a more
#   sea-urchin (vs balloon) read. Kept only for the comparison column.
# ═════════════════════════════════════════════════════════════════════════════
def build_pufferfish_alt_dense(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 14 + int(inf * 2)
    spk = 6 + int(inf * 5)
    cx, cy = BCX, BCY
    bf = 0.90 + 0.20 * inf
    core, mid, edge = (_shade(_BODY_CORE, bf), _shade(_BODY_MID, bf),
                       _shade(_BODY_EDGE, bf))
    sb, st = _shade(_SPIKE_BASE, bf), _shade(_SPIKE_TIP, bf)

    _spike_ring(surf, cx, cy, r - 1, spk, 20, sb, st, start=0.0, taper=0.36)
    _radial_body(surf, cx, cy, r, core, mid, edge)
    _aaellipse(surf, _shade(_BELLY, bf), (cx - 1, cy + 4), r - 6, r - 7)

    fx, fy = cx + EYE_OFF_X, cy + EYE_OFF_Y
    pygame.draw.circle(surf, _BLUSH, (fx - EYE_DX - 2, fy + 5), 2)
    pygame.draw.circle(surf, _BLUSH, (fx + EYE_DX + 2, fy + 5), 2)
    _eye(surf, fx - EYE_DX, fy, 4, iris=_DARK)
    _eye(surf, fx + EYE_DX, fy, 4, iris=_DARK)
    pygame.draw.circle(surf, _LIP, (fx, fy + MOUTH_DY), 3)
    pygame.draw.circle(surf, (96, 48, 44), (fx, fy + MOUTH_DY), 2)
    return surf


get_pufferfish_alt_dense = _make_prebuilt_skin(build_pufferfish_alt_dense)


# ═════════════════════════════════════════════════════════════════════════════
# ALT-B · WARM-CORAL STAR — same geometry, a coral/orange palette instead of
#   gold so the night-sky read doesn't lean on yellow alone. Comparison only.
# ═════════════════════════════════════════════════════════════════════════════
_C_CORE = (255, 188, 120)
_C_MID  = (240, 138, 70)
_C_EDGE = (190, 92, 44)
_C_SB, _C_ST = (188, 96, 44), (250, 168, 100)


def build_pufferfish_alt_coral(wing_angle_deg):
    surf = _new()
    inf = _inflate(wing_angle_deg)
    r = 14 + int(inf * 2)
    spk = 7 + int(inf * 6)
    cx, cy = BCX, BCY
    bf = 0.90 + 0.20 * inf
    core, mid, edge = (_shade(_C_CORE, bf), _shade(_C_MID, bf),
                       _shade(_C_EDGE, bf))
    sb, st = _shade(_C_SB, bf), _shade(_C_ST, bf)

    _spike_ring(surf, cx, cy, r - 1, spk, 16, sb, st, start=0.0, taper=0.44)
    _spike_ring(surf, cx, cy, r - 3, spk - 2, 16,
                _shade(_C_SB, bf * 0.92), _shade(_C_ST, bf * 0.92),
                start=math.pi / 16, taper=0.40)
    _radial_body(surf, cx, cy, r, core, mid, edge)
    _aaellipse(surf, _shade((255, 236, 214), bf), (cx - 1, cy + 4), r - 6, r - 7)

    fx, fy = cx + EYE_OFF_X, cy + EYE_OFF_Y
    pygame.draw.circle(surf, (255, 150, 120), (fx - EYE_DX - 2, fy + 5), 2)
    pygame.draw.circle(surf, (255, 150, 120), (fx + EYE_DX + 2, fy + 5), 2)
    _eye(surf, fx - EYE_DX, fy, 4, iris=_DARK)
    _eye(surf, fx + EYE_DX, fy, 4, iris=_DARK)
    pygame.draw.circle(surf, _LIP, (fx, fy + MOUTH_DY), 3)
    pygame.draw.circle(surf, (96, 48, 44), (fx, fy + MOUTH_DY), 2)
    return surf


get_pufferfish_alt_coral = _make_prebuilt_skin(build_pufferfish_alt_coral)


# ─────────────────────────────────────────────────────────────────────────────
# Review registry. `skin_pufferfish` is the production lead that lifts into
# game/animal_skins.py; the two alts are comparison-only.
# ─────────────────────────────────────────────────────────────────────────────
BUILDERS = {
    "skin_pufferfish": get_pufferfish,
    "alt_dense_star":  get_pufferfish_alt_dense,
    "alt_coral_star":  get_pufferfish_alt_coral,
}

TELLS = {
    "skin_pufferfish": "urchin needle-star + friendly eyes & pouty O, golden",
    "alt_dense_star":  "tighter 20-ray needle star, same face",
    "alt_coral_star":  "coral palette so night read isn't yellow-only",
}
