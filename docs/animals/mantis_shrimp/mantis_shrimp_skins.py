"""Production MANTIS SHRIMP skin (`skin_mantis_shrimp`) — round-2 build.

Round 1 explored five takes; the art-director picked **v3 DUOTONE BRUISER**
and asked for one ship-ready convergence. This module now exposes the SINGLE
primary production build so it lifts straight into game/animal_skins.py:

  * `build_mantis_shrimp(wing_angle_deg) -> pygame.Surface` on a 64×84
    SRCALPHA canvas; body mass centred at (32,44), head/eye-stalks near
    (44,34) and up into the headroom.
  * `get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)` — a cached
    `(frame_idx, tilt_deg) -> Surface` getter (4 frames, per-3° rotation
    cache, each house-outlined for the day-sky contour).
  * `BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}`.

THE FLAP IS A STRIKE: the raptorial clubs cock BACK on the down-pose
(_WING_ANGLES starts at 50) and PUNCH FORWARD on the up-pose (ends at -40).
`_strike()` maps a wing angle to a 0..1 punch. The lead club crosses PAST the
snout line on the punch and the body recoils a touch, so the haymaker reads at
40px in motion.

Colour is STRUCTURE, not noise: a teal duotone shield carries two bold orange
load-bearing stripes plus one thin banded mid-stripe as a third accent, and
iridescent eye-jewels — controlled technicolor that never breaks the duotone
read. The night biome borrows a faint glow on ONLY the eye-jewels and
club-tips so the bruiser stays bold on dark skies without lighting the body.

North star: "a skin lives or dies at 40px in motion." The 40px tell is the
giant orange double-fist snapping past the snout, the teal/orange striped
shield, and the twin jewel periscopes.
"""
import math
import pygame

from game.parrot import (
    SPRITE_W, SPRITE_H, _WING_ANGLES, _add_outline, _aaellipse,
)


# ── tall-canvas constants (eye-stalks reach up into the headroom) ─────────────
COMPOSITE_W = SPRITE_W          # 64
COMPOSITE_H = 84
DY          = 12

BCX, BCY = 32, 32 + DY          # body centre  → (32, 44)
HCX, HCY = 44, 22 + DY          # head centre  → (44, 34)
CROWN_Y  = 12 + DY              # top of head  → 24


def _make_prebuilt_skin(build_fn):
    """Cached `(frame_idx, tilt_deg) -> Surface` getter — lazy 4-frame build
    + per-(frame, 3°) rotation cache, each frame house-outlined (the 1px dark
    contour the day-sky read needs)."""
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


def _strike(angle_deg):
    """0 = clubs cocked back (down-pose, wing=50), 1 = punched fully forward
    (up-pose, wing=-40). The reverse sense of a flap: lift the bird by
    throwing the punch, so the strike reads on the up-stroke."""
    return 1.0 - (angle_deg + 40) / 90.0


# ═════════════════════════════════════════════════════════════════════════════
# DUOTONE BRUISER palette — teal armoured shield + hot-orange hero.
#   Colour is load-bearing structure: the teal body and TWO bold orange
#   stripes are the read; the thin banded mid-stripe + jewel eyes are the
#   controlled third accent. No rainbow noise.
# ═════════════════════════════════════════════════════════════════════════════
_CARA   = (38, 178, 168)
_CARA_D = (20, 116, 110)
_CARA_H = (138, 236, 224)
_BAND   = (255, 124, 48)            # the two load-bearing orange stripes
_BAND_D = (206, 82, 26)
_BAND_H = (255, 192, 120)
_MID_A  = (255, 214, 70)            # thin banded mid-stripe — third accent
_MID_B  = (90, 210, 240)
_CLUB   = (255, 112, 56)
_CLUB_H = (255, 206, 140)
_CLUB_D = (182, 60, 24)
_CLUB_TIP = (255, 232, 188)         # club striking-face spark (night glow seed)
_STALK  = (36, 18, 58)
_STALK_RIM = (12, 8, 24)
_RIM    = (16, 86, 84)              # in-body dark rim that separates the fists
_EYE_HUE  = (118, 236, 216)
_EYE_HUE2 = (96, 150, 250)          # iridescent shift toward the jewel rim
_GLOW   = (120, 240, 220)


def _glow_dot(surf, cx, cy, r, col):
    """Soft additive halo for the night biome — used ONLY on eye-jewels and
    club-tips so the body stays a flat duotone silhouette."""
    g = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
    for rr, a in ((r * 2, 40), (int(r * 1.4), 70), (r, 120)):
        pygame.draw.circle(g, (*col, a), (r * 2, r * 2), rr)
    surf.blit(g, (cx - r * 2, cy - r * 2), special_flags=pygame.BLEND_RGBA_ADD)


def _jewel_eye(surf, cx, cy, r, *, glow):
    """Iridescent compound eye on a thick periscope stalk tip: a teal jewel
    that shifts blue toward the rim, the famous equatorial mid-band of
    ommatidia, a bright specular pixel, and (night only) a soft halo.

    The jewel reads as the head's brightest mass so the twin periscopes carry
    the silhouette on both bright-day and dark-night skies."""
    if glow:
        # Keep the halo tighter than the jewel so the close-set twins stay
        # two distinct periscope lamps, not one goggle band, on night skies.
        _glow_dot(surf, cx, cy, max(2, r - 2), _GLOW)
    # Thin dark seat ring so the jewel pops off any sky (day-contour assist)
    # without bloating into a goggle when the twin eyes sit close.
    pygame.draw.circle(surf, _STALK_RIM, (cx, cy), r + 1, 1)
    # Iridescent body: blue-shifted rim, teal core.
    pygame.draw.circle(surf, _EYE_HUE2, (cx, cy), r)
    pygame.draw.circle(surf, _EYE_HUE, (cx, cy), max(1, r - 1))
    # Equatorial midband of ommatidia (the signature stripe across the eye).
    pygame.draw.line(surf, (250, 252, 250), (cx - r, cy), (cx + r, cy), 1)
    # One hot specular pixel so the eye snaps to attention at 40px.
    pygame.draw.circle(surf, (255, 255, 255), (cx - max(1, r // 3), cy - max(1, r // 3)),
                       max(1, r // 3))


# ═════════════════════════════════════════════════════════════════════════════
# Raptorial club arm — a "boxing-glove" dactyl club on a folded arm.
#   Drawn in ABSOLUTE world coordinates straight onto the body surface so the
#   two fists can be aimed at independent targets: the lead fist drives UP +
#   FORWARD to OVERLAP the snout vector on the punch, the rear fist parks as a
#   separate orange mass with a clear gap to the lead fist. Aiming in world
#   space (not nested local offsets) is what keeps both reads honest at 40px.
# ═════════════════════════════════════════════════════════════════════════════
def _club_arm(surf, shoulder, elbow, fist, *, club_col, club_hi, arm_col,
              club_r, lead, glow):
    """Draw one raptorial club arm (shoulder→elbow→fist) at world coordinates.

    The striking face points along the shoulder→fist vector so the club reads
    as a hammer thrown in the punch direction, not a static ball. Each fist
    keeps a dark heel rim so the twin fists never visually merge."""
    # Segmented limb: dark-rimmed so the arm separates from the shield.
    pygame.draw.line(surf, _RIM, shoulder, elbow, 5)
    pygame.draw.line(surf, arm_col, shoulder, elbow, 3)
    pygame.draw.line(surf, _RIM, elbow, fist, 5)
    pygame.draw.line(surf, arm_col, elbow, fist, 3)
    pygame.draw.circle(surf, arm_col, elbow, 2)

    # The dactyl club — a chunky rounded fist with a dark heel rim so the two
    # fists keep a 1px dark separation even when they sit close in depth.
    pygame.draw.circle(surf, _STALK_RIM, fist, club_r + 1)
    pygame.draw.circle(surf, club_col, fist, club_r)
    pygame.draw.circle(surf, club_hi, (fist[0] - 1, fist[1] - 1), max(1, club_r - 2))

    # Striking-face spark + ridge oriented along the throw so the hammer face
    # leads. dx,dy is the unit-ish punch direction from the shoulder.
    dx, dy = fist[0] - shoulder[0], fist[1] - shoulder[1]
    mag = max(1.0, math.hypot(dx, dy))
    ux, uy = dx / mag, dy / mag
    fx, fy = int(fist[0] + ux * (club_r - 1)), int(fist[1] + uy * (club_r - 1))
    pygame.draw.line(surf, _CLUB_D,
                     (int(fist[0] + ux * club_r - uy * club_r),
                      int(fist[1] + uy * club_r + ux * club_r)),
                     (int(fist[0] + ux * club_r + uy * club_r),
                      int(fist[1] + uy * club_r - ux * club_r)), 1)
    pygame.draw.circle(surf, _CLUB_TIP, (fx, fy), 1)
    if glow and lead:
        _glow_dot(surf, fx, fy, max(2, club_r - 3), _CLUB)


def _segmented_tail(surf, cx, cy, *, count, span):
    """Armoured teal abdomen sweeping back from the body with orange-banded
    plate edges, ending in an orange tail-fan (telson + uropods)."""
    step = span / count
    for i in range(count):
        x = cx - int(i * step)
        rx = 8 - i
        ry = 11 - i
        pygame.draw.ellipse(surf, _CARA_D, (x - rx, cy - ry + 1, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _CARA, (x - rx, cy - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surf, _BAND, (x - rx, cy - ry, rx * 2, ry * 2), 1)
    tx = cx - int(span)
    for dy, dx in ((-7, -6), (0, -9), (7, -6)):
        pygame.draw.polygon(surf, _BAND, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)])
        pygame.draw.polygon(surf, _BAND_D, [
            (tx, cy), (tx + dx, cy + dy), (tx + dx + 3, cy + dy)], 1)


def _lerp_pt(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def _build(wing_angle_deg, *, glow):
    surf = _new()
    s = _strike(wing_angle_deg)

    # Body recoils slightly on the punch (shifts back + down) so the haymaker
    # has weight — the whole bruiser rocks with the strike.
    rcx = -int(s * 2)
    rcy = int(s * 1)
    bcx, bcy = BCX + rcx, BCY + rcy
    hcx, hcy = HCX + rcx, HCY + rcy

    # Shared front-lower shoulder for both arms. World-space targets below are
    # tuned so (a) the rear fist is ALWAYS a separate orange mass parked below
    # the lead fist with a sky gap, and (b) the lead fist drives UP+FORWARD to
    # OVERLAP the snout vector on the punch — the single dominant diagonal that
    # sells "strike" at 40px.
    sh = (bcx + 7, bcy + 3)

    # ── REAR fist: behind the shield, the second of the two fists. Cocked it
    #    sits low+forward; punched it rises a little but STAYS below the lead
    #    fist's path so the two orange masses never collapse into one.
    far_elbow = _lerp_pt((bcx + 10, bcy + 9), (bcx + 13, bcy + 8), s)
    far_fist  = _lerp_pt((bcx + 14, bcy + 14), (bcx + 21, bcy + 10), s)
    _club_arm(surf, (bcx + 4, bcy + 6), far_elbow, far_fist,
              club_col=_CLUB_D, club_hi=_CLUB, arm_col=_CARA_D,
              club_r=6, lead=False, glow=glow)

    # Segmented abdomen + orange tail-fan.
    _segmented_tail(surf, bcx - 7, bcy + 1, count=3, span=18)

    # ── Carapace shield — broad torpedo body, dark-rimmed for the day contour.
    _aaellipse(surf, _CARA_D, (bcx + 1, bcy + 1), 17, 14)
    _aaellipse(surf, _CARA, (bcx, bcy), 16, 13)
    _aaellipse(surf, _CARA_H, (bcx - 3, bcy - 4), 8, 4)

    # TWO bold orange load-bearing stripes across the shield (duotone signature).
    for off in (-5, 5):
        pygame.draw.line(surf, _BAND_D, (bcx + off - 1, bcy - 11),
                         (bcx + off - 1, bcy + 11), 4)
        pygame.draw.line(surf, _BAND, (bcx + off, bcy - 11),
                         (bcx + off, bcy + 11), 3)
        pygame.draw.line(surf, _BAND_H, (bcx + off, bcy - 9),
                         (bcx + off, bcy - 3), 1)
    # ONE thin banded mid-stripe between them — the controlled third accent
    # (alternating gold/cyan ticks), the only technicolor on the body.
    midx = bcx
    for k, ty in enumerate(range(bcy - 9, bcy + 10, 3)):
        pygame.draw.line(surf, (_MID_A, _MID_B)[k % 2], (midx, ty), (midx, ty + 1), 1)
    # Re-rim so the bands clamp inside the shield silhouette.
    pygame.draw.ellipse(surf, _CARA_D, (bcx - 16, bcy - 13, 32, 26), 1)

    # ── Head.
    _aaellipse(surf, _CARA_D, (hcx, hcy + 1), 11, 10)
    _aaellipse(surf, _CARA, (hcx - 1, hcy), 10, 9)
    _aaellipse(surf, _CARA_H, (hcx - 2, hcy - 3), 4, 2)

    # ── HERO: long widely-spread eye-stalks, thick (3px core + dark rim) so the
    #    twin periscopes read on both skies; jewel tip 2× the stalk width.
    for sgn, ex in ((-1, hcx - 6), (1, hcx + 7)):
        base = (hcx + sgn * 3, hcy - 3)
        tip = (ex + sgn * 4, CROWN_Y - 6 + rcy)
        pygame.draw.line(surf, _STALK_RIM, base, tip, 5)   # dark outline
        pygame.draw.line(surf, _STALK, base, tip, 3)        # 3px stalk core
        _jewel_eye(surf, tip[0], tip[1], 6, glow=glow)      # jewel ≈ 2× stalk

    # ── HERO: OVERSIZED lead club — the haymaker, drawn IN FRONT of head+shield.
    #    Cocked (s=0): pulled low+forward, clear of the face. Punched (s=1): the
    #    fist drives UP + FORWARD to land OVER the snout — the orange mass clearly
    #    overlaps the snout vector (hcx,hcy → eye-jewels), reading as a punch
    #    thrown past the face, never a leg dangling under the gut.
    near_elbow = _lerp_pt((bcx + 13, bcy + 6), (hcx + 5, hcy + 0), s)
    near_fist  = _lerp_pt((bcx + 19, bcy + 11), (hcx + 15, hcy - 10), s)
    _club_arm(surf, sh, near_elbow, near_fist,
              club_col=_CLUB, club_hi=_CLUB_H, arm_col=_CARA_D,
              club_r=8, lead=True, glow=glow)
    return surf


def build_mantis_shrimp(wing_angle_deg):
    """Day/standard build — flat duotone, no body glow (the 1px house outline
    supplies the day-sky contour)."""
    return _build(wing_angle_deg, glow=False)


def build_mantis_shrimp_night(wing_angle_deg):
    """Night-biome build — identical silhouette with a faint glow on ONLY the
    eye-jewels and the lead club-tip. For review parity; the live skin can
    branch on biome phase to swap builds."""
    return _build(wing_angle_deg, glow=True)


get_mantis_shrimp = _make_prebuilt_skin(build_mantis_shrimp)
get_mantis_shrimp_night = _make_prebuilt_skin(build_mantis_shrimp_night)

# Liftable into game/animal_skins.py.
BUILDERS = {"skin_mantis_shrimp": get_mantis_shrimp}
